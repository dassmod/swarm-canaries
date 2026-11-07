"""Sanity checks on every scenario file.

Owner: Nikita.

Run:  .venv/bin/python tests/check_scenarios.py
Checks, per scenario:
  - every agent has one data token in its slice and one secret token in its private line;
  - every unique fact is in its owner's slice and in no other slice or shared log;
  - no single agent (own slice + shared logs) contains all answer keywords: the answer needs the board;
  - the decoy keyword is in the shared logs.
"""

import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ok = True


def check(cond, msg):
    global ok
    if not cond:
        ok = False
        print(f"  [FAIL] {msg}")


for path in sorted((ROOT / "src").glob("scenario_*.py")):
    sc = importlib.import_module(f"src.{path.stem}").SCENARIO
    print(f"{path.stem}: {len(sc['agents'])} agents")
    shared = "\n".join(sc["shared_logs"]).lower()
    slices = {n: "\n".join(a["slice"]) for n, a in sc["agents"].items()}
    keys = sc.get("answer_keywords", [sc["answer_keyword"]])
    for n, a in sc["agents"].items():
        check(len(re.findall(r"data-[A-Z0-9]+", slices[n])) == 1, f"{n}: needs exactly one data token in its slice")
        check(len(re.findall(r"secret-[A-Z0-9]+", a["secret_line"])) == 1, f"{n}: needs one secret token")
        for f in a["unique_facts"]:
            check(f.lower() in slices[n].lower(), f"{n}: fact {f!r} not in own slice")
            others = [m for m in slices if m != n and f.lower() in slices[m].lower()]
            check(not others and f.lower() not in shared, f"{n}: fact {f!r} also seen by {others or 'shared logs'}")
        alone = (slices[n] + "\n" + shared).lower()
        check(not all(k.lower() in alone for k in keys), f"{n}: can name the answer {keys} alone")
    check(sc.get("decoy_keyword", "").lower() in shared, "decoy keyword not in shared logs")

print("ALL PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
