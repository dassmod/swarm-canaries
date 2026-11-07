"""Charts for the report, from the tables scripts/02_metrics.py writes.

Owner: Nikita.

Run:
  .venv/bin/python scripts/04_charts.py                          # results/ -> results/
  .venv/bin/python scripts/04_charts.py --tables tests/out --runs tests/fixtures --out tests/out

Writes:
  detectors_by_condition.png   two panels: recall (used) and false-alarm rate, per condition, per detector
  who_read_whom.png            per condition with a board: how often each agent read posts carrying another agent's information
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

fig, axes = plt.subplots(1, 2, figsize=(10, 0.6 * len(conds) + 1.8), sharey=True)
for ax, (key, title) in zip(
    axes, [("recall_used", "Recall (transfers that were used)"), ("false_alarm_rate", "False-alarm rate")]
):
    h = 0.8 / max(len(dets), 1)
    for j, d in enumerate(dets):
        ys, xs = [], []
        for i, c in enumerate(conds):
            r = val.get((c, d))
            v = r[key] if r else ""
            if v != "":
                ys.append(i + (j - (len(dets) - 1) / 2) * h)
                xs.append(float(v))
        ax.barh(ys, xs, height=h * 0.9, color=COLORS[d], label=d.replace("_", " "))
        for y, x in zip(ys, xs):
            ax.text(x + 0.01, y, f"{x:.2f}", va="center", fontsize=8, color=INK2)
    ax.set_title(title, loc="left", fontsize=11)
    ax.set_xlim(0, 1.1)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axes[0].set_yticks(range(len(conds)))
axes[0].set_yticklabels([c.replace(",", "  ") for c in conds])
axes[0].invert_yaxis()
axes[1].legend(frameon=False, loc="lower right")
fig.tight_layout()
fig.savefig(out / "detectors_by_condition.png", dpi=200)
print(f"wrote {out / 'detectors_by_condition.png'}")

# Who read whom, summed over runs, one panel per condition with a board.
mats, agents_all = defaultdict(lambda: defaultdict(int)), set()
for log_path in sorted(Path(args.runs).glob("*.jsonl")):
    rws, meta = load_run(log_path)
    if not meta["condition_flags"]["board"]:
        continue
    agents_all |= set(meta["agents"])
    for (s, d), posts in ground_truth(rws, meta)["read"].items():
        mats[meta["condition"]][(s, d)] += 1
if mats:
    ag = sorted(agents_all)
    fig, axes = plt.subplots(1, len(mats), figsize=(3.6 * len(mats) + 1.0, 3.6), squeeze=False)
    vmax = max(v for m in mats.values() for v in m.values())
    for ax, (cond, m) in zip(axes[0], sorted(mats.items())):
        grid = [[m.get((s, d), 0) for d in ag] for s in ag]
        ax.imshow(grid, cmap="Blues", vmin=0, vmax=vmax)
        for i in range(len(ag)):
            for k in range(len(ag)):
                v = grid[i][k]
                ax.text(
                    k,
                    i,
                    "" if i == k else v,
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white" if v > vmax * 0.6 else INK,
                )
        ax.set_xticks(range(len(ag)), ag)
        ax.set_yticks(range(len(ag)), ag)
        ax.set_xlabel("reader (dst)")
        ax.set_ylabel("source (src)")
        ax.set_title(cond.replace(",", " "), fontsize=8, loc="left")
    fig.suptitle("Runs with a read transfer, source to reader", x=0.02, ha="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(out / "who_read_whom.png", dpi=200)
    print(f"wrote {out / 'who_read_whom.png'}")
