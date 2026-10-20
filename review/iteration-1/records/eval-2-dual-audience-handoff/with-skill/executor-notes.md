# User notes - eval 2 (dual-audience handoff), with skill, run 1

Deliverables: `report.md`, `report.evidence.md`, `report.assets/task-map.png`, `report.assets/task-map.dot`, and this file.

## 1 Skill instructions I followed

- Read `SKILL.md`, `assets/skeleton.md`, `references/diagrams.md` and `scripts/check_doc.py`; nothing else in the skill folder.
- Treated the output as "Large" (a saved report). Step 1: sorted the notes into human-read, AI-input and archive before drafting. Step 2: fixed the headline first (bottom line, verdict and confidence, ask, ranked risks). Step 3: two-zone layout from the skeleton, with the 👤 and 🗄️ zone headings, `<!-- zone:... -->` markers, lettered `<details>` blocks A to H that each open with a "what it is" line, and a blank line after `</summary>` and `</details>`.
- Glance panel in the skill's order: 🟡 verdict blockquote with confidence, 🧭 decision blockquote (who, by when, recommendation, cost of being wrong), risk table with the severity glyph first, key facts, one picture with caption, numbered "Read next" with minutes and who may stop where.
- Reading path: headings that state the point, a one-line question under each section, `Next →`, links from panel claims to sections and from evidence back to claims, one name per entity (Q1 to Q6, T1 to T11, "legacy cron", "blockers"), plain-word headings for every link target, defined terms on first use.
- Draw the web: the trigger fired (11 tasks in a dependency web). Wrote nodes and edges first (all 12 edges come from the "Depends on" column), rendered a Graphviz PNG, kept the `.dot` beside it in `report.assets/`, one focal point (T9 thick outline, red and amber blockers), a verb on every edge, a legend inside the image, and a caption. Looked at the PNG at full size and downscaled to 800 px. Put the edge list in block H.
- Highlight budget: plain blockquotes, no `> [!NOTE]`, no HTML styling, bold only on labels and a few key items.
- Deliver: file first; images in `report.assets/` with relative forward-slash links; the long archive material in a sibling `report.evidence.md`.
- Before-you-deliver: `check_doc.py` on `report.md` gives 0 errors and 0 warnings. I checked the evidence-to-report anchors with a small script because the checker ignores cross-file anchors. Did the thirty-second, skim, zone, diagram, honesty and duplication passes by hand; for duplication I replaced repeated numbers, dates and the secrets path with pointers.
- Chat reply: per your rules it is only the file list, not the skill's "glance panel in miniature".

## 2 Unclear, contradictory, or not followed

- **AI-input length rule vs your request.** The skill says AI-input over about 60 lines in total goes into a sibling file. You said the agent works "from this same document" and must not need to ask anything. I kept the agent material inline in `report.md` (blocks A to F, about 100 non-blank lines, each block at or under 25 non-blank lines, collapsed, at the bottom) and moved only the archive (evidence, work-log digest) to the sibling file. The skill does not say which rule wins when the user wants one self-sufficient document.
- **One decision vs six asks.** The skeleton has a single-sentence "Decision needed". I had six open questions with different owners and dates, two of which are actions (chase Marketing, name a person). I used a bulleted list inside the 🧭 blockquote and headed it "Decisions and actions".
- **"Fits on one screen".** Verdict, six asks, five risks, key facts, a picture and a reading path cannot fit one screen. I kept every element and accepted about two screens.
- **"A verb on every edge"** gives 12 identical "unblocks" labels on a pure dependency graph. I followed the rule literally; it is readable but noisy. Allowing one legend verb for uniform edges would be cleaner.
- **"Write each fact once"** conflicts with a glance panel that by design restates the body. I treated the panel as a linked summary and kept full detail in one place (for example the SLA numbers are in Q2; elsewhere there are pointers or short restatements).
- **Absolute paths.** The notes use repo-relative paths. I gave the absolute repo root once (`C:\work\nimbus-exports`) and said that every path is relative to it, instead of rewriting each path.
- **Documents that agents update.** The skill covers only "keep the glance panel true after your edit". The Answer column (how the agent learns Dana's decisions), the progress log, and the rule to flip the verdict to 🔴 after 30 Oct if Q1 to Q4 are open are my additions, not skill instructions.
- **`check_doc.py` on the evidence file** reports 2 WARN (no `zone:human`, no "Read next"). They do not apply to an archive-only file. The checker also does not validate cross-file anchors.
- **"Save where the repo's conventions say"** did not apply: you named the folder and told me not to look at the repository.

## 3 What I was unsure about

- **Today's date.** I wrote Fri 2026-10-16, because your notes say leave starts 2026-10-17 and you said "tomorrow", but the system clock read 2026-10-17 (+08:00). 7 Nov is a Saturday, so I wrote that your first working day is Mon 9 Nov.
- **What "cutover" means.** I assumed T9 (every tenant on JobRunner) is complete on 10 Nov and T10 follows. The notes do not define it.
- **Who decides what.** I assumed Dana answers Q1, Q2 and Q6 and names the person for Q4. Your notes state a preference only for Q1; my recommendations for Q2, Q3, Q4 and Q6 are my reading of your numbers. Please confirm before Dana reads them.
- **Agent access.** I assumed the agent has staging access, no production access, and may only commit to a new branch. The notes say nothing about this.
- **The flag.** That `exports.jobrunner.enabled` switches a tenant from legacy cron to JobRunner is inferred. Block E tells the agent to verify it, including whether a flagged tenant could also still run from legacy cron.
- **Unknowns I could not resolve from the notes:** which branch holds the work and whether it is pushed; whether the 11 mapped definitions exist in `jobs/`; where the pool size is set and how to scale it; how the staging benchmarks were started; valid `-Env` values other than `staging`; rollout stage durations and rollback; the Marketing contact. All are listed for the agent.
- **Additions from me, not from your notes:** the T8 steps, the "20 runs in a row" and half-day time-boxes, the `xlsxwriter` `constant_memory` hint (my own knowledge, untested), "look in `docs/` for the JobRunner docs", and the CET/CEST conversion of the 22:00 UTC DBA window (assumes the team is in CET, as the legacy cron logs suggest).
- **Unverified paths and commands.** I did not have the repository, so every path and command is copied from your notes.
- **Answer column.** It assumes Dana will edit the table or tell the agent in a session; that may not match how your team works.
