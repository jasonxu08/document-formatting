#!/usr/bin/env python3
"""Check every relative link, image and anchor in the repository's Markdown files.

Usage:
    python tools/check_links.py [PATH ...]     files or folders; default: the whole repository
    python tools/check_links.py --all           also check the review evidence listed below

What is checked: Markdown links and images, reference definitions, and the href, src and srcset of
inline HTML. A link with a #fragment must match a heading slug (GitHub rules) or an explicit id in the
target file. The letter case of every path part must match the disk, because GitHub and Linux are
case-sensitive while Windows and macOS are not. URLs with a scheme (https:, mailto:, ...) are not fetched.

Not checked by default, because these are evidence that must stay as the agents wrote it, or templates:
documents under examples/*/{input,with-skill,without-skill}, review/iteration-1/outputs, every records/
folder, and the placeholders in skills/*/assets/skeleton.md.

Exit code 1 when a link is broken. Standard library only.
"""
import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True  # importing the checker below must not leave a __pycache__ in the skill folder
sys.path.insert(0, str(ROOT / "skills" / "document-formatting" / "scripts"))
import check_doc  # noqa: E402  (the checker's slug and anchor rules are the single source of truth)

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist"}
EVIDENCE = (
    re.compile(r"^examples/[^/]+/(input|with-skill|without-skill)/"),
    re.compile(r"^review/iteration-1/outputs/"),
    re.compile(r"/records/"),
    re.compile(r"^skills/[^/]+/assets/skeleton\.md$"),
)
# Example links that sit inside the skill's own instructions, as sample wording for the agent.
ILLUSTRATIVE = {("skills/document-formatting/SKILL.md", "#2-the-dependency-map")}
MD_LINK = re.compile(r"(!?)(?<!\\)\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
REF_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+.*)?$")
HTML_ATTR = re.compile(r"""\b(?:href|src|srcset)\s*=\s*["']([^"']+)["']""", re.I)
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
INLINE_CODE = re.compile(r"`[^`\n]*`")


def markdown_files(paths, include_evidence):
    seen = []
    for base in paths:
        base = base.resolve()
        found = [base] if base.is_file() else sorted(base.rglob("*.md"))
        for p in found:
            if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
                continue
            rel = p.relative_to(ROOT).as_posix()
            if not include_evidence and any(rx.search(rel) for rx in EVIDENCE):
                continue
            seen.append(p)
    return seen


def targets(path):
    """Yield (line number, raw target) for every link-like reference outside code."""
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    body, _, _ = check_doc.scan(lines)
    for n, line in body:
        text = INLINE_CODE.sub("", line)
        for m in MD_LINK.finditer(text):
            yield n, m.group(2)
        m = REF_DEF.match(text)
        if m:
            yield n, m.group(1)
        for m in HTML_ATTR.finditer(text):
            value = m.group(1).strip()
            if value:
                yield n, value.split(",")[0].split()[0]


_LISTINGS = {}


def wrong_case(base, target):
    """Name the first path part whose letter case differs from the disk, or return None.

    A link that resolves on Windows or macOS can still be broken on GitHub, which is case-sensitive.
    """
    try:
        parts = Path(os.path.normpath(str(base / target))).relative_to(ROOT).parts
    except ValueError:
        return None  # outside the repository: there is nothing to compare with
    folder = ROOT
    for part in parts:
        if folder not in _LISTINGS:
            _LISTINGS[folder] = os.listdir(str(folder)) if folder.is_dir() else []
        if part not in _LISTINGS[folder]:
            same = [name for name in _LISTINGS[folder] if name.lower() == part.lower()]
            return "'%s' is '%s' on disk" % (part, same[0]) if same else None
        folder = folder / part
    return None


def check_file(path, anchor_cache):
    problems = []
    rel = path.relative_to(ROOT).as_posix()
    for n, raw in targets(path):
        if not raw or SCHEME.match(raw) or raw.startswith("//") or raw.startswith("{") or (rel, raw) in ILLUSTRATIVE:
            continue
        target, _, frag = raw.partition("#")
        target = unquote(target.split("?")[0])
        if target:
            base = ROOT if target.startswith("/") else path.parent
            dest = (base / target.lstrip("/")).resolve()
            if not dest.exists():
                problems.append((n, "missing file: %s" % raw))
                continue
            case = wrong_case(base, target.lstrip("/"))
            if case:
                problems.append((n, "wrong letter case in %s: %s (GitHub is case-sensitive)" % (raw, case)))
                continue
        else:
            dest = path
        if frag and dest.is_file() and dest.suffix.lower() == ".md":
            anchors = anchor_cache.setdefault(dest, check_doc.collect_anchors(dest))
            if unquote(frag).lower() not in anchors:
                problems.append((n, "no such anchor: %s" % raw))
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="*", help="files or folders to check (default: the whole repository)")
    ap.add_argument("--all", action="store_true", help="also check the review evidence that is skipped by default")
    args = ap.parse_args(argv)
    paths = [Path(p) for p in args.paths] or [ROOT]
    files = markdown_files(paths, args.all)
    cache, broken = {}, 0
    for f in files:
        for n, msg in check_file(f, cache):
            broken += 1
            print("%s:%d: %s" % (f.relative_to(ROOT).as_posix(), n, msg))
    print("checked %d Markdown files: %s" % (len(files), "%d broken links" % broken if broken else "all links resolve"))
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
