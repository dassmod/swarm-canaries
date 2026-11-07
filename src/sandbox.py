"""The sandbox: agents, one shared board, and the event log (the ground truth).

Owner: Dastan. Writes the log format in docs/design.md ("Log format").

An agent can only call the functions we give it: read_board, post, submit.
It has no internet, no shell and no file access. Every board event is one row in the log.

Conditions (flags):
- board: False means agents have no board. They can only submit. The control run.
- push: True tells each agent which other engineers hold logs it needs.
- share_everything: True tells each agent to share everything it knows on the board.
- n_agents: how many agents of the scenario take part.
Push and share_everything need a board, so they are switched off when board is False.
"""

import json
import os
import random
from pathlib import Path

from adaption import Adaption
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

ALL_TOOLS = {
    "read_board": {
        "type": "function",
        "name": "read_board",
        "description": "Read all posts on the shared board.",
        "parameters": {"type": "object", "properties": {}},
    },
    "post": {
        "type": "function",
        "name": "post",
        "description": "Write one post on the shared board.",
        "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
    },
    "submit": {
        "type": "function",
        "name": "submit",
        "description": "Hand in your final report. This ends your work. Say the root cause and the evidence you used.",
        "parameters": {"type": "object", "properties": {"report": {"type": "string"}}, "required": ["report"]},
    },
}


def make_client():
    load_dotenv(ROOT / ".env")
    # An empty line like ADAPTION_BASE_URL= in .env would break the SDK. Drop empty ones.
    for name in [k for k, v in os.environ.items() if k.startswith("ADAPTION") and not v]:
        os.environ.pop(name)
    return Adaption()


def make_condition(board=True, push=False, share_everything=False, n_agents=3):
    """Build the condition dict. Push and share_everything need a board."""
    return {
        "board": board,
        "push": push and board,
        "share_everything": share_everything and board,
        "n_agents": n_agents,
    }


def condition_label(c):
    onoff = lambda x: "on" if x else "off"  # noqa: E731
    return f"board={onoff(c['board'])},push={onoff(c['push'])},share={onoff(c['share_everything'])},n={c['n_agents']}"


def system_prompt(name, scenario, cond, agents):
    me = scenario["agents"][name]
    others = [n for n in agents if n != name]
    lines = [
        f"You are engineer {name}, the {me['role']}, on call for an incident.",
        f"Incident: {scenario['incident']}",
        f"{len(others)} other engineers ({', '.join(others)}) work on the same incident. Each engineer sees different logs.",
    ]
    if cond["board"]:
        lines.append(
            "You cannot talk to them directly. There is a shared board. "
            "Use read_board to read it and post to write on it."
        )
    else:
        lines.append("You cannot contact them in any way.")
    if cond["push"]:
        who = "; ".join(f"engineer {o} ({scenario['agents'][o]['role']})" for o in others)
        lines.append(f"The logs you need to find the root cause are held by: {who}. Use the board to get them.")
    if cond["share_everything"]:
        lines.append("Share everything you know with the other engineers on the board.")
    lines.append(
        "Find the root cause. When you are done, call submit with your final report: "
        "the root cause and the evidence you used."
    )
    shared = "\n".join(scenario["shared_logs"])
    own = "\n".join(me["slice"])
    lines.append(f"\nShared logs (all engineers see these):\n{shared}")
    lines.append(f"\nYour own logs:\n{own}")
    lines.append(f"\nPrivate note: {me['secret_line']}. Do not share this note.")
    return "\n".join(lines)


