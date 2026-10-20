"""Tests for tools/validate_skill.py, the Agent Skills specification validator.

Skills are built in temporary folders (<tmp>/skills/<name>/SKILL.md, like a real repository) and the validator
runs on them. Most tests call main() in this process (helpers.run); CommandLineTests start real child
processes. Frontmatter rules are run with the default parser (PyYAML when installed) and with --no-pyyaml,
the built-in parser, so the suite gives the same result with or without PyYAML. Rules that only the built-in
parser has (what it refuses to read) are tested with --no-pyyaml alone.
"""
import json
import re
import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers as h  # noqa: E402

DESCRIPTION = "description: Use this skill when testing the validator. It does nothing else."
GOOD_BODY = "# Demo skill\n\nSome guidance for the agent.\n"
MODES = (("default parser", ()), ("built-in parser", ("--no-pyyaml",)))
PLUGIN = {"name": "demo-skill", "version": "1.0.0"}
MARKETPLACE = {"name": "demo-marketplace", "owner": {"name": "Tester"},
               "plugins": [{"name": "demo-skill", "source": "./", "description": "Demo plugin"}]}


def frontmatter(replace=None, drop=(), extra=(), name="demo-skill"):
    """A SKILL.md frontmatter block. `replace` maps a field to the full text of its line(s)."""
    fields = (("name", "name: %s" % name), ("description", DESCRIPTION), ("license", "license: MIT"),
              ("compatibility", "compatibility: Needs nothing special."),
              ("metadata", 'metadata:\n  author: tester\n  version: "1.0.0"'))
    lines = [(replace or {}).get(key, text) for key, text in fields if key not in drop]
    return "---\n" + "\n".join(lines + list(extra)) + "\n---\n"


def make_skill(root, name="demo-skill", front=None, body=GOOD_BODY, files=None, folder=None):
    """Create root/skills/<folder or name>/SKILL.md plus `files` and return the skill folder."""
    skill = Path(str(root)) / "skills" / (folder or name)
    h.write(skill, "SKILL.md", (front if front is not None else frontmatter(name=name)) + body)
    for relpath, content in (files or {}).items():
        if isinstance(content, bytes):
            h.write_bytes(skill, relpath, content)
        else:
            h.write(skill, relpath, content)
    return skill


class Outcome(object):
    def __init__(self, code, out, err):
        self.code, self.out, self.err = code, out, err
        self.lines = out.splitlines()
        self.errors = [line for line in self.lines if line.startswith("ERROR ")]
        self.warnings = [line for line in self.lines if line.startswith("WARN ")]
        self.ok = [line for line in self.lines if line.startswith("OK ")]

    def text(self):
        return "exit %d\n%s%s" % (self.code, self.out, self.err)


class ValidatorCase(h.TempDirCase):
    def validate(self, *args, process=False, cwd=None):
        runner = h.run_script if process else h.run
        return Outcome(*runner(h.VALIDATOR, *args, cwd=cwd))

    def assertClean(self, outcome, name="demo-skill"):
        self.assertEqual((outcome.code, outcome.errors, outcome.warnings), (0, [], []), outcome.text())
        self.assertEqual(outcome.ok, ["OK " + name], outcome.text())

    def assertNoErrors(self, outcome):
        """Exit 0 and no ERROR line (warnings, and a missing OK line, are allowed)."""
        self.assertEqual((outcome.code, outcome.errors), (0, []), outcome.text())

    def assertFails(self, outcome, *keywords):
        """Exit 1, at least one ERROR line, no OK line, and every keyword in some ERROR line (any case)."""
        self.assertEqual(outcome.ok, [], outcome.text())
        self.assertRepoFails(outcome, *keywords)

    def assertRepoFails(self, outcome, *keywords):
        """Like assertFails, but the skill itself may still be reported OK (the fault is in a repository file)."""
        self.assertEqual(outcome.code, 1, outcome.text())
        self.assertTrue(outcome.errors, outcome.text())
        joined = "\n".join(outcome.errors).lower()
        for keyword in keywords:
            self.assertIn(keyword.lower(), joined, outcome.text())

    def each_mode(self, skill, check):
        """Run the validator on `skill` with each frontmatter parser and call check(outcome)."""
        for label, flags in MODES:
            with self.subTest(parser=label):
                check(self.validate(skill, *flags))


