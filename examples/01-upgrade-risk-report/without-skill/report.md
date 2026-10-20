# Runtime upgrade v8 → v10: risk assessment and recommendation

- **For:** Marcus Hale, Engineering Lead (decision owner)
- **Decision needed by:** Friday 2026-10-23
- **Prepared:** 2026-10-17 · version 1.0 · status: awaiting decision (record the outcome in Section 7)
- **Based on:** the Platform team's upgrade notes (2026-10-14; staging runs 2026-10-09 to 2026-10-11), the service inventory, and the Q3 2026 incident log (2026-07-02 to 2026-09-28). Verbatim copies are in [`evidence/source/`](evidence/source/). Appendix A explains how each derived number was calculated.
- **Reading guide:** Sections 1 and 2 are enough to decide. Sections 3 to 6 hold the evidence, plan, risks and open questions. Section 7 records the outcome.

## 1. Recommendation

**Split the upgrade (Option C).** Move the seven services that passed staging to v10 before the code freeze starts on Sunday 2026-11-01. Keep auth-service and user-store on v8 until January, and order one quarter of v8 extended support ($18,000) to cover them. Upgrading everything before the freeze is not realistic, and deferring everything to January gives up a workable window for no saving on extended support (assuming a flat price).

**Why**

1. **The two services that are not ready are the ones nearly everything depends on.** auth-service is called directly by 6 of the other 8 services, and 7 of the 8 depend on user-store beneath it. user-store has not been tested on v10 (no staging environment). auth-service fails 2 of 148 integration tests on the compatibility shim, cause unconfirmed.
2. **Neither can be rolled back.** Recovery after the one-way migration is a restore from backup, estimated at 4 hours, about three times the longest incident of last quarter (78 minutes).
3. **They cannot be ready before the freeze.** The vendor's v10-compatible identity library (6.0) is promised "by end of November" but not committed, and one of Identity's two engineers is on leave from 2026-10-26 to 2026-11-13.
4. **The other seven have a fast exit.** Rollback is a redeploy of the previous version, 10–15 minutes. Last quarter's five failed rollouts (all SEV3) were rolled back in 10–19 minutes.
5. **Deferring everything does not reduce the bill.** Extended support is needed for auth-service and user-store either way (Open question 3 covers the price assumption). Deferring the seven as well leaves nine services for January and loses the Data team's window.

**Decisions needed by Friday 2026-10-23**

1. Approve Option C.
2. Approve $18,000 for one quarter of v8 extended support, which both B and C need. It must be ordered by Thursday 2026-11-05 to be active on 2026-11-12. Submit it in the week of 2026-10-26, not at the deadline; the notes give no processing lead time.
3. Tell the Data team to start on Monday 2026-10-26. They need all five working days, to Friday 2026-10-30. If the decision slips past Friday, their last service lands inside the freeze and needs a CAB exception.
4. Ask the change advisory board (CAB) how it would treat a slipped deploy, or a rollback or fix of a v10 service, during the freeze (Section 4.3).

**Two gates before the first production deploy on 2026-10-26.** If either cannot be met, fall back to Option B.

- **Gate 1, mixed-version check.** Platform confirms the seven staging passes were run the way production will look: v10 services calling auth-service on v8. The notes do not say which auth-service version staging used. If it was something else, re-run the seven suites against auth-service on v8. Ideally this is answered before the decision.
- **Gate 2, team readiness.** The Data team confirms the 2026-10-26 start and that "one week" includes the production rollout. Platform and Integration confirm their slots (notify-service, gateway, connector-service); the notes give capacity only for the Data team.

## 2. Options

The notes pose a two-way choice: upgrade before the freeze, or defer to January. The evidence says the two hard services (auth-service and user-store) should not go before the freeze, so the real question is what happens to the seven that are ready.

