"""Tests for tools/check_links.py, the relative-link and anchor checker.

Each test builds a tiny repository in a temporary folder and points the checker's ROOT at it, so the real
documents are never touched. The letter-case rule is tested through wrong_case() directly, because that
function lists the folder instead of asking the file system: the result is the same on Windows, macOS and
Linux, which treat a wrong-case link differently (it resolves on the first two, GitHub and Linux do not).
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers as h  # noqa: E402

checker = h.load_script("tools/check_links.py")


class LinkCase(h.TempDirCase):
    def setUp(self):
        super().setUp()
        self.root = self.tmp.resolve()
        patcher = mock.patch.object(checker, "ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        checker._LISTINGS.clear()
        self.addCleanup(checker._LISTINGS.clear)

    def page(self, relpath, text):
        return h.write(self.root, relpath, text)

    def problems(self, relpath):
        return checker.check_file(self.root / relpath, {})

    def messages(self, relpath):
        return [message for _, message in self.problems(relpath)]


class ResolutionTests(LinkCase):
    def test_a_working_link_and_a_working_anchor_pass(self):
        self.page("docs/a.md", "[b](b.md#section-one) and [self](#top)\n\n# Top\n")
        self.page("docs/b.md", "# B\n\n## Section One\n")
        self.assertEqual(self.problems("docs/a.md"), [])

    def test_a_missing_file_is_reported_with_its_line(self):
        self.page("docs/a.md", "text\n\n[gone](nope.md)\n")
        self.assertEqual(self.problems("docs/a.md"), [(3, "missing file: nope.md")])

    def test_a_missing_anchor_is_reported(self):
        self.page("docs/a.md", "[b](b.md#no-such-heading)\n")
        self.page("docs/b.md", "# B\n")
        self.assertEqual(self.messages("docs/a.md"), ["no such anchor: b.md#no-such-heading"])

    def test_images_and_html_attributes_are_checked_too(self):
        self.page("docs/a.md", '![alt](img/missing.png)\n\n<img src="img/also-missing.png" width="10">\n')
        self.assertEqual(len(self.problems("docs/a.md")), 2)

    def test_dot_dot_segments_resolve_from_the_page_folder(self):
        self.page("README.md", "# Readme\n")
        self.page("docs/deep/a.md", "[up](../../README.md)\n")
        self.assertEqual(self.problems("docs/deep/a.md"), [])

    def test_a_root_relative_link_starts_at_the_repository_root(self):
        self.page("README.md", "# Readme\n")
        self.page("docs/a.md", "[root](/README.md)\n")
        self.assertEqual(self.problems("docs/a.md"), [])

    def test_percent_encoded_paths_are_decoded(self):
        self.page("docs/with space.md", "# Spaced\n")
        self.page("docs/a.md", "[s](with%20space.md)\n")
        self.assertEqual(self.problems("docs/a.md"), [])


class IgnoredTests(LinkCase):
    def test_links_in_code_are_not_links(self):
        self.page("docs/a.md", "`[x](nope.md)`\n\n```\n[y](nope.md)\n```\n")
        self.assertEqual(self.problems("docs/a.md"), [])

    def test_urls_with_a_scheme_are_not_fetched(self):
        self.page("docs/a.md", "[web](https://example.com/x) [mail](mailto:a@b.c) [proto](//cdn.example/x.js)\n")
        self.assertEqual(self.problems("docs/a.md"), [])

    def test_the_illustrative_link_in_skill_md_is_allowed_but_only_that_one(self):
        body = "[sample](#2-the-dependency-map) [other](#2-another-sample)\n"
        self.page("skills/document-formatting/SKILL.md", body)
        self.assertEqual(self.messages("skills/document-formatting/SKILL.md"), ["no such anchor: #2-another-sample"])

    def test_evidence_folders_are_skipped_unless_all_is_asked_for(self):
        self.page("README.md", "# Readme\n")
        self.page("examples/01/with-skill/report.md", "[x](nope.md)\n")
        self.page("examples/01/README.md", "# Page\n")
        names = lambda include: sorted(p.relative_to(self.root).as_posix()
                                       for p in checker.markdown_files([self.root], include))
        self.assertEqual(names(False), ["README.md", "examples/01/README.md"])
        self.assertEqual(names(True), ["README.md", "examples/01/README.md", "examples/01/with-skill/report.md"])


class LetterCaseTests(LinkCase):
    def test_a_wrong_case_file_name_is_named(self):
        self.page("docs/Guide.md", "# Guide\n")
        self.assertEqual(checker.wrong_case(self.root, "docs/guide.md"), "'guide.md' is 'Guide.md' on disk")

    def test_a_wrong_case_folder_name_is_named(self):
        self.page("Docs/guide.md", "# Guide\n")
        self.assertEqual(checker.wrong_case(self.root, "docs/guide.md"), "'docs' is 'Docs' on disk")

    def test_the_exact_case_is_fine(self):
        self.page("Docs/Guide.md", "# Guide\n")
        self.assertIsNone(checker.wrong_case(self.root, "Docs/Guide.md"))

    def test_dot_dot_segments_do_not_confuse_the_comparison(self):
        self.page("docs/Guide.md", "# Guide\n")
        self.page("other/a.md", "# A\n")
        self.assertIsNone(checker.wrong_case(self.root / "other", "../docs/Guide.md"))
        self.assertEqual(checker.wrong_case(self.root / "other", "../docs/guide.md"), "'guide.md' is 'Guide.md' on disk")

    def test_a_target_outside_the_repository_is_not_compared(self):
        self.assertIsNone(checker.wrong_case(self.root, "../elsewhere/File.md"))

    def test_a_wrong_case_link_is_reported_by_check_file_on_every_platform(self):
        # Windows and macOS: "wrong letter case". Linux: the file is simply not there.
        self.page("docs/Guide.md", "# Guide\n")
        self.page("docs/a.md", "[g](guide.md)\n")
        messages = self.messages("docs/a.md")
        self.assertEqual(len(messages), 1)
        self.assertRegex(messages[0], r"^(wrong letter case|missing file)")


class CommandLineTests(LinkCase):
    def test_exit_code_and_summary_for_a_clean_repository(self):
        self.page("README.md", "# Readme\n\n[self](#readme)\n")
        code, out, _ = h.run_main("tools/check_links.py")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "checked 1 Markdown files: all links resolve")

    def test_exit_code_and_report_for_a_broken_repository(self):
        self.page("README.md", "# Readme\n\n[gone](nope.md)\n")
        code, out, _ = h.run_main("tools/check_links.py")
        self.assertEqual(code, 1)
        self.assertIn("README.md:3: missing file: nope.md", out)
        self.assertIn("1 broken links", out)


if __name__ == "__main__":
    unittest.main()
