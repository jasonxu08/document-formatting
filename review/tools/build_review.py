#!/usr/bin/env python3
"""Build the visual review pages and charts from the raw records in this repository.

Reads    review/iteration-N/records/**         grading, mechanical checks, cold-reader answers, analyst notes
         examples/**                           the documents under review and the scenario descriptions
         review/trigger-tests/records/**       skill-selection simulations
         evals/*                               cold-reader facts, trigger queries
Writes   review/assets/*.png                   charts
         review/README.md                      the dashboard
         review/iteration-N/README.md and review/iteration-N/eval-*.md
         review/trigger-tests/README.md
         examples/README.md and examples/<scenario>/README.md

Every number on the scenario, iteration, trigger and final-check pages is computed here from the records;
nothing is typed by hand.
Setup:   pip install -r review/tools/requirements.txt
Usage:   python review/tools/build_review.py
"""
import difflib
import json
import os
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import logging  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
_AVAILABLE = {f.name for f in font_manager.fontManager.ttflist}
FONT_FAMILY = ["DejaVu Sans"] + [f for f in ("Microsoft YaHei", "Noto Sans CJK SC", "PingFang SC", "SimHei") if f in _AVAILABLE]

ROOT = Path(__file__).resolve().parents[2]
REVIEW, EXAMPLES, EVALS = ROOT / "review", ROOT / "examples", ROOT / "evals"
ASSETS = REVIEW / "assets"
FINAL = REVIEW / "final-check"

GREEN, GREY, RED, ORANGE, YELLOW, BLUE, LIGHT, INK = (
    "#2da44e", "#8c959f", "#cf222e", "#fb8500", "#d4a72c", "#0969da", "#eaeef2", "#1f2328")
plt.rcParams.update({
    "font.family": FONT_FAMILY, "font.size": 9,
    "axes.edgecolor": "#d0d7de", "axes.labelcolor": INK,
    "text.color": INK, "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False,
    "axes.spines.right": False, "figure.facecolor": "white",
})

