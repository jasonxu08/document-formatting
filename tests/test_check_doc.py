"""Tests for skills/document-formatting/scripts/check_doc.py.

Each test builds a small document from helpers.good_doc() (which the checker passes with no finding at
all), breaks exactly one thing, runs the real script and asserts on rule ids and tiers, never on message
wording. Most tests call the script's main() in this process (helpers.run); CommandLineTests start real
child processes.

Exit codes seen: 0 no blocker (majors and minors do not fail the run), 1 at least one blocker, 2 file not
found or a command-line usage error. `--json` prints the keys file, stats, gate, blockers, majors and
minors (each finding is {rule, line, message}).
"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers as h  # noqa: E402
from helpers import GOOD_DOC, bullets, code_block, good_doc, png_bytes, replace_once, table  # noqa: E402

PARAGRAPH = ("This paragraph is intentionally long enough to be repeated verbatim so that the duplicate "
             "rule fires on it.")
WINDOWS_HOME = "C:" + h.BACKSLASH + "Users" + h.BACKSLASH + "alice" + h.BACKSLASH + "run.txt"
ARCHIVE_ONLY = ("<!-- zone:archive -->\n# Evidence for the cache move\n\n" + bullets(30)
                + "\n\n## Part two\n\nMore raw text.\n")
SLUG_LINE = re.compile(r"^line\s+(\d+)\s+h(\d)\s+#(\S*)\s+<-\s(.*)$")
TABLE_LINK = "| 🟠 | Warm-up is slow | The first hour is slower | [2 Risks and warm-up](#2-risks-and-warm-up) |"
NEXT_LINK = "**Next →** [2 Risks and warm-up](#2-risks-and-warm-up)\n"
TITLE_AND_DATE = "# Cache move\n\n*2026-10-19 · fixture · final · for the team*\n\n"


def line_of(text, fragment):
    """The 1-based number of the first line of `text` that contains `fragment`."""
    for number, line in enumerate(text.splitlines(), 1):
        if fragment in line:
            return number
    raise AssertionError("no line contains %r" % fragment)


class GoodDocumentTests(h.CheckCase):
    def test_good_document_has_no_findings(self):
        for label, text, newline in (("LF", GOOD_DOC, "\n"), ("CRLF and a BOM", "\ufeff" + GOOD_DOC, "\r\n")):
            with self.subTest(file=label):
                result = self.check(text, newline=newline)
                self.assertEqual(result.findings, [], result.describe())
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stats["zones"], ["human", "archive"])
                self.assertFalse(result.stats["machine_only"])

    def test_the_shipped_skeleton_is_flagged_for_its_placeholders(self):
        code, out, _ = h.run("check_doc.py", h.SKELETON, "--json")
        result = h.CheckResult(code, out, "")
        self.assertHas(result, "B4", "BLOCKER")
        self.assertEqual(result.returncode, 1)


class ZoneTests(h.CheckCase):
    def test_large_document_without_zone_markers_is_an_a1_major(self):
        large = replace_once(good_doc(filler=90), "<!-- zone:human -->\n", "")
        large = replace_once(large, "<!-- zone:archive -->\n", "")
        result = self.check(large)
        self.assertHas(result, "A1", "MAJOR")
        self.assertEqual(result.stats["zones"], [])
        # a short document is not expected to carry zones
        small = replace_once(replace_once(GOOD_DOC, "<!-- zone:human -->\n", ""), "<!-- zone:archive -->\n", "")
        self.assertLacks(self.check(small), "A1")

    def test_zone_markers_without_a_human_zone_are_an_a1_major(self):
        doc = replace_once(GOOD_DOC, "zone:human", "zone:notes")
        doc = replace_once(doc, "zone:archive", "zone:notes")
        self.assertHas(self.check(doc), "A1", "MAJOR")

    def test_machine_zone_before_the_human_zone_is_an_a1_major(self):
        self.assertHas(self.check("<!-- zone:archive -->\n" + GOOD_DOC), "A1", "MAJOR")

    def test_long_document_without_a_machine_zone_is_an_a1_minor(self):
        doc = replace_once(good_doc(filler=160), "<!-- zone:archive -->\n", "")
        result = self.check(doc)
        self.assertHas(result, "A1", "MINOR")
        self.assertLacks(result, "A1", "MAJOR")

    def test_machine_only_mode_by_marker_or_by_flag_skips_panel_rules(self):
        for zone in ("archive", "ai-input", "machine"):
            with self.subTest(zone=zone):
                result = self.check(ARCHIVE_ONLY.replace("zone:archive", "zone:" + zone))
                self.assertEqual(result.findings, [], result.describe())
                self.assertTrue(result.stats["machine_only"])
                self.assertEqual(result.stats["zones"], [zone])
                self.assertEqual(result.stats["panel_words"], 0)
        plain = ARCHIVE_ONLY.replace("<!-- zone:archive -->\n", "")
        without_flag = self.check(plain)
        for rule, tier in (("B1", "MAJOR"), ("C1", "MAJOR"), ("E3", "MINOR")):
            self.assertHas(without_flag, rule, tier)
        flagged = self.check(plain, "--machine-only")
        self.assertEqual(flagged.findings, [], flagged.describe())
        self.assertTrue(flagged.stats["machine_only"])


class LinkTests(h.CheckCase):
    def test_broken_in_document_anchor_is_a_b4_blocker_and_exits_one(self):
        doc = replace_once(GOOD_DOC, "(#a-evidence)", "(#a-evidnce)")
        result = self.check(doc)
        self.assertEqual([f[:2] for f in result.findings], [("BLOCKER", "B4")], result.describe())
        self.assertEqual(result.findings[0][2], line_of(doc, "#a-evidnce"))
        self.assertEqual(result.returncode, 1)

    def test_link_to_a_missing_sibling_file_is_a_b4_major(self):
        # rubric B4 lists every unresolved link as a Blocker; the script rates a missing file a Major
        # (images and anchors are Blockers), which is what is pinned here
        doc = good_doc(panel="See [the full log](doc.log.md).")
        result = self.check(doc)
        self.assertHas(result, "B4", "MAJOR")
        self.assertLacks(result, "B4", "BLOCKER")
        self.assertEqual(result.returncode, 0)
        fixed = self.check(doc, files={"doc.log.md": "# Log\n"})
        self.assertEqual(fixed.findings, [], fixed.describe())

    def test_cross_file_anchors_are_checked_against_the_sibling_headings(self):
        files = {"notes.md": "# Notes\n\n## Real heading\n\ntext\n"}
        good = self.check(good_doc(panel="See [the notes](notes.md#real-heading)."), files=files)
        self.assertEqual(good.findings, [], good.describe())
        bad = self.check(good_doc(panel="See [the notes](notes.md#real-headng)."), files=files)
        self.assertHas(bad, "B4", "BLOCKER")
        self.assertEqual(bad.returncode, 1)

    def test_missing_image_is_a_b4_blocker(self):
        doc = good_doc(body="![Overview of the move](doc.assets/overview.png)\n\n*How to read it.*")
        result = self.check(doc)
        self.assertHas(result, "B4", "BLOCKER")
        self.assertEqual(result.returncode, 1)
        files = {"doc.assets/overview.png": png_bytes(1200), "doc.assets/overview.dot": "digraph {}"}
        fixed = self.check(doc, files=files)
        self.assertEqual(fixed.findings, [], fixed.describe())

    def test_machine_local_and_malformed_paths_are_flagged(self):
        encoded = {"my pic.png": png_bytes(1200), "my pic.dot": "digraph {}"}
        cases = (
            ("image with a drive letter", "![Overview](C:/work/pic.png)", None, "B4", "BLOCKER"),
            ("image with a file URL", "![Overview](file:///work/pic.png)", None, "B4", "BLOCKER"),
            ("link with backslashes", "[the log](logs" + h.BACKSLASH + "run.txt)", None, "B4", "MAJOR"),
            ("image with a raw space", "![Overview](my pic.png)", None, "B4", "MAJOR"),
            ("image with an encoded space", "![Overview](my%20pic.png)", encoded, "F5", "MINOR"),
        )
        for label, markdown, files, rule, tier in cases:
            with self.subTest(case=label):
                self.assertHas(self.check(good_doc(body=markdown), files=files), rule, tier)

    def test_links_in_code_are_ignored_and_html_anchor_ids_are_valid_targets(self):
        in_code = "Inline `[x](#no-such-anchor)` and a block:\n\n```md\n[y](missing.md)\n![z](missing.png)\n```"
        result = self.check(good_doc(body=in_code))
        self.assertEqual(result.findings, [], result.describe())
        with_id = good_doc(body='<a id="notes-anchor"></a>\n\nSee [the anchor](#notes-anchor).')
        result = self.check(with_id)
        self.assertEqual(result.findings, [], result.describe())


class PlaceholderTests(h.CheckCase):
    def test_template_placeholders_and_skeleton_hints_are_b4_blockers(self):
        leftovers = ("{date}", "{Who}", "{doc-stem}", "{Section title}", "{...}",
                     "<!-- No judgment to give (explainer, reference)? Replace the blocks. -->",
                     "<!-- If this material is long, keep it in a sibling file. -->",
                     "<!-- Block A only if a later agent will continue the work. -->")
        for leftover in leftovers:
            with self.subTest(leftover=leftover[:24]):
                result = self.check(good_doc(body="Updated %s by the team." % leftover))
                self.assertHas(result, "B4", "BLOCKER")
                self.assertEqual(result.returncode, 1)


class StructureTests(h.CheckCase):
    def test_unbalanced_details_is_a_b4_blocker_and_inline_code_tags_are_text(self):
        cases = {
            "extra opening tag": replace_once(GOOD_DOC, "<details>\n", "<details>\n<details>\n"),
            "missing closing tag": replace_once(GOOD_DOC, "</details>\n", ""),
            "extra closing tag": GOOD_DOC + "\n</details>\n",
        }
        for label, doc in cases.items():
            with self.subTest(case=label):
                result = self.check(doc)
                self.assertHas(result, "B4", "BLOCKER")
                self.assertEqual(result.returncode, 1)
        quoted = good_doc(body="Wrap raw output in `<details>` when it is long.")
        self.assertEqual(self.check(quoted).findings, [])

    def test_unclosed_code_fence_is_a_b4_blocker_at_the_opening_fence(self):
        doc = good_doc(body="```text\nnever closed")
        result = self.check(doc)
        blocker_lines = [f[2] for f in result.matching("B4", "BLOCKER")]
        self.assertIn(line_of(doc, "```text"), blocker_lines, result.describe())
        self.assertEqual(result.returncode, 1)

    def test_missing_blank_line_after_summary_or_details_is_an_f5_major(self):
        no_gap = replace_once(GOOD_DOC, "</summary>\n\n", "</summary>\n")
        self.assertHas(self.check(no_gap), "F5", "MAJOR")
        self.assertHas(self.check(GOOD_DOC + "Text glued to the closing tag.\n"), "F5", "MAJOR")

    def test_hygiene_problems_are_f5_minors(self):
        loud = "\n\n".join("> ### Loud heading %d\n> text" % i for i in (1, 2))
        cases = {
            "alert": "> [!NOTE]\n> A note.",
            "html colour": '<font color="red">warning</font>',
            "too many loud blockquote headings": loud,
            "repeated paragraph": PARAGRAPH + "\n\n" + PARAGRAPH,
        }
        for label, markdown in cases.items():
            with self.subTest(case=label):
                result = self.check(good_doc(body=markdown))
                self.assertHas(result, "F5", "MINOR")
                self.assertGate(result, blockers=0, majors=0)

    def test_machine_local_paths_are_an_a5_major(self):
        paths = {"windows home": WINDOWS_HOME, "linux home": "/home/alice/run.txt",
                 "macOS home": "/Users/alice/run.txt"}
        for label, path in paths.items():
            with self.subTest(path=label):
                self.assertHas(self.check(good_doc(body="The log is in %s here." % path)), "A5", "MAJOR")
        in_fence = self.check(good_doc(archive="```text\n%s\n```" % paths["linux home"]))
        self.assertHas(in_fence, "A5", "MAJOR")
        many = "\n\n".join("Copy of /home/alice%d/run.txt kept." % i for i in range(6))
        found = self.check(good_doc(body=many)).matching("A5", "MAJOR")
        self.assertTrue(0 < len(found) < 6, "paths beyond the first few are summarised in one finding")


class RawMaterialAndDiagramTests(h.CheckCase):
    MERMAID = "```mermaid\ngraph TD\n  A --> B\n```"

    def test_inline_mermaid_in_the_human_zone_is_a_d3_major_unless_allowed(self):
        doc = good_doc(body=self.MERMAID)
        self.assertHas(self.check(doc), "D3", "MAJOR")
        allowed = self.check(doc, "--allow-mermaid")
        self.assertEqual(allowed.findings, [], allowed.describe())
        self.assertLacks(self.check(good_doc(archive=self.MERMAID)), "D3")
        quirks = self.check(good_doc(archive="```mermaid\nflowchart LR\n  A ----> B\n```"))
        self.assertEqual(len(quirks.matching("D3", "MINOR")), 2, quirks.describe())
        self.assertGate(quirks, blockers=0, majors=0)

    def test_table_over_the_row_limit_is_an_a2_major(self):
        self.assertLacks(self.check(good_doc(body=table(15))), "A2")
        long_table = good_doc(body=table(16))
        self.assertHas(self.check(long_table), "A2", "MAJOR")
        self.assertLacks(self.check(long_table, "--max-table", "20"), "A2")
        self.assertLacks(self.check(good_doc(archive=table(40))), "A2")

    def test_requested_table_marker_exempts_a_long_table(self):
        marker = "<!-- requested-table -->"
        self.assertHas(self.check(good_doc(body=table(20))), "A2", "MAJOR")
        for label, gap in (("directly above", "\n"), ("one blank line above", "\n\n")):
            with self.subTest(marker=label):
                result = self.check(good_doc(body=marker + gap + table(20)))
                self.assertLacks(result, "A2")
                self.assertEqual(result.findings, [], result.describe())

    def test_code_block_over_the_line_limit_is_an_a2_major(self):
        self.assertLacks(self.check(good_doc(body=code_block(25))), "A2")
        long_block = good_doc(body=code_block(26))
        self.assertHas(self.check(long_block), "A2", "MAJOR")
        self.assertLacks(self.check(long_block, "--max-block", "40"), "A2")
        self.assertLacks(self.check(good_doc(archive=code_block(60))), "A2")
        # diagram sources are exempt from the limit, and a short shell block is only a minor
        self.assertLacks(self.check(good_doc(body=code_block(40, "dot"))), "A2")
        self.assertHas(self.check(good_doc(body="```powershell\nGet-Date\n```")), "A2", "MINOR")
        self.assertLacks(self.check(good_doc(archive="```powershell\nGet-Date\n```")), "A2")

    def test_diagram_with_more_than_25_edges_is_a_d4_major(self):
        def dot(edges):
            return "```dot\ndigraph {\n%s\n}\n```" % "\n".join("a%d -> b%d;" % (i, i) for i in range(edges))
        self.assertLacks(self.check(good_doc(archive=dot(25))), "D4")
        self.assertHas(self.check(good_doc(archive=dot(26))), "D4", "MAJOR")


class BudgetTests(h.CheckCase):
    def test_word_budgets_c2_and_f2_and_their_flags(self):
        base = self.check(GOOD_DOC).stats["panel_words"]
        doc = good_doc(panel=" ".join("word%d" % i for i in range(320)))
        result = self.check(doc)
        self.assertHas(result, "C2", "MAJOR")
        self.assertGreater(result.stats["panel_words"], base + 300)
        self.assertLacks(self.check(doc, "--panel-words", "500"), "C2")
        self.assertLacks(self.check(good_doc(panel=" ".join("word%d" % i for i in range(150)))), "C2")
        self.assertLacks(self.check(GOOD_DOC), "F2")
        advice = self.check(GOOD_DOC, "--human-words", "100")
        self.assertHas(advice, "F2", "MINOR")
        self.assertGreater(advice.stats["human_zone_words"], 100)

    def test_cjk_text_is_counted_per_character_not_as_one_word(self):
        base = self.check(GOOD_DOC).stats["panel_words"]
        samples = (("chinese", "缓存迁移计划" * 100), ("japanese", "キャッシュ移行の計画です" * 50),
                   ("korean", "캐시이전계획입니다" * 60))
        for label, paragraph in samples:
            with self.subTest(script=label):
                added = self.check(good_doc(panel=paragraph)).stats["panel_words"] - base
                self.assertGreaterEqual(added, len(paragraph) / 3.0)
                self.assertLessEqual(added, len(paragraph))
        self.assertHas(self.check(good_doc(panel="缓存迁移计划" * 120)), "C2", "MAJOR")


class NavigationTests(h.CheckCase):
    def test_reading_path_needs_three_links_near_the_title_b1(self):
        unlinked_row = TABLE_LINK.replace("[2 Risks and warm-up](#2-risks-and-warm-up)", "2 Risks and warm-up")
        three = replace_once(replace_once(GOOD_DOC, TABLE_LINK, unlinked_row), NEXT_LINK, "")
        self.assertLacks(self.check(three), "B1")
        two = replace_once(three, "- [A Evidence](#a-evidence) - raw numbers · archive only\n", "")
        self.assertHas(self.check(two), "B1", "MAJOR")

    def test_large_document_needs_five_in_document_links_b5(self):
        large = good_doc(filler=160)
        self.assertLacks(self.check(large), "B5")
        result = self.check(replace_once(large, NEXT_LINK, ""))
        self.assertHas(result, "B5", "MAJOR")
        self.assertLacks(result, "B1")

    def test_missing_glance_panel_or_late_panel_is_a_c1_major(self):
        paragraphs = "\n\n".join("Plain paragraph number %d with no panel element." % i for i in range(8))
        self.assertHas(self.check(TITLE_AND_DATE + paragraphs + "\n"), "C1", "MAJOR")
        late = (TITLE_AND_DATE
                + "\n\n".join("Background sentence number %d before the verdict." % i for i in range(20))
                + "\n\n> **Bottom line:** the move is safe.\n")
        self.assertHas(self.check(late), "C1", "MAJOR")
        early = TITLE_AND_DATE + "> **Bottom line:** the move is safe.\n\n" + paragraphs + "\n"
        self.assertLacks(self.check(early), "C1")

    def test_missing_date_near_the_title_is_an_e3_minor(self):
        result = self.check(replace_once(GOOD_DOC, "2026-10-19", "today"))
        self.assertHas(result, "E3", "MINOR")
        self.assertGate(result, blockers=0, majors=0)


class ImageAndHeadingTests(h.CheckCase):
    IMAGE = "![Overview of the move](pic.png)\n\n*How to read it.*"

    def check_png(self, width, with_source=True):
        files = {"pic.png": png_bytes(width)}
        if with_source:
            files["pic.dot"] = "digraph {}"
        return self.check(good_doc(body=self.IMAGE), files=files)

    def test_png_width_outside_500_to_2600_px_is_a_d4_finding(self):
        self.assertEqual(self.check_png(1200).findings, [])
        self.assertHas(self.check_png(3000), "D4", "MAJOR")
        self.assertHas(self.check_png(300), "D4", "MINOR")

    def test_png_without_source_is_d6_and_empty_alt_text_is_d5(self):
        self.assertHas(self.check_png(1200, with_source=False), "D6", "MINOR")
        for extension in (".dot", ".mmd", ".py", ".svg"):
            with self.subTest(source=extension):
                files = {"pic.png": png_bytes(1200), "pic" + extension: "source"}
                self.assertEqual(self.check(good_doc(body=self.IMAGE), files=files).findings, [])
        empty_alt = good_doc(body=self.IMAGE.replace("![Overview of the move]", "![]"))
        files = {"pic.png": png_bytes(1200), "pic.dot": "digraph {}"}
        self.assertHas(self.check(empty_alt, files=files), "D5", "MINOR")

    def test_link_target_headings_with_punctuation_or_duplicates_are_b6_minors(self):
        punctuated = replace_once(GOOD_DOC, "## 1 What changes\n", "## 1 What changes (v2.0)\n")
        punctuated = punctuated.replace("(#1-what-changes)", "(#1-what-changes-v20)")
        self.assertHas(self.check(punctuated), "B6", "MINOR")
        second = "## 1 What changes\n\nA second section.\n\n## 2 Risks and warm-up\n\nThe cache"
        twice = replace_once(GOOD_DOC, "## 2 Risks and warm-up\n\nThe cache", second)
        self.assertLacks(self.check(twice), "B6")
        see_also = "*Only deciding? See also [the repeat](#1-what-changes-1).*"
        linked = replace_once(twice, "*Only deciding? You can stop here.*", see_also)
        self.assertHas(self.check(linked), "B6", "MINOR")


class SlugTests(h.CheckCase):
    def slugs(self, text):
        path = h.write(self.tmp, "slugs.md", text)
        code, out, err = h.run("check_doc.py", path, "--slugs")
        self.assertEqual(code, 0, err)
        found = []
        for line in out.splitlines():
            match = SLUG_LINE.match(line)
            self.assertIsNotNone(match, "unparsable --slugs line: %r" % line)
            found.append((int(match.group(2)), match.group(3)))
        return found

    def test_slugs_follow_github_rules_and_exit_zero_even_for_a_broken_document(self):
        text = "\n".join([
            '# Title: A "quoted" thing?', "## Q&A (v1.2)", "## Notes", "## Notes", "## Notes",
            "## Snake_case and café", "## 缓存迁移", "## 👤 Start here", "### **Bold** and `code`",
            "", "```bash", "# a shell comment, not a heading", "```", "", "See [broken](#nowhere).", ""])
        self.assertEqual(self.slugs(text), [
            (1, "title-a-quoted-thing"), (2, "qa-v12"), (2, "notes"), (2, "notes-1"), (2, "notes-2"),
            (2, "snake_case-and-café"), (2, "缓存迁移"), (2, "-start-here"), (3, "bold-and-code")])


class CommandLineTests(h.CheckCase):
    """These start real child processes: exit status, stdout and stderr as a user or a CI job sees them."""

    def process_result(self, text, *flags):
        return self.check(text, *flags, process=True)

    def test_json_output_has_the_keys_the_script_emits(self):
        doc = replace_once(good_doc(body="The log is in /home/alice/run.txt here."), "2026-10-19", "today")
        result = self.process_result(doc)
        self.assertEqual(result.returncode, 0)  # a major and a minor, but no blocker
        self.assertTrue({"file", "stats", "gate", "blockers", "majors", "minors"} <= set(result.data))
        self.assertTrue({"lines", "headings", "internal_links", "images", "diagram_blocks", "details_blocks",
                         "zones", "machine_only", "panel_words", "human_zone_words"} <= set(result.stats))
        self.assertEqual(sorted(result.gate), ["blockers", "majors", "minors"])
        self.assertTrue(result.data["file"].endswith("doc.md"))
        for key in ("blockers", "majors", "minors"):
            self.assertEqual(result.gate[key], len(result.data[key]))
            for item in result.data[key]:
                self.assertEqual(sorted(item), ["line", "message", "rule"])
                self.assertIsInstance(item["line"], int)
        self.assertTrue(result.has("A5", "MAJOR") and result.has("E3", "MINOR"))

    def test_text_output_lists_findings_worst_first_and_ends_with_a_summary_line(self):
        doc = replace_once(good_doc(body="The log is in /home/alice/run.txt here."), "2026-10-19", "today")
        doc = replace_once(doc, "(#a-evidence)", "(#a-evidnce)")
        path = h.write(self.tmp, "doc.md", doc)
        code, out, err = h.run_script("check_doc.py", path)
        self.assertEqual(err, "")
        lines = out.splitlines()
        self.assertEqual([line.split()[0] for line in lines[:-1]], ["BLOCKER", "MAJOR", "MINOR"])
        counts = re.search(r"(\d+) blocker\(s\), (\d+) major\(s\), (\d+) minor\(s\)", lines[-1])
        self.assertEqual(tuple(int(n) for n in counts.groups()), (1, 1, 1))
        self.assertEqual(code, 1)

    def test_missing_file_and_usage_errors_exit_two(self):
        code, out, _ = h.run_script("check_doc.py", self.tmp / "no-such-file.md")
        self.assertEqual(code, 2)
        self.assertIn("not found", out)
        doc = h.write(self.tmp, "doc.md", GOOD_DOC)
        for label, args in (("no arguments", ()), ("unknown flag", (doc, "--bogus")),
                            ("non-numeric limit", (doc, "--max-block", "many")), ("a folder", (self.tmp,))):
            with self.subTest(case=label):
                self.assertEqual(h.run("check_doc.py", *args)[0], 2)

    def test_slugs_print_utf8_and_empty_or_binary_files_do_not_crash(self):
        heading = h.write(self.tmp, "zh.md", "# 缓存迁移 🚀\n")
        code, out, _ = h.run_script("check_doc.py", heading, "--slugs")
        self.assertEqual(code, 0)
        self.assertIn("#缓存迁移-", out)
        empty = self.check("")
        self.assertHas(empty, "C1", "MAJOR")
        self.assertEqual(empty.returncode, 0)
        path = h.write_bytes(self.tmp, "binary.md", bytes(range(256)) * 8)
        code, out, err = h.run("check_doc.py", path, "--json")
        self.assertEqual(err, "")
        self.assertIn(code, (0, 1))
        h.parse_json_output(out)


if __name__ == "__main__":
    unittest.main()
