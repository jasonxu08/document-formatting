#!/usr/bin/env python3
"""Rewrite a large existing document without losing anything: slice it verbatim, then verify.

  slice   copy line ranges of the source, unchanged, into a sibling Markdown file
  verify  check that every non-blank line of the source is reachable in the rewritten set
          and that every H2 section of the source is named outside the verbatim copies (the section map)

Every copied range is wrapped in markers, so it can be checked later:

    <!-- src:12-58 shift:+1 -->
    ...source lines 12-58; headings outside code fences are demoted by 1 level...
    <!-- /src -->

Headings are demoted so the sibling file keeps a usable outline (a verbatim copy of several "## Notes"
sections would otherwise collide with its own block headings). `verify` promotes them back before
comparing, so the copy is still proven identical.

Usage:
  python source_set.py slice SOURCE OUT.md --title "Supporting evidence" --intro "What this file is and what it supports." \\
        --block "12-58:Benchmark tables" --block "59-96:Raw logs:+2" [--zone archive|ai-input]
  python source_set.py verify MAIN.md --source SOURCE [--sha256 HEX] [--verbose]

The document set is MAIN.md plus the siblings named <MAIN stem>.*.md in the same folder.
Only the standard library is used. Exit code 1 means something is missing or different.
"""
import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path

