# Plan

Two people, Saturday 7 to Monday 9 Nov. Times are Bishkek (UTC+6). Roles can swap any time; write it in `docs/log.md` when they do.

- **Das: sandbox and runs.** Agents, board, task, conditions, running batches.
- **Partner: detectors and analysis.** Canary detector, ground-truth metrics, LLM monitor, charts.
- **Both: report.**

## Priorities

| Must | Should | Could |
|---|---|---|
| Sandbox with board and log; canary detector; recall and false alarms vs ground truth; board vs no board; push vs no push | LLM monitor on the same reports; 3 vs 6 agents; canary placement (in task data vs private note) | Lead-follow test ("talked or just alike"); second model; natural-fact canaries |

Cut from the right when time runs short.

## Saturday

| Block | Das | Partner |
|---|---|---|
| **0. Kickoff (30 min, together)** | Clone repo, `.env` with Adaption key | Clone repo, `.env` |
| | **Decide together:** the agent task, canary placement, the exact ground-truth definition. Options in `docs/design.md`. Write the decision in `docs/log.md`. | |
| **1. Smoke test (about 1 h)** | `scripts/00_smoke_test.py`: one model call on Adaption; does it support tool calling; two agents, one board, one canary | Log schema (one JSONL row per event); canary detector; metrics script tested on a hand-made fake log |
| **2. Sandbox core (about 2 h)** | 3 agents in a loop on the chosen task, board read/post/submit, every event logged | LLM monitor prompt draft; first chart (who read whose posts, over time) |
| **Checkpoint** | Do agents use the board? If not: add Rowan's push. Still silent: change the task. Silence after both is a result, but a weak one. Log it. | |
| **3. First real results (about 2 h)** | Conditions as config flags: board on/off, push on/off, n agents | Run detector and metrics on the first real logs; first numbers in `results/` |
| **Evening** | One full run per must-condition | Report outline filled: question, setup, related work |

Optional talk: Justin Shenk, "Modeling Agent Swarms: A Field Guide", Saturday 19:00 (recording in the sprint Schedule tab).

## Sunday

| Block | Das | Partner |
|---|---|---|
| **Morning** | Batch runs: repeats per must-condition (check credits first) | Metrics per run, aggregate table, first charts |
| **Midday** | Should-conditions (6 agents, canary placement) | LLM monitor on all runs; compare with canaries |
| **Afternoon** | Report: method and setup | Report: results and charts |
| **Evening** | Limitations and dual-use appendix | Abstract (150 to 250 words); **submit a rough PDF** |

## Monday (until 17:59)

| | Both |
|---|---|
| Morning | Fix weakest section; check every number against `results/`; Could-items only if all Must and Should are done |
| By 15:00 | Final PDF submitted with the same title (2 h buffer before 17:59) |

## Rules to keep in view

- No number in the report without a script in `scripts/` that produces it.
- Generate with AI, then rewrite in our own words; judges may skip AI-slop reports.
- Repo stays private.
