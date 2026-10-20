"""Recomputes every number and figure quoted in report.md from the files in evidence/.

Run from any directory:  python analysis/analyze.py
Needs Python 3.9+ and matplotlib. The dependency-graph PNG also needs Graphviz (`dot`) on PATH.

Writes
  analysis/derived/incidents-by-service.csv
  analysis/derived/incidents-by-cause.csv
  analysis/derived/service-dependencies.csv
  analysis/derived/key-numbers.csv
  figures/dependency-graph.dot and .png
  figures/q3-incidents-by-service.png
  figures/timeline.png
"""
from __future__ import annotations

import csv
import re
import shutil
import statistics
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
DERIVED = ROOT / "analysis" / "derived"
FIGURES = ROOT / "figures"

# Okabe-Ito palette (colour-blind safe), shared by all figures.
GREEN, GREEN_FILL = "#009E73", "#D5EFE6"
RED, RED_FILL = "#D55E00", "#F6D5C4"
AMBER, AMBER_FILL = "#E69F00", "#FBE5B6"
SLATE, GREY, INK = "#5B6B7F", "#B8C0CC", "#1F2933"

# Dates stated in evidence/upgrade-notes.md.
FREEZE_START, FREEZE_END = date(2026, 11, 1), date(2027, 1, 5)
DECISION_DUE = date(2026, 10, 23)
PHASE1_START = date(2026, 10, 26)  # Data team: "if it starts Monday 2026-10-26"
LEAVE_START, LEAVE_END = date(2026, 10, 26), date(2026, 11, 13)
ORDER_DEADLINE = date(2026, 11, 5)  # extended support must be ordered by this date
V8_END = date(2026, 11, 12)
VENDOR_TARGET = date(2026, 11, 30)  # "by end of November", not committed

# Dates proposed by this assessment (not in the notes).
PHASE1_LAST_DAY = date(2026, 10, 30)  # last working day before the freeze
CAB_SLIP_END = date(2026, 11, 6)
CHECKPOINT = date(2026, 12, 15)
FIRST_QUARTER_END = date(2027, 2, 12)  # assumes a 3-month term starting 2026-11-12

Q3_START, Q3_END = date(2026, 7, 1), date(2026, 9, 30)
RTO_MINUTES = 240  # notes: "estimated RTO 4 hours"
CAUSED_BY = re.compile(r"\(caused by ([a-z-]+) (SEV\d)\)")


