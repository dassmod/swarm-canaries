# swarm-canaries

If you can read only what each AI agent reports, can you prove that information moved from one agent to another?

Entry for Apart Research's [Swarm Alignment Hackathon](https://apartresearch.com/sprints/swarm-alignment-2026), 6 to 8 Nov 2026 AoE. Team The Bookkeepers: Dastan Modubash and Nikita Stanchenkov. The repository is public.

**Report:** [`report/The_Monitor_Was_Reading_the_Credits.pdf`](report/The_Monitor_Was_Reading_the_Credits.pdf). **Slides:** [`report/The_Monitor_Was_Reading_the_Credits_slides.pdf`](report/The_Monitor_Was_Reading_the_Credits_slides.pdf).

**Deadline:** Monday 9 Nov, 17:59 Bishkek (Sunday 8 Nov, 23:59 AoE). A new submission with the same title replaces the old one.

## The result in five lines

- A harness logs every read on a shared board, so every real transfer between agents is known. 465 runs, incident-triage tasks, one open model (`qwen3.5-397b`).
- A blind LLM monitor caught 98% of transfers on the plain board. It caught 94 to 100% when the report named the source, and 13 to 25% when it did not.
- One report format (cite the id of each log line) cut the blind monitor to 14%, and to 10% on a second monitor model. Nobody was asked to hide.
- The same format raised a token canary from 9% to 100%, because we required the id. When agents knew the ids were checked, the canary fell to 12%.
- An informed monitor, which knows what each agent was given, held at 77 to 79% when agents hid.

All cite and follow-up conditions were chosen after we saw data, so they are exploratory. Limitations are in the report.

## Layout

```
report/              report and slide PDFs, draft.md (the report text), assets/ (project image and slide art)
results/             tables and charts that go into the report
src/                 sandbox, scenarios, ground truth, canary detectors
scripts/             numbered runnable steps, listed below
tests/               fake runs and checks for the detector code
docs/design.md       the experiment: question, setup, conditions, detectors, metrics
docs/scenarios.md    the four incident scenarios
docs/what-we-measure.md   the measures in plain words
docs/related-work.md what exists and how we differ
docs/discussion-talks.md  framing ideas from two sprint talks
docs/log.md          dated decisions and findings, newest first
PLAN.md              the weekend plan, kept as written
data/                raw run logs and monitor outputs, not in git
```

## Scripts

| Script | What it does |
|---|---|
| `00_smoke_test.py` | Checks the model call, a tool call and a two-agent board |
| `01_run_sandbox.py` | Runs one scenario under one condition |
| `02_metrics.py` | Scores the detectors against the log |
| `03_monitor.py` | Runs the LLM monitor (blind, informed, redacted, notrace, neutral) |
| `04_charts.py` | Charts over all conditions |
| `05_run_plan.py` | Runs the whole plan of scenarios, conditions and repeats |
| `06_names.py` | Counts reports and posts that name another engineer |
| `07_robustness.py` | Intervals over runs, names against recall, format compliance, baselines |
| `08_oracle.py` | Baseline: one agent with all the logs |
| `09_figures.py` | Figures 1 and 2 of the report |
| `10_cover.py`, `11_cover_cone.py` | Project image options and slide backgrounds |
| `12_build_report.py`, `13_build_slides.py` | Build the report and slide PDFs |

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your Adaption key in .env
```

## Reproduce

The tables in `results/` are in the repository. The raw logs in `data/` are not, and are available on request. A new run needs an Adaption key and produces new data, so its numbers will differ from the report.

```bash
.venv/bin/python scripts/05_run_plan.py --repeats 15 --series cite
```

```bash
.venv/bin/python scripts/03_monitor.py --workers 8
```

```bash
.venv/bin/python scripts/02_metrics.py
```

```bash
.venv/bin/python scripts/07_robustness.py
```

## Tools

| Tool | What for |
|---|---|
| Python with the `adaption` SDK | Agent and monitor calls (Responses API with function tools) |
| Adaption inference stack | Hosted open models: `qwen3.5-397b` for agents and monitor, `gemma-4-31b-it` for the second monitor |
| matplotlib, numpy, Pillow | Charts and slide art |
| markdown, Google Chrome (headless) | Report and slide PDFs |
| ruff | Formatting and lint (see `CLAUDE.md`) |
| Claude Code | Code, analysis and report drafts. The report states how it was used |

The sandbox is plain Python: agents can only call the functions we give them, so nothing reaches the internet or the file system. All tokens, passwords and logs in the scenarios are invented.

## Pre-existing work

None. Everything in this repository was written during the sprint, starting 7 Nov 2026.