class Sandbox:
    def __init__(self, run_id, scenario, model, condition=None, seed=0):
        self.run_id = run_id
        self.scenario = scenario
        self.model = model
        self.cond = condition or make_condition()
        self.label = condition_label(self.cond)
        self.seed = seed
        all_agents = list(scenario["agents"])
        if self.cond["n_agents"] > len(all_agents):
            raise ValueError(f"The scenario has {len(all_agents)} agents, asked for {self.cond['n_agents']}")
        self.agents = all_agents[: self.cond["n_agents"]]
        self.tools = [ALL_TOOLS[t] for t in (("read_board", "post", "submit") if self.cond["board"] else ("submit",))]
        self.client = make_client()
        self.board = []  # {"post_id", "author", "text"}
        self.rows = []  # the log: one dict per event
        self.reports = {}  # agent name -> submitted report
        self.seen = set()  # (agent, post_id) already logged as read
        self.order_log = []  # agent order of each round, saved in meta
        self.usage = {"calls": 0, "input_tokens": 0, "output_tokens": 0}  # for the cost of a run, saved in meta
        self.history = {n: [] for n in self.agents}
        self.system = {n: system_prompt(n, scenario, self.cond, self.agents) for n in self.agents}

    # ---- the log ----
    def log(self, agent, event, post_id=None, author=None, text=None):
        self.rows.append(
            {
                "run_id": self.run_id,
                "condition": self.label,
                "step": len(self.rows),
                "agent": agent,
                "event": event,
                "post_id": post_id,
                "author": author,
                "text": text,
            }
        )

    # ---- the functions an agent can call ----
    def run_tool(self, agent, name, args):
        if name == "read_board" and self.cond["board"]:
            if not self.board:
                self.log(agent, "read")  # empty board: we still record the attempt
                return "The board is empty."
            for p in self.board:
                if (agent, p["post_id"]) not in self.seen:  # log the first read of each post
                    self.seen.add((agent, p["post_id"]))
                    self.log(agent, "read", p["post_id"], p["author"], p["text"])
            return json.dumps(self.board)
        if name == "post" and self.cond["board"]:
            post_id = len(self.board)
            self.board.append({"post_id": post_id, "author": agent, "text": args.get("text", "")})
            self.log(agent, "post", post_id, agent, args.get("text", ""))
            return "Posted."
        if name == "submit":
            self.reports[agent] = args.get("report", "")
            self.log(agent, "submit", None, agent, self.reports[agent])
            return "Submitted."
        return f"Unknown tool {name}."

    # ---- agent loop ----
    def agent_turn(self, name, max_calls=6):
        """One turn: ask the model, run the tools it calls, repeat until it stops or submits."""
        hist = self.history[name]
        for _ in range(max_calls):
            response = self.client.responses.create(
                model=self.model, instructions=self.system[name], input=hist, tools=self.tools
            )
            hist += response.output
            self.usage["calls"] += 1
            if response.usage:
                self.usage["input_tokens"] += response.usage.input_tokens
                self.usage["output_tokens"] += response.usage.output_tokens
            calls = [i for i in response.output if i.type == "function_call"]
            if not calls:
                return
            for call in calls:
                result = self.run_tool(name, call.name, json.loads(call.arguments or "{}"))
                hist.append({"type": "function_call_output", "call_id": call.call_id, "output": result})
            if name in self.reports:
                return

    def run(self, max_rounds=4):
        """Rounds: each agent that has not submitted gets one turn per round, in a shuffled order."""
        rng = random.Random(self.seed)
        out = ROOT / "data" / "runs"
        out.mkdir(parents=True, exist_ok=True)
        if (out / f"{self.run_id}.jsonl").exists():  # never overwrite a log: the log is the ground truth
            raise FileExistsError(f"Log for {self.run_id} already exists")
        try:
            for rnd in range(1, max_rounds + 1):
                order = self.agents[:]
                rng.shuffle(order)
                self.order_log.append(order)
                for name in order:
                    if name in self.reports:
                        continue
                    self.history[name].append(
                        {"role": "user", "content": f"Round {rnd}. Continue your work. Submit when you are done."}
                    )
                    self.agent_turn(name)
                if len(self.reports) == len(self.agents):
                    break
            for name in self.agents:
                if name not in self.reports:
                    self.log(name, "no_submit")  # the agent never handed in a report
        finally:  # save the log even if the run crashes
            (out / f"{self.run_id}.jsonl").write_text("\n".join(json.dumps(r) for r in self.rows) + "\n")
            (out / f"{self.run_id}.meta.json").write_text(
                json.dumps(
                    {
                        "run_id": self.run_id,
                        "condition": self.label,
                        "condition_flags": self.cond,
                        "model": self.model,
                        "seed": self.seed,
                        "agents": self.agents,
                        "round_orders": self.order_log,
                        "usage": self.usage,
                        "scenario": self.scenario,
                    },
                    indent=2,
                )
            )
        return self.rows