| | A. Everything before the freeze | B. Everything in January | C. Split (recommended) |
|---|---|---|---|
| What happens | All nine services on v10 by Friday 2026-10-30 | No change before the freeze; upgrade after it ends on 2027-01-05 | Seven ready services on v10 by 2026-10-30; auth-service and user-store in January |
| Still on v8 after 2026-11-12 | None, if it works | All nine, for at least 54 days (to 2027-01-05; T1) | auth-service and user-store (plus gateway if it is deferred, Section 4.3) |
| v8 extended support (security patches only) | None planned; $18,000 if the Identity services have to be restored to v8 | $18,000 for one quarter; $36,000 if the January upgrade is not done by about 2027-02-12 (T6) | $18,000, the same as B (lower only if the price scales with the services still on v8; Open question 3) |
| If it goes wrong | The auth-service or user-store migration fails: no rollback, about 4 hours to restore from backup, "every login" down (Identity), and fixes limited to P1 hotfixes from 2026-11-01 | January overload: nine services plus a vendor-dependent auth-service in one window; extended support has to be renewed | A v10 problem in a ready service appears after 2026-11-01. Rollback takes 10–20 minutes, but only P1 hotfixes deploy in the freeze |
| What must be true | user-store tested (about a week to build an environment), the 2 failing tests fixed, the vendor library released, Identity at full strength | Nothing new | Gates 1 and 2; a CAB route for slips |
| Verdict | Not recommended: it needs untested, one-way changes to login by 2026-10-30 | Safe fallback | **Recommended** |

**Criteria used:** (1) no untested, one-way change to login before the freeze; (2) no unpatched critical service after 2026-11-12; (3) use the pre-freeze window and the Data team's availability for work that is ready; (4) a fast exit for everything that ships.

**C versus B.** C puts seven services on v10 before v8 support ends and leaves January with only the two hard services. It costs a compressed week with no slack, v10 running during the freeze when only P1 hotfixes ship, and mixed v8/v10 operation for at least nine weeks (2026-10-30 to 2027-01-05, 67 days; T7). B avoids those costs but moves the work, and the schedule risk, into January. The seven are ready, can be reversed in 10–20 minutes, and the window is open now, so the costs of C are manageable with the two gates and the swing rule in Section 4.3. B is the right choice if either gate cannot be met.

## 3. Evidence

Codes in brackets, such as (D1) or (I20), are rows of [`evidence/derived/key-figures.csv`](evidence/derived/key-figures.csv), which gives the calculation behind each number.

### 3.1 The risk is concentrated in two services

![Dependency map. Six services (gateway, share-service, connector-service, catalog-service, map-service, notify-service) call auth-service, which depends on user-store. search-index sits under catalog-service, and catalog-service and map-service depend on each other. Seven services are green: passed staging, rollback available. auth-service is red: 2 of 148 tests fail, no rollback. user-store is grey: not tested, no rollback.](figures/dependency-map.png)

*Figure 1. Dependencies and v10 readiness, built from `services.csv` by `evidence/analysis.py` (diagram source: `figures/dependency-map.dot`).*

Services that are not ready come first.

| Service | Owner · criticality | Staging (2026-10-09 to 10-11) | Rollback | Direct dependents | Q3 incidents (minutes) |
|---|---|---|---|---|---|
| auth-service | Identity · critical | **Fail:** 2 of 148 integration tests (token refresh, on the shim) | **No** | 6 | 11 (380) |
| user-store | Identity · critical | **Not tested:** no staging environment | **No** | 1 (7 services depend on it transitively) | 1 (33) |
| gateway | Platform · critical | Pass | Yes | 0 | 7 (178) |
| catalog-service | Data · high | Pass | Yes | 4 | 5 (124) |
| share-service | Data · high | Pass | Yes | 1 | 4 (84) |
| connector-service | Integration · medium | Pass | Yes | 1 | 3 (72) |
| map-service | Data · medium | Pass | Yes | 1 | 2 (26) |
| search-index | Data · medium | Pass | Yes | 1 | 1 (18) |
| notify-service | Platform · low | Pass | Yes | 1 | 2 (17) |

Rollback "Yes" means redeploying the previous version, 10–15 minutes. "No" means restoring from backup after the schema migration, estimated RTO 4 hours. Direct dependents are the services that list this one in `depends_on`. The Q3 columns count log rows; the 2026-07-11 SEV1 appears under both auth-service and gateway (Appendix A.3).

