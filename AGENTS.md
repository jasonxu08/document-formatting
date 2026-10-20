# AGENTS.md

Instructions for AI coding agents working in this repository. Humans: see [CONTRIBUTING.md](CONTRIBUTING.md).

## What this repository is

`document-formatting` is an [Agent Skill](https://agentskills.io): a folder with a `SKILL.md` that makes an AI agent write large documents for human readers first. The repository also holds the evidence for it: reviewed example documents, every raw review record, a regression kit and tests.

## Layout

| Path | Contents | Edit by hand? |
|---|---|---|
| `skills/document-formatting/` | the skill: `SKILL.md`, `assets/`, `references/`, `scripts/` | yes, with care (see below) |
| `examples/` | scenario inputs and the documents written with and without the skill | no: they are review evidence |
| `review/**/records/`, `review/skill-evolution/diffs/` | raw records | no |
| `review/**/README.md`, `review/iteration-*/eval-*.md`, `examples/**/README.md`, `review/assets/*.png` | generated pages and charts | no: run `python review/tools/build_review.py` |
| `review/method.md`, `review/maintainer-review.md`, `review/skill-evolution/README.md` | hand-written review pages | yes |
| `evals/` | the regression kit | yes |
| `tests/`, `tools/` | unit tests, validators, maintainer tools | yes |
| `README.md`, `README.zh-CN.md` | the front page, English and Chinese | yes; keep the two in step |

## Commands

```bash
# unit tests (standard library only)
python -m unittest discover -s tests -v
# the skill against the Agent Skills spec, plugin manifests, changelog
python tools/validate_skill.py
# every relative link and anchor in every Markdown file
python tools/check_links.py
# regenerate review pages and charts (needs matplotlib, numpy)
python review/tools/build_review.py
```

Run the first three before you finish any change. The scripts support Python 3.9 and newer.

## Rules for changing the skill

- Keep `SKILL.md` under 500 lines and lean; put detail in `references/` and mechanical work in `scripts/`.
- The `description` in the frontmatter is valid YAML as written (no `: ` in an unquoted value, no angle brackets) and at most 1,024 characters. Changing it means rerunning the trigger simulation in `evals/README.md`.
- A rubric rule marked `auto` must exist in `scripts/check_doc.py` and have a test in `tests/`.
- Scripts use only the standard library, never write bytecode into the skill folder, and make no network calls.
- When you change the version, change `metadata.version` in `SKILL.md`, `.claude-plugin/plugin.json` and `CHANGELOG.md` together.

## Rules for the records

- Never edit a raw record to improve a number. If a record is wrong, say so in the page that cites it.
- New records come from real runs and go under `review/`; then rebuild the pages. Every number on a generated page must come from a file.
- Do not add private documents, employer or customer names, local absolute paths or credentials anywhere. Sanitise or leave it out.

## Style

Write the way the skill asks documents to be written: the conclusion first, short paragraphs, plain headings, honest labels for what is inferred or unknown, and no claim without a record to point at.
