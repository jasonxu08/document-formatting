"""Tests for skills/document-formatting/scripts/source_set.py (slice and verify).

slice copies line ranges of a source file, verbatim, into a sibling Markdown file, each range wrapped in
`<!-- src:FIRST-LAST shift:+N -->` ... `<!-- /src -->` markers with the headings outside code fences
demoted by N levels. verify proves every block still equals its source lines and that nothing was lost.
Exit status seen: slice 0 (1 for a bad or out-of-range --block, a heading shift past level 6, more than 26
blocks; 2 for a missing option), verify 0 when ALL OK and 1 for any problem.

Most tests call main() in this process (helpers.run); CommandLineTests start real child processes.
"""
import collections
import hashlib
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers as h  # noqa: E402

SOURCE_LINES = [
    "# Cache notes",                       # 1
    "",                                    # 2
    "Intro line for the notes.",           # 3
    "",                                    # 4
    "## Alpha tables",                     # 5
    "",                                    # 6
    "The nightly job finished in 48 minutes.",  # 7
    "Second line of alpha.",               # 8
    "",                                    # 9
    "```bash",                             # 10
    "# not a heading, a shell comment",    # 11
    "## also not a heading",               # 12
    "echo done",                           # 13
    "```",                                 # 14
    "",                                    # 15
    "## Beta logs",                        # 16
    "",                                    # 17
    "### Beta detail",                     # 18
    "",                                    # 19
    "Archive the logs on Monday.",         # 20
]
SOURCE = "\n".join(SOURCE_LINES) + "\n"
BLOCKS = ("1-4:Intro", "5-15:Alpha tables", "16-20:Beta logs")
SECTION_MAP = "# Report\n\n## Section map\n\n- Alpha tables: verbatim in the evidence file\n- Beta logs: same\n"
OPEN_MARKER = re.compile(r"^<!-- src:(\d+)-(\d+) shift:\+(\d) -->$")
CLOSE_MARKER = "<!-- /src -->"
SHA_IN_HEADER = re.compile(r"SHA-256 `([0-9A-F]{64})`")
Block = collections.namedtuple("Block", "first last shift lines")


def parse_blocks(text):
    """The verbatim blocks of a sliced file as Block(first, last, shift, lines between the markers)."""
    lines = text.split("\n")
    blocks, index = [], 0
    while index < len(lines):
        match = OPEN_MARKER.match(lines[index])
        if match:
            end = lines.index(CLOSE_MARKER, index + 1)
            region = lines[index + 1:end]
            if region and region[-1] == "":  # the spacer line slice adds before the closing marker
                region = region[:-1]
            blocks.append(Block(int(match.group(1)), int(match.group(2)), int(match.group(3)), region))
            index = end
        index += 1
    return blocks


def demoted(lines, levels):
    """Reference implementation: ATX headings outside ``` and ~~~ fences pushed down `levels` levels."""
    out, fence = [], None
    for line in lines:
        marker = line.strip()[:3]
        if marker in ("```", "~~~"):
            fence = None if fence == marker else (fence or marker)
        elif fence is None and re.match(r"^#{1,6}(\s|$)", line):
            line = "#" * levels + line
        out.append(line)
    return out


class SourceSetCase(h.TempDirCase):
    def setUp(self):
        super().setUp()
        self.source = h.write(self.tmp, "source.md", SOURCE)

    def slice(self, *blocks, out="doc.evidence.md", source=None, extra=(), process=False):
        args = ["slice", source or self.source, self.tmp / out, "--title", "Supporting evidence",
                "--intro", "What this file is."]
        for block in blocks:
            args += ["--block", block]
        runner = h.run_script if process else h.run
        return runner("source_set.py", *(args + list(extra)))

    def verify(self, main="doc.md", *extra, source=None, process=False):
        runner = h.run_script if process else h.run
        return runner("source_set.py", "verify", self.tmp / main, "--source", source or self.source, *extra)

    def assemble(self, blocks=BLOCKS, main_text=SECTION_MAP):
        """A main document plus its verbatim evidence sibling; returns the evidence text."""
        code, out, err = self.slice(*blocks)
        self.assertEqual(code, 0, err or out)
        h.write(self.tmp, "doc.md", main_text)
        return h.read(self.tmp / "doc.evidence.md")