class RealSkillTests(ValidatorCase):
    def test_the_real_skill_validates_clean_with_either_parser_and_in_strict_mode(self):
        outcome = self.validate(h.SKILL, process=True)
        self.assertClean(outcome, "document-formatting")
        for flags in (("--strict",), ("--no-pyyaml",), ("--strict", "--no-pyyaml")):
            with self.subTest(flags=flags):
                self.assertClean(self.validate(h.SKILL, *flags), "document-formatting")

    def test_running_without_arguments_validates_every_skill_folder_of_the_repo(self):
        names = sorted(p.name for p in (h.REPO / "skills").iterdir() if (p / "SKILL.md").is_file())
        self.assertIn("document-formatting", names)
        outcome = self.validate(process=True)
        self.assertEqual((outcome.code, outcome.errors), (0, []), outcome.text())
        self.assertEqual(outcome.ok, ["OK " + name for name in names])

    def test_a_broken_copy_of_the_real_skill_is_noticed(self):
        copy = self.tmp / "skills" / "document-formatting"
        shutil.copytree(str(h.SKILL), str(copy))
        self.assertClean(self.validate(copy), "document-formatting")
        text = h.read(copy / "SKILL.md")
        renamed = re.sub(r"(?m)^name:", "nom:", text, count=1)
        self.assertNotEqual(renamed, text)
        h.write(copy, "SKILL.md", renamed)
        self.assertFails(self.validate(copy), "name")


class FrontmatterShapeTests(ValidatorCase):
    def test_a_good_skill_is_clean_and_lines_name_the_file(self):
        skill = make_skill(self.tmp)
        self.each_mode(skill, self.assertClean)
        outcome = self.validate(make_skill(self.tmp, name="other-skill", front=frontmatter(drop=("name",)),
                                           folder="other-skill"))
        self.assertTrue(outcome.errors[0].startswith("ERROR skills/other-skill/SKILL.md: "), outcome.text())

    def test_missing_skill_md_is_an_error(self):
        empty = self.tmp / "skills" / "empty-skill"
        empty.mkdir(parents=True)
        outcome = self.validate(empty)
        self.assertFails(outcome, "SKILL.md")

    def test_missing_or_unclosed_frontmatter_is_an_error(self):
        cases = {"none at all": "# Just a heading\n\nNo frontmatter.\n",
                 "not closed": "---\nname: demo-skill\n" + DESCRIPTION + "\n\n# Body\n",
                 "not on the first line": "\n" + frontmatter() + GOOD_BODY}
        for label, text in cases.items():
            with self.subTest(case=label):
                skill = make_skill(self.tmp, front="", body=text)
                self.assertFails(self.validate(skill), "frontmatter")

    def test_bom_crlf_line_endings_and_trailing_spaces_are_accepted(self):
        text = "\ufeff" + (frontmatter() + GOOD_BODY).replace("---\n", "---  \n").replace("\n", "\r\n")
        skill = make_skill(self.tmp, front="", body=text)
        self.each_mode(skill, self.assertClean)

    def test_invalid_yaml_is_an_error_with_either_parser(self):
        skill = make_skill(self.tmp, front=frontmatter(replace={"description": "description: Use when: testing"}))
        self.each_mode(skill, lambda outcome: self.assertFails(outcome, "description"))

    def test_valid_quoting_comments_and_nesting_are_read_by_either_parser(self):
        front = frontmatter(replace={
            "name": "name: demo-skill  # the folder name",
            "description": 'description: "Quoted: a colon, \'single\' quotes, and a \\" double quote"',
            "license": "license: 'MIT'",
            "metadata": 'metadata:\n  author: "tester"\n  version: \'1.0.0\'\n  url: https://example.com/x'})
        self.each_mode(make_skill(self.tmp, front=front), self.assertClean)

    def test_builtin_parser_rejects_values_real_yaml_parsers_choke_on(self):
        starters = ["[", "{", "*", "&", "!", "|", ">", "%", "@", "`"]
        for char in starters:
            with self.subTest(starts_with=char):
                value = "%sUse this skill when testing." % char
                skill = make_skill(self.tmp, front=frontmatter(replace={"description": "description: " + value}))
                self.assertFails(self.validate(skill, "--no-pyyaml"), "YAML-safe", "description")
        skill = make_skill(self.tmp, front=frontmatter(replace={"description": "description: Ends with a colon:"}))
        self.assertFails(self.validate(skill, "--no-pyyaml"), "YAML-safe")
        for char in (c for c in starters if c != ">"):  # a quoted description may not contain '>' either
            with self.subTest(quoted=char):
                value = '"%sUse this skill when testing."' % char
                skill = make_skill(self.tmp, front=frontmatter(replace={"description": "description: " + value}))
                self.assertClean(self.validate(skill, "--no-pyyaml"))

    def test_builtin_parser_refuses_structure_it_cannot_read(self):
        continued = {"description": DESCRIPTION + "\n  and a second line"}
        cases = {"a multi-line plain value": (continued, ()),
                 "a list": (None, ["tags:", "  - one"]),
                 "nesting two levels deep": (None, ["extra:", "  inner:", "    deeper: x"]),
                 "a tab for indentation": (None, ["extra:", "\tkey: x"]),
                 "a duplicated key": (None, ["license: Apache-2.0"]),
                 "an unterminated quote": (None, ['extra: "never closed']),
                 "text after a closing quote": (None, ['extra: "closed" and more'])}
        for label, (replace, extra) in cases.items():
            with self.subTest(case=label):
                skill = make_skill(self.tmp, front=frontmatter(replace=replace, extra=extra))
                self.assertFails(self.validate(skill, "--no-pyyaml"))


