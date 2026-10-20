"""Incident statistics and chart for report.md, section 3.

Run from the folder that contains report.md:
    python report.assets/incidents.py
Reads report.data/incidents-q3.csv, prints the per-service statistics (they are reproduced in
report.evidence.md) and writes report.assets/incidents.png.
"""
import collections
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE.parent / "report.data" / "incidents-q3.csv"
PNG_PATH = HERE / "incidents.png"
FOCUS = "auth-service"
SEVERE = ("SEV1", "SEV2")

with open(CSV_PATH, encoding="utf-8", newline="") as fh:
    rows = list(csv.DictReader(fh))

per = collections.defaultdict(lambda: {"severe": 0, "sev3": 0, "minutes": 0})
for r in rows:
    d = per[r["service"]]
    d["severe" if r["severity"] in SEVERE else "sev3"] += 1
    d["minutes"] += int(r["duration_min"])

order = sorted(per, key=lambda s: (-(per[s]["severe"] + per[s]["sev3"]), s))

print("service            records  sev1/2  sev3  minutes")
for s in order:
    d = per[s]
    print(f"{s:18} {d['severe'] + d['sev3']:7} {d['severe']:7} {d['sev3']:5} {d['minutes']:8}")
print(f"{'total':18} {len(rows):7} {sum(d['severe'] for d in per.values()):7} "
      f"{sum(d['sev3'] for d in per.values()):5} {sum(d['minutes'] for d in per.values()):8}")

total_focus = per[FOCUS]["severe"] + per[FOCUS]["sev3"]
fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=160)
ypos = list(range(len(order)))[::-1]
for y, s in zip(ypos, order):
    severe, sev3 = per[s]["severe"], per[s]["sev3"]
    dark, light = ("#B42318", "#FDA29B") if s == FOCUS else ("#475467", "#D0D5DD")
    ax.barh(y, severe, color=dark, height=0.62)
    ax.barh(y, sev3, left=severe, color=light, height=0.62)
    label = str(severe + sev3) + (f"  ({severe} SEV1 or SEV2)" if severe else "")
    ax.text(severe + sev3 + 0.2, y, label, va="center", fontsize=11,
            fontweight="bold" if s == FOCUS else "normal", color="#101828")

ax.set_yticks(ypos)
ax.set_yticklabels(order, fontsize=12)
for tick in ax.get_yticklabels():
    if tick.get_text() == FOCUS:
        tick.set_fontweight("bold")
ax.set_xlim(0, 16)
ax.set_xticks(range(0, 13, 2))
ax.tick_params(axis="x", labelsize=11)
ax.set_xlabel("Incident records in Q3 2026 (count)", fontsize=12)
ax.set_title(f"{FOCUS} had {total_focus} of Q3's {len(rows)} incident records, the most of any service",
             loc="left", fontsize=13, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(handles=[Patch(color="#475467", label="SEV1 or SEV2 (darker)"),
                   Patch(color="#D0D5DD", label="SEV3 (lighter)")],
          loc="lower right", frameon=False, fontsize=11)
fig.text(0.0, -0.03, "The gateway's SEV1 on 2026-07-11 is the same event as auth-service's SEV1; "
         "both bars include it.", fontsize=10.5, color="#475467")
fig.savefig(PNG_PATH, bbox_inches="tight")
print("wrote", PNG_PATH.name)
