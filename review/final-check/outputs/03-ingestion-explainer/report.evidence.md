<!-- zone:archive -->
# Evidence for the ingestion platform explainer

*🗄️ Archive - the settings table, the edge lists of both figures, a ledger of what this page adds to the notes, and the source checksums. It backs the claims in [report.md](report.md); nothing here is needed to understand the platform.*

Contents: [Config reference](#config-reference) · [Diagram edge lists](#diagram-edge-lists) · [Stated versus inferred](#stated-versus-inferred) · [Sources](#sources)

## Config reference

*🗄️ Archive - the table "Config values I always have to look up" from `architecture-notes.md`. The first three columns are verbatim; the last column is this page's pointer to where the setting is used in [report.md](report.md). Backs the numbers in sections 2 to 5.*

| Setting | Default | Notes | Used in report.md |
|---|---|---|---|
| MAX_UPLOAD_MB | 5120 | Uploader API hard limit | panel, section 2 |
| UPLOAD_CHUNK_MB | 16 | streaming chunk size | section 2 |
| VALIDATION_BATCH_ROWS | 50000 | rows per validation batch | - |
| VALIDATION_TIMEOUT_S | 600 | per message | section 2 |
| TRANSFORM_TIMEOUT_S | 1800 | per message | sections 2 and 6 |
| QUEUE_MAX_ATTEMPTS | 3 | then DLQ | panel, sections 4 and 6 |
| QUEUE_BACKOFF_S | 30,120,600 | retry delays | sections 4 and 6 |
| DLQ_ALERT_THRESHOLD | 1 | page when DLQ depth is at least this | section 4 |
| QUARANTINE_RETENTION_DAYS | 30 | | panel, sections 2 and 4 |
| RAW_RETENTION_DAYS | 365 | | panel, section 2 |
| CATALOG_CACHE_TTL_S | 60 | Catalog reads cached in workers | section 2 |
| POLICY_MODE | strict | `allow-all` only in local dev | panel, sections 5 and 6 |
| POLICY_CACHE_TTL_S | 30 | | - |
| NOTIFIER_RETRY | 2 | fire-and-forget retries | section 2 |
| SCHEMA_CACHE_TTL_S | 300 | Schema Registry reads cached | section 2 |
| MAX_ROW_BYTES | 1048576 | reject longer rows | - |
| PARQUET_ROW_GROUP_MB | 128 | transform output | - |
| CURATED_PARTITION_BY | upload_date | default partitioning | - |
| WORKER_CONCURRENCY | 4 | messages per worker | - |
| LOG_LEVEL | info | | - |

## Diagram edge lists

*🗄️ Archive - every edge of Figure 1 ([flow-map.dot](report.assets/flow-map.dot)) and Figure 2 ([touch-map.dot](report.assets/touch-map.dot)) with the statement in `architecture-notes.md` that backs it. Every edge is stated in the notes, so none is dashed. Backs the figures in the panel and in section 2 of [report.md](report.md).*

### Figure 1 edges

| From | Relation | To | Verified? Backing statement in the notes |
|---|---|---|---|
| Customer | uploads file | Uploader API | Stated: "Customers upload files"; the Uploader API is "the only public entry point" |
| Uploader API | queues validate | Message Queue | Stated: "puts a `validate` message on the Message Queue" |
| Message Queue | delivers validate | Validation Worker | Stated: the Validation Worker "takes a `validate` message" |
| Validation Worker | queues transform (file passed) | Message Queue | Stated: "a `transform` message goes on the queue" |
| Message Queue | delivers transform | Transform Worker | Stated: the Transform Worker "takes a `transform` message" |
| Transform Worker | writes tables | Curated Zone | Stated: "writes it to the Curated Zone (lakehouse tables)" |
| Validation Worker | copies failed file | Quarantine Store | Stated: "the file is copied to the Quarantine Store" |
| Message Queue | dead-letters after 3 failed attempts | DLQ | Stated: "After 3 failed attempts a message goes to the dead-letter queue (DLQ)" |
| DLQ | pages | On-call engineer | Stated: "DLQ messages page the on-call engineer" |
| Uploader API | sets received | Catalog | Stated: "creates a Version record in the Catalog with status `received`" |
| Validation Worker | sets validated or quarantined | Catalog | Stated: "Catalog status `validated`" on a pass, "Catalog status `quarantined`" on a fail |
| Transform Worker | sets published | Catalog | Stated: "sets Catalog status `published`" |

### Figure 2 edges

| From | Relation | To | Verified? Backing statement in the notes |
|---|---|---|---|
| Uploader API | streams file in | Raw Zone | Stated: "streams the file into the Raw Zone (blob storage)" |
| Uploader API | asks: may this tenant upload? | Policy Engine | Stated: "asks the Policy Engine whether this tenant may upload to this dataset" |
| Validation Worker | reads file | Raw Zone | Stated: "reads the file from the Raw Zone" |
| Validation Worker | fetches contract | Schema Registry | Stated: "fetches the Schema contract for the dataset from the Schema Registry" |
| Validation Worker | copies failed file | Quarantine Store | Stated: "the file is copied to the Quarantine Store" |
| Validation Worker | notifies: quarantined | Notifier | Stated: "the Notifier tells the dataset owner why"; the Notifier is "called by the Validation Worker (on quarantine)" |
| Transform Worker | reads file | Raw Zone | Stated: "reads the validated file from the Raw Zone" |
| Transform Worker | writes tables | Curated Zone | Stated: "writes it to the Curated Zone (lakehouse tables)" |
| Transform Worker | notifies: published | Notifier | Stated: "asks the Notifier to email the owner"; the Notifier is called "by the Transform Worker (on publish)" |
| Catalog | asks: who may see a dataset? | Policy Engine | Stated: the Policy Engine is "called ... by the Catalog (who can see a dataset)" |
| Curated Zone | asks: row-level rules | Policy Engine | Stated: the Policy Engine is called "by the Curated Zone (row-level rules)" |
| Notifier | emails or webhooks | Dataset owner | Stated: "Notifier - sends emails and webhooks"; it tells or emails the owner |

## Stated versus inferred

*🗄️ Archive - everything [report.md](report.md) adds to `architecture-notes.md` and `onboarding-checklist.md`, so a reviewer knows what to confirm. Backs the "Confidence" line in the panel.*

| Item | Where it appears | Kind | Basis |
|---|---|---|---|
| Stage numbers 1 to 3 | Figures 1 and 2, section 3 | This page's label | The notes describe three components in order but number nothing |
| Three component groups (Pipeline, Storage, Shared services) | Section 2 | This page's label | Grouping for readability only |
| "Set by" column of the status table | Section 1 | Stated, regrouped | The Uploader API creates `received`, the Validation Worker sets `validated` or `quarantined`, the Transform Worker sets `published` |
| "Three different things are called a version" | Section 1 | This page's observation | The notes use "Version", "schema contract version" and "dataset major version" but never compare them |
| 12.5 minutes of retry delays | Section 6 | Derived | 30 s + 120 s + 600 s from `QUEUE_BACKOFF_S`; assumes all three delays are served before the DLQ |
| 5 GB takes about 30 minutes to transform | Section 6 | Derived, unverified | 5 x 6 minutes; assumes the 1 GB p95 scales linearly, which the notes do not say |
| A dead-lettered Version keeps its last status | Section 6 | Inference | Each stage sets only its own status; the notes never say what the Catalog shows for a dead-lettered message |
| `POLICY_MODE` default in local runs | Panel, sections 5 and 6 | Conflict in the notes | The config table says `strict`; the gotcha says the local stack mocks allow-all unless set. This page follows the gotcha |
| "3 attempts" versus "retried 3 times" | Sections 4 and 6 | Ambiguity in the notes | This page uses "3 attempts, then DLQ" |
| With the allow-all mock a permission problem cannot show up locally | Section 5 | Consequence of a stated fact | The notes say the Policy Engine is mocked as allow-all locally |
| End states of the two sample uploads (`published`, `quarantined`) | Section 5 | Consequence of the stated flow | A passing file ends at `published` and a failing file at `quarantined`, per the stages in the notes |
| Read the Catalog status first when debugging | Section 4 | Suggestion | Follows from the stated rule "trust the Catalog" |
| Do the access step first | Section 5 | Suggestion | The later steps need repo, subscription and rota access |
| Sections to read for INGEST-310 and INGEST-322 | Section 5 | Suggestion | Based on the ticket titles alone |
| Quarantine notifies the dataset owner; paging is mentioned only for DLQ messages | Section 4 | Stated absence | The notes describe paging for DLQ messages and say nothing about paging on quarantine |
| Customers querying the Curated Zone is not drawn as an edge | Figure 1 | Omission | The notes say customers query these tables but not through which component |
| Reading times in the panel | Panel | Estimate | Word counts at 150 to 200 words a minute, rounded up |

## Sources

*🗄️ Archive - the two input files this page was written from, identified by checksum so a later reader can tell whether they changed. The files are not copied here.*

| File | SHA-256 | What it is |
|---|---|---|
| `architecture-notes.md` | `1348CF80527FE2F56B43DAED9CA940973F1B9C3A158ED6A07AF7AA2C6B0F5A4E` | Sam's unedited brain dump, "true as of October 2026" |
| `onboarding-checklist.md` | `DC4A5CAAC6DBF074145DF1283AD2CC62153D4D618213A8FF52381770E728D9CD` | Week-one checklist for new ingestion engineers |
