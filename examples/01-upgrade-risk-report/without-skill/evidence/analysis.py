"""Recompute every derived number and the dependency diagram used in ../report.md.

    python evidence/analysis.py

Reads    evidence/source/services.csv and evidence/source/incidents-q3.csv
Checks   the three source files against evidence/SHA256SUMS.txt
Writes   evidence/derived/*.csv
         figures/dependency-map.dot   (always)
         figures/dependency-map.png   (only if Graphviz `dot` is installed)
Needs    Python 3.9+, standard library only. Nothing outside evidence/derived and figures is touched.

Classification rules that rely on the free-text `summary` column (kept deliberately simple):
  * failed rollout            -> summary contains "rolled back"
  * gateway row citing auth   -> service == "gateway" and summary contains "auth-service"
  * overlapping rows          -> same date, severity and duration, and one summary names the other row's service
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
DERIVED = HERE / "derived"
FIGURES = HERE.parent / "figures"

# Values quoted from source/upgrade-notes.md (they are inputs, not computed from the CSVs).
EOL_V8 = dt.date(2026, 11, 12)               # Context: v8 end of security support
FREEZE_START = dt.date(2026, 11, 1)          # Context: code freeze starts
FREEZE_END = dt.date(2027, 1, 5)             # Context: code freeze ends
DECISION_DUE = dt.date(2026, 10, 23)         # header: decision needed by Friday
DATA_TEAM_START = dt.date(2026, 10, 26)      # Costs and options: Data team "if it starts Monday"
LAST_PRE_FREEZE_WORKDAY = dt.date(2026, 10, 30)  # derived: last Mon-Fri day before the freeze
IDENTITY_LEAVE = (dt.date(2026, 10, 26), dt.date(2026, 11, 13))  # Costs and options
EXT_SUPPORT_ORDER_BY = dt.date(2026, 11, 5)  # Costs and options
EXT_SUPPORT_USD_PER_QUARTER = 18_000         # Costs and options
RTO_MINUTES = 4 * 60                         # Rollback: "estimated RTO 4 hours"
VENDOR_LIB_PROMISE = dt.date(2026, 11, 30)   # Context: IdentityModel 6.0 "by end of November", not committed
CHECKPOINT = dt.date(2026, 12, 15)           # proposed in report.md (not from the notes)
Q3 = (dt.date(2026, 7, 1), dt.date(2026, 9, 30))


# ----------------------------------------------------------------------------- helpers
def read_csv(name: str) -> list[dict]:
    with (SOURCE / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(name: str, fields: list[str], rows: list[dict]) -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    with (DERIVED / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def workdays(a: dt.date, b: dt.date) -> int:
    """Mon-Fri days from a to b, both inclusive."""
    return sum(1 for i in range((b - a).days + 1) if (a + dt.timedelta(days=i)).weekday() < 5)


def add_months(d: dt.date, n: int) -> dt.date:
    m = d.month - 1 + n
    return d.replace(year=d.year + m // 12, month=m % 12 + 1)


def staging_state(text: str) -> str:
    t = text.lower()
    return "pass" if t.startswith("pass") else "fail" if t.startswith("fail") else "not tested"


def verify_checksums() -> bool:
    ok = True
    for line in (HERE / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split(None, 1)
        actual = hashlib.sha256((HERE / rel.strip()).read_bytes()).hexdigest()
        good = actual == expected
        ok &= good
        print(f"  {'OK      ' if good else 'MISMATCH'}  {rel.strip()}")
    if not ok:
        print("  (If this follows a git checkout, check line-ending conversion, e.g. core.autocrlf.)")
    return ok


# ----------------------------------------------------------------------------- dependencies
def analyse_dependencies(services: list[dict]) -> dict:
    names = [s["service"] for s in services]
    deps = {s["service"]: [d for d in s["depends_on"].split(";") if d] for s in services}
    callers = {n: [m for m in names if n in deps[m]] for n in names}

    def reachable(start: str) -> set[str]:
        seen, todo = set(), list(deps[start])
        while todo:
            n = todo.pop()
            if n not in seen:
                seen.add(n)
                todo.extend(deps[n])
        return seen

    reach = {n: reachable(n) for n in names}
    transitive = {n: sorted(m for m in names if m != n and n in reach[m]) for n in names}
    cycle_with = {n: sorted(m for m in reach[n] if m != n and n in reach[m]) for n in names}
    return {"names": names, "deps": deps, "callers": callers, "transitive": transitive, "cycle_with": cycle_with}


def dependency_rows(services: list[dict], d: dict) -> list[dict]:
    rows = []
    for s in services:
        n = s["service"]
        rows.append({
            "service": n,
            "owner_team": s["owner_team"],
            "criticality": s["criticality"],
            "staging_state": staging_state(s["staging_result"]),
            "rollback_path": s["rollback_path"],
            "depends_on_count": len(d["deps"][n]),
            "depends_on": ";".join(d["deps"][n]),
            "direct_dependents_count": len(d["callers"][n]),
            "direct_dependents": ";".join(d["callers"][n]),
            "transitive_dependents_count": len(d["transitive"][n]),
            "in_cycle_with": ";".join(d["cycle_with"][n]),
        })
    return rows


# ----------------------------------------------------------------------------- incidents
def sev_counts(rows: list[dict]) -> tuple[int, int, int]:
    c = Counter(r["severity"] for r in rows)
    return c["SEV1"], c["SEV2"], c["SEV3"]


def minutes(rows: list[dict]) -> int:
    return sum(r["duration_min"] for r in rows)


def overlapping_groups(rows: list[dict]) -> list[list[dict]]:
    groups = defaultdict(list)
    for r in rows:
        groups[(r["date"], r["severity"], r["duration_min"])].append(r)
    return [g for g in groups.values()
            if len(g) > 1 and any(a["service"] in b["summary"] for a in g for b in g if a is not b)]


def incident_tables(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    by_service, by_cause = defaultdict(list), defaultdict(list)
    for r in rows:
        by_service[r["service"]].append(r)
        by_cause[r["cause"]].append(r)

    svc_out = []
    for name, rs in sorted(by_service.items(), key=lambda kv: (-minutes(kv[1]), kv[0])):
        s1, s2, s3 = sev_counts(rs)
        causes = Counter(r["cause"] for r in rs)
        svc_out.append({
            "service": name, "incidents": len(rs), "total_minutes": minutes(rs),
            "sev1": s1, "sev2": s2, "sev3": s3,
            "longest_minutes": max(r["duration_min"] for r in rs),
            "causes": "; ".join(f"{c} x{k}" for c, k in sorted(causes.items(), key=lambda kv: (-kv[1], kv[0]))),
        })

    cause_out = []
    for name, rs in sorted(by_cause.items(), key=lambda kv: (-minutes(kv[1]), kv[0])):
        s1, s2, s3 = sev_counts(rs)
        cause_out.append({
            "cause": name, "incidents": len(rs), "total_minutes": minutes(rs),
            "sev1": s1, "sev2": s2, "sev3": s3,
            "services": "; ".join(sorted({r["service"] for r in rs})),
        })
    return svc_out, cause_out


# ----------------------------------------------------------------------------- key figures and dates
def key_dates() -> list[dict]:
    items = [
        (dt.date(2026, 10, 14), "Platform team notes written", "upgrade-notes.md, header"),
        (DECISION_DUE, "Decision due from the Engineering Lead", "upgrade-notes.md, header"),
        (DATA_TEAM_START, "Earliest start for the Data team (four services, about one week); one Identity engineer's leave begins", "upgrade-notes.md, Costs and options"),
        (LAST_PRE_FREEZE_WORKDAY, "Last working day before the code freeze", "derived (Mon-Fri before 2026-11-01)"),
        (FREEZE_START, "Code freeze starts (only P1 hotfixes; otherwise CAB exception)", "upgrade-notes.md, Context"),
        (EXT_SUPPORT_ORDER_BY, "Last day to order v8 extended support", "upgrade-notes.md, Costs and options"),
        (EOL_V8, "v8 end of security support", "upgrade-notes.md, Context"),
        (IDENTITY_LEAVE[1], "End of the Identity engineer's leave", "upgrade-notes.md, Costs and options"),
        (VENDOR_LIB_PROMISE, "IdentityModel 6.0 promised 'by end of November' (not committed)", "upgrade-notes.md, breaking change 3"),
        (CHECKPOINT, "Proposed checkpoint on January readiness (vendor library, failing tests, user-store staging)", "proposed in report.md, section 4.4"),
        (FREEZE_END, "Code freeze ends", "upgrade-notes.md, Context"),
    ]
    return [{"date": d.isoformat(), "weekday": d.strftime("%A"), "event": e, "source": s} for d, e, s in items]


def key_figures(services, dep, incidents) -> list[dict]:
    F: list[dict] = []

    def add(fid, label, value, unit, how):
        F.append({"id": fid, "figure": label, "value": value, "unit": unit, "how_computed": how})

    names, callers, transitive = dep["names"], dep["callers"], dep["transitive"]
    others = len(names) - 1
    hub = max(names, key=lambda n: len(callers[n]))
    base = max(names, key=lambda n: len(transitive[n]))
    second_hub = sorted(names, key=lambda n: (-len(callers[n]), n))[1]

    # Calendar
    add("T1", "Days between v8 end of support and the end of the freeze", (FREEZE_END - EOL_V8).days, "days",
        "2027-01-05 minus 2026-11-12")
    add("T2", "Working days for the Data team from Mon 2026-10-26 to the last pre-freeze working day",
        workdays(DATA_TEAM_START, LAST_PRE_FREEZE_WORKDAY), "working days", "Mon-Fri days, 2026-10-26 to 2026-10-30 inclusive")
    add("T3", "Length of the Identity engineer's leave", (IDENTITY_LEAVE[1] - IDENTITY_LEAVE[0]).days + 1, "calendar days",
        "2026-10-26 to 2026-11-13 inclusive")
    add("T4", "Length of the Identity engineer's leave", workdays(*IDENTITY_LEAVE), "working days",
        "Mon-Fri days, 2026-10-26 to 2026-11-13 inclusive")
    add("T5", "Length of the code freeze", (FREEZE_END - FREEZE_START).days, "days", "2027-01-05 minus 2026-11-01")
    add("T6", "End of a 3-month extended-support term activated on 2026-11-12 (assumption: term runs from activation)",
        add_months(EOL_V8, 3).isoformat(), "date", "2026-11-12 plus 3 months")
    add("T7", "Days from the last pre-freeze working day to the end of the freeze (minimum v8/v10 mixed running)",
        (FREEZE_END - LAST_PRE_FREEZE_WORKDAY).days, "days", "2027-01-05 minus 2026-10-30")

    # Dependencies
    add("D1", f"Services that call {hub} directly", len(callers[hub]), f"of {others} other services",
        ", ".join(callers[hub]))
    add("D2", f"Services that depend on {base} directly or indirectly", len(transitive[base]), f"of {others} other services",
        "transitive closure of depends_on; not dependent: " + ", ".join(sorted(set(names) - set(transitive[base]) - {base})))
    add("D3", f"Direct dependents of {second_hub}", len(callers[second_hub]), "services", ", ".join(callers[second_hub]))
    pairs = sorted({tuple(sorted((n, m))) for n in names for m in dep["cycle_with"][n]})
    add("D4", "Circular dependencies", len(pairs), "pairs", "; ".join(f"{a} <-> {b}" for a, b in pairs))
    ready = [s["service"] for s in services if staging_state(s["staging_result"]) == "pass"]
    add("D5", "Services that passed staging", len(ready), f"of {len(names)}", ", ".join(ready))

    # Incidents
    by_service = defaultdict(list)
    for r in incidents:
        by_service[r["service"]].append(r)
    overlaps = overlapping_groups(incidents)
    dup_rows = sum(len(g) - 1 for g in overlaps)
    dup_minutes = sum(minutes(g[1:]) for g in overlaps)
    s1, s2, s3 = sev_counts(incidents)
    add("I1", "Incident rows in the Q3 log", len(incidents), "rows", f"{min(r['date'] for r in incidents)} to {max(r['date'] for r in incidents)}")
    add("I2", "Distinct incident events", len(incidents) - dup_rows, "events",
        "rows minus overlapping rows: " + "; ".join(f"{g[0]['date']} {' + '.join(r['service'] for r in g)}" for g in overlaps))
    add("I3", "Logged incident minutes (sum of rows)", minutes(incidents), "minutes", "sum of duration_min")
    add("I4", "Logged incident minutes counting overlapping events once", minutes(incidents) - dup_minutes, "minutes", "I3 minus duplicated rows")
    add("I5", "Severity mix, by row", f"SEV1 {s1} / SEV2 {s2} / SEV3 {s3}", "rows", "count of severity (the 2 SEV1 rows are one event)")
    a = by_service["auth-service"]
    a1, a2, a3 = sev_counts(a)
    add("I6", "auth-service incidents", len(a), "rows", f"SEV1 {a1} / SEV2 {a2} / SEV3 {a3}")
    add("I7", "auth-service share of incident rows", round(100 * len(a) / len(incidents), 1), "%", f"{len(a)} / {len(incidents)}")
    add("I8", "auth-service incident minutes", minutes(a), "minutes", "sum of duration_min")
    add("I9", "auth-service share of logged minutes", round(100 * minutes(a) / minutes(incidents), 1), "%",
        f"{minutes(a)} / {minutes(incidents)} (about {round(100 * minutes(a) / (minutes(incidents) - dup_minutes))}% if the overlap is counted once)")
    all_sev2 = [r for r in incidents if r["severity"] == "SEV2"]
    add("I10", "auth-service SEV2 rows as a share of all SEV2 rows", f"{a2} of {len(all_sev2)}", "rows", "severity == SEV2")
    gw = by_service["gateway"]
    gw_auth = [r for r in gw if "auth-service" in r["summary"]]
    gw_auth_ex = [r for r in gw_auth if not any(r in g for g in overlaps)]
    add("I11", "gateway incidents whose summary cites auth-service", f"{len(gw_auth)} of {len(gw)}", "rows",
        f"{minutes(gw_auth)} min in total; {len(gw_auth_ex)} rows / {minutes(gw_auth_ex)} min excluding the overlapping 07-11 row")
    gw_dt = [r for r in gw if r["cause"] == "downstream-timeout"]
    add("I12", "gateway incidents caused by downstream timeouts", f"{len(gw_dt)} of {len(gw)}", "rows", "cause == downstream-timeout")
    tr = [r for r in incidents if r["cause"] == "token-refresh-bug"]
    add("I13", "token-refresh-bug incidents", len(tr), "rows", f"{minutes(tr)} min; services: {', '.join(sorted({r['service'] for r in tr}))}")
    gc = [r for r in incidents if r["cause"] == "runtime-gc"]
    add("I14", "runtime-gc incidents", len(gc), "rows", f"{minutes(gc)} min; services: {', '.join(sorted({r['service'] for r in gc}))}")
    casc = [r for r in incidents if r["cause"] in ("dependency", "downstream-timeout")]
    add("I15", "Dependency or downstream-timeout incidents", len(casc), "rows",
        f"{minutes(casc)} min; {round(100 * len(casc) / len(incidents))}% of rows")
    rb = [r for r in incidents if "rolled back" in r["summary"]]
    add("I16", "Failed rollouts that were rolled back", len(rb), "rows",
        f"duration {min(r['duration_min'] for r in rb)}-{max(r['duration_min'] for r in rb)} min, median {median(r['duration_min'] for r in rb):g}; "
        f"severities {', '.join(sorted({r['severity'] for r in rb}))}; "
        + ", ".join(f"{k} x{v}" for k, v in sorted(Counter(r['service'] for r in rb).items(), key=lambda kv: (-kv[1], kv[0]))))
    q3_days = (Q3[1] - Q3[0]).days + 1
    window = (IDENTITY_LEAVE[1] - IDENTITY_LEAVE[0]).days + 1
    add("I17", "auth-service incident rate in Q3", round(len(a) / q3_days, 3), "incidents per day", f"{len(a)} rows / {q3_days} days (2026-07-01 to 2026-09-30)")
    add("I18", "auth-service incidents expected in a window as long as the leave, at the Q3 rate (illustration, not a forecast)",
        round(len(a) / q3_days * window, 1), "incidents", f"rate x {window} days")
    longest = max(incidents, key=lambda r: r["duration_min"])
    add("I19", "Longest incident in Q3", longest["duration_min"], "minutes", f"{longest['date']} {longest['service']} {longest['severity']}")
    add("I20", "Restore-from-backup RTO (4 hours, from the notes) compared with the longest Q3 incident", round(RTO_MINUTES / longest["duration_min"], 1), "x",
        f"{RTO_MINUTES} / {longest['duration_min']}")
    add("I21", "Restore-from-backup RTO as a share of all auth-service incident minutes in Q3", round(100 * RTO_MINUTES / minutes(a)), "%", f"{RTO_MINUTES} / {minutes(a)}")

    # Money (price quoted in the notes; flat-price and quarter-length are assumptions stated in the report)
    add("X1", "v8 extended support, one quarter", EXT_SUPPORT_USD_PER_QUARTER, "USD", "price quoted in the notes")
    add("X2", "v8 extended support, two quarters", 2 * EXT_SUPPORT_USD_PER_QUARTER, "USD", "assumes the same price for a second quarter")
    return F


# ----------------------------------------------------------------------------- diagram
FILL = {"pass": "#DDF0DA", "fail": "#F8D4D4", "not tested": "#E3E3E3"}
LINE = {"pass": "#2E7D32", "fail": "#B3261E", "not tested": "#555555"}


def node_label(s: dict) -> str:
    state = staging_state(s["staging_result"])
    if state == "fail":
        m = re.search(r"\((\d+) of (\d+)", s["staging_result"])
        staging = f"staging: fail ({m.group(1)} of {m.group(2)} tests)" if m else "staging: fail"
    else:
        staging = f"staging: {state}"
    rollback = "rollback: yes" if s["rollback_path"] == "yes" else "rollback: no"
    return (f'<<b>{s["service"]}</b><br/>{s["owner_team"]} \u00b7 {s["criticality"]}'
            f'<br/><font point-size="10">{staging} \u00b7 {rollback}</font>>')


def build_dot(services: list[dict], dep: dict) -> str:
    by_name = {s["service"]: s for s in services}
    names, deps, callers = dep["names"], dep["deps"], dep["callers"]
    hub = max(names, key=lambda n: len(callers[n]))
    group = [n for n in names if hub in deps[n]]
    outside = [n for n in names if n not in group and n != hub]
    tail = max(group, key=lambda n: (len(callers[n]), n))

    def node(n: str) -> str:
        s = by_name[n]
        state = staging_state(s["staging_result"])
        width = "2.8" if s["criticality"] == "critical" else "1.4"
        return (f'"{n}" [label={node_label(s)}, fillcolor="{FILL[state]}", color="{LINE[state]}", penwidth={width}];')

    L = ["digraph dependencies {",
         '  graph [rankdir=TB, compound=true, fontname="Arial", fontsize=10, nodesep=0.45, ranksep=0.65, pad=0.25, '
         'bgcolor="white", labelloc=b, labeljust=l,',
         '         label=<<font point-size="10">An arrow from A to B means A depends on B (calls it).<br align="left"/>'
         'Green: passed staging, rollback available. Red: failed staging, no rollback. Grey: not tested, no rollback.'
         '<br align="left"/>'
         'Thick outline: critical service. Amber double arrow: the two services depend on each other.'
         '<br align="left"/></font>>];',
         '  node  [shape=box, style="rounded,filled", fontname="Arial", fontsize=12, margin="0.16,0.09"];',
         '  edge  [color="#444444", arrowsize=0.8, penwidth=1.2, fontname="Arial", fontsize=11];',
         "",
         "  subgraph cluster_callers {",
         f'    label="{len(group)} services call {hub} directly";',
         '    labelloc=t; labeljust=l; fontsize=11; style="rounded,dashed"; color="#7A7A7A"; margin=14;']
    L += ["    " + node(n) for n in group]
    done = set()
    for n in group:
        for m in deps[n]:
            if m in group:
                key = tuple(sorted((n, m)))
                if n in deps[m]:
                    if key in done:
                        continue
                    done.add(key)
                    L.append(f'    "{n}" -> "{m}" [dir=both, constraint=false, color="#B26A00", fontcolor="#B26A00", '
                             f'penwidth=1.8, label="mutual"];')
                    L.append(f'    {{ rank=same; "{n}"; "{m}"; }}')
                else:
                    L.append(f'    "{n}" -> "{m}";')
    L += ["  }", ""]
    L += ["  " + node(n) for n in [hub] + outside]
    L.append("")
    for n in group:
        for m in deps[n]:
            if m in outside:
                L.append(f'  "{n}" -> "{m}";')
    L.append(f'  "{tail}" -> "{hub}" [ltail=cluster_callers, penwidth=3, color="#B3261E", label="  {len(group)} services"];')
    for m in deps[hub]:
        L.append(f'  "{hub}" -> "{m}";')
    L.append("}")
    return "\n".join(L) + "\n"


def find_dot() -> str | None:
    exe = shutil.which("dot")
    if exe:
        return exe
    for p in (r"C:\Program Files\Graphviz\bin\dot.exe", r"C:\Program Files (x86)\Graphviz\bin\dot.exe"):
        if Path(p).exists():
            return p
    return None


# ----------------------------------------------------------------------------- main
def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    print("Source checksums:")
    ok = verify_checksums()

    services = read_csv("services.csv")
    incidents = read_csv("incidents-q3.csv")
    for r in incidents:
        r["date"] = dt.date.fromisoformat(r["date"])
        r["duration_min"] = int(r["duration_min"])

    dep = analyse_dependencies(services)
    write_csv("dependency-analysis.csv",
              ["service", "owner_team", "criticality", "staging_state", "rollback_path", "depends_on_count", "depends_on",
               "direct_dependents_count", "direct_dependents", "transitive_dependents_count", "in_cycle_with"],
              dependency_rows(services, dep))

    by_service, by_cause = incident_tables(incidents)
    write_csv("incidents-by-service.csv",
              ["service", "incidents", "total_minutes", "sev1", "sev2", "sev3", "longest_minutes", "causes"], by_service)
    write_csv("incidents-by-cause.csv",
              ["cause", "incidents", "total_minutes", "sev1", "sev2", "sev3", "services"], by_cause)
    write_csv("key-dates.csv", ["date", "weekday", "event", "source"], key_dates())
    figures = key_figures(services, dep, incidents)
    write_csv("key-figures.csv", ["id", "figure", "value", "unit", "how_computed"], figures)

    FIGURES.mkdir(parents=True, exist_ok=True)
    dot_path, png_path = FIGURES / "dependency-map.dot", FIGURES / "dependency-map.png"
    dot_path.write_text(build_dot(services, dep), encoding="utf-8", newline="\n")
    exe = find_dot()
    if exe:
        subprocess.run([exe, "-Tpng", "-Gdpi=170", str(dot_path), "-o", str(png_path)], check=True)
        print(f"Wrote {png_path.relative_to(HERE.parent)}")
    else:
        print("Graphviz `dot` not found: wrote the .dot source only. Install Graphviz to rebuild the PNG.")

    print("\nKey figures:")
    for f in figures:
        print(f"  {f['id']:<4} {f['value']!s:<28} {f['unit']:<22} {f['figure']}")
    print(f"\nWrote derived files to {DERIVED.relative_to(HERE.parent)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
