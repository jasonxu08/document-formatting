# Security policy

## What this project runs

The skill is Markdown instructions plus two Python scripts that use only the standard library:

- `check_doc.py` reads one Markdown file and the files it links to, and prints findings. It writes nothing and makes no network calls.
- `source_set.py` reads a source document and writes the sibling Markdown files you name. It makes no network calls.

The instructions tell an agent to run these scripts and to draw diagrams with tools it finds installed (for example Graphviz or matplotlib). As with any skill, the instructions are part of what the agent executes: read `SKILL.md` before you install a skill from any source.

## Reporting a vulnerability

Please report a vulnerability privately through GitHub: **Security → Report a vulnerability** on this repository. If that is not available to you, open an issue that says only that you have a security report, without details, and I will contact you.

Examples of what is in scope: a script that can be made to read or write outside the paths it was given, an instruction in the skill that would make an agent expose data it was not asked to, or a release artifact that differs from the repository.

You can expect an acknowledgement within a week. This is a small project maintained by one person, so fixes follow as fast as that allows.

## Supported versions

The latest release receives fixes. Older versions are not maintained.

## Privacy note

The `npx skills add` command sends anonymous install telemetry to skills.sh. That is the skills CLI's behaviour, not this project's; set `DISABLE_TELEMETRY=1` to turn it off. The review records in this repository were sanitised before publication: absolute machine paths and account names were replaced ([method](review/method.md#what-is-not-published-and-why)).
