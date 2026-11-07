"""Run one sandbox run: 3 agents, one shared board, incident triage.

Run:  .venv/bin/python scripts/01_run_sandbox.py
Writes data/runs/<run_id>.jsonl (the log) and data/runs/<run_id>.meta.json.
Prints a quick check: did the agents use the board, and did they solve the task.
This is not the detector. Detectors and metrics are Nikita's scripts.
"""
import os
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.sandbox import Sandbox, make_client  # noqa: E402
from src.scenario_incident_01 import SCENARIO  # noqa: E402

make_client()  # loads .env
MODEL = os.getenv("AGENT_MODEL")
if not MODEL:
    sys.exit("Put AGENT_MODEL in .env")

run_id = time.strftime("run_%Y%m%d_%H%M%S")
box = Sandbox(run_id, SCENARIO, MODEL)
rows = box.run()

print(f"run {run_id}: {len(rows)} events")
counts = Counter((r["agent"], r["event"]) for r in rows)
print("\nevents per agent")
for agent in SCENARIO["agents"]:
    print(f"  {agent}: " + ", ".join(f"{e}={counts[(agent, e)]}" for e in ("post", "read", "submit", "no_submit")))

print("\nwho read whose post")
for r in rows:
    if r["event"] == "read" and r["post_id"] is not None:
        print(f"  step {r['step']}: {r['agent']} read post {r['post_id']} by {r['author']}")

key = SCENARIO["answer_keyword"]
print(f"\nanswer check (report contains '{key}')")
for agent in SCENARIO["agents"]:
    rep = box.reports.get(agent)
    print(f"  {agent}: " + ("no report" if rep is None else ("correct" if key in rep else "wrong")))
