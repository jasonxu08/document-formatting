# Notes on report.md

## 1. Choices about structure, and why

- **One Markdown file plus an `images/` folder.** It is a wiki-repo drop-in: copy `report.md` and `images/` together (image links are relative). The diagrams are PNGs rendered with Graphviz, with the `.dot` sources kept beside them. I chose PNG over Mermaid because I don't know which wiki renderer you use, and Mermaid support varies. Callouts are plain blockquotes (not GitHub-only alert syntax) for the same reason.
- **Written for any new joiner, not for Priya by name.** The doc will outlive her first week.
- **Outcome first, then a reading guide.** The page opens with what the reader will be able to do, then a short "how to use this page" (what to read on day one, what to read before shadowing on-call or opening a PR, what is reference).
- **Mental model before detail.** "Six ideas that explain most of the design" comes right after the one-paragraph overview, then the diagram, then the six core terms. A strong backend dev can reason about the rest from those ideas.
- **Organised around a file's journey, not Sam's list of components.** Sam's notes are component-by-component. A newcomer needs the flow, so the middle of the doc is a stage-by-stage walkthrough (upload, validate, transform and publish) with numbered steps that match the numbers on Figure 1. The component details that don't fit the walkthrough (who calls the Policy Engine, caches, retention) went into one reference table.
- **Two figures.** Figure 1 is the architecture with numbered steps and failure paths. Figure 2 is the Version status lifecycle, which is where "Catalog is the source of truth" becomes concrete. Colour is never the only signal (shapes, labels and a legend), and each figure has alt text and a text equivalent in the prose.
- **Operational material in its own sections.** Failure handling (two kinds of failure, retry/DLQ, trust the Catalog), a quick-triage table, numbers, local setup and gotchas each get a short section so the on-call shadowing day has something to read.
- **First-week plan maps all eight checklist items** into Monday to Friday, with what to look for in the pass/fail sample uploads and what each starter ticket touches. A six-question self-check at the end links back to the sections.
- **Reference at the back.** The 20 config settings are regrouped by area (the source table was flat) and checked programmatically: every setting and default matches the notes.
- **Assumptions and gaps are visible.** Inline callouts marked **Assumption** or **Open question** where they matter, collected in Appendix B so someone can resolve them and delete them.

## 2. What I was unsure about

- **Retry semantics.** The notes say both "3 attempts" and "retried 3 times", and list three back-off delays (30 s, 2 min, 10 min). I did not resolve this; it is flagged in the doc.
- **Catalog status while a message is in the DLQ.** The notes list four statuses only. I assumed there is no fifth and said so.
- **Repo contents.** The notes name four repos but not what is in them. The mapping in "Your first week" is inferred from the names.
- **What `quarantine-release` does** to the status, and whether a released file is re-validated.
- **`MAX_ROW_BYTES`.** I mention it in the Stage 2 text but don't attribute it to validation, because the notes don't say where it is enforced or whether an over-long row fails the whole file.
- **Ownership.** The notes don't say which of the Catalog, Policy Engine, Notifier, Schema Registry and queue the ingestion team owns versus consumes.
- **Local stack.** The notes mention queue and blob emulators and a mocked Policy Engine only. I don't know whether sample uploads in week one go to the local stack or to `ingestion-dev`, or what the exact smoke-test command is.
- **Derived statements.** The 15-minute budget arithmetic, the 5 GB versus `TRANSFORM_TIMEOUT_S` observation, the "stuck in `received`/`validated`" triage row and the "caches can delay changes" note are my inferences from the numbers and flow. Each is labelled as derived.
- **The day-by-day order** is my suggestion; only the Wednesday sync and the Friday review are fixed. "10:00 CET" is taken as written (central European clocks change on 25 October 2026, so the invite is the authority).
- **Naming Sam** as the source in the footer and in the open questions. Remove it if that isn't wanted.
- **Rendering.** Heading anchors assume GitHub-style slugs and `- [ ]` task lists render as checkboxes only in GitHub-flavoured renderers. All files are UTF-8 with CRLF line endings (as written by my tooling), so convert if your repo enforces LF.
- **A side effect to flag.** While trying to preview the page, one browser-tool call wrote two scratch files into a `.playwright-mcp` folder at the root of the git repo I started in. I deleted both files and the empty folder straight away and made no other change outside this outputs folder. The preview itself used a temporary local server and headless Edge, and those temporary files are gone too.
