# Upgrade risk report · iteration 2

[← Iteration 2](README.md) · [Review dashboard](../README.md) · [Example documents](../../examples/01-upgrade-risk-report/README.md)

> **Prompt given to both agents**
>
> Our runtime upgrade (v8 to v10) is on the table and our Eng Lead, Marcus, has to decide by Friday whether we upgrade before the November code freeze or push everything to January. I put the notes, the service inventory and last quarter's incidents in examples/01-upgrade-risk-report/input/. Write the assessment report for Marcus. I also want it kept in the repo as the audit trail for whatever we decide, so keep the supporting data.

## Result

| | Without the skill | With the skill |
|---|---|---|
| Assertions passed | **10 / 22** (45%) | **22 / 22** (100%) |
| Automatic checker | ❌ 0 Blockers · 5 Majors · 1 Minor | ✅ 0 Blockers · 0 Majors · 1 Minor |
| First section, words (the checker's panel measure; budget about 300) | 495 | 292 |
| Words in the human-read zone (the whole document when there are no zones) | 4,126 | 2,472 |
| Cold reader, first 60 lines | 5 / 6 key facts | 5 / 6 key facts |

## What the reader sees first

| Without the skill | With the skill |
|---|---|
| ![first screen without the skill](../../examples/01-upgrade-risk-report/images/without-skill-first-screen.png) | ![first screen with the skill](../../examples/01-upgrade-risk-report/images/with-skill-first-screen.png) |
| [Open the document](../../examples/01-upgrade-risk-report/without-skill/report.md) | [Open the document](../../examples/01-upgrade-risk-report/with-skill/report.md) |

## Assertion scorecard

Each assertion was graded by an agent that read the document and cited evidence; ✅ passed, ❌ failed. The evidence for every failure is below, and the full evidence for every assertion is in the raw `grading.json` of each run.

| Assertion | Without | With |
|---|:-:|:-:|
| A1 Zones marked and ordered | ❌ | ✅ |
| A3 Machine blocks collapsed | ❌ | ✅ |
| B1 Reading path | ❌ | ✅ |
| B2 Order follows understanding | ❌ | ✅ |
| B3 Headings carry the story | ❌ | ✅ |
| C1 Conclusion first | ❌ | ✅ |
| C2 Compact glance panel | ❌ | ✅ |
| C3 Verdict, decisions, risks complete | ❌ | ✅ |
| C4 Nothing invented | ✅ | ✅ |
| C5 Numbers trace to sources | ✅ | ✅ |
| D1 Diagram drawn | ✅ | ✅ |
| D2 Coverage and truth | ✅ | ✅ |
| D3 D4 Image-first and legible | ✅ | ✅ |
| D5 D6 Explained and reproducible | ❌ | ✅ |
| E1 E2 Honesty and labelling | ❌ | ✅ |
| F3 Chat reply is the panel | ❌ | ✅ |
| Automatic checks (gate) | ❌ | ✅ |
| Verdict and ask | ✅ | ✅ |
| Key risks present | ✅ | ✅ |
| Figures | ✅ | ✅ |
| Audit data kept | ✅ | ✅ |
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
- D1 Diagram drawn: the nine related services (gateway, auth-service, user-store, catalog-service, share-service, connector-service, map-service, search-index, notify-service) are shown in at least one diagram
- D2 Coverage and truth: every one of the nine services appears in at least one diagram (a single diagram or an overview plus zoomed views), every drawn edge exists in services.csv, and inferred edges are dashed and captioned
- D3 D4 Image-first and legible: the diagram a human sees first is an embedded image file that exists (PNG or SVG), not only a Mermaid or other code block, and viewing it at about 800 px wide shows legible labels, no overlap and no empty glyph boxes
- D5 D6 Explained and reproducible: alt text, a caption saying how to read the diagram and its takeaway, a legend where colour carries meaning, the relation stated (verbs on edges, or once when all edges are alike), the diagram source file beside each image, and an edge list or equivalent in the archive
- E1 E2 Honesty: every judgment has a confidence level and its basis; content not in the inputs (assumptions, suggestions, inferences) is labelled as such; unknowns are listed
- F3 Chat reply: the executor's final reply (final_reply.md) is the glance panel in miniature (verdict, decisions, top risks, the file path, where to start) and does not paste the document
- Automatic checks: check_doc.py on report.md and every sibling Markdown file reports no Blocker and at most two Majors in total
- Verdict and ask: the panel gives a clear recommendation on upgrading before the freeze versus deferring (a split or conditional answer is fine) and names the decision Marcus must make with its deadline (Friday 23 Oct)
- Key risks present: the 12 Nov end of support and the missing rollback path for auth-service (and user-store) appear among the top risks
- Figures: the report states that auth-service has 6 dependents and accounts for 11 of the 36 incident rows (11 of 35 is also acceptable if the merged 11 Jul pair is disclosed)
- Audit data kept: the 36 incident rows and the 9-service inventory are preserved for audit (archive part or linked files), as the user asked
- Cold reader: a fresh reader who sees only the first 60 lines and the images in them recovers at least 80% of the key facts (cold-reader test, scored separately)

</details>

### Evidence for the failed assertions

<details>
<summary>❌ <b>A1 Zones marked and ordered</b> · without the skill</summary>

**Assertion:** A1 Zones marked and ordered: the document opens with a human zone whose heading or banner names its audience (a pointer line in the header does not count), and any AI-input or archive material sits last in its own labelled zone; nothing for people follows machine content

**Grader evidence:** mechanical.json: zones=\[] and check_doc A1 Major 'no &lt;!-- zone:... --&gt; markers'. The file opens with the H1 and a 5-bullet metadata block (lines 3-7, including '- **For:** Marcus Hale, Engineering Lead (decision owner)'), then '## 1. Recommendation' (line 9). No heading or banner marks a human zone; the For: line is header metadata, not a zone banner. Archive-type material does sit last (Appendix A line 204, Appendix B line 235) but is not in a labelled zone: the headings are 'Appendix A. Evidence and method' and 'Appendix B. Q3 2026 incident summary', and neither names a bin (archive / AI input).

</details>

<details>
<summary>❌ <b>A3 Machine blocks collapsed</b> · without the skill</summary>

**Assertion:** A3 Machine and archive blocks are collapsed in details blocks and plain-headed, each opening with a line that names its bin (AI input or archive) and what it supports; long material sits in a sibling file behind a pointer

**Grader evidence:** details_blocks=0; grep finds no &lt;details&gt; or &lt;summary&gt; in report.md. Appendix A (file table, A.2, A.3 data notes) and Appendix B (two aggregate tables, lines 235-264) are open on the page, and neither opens with a line naming its bin or what it supports. Only the sibling-file part holds: the raw data sits in evidence/source/*.csv behind links in A.1 (lines 206-220).

</details>

<details>
<summary>❌ <b>B1 Reading path</b> · without the skill</summary>

**Assertion:** B1 Reading path: within 60 lines of the title there are at least 3 links to sections, each saying what the reader gets, and a line saying who can stop where

**Grader evidence:** check_doc B1: 0 in-document links in the 60 lines after the title (0 internal links in the whole file). Lines 3-7 hold one link, to the folder \[evidence/source/](evidence/source/), which is not a section. Line 7 is a plain-text 'Reading guide: Sections 1 and 2 are enough to decide. Sections 3 to 6 hold the evidence, plan, risks and open questions. Section 7 records the outcome.' It says where a reader can stop but has no section links.

</details>

<details>
<summary>❌ <b>B2 Order follows understanding</b> · without the skill</summary>

**Assertion:** B2 Order follows understanding: the mental model comes first, terms are defined before the first section that uses them, and chronology lives in the archive

**Grader evidence:** Chronology is fine: incident dates live only in evidence/source/incidents-q3.csv and the body has aggregates. But terms are used before they are defined and the mental model comes late. 'Option C' is introduced on line 11; 'which both B and C need' (line 24) and 'fall back to Option B' (line 28) are used before the options table (header line 35) defines A/B/C. Codes T1/T6/T7 appear in the Section 2 table (lines 40, 41, 48) but are only explained on line 52 in Section 3. 'compatibility shim' (line 15) and 'RTO' (line 74) are never defined. The dependency picture, which is the mental model, first appears in 3.1 (line 56), after the recommendation, options table and criteria.

</details>

<details>
<summary>❌ <b>B3 Headings carry the story</b> · without the skill</summary>

**Assertion:** B3 The H2 headings of the human zone, read alone, give the outline or the argument; question and decision headings carry their answer or ask

**Grader evidence:** H2s are '1. Recommendation', '2. Options', '3. Evidence', '4. Plan', '5. Risks', '6. Open questions and assumptions', '7. Decision record', 'Appendix A. Evidence and method', 'Appendix B. Q3 2026 incident summary'. Read alone they are generic topic labels, not the argument: 'Recommendation' does not carry the recommendation, and 'Open questions and assumptions' and 'Decision record' carry no answer or ask. Only an H3 (3.1 'The risk is concentrated in two services') is argumentative.

</details>

<details>
<summary>❌ <b>C1 Conclusion first</b> · without the skill</summary>

**Assertion:** C1 Conclusion first: the glance panel opens the document straight after the title and one metadata line, and its bottom line states the conclusion itself, not what the document covers

**Grader evidence:** check_doc C1: '21 lines of text come before the first panel element'. Directly after the H1 come five metadata, provenance and reading-guide bullets (lines 3-7: For, Decision needed by, Prepared, Based on, Reading guide), not one metadata line, and there is no separate glance panel; provenance and a reading guide sit ahead of the conclusion. The conclusion itself is stated plainly once Section 1 starts (line 11: 'Split the upgrade (Option C). Move the seven services that passed staging to v10 before the code freeze...'), so only the position and format fail.

</details>

<details>
<summary>❌ <b>C2 Compact glance panel</b> · without the skill</summary>

**Assertion:** C2 Compact panel: about 300 words of prose or fewer (tables and picture excluded; mechanical.json gives panel_words), one line per decision and per risk, and verdict, decisions and top risks fit the first screen

**Grader evidence:** mechanical.json panel_words=495 against a budget of about 300 (check_doc C2: 'the first section runs to about 495 words'). Section 1 (lines 9-31) is a recommendation paragraph, five 'Why' items, four numbered decisions (several run 2-3 sentences, e.g. line 24) and two multi-sentence gate bullets, so decisions are not one line each. No risk lines appear in the first screen at all; the risk table is in Section 5 (line 144).

</details>

<details>
<summary>❌ <b>C3 Verdict, decisions, risks complete</b> · without the skill</summary>

**Assertion:** C3 Verdict, decisions and risks are complete and loud in the panel: the verdict has a glyph, confidence and basis; each decision has who, what, by when and a recommendation; at most 5 ranked risks, each with severity and consequence

**Grader evidence:** Verdict (line 11) is plain prose with no glyph and no confidence level (grep for 'confiden' finds nothing); the basis is the 'Why' list. Decisions (lines 21-26) give what and by-when ('Decisions needed by Friday 2026-10-23'; 'ordered by Thursday 2026-11-05') but no per-decision owner (Marcus appears only in the header) and the recommendation is implicit in 'Approve...'. Risks: none in the opening section; the Section 5 table (lines 144-153) lists R1-R6 as 'Risk | Why it matters | Response' with no severity and no ranking.

</details>

<details>
<summary>❌ <b>D5 D6 Explained and reproducible</b> · without the skill</summary>

**Assertion:** D5 D6 Explained and reproducible: alt text, a caption saying how to read the diagram and its takeaway, a legend where colour carries meaning, the relation stated (verbs on edges, or once when all edges are alike), the diagram source file beside each image, and an edge list or equivalent in the archive

**Grader evidence:** Present: long alt text (line 56); an in-image legend that also states the relation ('An arrow from A to B means A depends on B (calls it). Green: ... Red: ... Grey: ... Thick outline: critical service. Amber double arrow: ...'); figures/dependency-map.dot beside the PNG; and an edge-list equivalent (evidence/derived/dependency-analysis.csv lists depends_on and direct_dependents per service; evidence/source/services.csv). Missing: the caption (line 58) is only 'Figure 1. Dependencies and v10 readiness, built from services.csv by evidence/analysis.py (diagram source: figures/dependency-map.dot).' It says neither how to read the diagram nor the takeaway; the takeaway sits in the H3 above and a bullet below, and the reading key is inside the image, so the caption requirement is not met.

</details>

<details>
<summary>❌ <b>E1 E2 Honesty and labelling</b> · without the skill</summary>

**Assertion:** E1 E2 Honesty: every judgment has a confidence level and its basis; content not in the inputs (assumptions, suggestions, inferences) is labelled as such; unknowns are listed

**Grader evidence:** E2 half holds: inferences and proposals are labelled (line 85 'this link is an inference, not something the notes state'; R4 'This is an inference, not a finding'; key dates 'Derived, proposed' / 'Proposed'), assumptions are listed (6.2, lines 170-180) and unknowns are listed (6.1 open questions with owner and needed-by; A.3 'Not in the data'). E1 fails: no confidence level appears anywhere in report.md (grep for 'confiden' returns nothing). The verdict (line 11), its basis (Why 1-5) and risks R1-R6 carry reasons but no stated confidence.

</details>

<details>
<summary>❌ <b>F3 Chat reply is the panel</b> · without the skill</summary>

**Assertion:** F3 Chat reply: the executor's final reply (final_reply.md) is the glance panel in miniature (verdict, decisions, top risks, the file path, where to start) and does not paste the document

**Grader evidence:** final_reply.md (about 230 words) does not paste the document. It gives the verdict (upgrade the 7 services that passed staging before 2026-11-01, keep auth-service and user-store on v8, order $18,000 extended support by 2026-11-05), five short reasons that act as top risks, and the full path to the outputs folder. Missing: it never names the decision Marcus must make or its Friday 2026-10-23 deadline (the word 'Friday' does not appear), and it gives no where-to-start pointer (only a file list: report.md, user_notes.md, evidence/, figures/). The only ask it makes is that the requester check three assumptions.

</details>

<details>
<summary>❌ <b>Automatic checks (gate)</b> · without the skill</summary>

**Assertion:** Automatic checks: check_doc.py on report.md and every sibling Markdown file reports no Blocker and at most two Majors in total

**Grader evidence:** mechanical.json gate.passed=false: 0 Blockers but 5 Majors (A1 no zone markers; B5 0 in-document links; B1 0 links within 60 lines; C1 21 lines before the first panel element; C2 panel 495 words) and 1 Minor (F2, human zone about 4126 words). Re-ran scripts/check_doc.py on report.md and got the same result. Five Majors exceeds the limit of two.

</details>

## Cold reader

A fresh agent saw only the first 60 lines of each document (and the images in them), answered six fixed questions, and was scored against key facts derived from the *inputs*, so both arms face the same list.

| Key fact | Without | With |
|---|:-:|:-:|
| **K1** Recommendation is a split: upgrade the 7 services that passed staging before the freeze; hold auth-service and user-store until January. | ✅ | ✅ |
| **K2** auth-service is the hub (6 services depend on it), has no rollback path (restore from backup, about 4 hours) and failed 2 of 148 staging tests; user-store was never tested. | ✅ | ✅ |
| **K3** Marcus (Engineering Lead) must decide by Friday 23 Oct, so the Data team can start Monday 26 Oct. | ✅ | ✅ |
| **K4** v8 security support ends 12 Nov; extended support costs 18,000 USD per quarter and must be ordered by 5 Nov. | ✅ | ✅ |
| **K5** Code freeze runs 1 Nov to 5 Jan; only P1 hotfixes deploy unless the change advisory board grants an exception. | ✅ | ✅ |
| **K6** auth-service accounts for about a third of the Q3 incidents (11 of 36 records, mostly token-validation timeouts). | ❌ | ❌ |

Raw answers: [without the skill](records/eval-1-upgrade-risk-report/without-skill/coldreader-answers.md) · [with the skill](records/eval-1-upgrade-risk-report/with-skill/coldreader-answers.md)

- Scoring note, without the skill: K6 (11 of 36 Q3 incidents) is an evidence-level detail; both configurations missed it.
- Scoring note, with the skill: K6 (11 of 36 Q3 incidents) is an evidence-level detail; both configurations missed it.

## What the graders said about the assertions themselves

Graders were asked to critique the test, not only the document. These are the suggestions they raised for this scenario (the skill and the assertions were revised from them; see [how the skill evolved](../skill-evolution/README.md)).

<details>
<summary><b>Grader critique, with the skill run</b> (7 suggestions)</summary>

- **Automatic checks (gate)** — 'Every sibling Markdown file' is ambiguous. The outputs folder also holds user_notes.md and report.data/upgrade-notes.md. Run on them, user_notes.md gives a Blocker (B4 'unbalanced details': a false positive, because check_doc.py counts the literal tag inside inline code on lines 19 and 39) and the unedited input copy gives two Majors (B1, C1), which an input file can never avoid. Name the files in scope (report.md and report.*.md) and make the checker skip inline-code spans.
- **A1 Zones marked and ordered** — The skeleton's own heading '## \[person glyph] START HERE - at a glance' does not literally name an audience. I passed it because the metadata line says 'for Marcus Hale, Engineering Lead' and the marker reads zone:human, but a stricter grader would fail every output that copies the skeleton. Decide whether the heading itself must name the audience and align the skeleton or the assertion.
- **B2 Order follows understanding** — It is unclear whether the glance panel counts as 'the first section that uses' a term. The run uses 'the shim' and 'mixed-version check' in the panel (lines 27, 10) before the section 1 glossary (lines 59, 61). Say whether the glossary must precede the panel's jargon or only the numbered sections.
- **A3 Machine blocks collapsed** — The assertion asks for details blocks and for pointers at once. The run satisfied it with two collapsed blocks and two uncollapsed pointer blocks (the executor flagged the same ambiguity). State whether a pointer block needs details.
- No assertion checks body-level factual accuracy beyond the two Figures numbers, and I found three small slips: section 1 says a failure in the Identity pair reaches 'seven of the other eight' services (true only for user-store); section 4 calls auth-service and user-store 'the two most critical services' although services.csv also marks gateway critical; the timeline title says v8 support ends 'a week later' than Fri 30 Oct (it is 13 days). Add an assertion such as: every number or ranking in sections 1-5 that restates services.csv or incidents-q3.csv matches the data (spot-check five).
- **D2 Coverage and truth** — Vacuous for this fixture: every dependency edge is in services.csv, so the clause can never be tested. A fixture variant with one dependency mentioned only in the notes would exercise it.
- **C2 Compact glance panel** — Tension with B1: the 7-link reading path takes roughly a third of the budget (292 of 300 words used) and the run shrank each descriptor to 2-3 words such as 'terms, table'. State whether the reading path is excluded from the panel word count or require descriptors of a minimum useful length.

**Overall:** The assertions are mostly meaningful and this run met all 21 with concrete evidence, but several (A1, A3, B2, F3) hinge on wording that the skeleton itself satisfies verbatim or ambiguously, and no assertion covers body-level factual accuracy, where three small slips went uncaught. Tighten those four wordings, scope the automatic-check files, and add a data-accuracy spot-check.

</details>

<details>
<summary><b>Grader critique, without the skill run</b> (6 suggestions)</summary>

- **Key risks present** — 'Among the top risks' is ambiguous when a document has no risk panel. Here the rollback gap is in the opening 'Why' list but not in the Section 5 risk table, and the 12 Nov end of support is the reverse. Say where to look (for example the risk lines within the first 60 lines) so graders rule the same way.
- **D5 D6 Explained and reproducible** — Six sub-requirements sit in one boolean. This run has alt text, an in-image legend, the relation stated, a .dot beside the PNG and an edge-list CSV, and fails only because the caption is a provenance line. Splitting 'explained' (alt, caption, legend, relation) from 'reproducible' (source file, archive edge list) would show which half failed.
- **E1 E2 Honesty and labelling** — Two rules in one boolean hide a lopsided result: this run fully passes E2 (inferences labelled, assumptions and unknowns listed) and fully fails E1 (no confidence level anywhere). Split them.
- **C4 Nothing invented** — 'Empty slots are omitted' collides with a deliberately blank decision-record table (this run's Section 7), which an audit-trail request arguably invites. State whether the clause applies only to the glance panel.
- **D2 Coverage and truth** — The clause is satisfied vacuously when no inferred edge is drawn, and the assertion does not say how to treat an aggregate arrow (here one 'cluster -&gt; auth-service, 6 services' arrow standing for six edges). Add that an aggregate arrow is fine when every member edge exists in services.csv.
- **F3 Chat reply is the panel** — 'Where to start' is hard to judge when the reply just lists several files. Require an explicit pointer such as 'start at Section 1', and say whether naming the decision plus its deadline is required (this reply omits the Friday 23 Oct deadline entirely).

**Overall:** The structural assertions (A, B, C1-C3, automatic checks) separate this answer-first but unzoned report from a skill-shaped one clearly, and the content assertions (Figures, Audit data kept, Verdict and ask) check specific values rather than mere presence. Weak spots are the bundled D5 D6 and E1 E2 booleans and a few scope ambiguities (top risks, empty slots, aggregate edges). No assertion checks the correctness of the other body numbers; I verified them all and found no errors.

</details>

## Executor notes and raw records

The agent that wrote each document also left notes on where the instructions it had were unclear.

| Record | Without the skill | With the skill |
|---|---|---|
| Executor notes | [executor-notes.md](records/eval-1-upgrade-risk-report/without-skill/executor-notes.md) | [executor-notes.md](records/eval-1-upgrade-risk-report/with-skill/executor-notes.md) |
| Cold-reader answers | [coldreader-answers.md](records/eval-1-upgrade-risk-report/without-skill/coldreader-answers.md) | [coldreader-answers.md](records/eval-1-upgrade-risk-report/with-skill/coldreader-answers.md) |
| Grading (assertions, evidence, claims, critique) | [grading.json](records/eval-1-upgrade-risk-report/without-skill/grading.json) | [grading.json](records/eval-1-upgrade-risk-report/with-skill/grading.json) |
| Automatic checker output | [mechanical.json](records/eval-1-upgrade-risk-report/without-skill/mechanical.json) | [mechanical.json](records/eval-1-upgrade-risk-report/with-skill/mechanical.json) |
| Timing (estimated from file times) | [timing.json](records/eval-1-upgrade-risk-report/without-skill/timing.json) | [timing.json](records/eval-1-upgrade-risk-report/with-skill/timing.json) |
| Prompt and assertions | [eval_metadata.json](records/eval-1-upgrade-risk-report/eval_metadata.json) | |
