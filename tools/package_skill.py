#!/usr/bin/env python3
"""Package the skill as release artefacts.

Usage:
    python tools/package_skill.py [--out dist] [--skill skills/document-formatting]

Writes <name>.zip and <name>.skill (the same archive; Claude.ai and Claude Desktop accept either) and
SHA256SUMS to the output folder. The archive holds one top-level folder named after the skill, with
SKILL.md and the skill's own files only. Entries are sorted and timestamped 1980-01-01, so the same
sources always produce the same bytes. Standard library only.
"""
import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"__pycache__", "evals", ".DS_Store"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def skill_files(skill):
    for p in sorted(skill.rglob("*")):
        rel = p.relative_to(skill)
        if p.is_file() and not (set(rel.parts) & SKIP_PARTS) and p.suffix not in SKIP_SUFFIXES:
            yield p, rel


def build(skill, out):
    name = skill.name
    out.mkdir(parents=True, exist_ok=True)
    archive = out / ("%s.zip" % name)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path, rel in skill_files(skill):
            info = zipfile.ZipInfo("%s/%s" % (name, rel.as_posix()), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
    twin = out / ("%s.skill" % name)
    twin.write_bytes(archive.read_bytes())
    sums = "".join("%s  %s\n" % (hashlib.sha256(p.read_bytes()).hexdigest(), p.name) for p in (archive, twin))
    with open(str(out / "SHA256SUMS"), "w", encoding="utf-8", newline="\n") as fh:  # Path.write_text(newline=) needs Python 3.10
        fh.write(sums)
    return archive, twin


def main(argv=None):
    ap = argparse.ArgumentParser(description="Package the skill as .zip and .skill")
    ap.add_argument("--skill", default=str(ROOT / "skills" / "document-formatting"), help="the skill folder")
    ap.add_argument("--out", default=str(ROOT / "dist"), help="output folder")
    args = ap.parse_args(argv)
    skill = Path(args.skill).resolve()
    if not (skill / "SKILL.md").is_file():
        print("error: %s has no SKILL.md" % skill, file=sys.stderr)
        return 2
    archive, twin = build(skill, Path(args.out).resolve())
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
    print("wrote %s and %s (%d files)" % (archive.name, twin.name, len(names)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
