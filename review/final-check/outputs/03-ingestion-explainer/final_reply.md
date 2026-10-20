Priya's explainer is written as a wiki-ready draft: `final-check\eval-3-ingestion-explainer\with_skill\outputs\report.md`.

**Mental model:** a customer uploads a file; the platform checks it against the dataset's schema contract and publishes it as a queryable table, asynchronously, with the Catalog (not the queue) recording where each upload stands.

**Confidence: medium.** It rests only on Sam's notes and the week-one checklist, not on code or runbooks.

🧭 **Needed from Sam** (no date set; before Monday is my suggestion): confirm the seven open points in section 6. The two biggest: the notes contradict themselves on the local `POLICY_MODE` default (I followed "allow-all unless `strict`"), and say both "3 attempts" and "retried 3 times" (I wrote "3 attempts, then DLQ").

**Where to start:** the "At a glance" panel at the top of `report.md`. Priya's short route is the panel, then sections 3 and 4. Drop `report.md`, `report.assets/` and `report.evidence.md` (settings, edge lists, what I inferred) into the wiki together.

Checker: 0 blockers, majors or minors on both Markdown files. I could not preview the page in a browser.
