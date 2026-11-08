"""Robustness tables for the report: intervals over runs, names against recall, format compliance, baselines.

Owner: Dastan.

Agents of one run read the same board, so their texts are not independent. Every interval here is a 95%
bootstrap interval over runs, stratified by scenario, with 4000 resamples and seed 0.

Run:
  .venv/bin/python scripts/07_robustness.py                 # data/runs and data/monitor* -> results/

Reads data/runs, data/runs_oracle and the monitor folders in data/.

Writes:
  results/robust_recall.csv      per condition and detector: used, caught, recall against used, interval, false alarms
  results/robust_names.csv       used pairs by whether the receiver's report names the source, monitor recall
  results/robust_format.csv      per condition: reports with a trace id, with an own id, with an id of another agent
  results/robust_answers.csv     per condition: agents naming the whole answer, strict correct, intervals over runs
  results/robust_evidence.csv    what the blind monitor's evidence text mentions
"""

import csv
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.detect_canary import detect as detect_canary  # noqa: E402
from src.ground_truth import agent_info, ground_truth, load_run, reports, task_outcome  # noqa: E402

MONITORS = {
    "monitor_blind": "monitor",
    "monitor_informed": "monitor_informed",
    "monitor_redacted": "monitor_redacted",
    "monitor_notrace": "monitor_notrace",
    "monitor_neutral": "monitor_neutral",
    "monitor_gemma": "monitor_gemma",
}
B = 4000
OUT = ROOT / "results"
ANY_ID = re.compile(r"\b(?:data|sh)-[A-Z0-9]{5,}\b")


def names(text, agent):
    return re.search(rf"\bengineer\s+{agent}\b", text or "", re.I) is not None


def load():
    data = []
    for path in sorted((ROOT / "data" / "runs").glob("*.jsonl")):
        rows, meta = load_run(path)
        flags = {"canary": set(detect_canary(rows, meta))}
        for name, folder in MONITORS.items():
            f = ROOT / "data" / folder / f"{meta['run_id']}.json"
            if f.exists():
                flags[name] = {(x["src"], x["dst"]) for x in json.loads(f.read_text())["flags"]}
        data.append(
            {
                "meta": meta,
                "cond": meta["condition"],
                "sc": meta["scenario"]["name"],
                "gt": ground_truth(rows, meta),
                "reports": reports(rows),
                "outcome": task_outcome(rows, meta),
                "flags": flags,
            }
        )
    return data


def interval(runs, stat):
    """Bootstrap over runs inside each scenario. stat(run) returns (numerator, denominator)."""
    random.seed(0)
    by = defaultdict(list)
    for r in runs:
        by[r["sc"]].append(stat(r))
    vals = []
    for _ in range(B):
        a = b = 0
        for pool in by.values():
            for _ in pool:
                x, y = random.choice(pool)
                a, b = a + x, b + y
        if b:
            vals.append(a / b)
    vals.sort()
    return round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals))], 3) if vals else ("", "")