class SliceTests(SourceSetCase):
    def test_slice_copies_exact_lines_in_markers_and_demotes_headings(self):
        code, out, err = self.slice(*BLOCKS)
        self.assertEqual(code, 0, err)
        text = h.read(self.tmp / "doc.evidence.md")
        blocks = parse_blocks(text)
        self.assertEqual([(b.first, b.last, b.shift) for b in blocks], [(1, 4, 2), (5, 15, 1), (16, 20, 1)])
        for block in blocks:
            expected = demoted(SOURCE_LINES[block.first - 1:block.last], block.shift)
            self.assertEqual(block.lines, expected, "block %d-%d" % (block.first, block.last))
        self.assertIn("### Cache notes", blocks[0].lines)
        self.assertIn("### Alpha tables", blocks[1].lines)
        self.assertIn("#### Beta detail", blocks[2].lines)

    def test_headings_inside_code_fences_are_not_demoted(self):
        source = "## One\n\n~~~text\n# tilde comment\n## tilde h2\n~~~\n\n```bash\n# backtick comment\n```\n\n## Two\n"
        path = h.write(self.tmp, "fences.md", source)
        code, out, err = self.slice("1-12:Fences", source=path, out="fences.evidence.md")
        self.assertEqual(code, 0, err)
        block = parse_blocks(h.read(self.tmp / "fences.evidence.md"))[0]
        for kept in ("# tilde comment", "## tilde h2", "# backtick comment"):
            self.assertIn(kept, block.lines)
        self.assertIn("### One", block.lines)
        self.assertIn("### Two", block.lines)

    def test_default_shift_follows_the_shallowest_heading_and_can_be_overridden(self):
        cases = (("1-20:All", 2), ("5-20:H2 only", 1), ("3-4:No headings", 1), ("5-20:Explicit:+3", 3))
        for spec, shift in cases:
            with self.subTest(block=spec):
                self.assertEqual(self.slice(spec)[0], 0)
                block = parse_blocks(h.read(self.tmp / "doc.evidence.md"))[0]
                self.assertEqual(block.shift, shift)
                self.assertEqual(block.lines, demoted(SOURCE_LINES[block.first - 1:block.last], shift))

    def test_shift_past_heading_level_six_is_refused_and_nothing_is_written(self):
        code, out, err = self.slice("5-20:Too deep:+5")
        self.assertNotEqual(code, 0)
        self.assertFalse((self.tmp / "doc.evidence.md").exists())

    def test_header_records_the_source_sha256_and_lists_every_block(self):
        self.assertEqual(self.slice(*BLOCKS)[0], 0)
        text = h.read(self.tmp / "doc.evidence.md")
        recorded = SHA_IN_HEADER.search(text).group(1)
        self.assertEqual(recorded, hashlib.sha256(SOURCE.encode("utf-8")).hexdigest().upper())
        for anchor in ("#a-intro", "#b-alpha-tables", "#c-beta-logs"):
            self.assertIn("(%s)" % anchor, text)
        code, out, _ = h.run("check_doc.py", self.tmp / "doc.evidence.md", "--json")
        result = h.CheckResult(code, out, "")
        self.assertEqual(result.gate["blockers"], 0, result.describe())
        self.assertTrue(result.stats["machine_only"])

    def test_zone_option_labels_the_file_as_archive_or_ai_input(self):
        self.assertEqual(self.slice(*BLOCKS)[0], 0)
        self.assertEqual(h.read(self.tmp / "doc.evidence.md").split("\n")[0], "<!-- zone:archive -->")
        self.assertEqual(self.slice(*BLOCKS, extra=("--zone", "ai-input"))[0], 0)
        text = h.read(self.tmp / "doc.evidence.md")
        self.assertEqual(text.split("\n")[0], "<!-- zone:ai-input -->")
        self.assertEqual(h.run("source_set.py", "slice", self.source, self.tmp / "x.md", "--title", "T",
                               "--intro", "I", "--block", "1-4:A", "--zone", "elsewhere")[0], 2)

    def test_invalid_ranges_are_rejected_without_writing_a_file(self):
        bad = ("5-4:Backwards", "0-3:Starts at zero", "1-999:Past the end", "21-21:One past the end",
               "nonsense", "3:No range")
        for spec in bad:
            with self.subTest(block=spec):
                code, out, err = self.slice(spec, out="bad.md")
                self.assertNotEqual(code, 0)
                self.assertFalse((self.tmp / "bad.md").exists())

    def test_range_ends_are_inclusive_and_26_blocks_is_the_limit(self):
        self.assertEqual(self.slice("1-1:First line", out="first.md")[0], 0)
        self.assertEqual(self.slice("20-20:Last line", out="last.md")[0], 0)
        self.assertEqual(parse_blocks(h.read(self.tmp / "last.md"))[0].lines, ["Archive the logs on Monday."])
        many = h.write(self.tmp, "many.md", "\n".join("line number %d here" % i for i in range(1, 31)) + "\n")
        for count, expected_ok in ((26, True), (27, False)):
            with self.subTest(blocks=count):
                specs = ["%d-%d:Block%d" % (i, i, i) for i in range(1, count + 1)]
                code, out, err = self.slice(*specs, source=many, out="many.evidence.md")
                self.assertEqual(code == 0, expected_ok, err)
                self.assertNotIn("Traceback", err, "the limit is reported by a message, not by a crash")

    def test_empty_or_missing_source_cannot_be_sliced(self):
        empty = h.write(self.tmp, "empty.md", "")
        code, out, err = self.slice("1-1:Nothing", source=empty, out="empty.evidence.md")
        self.assertNotEqual(code, 0)
        code, out, err = self.slice("1-4:Missing", source=self.tmp / "no-such.md", out="missing.evidence.md")
        self.assertNotEqual(code, 0)
        self.assertFalse((self.tmp / "missing.evidence.md").exists())

    def test_punctuation_in_a_block_title_only_warns(self):
        code, out, err = self.slice("1-4:Run: with punctuation")
        self.assertEqual(code, 0, err)
        self.assertIn("warning", out.lower())
        self.assertTrue((self.tmp / "doc.evidence.md").exists())

    def test_crlf_bom_and_unicode_sources_are_sliced_without_loss(self):
        crlf = SOURCE.replace("\n", "\r\n").encode("utf-8")
        bom = b"\xef\xbb\xbf" + SOURCE.rstrip("\n").encode("utf-8")
        chinese = "# 缓存迁移\n\n## 第一部分\n\n第一次运行用了 48 分钟。\n\n## 第二部分\n\n周一进行第二次运行。\n"
        cases = (("crlf", crlf, BLOCKS), ("bom and no final newline", bom, BLOCKS),
                 ("chinese", chinese.encode("utf-8"), ("1-2:Intro", "3-6:第一部分", "7-9:第二部分")))
        for label, data, blocks in cases:
            with self.subTest(source=label):
                source = h.write_bytes(self.tmp, "variant.md", data)
                code, out, err = self.slice(*blocks, source=source, out="variant.evidence.md")
                self.assertEqual(code, 0, err)
                raw = (self.tmp / "variant.evidence.md").read_bytes()
                self.assertNotIn(b"\r", raw)
                self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
                recorded = SHA_IN_HEADER.search(raw.decode("utf-8")).group(1)
                self.assertEqual(recorded, hashlib.sha256(data).hexdigest().upper())
                code, out, err = self.verify("variant.evidence.md", source=source)
                self.assertEqual(code, 0, out)


