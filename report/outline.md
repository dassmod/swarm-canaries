# Report outline

Apart template, up to 8 pages without references and appendices. Abstract 150 to 250 words. Fill from `docs/` and `results/`, then rewrite in our own words.

1. **Introduction.** The Hugging Face incident: agents coordinated on a channel nobody intended. The observer's problem: you see reports, not the channel. Our question in one sentence.
2. **Related work.** From `docs/related-work.md`: what exists, the gap.
3. **Method.** Sandbox, task, canaries, board log as ground truth, conditions, detectors, metrics.
4. **Results.** Recall and false alarms per detector and condition. The spread chart. Counts of runs stated plainly.
5. **Discussion.** What canaries can and cannot see. Where the LLM monitor goes wrong. What a lab could deploy.
6. **Limitations.** Toy sandbox, few agents, open models, small number of runs.
7. **Appendix: Limitations, Dual-Use and Ethical Considerations.** Required. Canary bait vs prompt injection; sandbox only.
8. **References.** Only papers we opened.

Title (draft): *Canaries in the Swarm: Proving Information Transfer Between AI Agents from Their Reports Alone*
