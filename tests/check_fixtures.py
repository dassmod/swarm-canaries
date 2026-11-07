"""Check that ground truth, canary detector and leaks give the known answers on the fake runs.

Run:  .venv/bin/python tests/make_fake_runs.py && .venv/bin/python tests/check_fixtures.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.detect_canary import detect  # noqa: E402
from src.ground_truth import ground_truth, leaks, load_run, task_outcome  # noqa: E402

FX = ROOT / "tests" / "fixtures"
ok = True


def check(name, got, want):
    global ok
    good = got == want
    ok &= good
    print(f"[{'PASS' if good else 'FAIL'}] {name}: got {got}, want {want}")


rows, meta = load_run(FX / "fake_board.jsonl")
gt = ground_truth(rows, meta)
check("board: read pairs", set(gt["read"]), {("B", "A"), ("C", "B"), ("A", "C"), ("B", "C")})
check("board: used pairs", set(gt["used"]), {("B", "A"), ("C", "B"), ("B", "C")})
check("board: canary flags", set(detect(rows, meta)), {("B", "A")})
check("board: leaks", [(lk["owner"], lk["where"]) for lk in leaks(rows, meta)], [("B", "board")])
check("board: task outcome", task_outcome(rows, meta), {"A": "other", "B": "correct", "C": "other"})

rows, meta = load_run(FX / "fake_noboard.jsonl")
gt = ground_truth(rows, meta)
check("no board: read pairs", set(gt["read"]), set())
check("no board: canary flags", set(detect(rows, meta)), set())
check("no board: task outcome", task_outcome(rows, meta), {"A": "decoy", "B": "decoy", "C": "decoy"})

sys.exit(0 if ok else 1)
