# Dual-audience handoff · iteration 2

[← Iteration 2](README.md) · [Review dashboard](../README.md) · [Example documents](../../examples/02-dual-audience-handoff/README.md)

> **Prompt given to both agents**
>
> I'm on leave from tomorrow for three weeks (back 7 Nov). My notes on the exports migration are in examples/02-dual-audience-handoff/input/ (work log, task list, open questions). Turn them into a handoff document. My manager Dana will skim it to see where things stand and what she needs to decide, and an AI coding agent will pick up the remaining work next week from this same document, so it has to be able to continue without asking me anything.

## Result

| | Without the skill | With the skill |
|---|---|---|
| Assertions passed | **9 / 22** (41%) | **22 / 22** (100%) |
| Automatic checker | ❌ 0 Blockers · 4 Majors · 2 Minors | ✅ 0 Blockers · 0 Majors · 1 Minor |
| First section, words (the checker's panel measure; budget about 300) | 677 | 298 |
| Words in the human-read zone (the whole document when there are no zones) | 4,229 | 2,140 |
| Cold reader, first 60 lines | 6 / 6 key facts | 5 / 6 key facts |

## What the reader sees first

| Without the skill | With the skill |
|---|---|
| ![first screen without the skill](../../examples/02-dual-audience-handoff/images/without-skill-first-screen.png) | ![first screen with the skill](../../examples/02-dual-audience-handoff/images/with-skill-first-screen.png) |
| [Open the document](../../examples/02-dual-audience-handoff/without-skill/report.md) | [Open the document](../../examples/02-dual-audience-handoff/with-skill/report.md) |

## Assertion scorecard

Each assertion was graded by an agent that read the document and cited evidence; ✅ passed, ❌ failed. The evidence for every failure is below, and the full evidence for every assertion is in the raw `grading.json` of each run.

| Assertion | Without | With |
|---|:-:|:-:|
| A1 Zones marked and ordered | ✅ | ✅ |
| A3 Machine blocks collapsed | ❌ | ✅ |
| B1 Reading path | ❌ | ✅ |
| B2 Order follows understanding | ❌ | ✅ |
| B3 Headings carry the story | ❌ | ✅ |
| C1 Conclusion first | ❌ | ✅ |
| C2 Compact glance panel | ❌ | ✅ |
| C3 Verdict, decisions, risks complete | ❌ | ✅ |
| C4 Nothing invented | ❌ | ✅ |
| C5 Numbers trace to sources | ✅ | ✅ |
| D1 Diagram drawn | ✅ | ✅ |
| D2 Coverage and truth | ❌ | ✅ |
| D3 D4 Image-first and legible | ✅ | ✅ |
| D5 D6 Explained and reproducible | ❌ | ✅ |
| E1 E2 Honesty and labelling | ❌ | ✅ |
| F3 Chat reply is the panel | ❌ | ✅ |
| Automatic checks (gate) | ❌ | ✅ |
| Dana's view | ✅ | ✅ |
| Cutover risk | ✅ | ✅ |
| Agent-ready | ✅ | ✅ |
| Guardrails and protocol | ✅ | ✅ |
| Cold reader at least 80% | ✅ | ✅ |

<details>
<summary>The full text of every assertion in this scorecard</summary>

- A1 Zones marked and ordered: the document opens with a human zone whose heading or banner names its audience (a pointer line in the header does not count), and any AI-input or archive material sits last in its own labelled zone; nothing for people follows machine content
- A3 Machine and archive blocks are collapsed in details blocks and plain-headed, each opening with a line that names its bin (AI input or archive) and what it supports; long material sits in a sibling file behind a pointer
- B1 Reading path: within 60 lines of the title there are at least 3 links to sections, each saying what the reader gets, and a line saying who can stop where
- B2 Order follows understanding: the mental model comes first, terms are defined before the first section that uses them, and chronology lives in the archive
- B3 The H2 headings of the human zone, read alone, give the outline or the argument; question and decision headings carry their answer or ask
- C1 Conclusion first: the glance panel opens the document straight after the title and one metadata line, and its bottom line states the conclusion itself, not what the document covers
- C2 Compact panel: about 300 words of prose or fewer (tables and picture excluded; mechanical.json gives panel_words), one line per decision and per risk, and verdict, decisions and top risks fit the first screen
- C3 Verdict, decisions and risks are complete and loud in the panel: the verdict has a glyph, confidence and basis; each decision has who, what, by when and a recommendation; at most 5 ranked risks, each with severity and consequence
- C4 Nothing invented: no verdict, decision or risk block without grounding in the sources, any ranking is traceable, empty slots are omitted
- C5 Numbers in the panel trace to the sources (spot-check at least three); derived, merged or de-duplicated numbers say so
- D1 Diagram drawn: the eleven related tasks T1-T11 and their dependencies are shown in at least one diagram
- D2 Coverage and truth: every one of the eleven tasks appears in at least one diagram, every drawn dependency edge exists in tasks.md, and inferred edges are dashed and captioned
- D3 D4 Image-first and legible: the diagram a human sees first is an embedded image file that exists (PNG or SVG), not only a Mermaid or other code block, and viewing it at about 800 px wide shows legible labels, no overlap and no empty glyph boxes
- D5 D6 Explained and reproducible: alt text, a caption saying how to read the diagram and its takeaway, a legend where colour carries meaning, the relation stated (verbs on edges, or once when all edges are alike), the diagram source file beside each image, and an edge list or equivalent in the archive
- E1 E2 Honesty: every judgment has a confidence level and its basis; content not in the inputs (assumptions, suggestions, inferences) is labelled as such; unknowns are listed
- F3 Chat reply: the executor's final reply (final_reply.md) is the glance panel in miniature (verdict, decisions, top risks, the file path, where to start) and does not paste the document
- Automatic checks: check_doc.py on report.md and every sibling Markdown file reports no Blocker and at most two Majors in total
- Dana's view: the panel says where things stand (how many of the 11 tasks are done, blocked and open) and lists the decisions she must make (XLS above 1M rows, pool size and its cost, DBA window, email template, owner of the 3 cron jobs), each with an option or a recommendation
- Cutover risk: states that the 10 Nov cutover depends on tasks T4 to T7 and slips if the decisions land after about 30 Oct
- Agent-ready: the AI-input part holds exact commands and paths from the log (for example pytest tests/exports -q, the staging deploy command, jobs/export-dataset.yaml) and an ordered next-steps list that respects the task dependencies
- Guardrails and protocol: the AI-input part says what not to do (no in-memory or OFFSET retries, no migration 0042 in production outside the DBA window, no copying secrets) and what to do while decisions are open and where answers are recorded
- Cold reader: a fresh reader who sees only the first 60 lines and the images in them recovers at least 80% of the key facts (cold-reader test, scored separately)

</details>

### Evidence for the failed assertions

<details>
<summary>❌ <b>A3 Machine blocks collapsed</b> · without the skill</summary>

**Assertion:** A3 Machine and archive blocks are collapsed in details blocks and plain-headed, each opening with a line that names its bin (AI input or archive) and what it supports; long material sits in a sibling file behind a pointer

**Grader evidence:** mechanical.json: details_blocks = 0. Part B (L75-L297, about 3,300 words: command block, tables, eight task cards, logs) is fully expanded inline; there is no &lt;details&gt;/&lt;summary&gt; anywhere. No opening line names a bin ('AI input' or 'archive') and what it supports (L77 opens 'You are picking this up from Alex...'). Nothing long sits behind a pointer in a sibling file: outputs holds only report.md, user_notes.md (not referenced from report.md) and assets/.

</details>

<details>
<summary>❌ <b>B1 Reading path</b> · without the skill</summary>

**Assertion:** B1 Reading path: within 60 lines of the title there are at least 3 links to sections, each saying what the reader gets, and a line saying who can stop where

**Grader evidence:** mechanical.json: internal_links = 0 and a B1 Major ('only 0 in-document link(s) in the 60 lines after the title'). L6-L7 are plain-text lines: 'Who reads what: Dana reads Part A ...; the AI coding agent reads Part A for context, then works from Part B' and 'Contents: Part A: A1 bottom line, A2 what is needed, ...'. They list section names only: no links, nothing saying what the reader gets from each section, and the stop point is only implied.

</details>

<details>
<summary>❌ <b>B2 Order follows understanding</b> · without the skill</summary>

**Assertion:** B2 Order follows understanding: the mental model comes first, terms are defined before the first section that uses them, and chronology lives in the archive

**Grader evidence:** Not clearly met on any of the three clauses. (1) The system's mental model ('What this is: ... 14 legacy cron jobs to JobRunner, the new job platform: YAML definitions in jobs/, executed by workers in a runner pool', L107) arrives after Part A (L11-L74) and after the B1 ground rules (L79-L103); Part A opens with status. (2) Terms are used before they are defined: 'JobRunner' (L1, L62) is first explained at L107; 'cutover' (L4, L5, L17, A2, A3) is first defined, as an \[Assumption], at L220; B1 leans on forward references ('the dead ends in B4', 'Decision log, B6'). (3) There is no archive zone; the dated measurements table and the Update log sit inside the AI zone. In its favour: the work-log chronology was not copied; the document is organised by status, ask and task.

</details>

<details>
<summary>❌ <b>B3 Headings carry the story</b> · without the skill</summary>

**Assertion:** B3 The H2 headings of the human zone, read alone, give the outline or the argument; question and decision headings carry their answer or ask

**Grader evidence:** Only two H2s exist: 'Part A: Status and decisions (for Dana)' and 'Part B: Continuing the work (for the AI agent)'. The human zone's single H2 is a topic label. Its H3s ('A1. Bottom line', 'A2. What is needed from Dana', 'A3. Key dates', 'A4. Detail behind the two decisions') and H4s ('Q1: XLS above 1,048,576 rows', 'Q2: pool size') are labels too; none carries a conclusion or the ask. Read alone they give a table of contents, not the argument.

</details>

<details>
<summary>❌ <b>C1 Conclusion first</b> · without the skill</summary>

**Assertion:** C1 Conclusion first: the glance panel opens the document straight after the title and one metadata line, and its bottom line states the conclusion itself, not what the document covers

**Grader evidence:** The conclusion is not straight after the title and one metadata line. Before 'A1. Bottom line' (L13) come five header bullets (L3-L7: status date, leave dates, cutover target, 'Who reads what', 'Contents', the last two describing what the document covers), a 'Convention' blockquote (L9) and the Part A heading (L11): about 184 words by my count of L1-L10. The bottom line itself opens with a description ('Where it stands. Built: the export job, a streaming CSV writer ...', L15); the conclusion ('The 2026-11-10 cutover is at risk if Q1 to Q4 are not settled by Fri 2026-10-30', L17) is the third bullet and there is no verdict line. The content is conclusion-bearing and sits within the first 20 lines, but the placement test is not met. Mechanical C1 did not fire because check_doc.py treats the L9 blockquote as the first panel element (only 5 text lines before it).

</details>

<details>
<summary>❌ <b>C2 Compact glance panel</b> · without the skill</summary>

**Assertion:** C2 Compact panel: about 300 words of prose or fewer (tables and picture excluded; mechanical.json gives panel_words), one line per decision and per risk, and verdict, decisions and top risks fit the first screen

**Grader evidence:** mechanical.json: panel_words = 677 against a budget of about 300 (C2 Major at L11: 'the first section runs to about 677 words'). There is no short panel: the human zone is a run of sections (A1 about 208 words of bullets; A2 table plus three prose paragraphs at L37-L41; A3; A4 detail). Decision rows are multi-sentence rather than one line (Q1 L29 has three sentences, Q5 L33 four), and there is no per-risk line. The bottom line, the asks table and the single risk do start inside the first 60 lines (L15-L19, L27-L35), but not compactly.

</details>

<details>
<summary>❌ <b>C3 Verdict, decisions, risks complete</b> · without the skill</summary>

**Assertion:** C3 Verdict, decisions and risks are complete and loud in the panel: the verdict has a glyph, confidence and basis; each decision has who, what, by when and a recommendation; at most 5 ranked risks, each with severity and consequence

**Grader evidence:** No verdict glyph and no confidence anywhere (a grep for confidence/high/medium/severity/consequence and status glyphs finds only 'low priority' for T11). The only verdict-like statement is the L17 'Risk' bullet: the cutover is 'at risk if Q1 to Q4 are not settled by Fri 2026-10-30 (Alex's estimate ...)'; it gives a basis but no confidence and no consequence. The A2 decisions (L29-L35) carry what and by when ('who' only through the table heading), but 'Alex's view', the recommendation column, is '-' for Q3, Q4, Q5 and Q7. Only one risk is stated; none is ranked or given a severity.