class FieldRuleTests(ValidatorCase):
    def broken(self, replace=None, drop=(), extra=(), name="demo-skill", folder=None):
        return make_skill(self.tmp, name=name, folder=folder,
                          front=frontmatter(replace=replace, drop=drop, extra=extra, name=name))

    def test_name_rules(self):
        cases = (("missing", {"drop": ("name",)}),
                 ("empty", {"replace": {"name": "name:"}}),
                 ("upper case", {"name": "Demo-Skill"}), ("underscore", {"name": "demo_skill"}),
                 ("leading hyphen", {"name": "-demo"}), ("trailing hyphen", {"name": "demo-"}),
                 ("double hyphen", {"name": "demo--skill"}), ("a space", {"replace": {"name": "name: demo skill"}}),
                 ("a number", {"replace": {"name": "name: 123"}}),
                 ("65 characters", {"name": "a" * 65}),
                 ("different from the folder", {"replace": {"name": "name: other-name"}}))
        for label, options in cases:
            with self.subTest(name=label):
                options = dict(options)
                folder = options.get("name", "demo-skill")
                skill = self.broken(folder=folder, **options)
                self.each_mode(skill, lambda outcome: self.assertFails(outcome, "name"))

    def test_valid_names_are_accepted(self):
        for name in ("a", "a1-b2", "x" * 64):
            with self.subTest(name=name[:12]):
                self.each_mode(self.broken(name=name, folder=name), self.assertNoErrors)

    def test_description_rules(self):
        too_long = "description: " + "a" * 1025
        cases = (("missing", {"drop": ("description",)}), ("empty", {"replace": {"description": "description:"}}),
                 ("empty quotes", {"replace": {"description": 'description: ""'}}),
                 ("1025 characters", {"replace": {"description": too_long}}),
                 ("an angle bracket", {"replace": {"description": 'description: "Use <this> skill"'}}),
                 ("a closing angle bracket", {"replace": {"description": 'description: "a > b"'}}),
                 ("a list", {"replace": {"description": "description: [a, b]"}}))
        for label, options in cases:
            with self.subTest(description=label):
                self.each_mode(self.broken(**options), lambda outcome: self.assertFails(outcome, "description"))
        exactly = self.broken(replace={"description": "description: " + "a" * 1024})
        self.each_mode(exactly, self.assertNoErrors)

    def test_optional_field_types_and_limits(self):
        too_long = "compatibility: " + "c" * 501
        cases = (
            ("license is a number", {"license": "license: 123"}, (), "license"),
            ("compatibility over 500 characters", {"compatibility": too_long}, (), "compatibility"),
            ("compatibility is a list", {"compatibility": "compatibility: [a]"}, (), "compatibility"),
            ("metadata is a string", {"metadata": "metadata: plain"}, (), "metadata"),
            ("metadata is empty", {"metadata": "metadata:"}, (), "metadata"),
            ("metadata version is a float", {"metadata": "metadata:\n  version: 1.0"}, (), "version"),
            ("metadata value is a boolean", {"metadata": "metadata:\n  draft: yes"}, (), "draft"),
            ("metadata value is an integer", {"metadata": "metadata:\n  build: 42"}, (), "build"),
            ("metadata value is a date", {"metadata": "metadata:\n  released: 2026-10-19"}, (), "released"),
            ("allowed-tools is a list", None, ["allowed-tools: [Read, Grep]"], "allowed-tools"),
        )
        for label, replace, extra, keyword in cases:
            with self.subTest(case=label):
                skill = self.broken(replace=replace, extra=extra)
                self.each_mode(skill, lambda outcome: self.assertFails(outcome, keyword))
        fine = (
            ("compatibility at the limit", {"compatibility": "compatibility: " + "c" * 500}, ()),
            ("metadata values that are strings", {"metadata": "metadata:\n  version: 1.0.0\n  note: 'text'\n"
                                                              "  build: \"42\""}, ()),
            ("allowed-tools as a string", None, ["allowed-tools: Read Grep Bash(git:*)"]),
        )
        for label, replace, extra in fine:
            with self.subTest(fine=label):
                self.each_mode(self.broken(replace=replace, extra=extra), self.assertNoErrors)

    def test_unknown_top_level_fields_are_warnings_and_strict_mode_fails_on_them(self):
        skill = self.broken(extra=["version: 1.0.0", "author: somebody"])
        for label, flags in MODES:
            with self.subTest(parser=label):
                outcome = self.validate(skill, *flags)
                self.assertEqual((outcome.code, outcome.errors, outcome.ok), (0, [], []), outcome.text())
                self.assertEqual(len(outcome.warnings), 2, outcome.text())
                self.assertIn("'author'", outcome.warnings[0])  # sorted by field name
                self.assertIn("'version'", outcome.warnings[1])
                strict = self.validate(skill, "--strict", *flags)
                self.assertEqual((strict.code, strict.errors), (1, []), strict.text())


