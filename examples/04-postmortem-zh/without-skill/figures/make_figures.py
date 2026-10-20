"""Regenerates the three figures used in ../report.md.

Usage: python make_figures.py   (writes PNGs next to this script)
Data comes from timeline.md, chat-log.txt and services.csv of the 10-09 incident.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parent
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DengXian"]
plt.rcParams["axes.unicode_minus"] = False

INK = "#222222"
MUTED = "#666666"


def fig_phases():
    # x axis = minutes since 14:02 (the config push)
    phases = [
        ("未被发现", 0, 7, False),
        ("响应与拉群", 7, 18, False),
        ("定位根因", 18, 56, True),
        ("决策并回滚", 56, 68, False),
        ("恢复与确认", 68, 105, True),
    ]
    events = [
        (0, "13:58 合并 CFG-2231 → 14:02 全量推送（无灰度）", 5.3, "left"),
        (7, "14:09 告警触发", 4.5, "left"),
        (18, "14:20 拉起故障群", 3.7, "left"),
        (56, "14:58 定位到 CFG-2231", 4.5, "left"),
        (68, "15:10 回滚", 3.7, "left"),
        (105, "15:47 宣布结束", 3.7, "right"),
    ]
    light, strong = "#BCCDE4", "#C0504D"

    fig = plt.figure(figsize=(9.6, 3.7), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-4, 109)
    ax.set_ylim(-0.5, 6)
    ax.axis("off")

    for name, x0, x1, hot in phases:
        ax.add_patch(
            Rectangle((x0, 1.6), x1 - x0, 1.4, facecolor=strong if hot else light,
                      edgecolor="white", linewidth=2)
        )
        ax.text((x0 + x1) / 2, 2.3, f"{name}\n{x1 - x0} 分钟", ha="center", va="center",
                fontsize=9 if x1 - x0 < 8 else 10, fontweight="bold",
                color="white" if hot else INK, linespacing=1.5)

    for x, label, level, ha in events:
        ax.plot([x, x], [3.0, level], color=MUTED, linewidth=0.9)
        ax.text(x + (0.8 if ha == "left" else -0.8), level, label, ha=ha, va="center",
                fontsize=10, color=INK)

    ax.annotate("", xy=(0, 1.05), xytext=(105, 1.05),
                arrowprops=dict(arrowstyle="<->", color=MUTED, linewidth=1))
    ax.text(52.5, 0.55, "共 105 分钟（14:02–15:47）", ha="center", va="center",
            fontsize=10, color=MUTED)
    ax.add_patch(Rectangle((0, -0.33), 2.2, 0.36, facecolor=strong, edgecolor="none"))
    ax.text(3.4, -0.15, "深色：耗时最长的两个阶段，合计 75 分钟（占 71%）", ha="left",
            va="center", fontsize=9.5, color=INK)

    fig.savefig(OUT / "fig1-phases.png", bbox_inches="tight", pad_inches=0.15,
                facecolor="white")
    plt.close(fig)


def node(ax, cx, cy, name, sub, status, fc, ec, status_color, w=2.0, h=1.1):
    ax.add_patch(
        FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                       facecolor=fc, edgecolor=ec, linewidth=1.6, zorder=3)
    )
    name_dy, sub_dy = (0.32, 0.02) if status else (0.13, -0.2)
    ax.text(cx, cy + name_dy, name, ha="center", va="center", fontsize=12.5, fontweight="bold",
            color=INK, zorder=4)
    ax.text(cx, cy + sub_dy, sub, ha="center", va="center", fontsize=8.8, color=MUTED, zorder=4)
    if status:
        ax.text(cx, cy - 0.32, status, ha="center", va="center", fontsize=9.5, fontweight="bold",
                color=status_color, zorder=4)


def arrow(ax, start, end, color, style="-", width=1.5, rad=0.0, zorder=5):
    ax.annotate(
        "", xy=end, xytext=start, zorder=zorder,
        arrowprops=dict(arrowstyle="-|>", color=color, linewidth=width, linestyle=style,
                        shrinkA=0, shrinkB=0, mutation_scale=14,
                        connectionstyle=f"arc3,rad={rad}"),
    )


def fig_propagation():
    # data units are inches: the axes fill the whole figure
    fig = plt.figure(figsize=(10.7, 6.8), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 10.7)
    ax.set_ylim(-0.45, 6.35)
    ax.axis("off")

    grey_fc, grey_ec = "#F1F1F1", "#9A9A9A"
    red_fc, red_ec = "#F4CCCC", "#C0392B"
    org_fc, org_ec = "#FCE5CD", "#E67E22"
    blue_fc, blue_ec = "#D9E7F7", "#2F6DB5"
    call, push, retry = "#555555", "#2F6DB5", "#C0392B"

    gx, ox, px, nx = 1.15, 3.95, 6.75, 9.55
    row_a, row_b, row_c, row_cfg = 3.9, 2.0, 0.25, 5.7
    ux, ix, cx = 2.2, 5.7, 3.95
    w, h = 2.0, 1.1

    node(ax, ox, row_cfg, "配置中心", "config-center · 平台组", "CFG-2231 全量推送", blue_fc, blue_ec, push)
    node(ax, gx, row_a, "网关", "gateway · 平台组", "5xx 上升（订单接口）", org_fc, org_ec, "#B35C00")
    node(ax, ox, row_a, "订单服务", "order-service · 交易组", "连接池上限 200 → 20", red_fc, red_ec, retry)
    node(ax, px, row_a, "支付服务", "payment-service · 交易组", "CPU > 90%", org_fc, org_ec, "#B35C00")
    node(ax, nx, row_a, "通知服务", "notification-service · 平台组", "", grey_fc, grey_ec, MUTED)
    node(ax, ux, row_b, "用户服务", "user-service · 账号组", "", grey_fc, grey_ec, MUTED)
    node(ax, ix, row_b, "库存服务", "inventory-service · 交易组", "", grey_fc, grey_ec, MUTED)
    node(ax, cx, row_c, "缓存", "cache · 平台组", "", grey_fc, grey_ec, MUTED)

    top = h / 2 + 0.07
    # config push (config-center -> gateway / order / payment)
    for tx in (gx, ox, px):
        arrow(ax, (ox + (tx - ox) * 0.25, row_cfg - top), (tx, row_a + top), push, width=2.0)
    ax.text(1.3, 5.3, "14:02 一次性推送\n没有灰度", ha="center", va="center", fontsize=9.5,
            color=push, fontweight="bold")

    # calls listed in services.csv
    arrow(ax, (gx + w / 2 + 0.07, row_a), (ox - w / 2 - 0.07, row_a), call)
    arrow(ax, (ox + w / 2 + 0.07, row_a + 0.2), (px - w / 2 - 0.07, row_a + 0.2), call)
    arrow(ax, (px + w / 2 + 0.07, row_a), (nx - w / 2 - 0.07, row_a), call)
    arrow(ax, (gx + 0.3, row_a - top), (ux - 0.3, row_b + top), call)
    arrow(ax, (ox - 0.3, row_a - top), (ux + 0.5, row_b + top), call)
    arrow(ax, (ox + 0.3, row_a - top), (ix - 0.5, row_b + top), call)
    arrow(ax, (ux + 0.3, row_b - top), (cx - 0.5, row_c + top), call)
    arrow(ax, (ix - 0.3, row_b - top), (cx + 0.5, row_c + top), call)

    # retry storm: payment -> order, not listed in services.csv
    arrow(ax, (px - w / 2 - 0.07, row_a - 0.2), (ox + w / 2 + 0.07, row_a - 0.2), retry,
          style=(0, (4, 2)), width=2.0)
    ax.text((ox + px) / 2, row_a - 0.55, "重试风暴 *", ha="center", va="center", fontsize=9.5,
            color=retry, fontweight="bold")

    # legend
    lx, step = 7.5, 0.34
    ax.text(lx, 3.0, "图例", fontsize=9.5, fontweight="bold", color=INK, va="center")
    items = [
        ("box", red_fc, red_ec, "直接故障：线程排队等连接"),
        ("box", org_fc, org_ec, "被牵连：5xx 或 CPU 过高"),
        ("box", blue_fc, blue_ec, "变更来源"),
        ("box", grey_fc, grey_ec, "资料未提及受影响"),
        ("line", call, "-", "调用关系（services.csv）"),
        ("line", push, "-", "配置推送"),
        ("line", retry, (0, (4, 2)), "重试（* 服务清单未列出此方向）"),
    ]
    for i, (kind, a, b, text) in enumerate(items):
        y = 2.65 - i * step
        if kind == "box":
            ax.add_patch(Rectangle((lx, y - 0.11), 0.3, 0.22, facecolor=a, edgecolor=b, linewidth=1.2))
        else:
            ax.plot([lx, lx + 0.3], [y, y], color=a, linestyle=b, linewidth=2)
        ax.text(lx + 0.42, y, text, fontsize=9, va="center", color=INK)

    fig.savefig(OUT / "fig2-propagation.png", bbox_inches="tight", pad_inches=0.15,
                facecolor="white")
    plt.close(fig)


def fig_budget():
    effort = {"A4": 0.5, "A3": 0.5, "A6": 1, "A1": 3, "A5": 4, "A2": 8}
    batch = {"A4": 0, "A3": 0, "A6": 0, "A1": 1, "A5": 1, "A2": 2}
    palette = ["#6FA8DC", "#76A5AF", "#E69138"]
    rows = [
        ("全部 6 项", ["A4", "A3", "A6", "A1", "A5", "A2"], "17 人天，超出 7"),
        ("方案一（建议）", ["A4", "A3", "A6", "A1", "A5"], "9 人天，余 1"),
        ("方案二", ["A4", "A3", "A6", "A2"], "10 人天，无余量"),
    ]

    fig, ax = plt.subplots(figsize=(9.8, 3.5), dpi=200)
    fig.subplots_adjust(left=0.15, right=0.985, top=0.9, bottom=0.3)
    for i, (label, ids, note) in enumerate(rows):
        y = len(rows) - 1 - i
        left = 0
        for item in ids:
            ax.barh(y, effort[item], left=left, height=0.58, color=palette[batch[item]],
                    edgecolor="white", linewidth=1.5)
            ax.text(left + effort[item] / 2, y, item, ha="center", va="center",
                    fontsize=8 if effort[item] < 1 else 10, fontweight="bold", color=INK)
            left += effort[item]
        ax.text(max(left, 10) + 0.4, y, note, ha="left", va="center", fontsize=10, color=INK)

    ax.axvline(10, color="#C0392B", linestyle=(0, (4, 3)), linewidth=1.6)
    ax.text(10, len(rows) - 0.4, "下个迭代约 10 人天", ha="center", va="bottom", fontsize=10,
            color="#C0392B", fontweight="bold")

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in reversed(rows)], fontsize=10.5)
    ax.set_xlim(0, 21)
    ax.set_ylim(-0.6, len(rows) - 0.2)
    ax.set_xticks(range(0, 19, 2))
    ax.tick_params(axis="x", labelsize=9, colors=MUTED)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("累计人天", fontsize=9.5, color=MUTED)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#BBBBBB")

    handles = [Rectangle((0, 0), 1, 1, color=c) for c in palette]
    ax.legend(handles, ["A4、A3、A6（合计 2 人天）", "A1、A5（合计 7 人天）", "A2（8 人天）"],
              loc="upper center", bbox_to_anchor=(0.45, -0.28), ncol=3, frameon=False, fontsize=9.5)

    fig.savefig(OUT / "fig3-budget.png", bbox_inches="tight", pad_inches=0.15,
                facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig_phases()
    fig_propagation()
    fig_budget()
