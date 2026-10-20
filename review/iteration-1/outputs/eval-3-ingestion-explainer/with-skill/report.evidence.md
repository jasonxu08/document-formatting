<!-- zone:human -->
# Evidence behind "How the ingestion platform works"

*What it is: archive material for [report.md](report.md), written 2026-10-17 from Sam's architecture notes and the week-one checklist. What it is for: checking a claim in the guide, or continuing the work as an agent. How to use it: jump to a block, B [Config reference](#b-config-reference), C [Diagram sources and edge lists](#c-diagram-sources-and-edge-lists) or D [Source trace](#d-source-trace); otherwise skip it. Block A, the handoff context, is in the machine zone of `report.md`.*

<!-- zone:archive -->
## B Config reference

*All 20 settings from Sam's architecture notes, unchanged, plus the sections of the guide that use each one. Supports [4 Two kinds of failure and one source of truth](report.md#4-two-kinds-of-failure-and-one-source-of-truth), [5 Test locally in strict policy mode](report.md#5-test-locally-in-strict-policy-mode) and the numbers in sections 1, 3 and 7.*

| Setting | Default | Notes from the source | Used in section |
|---|---|---|---|
| `MAX_UPLOAD_MB` | 5120 | Uploader API hard limit | panel, 1, 3 |
| `UPLOAD_CHUNK_MB` | 16 | streaming chunk size | - |
| `VALIDATION_BATCH_ROWS` | 50000 | rows per validation batch | - |
| `VALIDATION_TIMEOUT_S` | 600 | per message | - |
| `TRANSFORM_TIMEOUT_S` | 1800 | per message | 7 |
| `QUEUE_MAX_ATTEMPTS` | 3 | then DLQ | 4, 7 |
| `QUEUE_BACKOFF_S` | 30,120,600 | retry delays | 4, 7 |
| `DLQ_ALERT_THRESHOLD` | 1 | page when DLQ depth is at least this | 4 |
| `QUARANTINE_RETENTION_DAYS` | 30 | | panel, 3 |
| `RAW_RETENTION_DAYS` | 365 | | panel, 3 |
| `CATALOG_CACHE_TTL_S` | 60 | Catalog reads cached in workers | 3 |
| `POLICY_MODE` | strict | `allow-all` only in local dev | panel, 5 |
| `POLICY_CACHE_TTL_S` | 30 | | 3 |
| `NOTIFIER_RETRY` | 2 | fire-and-forget retries | - |
| `SCHEMA_CACHE_TTL_S` | 300 | Schema Registry reads cached | 3 |
| `MAX_ROW_BYTES` | 1048576 | reject longer rows | - |
| `PARQUET_ROW_GROUP_MB` | 128 | transform output | 3 |
| `CURATED_PARTITION_BY` | upload_date | default partitioning | 3 |
| `WORKER_CONCURRENCY` | 4 | messages per worker | - |
| `LOG_LEVEL` | info | | - |

<!-- zone:archive -->
## C Diagram sources and edge lists