- **auth-service is the hub.** 6 of the other 8 services call it directly, and 7 of 8 depend on user-store beneath it (D1, D2). Identity: "A failed upgrade takes down every login."
- **Neither hard service can be rolled back.** Recovery is a restore from backup, estimated RTO 4 hours (notes, Rollback). That is 3.1 times the longest incident of Q3 (78 minutes) and 63% of all auth-service incident minutes in the quarter, in a single event (I19, I20, I21).
- **user-store is untested.** There is no staging environment, and building one takes about a week. Its v10 change is the database driver, which makes schema migrations one-way (notes, breaking change 4).
- **auth-service fails on the shim.** 2 of 148 integration tests fail in the token refresh flow, root cause not confirmed. The v10-compatible library (6.0) is promised "by end of November" and not committed (notes, breaking change 3), so a pre-freeze upgrade would go live on the shim and change again when 6.0 arrives, inside the freeze.
- **Identity is short-handed.** One of two engineers is on leave from 2026-10-26 to 2026-11-13, 15 working days (T4). At the Q3 rate, about two auth-service incidents would be expected in that window (I18; an illustration, not a forecast).

### 3.2 What last quarter's incidents add

- **auth-service is the most incident-prone service.** It has 11 of the 36 incident rows (31%) and 380 of the 932 logged minutes (41%), including the quarter's only SEV1 event (78 minutes, 2026-07-11) and 6 of the quarter's 10 SEV2 rows (I6 to I10). Four of gateway's seven incidents trace back to auth-service according to their summaries (I11). The 2026-07-11 SEV1 is one outage logged twice, so Q3 had 35 distinct events, not 36 (I2).
- **The failing tests sit in a known weak spot.** The two failures are in the token refresh flow, and token-refresh bugs caused 3 auth-service incidents in Q3 (72 minutes; I13). Whether the failures come from the shim or from a pre-existing bug is not known, so this link is an inference, not something the notes state.
- **Rollback works in practice.** 5 failed rollouts, all SEV3, were rolled back in 10–19 minutes, median 15 (I16). The notes' 10–15 minutes is realistic, but plan for up to 20.
- **Cascades are the common failure.** 12 of the 36 rows (33%, 354 minutes) were dependency or downstream-timeout incidents (I15), including 5 of gateway's 7 (I12). The default retry behaviour changed in v10, which matters here (R4).
- **No reliability benefit from v10 is assumed.** 3 incidents were runtime GC pauses (82 minutes; I14), but the notes do not say v10 changes that. The case for upgrading is the end of security support, which is all the notes claim.

## 4. Plan

### 4.1 Key dates

| Date | Event | Basis |
|---|---|---|
| Fri 2026-10-23 | Decision due | Notes |
| Mon 2026-10-26 | Data team can start; one Identity engineer's leave begins (runs to 2026-11-13) | Notes |
| Fri 2026-10-30 | Last working day before the freeze; waves 1 to 3 (Section 4.2) should be complete | Derived, proposed |
| Sun 2026-11-01 | Code freeze starts: only P1 hotfixes, otherwise a CAB exception | Notes |
| Thu 2026-11-05 | Last day to order v8 extended support | Notes |
| Thu 2026-11-12 | v8 end of security support | Notes |
| End of 2026-11 | IdentityModel 6.0 promised "by end of November"; not committed | Notes |
| Tue 2026-12-15 | Checkpoint on January readiness (Section 4.4) | Proposed |
| Tue 2027-01-05 | Freeze ends; earliest date for auth-service and user-store | Notes |

### 4.2 Upgrade order for the seven

Dates are indicative; the owning teams set the detail.

| Wave | When | Services (owner) | Why here |
|---|---|---|---|
| 1 | Mon 2026-10-26 to Tue 10-27 | notify-service (Platform), connector-service (Integration), search-index (Data) | Smallest blast radius. notify-service is low criticality with one dependent; connector-service has one dependent (gateway) and Integration rates it low risk; search-index has no dependencies. A clean first day on v10 and a trial of the roll-out steps. |
| 2 | Tue 2026-10-27 to Thu 10-29 | map-service and catalog-service together, then share-service (all Data) | catalog-service and map-service depend on each other (D4; the Q3 incidents of 2026-09-08 and 2026-09-19 show the same loop), so they move as a pair. catalog-service also has four dependents (D3). share-service has custom JSON converters and two of Q3's five failed rollouts, so it goes last, with room for a rollback. |
| 3 | Fri 2026-10-30 | gateway (Platform) | Platform: "last among the ones that pass". It is the swing item (Section 4.3). |

### 4.3 Rules for the week

