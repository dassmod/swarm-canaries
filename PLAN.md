# Plan

Two people, Saturday 7 to Monday 9 Nov. Times are Bishkek (UTC+6). Nikita is in UTC-3, 9 hours behind: Bishkek 15:00 is 06:00 for Nikita, the 17:59 deadline is 08:59. Roles can swap any time; write it in `docs/log.md` when they do.

- **Dastan: sandbox and runs.** Agents, board, task, conditions, running batches.
- **Nikita: detectors and analysis.** Canary detector, ground-truth metrics, LLM monitor, charts.
- **Both: report.**

## Priorities

| Must | Should | Could |
|---|---|---|
| Sandbox with board and log; canary detector; recall and false alarms vs ground truth; board vs no board; push vs no push | LLM monitor on the same reports; 3 vs 6 agents; canary placement (in task data vs private note) | Lead-follow test ("talked or just alike"); second model; natural-fact canaries |

Cut from the right when time runs short.

**Nikita's proposal for the priorities (decide in block 0):**

| Change | Why |
|---|---|
| LLM monitor: Should to Must | The headline ("monitor mistakes likeness for communication") needs it |
| Leak rate: add to Must | Free: read straight from the board log, no detector needed |
| Two-level ground truth (read, used): add to Must | Part of the metrics script; recall against "read" alone looks worse than it is |
| "Share everything" instruction vs normal: add to Should | Does the leak rate rise with accuracy (HiddenBench says accuracy rises) |

## Saturday

| Block | Dastan | Nikita |
|---|---|---|
| **0. Kickoff (30 min, together)** | Clone repo, `.env` with Adaption key | Clone repo, `.env` |
| | **Decide together:** the agent task, canary placement, the exact ground-truth definition. Options in `docs/design.md`. Write the decision in `docs/log.md`. | |
| **1. Smoke test (about 1 h)** | `scripts/00_smoke_test.py`: one model call on Adaption; does it support tool calling; two agents, one board, one canary | Log schema (one JSONL row per event); canary detector; metrics script tested on a hand-made fake log. Proposal: metrics count both "read" and "used" transfers, plus leak rate. If incident triage is chosen: Nikita drafts scenario 1 (three log slices, decoy cause, true cause, one token per agent) for Dastan to plug in |
| **2. Sandbox core (about 2 h)** | 3 agents in a loop on the chosen task, board read/post/submit, every event logged | LLM monitor prompt draft; first chart (who read whose posts, over time) |
| **Checkpoint** | Do agents use the board? If not: add Rowan's push. Still silent: change the task. Silence after both is a result, but a weak one. Log it. | |
| **3. First real results (about 2 h)** | Conditions as config flags: board on/off, push on/off, n agents (proposal: plus "share everything" on/off) | Run detector and metrics on the first real logs; first numbers in `results/` |
| **Evening** | One full run per must-condition | Report outline filled: question, setup, related work |

Optional talk: Justin Shenk, "Modeling Agent Swarms: A Field Guide", Saturday 19:00 (recording in the sprint Schedule tab).

## Sunday

| Block | Dastan | Nikita |
|---|---|---|
| **Morning** | Batch runs: repeats per must-condition (check credits first) | Metrics per run, aggregate table, first charts |
| **Midday** | Should-conditions (6 agents, canary placement; proposal: "share everything") | LLM monitor on all runs; compare with canaries; leak rate per condition |
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