class VerifyTests(SourceSetCase):
    def test_verify_passes_on_an_untouched_assembled_document(self):
        self.assemble()
        code, out, err = self.verify()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.verify("doc.evidence.md")[0], 0)  # the evidence file alone also names every H2
        # a file that does not match <main stem>.*.md is not part of the set
        h.write(self.tmp, "doc-notes.md", "<!-- src:1-4 shift:+1 -->\nnot the source\n<!-- /src -->\n")
        self.assertEqual(self.verify()[0], 0)

    def test_verify_fails_after_changing_one_character_in_a_verbatim_block(self):
        evidence = self.assemble()
        self.assertEqual(self.verify()[0], 0)
        tampered = {
            "one letter of text": evidence.replace("48 minutes", "49 minutes"),
            "one letter inside a fence": evidence.replace("echo done", "echo dona"),
            "a heading level": evidence.replace("### Alpha tables", "## Alpha tables"),
            "a deleted line": evidence.replace("Second line of alpha.\n", ""),
        }
        for label, text in tampered.items():
            with self.subTest(change=label):
                self.assertNotEqual(text, evidence)
                h.write(self.tmp, "doc.evidence.md", text)
                code, out, err = self.verify()
                self.assertEqual(code, 1, out)
        h.write(self.tmp, "doc.evidence.md", evidence)
        self.assertEqual(self.verify()[0], 0)

    def test_verify_fails_when_the_recorded_sha256_does_not_match(self):
        self.assemble()
        real = hashlib.sha256(SOURCE.encode("utf-8")).hexdigest()
        for label, given, expected in (("upper case", real.upper(), 0), ("lower case", real, 0),
                                       ("another checksum", "0" * 64, 1),
                                       ("checksum of other text", hashlib.sha256(b"other").hexdigest(), 1)):
            with self.subTest(sha256=label):
                self.assertEqual(self.verify("doc.md", "--sha256", given)[0], expected)

    def test_verify_flags_a_source_modified_after_slicing(self):
        self.assemble()
        original_sha = hashlib.sha256(SOURCE.encode("utf-8")).hexdigest()
        self.assertEqual(self.verify()[0], 0)
        edits = {
            "a changed line": SOURCE.replace("Monday", "Tuesday"),
            "a line appended": SOURCE + "A late addition to the notes.\n",
            "a line inserted at the top": "A new first line.\n" + SOURCE,
        }
        for label, text in edits.items():
            with self.subTest(edit=label):
                h.write(self.tmp, "source.md", text)
                self.assertEqual(self.verify()[0], 1)
                self.assertEqual(self.verify("doc.md", "--sha256", original_sha)[0], 1)
        h.write(self.tmp, "source.md", SOURCE)
        self.assertEqual(self.verify("doc.md", "--sha256", original_sha)[0], 0)

    def test_verify_fails_when_part_of_the_source_was_never_copied(self):
        blocks = ("1-4:Intro", "5-6:Alpha tables", "9-20:Beta logs")  # lines 7 and 8 are left out
        self.assemble(blocks)
        self.assertEqual(self.verify()[0], 1)
        # a line quoted anywhere in the set counts as reachable
        quoted = SECTION_MAP + "\nThe nightly job finished in 48 minutes.\n\nSecond line of alpha.\n"
        h.write(self.tmp, "doc.md", quoted)
        self.assertEqual(self.verify()[0], 0)

    def test_verify_fails_when_a_source_section_is_missing_from_the_section_map(self):
        self.assemble(("1-20:Everything",), main_text="# Report\n\nNothing about the sections here.\n")
        self.assertEqual(self.verify()[0], 1)
        h.write(self.tmp, "doc.md", SECTION_MAP)
        self.assertEqual(self.verify()[0], 0)

    def test_verify_fails_on_a_block_that_is_never_closed(self):
        evidence = self.assemble()
        self.assertEqual(evidence.count(CLOSE_MARKER), 3)
        head, _, tail = evidence.rpartition(CLOSE_MARKER)
        h.write(self.tmp, "doc.evidence.md", head + tail)
        self.assertEqual(self.verify()[0], 1)

    def test_a_block_copied_twice_still_verifies_and_verbose_lists_the_blocks(self):
        evidence = self.assemble()
        block = evidence[evidence.index("<!-- src:1-4"):evidence.index(CLOSE_MARKER) + len(CLOSE_MARKER)]
        h.write(self.tmp, "doc.evidence.md", evidence + "\n" + block + "\n")
        plain = self.verify()
        verbose = self.verify("doc.md", "--verbose")
        self.assertEqual((plain[0], verbose[0]), (0, 0), plain[1])
        self.assertGreater(len(verbose[1]), len(plain[1]))

    def test_verify_with_a_missing_source_fails(self):
        self.assemble()
        self.assertNotEqual(self.verify("doc.md", source=self.tmp / "no-such.md")[0], 0)


