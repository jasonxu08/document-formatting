#!/usr/bin/env python3
"""Draw timeline.png: the fixed dates and the proposed plan on one calendar.

Run from any directory:   python report.assets/timeline.py
Grey items are dates and constraints stated in report.data/upgrade-notes.md. Blue items are the
plan proposed in report.md; they are proposals, not facts. Standard matplotlib only.
"""
from datetime import date, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Polygon

OUT = Path(__file__).resolve().parent / "timeline.png"
START, END = date(2026, 10, 19), date(2027, 1, 25)   # Monday of the decision week, right edge


def x(d, end_of_day=False):
    """Chart position of a date: the start of that day, or its end for deadlines and 'ends on' dates."""
    return (d - START).days + (1 if end_of_day else 0)


GREY, GREY_EDGE, GREY_TEXT = "#D0D5DD", "#98A2B3", "#344054"
BLUE, BLUE_LIGHT = "#175CD3", "#D1E0FF"
RED, RED_LIGHT = "#D92D20", "#FEE4E2"

plt.rcParams["font.family"] = ["Arial", "DejaVu Sans"]
plt.rcParams["hatch.linewidth"] = 1.0
fig, ax = plt.subplots(figsize=(9.6, 6.3), dpi=170)

# lane label -> y position (fixed constraints on top, our plan below a divider)
Y = {"Code freeze": 7.2, "v8 security support": 6.2, "Identity engineers": 5.2, "Vendor identity library": 4.2,
     "Seven services": 2.0, "v8 extended support": 1.0, "auth-service and user-store": 0.0}
H = 0.58
right_edge = x(END)


def bar(lane, x0, x1, fc, ec=None, hatch=None):
    ax.barh(Y[lane], x1 - x0, left=x0, height=H, color=fc, edgecolor=ec or fc, hatch=hatch, linewidth=0.8, zorder=3)


def text(lane, xpos, s, ha="left", color=GREY_TEXT, weight="normal", size=10.5, chip=False):
    # chip=True puts a white box behind the text so dotted lines and hatching do not run through it
    box = dict(facecolor="white", edgecolor="none", pad=2.0, alpha=0.95) if chip else None
    ax.text(xpos, Y[lane], s, ha=ha, va="center", color=color, fontsize=size, fontweight=weight, zorder=5, bbox=box)


def continues(lane, color):
    """Small arrowhead past the right edge: the bar goes on beyond the chart."""
    y = Y[lane]
    ax.add_patch(Polygon([[right_edge, y + H / 2 + 0.12], [right_edge + 2.2, y], [right_edge, y - H / 2 - 0.12]],
                         closed=True, facecolor=color, edgecolor=color, clip_on=False, zorder=3))


freeze_start, freeze_end = x(date(2026, 11, 1)), x(date(2027, 1, 5), True)
v8_end = x(date(2026, 11, 12), True)

# ---- fixed constraints (grey)
bar("Code freeze", freeze_start, freeze_end, GREY, GREY_EDGE)
text("Code freeze", (freeze_start + freeze_end) / 2, "Code freeze, only P1 hotfixes: 1 Nov to 5 Jan (66 days)", ha="center")

bar("v8 security support", x(START), v8_end, GREY, GREY_EDGE)
text("v8 security support", x(START) + 0.7, "supported")
bar("v8 security support", v8_end, right_edge, RED_LIGHT, RED, hatch="////")
continues("v8 security support", RED)
text("v8 security support", v8_end + 1.2, "no security patches unless extended support is bought",
     color="#912018", weight="bold", size=10, chip=True)

bar("Identity engineers", x(date(2026, 10, 26)), x(date(2026, 11, 13), True), GREY, GREY_EDGE)
text("Identity engineers", x(date(2026, 11, 13), True) + 1.0, "1 of 2 on leave, 26 Oct to 13 Nov", chip=True)

dx, dy = x(date(2026, 11, 30), True), Y["Vendor identity library"]
ax.add_patch(Polygon([[dx, dy + 0.3], [dx + 0.9, dy], [dx, dy - 0.3], [dx - 0.9, dy]],
                     closed=True, facecolor="white", edgecolor=GREY_TEXT, linewidth=1.4, zorder=4))
text("Vendor identity library", dx + 1.8, "IdentityModel 6.0 promised by end of Nov, not committed", chip=True)

