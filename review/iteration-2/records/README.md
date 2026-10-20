# Iteration 2 · raw records

What the agents wrote in this round, as they wrote it, apart from the publication edits listed in [method.md](../../method.md#what-is-not-published-and-why). The charts and pages that summarise these files are in [the iteration page](../README.md).

| File | What it is |
|---|---|
| `benchmark.json`, `benchmark.md` | pooled and per-scenario results, in the format of the skill-creator review viewer |
| `analyst-notes.json` | the analyst pass: what discriminated, what did not, problems in the skill and in the assertions |
| `coldreader-scores.json` | for every document, the key facts the cold reader recovered and missed, with scoring notes. The key facts themselves are in [`evals/cold_reader_facts.json`](../../../evals/cold_reader_facts.json) |
| `<scenario>/eval_metadata.json` | the prompt given to both agents and the assertions (derived from the rubric) |
| `<scenario>/<arm>/grading.json` | each assertion with pass or fail, the grader's evidence, and its critique of the assertions themselves |
| `<scenario>/<arm>/mechanical.json` | output of the tiered checker: findings by rule ID and tier, the gate result, and the statistics used in the pages |
| `<scenario>/<arm>/coldreader-answers.md` | the cold reader's answers to the six questions, from the first 60 lines only |
| `<scenario>/<arm>/executor-notes.md` | the executor's own notes on where the instructions were unclear or contradictory |
| `<scenario>/<arm>/timing.json` | an estimate from file timestamps; it includes idle waits, and tokens are 0 because the harness reports none |

`<arm>` is `with-skill` or `without-skill`. The documents these runs produced are in [`../../../examples/`](../../../examples/README.md).
