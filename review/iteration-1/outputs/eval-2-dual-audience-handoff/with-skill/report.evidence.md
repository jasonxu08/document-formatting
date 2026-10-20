<!-- zone:archive -->
# Evidence and provenance: exports migration handoff

*What this is: the sources behind [report.md](report.md), where each figure comes from and whether it was measured, estimated, inferred or computed, and a dated digest of Alex's work log with the dead ends. Who needs it: anyone checking a number, and an agent looking for what was already tried. It supports the figures in [section 1](report.md#1-the-csv-path-works-on-staging-and-nothing-is-in-production-yet) and [section 2](report.md#2-six-open-questions-and-four-of-them-block-the-rollout) of the report.*

## Sources

*The only inputs. Nothing else was read; in particular the repository `C:\work\nimbus-exports` was not inspected, so paths, commands and file names are as Alex wrote them.*

Folder: `<workspace>\fixtures\handoff\`

| File | What it is |
|---|---|
| `work-log.md` | Alex's dated log, 2026-10-01 to 2026-10-15, plus a "things that bit me" list |
| `tasks.md` | The task table T1 to T11 with statuses and dependencies |
| `open-questions.md` | The six open questions that need a human decision; Q1 to Q6 in the report use the same numbers |

## Claim-to-source table

*Supports the "Measured so far" and "Not proven" table in section 1 and the figures in Q1 to Q6 of section 2.*

| # | Claim | Value | Type | Source |
|---|---|---|---|---|
| 1 | Acme's biggest dataset (4.2M rows), run alone, pool of 3 workers | 9.5 min | measured | work log 2026-10-09 |
| 2 | Same dataset, three exports at the same time | 21 min | measured | work log 2026-10-09 |
| 3 | Acme's SLA | an export completes within 15 min | contract, as quoted by Alex | work log 2026-10-09 |
| 4 | 6 workers fix the overlap case; extra cost | about 1,200 USD per month | estimate, never run | work log 2026-10-09 |
| 5 | Streaming CSV benchmark | 5M rows in 6 min on one worker, memory under 300 MB | measured | work log 2026-10-05 |
| 6 | All rows in memory | worker OOM-killed at 2M rows (2 GB container limit) | observed dead end | work log 2026-10-02 |
| 7 | LIMIT/OFFSET paging | slower with every page (sequential scan) | observed dead end | work log 2026-10-02 |
| 8 | Test suite | 212 pass, 1 xfail | measured; date of the last run not recorded | work log 2026-10-05 (it refers to 10-08) |
| 9 | Internal tenant on staging | 20 CSV exports, all fine | measured | work log 2026-10-13 |
| 10 | Sheet limit in `xlsxwriter` | 1,048,576 rows per sheet | stated in the notes | work log 2026-10-06 |
| 11 | Legacy cron | 14 jobs: 11 mapped, 3 unmapped | counted by Alex | work log 2026-10-15 |
| 12 | Migration 0042 | applied to staging only | stated | work log 2026-10-07 |
| 13 | DBA windows | Tuesdays and Thursdays 22:00-23:00 UTC; ticket DBA-5521 not scheduled | stated | work log 2026-10-14 |
| 14 | The flag switches a tenant from legacy cron to JobRunner | n/a | inferred from the rollout plan | work log 2026-10-13 |
| 15 | Decisions needed by 30 Oct | date after which the cutover is at risk | Alex's estimate | open questions, item 6 |
| 16 | About 5 files for Acme under option (a) | 4.2M rows divided by 1M | computed | work log 2026-10-06 |
| 17 | About 14,400 USD a year for 6 workers | 1,200 times 12 | computed | work log 2026-10-09 |
| 18 | Weekdays, DBA windows and "six working days" between 19 Oct and 10 Nov | calendar | computed, not in the notes | none |

## Work-log digest

*Dated summary of Alex's log. Supports the dead-end rules in [block A](report.md#a-agent-brief-with-rules-and-order-of-work) and the task statuses in section 1.*

| Date | What happened | Note |
|---|---|---|
| 2026-10-01 | Read the JobRunner docs; created `jobs/export-dataset.yaml`; local run works | |
| 2026-10-02 | Loaded all rows into memory, then wrote the CSV: fine at 100k rows, OOM at 2M | dead end, do not retry |
| 2026-10-02 | LIMIT/OFFSET paging: slower with each page | dead end, do not retry |
| 2026-10-05 | Keyset pagination plus streaming writer (`src/exports/streaming_csv.py`); 5M rows in 6 min; 212 tests pass, 1 xfail | T2 done |
| 2026-10-06 | XLS: `xlsxwriter` caps a sheet at 1,048,576 rows; options (a), (b), (c); asked Dana, no answer; only a stub written | Q1 opened |
| 2026-10-07 | `export_id` idempotency key; table `export_runs`, migration 0042 applied to staging only; staging deploy command noted | T3 done |
| 2026-10-08 | `test_export_cancel` flaky, marked `xfail` after half a day | time already spent, low priority |
| 2026-10-09 | SLA runs: 9.5 min alone (pass), 21 min with three at once (fail); 6 workers estimated to fix it | Q2 opened |
| 2026-10-12 | New HTML email template wired in; draft sent to Marketing | Q3 opened |
| 2026-10-13 | Feature flag `exports.jobrunner.enabled`; on for `nimbus-internal` in staging; 20 CSV exports fine; rollout order planned | |
| 2026-10-14 | Production migration needs a DBA window; ticket DBA-5521 opened; production secrets are in the vault | Q4 opened |
| 2026-10-15 | Legacy cron audit: 14 jobs, 11 mapped, 3 unmapped, owner unknown; ideas: Grafana dashboards, dead-letter alert | Q5 opened |