- **Gateway is the swing item.** It goes on 2026-10-30 only if waves 1 and 2 landed without a rollback or an open regression, and Platform is satisfied that its retry behaviour holds when downstreams are slow (R4). Otherwise it stays on v8 into January, covered by the extended support that is being ordered anyway (assuming a flat price).
- **A rollback pauses the next wave** until the cause is known.
- **Slips are not rushed into the freeze.** A service that is not live by 2026-10-30 either goes under a CAB exception (the notes say CAB can approve work that is already staged and tested) or waits for January.
- **Identity stays out of the roll-out.** Neither Identity service is in a wave, which keeps the Identity team on auth-service stability and the January preparation.
- **Ask CAB this week.** How would it treat a slipped deploy, and a rollback or fix of a v10 service, during the freeze? (Open question 2.)

### 4.4 Getting auth-service and user-store ready for January

Schedule the one-way change only when all of these hold:

- The 2 failing tests are root-caused and fixed, and it is known whether they come from the shim or were already there.
- IdentityModel 6.0 is released, and auth-service passes all 148 integration tests on it rather than on the shim.
- A user-store staging environment exists (about a week to build) and the v10 migration has been rehearsed in it. The rehearsal should include connection-pool behaviour (the Q3 incident on 2026-09-04 was a pool exhaustion) and a timed restore from backup to confirm the 4-hour RTO.
- Both Identity engineers are available.

The earliest production date is Tuesday 2027-01-05. A CAB exception for an earlier date is possible only for work that is staged and tested, and is not planned. At the checkpoint on 2026-12-15, if the library or the staging work is not on track, decide whether to renew extended support for a second quarter ($18,000 more, same-price assumption).

### 4.5 What each team said, and how the plan treats it

| Team | Stated position (paraphrased from the notes) | In this plan |
|---|---|---|
| Identity | Hold auth-service until the vendor library is out; a failed upgrade takes down every login | Followed. auth-service and user-store stay on v8 until January. |
| Data | Four services in a week if they start Monday | Used. Waves 1 and 2, 2026-10-26 to 2026-10-29. Needs the decision on Friday. |
| Platform | gateway last among the services that pass, because it fronts everything | Followed. gateway is wave 3 and the swing item. notify-service is in wave 1. |
| Integration | connector-service is low risk and can go any time | Wave 1. Consistent with the data: 3 SEV3 incidents in Q3, none runtime-related. It has custom JSON converters, which passed staging. |

## 5. Risks

| # | Risk | Why it matters | Response |
|---|---|---|---|
| R1 | Mixed v8/v10 operation misbehaves | Seven v10 services will call auth-service on v8 for at least nine weeks (T7). The JSON serializer defaults changed, and the notes do not say staging ran this mix. | Gate 1 before the first deploy. If it fails, Option B. |
| R2 | No slack before the freeze | The Data team's five working days end Friday 2026-10-30, and the freeze starts Sunday 2026-11-01. A regression that appears a few days after the last wave shows up inside the freeze. | Decide on Friday. Gateway is the swing item. Brief CAB now; staged and tested work can go by exception. |
| R3 | v10 problems after 2026-11-01 are harder to fix | Only P1 hotfixes deploy in the freeze. If P1 means SEV1 (assumed), 34 of Q3's 35 incident events would have needed a CAB exception (I2, I5). A rollback is itself a redeploy, and the notes do not say whether it is exempt. | Ask CAB in advance (Open question 2). Pause waves after any rollback. Watch the seven services closely for the first two weeks. |
| R4 | Retry and timeout behaviour changes under load | The default HTTP client handler and retry behaviour changed. Gateway's custom retry policy passes staging, but staging checked function, and 5 of gateway's 7 Q3 incidents were downstream timeouts. This is an inference, not a finding. | A staging run with auth-service and catalog-service slowed down, before gateway goes. If it cannot be done, gateway waits for January. |
| R5 | Critical identity services unpatched after 2026-11-12 | v8 patches stop on 2026-11-12, and extended support must be ordered by 2026-11-05. auth-service and user-store stay on v8 for at least 54 days (T1). | Approve now and order in the week of 2026-10-26. Confirm the terms (Open question 3). |
| R6 | January slips | The vendor library is not committed, the failing-test cause is unknown, there is no user-store staging environment, and Identity is at half strength until 2026-11-13. | Entry criteria (Section 4.4); checkpoint on 2026-12-15; a second quarter of extended support ($18,000) as the contingency. |

## 6. Open questions and assumptions

### 6.1 Open questions

