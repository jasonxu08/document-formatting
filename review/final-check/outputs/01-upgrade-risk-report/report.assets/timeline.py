"""Draws timeline.png for report.md: the dates that constrain the upgrade decision.

Every date comes from upgrade-notes.md (copy in ../report.data/); the weekdays in the labels were
checked against the calendar. Run from the folder that holds report.md:  python report.assets/timeline.py
"""
import datetime as dt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "timeline.png"
D = dt.datetime.fromisoformat  # datetimes, so that fractional-day offsets below are honoured
DAY = dt.timedelta(days=1)
AXIS_START, AXIS_END = D("2026-10-19"), D("2026-12-02")
FREEZE_START = D("2026-11-01")

GREY, AMBER, RED, DARK = "#667085", "#F79009", "#D92D20", "#475467"
INK = "#1D2939"
TXT = 11  # in-chart text size, chosen so labels still read when the image is shown 800 px wide

# (row label, kind, start, end, text, colour, text placement)
ROWS = [
    ("Decision due", "mark", D("2026-10-23"), None, "Fri 10-23: Marcus decides the plan", DARK, "right"),
    ("Data team, 4 services", "bar", D("2026-10-26"), D("2026-10-31"),
     "Mon 10-26 to Fri 10-30 (\"one week\", my reading)\nno spare working day before the freeze", AMBER, "after-freeze"),
    ("Identity team", "bar", D("2026-10-26"), D("2026-11-14"), "10-26 to 11-13: 1 of 2 on leave", GREY, "inside"),
    ("Code freeze", "bar", FREEZE_START, AXIS_END, "Sun 11-01 to Tue 2027-01-05: only P1 hotfixes", DARK, "inside"),
    ("Order extended support", "mark", D("2026-11-05"), None, "Thu 11-05: last day (18,000 USD per quarter)", DARK, "right"),
    ("v8 security support ends", "mark", D("2026-11-12"), None, "Thu 11-12: no CVE patches after this", RED, "right"),
    ("Vendor library 6.0", "promise", D("2026-11-30"), None,
     "Mon 11-30: promised \"by end of November\", not committed", DARK, "left"),
]

fig, ax = plt.subplots(figsize=(9.4, 4.8), dpi=150)
n = len(ROWS)

ax.axvspan(FREEZE_START, AXIS_END, color="#FFF4E5", zorder=0)
ax.text(FREEZE_START + DAY * 0.5, -0.62, "freeze starts", color="#B54708", fontsize=TXT, va="bottom")

for i, (label, kind, start, end, text, colour, where) in enumerate(ROWS):
    y = n - 1 - i
    if kind == "bar":
        ax.barh(y, (end - start).days, left=start, height=0.5, color=colour, zorder=2)
        if where == "inside":
            ax.text(start + DAY * 0.8, y, text, va="center", ha="left", fontsize=TXT, color="white", zorder=3)
        else:
            ax.text(FREEZE_START + DAY * 1.5, y, text, va="center", ha="left", fontsize=TXT, color=INK,
                    zorder=3, linespacing=1.25)
        continue
    ax.plot([start], [y], marker="D", markersize=10, color=colour if kind == "mark" else "white",
            markeredgecolor=colour, markeredgewidth=2, zorder=3)
    if where == "right":
        ax.text(start + DAY * 1.6, y, text, va="center", ha="left", fontsize=TXT, color=INK, zorder=3)
    else:
        ax.text(start - DAY * 1.6, y, text, va="center", ha="right", fontsize=TXT, color=INK, zorder=3)

# the freeze bar runs past the right edge of the chart (it ends on 2027-01-05)
ax.text(AXIS_END - DAY * 0.4, n - 1 - 3, "\u25b6", va="center", ha="right", fontsize=TXT, color="white", zorder=3)

ax.set_yticks(range(n))
ax.set_yticklabels([r[0] for r in reversed(ROWS)], fontsize=12)
ax.set_ylim(-0.7, n - 0.4)
ax.set_xlim(AXIS_START, AXIS_END)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
ax.tick_params(axis="x", labelsize=TXT)
ax.tick_params(axis="y", length=0)
ax.set_xlabel("Mondays of 2026 (month-day)", fontsize=TXT)
ax.grid(axis="x", color="#EAECF0", lw=0.8, zorder=0)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.set_title("Every date that matters after the Data week falls inside the freeze", loc="left",
             fontsize=14, fontweight="bold")

fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT.name)
