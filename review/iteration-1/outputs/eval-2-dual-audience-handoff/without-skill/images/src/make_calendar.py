"""Calendar strip for the exports migration handoff.

Run: python make_calendar.py   (writes ..\\calendar.png next to this folder)
All dates are computed here so the figure and the text in report.md can be re-checked.
"""
import datetime as dt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parent.parent / "calendar.png"

LEAVE_START = dt.date(2026, 10, 17)   # Saturday
LEAVE_END = dt.date(2026, 11, 6)      # Friday (last day of leave)
BACK = dt.date(2026, 11, 7)           # Saturday, "back 7 Nov"
FIRST_WORKDAY = dt.date(2026, 11, 9)  # Monday (assumption)
AGENT_START = dt.date(2026, 10, 19)   # Monday
CHECKPOINT = dt.date(2026, 10, 30)    # Friday
TARGET = dt.date(2026, 11, 10)        # Tuesday
FIRST_MONDAY = dt.date(2026, 10, 19)
WEEKS = 4

# Tuesday/Thursday DBA windows that can still be used before the target date.
dba = []
d = FIRST_MONDAY
while d < TARGET:
    if d.weekday() in (1, 3):
        dba.append(d)
    d += dt.timedelta(days=1)

TAGS = {  # date -> list of (text, face colour, text colour)
    AGENT_START: [("Agent starts", "#6b5b95", "white")],
    LEAVE_END: [("Last day\nof leave", "#5b7a99", "white")],
    BACK: [("Alex back (Sat)", "#5b7a99", "white")],
    FIRST_WORKDAY: [("Alex's first\nworking day", "#5b7a99", "white")],
    CHECKPOINT: [("Decision\ncheckpoint", "#e08a1e", "white")],
    TARGET: [("CUTOVER\nTARGET", "#c0392b", "white")],
}
for day in dba:
    TAGS.setdefault(day, []).insert(0, ("DBA window", "#1f8a8a", "white"))

fig, ax = plt.subplots(figsize=(9.2, 5.3))
HEADER = 0.42
CELL_H = 1.0
ax.set_xlim(0, 7)
ax.set_ylim(HEADER + WEEKS * CELL_H + 0.92, 0)
ax.axis("off")

for i, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
    ax.text(i + 0.5, HEADER / 2, name, ha="center", va="center", fontsize=11, fontweight="bold", color="#333333")

for w in range(WEEKS):
    for c in range(7):
        day = FIRST_MONDAY + dt.timedelta(days=7 * w + c)
        x, y = c, HEADER + w * CELL_H
        weekend = c >= 5
        on_leave = LEAVE_START <= day <= LEAVE_END
        if weekend:
            face = "#eeeeee"
        elif on_leave:
            face = "#e3eefa"
        else:
            face = "white"
        edge = "#c8c8c8"
        lw = 0.8
        if day == TARGET:
            edge, lw = "#c0392b", 3.0
        elif day == CHECKPOINT:
            edge, lw = "#e08a1e", 3.0
        ax.add_patch(Rectangle((x, y), 1, CELL_H, facecolor=face, edgecolor=edge, linewidth=lw, zorder=1 if lw < 2 else 3))
        label = day.strftime("%b %d").replace(" 0", " ") if (w == 0 and c == 0) or day.day == 1 else str(day.day)
        ax.text(x + 0.06, y + 0.09, label, ha="left", va="top", fontsize=11, fontweight="bold", color="#222222", zorder=4)

        tags = TAGS.get(day, [])
        ty = y + 0.36
        for text, fc, tc in tags:
            lines = text.count("\n") + 1
            th = 0.17 + 0.17 * lines
            ax.add_patch(
                FancyBboxPatch(
                    (x + 0.06, ty), 0.88, th - 0.04,
                    boxstyle="round,pad=0.0,rounding_size=0.04",
                    facecolor=fc, edgecolor="none", zorder=4,
                )
            )
            ax.text(x + 0.5, ty + (th - 0.04) / 2, text, ha="center", va="center", fontsize=8.6,
                    color=tc, fontweight="bold", zorder=5, linespacing=1.05)
            ty += th + 0.01

# Legend
ly = HEADER + WEEKS * CELL_H + 0.22
items = [
    ("#e3eefa", "Alex on leave (from Sat 10-17)"),
    ("#1f8a8a", "DBA window, 22:00-23:00 UTC"),
    ("#e08a1e", "Decision checkpoint"),
    ("#c0392b", "Cutover target"),
]
lx = 0.0
widths = [2.05, 2.05, 1.5, 1.4]
for (col, text), wdt in zip(items, widths):
    ax.add_patch(Rectangle((lx + 0.02, ly - 0.09), 0.18, 0.18, facecolor=col, edgecolor="#999999", linewidth=0.6))
    ax.text(lx + 0.26, ly, text, ha="left", va="center", fontsize=9, color="#333333")
    lx += wdt

ax.text(0.0, ly + 0.3, "Two DBA windows remain after the checkpoint (Tue 11-03, Thu 11-05); six working days between 10-30 and 11-10.",
        ha="left", va="center", fontsize=9, color="#333333", style="italic")
ax.text(0.0, ly + 0.58, "\"Back 7 Nov\" is a Saturday, so Mon 11-09 is assumed to be Alex's first working day. 'Agent starts' = week after Alex leaves.",
        ha="left", va="center", fontsize=9, color="#333333", style="italic")

fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
fig.savefig(OUT, dpi=130, facecolor="white")
print("wrote", OUT)
print("DBA windows shown:", [x.isoformat() for x in dba])
