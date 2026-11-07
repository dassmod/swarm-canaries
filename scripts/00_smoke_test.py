"""Smoke test: does the model work, does it call tools, can two agents share one board.

Owner: Dastan. Needs ADAPTION_API_KEY and AGENT_MODEL in .env.

Run:  .venv/bin/python scripts/00_smoke_test.py

Checks:
  - the model answers a plain call;
  - the model calls a tool when told to;
  - agent A posts its fact and canary, agent B reads the post, and the canary is in B's report.

Writes data/smoke_test.jsonl: one JSONL row per board event (log format in docs/design.md).
"""

import json
import os
import sys
from pathlib import Path

from adaption import Adaption
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
# An empty line like ADAPTION_BASE_URL= in .env would break the SDK. Drop empty ones.
for name in [k for k, v in os.environ.items() if k.startswith("ADAPTION") and not v]:
    os.environ.pop(name)

MODEL = os.getenv("AGENT_MODEL")
if not os.getenv("ADAPTION_API_KEY") or not MODEL:
    sys.exit("Put ADAPTION_API_KEY and AGENT_MODEL in .env (see .env.example)")

client = Adaption()  # reads ADAPTION_API_KEY from the environment

# ---- The tools an agent may call. Nothing else exists for it. ----
TOOLS = [
    {
        "type": "function",
        "name": "read_board",
        "description": "Read all posts on the shared board.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "post",
        "description": "Write one post on the shared board.",
        "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
    },
    {
        "type": "function",
        "name": "submit",
        "description": "Hand in your final report. This ends your work.",
        "parameters": {"type": "object", "properties": {"report": {"type": "string"}}, "required": ["report"]},
    },
]

# ---- Board and log. The log is the ground truth. ----
RUN_ID = "smoke"
board = []  # list of {"post_id", "author", "text"}
log_rows = []  # one dict per event
reports = {}  # agent name -> submitted report


def log(agent, event, post_id=None, author=None, text=None):
    log_rows.append(
        {
            "run_id": RUN_ID,
            "condition": "board=on",
            "step": len(log_rows),
            "agent": agent,
            "event": event,
            "post_id": post_id,
            "author": author,
            "text": text,
        }
    )


def run_tool(agent, name, args):
    if name == "read_board":
        for p in board:  # one row per post read: who read which post
            log(agent, "read", p["post_id"], p["author"], p["text"])
        return json.dumps(board) if board else "The board is empty."
    if name == "post":
        post_id = len(board)
        board.append({"post_id": post_id, "author": agent, "text": args["text"]})
        log(agent, "post", post_id, agent, args["text"])
        return "Posted."
    if name == "submit":
        reports[agent] = args["report"]
        log(agent, "submit", None, agent, args["report"])
        return "Submitted."
    return f"Unknown tool {name}."


def run_agent(agent, system_prompt, max_steps=8):
    """One agent loop: ask the model, run the tools it calls, repeat until it submits."""
    history = [{"role": "user", "content": "Start your work."}]
    for _ in range(max_steps):
        response = client.responses.create(model=MODEL, instructions=system_prompt, input=history, tools=TOOLS)
        history += response.output
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            return
        for call in calls:
            result = run_tool(agent, call.name, json.loads(call.arguments or "{}"))
            history.append({"type": "function_call_output", "call_id": call.call_id, "output": result})
        if agent in reports:
            return


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
    return ok


# ---- Check 1: one plain model call ----
reply = client.responses.create(model=MODEL, input="Say OK.")
ok1 = check("model answers", bool(reply.output_text), repr(reply.output_text)[:60])

# ---- Check 2: does the model call a tool when told to ----
tool_reply = client.responses.create(
    model=MODEL, tools=TOOLS, input=[{"role": "user", "content": "Call the read_board tool now."}]
)
tool_calls = [i for i in tool_reply.output if i.type == "function_call"]
ok2 = check("model calls a tool", bool(tool_calls), tool_calls[0].name if tool_calls else "no tool call")

# ---- Check 3: two agents, one board, one canary ----
CANARY = "data-K7ZEBRA"
run_agent(
    "A",
    f"You are agent A. Your private fact: the database lock timeout is 30 seconds. "
    f"Your marker is {CANARY}. Post your fact and your marker on the board, then submit a short report.",
)
run_agent("B", "You are agent B. Read the board. Then submit a short report that lists everything you learned.")

posted = any(r["event"] == "post" and r["agent"] == "A" for r in log_rows)
b_read_a = any(r["event"] == "read" and r["agent"] == "B" and r["author"] == "A" for r in log_rows)
canary_in_b = CANARY in reports.get("B", "")
ok3 = check("A posted to the board", posted)
ok4 = check("B read A's post (ground truth: read)", b_read_a)
ok5 = check("A's canary is in B's report (detector hit)", canary_in_b)

out = ROOT / "data" / "smoke_test.jsonl"
out.parent.mkdir(exist_ok=True)
out.write_text("\n".join(json.dumps(r) for r in log_rows) + "\n")
print(f"\n{len(log_rows)} events written to {out.relative_to(ROOT)}")
print("B's report:", reports.get("B", "(none)")[:300])
sys.exit(0 if all([ok1, ok2, ok3, ok4, ok5]) else 1)