| # | Question | Ask | Needed by | Affects |
|---|---|---|---|---|
| 1 | Which auth-service version and configuration did the 2026-10-09 to 10-11 staging runs of the seven services use? | Platform | Before the first deploy (2026-10-26) | Gate 1; C versus B |
| 2 | During the freeze, what counts as P1? Is a rollback of a v10 service exempt? Does the staging evidence from 2026-10-09 to 10-11 count as "staged and tested" for an exception? | CAB / change manager | 2026-10-23 | R3; slips under 4.3 |
| 3 | Is the $18,000 a flat price for the v8 estate, or per service or host? Does a quarter run from activation (2026-11-12) or follow the calendar? What are the renewal terms? | Procurement / vendor | Before ordering; order by 2026-11-05 | Cost of B versus C; whether January needs $18,000 or $36,000 |
| 4 | Do the 2 failing tests come from the shim or from a pre-existing token-refresh bug? | Identity | Start now | January readiness; R6 |
| 5 | Will the vendor commit to a date for IdentityModel 6.0? | Identity, with the vendor | Checkpoint on 2026-12-15 | January date; extended support |
| 6 | Who builds the user-store staging environment (about a week), and when? | Engineering Lead with Identity and Platform | By 2026-11-13 | January readiness |
| 7 | Does the Data team's "one week" include production rollout and room for a rollback? Do Platform and Integration have capacity for their waves? | Data, Platform, Integration | Before 2026-10-26 | Gate 2; R2 |
| 8 | Has anything changed since the inputs were captured (staging 2026-10-09 to 10-11; incidents to 2026-09-28)? | Platform | Before 2026-10-23 | Everything above |

### 6.2 Assumptions

- The freeze restricts production deployments only; building and testing in staging continues.
- "P1 hotfix" means SEV1-class. SEV2 and SEV3 fixes need a CAB exception. The inputs do not define P1.
- Extended support is $18,000 per quarter as a flat price for the whole v8 estate, a quarter runs 3 months from 2026-11-12 (to 2027-02-12), and a second quarter costs the same.
- A working week is Monday to Friday with no weekend deployments. The Data team's week is 2026-10-26 to 2026-10-30 and includes the production rollout.
- `depends_on` in the inventory means a runtime call: if A depends on B, a B failure reaches A.
- auth-service and user-store are upgraded together or in sequence, because both lack a rollback path and auth-service depends on user-store.
- The staging results of 2026-10-09 to 10-11 still hold; nothing has changed in staging since.
- The inventory and the incident log carry no as-of date. They are taken as current on 2026-10-17, the day they were received.
- Percentages and the expected-incident rate are there to show scale. They are not forecasts.

## 7. Decision record

Keep Sections 1 to 6 as they were at the time of the decision. Record the outcome here and put any later change in a dated addendum below.

| Field | Entry |
|---|---|
| Recommendation in this report | Option C (split) |
| Decision (A / B / C / other) | |
| Decided by | Marcus Hale |
| Date | |
| Conditions attached (for example Gates 1 and 2) | |
| v8 extended support ordered (yes / no, date, reference) | |
| CAB reference | |
| Next checkpoint | |
| Reasons, and any dissent | |

**Addenda**

(none yet)

**Revision history:** 1.0, 2026-10-17, first version for the 2026-10-23 decision.

## Appendix A. Evidence and method

### A.1 Files

| File | What it is |
|---|---|
| [`report.md`](report.md) | This report |
| [`evidence/source/upgrade-notes.md`](evidence/source/upgrade-notes.md) | Platform team's notes, 2026-10-14. Verbatim copy |
| [`evidence/source/services.csv`](evidence/source/services.csv) | Service inventory (owner, criticality, dependencies, rollback, staging result). Verbatim copy |
| [`evidence/source/incidents-q3.csv`](evidence/source/incidents-q3.csv) | Q3 2026 incident log, 36 rows. Verbatim copy |
| [`evidence/SHA256SUMS.txt`](evidence/SHA256SUMS.txt) | SHA-256 of the three source files as received |
| [`evidence/derived/key-figures.csv`](evidence/derived/key-figures.csv) | Every derived number cited here (IDs such as I20 in the text), with how it was calculated |
| [`evidence/derived/key-dates.csv`](evidence/derived/key-dates.csv) | The dates used, with weekdays and sources |
| [`evidence/derived/dependency-analysis.csv`](evidence/derived/dependency-analysis.csv) | Dependents, transitive dependents and cycles per service |
| [`evidence/derived/incidents-by-service.csv`](evidence/derived/incidents-by-service.csv), [`incidents-by-cause.csv`](evidence/derived/incidents-by-cause.csv) | The aggregates in Appendix B |
| [`evidence/analysis.py`](evidence/analysis.py) | Recomputes everything in `evidence/derived/` and `figures/` |
| [`figures/dependency-map.png`](figures/dependency-map.png), [`.dot`](figures/dependency-map.dot) | Figure 1 and its Graphviz source |

