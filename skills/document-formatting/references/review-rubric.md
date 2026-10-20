# Review rubric for large documents

This is the standard a large document written under this skill is held to. Use it as the writer's last pass before delivering, as a checklist for a reviewer (human or agent) scoring any document, and as the source of the skill's test assertions.

## Run a review

1. Run `python scripts/check_doc.py <file>` on the main file and on every sibling file. It covers every rule marked **auto** and prints each finding with its rule id and tier. For a rewrite of an existing document, also run `python scripts/source_set.py verify <main.md> --source <original>` (rule G1).
2. Walk the **judge** rules that apply (column "For"), looking at the document the way its first reader will: the top of the rendered page and nothing else. Rules that need the sources (C5, C6) are checked against them.
3. Gate: deliver when no Blocker is left and at most two Majors remain. Name the remaining Majors, with the reason, in your reply. Minors are advice.
4. Fit the effort to the document. A short answer needs only C1, E1, F1 and F4. A medium document adds the rest of C, B3 and D1. A large one gets everything that applies.

**Tiers.** Blocker: the document fails its purpose or has a certain defect. Major: it weakens comprehension or trust. Minor: polish.

**Reader profile.** The rules assume the readers open Markdown in VS Code's preview and on Azure DevOps repo and PR pages, which do not render Mermaid. If they only use GitHub or Azure DevOps wikis, inline Mermaid is fine: pass `--allow-mermaid` and treat D3 as met.

**For.** all = every document. medium+ = medium and large. large = large only. dec = decision or proposal. rca = investigation or root cause. rev = review, audit or assessment. ver = test or verification report. hand = status or handoff. expl = explainer or onboarding. rewrite = a restructured version of an existing large document.

## Rules

### A Audience split

| ID | Pass condition | Tier | Check | For |
|---|---|---|---|---|
| A1 | Zones are marked and ordered. A human zone comes first, opened by a heading or banner that names who it is for in words (`START HERE - at a glance (for the release managers)`); a glyph alone, or an audience named only in a header pointer line, is not enough. AI-input and archive material, if any, comes last in its own labelled zone. Nothing for people sits after machine content. No raw material means no machine zone is needed. | Blocker for a large document with raw material, else Major | auto (markers, order) + judge | all |
| A2 | The human zone holds no raw material: no table over 15 rows, no code block over 25 lines (diagram sources excepted), no logs, listings or data dumps. Shell commands belong in the AI-input block unless the reader must run them. A table the user asked for by name (a map, an inventory) is exempt (mark it with `<!-- requested-table -->` on the line above); place it where its readers look for it and link it from the reading path. | Major | auto | all |
| A3 | Machine and archive blocks are plain-headed and collapsed in `<details>`, or reduced to a one-line pointer when the material lives in a sibling file (a pointer counts as collapsed). Each opens with a line naming its bin (AI input or archive) and what it supports. Long material sits in a sibling file, unless the user asked for it to stay in the document. Blocks inside an archive-only sibling need not be collapsed: the file is the destination. | Major | judge | large |
| A4 | The AI-input block is self-sufficient: current state, repo-relative paths with the root stated once, copy-paste commands, ordered next steps, constraints and what not to do, a definition of done, and what to do while decisions are open and where answers are recorded. | Major | judge | hand |
| A5 | No machine-local paths (home folder, temp or session folders). | Major | auto | all |

### B Guided reading

| ID | Pass condition | Tier | Check | For |
|---|---|---|---|---|
| B1 | A reading path sits within 60 lines of the title: at least 3 links to sections, each saying what the reader gets, and who can stop where. | Major | auto + judge | medium+ |
| B2 | Order follows understanding, not discovery. The mental model comes first, terms are defined before the first numbered section that uses them (including codes, abbreviations and internal names the reader must decode), and chronology lives in the archive. The glance panel is exempt from the glossary but must read cold: a term it needs gets a short gloss in the line itself. | Major | judge | expl, rca, large |
| B3 | The H2 headings of the human zone, read alone, give the outline or the argument, in words that cannot be misread (a heading about a handover must say from whom to whom). A question or decision heading carries its answer or ask. | Major | judge | medium+ |
| B4 | Every in-document link, cross-file anchor and image path resolves. Fences and `<details>` balance. No template placeholder is left. | Blocker | auto | all |
| B5 | A large document has real navigation: at least 5 in-document links. | Major | auto | large |
| B6 | Link-target headings use plain words and digits (no emoji, no punctuation) and are unique. `python scripts/check_doc.py <file> --slugs` prints the anchor of every heading. | Minor | auto | all |
| B7 | A section whose heading does not already say what it answers opens with a one-line orientation. Each entity keeps one name throughout. Cross-references name something the reader can see (a numbered row, a heading), not an unlabelled "risk 3". | Minor | judge | large |

### C Glance first

