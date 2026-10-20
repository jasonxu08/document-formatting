"""Builds the two diagrams used in ../report.md.

Outputs (next to this script):
  pipeline.svg / pipeline.png                    Figure 1: the platform map
  version-lifecycle.svg / version-lifecycle.png  Figure 2: Catalog status of one Version

Usage:  python build_diagrams.py              writes the SVGs, and the PNGs if Edge or Chrome is found
        python build_diagrams.py --svg-only

The SVGs are plain, hand-editable XML. The PNGs are what the guide embeds, because PNG
renders everywhere (wiki engines differ in how they treat SVG). Change the coordinates in
this file rather than editing the images.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

FONT = "'Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "Consolas,'Cascadia Mono','Courier New',monospace"

INK = "#1F2937"
MUTED = "#6B7280"
LINE = "#374151"
PURPLE = "#7B4EA3"
RED = "#C0392B"

THEMES = {  # fill, stroke
    "svc":   ("#F1E8FA", "#7B4EA3"),   # supporting services
    "app":   ("#DCEBFA", "#2F6EB5"),   # our pipeline components
    "queue": ("#FFF1CC", "#B7791F"),   # message queue
    "store": ("#E4F3DA", "#4C8C2B"),   # storage zones
    "fail":  ("#FDE9E7", "#C0392B"),   # quarantine / failure path
}


class Svg:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def band(self, y0, y1, label):
        self.add(f'<rect x="0" y="{y0}" width="{self.w}" height="{y1 - y0}" rx="12" fill="#F5F7FA"/>')
        self.add(
            f'<text transform="translate(26 {(y0 + y1) / 2}) rotate(-90)" text-anchor="middle" '
            f'font-size="14" font-weight="600" letter-spacing="2" fill="{MUTED}">{escape(label)}</text>'
        )

    def box(self, x, y, w, h, theme, title, subs=(), mono=False, title_size=21, sub_size=16, rx=12,
            sub_mono=False):
        fill, stroke = THEMES[theme]
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.8"/>'
        )
        tl, sl = 26, 21  # line heights
        top = y + (h - (tl + len(subs) * sl)) / 2
        cx = x + w / 2
        fam = MONO if mono else FONT
        sfam = f' font-family="{MONO}"' if sub_mono else ""
        self.add(
            f'<text x="{cx}" y="{top + 19}" text-anchor="middle" font-family="{fam}" '
            f'font-size="{title_size}" font-weight="600" fill="{INK}">{escape(title)}</text>'
        )
        for i, s in enumerate(subs):
            self.add(
                f'<text x="{cx}" y="{top + tl + 15 + i * sl}" text-anchor="middle"{sfam} '
                f'font-size="{sub_size}" fill="#374151">{escape(s)}</text>'
            )

    def label(self, x, y, text, anchor="start", color=INK, size=17, weight=400):
        """Text label; use `backticks` for monospace runs and \\n for line breaks."""
        for i, ln in enumerate(text.split("\n")):
            body = "".join(
                f'<tspan font-family="{MONO}">{escape(r)}</tspan>' if n % 2 else escape(r)
                for n, r in enumerate(ln.split("`"))
            )
            self.add(
                f'<text x="{x}" y="{y + i * (size + 3)}" text-anchor="{anchor}" '
                f'font-size="{size}" font-weight="{weight}" fill="{color}">{body}</text>'
            )

    def arrow(self, d, color=LINE, dash=False, width=2.2):
        mk = {LINE: "dark", PURPLE: "purple", RED: "red"}[color]
        da = ' stroke-dasharray="7 5"' if dash else ""
        self.add(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da} '
            f'marker-end="url(#m-{mk})"/>'
        )

    def render(self, title, desc):
        defs = "".join(
            f'<marker id="m-{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
            f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
            for n, c in (("dark", LINE), ("purple", PURPLE), ("red", RED))
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}" role="img">'
            f"<title>{escape(title)}</title><desc>{escape(desc)}</desc><defs>{defs}</defs>"
            f'<rect width="{self.w}" height="{self.h}" fill="#FFFFFF"/>'
            + "".join(self.parts)
            + "</svg>\n"
        )


# --------------------------------------------------------------------------------------
# Figure 1: platform map. Three bands: supporting services (top), pipeline (middle),
# storage (bottom). Each pipeline component has straight vertical links to the shared
# hubs (Catalog above, Raw Zone below), so no two lines cross.
# --------------------------------------------------------------------------------------
def pipeline():
    W, H = 1380, 925
    s = Svg(W, H)
    s.band(10, 296, "SUPPORTING SERVICES")
    s.band(306, 486, "PIPELINE")
    s.band(496, 800, "STORAGE")

    # shared hubs
    s.box(160, 30, 1180, 62, "svc", "Catalog",
          ["metadata store, source of truth for status: datasets, Versions, lineage, owners"])
    s.box(160, 716, 1180, 62, "store", "Raw Zone",
          ["immutable blob storage; keeps the original upload for 1 year"])

    # supporting services
    s.box(145, 172, 170, 60, "svc", "Policy Engine", ["access decisions"])
    s.box(572, 172, 176, 60, "svc", "Schema Registry", ["Schema contracts"])
    s.box(915, 172, 170, 60, "svc", "Notifier", ["fire-and-forget"])

    # pipeline spine
    cy = 395
    top, bot = cy - 35, cy + 35
    s.box(190, top, 200, 70, "app", "Uploader API", ["only public entry point"])
    s.box(435, top, 160, 70, "queue", "Message Queue", ["validate"], title_size=19, sub_mono=True)
    s.box(640, top, 205, 70, "app", "Validation Worker")
    s.box(900, top, 160, 70, "queue", "Message Queue", ["transform"], title_size=19, sub_mono=True)
    s.box(1105, top, 205, 70, "app", "Transform Worker")

    # storage
    s.box(575, 556, 170, 70, "fail", "Quarantine Store", ["kept 30 days"], title_size=19)
    s.box(1170, 556, 170, 70, "store", "Curated Zone", ["lakehouse tables"])

    # main data path
    s.arrow(f"M52,{cy} H190")
    s.label(121, cy - 33, "customer", anchor="middle")
    s.label(121, cy - 12, "upload", anchor="middle")
    s.arrow(f"M390,{cy} H435")
    s.arrow(f"M595,{cy} H640")
    s.arrow(f"M845,{cy} H900")
    s.label(872.5, cy - 12, "pass", anchor="middle")
    s.arrow(f"M1060,{cy} H1105")

    # calls up to supporting services (dashed purple)
    s.arrow(f"M230,{top} V232", PURPLE, dash=True)
    s.label(238, 305, "may upload?", color=PURPLE)
    s.arrow(f"M360,{top} V92", PURPLE, dash=True)
    s.label(368, 138, "Version: `received`", color=PURPLE)
    s.arrow(f"M660,{top} V232", PURPLE, dash=True)
    s.label(668, 305, "get contract", color=PURPLE)
    s.arrow(f"M790,{top} V92", PURPLE, dash=True)
    s.label(798, 138, "`validated` / `quarantined`", color=PURPLE)
    s.arrow(f"M825,{top} L955,232", PURPLE, dash=True)
    s.label(890, 338, "on quarantine", color=PURPLE)
    s.arrow(f"M1140,{top} L1045,232", PURPLE, dash=True)
    s.label(1130, 338, "on publish", color=PURPLE)
    s.arrow(f"M1275,{top} V92", PURPLE, dash=True)
    s.label(1267, 138, "lineage + `published`", anchor="end", color=PURPLE)
    s.arrow("M230,92 V172", PURPLE, dash=True)
    s.label(222, 138, "who can see a dataset", anchor="end", color=PURPLE)

    # storage links
    s.arrow(f"M350,{bot} V716")
    s.label(358, 600, "stream file")
    s.arrow(f"M660,{bot} V556", RED)
    s.label(668, 500, "fail: copy file", color=RED)
    s.arrow(f"M810,716 V{bot}")
    s.label(818, 640, "read")
    s.arrow(f"M1135,716 V{bot}")
    s.label(1127, 640, "read", anchor="end")
    s.arrow(f"M1265,{bot} V556")
    s.label(1257, 500, "write tables", anchor="end")

    # legend and notes
    ly = 842
    s.arrow(f"M60,{ly} H110")
    s.label(120, ly + 6, "main data path")
    s.arrow(f"M290,{ly} H340", PURPLE, dash=True)
    s.label(350, ly + 6, "call to a supporting service (label says why)")
    s.arrow(f"M760,{ly} H810", RED)
    s.label(820, ly + 6, "validation failure path")
    s.label(60, ly + 42,
            "The two Message Queue boxes are one queue carrying two message types. "
            "After 3 failed attempts a message goes to the DLQ.", color=MUTED, size=15)
    s.label(60, ly + 64,
            "The Policy Engine is also called by the Curated Zone, for row-level access rules.",
            color=MUTED, size=15)
    return s.render(
        "Ingestion platform map",
        "A customer uploads to the Uploader API, which checks the Policy Engine, streams the file into the Raw Zone, "
        "records the Version in the Catalog and queues a validate message. The Validation Worker checks the file "
        "against its Schema contract from the Schema Registry; a pass queues a transform message, a failure copies the "
        "file to the Quarantine Store and notifies the owner. The Transform Worker writes the Curated Zone, records "
        "lineage and published status in the Catalog and notifies the owner.",
    ), W, H


# --------------------------------------------------------------------------------------
# Figure 2: Catalog status of one Version
# --------------------------------------------------------------------------------------
def lifecycle():
    W, H = 1240, 430
    s = Svg(W, H)
    s.label(24, 32, "CATALOG STATUS OF ONE VERSION", color=MUTED, size=14, weight=600)

    y, h, w = 78, 96, 236
    cy = y + h / 2
    qy = 246
    qcy = qy + h / 2
    rx_, vx, px = 170, 566, 962

    s.box(rx_, y, w, h, "app", "received", ["file stored in Raw Zone,", "validate message queued"], mono=True)
    s.box(vx, y, w, h, "app", "validated", ["file matches its contract,", "transform message queued"], mono=True)
    s.box(px, y, w, h, "store", "published", ["tables in Curated Zone,", "Lineage record written"], mono=True)
    s.box(vx, qy, w, h, "fail", "quarantined", ["copy in Quarantine Store,", "owner told why"], mono=True)

    # start
    s.add(f'<circle cx="36" cy="{cy}" r="9" fill="{LINE}"/>')
    s.arrow(f"M46,{cy} H{rx_}")
    s.label((46 + rx_) / 2, cy - 12, "Uploader API", anchor="middle")

    # received -> validated -> published
    s.arrow(f"M{rx_ + w},{cy} H{vx}")
    mid1 = (rx_ + w + vx) / 2
    s.label(mid1, cy - 33, "Validation Worker:", anchor="middle")
    s.label(mid1, cy - 12, "file passes", anchor="middle")
    s.arrow(f"M{vx + w},{cy} H{px}")
    mid2 = (vx + w + px) / 2
    s.label(mid2, cy - 33, "Transform Worker:", anchor="middle")
    s.label(mid2, cy - 12, "done", anchor="middle")

    # received -> quarantined
    qx = 290
    s.arrow(f"M{qx},{y + h} V{qcy} H{vx}", RED)
    s.label((qx + vx) / 2, qcy - 27, "Validation Worker:", anchor="middle", color=RED)
    s.label((qx + vx) / 2, qcy - 7, "file fails", anchor="middle", color=RED)

    # quarantined -> back to the start: a corrected upload is a new Version
    loop_y = qy + h + 54
    lx = 234
    s.arrow(f"M{vx + w / 2},{qy + h} V{loop_y} H{lx} V{y + h}", LINE, dash=True)
    cxl = (lx + vx + w / 2) / 2
    s.label(cxl, loop_y - 31, "Owner fixes the file and re-uploads:", anchor="middle")
    s.label(cxl, loop_y - 11, "a new Version starts at `received`", anchor="middle")
    return s.render(
        "Catalog status of one Version",
        "A Version starts as received (set by the Uploader API). The Validation Worker moves it to validated if the "
        "file passes or to quarantined if it fails. The Transform Worker moves a validated Version to published. "
        "A quarantined file is fixed by the owner and re-uploaded, which creates a new Version that starts at received.",
    ), W, H


# --------------------------------------------------------------------------------------
def find_browser():
    for p in (
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ):
        if os.path.exists(p):
            return p
    return shutil.which("msedge") or shutil.which("chrome") or shutil.which("chromium")


def rasterize(svg_path, png_path, w, h, scale=2):
    browser = find_browser()
    if not browser:
        print("No Edge/Chrome found: skipped PNG for", svg_path.name)
        return
    profile = Path(tempfile.mkdtemp(prefix="diagram-profile-", dir=HERE))
    try:
        cmd = [
            browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            f"--user-data-dir={profile}", f"--force-device-scale-factor={scale}",
            f"--window-size={w},{h + 200}", f"--screenshot={png_path}", svg_path.as_uri(),
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    finally:
        # the browser's helper processes can hold the profile for a moment after exit; on Windows the
        # profile path can also exceed the 260-character limit, so delete via an extended-length path
        target = "\\\\?\\" + str(profile) if os.name == "nt" else str(profile)
        for _ in range(40):
            shutil.rmtree(target, ignore_errors=True)
            if not profile.exists():
                break
            time.sleep(0.5)
    try:
        from PIL import Image
        im = Image.open(png_path)
        # the screenshot viewport is taller than the drawing: crop to the drawing size
        im.crop((0, 0, w * scale, h * scale)).save(png_path, optimize=True)
    except ImportError:
        pass


if __name__ == "__main__":
    for name, fn in (("pipeline", pipeline), ("version-lifecycle", lifecycle)):
        svg, w, h = fn()
        svg_path = HERE / f"{name}.svg"
        svg_path.write_text(svg, encoding="utf-8")
        if "--svg-only" not in sys.argv:
            rasterize(svg_path, HERE / f"{name}.png", w, h)
        print("built", name)
