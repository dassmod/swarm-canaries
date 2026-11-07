"""Run the whole run plan from docs/scenarios.md: every scenario, condition and repeat.

Owner: Dastan.

Needs ADAPTION_API_KEY and AGENT_MODEL in .env.

Run:
  .venv/bin/python scripts/05_run_plan.py --dry-run              # list the jobs, call no model
  .venv/bin/python scripts/05_run_plan.py                        # run all jobs, 5 at a time
  .venv/bin/python scripts/05_run_plan.py --repeats 2 --workers 3

The plan (repeats per cell, default 5):
  main              scenarios 1, 2, 3   with board and without board
  push              scenarios 1, 2, 3   --push
  share everything  scenarios 1, 2, 3   --share-everything
  six agents        scenario 4          with board and without board

Repeat k uses seed k in every condition, so the agent order is the same across conditions.
A job is skipped if its run is already complete in data/runs, so a stopped plan can be started again.
Each job calls scripts/01_run_sandbox.py. Its printed summary goes to data/plan_output/<job>.txt.
"""

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.sandbox import condition_tag, make_condition  # noqa: E402
from src.scenario_incident_01 import SCENARIO as SCENARIO_1  # noqa: E402
from src.scenario_incident_04 import SCENARIO as SCENARIO_4  # noqa: E402

N3 = len(SCENARIO_1["agents"])
N6 = len(SCENARIO_4["agents"])

# (series, scenario, flags for 01_run_sandbox.py, condition)
CELLS = []
for s in (1, 2, 3):
    CELLS.append(("main", s, [], make_condition(True, False, False, N3)))
    CELLS.append(("main", s, ["--no-board"], make_condition(False, False, False, N3)))
    CELLS.append(("push", s, ["--push"], make_condition(True, True, False, N3)))
    CELLS.append(("share", s, ["--share-everything"], make_condition(True, False, True, N3)))
CELLS.append(("six", 4, [], make_condition(True, False, False, N6)))
CELLS.append(("six", 4, ["--no-board"], make_condition(False, False, False, N6)))


def is_complete(scenario, cond, seed):
    """True if data/runs holds a finished run for this scenario, condition and seed."""
    for log in (ROOT / "data" / "runs").glob(f"*_s{scenario}_{condition_tag(cond)}_seed{seed}.jsonl"):
        rows = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
        done = {r["agent"] for r in rows if r["event"] in ("submit", "no_submit")}
        if len(done) == cond["n_agents"]:
            return True
    return False


def run_job(job):
    series, scenario, flags, cond, seed = job
    name = f"{series}_s{scenario}_{condition_tag(cond)}_seed{seed}"
    cmd = [sys.executable, str(ROOT / "scripts" / "01_run_sandbox.py"), "--scenario", str(scenario), *flags]
    cmd += ["--seed", str(seed)]
    out = ROOT / "data" / "plan_output"
    out.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    (out / f"{name}.txt").write_text(result.stdout + result.stderr)
    status = "ok" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
    print(f"{status}  {name}", flush=True)
    return name, result.returncode


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true", help="list the jobs and stop")
    args = ap.parse_args()

    jobs = [(*cell, seed) for seed in range(args.repeats) for cell in CELLS]
    todo = [j for j in jobs if not is_complete(j[1], j[3], j[4])]
    print(f"{len(jobs)} jobs in the plan, {len(jobs) - len(todo)} already complete, {len(todo)} to run", flush=True)
    if args.dry_run:
        for series, scenario, flags, cond, seed in todo:
            print(f"  {series:6} scenario {scenario} {' '.join(flags) or '(board on)':20} seed {seed}")
        sys.exit(0)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(run_job, todo))
    failed = [name for name, code in results if code != 0]
    print(f"\ndone: {len(results) - len(failed)} ok, {len(failed)} failed")
    for name in failed:
        print(f"  failed: {name}")
    sys.exit(1 if failed else 0)