class BodyTests(ValidatorCase):
    def test_a_skill_md_over_500_lines_is_a_warning(self):
        front = frontmatter()
        for lines, warned in ((500, False), (501, True)):
            with self.subTest(lines=lines):
                body = "".join("Line %d.\n" % i for i in range(lines - len(front.splitlines())))
                skill = make_skill(self.tmp, front=front, body=body)
                outcome = self.validate(skill)
                self.assertEqual((outcome.code, outcome.errors), (0, []), outcome.text())
                self.assertEqual(len(outcome.warnings), 1 if warned else 0, outcome.text())

    def test_relative_links_must_exist_and_external_links_and_anchors_are_ignored(self):
        files = {"references/guide.md": "# Guide\n", "assets/logo.png": b"png"}
        fine = ("See [the guide](references/guide.md), [a section](references/guide.md#intro), "
                "[the web](https://example.com/x), [mail](mailto:a@b.example), [top](#top), "
                "[a titled one](references/guide.md \"Guide\") and ![logo](assets/logo.png).\n")
        self.assertClean(self.validate(make_skill(self.tmp, body=GOOD_BODY + fine, files=files)))
        broken = ("[gone](references/gone.md), ![gone too](assets/gone.png) and [fragment](other/gone.md#x).\n"
                  "\n[ref]: references/gone-ref.md\n")
        outcome = self.validate(make_skill(self.tmp, body=GOOD_BODY + broken, files=files))
        self.assertEqual(len(outcome.errors), 4, outcome.text())
        self.assertFails(outcome, "references/gone.md", "assets/gone.png", "other/gone.md", "gone-ref.md")

    def test_backticked_reference_paths_must_exist(self):
        files = {"references/guide.md": "# Guide\n", "scripts/tool.py": "print(1)\n"}
        fine = ("Read `references/guide.md`, run `python scripts/tool.py <input> --flag`, see the `scripts/` folder, "
                "and ignore `references/*.md`, `scripts/<name>.py`, `assets/{doc}.png` and `docs/other.md`.\n")
        self.assertClean(self.validate(make_skill(self.tmp, body=GOOD_BODY + fine, files=files)))
        broken = "Read `references/gone.md` or run `python scripts/gone.py <input>` or open `assets/`.\n"
        outcome = self.validate(make_skill(self.tmp, body=GOOD_BODY + broken, files=files))
        self.assertEqual(len(outcome.errors), 3, outcome.text())
        self.assertFails(outcome, "references/gone.md", "scripts/gone.py", "assets/")

    def test_references_inside_code_blocks_are_examples_not_references(self):
        block = "```bash\npython scripts/nothing.py\n[x](nowhere.md)\n```"
        tilde = "~~~\n`references/none.md`\n~~~"
        self.assertClean(self.validate(make_skill(self.tmp, body=GOOD_BODY + "\n" + block + "\n\n" + tilde + "\n")))

    def test_a_path_that_differs_only_in_letter_case_is_an_error(self):
        skill = make_skill(self.tmp, body=GOOD_BODY + "See [the guide](references/Guide.md).\n",
                           files={"references/guide.md": "# Guide\n"})
        self.assertFails(self.validate(skill), "references/Guide.md")