*What the two figures are built from. Supports the figure in the glance panel of the guide and the figure in [3 Eleven components in five roles with two hubs](report.md#3-eleven-components-in-five-roles-with-two-hubs). "Verified" means Sam's notes state the relation; no edge in either figure is inferred, so none is dashed. From and To follow the arrows in the figures, which point the way a file, message, query or status update travels.*

Sources: [ingestion-overview.dot](report.assets/ingestion-overview.dot) renders to `ingestion-overview.png`, and [shared-services.dot](report.assets/shared-services.dot) renders to `shared-services.png`. Rebuild from inside `report.assets` with `dot -Tpng -Gdpi=150 <name>.dot -o <name>.png`.

### C1 Edge list of the overview figure (glance panel)

| From | Relation | To | Verified? | Source passage in the architecture notes |
|---|---|---|---|---|
| Customer | uploads file | Uploader API | yes | What it is; The pieces, Uploader API ("the only public entry point") |
| Uploader API | streams file | Raw Zone | yes | The pieces, Uploader API |
| Uploader API | queues `validate` message | Message Queue | yes | The pieces, Uploader API |
| Message Queue | delivers `validate` message | Validation Worker | yes | The pieces, Validation Worker ("takes a `validate` message") |
| Raw Zone | supplies the file to check | Validation Worker | yes | The pieces, Validation Worker ("reads the file from the Raw Zone") |
| Validation Worker | queues `transform` message when the file passes | Message Queue | yes | The pieces, Validation Worker |
| Validation Worker | copies the file when validation fails | Quarantine Store | yes | The pieces, Validation Worker |
| Message Queue | delivers `transform` message | Transform Worker | yes | The pieces, Transform Worker ("takes a `transform` message") |
| Raw Zone | supplies the file to convert | Transform Worker | yes | The pieces, Transform Worker ("reads the validated file from the Raw Zone") |
| Transform Worker | writes tables | Curated Zone | yes | The pieces, Transform Worker |
| Customer | queries | Curated Zone | yes | The pieces, Curated Zone ("tables that customers query"); the access path is not described |
| Uploader API | sets `received` | Catalog | yes | The pieces, Uploader API |
| Validation Worker | sets `validated` or `quarantined` | Catalog | yes | The pieces, Validation Worker |
| Transform Worker | writes lineage and sets `published` | Catalog | yes | The pieces, Transform Worker |

### C2 Edge list of the shared-services figure (section 3)

| From | Relation | To | Verified? | Source passage in the architecture notes |
|---|---|---|---|---|
| Uploader API | asks "may this tenant upload?" | Policy Engine | yes | The pieces, Policy Engine ("Called by the Uploader API (upload rights)") |
| Catalog | asks "who can see this dataset?" | Policy Engine | yes | The pieces, Policy Engine ("by the Catalog (who can see a dataset)") |
| Curated Zone | asks for row-level rules | Policy Engine | yes | The pieces, Policy Engine ("by the Curated Zone (row-level rules)"); Curated Zone |
| Uploader API | sets `received` | Catalog | yes | The pieces, Uploader API |
| Validation Worker | sets `validated` or `quarantined` | Catalog | yes | The pieces, Validation Worker |
| Transform Worker | writes lineage and sets `published` | Catalog | yes | The pieces, Transform Worker |
| Validation Worker | gets the Schema contract | Schema Registry | yes | The pieces, Validation Worker |
| Validation Worker | sends the quarantine notice | Notifier | yes | The pieces, Notifier ("Called by the Validation Worker (on quarantine)") |
| Transform Worker | sends the publish notice | Notifier | yes | The pieces, Notifier ("and the Transform Worker (on publish)") |

<!-- zone:archive -->
## D Source trace

*Which passage of the notes each part of the guide rests on, and which statements are inference or arithmetic rather than Sam's words. Supports [7 What this guide does not know](report.md#7-what-this-guide-does-not-know).*

| Part of the guide | Built from | Kind |
|---|---|---|
| Glance panel: mental model, key facts | Architecture notes: What it is; The pieces; Numbers; Failure handling | stated |
| 1 Walkthrough table | The pieces: Uploader API, Validation Worker, Transform Worker | stated |
| 1 Timing paragraph | Numbers | stated; "about 7 of those minutes" adds the two p95 figures |
| 2 Terms and the three kinds of version | Concepts you must get right; Gotchas 1 and 2; The pieces: Schema Registry | stated |
| 3 Component table | The pieces; Gotchas 3, 5 and 6; settings table for Parquet row groups and partitioning | stated |
| 3 Cache sentence | Settings table: `CATALOG_CACHE_TTL_S`, `SCHEMA_CACHE_TTL_S`, `POLICY_CACHE_TTL_S` | inferred: the effect that a change takes up to the TTL to show up |
| 4 Failure table and the three rules | Failure handling; Numbers; The pieces: Message Queue, Quarantine Store, Notifier; Gotcha 5 | stated, except the Version-status row for infrastructure failures and the stuck-Version hint, both inferred |
| 5 Local testing | Gotcha 4; settings table `POLICY_MODE`; week-one checklist, item 3 | stated |
| 6 First week | Week-one checklist, all eight items | stated; the days, the repo purposes and the ticket mapping are suggestions or inferences, marked in the text |
| 6 Self-check questions | Sections 1 to 5 of the guide | added by the author, derived from the stated facts |
| 7 Open questions | Cross-reading of both source files | inferred or arithmetic, each with its basis in the row |
