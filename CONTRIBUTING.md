# Contributing

Thanks for looking. This project is a skill, so a change is good when a document an agent writes gets easier for a person to read. That is a claim about readers, so it needs evidence, and the repository is set up to produce it.

## The most useful contribution: a document that went wrong

Open an issue with:

1. the prompt you gave the agent and which agent and model you used;
2. the document that came out (or the relevant part), and which input files it was written from;
3. what a reader could not find or understood wrongly, and which [rule](skills/document-formatting/references/review-rubric.md) it breaks, or that no rule covers it.

A rule that no existing rule covers is exactly what the [open items](review/skill-evolution/README.md#open-items) are made of.

## Set up

Python 3.9 or newer. The skill's scripts and the tests use only the standard library.

```bash
# unit tests for check_doc.py, source_set.py, check_links.py, package_skill.py and the validators
python -m unittest discover -s tests -v
# the skill against the Agent Skills spec and the plugin manifests
python tools/validate_skill.py
# every relative link and anchor in every Markdown file, letter case included
python tools/check_links.py
```

Only if you touch the review or the figures:

```bash
# regenerate charts and pages from the records
pip install -r review/tools/requirements.txt
python review/tools/build_review.py

# redraw the README figures
pip install playwright pillow && playwright install chromium
python tools/build_readme_assets.py
```

## Changing the skill

- **Keep `SKILL.md` lean.** It is loaded whenever the skill triggers (about 23 KB today). Put detail in `references/`, which is read on demand, and mechanical work in `scripts/`. The Agent Skills guidance is under 500 lines; `tools/validate_skill.py` warns above it.
- **Explain the why.** An instruction the agent understands is followed more reliably than one that is only shouted. Prefer a reason to an all-caps MUST.
- **The description is the trigger.** It must stay valid YAML as written (no `: ` inside an unquoted value, no angle brackets) and at most 1,024 characters. If you change it, rerun the trigger simulation in [`evals/README.md`](evals/README.md) and record the result under [`review/trigger-tests/`](review/trigger-tests/README.md).
- **Rubric and checker move together.** A rule marked `auto` in the rubric must be implemented in `check_doc.py` and covered by a test in `tests/`. A rule you add must say who it is for, its tier, and how to check it.
- **Scripts stay standard library only and run on Python 3.9.** No bytecode may be written into the skill folder.
- **Bump the version** in `SKILL.md` (`metadata.version`), `.claude-plugin/plugin.json` and `CHANGELOG.md` together; the validator checks that they agree.

## Evidence for a change

If your change is meant to improve documents, show it:

1. run the regression kit ([`evals/README.md`](evals/README.md)): the four scenarios with and without your version, the checker gate, the cold-reader test;
2. add the raw records under `review/` and rebuild the pages with `build_review.py`, so the numbers come from files;
3. say what the run cannot show. One run per arm is a smoke test, not a statistic.

## Privacy

Examples and records must not contain private or employer documents, names, paths or credentials. Use synthetic inputs.

## Pull requests

Keep them small and say what a reader gains. CI runs the tests, the validators and the link check on Ubuntu and Windows with Python 3.9 and 3.12. By contributing you agree that your contribution is licensed under the [MIT license](LICENSE).