### A.2 Verify and regenerate

Run `python evidence/analysis.py`. It checks the source files against `SHA256SUMS.txt`, rewrites `evidence/derived/` and `figures/`, and prints the key figures. It uses only the Python standard library; the PNG also needs Graphviz (`dot`), and without it only the `.dot` source is written. The source files are hashed as received. If a checksum fails after a git checkout, check line-ending conversion.

### A.3 Data notes

- **One outage logged twice.** The 2026-07-11 SEV1 (78 minutes) appears under auth-service and under gateway, and the gateway row says it was caused by auth-service. Per-service tables keep both rows. Event counts count it once: 35 events and 854 minutes, against 36 rows and 932 minutes.
- **Circular dependency.** catalog-service and map-service list each other in `depends_on`.
- **Classification rules** that use the free-text `summary` column: a failed rollout is a summary containing "rolled back"; a gateway row cites auth-service when its summary contains "auth-service".
- **Rates** use the 92 days of Q3 (2026-07-01 to 2026-09-30) as the denominator, although the log runs from 2026-07-02 to 2026-09-28.
- **Rollback times.** The notes say 10–15 minutes. The five Q3 rollbacks took 10–19 (connector-service took 19).
- **Not in the data.** Incidents after 2026-09-28, the cost of downtime, any assessment of the security exposure on v8 after 2026-11-12, and who would build the user-store staging environment.

## Appendix B. Q3 2026 incident summary

By service, in order of logged minutes. Source: `evidence/derived/incidents-by-service.csv`.

| Service | Incidents | Minutes | SEV1 | SEV2 | SEV3 | Longest (min) | Causes |
|---|---|---|---|---|---|---|---|
| auth-service | 11 | 380 | 1 | 6 | 4 | 78 | token-validation-timeout ×5; token-refresh-bug ×3; config ×2; runtime-gc ×1 |
| gateway | 7 | 178 | 1 | 1 | 5 | 78 | downstream-timeout ×5; config ×2 |
| catalog-service | 5 | 124 | 0 | 1 | 4 | 52 | dependency ×2; config ×1; deploy ×1; runtime-gc ×1 |
| share-service | 4 | 84 | 0 | 1 | 3 | 45 | deploy ×2; dependency ×1; downstream-timeout ×1 |
| connector-service | 3 | 72 | 0 | 0 | 3 | 28 | dependency ×2; deploy ×1 |
| user-store | 1 | 33 | 0 | 1 | 0 | 33 | config ×1 |
| map-service | 2 | 26 | 0 | 0 | 2 | 14 | dependency ×1; deploy ×1 |
| search-index | 1 | 18 | 0 | 0 | 1 | 18 | runtime-gc ×1 |
| notify-service | 2 | 17 | 0 | 0 | 2 | 9 | queue-backlog ×2 |
| **Total (rows)** | **36** | **932** | **2** | **10** | **24** | 78 | |

By cause, in order of logged minutes. Source: `evidence/derived/incidents-by-cause.csv`.

| Cause | Incidents | Minutes | SEV1 | SEV2 | SEV3 | Services |
|---|---|---|---|---|---|---|
| token-validation-timeout | 5 | 221 | 1 | 4 | 0 | auth-service |
| dependency | 6 | 183 | 0 | 2 | 4 | catalog-service, connector-service, map-service, share-service |
| downstream-timeout | 6 | 171 | 1 | 1 | 4 | gateway, share-service |
| config | 6 | 113 | 0 | 1 | 5 | auth-service, catalog-service, gateway, user-store |
| runtime-gc | 3 | 82 | 0 | 1 | 2 | auth-service, catalog-service, search-index |
| deploy | 5 | 73 | 0 | 0 | 5 | catalog-service, connector-service, map-service, share-service |
| token-refresh-bug | 3 | 72 | 0 | 1 | 2 | auth-service |
| queue-backlog | 2 | 17 | 0 | 0 | 2 | notify-service |
| **Total (rows)** | **36** | **932** | **2** | **10** | **24** | |
