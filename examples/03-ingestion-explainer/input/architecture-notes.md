# Ingestion platform - brain dump (Sam, unedited)

Written for myself, so it is messy. Everything here is true as of October 2026.

## What it is
Customers upload files (CSV, Parquet, JSON lines) and the platform checks them, transforms them, and publishes them as queryable tables. The whole thing is asynchronous. Nobody waits on an HTTP call for the result.

## The pieces
- **Uploader API** - the only public entry point. Authenticates the caller, asks the **Policy Engine** whether this tenant may upload to this dataset, streams the file into the **Raw Zone** (blob storage), creates a Version record in the **Catalog** with status `received`, and puts a `validate` message on the **Message Queue**.
- **Message Queue** - carries `validate` and `transform` messages. Delivery is at-least-once, so every worker must be idempotent. After 3 failed attempts a message goes to the dead-letter queue (DLQ).
- **Validation Worker** - takes a `validate` message, reads the file from the Raw Zone, fetches the **Schema contract** for the dataset from the **Schema Registry**, and checks the file against it. If it passes: Catalog status `validated` and a `transform` message goes on the queue. If it fails: the file is copied to the **Quarantine Store**, Catalog status `quarantined`, and the **Notifier** tells the dataset owner why.
- **Schema Registry** - stores the Schema contract per dataset, versioned. Only backward-compatible changes are allowed. A breaking change means a new dataset major version.
- **Quarantine Store** - holds files that failed validation, for 30 days. Owners can fix and re-upload, or ask support to release a file with the `quarantine-release` runbook.
- **Transform Worker** - takes a `transform` message, reads the validated file from the Raw Zone, converts it to the curated format, writes it to the **Curated Zone** (lakehouse tables), writes a Lineage record to the Catalog (which version came from which raw file and which schema contract), sets Catalog status `published`, and asks the Notifier to email the owner.
- **Raw Zone** - immutable blob storage. Keeps the original upload for 1 year.
- **Curated Zone** - the lakehouse tables that customers query. Row-level access is enforced by the Policy Engine.
- **Catalog** - metadata store. Datasets, Versions, statuses, lineage, owners. The Catalog is the source of truth for status, NOT the queue.
- **Policy Engine** - answers "may this user or tenant do X on dataset Y". Called by the Uploader API (upload rights), by the Catalog (who can see a dataset) and by the Curated Zone (row-level rules).
- **Notifier** - sends emails and webhooks. Called by the Validation Worker (on quarantine) and the Transform Worker (on publish).

## Concepts you must get right
- **Dataset** - a named collection a tenant owns, with a Schema contract. Example: `acme/orders`.
- **Version** - one upload of a dataset. Immutable. Re-uploading creates a new Version, it never overwrites.
- **Schema contract** - the agreed column names, types and constraints. Validation checks against it.
- **Quarantine** - where a Version goes when validation fails. The Version stays visible in the Catalog with status `quarantined`.
- **Lineage record** - links a published Version to its raw file and to the schema contract version it was validated with.
- **Tenant** - a customer organisation. Everything is scoped to a tenant.

## Numbers
- Typical file: 50 to 500 MB. Maximum: 5 GB.
- Validation p95: 40 seconds for 1 GB. Transform p95: 6 minutes for 1 GB.
- Target: published within 15 minutes for files up to 1 GB.
- Retries: 3 attempts with backoff 30 s, 2 min, 10 min. Then DLQ. DLQ messages page the on-call engineer.
- Replaying the DLQ: runbook `replay-dlq`. Safe to run because workers are idempotent.

## Failure handling, in one paragraph
Validation failure is not an error of the platform, it is an expected outcome: the file is quarantined and the owner is told. Infrastructure failures (blob timeouts, registry unavailable) are retried 3 times and then go to the DLQ. If status in the Catalog and what you see in the queue disagree, trust the Catalog.

## Gotchas
1. Versions are immutable. People ask to "fix" a Version. They must upload a new one.
2. Breaking schema changes need a new dataset major version, not a new Version.
3. All timestamps are UTC, including in the Catalog UI. Support gets confused about this every week.
4. Locally, `docker compose up` starts emulators for the queue and blob storage. The Policy Engine is mocked as allow-all unless you set `POLICY_MODE=strict`. Always run the e2e smoke test with `POLICY_MODE=strict` before opening a PR.
5. The Notifier is fire-and-forget. A failed email never fails a Version.
6. Quarantine retention is 30 days, Raw Zone retention is 1 year. People mix these up.

## Config values I always have to look up
| Setting | Default | Notes |
|---|---|---|
| MAX_UPLOAD_MB | 5120 | Uploader API hard limit |
| UPLOAD_CHUNK_MB | 16 | streaming chunk size |
| VALIDATION_BATCH_ROWS | 50000 | rows per validation batch |
| VALIDATION_TIMEOUT_S | 600 | per message |
| TRANSFORM_TIMEOUT_S | 1800 | per message |
| QUEUE_MAX_ATTEMPTS | 3 | then DLQ |
| QUEUE_BACKOFF_S | 30,120,600 | retry delays |
| DLQ_ALERT_THRESHOLD | 1 | page when DLQ depth is at least this |
| QUARANTINE_RETENTION_DAYS | 30 | |
| RAW_RETENTION_DAYS | 365 | |
| CATALOG_CACHE_TTL_S | 60 | Catalog reads cached in workers |
| POLICY_MODE | strict | `allow-all` only in local dev |
| POLICY_CACHE_TTL_S | 30 | |
| NOTIFIER_RETRY | 2 | fire-and-forget retries |
| SCHEMA_CACHE_TTL_S | 300 | Schema Registry reads cached |
| MAX_ROW_BYTES | 1048576 | reject longer rows |
| PARQUET_ROW_GROUP_MB | 128 | transform output |
| CURATED_PARTITION_BY | upload_date | default partitioning |
| WORKER_CONCURRENCY | 4 | messages per worker |
| LOG_LEVEL | info | |
