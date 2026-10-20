<!-- zone:archive -->
# Evidence for the runtime upgrade assessment (v8 to v10)

*🗄️ Archive - the supporting data behind [report.md](report.md), kept as the audit trail for the decision. Nothing here is needed to decide; it exists so every number in the report can be checked. Data as of the Platform team's notes of 2026-10-14 and the incidents of Q3 2026.*

Contents: [Sources and integrity](#sources-and-integrity) · [Claim traceability](#claim-traceability) · [Service inventory](#service-inventory) · [Dependency edges](#dependency-edges) · [Incident log](#incident-log) · [Incident statistics](#incident-statistics) · [Date checks](#date-checks) · [Method and interpretation choices](#method-and-interpretation-choices)

## Sources and integrity

*🗄️ Archive - the three inputs, copied without editing; supports every number in the report.*

| File | What it is | Size | SHA-256 |
|---|---|---|---|
| [report.data/upgrade-notes.md](report.data/upgrade-notes.md) | Platform team's notes for the decision, written 2026-10-14 | 2,886 bytes | `aad08996cde2677599234aa09a00c877e875e9e444f1a1122958e908b6abd735` |
| [report.data/services.csv](report.data/services.csv) | The nine services: team, criticality, dependencies, rollback path, staging result | 9 rows, 732 bytes | `8573da3565d6e080d4aee06cc0469a06e5ef6d1dde0b20ffed93bdf4d937a3cc` |
| [report.data/incidents-q3.csv](report.data/incidents-q3.csv) | Incidents from 2026-07-02 to 2026-09-28 | 36 rows, 3,279 bytes | `2600694c932efbee7c02eda5bf4e89474835c1f3d3d579338cbdbfbaf62b64c4` |

Copied on 2026-10-17 from the input folder supplied with the request, byte for byte. Do not edit them: they are the baseline of the audit trail. To verify, run one of these from the folder that contains `report.md` and compare with the hashes above:

```powershell
Get-FileHash -Algorithm SHA256 report.data/*
```

```bash
sha256sum report.data/*
```

## Claim traceability

*🗄️ Archive - where each headline number in the report comes from and how it was derived; supports every section of the report.*

| Claim in the report | Where | Source | How derived |
|---|---|---|---|
| 7 of 9 services passed staging | panel, [1](report.md#1-seven-of-nine-services-are-ready-and-two-are-not) | notes ("Staging results"); services.csv `staging_result` | Seven rows say `pass`; auth-service says `fail (2 of 148 integration tests)`; user-store says `not tested (no staging environment)` |
| The seven roll back in 10 to 15 minutes | panel, [1](report.md#1-seven-of-nine-services-are-ready-and-two-are-not) | notes ("Rollback"); services.csv `rollback_path` = yes for the seven | Quoted from the notes. Supported, not proven, by the 5 Q3 rollbacks (Method, item 4) |
| auth-service and user-store have no rollback; recovery from backup is estimated at 4 hours | panel, [2](report.md#2-auth-service-and-user-store-must-wait-for-january) | notes ("Rollback"); services.csv `rollback_path` = no | Quoted. The notes call the 4 hours an RTO estimate |
| Six services depend directly on auth-service | panel, [1](report.md#1-seven-of-nine-services-are-ready-and-two-are-not) | services.csv `depends_on` | Rows listing auth-service: gateway, catalog-service, share-service, connector-service, map-service, notify-service |
| A failure in user-store can reach seven of the other eight services | [1](report.md#1-seven-of-nine-services-are-ready-and-two-are-not) | services.csv | auth-service depends on user-store, and the six services above depend on auth-service; only search-index does not. Counts dependency, not observed failure spread |
| The two v10 changes that hit the seven passed staging; the two that hit the Identity pair did not | [1](report.md#1-seven-of-nine-services-are-ready-and-two-are-not) | notes ("What the upgrade changes", items 1 to 4; "Staging results") | Each named change is matched to the service the notes name for it: JSON converters (connector-service, share-service) and gateway retry policy passed; IdentityModel on a shim (auth-service) failed 2 of 148 tests; the one-way migration (user-store) is untested. "None named" means the notes name no change for that service, not that none applies |
| catalog-service and map-service depend on each other; catalog-service has four dependents | [1](report.md#1-seven-of-nine-services-are-ready-and-two-are-not), [5](report.md#5-the-seven-fit-before-the-freeze-with-no-slack) | services.csv | Each lists the other in `depends_on`; gateway, share-service, connector-service and map-service list catalog-service |
| auth-service had 11 of 36 incident records | [3](report.md#3-q3-incidents-point-the-same-way) | incidents-q3.csv | Row count by `service` (Incident statistics) |
| 7 of the 11 SEV1 or SEV2 events started in auth-service | [3](report.md#3-q3-incidents-point-the-same-way) | incidents-q3.csv | 12 SEV1 or SEV2 rows; rows 4 and 5 are one event, so 11 events; auth-service has 1 SEV1 and 6 SEV2 |
| 4 of the gateway's 7 incidents name auth-service | [3](report.md#3-q3-incidents-point-the-same-way) | incidents-q3.csv `summary` | Rows 2, 5, 21 and 28; judged from the summary text |
| Token refresh bugs caused 3 of auth-service's 11 incidents | [2](report.md#2-auth-service-and-user-store-must-wait-for-january), [3](report.md#3-q3-incidents-point-the-same-way) | incidents-q3.csv `cause` | Rows 8, 17 and 36 |
| 3 of 36 incidents were GC pauses | [3](report.md#3-q3-incidents-point-the-same-way) | incidents-q3.csv `cause` = runtime-gc | Rows 18 (catalog-service), 23 (auth-service), 34 (search-index) |
| 5 failed rollouts were rolled back in 10 to 19 minutes, 4 of them within 15 | [3](report.md#3-q3-incidents-point-the-same-way) | incidents-q3.csv `cause` = deploy | Rows 6, 13, 22, 29, 35: 15, 14, 10, 19, 15 minutes |
| 4 hours is about three times the longest Q3 incident | [2](report.md#2-auth-service-and-user-store-must-wait-for-january) | notes (4 hours); incidents-q3.csv row 4 (78 minutes) | 240 / 78 = 3.08. Compares an estimate with an observed outage |
| Data's week ends Fri 2026-10-30, the last working day before the freeze | [5](report.md#5-the-seven-fit-before-the-freeze-with-no-slack) | notes (start Monday 2026-10-26, one week; freeze from 2026-11-01) | Calendar (Date checks). Assumes a Monday-to-Friday week |
| v8 is unpatched for 54 days if the Identity pair moves on the day the freeze ends | [4](report.md#4-the-split-costs-no-more-than-waiting) | notes | 2026-11-12 to 2027-01-05 is 54 days; longer if the move slips, shorter if a CAB exception allows an earlier move |
| A CAB exception covers only work already staged and tested | [2](report.md#2-auth-service-and-user-store-must-wait-for-january), [4](report.md#4-the-split-costs-no-more-than-waiting) | notes ("Costs and options") | Quoted. That the Identity pair could qualify later in the freeze, and that January is the realistic date, are inferences |
| Identity has two engineers, one on leave from 2026-10-26 to 2026-11-13 | [2](report.md#2-auth-service-and-user-store-must-wait-for-january) | notes ("Costs and options") | Quoted |
| IdentityModel 6.0 is promised "by end of November" but not committed | [2](report.md#2-auth-service-and-user-store-must-wait-for-january), [6](report.md#6-five-unknowns-could-change-the-call) | notes ("What the upgrade changes", item 3) | Quoted |
| The seven's staging results are 86 days old on 2027-01-05 | [4](report.md#4-the-split-costs-no-more-than-waiting) | notes (staging 2026-10-09 to 2026-10-11) | 2026-10-11 to 2027-01-05 |
| Extended support is 18,000 USD a quarter and must be ordered by 2026-11-05 | panel, [4](report.md#4-the-split-costs-no-more-than-waiting) | notes ("Costs and options") | Quoted. "A flat price for the whole v8 estate" and "a quarter runs from 2026-11-12" are assumptions, not in the notes |

## Service inventory

*🗄️ Archive - services.csv in full, plus one derived column; supports [section 1](report.md#1-seven-of-nine-services-are-ready-and-two-are-not).*

| Service | Team | Criticality | Runtime | Depends on | Depended on by (derived) | Rollback path | Staging result |
|---|---|---|---|---|---|---|---|
| gateway | Platform | critical | v8 | auth-service, catalog-service, share-service, connector-service | 0 | yes | pass |
| auth-service | Identity | critical | v8 | user-store | 6 | no | fail (2 of 148 integration tests) |
| user-store | Identity | critical | v8 | - | 1 | no | not tested (no staging environment) |
| catalog-service | Data | high | v8 | auth-service, search-index, map-service | 4 | yes | pass |
| share-service | Data | high | v8 | auth-service, catalog-service, notify-service | 1 | yes | pass |
| connector-service | Integration | medium | v8 | auth-service, catalog-service | 1 | yes | pass |
| map-service | Data | medium | v8 | auth-service, catalog-service | 1 | yes | pass |
| search-index | Data | medium | v8 | - | 1 | yes | pass |
| notify-service | Platform | low | v8 | auth-service | 1 | yes | pass |

## Dependency edges

*🗄️ Archive - the text equivalent of the dependency map in the glance panel (source: [dependency-map.dot](report.assets/dependency-map.dot)); supports [section 1](report.md#1-seven-of-nine-services-are-ready-and-two-are-not).*

All 16 edges are read from the `depends_on` column of services.csv; none is inferred. Edges 8 and 15 are the same pair in both directions and are drawn as one two-way orange arrow.

| # | From | Relation | To | Verified? |
|---|---|---|---|---|
| 1 | gateway | depends on | auth-service | yes, services.csv |
| 2 | gateway | depends on | catalog-service | yes, services.csv |
| 3 | gateway | depends on | share-service | yes, services.csv |
| 4 | gateway | depends on | connector-service | yes, services.csv |
| 5 | auth-service | depends on | user-store | yes, services.csv |
| 6 | catalog-service | depends on | auth-service | yes, services.csv |
| 7 | catalog-service | depends on | search-index | yes, services.csv |
| 8 | catalog-service | depends on | map-service | yes, services.csv |
| 9 | share-service | depends on | auth-service | yes, services.csv |
| 10 | share-service | depends on | catalog-service | yes, services.csv |
| 11 | share-service | depends on | notify-service | yes, services.csv |
| 12 | connector-service | depends on | auth-service | yes, services.csv |
| 13 | connector-service | depends on | catalog-service | yes, services.csv |
| 14 | map-service | depends on | auth-service | yes, services.csv |
| 15 | map-service | depends on | catalog-service | yes, services.csv |
| 16 | notify-service | depends on | auth-service | yes, services.csv |

## Incident log

*🗄️ Archive - incidents-q3.csv in full (36 records, in file order) with one added Note column; supports [section 3](report.md#3-q3-incidents-point-the-same-way).*

| # | Date | Service | Severity | Minutes | Cause | Summary | Note |
|---|---|---|---|---|---|---|---|
| 1 | 2026-07-02 | auth-service | SEV2 | 34 | token-validation-timeout | Token validation p99 above 5s during morning peak |  |
| 2 | 2026-07-05 | gateway | SEV3 | 12 | downstream-timeout | Gateway 504s while auth-service slow | summary names auth-service |
| 3 | 2026-07-09 | catalog-service | SEV3 | 20 | config | Wrong connection string after config rollout |  |
| 4 | 2026-07-11 | auth-service | SEV1 | 78 | token-validation-timeout | Login failures for 78 minutes after cache eviction storm |  |
| 5 | 2026-07-11 | gateway | SEV1 | 78 | downstream-timeout | Gateway returned 503 for all authenticated routes (caused by auth-service SEV1) | summary names auth-service; same event as row 4, counted once in event totals |
| 6 | 2026-07-14 | share-service | SEV3 | 15 | deploy | Failed rollout; rolled back within 15 minutes | rollback evidence |
| 7 | 2026-07-18 | connector-service | SEV3 | 25 | dependency | Upstream partner API schema change |  |
| 8 | 2026-07-21 | auth-service | SEV2 | 41 | token-refresh-bug | Refresh tokens rejected after clock skew on one node |  |
| 9 | 2026-07-23 | notify-service | SEV3 | 9 | queue-backlog | Notification queue backlog after batch share |  |
| 10 | 2026-07-25 | catalog-service | SEV2 | 52 | dependency | Search index lag made catalog listings stale |  |
| 11 | 2026-07-29 | gateway | SEV3 | 18 | downstream-timeout | Intermittent 504s from share-service |  |
| 12 | 2026-08-01 | auth-service | SEV3 | 22 | config | Signing key rotated before dependents refreshed |  |
| 13 | 2026-08-03 | map-service | SEV3 | 14 | deploy | Failed rollout; rolled back within 14 minutes | rollback evidence |
| 14 | 2026-08-06 | auth-service | SEV2 | 37 | token-validation-timeout | Token validation timeouts under load test traffic |  |
| 15 | 2026-08-08 | share-service | SEV2 | 45 | dependency | Catalog latency stalled share creation |  |
| 16 | 2026-08-12 | gateway | SEV3 | 11 | config | Rate-limit rule misconfigured for one tenant |  |
| 17 | 2026-08-14 | auth-service | SEV3 | 19 | token-refresh-bug | Refresh token reuse detection false positives |  |
| 18 | 2026-08-19 | catalog-service | SEV3 | 16 | runtime-gc | GC pauses on large dataset listing |  |
| 19 | 2026-08-21 | connector-service | SEV3 | 28 | dependency | Partner API throttling |  |
| 20 | 2026-08-24 | auth-service | SEV2 | 29 | token-validation-timeout | Cache miss storm after deploy |  |
| 21 | 2026-08-27 | gateway | SEV3 | 13 | downstream-timeout | 504s while auth-service cache warmed | summary names auth-service |
| 22 | 2026-08-29 | share-service | SEV3 | 10 | deploy | Failed rollout; rolled back within 10 minutes | rollback evidence |
| 23 | 2026-09-02 | auth-service | SEV2 | 48 | runtime-gc | Long GC pauses blocked token endpoint |  |
| 24 | 2026-09-04 | user-store | SEV2 | 33 | config | Connection pool exhausted after pool size change |  |
| 25 | 2026-09-08 | catalog-service | SEV3 | 21 | dependency | Map-service latency slowed dataset detail pages |  |
| 26 | 2026-09-10 | notify-service | SEV3 | 8 | queue-backlog | Retry storm after provider outage |  |
| 27 | 2026-09-12 | auth-service | SEV3 | 17 | config | Wrong audience setting in one environment |  |
| 28 | 2026-09-15 | gateway | SEV2 | 36 | downstream-timeout | 504s traced to auth-service latency | summary names auth-service |
| 29 | 2026-09-17 | connector-service | SEV3 | 19 | deploy | Failed rollout; rolled back within 19 minutes | rollback evidence |
| 30 | 2026-09-19 | map-service | SEV3 | 12 | dependency | Catalog-service latency caused timeouts |  |
| 31 | 2026-09-22 | share-service | SEV3 | 14 | downstream-timeout | Timeout calling notify-service |  |
| 32 | 2026-09-24 | auth-service | SEV2 | 43 | token-validation-timeout | Token validation timeouts during onboarding batch |  |
| 33 | 2026-09-25 | gateway | SEV3 | 10 | config | Wrong upstream URL after environment swap |  |
| 34 | 2026-09-26 | search-index | SEV3 | 18 | runtime-gc | Index rebuild paused by GC |  |
| 35 | 2026-09-27 | catalog-service | SEV3 | 15 | deploy | Failed rollout; rolled back within 15 minutes | rollback evidence |
| 36 | 2026-09-28 | auth-service | SEV3 | 12 | token-refresh-bug | Intermittent refresh failures after deploy |  |

## Incident statistics

*🗄️ Archive - the counts used in [section 3](report.md#3-q3-incidents-point-the-same-way); reproduce them with `python report.assets/incidents.py` (see [report.assets/incidents.py](report.assets/incidents.py)).*

Per service (36 records, 932 row-minutes):

| Service | Records | SEV1 | SEV2 | SEV3 | Minutes | Causes |
|---|---|---|---|---|---|---|
| auth-service | 11 | 1 | 6 | 4 | 380 | token-validation-timeout 5, token-refresh-bug 3, config 2, runtime-gc 1 |
| gateway | 7 | 1 | 1 | 5 | 178 | downstream-timeout 5, config 2 |
| catalog-service | 5 | 0 | 1 | 4 | 124 | dependency 2, config 1, deploy 1, runtime-gc 1 |
| share-service | 4 | 0 | 1 | 3 | 84 | deploy 2, dependency 1, downstream-timeout 1 |
| connector-service | 3 | 0 | 0 | 3 | 72 | dependency 2, deploy 1 |
| map-service | 2 | 0 | 0 | 2 | 26 | dependency 1, deploy 1 |
| notify-service | 2 | 0 | 0 | 2 | 17 | queue-backlog 2 |
| search-index | 1 | 0 | 0 | 1 | 18 | runtime-gc 1 |
| user-store | 1 | 0 | 1 | 0 | 33 | config 1 |
| Total | 36 | 2 | 10 | 24 | 932 |  |

After counting the 2026-07-11 outage once (rows 4 and 5): 35 distinct events, of which 11 are SEV1 or SEV2, and 854 incident-minutes.

Per cause:

| Cause | Records | Services |
|---|---|---|
| config | 6 | auth-service 2, gateway 2, catalog-service, user-store |
| dependency | 6 | catalog-service 2, connector-service 2, map-service, share-service |
| downstream-timeout | 6 | gateway 5, share-service |
| deploy | 5 | share-service 2, catalog-service, connector-service, map-service |
| token-validation-timeout | 5 | auth-service 5 |
| runtime-gc | 3 | auth-service, catalog-service, search-index |
| token-refresh-bug | 3 | auth-service 3 |
| queue-backlog | 2 | notify-service 2 |

## Date checks

*🗄️ Archive - the calendar arithmetic behind the schedule claims in [section 4](report.md#4-the-split-costs-no-more-than-waiting) and [section 5](report.md#5-the-seven-fit-before-the-freeze-with-no-slack).*

| Date | Weekday | What happens (source) |
|---|---|---|
| 2026-10-09 to 2026-10-11 | Friday to Sunday | Staging runs (notes) |
| 2026-10-14 | Wednesday | Notes written (notes) |
| 2026-10-17 | Saturday | This report is drafted |
| 2026-10-23 | Friday | Decision due (notes) |
| 2026-10-26 | Monday | Data team would start; Identity engineer's leave begins (notes) |
| 2026-10-30 | Friday | End of the Data team's five working days; last working day before the freeze (derived) |
| 2026-11-01 | Sunday | Freeze starts (notes) |
| 2026-11-05 | Thursday | Last day to order extended support (notes) |
| 2026-11-12 | Thursday | v8 security support ends (notes) |
| 2026-11-13 | Friday | Last day of the Identity engineer's leave (notes) |
| 2026-11-30 | Monday | End of November: vendor library 6.0 promised, not committed (notes) |
| 2027-01-05 | Tuesday | Freeze ends (notes) |

Intervals: 2026-11-12 to 2027-01-05 is 54 days; 2026-11-01 to 2027-01-05 is 65 days (the freeze); 2026-10-11 to 2027-01-05 is 86 days.

## Method and interpretation choices

*🗄️ Archive - how the data was read, so the numbers can be challenged; supports every section of the report.*

1. **One event counted once.** Rows 4 and 5 (2026-07-11) have the same date, severity and duration, and the gateway row says "caused by auth-service SEV1". They are one event in event totals and two rows in per-service counts, because both services were affected.
2. **Severe means SEV1 or SEV2.** That is 12 rows and 11 distinct events; 7 of the events started in auth-service (1 SEV1, 6 SEV2).
3. **Gateway incidents linked to auth-service** are judged from the summary text only: rows 2, 5, 21 and 28. Row 11 names share-service; rows 16 and 33 are configuration errors. Other incidents may have links the summaries do not state.
4. **Rollback evidence** is every incident with cause `deploy` (rows 6, 13, 22, 29, 35); each summary states the time to roll back (15, 14, 10, 19 and 15 minutes). These are ordinary deploys, not runtime upgrades, so they support the 10 to 15 minute estimate without proving it.
5. **Dependents** are direct and counted from `depends_on`. Indirect dependents are used only where the report says so.
6. **Labels coined in the report:** "the seven" (the services that passed staging), "the Identity pair" (auth-service and user-store), "the split plan" (the seven now, the pair in January) and "mixed-version check" (a staging run with the seven on v10 and the pair on v8).
7. **Not done:** no staging re-run, no contact with the vendor, no access to code or production, no sources beyond the three files. The report is a reading of those files.
8. **Considered and dropped:** quoting auth-service's staging pass rate (146 of 148 tests), because it hides that both failures sit in the token refresh flow; presenting extended support as avoidable under the split plan, because the Identity pair stays on v8 after 2026-11-12 under both options.
9. **Assumptions** (also marked where they matter in the report): extended support is a flat 18,000 USD for the whole v8 estate and one quarter runs from 2026-11-12 to about 2027-02-12; the Data team's week is Monday to Friday; the freeze limits production deployments only, not staging work; Marcus Hale can approve the spend.
