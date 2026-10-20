<!-- zone:archive -->
# Ingestion platform explainer - lookup tables and diagram edge lists

*🗄️ Archive - companion to [report.md](report.md). For people looking up a setting and for agents verifying or regenerating the diagrams. Not meant to be read top to bottom. Source: Sam's architecture notes, true as of October 2026.*

## B Configuration reference

*🗄️ Archive - the 20 settings the notes' author always has to look up, copied unchanged from the source notes; supports [3 Failures](report.md#3-a-bad-file-is-normal-and-a-stuck-message-is-an-alarm) and [5 Week one](report.md#5-week-one-means-a-local-stack-two-runbooks-and-a-starter-ticket).*

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

Two rows raise open questions, both listed in [6 Seven questions the source notes leave open](report.md#6-seven-questions-the-source-notes-leave-open): `QUEUE_MAX_ATTEMPTS` (3) against `QUEUE_BACKOFF_S` (three delays) is question 1, and the `POLICY_MODE` default of `strict` against a local stack that mocks allow-all is question 2.

## C Diagram edge lists

*🗄️ Archive - every arrow in the two diagrams with its basis in the source notes; supports Figure 1 in the glance panel of [report.md](report.md) and Figure 2 in [1 Vocabulary](report.md#1-six-concepts-and-eleven-components-make-up-the-platform). Sources: [journey.dot](report.assets/journey.dot) and [shared-services.dot](report.assets/shared-services.dot). No arrow is inferred, so none is dashed.*

### Figure 1 - the flow of one upload

| # | From | Relation | To | Verified? | Basis in the notes |
|---|---|---|---|---|---|
| 1 | Customer | uploads file | Uploader API | yes | "Customers upload files"; the Uploader API is "the only public entry point" |
| 2 | Uploader API | sends `validate` message | Message Queue | yes | Uploader API: "puts a `validate` message on the Message Queue" |
| 3 | Uploader API | creates Version, status `received` | Catalog | yes | Uploader API: "creates a Version record in the Catalog with status `received`" |
| 4 | Message Queue | delivers `validate` message | Validation Worker | yes | Validation Worker: "takes a `validate` message"; whether the worker pulls or the queue pushes is not stated, so the arrow shows message flow |
| 5 | Validation Worker | sends `transform` message if the file is valid | Message Queue | yes | Validation Worker: "If it passes ... a `transform` message goes on the queue"; passive wording, listed under the Validation Worker |
| 6 | Validation Worker | copies invalid file | Quarantine Store | yes | "the file is copied to the Quarantine Store" |
| 7 | Validation Worker | sets `validated` or `quarantined` | Catalog | yes | "Catalog status `validated`" and "Catalog status `quarantined`" |
| 8 | Message Queue | delivers `transform` message | Transform Worker | yes | Transform Worker: "takes a `transform` message" |
| 9 | Message Queue | moves message after 3 failed attempts | DLQ | yes | Message Queue: "After 3 failed attempts a message goes to the dead-letter queue (DLQ)" |
| 10 | Transform Worker | writes tables | Curated Zone | yes | "writes it to the Curated Zone (lakehouse tables)" |
| 11 | Transform Worker | writes lineage, sets `published` | Catalog | yes | "writes a Lineage record to the Catalog ... sets Catalog status `published`" |

Facts in Figure 1 node labels, not drawn as arrows: the DLQ pages on-call ("DLQ messages page the on-call engineer"), the Quarantine Store keeps files 30 days, the Curated Zone holds the tables customers query, the Catalog is the source of truth for status.

### Figure 2 - who uses the shared services

| # | From | Relation | To | Verified? | Basis in the notes |
|---|---|---|---|---|---|
| 12 | Uploader API | asks whether this tenant may upload here | Policy Engine | yes | "asks the Policy Engine whether this tenant may upload to this dataset" |
| 13 | Catalog | asks who may see a dataset | Policy Engine | yes | Policy Engine: "Called by ... the Catalog (who can see a dataset)" |
| 14 | Curated Zone | asks for row-level rules | Policy Engine | yes | "Called by ... the Curated Zone (row-level rules)"; "Row-level access is enforced by the Policy Engine" |
| 15 | Uploader API | streams file in | Raw Zone | yes | "streams the file into the Raw Zone" |
| 16 | Validation Worker | reads file | Raw Zone | yes | "reads the file from the Raw Zone" |
| 17 | Transform Worker | reads file | Raw Zone | yes | "reads the validated file from the Raw Zone" |
| 18 | Validation Worker | fetches Schema contract | Schema Registry | yes | "fetches the Schema contract for the dataset from the Schema Registry" |
| 19 | Validation Worker | triggers a notification on quarantine | Notifier | yes | Notifier: "Called by the Validation Worker (on quarantine)" |
| 20 | Transform Worker | triggers a notification on publish | Notifier | yes | Notifier: "Called by ... the Transform Worker (on publish)" |
