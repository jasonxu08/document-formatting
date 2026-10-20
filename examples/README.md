# Examples

Four scenarios, each run twice with the same prompt and the same inputs: once by an agent **without** the skill and once **with** it. The documents are exactly what the agents produced (only machine-specific paths were removed), so you can read both and judge for yourself.

| # | Scenario | Kind | Language | Without the skill | With the skill |
|---|---|---|---|---|---|
| 1 | [Upgrade risk report](01-upgrade-risk-report/README.md) | Decision report | English | 10/22 assertions · gate ❌ | 22/22 assertions · gate ✅ |
| 2 | [Dual-audience handoff](02-dual-audience-handoff/README.md) | Status and handoff | English | 9/22 assertions · gate ❌ | 22/22 assertions · gate ✅ |
| 3 | [Platform explainer for a new hire](03-ingestion-explainer/README.md) | Explainer | English | 12/21 assertions · gate ❌ | 20/21 assertions · gate ✅ |
| 4 | [Post-mortem in Chinese](04-postmortem-zh/README.md) | Root-cause report | Chinese | 12/23 assertions · gate ❌ | 22/23 assertions · gate ✅ |

## How to read an example

Each scenario folder holds:

- `input/`: the notes the agent was given,
- `without-skill/`: what an agent produced from the same prompt without the skill,
- `with-skill/`: what it produced with the skill (the main `report.md`, its siblings, its diagram and the chat reply it gave),
- `images/`: the first screen of each document as a reader sees it,
- a `README.md` with the prompt, what to look for and the scores.

The scores come from the [review records](../review/README.md): every assertion, every grader's evidence and every cold reader's answers are published.
