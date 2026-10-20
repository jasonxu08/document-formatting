# Trigger tests · raw records

| File | What it is |
|---|---|
| `A-1.answers.json` to `A-3.answers.json` | three runs of the skill-selection simulation with description A (the skill's description at v0.3) |
| `B-1.answers.json` to `B-3.answers.json` | three runs with description B (adds the rewrite wording) |
| `C-1.answers.json` to `C-3.answers.json` | three runs with description C, the text published in `SKILL.md`; same requests and same order as the B runs |
| `desc-A.txt`, `desc-B.txt`, `desc-C.txt` | the descriptions under test |

Each answers file has one entry per request: `{"id": 1, "skills": [...], "why": "..."}`, where `skills` lists the skills the simulated agent would invoke first. The 22 requests are in [`evals/trigger-eval.json`](../../../evals/trigger-eval.json); the shuffled order differs per run. The prompt given to the simulating agent also held the rule for choosing skills and a list of about 100 real skills, which is not published because it names internal project skills. The summary, matrix and limits are on [the trigger-tests page](../README.md).
