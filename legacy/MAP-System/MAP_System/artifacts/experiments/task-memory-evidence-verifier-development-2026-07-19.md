# TASK-261 Query-Global Evidence and Local Verifier Development

## Outcome

The query-global selector is worth carrying into one fresh holdout, but it is not ready for integration. Conditioned on the task IDs already chosen correctly by TASK-260's blinded evaluator, one shared three-source budget exposed 16 of 20 exact expected sources (80%), compared with 15 of 20 (75%) from the frozen two-sources-per-task selector. It did this without changing the retriever and without allowing compound queries to expand to four evidence slots.

The visible Pi verifier is not viable for this job. It rejected all three negative queries, but positive task recall was only 8/12 (66.7%), positive task precision was 8/13 (61.5%), exact expected-source visibility was 9/20 (45%), and only one of eight positive queries received an exact, non-contradictory task set. It must not be placed in the retrieval, abstention, task-selection, or evidence-selection path.

This is known-data development, not fresh evidence. TASK-260 truth and packets were reused only after its blinded evaluator had already selected all 12 expected tasks with no extras. No production, startup, routing, UI, canonical authority, embedding, model, or external-service integration occurred.

## Question Isolated by This Experiment

TASK-260 established two different facts:

1. task retrieval was already strong on fresh data (12/12 expected tasks, including all four compound sets); and
2. a fixed evidence layout hid 5/20 exact expected sources and its numeric abstention rule was unreliable.

TASK-261 therefore did not rerun the task-retrieval question. It supplied the task set selected by the prior evaluator and asked a narrower question: given the right tasks, can a single query-wide budget expose better proof? This isolates evidence allocation from task retrieval and avoids claiming that known labels constitute a second holdout.

## Deterministic Query-Global Selector

The disposable selector in `MAP_System/scripts/task_memory_packet_selector.py` imports but does not modify the frozen FTS5/RRF engine. For each query and already-selected task set it:

- enumerates every registered source linked to those tasks;
- excludes task snapshots unless the question explicitly asks for a task record, owner, status, or declared scope;
- scores lexical overlap, bounded clause coverage, requested proof roles, global source rank, and selected-task linkage;
- prefers resolved current-unique evidence, penalizes unresolved and current-shared evidence, and records temporal mode and SHA-256;
- reads at most 64 KiB from executable/code-like candidate files to obtain a small tie signal, without placing source bodies into model context;
- greedily rewards newly covered terms, clauses, tasks, and requested roles while penalizing redundancy and duplicate file hashes; and
- returns at most three sources across the entire task set. Role diversity is a soft reward, not a quota, so two complementary tests can both be selected.

The generated packets are evidence-only audit packets, not full discovery packets. Their total estimated size was 2,916 tokens for eight positives (median 380 per query). The selector's median development runtime was 8.397 ms after the disposable index was built.

## Known-Data Comparison

| Query | Fixed exact sources | Query-global exact sources | Exact total | Query-global observation |
|---|---:|---:|---:|---|
| F1 | 2 | 2 | 3 | Replaced the desired combat parity report with the plausible state parity report. |
| F2 | 2 | 2 | 2 | Preserved both exact sources while using one extra implementation lead. |
| F3 | 2 | 3 | 3 | Added the missing supervisor outcome report; this is the net improvement. |
| F4 | 2 | 2 | 3 | Chose a second executable runner test instead of the exact advisory-lane outcome report. |
| F5 | 1 | 1 | 2 | Still preferred graph/run-test leads over the exact governing `AGENTS.md`. |
| F6 | 2 | 2 | 3 | Preferred the attention verification artifact over the exact shared `chat.js`. |
| F7 | 2 | 2 | 2 | Exact. |
| F8 | 2 | 2 | 2 | Exact, with the queue as the third lead. |
| **Total** | **15 (75%)** | **16 (80%)** | **20** | Three-source query-wide budget. |

The four remaining exact misses are not all obviously bad retrieval leads. State-parity, executable runner tests, graph helper-accounting documentation, and the attention-popup verification artifact are relevant alternatives. The strict metric is still useful because it exposes a real limitation: lexical overlap cannot consistently distinguish the precise proof role intended by an independently authored question from another legitimate source with similar vocabulary. Direct tuning to those four known paths would overfit this development set.

## Visible Pi Capability-Verifier Run

`helper-index-local-verifier-bero` ran in a visible WezTerm tab using the displayed `qwen2.5-coder:7b-16k` model. It received one frozen TASK-260 packet per hcom message and was prohibited from repository search, file reads, writes, tools, prior-packet reliance, or action. No repository command or file events were observed, and every response self-reported that it accessed no outside context. The helper was stopped and its tab closed after the 11th packet.

