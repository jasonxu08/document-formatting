## What changes for a reader

<!-- One or two sentences. A change to the skill is good when a document an agent writes becomes easier for a person to read. -->

## Evidence

<!-- Tick what applies. -->

- [ ] `python -m unittest discover -s tests -v` passes
- [ ] `python tools/validate_skill.py` and `python tools/check_links.py` pass
- [ ] I ran the regression kit (`evals/README.md`) and added the records under `review/`, then rebuilt the pages with `python review/tools/build_review.py`
- [ ] A rule marked `auto` in the rubric is implemented in `check_doc.py` and has a test
- [ ] I changed the description: it is valid YAML as written, at most 1,024 characters, and I reran the trigger simulation
- [ ] I changed the version in `SKILL.md`, `.claude-plugin/plugin.json` and `CHANGELOG.md` together
- [ ] No private documents, names, local paths or credentials are included

## What this cannot show

<!-- One run per arm is a smoke test, not a statistic. Say what your evidence does not cover. -->
