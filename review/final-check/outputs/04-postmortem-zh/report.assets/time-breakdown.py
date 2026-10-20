"""Draws time-breakdown.png: where the 105 minutes of the 9 October order incident went.

Data: timeline.md (14:02 push, 14:09 alert, 15:10 rollback, 15:25 latency normal, 15:47 declared over)
and chat-log.txt (14:20 incident group created, 14:58 CFG-2231 found). Phase minutes are end minus start.
Run:  python time-breakdown.py     (needs matplotlib; Microsoft YaHei or SimHei for the Chinese labels)
Output: time-breakdown.png next to this script.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


T0 = minutes("14:00")
CAUSE_FOUND = minutes("14:58") - T0
PHASES = [
    ("1 推送 → 告警", "14:02", "14:09"),
    ("2 告警 → 拉群", "14:09", "14:20"),
    ("3 拉群 → 找到根因", "14:20", "14:58"),
    ("4 找到根因 → 回滚", "14:58", "15:10"),
    ("5 回滚 → 延迟恢复", "15:10", "15:25"),
    ("6 延迟恢复 → 宣布结束", "15:25", "15:47"),
]
RED, GREY = "#D92D20", "#98A2B3"

start, end = minutes(PHASES[0][1]) - T0, minutes(PHASES[-1][2]) - T0
before = CAUSE_FOUND - start
after = end - CAUSE_FOUND
total = end - start

fig, ax = plt.subplots(figsize=(9, 4.6), dpi=160)
ax.axvspan(start, CAUSE_FOUND, color="#FEF3F2", zorder=0)
ax.axvspan(CAUSE_FOUND, end, color="#F2F4F7", zorder=0)
for i, (name, a, b) in enumerate(PHASES):
    s, e = minutes(a) - T0, minutes(b) - T0
    ax.barh(i, e - s, left=s, height=0.58, color=RED if i < 3 else GREY, zorder=2)
    ax.text(e + 1.2, i, "%d 分钟" % (e - s), va="center", ha="left", fontsize=11,
            fontweight="bold" if i == 2 else "normal", zorder=3)

ax.axvline(CAUSE_FOUND, color="#475467", lw=1.2, ls="--", zorder=1)
ax.text(start + before / 2, -0.95, "还不知道原因：%d 分钟（%d%%）" % (before, round(before / total * 100)),
        ha="center", va="center", fontsize=11, color=RED, fontweight="bold")
ax.text(CAUSE_FOUND + after / 2, -0.95, "已知原因：%d 分钟" % after,
        ha="center", va="center", fontsize=11, color="#475467", fontweight="bold")
ax.text(CAUSE_FOUND + 1, 5.62, "14:58 找到根因 CFG-2231", fontsize=10, color="#475467", va="center")

ax.set_yticks(range(len(PHASES)))
ax.set_yticklabels([p[0] for p in PHASES], fontsize=11)
ax.set_ylim(5.9, -1.4)
ticks = list(range(0, 111, 10))
ax.set_xticks(ticks)
ax.set_xticklabels(["%d:%02d" % (14 + t // 60, t % 60) for t in ticks], fontsize=10)
ax.set_xlim(0, 118)
ax.set_xlabel("时钟时间（10 月 9 日，北京时间）", fontsize=10)
ax.set_title("找到根因之前已过去 %d 分钟，占整个故障 %d 分钟的 %d%%" % (before, total, round(before / total * 100)),
             loc="left", fontsize=13, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(axis="y", length=0)

out = Path(__file__).with_suffix(".png")
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("wrote", out.name)