class CommandLineTests(SourceSetCase):
    """These start real child processes: exit status and output as a user or a CI job sees them."""

    def test_slice_and_verify_exit_codes_in_child_processes(self):
        code, out, err = self.slice(*BLOCKS, process=True)
        self.assertEqual(code, 0, err)
        self.assertIn("wrote", out)
        h.write(self.tmp, "doc.md", SECTION_MAP)
        code, out, err = self.verify(process=True)
        self.assertEqual((code, err), (0, ""), out)
        evidence = h.read(self.tmp / "doc.evidence.md")
        h.write(self.tmp, "doc.evidence.md", evidence.replace("48 minutes", "49 minutes"))
        self.assertEqual(self.verify()[0], 1)

    def test_usage_errors_and_help(self):
        self.assertEqual(h.run_script("source_set.py", "slice", self.source, self.tmp / "x.md")[0], 2)
        code, out, _ = h.run("source_set.py", "--help")
        self.assertEqual(code, 0)
        self.assertIn("verify", out)
        self.assertEqual(h.run("source_set.py")[0], 2)
        self.assertEqual(h.run("source_set.py", "frobnicate")[0], 2)

    def test_unicode_content_survives_a_round_trip_through_a_child_process(self):
        chinese = "# 缓存迁移\n\n## 第一部分\n\n第一次运行用了 48 分钟。\n"
        source = h.write(self.tmp, "zh.md", chinese)
        code, out, err = self.slice("1-5:第一部分", source=source, out="zh.evidence.md", process=True)
        self.assertEqual(code, 0, err)
        self.assertIn("第一次运行用了 48 分钟。", h.read(self.tmp / "zh.evidence.md"))
        code, out, err = self.verify("zh.evidence.md", source=source)
        self.assertEqual(code, 0, out + err)


if __name__ == "__main__":
    unittest.main()
