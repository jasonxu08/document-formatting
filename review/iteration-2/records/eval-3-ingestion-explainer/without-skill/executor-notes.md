# Notes on the ingestion explainer

Deliverable: `report.md` (the guide) plus `diagrams/` (two figures and their sources). Everything is in this folder.

## 1. Structure choices, and why

**Reader-first order, not Sam's order.** Sam's notes are organised by component, which suits someone who already knows the system and looks things up. A new engineer needs the mental model first, so the guide goes: short version (five rules) → vocabulary → how a file moves (map, three stages, status lifecycle) → components → failures → running locally → gotchas → first week → settings reference → open questions. The first three sections are the day-one read (about 15 minutes); everything after is reference. The header says so.

**Five rules up front.** The notes repeat a handful of principles (Catalog is the source of truth, idempotent workers, immutable Versions, validation failure is not an error, tenant scoping). Putting them first gives Priya a frame for everything that follows.

**Two figures, hand-laid-out.** The notes describe 11 components whose relationships are the hard part, so Figure 1 is a map. Figure 2 shows the Catalog status of one Version, because that is what she will watch in the Catalog UI and what failure handling hinges on. I tried Graphviz first, but the shared stores (Catalog, Raw Zone) caused crossing lines, so I drew them as SVG in three bands with straight links. Each figure is followed by a text version of the same content.

**Tables for lookup and comparison, prose and numbered steps for sequence.** Tables: vocabulary, status, components, validation vs infrastructure failure, settings. Numbered steps: the three stages.

**Gotchas kept as their own section** (as in the notes) because people look them up, but each is one or two lines.

**Checklist kept intact** (all eight items, same meaning) with a pointer to the relevant section for each. I added a short "By Friday you should be able to" list as the first-week success measure. I did not invent a day-by-day schedule beyond the two fixed meetings; the suggested pacing is labelled as a suggestion.

**Assumptions are visible.** Two inline markers (**Assumption**, **Check**) appear where they matter, and the last section collects every open item so someone can resolve them and delete the entry.

**Written for "a new engineer", not for Priya by name**, with no calendar dates, so it can be reused for later hires. British spelling, matching the notes.

**Wiki portability.** Plain Markdown, relative image paths, no raw HTML, GitHub-style heading anchors, PNG figures (render in every engine) with SVG and the generator script kept alongside as editable sources.

**Fidelity.** I checked with a script that all 20 settings and defaults match the notes, that all numbers match, and that every code-formatted platform identifier in the guide exists in the notes (nothing invented).

## 2. What I was unsure about

**Where the notes conflict (flagged in the guide as "Check"):**
- Retry count: "3 attempts", "retried 3 times" and three backoff delays (30 s, 2 min, 10 min) do not line up.
- `POLICY_MODE`: the settings table says the default is `strict`, but the local stack is described as allow-all unless you opt in. I assumed compose overrides it. Also unclear where it must be set (stack, test runner or both).
- A 5 GB file at the 6 min/GB transform p95 is about 30 minutes, which equals `TRANSFORM_TIMEOUT_S` (1,800 s). I raised it as a question rather than a claim.

**Where I filled a gap (flagged as "Assumption"):**
- Repo contents are inferred from the repo names.
- A Version whose message is retrying or dead-lettered is assumed to keep its last status (no "failed" status is mentioned). The "if a Version looks stuck" steps rest on this and are derived from the flow, not from a runbook.
- Cache TTLs are read as "a change can take up to this long to be seen".
- I grouped the settings by area from their names. For example `MAX_ROW_BYTES` sits under Validation, but the notes do not say which component enforces it.
- The "three kinds of version" callout (Version, Schema contract version, dataset major version) is my synthesis of how the notes use the word.

**Not in the notes at all (listed as "ask the team"):** which components the team owns versus consumes and where their code and runbooks live; how the Catalog, Schema Registry and Notifier run locally; where the sample files come from; what happens if the Uploader API crashes between creating the Version and queuing `validate`; how a new dataset major version is created; deployment, CI and review process. The meeting time is "10:00 CET" with no stated incident-review time, and CET may or may not include summer time.

**Small practical points:**
- The file is called `report.md` as requested; rename it for the wiki and keep `diagrams/` beside it (or update the two image paths).
- Heading anchors are GitHub-style. Azure DevOps wiki and some others slug headings differently, so in-page links may need a quick check.
- The file uses CRLF line endings (Windows default). Normalise if your repo enforces LF.
- Figure 1 is dense: its text is readable at page width but small. Clicking the image opens the full-size PNG.
- `diagrams/build_diagrams.py` is only needed to change the figures. It needs Python, plus Edge or Chrome for the PNGs.
- The 15-minute reading time is an estimate, not measured.