| ID | Pass condition | Tier | Check | For |
|---|---|---|---|---|
| C1 | The glance panel opens the document, straight after the title and one metadata line. Its bottom line states the conclusion (for an explainer, the mental model), not what the document covers. | Blocker | judge + auto (more than 12 lines of text before the first panel element) | medium+ |
| C2 | The panel is compact: about 300 words of prose or fewer (tables, the picture and the Read-next list excluded), one line per decision and per risk. Verdict, decisions and top risks fit the first screen. | Major | auto + judge | medium+ |
| C3 | When a judgment, decision or risk exists, the panel states it loudly and completely. The verdict has a glyph, confidence and basis; a partial result says "partial" and which part is missing. Each decision has who, what, by when and a recommendation; where the sources give no date or recommendation the panel says so ("no date set"), and a date or recommendation you propose is marked "(suggested)". At most 5 risks, ranked, each with severity and consequence. | Blocker | judge | dec, rca, rev, ver, hand |
| C4 | Nothing is invented to fill the template: no verdict, decision or risk block without grounding in the sources, any ranking is traceable (a ranking of your own says so), and empty slots are omitted. A recommendation or stance attributed to a source matches that source's own wording and version (the source's option, not a stronger paraphrase; a claim about one version holds only for that version). A caption or takeaway agrees with the table or picture it describes: it never claims more than the table shows (no "all passed" above a table with a failed row). | Major | judge | all |
| C5 | Numbers in the panel trace to the sources (spot-check at least three). Derived, merged or de-duplicated numbers say so, and every derived count, weekday and date calculation is recomputed from the source before delivery. | Major | judge, needs sources | all |
| C6 | Every open question or decision in the sources appears in the decision block or is explicitly parked. | Major | judge, needs sources | dec, hand, ver |

### D Diagrams

| ID | Pass condition | Tier | Check | For |
|---|---|---|---|---|
| D1 | More than 5 related entities, or any web of relationships, means at least one diagram. A linear chain of 5 steps or fewer, or a flat list, gets none. | Major | judge | all |
| D2 | Coverage and truth: every entity the document names as a participant appears in at least one diagram as its own labelled node (a name tucked into another node's label does not count; if that makes the picture illegible, split it into an overview plus zoomed views), every drawn edge exists in the sources, and inferred edges are dashed and captioned. | Major | judge | all |
| D3 | Image-first: a diagram in the human zone is an embedded image file that exists. Inline Mermaid there is a defect under the default reader profile. For Azure DevOps wikis use `graph`, not `flowchart`. | Major | auto | all |
| D4 | Legible: the image is 500 to 2600 px wide. At 800 px wide the labels read, nothing overlaps, and no glyph shows as an empty box (look at the image to check). | Major | auto (size) + judge | all |
| D5 | Explained: alt text, a caption with how to read it and the takeaway, a legend where colour carries meaning, one focal point, and the relation stated (verbs on edges, or once in the caption when every edge is alike). | Minor | judge, auto for alt text | all |
| D6 | Source kept: the DOT, Mermaid or script file sits beside each image. When edges are inferred, or the diagram has more than about 12 edges, an edge list that says how each edge was verified is in the archive; for a small, fully verified diagram the source file is the text equivalent. | Minor | auto (file) + judge | all |

### E Honesty and provenance

| ID | Pass condition | Tier | Check | For |
|---|---|---|---|---|
| E1 | Every judgment carries a confidence level and what it rests on. | Major | judge | all |
| E2 | Inferred, assumed and proposed content is labelled as such, unknowns are listed, and nothing presented as fact is unsourced. When two sources disagree, the document says so and which one it used. Evidence from a simulation, mock or stand-in is called that every time it is mentioned, never "verified in production". | Major | judge | all |
| E3 | A metadata line under the title gives date, author or agent, status and audience. Sources are named. | Minor | auto (date) + judge | medium+ |

### F Fit and delivery

| ID | Pass condition | Tier | Check | For |
|---|---|---|---|---|
| F1 | Proportionate: a short answer gets no zones or panel. A mandated template or schema is kept, with the human layer added around it. | Major | judge | all |
| F2 | The human zone is not bloated: about 2,500 words or fewer. Beyond that, check whether detail only some readers need has leaked in. A document with several decisions, a coverage matrix and a status table may need more; that is fine when every part serves a decision or a review. | Minor | auto | all |
| F3 | The chat reply is the panel in miniature (verdict, decisions, top risks, file path, where to start) and does not paste the document. The path is the folder plus file name, relative to the repo root when there is one. | Major | judge, needs the transcript | large |
| F4 | Language: the document, its headings, labels and diagram text are in the reader's language, with no missing-glyph boxes. | Major | judge | all |
| F5 | Hygiene: a blank line after `</summary>` and `</details>` (Major); no `> [!NOTE]` alerts, no HTML colour or style, at most about 3 loud blockquote headings, no paragraph repeated verbatim, no spaces in file names (all Minor). | Major / Minor | auto | all |

### G Rewriting an existing document

| ID | Pass condition | Tier | Check | For |
|---|---|---|---|---|
| G1 | Nothing is lost: every non-blank line of the source is reachable, either in a verbatim copy in the machine zone or a sibling file, or because the source stays beside the output and the document names it and records its SHA-256. Every H2 section of the source is named in a section map. | Blocker | auto (`source_set.py verify`) | rewrite |
| G2 | Current truth first: where the source contradicts itself over time (an early note says a check was not run, a later entry says it ran), the human zone states the current truth and says the older note predates it. The older text stays in the archive, labelled superseded. Labels match the source's own marking: nothing still current is labelled superseded or history, and text the source marks superseded is not presented as current. | Major | judge | rewrite |
| G3 | The human zone restates; the archive proves. Each restated claim links to the verbatim block behind it, and the document says which parts are verbatim and which are rewritten. | Major | judge | rewrite |

## Scorecard format

A reviewer replies with one line, **Verdict: deliver** or **Verdict: fix first**, followed by the counts of Blockers, Majors and Minors. Then a table of only the rules that failed: rule id, line or quote as evidence, and the fix. One line for anything notable that passed on a close call.

The project's own regression tests (test cases with assertions, fixtures, the cold-reader test and the trigger set) live in the repository's `evals/` folder and are not part of the installed skill.