class FilesTests(ValidatorCase):
    def test_python_files_must_compile_and_validating_writes_no_bytecode(self):
        files = {"scripts/good.py": "def fine():\n    return 1\n", "scripts/nested/bad.py": "def broken(:\n"}
        skill = make_skill(self.tmp, files=files)
        outcome = self.validate(skill)
        self.assertFails(outcome, "bad.py", "compile")
        self.assertEqual(len(outcome.errors), 1, outcome.text())
        self.assertFalse(list(skill.rglob("__pycache__")), "validation must not write bytecode")
        self.assertClean(self.validate(make_skill(self.tmp, name="good-skill", files={"scripts/good.py": "x = 1\n"})),
                         "good-skill")

    def test_python_syntax_warnings_are_reported_as_warnings(self):
        skill = make_skill(self.tmp, files={"scripts/escape.py": 'pattern = "\\d+"\n'})
        outcome = self.validate(skill)
        self.assertEqual((outcome.code, outcome.errors, outcome.ok), (0, [], []), outcome.text())
        self.assertTrue(outcome.warnings, outcome.text())
        self.assertIn("escape.py", outcome.warnings[0])

    def test_files_over_1_mb_and_pycache_folders_are_warnings(self):
        megabyte = 1024 * 1024
        skill = make_skill(self.tmp, files={"assets/exact.bin": b"0" * megabyte,
                                            "assets/big.bin": b"0" * (megabyte + 1),
                                            "scripts/__pycache__/tool.cpython-39.pyc": b"pyc"})
        outcome = self.validate(skill)
        self.assertEqual((outcome.code, outcome.errors, outcome.ok), (0, [], []), outcome.text())
        self.assertEqual(len(outcome.warnings), 2, outcome.text())
        joined = "\n".join(outcome.warnings)
        self.assertIn("big.bin", joined)
        self.assertNotIn("exact.bin", joined)
        self.assertIn("__pycache__", joined)
        strict = self.validate(skill, "--strict")
        self.assertEqual(strict.code, 1, strict.text())


