#!/usr/bin/env python3
"""Check a Markdown document against the automatic rules of references/review-rubric.md.

Usage:
    python check_doc.py REPORT.md [--json] [--allow-mermaid] [--machine-only]
                        [--max-block 25] [--max-table 15] [--panel-words 300] [--human-words 2500]
    python check_doc.py REPORT.md --slugs      # print each heading's anchor, for writing links

Every finding carries a rubric rule id and a tier:
  BLOCKER  certain defect: broken link or image, unbalanced fence or <details>, leftover
           template placeholder. Exit code 1.
  MAJOR    likely defect that weakens comprehension or trust. Fix it, or say why not.
  MINOR    polish.
The judgment rules of the rubric (conclusion first, honest labelling, diagram truth...)
cannot be checked by a script; the rubric says how to check those.

Only the standard library is used. Anchors follow the GitHub slug rules, which VS Code also
uses; Azure DevOps differs for headings with punctuation, which is why link-target headings
should be plain words and digits.
"""
import argparse
import difflib
import json
import re
import struct
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode = True  # importing this file as a module must not litter the skill folder
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*([\w+#.-]*)")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
LINK = re.compile(
    r"(!?)\[((?:[^\]\\]|\\.)*)\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
)
ZONE = re.compile(r"<!--\s*zone:\s*([a-z-]+)\s*-->", re.I)
REQUESTED_TABLE = re.compile(r"<!--\s*requested-table\b", re.I)
EXPLICIT_ID = re.compile(r"""<a\s+[^>]*?(?:id|name)\s*=\s*["']([^"']+)["']""", re.I)
EDGE = re.compile(r"-\.->|==>|-->|---|->|--")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
DIAGRAM_LANGS = {"mermaid", "dot", "graphviz", "plantuml"}
SHELL_LANGS = {"powershell", "ps1", "pwsh", "bash", "sh", "shell", "console", "cmd", "bat", "zsh"}
MACHINE_ZONES = {"ai-input", "archive", "machine"}
PLACEHOLDER = re.compile(
    r"\{(?:doc-stem|anchor|Section title|Who|what|when|overview|N|n|slug|title|date|audience|author or agent|\.\.\.)\}"
    r"|<!--\s*(?:No judgment to give|If this material is long|Block A only if)", re.I)
MACHINE_PATH = re.compile(r"[A-Za-z]:\\Users\\[^\\\s`'\"|)]+|/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/")
DATE = re.compile(r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}")
ALERT = re.compile(r"^\s*>\s*\[!(?:NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", re.I)
LOUD_QUOTE = re.compile(r"^\s*>\s*#{1,6}\s")
SOURCE_EXT = (".dot", ".gv", ".mmd", ".puml", ".py", ".svg", ".drawio")
CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")
LATIN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_'\u2019-]*")
MAX_PNG_WIDTH = 2600
MIN_PNG_WIDTH = 500
TIER_ORDER = {"BLOCKER": 0, "MAJOR": 1, "MINOR": 2}


def slugify(text):
    """GitHub-style heading slug (no trimming, so a leading emoji gives a leading hyphen)."""
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    t = re.sub(r"<[^>]+>", "", t).lower()
    out = []
    for ch in t:
        if ch in "\ufe0f\u200d\u20e3":
            continue
        if unicodedata.category(ch)[0] in "LNM" or ch in "-_ ":
            out.append(ch)
    return "".join(out).replace(" ", "-")


def count_words(text):
    """English words plus CJK characters scaled to reading effort (about 1.6 characters per word)."""
    return len(LATIN.findall(text)) + len(CJK.findall(text)) / 1.6


def prose(line):
    """A line reduced to the words a reader reads: no markup, link targets, images or comments."""
    t = re.sub(r"<!--.*?-->", "", line)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"^\s*(?:>\s*)*(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)?", "", t)
    if t.lstrip().startswith("|"):
        t = re.sub(r"[|:\-]+", " ", t)
    return t.replace("**", "").replace("`", "")


def png_size(path):
    """Width and height of a PNG from its header, or None."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(24)
    except OSError:
        return None
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def scan(lines):
    """Split a document into lines outside code fences and the fences themselves."""
    body, fences = [], []
    in_fence, fchar, flen, flang, fstart = False, "", 0, "", 0
    for i, line in enumerate(lines, 1):
        m = FENCE.match(line)
        if in_fence:
            if m and m.group(1)[0] == fchar and len(m.group(1)) >= flen and not m.group(2).strip():
                fences.append((fstart, i, flang))
                in_fence = False
            continue
        if m:
            in_fence, fchar, flen, flang, fstart = True, m.group(1)[0], len(m.group(1)), m.group(2).lower(), i
            continue
        body.append((i, line))
    unclosed = (fstart, flang) if in_fence else None
    return body, fences, unclosed


def headings_of(body):
    """Headings as (line, level, raw text, slug) plus a slug -> (line, raw) map, GitHub duplicate rules."""
    headings, slugs, seen = [], {}, {}
    for n, line in body:
        m = HEADING.match(line)
        if not m:
            continue
        base = slugify(m.group(2))
        k = seen.get(base, 0)
        seen[base] = k + 1
        slug = base if k == 0 else "%s-%d" % (base, k)
        headings.append((n, len(m.group(1)), m.group(2), slug))
        slugs[slug] = (n, m.group(2))
    return headings, slugs


def collect_anchors(path):
    """Heading slugs and explicit ids of another Markdown file."""
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return set()
    body, _, _ = scan(lines)
    _, slugs = headings_of(body)
    found = set(slugs)
    for _, line in body:
        found.update(i.lower() for i in EXPLICIT_ID.findall(line))
    return found


def check(path, args):
    findings = []  # (tier, rule, line, message)

    def add(tier, rule, line, msg):
        findings.append((tier, rule, line, msg))

    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    body, fences, unclosed = scan(lines)
    if unclosed:
        add("BLOCKER", "B4", unclosed[0], "code fence opened here is never closed")
    nonblank = sum(1 for l in lines if l.strip())

    headings, slugs = headings_of(body)
    explicit = set()
    for _, line in body:
        explicit.update(i.lower() for i in EXPLICIT_ID.findall(line))

    # Zones (needed early: several rules only apply to the human zone)
    zones = [(n, ZONE.search(t).group(1).lower()) for n, t in body if ZONE.search(t)]
    names = [z for _, z in zones]
    machine_only = args.machine_only or (
        bool(names) and "human" not in names and any(z in MACHINE_ZONES for z in names))
    human_start = next((n for n, z in zones if z == "human"), 1)
    first_machine = next((n for n, z in zones if z in MACHINE_ZONES), None)
    if machine_only:
        human_start, human_end = 0, 0
    else:
        human_end = first_machine if first_machine and first_machine > human_start else len(lines) + 1
    in_human = lambda n: human_start <= n < human_end  # noqa: E731

    # Links and images (inline code removed first so `[x](#y)` in code is ignored)
    links, img_openers = [], 0
    for n, line in body:
        clean = re.sub(r"`[^`]*`", "", line)
        img_openers += len(re.findall(r"!\[", clean))
        for m in LINK.finditer(clean):
            links.append((n, m.group(1) == "!", m.group(2), m.group(3)))
    parsed_images = sum(1 for _, is_img, _, _ in links if is_img)
    if img_openers > parsed_images:
        add("MAJOR", "B4", 0, "%d image(s) use unusual syntax (spaces in the path?); they were not checked"
            % (img_openers - parsed_images))

    for n, line in body:
        hit = PLACEHOLDER.search(line)
        if hit:
            add("BLOCKER", "B4", n, "leftover template placeholder or hint: %s" % hit.group(0)[:40])

    internal, target_slugs, anchor_cache = 0, set(), {}
    for n, is_img, alt, target in links:
        if is_img and not alt.strip():
            add("MINOR", "D5", n, "image has empty alt text; say in one sentence what it shows")
        if target.startswith("#"):
            internal += 1
            anchor = unquote(target[1:]).lower()
            if anchor in slugs or anchor in explicit:
                target_slugs.add(anchor)
            else:
                near = difflib.get_close_matches(anchor, list(slugs), n=1, cutoff=0.6)
                hint = " - did you mean #%s?" % near[0] if near else ""
                add("BLOCKER", "B4", n, "broken in-document link #%s%s" % (anchor, hint))
            continue
        if SCHEME.match(target) or target.startswith("//") or target.startswith("/"):
            if is_img and re.match(r"^(file:|[a-z]:[\\/])", target, re.I):
                add("BLOCKER", "B4", n, "image uses a machine-local path (%s); use a relative path" % target)
            continue
        if re.match(r"^[a-z]:[\\/]", target, re.I) or "\\" in target:
            add("MAJOR", "B4", n, "path %r uses a drive letter or backslashes; use a relative path with "
                "forward slashes" % target)
            continue
        if "%20" in target:
            add("MINOR", "F5", n, "path %r contains a space; name files without spaces" % target)
        rel = unquote(re.split(r"[#?]", target)[0])
        if not rel:
            continue
        target_path = path.parent / rel
        if not target_path.exists():
            add("BLOCKER" if is_img else "MAJOR", "B4", n,
                "%s target not found: %s" % ("image" if is_img else "link", rel))
            continue
        if "#" in target and rel.lower().endswith((".md", ".markdown")):
            frag = unquote(target.split("#", 1)[1]).lower()
            if frag:
                if target_path not in anchor_cache:
                    anchor_cache[target_path] = collect_anchors(target_path)
                known = anchor_cache[target_path]
                if frag not in known:
                    near = difflib.get_close_matches(frag, list(known), n=1, cutoff=0.6)
                    hint = " - did you mean #%s?" % near[0] if near else ""
                    add("BLOCKER", "B4", n, "broken link: %s has no heading #%s%s" % (rel, frag, hint))
        if is_img and rel.lower().endswith(".png"):
            size = png_size(target_path)
            if size and size[0] > MAX_PNG_WIDTH:
                add("MAJOR", "D4", n, "%s is %d px wide; its labels shrink to a speck at 800 px - split the "
                    "diagram or use fewer, larger labels" % (rel, size[0]))
            elif size and size[0] < MIN_PNG_WIDTH:
                add("MINOR", "D4", n, "%s is only %d px wide; check that it is sharp enough" % (rel, size[0]))
            if not any(target_path.with_suffix(ext).exists() for ext in SOURCE_EXT):
                add("MINOR", "D6", n, "no source file beside %s (.dot, .mmd, .py ...); keep it so the image "
                    "can be regenerated" % rel)

    # Fragile anchors and duplicates among link targets
    for n, _, raw, slug in headings:
        if slug not in target_slugs:
            continue
        plain = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", raw).replace("*", "").replace("`", "")
        if re.search(r"[^\w\s-]", plain):
            add("MINOR", "B6", n, "heading %r is a link target but contains punctuation or emoji; its anchor may "
                "differ between viewers - use plain words and digits" % raw)
        if re.search(r"-\d+$", slug) and slug[: slug.rfind("-")] in slugs:
            add("MINOR", "B6", n, "duplicate heading text %r; its anchor depends on order - make it unique" % raw)

    # <details> hygiene (blank lines matter for nested Markdown and in Azure DevOps); tags inside inline code are text
    body_nocode = [(n, re.sub(r"`[^`]*`", "", t)) for n, t in body]
    opens = sum(len(re.findall(r"<details\b", t, re.I)) for _, t in body_nocode)
    closes = sum(len(re.findall(r"</details>", t, re.I)) for _, t in body_nocode)
    if opens != closes:
        add("BLOCKER", "B4", 0, "unbalanced <details>: %d opening vs %d closing tags" % (opens, closes))
    for n, line in body_nocode:
        for tag in ("</summary>", "</details>"):
            if tag in line.lower() and n < len(lines) and lines[n].strip():
                add("MAJOR", "F5", n, "add a blank line after %s (needed for rendering)" % tag)

    # A1 zones
    if not zones and nonblank > 80 and not machine_only:
        add("MAJOR", "A1", 0, "no <!-- zone:... --> markers; human-read and machine/archive content are not marked "
            "(for a large document with raw material this is a Blocker)")
    if zones and "human" not in names and not machine_only:
        add("MAJOR", "A1", 0, "zone markers exist but none is <!-- zone:human -->")
    if "human" in names and first_machine is not None and first_machine < human_start:
        add("MAJOR", "A1", first_machine, "machine/archive zone starts before the human zone")
    if "human" in names and first_machine is None and nonblank > 150:
        add("MINOR", "A1", 0, "no machine/archive zone; confirm no raw logs, listings or data sit in the human part")

    # A2 raw material in the human zone
    for s, e, lang in fences:
        if not in_human(s) or lang in DIAGRAM_LANGS:
            continue
        if (e - s - 1) > args.max_block:
            add("MAJOR", "A2", s, "%d-line code block in the human zone; move raw material to the machine/archive zone"
                % (e - s - 1))
        elif lang in SHELL_LANGS:
            add("MINOR", "A2", s, "shell commands in the human zone; move them to the AI-input block unless "
                "the reader must run them")
    run_start, run_len = 0, 0
    for n, line in body + [(10 ** 9, "")]:
        if line.lstrip().startswith("|"):
            run_start = run_start or n
            run_len += 1
            continue
        if run_len > args.max_table + 2 and in_human(run_start):
            marked = any(REQUESTED_TABLE.search(lines[k]) for k in range(max(run_start - 4, 0), run_start - 1))
            if not marked:
                add("MAJOR", "A2", run_start, "%d-row table in the human zone; summarise it and move the full table "
                    "to the archive (a table the user asked for by name is fine: put <!-- requested-table --> on "
                    "the line above it)" % (run_len - 2))
        run_start, run_len = 0, 0

    # A5 machine-local paths
    local_paths = [(n, m.group(0)) for n, l in enumerate(lines, 1) for m in [MACHINE_PATH.search(l)] if m]
    for n, p in local_paths[:3]:
        add("MAJOR", "A5", n, "machine-specific path %r; use a path relative to the document or the repo "
            "(fine only if it comes from the source material)" % p[:60])
    if len(local_paths) > 3:
        add("MAJOR", "A5", local_paths[3][0], "%d more machine-specific paths further down" % (len(local_paths) - 3))

    # B1/B5/C1/C2 glance panel and reading path
    h1 = next((n for n, lvl, _, _ in headings if lvl == 1), 0)
    panel_words = human_words = 0
    if not machine_only:
        window = range(h1 + 1, h1 + 61)
        top_links = sum(1 for n, _, _, tgt in links if tgt.startswith("#") and n in window)
        if top_links < 3:
            add("MAJOR", "B1", h1 or 1, "only %d in-document link(s) in the 60 lines after the title; "
                "give a 'Read next' path with at least 3" % top_links)
        if nonblank > 150 and internal < 5:
            add("MAJOR", "B5", 0, "a large document needs navigation: %d in-document link(s), expected at least 5"
                % internal)
        first_el = next((n for n, t in body if n > h1 and re.match(r"^\s*(>|\||!\[)", t)), None)
        if first_el is None or first_el > h1 + 60:
            add("MAJOR", "C1", h1 or 1, "no blockquote, table or image in the 60 lines after the title; "
                "is there a glance panel with the verdict, decision and risks?")
        else:
            before = sum(1 for n, t in body if h1 < n < first_el and t.strip()
                         and not ZONE.search(t) and not HEADING.match(t))
            if before > 12:
                add("MAJOR", "C1", h1 or 1, "%d lines of text come before the first panel element; the conclusion "
                    "should open the document, ahead of background, provenance or reading guides" % before)
        h2s = [n for n, lvl, _, _ in headings if lvl == 2 and n > h1]
        if h2s:
            end = h2s[1] if len(h2s) > 1 else human_end
            if first_machine and h2s[0] < first_machine < end:
                end = first_machine
            panel_words = sum(count_words(prose(t)) for n, t in body
                              if h2s[0] < n < end and not t.lstrip().startswith("|")
                              and not t.lstrip().startswith("![")
                              and not re.match(r"^\s*(?:>\s*)*[-*+]\s+\[", t))
            if panel_words > args.panel_words:
                add("MAJOR", "C2", h2s[0], "the first section runs to about %d words (budget %d; tables, picture and "
                    "link-led Read-next bullets excluded); keep the panel short and link to detail"
                    % (panel_words, args.panel_words))
        human_words = sum(count_words(prose(t)) for n, t in body if in_human(n))
        if human_words > args.human_words:
            add("MINOR", "F2", human_start or 1, "the human zone runs to about %d words (advice: %d); fine when every "
                "part is needed by someone deciding or reviewing, otherwise move detail to the archive"
                % (human_words, args.human_words))
        if not any(DATE.search(t) for n, t in body if h1 <= n <= h1 + 8):
            add("MINOR", "E3", h1 or 1, "no date near the title; add a line with date, author or agent, status, "
                "audience")

    # D3/D4 diagrams in code fences
    diagrams = 0
    for s, e, lang in fences:
        if lang not in DIAGRAM_LANGS:
            continue
        diagrams += 1
        block = "\n".join(lines[s:e - 1])
        edges = len(EDGE.findall(block))
        if edges > 25:
            add("MAJOR", "D4", s, "%s diagram has about %d edges; split it into an overview plus zoomed views" % (lang, edges))
        if lang == "mermaid":
            first = next((l.strip() for l in lines[s:e - 1] if l.strip()), "")
            if first.startswith("flowchart"):
                add("MINOR", "D3", s, "Azure DevOps wikis do not support 'flowchart'; use 'graph' if it will be read there")
            if "---->" in block:
                add("MINOR", "D3", s, "long arrows (---->) are unsupported in Azure DevOps Mermaid")
            if in_human(s) and not args.allow_mermaid:
                add("MAJOR", "D3", s, "inline Mermaid in the human zone does not render in VS Code's preview or Azure "
                    "DevOps repo pages; embed a rendered PNG and keep the source beside it")

    # F5 hygiene
    quotes = [n for n, t in body if LOUD_QUOTE.match(t)]
    if len(quotes) > 3:
        add("MINOR", "F5", quotes[3], "%d blockquote headings; loud formatting is for the verdict and the decisions "
            "(a budget of about 3)" % len(quotes))
    alerts = [n for n, t in body if ALERT.match(t)]
    if alerts:
        add("MINOR", "F5", alerts[0], "'> [!NOTE]'-style alert (%d); many previews and Azure DevOps show the raw tag - "
            "use a plain blockquote" % len(alerts))
    styled = [n for n, t in body if re.search(r"<font\b|\bstyle\s*=", t, re.I)]
    if styled:
        add("MINOR", "F5", styled[0], "HTML colour or style (%d); it is stripped by GitHub and Azure DevOps" % len(styled))
    seen_lines = {}
    for n, t in body:
        norm = re.sub(r"\s+", " ", prose(t)).strip().lower()
        if len(norm) >= 80 and not t.lstrip().startswith("|"):
            if norm in seen_lines:
                add("MINOR", "F5", n, "same text as line %d; write each fact once and link to it" % seen_lines[norm])
            else:
                seen_lines[norm] = n

    stats = {
        "lines": len(lines),
        "headings": len(headings),
        "internal_links": internal,
        "images": parsed_images,
        "diagram_blocks": diagrams,
        "details_blocks": opens,
        "zones": names,
        "machine_only": bool(machine_only),
        "panel_words": round(panel_words),
        "human_zone_words": round(human_words),
    }
    return findings, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true", help="print machine-readable results")
    ap.add_argument("--allow-mermaid", action="store_true",
                    help="readers use GitHub or Azure DevOps wikis: inline Mermaid in the human zone is fine")
    ap.add_argument("--machine-only", action="store_true",
                    help="treat the file as archive or AI-input only (skips human-zone rules)")
    ap.add_argument("--max-block", type=int, default=25, help="longest code block allowed in the human zone")
    ap.add_argument("--max-table", type=int, default=15, help="most table rows allowed in the human zone")
    ap.add_argument("--panel-words", type=int, default=300, help="prose budget of the glance panel")
    ap.add_argument("--human-words", type=int, default=2500, help="advisory word count of the human zone")
    ap.add_argument("--slugs", action="store_true",
                    help="print the anchor of every heading (as VS Code and GitHub build them) and exit")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    path = Path(args.file)
    if not path.is_file():
        print("ERROR: file not found: %s" % path)
        return 2
    if args.slugs:
        body, _, _ = scan(path.read_text(encoding="utf-8-sig", errors="replace").splitlines())
        for n, level, raw, slug in headings_of(body)[0]:
            print("line %4d  h%d  #%s   <- %s" % (n, level, slug, raw))
        return 0
    findings, stats = check(path, args)
    findings.sort(key=lambda f: (TIER_ORDER[f[0]], f[2]))
    counts = {t: sum(1 for f in findings if f[0] == t) for t in TIER_ORDER}
    if args.json:
        out = {"file": str(path), "stats": stats,
               "gate": {"blockers": counts["BLOCKER"], "majors": counts["MAJOR"], "minors": counts["MINOR"]}}
        for tier, key in (("BLOCKER", "blockers"), ("MAJOR", "majors"), ("MINOR", "minors")):
            out[key] = [{"rule": r, "line": l, "message": m} for t, r, l, m in findings if t == tier]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for tier, rule, line, msg in findings:
            print("%-7s %-3s %s %s" % (tier, rule, ("line %d:" % line) if line else "doc:", msg))
        print("-- %s: %d blocker(s), %d major(s), %d minor(s); %s" % (
            path.name, counts["BLOCKER"], counts["MAJOR"], counts["MINOR"], json.dumps(stats)))
    return 1 if counts["BLOCKER"] else 0


if __name__ == "__main__":
    sys.exit(main())
