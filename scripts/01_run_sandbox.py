"""Run the sandbox: 3 agents (or more), incident triage, one condition, one or more repeats.

Examples:
  .venv/bin/python scripts/01_run_sandbox.py                       # board on
  .venv/bin/python scripts/01_run_sandbox.py --no-board            # control: no board
  .venv/bin/python scripts/01_run_sandbox.py --push                # tell agents who holds what
  .venv/bin/python scripts/01_run_sandbox.py --share-everything    # "share everything" instruction
  .venv/bin/python scripts/01_run_sandbox.py --repeats 5 --seed 100
  .venv/bin/python scripts/01_run_sandbox.py --show-prompts        # print prompts, call no model

Writes data/runs/<run_id>.jsonl (the log) and data/runs/<run_id>.meta.json.
The summary is a quick check, not the detector. Detectors and metrics are Nikita's scripts.
"""
import argparse
import os
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.sandbox import Sandbox, condition_label, make_client, make_condition, system_prompt  # noqa: E402
from src.scenario_incident_01 import SCENARIO  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--board", action=argparse.BooleanOptionalAction, default=True, help="agents have a board (default on)")
ap.add_argument("--push", action="store_true", help="tell each agent who holds the logs it needs")
ap.add_argument("--share-everything", action="store_true", help="tell each agent to share everything")
ap.add_argument("--agents", type=int, default=3, help="number of agents (the scenario must have that many)")
ap.add_argument("--repeats", type=int, default=1)
ap.add_argument("--seed", type=int, default=0, help="seed of the agent order; repeat i uses seed+i")
ap.add_argument("--show-prompts", action="store_true", help="print the agent prompts and stop")
args = ap.parse_args()

cond = make_condition(args.board, args.push, args.share_everything, args.agents)
label = condition_label(cond)

if args.show_prompts:
    names = list(SCENARIO["agents"])[:cond["n_agents"]]
    print(f"condition: {label}\n")
    print(system_prompt(names[0], SCENARIO, cond, names))
    sys.exit(0)

make_client()  # loads .env
MODEL = os.getenv("AGENT_MODEL")
if not MODEL:
    sys.exit("Put AGENT_MODEL in .env")

key = SCENARIO["answer_keyword"]
for i in range(args.repeats):
    run_id = time.strftime("run_%Y%m%d_%H%M%S") + f"_seed{args.seed + i}"
    box = Sandbox(run_id, SCENARIO, MODEL, cond, seed=args.seed + i)
    rows = box.run()
    counts = Counter((r["agent"], r["event"]) for r in rows)
    print(f"\n{run_id}  [{label}]  {len(rows)} events, order of round 1: {box.order_log[0]}")
    for a in box.agents:
        rep = box.reports.get(a)
        verdict = "no report" if rep is None else ("correct" if key in rep else "wrong")
        ev = ", ".join(f"{e}={counts[(a, e)]}" for e in ("post", "read", "submit"))
        print(f"  {a}: {ev}  answer {verdict}")
    cross = [r for r in rows if r["event"] == "read" and r["post_id"] is not None and r["author"] != r["agent"]]
    print(f"  reads of another agent's post: {len(cross)}")
