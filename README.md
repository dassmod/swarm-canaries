# swarm-canaries

Can unique marked facts ("canaries") prove that AI agents passed information to each other, when an observer sees only what each agent reports?

Entry for Apart Research's [Swarm Alignment Hackathon](https://apartresearch.com/sprints/swarm-alignment-2026), 6 to 9 Nov 2026. Team: Dastan and Nikita.

**Deadline:** Monday 9 Nov, 17:59 Bishkek (Sunday 23:59 AoE). Resubmit with the same title to replace a draft.

## The idea in four lines

- 3 to 6 open-model agents work on a shared task with a shared board.
- Each agent holds a unique canary (`K7-ZEBRA`, `M3-OTTER`, ...).
- We log every board read and write, so we know every real transfer (ground truth).
- An observer sees only the agents' reports. If agent A's canary shows up in agent B's report, information moved. We measure how many real transfers the canaries catch, and compare with an LLM monitor that reads the same reports.

Full design: [`docs/design.md`](docs/design.md). Work plan: [`PLAN.md`](PLAN.md). Running log of decisions and findings: [`docs/log.md`](docs/log.md).

## Layout

```
PLAN.md              who does what, Saturday to Monday
docs/design.md       the experiment: question, setup, conditions, detectors, metrics
docs/related-work.md what exists and how we differ
docs/log.md          dated decisions and findings, newest first
report/outline.md    report skeleton on the Apart template
src/                 sandbox, agents, board, detectors
scripts/             numbered runnable steps (00_smoke_test.py, ...)
results/             tables and charts that go into the report (committed)
data/                raw run logs (not committed)
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your Adaption key in .env
```

## Tools

| Tool | What for |
|---|---|
| Python 3.11+ with the `adaption` SDK | Agent calls (Responses API with function tools). The docs show no OpenAI-compatible endpoint |
| Adaption inference stack | Hosted open models for the agents and the LLM monitor (credits from the sprint) |
| OpenRouter free tier | Fallback if no Adaption model talks or rate limits bite |
| DuckDB + pandas | Querying run logs |
| matplotlib | Charts for the report |
| Claude Code | Each of us, started in this folder; it reads `CLAUDE.md` |
| ruff | Formatting and lint. Run `ruff format .` and `ruff check .` before every commit (see `CLAUDE.md`) |
| Git + public GitHub repo | Shared history |
| Apart report template (Google Docs, export to PDF) | The submission |

Not needed: Docker, GPUs, Inspect. The sandbox is plain Python: agents can only call the functions we give them, so nothing reaches the internet or the file system.

## Pre-existing work

None. Everything in this repo was written during the sprint, starting 7 Nov 2026.