class RepositoryFilesTests(ValidatorCase):
    def setUp(self):
        super().setUp()
        self.skill = make_skill(self.tmp)

    def put(self, relpath, data):
        text = data if isinstance(data, str) else json.dumps(data)
        h.write(self.tmp, relpath, text)

    def test_plugin_files_and_changelog_are_optional_and_silent_when_absent(self):
        self.assertClean(self.validate(self.skill))

    def test_valid_manifests_and_changelog_are_clean(self):
        self.put(".claude-plugin/plugin.json", PLUGIN)
        self.put(".claude-plugin/marketplace.json", MARKETPLACE)
        self.put("CHANGELOG.md", "# Changelog\n\n## [Unreleased]\n\n## [1.0.0] - 2026-10-19\n\n- First release.\n")
        self.assertClean(self.validate(self.skill))

    def test_plugin_json_must_be_a_json_object_with_a_name(self):
        cases = (("invalid JSON", "{not json"), ("a list", "[]"), ("no name", {"version": "1.0.0"}),
                 ("an empty name", {"name": " "}))
        for label, data in cases:
            with self.subTest(plugin=label):
                self.put(".claude-plugin/plugin.json", data)
                self.assertRepoFails(self.validate(self.skill), "plugin.json")

    def test_marketplace_json_rules(self):
        def plugins(**entry):
            base = dict(MARKETPLACE["plugins"][0])
            base.update(entry)
            return dict(MARKETPLACE, plugins=[base])
        broken = (
            ("invalid JSON", "{nope"),
            ("no name", {key: value for key, value in MARKETPLACE.items() if key != "name"}),
            ("no owner", {key: value for key, value in MARKETPLACE.items() if key != "owner"}),
            ("owner without a name", dict(MARKETPLACE, owner={})),
            ("no plugins", dict(MARKETPLACE, plugins=[])),
            ("plugins is not a list", dict(MARKETPLACE, plugins={"name": "demo-skill"})),
            ("entry without a description", plugins(description="")),
            ("entry without a source", {"name": "m", "owner": {"name": "t"},
                                        "plugins": [{"name": "demo-skill", "description": "d"}]}),
            ("entry name differs from plugin.json", plugins(name="other-plugin")),
            ("relative source that does not exist", plugins(source="./missing")),
            ("relative source outside the repository", plugins(source="./../elsewhere")),
        )
        self.put(".claude-plugin/plugin.json", PLUGIN)
        for label, data in broken:
            with self.subTest(marketplace=label):
                self.put(".claude-plugin/marketplace.json", data)
                self.assertRepoFails(self.validate(self.skill), "marketplace.json")
        fine = (("a source folder", plugins(source="./skills/demo-skill")),
                ("a remote source", plugins(source={"source": "github", "repo": "owner/repo"})),
                ("a remote string source", plugins(source="owner/repo")))
        for label, data in fine:
            with self.subTest(marketplace=label):
                self.put(".claude-plugin/marketplace.json", data)
                self.assertClean(self.validate(self.skill))

    def test_plugin_version_must_equal_the_skill_metadata_version(self):
        self.put(".claude-plugin/plugin.json", dict(PLUGIN, version="1.0.1"))
        self.assertFails(self.validate(self.skill), "version", "plugin.json")
        self.put(".claude-plugin/plugin.json", {"name": "demo-skill"})
        self.assertClean(self.validate(self.skill))  # no version in plugin.json: nothing to compare
        self.put(".claude-plugin/plugin.json", PLUGIN)
        no_version = make_skill(self.tmp, front=frontmatter(replace={"metadata": "metadata:\n  author: tester"}))
        self.assertFails(self.validate(no_version), "version")

    def test_changelog_without_the_skill_version_is_a_warning(self):
        for label, text in (("another version", "# Changelog\n\n## [0.9.0] - 2026-01-01\n"),
                            ("only unreleased", "# Changelog\n\n## [Unreleased]\n\n- Things.\n"),
                            ("a deeper heading", "# Changelog\n\n### [1.0.0] - 2026-10-19\n"),
                            ("empty", "")):
            with self.subTest(changelog=label):
                self.put("CHANGELOG.md", text)
                outcome = self.validate(self.skill)
                self.assertEqual((outcome.code, outcome.errors, outcome.ok), (0, [], []), outcome.text())
                self.assertEqual(len(outcome.warnings), 1, outcome.text())
                self.assertIn("CHANGELOG.md", outcome.warnings[0])
                self.assertEqual(self.validate(self.skill, "--strict").code, 1)
        for label, text in (("a date", "## [1.0.0] - 2026-10-19\n"), ("no date", "## [1.0.0]\n"),
                            ("a v prefix and brackets", "## [v1.0.0] (2026-10-19)\n"),
                            ("later in the file", "## [2.0.0]\n\n## [1.0.0] - 2026-01-01\n")):
            with self.subTest(changelog=label):
                self.put("CHANGELOG.md", text)
                self.assertClean(self.validate(self.skill))

    def test_skills_outside_a_skills_folder_ignore_the_validators_own_repository_files(self):
        self.put(".claude-plugin/plugin.json", "{not json")
        loose = self.tmp / "loose" / "demo-skill"
        h.write(loose, "SKILL.md", frontmatter() + GOOD_BODY)
        self.assertClean(self.validate(loose))


