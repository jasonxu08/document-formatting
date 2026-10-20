# Notes on report.md

## 1. Structure choices and why

- **One file, two readers, one reading order.** Dana's part comes first (§1 status, §2 asks), the agent's part after it (§3 to §8). Dana can stop after the §2 summary table; the agent reads everything. A two-line reader guide at the top says who reads what.
- **§1 opens with a verdict, then evidence.** One-line status ("at risk") with the reason, five short bullets (what works, what is not live, what blocks, what Dana must do, what happens meanwhile), an 11-row task table in plain words, and a dependency diagram. T1 to T11 keep Alex's IDs so they can be cross-checked.
- **§2 is written as asks, not as Alex's list of open questions.** A summary table (ask, needed by, recommendation, what it blocks), then one short card per ask with why, options and consequence. Q1 to Q6 keep Alex's numbering. I put the decision log at the end of §2, next to the questions, so Dana answers in one place and the agent knows where decisions live.
- **A calendar figure**, because the real constraint is the calendar: Alex is back one working day before the target, only two DBA windows remain after the 10-30 checkpoint, and 11-07 is a Saturday. The dependency figure shows that four different inputs gate T9.
- **§3 gives the agent rules, a first-hour checklist and a work queue.** A reader that cannot ask questions tends to either stall (everything looks blocked) or do something unsafe in production. The rules (may do / needs a human / never) and the queue (what is safe to do now, with no decision) address both.
- **§4 is per task:** state, what it waits on, what the agent can do now, done-when. Alex's task table had no acceptance criteria, so I derived them from the notes and tagged anything I invented.
- **§5 and §6 are reference.** File map, commands, environments, measurements, and the dead ends marked "do not retry" are carried over faithfully, because those are what an agent would otherwise repeat.
- **§7 separates my assumptions from gaps in the notes,** and each gap says how to resolve it. Inline tags *(assumption)* and *(suggestion)* mark everything that is not from Alex's notes, so Alex can strip or approve it.
- **Format:** plain Markdown, no HTML, narrow tables, ASCII apart from "§". Both images have full text equivalents (alt text plus the tables and lists around them), so the agent does not need to read pixels. Diagram sources are in `images/src` (Graphviz `.dot`, matplotlib script).

## 2. What I was unsure about

- **Date of writing.** The system clock said 2026-10-17, but the notes say leave starts 2026-10-17 and you said "from tomorrow", so I assumed the document is written Fri 2026-10-16 and that the agent starts Mon 2026-10-19.
- **"Back 7 Nov" is a Saturday.** I assumed Mon 2026-11-09 as the first working day, which leaves one working day before the 11-10 target. If you actually return earlier, §1, Q6 and the calendar need a small edit.
- **What "cutover 2026-11-10" means.** I read it as the day the production rollout starts (internal tenant first). The notes do not say whether it is the start or the end, or how long each stage must soak. Flagged in Q6 and §7.
- **Who decides what.** Only Q1 was explicitly put to Dana. I addressed Q2 (budget) to her too, with "or route it to whoever holds the budget". Marketing's and the DBA contacts are not named in the notes.
- **Agent permissions.** I assumed: branches and staging are fine, production is humans-only, no push to the default branch. None of this is in the notes. Please change §3.1 if your setup differs.
- **Suggestions that go beyond your notes** (all tagged): approving Q2 conditionally on a staging test; the staging test itself (T6); building XLS option (a) on a branch as a hedge if Q1 is still open on 10-23; the DBA and rollout runbooks; aiming for the 10-27 or 10-29 DBA window; the "middle path" of keeping 11-10 for the internal tenant only; a one-hour timebox for T11; the dead-letter-queue alert before the first production tenant. Remove any you disagree with.
- **The "6 workers fixes it" claim.** The notes say it would fix the SLA but record no measurement. I also noticed that 3 exports on 3 workers took 21 min versus 9.5 min alone, which would be odd if each export runs on one worker. I wrote this as a question to check, not as a finding.
- **XLS timing.** The SLA tests were presumably CSV (XLS is only a stub), so the 15-minute SLA is unproven for XLS. Stated as "not yet known".
- **Double-running during rollout.** The notes do not say how legacy cron and JobRunner avoid both running a tenant's export once its flag is on. I listed it as a gap to verify before any production enablement. It may already be handled.
- **The 11 mapped cron jobs.** The notes record only `jobs/export-dataset.yaml` as created. Whether the other 10 mappings have definitions yet is unknown; listed as a gap.
- **T7 status.** Your task list says "in progress"; the work log says the wiring is done. I show it as "waiting on Marketing" and say why.
- **Test baseline.** The 212 passed / 1 xfail figure dates from 2026-10-05, before later work. Marked approximate.
- **I had no access to the repo,** so every path, command and file name is taken from your notes. The `--rows 4200000` idea for a 4.2M-row dataset and "about 5 files" for Acme under option (a) are my inferences and tagged as such.
- **Time zone.** The DBA window conversion assumes Central European time (from "CET" in your cron logs), including the clock change on 2026-10-25.
- **Length.** About 5,800 words. Dana's part is the first ~2,000; the rest is the agent's. If you want it shorter, §5's measurements table and the §7 gap table are the first things I would cut.