</details>

<details>
<summary>❌ <b>C4 Nothing invented</b> · without the skill</summary>

**Assertion:** C4 Nothing invented: no verdict, decision or risk block without grounding in the sources, any ranking is traceable, empty slots are omitted

**Grader evidence:** Most of the panel is grounded: the 3/1/3/4 status counts match tasks.md, Q1-Q6 map one-to-one to open-questions.md items 1-6, and the 30 Oct risk comes from item 6 (the Q1-Q4 reading is flagged at L37). But (a) Q7 ('Confirm who the agent escalates to ...', L35) is a decision block with no grounding in the three input files; the document itself says 'Q7 is not in Alex's notes' (L37), and its 'By when', Mon 2026-10-19, appears in no source. (b) Empty slots are not omitted: 'Alex's view' is '-' for Q3, Q4, Q5 and Q7 (L31, L32, L33, L35) and Q5's date reads 'No date'. The additions are disclosed, but the assertion is literal about ungrounded decision blocks and empty slots.

</details>

<details>
<summary>❌ <b>D2 Coverage and truth</b> · without the skill</summary>

**Assertion:** D2 Coverage and truth: every one of the eleven tasks appears in at least one diagram, every drawn dependency edge exists in tasks.md, and inferred edges are dashed and captioned

**Grader evidence:** Not every task appears on its own. The PNG and assets/task-status.dot (node 'built') collapse T1, T2 and T3 into one 'T1 to T3' node: T2 never appears as a task ID or node, and the T1-&gt;T2 and T1-&gt;T3 dependencies of tasks.md are not drawn. The single node's four outgoing edges to T4-T7 blur tasks.md (T4 depends on T3 only; T5, T6 and T7 depend on T2 only), and the grouping is not captioned as a simplification (caption L23 only says snapshot and source). The other drawn edges (T4-T7 -&gt; T9, T9 -&gt; T10, T8 -&gt; T10) exist in tasks.md and no edge is invented; there are no inferred edges, so none needed dashing. With the burden on the assertion ('every one of the eleven tasks appears'), the merged node does not meet it.

