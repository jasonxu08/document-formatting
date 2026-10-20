# Cold-reader answers

1. This is a handoff, written for Dana (decisions) and an AI coding agent (continues the work), for moving scheduled exports from a legacy cron to JobRunner while Alex is away 2026-10-17 to 2026-11-06.
   The code is largely built (3 of 11 tasks done, nothing live in production), but the Tue 2026-11-10 cutover is at risk unless four people-dependent items (Q1 to Q4) are settled by Fri 2026-10-30.

2. From Dana, 7 items (A2). Two decisions, both by Fri 2026-10-30: Q1 XLS above 1,048,576 rows (ZIP of several XLS files vs CSV only) and Q2 six workers instead of three (about +1,200 USD/month).
   Also by Fri 2026-10-30: chase Marketing's approval of the notification email (Q3), arrange a DBA window for migration 0042 (Q4), confirm or move the 2026-11-10 cutover (Q6).
   By Mon 2026-10-19: name who the agent escalates to and who approves production steps (Q7). No date: find owners of 3 unrecognised legacy cron jobs (Q5, needed before decommissioning).
   Answers go to whoever runs the agent or into the Decision log (B6); a decision counts as final only once it is logged there.

3. (i) Cutover Tue 2026-11-10 is at risk: Q1 XLS policy, Q2 budget, Q3 Marketing sign-off and Q4 DBA window are all open; production rollout cannot start until all four are done, and no effort estimates exist for the work after them.
   (ii) Little slack: the last DBA window is Thu 2026-11-05, leaving Fri 11-06, Mon 11-09 and Tue 11-10 for a three-stage rollout; Alex is unreachable until 11-06 and back one working day before cutover.
   (iii) Acme: no policy for XLS above 1,048,576 rows (Acme has 4.2M), and 3 workers would miss its 15-minute SLA when 3 exports run at once (6 would fix it, but no test is recorded).
   (iv) 3 legacy cron jobs have no known owner, so the old cron cannot be switched off (this does not block the rollout).

4. Pieces: an export job (replacing legacy cron), a streaming CSV writer, retry-safe exports (idempotency key), a per-tenant feature flag, and DB migration 0042 (done on staging only).
   Dependency map: T1-T3 (done) feed T4 production migration (blocked: DBA window), T5 XLS above 1M rows (blocked: Q1), T6 workers 3 to 6 (blocked: Q2) and T7 notification email (in progress: Marketing).
   T4-T7 must all finish before T9, the per-tenant rollout (internal, then Acme, then all); T9 and T8 (map the 3 unowned cron jobs, can start now) must finish before T10, decommissioning the legacy cron; T11 (fix flaky test) is independent.
   Layout: Part A (A1-A4) is status and decisions for Dana; Part B (B1-B6) is ground rules, tasks, learnings and logs for the agent.

5. Dates: cutover Tue 2026-11-10; Q1-Q4 and Q6 by Fri 2026-10-30; Q7 by Mon 2026-10-19; Alex away 2026-10-17 to 2026-11-06, back Sat 11-07, first working day Mon 11-09.
   DBA windows (Tue/Thu 22:00-23:00 UTC): 10-20, 10-22, 10-27, 10-29, 11-03, 11-05 (last before cutover); migration 0042, ticket DBA-5521.
   Progress: 3 of 11 tasks done, 1 in progress, 3 blocked, 4 not started; 20 staging CSV exports (internal tenant) ran cleanly.
   Sizing: XLS limit 1,048,576 rows vs Acme 4.2M rows; 15-minute SLA; 3 vs 6 workers (about +1,200 USD/month); 3 concurrent exports; 3 unowned cron jobs.

6. A4, "Detail behind the two decisions", starting with Q1 (XLS above 1,048,576 rows); the first screen stops right at that heading.
   I expect the options (a) ZIP of several XLS files vs (b) CSV only, their effect on Acme (4.2M rows) and why Alex prefers (a), then Q2 with the worker/SLA/cost figures (3 vs 6 workers, 15 minutes, +1,200 USD/month).
   After that, B3 (the task table, described as the live status) if I were working on the migration itself.
