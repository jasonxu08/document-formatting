# Iteration 1 · raw records

What the agents wrote in this round, as they wrote it, apart from the publication edits listed in [method.md](../../method.md#what-is-not-published-and-why). The charts and pages that summarise these files are in [the iteration page](../README.md).

| File | What it is |
|---|---|
| `benchmark.json`, `benchmark.md` | pooled and per-scenario results, in the format of the skill-creator review viewer |
| `analyst-notes.json` | the analyst pass: what discriminated, what did not, what the skill got wrong |
| `<scenario>/eval_metadata.json` | the prompt given to both agents and the hand-written assertions |
| `<scenario>/<arm>/grading.json` | each assertion with pass or fail, the grader's evidence, and its critique of the assertions themselves |
| `<scenario>/<arm>/mechanical.json` | output of the v0.1 checker (errors and warnings, no tiers) |
| `<scenario>/<arm>/timing.json` | an estimate from file timestamps; it includes idle waits, and tokens are 0 because the harness reports none |
| `<scenario>/<arm>/executor-notes.md` | the executor's own notes on where the instructions were unclear or contradictory |

`<arm>` is `with-skill` or `without-skill`. The documents these runs produced are in [`../outputs/`](../outputs/) and their first-screen screenshots in [`../images/`](../images/).
