# Regression kit

Run these after you change `SKILL.md`, the rubric, the checker or the diagram guidance. The kit is not part of the installed skill; it lives here so that a change to the skill can be tested the same way the original was.

## What is here

| File | What it is |
|---|---|
| [`evals.json`](evals.json) | Four test cases: an upgrade risk report, a dual-audience handoff, an explainer and a post-mortem in Chinese. Each has the prompt, the list of input files and 21 to 23 assertions. Replace `{EXAMPLES}` in a prompt with the absolute path of the folder that holds the inputs (see step 1). |
| [`trigger-eval.json`](trigger-eval.json) | 22 realistic requests: 12 that should load the skill (including two "rewrite an unreadable report" cases and one in Chinese) and 10 near-misses that should not. |
| [`cold-reader-test.md`](cold-reader-test.md), [`cold_reader_facts.json`](cold_reader_facts.json) | The cold-reader protocol and the key facts, derived from the inputs, for the four cases. |
| [`prepare_cold_reader.py`](prepare_cold_reader.py) | Cuts the first 60 lines of a document, plus the images they use, into a clean folder for the cold reader. |

The inputs of the four cases are in [`examples/<scenario>/input/`](../examples/README.md).

## How to run a round

1. **Execute.** For every case, run one agent with the skill and one without. **Copy the `input/` folders to a scratch folder first and give the agents that path**: `examples/` also holds the documents written in earlier rounds, which an agent must not be able to read. Point the with-skill agent at the skill folder; give the baseline the same prompt and nothing else. Each agent saves its document as `report.md` (siblings beside it) and its final chat reply as `final_reply.md`.
2. **Automatic gate.** Run `python skills/document-formatting/scripts/check_doc.py --json <file>` on `report.md` and on every sibling Markdown file. The gate is no Blocker and at most two Majors in total. `stats.panel_words` feeds the compactness assertion.
3. **Grade.** Have a grader agent (not the executor) score every assertion except the one that starts with "Cold reader", quoting evidence, and ask it to critique the assertions as well. The rubric is [`review-rubric.md`](../skills/document-formatting/references/review-rubric.md). Compare pass rates with and without the skill.
4. **Cold reader.** `python evals/prepare_cold_reader.py report.md <folder> --lines 60`, then have a fresh agent that sees only that folder answer the six questions in [`cold-reader-test.md`](cold-reader-test.md). Score its answers against [`cold_reader_facts.json`](cold_reader_facts.json); 80% or more passes. This measures first-screen understanding and is a regression check, not a quality score.
5. **Triggering.** Give an agent the rule for choosing skills, the list of skills it would really have (with your description for this skill) and each request in `trigger-eval.json`, and ask which skills it would invoke first, without doing the tasks. Run it three times with the requests shuffled. Aim for every should-trigger request in every run and none of the near-misses. The [published runs](../review/trigger-tests/README.md) show the format.
6. **Record it.** Save the raw files under `review/` the way [iteration 2](../review/iteration-2/records/README.md) does (`grading.json`, `mechanical.json`, cold-reader answers and scores), then rebuild the pages with `python review/tools/build_review.py` so that every number comes from a file.

## Reference results

From the last full round and the checks since ([dashboard](../review/README.md)):

- Four cases, with the skill versus without: 86 of 88 assertions versus 43 of 88. Every with-skill document passed the automatic gate; every without-skill document failed it with 4 to 5 Majors.
- Cold reader: 22 of 24 key facts both ways, so first-screen recall is the same on these cases. The skill's measurable value there is structure and consistency, not recall.
- Triggering (simulated selection, 3 runs): 36 of 36 should-trigger, 0 of 30 near-misses.

## Rewriting an existing document

The rewrite flow has no fixture in this kit yet. To test it, write a long synthetic document of your own (a long running log, older notes that were overtaken, long raw output), have an agent rewrite it following [`rewriting.md`](../skills/document-formatting/references/rewriting.md), and require:

- `python skills/document-formatting/scripts/source_set.py verify <main.md> --source <original> --sha256 <hash>` ends with ALL OK (rubric rule G1);
- the human part states the current truth and labels superseded text correctly (G2);
- every restated claim links to its verbatim block (G3);
- a cold reader recovers at least 80% of the key facts you listed for that document.