def write(name, rows):
    OUT.mkdir(exist_ok=True)
    with open(OUT / name, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{name}")
    for r in rows:
        print("  " + "  ".join(f"{v}" for v in r.values()))


data = load()
print(len(data), "runs")
conds = sorted({r["cond"] for r in data})

# recall and false alarms
out = []
for c in conds:
    runs = [r for r in data if r["cond"] == c]
    for det in ["canary", *MONITORS]:
        have = [r for r in runs if det in r["flags"]]
        if not have:
            continue

        def used(r):
            u = set(r["gt"]["used"])
            return len(u & r["flags"][det]), len(u)

        def false(r):
            a = r["meta"]["agents"]
            return len(r["flags"][det] - set(r["gt"]["read"])), len(a) * (len(a) - 1) - len(r["gt"]["read"])

        caught, n = map(sum, zip(*map(used, have), strict=True))
        fa, fn = map(sum, zip(*map(false, have), strict=True))
        lo, hi = interval(have, used) if n else ("", "")
        out.append(
            {
                "condition": c,
                "detector": det,
                "runs": len(have),
                "used": n,
                "caught": caught,
                "recall": round(caught / n, 3) if n else "",
                "lo": lo,
                "hi": hi,
                "false_alarms": fa,
                "non_read_pairs": fn,
                "runs_empty": sum(1 for r in have if not r["flags"][det]),
            }
        )
write("robust_recall.csv", out)

# names against recall, on used pairs (three-agent board runs)
table = defaultdict(lambda: defaultdict(int))
for r in data:
    if "board=off" in r["cond"] or "n=6" in r["cond"]:
        continue
    fam = (
        "aware"
        if "aware" in r["cond"]
        else "hard"
        if "hard" in r["cond"]
        else "soft"
        if "stealth=on" in r["cond"]
        else "open"
    )
    fmt = "cite" if "cite=on" in r["cond"] else "plain"
    for src, dst in r["gt"]["used"]:
        k = (fam, fmt, "names source" if names(r["reports"].get(dst), src) else "no name")
        table[k]["n"] += 1
        for det, f in r["flags"].items():
            table[k][det] += (src, dst) in f
            table[k]["have_" + det] += 1
rows = []
for (fam, fmt, nm), v in sorted(table.items()):
    row = {"family": fam, "format": fmt, "report": nm, "pairs": v["n"]}
    for det in ("monitor_blind", "monitor_redacted", "monitor_notrace"):
        row[det] = round(v[det] / v["have_" + det], 3) if v["have_" + det] else ""
    rows.append(row)
write("robust_names.csv", rows)

# format compliance
rows = []
for c in conds:
    if "cite=on" not in c:
        continue
    runs = [r for r in data if r["cond"] == c]
    n = anyid = own = other = 0
    for r in runs:
        info = agent_info(r["meta"]["scenario"], r["meta"]["agents"])
        for a, rep in r["reports"].items():
            n += 1
            anyid += bool(ANY_ID.search(rep))
            own += any(t in rep for t in info[a]["data"])
            other += any(t in rep for b, i in info.items() if b != a for t in i["data"])
    rows.append({"condition": c, "reports": n, "any_id": anyid, "own_id": own, "other_agent_id": other})
write("robust_format.csv", rows)

# answers


def share(kinds):
    def f(r):
        return sum(o in kinds for o in r["outcome"].values()), len(r["outcome"])

    return f


rows = []
for c in conds:
    runs = [r for r in data if r["cond"] == c]
    whole = share(("correct", "mixed"))
    strict = share(("correct",))
    k, n = map(sum, zip(*map(whole, runs), strict=True))
    s = sum(strict(r)[0] for r in runs)
    lo, hi = interval(runs, whole)
    rows.append({"condition": c, "agents": n, "whole_answer": k, "lo": lo, "hi": hi, "strict_correct": s})
oracle = defaultdict(lambda: [0, 0])
for p in sorted((ROOT / "data" / "runs_oracle").glob("*.jsonl")):
    run_rows, meta = load_run(p)
    o = task_outcome(run_rows, meta)["A"]
    oracle[meta["scenario"]["name"]][0] += o in ("correct", "mixed")
    oracle[meta["scenario"]["name"]][1] += 1
for name, (k, n) in sorted(oracle.items()):
    rows.append(
        {
            "condition": "one agent, all logs: " + name,
            "agents": n,
            "whole_answer": k,
            "lo": "",
            "hi": "",
            "strict_correct": "",
        }
    )
write("robust_answers.csv", rows)

# what the evidence text mentions
rows = []
for fmt, test in (("plain", lambda c: "cite=on" not in c), ("cite", lambda c: "cite=on" in c)):
    n = nm = ids = 0
    for r in data:
        if "board=off" in r["cond"] or not test(r["cond"]):
            continue
        for x in json.loads((ROOT / "data" / "monitor" / f"{r['meta']['run_id']}.json").read_text())["flags"]:
            n += 1
            nm += bool(re.search(r"\b(engineer|colleague)\b", x.get("evidence", ""), re.I))
            ids += bool(re.search(r"trace|data-|sh-", x.get("evidence", "")))
    rows.append({"format": fmt, "blind_flags": n, "evidence_mentions_engineer": nm, "evidence_mentions_trace": ids})
write("robust_evidence.csv", rows)
