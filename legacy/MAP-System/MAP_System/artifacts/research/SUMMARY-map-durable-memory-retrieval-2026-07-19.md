<!-- hpom: file: artifacts/research/SUMMARY-map-durable-memory-retrieval-2026-07-19.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: codex-lab-kiri -->
<!-- hpom: status: RESEARCH_COMPLETE -->
<!-- hpom: last_verified: 2026-07-19 -->
<!-- hpom: verified_against: primary IR papers, official SQLite FTS5 documentation, TASK-256/TASK-257 evidence, and TASK-258 development regression -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Research Summary

Summary ID: SUMMARY-MAP-DURABLE-MEMORY-RETRIEVAL-2026-07-19

- owner: codex-lab-kiri
- task: TASK-258
- date: 2026-07-19
- recommendation: **build a measured, source-level, two-stage local retriever;
  add semantic retrieval only as a separately scored fallback**

## Question

How should MAP retrieve useful prior task and evidence context without making
agents load broad history or trust an opaque index?

## Answer

MAP's problem is a small, heterogeneous, evidence-sensitive information
retrieval problem. It is not ordinary document search and it is not solved by
putting all history into a vector database.

The index must do four distinct jobs:

1. recover all plausible historical tasks under vocabulary mismatch;
2. distinguish task intent from implementation, verification, review, release,
   and outcome evidence;
3. handle questions that contain more than one historical cause;
4. abstain when MAP has no trustworthy answer.

Research and the first two MAP pilots point to this staged design:

```text
canonical MAP files
  -> disposable source fingerprints
  -> local sparse first-stage retrieval
  -> fuse full-query and subquery rankings
  -> evidence-aware/diverse reranking
  -> confidence/abstention gate
  -> compact agent packet
  -> bounded source confirmation when needed
```

This preserves MAP's file/database authority model. The index is derived state,
can be rebuilt, and never becomes the source of truth.

## 1. What established retrieval research implies for MAP

### 1.1 A heterogeneous holdout matters more than a single good score