</details>

<details>
<summary>❌ <b>D5 D6 Explained and reproducible</b> · without the skill</summary>

**Assertion:** D5 D6 Explained and reproducible: alt text, a caption saying how to read the diagram and its takeaway, a legend where colour carries meaning, the relation stated (verbs on edges, or once when all edges are alike), the diagram source file beside each image, and an edge list or equivalent in the archive

**Grader evidence:** Partly met, so not met. Present: long informative alt text (L21); an in-image colour legend (done / in progress / blocked on a person / not started); the source assets/task-status.dot beside the PNG, with a regenerate command; the Depends-on column of the B3 table (L152-L164) is a text equivalent of the edge list, though it sits in Part B, not in an archive. Missing: the visible caption (L23, 'Snapshot of 2026-10-17, drawn from assets/task-status.dot. The table in B3 is the live status.') says neither how to read the diagram nor what it shows; edges are unlabelled arrows and no visible text says what an arrow means (only the alt text says 'must finish before'). The document has no archive for the edge list.

</details>

<details>
<summary>❌ <b>E1 E2 Honesty and labelling</b> · without the skill</summary>

**Assertion:** E1 E2 Honesty: every judgment has a confidence level and its basis; content not in the inputs (assumptions, suggestions, inferences) is labelled as such; unknowns are listed

