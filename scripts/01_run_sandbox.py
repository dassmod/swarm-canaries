"""Run the sandbox: agents on one incident scenario, one condition, one or more repeats.

Owner: Dastan. Needs ADAPTION_API_KEY and AGENT_MODEL in .env.

Run:
  .venv/bin/python scripts/01_run_sandbox.py                       # scenario 1, board on
  .venv/bin/python scripts/01_run_sandbox.py --scenario 4          # six agents
  .venv/bin/python scripts/01_run_sandbox.py --no-board            # control: no board
  .venv/bin/python scripts/01_run_sandbox.py --push                # tell agents who holds what
  .venv/bin/python scripts/01_run_sandbox.py --share-everything    # "share everything" instruction
  .venv/bin/python scripts/01_run_sandbox.py --repeats 5 --seed 100
  .venv/bin/python scripts/01_run_sandbox.py --show-prompts        # print a prompt, call no model

Writes:
  data/runs/<run_id>.jsonl      the log: one row per board event (the ground truth)
  data/runs/<run_id>.meta.json  condition, model, seed, agent order, scenario

Prints a quick check per run: events per agent, reads of another agent's post, and the task
outcome by the rule in src/ground_truth.py. This is not a detector. Detectors and metrics
are scripts/02_metrics.py and scripts/03_monitor.py.
"""

import argparse
import os
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import importlib  # noqa: E402

from src.ground_truth import load_run, task_outcome  # noqa: E402
from src.sandbox import Sandbox, condition_label, make_client, make_condition, system_prompt  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--board", action=argparse.BooleanOptionalAction, default=True, help="agents have a board (default on)")
ap.add_argument("--push", action="store_true", help="tell each agent who holds the logs it needs")
ap.add_argument("--share-everything", action="store_true", help="tell each agent to share everything")
ap.add_argument(
    "--scenario",
    type=int,
    default=1,
    choices=[1, 2, 3, 4],
    help="scenario number: src/scenario_incident_0N.py (4 has six agents)",
)
ap.add_argument("--agents", type=int, default=None, help="number of agents (default: all agents of the scenario)")
ap.add_argument("--repeats", type=int, default=1)
ap.add_argument("--seed", type=int, default=0, help="seed of the agent order; repeat i uses seed+i")
ap.add_argument("--show-prompts", action="store_true", help="print the agent prompts and stop")
args = ap.parse_args()

SCENARIO = importlib.import_module(f"src.scenario_incident_0{args.scenario}").SCENARIO
n_agents = args.agents or len(SCENARIO["agents"])
cond = make_condition(args.board, args.push, args.share_everything, n_agents)
label = condition_label(cond)

if args.show_prompts:
    names = list(SCENARIO["agents"])[: cond["n_agents"]]
    print(f"condition: {label}\n")
    print(system_prompt(names[0], SCENARIO, cond, names))
    sys.exit(0)

# Credits per 1M tokens (input, output), from the Models page of docs.adaptionlabs.ai. Cached input is cheaper, so
# the estimate is an upper bound.
PRICES_PER_MILLION = {"qwen3.5-397b": (0.55, 3.50), "gemma-4-31b-it": (0.09, 0.34)}

make_client()  # loads .env
MODEL = os.getenv("AGENT_MODEL")
if not MODEL:
    sys.exit("Put AGENT_MODEL in .env")

for i in range(args.repeats):
    run_id = time.strftime("run_%Y%m%d_%H%M%S") + f"_s{args.scenario}_seed{args.seed + i}"
    box = Sandbox(run_id, SCENARIO, MODEL, cond, seed=args.seed + i)
    rows = box.run()
    counts = Counter((r["agent"], r["event"]) for r in rows)
    print(f"\n{run_id}  [{label}]  {len(rows)} events, order of round 1: {box.order_log[0]}")
    # Answer check uses Nikita's rule (src/ground_truth.py): correct, mixed, decoy, other, no_report
    saved_rows, meta = load_run(ROOT / "data" / "runs" / f"{run_id}.jsonl")
    outcome = task_outcome(saved_rows, meta)
    for a in box.agents:
        ev = ", ".join(f"{e}={counts[(a, e)]}" for e in ("post", "read", "submit"))
        print(f"  {a}: {ev}  answer {outcome[a]}")
    cross = [r for r in rows if r["event"] == "read" and r["post_id"] is not None and r["author"] != r["agent"]]
    print(f"  reads of another agent's post: {len(cross)}")
    u = box.usage
    price = PRICES_PER_MILLION.get(MODEL)
    cost = (
        f", about {(u['input_tokens'] * price[0] + u['output_tokens'] * price[1]) / 1e6:.3f} credits" if price else ""
    )
    print(f"  model calls: {u['calls']}, tokens in/out: {u['input_tokens']}/{u['output_tokens']}{cost}")
