# Scheduled exports migration: handoff

Moving scheduled exports from the legacy cron jobs to the new JobRunner platform, then switching the old cron off. Cutover target: **Tue 2026-11-10**.

> **Dana:** §1 and §2 are for you: where things stand, and the six items that need you.
>
> **Coding agent:** read everything. §3 is your brief. Alex cannot be asked anything: use this document, the repo and the decision log at the end of §2.

- **Owner:** Alex, on leave Sat 2026-10-17 to Fri 2026-11-06 and **not reachable**. "Back 7 Nov" is a Saturday, so Mon 2026-11-09 is assumed to be the first working day *(assumption)*.
- **Status as of:** 2026-10-15, the last entry in Alex's notes. All dates are 2026. Built from Alex's work log, task list and open-questions list; T1 to T11 and Q1 to Q6 keep their numbering. Everything the notes contain is in this document; what they leave out is listed in §7.
- **Repo:** `C:\work\nimbus-exports` (Python 3.12). **Escalation:** Dana (manager). No delegate for production steps is named yet (Q4).
- Text marked *(assumption)* or *(suggestion)* was added while drafting this document and is not from Alex's notes. Verify assumptions; treat suggestions as recommended, not mandatory.

## 1. Where things stand

**Status: at risk.** The 2026-11-10 cutover needs four things from outside the engineering work (Q1 to Q4), and none is settled yet. Alex's view: they need to be settled by Fri 2026-10-30.

- **What works:** CSV exports stream from the database: 5M rows in 6 minutes on one worker, under 300 MB of memory. An idempotency key is in place so a retried job does not send a second email or overwrite a finished file (the table behind it exists in staging only). The internal tenant `nimbus-internal` ran 20 CSV exports in staging without a failure.
- **What is not live:** nothing has changed in production. Migration 0042 is not applied there, the feature flag is off for every tenant, and all 14 legacy cron jobs still run as before.
- **What blocks the rollout:** T4 to T7 each wait on a different kind of input: a DBA slot, a product decision, a budget decision and Marketing's approval. None has a date. After Fri 10-30 only 6 working days and 2 DBA windows remain before the target, and Alex is back only on Mon 11-09 *(assumed)*.
- **What Dana needs to do:** six items (§2). Most urgent: name someone for the DBA window (Q4) and decide the XLS question (Q1). The rest by Fri 10-30.
- **While Alex is away:** the coding agent continues everything that needs no decision and does not touch production (§3, §4). Its first results (facts on the 3 unmapped cron jobs, a staging check of the worker pool) should be in the progress log (§8) by about Fri 10-23 *(suggestion)*.

3 of 11 tasks are done, 4 are blocked or waiting on other people, and 4 are not started (T8 can start now).

| ID | Task | Status | Waiting on |
|----|------|--------|------------|
| T1 | Job definition `export-dataset` | Done | - |
| T2 | Streaming CSV writer | Done | - |
| T3 | Idempotency key and `export_runs` migration | Done, staging only | - |
| T4 | Apply migration 0042 in production | Blocked | DBA window, ticket DBA-5521 (Q4) |
| T5 | XLS export above 1M rows | Blocked | Product decision (Q1) |
| T6 | Pool from 3 to 6 workers | Blocked | Budget decision (Q2) |
| T7 | Email template: approval and wiring | Waiting. Wiring is done, approval is missing | Marketing (Q3) |
| T8 | Map the 3 unmapped cron jobs | Not started. Can start now | Owners unknown (Q5) |
| T9 | Per-tenant rollout: `nimbus-internal`, then Acme, then everyone | Not started | T4, T5, T6, T7 |
| T10 | Decommission legacy cron | Not started | T8, T9 |
| T11 | Fix flaky `test_export_cancel` | Not started, low priority | - |

![Task dependency map. T1 feeds T2 and T3. T2 feeds T5, T6 and T7. T3 feeds T4. T4, T5, T6 and T7 must all finish before T9. T8 and T9 must finish before T10. T11 is independent. T1 to T3 are done, T4 to T6 are blocked, T7 is waiting on Marketing, T8 to T11 are not started.](images/task-dependencies.png)

