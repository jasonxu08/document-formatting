# Handoff: scheduled exports migration (legacy cron → JobRunner)

- **Status as of:** 2026-10-17 (last work-log entry: 2026-10-15).
- **Alex away:** 2026-10-17 to 2026-11-06 (work log). Back 2026-11-07, a Saturday, so the first working day is Mon 2026-11-09, one day before the cutover target. Alex is unreachable in the meantime.
- **Cutover target:** Tue 2026-11-10.
- **Who reads what:** **Dana** reads Part A (status, and what is needed from her). The **AI coding agent** reads Part A for context, then works from Part B.
- **Contents:** Part A: A1 bottom line, A2 what is needed, A3 key dates, A4 detail on Q1 and Q2. Part B: B1 ground rules, B2 orientation, B3 tasks, B4 what was learned, B5 not in the notes, B6 logs.

> **Convention.** Facts come from Alex's notes (work log, task list, open questions) or are calendar arithmetic on them. The structure, checklists and order of work were added when this handoff was written. **[Assumption]** marks a reading chosen where the notes were ambiguous. **[Suggestion]** marks an idea that is not in the notes and has not been checked with Alex.

## Part A: Status and decisions (for Dana)

### A1. Bottom line

- **Where it stands.** Built: the export job, a streaming CSV writer, retry-safe exports (idempotency key) and a per-tenant feature flag for the rollout. On staging, 20 CSV exports for the internal tenant ran cleanly. Nothing is live in production. 3 of 11 tasks are done, 1 is in progress, 3 are blocked and 4 have not started.
- **What is holding it up.** People, not code: an XLS policy decision (Q1), a budget decision (Q2), Marketing's sign-off on the notification email (Q3) and a DBA window (Q4). The production rollout cannot start until all four are done.
- **Risk.** The 2026-11-10 cutover is at risk if Q1 to Q4 are not settled by **Fri 2026-10-30** (Alex's estimate; the notes give no effort estimates for the work that follows each decision).
- **What is needed from Dana.** Seven items (A2). Two are decisions: Q1 (XLS policy) and Q2 (pool budget). The rest unblock others: Q3 (Marketing), Q4 (DBA window), Q5 (cron owners), Q6 (cutover date) and Q7 (escalation contact).
- **While Alex is away.** An AI coding agent continues all work that is not blocked (Part B) and logs its progress in B6. **[Assumption]** It makes no production change without a human go-ahead (Q7).

![Task dependency map as of 2026-10-17. T1 to T3 are done. T4 (DBA window), T5 (product decision) and T6 (budget decision) are blocked and T7 (Marketing) is in progress; all four must finish before T9 (rollout). T10 (decommission) needs T9 and T8. T8 can start now. T11 is independent and low priority. Full detail in section B3.](assets/task-status.png)

*Snapshot of 2026-10-17, drawn from `assets/task-status.dot`. The table in B3 is the live status.*

### A2. What is needed from Dana

| # | What is needed | Alex's view | By when |
|---|---|---|---|
| **Q1** | **Decide** the policy for XLS above 1,048,576 rows: (a) a ZIP of several XLS files, or (b) CSV only. Affects Acme (4.2M rows). Open since 2026-10-06. | Prefers (a) | Fri 2026-10-30 |
| **Q2** | **Decide** on 6 workers instead of 3 (about +1,200 USD/month), so that Acme meets its 15-minute SLA when 3 exports run at once. | 6 would fix it (no test recorded) | Fri 2026-10-30 |
| **Q3** | **Chase** Marketing's approval of the wording and logo of the new notification email. Draft sent 2026-10-12, no answer. | - | Fri 2026-10-30 |
| **Q4** | **Arrange** a DBA window for production migration 0042 (ticket DBA-5521) and a person who is reachable during it. | - | Book by Fri 2026-10-30; windows in A3 |
| **Q5** | **Find** the owners of 3 legacy cron jobs nobody on the team recognises: `export_weekly_xls`, `export_audit`, `export_adhoc`. They do not block the rollout, but the old cron cannot be switched off until they are mapped or retired. | - | No date (needed before T10) |
| **Q6** | **Confirm or move** the cutover date, Tue 2026-11-10. | At risk if Q1 to Q4 slip past 2026-10-30 | Fri 2026-10-30 |
| **Q7** | **Confirm** who the agent escalates to while Alex is away, and who approves production steps. | - | Mon 2026-10-19 |

**Assumptions behind the table.** "The decisions" in Alex's note on the cutover date (Q6) means Q1 to Q4, the four things the rollout waits for. Q7 is not in Alex's notes; the assumed contact is Dana, unless she names someone else. Q2 needs a budget decision but the notes do not say whose; route it to the budget owner if that is not Dana.

**How to answer.** Tell whoever runs the agent, or write the answer into the Decision log (B6). The agent treats a decision as final only once it is in that log.

**Coming up.** The agent will draft a rollout runbook for Dana's approval: the stages, the checks after each stage, and how long each stage runs before the next. The notes do not specify these.

### A3. Key dates

| Date | What |
|---|---|
| Week of 2026-10-19 | The agent starts on the unblocked work (Part B). |
| Tue 2026-10-20 | DBA window. All windows are Tue and Thu, 22:00 to 23:00 UTC. |
| Thu 2026-10-22 | DBA window. |
| Tue 2026-10-27 | DBA window. |
| Thu 2026-10-29 | DBA window. |
| **Fri 2026-10-30** | Deadline for Q1 to Q4 (Alex's estimate); checkpoint for Q6. |
| Tue 2026-11-03 | DBA window. |
| Thu 2026-11-05 | DBA window, the last one before the cutover. After it, only Fri 11-06, Mon 11-09 and Tue 11-10 remain for a three-stage rollout. |
| Sat 2026-11-07 | Alex's return date; the first working day is Mon 2026-11-09. |
| **Tue 2026-11-10** | Cutover target. |

### A4. Detail behind the two decisions

#### Q1: XLS above 1,048,576 rows

- **Problem.** `xlsxwriter` cannot write more than 1,048,576 rows per sheet; Acme's largest dataset has 4.2M. The XLS writer is only a stub that raises `NotImplementedError` above 1M rows, so such an export would fail on JobRunner.
- **(a) ZIP of several XLS files of 1M rows each** (5 files for Acme). Customers receive a ZIP instead of one file. Alex prefers this.
- **(b) Drop XLS for large datasets** and tell customers to use CSV. CSV has no row cap (Acme's 4.2M rows took 9.5 min alone on 3 workers). Nothing to build for splitting or zipping.
- **(c) Several sheets in one file.** Still capped per sheet, and confusing. Alex does not recommend it.
- **Either way,** Acme has to be told what changes. The notes do not say who does that.
- **Not known yet.** All measurements so far are CSV; XLS has not been timed because the writer is a stub. **[Suggestion]** XLS writing is typically slower than CSV, so the 9.5-minute figure may not carry over to (a). A quick timing spike (T5 in B3) would settle it before Dana decides.

#### Q2: pool size

- **Measured on 2026-10-09** (Acme's largest dataset, 4.2M rows, pool of 3 workers): 9.5 min when it runs alone, which passes; 21 min with 3 exports at once, which fails. Acme's contract requires an export to complete within 15 minutes, and Acme runs several exports on Monday mornings.
- **Not measured.** Alex expects 6 workers to fix the concurrent case; no 6-worker run is recorded. Estimated cost: about +1,200 USD/month.
- **The choice:** approve 6 workers, or keep 3 and accept the SLA risk on busy Monday mornings. **[Suggestion]** The notes do not look at cheaper options (for example staggering Acme's Monday exports). A 6-worker test on staging (T6 in B3) would turn the estimate into a measurement.

## Part B: Continuing the work (for the AI agent)

You are picking this up from Alex, who cannot be reached until 2026-11-07. Everything you need is meant to be in this document; where it is not, B5 says where to look or whom to ask. Escalate to Dana (Q7), and keep working on whatever is not blocked. Start with the first-session checklist in B2, then follow the order of work in B3.

### B1. Ground rules

**[Assumption]** The notes do not say who may change what. The rules below are the safe default, and they follow from the notes (DBA window, budget decision, the warning about secrets, cron to be switched off only after migration).

**Needs a recorded human go-ahead (Decision log, B6) before you do it:**

1. Apply migration 0042 in production (T4). It also needs a DBA window and a person who is reachable during it.
2. Enable `exports.jobrunner.enabled` or edit `tenant_flags` for any production tenant (T9).
3. Change the production worker count (T6).
4. Edit, disable or delete any legacy cron job (T8, T10).
5. Send or approve any customer communication, for example about XLS.

**Never:**

- Copy, print, log or commit anything from the vault path `kv://nimbus/exports/prod/*`. Refer to it by path only. If a step seems to need the values, stop and escalate.
- Retry the dead ends in B4.
- Treat Q1 to Q4 as answered before the Decision log says so. Alex's task list says T5 needs the "policy decision first".

**Always:**

- Say so when a step needs access you do not have (staging VPN, kubectl, database, Grafana, ticketing, vault), then move to the next unblocked item. Do not simulate success.
- Escalate by adding an Update-log row that starts with `NEEDS DANA:` and by saying so in your last message of the session.
- Run `kubectl get pods -n exports` after any staging deploy; the deploy script fails silently without the VPN.
- Update the status table (B3), the Decision log and the Update log (B6), and the "Status as of" line at the top, at the end of every session.
- **[Assumption]** Work on staging (deploys, manual pool scaling, test exports) is in scope, as it was for Alex. Note what you changed and restore the pool size afterwards.

### B2. Orientation

**What this is.** Scheduled exports are moving from 14 legacy cron jobs (`legacy/crontab.txt`) to JobRunner, the new job platform: jobs are YAML definitions in `jobs/`, executed by workers in a runner pool. The pool is `exports-pool` (3 workers). Alex's checkout is `C:\work\nimbus-exports` (Python 3.12, Windows, PowerShell).

**First-session checklist**

1. `git status`, `git branch -vv`, `git log --oneline -20`. The notes do not say which branch holds the work or whether it is pushed. Record the answer in the Update log. Do not discard uncommitted changes; tell Dana if there are any.
2. Start the database and run the tests; record the counts (last known: 212 passed, 1 xfailed).
3. Run the local smoke export.
4. Check staging access: VPN, then `kubectl get pods -n exports`.
5. Read `docs/cron-mapping.md`, `jobs/`, and how `exports.jobrunner.enabled` is used in the code (B5 explains why).

**Commands**

```powershell
cd C:\work\nimbus-exports                                             # or your own clone
docker compose up -d postgres                                         # needed for local runs and for the tests
python -m exports.cli run --dataset demo --format csv --rows 100000   # local smoke run
pytest tests/exports -q                                               # Postgres from docker compose must be running
./scripts/deploy.ps1 -Env staging -Service exports-runner             # repo root; needs the staging VPN
kubectl get pods -n exports                                           # always check after deploy.ps1
```

**Where things are**

| Path or name | What it is |
|---|---|
| `jobs/export-dataset.yaml` | The export job (T1). Parameters: `dataset`, `format`, `tenant`, `notify_email`. Runs on pool `exports-pool`. |
| `src/exports/streaming_csv.py` | `StreamingCsvWriter` (T2): keyset pagination plus a streaming writer; memory stays under 300 MB. |
| `src/exports/xls_writer.py` | XLS stub; raises `NotImplementedError` above 1M rows. |
| `migrations/0042_export_runs.sql` | Creates table `export_runs` (T3). `export_id` (a UUID) is an idempotency key: a retried job sends no second email and does not overwrite a finished file. Applied to staging only (logged 2026-10-07); **not** in production. |
| `templates/export_ready.html` | The new notification email (T7). Used only when `notify_email` is set. |
| `tests/exports/` | Tests. `test_export_cancel.py::test_export_cancel` is flaky and marked `xfail` (T11). |
| `legacy/crontab.txt`, `docs/cron-mapping.md` | The 14 legacy jobs, and the mapping of 11 of them to JobRunner. |
| Flag `exports.jobrunner.enabled`, table `tenant_flags` | Feature flag, default false, with a per-tenant override in `tenant_flags`. |
| `kv://nimbus/exports/prod/*` | Production runner secrets in the vault. Do not copy them anywhere. |
| Grafana folder "Exports" | Named in the notes as the place for export-duration dashboards (not started). |

**Gotchas (from Alex)**

- The runner pool autoscaler is disabled in staging. If exports queue up, scale the pool manually.
- Dates in `export_runs` are UTC. Legacy cron logs are in local time (Alex wrote "CET").
- **[Suggestion]** "CET" may mean local time with daylight saving. EU clocks go back on Sun 2026-10-25, during Alex's leave, so check the timestamp format in the logs before converting.
- `scripts/deploy.ps1` fails silently if the VPN is down; check `kubectl get pods -n exports` afterwards.

### B3. Tasks

| ID | Task | Status | Depends on | Waiting for |
|----|------|--------|------------|-------------|
| T1 | Job definition for export-dataset | DONE | - | - |
| T2 | Streaming CSV writer | DONE | T1 | - |
| T3 | Idempotency key and `export_runs` migration (staging) | DONE | T1 | - |
| T4 | Apply migration 0042 in production | **BLOCKED** | T3 | A DBA window (Q4; ticket DBA-5521) |
| T5 | XLS export above 1M rows | **BLOCKED** | T2 | Product decision (Q1) |
| T6 | Pool sizing, 3 to 6 workers | **BLOCKED** | T2 | Budget decision (Q2) |
| T7 | Email template approval and wiring | IN PROGRESS | T2 | Marketing (Q3) |
| T8 | Map the 3 unmapped cron jobs | TODO | - | Nothing; the agent can start. Owners are needed to finish (Q5) |
| T9 | Per-tenant rollout: nimbus-internal, then Acme, then all tenants | TODO | T4, T5, T6, T7 | T4 to T7 |
| T10 | Decommission legacy cron | TODO | T8, T9 | T8, T9 |
| T11 | Fix flaky `test_export_cancel` (low priority) | TODO | - | Nothing; the agent can start |

**Order of work (steps 1 to 5 need no decision)**

1. First-session checklist (B2).
2. T8: investigate the 3 unmapped cron jobs.
3. **[Suggestion]** Observability before the rollout: export-duration dashboards and a dead-letter-queue alert. These are Alex's "remaining ideas" and are not in the task list.
4. **[Suggestion]** Draft the T4 pre-checks and post-checks and the T9 runbook (documents only; put them under `docs/` and link them from the Update log).
5. T11 last, time-boxed.
6. When a decision or approval is logged, go to its card: T5 (Q1), T6 (Q2), T7 (Q3), T4 (Q4).
7. **[Suggestion]** On Fri 2026-10-30, write Dana a short status: which of Q1 to Q4 are closed, and the earliest cutover date that is still realistic (Q6).
8. When everything unblocked is done, log it and stop. Do not start blocked work.

#### T4. Apply migration 0042 in production (BLOCKED on Q4; needs a human)

- **State.** `migrations/0042_export_runs.sql` creates `export_runs`. Applied to staging only, not in production. Ticket DBA-5521 is open, with no slot scheduled.
- **Constraint.** DBA windows are Tue and Thu, 22:00 to 23:00 UTC. A person has to book the slot and be reachable during it. You cannot do this step yourself.
- **You can prepare.** Confirm from git history that the file has not changed since it ran on staging. Write the pre-checks and post-checks (table exists; columns and indexes match staging). Once a human has confirmed a slot, put it on DBA-5521.
- **Done when.** `export_runs` in production matches staging, DBA-5521 is updated, and the Update log has an entry.

#### T5. XLS export above 1M rows (BLOCKED on Q1; decision first)

- **State.** `src/exports/xls_writer.py` is a stub that raises `NotImplementedError` above 1M rows. Nothing else is implemented for XLS. Check what the stub does below 1M rows; the notes do not say.
- **Do not implement anything before Q1 is in the Decision log.** If the answer is (c) or something else, get the details from Dana first.
- **If Q1 = (a), ZIP of several XLS files.** Split at no more than 1M rows per file, and make sure each file stays within the 1,048,576-row sheet cap including its header row. Write each file as a stream, not from a full in-memory result (the in-memory approach was OOM-killed at 2M rows, B4). Zip the files, keep the `export_id` idempotency, and test with a small split size so the tests do not generate millions of rows. Time a 4.2M-row export against the 15-minute SLA.
- **If Q1 = (b), no XLS above the cap.** Fail fast with a clear message that points to CSV, instead of the bare `NotImplementedError` the stub raises today. Make sure no partial file and no misleading "ready" email results. Customer communication is for a human to send (B1), not you.
- **Either way.** The legacy job `export_weekly_xls` (T8) may be affected; the name suggests a weekly XLS export (unverified).
- **[Suggestion] While waiting.** A throw-away timing spike of `xlsxwriter` on a 1M-row sheet, so that Q1 can be decided with a real number for the SLA. Do not merge it.
- **Done when.** The chosen behaviour works for a 4.2M-row dataset within the 2 GB container limit and the 15-minute SLA, the tests pass, and the Update log records the outcome.

#### T6. Pool sizing, 3 to 6 workers (BLOCKED on Q2)

- **State.** Pool `exports-pool` has 3 workers. Measurements and the estimate are in B4.
- **After approval.** Scale `exports-pool` to 6 workers in the environment Dana approves. Then re-run the concurrency test (3 exports at once, Acme-sized, same method as on 2026-10-09) and record the duration; the target is under 15 min. How the pool is scaled is not in the notes (B5).
- **[Suggestion] Before approval.** The autoscaler is disabled in staging, so the pool is scaled by hand there. Running the 3-at-once test on 6 staging workers turns the estimate into a measurement for Dana. Scale back to 3 afterwards and log it. To reproduce without customer data, the closest documented command is `python -m exports.cli run --dataset demo --format csv --rows 4200000`; the notes do not say how the 2026-10-09 numbers were produced, so treat the results as indicative.
- **If Dana keeps 3 workers.** Log the accepted SLA risk and close T6 as "decided: no change". Treat T6 as resolved for T9.
- **Done when.** The approved pool size is live and the concurrent test passes the 15-minute SLA, or the result is recorded and Dana informed.

#### T7. Notification email (IN PROGRESS, waiting for Marketing: Q3)

- **State.** `templates/export_ready.html` is wired and used only when `notify_email` is set. The legacy system sent plain text. The draft went to Marketing on 2026-10-12; no answer. Who in Marketing has it is not recorded (B5).
- **When wording or logo comes back.** Change the template, deploy to staging, run an export with `notify_email` set, and check that exactly one email arrives, also after a retry (T3 idempotency). The notes do not say whether the 20 staging exports of 2026-10-13 used `notify_email`, so test it yourself.
- **Done when.** Marketing's approval (who, when) is in the Decision log and the final template is merged.

#### T8. Map the 3 unmapped cron jobs (TODO; no dependencies; start now)

- **State.** `legacy/crontab.txt` has 14 jobs. 11 map one-to-one to JobRunner definitions (`docs/cron-mapping.md`). The 3 unmapped are `export_weekly_xls`, `export_audit` and `export_adhoc`. Nobody on the team knows who owns them.
- **You can do now (read-only).** For each job: the schedule; the command or script it runs; its inputs, outputs and recipients; its last run in the cron logs (local time); what the repo history says about who wrote it. Write a short finding per job, next to `docs/cron-mapping.md`, with a proposed outcome: map to JobRunner, retire, or unknown.
- **A human must.** Confirm the owner and approve "map" or "retire" (Q5). Do not edit or disable any cron entry.
- **Done when.** Each of the 3 jobs has a confirmed owner and a recorded outcome: mapped (a definition in `jobs/` and an entry in `docs/cron-mapping.md`) or retired (the owner's written OK linked in the Update log).
- **Check.** The notes name only `jobs/export-dataset.yaml`. Find out whether "11 map to JobRunner definitions" means 11 separate YAML files or 11 parametrised uses of that one.

#### T9. Per-tenant rollout (TODO; starts only when T4, T5, T6 and T7 are done)

- **Plan (Alex).** `nimbus-internal` first, then Acme, then every other tenant. Switch: feature flag `exports.jobrunner.enabled` (default false) with a per-tenant override in `tenant_flags`.
- **State.** Staging: flag enabled for `nimbus-internal` on 2026-10-13; 20 CSV exports, all fine. Production: nothing done.
- **[Assumption]** "Cutover" on 2026-11-10 means every tenant's scheduled exports run on JobRunner, that is, T9 finished. T10 comes after it and has no date.
- **Prepare now (documents only).** Write a runbook: the exact steps to enable one tenant, the checks after each stage, and how to switch the tenant back. The notes do not say how long a stage should run before the next, so ask Dana to approve the runbook including that.
- **[Suggestion] Checks per stage.** The tenant's next scheduled export runs on JobRunner; its output matches the legacy output (row count at least); the `export_runs` row is complete; exactly one email is sent; duration is within 15 min; the dead-letter queue is empty; `kubectl get pods -n exports` is healthy.
- **Verify in the code before the first production stage.** How legacy cron and JobRunner avoid both running a migrated tenant's exports (duplicate files or emails), and that switching the flag back returns the tenant to the legacy path. The notes cover neither.
- **Each stage needs a human go-ahead** in the Decision log. Acme is the stage to watch: it runs several exports on Monday mornings, the case where 3 workers missed the SLA (Q2).

#### T10. Decommission legacy cron (TODO; needs T8 and T9)

- Only after every tenant is migrated and the 3 unmapped jobs are resolved. Needs an explicit human go-ahead. Nothing to do before then.

#### T11. Fix flaky `test_export_cancel` (TODO; low priority; no dependencies)

- **State.** `tests/exports/test_export_cancel.py::test_export_cancel` fails intermittently on timing: it cancels before the worker has started. Marked `xfail` on 2026-10-08. Alex spent half a day on it and judged more time not worth it.
- **If you pick it up.** Do it last and time-box it. **[Suggestion]** Wait until the run has started before cancelling, instead of sleeping. Also check whether "cancel before start" is something a user can do in production; if so, the test has found a product edge case and should assert the intended behaviour.
- **Done when.** It passes repeatedly (for example 20 runs in a row) and the `xfail` marker is gone, or it stays `xfail` with the reason written next to it.

### B4. What was learned

**Measurements**

| Date | Scenario | Result |
|---|---|---|
| 2026-10-05 | Streaming CSV writer, 5M rows, 1 worker | 6 min; memory under 300 MB |
| 2026-10-09 | Acme's largest dataset (4.2M rows), pool of 3 workers, one export alone | 9.5 min: **passes** the 15-minute SLA |
| 2026-10-09 | Same pool, 3 exports at the same time (Acme's Monday-morning pattern) | 21 min: **fails** the SLA |
| no run recorded | Same test on 6 workers | Alex expects it to pass; estimated cost about +1,200 USD/month |

- All of this is CSV; the XLS writer is a stub.
- Not recorded: the dataset sizes in the 3-at-once run, whether 21 min is the slowest export or the average, and where the 2026-10-09 test ran.
- The 2026-10-05 and 2026-10-09 figures do not line up (5M rows in 6 min on one worker, then 4.2M rows in 9.5 min on three). The notes do not say why. **[Assumption]** Different datasets or environments; do not extrapolate from one to the other.

**Tests.** Last recorded `pytest tests/exports -q`: 212 passed, 1 xfailed (the xfail is `test_export_cancel`). That count is from the 2026-10-05 entry, annotated later, and T3 (logged 2026-10-07) may have added tests. Re-run for the real baseline.

**Staging.** 2026-10-13: flag on for `nimbus-internal`, 20 CSV exports, all fine. Not recorded: XLS, the `notify_email` path, and parallel load with the flag on.

**What works.** Keyset pagination with a streaming writer (T2).

**Dead ends: do not retry**

| Approach | What happened |
|---|---|
| Load all rows into memory, then write the CSV | Fine at 100k rows. At 2M rows the worker was OOM-killed (container limit 2 GB). |
| `LIMIT`/`OFFSET` paging | Gets slower with every page (sequential scan). |

### B5. Not in the notes

| Missing | Why it matters | How to find out |
|---|---|---|
| Which branch holds the work, and whether it is pushed | Unpushed work exists only in Alex's checkout | First-session checklist, step 1. Tell Dana if you find uncommitted work |
| How migration 0042 was applied on staging; a rollback plan; how it will be applied in production | T4 | `scripts/`, `docs/`, DBA-5521; otherwise ask the DBA when the slot is booked |
| Who in Marketing has the draft, and who approves | Q3, T7 | Dana |
| Whether the 11 mapped cron jobs already exist as JobRunner definitions | Scope of T8 and T9 | `jobs/` and `docs/cron-mapping.md` |
| How legacy cron and JobRunner avoid both running a migrated tenant's exports | T9: duplicate files or emails | Read how `exports.jobrunner.enabled` is used in the code; confirm before the first production stage |
| How the pool is scaled, and the production pool and autoscaler settings (the notes say only that the staging autoscaler is off) | T6, Q2 | Pool configuration in the repo or platform docs; otherwise Dana |
| Rollout stage criteria, and how long each stage runs before the next | T9, and whether 2026-11-10 is feasible | Propose them in the T9 runbook; Dana approves |
| Customer communication for any XLS change; who talks to Acme | Q1 | Dana |
| How customers receive a finished export (link, attachment) and any size limit | Q1 option (a): a ZIP of 5 large XLS files | The delivery code path; otherwise Dana |
| What the agent can access: staging VPN, kubectl context, database, Grafana, ticketing, vault | Everything that touches staging | Check in the first session; list the gaps in the Update log |

### B6. Logs

**Decision log.** A decision counts only once it is written here. Add a row for each production go-ahead too (for example "T9, stage 1: nimbus-internal").

| Q | Decision | Decided by | Date | Notes |
|---|---|---|---|---|
| Q1 | open | | | Asked 2026-10-06 |
| Q2 | open | | | |
| Q3 | open | | | Draft sent 2026-10-12 |
| Q4 | open | | | Ticket DBA-5521, not scheduled |
| Q5 | open | | | |
| Q6 | open (target 2026-11-10) | | | |
| Q7 | open (assumed: Dana) | | | |

**Update log.** Append only, newest last.

| Date | By | What changed |
|---|---|---|
| 2026-10-17 | Alex (handoff) | Document created from the work log (to 2026-10-15), the task list and the open questions. |
