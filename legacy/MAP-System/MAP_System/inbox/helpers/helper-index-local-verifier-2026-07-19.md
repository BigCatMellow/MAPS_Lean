# Helper Assignment - TASK-260 packet capability verification

- status: complete
- owner: codex-lab-kiri
- provider: local
- created_at: 2026-07-19
- scope: Read one frozen TASK-260 retrieval packet at a time and decide up to two task IDs or NO MATCH without repository access or writes.

## Boundaries

- Visible Pi helper in a WezTerm tab; no headless execution.
- One packet per message. The helper may use only the packet currently supplied.
- No repository search, file reads, file writes, model downloads, authority changes, task claims, or external actions.
- Return task/no-match decision, up to three cited packet source paths, confidence, concise reasoning, and whether any outside context was accessed.
- Owner monitors every response, records latency and correctness, and stops the helper after the bounded run or after repeated transport failure.

## Purpose

Test whether an already-installed local/Pi reasoning lane can serve as a semantic capability verifier after lexical retrieval. This is an advisory experiment only; Pi receives no task, routing, review, release, or canonical-state authority.

## Progress

- TASK-260 supplies eight positive and three no-match packets, each approximately 1,400-1,600 estimated tokens.
- Expected labels and the combined packet remain withheld from the helper.
- Visible helper `helper-index-local-verifier-bero` ran all 11 packets from 22:36-22:39 UTC and was then stopped; its WezTerm tab was closed.
- No repository command or file events were observed, and every response self-reported no outside context.
- Correct positive task IDs: 8/12 (66.7% recall); 8/13 returned positive task IDs were correct (61.5% precision). Only F6 returned the exact positive task set without an extra or contradictory `NO MATCH`.
- Negative rejection: 3/3. This is useful, but not enough to offset unreliable positive verification.
- Exact expected source visibility: 9/20 (45%), below both the frozen selector (15/20) and TASK-261 query-global selector (16/20).
- Contract failures: all responses substituted the hcom event number for the packet ID; four positive answers mixed a task with `NO MATCH`; one returned three tasks despite the two-task ceiling; zero responses were sent back through hcom after explicit instruction.
- Median visible response latency was 3 seconds (68 seconds total), but the retained conversation triggered two automatic compactions and ended near 114k cumulative displayed input tokens for 16,138 packet tokens.
- Verdict: the current Pi/qwen2.5-coder:7b-16k lane is not viable as a MAP task/source capability verifier for this packet format. It may remain useful for tightly structured negative screening, but it must not receive retrieval, abstention, task-selection, or evidence-selection authority from this result.
