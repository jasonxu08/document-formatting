<!-- zone:archive -->
# Evidence for the exports migration handoff

*🗄️ Archive - Alex's three original notes (byte-exact copies with checksums), a map from every note entry to where [report.md](report.md) uses it, and the dates and counts the report derives. Supports every figure and date in sections 2 to 4 of the report. Not for skimming.*

**Contents:** [A Original notes and checksums](#a-original-notes-and-checksums) · [B Where each note went](#b-where-each-note-went) · [C Derived dates and counts](#c-derived-dates-and-counts)

### A Original notes and checksums

*🗄️ Archive - the three input files, copied unchanged into `report.data/` on 2026-10-19; the originals were only read. Each copy was compared with its original by SHA-256 and matched.*

| Copy | What it is | Lines | Bytes | SHA-256 |
|---|---|---|---|---|
| [report.data/work-log.md](report.data/work-log.md) | Alex's work log, 2026-10-01 to 2026-10-15, plus "Things that bit me" | 59 | 4594 | `e18488b536f01ace1c6a07ffd2b213c3b3238e6aba7af508d3eae6b267dc0ea2` |
| [report.data/tasks.md](report.data/tasks.md) | Task table T1 to T11 | 15 | 972 | `ea3d4d3bc62f7194b3884444cfb099e1064643f58f87da074e973e86e51bc23a` |
| [report.data/open-questions.md](report.data/open-questions.md) | Open questions Q1 to Q6 | 8 | 1120 | `5d324bf5eb186ec98fd7ccd7ca90d512bbf6a919bee820cd7310956a91149998` |

Re-check from the folder that holds `report.md` (PowerShell): `Get-FileHash report.data\work-log.md -Algorithm SHA256`

### B Where each note went

*🗄️ Archive - one row per entry in the notes, so a reader can confirm that nothing was dropped. "Panel" is the glance panel at the top of the report; "A" is its block A.*

| Note | Entry | Where the report uses it |
|---|---|---|
| work-log | Header: repo path, Python 3.12, goal, cutover target, leave dates | Title, section 1, section 3 Q6 dates table, A (repo root, leave dates in "Not recorded") |
| work-log | 2026-10-01: JobRunner YAML jobs, `export-dataset.yaml`, pool `exports-pool` with 3 workers, local run command | Section 1; A (commands, repo map) |
| work-log | 2026-10-02: in-memory load OOM-killed at 2M rows, LIMIT/OFFSET slower per page | Section 4 (must not); A (dead ends, step 6) |
| work-log | 2026-10-05: keyset pagination, `StreamingCsvWriter`, under 300 MB, 5M rows in 6 min, 212 tests pass, 1 xfail | Section 2 (proven so far); section 3 Q2; A (commands, repo map) |
| work-log | 2026-10-06: XLS row cap, options (a) (b) (c), Alex prefers (a), asked Dana, stub | Panel Q1; section 3 Q1; A (repo map, step 6) |
| work-log | 2026-10-07: `export_id` idempotency key, `export_runs`, migration 0042 on staging only, staging deploy command | Section 3 Q4; A (commands, repo map) |
| work-log | 2026-10-08: flaky `test_export_cancel`, marked xfail, half a day spent | Section 2 (T11); A (step 4) |
| work-log | 2026-10-09: 15-minute SLA, 9.5 min alone, 21 min with 3 at once, 6 workers about +1,200 USD/month | Panel Q2 and risk table; section 3 Q2; A (steps 3 and 7) |
| work-log | 2026-10-12: legacy plain-text email, new template, Marketing approval pending, wiring done, used only when `notify_email` is set | Panel Q3; section 3 Q3; A (step 5) |
| work-log | 2026-10-13: flag `exports.jobrunner.enabled`, `tenant_flags`, `nimbus-internal` on staging, 20 CSV exports fine, rollout order, nothing in production | Section 1; section 2 (proven so far); A (repo map, step 9) |
| work-log | 2026-10-14: DBA window Tue/Thu 22:00-23:00 UTC, ticket DBA-5521 not scheduled, production secrets under `kv://nimbus/exports/prod/*` | Panel Q4; section 3 Q4; section 4; A (limits, step 8) |
| work-log | 2026-10-15: 14 cron jobs, 11 mapped, 3 unmapped and ownerless, decommission rule, remaining ideas (Grafana dashboard, dead-letter alert) | Panel Q5; section 1; section 2 (not on the task list); section 3 Q5; A (steps 2 and 10) |
| work-log | Things that bit me: autoscaler off in staging, UTC versus CET, silent deploy failure without VPN | A (gotchas, step 2) |
| tasks | T1 to T11 with status and dependencies | Section 2 table; the task map; A (ordered steps, definition of done) |
| open-questions | Q1 to Q6 | Panel Decisions block; section 3; A (decision log) |

### C Derived dates and counts

*🗄️ Archive - every weekday, date and count in the report that is computed rather than copied, recomputed with Python's `datetime` on 2026-10-19.*

| Statement in the report | Computation | Result |
|---|---|---|
| Document date is a Monday | 2026-10-19 (system date of the writing session) | Mon |
| Cutover target is a Tuesday | 2026-11-10 | Tue, matches the notes |
| Alex's at-risk line is a Friday | 2026-10-30 | Fri |
| Alex's leave ends Fri 2026-11-06; back Sat 2026-11-07; first working day Mon 2026-11-09 | weekdays of 2026-11-06, 11-07, 11-09; a Monday-to-Friday working week is assumed | Fri, Sat, Mon; one working day (Mon) before Tue 2026-11-10 |
| DBA windows before the target | Tuesdays and Thursdays from 2026-10-19 to 2026-11-10 | Tue 10-20, Thu 10-22, Tue 10-27, Thu 10-29, Tue 11-03, Thu 11-05, Tue 11-10 |
| Work log leave start 2026-10-17 | weekday | Sat; 2026-10-17 to 2026-11-06 is 21 days inclusive, which is "three weeks" |
| Starting "tomorrow" from 2026-10-19 | 2026-10-20 to 2026-11-06 | Tue; 18 days inclusive |
| 3 done, 3 blocked, 1 in progress, 4 todo | count of statuses in tasks.md | T1 to T3, T4 to T6, T7, T8 to T11 = 11 tasks |
| Four tasks wait on other people | T4, T5, T6 blocked plus T7 waiting for Marketing | 4 |
| 14 cron jobs | 11 mapped plus 3 unmapped | 14, matches the notes |
