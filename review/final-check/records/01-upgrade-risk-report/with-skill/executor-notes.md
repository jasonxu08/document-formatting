# Notes on running the document-formatting skill: upgrade risk report

*What happened when the skill was applied to the v8-to-v10 upgrade assessment. Written for whoever improves the skill; file names are relative to `outputs/`.*

## 1 Skill instructions I followed

Read order: `SKILL.md` (in two reads, it is 22.6 KB), `assets/skeleton.md`, `references/review-rubric.md`, `references/diagrams.md`, and `references/rewriting.md` (SKILL.md points to it; not applied, because this was a new report and not a rewrite, so I did not run `source_set.py`).

- **Sizing.** Treated the report as Large (saved as a file, several findings): two-zone layout, glance panel, reading path, diagram.
- **Step 1, audience split.** Human zone = verdict, decisions, risks, five numbered sections. Archive = checksums, recomputed numbers, the 16-edge list, incident tables, decision record. AI input = one short block A ("Keeping this report current"), added because the user called the report an audit trail for the decision, so someone must update it after Friday.
- **Sibling rule.** AI-input plus archive material was well over 60 lines, so it went to `report.evidence.md`; the main file keeps block A (collapsed) and one-line pointer blocks B and C.
- **Audit-trail clause.** Byte-exact copies of the three inputs in `report.data/` (hash-verified), byte sizes and SHA-256 in evidence block A, originals untouched.
- **Step 2, headline first.** Filled bottom line, judgment, ask and ranked risks before drafting.
- **Panel.** Verdict glyph, confidence and basis; two decisions with who, what, by when and a recommendation, each recommendation marked "(suggested)" because the notes give an owner and a date but no recommendation; "If we get it wrong" once; five ranked risks with glyphs and "my ranking" said aloud; key facts flagged as my counts. Checker: 264 panel words.
- **Reading path.** Five "Read next" links with a time each and who can stop where. Headings carry the argument. Link-target headings use plain words and digits (checked with `--slugs`).
- **Draw the web.** Nine services and 16 edges, so a Graphviz PNG embedded in the panel, the `.dot` beside it, a caption with how to read it and the takeaway, and an edge list with source line numbers in evidence block C. I viewed the PNG and fixed the layout (shorter cluster labels took it from 1475 to 1155 px wide).
- **Second picture.** A timeline (matplotlib, `timeline.py` beside the PNG) in section 4 for the date squeeze.
- **Honesty rules.** Inferences are labelled ("Inference:", "my reading", "(suggested)"). Unknowns are a table in section 5. The one place two sources disagree (notes: rollback 10-15 min; Q3 log: one rollback took 19 min) is stated, with the figure I planned on. The two SEV1 rows are one outage and the counts say so (36 records, 35 distinct).
- **C5 recomputation.** Recomputed every count, weekday and day difference by script before delivery (43 weekday claims, 0 wrong).
- **Deliver.** No machine-local paths, plain blockquotes, two loud blockquotes. `final_reply.md` is the panel in miniature with folder plus file name. Checker on `report.md` and on `report.evidence.md`: 0 blockers, 0 majors, 0 minors.

## 2 Instructions that were unclear, contradictory, or that I did not follow

