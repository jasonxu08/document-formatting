#!/usr/bin/env python3
"""Reproduce every derived number quoted in report.md from the verbatim source data.

Run from any directory:   python report.assets/analyze.py
Reads ../report.data/services.csv and ../report.data/incidents-q3.csv (relative to this file),
prints the derived tables, then asserts the numbers quoted in report.md so that a change in the
data fails loudly. Standard library only.
"""
import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "report.data"


def load(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def table(rows, header):
    widths = [max(len(str(x)) for x in col) for col in zip(header, *rows)]
    line = lambda r: "  ".join(str(x).ljust(w) for x, w in zip(r, widths)).rstrip()
    print(line(header))
    for r in rows:
        print(line(r))


services = load("services.csv")
incidents = load("incidents-q3.csv")
for r in incidents:
    r["duration_min"] = int(r["duration_min"])

# ---------------------------------------------------------------- services and dependencies
names = [s["service"] for s in services]
deps = {s["service"]: [d for d in s["depends_on"].split(";") if d] for s in services}
dependents = defaultdict(list)
for caller, callees in deps.items():
    for callee in callees:
        dependents[callee].append(caller)


def all_dependents(start):
    """Services that depend on `start`, directly or through other services (never `start` itself)."""
    seen, todo = set(), [start]
    while todo:
        for p in dependents[todo.pop()]:
            if p not in seen:
                seen.add(p)
                todo.append(p)
    seen.discard(start)
    return seen


passing = [s["service"] for s in services if s["staging_result"].startswith("pass")]
with_rollback = [s["service"] for s in services if s["rollback_path"] == "yes"]
edges = [(a, b) for a, bs in deps.items() for b in bs]
mutual = sorted({tuple(sorted((a, b))) for a, b in edges if a in deps.get(b, [])})

print("== Services")
print("services: %d | pass staging: %d | with rollback path: %d | dependency edges: %d"
      % (len(names), len(passing), len(with_rollback), len(edges)))
print("not passing staging:", [n for n in names if n not in passing])
print("no rollback path   :", [n for n in names if n not in with_rollback])
print("mutual dependencies:", mutual)
print()
table([(n, len(dependents[n]), ", ".join(sorted(dependents[n])) or "-",
        len(all_dependents(n))) for n in sorted(names, key=lambda n: -len(dependents[n]))],
      ("service", "direct dependents", "who", "all dependents (transitive)"))

# ---------------------------------------------------------------- incidents
total = len(incidents)
minutes_total = sum(r["duration_min"] for r in incidents)
stats = defaultdict(lambda: {"n": 0, "min": 0, "SEV1": 0, "SEV2": 0, "SEV3": 0})
causes = defaultdict(lambda: defaultdict(int))
for r in incidents:
    s = stats[r["service"]]
    s["n"] += 1
    s["min"] += r["duration_min"]
    s[r["severity"]] += 1
    causes[r["service"]][r["cause"]] += 1

print("\n== Incident records by service (Q3 2026: %s to %s)"
      % (min(r["date"] for r in incidents), max(r["date"] for r in incidents)))
table([(n, s["n"], s["SEV1"], s["SEV2"], s["SEV3"], s["min"],
        ", ".join("%s x%d" % kv for kv in sorted(causes[n].items(), key=lambda kv: (-kv[1], kv[0]))))
       for n, s in sorted(stats.items(), key=lambda kv: (-kv[1]["n"], -kv[1]["min"]))],
      ("service", "records", "SEV1", "SEV2", "SEV3", "minutes", "causes"))
print("total records: %d | total minutes: %d" % (total, minutes_total))

auth = stats["auth-service"]
gateway_auth = [r for r in incidents if r["service"] == "gateway" and "auth-service" in r["summary"]]
other_mentions = [r for r in incidents if r["service"] != "gateway" and "auth-service" in r["summary"]]
sev1 = [r for r in incidents if r["severity"] == "SEV1"]
same_event = len({(r["date"], r["duration_min"]) for r in sev1}) < len(sev1)
duplicates = len(sev1) - len({(r["date"], r["duration_min"]) for r in sev1})
distinct = total - duplicates

print("\n== auth-service")
print("own records: %d (%.0f%% of %d) | own minutes: %d (%.0f%% of %d)"
      % (auth["n"], 100 * auth["n"] / total, total, auth["min"], 100 * auth["min"] / minutes_total, minutes_total))
print("gateway records whose summary names auth-service: %d" % len(gateway_auth))
for r in gateway_auth:
    print("   ", r["date"], r["severity"], r["duration_min"], "min |", r["summary"])
print("records involving auth-service (own + gateway records naming it): %d (%.0f%% of %d)"
      % (auth["n"] + len(gateway_auth), 100 * (auth["n"] + len(gateway_auth)) / total, total))
print("non-gateway records naming auth-service in the summary:", len(other_mentions))
print("distinct incidents (the two 11 Jul SEV1 records are one outage): %d | involving auth-service: %d (%.0f%%)"
      % (distinct, auth["n"] + len(gateway_auth) - duplicates,
         100 * (auth["n"] + len(gateway_auth) - duplicates) / distinct))
print("SEV1 records: %d, same outage counted twice: %s" % (len(sev1), same_event))
for r in sev1:
    print("   ", r["date"], r["service"], r["duration_min"], "min |", r["summary"])
longest = max(r["duration_min"] for r in incidents)
print("longest record: %d min | 4 h restore (240 min) is %.1fx that" % (longest, 240 / longest))

refresh = [r for r in incidents if r["cause"] == "token-refresh-bug"]
print("\ntoken-refresh-bug records:")
for r in refresh:
    print("   ", r["date"], r["service"], r["severity"], r["duration_min"], "min |", r["summary"])

rollouts = [r for r in incidents if r["cause"] == "deploy"]
print("\nfailed rollouts (cause = deploy):")
for r in rollouts:
    print("   ", r["date"], r["service"], r["severity"], r["duration_min"], "min |", r["summary"])

gc = [r for r in incidents if r["cause"] == "runtime-gc"]
print("\nruntime-gc records:", [(r["date"], r["service"], r["severity"], r["duration_min"]) for r in gc])

cyc_hits = [r for r in incidents
            if (r["service"] == "catalog-service" and "map-service" in r["summary"].lower())
            or (r["service"] == "map-service" and "catalog-service" in r["summary"].lower())]
print("\ncatalog-service <-> map-service latency records:",
      [(r["date"], r["service"], r["summary"]) for r in cyc_hits])

# ---------------------------------------------------------------- calendar
D = date
decision, window_start, window_end = D(2026, 10, 23), D(2026, 10, 26), D(2026, 10, 30)
freeze_start, freeze_end = D(2026, 11, 1), D(2027, 1, 5)
order_by, v8_eol = D(2026, 11, 5), D(2026, 11, 12)
leave_start, leave_end = D(2026, 10, 26), D(2026, 11, 13)
working_days = sum(1 for i in range((window_end - window_start).days + 1)
                   if (window_start + timedelta(days=i)).weekday() < 5)

print("\n== Calendar")
for label, d in [("decision", decision), ("window start", window_start), ("window end", window_end),
                 ("freeze start", freeze_start), ("extended-support order deadline", order_by),
                 ("v8 end of security support", v8_eol), ("Identity leave ends", leave_end),
                 ("freeze end", freeze_end)]:
    print("%-34s %s %s" % (label, d.isoformat(), d.strftime("%a")))
print("working days 26-30 Oct: %d | days v8 EOL -> freeze end: %d | freeze length: %d days"
      % (working_days, (freeze_end - v8_eol).days, (freeze_end - freeze_start).days + 1))
print("Identity leave overlaps the freeze by %d days (1-13 Nov)" % ((leave_end - freeze_start).days + 1))

# ---------------------------------------------------------------- assertions for report.md
checks = {
    "9 services": len(names) == 9,
    "7 pass staging": len(passing) == 7,
    "7 have a rollback path and they are the 7 that pass": set(with_rollback) == set(passing),
    "16 dependency edges": len(edges) == 16,
    "catalog-service and map-service depend on each other": mutual == [("catalog-service", "map-service")],
    "auth-service has 6 direct dependents": len(dependents["auth-service"]) == 6,
    "auth-service is depended on by every service except user-store and search-index":
        set(dependents["auth-service"]) == set(names) - {"auth-service", "user-store", "search-index"},
    "user-store has 7 dependents (direct or indirect)": len(all_dependents("user-store")) == 7,
    "36 incident records, 35 distinct incidents, 932 minutes": (total, distinct, minutes_total) == (36, 35, 932),
    "auth-service has 11 records and 380 minutes": auth["n"] == 11 and auth["min"] == 380,
    "14 of 35 distinct incidents involve auth-service": auth["n"] + len(gateway_auth) - duplicates == 14,
    "auth-service has 1 SEV1, 6 SEV2, 4 SEV3": (auth["SEV1"], auth["SEV2"], auth["SEV3"]) == (1, 6, 4),
    "4 gateway records name auth-service": len(gateway_auth) == 4,
    "no other record names auth-service": len(other_mentions) == 0,
    "the two SEV1 records are one outage": len(sev1) == 2 and same_event,
    "longest record is 78 minutes": longest == 78,
    "3 token-refresh-bug records, all auth-service": len(refresh) == 3 and all(r["service"] == "auth-service" for r in refresh),
    "5 failed rollouts, 10 to 19 minutes": len(rollouts) == 5 and min(r["duration_min"] for r in rollouts) == 10
        and max(r["duration_min"] for r in rollouts) == 19,
    "each of catalog-service and map-service logged one record blaming the other": len(cyc_hits) == 2,
    "26-30 Oct is 5 working days": working_days == 5,
    "54 days between v8 EOL and freeze end": (freeze_end - v8_eol).days == 54,
    "66-day freeze": (freeze_end - freeze_start).days + 1 == 66,
    "freeze starts on a Sunday, decision on a Friday": freeze_start.weekday() == 6 and decision.weekday() == 4,
}
print("\n== Checks against the numbers quoted in report.md")
failed = [k for k, ok in checks.items() if not ok]
for k, ok in checks.items():
    print("%-4s %s" % ("ok" if ok else "FAIL", k))
raise SystemExit("FAILED: %s" % failed if failed else 0)
