#!/usr/bin/env python3
"""Render the README figures to PNG: the before/after hero, the anatomy of a first screen,
the four ideas, the workflow (in English and Chinese) and the social-preview card.

Maintainer tool; the skill does not need it. The hero, the anatomy and the social card are built from the
first-screen screenshots in examples/, so the pictures in the README are the actual documents.

Setup:   pip install playwright pillow && playwright install chromium
Usage:   python tools/build_readme_assets.py [hero] [anatomy] [ideas] [workflow] [social]
         (no argument renders all of them; output goes to docs/assets/)
"""
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples" / "01-upgrade-risk-report" / "images"
OUT = ROOT / "docs" / "assets"

FONT = '-apple-system, "Segoe UI", "Noto Sans", Helvetica, Arial, "Microsoft YaHei", "Segoe UI Emoji", sans-serif'
CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: %s; color: #1f2328; }
.canvas { position: relative; overflow: hidden; }
.pill { display: inline-block; font-weight: 700; border-radius: 999px; }
.shadow { box-shadow: 0 18px 40px rgba(31,35,40,.16), 0 2px 6px rgba(31,35,40,.10); }
""" % FONT


def uri(path):
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode("ascii")


def render(html, name, width, height):
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    page_html = "<!doctype html><html><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>" % (CSS, html)
    target = OUT / name
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        page.set_content(page_html, wait_until="load")
        page.screenshot(path=str(target), clip={"x": 0, "y": 0, "width": width, "height": height})
        browser.close()
    try:
        from PIL import Image
        im = Image.open(target)
        im.save(target, optimize=True)
    except ImportError:
        pass
    print("  wrote", target.relative_to(ROOT), "%d KB" % (target.stat().st_size // 1024))


# --------------------------------------------------------------------------- hero
def hero():
    left, right = uri(EX / "without-skill-first-screen.png"), uri(EX / "with-skill-first-screen.png")
    s = 800 / 1470.0  # screenshot scale in the cards
    tags = [("Verdict", 440, "#fb8500"), ("Decisions", 790, "#0969da"), ("Ranked risks", 1180, "#cf222e")]
    tag_html = "".join(
        '<span class="pill tag" style="top:%dpx;background:%s">%s</span>' % (int(y * s) - 16, c, t) for t, y, c in tags)
    html = """