**Grader evidence:** E2 is largely met: the Convention (L9) defines \[Assumption] and \[Suggestion] and they are used throughout (for example L19, L67, L73, L81, L103, L147, L170-L174, L220, L249); unknowns are listed in B5 'Not in the notes' (L264-L277, ten rows) and in 'Not measured' / 'Not recorded' notes (L72, L248). Gaps: some additions are untagged (L181 T4 'Write the pre-checks and post-checks', L199 T6 'If Dana keeps 3 workers ... close T6', L205, L221 runbook). E1 is not met: no judgment carries a confidence level (no 'confidence', 'high', 'medium' or 'low' anywhere). The main judgment, cutover 'at risk if Q1 to Q4 are not settled by Fri 2026-10-30' (L17), cites a basis (Alex's estimate) but no confidence; 'People, not code' (L16) has neither.

</details>

<details>
<summary>❌ <b>F3 Chat reply is the panel</b> · without the skill</summary>

**Assertion:** F3 Chat reply: the executor's final reply (final_reply.md) is the glance panel in miniature (verdict, decisions, top risks, the file path, where to start) and does not paste the document

**Grader evidence:** final_reply.md describes the document's structure instead of giving its panel in miniature, though it does not paste the document. Missing: any verdict or status (no '3 of 11 done, 3 blocked', no 'cutover at risk'), the decisions themselves (only 'a table of the seven things she needs to decide or unblock (each with a deadline)' with none named), and the top risk. Present: the outputs folder path and file list. Where to start is only implied ('Part A is for Dana'). The rest of the reply asks the user to check the date arithmetic, the reading of the 30 Oct deadline and the Q7 escalation assumption.

</details>

<details>
<summary>❌ <b>Automatic checks (gate)</b> · without the skill</summary>

**Assertion:** Automatic checks: check_doc.py on report.md and every sibling Markdown file reports no Blocker and at most two Majors in total

**Grader evidence:** mechanical.json gate.passed = false: 0 Blockers, 4 Majors (A1 no &lt;!-- zone: --&gt; markers; B5 0 in-document links, at least 5 expected; B1 0 links in the 60 lines after the title; C2 first section about 677 words vs 300) and 2 Minors (F2 human zone about 4,229 words; A2 shell commands in the human zone at L119). Only report.md was scanned (there are no report.*.md siblings; user_notes.md is not one). Four Majors already exceed the limit of two.

</details>

## Cold reader

A fresh agent saw only the first 60 lines of each document (and the images in them), answered six fixed questions, and was scored against key facts derived from the *inputs*, so both arms face the same list.

| Key fact | Without | With |
|---|:-:|:-:|
| **K1** Status is at risk: the 10 Nov cutover depends on four blockers (T4 to T7) that need input from outside engineering by about 30 Oct. | ✅ | ✅ |
| **K2** Progress: 3 of 11 tasks are done (T1 to T3); CSV export works in staging; nothing is live in production yet. | ✅ | ✅ |
| **K3** Dana must decide or unblock: XLS policy above 1M rows (recommend a ZIP of 1M-row files), pool size 3 to 6 workers (about 1,200 USD per month), Marketing's email approval, a DBA window for migration 0042, and an owner for the 3 unmapped cron jobs. | ✅ | ✅ |
| **K4** Acme's 15-minute SLA fails when three exports run in parallel (21 minutes); a single export takes 9.5 minutes. | ✅ | ✅ |
| **K5** Alex is away until 7 Nov (a Saturday) and cannot be asked; an AI agent continues the work from this document. | ✅ | ✅ |
| **K6** The agent can continue work that needs no decision (for example mapping the 3 cron jobs) but must not touch production. | ✅ | ❌ |

Raw answers: [without the skill](records/eval-2-dual-audience-handoff/without-skill/coldreader-answers.md) · [with the skill](records/eval-2-dual-audience-handoff/with-skill/coldreader-answers.md)

- Scoring note, without the skill: K6 is borderline: credited from 'T8 can start now' plus 'who approves production steps'.
- Scoring note, with the skill: The panel says the agent investigates the unmapped cron jobs first, but not what the agent may do alone or that it must not touch production.

## What the graders said about the assertions themselves

Graders were asked to critique the test, not only the document. These are the suggestions they raised for this scenario (the skill and the assertions were revised from them; see [how the skill evolved](../skill-evolution/README.md)).

<details>
<summary><b>Grader critique, with the skill run</b> (8 suggestions)</summary>

- **Dana's view** — Ambiguous whether the picture can carry the task tally. This panel gives 'three done / four blocked or waiting' only in image alt text and per-node labels, and 'Three of eleven' only in the H2 just below the panel; the open count (4) and the total (11) are never stated in panel prose. Reword to say 'in text or in the picture', or require a prose tally such as '3 of 11 done, 4 blocked or waiting, 4 to do', and add a correctness check of those counts (T1-T3 done; T4-T6 blocked and T7 waiting; T8-T11 to do).
- **A1 Zones marked and ordered** — The skill's own skeleton heading ('START HERE - at a glance' with a person glyph) names no reader in words, while the L4 metadata line ('for Dana (manager) and the AI agent') is a header audience line; a strict grader could fail the skeleton itself. State whether glyph plus 'START HERE' counts or require wording such as 'for Dana' in the zone heading.
- Nothing checks date and derived-number correctness. This run's weekdays, DBA windows, six working days after 30 Oct and the DST shift were all right, but a wrong weekday would pass every assertion. Add a date-sanity assertion (10 Nov is a Tuesday, windows are Tue/Thu, 7 Nov is a Saturday).
- Nothing checks that invented deadlines are presented as suggestions rather than as the user's. The doc adds 20 Oct, 27 Oct and 6 Nov and labels them '(suggested)'; an unlabelled version would still pass C4/E1/E2 as written. Add an assertion that dates absent from the inputs are labelled.
- **D2 Coverage and truth** — Passes vacuously when no edge is inferred. The Q labels on nodes (T4-Q4, T5-Q1, T6-Q2, T7-Q3, T8-Q5) are derived mappings that tasks.md does not state; add a check that they agree with open-questions.md.
- **C2 Compact glance panel** — Passed at 298 of 300 words, but the word cap is met partly by dropping the Key facts slot, which is why the task tally is picture-only. The assertion cannot tell whether essential facts were cut; pair it with a key-facts-present check (the cold-reader test partly covers this).
- **F3 Chat reply is the panel** — The harness defines no expected path format; the reply says only 'Files are in outputs'. State whether a relative folder plus file name is enough.
- Not asserted but observed and worth keeping: block A states the repo root once with repo-relative paths, has a definition of done, a Decision log with a refresh-the-panel protocol, and the final reply asks Alex to push his branch before leaving. These A4-style behaviours have no dedicated assertion, so a regression there would go unnoticed.

**Overall:** Assertions are mostly structural and match the rubric; the content checks (Dana's view, cutover risk, agent-ready, guardrails) are discriminating. Main gaps: ambiguity about whether the picture can satisfy a text tally (Dana's view) and what 'names its audience' means (A1), plus no checks on date arithmetic, derived-number labelling or A4 completeness.

</details>

<details>
<summary><b>Grader critique, without the skill run</b> (6 suggestions)</summary>

- **D1 Diagram drawn** — Neither says whether one node that groups several tasks counts. This run merged three finished tasks into a single 'T1 to T3' node: a legitimate simplification, yet it hides T1-&gt;T2 and T1-&gt;T3 and which predecessor feeds T4 versus T5-T7. I passed D1 and failed D2, but another grader could go either way. State the rule ('each of T1...T11 has its own node or ID' or 'grouped done tasks are allowed if edges stay faithful'). D1 and D2 also overlap on coverage.
- **A1 Zones marked and ordered** — The assertion text (a heading or banner naming the audience) is met by 'Part A (for Dana)' and 'Part B (for the AI agent)', but check_doc.py's A1 check demands &lt;!-- zone: --&gt; markers, so the judged result (pass) and the mechanical result (Major) disagree. Decide whether audience-named H2s are enough or the markers are required.
- **C1 Conclusion first** — The judged placement ('straight after the title and one metadata line') is not what the checker measures. It counts text lines before the first blockquote, table or image, and here a 'Convention' blockquote at L9 hid five header bullets (two of them reading and contents pointers) before the bottom line. A numeric limit would make this repeatable, for example a bottom line within N lines of the title with no contents or pointer lines before it.
- **D5 D6 Explained and reproducible** — Both bundle several rules, so a run that satisfies most of them fails outright. D5/D6 here had alt text, legend, a .dot source and a text equivalent but no reading caption or relation statement. E1/E2 here had strong E2 (tags, unknowns table) and no E1 (no confidence levels). Splitting them would show which part the skill actually improves.
- **C4 Nothing invented** — No assertion checks that the decision list equals the six open questions with extras labelled. This run re-labelled Q3-Q6 (all 'need a human decision' in open-questions.md) as 'unblock others' and added an unsourced Q7 with an invented date; C4 catches it only by interpretation, and Dana's view passes regardless. An explicit check such as 'decision list = open questions 1-6, additions marked as the author's proposal' would score this consistently.
- **Cutover risk** — It passes when the bullet says 'Q1 to Q4' and only the figure says 'T4 to T7'. Require the dependency and the 30 Oct threshold to be stated in the panel text itself if that is what is intended.

**Overall:** Strong discriminating checks (A3, B1, C2, C3, Agent-ready, Guardrails, F3), but several outcomes depend on interpretation (D1/D2 grouped nodes, C1 placement, A1 markers vs headings, C4 labelled additions) and two bundled assertions (D5 D6, E1 E2) hide partial success. Clarify those and add a check that the decision list matches the sources.

</details>

## Executor notes and raw records

The agent that wrote each document also left notes on where the instructions it had were unclear.

| Record | Without the skill | With the skill |
|---|---|---|
| Executor notes | [executor-notes.md](records/eval-2-dual-audience-handoff/without-skill/executor-notes.md) | [executor-notes.md](records/eval-2-dual-audience-handoff/with-skill/executor-notes.md) |
| Cold-reader answers | [coldreader-answers.md](records/eval-2-dual-audience-handoff/without-skill/coldreader-answers.md) | [coldreader-answers.md](records/eval-2-dual-audience-handoff/with-skill/coldreader-answers.md) |
| Grading (assertions, evidence, claims, critique) | [grading.json](records/eval-2-dual-audience-handoff/without-skill/grading.json) | [grading.json](records/eval-2-dual-audience-handoff/with-skill/grading.json) |
| Automatic checker output | [mechanical.json](records/eval-2-dual-audience-handoff/without-skill/mechanical.json) | [mechanical.json](records/eval-2-dual-audience-handoff/with-skill/mechanical.json) |
| Timing (estimated from file times) | [timing.json](records/eval-2-dual-audience-handoff/without-skill/timing.json) | [timing.json](records/eval-2-dual-audience-handoff/with-skill/timing.json) |
| Prompt and assertions | [eval_metadata.json](records/eval-2-dual-audience-handoff/eval_metadata.json) | |
