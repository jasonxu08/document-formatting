"""Timeline of the constraints around the v8 to v10 decision, for report.md section 5.

Every date comes from report.data/upgrade-notes.md; the weekdays are calendar facts.
Solid bars are facts from the notes. The dashed box (gateway) is a proposal: its length is not in the notes.
Run from the folder that contains report.md:
    python report.assets/timeline.py
"""
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

PNG_PATH = Path(__file__).resolve().parent / "timeline.png"


def d(month, day, year=2026):
    return mdates.date2num(date(year, month, day))


X0, X1 = d(10, 18), d(12, 10)
YMIN, YMAX = -0.8, 7.3
FREEZE_START = d(11, 1)          # notes: freeze runs 2026-11-01 to 2027-01-05
V8_END = d(11, 12)               # notes: v8 security support ends 2026-11-12
SUPPORT_ORDER_BY = d(11, 5)      # notes: extended support must be ordered by 2026-11-05
DECISION = d(10, 23)             # notes: decision needed by Friday 2026-10-23
DATA_START, DATA_END = d(10, 26), d(10, 31)    # notes: one week from Monday 2026-10-26 (to end of Friday 10-30)
LEAVE_START, LEAVE_END = d(10, 26), d(11, 14)  # notes: leave 2026-10-26 to 2026-11-13 (inclusive)
VENDOR = d(11, 30)               # notes: vendor library "by end of November", not committed
BAND_TOP = 5.0

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=130)
FS = 12.5  # base font size: keeps labels readable when the image is shown about 800 px wide
ax.set_xlim(X0, X1)
ax.set_ylim(YMIN, YMAX)
BAND = "#EAECF0"

# freeze band behind the lanes
ax.add_patch(Rectangle((FREEZE_START, YMIN + 0.25), X1 - FREEZE_START, BAND_TOP - YMIN - 0.25,
                       facecolor=BAND, edgecolor="none", zorder=0))
ax.text(FREEZE_START + 0.4, BAND_TOP - 0.12, "Code freeze: P1 hotfixes only (Sun Nov 1 to Jan 5, 2027)",
        ha="left", va="top", fontsize=FS, color="#101828", fontweight="bold", zorder=3)

lanes = {"v8 security support": 3.7, "Data team: 4 services": 2.7, "Platform: gateway (last)": 1.7,
         "Identity team": 0.7, "Vendor library 6.0\n(date not committed)": -0.3}
H = 0.52


def box(y, x0, x1, color, text=None, **kw):
    ax.add_patch(Rectangle((x0, y - H / 2), x1 - x0, H, facecolor=color, edgecolor=kw.get("edge", "none"),
                           hatch=kw.get("hatch"), linestyle=kw.get("ls", "-"), linewidth=kw.get("lw", 1), zorder=2))
    if text:
        ax.text((x0 + x1) / 2, y, text, ha="center", va="center", fontsize=FS, color="#101828", zorder=4)


def note(x, y, text, ha="left", bg=BAND):
    ax.text(x, y, text, ha=ha, va="center", fontsize=FS, color="#101828", zorder=4,
            bbox=dict(facecolor=bg, edgecolor="none", pad=1.5))


# lane 1: v8 support cliff
box(3.7, X0, V8_END, "#ABEFC6", "security patches")
box(3.7, V8_END, X1, "#FDA29B", "no CVE patches without extended support")
# lane 2: Data team week, then the note on slack
box(2.7, DATA_START, DATA_END, "#84CAFF")
note(FREEZE_START + 0.6, 2.7, "ends Fri Oct 30, the last working day before the freeze")
# lane 3: gateway after the Data wave (proposal, dashed)
box(1.7, d(10, 30), d(11, 3), "#FFFFFF", hatch="///", edge="#475467", ls="--", lw=1.4)
note(d(11, 3) + 0.6, 1.7, "goes last: Fri Oct 30 at best, else a CAB exception")
# lane 4: Identity capacity
box(0.7, LEAVE_START, LEAVE_END, "#FEC84B", "1 of 2 engineers on leave")
# lane 5: vendor library
ax.plot([VENDOR], [-0.3], marker="D", markersize=11, markerfacecolor="white", markeredgecolor="#344054",
        markeredgewidth=2, zorder=4)
note(VENDOR - 0.9, -0.3, "promised \"by end of November\"", ha="right")

# vertical markers: later dates get lower labels, so no line crosses another label
marks = [
    (DECISION, "Decision due\nFri Oct 23", ":", "#101828", 5.55),
    (SUPPORT_ORDER_BY, "Last day to order extended support\nThu Nov 5", "--", "#344054", 6.35),
    (V8_END, "v8 support ends\nThu Nov 12", "--", "#B42318", 5.55),
]
for x, label, ls, color, ytxt in marks:
    ax.plot([x, x], [YMIN + 0.25, ytxt - 0.08], linestyle=ls, color=color, linewidth=1.6, zorder=1)
    ax.text(x + 0.25, ytxt, label, ha="left", va="bottom", fontsize=FS, color=color, fontweight="bold", zorder=4)
ax.plot([FREEZE_START] * 2, [YMIN + 0.25, BAND_TOP], color="#101828", linewidth=2, zorder=1)

ax.set_yticks(list(lanes.values()))
ax.set_yticklabels(list(lanes.keys()), fontsize=FS + 1)
ax.tick_params(axis="y", length=0)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.tick_params(axis="x", labelsize=FS)
ax.set_xlabel("2026 (ticks are Mondays)", fontsize=FS)
ax.grid(axis="x", color="#EAECF0", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.set_title("Data's week ends on the last working day before the freeze; v8 support ends a week later",
             loc="left", fontsize=13, fontweight="bold", pad=10)
ax.legend(handles=[Patch(facecolor=BAND, label="Code freeze"),
                   Patch(facecolor="white", edgecolor="#475467", hatch="///", linestyle="--",
                         label="Proposal (length not in the notes)")],
          loc="upper left", bbox_to_anchor=(0.0, -0.13), ncol=2, frameon=False, fontsize=FS)
fig.savefig(PNG_PATH, bbox_inches="tight")
print("wrote", PNG_PATH.name)
