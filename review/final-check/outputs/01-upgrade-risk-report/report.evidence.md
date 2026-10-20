<!-- zone:archive -->
# Evidence for the runtime upgrade assessment

*🗄️ Archive - the checksums, recomputed numbers, dependency edge list, incident breakdown and decision record behind [report.md](report.md). Nobody needs to read it start to finish; use the contents list.*

Contents:

- [A Source files and checksums](#a-source-files-and-checksums) - the three inputs, their SHA-256 and how to verify the copies
- [B Numbers and dates recomputed](#b-numbers-and-dates-recomputed) - every derived figure in the report and how it was calculated
- [C Service inventory and dependency edges](#c-service-inventory-and-dependency-edges) - the 16 edges of the map, each traced to the inventory
- [D Q3 incident breakdown](#d-q3-incident-breakdown) - counts by service, severity and cause, and the outage recorded twice
- [E Decision record](#e-decision-record) - where the outcome of the decision is logged

## A Source files and checksums

*🗄️ Archive - proves the supporting data was kept unchanged; supports every claim in [report.md](report.md).*

The three inputs were copied byte for byte into `report.data/` (original CRLF line endings kept). The originals were only read, never modified.

| File in `report.data/` | What it is | Bytes | SHA-256 |
|---|---|---|---|
| [upgrade-notes.md](report.data/upgrade-notes.md) | Platform team notes "Runtime upgrade (v8 to v10) - notes for the decision", written 2026-10-14 | 2886 | `aad08996cde2677599234aa09a00c877e875e9e444f1a1122958e908b6abd735` |
| [services.csv](report.data/services.csv) | Inventory of the 9 services: owner, criticality, runtime, depends_on, rollback_path, staging_result | 732 | `8573da3565d6e080d4aee06cc0469a06e5ef6d1dde0b20ffed93bdf4d937a3cc` |
| [incidents-q3.csv](report.data/incidents-q3.csv) | 36 incident records, 2026-07-02 to 2026-09-28 | 3279 | `2600694c932efbee7c02eda5bf4e89474835c1f3d3d579338cbdbfbaf62b64c4` |

To verify, run from the folder that holds `report.md`: `Get-FileHash report.data/* -Algorithm SHA256` (PowerShell) or `sha256sum report.data/*` (Linux, macOS) and compare with the table.

## B Numbers and dates recomputed

*🗄️ Archive - every figure in the report that is derived rather than copied, with its calculation; supports the panel and sections 1 to 5 of [report.md](report.md).*

Method: counts and day differences were computed by script (Python 3.12, `csv` and `datetime`) over the copies in `report.data/`. Images were rendered with Graphviz 14.1.3 and matplotlib 3.9.2. Where a figure is copied from the notes, the notes are named.

**Counts**

| Statement in the report | Value | How it was computed |
|---|---|---|
| Services passing staging | 7 of 9 | `staging_result` begins "pass" for `gateway`, `catalog-service`, `share-service`, `connector-service`, `map-service`, `search-index`, `notify-service`; the notes say the same |
| Services without a rollback path | 2 | `rollback_path` is "no" for `auth-service` and `user-store`; the notes say the same |
| Dependents of `auth-service` | 6 | Rows whose `depends_on` contains `auth-service`: `gateway`, `catalog-service`, `share-service`, `connector-service`, `map-service`, `notify-service` |
| Services that depend on `user-store` through `auth-service` | 7 of the other 8 | `auth-service` plus its 6 dependents; only `search-index`, which has no dependencies, does not |
| Dependency edges | 16 | Entries of `depends_on`, split on ";" (block C) |
| `catalog-service` and `map-service` depend on each other | 2 edges | Line 5 of `services.csv` lists `map-service`; line 8 lists `catalog-service` |
| Incident records in Q3 | 36 | Data rows of `incidents-q3.csv`, first 2026-07-02, last 2026-09-28 |
| `auth-service` share of records | 11 of 36 = 30.6%, shown as 31% | Rows with service `auth-service` |
| `auth-service` SEV2 and SEV1 records | 6 of 10 SEV2; 1 of 2 SEV1 | Severity column (block D) |
| The two SEV1 records are one outage | 1 outage | Both dated 2026-07-11, 78 minutes; the `gateway` summary reads "caused by auth-service SEV1" |
| `gateway` records naming `auth-service` | 4 of 7 | Summary text contains "auth-service": 2026-07-05, 2026-07-11, 2026-08-27, 2026-09-15 |
| Records that involve `auth-service` | 15 of 36 = 41.7%; 14 of 35 = 40.0% | 11 own plus 4 `gateway` = 15; dropping the duplicate 2026-07-11 `gateway` row gives 14 of 35 |
| `auth-service` failure types | 5 timeouts (221 min), 3 refresh bugs (72), 2 config (39), 1 GC (48) | Grouped by `cause`; 221 + 72 + 39 + 48 = 380 minutes, matching block D |
| Failed rollouts in Q3 | 5, recovered in 10, 14, 15, 15 and 19 minutes; 4 of 5 within 15 | Rows with cause `deploy`: `share-service` twice, `map-service`, `connector-service`, `catalog-service`, so four distinct services, all among the seven |
| Runtime-related records | 3, 82 minutes | Rows with cause `runtime-gc`: `catalog-service` 16, `auth-service` 48, `search-index` 18 |
| Token-refresh incidents | 3 | Rows with cause `token-refresh-bug`: 2026-07-21, 2026-08-14, 2026-09-28, all `auth-service` |
| Failing staging tests | 2 of 148 | The notes and the `staging_result` of `auth-service` |

**Dates and spans** (weekdays computed, not copied)

| Date or span | Value | Check |
|---|---|---|
| Report date | Mon 2026-10-19 | The day this report was written |
| Decision due | Fri 2026-10-23 | The notes say "Friday 2026-10-23"; computed Friday |
| Data team start | Mon 2026-10-26 | The notes say "Monday 2026-10-26"; computed Monday |
| Data week end, read as five working days | Fri 2026-10-30 | Monday plus 4 days (an assumption about "one week") |
| Freeze start | Sun 2026-11-01 | The notes |
| Extended-support order deadline | Thu 2026-11-05 | The notes |
| End of v8 security support | Thu 2026-11-12 | The notes |
| Identity leave | Mon 2026-10-26 to Fri 2026-11-13 | The notes; 19 days counting both ends |
| Vendor library, "by end of November" | Mon 2026-11-30 | Last day of the month; the notes give no exact date |
| Freeze end | Tue 2027-01-05 | The notes |
| Decision to Data start | 3 days | 2026-10-26 minus 2026-10-23 |
| Data week end to freeze start | 2 days | 2026-11-01 minus 2026-10-30 |
| Decision to order deadline | 13 days | 2026-11-05 minus 2026-10-23 |
| Order deadline to end of v8 support | 7 days | 2026-11-12 minus 2026-11-05 |
| Freeze start to end of v8 support | 11 days | 2026-11-12 minus 2026-11-01 |
| End of v8 support to freeze end | 54 days | 2027-01-05 minus 2026-11-12 |
| End of v8 support to 2026-11-30 | 18 days | 2026-11-30 minus 2026-11-12 |
| Freeze start to 2026-11-30 | 29 days | 2026-11-30 minus 2026-11-01 |
| Staging end to report date | 8 days | 2026-10-19 minus 2026-10-11 |
| One quarter of extended support | ends about Thu 2027-02-11 | 2026-11-12 plus 91 days; an assumption, the notes do not say how quarters are counted |

## C Service inventory and dependency edges

*🗄️ Archive - the 16 edges of the dependency map, each traced to a line of the inventory; supports the map in the panel of [report.md](report.md) and [2 auth-service is the hub and the weakest point in Q3](report.md#2-auth-service-is-the-hub-and-the-weakest-point-in-q3).*

An edge "A depends on B" means B is listed in the `depends_on` column of A's row in [services.csv](report.data/services.csv). Every edge is read directly from that file, so none is inferred. Diagram source: [dependency-map.dot](report.assets/dependency-map.dot).

| # | From | Depends on | Source line in `services.csv` | Verified |
|---|---|---|---|---|
| 1 | `gateway` | `auth-service` | 2 | yes |
| 2 | `gateway` | `catalog-service` | 2 | yes |
| 3 | `gateway` | `share-service` | 2 | yes |
| 4 | `gateway` | `connector-service` | 2 | yes |
| 5 | `auth-service` | `user-store` | 3 | yes |
| 6 | `catalog-service` | `auth-service` | 5 | yes |
| 7 | `catalog-service` | `search-index` | 5 | yes |
| 8 | `catalog-service` | `map-service` | 5 | yes |
| 9 | `share-service` | `auth-service` | 6 | yes |
| 10 | `share-service` | `catalog-service` | 6 | yes |
| 11 | `share-service` | `notify-service` | 6 | yes |
| 12 | `connector-service` | `auth-service` | 7 | yes |
| 13 | `connector-service` | `catalog-service` | 7 | yes |
| 14 | `map-service` | `auth-service` | 8 | yes |
| 15 | `map-service` | `catalog-service` | 8 | yes |
| 16 | `notify-service` | `auth-service` | 10 | yes |

`user-store` (line 4) and `search-index` (line 9) have an empty `depends_on`. Edges 8 and 15 are the mutual dependency of `catalog-service` and `map-service`; the Q3 incidents of 2026-09-08 and 2026-09-19 describe the same coupling in their summaries.

## D Q3 incident breakdown

*🗄️ Archive - counts of the 36 Q3 incident records by service, severity and cause, and the outage recorded twice; supports [2 auth-service is the hub and the weakest point in Q3](report.md#2-auth-service-is-the-hub-and-the-weakest-point-in-q3). The full list is [incidents-q3.csv](report.data/incidents-q3.csv).*

**By service** (minutes are the sum of `duration_min`)

| Service | Records | SEV1 | SEV2 | SEV3 | Minutes |
|---|---|---|---|---|---|
| `auth-service` | 11 | 1 | 6 | 4 | 380 |
| `gateway` | 7 | 1 | 1 | 5 | 178 |
| `catalog-service` | 5 | 0 | 1 | 4 | 124 |
| `share-service` | 4 | 0 | 1 | 3 | 84 |
| `connector-service` | 3 | 0 | 0 | 3 | 72 |
| `map-service` | 2 | 0 | 0 | 2 | 26 |
| `notify-service` | 2 | 0 | 0 | 2 | 17 |
| `search-index` | 1 | 0 | 0 | 1 | 18 |
| `user-store` | 1 | 0 | 1 | 0 | 33 |
| Total | 36 | 2 | 10 | 24 | 932 |

The total of 932 minutes counts the 78-minute outage of 2026-07-11 twice (once for `auth-service`, once for `gateway`). Counted once, Q3 has 35 distinct records and 854 minutes, and one SEV1 outage.

**By cause**

| Cause | Records | Minutes | Services |
|---|---|---|---|
| `config` | 6 | 113 | `auth-service` 2, `gateway` 2, `catalog-service` 1, `user-store` 1 |
| `dependency` | 6 | 183 | `connector-service` 2, `catalog-service` 2, `share-service` 1, `map-service` 1 |
| `downstream-timeout` | 6 | 171 | `gateway` 5, `share-service` 1 |
| `deploy` | 5 | 73 | `share-service` 2, `map-service` 1, `connector-service` 1, `catalog-service` 1 |
| `token-validation-timeout` | 5 | 221 | `auth-service` 5 |
| `runtime-gc` | 3 | 82 | `catalog-service` 1, `auth-service` 1, `search-index` 1 |
| `token-refresh-bug` | 3 | 72 | `auth-service` 3 |
| `queue-backlog` | 2 | 17 | `notify-service` 2 |

**Records quoted in the report**

| Date | Service | Severity | Minutes | Cause | Summary in the log | Why it is quoted |
|---|---|---|---|---|---|---|
| 2026-07-11 | `auth-service` | SEV1 | 78 | token-validation-timeout | Login failures for 78 minutes after cache eviction storm | The one SEV1 outage |
| 2026-07-11 | `gateway` | SEV1 | 78 | downstream-timeout | Gateway returned 503 for all authenticated routes (caused by auth-service SEV1) | Same outage, recorded a second time |
| 2026-07-05 | `gateway` | SEV3 | 12 | downstream-timeout | Gateway 504s while auth-service slow | Names `auth-service` |
| 2026-08-27 | `gateway` | SEV3 | 13 | downstream-timeout | 504s while auth-service cache warmed | Names `auth-service` |
| 2026-09-15 | `gateway` | SEV2 | 36 | downstream-timeout | 504s traced to auth-service latency | Names `auth-service` |
| 2026-07-21 | `auth-service` | SEV2 | 41 | token-refresh-bug | Refresh tokens rejected after clock skew on one node | Token refresh area |
| 2026-08-14 | `auth-service` | SEV3 | 19 | token-refresh-bug | Refresh token reuse detection false positives | Token refresh area |
| 2026-09-28 | `auth-service` | SEV3 | 12 | token-refresh-bug | Intermittent refresh failures after deploy | Token refresh area |
| 2026-07-14 | `share-service` | SEV3 | 15 | deploy | Failed rollout; rolled back within 15 minutes | Rollback evidence |
| 2026-08-03 | `map-service` | SEV3 | 14 | deploy | Failed rollout; rolled back within 14 minutes | Rollback evidence |
| 2026-08-29 | `share-service` | SEV3 | 10 | deploy | Failed rollout; rolled back within 10 minutes | Rollback evidence |
| 2026-09-17 | `connector-service` | SEV3 | 19 | deploy | Failed rollout; rolled back within 19 minutes | Rollback evidence, above the notes' 10-15 |
| 2026-09-27 | `catalog-service` | SEV3 | 15 | deploy | Failed rollout; rolled back within 15 minutes | Rollback evidence |
| 2026-08-19 | `catalog-service` | SEV3 | 16 | runtime-gc | GC pauses on large dataset listing | Runtime-related |
| 2026-09-02 | `auth-service` | SEV2 | 48 | runtime-gc | Long GC pauses blocked token endpoint | Runtime-related |
| 2026-09-26 | `search-index` | SEV3 | 18 | runtime-gc | Index rebuild paused by GC | Runtime-related |
| 2026-09-08 | `catalog-service` | SEV3 | 21 | dependency | Map-service latency slowed dataset detail pages | `catalog-service` and `map-service` coupling |
| 2026-09-19 | `map-service` | SEV3 | 12 | dependency | Catalog-service latency caused timeouts | `catalog-service` and `map-service` coupling |

## E Decision record

*🗄️ Archive - where the outcome of the decision is logged, so the report stays an audit trail; supports the decisions block in the panel of [report.md](report.md). Append a row for each decision and never edit earlier rows.*

| Date | Decided by | Decision | Notes |
|---|---|---|---|
| open | Marcus Hale | Not decided as of 2026-10-19 | Plan due Fri 2026-10-23; extended-support order due Thu 2026-11-05. The report recommends the split (suggested), see [report.md](report.md) |