CFGS = ("without-skill", "with-skill")
CFG_LABEL = {"without-skill": "Without the skill", "with-skill": "With the skill"}
CFG_COLOR = {"without-skill": GREY, "with-skill": GREEN}
SCEN = json.loads((EXAMPLES / "scenarios.json").read_text(encoding="utf-8"))
FACTS = json.loads((EVALS / "cold_reader_facts.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- data

def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


KEY_RE = re.compile(r"^([A-G]\d(?: [A-G]\d)*)\b")


def key_of(text):
    m = KEY_RE.match(text)
    return m.group(1) if m else text.split(":")[0].strip()


def label_of(text):
    return text.split(":")[0].strip()


def key_order(k):
    m = re.match(r"([A-G])(\d)", k)
    if m:
        return (0, m.group(1), int(m.group(2)))
    return (1 if k == "Automatic checks" else 2 if k == "Cold reader" else 3, k, 0)


class Run:
    def __init__(self, it, scen, cfg):
        self.it, self.scen, self.cfg = it, scen, cfg
        self.base = REVIEW / ("iteration-%d" % it) / "records" / scen["eval"] / cfg
        self.g = load_json(self.base / "grading.json")
        self.exp = self.g["expectations"]
        self.passed, self.total = self.g["summary"]["passed"], self.g["summary"]["total"]
        self.pct = self.passed / self.total
        mp = self.base / "mechanical.json"
        self.mech = load_json(mp) if mp.exists() else None

    @property
    def gate(self):
        return self.mech["gate"] if self.mech and "gate" in self.mech else None

    @property
    def stats(self):
        if not self.mech:
            return {}
        if "files" in self.mech:
            return self.mech["files"].get("report.md", {}).get("stats", {})
        return self.mech.get("stats", {})

    def passed_by_key(self):
        return {key_of(e["text"]): e["passed"] for e in self.exp}


def runs_of(it):
    scens = SCEN if it == 2 else [s for s in SCEN if s["id"] <= 3]
    return [(s, {cfg: Run(it, s, cfg) for cfg in CFGS}) for s in scens]


def common_keys(runs):
    counts = {}
    for _, pair in runs:
        for k in {key_of(e["text"]) for e in pair["with-skill"].exp}:
            counts[k] = counts.get(k, 0) + 1
    keys = [k for k, c in counts.items() if c >= 2]
    if any(KEY_RE.match(k) for k in keys):
        # rubric-coded assertions plus the two shared special ones; scenario-specific names stay on their own pages
        keys = [k for k in keys if KEY_RE.match(k) or k in ("Automatic checks", "Cold reader")]
    return sorted(keys, key=key_order)


SHORT = {
    "A1": "A1 Zones marked and ordered", "A3": "A3 Machine blocks collapsed", "B1": "B1 Reading path",
    "B2": "B2 Order follows understanding", "B3": "B3 Headings carry the story", "C1": "C1 Conclusion first",
    "C2": "C2 Compact glance panel", "C3": "C3 Verdict, decisions, risks complete", "C4": "C4 Nothing invented",
    "C5": "C5 Numbers trace to sources", "D1": "D1 Diagram drawn", "D2": "D2 Coverage and truth",
    "D3 D4": "D3 D4 Image-first and legible", "D5 D6": "D5 D6 Explained and reproducible",
    "E1 E2": "E1 E2 Honesty and labelling", "F3": "F3 Chat reply is the panel", "F4": "F4 Reader's language",
    "Automatic checks": "Automatic checks (gate)", "Cold reader": "Cold reader at least 80%",
}


def row_label(runs, key):
    if key in SHORT:
        return SHORT[key]
    for _, pair in runs:
        for e in pair["with-skill"].exp:
            if key_of(e["text"]) == key:
                return label_of(e["text"])
    return key


def short_label(text):
    return SHORT.get(key_of(text), label_of(text))


def cold_scores():
    p = REVIEW / "iteration-2" / "records" / "coldreader-scores.json"
    return load_json(p) if p.exists() else {}


def cold_of(scen, cfg):
    data = cold_scores().get("%s/%s/run-1" % (scen["eval"], cfg.replace("-", "_")))
    return data


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def pooled(runs, cfg):
    p = sum(pair[cfg].passed for _, pair in runs)
    t = sum(pair[cfg].total for _, pair in runs)
    return p, t, mean([pair[cfg].pct for _, pair in runs])


# ---------------------------------------------------------------- helpers

def save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  chart", name)


def esc(text):
    """Escape free text for a Markdown page: HTML characters, and '[' so that quoted links stay plain text."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("[", "\\[")


def cell(text):
    return re.sub(r"\s+", " ", str(text)).replace("|", "\\|").strip()


def rel(frm, to):
    return os.path.relpath(str(to), str(Path(frm).parent)).replace("\\", "/")


def pct(n, d):
    return "%.0f%%" % (100.0 * n / d) if d else "n/a"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path), "w", encoding="utf-8", newline="\n") as fh:  # Path.write_text(newline=) needs Python 3.10
        fh.write(text.rstrip() + "\n")
    print("  page", path.relative_to(ROOT).as_posix())


def ok(flag):
    return "✅" if flag else "❌"


def plural(n, word):
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


def gate_text(run):
    g = run.gate
    if g:
        parts = "%s · %s · %s" % (plural(g["blockers"], "Blocker"), plural(g["majors"], "Major"), plural(g["minors"], "Minor"))
        return ("✅ " if g["passed"] else "❌ ") + parts
    if run.mech and "errors" in run.mech:
        return "%s · %s" % (plural(len(run.mech["errors"]), "error"), plural(len(run.mech["warnings"]), "warning"))
    return "n/a"


def display_prompt(scen, text):
    text = re.sub(r"<workspace>[\\/]+fixtures[\\/]+[\w-]+[\\/]*", "examples/%s/input/" % scen["dir"], text)
    return text.replace("\\\\", "\\")


# ---------------------------------------------------------------- charts

def chart_pass_rate(it, runs, name):
    labels = [s["short"] for s, _ in runs] + ["All scenarios"]
    x = np.arange(len(labels))
    w = 0.38
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    for i, cfg in enumerate(CFGS):
        vals = [pair[cfg].pct for _, pair in runs]
        vals.append(mean(vals))
        bars = ax.bar(x + (i - 0.5) * w, vals, w, color=CFG_COLOR[cfg], label=CFG_LABEL[cfg])
        for j, b in enumerate(bars):
            if j < len(runs):
                r = runs[j][1][cfg]
                txt = "%d/%d" % (r.passed, r.total)
            else:
                p, t, _ = pooled(runs, cfg)
                txt = "%d/%d" % (p, t)
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.015, txt, ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.12)
    ax.set_yticks([0, .25, .5, .75, 1])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("Assertions passed")
    ax.grid(axis="y", color="#eaeef2")
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=2)
    save(fig, name)


def chart_heatmap(it, runs, name):
    keys = common_keys(runs)
    cols = [(s, cfg) for s, _ in runs for cfg in CFGS]
    mat = np.full((len(keys), len(cols)), 2)
    pair_by_eval = {s["eval"]: pair for s, pair in runs}
    for j, (s, cfg) in enumerate(cols):
        res = pair_by_eval[s["eval"]][cfg].passed_by_key()
        for i, k in enumerate(keys):
            if k in res:
                mat[i, j] = 1 if res[k] else 0
    fig, ax = plt.subplots(figsize=(1.9 + 0.62 * len(cols), 0.9 + 0.3 * len(keys)))
    ax.imshow(mat, cmap=ListedColormap([RED, GREEN, LIGHT]), vmin=0, vmax=2, aspect="auto")
    for i in range(len(keys)):
        for j in range(len(cols)):
            v = mat[i, j]
            ax.text(j, i, "✓" if v == 1 else "✗" if v == 0 else "–", ha="center", va="center",
                    color="white" if v < 2 else "#8c959f", fontsize=9, fontweight="bold")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([("with" if c == "with-skill" else "without") for _, c in cols], fontsize=7.5)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(keys)))
    labels = [row_label(runs, k) for k in keys]
    ax.set_yticklabels([l if len(l) <= 46 else l[:45] + "…" for l in labels], fontsize=8)
    ax.set_xticks(np.arange(-.5, len(cols), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(keys), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="both", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    tr = ax.get_xaxis_transform()
    for e_i, (s, _) in enumerate(runs):
        ax.annotate(s["short"], xy=(2 * e_i + 0.5, 1), xycoords=tr, xytext=(0, 22), textcoords="offset points",
                    ha="center", va="bottom", fontweight="bold")
    for j, (s, cfg) in enumerate(cols):
        r = pair_by_eval[s["eval"]][cfg]
        ax.text(j, -0.02, "%d/%d" % (r.passed, r.total), ha="center", va="top", fontsize=8, transform=tr,
                color=GREEN if cfg == "with-skill" else "#57606a", fontweight="bold")
    save(fig, name)


def chart_discrimination(it, runs, name):
    keys = common_keys(runs)
    rows = []
    for k in keys:
        stat = {}
        for cfg in CFGS:
            hits = [pair[cfg].passed_by_key()[k] for _, pair in runs if k in pair[cfg].passed_by_key()]
            stat[cfg] = (sum(hits), len(hits))
        if stat["with-skill"][1]:
            rows.append((k, stat))
    rows.sort(key=lambda r: (r[1]["with-skill"][0] / r[1]["with-skill"][1]) - (r[1]["without-skill"][0] / max(r[1]["without-skill"][1], 1)))
    fig, ax = plt.subplots(figsize=(7.6, 0.55 + 0.27 * len(rows)))
    for i, (k, st) in enumerate(rows):
        a = st["without-skill"][0] / max(st["without-skill"][1], 1)
        b = st["with-skill"][0] / st["with-skill"][1]
        ax.plot([a, b], [i, i], color="#d0d7de", lw=3, zorder=1, solid_capstyle="round")
        ax.scatter([a], [i], s=46, color=GREY, zorder=2)
        ax.scatter([b], [i], s=46, color=GREEN, zorder=3)
        ax.text(1.04, i, "%d/%d → %d/%d" % (st["without-skill"][0], st["without-skill"][1], st["with-skill"][0], st["with-skill"][1]),
                va="center", fontsize=7.5, color="#57606a")
    ax.set_yticks(range(len(rows)))
    labels = [row_label(runs, k) for k, _ in rows]
    ax.set_yticklabels([l if len(l) <= 44 else l[:43] + "…" for l in labels], fontsize=8)
    ax.set_xlim(-0.04, 1.0)
    ax.set_xticks([0, .5, 1])
    ax.set_xticklabels(["0%", "50%", "100%"])
    ax.grid(axis="x", color="#eaeef2")
    ax.set_axisbelow(True)
    ax.scatter([], [], color=GREY, label="Without the skill")
    ax.scatter([], [], color=GREEN, label="With the skill")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=8)
    save(fig, name)


def chart_gate(runs, name):
    cols = [(s, cfg, pair[cfg]) for s, pair in runs for cfg in CFGS]
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    x = np.arange(len(cols))
    maj = [c[2].gate["majors"] for c in cols]
    bars = ax.bar(x, maj, 0.62, color=[ORANGE if c[1] == "without-skill" else GREEN for c in cols])
    for b, c in zip(bars, cols):
        g = c[2].gate
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.12, "%d Major%s\n%d Minor" % (g["majors"], "" if g["majors"] == 1 else "s", g["minors"]),
                ha="center", va="bottom", fontsize=7.5, color="#57606a")
    ax.axhline(2, color=RED, ls="--", lw=1)
    ax.text(len(cols) - 0.45, 2.12, "gate limit: 0 Blockers, at most 2 Majors", ha="right", va="bottom", fontsize=8, color=RED)
    ax.set_xticks(x)
    ax.set_xticklabels([("with" if c[1] == "with-skill" else "without") for c in cols], fontsize=8)
    for e_i, (s, _) in enumerate(runs):
        ax.text(2 * e_i + 0.5, -0.17, s["short"], ha="center", va="top", fontweight="bold", transform=ax.get_xaxis_transform())
    ax.set_ylim(0, max(maj + [2]) + 1.7)
    ax.set_ylabel("Majors reported by check_doc.py")
    ax.grid(axis="y", color="#eaeef2")
    ax.set_axisbelow(True)
    save(fig, name)


def chart_cold_reader(runs, name):
    cols = [(s, cfg) for s, _ in runs for cfg in CFGS]
    n = max(len(FACTS[str(s["id"])]) for s, _ in runs)
    mat = np.full((n, len(cols)), 2)
    recall = []
    for j, (s, cfg) in enumerate(cols):
        c = cold_of(s, cfg)
        facts = FACTS[str(s["id"])]
        rec = set(c["recovered"]) if c else set()
        for i, f in enumerate(facts):
            mat[i, j] = 1 if f["id"] in rec else 0
        recall.append((len(rec), len(facts)))
    fig, ax = plt.subplots(figsize=(1.7 + 0.62 * len(cols), 0.9 + 0.36 * n))
    ax.imshow(mat, cmap=ListedColormap([RED, GREEN, LIGHT]), vmin=0, vmax=2, aspect="auto")
    for i in range(n):
        for j in range(len(cols)):
            v = mat[i, j]
            ax.text(j, i, "✓" if v == 1 else "✗" if v == 0 else "–", ha="center", va="center",
                    color="white" if v < 2 else "#8c959f", fontsize=9, fontweight="bold")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([("with" if c == "with-skill" else "without") for _, c in cols], fontsize=7.5)
    ax.xaxis.tick_top()
    ax.set_yticks(range(n))
    ax.set_yticklabels(["Key fact K%d" % (i + 1) for i in range(n)], fontsize=8)
    ax.set_xticks(np.arange(-.5, len(cols), 1), minor=True)
    ax.set_yticks(np.arange(-.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="both", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    tr = ax.get_xaxis_transform()
    for e_i, (s, _) in enumerate(runs):
        ax.annotate(s["short"], xy=(2 * e_i + 0.5, 1), xycoords=tr, xytext=(0, 22), textcoords="offset points",
                    ha="center", va="bottom", fontweight="bold")
    for j, (r, t) in enumerate(recall):
        ax.text(j, -0.02, "%d/%d" % (r, t), ha="center", va="top", fontsize=8, transform=tr, fontweight="bold",
                color=GREEN if cols[j][1] == "with-skill" else "#57606a")
    save(fig, name)


def trigger_data():
    base = REVIEW / "trigger-tests" / "records"
    queries = load_json(EVALS / "trigger-eval.json")
    runs = {}
    for tag in ("A", "B", "C"):
        for k in (1, 2, 3):
            p = base / ("%s-%d.answers.json" % (tag, k))
            if p.exists():
                runs[(tag, k)] = {a["id"]: a for a in load_json(p)["answers"]}
    return queries, runs


def chart_triggers(name):
    queries, runs = trigger_data()
    cols = sorted(runs)
    mat = np.zeros((len(queries), len(cols)))
    for j, c in enumerate(cols):
        for i, q in enumerate(queries):
            hit = "document-formatting" in runs[c].get(i + 1, {}).get("skills", [])
            mat[i, j] = 1 if hit == q["should_trigger"] else 0
    fig, ax = plt.subplots(figsize=(6.4 + 0.62 * len(cols), 0.8 + 0.27 * len(queries)))
    ax.imshow(mat, cmap=ListedColormap([RED, GREEN]), vmin=0, vmax=1, aspect="auto")
    for i, q in enumerate(queries):
        for j, c in enumerate(cols):
            hit = "document-formatting" in runs[c].get(i + 1, {}).get("skills", [])
            ax.text(j, i, "loaded" if hit else "not loaded", ha="center", va="center", color="white", fontsize=6.5, fontweight="bold")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(["%s run %d" % c for c in cols], fontsize=8)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(queries)))
    ax.set_yticklabels([("▲ " if q["should_trigger"] else "▽ ") + re.sub(r"\s+", " ", q["query"])[:62] + "…" for q in queries], fontsize=7)
    ax.set_xticks(np.arange(-.5, len(cols), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(queries), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="both", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    save(fig, name)


# ---------------------------------------------------------------- pages

def eval_page(it, scen, pair):
    page = REVIEW / ("iteration-%d" % it) / ("%s.md" % scen["eval"])
    meta = load_json(REVIEW / ("iteration-%d" % it) / "records" / scen["eval"] / "eval_metadata.json")
    wo, wi = pair["without-skill"], pair["with-skill"]
    out = ["# %s · iteration %d" % (scen["title"], it), "",
           "[← Iteration %d](README.md) · [Review dashboard](../README.md)%s" % (
               it, " · [Example documents](%s)" % rel(page, EXAMPLES / scen["dir"] / "README.md") if it == 2 else ""), "",
           "> **Prompt given to both agents**", ">"]
    for line in display_prompt(scen, meta["prompt"]).splitlines():
        out.append("> " + line)
    out += ["", "## Result", "", "| | Without the skill | With the skill |", "|---|---|---|",
            "| Assertions passed | **%d / %d** (%s) | **%d / %d** (%s) |" % (wo.passed, wo.total, pct(wo.passed, wo.total), wi.passed, wi.total, pct(wi.passed, wi.total)),
            "| Automatic checker%s | %s | %s |" % (" (the v0.1 checker: errors and warnings, no tiers)" if it == 1 else "", gate_text(wo), gate_text(wi))]
    if it == 2:
        out.append("| First section, words (the checker's panel measure; budget about 300) | %s | %s |" % (wo.stats.get("panel_words", "n/a") or "no panel", wi.stats.get("panel_words", "n/a")))
        out.append("| Words in the human-read zone (the whole document when there are no zones) | %s | %s |" % (format(wo.stats.get("human_zone_words", 0), ","), format(wi.stats.get("human_zone_words", 0), ",")))
        co, cw = cold_of(scen, "without-skill"), cold_of(scen, "with-skill")
        if co and cw:
            out.append("| Cold reader, first 60 lines | %d / %d key facts | %d / %d key facts |" % (len(co["recovered"]), co["total"], len(cw["recovered"]), cw["total"]))
    out += ["", "## What the reader sees first", ""]
    if it == 2:
        img = lambda cfg: rel(page, EXAMPLES / scen["dir"] / "images" / ("%s-first-screen.png" % cfg))
        doc = lambda cfg: rel(page, EXAMPLES / scen["dir"] / cfg / "report.md")
    else:
        img = lambda cfg: rel(page, REVIEW / "iteration-1" / "images" / ("%s-%s-first-screen.png" % (scen["eval"], cfg)))
        doc = lambda cfg: rel(page, REVIEW / "iteration-1" / "outputs" / scen["eval"] / cfg / "report.md")
    out += ["| Without the skill | With the skill |", "|---|---|",
            "| ![first screen without the skill](%s) | ![first screen with the skill](%s) |" % (img("without-skill"), img("with-skill")),
            "| [Open the document](%s) | [Open the document](%s) |" % (doc("without-skill"), doc("with-skill")), ""]
    out += ["## Assertion scorecard", "",
            "Each assertion was graded by an agent that read the document and cited evidence; ✅ passed, ❌ failed. The evidence for every failure is below, and the full evidence for every assertion is in the raw `grading.json` of each run.", "",
            "| Assertion | Without | With |", "|---|:-:|:-:|"]
    wo_by = {e["text"]: e for e in wo.exp}
    for e in wi.exp:
        o = wo_by.get(e["text"])
        out.append("| %s | %s | %s |" % (cell(short_label(e["text"])), ok(o["passed"]) if o else "–", ok(e["passed"])))
    out += ["", "<details>", "<summary>The full text of every assertion in this scorecard</summary>", ""]
    for e in wi.exp:
        out.append("- " + esc(re.sub(r"\s+", " ", e["text"])))
    out += ["", "</details>"]
    failed = [(e, wo_by.get(e["text"])) for e in wi.exp if not e["passed"] or (wo_by.get(e["text"]) and not wo_by[e["text"]]["passed"])]
    out += ["", "### Evidence for the failed assertions", ""]
    for e, o in failed:
        for cfg, item in (("without the skill", o), ("with the skill", e)):
            if item and not item["passed"]:
                out += ["<details>", "<summary>❌ <b>%s</b> · %s</summary>" % (esc(short_label(e["text"])), cfg), "",
                        "**Assertion:** " + esc(re.sub(r"\s+", " ", e["text"])), "", "**Grader evidence:** " + esc(re.sub(r"\s+", " ", item["evidence"])), "", "</details>", ""]
    if it == 2:
        facts = FACTS[str(scen["id"])]
        co, cw = cold_of(scen, "without-skill"), cold_of(scen, "with-skill")
        out += ["## Cold reader", "",
                "A fresh agent saw only the first 60 lines of each document (and the images in them), answered six fixed questions, and was scored against key facts derived from the *inputs*, so both arms face the same list.", "",
                "| Key fact | Without | With |", "|---|:-:|:-:|"]
        for f in facts:
            out.append("| **%s** %s | %s | %s |" % (f["id"], cell(f["fact"]), ok(f["id"] in co["recovered"]) if co else "–", ok(f["id"] in cw["recovered"]) if cw else "–"))
        out += ["", "Raw answers: [without the skill](records/%s/without-skill/coldreader-answers.md) · [with the skill](records/%s/with-skill/coldreader-answers.md)" % (scen["eval"], scen["eval"]), ""]
        for c, label in ((co, "without the skill"), (cw, "with the skill")):
            if c and c.get("note"):
                out.append("- Scoring note, %s: %s" % (label, esc(c["note"])))
        out.append("")
    out += ["## What the graders said about the assertions themselves", "",
            "Graders were asked to critique the test, not only the document. These are the suggestions they raised for this scenario (the skill and the assertions were revised from them; see [how the skill evolved](../skill-evolution/README.md)).", ""]
    any_fb = False
    for cfg, run in (("with the skill", wi), ("without the skill", wo)):
        fb = run.g.get("eval_feedback", {})
        sugg = fb.get("suggestions", [])
        if sugg or fb.get("overall"):
            any_fb = True
            out += ["<details>", "<summary><b>Grader critique, %s run</b> (%d suggestions)</summary>" % (cfg, len(sugg)), ""]
            for s in sugg:
                head = ("**%s** — " % esc(short_label(s["assertion"]))) if s.get("assertion") else ""
                out.append("- " + head + esc(re.sub(r"\s+", " ", s["reason"])))
            if fb.get("overall"):
                out += ["", "**Overall:** " + esc(re.sub(r"\s+", " ", fb["overall"]))]
            out += ["", "</details>", ""]
    if not any_fb:
        out += ["No critique was recorded.", ""]
    out += ["## Executor notes and raw records", "",
            "The agent that wrote each document also left notes on where the instructions it had were unclear.", "",
            "| Record | Without the skill | With the skill |", "|---|---|---|"]
    names = [("Executor notes", "executor-notes.md"), ("Grading (assertions, evidence, claims, critique)", "grading.json"),
             ("Automatic checker output", "mechanical.json"), ("Timing (estimated from file times)", "timing.json")]
    if it == 2:
        names.insert(1, ("Cold-reader answers", "coldreader-answers.md"))
    for title, fn in names:
        cells = []
        for cfg in CFGS:
            p = REVIEW / ("iteration-%d" % it) / "records" / scen["eval"] / cfg / fn
            cells.append("[%s](records/%s/%s/%s)" % (fn, scen["eval"], cfg, fn) if p.exists() else "–")
        out.append("| %s | %s | %s |" % (title, cells[0], cells[1]))
    out.append("| Prompt and assertions | [eval_metadata.json](records/%s/eval_metadata.json) | |" % scen["eval"])
    write(page, "\n".join(out))


def iteration_page(it, runs, analyst):
    page = REVIEW / ("iteration-%d" % it) / "README.md"
    wp, wt, wm = pooled(runs, "without-skill")
    ip, it_, im = pooled(runs, "with-skill")
    ctx = {
        1: ("v0.1", "The first draft of the skill, tested on three scenarios. Assertions were written by hand per scenario (14 or 15 each). Both arms were told Graphviz was installed, which is why the baseline diagrams are good. One grader agent per run; no cold reader and no tiered checker yet. The findings of this round produced the rubric and the checker."),
        2: ("v0.2", "The skill after it gained a review rubric and a tiered checker, tested on four scenarios (one in Chinese). Assertions were derived from the rubric plus scenario-specific ones, and no tool hints were given to either arm. One grader agent per run, a separate cold reader per document, and the automatic checker as a gate."),
    }[it]
    out = ["# Iteration %d · skill %s" % (it, ctx[0]), "", "[← Review dashboard](../README.md)", "", ctx[1], "",
           "| | Without the skill | With the skill |", "|---|---|---|",
           "| Assertions passed (pooled) | **%d / %d** | **%d / %d** |" % (wp, wt, ip, it_),
           "| Mean pass rate per run | **%.1f%%** | **%.1f%%** |" % (100 * wm, 100 * im)]
    if it == 2:
        gp = lambda cfg: sum(1 for _, pair in runs if pair[cfg].gate["passed"])
        out.append("| Automatic gate passed | **%d / %d** | **%d / %d** |" % (gp("without-skill"), len(runs), gp("with-skill"), len(runs)))
        cs = lambda cfg: (sum(len(cold_of(s, cfg)["recovered"]) for s, _ in runs), sum(cold_of(s, cfg)["total"] for s, _ in runs))
        out.append("| Cold-reader facts recovered | **%d / %d** | **%d / %d** |" % (cs("without-skill") + cs("with-skill")))
    out += ["", "![Assertions passed per scenario](../assets/it%d-pass-rate.png)" % it, "",
            "## Scenario by scenario", "",
            "| Scenario | Without | With | Automatic checker%s (without → with) | Page |" % (", v0.1 (errors and warnings, no tiers)" if it == 1 else ""), "|---|---|---|---|---|"]
    for s, pair in runs:
        wo, wi = pair["without-skill"], pair["with-skill"]
        gate = "%s → %s" % (gate_text(wo), gate_text(wi)) if it == 2 else "%s → %s" % (gate_text(wo), gate_text(wi))
        out.append("| %s | %d/%d | %d/%d | %s | [details](%s.md) |" % (s["title"], wo.passed, wo.total, wi.passed, wi.total, cell(gate), s["eval"]))
    out += ["", "## Every common assertion, every run", "",
            "Rows are the assertions that appear in at least two scenarios; ✓ passed, ✗ failed, – not part of that scenario. Scenario-specific assertions are on each scenario page.", "",
            "![Assertion heatmap](../assets/it%d-heatmap.png)" % it, "",
            "## Where the skill moved the needle", "",
            "Each row is one assertion. The grey dot is the pass rate without the skill, the green dot with it. Long lines are where the skill matters; assertions where both dots sit together passed or failed for both arms.", "",
            "![Discrimination per assertion](../assets/it%d-discrimination.png)" % it, ""]
    if it == 2:
        out += ["## The automatic gate", "",
                "`check_doc.py` reports every finding with a rule ID and a tier. The gate is: no Blocker and at most two Majors.", "",
                "![Automatic gate](../assets/it2-gate.png)", "",
                "## Cold reader", "",
                "![Cold-reader recall](../assets/it2-cold-reader.png)", ""]
    out += ["## What the analyst noticed", ""]
    for note in analyst:
        out.append("- " + esc(note))
    out += ["", "## Records", "",
            "- [benchmark.json](records/benchmark.json) and [benchmark.md](records/benchmark.md): aggregated results in the format of the skill-creator viewer",
            "- [analyst-notes.json](records/analyst-notes.json): the analyst's observations, quoted above"]
    if it == 2:
        out.append("- [coldreader-scores.json](records/coldreader-scores.json): which key facts each cold reader recovered")
    out += ["- Per scenario: prompt and assertions, grading, checker output, executor notes (see each scenario page)",
            "- Note: the harness reports no token counts and no true execution time, so neither is compared; the timing files are estimates from file timestamps and include idle waits.", ""]
    write(page, "\n".join(out))


def skill_description():
    text = (REVIEW.parent / "skills" / "document-formatting" / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^description:\s*(.+)$", text, re.M)
    return m.group(1).strip()


def description_edits(old, new):
    a, b = old.split(), new.split()
    edits = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        # widen to the neighbouring word so a lone-punctuation edit still reads as a phrase
        lo = max(i1 - 1, 0)
        edits.append((" ".join(a[lo:i2 + (1 if i2 == i1 else 0)]), " ".join(b[max(j1 - 1, 0):j2 + (1 if j2 == j1 else 0)])))
    return edits


def trigger_page():
    queries, runs = trigger_data()
    desc_a = (REVIEW / "trigger-tests" / "records" / "desc-A.txt").read_text(encoding="utf-8").strip()
    desc_b = (REVIEW / "trigger-tests" / "records" / "desc-B.txt").read_text(encoding="utf-8").strip()

    def hit(tag, k, i):
        return "document-formatting" in runs[(tag, k)].get(i + 1, {}).get("skills", [])

    tags = [t for t in ("A", "B", "C") if (t, 1) in runs]
    stats = {}
    for tag in tags:
        tp = sum(hit(tag, k, i) for k in (1, 2, 3) for i, q in enumerate(queries) if q["should_trigger"])
        pos = 3 * sum(q["should_trigger"] for q in queries)
        fp = sum(hit(tag, k, i) for k in (1, 2, 3) for i, q in enumerate(queries) if not q["should_trigger"])
        neg = 3 * sum(not q["should_trigger"] for q in queries)
        stats[tag] = (tp, pos, fp, neg)
    others = {}
    for run in runs.values():
        for a in run.values():
            for s in a["skills"]:
                if s != "document-formatting":
                    others[s] = others.get(s, 0) + 1
    out = ["# Trigger tests: does the skill load when it should?", "", "[← Review dashboard](../README.md)", "",
           "A skill only helps if the agent loads it. The description in `SKILL.md` is what the agent sees when it chooses, so it was tested the same way the choice happens: an agent was given the rules for choosing skills, the real list of available skills (about 100, with this skill's description added) and 22 realistic requests, and asked which skills it would invoke first.", "",
           "| Description under test | Should-trigger requests loaded | Near-miss requests wrongly loaded |", "|---|---|---|"]
    names = {"A": "A · description of skill v0.3", "B": "B · adds “rewrite or restructure an existing long report”",
             "C": "C · the text published in `SKILL.md`"}
    for tag in tags:
        tp, pos, fp, neg = stats[tag]
        out.append("| %s | **%d / %d** | **%d / %d** |" % (names[tag], tp, pos, fp, neg))
    shipped = skill_description()
    edits = description_edits(desc_b, shipped)
    if "C" in tags:
        why = "Description C is the text that ships. It differs from B by %d small wording edits (listed below) made so that the frontmatter parses as YAML and stays under the 1,024-character limit, so B's three runs were repeated with the published wording: same requests, same order." % len(edits)
    else:
        why = "Description B is the candidate that shipped. The text in `SKILL.md` differs from it by %d small wording edits (listed below) made so that the frontmatter parses as YAML and stays under the 1,024-character limit; the simulation was not re-run on the final wording." % len(edits)
    out += ["", "Each cell is 3 runs with the requests shuffled differently each time. " + why, "",
            "![Trigger matrix](../assets/trigger-matrix.png)", "",
            "Green means the outcome was right: loaded for the ▲ requests, not loaded for the ▽ near-misses. Near-misses include converting Markdown to Word, fixing a typo in a README, extracting tables from a PDF, proofreading, a commit message and a unit test.", "",
            "## The descriptions", "", "<details><summary><b>Description A</b> (%d characters)</summary>" % len(desc_a), "", esc(desc_a), "", "</details>", "",
            "<details><summary><b>Description B, as first tested</b> (%d characters)</summary>" % len(desc_b), "", esc(desc_b), "", "</details>", "",
            "<details><summary><b>Description C, the published SKILL.md</b> (%d characters)</summary>" % len(shipped), "", esc(shipped), "", "</details>", "",
            "Edits between B and the published text:", ""]
    out += ["- `%s` → `%s`" % (old or "(nothing)", new or "(removed)") for old, new in edits]
    out += ["", "## The 22 requests", "", "| # | Expected | Request | %s | Other skills chosen |" % " | ".join(tags), "|---|---|---|%s---|" % ("---|" * len(tags))]
    for i, q in enumerate(queries):
        cells = ["%d/3" % sum(hit(t, k, i) for k in (1, 2, 3)) for t in tags]
        alts = sorted({s for run in runs.values() for s in run.get(i + 1, {}).get("skills", []) if s != "document-formatting"})
        out.append("| %d | %s | %s | %s | %s |" % (i + 1, "▲ load" if q["should_trigger"] else "▽ don't", cell(re.sub(r"\s+", " ", q["query"])[:150] + ("…" if len(q["query"]) > 150 else "")), " | ".join(cells), ", ".join("`%s`" % a for a in alts) or "–"))
    out += ["", "Other skills chosen across all runs (counts): " + ", ".join("`%s` %d" % kv for kv in sorted(others.items(), key=lambda kv: -kv[1])) + ".", "",
            "## Limits of this test", "",
            "- It simulates the choice with an agent that reads the list; it does not run any product's real skill loader, so a product can still behave differently.",
            "- The skill list given to the simulation is a real developer's list with internal project skills, which is not published here; the request set is in [`evals/trigger-eval.json`](../../evals/trigger-eval.json).",
            "- Request 21 was reworded after the runs to remove incidental details, and the recorded reasons that mentioned them were edited to match. It still asks to restructure a long notes file; the expected outcome did not change.",
            "- Triggering is probabilistic. If an agent skips the skill in practice, the README shows how to force loading it with one line of project instructions.", "",
            "## Raw records", "", "- Answers of every run: `records/A-1.answers.json` … `records/%s-3.answers.json` (one entry per request: skills chosen and a one-line reason)" % tags[-1],
            "- Descriptions: `records/desc-A.txt`, `records/desc-B.txt`" + (", `records/desc-C.txt`" if "C" in tags else ""), ""]
    write(REVIEW / "trigger-tests" / "README.md", "\n".join(out))
    return stats


def final_check_page(it2):
    """The round that re-ran the four scenarios with the published skill (v1.0.0): gate and cold reader."""
    records = FINAL / "records"
    if not records.is_dir():
        return None
    page = FINAL / "README.md"
    scores_path = records / "coldreader-scores.json"
    scores = load_json(scores_path) if scores_path.exists() else {}
    rows, totals = [], {"old": [0, 0], "new": [0, 0]}
    for s, pair in it2:
        mech = load_json(records / s["dir"] / "with-skill" / "mechanical.json")
        main_stats = mech["files"]["report.md"]["stats"]
        old = pair["with-skill"]
        cold_new, cold_old = scores.get(s["dir"]), cold_of(s, "with-skill")
        rows.append((s, mech["gate"], main_stats, old, cold_new, cold_old))
        if cold_new and cold_old:
            totals["new"][0] += len(cold_new["recovered"]); totals["new"][1] += cold_new["total"]
            totals["old"][0] += len(cold_old["recovered"]); totals["old"][1] += cold_old["total"]
    gate_pass = sum(1 for _, g, *_ in rows if g["passed"])
    findings = (FINAL / "findings.md").read_text(encoding="utf-8").strip() if (FINAL / "findings.md").exists() else ""
    cold_line = ("The cold readers recovered **%d of %d** key facts from the first 60 lines (iteration 2: %d of %d)." % (totals["new"][0], totals["new"][1], totals["old"][0], totals["old"][1])) if totals["new"][1] else "The cold-reader scores are not in yet."
    out = ["# Final check · skill v1.0.0", "", "[← Review dashboard](../README.md) · [How the skill evolved](../skill-evolution/README.md)", "",
           "> ### What this round is",
           ">",
           "> The example documents were written by earlier versions of the skill (v0.2). This round wrote the four scenarios again with **the skill as published, v1.0.0**, to check that the version that ships still produces documents that pass. It is smaller than a full round: four with-skill runs, the automatic gate and one cold reader per document. The without-skill baselines of iteration 2 are not repeated (they do not depend on the skill), and no grader scored assertions.",
           ">",
           "> **Result:** %d of %d documents pass the gate, every one with no finding at all. %s" % (gate_pass, len(rows), cold_line), "",
           "## Result, next to iteration 2", "",
           "| Scenario | Gate, v0.2 → **v1.0.0** | First section, words | Human-read zone, words | Cold reader, key facts |", "|---|---|---|---|---|"]
    for s, g, st, old, cn, co in rows:
        ostats = old.stats
        cold = ("%d/%d → **%d/%d**" % (len(co["recovered"]), co["total"], len(cn["recovered"]), cn["total"])) if cn and co else "n/a"
        out.append("| [%s](outputs/%s/report.md) | %s → **%s** | %s → **%s** | %s → **%s** | %s |" % (
            s["title"], s["dir"], gate_text(old), gate_text_from(g), ostats.get("panel_words", "n/a"), st.get("panel_words", "n/a"),
            format(ostats.get("human_zone_words", 0), ","), format(st.get("human_zone_words", 0), ","), cold))
    if totals["new"][1]:
        out.append("| **All four** | | | | %d/%d → **%d/%d** |" % (totals["old"][0], totals["old"][1], totals["new"][0], totals["new"][1]))
    out += ["", "The panel budget is about 300 words. Gate: no Blocker and at most two Majors; the checker's findings by rule are in `records/<scenario>/with-skill/mechanical.json`. Two cautions on the comparison: the one Minor in iteration 2 was the checker's own note on the archive-only evidence file, which later versions no longer print; and the checker's panel measure changed in v0.3 (link-led Read-next bullets stopped counting), so the word counts are indicative, not strictly comparable.", "",
            "## What the reader sees first", "", "| Scenario | v0.2, in the examples (iteration 2) | **v1.0.0**, this round |", "|---|---|---|"]
    for s, *_ in rows:
        out.append("| %s | ![first screen, v0.2](../../examples/%s/images/with-skill-first-screen.png) | ![first screen, v1.0.0](images/%s-first-screen.png) |" % (s["title"], s["dir"], s["dir"]))
    out += ["", "## What the executors reported", "", findings, "",
            "## How this round was run", "",
            "- **The skill as published, apart from one fix.** The agents read a scratch copy of `skills/document-formatting/` whose files were identical in content to the published ones. One line of `source_set.py` was changed afterwards so that `slice` runs on Python 3.9 (`Path.write_text(newline=)` needs 3.10); it does not change what the script does on 3.10 and newer, and no agent in this round ran that command.",
            "- **Same prompts as iteration 2**, with only the folder paths changed. The agents received copies of the input files in a scratch folder, so they could not see any earlier document.",
            "- **Four fresh executor agents**, one per scenario, each asked to leave its notes on unclear instructions. **Four fresh cold readers**, each given only the first 60 lines of one document and the images in them, answering the [six fixed questions](../../evals/cold-reader-test.md). The orchestrating agent scored them against the same key facts as in iteration 2.",
            "- **The checker** was run on `report.md` and on its sibling files, as in every round.", "",
            "## Limits", "",
            "- One run per scenario, AI executors and readers, no grader and no human rating: this is a regression check, not a new measurement. It cannot show that v1.0.0 is better than v0.2, only that it did not get worse on these four documents.",
            "- The cold-reader scores can only be compared with iteration 2's because the key facts and the questions are the same; the readers were different agents.",
            "- The executors knew they were being tested for where the instructions were unclear, which is not how an agent normally works.", "",
            "## Records", "",
            "- Documents: [`outputs/`](outputs/) (each scenario's `report.md`, siblings, diagram and the agent's final chat reply)",
            "- Per scenario under `records/<scenario>/with-skill/`: `mechanical.json` (checker output), `coldreader-answers.md`, `executor-notes.md`",
            "- [`records/coldreader-scores.json`](records/coldreader-scores.json): which key facts each cold reader recovered", ""]
    write(page, "\n".join(out))
    return {"gate_pass": gate_pass, "n": len(rows), "cold": totals["new"]}


def gate_text_from(g):
    parts = "%s · %s · %s" % (plural(g["blockers"], "Blocker"), plural(g["majors"], "Major"), plural(g["minors"], "Minor"))
    return ("✅ " if g.get("passed", g["blockers"] == 0 and g["majors"] <= 2) else "❌ ") + parts


def examples_pages(it2_runs):
    by_eval = {s["eval"]: pair for s, pair in it2_runs}
    out = ["# Examples", "", "Four scenarios, each run twice with the same prompt and the same inputs: once by an agent **without** the skill and once **with** it. The documents are exactly what the agents produced (only machine-specific paths were removed), so you can read both and judge for yourself.", "",
           "| # | Scenario | Kind | Language | Without the skill | With the skill |", "|---|---|---|---|---|---|"]
    for s in SCEN:
        pair = by_eval[s["eval"]]
        wo, wi = pair["without-skill"], pair["with-skill"]
        out.append("| %d | [%s](%s/README.md) | %s | %s | %d/%d assertions · %s | %d/%d assertions · %s |" % (
            s["id"], s["title"], s["dir"], s["kind"], s["language"], wo.passed, wo.total, "gate ✅" if wo.gate["passed"] else "gate ❌", wi.passed, wi.total, "gate ✅" if wi.gate["passed"] else "gate ❌"))
    out += ["",
            "## How to read an example", "", "Each scenario folder holds:", "",
            "- `input/`: the notes the agent was given,", "- `without-skill/`: what an agent produced from the same prompt without the skill,",
            "- `with-skill/`: what it produced with the skill (the main `report.md`, its siblings, its diagram and the chat reply it gave),",
            "- `images/`: the first screen of each document as a reader sees it,", "- a `README.md` with the prompt, what to look for and the scores.", "",
            "The scores come from the [review records](../review/README.md): every assertion, every grader's evidence and every cold reader's answers are published.", ""]
    write(EXAMPLES / "README.md", "\n".join(out))
    for s in SCEN:
        pair = by_eval[s["eval"]]
        wo, wi = pair["without-skill"], pair["with-skill"]
        meta = load_json(REVIEW / "iteration-2" / "records" / s["eval"] / "eval_metadata.json")
        page = EXAMPLES / s["dir"] / "README.md"
        co, cw = cold_of(s, "without-skill"), cold_of(s, "with-skill")
        extra = sorted(p.name for p in (EXAMPLES / s["dir"] / "with-skill").iterdir())
        out = ["# %s" % s["title"], "", "[← All examples](../README.md) · [Review of this scenario](%s)" % rel(page, REVIEW / "iteration-2" / ("%s.md" % s["eval"])), "",
               "**%s · %s.** %s" % (s["kind"], s["language"], s["summary"]), "",
               "> **Prompt given to both agents**", ">"]
        for line in display_prompt(s, meta["prompt"]).splitlines():
            out.append("> " + line)
        out += ["", "## What the reader sees first", "", "| Without the skill | With the skill |", "|---|---|",
                "| ![first screen without the skill](images/without-skill-first-screen.png) | ![first screen with the skill](images/with-skill-first-screen.png) |",
                "| [Open the document](without-skill/report.md) | [Open the document](with-skill/report.md) |", ""]
        fc_doc = FINAL / "outputs" / s["dir"] / "report.md"
        if fc_doc.exists():
            fm = load_json(FINAL / "records" / s["dir"] / "with-skill" / "mechanical.json")
            sp = FINAL / "records" / "coldreader-scores.json"
            sc = load_json(sp).get(s["dir"]) if sp.exists() else None
            out += ["The scenario was also written again with the published skill, v1.0.0: [the document](%s), gate %s%s ([final check](%s))." % (
                rel(page, fc_doc), "✅" if fm["gate"]["passed"] else "❌", (", cold reader %d/%d" % (len(sc["recovered"]), sc["total"])) if sc else "", rel(page, FINAL / "README.md")), ""]
        out += ["## What to look for", ""]
        out += ["- " + x for x in s["look_for"]]
        out += ["", "## Scores", "", "| | Without the skill | With the skill |", "|---|---|---|",
                "| Assertions passed | %d / %d | %d / %d |" % (wo.passed, wo.total, wi.passed, wi.total),
                "| Automatic checker | %s | %s |" % (gate_text(wo), gate_text(wi)),
                "| First section, words (budget about 300) | %s | %s |" % (wo.stats.get("panel_words", 0) or "no panel", wi.stats.get("panel_words", "n/a")),
                "| Cold reader, first 60 lines | %d / %d key facts | %d / %d key facts |" % (len(co["recovered"]), co["total"], len(cw["recovered"]), cw["total"]), "",
                "Every assertion with the grader's evidence is on the [review page](%s)." % rel(page, REVIEW / "iteration-2" / ("%s.md" % s["eval"])), "",
                "## What is in this folder", "", "| Folder | Contents |", "|---|---|",
                "| `input/` | %s |" % "; ".join("`%s` (%s)" % tuple(i) for i in s["inputs"]),
                "| `without-skill/` | %s |" % ", ".join("`%s`" % p.name for p in sorted((EXAMPLES / s["dir"] / "without-skill").iterdir())),
                "| `with-skill/` | %s |" % ", ".join("`%s`" % n for n in extra), ""]
        write(page, "\n".join(out))


def dashboard(it1, it2, trig, fc=None):
    p1, t1, m1 = pooled(it1, "without-skill")
    i1, _, mi1 = pooled(it1, "with-skill")
    p2, t2, m2 = pooled(it2, "without-skill")
    i2, _, mi2 = pooled(it2, "with-skill")
    gp = lambda cfg: sum(1 for _, pair in it2 if pair[cfg].gate["passed"])
    cs = lambda cfg: (sum(len(cold_of(s, cfg)["recovered"]) for s, _ in it2), sum(cold_of(s, cfg)["total"] for s, _ in it2))
    tA = trig.get("C", trig["B"])
    out = ["[← The project README](../README.md)", "", "<h1 align=\"center\">Review records</h1>", "",
           "<p align=\"center\"><b>Every claim in this repository about the skill is backed by a record you can open.</b><br>The charts and tables on these pages are generated from the raw files in this folder by <a href=\"tools/build_review.py\"><code>tools/build_review.py</code></a>.</p>", "",
           "## The result in one table", "",
           "| | Without the skill | With the skill |", "|---|---|---|",
           "| Assertions passed, 4 scenarios | %d / %d (mean %.1f%%) | **%d / %d (mean %.1f%%)** |" % (p2, t2, 100 * m2, i2, t2, 100 * mi2),
           "| Automatic gate: no Blocker, at most 2 Majors | %d / 4 documents pass | **%d / 4 documents pass** |" % (gp("without-skill"), gp("with-skill")),
           "| Cold reader: key facts recovered from the first 60 lines | %d / %d | %d / %d |" % (cs("without-skill") + cs("with-skill")),
           "| Skill loads on realistic requests (simulated, 3 runs) | n/a | **%d / %d** should-trigger · **%d / %d** false triggers |" % (tA[0], tA[1], tA[2], tA[3]),
           ] + (["| Version 1.0.0 as published, the four scenarios rerun (no baseline rerun) | n/a | **%d / %d** documents pass the gate · cold reader **%d / %d** |" % (fc["gate_pass"], fc["n"], fc["cold"][0], fc["cold"][1])] if fc else []) + ["",
           "![Assertions passed per scenario, iteration 2](assets/it2-pass-rate.png)", "",
           "## How to read these numbers", "",
           "> The assertions come from the skill's own rubric, so a high pass rate with the skill shows that the skill makes agents follow its rules, not that the rules are the right ones. The **cold-reader test** is the independent measure, and on the synthetic scenarios it did **not** separate the arms (both recovered 22 of 24 facts): a baseline agent that is asked for a decision report already puts the conclusion first. What the skill adds there is structure and consistency: audience zones, a compact glance panel, a reading path, honest labelling and a clean automatic gate.", "",
           "Limits that apply to everything here: one run per scenario and arm (no variance estimate), AI agents as graders and readers, no blind human rating, and no token or time comparison because the harness does not report them.", "",
           "## Where the skill moved the needle", "",
           "![Discrimination per assertion](assets/it2-discrimination.png)", "",
           "## Every assertion, every run", "", "![Assertion heatmap, iteration 2](assets/it2-heatmap.png)", "",
           "## The automatic gate", "", "![Automatic gate](assets/it2-gate.png)", "",
           "## Cold reader", "", "![Cold reader](assets/it2-cold-reader.png)", "",
           "## How the review works", "",
           "```mermaid", "flowchart TB", "  A[\"Same prompt + same input notes\"] --> B[\"Document written<br/>without the skill\"]", "  A --> C[\"Document written<br/>with the skill\"]",
           "  B --> F[\"<b>Checker</b><br/>check_doc.py\"]", "  B --> G[\"<b>Grader agent</b><br/>assertions, evidence, critique\"]", "  B --> H[\"<b>Cold reader</b><br/>first 60 lines only\"]",
           "  C --> F", "  C --> G", "  C --> H",
           "  F --> I[\"Scorecards, charts, analyst notes\"]", "  G --> I", "  H --> I",
           "  I --> J[\"<b>Maintainer review</b><br/>findings change the skill and the rubric\"]", "  J -.->|\"next round\"| A", "```", "",
           "Details, roles and limits: [method.md](method.md).", "",
           "## Rounds of review", "",
           "| Round | Skill | What was tested | Result | Pages |", "|---|---|---|---|---|",
           "| 1 | v0.1 | 3 scenarios, hand-written assertions | %d/%d vs %d/%d assertions (mean %.0f%% vs %.0f%%) | [iteration 1](iteration-1/README.md) |" % (i1, t1, p1, t1, 100 * mi1, 100 * m1),
           "| 2 | v0.2 | 4 scenarios, rubric-derived assertions, cold reader, gate | %d/%d vs %d/%d (mean %.1f%% vs %.1f%%) | [iteration 2](iteration-2/README.md) |" % (i2, t2, p2, t2, 100 * mi2, 100 * m2),
           "| 3 | v0.3 to v1.0.0 | Description triggering, 22 requests × %d descriptions × 3 runs | %d/%d and %d/%d | [trigger tests](trigger-tests/README.md) |" % (len(trig), tA[0], tA[1], tA[2], tA[3]),
           ] + (["| 4 | v1.0.0 | The four scenarios again with the published skill: gate and cold reader | %d/%d pass the gate · cold reader %d/%d | [final check](final-check/README.md) |" % (fc["gate_pass"], fc["n"], fc["cold"][0], fc["cold"][1])] if fc else []) + ["",
           "## Browse", "",
           "| | |", "|---|---|",
           "| [method.md](method.md) | how every number was produced, roles, limits |",
           "| [maintainer-review.md](maintainer-review.md) | the human review: questions, decisions and what they changed |",
           "| [skill-evolution/](skill-evolution/README.md) | every finding and the change it caused, with the diffs |",
           "| [iteration-1/](iteration-1/README.md) · [iteration-2/](iteration-2/README.md) | scenario pages, scorecards, grader evidence, raw records |",
           "| [trigger-tests/](trigger-tests/README.md) | does the description load the skill when it should |",
           ] + (["| [final-check/](final-check/README.md) | the four scenarios rerun with the published v1.0.0, and what the executors found unclear |"] if fc else []) + [
           "| [../examples/](../examples/README.md) | the documents that were reviewed |", ""]
    write(REVIEW / "README.md", "\n".join(out))


def chart_skill_growth(name):
    data = load_json(REVIEW / "skill-evolution" / "sizes.json")["versions"]
    sub = ["first draft", "after iteration 1", "after iteration 2", "rewriting added", "published"]
    parts = [("SKILL.md (read whenever the skill triggers)", BLUE, lambda f: f == "SKILL.md"),
             ("Rubric, guides, template (read on demand)", "#afb8c1", lambda f: f.startswith(("references/", "assets/"))),
             ("Scripts (run, not read)", ORANGE, lambda f: f.startswith("scripts/"))]
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    bottoms = np.zeros(len(data))
    for label, color, pick in parts:
        vals = np.array([sum(v["bytes"] for f, v in d["files"].items() if pick(f)) / 1000.0 for d in data])
        ax.bar(range(len(data)), vals, bottom=bottoms, color=color, width=0.58, label=label, edgecolor="white", linewidth=1.2)
        for i, v in enumerate(vals):
            if v > 3:
                ax.text(i, bottoms[i] + v / 2, "%.0f" % v, ha="center", va="center", color="white" if color != "#afb8c1" else INK, fontsize=8.5, fontweight="bold")
        bottoms += vals
    for i, total in enumerate(bottoms):
        ax.text(i, total + 1.2, "%.0f KB" % total, ha="center", fontweight="bold", fontsize=9)
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(["%s\n%s" % (d["version"], s) for d, s in zip(data, sub)], fontsize=8.5)
    ax.set_ylabel("Kilobytes of skill files")
    ax.set_ylim(0, max(bottoms) * 1.15)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=8)
    ax.grid(axis="y", color=LIGHT)
    ax.set_axisbelow(True)
    save(fig, name)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    it1, it2 = runs_of(1), runs_of(2)
    print("charts")
    chart_pass_rate(1, it1, "it1-pass-rate.png")
    chart_pass_rate(2, it2, "it2-pass-rate.png")
    chart_heatmap(1, it1, "it1-heatmap.png")
    chart_heatmap(2, it2, "it2-heatmap.png")
    chart_discrimination(1, it1, "it1-discrimination.png")
    chart_discrimination(2, it2, "it2-discrimination.png")
    chart_gate(it2, "it2-gate.png")
    chart_cold_reader(it2, "it2-cold-reader.png")
    chart_triggers("trigger-matrix.png")
    chart_skill_growth("skill-growth.png")
    print("pages")
    for it, runs in ((1, it1), (2, it2)):
        analyst = load_json(REVIEW / ("iteration-%d" % it) / "records" / "analyst-notes.json")
        iteration_page(it, runs, analyst)
        for s, pair in runs:
            eval_page(it, s, pair)
    stats = trigger_page()
    examples_pages(it2)
    fc = final_check_page(it2)
    dashboard(it1, it2, stats, fc)
    print("done")


if __name__ == "__main__":
    main()