The [BEIR benchmark](https://arxiv.org/abs/2104.08663) was created because
retrievers that look strong in narrow, homogeneous tests can generalize poorly
across domains and task types. It found BM25 to be a robust baseline, while
reranking and late-interaction methods often improved effectiveness at greater
computational cost.

MAP implication:

- keep author/evaluator independence;
- test old and recent work, code and prose, single-task and compound queries;
- include hard distractors and genuine no-match questions;
- report results per query class instead of hiding failures in one average;
- never treat the curated TASK-256 score as production evidence.

For source code specifically, the
[CodeSearchNet challenge](https://arxiv.org/abs/1909.09436) frames the core
problem as bridging natural-language queries and technical code vocabulary and
uses function documentation as mechanically available query-like language.
This supports indexing module docstrings, function/class names, and focused test
names as separate fields instead of treating an entire source file as plain
text.

### 1.2 Sparse lexical retrieval is still the right first baseline

[SPLADE](https://arxiv.org/abs/2107.05720) shows why sparse retrieval remains
attractive: it retains explicit terms and inverted-index efficiency while
learned expansion can bridge vocabulary gaps. The result does not mean MAP
should deploy SPLADE now; it means exact-match sparse retrieval is a strong,
inspectable base, and vocabulary expansion is a distinct optional layer.

MAP already uses SQLite. The official
[SQLite FTS5 documentation](https://sqlite.org/fts5.html) provides:

- BM25 relevance ranking with per-column weights;
- Porter stemming;
- trigram substring matching;
- prefix, phrase, boolean, column-filter, and NEAR queries;
- snippets/highlights and integrity checks;
- contentless or external-content indexes.

MAP implication: the hand-written token counter in TASK-256 through TASK-258 is
an experiment harness, not the final sparse engine. The next implementation
baseline should be a disposable FTS5 source index with weighted fields.

Environment check on 2026-07-19: MAP's SQLite 3.45.1 reports `ENABLE_FTS5` and
successfully executed in-memory Porter/BM25 and trigram-index probes. This path
does not require adding a new package or network service.

### 1.3 Dense retrieval can help, but does not automatically generalize

[Dense Passage Retrieval](https://arxiv.org/abs/2004.04906) demonstrated large
gains over a BM25 baseline on several open-domain QA datasets. However, BEIR's
cross-domain evaluation found that dense and learned sparse systems can lose
ground out of distribution. [ColBERTv2](https://arxiv.org/abs/2112.01488)
improves retrieval through token-level late interaction and compression, but it
still adds model, storage, and operational complexity.

MAP implication:

- embeddings are a candidate recall channel, not a new authority;
- evaluate dense retrieval on the same frozen MAP truth set;
- fuse dense and sparse ranks rather than comparing incompatible raw scores;
- only keep the semantic channel if it recovers lexical misses without harming
  no-match precision, latency, privacy, or rebuild simplicity;
- prefer a local model/sidecar if that experiment is eventually authorized.

### 1.4 Rank fusion is safer than adding unrelated scores

[Reciprocal Rank Fusion](https://research.google/pubs/reciprocal-rank-fusion-outperforms-condorcet-and-individual-rank-learning-methods/)
combines independent ranked lists using rank position instead of assuming their
scores share a scale. In the reported experiments, the fused ranking
outperformed individual systems and Condorcet fusion.

MAP implication: retrieve independently with the full question, each bounded
subquery, task fields, source fields, and eventually sparse/semantic channels;
then use reciprocal-rank fusion. Do not add a BM25 score, fuzzy-match count, and
embedding cosine value as though the numbers meant the same thing.

### 1.5 Multi-part questions require staged retrieval

[IRCoT](https://aclanthology.org/2023.acl-long.557/) found that one-shot
retrieve-and-read was insufficient for multi-step questions and improved both
retrieval and answers by interleaving reasoning and retrieval. MAP does not
need a free-form chain-of-thought retriever to use the core lesson.

MAP implication:

1. split explicit connectors and clauses deterministically;
2. retrieve each subquestion independently;
3. fuse candidate ranks;
4. detect uncovered subquestions;
5. only then consider one bounded model-generated follow-up query.

This is more controllable than letting a model recursively search without a hop
or token budget.

### 1.6 Evidence diversity should be an objective, not an accident

Maximal Marginal Relevance was introduced to balance relevance with novelty,
rather than return a list of near-duplicates. The original
[MMR paper](https://dl.acm.org/doi/10.1145/290941.291025) motivates selecting
items that are useful to the query and add information beyond what has already
been selected.

MAP implication: evidence slots should cover different proof roles. For a
behavior question, a task record plus two generic planning artifacts is weaker
than one implementation source and one focused test. For an authority question,
current policy plus verification is stronger than two code files.

TASK-258 currently implements a deterministic role-diversity approximation.
An FTS5 version can make this explicit as constrained reranking or MMR over
source relevance and role/path similarity.

### 1.7 Abstention must be evaluated as a risk/coverage tradeoff

[SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html) treats the
reject option as part of the prediction problem and evaluates the relationship
between coverage and error. MAP's current score threshold is not calibrated;
it is only a testable starting point.

MAP implication:

- every holdout needs real negative/no-match questions;
- measure false-positive retrieval on negatives;
- measure recall separately at each abstention threshold;
- surface `no strong match` rather than filling the packet with weak history;
- calibrate on one development set, then freeze before the holdout.

### 1.8 Generative expansion is useful but risky

[Query2doc](https://aclanthology.org/2023.emnlp-main.585/) reports gains from
LLM-generated query expansion for sparse and dense retrieval. A later broad
study, [When do Generative Query and Document Expansions Fail?](https://aclanthology.org/2024.findings-eacl.134/),
found that expansion often helps weaker retrievers but can harm stronger ones.

MAP implication: do not let an LLM silently write synonyms into durable
fingerprints. If expansion is tested, preserve the original query, label the
generated expansion, rank it as an independent channel, fuse results, and
measure whether it improves frozen MAP queries.

## 2. Recommended MAP index architecture

### 2.1 Retrieval unit: registered source, not only task

Use one source document plus a separate task/source relationship. Suggested
retrieval fields:

| Field | Indexed? | Purpose |
|---|---|---|
| source_id | No | Stable derived-row identity |
| task_id | Filter/return | Link back to authority |
| path | Weighted | Exact filenames, symbols, subsystem terms |
| evidence_role | Filter/return | Scope, implementation, test, review, outcome, etc. |
| task_title | Weighted high | Concise intent |
| task_goal | Weighted medium | Wider intent and constraints |
| source_title | Weighted high | Heading, module docstring, HTML title |
| source_summary | Weighted high | Bounded deterministic extract |
| symbols | Weighted medium | Function/class/test/control names |
| project/workstream/status | Filter/low weight | Routing and lifecycle context |
| source_hash | No | Staleness/rebuild detection |
| exists/broken | No | Visible path health |

Task-level candidates are produced by aggregating source rows back to task IDs.
Evidence ranking stays source-level.

### 2.2 First-stage retrieval

Build a disposable SQLite FTS5 index using weighted BM25 fields. Compare at
least:

- `unicode61` baseline;
- Porter stemming for normal word inflection;
- a separate trigram/path channel for filenames, typos, and code identifiers;
- full query and deterministic subqueries;
- task-field and source-field rankings.

Fuse ranked lists with RRF. Keep top-K generous enough for recall, then rerank
to a small packet.

### 2.3 Second-stage reranking

Rerank candidate sources using:

- lexical relevance to source title/summary/symbols;
- path and task linkage;
- lifecycle and broken-reference state;
- evidence role requested by the question;
- diversity from already selected evidence;
- coverage of separate subquestions.

Return match reasons and source descriptions. Never return an unexplained
opaque score as the only justification.

### 2.4 Optional semantic channel

Only after the FTS5/RRF baseline is frozen, test a local embedding or
late-interaction channel on the same corpus. Keep it if it adds unique correct
hits. Record:

- incremental recall;
- negatives incorrectly pulled above the abstention threshold;
- index size and rebuild time;
- query latency;
- local model/resource requirements;
- privacy and availability behavior when the model is down.

Semantic failure must degrade to sparse retrieval, not make memory unavailable.

### 2.5 Temporal attribution and shared mutable sources

The TASK-100–159 corpus contains 336 registered output references but only 210
unique paths. Forty-six paths are registered by more than one task;
`shared/current-state.md` is registered by 15 tasks and `shared/decisions.md` by
14. Nineteen registered references are currently broken.

This creates a historical-attribution hazard: reading a shared file today and
copying its current description into every task that ever registered it can
make an old task appear to contain changes added much later.

The durable index should therefore separate:

- `source_documents`: one current fingerprint per unique path;
- `task_source_links`: the fact that a task registered that path;
- `task_evidence_snapshots`: immutable task-specific artifacts or a source
  version/hash known at completion time, when available.

For historical task retrieval, current content from a multiply registered
mutable path should be downweighted or excluded from task semantics unless MAP
can tie that content version to the task. Unique release/review/test artifacts
and task-specific reports are stronger historical attribution. Shared mutable
documents remain useful as current-state sources, but should not be cloned into
many historical fingerprints as if their present text existed at every task's
completion.

[Temporal JSON Keyword Search](https://doi.org/10.1145/3654980) formalizes the
difference between searching current documents and searching a chosen temporal
slice of versioned JSON. MAP does not need that complete system immediately,
but it reinforces the requirement that historical task retrieval must name the
version or time semantics it is using. If future task/release events reliably
record Git commits or source hashes, the index can retrieve the task-time
version; until then, it should label current-content evidence honestly.

## 3. Evaluation contract

Report at least:

- task recall@K and precision of evaluator selections;
- evidence recall@K, exact evidence precision, and reciprocal rank;
- complete-answer rate for compound questions;
- no-match precision, false-positive rate, and risk versus coverage;
- per-query packet tokens and confirmation-source tokens;
- index bytes, rebuild time, query latency, and stale/broken path count;
- helper/model scope adherence;
- performance by query class and age, not only aggregate averages.

Maintain two sets:

- development regression: known questions used to debug implementation;
- fresh holdout: authored after implementation freeze and never used for tuning.

## 4. Implementation sequence

1. Complete TASK-258's fresh source-fingerprint/decomposition holdout.
2. If it generalizes, replace the hand-written scorer with SQLite FTS5/BM25 and
   RRF while preserving the same packet/evaluation boundary.
3. Add explicit negative-query calibration and evidence reciprocal-rank metrics.
4. Only if frozen lexical misses remain, run a bounded local semantic-channel
   comparison.
5. Integrate nowhere until repeated holdouts meet a written adoption threshold
   and a separate review approves operational cost and failure behavior.

## 5. Current evidence watermark

Before the new TASK-258 holdout was authored, the known TASK-257 development
regression improved from:

- 7/9 to 9/9 expected task visibility;
- 10/16 to 16/16 expected evidence visibility.

That is encouraging but **not holdout evidence**. The owner knew the TASK-257
truth while debugging generic decomposition and evidence-slot behavior. The
implementation must now be frozen and challenged by a new independent author
and evaluator.

## Confidence

High for the recommended next lexical architecture and evaluation discipline:
the recommendation is supported by primary retrieval research, official SQLite
capabilities, local FTS5 probes, and three MAP experiments. Moderate for exact
field weights, rank-fusion constants, evidence-diversity penalties, and
abstention thresholds; those remain empirical questions for fresh holdouts.

## Confidence decays after

Re-evaluate this recommendation after either of these events:

- two new heterogeneous MAP holdouts produce materially different failure
  patterns;
- MAP changes its canonical task/source/version data model or SQLite runtime;
- 2027-01-19, if no intervening evaluation has refreshed the evidence.

## Open questions

- Which FTS5 field weights and tokenizers maximize frozen task/source recall?
- How should MAP capture task-time source hashes or versions without increasing
  authoring friction?
- What negative-query count is sufficient to calibrate abstention safely?
- Does a local semantic channel recover unique lexical misses after FTS5/RRF,
  and at what privacy, storage, and latency cost?

## Downstream effect

Use this summary to shape the next bounded FTS5/BM25 and reciprocal-rank-fusion
experiment. Preserve source documents separately from task/source links, label
current versus historical evidence, and retain the independent-author/blinded-
evaluator protocol. Do not use this research alone as approval to integrate a
retriever into startup, routing, Command Center, or automatic agent workflows.