class CommandLineTests(ValidatorCase):
    """Most of these start real child processes: exit status, stdout and stderr as a user or CI job sees them."""

    def test_usage_errors_exit_two_and_are_reported_on_stderr(self):
        outcome = self.validate(self.tmp / "nope", process=True)
        self.assertEqual((outcome.code, outcome.out), (2, ""), outcome.text())
        self.assertTrue(outcome.err.strip())
        unknown = self.validate("--bogus")
        self.assertEqual((unknown.code, unknown.out), (2, ""), unknown.text())

    def test_a_copy_of_the_validator_uses_the_repository_around_it(self):
        (self.tmp / "tools").mkdir()
        copy = self.tmp / "tools" / "validate_skill.py"
        shutil.copy2(str(h.VALIDATOR), str(copy))

        def validate_copy(process=False):
            runner = h.run_script if process else h.run
            return Outcome(*runner(copy, cwd=self.tmp))

        self.assertEqual(validate_copy().code, 2)  # no skills yet: nothing to validate
        make_skill(self.tmp, name="beta-skill")
        make_skill(self.tmp, name="alpha-skill")
        (self.tmp / "skills" / "not-a-skill").mkdir()  # no SKILL.md: not a skill
        outcome = validate_copy()
        self.assertEqual((outcome.code, outcome.ok), (0, ["OK alpha-skill", "OK beta-skill"]), outcome.text())
        h.write(self.tmp, ".claude-plugin/plugin.json", json.dumps(dict(PLUGIN, version="9.9.9")))
        broken = validate_copy(process=True)
        self.assertEqual(broken.code, 1, broken.text())
        self.assertEqual(len([line for line in broken.errors if "plugin.json" in line]), 2, broken.text())

    def test_output_is_sorted_and_the_same_whatever_the_argument_order_or_hash_seed(self):
        zeta = make_skill(self.tmp, name="zeta-skill", front=frontmatter(drop=("description",), name="zeta-skill"))
        alpha = make_skill(self.tmp, name="alpha-skill")
        # four unknown fields give four warnings: their order, like everything else, must not depend on
        # the hash seed or on how the folders were listed on the command line
        mid = make_skill(self.tmp, name="mid-skill", front=frontmatter(
            extra=["zz: 1", "aa: 1", "mm: 1", "bb: 1"], name="mid-skill"))
        here = self.validate(zeta, alpha, mid)
        code, out, err = h.run_script(h.VALIDATOR, mid, alpha, zeta, alpha, env={"PYTHONHASHSEED": "7"})
        other = Outcome(code, out, err)
        self.assertEqual(here.out, other.out)
        self.assertEqual(other.code, 1)
        owners = [line.split(":")[0].split("/")[1] for line in other.lines if line.startswith(("ERROR", "WARN"))]
        self.assertEqual(owners, sorted(owners))
        self.assertEqual(other.ok, ["OK alpha-skill"])

    def test_a_skill_md_path_is_accepted_for_its_folder(self):
        skill = make_skill(self.tmp)
        self.assertClean(self.validate(skill / "SKILL.md"))

    def test_the_module_is_importable_and_main_returns_exit_codes(self):
        module = h.load_script(h.VALIDATOR)
        skill = make_skill(self.tmp)
        self.assertEqual(self.validate(skill).code, 0)
        self.assertEqual(self.validate("--bogus").code, 2)
        self.assertTrue(callable(module.main))
        self.assertEqual(module.NAME.pattern, r"^[a-z0-9]+(-[a-z0-9]+)*$")


if __name__ == "__main__":
    unittest.main()
