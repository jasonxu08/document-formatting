I've written the explainer as `report.md`, with two figures in a `diagrams/` folder next to it. It covers upload to publish for an engineer new to the team, with a week-one checklist and starter tickets. The first three sections take about 15 minutes to read; the rest is reference.

Please have Sam or the team confirm three things the notes leave unclear (marked **Check** in the guide):
- **Retry count:** "3 attempts" and "retried 3 times" don't line up with the three backoff delays.
- **`POLICY_MODE` default:** the settings table says `strict`, but the local stack is described as allow-all unless you opt in.
- **5 GB transform time:** at the stated p95 rate it would reach the transform timeout.

Things I assumed rather than found in the notes (marked **Assumption**) include what each repo contains and the week-one pacing; they're listed in the last section.

To use it in the wiki, rename the file if you like and keep `diagrams/` beside it. Details are in `user_notes.md`.

Files are in `<workspace>\iteration-2\eval-3-ingestion-explainer\without_skill\run-1\outputs`:
- `report.md`
- `user_notes.md`
- `diagrams/`
