"""Baseline: one agent that sees the logs of all engineers. Can the task be solved at all?

Owner: Dastan.

Why: scenario 4 has 0 correct answers. This run tells a coordination failure from a task that is too hard.
It is the single-agent baseline of the hidden-profile design (HiddenBench).

Needs ADAPTION_API_KEY and AGENT_MODEL in .env.

Run:
  .venv/bin/python scripts/08_oracle.py --repeats 15 --workers 5

Writes:
  data/runs_oracle/<run_id>.jsonl and .meta.json   same format as data/runs, one agent, no board
Prints the answer counts per scenario by the rule in src/ground_truth.py.
"""

import argparse
import copy
import importlib
import os
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.ground_truth import load_run, task_outcome  # noqa: E402
from src.sandbox import Sandbox, make_client, make_condition  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--repeats", type=int, default=15)
ap.add_argument("--workers", type=int, default=5)
args = ap.parse_args()

OUT = ROOT / "data" / "runs_oracle"


def merged(scenario):
    """Copy of the scenario with one agent that holds every slice."""
    sc = copy.deepcopy(scenario)
    first = next(iter(sc["agents"].values()))
    sc["agents"] = {
        "A": {
            "role": "on-call engineer",
            "slice": [x for a in scenario["agents"].values() for x in a["slice"]],
            "secret_line": first["secret_line"],
            "unique_facts": [f for a in scenario["agents"].values() for f in a["unique_facts"]],
        }
    }
    return sc


def job(item):
    number, seed = item
    sc = merged(importlib.import_module(f"src.scenario_incident_0{number}").SCENARIO)
    run_id = time.strftime("run_%Y%m%d_%H%M%S") + f"_s{number}_oracle_seed{seed}"
    Sandbox(run_id, sc, os.getenv("AGENT_MODEL"), make_condition(False, n_agents=1), seed=seed, out_dir=OUT).run()
    rows, meta = load_run(OUT / f"{run_id}.jsonl")
    return number, task_outcome(rows, meta)["A"]


make_client()  # loads .env
jobs = [(n, seed) for n in (1, 2, 3, 4) for seed in range(args.repeats)]
with ThreadPoolExecutor(max_workers=args.workers) as pool:
    results = list(pool.map(job, jobs))
for n in (1, 2, 3, 4):
    print(f"scenario {n}:", dict(Counter(o for m, o in results if m == n)))