sys.dont_write_bytecode = True
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*([\w+#.-]*)")
ATX = re.compile(r"^(\s{0,3})(#{1,6})(\s.*|)$")
SRC_OPEN = re.compile(r"^<!-- src:(\d+)-(\d+) shift:\+(\d) -->$")
SRC_CLOSE = "<!-- /src -->"
BLOCK = re.compile(r"^(\d+)-(\d+):(.*?)(?::\+(\d))?$")


def read_lines(path):
    text = path.read_bytes().decode("utf-8-sig", errors="replace")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [l.rstrip("\r") for l in lines]


def shift_headings(chunk, levels):
    """Demote (levels > 0) or promote (levels < 0) ATX headings outside code fences."""
    out, in_fence, fchar, flen = [], False, "", 0
    for line in chunk:
        m = FENCE.match(line)
        if in_fence:
            out.append(line)
            if m and m.group(1)[0] == fchar and len(m.group(1)) >= flen and not m.group(2).strip():
                in_fence = False
            continue
        if m:
            in_fence, fchar, flen = True, m.group(1)[0], len(m.group(1))
            out.append(line)
            continue
        h = ATX.match(line)
        if h:
            level = len(h.group(2)) + levels
            if not 1 <= level <= 6:
                raise ValueError("heading %r would leave levels 1-6" % line[:60])
            out.append(h.group(1) + "#" * level + h.group(3))
        else:
            out.append(line)
    return out


def min_heading_level(chunk):
    levels, in_fence, fchar, flen = [], False, "", 0
    for line in chunk:
        m = FENCE.match(line)
        if in_fence:
            if m and m.group(1)[0] == fchar and len(m.group(1)) >= flen and not m.group(2).strip():
                in_fence = False
            continue
        if m:
            in_fence, fchar, flen = True, m.group(1)[0], len(m.group(1))
            continue
        h = ATX.match(line)
        if h:
            levels.append(len(h.group(2)))
    return min(levels) if levels else 6


def slug(text):
    t = re.sub(r"<[^>]+>", "", text).lower()
    return "".join(ch for ch in t if unicodedata.category(ch)[0] in "LNM" or ch in "-_ ").replace(" ", "-")


def norm(line):
    """A line without heading markers or extra spaces, for finding it again after a rewrite."""
    return re.sub(r"\s+", " ", re.sub(r"^\s*#{1,6}\s+", "", line)).strip()


def significant(line):
    return len(re.findall(r"\w", line)) >= 3


def cmd_slice(a):
    src = Path(a.source)
    lines = read_lines(src)
    sha = hashlib.sha256(src.read_bytes()).hexdigest().upper()
    blocks = []
    for spec in a.block:
        m = BLOCK.match(spec)
        if not m:
            sys.exit("bad --block %r (expected FIRST-LAST:Title or FIRST-LAST:Title:+N)" % spec)
        first, last, title = int(m.group(1)), int(m.group(2)), m.group(3).strip()
        if not 1 <= first <= last <= len(lines):
            sys.exit("--block %r is outside the source (%d lines)" % (spec, len(lines)))
        if re.search(r"[^\w\s-]", title):
            print("warning: block title %r has punctuation; block headings are link targets, keep them plain" % title)
        shift = int(m.group(4)) if m.group(4) else (2 if min_heading_level(lines[first - 1:last]) == 1 else 1)
        blocks.append((first, last, title, shift))
    if len(blocks) > 26:
        sys.exit("at most 26 blocks per file (A-Z); split the file")
    glyph, label = ("🗄️", "Archive") if a.zone == "archive" else ("🤖", "AI input")
    total = sum(l - f + 1 for f, l, _, _ in blocks)
    out = ["<!-- zone:%s -->" % a.zone, "# %s" % a.title, "",
           "*%s %s - %s*" % (glyph, label, a.intro.strip()), "",
           "Verbatim copy of %d lines of `%s` (SHA-256 `%s`). Each block is wrapped in `<!-- src:FIRST-LAST shift:+N -->` "
           "markers; headings outside code blocks are demoted by N levels so this file keeps a usable outline. "
           "`source_set.py verify` proves every block identical to its source lines." % (total, src.name, sha), "",
           "**Contents**", ""]
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, (first, last, title, _) in enumerate(blocks):
        out.append("- [%s %s](#%s) - source lines %d-%d" % (letters[i], title, slug("%s %s" % (letters[i], title)), first, last))
    out.append("")
    for i, (first, last, title, shift) in enumerate(blocks):
        chunk = lines[first - 1:last]
        try:
            moved = shift_headings(chunk, shift)
        except ValueError as exc:
            sys.exit("block %d-%d: %s; use a smaller shift (:+N)" % (first, last, exc))
        out += ["## %s %s" % (letters[i], title), "",
                "*%s %s - verbatim copy of source lines %d-%d (%d lines).*" % (glyph, label, first, last, last - first + 1), "",
                "<!-- src:%d-%d shift:+%d -->" % (first, last, shift)] + moved + ["", SRC_CLOSE, ""]
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:  # Path.write_text(newline=) needs Python 3.10
        fh.write("\n".join(out))
    print("wrote %s: %d blocks, %d source lines" % (a.out, len(blocks), total))


def cmd_verify(a):
    main, src = Path(a.main), Path(a.source)
    source = read_lines(src)
    sha = hashlib.sha256(src.read_bytes()).hexdigest().upper()
    print("source %s: %d lines, SHA-256 %s" % (src.name, len(source), sha))
    ok = True
    if a.sha256:
        match = a.sha256.strip().upper() == sha
        print("recorded SHA-256 %s" % ("matches" if match else "DOES NOT MATCH: the source changed"))
        ok = ok and match
    files = [main] + sorted(p for p in main.parent.glob(main.stem + ".*.md") if p != main)
    covered = [0] * (len(source) + 2)
    outside, every = [], set()
    for f in files:
        lines = read_lines(f)
        every.update(norm(l) for l in lines if significant(l))
        i, blocks, copied = 0, 0, 0
        while i < len(lines):
            m = SRC_OPEN.match(lines[i])
            if not m:
                outside.append(lines[i])
                i += 1
                continue
            first, last, levels = int(m.group(1)), int(m.group(2)), int(m.group(3))
            j = i + 1
            while j < len(lines) and lines[j] != SRC_CLOSE:
                j += 1
            if j >= len(lines):
                print("PROBLEM %s line %d: src block is never closed" % (f.name, i + 1))
                ok = False
                break
            region = lines[i + 1:j]
            if region and region[-1] == "":
                region = region[:-1]
            try:
                restored = shift_headings(region, -levels)
            except ValueError:
                restored = None
            expected = source[first - 1:last]
            if restored == expected:
                for n in range(first, last + 1):
                    covered[n] += 1
                blocks += 1
                copied += last - first + 1
                if a.verbose:
                    print("  %-44s source %4d-%4d identical" % (f.name, first, last))
            else:
                bad = next((k for k in range(min(len(expected), len(restored or []))) if restored[k] != expected[k]),
                           min(len(expected), len(restored or [])))
                print("PROBLEM %s line %d: block src:%d-%d is DIFFERENT from the source (first difference at source line %d)"
                      % (f.name, i + 1, first, last, first + bad))
                ok = False
            i = j + 1
        if blocks:
            print("%s: %d verbatim block(s), %d source lines" % (f.name, blocks, copied))
    missing = [n for n in range(1, len(source) + 1)
               if source[n - 1].strip() and significant(source[n - 1]) and not covered[n]
               and norm(source[n - 1]) not in every]
    twice = [n for n in range(1, len(source) + 1) if covered[n] > 1 and significant(source[n - 1])]
    print("source lines not reachable anywhere in the set: %d%s" % (len(missing), (" (first: %s)" % missing[:8]) if missing else ""))
    if twice:
        print("note: %d source lines are copied more than once (first: %s)" % (len(twice), twice[:8]))
    ok = ok and not missing
    # Section map: every H2 of the source must be named outside the verbatim copies
    blob = "\n".join(norm(l).lower() for l in outside)
    h2s, in_fence, fchar, flen = [], False, "", 0
    for n, line in enumerate(source, 1):
        m = FENCE.match(line)
        if in_fence:
            if m and m.group(1)[0] == fchar and len(m.group(1)) >= flen and not m.group(2).strip():
                in_fence = False
            continue
        if m:
            in_fence, fchar, flen = True, m.group(1)[0], len(m.group(1))
            continue
        h = re.match(r"^\s{0,3}##\s+(.*?)\s*#*\s*$", line)
        if h:
            h2s.append((n, h.group(1)))
    unmapped = [(n, t) for n, t in h2s if norm(t).lower() not in blob]
    print("source H2 sections: %d; not named outside the verbatim copies (no map entry): %d" % (len(h2s), len(unmapped)))
    for n, t in unmapped[:10]:
        print("  line %d: %s" % (n, t[:100]))
    ok = ok and not unmapped
    print("ALL OK: every source line is reachable and every H2 section is in the map." if ok else "PROBLEM: see above.")
    return 0 if ok else 1


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("slice", help="copy source line ranges verbatim into a sibling file")
    s.add_argument("source")
    s.add_argument("out")
    s.add_argument("--title", required=True)
    s.add_argument("--intro", required=True, help="one line: what this file is and which claims it supports")
    s.add_argument("--zone", choices=("archive", "ai-input"), default="archive")
    s.add_argument("--block", action="append", required=True, metavar="FIRST-LAST:Title[:+N]")
    v = sub.add_parser("verify", help="prove nothing was lost")
    v.add_argument("main")
    v.add_argument("--source", required=True)
    v.add_argument("--sha256", help="the checksum recorded in the document, to prove the source is unchanged")
    v.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    return cmd_slice(a) if a.cmd == "slice" else cmd_verify(a)


if __name__ == "__main__":
    sys.exit(main())
