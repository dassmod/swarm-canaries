"""Charts for the report, from the tables scripts/02_metrics.py writes.

Owner: Nikita.

Run:
  .venv/bin/python scripts/04_charts.py                          # results/ -> results/
  .venv/bin/python scripts/04_charts.py --tables tests/out --runs tests/fixtures --out tests/out

Writes:
  detectors_by_condition.png   four panels per condition and detector: recall at the read, used and integrated
                               levels, and the false-alarm rate. The fact canary is left out of the used and
                               integrated panels: those levels are defined by the same facts, so its recall there
                               is 1.0 by construction.
  who_read_whom.png            per condition with a board: how often each agent read posts carrying another
                               agent's information, one small matrix per condition, four per row
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.ground_truth import ground_truth, load_run  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--tables", default=str(ROOT / "results"))
ap.add_argument("--runs", default=str(ROOT / "data" / "runs"))
ap.add_argument("--out", default=str(ROOT / "results"))
args = ap.parse_args()
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)

# Validated reference palette (dataviz skill, light mode): slot 1 blue, slot 2 orange.
COLORS = {
    "canary": "#2a78d6",
    "fact_canary": "#e87ba4",
    "llm_monitor": "#eb6834",
    "llm_monitor_redacted": "#1baf7a",
    "llm_monitor_informed": "#eda100",
}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update(
    {
        "font.size": 10,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK2,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "axes.titlecolor": INK,
    }
)

rows = list(csv.DictReader(open(Path(args.tables) / "metrics_by_condition.csv")))
conds = sorted({r["condition"] for r in rows})
dets = [d for d in COLORS if any(r["detector"] == d for r in rows)]
val = {(r["condition"], r["detector"]): r for r in rows}
has_integrated = "recall_integrated" in rows[0]

panels = [
    ("recall_read", "Recall: read", dets),
    ("recall_used", "Recall: used", [d for d in dets if d != "fact_canary"]),
]
if has_integrated:
    panels.append(("recall_integrated", "Recall: integrated", [d for d in dets if d != "fact_canary"]))
panels.append(("false_alarm_rate", "False-alarm rate", dets))

fig, axes = plt.subplots(
    1, len(panels), figsize=(4.2 * len(panels) + 3.5, 0.55 * len(conds) * len(dets) / 3 + 2.2), sharey=True
)
for ax, (key, title, shown) in zip(axes, panels):
    h = 0.84 / max(len(shown), 1)
    for j, d in enumerate(shown):
        ys, xs = [], []
        for i, c in enumerate(conds):
            r = val.get((c, d))
            v = r.get(key, "") if r else ""
            if v != "":
                ys.append(i + (j - (len(shown) - 1) / 2) * h)
                xs.append(float(v))
        ax.barh(ys, xs, height=h * 0.85, color=COLORS[d], label=d.replace("_", " "))
        for y, x in zip(ys, xs):
            ax.text(x + 0.015, y, f"{x:.2f}", va="center", fontsize=6.5, color=INK2)
    ax.set_title(title, loc="left", fontsize=11)
    ax.set_xlim(0, 1.15)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
axes[0].set_yticks(range(len(conds)))
axes[0].set_yticklabels([c.replace(",", "  ") for c in conds], fontsize=8)
axes[0].invert_yaxis()
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=len(dets), frameon=False, bbox_to_anchor=(0.5, 0.0))
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(out / "detectors_by_condition.png", dpi=200)
print(f"wrote {out / 'detectors_by_condition.png'}")

# Who read whom, summed over runs, one small matrix per condition with a board, four per row.
mats, agents_by = defaultdict(lambda: defaultdict(int)), defaultdict(set)
for log_path in sorted(Path(args.runs).glob("*.jsonl")):
    rws, meta = load_run(log_path)
    if not meta["condition_flags"]["board"]:
        continue
    agents_by[meta["condition"]] |= set(meta["agents"])
    for (s, d), _posts in ground_truth(rws, meta)["read"].items():
        mats[meta["condition"]][(s, d)] += 1
if mats:
    items = sorted(mats.items())
    ncol = min(4, len(items))
    nrow = (len(items) + ncol - 1) // ncol
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.6 * ncol, 3.7 * nrow), squeeze=False)
    vmax = max(v for m in mats.values() for v in m.values())
    for k, (cond, m) in enumerate(items):
        ax = axes[k // ncol][k % ncol]
        ag = sorted(agents_by[cond])
        grid = [[m.get((s, d), 0) for d in ag] for s in ag]
        ax.imshow(grid, cmap="Blues", vmin=0, vmax=vmax)
        for i in range(len(ag)):
            for j in range(len(ag)):
                v = grid[i][j]
                ax.text(
                    j,
                    i,
                    "" if i == j else v,
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if v > vmax * 0.6 else INK,
                )
        ax.set_xticks(range(len(ag)), ag)
        ax.set_yticks(range(len(ag)), ag)
        ax.set_xlabel("reader (dst)", fontsize=8)
        ax.set_ylabel("source (src)", fontsize=8)
        ax.set_title(cond.replace("board=on,", "").replace(",", " "), fontsize=7.5, loc="left")
    for k in range(len(items), nrow * ncol):
        axes[k // ncol][k % ncol].axis("off")
    fig.suptitle("Runs with a read transfer, source to reader", x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(out / "who_read_whom.png", dpi=200)
    print(f"wrote {out / 'who_read_whom.png'}")