*Arrows point from a task to what it unlocks. The four blockers in front of T9 are four different kinds of input: a DBA slot, a product decision, a budget decision and Marketing's approval.*

## 2. What Dana needs to decide or unblock

Six items. Q1 to Q4 gate the rollout: it cannot start until all four are resolved. Q1 was put to Dana on 2026-10-06 and Q3 was sent to Marketing on 2026-10-12; neither had an answer on 2026-10-15. The agent cannot clear any of these. Write each answer in the decision log at the end of this section, or tell the person running the agent.

| # | Ask | Needed by | Recommendation | Blocks |
|---|-----|-----------|----------------|--------|
| Q1 | Decide how XLS exports above 1,048,576 rows are delivered | Fri 10-30; sooner is better | (a) ZIP of several XLS files (Alex's preference) | T5, then T9 |
| Q2 | Approve a 6-worker pool, about +1,200 USD/month | Fri 10-30 | Approve, conditional on a staging check *(suggestion)* | T6, then T9 |
| Q3 | Get Marketing to approve the email wording and logo | Fri 10-30 | - | T7, then T9 |
| Q4 | Name someone to book and attend the DBA window for migration 0042 | Book now. Thu 11-05 is the last usable window | Aim for Tue 10-27 or Thu 10-29 *(suggestion)* | T4, then T9 |
| Q5 | Help find the owner of 3 unmapped legacy cron jobs | Before the old cron is switched off; no date | - | T8, then T10 |
| Q6 | Keep or move the 2026-11-10 date | Checkpoint Fri 10-30 | - | - |

Q1 and Q4 are the most urgent: Q1 needs implementation time after the decision, and DBA slots come only twice a week.

![Calendar from Mon 2026-10-19 to Sun 2026-11-15. Alex is on leave until Fri 11-06. DBA windows fall on Tue 10-20, Thu 10-22, Tue 10-27, Thu 10-29, Tue 11-03 and Thu 11-05. The decision checkpoint is Fri 10-30 and the cutover target is Tue 11-10. Alex's first working day back is assumed to be Mon 11-09.](images/calendar.png)

### Q1. Decide how XLS exports above 1,048,576 rows are delivered

- **Why:** an XLS sheet holds at most 1,048,576 rows (the library in use, `xlsxwriter`, cannot exceed it). Acme's biggest dataset has 4.2M rows and would break on migration. Today the code simply fails for such exports.
- **Options:**
    - (a) Several XLS files of 1M rows each, delivered as a ZIP. Acme would receive about 5 files *(4.2M rows / 1M, rounded up)*. Customers receive something different from before, which is why this needs a product decision.
    - (b) No XLS for large datasets; customers use CSV.
    - (c) Several sheets in one file. Dismissed: each sheet is still capped, and it is confusing.
- **Recommendation:** (a), Alex's preference.
- **Not yet known:** how long a 4.2M-row XLS export takes. The SLA tests so far were presumably CSV, because XLS is not implemented. The agent measures it after the decision (§4, T5).

### Q2. Approve 6 workers instead of 3

- **Why:** Acme's contract requires an export to finish within 15 minutes. On 3 workers, Acme's biggest dataset (4.2M rows) takes 9.5 minutes when it runs alone (passes) and 21 minutes when three run at once (fails). Acme runs several at once on Monday mornings.
- **Ask:** approve about +1,200 USD/month (an estimate) for 6 workers, or route it to whoever holds the budget (the notes do not say who).
- **Caveat:** the notes record no measurement on 6 workers. *(suggestion)* Approve conditionally: the agent tests three parallel exports on 6 workers in staging in week 1 (§4, T6) and reports the times in the progress log (§8) before production changes.
- **If refused:** Acme would likely miss its SLA at Monday peaks. Moving Acme (T9, stage 2) would then need a separate decision.

### Q3. Get Marketing to approve the notification email

- **Why:** the new HTML email (`templates/export_ready.html`) replaces the legacy plain-text email. Marketing must approve the wording and the logo. Alex sent the draft on 2026-10-12. The wiring is done; only the approval is missing.
- **Ask:** get a named Marketing approver to approve it or send changes.
- **If still open on Fri 10-30:** Dana's call: wait (the date moves) or go live without Marketing's sign-off.
- **If Q1 is (a):** the email may have to mention a ZIP; tell Marketing *(suggestion)*.

### Q4. Name someone to book and attend the DBA window for migration 0042

- **Why:** migration 0042 creates `export_runs`, the table that makes retries safe. It is applied in staging, not in production, and production needs a DBA window (Tue and Thu, 22:00-23:00 UTC). Ticket DBA-5521 (2026-10-14) is not scheduled. Someone must book a slot and be reachable during it; Alex is on leave.
- **Ask:** name that person now. T4 does not depend on Q1 to Q3.
- **Windows before the target:** Tue 10-20, Thu 10-22, Tue 10-27, Thu 10-29, Tue 11-03, Thu 11-05. *(suggestion)* Aim for 10-27 or 10-29 and keep 11-03 and 11-05 as fallbacks; after 10-30 only two windows are left.
- **Local time:** 22:00-23:00 UTC is 23:00-00:00 CET, or 00:00-01:00 CEST (next day) until the clocks change on Sun 10-25 *(assuming Central European time, as in Alex's cron logs)*.

### Q5. Help find the owner of 3 unmapped legacy cron jobs

- **Why:** the legacy crontab has 14 jobs. 11 map one-to-one to JobRunner definitions. Three do not (`export_weekly_xls`, `export_audit`, `export_adhoc`) and nobody on the team knows who owns them. Each must be mapped or retired before the old cron is switched off (T10). They do not block the 2026-11-10 rollout.
- **Ask:** help find the owners. The agent first collects facts on each job (what it runs, when, for whom, when it last ran) to make that conversation easy (§4, T8).

### Q6. Keep or move the 2026-11-10 date (checkpoint Fri 10-30)

- **Why:** the rollout (T9) cannot start until T4 to T7 are done. Alex's view: if Q1 to Q4 slip past 10-30, the date is at risk. After that day only 6 working days and two DBA windows (11-03, 11-05) remain, and Alex is back only on Mon 11-09, so plan the cutover without Alex.
- **Ask:** on 10-30, check the table in §1. If any of T4 to T7 is still blocked, decide whether to move the date.
- **Middle path** *(suggestion)*: the first stage (`nimbus-internal`, CSV) looks like it needs only T4; Acme also needs T5 and T6, and T7 matters wherever `notify_email` is used. Keeping 11-10 for the internal tenant and moving the later stages is an alternative to moving the whole date. Alex's task list requires T4 to T7 before any rollout and the notes do not analyse this, so confirm it before relying on it.
- **Confirm what "cutover" means, and the rollout order.** This document reads "cutover" as the day the production rollout (T9) starts, `nimbus-internal` first *(assumption)*; the notes do not say how long Acme and the remaining tenants take after that. The order (internal tenant, then Acme, then everyone else) is Alex's own plan and is not known to have been reviewed. Acme, the customer with a contractual SLA, would be the first external tenant.

### Decision log

Dana (or the delegate) fills this in. The agent acts only on decisions recorded here, and records any decision given to it in a session.

| Q | Answer format | Decision | Decided by | Date | Notes |
|---|---------------|----------|------------|------|-------|
| Q1 | (a) ZIP of XLS files, or (b) CSV only | | | | |
| Q2 | Approved or refused, with the budget limit | | | | |
| Q3 | Approved as is, or changes requested; the approver's name | | | | |
| Q4 | Name of the person; the booked window (date) | | | | |
| Q5 | Owner of each of the 3 jobs, or "retire" | | | | |
| Q6 | Keep 2026-11-10, or the new date; confirm the meaning of "cutover" and the rollout order | | | | |

## 3. Agent brief

Alex is unreachable until the leave ends (Fri 2026-11-06); do not wait for Alex. Work from this document, the repo and the decision log (§2). Dana is the escalation point, reached through whoever runs this session; "tell Dana" in this document means say it to that person and write it in the progress log (§8). If you have no channel to her, write the question in the progress log and carry on with unblocked work. A delegate may be named (Q4).

### 3.1 Rules

**You may do on your own**

- Change code, tests, docs and runbooks in the repo on a branch. Do not push to the default branch; assume a human reviews and merges *(assumption)*.
- Run the local environment and the tests. Keep the suite green: run `pytest tests/exports -q` before and after code changes.
- Deploy to staging and scale the staging pool (needs the staging VPN).
- Read the legacy cron files and logs.

**A named human must do or approve it (you prepare, they execute)**

- Anything in production: applying migration 0042 (T4), changing `tenant_flags` or the pool size, deploying, the rollout (T9), any change to the legacy cron (T10). No production procedure is recorded; do not improvise one.
- Contacting Marketing, the DBA team or customers.
- Merging or shipping XLS work (T5) before Q1 is recorded in the decision log (§2).

**Never**

- Copy secrets. Production secrets live in the vault under `kv://nimbus/exports/prod/*`. Never put their values in files, logs, commits, tickets or this document.
- Change the default of `exports.jobrunner.enabled` (it is `false`) or enable it in production outside the T9 plan. Never enable it in production before migration 0042 is applied there.
- Disable or remove legacy cron jobs before T8 and T9 are done.
- Retry the dead ends in §6.

**When something is unclear:** take the conservative, reversible option, write it in the progress log (§8), and raise it with Dana if it blocks you. Act only on decisions recorded in §2; a Q without a recorded answer means the task behind it stays blocked.

### 3.2 First hour

1. Check the repo state. The notes do not record the branch or whether everything is pushed. Do not discard uncommitted work; if there is any, commit it to a new branch first *(suggestion)*.

   ```powershell
   cd C:\work\nimbus-exports
   git status
   git branch -vv
   git log --oneline -10
   ```

2. Activate the Python 3.12 environment (setup is not described in the notes; if none exists, create one from the repo's dependency file), then start the database, run the tests and a local export:

   ```powershell
   docker compose up -d postgres
   pytest tests/exports -q
   python -m exports.cli run --dataset demo --format csv --rows 100000
   ```

   The last recorded result was 212 passed and 1 xfailed, written down on 2026-10-05, before later changes. Treat it as approximate and note the actual baseline in the progress log (§8). If anything other than the known `xfail` fails, record it there and tell Dana before you change code.
3. Read `jobs/export-dataset.yaml`, `migrations/0042_export_runs.sql`, `src/exports/streaming_csv.py`, `src/exports/xls_writer.py`, `docs/cron-mapping.md` and `legacy/crontab.txt`.
4. Check the decision log (§2) for answers recorded since this document was written.

### 3.3 Work queue

| # | Work | Needs | Output |
|---|------|-------|--------|
| 1 | Baseline: git state and tests (§3.2) | Nothing | Baseline in §8 |
| 2 | T8: fact sheet on the 3 unmapped cron jobs | Nothing | Fact sheet and proposal in `docs/cron-mapping.md`, summary in §8. Aim for Fri 10-23 *(suggestion)* |
| 3 | T6: staging check, 3 parallel 4.2M-row exports on 6 workers | Staging access | Measured times in §8. Aim for Fri 10-23 *(suggestion)* |
| 4 | T4: review migration 0042, write the DBA runbook | Nothing | Runbook for the human who attends the window. Aim for Fri 10-23 *(suggestion)* |
| 5 | T9: draft the rollout and rollback runbook | Nothing | `docs/rollout-runbook.md` *(suggestion)* |
| 6 | T5: implement the answer to Q1 once it is recorded. If Q1 is still open on Fri 10-23, start option (a) on a branch as a hedge | Q1, or nothing for the hedge | A branch. Nothing merged before Q1 is recorded |
| 7 | T7: apply Marketing's changes | Q3 | Updated template |
| 8 | Optional: export dashboard and dead-letter-queue alert (§4) | Nothing | Dashboard, alert |
| 9 | T11: flaky cancel test, last | Nothing | Fixed test, or findings |
| 10 | By Thu 10-29: bring §1 up to date so Dana's checkpoint on Fri 10-30 has current facts *(suggestion)* | Nothing | Current §1 and §8 |

If everything left is blocked, say so in the progress log and stop. Do not execute T9 or T10.

### 3.4 Keeping this document current

At the start of every session, check the decision log (§2). After each session, update the status in the §1 table and add a dated line to the progress log (§8). Add newly found facts and gaps to §7. Do not rewrite Alex's facts in §5 and §6; correct them in the progress log.

## 4. Remaining work, task by task

"Human" means a named person, not the agent.

### T4. Apply migration 0042 in production (human-run)

- **State:** `migrations/0042_export_runs.sql` creates `export_runs`, the table behind the idempotency key. Applied in staging on 2026-10-07. **Not applied in production.** Ticket DBA-5521 was opened on 2026-10-14 and is not scheduled.
- **Waiting on:** a DBA window (Tue and Thu, 22:00-23:00 UTC) and a named human to attend (Q4).
- **You can do now:**
    - Read the SQL and confirm it only adds what `export_runs` needs: no changes to existing tables, no long locks *(suggestion)*.
    - Check what the code does if `export_runs` is missing while the flag is off. That tells you whether the runner may be deployed before the migration *(suggestion)*.
    - Write a short runbook for the DBA: pre-checks, how to apply (the team's migration process is not recorded), post-checks (table, columns and indexes match staging), rollback. Dropping the table is safe only while no tenant has the flag on; the DBA confirms *(suggestion)*.
- **Done when:** the migration is applied in production, the post-check is recorded in §8, and a human has updated DBA-5521.

### T5. XLS export above 1,048,576 rows (waits for Q1)

- **State:** only a stub exists in `src/exports/xls_writer.py`. It raises `NotImplementedError` above 1M rows; what it does below that is not recorded. `xlsxwriter` caps a sheet at 1,048,576 rows, and the header row counts.
- **If Q1 is (a), a ZIP of XLS files of 1M rows each:**
    - Split by row count. Every part is its own XLS file with a header row. Bundle the parts into one ZIP. Acme would get about 5 files.
    - Stream every part. Do not load all rows into memory: that was a dead end (§6). Reuse the keyset pagination of `StreamingCsvWriter`. `xlsxwriter` has a constant-memory mode worth checking *(suggestion)*.
    - If the notification email names the file, make sure it works for a ZIP (coordinate with T7).
- **If Q1 is (b), CSV only above the cap:** replace the `NotImplementedError` with a handled outcome: refuse the request early and tell the user to choose CSV. Never truncate silently. Telling customers is a human task.
- **Either way:**
    - Test at the boundary: cap minus 1, cap, and cap plus 1 rows.
    - Run a 4.2M-row export in staging, alone and three at once, with timings and peak memory (container limit 2 GB). Expect XLS to be slower than CSV; there is no XLS timing yet. Report to Dana whether it stays inside the 15-minute SLA.
- **Hedge** *(suggestion)*: if Q1 is still open on Fri 10-23, build (a) on a branch. Do not merge or ship until the decision log says (a). If the answer is (b), discard the branch.
- **Done when:** behaviour matches the recorded decision, tests pass, the stub is gone and the timings are reported.

### T6. Pool from 3 to 6 workers (waits for Q2)

- **State:** the pool `exports-pool` has 3 workers. Measured with Acme's 4.2M-row dataset on 3 workers: 9.5 minutes alone (pass), 21 minutes with three at once (fail). The SLA is 15 minutes. 6 workers are expected to fix it for about +1,200 USD/month. **That is not measured.**
- **You can do now, in staging only, with no approval needed** *(suggestion)*:
    1. Find out how the pool size is set and how to scale it by hand in staging. The notes do not say; the staging autoscaler is off.
    2. Scale staging to 6 workers, submit three exports of a 4.2M-row dataset at the same time (how jobs are submitted: see §7) and record every duration. The 2026-10-09 setup is not recorded; the demo dataset with `--rows 4200000` is the likely way to get that size *(assumption)*.
    3. Find out whether one export runs on one worker or is split across workers. If it is one worker per export, three exports on three workers should not take twice as long as one. That would point to another bottleneck, for example the database, which more workers will not fix. Tell Dana before money is spent.
    4. Scale staging back to 3.
- **Pass:** all three exports finish within 15 minutes, with margin.
- **When Q2 is approved:** a human sets the production pool to 6. Watch the first Monday-morning peak.
- **If Q2 is refused:** mark T6 "won't do". Tell Dana that Acme's SLA exposure remains. Do not propose enabling Acme on JobRunner without her decision.

### T7. Email template: approval and wiring (waits for Q3)

- **State:** `templates/export_ready.html` is wired in and used only when `notify_email` is set. The legacy system sent plain text. Alex's task list says "in progress", but per the work log only the approval is missing. The draft went to Marketing on 2026-10-12.
- **Waiting on:** Marketing, via Dana (Q3). Nothing for you to do until an answer is in the progress log (§8).
- **When approved:** apply any wording or logo changes, run the tests, send a test notification from staging to an internal test address, and check that a retried export sends only one email. If Q1 is (a), make sure the wording works for a ZIP.
- **Done when:** the approval (who and when) is in §8 and the template matches it.

### T8. Map the 3 unmapped cron jobs (can start now)

- **State:** `legacy/crontab.txt` has 14 jobs. 11 map one-to-one to JobRunner definitions, listed in `docs/cron-mapping.md`. Unmapped: `export_weekly_xls`, `export_audit`, `export_adhoc`. Nobody on the team knows who owns them (Q5).
- **You can do now:** for each job collect the command or script it runs, the schedule, parameters and tenants, where the output goes and who receives it, and when it last ran successfully. Cron logs are in CET (§6). Write a short fact sheet in `docs/cron-mapping.md` with a proposal: map it (a JobRunner definition following the 11 existing mappings) or retire it.
- **Lead:** `export_weekly_xls` probably produces XLS files *(guess from the name)*. Check whether it can exceed the 1,048,576-row cap and whether it is what Acme receives; that bears on Q1 and T5.
- **Do not** disable or edit any legacy cron entry. Owner sign-off goes through Dana.
- **Done when:** all 14 jobs are accounted for in `docs/cron-mapping.md`, and each of the 3 has an owner and a decision (map or retire).

### T9. Per-tenant rollout (human-run, you prepare; needs T4, T5, T6, T7)

- **State:** staging only. `nimbus-internal` is enabled in staging, and 20 CSV exports ran fine on 2026-10-13. Production is untouched.
- **Order:** `nimbus-internal`, then Acme, then everyone else. This is Alex's plan; the notes do not show it was reviewed with anyone (Q6). The switch is the per-tenant override of `exports.jobrunner.enabled` in table `tenant_flags`; the default stays `false`. How "everyone else" is switched (per-tenant rows or the default) is not recorded; settle it with Dana in the runbook.
- **You can do now:** draft `docs/rollout-runbook.md` *(suggestion)*. Preconditions: T4 to T7 done, vault secrets present, pool size. Steps per stage. Checks before the next stage: exports succeed, durations are inside the SLA, nothing lands in the dead-letter queue, one email per export, XLS behaves as decided in Q1. Rollback: set the tenant's flag back to `false` and confirm the legacy cron serves that tenant again (verify this, see §7).
- **Check first:** how the legacy cron and JobRunner avoid both running a tenant's export once its flag is on (§7).
- **Acme timing:** Acme's SLA risk is the Monday-morning peak, so watch the first Monday after Acme is switched.
- **Done when:** every tenant has the flag on in production with successful runs, and Acme's Monday peak has met the 15-minute SLA.

### T10. Decommission legacy cron (human-approved; needs T8 and T9)

- Only after every tenant is migrated and the 3 unmapped jobs are resolved (Alex). No date is set. Do not start this.
- *(suggestion)* Disable first, delete later, and keep `legacy/crontab.txt` in version control so the old schedule can be restored.

### T11. Fix flaky `test_export_cancel` (low priority)

- **State:** `tests/exports/test_export_cancel.py::test_export_cancel` is flaky: the cancel arrives before the worker has started. It is marked `xfail`. Alex spent half a day on it and decided more time is not worth it.
- **If you pick it up** (last, only when nothing else is open): timebox it to about an hour *(suggestion)*. Either make the test wait until the worker is running before it cancels, or define what "cancel before start" should do and test that as its own case. A user can cancel before the worker starts, so check the product handles it; if it does not, that is a real bug rather than a flaky test.
- **Done when:** the test passes repeatedly (for example 20 runs in a row *(suggestion)*) and the `xfail` marker is removed. Otherwise leave it `xfail` and record what you found in §8.

### Not in the task list (optional)

- A Grafana dashboard for export duration, in the folder "Exports".
- An alert on the dead-letter queue.

Both are ideas from Alex's last notes, with no owner or dependency. *(suggestion)* The dead-letter-queue alert is worth having before the first production tenant is enabled.

## 5. Reference

### Where things are

| Path or name | What it is |
|--------------|------------|
| `jobs/export-dataset.yaml` | The JobRunner job definition. Parameters: `dataset`, `format`, `tenant`, `notify_email`. Runs on pool `exports-pool` (3 workers). |
| `src/exports/streaming_csv.py` | `StreamingCsvWriter`: keyset pagination plus a streaming writer. Memory stays under 300 MB. |
| `src/exports/xls_writer.py` | XLS stub. Raises `NotImplementedError` above 1M rows. |
| `migrations/0042_export_runs.sql` | Creates `export_runs`. Applied in staging only. |
| `export_runs` (table) | One row per run. `export_id` (UUID) is the idempotency key, so a retried job sends no second email and does not overwrite a finished file. Timestamps are UTC. |
| `templates/export_ready.html` | Notification email. Used only when `notify_email` is set. |
| `exports.jobrunner.enabled` | Feature flag, default `false`. Per-tenant override in table `tenant_flags`. |
| `tests/exports/` | Test suite. `test_export_cancel.py::test_export_cancel` is marked `xfail`. |
| `scripts/deploy.ps1` | Deploy script (PowerShell). |
| `legacy/crontab.txt` | The 14 legacy cron jobs. |
| `docs/cron-mapping.md` | Mapping of 11 legacy jobs to JobRunner definitions. |
| `kv://nimbus/exports/prod/*` | Production secrets in the vault. Never copy. |
| Grafana folder "Exports" | Planned home for export dashboards. |

### Commands

All from the repo root, in PowerShell.

```powershell
docker compose up -d postgres                       # needed before local runs and tests
python -m exports.cli run --dataset demo --format csv --rows 100000
pytest tests/exports -q                             # Postgres from docker compose must be running

# Staging deploy. Needs the staging VPN.
./scripts/deploy.ps1 -Env staging -Service exports-runner
kubectl get pods -n exports                         # always check afterwards, see §6
```

### Environments

| Environment | Access | State |
|-------------|--------|-------|
| Local | `docker compose up -d postgres` | Works. Demo dataset through the CLI. |
| Staging | Staging VPN. Namespace `exports`. | Migration 0042 applied. Flag on for `nimbus-internal`. Pool autoscaler disabled. |
| Production | Humans only | Migration 0042 not applied. Flag off for every tenant. Legacy cron runs everything. |

### Measurements

| What | Setup | Result | Date |
|------|-------|--------|------|
| Load all rows in memory | 100k rows | Fine | 10-02 |
| Load all rows in memory | 2M rows, container limit 2 GB | OOM-killed | 10-02 |
| Streaming CSV, keyset pagination | 5M rows, one worker | 6 min, under 300 MB | 10-05 |
| Acme dataset, runs alone | 4.2M rows, 3 workers | 9.5 min. Pass (SLA 15 min) | 10-09 |
| Acme dataset, three at once | 4.2M rows, 3 workers | 21 min. Fail | 10-09 |
| Acme dataset, three at once | 4.2M rows, 6 workers | Not measured | - |
| `nimbus-internal` in staging | CSV | 20 exports, all fine | 10-13 |
| Test suite | `pytest tests/exports -q` | 212 passed, 1 xfailed (approximate, see §3.2) | 10-05 |

The 5M-row benchmark and the Acme tests are different setups; do not extrapolate between them.

### People and tenants

- **Dana:** Alex's manager. Escalation point. Q1 was put to her on 2026-10-06.
- **Marketing:** approves the email wording and logo (Q3).
- **DBA team:** production migration windows, ticket DBA-5521 (Q4).
- **Acme:** customer with a 4.2M-row dataset. Contract SLA: an export completes within 15 minutes. Runs several exports on Monday mornings.
- **`nimbus-internal`:** internal tenant. First in the rollout. Enabled in staging.

## 6. Dead ends and gotchas

**Dead ends. Do not retry.**

- **Loading all rows into memory, then writing the CSV.** Fine at 100k rows; at 2M rows the worker was OOM-killed (container limit 2 GB). Use the streaming writer.
- **`LIMIT`/`OFFSET` paging.** Each page is slower than the last (sequential scan). Use keyset pagination.
- **Multiple sheets for XLS (Q1 option c).** Each sheet is still capped, and it is confusing.
- **More time on `test_export_cancel`.** Alex spent half a day; see T11.

**Gotchas**

- `scripts/deploy.ps1` **fails silently if the VPN is down.** After every deploy run `kubectl get pods -n exports` and check the pods.
- The runner-pool **autoscaler is disabled in staging.** If exports queue up, scale manually.
- **Timezones:** timestamps in `export_runs` are UTC. Legacy cron logs are in local time (CET). Convert before comparing. The clocks change on Sun 2026-10-25, inside the leave period, so check whether the log timestamps follow daylight saving time. DBA windows are in UTC.
- **Secrets:** never copy production secrets anywhere (§3.1).

## 7. Assumptions and gaps

### Assumptions made while drafting

1. This document was written on Fri 2026-10-16, the last working day before leave. The notes end on 2026-10-15.
2. "Back 7 Nov" is a Saturday; Mon 2026-11-09 is Alex's first working day.
3. The agent starts on Mon 2026-10-19 ("next week" in Alex's words), so "week 1" means 10-19 to 10-23.
4. "Cutover" on 2026-11-10 means the production rollout (T9) starts that day with `nimbus-internal`. The notes do not say whether it means the start or the end of the rollout, or how long each stage must run before the next.
5. The agent has no authority over production. Humans run T4, T9, T10 and production pool changes. The agent works on branches and a human reviews them.
6. The agent runs on a machine where `C:\work\nimbus-exports` exists with Python 3.12, Docker, and (for staging) VPN and `kubectl` access.
7. The team is on Central European time (the legacy cron logs are in CET). Used only for converting the DBA window.
8. Dana owns Q1 and Q2 or can route them. The notes do not name who holds the budget.

### Gaps in the notes: verify, do not guess

The git state and the current test baseline are also unknown; the first hour (§3.2) covers them.

| Gap | How to resolve | Matters for |
|-----|----------------|-------------|
| How jobs are submitted to JobRunner in staging, and where the JobRunner docs are (Alex read them 2026-10-01) | Repo `README`, `docs/`, `scripts/`; otherwise ask Dana | T6, T9 |
| Where the pool size (3 workers) is set, and how to scale by hand | `jobs/export-dataset.yaml`, `scripts/deploy.ps1`, the `exports` namespace | T6 |
| Production deploy procedure, and how `tenant_flags` is changed in production | Not recorded. Humans with production access. Do not improvise | T9 |
| Whether legacy cron and JobRunner both run a tenant's export once its flag is on (duplicate exports and emails) | Read the legacy cron scripts and the flag handling; test in staging before any production enablement | T9 |
| Whether all 11 mapped cron jobs already have JobRunner definitions in `jobs/` (the notes record only `export-dataset.yaml`) | Compare `docs/cron-mapping.md` with `jobs/`. Anything missing is untracked work: add a task and tell Dana | T9 |
| What the XLS stub does at or below 1M rows, and what the legacy system does today for XLS above the cap | Read `src/exports/xls_writer.py`, its tests and the legacy export code | T5, Q1 |
| How many exports Acme really runs at once on Mondays ("several"), and whether 6 workers is enough | Query `export_runs` (UTC) and the legacy cron logs (CET) | T6, Q2 |
| Which format the 2026-10-09 SLA tests used (presumably CSV) | Re-run with the format stated (§4, T5 and T6) | Q1, Q2 |
| Whether the production autoscaler is on, and whether scheduled or automatic scaling could meet the SLA for less than a fixed pool of 6. Not investigated | Check the production pool config; report to Dana | Q2 |

## 8. Progress log

The agent adds one line per session, newest last. Decisions go in the decision log at the end of §2.

| Date | By | What happened | Next |
|------|----|---------------|------|
| 2026-10-15 | Alex | Last entry in the work log: legacy crontab reviewed, 3 of 14 jobs unmapped, decommissioning not started. | See §3.3 |
