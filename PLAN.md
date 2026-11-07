# Plan

Two people, Saturday 7 to Monday 9 Nov. Times are Bishkek (UTC+6). Nikita is in UTC-3, 9 hours behind: Bishkek 15:00 is 06:00 for Nikita, the 17:59 deadline is 08:59. Roles can swap any time; write it in `docs/log.md` when they do.

- **Dastan: sandbox and runs.** Agents, board, task, conditions, running batches.
- **Nikita: detectors and analysis.** Canary detector, ground-truth metrics, LLM monitor, charts.
- **Both: report.**

## Who does what, in one picture (Nikita's addition)

```
Nikita: scenario --> Dastan: sandbox + runs --> board logs + agent reports --> Nikita: detectors + numbers
```

| Dastan | Nikita |
|---|---|
| Sandbox: agents in a loop, the board, every read and post logged | Scenario content: log slices per agent, decoy and true cause, tokens (if incident triage is chosen; with Jigsaw, Dastan writes the clues) |
| Condition flags: board, push, n agents, "share everything" | Canary detector, LLM monitor prompt |
| Batch runs; hands over logs and reports | Metrics against the log: recall, false alarms, leak rate; charts and tables |

**First thing to agree:** the log format (fields of one JSONL row). Dastan's sandbox writes it, Nikita's scripts read it.

**While the sandbox is not ready, Nikita does not wait:** writes scenario 1, makes a fake log by hand, builds the detector and metrics on it. Real logs then drop straight in.

**Costs:** each of us uses our own Adaption credits ($500 per participant, sign up with the sprint email). Dastan's key for the agents, Nikita's key for the LLM monitor. If one runs out, the other runs batches. Keys stay in each person's own `.env`, never shared or committed. Anything paid from our own cards (closed-model APIs) only if we both agree first; then we split it.

## Priorities

| Must | Should | Could |
|---|---|---|
| Sandbox with board and log; canary detector; LLM monitor; recall and false alarms vs ground truth (two levels, read and used); leak rate; board vs no board; push vs no push | "Share everything" vs normal; 3 vs 6 agents; canary placement | Lead-follow test ("talked or just alike"); second model; natural-fact canaries |

Cut from the right when time runs short.

**Decided 7 Nov (block 0):** LLM monitor, leak rate and two-level ground truth moved to Must; "share everything" added to Should. Why: the headline needs the monitor; leak rate is free from the board log; recall against "read" alone looks worse than it is. Reasons in `docs/design.md`.

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