# ---- proposed plan (blue)
bar("Seven services", x(date(2026, 10, 26)), x(date(2026, 10, 30), True), BLUE)
text("Seven services", x(date(2026, 10, 30), True) + 1.0,
     "5 working days: Data team starts Mon 26 Oct, gateway goes last", chip=True)

bar("v8 extended support", v8_end, right_edge, BLUE)
continues("v8 extended support", BLUE)
text("v8 extended support", v8_end + 1.2, "order by Thu 5 Nov, 18,000 USD per quarter, one quarter assumed",
     color="white", weight="bold", size=10)

prep0 = x(date(2026, 11, 16))
bar("auth-service and user-store", prep0, freeze_end, BLUE_LIGHT, BLUE, hatch="\\\\\\\\")
text("auth-service and user-store", (prep0 + freeze_end) / 2, "prepare in staging, no deployment",
     ha="center", color="#102A56", weight="bold", size=10, chip=True)
bar("auth-service and user-store", freeze_end, right_edge, BLUE)
continues("auth-service and user-store", BLUE)
text("auth-service and user-store", freeze_end + 1.2, "upgrade", color="white", weight="bold")

# ---- milestone lines with staggered labels (a descending staircase so labels never collide)
marks = [  # (position, label, label height, label side)
    (x(date(2026, 10, 23), True), "Decision due, Fri 23 Oct", 9.65, "right"),
    (x(date(2026, 11, 5), True), "Order extended support by Thu 5 Nov", 9.05, "right"),
    (v8_end, "v8 security support ends, Thu 12 Nov", 8.45, "right"),
    (freeze_end, "Freeze ends, Tue 5 Jan", 9.65, "left"),
]
for px, label, ytxt, side in marks:
    ax.plot([px, px], [-0.55, ytxt - 0.12], color="#667085", linestyle=(0, (2, 2)), linewidth=1.0, zorder=2)
    ax.text(px + (0.6 if side == "right" else -0.6), ytxt, label, ha="left" if side == "right" else "right",
            va="center", fontsize=10.5, fontweight="bold", color="#101828", zorder=5)

ax.axhline(3.1, color=GREY_EDGE, linewidth=0.8, zorder=1)
ax.text(right_edge - 0.4, 3.3, "FIXED BY OTHERS", ha="right", va="bottom", fontsize=9.5, color="#667085")
ax.text(right_edge - 0.4, 2.9, "PROPOSED PLAN", ha="right", va="top", fontsize=9.5, color=BLUE, fontweight="bold")

# ---- axes
ax.set_xlim(0, right_edge)
ax.set_ylim(-0.7, 10.1)
mondays = list(range(0, right_edge, 7))
ax.set_xticks(mondays)
ax.set_xticklabels([(START + timedelta(days=i)).strftime("%d %b").lstrip("0") for i in mondays], fontsize=9.5)
ax.xaxis.set_ticks_position("bottom")
ax.set_xlabel("Week starting (Mondays), 2026-27", fontsize=10, color="#475467")
ax.set_yticks(list(Y.values()))
ax.set_yticklabels(list(Y.keys()), fontsize=11, color="#101828")
ax.tick_params(axis="y", length=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.grid(axis="x", color="#EAECF0", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

ax.set_title("Only 5 working days between the decision and the freeze, and v8 support ends inside it",
             loc="left", fontsize=13, fontweight="bold", color="#101828", pad=14)

ax.legend(handles=[
    Patch(facecolor=GREY, edgecolor=GREY_EDGE, label="date or constraint from the notes"),
    Patch(facecolor=RED_LIGHT, edgecolor=RED, hatch="////", label="exposure: no security patches"),
    Patch(facecolor=BLUE, edgecolor=BLUE, label="proposed action"),
    Patch(facecolor=BLUE_LIGHT, edgecolor=BLUE, hatch="\\\\\\\\",
          label="proposed preparation (assumed allowed in the freeze)"),
], loc="upper center", bbox_to_anchor=(0.42, -0.12), ncol=2, frameon=False, fontsize=9.5)
ax.text(1.0, -0.245, "Arrowheads: the bar continues past the chart", transform=ax.transAxes, ha="right", va="top",
        fontsize=9, color="#667085")

fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
