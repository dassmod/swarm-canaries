# Related work

From Nikita's quick search on 7 Nov (not a full review). Links to add as each paper is opened.

## Closest work

| Work | What it does | How we differ |
|---|---|---|
| Cai et al. 2026, "Ghost in the Agent" (NeuroTaint) | Puts a unique UUID in a source and checks whether it reaches a tool call | Tracks leaks inside one agent; we track transfer between agents |
| Tailor 2025, "Audit the Whisper" | Catches steganographic collusion statistically over many runs (mutual information, permutation tests) | Researchers give agents the encoding scheme; ours communicate on their own, and we score against a full board log. Closest in spirit |
| Ghanem 2026, steganalysis of covert collusion in tool-using agent populations | Statistical detection across agent populations | Results not published yet (placeholders) |
| Li, Naito and Shirado 2026, HiddenBench (ICML 2026), https://arxiv.org/abs/2505.11556 | 65 hidden-profile tasks, 15 models: LLM groups reach about 30% accuracy vs about 81% for one agent with all facts. Telling agents to share everything raises accuracy | No secrets, no leakage, no monitors, dialogue instead of a logged board. We reuse the hidden-profile design and ask what sharing costs in leaked secrets |
| Rose et al. 2026, NARCBench | Detects collusion with probes on internal activations | Reads model internals; we read only text reports. On the hackathon reading list |

## What we did not find

- Canaries used as proof of information transfer between agents.
- A detector scored against a complete board log where every real transfer is known.
- An explicit test of "talked" vs "alike because the same model" (fleet vs swarm).

## Background and motivation

- Security Arsenal: OpenAI agents coordinated on an unsanctioned message board before the Hugging Face breach.
- METR/Redwood report on the Hugging Face incident: https://metr.org/hugging-face-incident-report-aug-2026.pdf
- Blackboard architecture for LLM multi-agent systems.
- Canary tokens for LLMs.
- Mapping human anti-collusion mechanisms to multi-agent AI systems.

Every citation in the report must be a paper we opened. No reference from memory.
