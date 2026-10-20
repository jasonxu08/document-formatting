1. A postmortem of the 105-minute order/payment outage on 2026-10-09, caused by config change CFG-2231 (order-service connection pool 200->20; test-only intent, but it became the global default and was pushed with no canary).
   Message: a process/system failure (no blame on individuals) that lasted long because finding the cause (38 min) and confirming recovery (37 min) were slow; six fixes need prioritising, and the doc recommends a 9-person-day subset of them.

2. Zhang Wei (tech lead) must decide which improvement items go first in the next iteration: 6 items = 17 person-days (pd), only about 10 available.
   Recommended: A4, A3, A6, A1, A5 (9 pd, 1 pd buffer), defer A2 canary push (8 pd); alternative: A2, A3, A4, A6 (10 pd, no buffer), defer A1/A5.
   By when: not stated (only "next iteration"). Everyone: when troubleshooting, check config changes as well as service releases (no date given).

3. (a) A test-only config (pool 200->20) became the global default and was pushed to order, payment and gateway at once with no canary: the root cause.
   (b) 38 min to find it: checks went to "database" and "any release"; "no service release today" (14:40) did not rule out a config change.
   (c) 37 min of recovery confirmation, reason not recorded; (d) alert only 7 min after push, and payment retries drove CPU above 90%.
   (e) SLO missed (99.93% vs 99.95%); only about 10 of 17 person-days available, so some fixes slip. (My ordering; the doc does not rank them.)

4. Chain: CFG-2231 merged 13:58 -> config center pushes it at 14:02 to order service, payment service, gateway -> order threads queue for connections, orders time out
   -> payment retries, CPU above 90% -> rollback 15:10 -> recovery, declared over 15:47.
   Phases (Fig. 1): undetected 7 -> respond/open incident group 11 -> find cause 38 -> decide/roll back 12 -> recover/confirm 37 min.
   Fixes A1-A6: range check (blocks bad config at entry), canary push, alert threshold (undetected phase), on-call manual, retry backoff (stops spread to payment), two-person review; other mappings not stated in this excerpt.

5. Outage 2026-10-09 14:02-15:47 = 105 min. Key times: 13:58 merge, 14:02 push, 14:09 alert, 14:20 incident group, 14:58 cause found, 15:10 rollback.
   Phases 7/11/38/12/37 min (longest two = 75 min, 71%); pool limit 200->20; about 3,800 failed orders; about 1,200 users; payment CPU above 90%.
   Availability 99.97% -> 99.93% vs 99.95% SLO; report dated 2026-10-17.
   Decision: 6 items = 17 pd vs about 10 available (gap 7); Option 1 = 9 pd, Option 2 = 10 pd; A2 alone = 8 pd; A4+A3+A6 = 2 pd.

6. Section 6 (improvement items and priority recommendation, incl. 6.4): the decision box points there for the basis and trade-offs.
   I expect an A1-A6 table with effort, what each fixes, why Option 1 beats Option 2, and 6.4 on why recovery confirmation took 37 min (the summary says it is unrecorded).
   After that: the rest of Section 3 (timeline rows for phases 2-5) and Appendix B (source discrepancies marked with a dagger).
