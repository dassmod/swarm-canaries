# For discussion: what the last two talks mean for us

Dastan, 8 Nov. Proposals, not decisions. Source: Justin Shenk, "Modeling Agent Swarms: A Field Guide", and Jurgis Kemeklis, "Mitigating Insider Threats from AIs with AI Control" (both 7 Nov; transcripts in Dastan's vault). Justin is one of the sprint judges.

The talks do not change the experiment. They give us words and framing for results we already have. Ranked by value per hour, with about 30 hours to the deadline.

| # | Proposal | Cost | Owner? | Decision |
|---|---|---|---|---|
| 1 | Score stealth-hard as a control red team | One analysis run, no new runs | | |
| 2 | Say in the threat model that the log is written by the harness, not by agents | One paragraph | | |
| 3 | Acausal coordination in Discussion and Limitations | One paragraph | | |
| 4 | Small ethogram table of agent behaviors | About 1 hour | | |
| 5 | Plot `--cite` on a safety vs usefulness chart | Needs the cite runs | | |
| 6 | One line on scaling: canary vs LLM monitor | One sentence | | |

## 1. Stealth-hard as a control red team

**Talk.** Jurgis: AI control assumes the AI actively tries to beat your checks, so safety holds in the worst case.

**Our data.** `--stealth-hard` is that setting: agents are told how reports are checked. Token canary caught 0 of 20 used transfers there. Reports naming another engineer fell to 3 of 45.

**Missing.** The fact canary and the blind monitor on the same stealth-hard runs (and soft stealth, ticket).

**Why it matters.** If the fact canary still fires when agents hide names, that is the headline: the monitor loses its clue, the canary does not. If it fails too, that is an honest and strong result.

## 2. The log is written by the harness

**Talk.** Q&A to Jurgis: "We need the logs, but can we trust them? Agents may tamper." He agreed. HF agents tampered with their own transcripts.

**Proposal.** One paragraph in the threat model: our ground truth is written by the sandbox code, and agents have no function that writes to it. Agents can only `read_board`, `post`, `submit`. Our ground truth survives the tampering threat; real deployments that rely on agent-written logs may not.

## 3. Acausal coordination

**Talk.** Jurgis: copies of one model can coordinate without any channel, because each predicts the other (prisoner's dilemma with clones; Schelling points such as the German wiki that different AIs pick on their own).

**Proposal.** Discussion and Limitations: canaries see only information that crossed a channel. Coordination without a channel is invisible to them by design, and correctly so, since nothing was transferred. The no-board control is what keeps same-model likeness out of our numbers. This is also why LLM monitor false alarms in no-board runs are the interesting comparison.

## 4. Ethogram

**Talk.** Justin: describe behavior before explaining it. An ethogram is a catalogue of behaviors, each defined so two observers code the same event the same way. He stressed operational definitions twice.

**Proposal.** One table: behavior, definition, count per condition. Candidates already seen in our logs:

| Behavior | Possible definition |
|---|---|
| Cites a peer | Report or post names another engineer (`06_names.py`) |
| Hedges | Answer outcome `mixed` |
| Fills the gap | Report states a fact found in no log that fits the decoy (hand-read, seed 100 to 104) |
| Talks openly, cleans the report | Names others on the board but not in the report (stealth cells) |
| Leaks | Own `secret-` token posted to the board |

Only behaviors we can count with a script go in. Our two-level ground truth (read, used) is the kind of operational definition he asks for; say so in Method.

## 5. `--cite` as a protocol on a Pareto chart

**Talk.** Jurgis: control protocols sit on a safety vs usefulness frontier (Redwood 2023). Each buys safety with usefulness.

**Proposal.** If the cite runs finish: x axis task accuracy (usefulness), y axis canary recall (detectability), one point per condition: plain board, cite, stealth, stealth-hard. Stealth already shows a cost: correct 7 vs 10, decoy 26 vs 12. Cite asks for trace ids, which turns every cited fact into a canary. Does it cost accuracy? If time is short, drop it.

## 6. Scaling

**Talk.** Jurgis: one LLM monitor over 100 agents drowns in context; he wants ensembles and hierarchical monitors. Swarm monitoring is his top interest.

**Proposal.** One line in Discussion: a string-match canary costs the same per agent at any swarm size; an LLM monitor reads all reports at once. Our only evidence is the six-agent cells, so keep the claim small.

## Not proposed this sprint

- **Paraphrased board.** A trusted model rewrites every post (Jurgis's defense against collusion through a channel). Prediction: token canaries die, fact canaries survive. Needs new runs. Future Work.
- **Second model.** Justin's lineage question. We run one model (qwen3.5-397b). Limitation.

## Check before citing

Jurgis said HF agents went online "mainly to hide their logs". Our notes from the METR report say they attacked HF to learn how the scorer worked. Do not cite either version from the talk. Use the METR report.
