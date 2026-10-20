# Work log - scheduled exports migration (Alex)

Repo: `C:\work\nimbus-exports` (Python 3.12). Goal: move scheduled exports from the legacy cron jobs to the new JobRunner platform. Cutover target: Tuesday 2026-11-10. I am on leave 2026-10-17 to 2026-11-06.

## 2026-10-01
- Read the JobRunner docs. Jobs are YAML definitions in `jobs/`, executed by workers in a runner pool.
- Created `jobs/export-dataset.yaml` (parameters: dataset, format, tenant, notify_email). Pool is `exports-pool`, currently 3 workers.
- Local run works: `python -m exports.cli run --dataset demo --format csv --rows 100000` (needs `docker compose up -d postgres` first).

## 2026-10-02
- First approach: load all rows into memory, then write the CSV. Fine at 100k rows. At 2M rows the worker was OOM-killed (container limit 2 GB). Dead end, do not retry.
- Looked at paging with LIMIT/OFFSET. Gets slower with each page (seq scan). Dead end.

## 2026-10-05
- Switched to keyset pagination + a streaming writer: `src/exports/streaming_csv.py` (class `StreamingCsvWriter`). Memory stays under 300 MB.
- Benchmark with 5M rows: 6 min on one worker.
- Tests: `pytest tests/exports -q` (Postgres from docker compose must be running). 212 pass, 1 xfail (see 10-08).

## 2026-10-06
- XLS support. The library `xlsxwriter` cannot write more than 1,048,576 rows per sheet. Customers with bigger datasets (Acme: 4.2M rows) would break.
- Options I see: (a) split into several XLS files of 1M rows in a ZIP, (b) drop XLS for large datasets and tell customers to use CSV, (c) multiple sheets (still capped per sheet, confusing). I prefer (a) but this changes what customers receive, so a product decision is needed. Asked Dana, no answer yet.
- Implemented nothing for XLS beyond a stub in `src/exports/xls_writer.py` that raises `NotImplementedError` above 1M rows.

## 2026-10-07
- Retries and idempotency. Added `export_id` (UUID) as an idempotency key so a retried job does not send a second email or overwrite a finished file.
- New table `export_runs`, migration `migrations/0042_export_runs.sql`. Applied to STAGING only. NOT applied in production.
- Staging deploy command: `./scripts/deploy.ps1 -Env staging -Service exports-runner` (PowerShell, run from repo root, needs the staging VPN).

## 2026-10-08
- `tests/exports/test_export_cancel.py::test_export_cancel` is flaky (timing: cancels before the worker has started). Marked `xfail` for now. Spent half a day on it, not worth more. Low priority.

## 2026-10-09
- Performance against the SLA. Acme's contract says an export must complete within 15 minutes.
- Acme's biggest dataset (4.2M rows): 9.5 min on a pool of 3 workers when it runs alone. PASS.
- With 3 exports running at the same time (Acme runs several on Monday mornings): 21 min. FAIL.
- Pool of 6 workers would fix it: estimated +1,200 USD/month. Needs a budget decision.

## 2026-10-12
- Notification email. The legacy system sent plain text. New template: `templates/export_ready.html`. Marketing must approve the wording and logo. Sent them the draft, no answer yet.
- Wiring is done for the template; it is used only when `notify_email` is set.

## 2026-10-13
- Feature flag `exports.jobrunner.enabled`, default false. Per-tenant override in table `tenant_flags`.
- Enabled for the internal tenant `nimbus-internal` in staging. Ran 20 exports in CSV, all fine.
- Rollout plan I had in mind: internal tenant, then Acme, then everyone else. Nothing done in production yet.

## 2026-10-14
- Production migration `0042` needs a DBA window (Tuesdays and Thursdays 22:00-23:00 UTC). Ticket DBA-5521 opened. Not scheduled.
- Secrets for the production runner are in the vault under `kv://nimbus/exports/prod/*`. Do not copy them anywhere.

## 2026-10-15
- Legacy cron: `legacy/crontab.txt` has 14 jobs. 11 map one-to-one to JobRunner definitions (listed in `docs/cron-mapping.md`). 3 are unmapped: `export_weekly_xls`, `export_audit`, `export_adhoc`. I do not know who owns them.
- Decommissioning of the old cron has not started. It must only happen after every tenant is migrated and the 3 unmapped jobs are resolved.
- Remaining ideas: dashboards for export duration (Grafana folder "Exports"), alert on the dead-letter queue.

## Things that bit me (for whoever continues)
- The runner pool autoscaler is disabled in staging. If exports queue up, scale manually.
- Dates in `export_runs` are UTC. Legacy cron logs are in local time (CET).
- `scripts/deploy.ps1` fails silently if the VPN is down; check `kubectl get pods -n exports` afterwards.
