# Cold-read answers

Based only on top.md (first 60 lines) and its one image, task-map.png. Anything I could not see is marked as such.

## 1. What is it about, and what is the message? (two sentences)

This is a draft handoff (2026-10-19, written by GitHub Copilot from Alex's notes, for Dana who decides and for the next coding agent) about moving scheduled data exports from a legacy cron to a new platform called JobRunner, one tenant at a time behind a feature flag. Its message is that the CSV export path is built and passed 20 staging exports, but the work is rated "At risk" because four open answers (XLS above 1M rows, the production migration, the pool size, the email wording) wait on other people, nothing is done in production yet, and the Tue 2026-11-10 cutover needs those answers by Fri 2026-10-30.

## 2. Decision or action requested, from whom, by when

Answers to four gating questions by **Fri 2026-10-30** (called Alex's at-risk line; none of the four has a committed date):

- **Q1 - Dana** (asked 2026-10-06, still no answer): XLS above 1M rows - (a) a ZIP of several 1M-row XLS files, or (b) CSV only? Alex prefers (a).
- **Q2 - budget holder (not named):** pay +1,200 USD/month for 6 pool workers instead of 3, so Acme's 15-minute SLA holds? No recommendation given.
- **Q3 - Marketing:** approve email wording and logo (draft out since 2026-10-12); Dana to chase (suggested).
- **Q4 - someone to be named:** book the production DBA (database-admin) slot and stay reachable; suggested: the earliest slot.

Also listed, with no date: **Q5** (someone to be named: find owners for 3 unclaimed cron jobs) and **Q6** (Dana, suggested: keep or move the 2026-11-10 cutover; no recommendation). Who names the "someone" is not stated. Production steps by the continuing agent need Dana's go-ahead (suggested).

Counting note: the callout says "Q1 to Q4 gate the rollout" but lists six items, and the figure shows five answers. The caption reconciles it: Q5 only gates the cron shutdown (T10) and Q6 is the date on T9.

## 3. Most important risks, in the document's order (the table says the ranking is the writer's, not Alex's)

1. Four rollout prerequisites wait on other people and none has a date, so the cutover slips (red).
2. Acme's SLA fails with 3 exports at once on 3 workers (21 min against a 15 min limit), at risk on Monday mornings; fix is about +1,200 USD/month.
3. XLS above 1M rows is only a stub; Acme's 4.2M-row XLS exports fail if switched before that work (T5) is done.
4. Three legacy cron jobs have no known owner, so the old cron cannot be switched off and those jobs would stop.
5. Alex is back only on Sat 2026-11-07, one working day before cutover; nobody who knows the code until then.

Also named: confidence is only "medium" (Alex's notes, not re-checked in the repo; rollout length and production deploy steps unknown). A late answer only moves the date, while a wrong Q1 or Q2 changes what Acme gets or breaks its SLA.

## 4. Key components and how they relate

- **Legacy cron:** 14 scheduled export jobs; 11 map one-to-one to JobRunner definitions, 3 have no known owner. It is being replaced by **JobRunner**: a job is a YAML file in `jobs/`, run by workers in a pool. Alex built one job, `export-dataset`, for pool `exports-pool` (3 workers). (Unclear to me how 11 mapped definitions fit with only one built job.)
- **Per-tenant flag** `exports.jobrunner.enabled` (off by default, overridable per tenant) moves tenants in order: `nimbus-internal`, then Acme (the customer with the 15-minute SLA), then everyone else. Only local and staging work is recorded; the old cron is switched off last (T10).
- **Task map** (11 tasks, arrow = "must finish first", ovals = answers from people, dashed = inferred):
  - Done: T1 job definition, which leads to T2 streaming CSV writer and T3 idempotency key plus staging migration.
  - Waiting on a person: T4 production migration 0042 (Q4, ticket DBA-5521), T5 XLS above 1M rows (Q1), T6 pool 3 to 6 workers (Q2), T7 email template approval and wiring (Q3).
  - Those four all feed T9 per-tenant rollout (target Tue 2026-11-10), which feeds T10 decommission legacy cron; T10 also needs T8 map the 3 unmapped cron jobs (owners needed, Q5).
  - T11 fix flaky `test_export_cancel` is low priority and independent.

## 5. Numbers and dates that matter

- **Dates:** cutover Tue 2026-11-10; answers needed Fri 2026-10-30; Alex back Sat 2026-11-07; Q1 asked 2026-10-06; email draft out 2026-10-12; document dated 2026-10-19.
- **Counts:** 20 staging exports passed; 3 of 11 tasks done and 4 waiting on people; 6 open questions, 4 gate the rollout; 14 cron jobs (11 mapped, 3 unowned).
- **Sizing:** 1M-row XLS limit against Acme's 4.2M rows; 21 min against the 15 min SLA; 3 to 6 workers = +1,200 USD/month.

## 6. Which section next, and what I expect there

Section 3, "Six open questions need answers and four gate the rollout" (about 4 min); the document itself says "Only deciding? Read 3 and stop." I expect, for each of Q1 to Q6: the options, the evidence (the 21-minute run, the 4.2M-row exports, the 1,200 USD figure), who was asked and when, what each answer unblocks (Q1 to T5, Q2 to T6, Q3 to T7, Q4 to T4, Q5 to T8 and T10, Q6 to the T9 date) and the cost of a late or wrong answer. As the continuing agent I would instead read 4 and then A (commands, ordered steps). None of that content is visible to me, so these are expectations only.
