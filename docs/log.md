# Log

Decisions and findings, newest first. One line each, with who wrote it.

| Date | Who | Entry |
|---|---|---|
| 2026-11-07 | Nikita | Proposals: two tokens per agent (data and secret); "used" means a task fact, the token is a detector; `PLAN.md` gets a who-does-what section, log format first, cost split |
| 2026-11-07 | Nikita | `PLAN.md`: added time-zone note (Nikita UTC-3) and proposed changes to priorities and Nikita's blocks, to decide in block 0 |
| 2026-11-07 | Nikita | Added `docs/what-we-measure.md`: plain-words summary of the question, ground truth, three detectors and the numbers we report |
| 2026-11-07 | Nikita | Proposals for block 0, added to `design.md` as options, not decisions: incident-triage task with token canaries; hidden-profile variant; two-level ground truth (read, used); LLM monitor to Must; leak rate plus "share everything" condition. HiddenBench added to `related-work.md` |
| 2026-11-07 | Dastan | Chose C1 (canary tokens), with Nikita's design: three detectors scored against the board log |
| 2026-11-07 | Nikita | Quick search for prior work: no direct repeat found; closest is "Audit the Whisper" (see `related-work.md`) |
| 2026-11-07 | Dastan | Data check on swarmtraces.org: no timestamps, so timing-based detection was dropped as an option |