### Measured result

| Measure | Result |
|---|---:|
| Expected positive task IDs found | 8/12 (66.7%) |
| Precision among returned positive task IDs | 8/13 (61.5%) |
| Exact positive task sets without extras/contradiction | 1/8 |
| Negative queries correctly rejected | 3/3 |
| Exact expected-source visibility | 9/20 (45%) |
| Exact-source precision | 9/14 (64.3%) |
| Median visible response latency | 3 seconds |
| Total visible response latency | 68 seconds |
| Responses returned through requested hcom path | 0/11 |
| Automatic context compactions | 2 |

Four positive responses combined a task ID with `NO MATCH`, which is logically contradictory. F3 returned three task IDs despite the two-task ceiling. Every response substituted the hcom input event number for the packet's F/N identifier. F7 invented an absolute source path that was not present in the packet. The terminal's cumulative display reached approximately 114k input tokens for 16,138 estimated packet tokens because the conversation retained prior turns and compacted twice.

The three correct negative rejections show a narrower possible use: a local model might help challenge obviously absent capabilities after a stronger deterministic or core-agent decision. This run does not support giving it decision authority, and its positive unreliability plus context growth makes even that narrow use premature without a reset-per-query transport and a much stricter structured-output gate.

## Abstention and Verification Tradeoff

TASK-260's numeric abstention rule was only 7/11 correct, including false positives on all three negatives. The prior core evaluator corrected all 11 decisions. TASK-261 shows that replacing the numeric rule with this Pi verifier would trade one failure for another: negative rejection improves, but positive retrieval is damaged and response-contract compliance collapses.

The next abstention candidate should therefore remain deterministic and auditable. A useful design is a clause-level capability checklist over the top task candidates: require an implementation-bearing task to cover the requested capability clauses, require negation/absence language to have direct support, and abstain when the packet contains only lexical neighbors. It should be evaluated on fresh negatives and hard near-misses; this development run does not justify a threshold.

## Temporal and Evidence Limitations

- Source files are current projections. A `current_shared` source may contain changes made after an older task, even though the task/source link is real.
- The selector records current SHA-256 values but still lacks task-time source snapshots or hashes. Task-time fingerprints remain the highest-value temporal follow-up.
- Exact-source truth is intentionally narrow and may penalize another valid proof source. Future truth sets should distinguish required source, acceptable substitute, and merely relevant lead.
- This run is task-conditioned. It says nothing new about autonomous task selection.
- Evidence-only packet size cannot be compared directly with TASK-260's full candidate packets because it omits the six candidate task summaries.
- The 64 KiB code-prefix tie signal is deterministic and token-free for a model, but it increases local file I/O and reflects current content.

## Candidate Freeze for a Fresh Holdout

The following candidate is frozen for later fresh evaluation:

- selector: `MAP_System/scripts/task_memory_packet_selector.py`
- selector SHA-256: `1c33ed6c84189168e1cb1abc793495f3beeaebac872bb57d8d1a5d2f4e68b8f6`
- focused tests: `MAP_System/tests/test_task_memory_packet_selector.py`
- test SHA-256: `cbadf1c6a6dcb2e108fc769d2a0556d0368b22f05a26a5828a5ba907b1544d86`
- budget: three sources per query across the selected task set
- use: evidence allocation only, after task selection
- no Pi verifier in the candidate path

A later holdout must use new tasks and independently authored questions, freeze acceptable source alternatives before scoring, and preserve this selector and its tests byte-for-byte until evaluation is complete. The candidate should be rejected if it loses task-conditioned source coverage, expands context materially, hides unresolved paths, or makes current shared content look like task-time evidence.

## Verification

- 21 focused and adjacent tests passed: selector (7), frozen retriever (9), and frozen holdout harness (5).
- All four frozen TASK-259/TASK-260 code/test hashes match their recorded values in the JSON result.
- Generated JSON validates and contains the selector comparison, per-query source choices, frozen-input hashes, Pi decisions, latency, scope evidence, context observations, and verdict.
- Helper note: `MAP_System/inbox/helpers/helper-index-local-verifier-2026-07-19.md`.
- Machine-readable result: `MAP_System/artifacts/experiments/task-memory-evidence-verifier-development-2026-07-19.json`.
- Generated evidence packets: `MAP_System/artifacts/experiments/task-memory-query-global-packets-2026-07-19/`.

## Recommendation

Carry the deterministic query-global selector—not Pi—into one fresh task-conditioned evidence holdout. In parallel, add task-time source hashes or snapshots and design an auditable clause-level capability/abstention gate. Do not add embeddings yet: fresh task retrieval is already 12/12, and the measured failures are proof selection, temporal attribution, and abstention rather than semantic task recall.
