<!-- zone:archive -->
# Exports migration handoff - evidence

*🗄️ Archive - supports [report.md](report.md). Condensed from Alex's work log (1 to 15 Oct 2026), task list and open questions, supplied as `work-log.md`, `tasks.md` and `open-questions.md`. Nothing here was re-run or re-measured; figures are as Alex recorded them. "Derived" marks calendar or arithmetic done while writing.*

## Sources

| Source | What it holds | Used for |
|---|---|---|
| Work log | Dated notes from 2026-10-01 to 2026-10-15 and a list of things that bit Alex | the digest, benchmarks, dead ends and rules |
| Task list | T1 to T11 with status and dependencies | the task map and the Task board |
| Open questions | Q1 to Q6 | the decisions block |

## Performance results

*Supports [Q2 in the report](report.md#q2-three-workers-miss-the-acme-sla-and-six-are-expected-to-fix-it) and the SLA risk in the panel.*

| Date | Test | Rows | Workers | Exports at once | Result | Against the 15-minute SLA |
|---|---|---|---|---|---|---|
| 2026-10-05 | Streaming CSV benchmark | 5M | 1 | 1 | 6 min, memory under 300 MB | no SLA stated for this test |
| 2026-10-09 | Acme's largest dataset | 4.2M | 3 | 1 | 9.5 min | pass |
| 2026-10-09 | Acme's largest dataset | 4.2M | 3 | 3 | 21 min | fail |
| not run | Acme's largest dataset | 4.2M | 6 | 3 | not measured; Alex expects a pass, at about +1,200 USD per month | unknown |

- The 6-worker row is an expectation, not a result: the work log says 6 workers "would fix it" and gives no run.
- The 5M-row run (1 worker, 6 min) and the 4.2M-row run (3 workers, 9.5 min) are not comparable as recorded. The work log gives no dataset width, format or environment for either, so the difference is unexplained.
- Where the SLA tests ran (staging, local or a copy of production data) is not recorded.

## XLS options

*Supports [Q1 in the report](report.md#q1-xls-above-1m-rows-needs-a-policy-and-a-zip-of-files-is-recommended).*

| Option | What the customer gets | Alex's view |
|---|---|---|
| a | One ZIP with several XLS files of 1M rows each | preferred; changes what customers receive, so a product decision is needed |
| b | No XLS for large datasets; customers use CSV | alternative; customers must be told |
| c | Several sheets in one workbook | dropped: the cap applies per sheet and it is confusing |

The Excel library `xlsxwriter` writes at most 1,048,576 rows per sheet; Acme's largest dataset has 4.2M rows, so option a gives 5 files (derived: 4.2M / 1M, rounded up). The stub in `src/exports/xls_writer.py` raises `NotImplementedError` above 1M rows. Alex implemented nothing else for XLS.

## Dead ends

*Supports rule 7 in block A of the report.*

| Date | Approach | Result |
|---|---|---|
| 2026-10-02 | Load all rows into memory, then write the CSV | fine at 100k rows; at 2M rows the worker was OOM-killed (container limit 2 GB) |
| 2026-10-02 | `LIMIT`/`OFFSET` paging | slower with every page (sequential scan) |

The approach that works is keyset pagination with a streaming writer (2026-10-05). Several sheets in one workbook for XLS (option c) was never tried; Alex set it aside on paper, see XLS options.

## Dated digest of the work log

*Supports sections 1 to 3 of the report. Chronology lives here on purpose; the report is ordered by what the reader must decide.*

| Date | What happened | Task or question |
|---|---|---|
| 2026-10-01 | JobRunner docs read. `jobs/export-dataset.yaml` created (parameters `dataset`, `format`, `tenant`, `notify_email`; pool `exports-pool`, 3 workers). Local run works after `docker compose up -d postgres` | T1 |
| 2026-10-02 | Two dead ends: all rows in memory, and `LIMIT`/`OFFSET` paging | see Dead ends |
| 2026-10-05 | Keyset pagination and `StreamingCsvWriter` in `src/exports/streaming_csv.py`; memory under 300 MB; 5M rows in 6 min on one worker; tests 212 pass, 1 xfail | T2 |
| 2026-10-06 | XLS: sheet cap of 1,048,576 rows; options a, b, c; Alex prefers a; asked Dana, no answer; stub in `src/exports/xls_writer.py` | Q1, T5 |
| 2026-10-07 | `export_id` idempotency key; table `export_runs` with `migrations/0042_export_runs.sql`, applied to staging only; staging deploy command recorded | T3 |
| 2026-10-08 | `test_export_cancel` is flaky (cancels before the worker has started); marked xfail after half a day; low priority | T11 |
| 2026-10-09 | SLA tests: 9.5 min alone (pass), 21 min with 3 at once (fail); 6 workers expected to fix it for about +1,200 USD per month | Q2, T6 |
| 2026-10-12 | Legacy emails were plain text; new `templates/export_ready.html`, used only when `notify_email` is set; draft sent to Marketing, no answer | Q3, T7 |
| 2026-10-13 | Flag `exports.jobrunner.enabled` (default false) with per-tenant override in `tenant_flags`; `nimbus-internal` enabled on staging, 20 CSV exports fine; rollout plan internal, Acme, everyone else; nothing in production | T9 |
| 2026-10-14 | Migration 0042 needs a DBA window (Tue and Thu 22:00 to 23:00 UTC); ticket DBA-5521 opened, not scheduled; production secrets are in the vault under `kv://nimbus/exports/prod/*` and must not be copied | Q4, T4 |
| 2026-10-15 | Legacy cron has 14 jobs; 11 map one-to-one (`docs/cron-mapping.md`), 3 are unmapped with unknown owners; decommissioning only after all tenants migrate and the 3 are resolved; ideas: Grafana dashboard, dead-letter-queue alert | Q5, T8, T10 |
| undated | Things that bit Alex: staging autoscaler is disabled; `export_runs` dates are UTC while legacy logs are CET; `scripts/deploy.ps1` fails silently when the VPN is down | rules 9 to 11 in block A |

## Where each number in the panel comes from

*Supports the panel of the report; lets a reader spot-check every figure.*

| Statement in the panel | Value | Source |
|---|---|---|
| Tasks done | 3 of 11 (T1 to T3) | Task list |
| Tasks waiting on other people | 4: T4 blocked, T5 blocked, T6 blocked, T7 in progress and waiting for Marketing | Task list; work log 2026-10-12 for T7 |
| Decisions that block the rollout | 4 of 6: Q4 (T4), Q1 (T5), Q2 (T6), Q3 (T7); Q5 blocks T10 and Q6 is the date | Task list "Depends on" and "Status" columns; open questions 1 to 6 |
| Changes in production | 0 | Work log 2026-10-07 (0042 not applied in production) and 2026-10-13 (nothing done in production) |
| SLA figures | 21 min with 3 parallel exports against 15 min allowed; 9.5 min alone | Work log 2026-10-09 |
| Pool cost | about +1,200 USD per month for 6 workers | Work log 2026-10-09 and open question 2; an estimate |
| XLS cap and Acme size | 1,048,576 rows per sheet; 4.2M rows | Work log 2026-10-06 |
| Files for Acme with option a | 5 | Derived: 4.2M / 1M, rounded up |
| Cron jobs | 14 in total, 11 mapped, 3 unmapped | Work log 2026-10-15 |
| Tests | 212 pass, 1 xfail | Work log 2026-10-05 |
| Decision deadline | 30 Oct | Open question 6 |
| Cutover target | Tue 10 Nov | Work log header; open question 6 |
| Leave | 17 Oct to 6 Nov, back 7 Nov | Work log header; the request |
| Six working days after 30 Oct | 2, 3, 4, 5, 6 and 9 Nov | Derived |
| Dates 20 Oct and 6 Nov for Q4 and Q5 | - | Suggested, not in the notes |

## Calendar arithmetic

*Supports section 3 of the report. Derived while writing; assumes a Monday to Friday week.*

| Fact | Result |
|---|---|
| 2026-10-16 and 2026-10-17 | a Friday and a Saturday |
| Leave from 17 Oct to 6 Nov | 21 days, of which 15 working days (19 Oct to 6 Nov) |
| 7 Nov | a Saturday, so Alex's first working day back is Mon 9 Nov |
| 10 Nov | a Tuesday, as Alex's notes say |
| DBA windows (Tue and Thu) from 19 Oct to 10 Nov | Tue 20, Thu 22, Tue 27 and Thu 29 Oct; Tue 3, Thu 5 and Tue 10 Nov |
| Working days strictly between 30 Oct and 10 Nov | 6 (2 to 6 Nov and 9 Nov) |
| 22:00 to 23:00 UTC in local time | 23:00 to 00:00 CET after the clocks change on Sun 25 Oct; 00:00 to 01:00 CEST before |
