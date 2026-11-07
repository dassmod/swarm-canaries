"""Fact canary detector: another agent's unique task fact in a report.

Owner: Nikita.

Sees only the final reports, never the board. The operator knows which logs it gave
to which agent, so it knows each agent's unique facts (ids and numbers such as
"90 connections" or "pay-gw-3").
Rule: if a unique fact of agent O appears in agent R's report (R != O), flag O -> R.

Unlike the data token, a task fact is useful, so agents keep it when they retell.
It can also be guessed (a false alarm), which the no-board runs measure.
Score it against the "read" level only: "used" is defined by the same facts, so
recall against "used" would be circular.
"""

from src.ground_truth import agent_info, has_word, reports


def detect(rows, meta):
    """Return {(src, dst): [facts]} for every flagged transfer."""
    info = agent_info(meta["scenario"], meta["agents"])
    flags = {}
    for dst, rep in reports(rows).items():
        for src, i in info.items():
            if src == dst:
                continue
            hit = [f for f in i["facts"] if has_word(rep, f)]
            if hit:
                flags[(src, dst)] = hit
    return flags
