#!/usr/bin/env python3
"""Render a Markdown document (or the top of it) to a PNG with a GitHub-like stylesheet.

Maintainer tool: it produced the first-screen screenshots in examples/ and docs/.
The skill itself does not need it.

Setup:   pip install markdown-it-py playwright && playwright install chromium
Usage:   python tools/render_preview.py DOC.md OUT.png [--width 980] [--height 1100] [--start 0]
                                       [--scale 1.5] [--open-details]

Relative images are embedded, <details> blocks stay collapsed (as a reader first sees them) unless
--open-details is given, and Mermaid fences are shown as plain code (as in VS Code's classic preview).
"""
import argparse
import base64
import mimetypes
import re
import sys
import unicodedata
from pathlib import Path

CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, "Segoe UI", "Noto Sans", Helvetica, Arial, "Microsoft YaHei", "Noto Sans CJK SC",
       "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif;
       font-size: 16px; line-height: 1.5; color: #1f2328; margin: 0; padding: 28px 36px; background: #fff; }
h1 { font-size: 2em; border-bottom: 1px solid #d1d9e0; padding-bottom: .3em; margin: 0 0 16px; }
h2 { font-size: 1.5em; border-bottom: 1px solid #d1d9e0; padding-bottom: .3em; margin: 24px 0 16px; }
h3 { font-size: 1.25em; margin: 24px 0 16px; }
h4 { font-size: 1em; margin: 24px 0 16px; }
p, ul, ol, table, blockquote, pre, details { margin: 0 0 16px; }
blockquote { padding: 0 1em; color: #59636e; border-left: .25em solid #d1d9e0; }
blockquote h1, blockquote h2, blockquote h3 { border: 0; margin: 12px 0; color: #1f2328; }
table { border-collapse: collapse; display: block; max-width: 100%; overflow: auto; font-size: 14px; }
th, td { border: 1px solid #d1d9e0; padding: 6px 13px; vertical-align: top; }
th { font-weight: 600; background: #f6f8fa; }
tr:nth-child(2n) td { background: #f6f8fa; }
code { font-family: ui-monospace, "Cascadia Mono", Consolas, "Courier New", monospace; background: #818b981f;
       padding: .2em .4em; border-radius: 6px; font-size: 85%; }
pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow: auto; font-size: 85%; line-height: 1.45; }
pre code { background: none; padding: 0; }
img { max-width: 100%; }
a { color: #0969da; text-decoration: none; }
hr { border: 0; border-top: 1px solid #d1d9e0; margin: 24px 0; height: 0; }
details { border: 1px solid #d1d9e0; border-radius: 6px; padding: 8px 14px; }
summary { cursor: pointer; font-weight: 600; }
"""


def slugify(text):
    t = re.sub(r"<[^>]+>", "", text).lower()
    out = []
    for ch in t:
        if ch in "\ufe0f\u200d\u20e3":
            continue
        if unicodedata.category(ch)[0] in "LNM" or ch in "-_ ":
            out.append(ch)
    return "".join(out).replace(" ", "-")


def build_html(md_path, open_details=False):
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])
    env = {}
    tokens = md.parse(md_path.read_text(encoding="utf-8-sig", errors="replace"), env)
    seen = {}
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open" and i + 1 < len(tokens):
            base = slugify(tokens[i + 1].content)
            k = seen.get(base, 0)
            seen[base] = k + 1
            tok.attrSet("id", base if k == 0 else "%s-%d" % (base, k))
        if tok.type == "inline" and tok.children:
            for child in tok.children:
                if child.type != "image":
                    continue
                src = child.attrGet("src") or ""
                if re.match(r"^[a-z][a-z0-9+.-]*:", src, re.I):
                    continue
                p = (md_path.parent / src.replace("%20", " ")).resolve()
                if p.is_file():
                    mime = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
                    child.attrSet("src", "data:%s;base64,%s" % (mime, base64.b64encode(p.read_bytes()).decode("ascii")))
    body = md.renderer.render(tokens, md.options, env)
    if open_details:
        body = body.replace("<details>", "<details open>")
    return "<!doctype html><html><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>" % (CSS, body)


def screenshot_html(html, out_png, width=980, height=1100, start=0, scale=1.5):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=scale)
        page.set_content(html, wait_until="load")
        page.wait_for_timeout(300)
        total = page.evaluate("document.documentElement.scrollHeight")
        clip = {"x": 0, "y": start, "width": width, "height": max(min(height, total - start), 100)}
        page.screenshot(path=str(out_png), full_page=True, clip=clip)
        browser.close()
    return total


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doc")
    ap.add_argument("out")
    ap.add_argument("--width", type=int, default=980)
    ap.add_argument("--height", type=int, default=1100)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--scale", type=float, default=1.5)
    ap.add_argument("--open-details", action="store_true")
    a = ap.parse_args()
    doc = Path(a.doc).resolve()
    out = Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    total = screenshot_html(build_html(doc, a.open_details), out, a.width, a.height, a.start, a.scale)
    print("%s: page height %d px -> %s (%d bytes)" % (doc.name, total, out.name, out.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
