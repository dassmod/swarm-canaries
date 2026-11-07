# CLAUDE.md

Research code for Apart Research's Swarm Alignment Hackathon: canary tokens as proof of information transfer between agents. Two people use this repo: Dastan and Nikita. Read `README.md`, `PLAN.md` and `docs/design.md` before changing code.

## Rules for everyone

- Only weekend work is judged. Anything written before 7 Nov 2026 is marked as pre-existing in the README.
- No fabricated numbers. Every figure in the report comes from a script in `scripts/` that can be re-run.
- The repo stays private. Never commit `.env` or anything in `data/`.
- Agents in the sandbox can only call the functions we give them. No internet, no shell, no file access for agents.
- Log every board read and post as one JSONL row. The log is the ground truth.
- Record decisions and findings in `docs/log.md`, newest first.
- Never use em-dashes or en-dashes in prose.

## When working with Dastan

- Dastan is learning this field and this code while building it. Build first, then name the concept on what just happened.
- Before explaining a result, ask Dastan to say what he sees in it, wrong parts included. Then correct the gap.
- Explanations: short sentences, one idea each, bold anchor lines, a table for any trace. Full depth, simple words.
- When Dastan does not follow a piece of code: explain the primitive it stands on directly, show one input giving two different results side by side, then hand his own code back for him to walk. Never restate a sentence that did not land; go one layer down.
- Do not do the whole task silently. Propose the next step, say why, then do it.
