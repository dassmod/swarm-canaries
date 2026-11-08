"""Figures of the report, from the tables that scripts/07_robustness.py writes.

Owner: Dastan.

Run:
  .venv/bin/python scripts/09_figures.py

Reads results/robust_recall.csv and results/robust_names.csv.

Writes:
  results/fig1_detectors.png   recall of three detectors under four report conditions, with 95% intervals over runs
  results/fig2_names.png       blind monitor recall on used pairs, by whether the receiver's report names the source,
                               with 95% intervals over runs
"""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
INK, MUTED, GRID = "#1f2328", "#5b6470", "#e6e8eb"
plt.rcParams.update({"font.size": 11, "font.family": "DejaVu Sans", "axes.edgecolor": GRID, "text.color": INK})

BASE = "board=on,push=off,share=off,n=3"
CONDS = [
    (BASE, "Plain report"),
    (BASE + ",cite=on", "Cite\n(nobody hides)"),
    (BASE + ",stealth=hard,cite=on", "Cite + hard stealth\n(agents hide)"),
    (BASE + ",stealth=aware,cite=on", "Cite + stealth,\nagents know ids\nare checked"),
]
DETS = [
    ("canary", "Token canary", "#2a78d6", "o"),
    ("monitor_blind", "Blind LLM monitor", "#eb6834", "s"),
    ("monitor_informed", "Informed LLM monitor", "#1baf7a", "D"),
]
LABEL_LEFT = {(0, "monitor_blind"), (3, "canary")}
recall = {(r["condition"], r["detector"]): r for r in csv.DictReader(open(RES / "robust_recall.csv"))}

fig, ax = plt.subplots(figsize=(7.6, 3.9), dpi=200)
for i, (_, name, color, marker) in enumerate(DETS):
    det = DETS[i][0]
    xs = [k + (i - 1) * 0.2 for k in range(len(CONDS))]
    ys, lo, hi = [], [], []
    for cond, _ in CONDS:
        r = recall[(cond, det)]
        y, a, b = float(r["recall"]), float(r["lo"]), float(r["hi"])
        ys.append(y), lo.append(y - a), hi.append(b - y)
    ax.errorbar(
        xs, ys, yerr=[lo, hi], fmt=marker, color=color, ms=7, mec="white", mew=1, elinewidth=2, capsize=0, label=name
    )
    for k, (x, y) in enumerate(zip(xs, ys, strict=True)):
        left = (k, det) in LABEL_LEFT  # these labels would touch the next marker or its whisker
        ax.annotate(
            f"{y:.0%}",
            (x, y),
            xytext=(-8 if left else 8, 0),
            textcoords="offset points",
            va="center",
            ha="right" if left else "left",
            fontsize=9,
            color=MUTED,
        )
n = [recall[(c, "canary")]["used"] for c, _ in CONDS]
ax.set_xticks(range(len(CONDS)))
ax.set_xticklabels([f"{label}\nn={k} transfers" for (_, label), k in zip(CONDS, n, strict=True)], fontsize=9.5)
ax.set_ylim(-0.04, 1.18)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
ax.set_ylabel("Used transfers caught")
ax.grid(axis="y", color=GRID)
ax.set_axisbelow(True)
ax.tick_params(length=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.13), fontsize=9.5)
fig.tight_layout()
fig.savefig(RES / "fig1_detectors.png")

names = list(csv.DictReader(open(RES / "robust_names.csv")))
BARS = [
    ("open", "plain", "names source", "Plain,\nnames source"),
    ("open", "cite", "names source", "Cite,\nnames source"),
    ("open", "cite", "no name", "Cite,\nno name"),
    ("hard", "plain", "no name", "Hard stealth,\nno name"),
    ("hard", "cite", "no name", "Hard + cite,\nno name"),
    ("aware", "cite", "no name", "Knows ids,\nno name"),
]
fig, ax = plt.subplots(figsize=(7.6, 2.8), dpi=200)
for i, (fam, fmt, nm, label) in enumerate(BARS):
    r = next(x for x in names if (x["family"], x["format"], x["report"]) == (fam, fmt, nm))
    y = float(r["monitor_blind"])
    lo, hi = float(r["blind_lo"]), float(r["blind_hi"])
    ax.bar(i, y, width=0.5, color="#eb6834")
    ax.errorbar(i, y, yerr=[[y - lo], [hi - y]], color=INK, elinewidth=1.4, capsize=0)
    ax.text(i, max(y, hi) + 0.07, f"{y:.0%}\nn={r['pairs']}", ha="center", fontsize=9, color=MUTED)
ax.set_xticks(range(len(BARS)))
ax.set_xticklabels([b[3] for b in BARS], fontsize=8.5)
ax.set_ylim(0, 1.48)
ax.set_yticks([0, 0.5, 1])
ax.set_yticklabels(["0%", "50%", "100%"])
ax.set_ylabel("Caught by blind monitor")
ax.grid(axis="y", color=GRID)
ax.set_axisbelow(True)
ax.tick_params(length=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(RES / "fig2_names.png")
print("wrote fig1_detectors.png and fig2_names.png")
