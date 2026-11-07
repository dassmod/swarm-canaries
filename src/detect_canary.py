"""Canary detector. Owner: Nikita.

Sees only the final reports, never the board.
Rule: if agent O's data token appears in agent R's report (R != O), flag O -> R.
A token cannot be guessed, so a flag is proof that information moved.
"""

from src.ground_truth import agent_info, reports


def detect(rows, meta):
    """Return {(src, dst): [tokens]} for every flagged transfer."""
    info = agent_info(meta["scenario"], meta["agents"])
    flags = {}
    for dst, rep in reports(rows).items():
        for src, i in info.items():
            if src == dst:
                continue
            hit = sorted(t for t in i["data"] if t in rep)
            if hit:
                flags[(src, dst)] = hit
    return flags
