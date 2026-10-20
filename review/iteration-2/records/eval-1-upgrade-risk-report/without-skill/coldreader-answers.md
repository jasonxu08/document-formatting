1. This document assesses the risk of upgrading nine services from runtime v8 to v10 before a code freeze that starts on Sunday 2026-11-01.
   Its main conclusion is to split the upgrade (Option C): move the seven services that passed staging before the freeze, keep auth-service and user-store on v8
   until January, and buy one quarter of v8 extended support ($18,000) to cover those two.

2. Marcus Hale (Engineering Lead, decision owner) must decide by Friday 2026-10-23: (1) approve Option C, the split upgrade;
   (2) approve $18,000 for one quarter of v8 extended support (order by Thursday 2026-11-05; submit in the week of 2026-10-26);
   (3) tell the Data team to start Monday 2026-10-26; (4) ask the change advisory board how slipped deploys, rollbacks or fixes during the freeze would be treated.
   Before the first production deploy on 2026-10-26, Platform must pass Gate 1 (mixed-version check) and the teams Gate 2 (readiness); if either fails, fall back to Option B.

3. (1) auth-service (fails 2 of 148 tests, cause unconfirmed) and user-store (untested on v10) are not ready, yet 6 of the other 8 services call auth-service directly.
   (2) Neither can be rolled back: the migration is one-way and a restore from backup takes about 4 hours (longest incident last quarter: 78 minutes); "every login" would be down.
   (3) They cannot be ready before the freeze: the vendor's v10 identity library is only promised "by end of November", and one of Identity's two engineers is on leave 2026-10-26 to 2026-11-13.
   (4) Option C's own risks: no slack in the Data team's week (a late decision pushes work into the freeze), v10 live while only P1 hotfixes ship, 67 days of mixed v8/v10, staging setup unverified (Gate 1).

4. Nine services: seven (gateway, share, connector, catalog, map, notify, search-index) passed staging and can roll back in 10-15 min; auth-service (2 failing tests) and user-store (untested) cannot.
   Figure 1: six services call auth-service, which depends on user-store; search-index sits under catalog-service; catalog-service and map-service depend on each other.
   Options: A all nine before the freeze (not recommended); B all in January (safe fallback); C split - seven by 2026-10-30, auth-service and user-store in January.
   C goes ahead only if two gates pass before the first deploy on 2026-10-26 (Gate 1 mixed-version check, Gate 2 team readiness); otherwise fall back to B.

5. Dates: decision by Fri 2026-10-23; Data team starts Mon 2026-10-26 and the seven services must be on v10 by Fri 2026-10-30; freeze runs from Sun 2026-11-01 to 2027-01-05.
   Money: $18,000 for one quarter of v8 extended support, ordered by 2026-11-05 and active 2026-11-12 ($36,000 if the January upgrade is not done by about 2027-02-12).
   Counts: 7 of 9 services ready; auth-service fails 2 of 148 tests; 6 of 8 services call auth-service directly, 7 of 8 depend on user-store.
   Time: restore ~4 h vs rollback 10-15 min (worst Q3 incident 78 min); 67 days of mixed v8/v10 under C; Identity engineer away 2026-10-26 to 2026-11-13; vendor library "by end of November".

6. Section 3 (Evidence), continuing 3.1 "The risk is concentrated in two services", where this page breaks off after "Services that are not ready come first".
   I expect per-service facts for auth-service and user-store (failing tests, no staging environment, no rollback), with bracketed codes like (D1) pointing to key-figures.csv.
   After that, Section 4.3 (freeze handling, CAB route, "swing rule", possible gateway deferral) and the open questions (e.g. the extended-support price assumption).
