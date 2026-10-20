#!/usr/bin/env python3
"""Prepare a cold-reader folder for ONE document.

Copies the first N lines of the document to OUTDIR/top.md and the images those lines
reference to the same relative paths inside OUTDIR, so a fresh agent sees exactly the first
screen and nothing else. Prints size figures (lines, words, characters) of what the reader gets.

Usage: python evals/prepare_cold_reader.py DOC.md OUTDIR [--lines 60]
"""
import re
import shutil
import sys
from pathlib import Path

IMG = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)")
CJK = re.compile(r"[\u4e00-\u9fff]")


def main():
    doc = Path(sys.argv[1])
    out = Path(sys.argv[2])
    n = int(sys.argv[sys.argv.index("--lines") + 1]) if "--lines" in sys.argv else 60
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    top = doc.read_text(encoding="utf-8-sig", errors="replace").splitlines()[:n]
    (out / "top.md").write_text("\n".join(top) + "\n", encoding="utf-8")
    copied = []
    for line in top:
        for rel in IMG.findall(line):
            if re.match(r"^[a-z][a-z0-9+.-]*:", rel, re.I):
                continue
            src = (doc.parent / rel)
            if src.is_file():
                dst = out / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied.append(rel)
    text = "\n".join(top)
    words = len(re.findall(r"\w+", CJK.sub(" x ", text)))
    print("%s: %d lines, %d words, %d chars; images: %s" % (doc.name, len(top), words, len(text), copied or "none"))


if __name__ == "__main__":
    main()