<div class="canvas" style="width:1920px;height:1270px;background:linear-gradient(135deg,#f6f8fa 0%%,#e6edf6 100%%);padding:54px 72px 0 72px">
  <style>
    .kicker { font-size: 22px; letter-spacing: .14em; text-transform: uppercase; color: #57606a; font-weight: 700; }
    h1.big { font-size: 60px; line-height: 1.1; margin: 10px 0 34px; letter-spacing: -.02em; }
    h1.big em { font-style: normal; color: #0969da; }
    .row { display: flex; align-items: flex-start; }
    .card { width: 800px; position: relative; }
    .card .label { font-size: 24px; padding: 8px 20px; margin-bottom: 14px; }
    .grey { background: #d0d7de; color: #24292f; }
    .green { background: #2da44e; color: #fff; }
    .shotwrap { position: relative; width: 800px; height: 700px; }
    .shot { position: absolute; left: 0; top: 0; width: 800px; height: 700px; overflow: hidden; background: #fff; border: 1px solid #d0d7de; border-radius: 14px; }
    .shot img { display: block; width: 800px; }
    .card p { margin-top: 16px; font-size: 22px; line-height: 1.4; color: #424a53; width: 800px; }
    .mid { width: 160px; text-align: center; font-size: 64px; color: #8c959f; padding-top: 330px; }
    .tag { position: absolute; right: -66px; color: #fff; font-size: 20px; padding: 6px 16px; box-shadow: 0 4px 12px rgba(31,35,40,.25); }
    .stats { margin-top: 30px; background: #fff; border: 1px solid #d0d7de; border-radius: 16px; display: flex; padding: 20px 10px; width: 1760px; }
    .stat { flex: 1; text-align: center; border-right: 1px solid #eaeef2; }
    .stat:last-child { border-right: 0; }
    .stat b { display: block; font-size: 44px; letter-spacing: -.02em; }
    .stat b i { font-style: normal; color: #2da44e; padding: 0 8px; }
    .stat span { font-size: 19px; color: #57606a; }
  </style>
  <div class="kicker">Same agent &middot; same inputs &middot; same prompt</div>
  <h1 class="big">The only difference is <em>one skill</em>.</h1>
  <div class="row">
    <div class="card">
      <span class="pill label grey">Without the skill</span>
      <div class="shotwrap"><div class="shot shadow"><img src="%s"></div></div>
      <p>A competent report. The recommendation arrives in section 1, after a metadata list; the decisions, risks and evidence share one long body.</p>
    </div>
    <div class="mid">&rarr;</div>
    <div class="card">
      <span class="pill label green">With document-formatting</span>
      <div class="shotwrap"><div class="shot shadow"><img src="%s"></div>%s</div>
      <p>The same facts for a reader with one minute: the verdict, the decisions and the ranked risks fit the first screen, and each links to its proof.</p>
    </div>
  </div>
  <div class="stats shadow">
    <div class="stat"><b>10/22<i>&rarr;</i>22/22</b><span>assertions passed in this scenario</span></div>
    <div class="stat"><b>5<i>&rarr;</i>0</b><span>Major findings from the automatic checker</span></div>
    <div class="stat"><b>43/88<i>&rarr;</i>86/88</b><span>assertions passed across all four scenarios</span></div>
  </div>
</div>""" % (left, right, tag_html)
    render(html, "hero.png", 1920, 1270)


# --------------------------------------------------------------------------- anatomy
def anatomy():
    shot = uri(EX / "with-skill-first-screen.png")
    w = 700
    s = w / 1470.0
    top = 150
    marks = [  # (number, y in the screenshot, card top, title, text)
        (1, 268, 156, "Provenance in one line", "Date, who prepared it (here an AI agent), status, who it is for, and the sources with checksummed copies."),
        (2, 365, 286, "A banner that names the audience", "START HERE marks the part written for people. Machine and archive material comes last, collapsed."),
        (3, 580, 416, "Verdict", "A glyph and a word, the bottom line in two sentences, then the confidence and what it rests on."),
        (4, 947, 564, "Decisions needed", "One line each: who decides what by when, with a recommendation. The cost of being wrong is said once."),
        (5, 1375, 716, "Ranked risks", "A severity glyph, the consequence, and a link to the section that handles each risk."),
    ]
    markers, cards, lines = [], [], []
    x_img, x_card = 64 + w, 880
    for n, y, ctop, title, text in marks:
        my = top + int(y * s)
        markers.append('<span class="mk" style="left:%dpx;top:%dpx">%d</span>' % (x_img - 17, my - 17, n))
        cards.append('<div class="note" style="left:%dpx;top:%dpx"><span class="mk small">%d</span><h3>%s</h3><p>%s</p></div>' % (x_card, ctop, n, title, text))
        lines.append('<line x1="%d" y1="%d" x2="%d" y2="%d"/>' % (x_img + 17, my, x_card - 6, ctop + 40))
    html = """
<div class="canvas" style="width:1700px;height:1060px;background:linear-gradient(135deg,#f6f8fa,#e6edf6)">
  <style>
    h1.t { position: absolute; left: 64px; top: 40px; font-size: 44px; letter-spacing: -.02em; }
    p.sub { position: absolute; left: 64px; top: 96px; font-size: 22px; color: #57606a; }
    .page { position: absolute; left: 64px; top: %dpx; width: %dpx; border: 1px solid #d0d7de; border-radius: 12px; overflow: hidden; background: #fff; }
    .page img { display: block; width: %dpx; }
    .mk { position: absolute; width: 34px; height: 34px; border-radius: 50%%; background: #0969da; color: #fff; font-weight: 800; font-size: 19px; text-align: center; line-height: 34px; box-shadow: 0 2px 8px rgba(9,105,218,.5); border: 2px solid #fff; }
    .mk.small { position: static; display: inline-block; vertical-align: middle; margin-right: 10px; width: 30px; height: 30px; line-height: 26px; font-size: 17px; }
    .note { position: absolute; width: 756px; background: #fff; border: 1px solid #d0d7de; border-radius: 12px; padding: 14px 22px 14px; height: 118px; }
    .note h3 { font-size: 24px; display: inline-block; vertical-align: middle; }
    .note p { margin: 8px 0 0 40px; font-size: 19px; line-height: 1.35; color: #424a53; }
    svg.l { position: absolute; left: 0; top: 0; }
    svg.l line { stroke: #0969da; stroke-width: 2; stroke-dasharray: 5 5; opacity: .7; }
    .below { position: absolute; left: 64px; right: 64px; bottom: 36px; background: #fff; border: 1px dashed #8c959f; border-radius: 12px; padding: 14px 24px; font-size: 20px; color: #424a53; }
    .below b { color: #1f2328; }
  </style>
  <h1 class="t">Anatomy of a first screen</h1>
  <p class="sub">What the reader sees before scrolling, from the example report in <code>examples/01-upgrade-risk-report</code>. Everything here is one screen.</p>
  <div class="page shadow"><img src="%s"></div>
  %s
  <svg class="l" width="1700" height="1060">%s</svg>
  %s
  <div class="below"><b>Below the fold:</b> one picture of how the nine services depend on each other, a reading path with minutes and who can stop where, the numbered sections, then the machine and archive zone, last and collapsed.</div>
</div>""" % (top, w, w, shot, "".join(markers), "".join(lines), "".join(cards))
    render(html, "anatomy.png", 1700, 1060)


# --------------------------------------------------------------------------- four ideas
def ideas():
    graph = """<svg viewBox="0 0 220 130" width="220" height="130">
      <g stroke="#8c959f" stroke-width="2.4" fill="none">
        <path d="M110 24 L52 62 M110 24 L168 62 M52 62 L84 106 M168 62 L136 106 M84 106 L136 106 M110 24 L110 62 M110 62 L84 106 M110 62 L136 106"/>
      </g>
      <g fill="#2da44e"><circle cx="110" cy="24" r="14" fill="#fb8500"/><circle cx="52" cy="62" r="11"/><circle cx="168" cy="62" r="11"/>
        <circle cx="110" cy="62" r="11"/><circle cx="84" cy="106" r="11"/><circle cx="136" cy="106" r="11"/></g></svg>"""
    html = """
<div class="canvas" style="width:1800px;height:640px;background:linear-gradient(135deg,#f6f8fa,#e6edf6);padding:44px 56px">
  <style>
    h1.t { font-size: 40px; letter-spacing: -.02em; margin-bottom: 26px; }
    .grid { display: flex; gap: 24px; }
    .idea { flex: 1; background: #fff; border: 1px solid #d0d7de; border-radius: 16px; padding: 24px 26px; height: 470px; }
    .num { display: inline-block; width: 40px; height: 40px; border-radius: 50%%; background: #0969da; color: #fff; font-weight: 800; text-align: center; line-height: 40px; font-size: 22px; }
    .idea h2 { font-size: 30px; margin: 14px 0 6px; letter-spacing: -.01em; }
    .idea p { font-size: 20px; line-height: 1.4; color: #424a53; height: 112px; }
    .viz { margin-top: 10px; height: 200px; display: flex; align-items: center; justify-content: center; }
    .bin { border-radius: 10px; padding: 12px 16px; font-weight: 700; font-size: 20px; margin: 8px 0; width: 100%%; }
    .b1 { background: #0969da; color: #fff; box-shadow: 0 0 0 4px rgba(9,105,218,.2); }
    .b2 { background: #eaeef2; color: #57606a; font-weight: 600; }
    .b3 { background: #f6f8fa; color: #8c959f; font-weight: 600; border: 1px dashed #d0d7de; }
    .panel { width: 100%%; border-left: 5px solid #fb8500; background: #fff8f0; padding: 10px 14px; font-size: 18px; border-radius: 4px; }
    .panel b { font-size: 20px; }
    .rows span { display: inline-block; width: 12px; height: 12px; border-radius: 50%%; margin-right: 8px; }
    .rows div { font-size: 17px; margin-top: 7px; color: #424a53; }
    .path { display: flex; align-items: center; gap: 6px; font-size: 17px; font-weight: 700; flex-wrap: nowrap; justify-content: center; }
    .chip { background: #ddf4ff; color: #0550ae; padding: 8px 12px; border-radius: 10px; white-space: nowrap; }
    .arrow { color: #8c959f; font-size: 22px; }
    .stop { font-size: 17px; color: #57606a; margin-top: 12px; text-align: center; width: 100%%; }
  </style>
  <h1 class="t">Four ideas do the work</h1>
  <div class="grid">
    <div class="idea"><span class="num">1</span><h2>Audience split</h2>
      <p>Human-read, AI-input and archive content are kept apart, and the human part is unmistakable.</p>
      <div class="viz"><div style="width:100%%"><div class="bin b1">&#128100; For people &mdash; highlighted, first</div><div class="bin b2">&#129302; AI input &mdash; quiet, collapsed</div><div class="bin b3">&#128451; Archive &mdash; last, collapsed</div></div></div></div>
    <div class="idea"><span class="num">2</span><h2>Glance first</h2>
      <p>Verdict, decisions and risks come before anything else, in a form that lands in seconds.</p>
      <div class="viz"><div style="width:100%%"><div class="panel"><b>&#128993; Go with conditions</b><div class="rows"><div><span style="background:#0969da"></span>3 decisions: who, what, by when</div><div><span style="background:#cf222e"></span>Risk 1, ranked</div><div><span style="background:#fb8500"></span>Risk 2, ranked</div></div></div></div></div></div>
    <div class="idea"><span class="num">3</span><h2>Guided reading</h2>
      <p>Order, links and signposts follow how people learn, so the reader always knows what to read next.</p>
      <div class="viz"><div style="width:100%%"><div class="path"><span class="chip">Start here</span><span class="arrow">&rarr;</span><span class="chip">Why</span><span class="arrow">&rarr;</span><span class="chip">Evidence</span></div><div class="stop">Read next &middot; 3 min &middot; who can stop where</div></div></div></div>
    <div class="idea"><span class="num">4</span><h2>Draw the web</h2>
      <p>When related things form a network, show a picture instead of describing it.</p>
      <div class="viz">%s</div></div>
  </div>
</div>""" % graph
    render(html, "four-ideas.png", 1800, 640)


# --------------------------------------------------------------------------- workflow
WORKFLOW = {
    "en": {
        "file": "workflow.png",
        "title": "What the agent does, in order",
        "sub": "The skill loads by itself when your agent is about to write a large document.",
        "steps": [
            ("Sort", "Decide who each piece is for: people, the next AI agent, or the record."),
            ("Headline", "Write the verdict, the decisions and the ranked risks before anything else."),
            ("Layout", "Two zones, a glance panel, a reading path and sections that link to each other."),
            ("Draw", "Draw the web as an image, with its source file and a caption."),
            ("Check", "Run the checker and the rubric, then deliver the file and a short reply."),
        ],
        "loop": "Blocker or 3+ Majors: fix, then check again",
    },
    "zh-CN": {
        "file": "workflow-zh-CN.png",
        "title": "agent 的工作顺序",
        "sub": "当你的 agent 准备撰写大型文档时，skill 会自动加载。",
        "steps": [
            ("分类", "判断每一部分是写给谁的：<br>人、下一个 AI agent，<br>还是留作记录。"),
            ("先写核心", "先写结论、需要做的决定<br>和排序后的风险。"),
            ("布局", "两个分区、概览面板、<br>阅读路径，各节互相链接。"),
            ("画关系网", "把关系网画成图片，<br>并附上源文件和图注。"),
            ("检查", "运行检查器和评审标准，<br>然后交付文件和<br>一段简短的回复。"),
        ],
        "loop": "出现 Blocker 或 3 个以上 Major：修改后再检查",
    },
}


def workflow(lang="en"):
    text = WORKFLOW[lang]
    left0, pitch, width, top, height, canvas_h = 52, 352, 296, 170, 240, 520
    bottom = top + height
    drop = bottom + 54
    cx3, cx5 = left0 + 2 * pitch + width // 2, left0 + 4 * pitch + width // 2
    cards = []
    for i, (name, line) in enumerate(text["steps"]):
        x = left0 + i * pitch
        cards.append('<div class="step" style="left:%dpx"><span class="num">%d</span><h2>%s</h2><p>%s</p></div>' % (x, i + 1, name, line))
        if i < 4:
            cards.append('<div class="arrow" style="left:%dpx">&rarr;</div>' % (x + width))
    loop = "M%d %d V%d Q%d %d %d %d H%d Q%d %d %d %d V%d" % (cx5, bottom, drop - 16, cx5, drop, cx5 - 16, drop, cx3 + 16, cx3, drop, cx3, drop - 16, bottom + 8)
    html = (
        '<div class="canvas" style="width:1800px;height:%dpx;background:linear-gradient(135deg,#f6f8fa,#e6edf6)">' % canvas_h
        + """
  <style>
    h1.t { position: absolute; left: 56px; top: 40px; font-size: 40px; letter-spacing: -.02em; }
    .sub { position: absolute; left: 56px; top: 100px; font-size: 22px; color: #57606a; }
    .step { position: absolute; top: %dpx; width: %dpx; height: %dpx; background: #fff; border: 1px solid #d0d7de; border-radius: 16px; padding: 22px 24px; }
    .num { display: inline-block; width: 40px; height: 40px; border-radius: 50%%; background: #0969da; color: #fff; font-weight: 800; text-align: center; line-height: 40px; font-size: 22px; }
    .step h2 { font-size: 30px; margin: 12px 0 6px; letter-spacing: -.01em; }
    .step p { font-size: 20px; line-height: 1.4; color: #424a53; }
    .arrow { position: absolute; top: %dpx; width: 56px; text-align: center; font-size: 38px; color: #8c959f; }
    .loop { position: absolute; transform: translate(-50%%, -50%%); background: #fff8f0; border: 1px solid #fb8500; color: #953800; border-radius: 999px; padding: 6px 20px; font-size: 20px; font-weight: 700; white-space: nowrap; }
  </style>
  <h1 class="t">%s</h1><div class="sub">%s</div>
  <svg width="1800" height="%d" style="position:absolute;left:0;top:0">
    <defs><marker id="ah" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#fb8500"/></marker></defs>
    <path d="%s" fill="none" stroke="#fb8500" stroke-width="3" stroke-linejoin="round" marker-end="url(#ah)"/>
  </svg>
  """ % (top, width, height, top + height // 2 - 24, text["title"], text["sub"], canvas_h, loop)
        + "".join(cards)
        + '<div class="loop" style="left:%dpx;top:%dpx">%s</div></div>' % ((cx3 + cx5) // 2, drop, text["loop"])
    )
    render(html, text["file"], 1800, canvas_h)


# --------------------------------------------------------------------------- social preview
def social():
    shot = uri(EX / "with-skill-first-screen.png")
    icon = (OUT / "icon.svg").read_text(encoding="utf-8")
    html = """
<div class="canvas" style="width:1280px;height:640px;background:linear-gradient(135deg,#0d1117 0%%,#161b22 60%%,#0b2a4d 100%%);color:#f0f6fc">
  <style>
    .brand { position: absolute; left: 72px; top: 110px; width: 640px; }
    .brand svg { width: 124px; height: 124px; }
    .kick { font-size: 20px; letter-spacing: .18em; text-transform: uppercase; color: #58a6ff; font-weight: 700; margin-top: 26px; }
    h1.n { font-size: 62px; letter-spacing: -.03em; margin: 8px 0 12px; line-height: 1.05; }
    .tag { font-size: 30px; color: #adbac7; line-height: 1.3; }
    .chips { position: absolute; left: 72px; bottom: 64px; width: 660px; }
    .chips span { display: inline-block; margin: 0 10px 10px 0; padding: 8px 16px; border-radius: 999px; background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.18); font-size: 20px; color: #e6edf3; }
    .card { position: absolute; left: 770px; top: 56px; width: 560px; transform: rotate(3deg); border-radius: 14px; overflow: hidden; border: 1px solid #30363d; background: #fff; box-shadow: 0 30px 70px rgba(0,0,0,.55); }
    .card img { display: block; width: 560px; }
  </style>
  <div class="brand">%s<div class="kick">Agent skill</div><h1 class="n">document-formatting</h1><div class="tag">Write large documents for humans first.</div></div>
  <div class="chips"><span>Claude Code</span><span>GitHub Copilot</span><span>Codex</span><span>Cursor</span><span>Gemini CLI</span><span>OpenCode</span></div>
  <div class="card"><img src="%s"></div>
</div>""" % (icon, shot)
    render(html, "social-preview.png", 1280, 640)


if __name__ == "__main__":
    wanted = sys.argv[1:] or ["hero", "anatomy", "ideas", "workflow", "social"]
    figures = {"hero": hero, "anatomy": anatomy, "ideas": ideas, "social": social,
               "workflow": lambda: [workflow(lang) for lang in WORKFLOW]}
    for name in wanted:
        print(name)
        figures[name]()
