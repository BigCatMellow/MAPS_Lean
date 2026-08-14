# Synthesis Note

Synthesis ID: SYN-0003
Project: MAP
Related insights:
- INS-0030
- `artifacts/experiments/conversation-notes-ei-triage-intake-2026-07-19.md`
- `artifacts/experiments/task-memory-evidence-verifier-development-2026-07-19.md`
- `artifacts/experiments/task-memory-capsule-development-2026-07-19.md`

Date: 2026-07-19
Created by: codex-lab-kiri
Status: CLARIFIED

## Pieces being combined

### Piece A

- a: The measured MAP pilots already find the correct fresh task 12/12 times and find an exact source 18/20 times with structured capsules. The remaining errors are not one generic “search” problem: they separate into proof-location, source-type, negative-boundary, acceptable-substitute, and historical-version failures.

### Piece B

- b: Evidence-verification research evaluates a claim against exact supporting evidence and allows an explicit unknown or insufficient-evidence outcome. That is closer to MAP's remaining problem than whole-document relevance. FEVER is the clearest model for exact evidence plus a `NOT ENOUGH INFO` class; constrained fact verification shows the value of evaluating only against identified evidence.

### Piece C (optional)

- c: Passage- and token-level retrieval research shows several later ways to improve vocabulary matching or ranking—document expansion, contextual term weighting, learned token impacts, late interaction, and graph retrieval—but each adds cost or new failure modes. Because MAP's first-stage recall is already strong, these belong behind a simpler claim-and-anchor experiment, not in front of it.

## New combination


- combo: Claim-addressed evidence units connect task memory to exact, time-correct proof.

## What this makes possible


- opens: A retrieval packet can say not merely “this file is relevant,” but “this exact acceptance claim is supported by this section or symbol in this source version; this separate boundary says what it does not prove.”
- opens: Historical questions can be scored separately from current-source questions instead of silently treating today's file as proof of yesterday's state.
- opens: A semantic model, if later justified, can rerank small evidence units instead of searching the entire repository and consuming a large context budget.

## Why this was not obvious before

- why-hidden: Earlier work was dominated by task discovery and token reduction, so “find the right document” looked like the central objective. Once task recall reached 12/12 and capsules reached 18/20 exact sources, the residual errors became specific enough to reveal a different unit of retrieval: the claim-to-evidence relationship.

## Possible uses

- use: Create release-time claim cards that map one acceptance claim to one or more acceptable evidence sources, exact Markdown sections or code symbols, proof role, source hash, and task-time watermark.
- use: Extract Markdown headings, paragraphs, test names, and code symbols mechanically so retrieval can return a small anchored excerpt rather than a whole file.
- use: Keep limitations, exclusions, and unsupported claims in a distinct negative-boundary channel checked after positive evidence selection.
- use: Maintain a small controlled alias registry for recurring MAP terms such as `RnS` and “reset-and-session supervisor,” without rewriting source prose for keyword stuffing.
- use: Label acceptable evidence *sets* before evaluation. A question may have more than one legitimate source, so scoring only one pathname can create a false miss.

## Method landscape

| Method | Residual problem addressed | Expected value now | Main cost or risk | E/I route |
|---|---|---:|---|---|
| Claim-evidence ledger | Exact proof and claim alignment | High | Authoring and validation | Experiment first |
| Section/paragraph/symbol index | Buried Markdown and non-Markdown code evidence | High | Parsers by file type | Include in experiment |
| Separate negative-boundary channel | False positives from “does not provide” text | High | Two-stage scoring | Include in experiment |
| Task-time hashes or retained snapshots | Historical correctness | High | Storage and version semantics | Measure separately |
| Acceptable evidence-set labels | False evaluation misses | High | Independent labeling | Freeze before treatment |
| Controlled concept/alias registry | Vocabulary mismatch | Medium | Drift and keyword overfitting | Small later pilot |
| Document/query expansion | Vocabulary mismatch at query time | Medium | Hallucinated or noisy expansions | Defer until simple pilot plateaus |
| Learned sparse term impacts or pairwise reranking | Ranking subtle candidates | Low today | Needs a larger labeled set | Park |
| Late-interaction dense retrieval | Semantic matching across wording | Low today | Model, index, dependency, and token costs | Park behind measured trigger |
| Evidence graph / full knowledge graph | Multi-hop claims | Low today | Authority duplication and maintenance | Do not build yet |

## Research grounding

- The [FEVER paper](https://aclanthology.org/N18-1074/) couples claim labels with exact sentence evidence and includes a not-enough-information outcome. Applied to MAP, this supports claim-level proof records and explicit abstention; it does not establish that MAP needs a fact-verification model.
- [Constrained Fact Verification](https://aclanthology.org/2020.emnlp-main.629/) studies verification against identified evidence. Applied to MAP, this reinforces a closed evidence boundary rather than letting a model invent unstated support.
- [Document Expansion by Query Prediction](https://arxiv.org/abs/1904.08375) and [Query2doc](https://aclanthology.org/2023.emnlp-main.585/) show that generated query-like text can bridge vocabulary mismatch. [Doc2Query--](https://arxiv.org/abs/2301.03266) also documents why poor or hallucinated expansions should be filtered, which is the main reason to defer this method here.
- [DeepCT](https://www.cs.cmu.edu/~callan/Papers/sigir20-Zhuyun_Dai.pdf) and [DeepImpact](https://research.engineering.nyu.edu/~suel/papers/impact-sigir21.pdf) show learned contextual term weighting and learned token impacts compatible with inverted indexes. These are later ranking options if MAP earns a sufficient labeled set.
- [ColBERT](https://arxiv.org/abs/2004.12832) supplies a later-interaction semantic retrieval design. It is a plausible later reranker over small units, not evidence that MAP should adopt embeddings now.
- The [RAV evidence-retrieval paper](https://aclanthology.org/2024.findings-acl.551/) supports a staged pattern—cheap candidate pruning followed by a stronger ranker. MAP's local inference is to preserve lexical task discovery and add precision only to the small candidate set.
- [Graph-based FEVER retrieval](https://aclanthology.org/2023.fever-1.4/) shows graph structure can help multi-hop evidence. MAP presently lacks measured multi-hop failures that justify the maintenance and authority risks of a full graph.

## Risks or limits

- risk: Claim cards must remain derived indexes. If an agent treats them as authority, they can preserve stale or simplified claims after the source changes.
- risk: Hand-authored claim cards can leak the evaluation questions into the treatment. The holdout and acceptable evidence sets must be frozen independently before card authoring.
- risk: A source hash can detect drift but cannot by itself reconstruct the historical content. Questions about what existed at task completion require a retained snapshot or another content-addressed source.
- risk: Research findings are analogies applied to MAP's measured failure modes, not proof that the corresponding production methods will work here.

## Recommended next step

- [ ] park
- [x] idea — `IDEA-0023`
- [x] experiment — `EXP-0006` is proposal-only and requires normal approval before execution.
- [ ] escalate