- **Did not copy the skeleton file.** SKILL.md says "start from `assets/skeleton.md`, fill it in and delete its hint comments". I wrote the file fresh in the skeleton's shape and kept its zone markers, so no hint comments could be left over. If copying is required, say so.
- **Panel word budget is under-specified.** SKILL.md says about 300 words with tables, picture and Read-next list excluded. `check_doc.py` counts everything between the first and second H2, including the image caption, the "Only deciding?" line and the Key facts line, and excludes only tables, image lines and bullets that start with a link. I learned that only by running it. Please list what counts.
- **Recording a decision in an audit-trail document is not covered.** The user wanted an audit trail "for whatever we decide". The skill says to add an AI-input block when the document must be kept current, but gives no pattern for logging the outcome. I invented a "Decision record" (evidence block E) and a refresh checklist in block A. Rubric A4 targets handoffs only, so I used its list informally.
- **Block letters collide across files.** The main file has blocks A-C and the evidence file has A-E (the skill's own `source_set.py` also letters sibling blocks from A), so "block A" is ambiguous. I always wrote the file name with it. A convention would help.
- **"Who decides" when the source is silent.** The notes name the Eng Lead as owner of the main decision but not who approves the 18,000 USD extended support. The skill covers a missing date or recommendation, not a missing decider. I kept "Marcus" and added "approver not named in the notes".
- **"Link each claim in the panel to the section that supports it."** I linked the risk rows, key facts, bottom line and decisions, but not every phrase (the confidence line has no link). Unclear how dense this should be.
- **Duplication rule vs the panel.** "Write each fact once" conflicts with a panel that must restate the headline numbers; the only written exemption is for rewrites. I let the panel restate and link to the body, so 18,000 USD and the main dates appear in the panel, the body, the timeline image and the evidence file.
- **Repo-relative path.** The user said "kept in the repo" but gave no repo, no docs location and no conventions, and the run rules fixed the folder. "Save where the repo's conventions say" and "path relative to the repo root" could not be followed; I used `outputs/report.md`.
- **800 px legibility.** The skill says legible at about 800 px; the checker only tests 500-2600 px wide. I viewed the PNGs at native size (1155 and 1447 px), not scaled to 800 px, so D4 rests on my eye.
- **Second picture.** The skill says one picture in the panel, and a diagram only when the diagram rule fires. A timeline is listed as a possible picture but does not trigger the rule. I added one because the decision is date-driven; say whether that is welcome or padding.
- **SKILL.md size.** At 22.6 KB my viewer refused a single read (limit about 20 KB). Moving some of "Highlight with a budget" or "Draw the web" into references would keep the main file under that.
- **Two tips that cost me retries** (suggest adding to `diagrams.md`): in matplotlib date charts use `datetime`, not `date`, as positions, because `date + timedelta(days=0.8)` silently adds 0 days and labels land on the markers; a long Graphviz cluster label widens the whole graph, so break it with `\l` lines.

## 3 What I am unsure about

- **The recommendation.** The split is medium confidence. It leans on three things the notes do not state: whether the seven were staged next to a v8 `auth-service`, whether a rollback during the freeze needs a CAB exception, and how extended support is priced.
- **"No more than B" on cost.** True if the 18,000 USD is flat. If it is per service the split is cheaper than all-January; if quarters are calendar quarters one quarter might not cover mid-November to mid-February.
- **"One week" for the Data team.** I read it as five working days, Mon 2026-10-26 to Fri 2026-10-30. If it means seven calendar days the work ends on the first day of the freeze. Section 4 says so; the panel risk row only says "no spare day".
- **Gateway records that "name auth-service".** I classified by summary text; some name it as context ("while auth-service slow") rather than cause, so the report says "as cause or circumstance".
- **Length.** The human zone is 2,474 words by the checker (advice 2,500) for one decision. Section 2 and the options table may be more than Marcus needs.
- **Whether a term list inside section 1 satisfies B2.** The panel uses "freeze" (glossed by dates), "CAB" (glossed) and "extended support" (priced, not defined) before the term list.
- **What "keep the supporting data" covers.** I kept the three inputs byte-exact and put my derived tables (edge list, incident breakdown, recomputed numbers) in the evidence file as Markdown. I did not export them as CSV or JSON in `report.data/`.
- **First-person wording.** "My ranking" and "my reading" are honest labels but may read oddly once the report sits in the repo under the team's name.
- **Rendering.** I could not open VS Code or Azure DevOps. I checked structure with a CommonMark parser (tables, blockquotes, details and images all parse) and with the checker. A link to a folder (`report.data/`) passes the checker but may show a directory listing in Azure DevOps.
- **A stray bytecode file.** A `scripts/__pycache__/check_doc.cpython-312.pyc` appeared in the skill folder during my run. Re-running `check_doc.py` (with and without `--slugs`) and `source_set.py --help` does not recreate it, so I cannot say what wrote it (an import of `check_doc` by some other process, perhaps). I deleted it to leave the skill folder as I found it.
