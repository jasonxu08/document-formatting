# Changelog

All notable changes to the skill are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the version is the skill's `metadata.version` in [`SKILL.md`](skills/document-formatting/SKILL.md), which `tools/validate_skill.py` keeps in step with the plugin manifest and this file.

## [Unreleased]

## [1.0.0] - 2026-10-20

First public release.

### Added

- The skill: a human-first workflow in [`SKILL.md`](skills/document-formatting/SKILL.md), a document skeleton, a diagram guide, a 35-rule [review rubric](skills/document-formatting/references/review-rubric.md) and a [rewriting guide](skills/document-formatting/references/rewriting.md).
- `scripts/check_doc.py`: a tiered checker (Blocker, Major, Minor) with `--json`, `--allow-mermaid`, `--machine-only` and `--slugs`, standard library only.
- `scripts/source_set.py`: `slice` copies verbatim ranges of a source into sibling files, `verify` proves that nothing was lost.
- The review: four scenarios with and without the skill, trigger tests, every raw record, a generated dashboard and the diffs of every version ([`review/`](review/README.md)).
- A regression kit ([`evals/`](evals/README.md)), unit tests, continuous integration, release packaging, Claude Code plugin manifests and an English and a Chinese README.

### Fixed

- `source_set.py slice` and the packaging script crashed on Python 3.9 (`Path.write_text(newline=)` needs 3.10). Found by the unit tests, which run on 3.9 in CI.

### Changed since the last fully graded version (v0.4)

- The description now covers requests to rewrite or restructure an existing long report, is valid YAML as written and fits the 1,024-character limit.
- The frontmatter gained `license`, `compatibility` and `metadata`.
- Rule A2: a table the user asked for by name is exempt when marked `<!-- requested-table -->`; the rewriting guide says how to give a short grouped map instead.
- Rule E2: evidence from a simulation or stand-in is called that every time it is mentioned.
- The rewriting guide tells the agent to mine the supporting notes (release notes, exceptions, known gaps) for caveats and carry them into the human part.

### Before 1.0.0

Versions 0.1 to 0.4 were never tagged. Each finding that led to a change, and the diffs, are in [how the skill evolved](review/skill-evolution/README.md).

[Unreleased]: https://github.com/jasonxu08/document-formatting/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/jasonxu08/document-formatting/releases/tag/v1.0.0
