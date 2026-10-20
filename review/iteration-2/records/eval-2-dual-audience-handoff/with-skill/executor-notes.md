# User notes - document-formatting skill, eval 2 (dual-audience handoff), run 1

## 1. Skill instructions I followed

- Read `SKILL.md`, then `assets/skeleton.md`, `references/diagrams.md` and `references/review-rubric.md`, and ran `scripts/check_doc.py` on `report.md` and on the sibling `report.evidence.md`. I did not read anything else in the skill folder.
- **Step 1, audience split.** I sorted every fact into human-read, AI-input or archive before drafting. Human: verdict, six decisions, risks, calendar, assumptions. AI-input: repo map, commands, task board, ordered steps, rules, decision log, panel-refresh list, gaps, definition of done. Archive: benchmarks, XLS options, dead ends, dated log digest, number provenance, calendar arithmetic.
- **Step 2, headline first.** Bottom line, judgment (🟡 go with conditions, medium confidence and its basis), ask (six decisions with who/what/by when/recommendation) and ranked risks were settled before writing.
- **Step 3, two-zone layout** from the skeleton: `<!-- zone:... -->` markers, 👤 START HERE and 🗄️ headings, lettered blocks A-C with an italic "bin" line each, `<details>` for the machine blocks, reading path ("Read next" with minutes and who can stop where), `Next →` signposts, numbered H2s that tell the story.
- **Glance panel:** verdict blockquote, 🧭 decisions blockquote, risk table with severity glyphs, one picture with alt text and caption, reading path. I dropped the optional "Key facts" slot because the verdict, risk table and picture already carried those numbers (the skill allows this) and the 300-word budget was tight.
- **Handoff specifics:** the AI block has current state, the repo root stated once, copy-paste commands, ordered next steps, constraints and dead ends, a definition of done, what to do while decisions are open, where answers are recorded (Decision log), and which panel parts to refresh when status changes.
- **Draw the web:** 11 tasks with 12 dependencies, so I drew a Graphviz PNG (image-first, no Mermaid), kept `report.assets/tasks.dot` beside it, put the edge list in block C, and put the legend in the caption. I viewed the image and re-laid it out.
- **File layout:** AI-input kept inline (collapsed) because the user said the agent works "from this same document" (the skill's exception); archive moved to `report.evidence.md`, which starts with `<!-- zone:archive -->`.
- **Highlight budget, plain blockquotes, no alerts, no machine-local paths, plain-word anchors.**
- **Before delivery:** checker result is 0 Blocker / 0 Major / 0 Minor on `report.md` (panel 298 words, human zone about 2,140 words). The sibling file only gets the checker's informational Minor A1 ("machine/archive-only file: human-zone rules skipped"). I also walked the judge rules (A1, A3, A4, B1-B3, B7, C1-C6, D1-D6, E1-E3, F1-F5) and re-validated all 25 links/anchors with my own script.

## 2. Unclear, contradictory, or not followed (and why)

- **Anchor rule vs heading example.** The skill says link-target headings must be plain words and digits with no punctuation, but its own example of a decision heading ("Q1 Allow XLS above 1M rows? Recommend: split") uses `?` and `:`. I followed the plain-word rule and wrote punctuation-free sentence headings ("Q1 XLS above 1M rows needs a policy and a ZIP of files is recommended"), because I link to them.
- **Panel budget vs a handoff with six decisions.** Verdict, six decision lines, five risks, picture, reading path, a 300-word prose budget and "reading path within 60 lines" are hard to satisfy together. My first draft was 464 words (a Major). I cut the Key facts line, shortened the caption and link texts, and kept the "(suggested)" labels short. This works, but at 298 words it is at the edge.
- **"Section number in the link text so it matches the headings"** conflicts with story-telling headings plus the word budget. I used short link texts ("1 Where things stand") that differ from the long headings. The number matches; the words do not.
- **"Write each fact once"** conflicts with a panel that must summarise, a body that gives options, and an AI block that must be self-sufficient. Some facts (the 21 vs 15 minute SLA, the deadlines, the DBA window) appear two or three times in different roles. No paragraph is repeated verbatim, and I trimmed the worst repeats.
- **Sibling-file threshold (about 60 lines) vs the "agent receives only this file" exception.** The AI block is about 170 lines inline, so `report.md` is long (373 lines), even though collapsed. I judged the exception correct for this request.
- **Where the skill is silent:**
  - A document written on someone's behalf: recommendations are partly the user's and partly mine. I added labels *(Alex)*, *derived*, *suggested*, *assumed* and explained them in section 4.
  - Which date to put on the metadata line when the request date conflicts with the notes. I used "Status as of 2026-10-15" (last log entry) instead of a writing date.
- **Checker gap (feedback):** the 2,600 px width limit would have accepted my first diagram (2,397 px wide), but at 800 px its text was only about 10 px high. I fixed it by switching to a top-to-bottom layout (1,381 px). A check on the effective font size at 800 px would catch this.
- **Bold budget:** I did not count bold facts precisely. Bold is mostly in structural lead-ins and decision lines; running text has little bold.
- I did not draw a second diagram (system architecture or timeline): the calendar is a flat list, so I used a table.

## 3. What I am unsure about

- **Today's date.** The system clock says 2026-10-17, but the user says leave starts "tomorrow" and the notes say 2026-10-17. I avoided committing to a writing date. The document does say Mon 19 Oct is the first working day of the leave and the agent's start ("next week"), which holds under either reading.
- **Who decides what.** The notes name Dana only for Q1 (XLS). I assumed she decides or routes Q2-Q6 and the agent's production approvals; this is stated in section 4 and rule 1 of block A.
- **"Cutover" meaning.** I assumed all tenants on JobRunner (T9 done), with decommissioning (T10) after. If Dana means "cron switched off", Q5's date (6 Nov, suggested) becomes critical.
- **Suggested content not in the notes:** the dates 20 Oct, 27 Oct and 6 Nov; the DBA booking recommendation; the staging re-test before enabling Acme; the T4 pre-flight; the 20-run rule for the flaky test; the branch/PR rule; the rollback hint; and the idea that the internal-tenant stage might need only T4. All are labelled *suggested*, but some may be unwelcome in a handoff.
- **Facts I could not verify** (the repo, staging and production were out of scope): all statuses are "as Alex reported". Examples: whether the work is pushed (branch unnamed), whether the 11 mapped cron jobs already exist as JobRunner definitions, where the pool size is configured, how tenant flags are switched, the production deploy invocation, and "XLS" meaning `.xlsx`.
- **An inconsistency in the notes** I flagged but cannot resolve: 5M rows in 6 minutes on one worker versus 4.2M rows in 9.5 minutes on three workers, which makes "6 workers would fix it" unproven.
- **Rendering.** I validated the PNG and the Markdown structure but could not see the file in VS Code or Azure DevOps. Collapsed blocks with `#### ` headings and tables inside `<details>` should render, but I did not confirm it.
- **Length.** The human zone is about 2,140 words, under the 2,500 limit but long for a skim; the panel and section 2 are meant to be the only parts Dana needs.