def read_csv(name: str) -> list[dict]:
    with open(EVIDENCE / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def load():
    services = read_csv("services.csv")
    incidents = []
    for row in read_csv("incidents-q3.csv"):
        row["minutes"] = int(row["duration_min"])
        row["when"] = date.fromisoformat(row["date"])
        incidents.append(row)
    return services, incidents


def validate(services, incidents) -> None:
    names = [s["service"] for s in services]
    assert len(names) == len(set(names)) == 9, "expected 9 unique services"
    for s in services:
        for dep in filter(None, s["depends_on"].split(";")):
            assert dep in names, f"{s['service']} depends on unknown service {dep}"
    for i in incidents:
        assert i["service"] in names, f"incident for unknown service {i['service']}"
        assert i["severity"] in ("SEV1", "SEV2", "SEV3"), i
        assert Q3_START <= i["when"] <= Q3_END, i


def distinct_events(incidents):
    """Drop rows that restate another logged incident ("(caused by <service> <SEV>)")."""
    for row in incidents:
        row["duplicate_of"] = None
        m = CAUSED_BY.search(row["summary"])
        if not m:
            continue
        twin = next(
            (
                o
                for o in incidents
                if o is not row
                and o["service"] == m.group(1)
                and o["when"] == row["when"]
                and o["minutes"] == row["minutes"]
                and o["severity"] == m.group(2)
            ),
            None,
        )
        if twin:
            row["duplicate_of"] = f"{twin['service']} {twin['date']}"
    events = [r for r in incidents if not r["duplicate_of"]]
    for e in events:
        # Gateway rows whose summary names auth-service as the cause of the 504s.
        e["traced_to_auth"] = e["service"] != "auth-service" and "auth-service" in e["summary"]
    return events


def dependency_maps(services):
    deps = {s["service"]: [d for d in s["depends_on"].split(";") if d] for s in services}
    dependents = defaultdict(list)
    for svc, ds in deps.items():
        for d in ds:
            dependents[d].append(svc)
    mutual = sorted(
        {tuple(sorted((a, b))) for a in deps for b in deps[a] if a in deps.get(b, [])}
    )
    return deps, dependents, mutual


def by_service(services, events):
    rows = []
    for s in services:
        mine = [e for e in events if e["service"] == s["service"]]
        own = [e for e in mine if not e["traced_to_auth"]]
        traced = [e for e in mine if e["traced_to_auth"]]
        sev = Counter(e["severity"] for e in mine)
        rows.append(
            {
                "service": s["service"],
                "owner_team": s["owner_team"],
                "criticality": s["criticality"],
                "events": len(mine),
                "minutes": sum(e["minutes"] for e in mine),
                "sev1": sev["SEV1"],
                "sev2": sev["SEV2"],
                "sev3": sev["SEV3"],
                "traced_to_auth_events": len(traced),
                "traced_to_auth_minutes": sum(e["minutes"] for e in traced),
                "own_events": len(own),
                "own_minutes": sum(e["minutes"] for e in own),
            }
        )
    total_events = sum(r["events"] for r in rows)
    total_minutes = sum(r["minutes"] for r in rows)
    for r in rows:
        r["share_of_events"] = round(100 * r["events"] / total_events, 1)
        r["share_of_minutes"] = round(100 * r["minutes"] / total_minutes, 1)
    rows.sort(key=lambda r: (-r["events"], -r["minutes"]))
    return rows


def by_cause(events):
    agg = defaultdict(lambda: {"events": 0, "minutes": 0})
    for e in events:
        agg[e["cause"]]["events"] += 1
        agg[e["cause"]]["minutes"] += e["minutes"]
    rows = [{"cause": c, **v} for c, v in agg.items()]
    rows.sort(key=lambda r: (-r["events"], -r["minutes"]))
    return rows


def key_numbers(services, incidents, events, svc_rows, cause_rows, dependents, mutual):
    s = {r["service"]: r for r in svc_rows}
    auth = s["auth-service"]
    total_events, total_minutes = len(events), sum(e["minutes"] for e in events)
    traced = [e for e in events if e["traced_to_auth"]]
    sev12 = [e for e in events if e["severity"] in ("SEV1", "SEV2")]
    rollouts = sorted(e["minutes"] for e in incidents if e["cause"] == "deploy")
    cause = {r["cause"]: r for r in cause_rows}
    q3_days = (Q3_END - Q3_START).days + 1
    leave_days = (LEAVE_END - LEAVE_START).days + 1
    monthly = Counter(e["date"][:7] for e in events)
    n = []

    def add(key, value, definition):
        n.append({"id": key, "value": value, "definition": definition})

    add("incident_rows", len(incidents), "Rows in incidents-q3.csv")
    add("incident_events", total_events, "Distinct events: rows minus rows that restate another logged incident")
    add("duplicate_rows", len(incidents) - total_events, "Rows excluded as duplicates (2026-07-11 gateway SEV1 restates the auth-service SEV1)")
    add("incident_minutes_rows", sum(i["minutes"] for i in incidents), "Sum of duration_min over all rows")
    add("incident_minutes_events", total_minutes, "Sum of duration_min over distinct events")
    add("auth_events", auth["events"], "Distinct events logged against auth-service")
    add("auth_minutes", auth["minutes"], "Minutes of those events")
    add("auth_share_of_events_pct", auth["share_of_events"], "auth_events / incident_events")
    add("auth_share_of_minutes_pct", auth["share_of_minutes"], "auth_minutes / incident_minutes_events")
    add("traced_to_auth_events", len(traced), "Non-auth events whose summary points to auth-service, e.g. 504s while auth-service was slow (all gateway)")
    add("traced_to_auth_minutes", sum(e["minutes"] for e in traced), "Minutes of those events")
    add("auth_involved_events", auth["events"] + len(traced), "auth_events + traced_to_auth_events")
    add("auth_involved_share_of_events_pct", round(100 * (auth["events"] + len(traced)) / total_events, 1), "auth_involved_events / incident_events")
    add("auth_involved_minutes", auth["minutes"] + sum(e["minutes"] for e in traced), "auth_minutes + traced_to_auth_minutes")
    add("auth_involved_share_of_minutes_pct", round(100 * (auth["minutes"] + sum(e["minutes"] for e in traced)) / total_minutes, 1), "auth_involved_minutes / incident_minutes_events")
    add("sev1_events", sum(1 for e in events if e["severity"] == "SEV1"), "Distinct SEV1 events (2 rows, 1 event)")
    add("sev1_rows", sum(1 for i in incidents if i["severity"] == "SEV1"), "SEV1 rows before de-duplication")
    add("sev1_sev2_events", len(sev12), "Distinct SEV1 + SEV2 events")
    add("sev1_sev2_auth_events", sum(1 for e in sev12 if e["service"] == "auth-service"), "Of those, logged against auth-service")
    add("longest_auth_incident_min", max(e["minutes"] for e in events if e["service"] == "auth-service"), "Longest auth-service event (2026-07-11 SEV1)")
    add("token_refresh_bug_events", cause["token-refresh-bug"]["events"], "Events with cause token-refresh-bug (all auth-service)")
    add("token_refresh_bug_minutes", cause["token-refresh-bug"]["minutes"], "Minutes of those events")
    add("runtime_gc_events", cause["runtime-gc"]["events"], "Events with cause runtime-gc")
    add("failed_rollout_events", len(rollouts), "Events with cause deploy (every summary says rolled back)")
    add("failed_rollout_min_range", f"{rollouts[0]}-{rollouts[-1]}", "Shortest-longest minutes of those events")
    add("failed_rollout_median_min", statistics.median(rollouts), "Median minutes of those events")
    add("change_related_events", cause["config"]["events"] + cause["deploy"]["events"], "Events with cause config or deploy")
    add("propagated_events", cause["dependency"]["events"] + cause["downstream-timeout"]["events"], "Events with cause dependency or downstream-timeout")
    add("q3_days", q3_days, "Days from 2026-07-01 to 2026-09-30 inclusive")
    add("auth_days_between_events", round(q3_days / auth["events"], 1), "q3_days / auth_events")
    add("leave_days", leave_days, "Days from 2026-10-26 to 2026-11-13 inclusive")
    add("auth_expected_events_in_leave", round(auth["events"] / q3_days * leave_days, 1), "Q3 auth-service rate applied to the leave window (illustration only)")
    add("rto_vs_longest_auth_incident_x", round(RTO_MINUTES / max(e["minutes"] for e in events if e["service"] == "auth-service"), 1), "240 min estimated RTO / longest auth-service event")
    add("rto_share_of_auth_q3_minutes_pct", round(100 * RTO_MINUTES / auth["minutes"]), "240 min / auth_minutes")
    add("auth_dependents", len(dependents["auth-service"]), "Services that list auth-service in depends_on")
    add("catalog_dependents", len(dependents["catalog-service"]), "Services that list catalog-service in depends_on")
    add("mutual_dependencies", "; ".join(f"{a} <-> {b}" for a, b in mutual), "Pairs that list each other in depends_on")
    add("events_jul_aug_sep", "/".join(str(monthly[m]) for m in ("2026-07", "2026-08", "2026-09")), "Distinct events per month")
    add("freeze_days_inclusive", (FREEZE_END - FREEZE_START).days + 1, "2026-11-01 to 2027-01-05 inclusive")
    return n


# ---------------------------------------------------------------- figures

def build_dot(services, deps, mutual) -> str:
    style = {
        "pass": (GREEN_FILL, GREEN),
        "fail": (RED_FILL, RED),
        "not tested": (AMBER_FILL, AMBER),
    }
    lines = [
        "digraph services {",
        '  graph [rankdir=TB, fontname="Arial", nodesep=0.5, ranksep=0.8, pad=0.25, labelloc=b, labeljust=c, label=<@@LEGEND@@>];',
        '  node [shape=box, style="rounded,filled", fontname="Arial", margin="0.16,0.09", penwidth=1.8];',
        '  edge [color="#8A94A1", arrowsize=0.8, penwidth=1.2];',
    ]
    for s in services:
        status = next(k for k in style if s["staging_result"].startswith(k))
        fill, border = style[status]
        if status == "pass":
            detail = "Passed staging, rollback yes"
        elif status == "fail":
            detail = "Failed staging (2 of 148), no rollback"
        else:
            detail = "Not tested, no rollback"
        label = (
            f'<<B>{s["service"]}</B><BR/><FONT POINT-SIZE="11">{s["owner_team"]}, {s["criticality"]}</FONT>'
            f'<BR/><FONT POINT-SIZE="11">{detail}</FONT>>'
        )
        lines.append(f'  "{s["service"]}" [label={label}, fillcolor="{fill}", color="{border}"];')
    mutual_set = {frozenset(p) for p in mutual}
    drawn = set()
    for svc, ds in deps.items():
        for d in ds:
            pair = frozenset((svc, d))
            if pair in mutual_set:
                if pair in drawn:
                    continue
                drawn.add(pair)
                a, b = sorted(pair)
                lines.append(
                    f'  "{a}" -> "{b}" [dir=both, penwidth=1.8, color="#4A5563", fontname="Arial", fontsize=11, label="  call each other"];'
                )
            elif d == "auth-service":
                lines.append(f'  "{svc}" -> "{d}" [color="{RED}", penwidth=1.6];')
            else:
                lines.append(f'  "{svc}" -> "{d}";')
    lines.append("}")
    legend = (
        '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="4" CELLPADDING="2">'
        '<TR><TD WIDTH="18" HEIGHT="14" FIXEDSIZE="TRUE" BGCOLOR="{gf}" BORDER="2" COLOR="{g}"></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="11">Passed staging, rollback in 10 to 15 minutes</FONT></TD>'
        '<TD WIDTH="18" HEIGHT="14" FIXEDSIZE="TRUE" BGCOLOR="{rf}" BORDER="2" COLOR="{r}"></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="11">Failed staging, no rollback path</FONT></TD>'
        '<TD WIDTH="18" HEIGHT="14" FIXEDSIZE="TRUE" BGCOLOR="{af}" BORDER="2" COLOR="{a}"></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="11">Not tested, no rollback path</FONT></TD></TR>'
        '<TR><TD COLSPAN="6" ALIGN="LEFT"><FONT POINT-SIZE="11">An arrow points from a service to a service it depends on. Red arrows point at auth-service.</FONT></TD></TR>'
        "</TABLE>"
    ).format(gf=GREEN_FILL, g=GREEN, rf=RED_FILL, r=RED, af=AMBER_FILL, a=AMBER)
    return "\n".join(lines).replace("@@LEGEND@@", legend)


def draw_dependency_graph(services, deps, mutual) -> None:
    dot_path = FIGURES / "dependency-graph.dot"
    dot_path.write_text(build_dot(services, deps, mutual), encoding="utf-8")
    if shutil.which("dot") is None:
        print("Graphviz `dot` not found: wrote the .dot source only")
        return
    subprocess.run(
        ["dot", "-Tpng", "-Gdpi=150", str(dot_path), "-o", str(FIGURES / "dependency-graph.png")],
        check=True,
    )


def draw_incidents(svc_rows, n_events, n_minutes) -> None:
    order = svc_rows
    ypos = list(range(len(order)))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.3), sharey=True)
    panels = (
        (axes[0], "own_events", "traced_to_auth_events", f"Incidents, Q3 2026 (n = {n_events})"),
        (axes[1], "own_minutes", "traced_to_auth_minutes", f"Incident minutes (total = {n_minutes})"),
    )
    for ax, own_key, traced_key, title in panels:
        top = max(r[own_key] + r[traced_key] for r in order)
        for y, r in zip(ypos, order):
            colour = RED if r["service"] == "auth-service" else SLATE
            ax.barh(y, r[own_key], color=colour, height=0.62)
            if r[traced_key]:
                ax.barh(y, r[traced_key], left=r[own_key], facecolor="white", edgecolor=RED, hatch="////", linewidth=1.2, height=0.62)
            total = r[own_key] + r[traced_key]
            ax.text(total + top * 0.015, y, str(total), va="center", ha="left", fontsize=11.5, color=INK)
        ax.set_title(title, fontsize=12, loc="left", color=INK)
        ax.set_xlim(0, top * 1.14)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="both", labelsize=11, length=0)
        ax.set_xticks([])
        ax.spines["bottom"].set_visible(False)
    axes[0].set_yticks(ypos)
    axes[0].set_yticklabels([r["service"] for r in order])
    axes[0].spines["left"].set_color(GREY)
    axes[1].spines["left"].set_visible(False)
    fig.legend(
        handles=[
            Patch(facecolor=RED, label="auth-service"),
            Patch(facecolor=SLATE, label="other services"),
            Patch(facecolor="white", edgecolor=RED, hatch="////", label="gateway incidents traced to auth-service"),
        ],
        loc="lower center", ncol=3, frameon=False, fontsize=10.5, bbox_to_anchor=(0.5, -0.02),
    )
    fig.text(
        0.01, -0.095,
        "36 log rows describe 35 events: the 2026-07-11 SEV1 is logged under both auth-service and gateway and is counted once, under auth-service.",
        fontsize=9, color="#52606D",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(FIGURES / "q3-incidents-by-service.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def draw_timeline() -> None:
    d = mdates.date2num
    lanes = [
        "Code freeze",
        "Phase 1: the seven\npassing services",
        "Identity engineers",
        "v8 support",
        "IdentityModel 6.0\n(vendor library)",
        "Phase 2: auth-service\nand user-store",
    ]
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    x0, x1 = date(2026, 10, 14), date(2027, 2, 22)
    ax.set_xlim(d(x0), d(x1))
    ax.set_ylim(len(lanes) - 0.4, -0.6)
    ax.set_yticks(range(len(lanes)))
    ax.set_yticklabels(lanes, fontsize=11, color=INK)

    def bar(lane, a, b, face, edge=None, hatch=None, text=None, text_colour="white", ls="-"):
        ax.barh(lane, d(b) - d(a), left=d(a), height=0.5, facecolor=face, edgecolor=edge or face, hatch=hatch, linewidth=1.3, linestyle=ls)
        if text:
            ax.text((d(a) + d(b)) / 2, lane, text, ha="center", va="center", fontsize=10, color=text_colour)

    def note(lane, x, text):
        ax.text(
            d(x), lane, text, ha="left", va="center", fontsize=10, color=INK,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5},
        )

    bar(0, FREEZE_START, FREEZE_END, SLATE, text="Only P1 hotfixes deploy")
    bar(1, PHASE1_START, PHASE1_LAST_DAY, GREEN)
    bar(1, date(2026, 11, 2), CAB_SLIP_END, "white", edge=GREEN, hatch="////")
    note(1, date(2026, 11, 9), "Mon 10-26 to Fri 10-30; slipped work needs a CAB exception")
    bar(2, LEAVE_START, LEAVE_END, "white", edge=AMBER, hatch="////")
    note(2, date(2026, 11, 16), "One of two engineers on leave until Fri 11-13")
    bar(3, x0, V8_END, GREEN_FILL, edge=GREEN, text="Security patches", text_colour=INK)
    bar(3, V8_END, FIRST_QUARTER_END, AMBER, text="Extended support, first quarter (USD 18,000)", text_colour=INK)
    bar(4, date(2026, 11, 1), VENDOR_TARGET, "white", edge=AMBER, text="?", text_colour=INK, ls=":")
    note(4, date(2026, 12, 3), "Vendor says by end of November; not committed")
    bar(5, date(2026, 11, 16), date(2027, 1, 4), "white", edge=SLATE, text="Prepare in staging, meet the gates", text_colour=INK, ls="--")
    bar(5, FREEZE_END, FIRST_QUARTER_END, GREEN, text="Upgrade window", text_colour="white")

    # Staircase of flags above the plot: each label sits to the right of its line, higher flags first.
    markers = [
        (DECISION_DUE, "10-23  Decision due", INK, 1.27),
        (ORDER_DEADLINE, "11-05  Last day to order extended support", RED, 1.19),
        (V8_END, "11-12  v8 security support ends", RED, 1.11),
        (CHECKPOINT, "12-15  Phase 2 checkpoint (proposed)", SLATE, 1.03),
    ]
    flag_transform = ax.get_xaxis_transform()
    for when, text, colour, top in markers:
        ax.plot([d(when)] * 2, [0, top], transform=flag_transform, color=colour, lw=1.1, ls="--", clip_on=False, zorder=0)
        ax.text(d(when) + 1.5, top, text, transform=flag_transform, ha="left", va="center", fontsize=10.5, color=colour)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.tick_params(axis="x", which="major", labelsize=10.5, length=5, pad=2)
    ax.tick_params(axis="x", which="minor", length=2)
    ax.tick_params(axis="y", length=0)
    for side in ("left", "right", "bottom", "top"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="#E4E7EB", lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(FIGURES / "timeline.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    services, incidents = load()
    validate(services, incidents)
    events = distinct_events(incidents)
    deps, dependents, mutual = dependency_maps(services)
    svc_rows = by_service(services, events)
    cause_rows = by_cause(events)

    write_csv(DERIVED / "incidents-by-service.csv", svc_rows)
    write_csv(DERIVED / "incidents-by-cause.csv", cause_rows)
    write_csv(
        DERIVED / "service-dependencies.csv",
        [
            {
                "service": s["service"],
                "depends_on": ";".join(deps[s["service"]]),
                "depended_on_by": ";".join(sorted(dependents[s["service"]])),
                "dependent_count": len(dependents[s["service"]]),
                "mutual_with": ";".join(b if a == s["service"] else a for a, b in mutual if s["service"] in (a, b)),
            }
            for s in services
        ],
    )
    numbers = key_numbers(services, incidents, events, svc_rows, cause_rows, dependents, mutual)
    write_csv(DERIVED / "key-numbers.csv", numbers)
    for row in numbers:
        print(f"{row['id']:38s} {row['value']}")

    draw_dependency_graph(services, deps, mutual)
    draw_incidents(svc_rows, len(events), sum(e["minutes"] for e in events))
    draw_timeline()
    print("figures written to", FIGURES.relative_to(ROOT))


if __name__ == "__main__":
    main()
