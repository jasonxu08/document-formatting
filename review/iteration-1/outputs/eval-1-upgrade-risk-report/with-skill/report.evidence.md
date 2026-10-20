<!-- zone:archive -->
# Evidence for the v8 to v10 upgrade assessment

*Archive for [report.md](report.md), written 2026-10-17. Skip unless you are auditing a number or continuing the work: nothing here is needed to make the decision. Every figure in the report is reproduced by `report.assets/analyze.py`.*

Contents: [E1 Sources and hashes](#e1-sources-and-hashes) · [E2 Method](#e2-method) · [E3 Claim register](#e3-claim-register) · [E4 Incidents by service](#e4-incidents-by-service) · [E5 Incident records cited in the report](#e5-incident-records-cited-in-the-report) · [E6 Dependency analysis](#e6-dependency-analysis) · [E7 Calendar](#e7-calendar) · [E8 Reproduce](#e8-reproduce)

## E1 Sources and hashes

*Supports every claim in the report: what the inputs were, and proof that the copies are unchanged.*

The requester supplied three files. They were copied on 2026-10-17, byte for byte, into `report.data/`; the SHA-256 values below were taken from the copies and match the originals.

| File in `report.data/` | What it is | Bytes | SHA-256 |
|---|---|---|---|
| `upgrade-notes.md` | Platform team's notes for the decision, written 2026-10-14 | 2886 | `aad08996cde2677599234aa09a00c877e875e9e444f1a1122958e908b6abd735` |
| `services.csv` | Inventory of the 9 services: team, criticality, runtime, `depends_on`, rollback path, staging result | 732 | `8573da3565d6e080d4aee06cc0469a06e5ef6d1dde0b20ffed93bdf4d937a3cc` |
| `incidents-q3.csv` | 36 incident records, 2026-07-02 to 2026-09-28 | 3279 | `2600694c932efbee7c02eda5bf4e89474835c1f3d3d579338cbdbfbaf62b64c4` |

Line references such as L22 mean line 22 of `upgrade-notes.md`.

## E2 Method

*Supports [section 2](report.md#2-auth-service-is-also-the-weak-point-in-production) and the dependency counts in [section 1](report.md#1-seven-services-are-ready-and-the-two-identity-services-are-not).*

- **Records versus incidents.** The log has 36 records. The `gateway` record of 2026-07-11 (SEV1, 78 minutes, summary "caused by auth-service SEV1") has the same date, severity and duration as the `auth-service` SEV1 and describes the same outage, so the log holds 35 distinct incidents. Counts by service use records; shares of the quarter use distinct incidents.
- **Attribution to `auth-service`.** An incident counts when it is in `auth-service`'s own records (11), or when a `gateway` record's summary names `auth-service` (4 records; 3 distinct after removing the 2026-07-11 duplicate). No other record names `auth-service`. Records that blame other services (for example `catalog-service` and `map-service` blaming each other) are not attributed. Result: 11 + 3 = 14 of 35 distinct incidents (40%).
- **Dependencies.** Edges come from the `depends_on` column. Direct dependents are the reverse of those edges; "direct or indirect" follows the edges transitively and never counts a service as its own dependent.
- **Calendar arithmetic.** The freeze, 2026-11-01 to 2027-01-05, is read as inclusive, which gives 66 days. End of v8 security support (2026-11-12) to the end of the freeze is 54 days. Working days are Monday to Friday, so 2026-10-26 to 2026-10-30 is 5.
- **Restore time against history.** RTO of 4 hours is 240 minutes; the longest Q3 record is 78 minutes; 240 / 78 = 3.08, quoted as 3.1.
- **Limits.** Nothing was checked against live systems or code: the inventory, staging results and incident log are taken as supplied. The log predates the upgrade, so it says nothing about how v10 changes any failure mode.
- **Choice made on the dependency map.** Labelling all 16 edges "depends on" was tried and dropped: every edge means the same thing, the 10 pt labels were unreadable at 800 px width, and two labels overlapped. The legend inside the picture states the relation once.

## E3 Claim register

*Supports every claim in [report.md](report.md): where it comes from and how firm it is.*

Types: **stated** = said in a source file; **derived** = computed from source data by `analyze.py`; **inferred** = judgment from stated facts; **assumed** = not known, assumed so the plan can be written; **proposed** = the recommendation itself.

| ID | Claim | Used in | Source | Type |
|---|---|---|---|---|
| C1 | v8 reaches end of security support on 2026-11-12; no CVE patches afterwards unless extended support is bought | panel, 3, 4 | notes L7 | stated |
| C2 | Freeze 2026-11-01 to 2027-01-05; only P1 hotfixes deploy; anything else needs a CAB exception | panel, 1, 3, 4 | notes L8 | stated |
| C3 | 7 of 9 services pass staging; `auth-service` fails 2 of 148 integration tests (token refresh flow, on the shim, root cause not confirmed); `user-store` was not tested, has no staging environment, and building one takes about a week | panel, 1 | notes L21-L23; `services.csv` staging_result | stated |
| C4 | The 7 passing services roll back by redeploying the previous version in 10 to 15 minutes; `auth-service` and `user-store` have no rollback path, recovery is a restore from backup, RTO about 4 hours | panel, 1, 3 | notes L27-L28; `services.csv` rollback_path | stated |
| C5 | IdentityModel 6.0 is promised "by end of November" but not committed; until then `auth-service` would run on a compatibility shim | panel, 1, 4, 5 | notes L16 | stated |
| C6 | The `user-store` database driver changes the schema migration format; migrations are one-way after the upgrade | 1 | notes L17 | stated |
| C7 | Extended support: 18,000 USD per quarter, security patches only, order by 2026-11-05 to be active on 2026-11-12 | panel, 3, 4 | notes L32 | stated |
| C8 | A CAB exception during the freeze is possible only for work already staged and tested | 3, 4 | notes L33 | stated |
| C9 | The Identity team has 2 engineers; one is on leave 2026-10-26 to 2026-11-13 | 1, 3 | notes L34 | stated |
| C10 | The Data team can upgrade `catalog-service`, `share-service`, `map-service` and `search-index` in one week if it starts Monday 2026-10-26 | 3, 4 | notes L35, L40 | stated |
| C11 | Platform: `gateway` should go last among the passing services | 3, 4 | notes L41 | stated |
| C12 | Integration: `connector-service` is low risk and can go any time | 3 | notes L42 | stated |
| C13 | Identity would rather not touch `auth-service` until the vendor library is out | 3 | notes L39 | stated |
| C14 | Staging passed for the custom JSON converters (`connector-service`, `share-service`) and for `gateway`'s custom retry policy | 1 | notes L14-L15 | stated |
| C15 | 16 dependency edges; `auth-service` has 6 direct dependents (every service except `user-store` and `search-index`); `user-store` has 7 dependents, direct or indirect | panel, map, 1 | `services.csv` depends_on; E6 | derived |
| C16 | `catalog-service` and `map-service` list each other in `depends_on`; each logged one Q3 incident blaming the other (2026-09-08, 2026-09-19) | map, 4 | `services.csv`; E5 | derived |
| C17 | 36 incident records, 35 distinct incidents, 932 record-minutes | 2 | `incidents-q3.csv`; E2, E4 | derived |
| C18 | `auth-service` logged 11 records, 380 minutes (1 SEV1, 6 SEV2, 4 SEV3); 3 further `gateway` incidents name `auth-service` in their summaries; together 14 of 35 distinct incidents (40%) involve it | panel, 2 | `incidents-q3.csv`; E2, E4 | derived |
| C19 | On 2026-07-11 logins failed for 78 minutes and `gateway` returned 503 on every authenticated route; the only SEV1 outage of the quarter | 2 | `incidents-q3.csv`; E5 | stated and derived |
| C20 | `auth-service` causes: token-validation timeout 5, token-refresh bug 3, config 2, runtime GC 1 | 2 | `incidents-q3.csv`; E4 | derived |
| C21 | All 5 failed rollouts in the seven services were rolled back within 10 to 19 minutes | 1 | `incidents-q3.csv` (cause = deploy); E5 | derived |
| C22 | A 4-hour restore is 3.1 times the longest Q3 record (78 minutes) | panel, 2 | C4, C17; E2 | derived |
| C23 | 5 working days between the decision (Fri 2026-10-23) and the freeze (Sun 2026-11-01): Mon 26 to Fri 30 Oct | panel, 4 | E7 | derived |
| C24 | 54 days from end of v8 security support to end of the freeze; the freeze lasts 66 days | panel, 3 | E7 | derived |
| C25 | The 3 token-refresh incidents and the 2 failing staging tests are related; the refresh flow is already fragile | 2 | `incidents-q3.csv`; notes L22 | inferred |
| C26 | The seven services' staging runs may have used a v10 `auth-service`, so the v10-to-v8 mix is untested | panel, 4, 5 | notes L22 says only that `auth-service` ran on the shim | inferred |
| C27 | Rolling back an upgraded service in the freeze may need a CAB exception, because only P1 hotfixes deploy | panel, 4, 5 | C2, C4 | inferred |
| C28 | Fri 2026-10-23 is the last day that lets the Data team start on Monday 2026-10-26 and finish before the freeze | panel | C10; E7 | inferred |
| C29 | Extended support is a flat price for any number of services, and a quarter runs 3 months from 2026-11-12 | 3, 4, 5 | none | assumed |
| C30 | Staging work and testing may continue during the freeze | 4, 5 | none | assumed |
| C31 | Smaller assumptions listed in section 5: 5 Jan is the last frozen day; working days are Monday to Friday and the Data team's "one week" means 26 to 30 Oct; `services.csv` is complete and current and the staging results still hold; incident causes follow each summary; Platform can rerun the staging suites | 4, 5 | none | assumed |
| C32 | The split plan, the order of the seven, the two checks, the Identity preparation window, and the 🟡 verdict | all | none | proposed |

## E4 Incidents by service

*Supports [section 2](report.md#2-auth-service-is-also-the-weak-point-in-production): Q3 2026, 2026-07-02 to 2026-09-28, counted by record.*

| Service | Records | SEV1 | SEV2 | SEV3 | Minutes | Causes |
|---|---|---|---|---|---|---|
| auth-service | 11 | 1 | 6 | 4 | 380 | token-validation-timeout x5, token-refresh-bug x3, config x2, runtime-gc x1 |
| gateway | 7 | 1 | 1 | 5 | 178 | downstream-timeout x5, config x2 |
| catalog-service | 5 | 0 | 1 | 4 | 124 | dependency x2, config x1, deploy x1, runtime-gc x1 |
| share-service | 4 | 0 | 1 | 3 | 84 | deploy x2, dependency x1, downstream-timeout x1 |
| connector-service | 3 | 0 | 0 | 3 | 72 | dependency x2, deploy x1 |
| map-service | 2 | 0 | 0 | 2 | 26 | dependency x1, deploy x1 |
| notify-service | 2 | 0 | 0 | 2 | 17 | queue-backlog x2 |
| user-store | 1 | 0 | 1 | 0 | 33 | config x1 |
| search-index | 1 | 0 | 0 | 1 | 18 | runtime-gc x1 |
| **Total** | **36** | **2** | **10** | **24** | **932** | |

The other eight services together: 25 records, 1 SEV1 (the `gateway` side of the 2026-07-11 outage), 4 SEV2, 20 SEV3.

## E5 Incident records cited in the report

*Supports [section 2](report.md#2-auth-service-is-also-the-weak-point-in-production) and the rollback claim in [section 1](report.md#1-seven-services-are-ready-and-the-two-identity-services-are-not). Summaries are verbatim from `incidents-q3.csv`.*

| Date | Service | Severity | Minutes | Cause | Summary | Cited for |
|---|---|---|---|---|---|---|
| 2026-07-11 | auth-service | SEV1 | 78 | token-validation-timeout | Login failures for 78 minutes after cache eviction storm | the quarter's only SEV1 outage |
| 2026-07-11 | gateway | SEV1 | 78 | downstream-timeout | Gateway returned 503 for all authenticated routes (caused by auth-service SEV1) | same outage seen from `gateway`; counted once |
| 2026-07-05 | gateway | SEV3 | 12 | downstream-timeout | Gateway 504s while auth-service slow | gateway incident naming `auth-service` |
| 2026-08-27 | gateway | SEV3 | 13 | downstream-timeout | 504s while auth-service cache warmed | gateway incident naming `auth-service` |
| 2026-09-15 | gateway | SEV2 | 36 | downstream-timeout | 504s traced to auth-service latency | gateway incident naming `auth-service` |
| 2026-07-21 | auth-service | SEV2 | 41 | token-refresh-bug | Refresh tokens rejected after clock skew on one node | token-refresh pattern |
| 2026-08-14 | auth-service | SEV3 | 19 | token-refresh-bug | Refresh token reuse detection false positives | token-refresh pattern |
| 2026-09-28 | auth-service | SEV3 | 12 | token-refresh-bug | Intermittent refresh failures after deploy | token-refresh pattern |
| 2026-07-14 | share-service | SEV3 | 15 | deploy | Failed rollout; rolled back within 15 minutes | rollback in practice |
| 2026-08-03 | map-service | SEV3 | 14 | deploy | Failed rollout; rolled back within 14 minutes | rollback in practice |
| 2026-08-29 | share-service | SEV3 | 10 | deploy | Failed rollout; rolled back within 10 minutes | rollback in practice |
| 2026-09-17 | connector-service | SEV3 | 19 | deploy | Failed rollout; rolled back within 19 minutes | rollback in practice; longest, above the 10 to 15 minute estimate |
| 2026-09-27 | catalog-service | SEV3 | 15 | deploy | Failed rollout; rolled back within 15 minutes | rollback in practice |
| 2026-09-08 | catalog-service | SEV3 | 21 | dependency | Map-service latency slowed dataset detail pages | `catalog-service` and `map-service` depend on each other |
| 2026-09-19 | map-service | SEV3 | 12 | dependency | Catalog-service latency caused timeouts | `catalog-service` and `map-service` depend on each other |
| 2026-08-19 | catalog-service | SEV3 | 16 | runtime-gc | GC pauses on large dataset listing | GC-pause incidents (3 in Q3) |
| 2026-09-02 | auth-service | SEV2 | 48 | runtime-gc | Long GC pauses blocked token endpoint | GC-pause incidents (3 in Q3) |
| 2026-09-26 | search-index | SEV3 | 18 | runtime-gc | Index rebuild paused by GC | GC-pause incidents (3 in Q3) |

## E6 Dependency analysis

*Supports [section 1](report.md#1-seven-services-are-ready-and-the-two-identity-services-are-not) and the dependency map. The edge list is in block C of the report.*

| Service | Direct dependents | Who | Direct or indirect dependents |
|---|---|---|---|
| auth-service | 6 | catalog-service, connector-service, gateway, map-service, notify-service, share-service | 6 |
| catalog-service | 4 | connector-service, gateway, map-service, share-service | 4 |
| user-store | 1 | auth-service | 7 |
| share-service | 1 | gateway | 1 |
| connector-service | 1 | gateway | 1 |
| map-service | 1 | catalog-service | 4 |
| search-index | 1 | catalog-service | 5 |
| notify-service | 1 | share-service | 2 |
| gateway | 0 | none | 0 |

- `auth-service` is depended on by every service except `user-store` (its own dependency) and `search-index`. Six of the seven passing services call it; `search-index` is the exception.
- `catalog-service` and `map-service` list each other: a dependency cycle, so they have no safe one-before-the-other order and are best upgraded together.
- `user-store` has 7 direct or indirect dependents, which is 7 of the other 8 services.

## E7 Calendar

*Supports [section 4](report.md#4-the-plan-puts-seven-services-in-the-26-to-30-october-window-and-two-in-january) and `report.assets/timeline.png`, which draws these dates.*

| Date | Day | Event | Source |
|---|---|---|---|
| 2026-10-14 | Wed | Platform team writes the notes | notes L3 |
| 2026-10-17 | Sat | This report is written | none |
| 2026-10-23 | Fri | Decision due | notes L3 |
| 2026-10-26 | Mon | Data team can start; one Identity engineer's leave begins | notes L34, L35 |
| 2026-10-30 | Fri | Last working day before the freeze | derived |
| 2026-11-01 | Sun | Freeze begins | notes L8 |
| 2026-11-05 | Thu | Last day to order extended support | notes L32 |
| 2026-11-12 | Thu | v8 end of security support; extended support must be active | notes L7, L32 |
| 2026-11-13 | Fri | Identity engineer's leave ends | notes L34 |
| 2026-11-16 | Mon | Proposed start of Identity preparation work | proposed |
| 2026-11-30 | Mon | "End of November": vendor promise for IdentityModel 6.0, not committed | notes L16 |
| 2027-01-05 | Tue | Freeze ends | notes L8 |
| about 2027-02-12 | Fri | End of one extended-support quarter, if it runs 3 months from 2026-11-12 | assumed |

Derived: 5 working days from 2026-10-26 to 2026-10-30; 66 days of freeze; 54 days from 2026-11-12 to 2027-01-05; the leave overlaps the freeze by 13 days (2026-11-01 to 2026-11-13).

<!-- zone:ai-input -->
## E8 Reproduce

*Supports the "every number is reproduced" claim: commands and expected output.*

Run from the folder that holds `report.md`. Versions used: Python 3.12.7, matplotlib 3.9.2, Graphviz 14.1.3.

```text
python report.assets/analyze.py
dot -Tpng -Gdpi=150 report.assets/overview.dot -o report.assets/overview.png
python report.assets/timeline.py
```

- `analyze.py` prints the derived tables, then 23 lines beginning `ok`, and exits with code 0. Any `FAIL` line means a number in the report no longer matches the data.
- `overview.png` renders at 1765 x 1068 px and `timeline.png` at 1653 x 1135 px; both are meant to be read at about 800 px width.
