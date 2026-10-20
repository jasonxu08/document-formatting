# How the review was done

[← Review dashboard](README.md)

> ### What this page is
>
> Every number in this repository comes from one design: give the **same task to two fresh AI agents, one with the skill and one without**, then score both documents in independent ways. This page defines each instrument, says who did what, and lists what the evidence **cannot** show.
>
> **Strongest evidence:** the automatic gate (deterministic, no judgment involved). **Weakest:** the assertion pass rates, because the assertions come from the skill's own rubric.

| If you want to know | Read |
|---|---|
| who did what | [The cast](#the-cast) |
| what each score means | [The instruments](#the-instruments) |
| how far to trust the numbers | [What the evidence cannot show](#what-the-evidence-cannot-show) |
| where a number comes from, or how to redo it | [Where every number comes from](#where-every-number-comes-from) and [Reproduce it](#reproduce-it) |

## The cast

| Role | Who | What it did | Limit |
|---|---|---|---|
| Maintainer | a human, the repository owner | asked for the skill, chose the scope, asked the hard questions, decided what to keep ([the decision log](maintainer-review.md)) | did not rate individual documents blind; the viewer's feedback files are empty because the review happened in conversation |
| Orchestrator | the maintainer's coding agent (a GitHub Copilot CLI session) | wrote and revised the skill and the assertions, launched every run, scored the cold readers, read the results for patterns | it wrote the thing it tested, which is a conflict of interest |
| Executor | a fresh sub-agent per run | wrote the document from the prompt and the input files. The with-skill executor was pointed at the skill folder; the baseline got the same prompt and nothing else | one run per arm and scenario |
| Checker | [`check_doc.py`](../skills/document-formatting/scripts/check_doc.py) | applied the rubric rules that can be checked mechanically | cannot judge whether the content is right |
| Grader | a fresh sub-agent per run | read the document and the inputs, scored every assertion with quoted evidence, and critiqued the assertions themselves | not blind: its folders were named after the arm |
| Cold reader | a fresh sub-agent per document | saw only the first 60 lines and the images they use, then answered six fixed questions | not blind either: its folder sat inside the run folder |
| Analyst pass | the orchestrator | read the aggregated data for patterns the totals hide (assertions that never discriminate, contradictions between the skill and the tests) | the same agent that wrote the tests |

The sub-agents were run by the same coding-agent harness. The model each one used is whatever the session's sub-agent setting selected at the time and was not recorded per run.

## The instruments

### 1. Automatic gate

`check_doc.py` applies the rules of [`review-rubric.md`](../skills/document-formatting/references/review-rubric.md) that a program can decide: zone markers, link and anchor resolution, image files, leftover template placeholders, table and code-block size in the human zone, panel length, Mermaid where it will not render, machine-local paths. Each finding has a rule ID and a tier. The delivery gate is **no Blocker and at most two Majors**. It was run on the main file and on every sibling Markdown file. Iteration 1 used an older version with errors and warnings but no tiers.

### 2. Assertions, graded by an agent

| Round | Assertions per scenario | Where they came from |
|---|---|---|
| Iteration 1 | 14 to 15 | written by hand for each scenario |
| Iteration 2 | 21 to 23 | the rubric rules (A1 to F3), a few scenario-specific checks, one assertion for the automatic gate and one for the cold reader |

The grader scored each assertion pass or fail, quoted evidence, and was asked to critique the test as well (assertions that are ambiguous, unmeasurable or satisfied by anything). Those critiques are on every scenario page and produced several rubric fixes ([skill evolution](skill-evolution/README.md)).

**What a pass rate means.** The assertions are the skill's own rules, so a high pass rate with the skill shows that the skill makes an agent follow its rules. It does not show that the rules are the right ones for every reader. That question is what the cold reader is for.

### 3. Cold reader

The protocol is in [`evals/cold-reader-test.md`](../evals/cold-reader-test.md). Before any output existed, six key facts per scenario were derived **from the input files** (so both arms face the same list; [`cold_reader_facts.json`](../evals/cold_reader_facts.json)). A fresh agent then read only the first 60 lines of one document plus the images in them, and answered six fixed questions: what is it about, what is asked of whom by when, the main risks, the key components and how they relate, the numbers that matter, and what to read next. A fact counts as recovered when the answer states it substantially, with the right names and numbers in the right range. The orchestrator did the scoring; borderline calls are noted on the scenario pages. Pass is 80% or more.

On the synthetic scenarios this test **did not separate the arms** (22 of 24 facts each). A baseline agent that is asked for a decision report already puts the conclusion first. The test stays in the kit as a regression check.

### 4. Trigger test

A skill only helps if the agent loads it, so the description was tested the way the choice happens. An agent was given the rule for choosing skills, a list of about 100 real skills with this skill's description added, and 22 realistic requests (12 that should load the skill, 10 near-misses), and asked which skills it would invoke first. Three runs per description, shuffled differently each time. Details and limits: [trigger tests](trigger-tests/README.md).

## What the evidence cannot show

- **One run per arm and scenario**, in both iterations. There is no variance estimate. A difference of one assertion is noise.
- **AI judges throughout.** No human rated these documents blind, so the repository makes no claim about human preference.
- **The assertions measure compliance** with the skill's own rubric. The independent measure is the cold reader, and it did not separate the arms on the synthetic scenarios.
- **The inputs are synthetic.** The four scenarios were written for the tests, so they may be tidier than real notes.
- **The rewrite flow has no review round.** The rewriting guide and `source_set.py` (added in v0.4) are covered by unit tests of the script only; no published run exercises the method end to end.
- **The baseline is a bare agent** with no hint about readability. A baseline told "write this so a busy reader understands it in a minute" would probably close part of the gap; that comparison was not run.
- **Cost is not measured.** The harness reports no token counts and no true execution time (the timing files are estimates from file timestamps and include idle waits). The skill adds instructions to the context: `SKILL.md` is about 23 KB, roughly 5 to 6 thousand tokens, loaded whenever the skill triggers.
- **Most documents under review were written by earlier versions of the skill** (v0.1 and v0.2), not by v1.0.0. A smaller [final check](final-check/README.md) re-ran the four scenarios with v1.0.0 and scored them with the gate and the cold reader only. The trigger test of the final description is a simulation, not a run of any product's real skill loader.
- **Thresholds are provisional.** The 300-word panel budget, the 2,500-word human zone, 15-row tables and 25-line code blocks were calibrated on a handful of documents.

No run in iterations 1 and 2 was discarded or repeated to improve a score: each scenario has exactly one run per arm.

## What is not published, and why

| Withheld | Why |
|---|---|
| The list of installed skills used in the trigger simulation | it names internal project skills; the requests are in [`evals/trigger-eval.json`](../evals/trigger-eval.json) |
| PDF renders of the documents, `metrics.json` files and the viewer's `feedback.json` | derived or empty; nothing in them is not already on these pages |

For publication the records were edited in three ways: absolute machine paths were replaced by `<workspace>`, `<skill>` and `<home>`; the local account name became `user`; and a few short strings were reworded by hand (five that named a local project or session folder, three in the trigger-test answers and two in iteration-1 grading evidence; three more in the trigger-test answers that named an internal skill; and trigger request 21 with the recorded reasons that mentioned its incidental details; see the [trigger tests](trigger-tests/README.md#limits-of-this-test)). Before the diffs in [skill evolution](skill-evolution/README.md) were produced, a few illustrative phrases (example wording and numbers) in the older snapshots were replaced by the published wording. Grading, evidence, notes and checker output are otherwise as the agents wrote them. The prompts in `evals/evals.json` now point at `examples/<scenario>/input/` instead of the session workspace.

## Where every number comes from

| Number | Computed from |
|---|---|
| Assertions passed | `summary` in each run's `grading.json` (under `iteration-N/records/<scenario>/<arm>/`) |
| Automatic gate | `gate` in each run's `mechanical.json` |
| Cold-reader recall | [`coldreader-scores.json`](iteration-2/records/coldreader-scores.json) against [`evals/cold_reader_facts.json`](../evals/cold_reader_facts.json) |
| Trigger rates | `trigger-tests/records/*.answers.json` against [`evals/trigger-eval.json`](../evals/trigger-eval.json) |

The charts and every table on the scenario, iteration, trigger and final-check pages are produced by [`tools/build_review.py`](tools/build_review.py) from those files.

## Reproduce it

1. **Rebuild the pages and charts from the records:** `pip install -r review/tools/requirements.txt`, then `python review/tools/build_review.py`.
2. **Repeat the experiment with your own agent:** follow [`evals/README.md`](../evals/README.md). The prompts, assertions, cold-reader facts and trigger requests are all there.
3. **Check the checker yourself:** `python skills/document-formatting/scripts/check_doc.py examples/01-upgrade-risk-report/with-skill/report.md`, then the same on `without-skill/report.md`.
