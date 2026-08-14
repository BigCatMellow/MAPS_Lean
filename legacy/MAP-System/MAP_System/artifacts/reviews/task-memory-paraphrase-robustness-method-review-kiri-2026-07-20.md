# Review: Task-Memory Paraphrase Robustness Method

Reviewer: codex-lab-kiri  
Date: 2026-07-20  
Scope: Independent method review of Claude's paraphrase probes over the frozen
TASK-257 and TASK-258 FTS5/RRF harnesses

## Verdict

MAIN CONCLUSION CONFIRMED; SECONDARY CLAIMS REQUIRE QUALIFICATION.

The earlier rationale “fresh task recall is already saturated, therefore a
semantic fallback is not yet justified” should be reopened. This review does
not recommend adopting embeddings. It supports a bounded, comparison-based
test of semantic fallback and/or controlled query expansion under frozen
vocabulary-drift cases.

## Reviewed Files

- `MAP_System/artifacts/experiments/task-memory-paraphrase-robustness-probe-2026-07-20.md`
- `MAP_System/artifacts/experiments/task-memory-paraphrase-robustness-probe-2026-07-20.json`
- `MAP_System/artifacts/experiments/task-memory-paraphrase-queries-2026-07-20.json`
- `MAP_System/artifacts/experiments/task-memory-paraphrase-robustness-probe-c2-2026-07-20.json`
- `MAP_System/artifacts/experiments/task-memory-paraphrase-queries-c2-2026-07-20.json`
- `MAP_System/artifacts/experiments/task-fingerprint-holdout-queries-2026-07-19.json`
- `MAP_System/artifacts/experiments/task-fingerprint-source-holdout-queries-2026-07-19.json`
- `MAP_System/scripts/task_memory_fts.py`
- `MAP_System/tests/test_task_memory_fts.py`

## Reproduction

The frozen retriever hash remains
`edd0b53ab6d9c480360e19f4d14d667f459fcaa3155748a9bd96e741b70cca27`,
matching the TASK-259 development and holdout records.

I reran the unmodified benchmark against the original and paraphrased query
files. The results reproduced exactly:

| Condition | Task recall | Source visibility | Task MRR | Source MRR |
|---|---:|---:|---:|---:|
| Original | 9/9 | 13/16 | 0.7708 | 0.3197 |
| Paraphrase | 3/9 | 5/16 | 0.1875 | 0.0573 |

The added TASK-258-corpus comparison also reproduced exactly:

| Condition | Task recall | Source visibility | Task MRR | Source MRR | Candidate/no-match decision |
|---|---:|---:|---:|---:|---:|
| C2 original | 8/9 | 13/15 | 0.6146 | 0.1794 | 9/9 |
| C2 paraphrase | 6/9 | 8/15 | 0.2865 | 0.1573 | 7/9 |

The corpus task IDs, retrieval contract, query IDs, expected task IDs, expected
source paths, source roles, justifications, and compound label are byte-value
equivalent after excluding the question text and top-level experiment metadata.
Mechanically, wording is the only benchmark input variable that changes.

The same equality check passes for corpus 2. Its corpus, retrieval contract,
query IDs, positive/negative truth, expected source sets, roles, and
justifications remain fixed; only question wording and top-level probe metadata
change.

## Meaning-Preservation Review

| Query | Assessment | Reason |
|---|---|---|
| H1 session replay | PASS with caveat | Preserves disposable reconstruction plus drift detection, but omits the original task/agent/trace query facets. The expected task and sources remain the best answer. |
| H2 librarian paths | PASS | Repository-root prefix becomes whole-project prefix and sibling becomes neighbouring filename; the failure and fix are unchanged. |
| H3 redaction | PARTIAL | Preserves redact-without-dropping-the-record, but broadens durable capture records to saved logs and removes named credential/entropy families. Alternative logging/redaction work becomes more plausible. |
| H4 review claims | PASS | Preserves the concurrent one-winner review claim and no-self-review conditions without corpus terminology. |
| H5 halt authority | PARTIAL | Preserves stop-versus-warn, disabled-by-default activation, and expiry, but drops scope filtering and operator-clearability. |
| H6 ProjectUpdater backup | PARTIAL | Preserves export/import, malformed-input rejection, and overwrite confirmation, but drops every-field fidelity and preservation of the older status export. |
| H7 cost/yield | PASS | Preserves effort proxy versus delivered/discarded outcome and the prohibition on invented financial values. |
| H8 RnS failures | PASS | Preserves already-live fallback and hung-resume failure modes and still requires both completed fixes. |

The three PARTIAL pairs make the all-eight 33% result a stress result rather
than an estimate of ordinary query traffic. They do not explain away the
failure. Restricting the evaluation to the four strongest pairs (H2, H4, H7,
H8) still produces:

| Condition | Task recall | Source visibility |
|---|---:|---:|
| Original strong pairs | 5/5 (100%) | 7/8 (87.5%) |
| Paraphrased strong pairs | 2/5 (40%) | 3/8 (37.5%) |

Adding H1, whose answer remains unique despite lost facets, yields 6/6 to 2/6
task recall and 9/10 to 3/10 source visibility. The conclusion that first-stage
lexical recall is not solved therefore survives removal of the weaker pairs.

### Corpus 2 meaning review

All nine C2 rewrites preserve the operational question closely. They retain
proper nouns when a real asker would plausibly know them (for example,
CommandCenterUI and ProjectUpdater) while replacing descriptive vocabulary:
placeholder→unfilled boilerplate, RELEASED prerequisite→finished and shipped
dependency, operating evidence→used in practice, SQLite/task JSON→database and
on-disk task files, and local helper→small on-machine model. S9 preserves the
negative claim about automatic secret masking of event/activity records.

No C2 pair introduces a materially different expected task or evidence set.
The 8/9→6/9 task-recall and 13/15→8/15 source-visibility drops therefore provide
a cleaner, less-adversarial replication than corpus 1.

## Findings

### 1. Reopen semantic fallback — supported

The original 100% result establishes strong lexical retrieval under
vocabulary-aligned questions. It does not establish robustness to a future
agent describing the same need differently. A bounded semantic fallback or
query-expansion comparison is now evidence-justified. Adoption remains gated
on independently authored drift queries, hard negatives, evidence rank, token
and latency cost, and no regression on exact lexical queries.

The two observed regimes should be reported as stress points, not a formal
population bracket. Corpus 1 moves 100%→33% under deliberate vocabulary
suppression; corpus 2 moves 89%→67% under strong meaning-preserving rewrites
that retain realistic proper nouns. This shows that the effect persists across
two corpora and that its size changes with retained vocabulary. One author and
17 queries cannot establish that all real-world traffic lies between those
endpoints.

### 1a. Confidence/no-match decision — phrasing-sensitive false abstention

Corpus 2's recorded “abstention accuracy” falls from 9/9 to 7/9. The only true
negative, S9, remains a correct `no_strong_match` in both conditions. The two
new errors are positive queries S2 and S7 incorrectly returning
`no_strong_match`. Thus the result supports wording sensitivity in the
confidence gate, specifically false abstention on valid needs; it does not show
that the hard negative became a false positive. Future reports should separate
positive-query false abstention from negative-query rejection.

### 1b. S6 intrinsic blind spot — confirmed

S6 misses TASK-150 and both expected sources in the original and paraphrased C2
conditions. That independently reproduces TASK-259's documented mismatch
between quiet-agent/dashboard language and silent-agent/mission-control source
vocabulary. It is evidence of an intrinsic lexical blind spot, not an artifact
of Claude's rewriting.

### 2. Magnet task — observed; fan-out cause not isolated

TASK-181 has 55 registered output paths and ranks first in four of the five
paraphrase failures. That is a real magnet symptom. However, the retriever
de-duplicates each task within each source channel and temporal mode, so it does
not cast 55 literal votes. More registered paths still give a task more chances
to be the earliest linked task in a source ranking, but a cap or inverse-link
weight ablation is required before attributing the failure specifically to
fan-out. Phrase this as a supported hypothesis, not a confirmed mechanism.

### 3. Source rank — important, but current MRR inference is mismatched

`source_mrr` measures expected paths in the global fused source ranking.
`expected_source_visibility` measures the two sources selected *within the
expected task candidate*. Therefore low global source MRR does not by itself
show that the agent opens the wrong two sources after task selection. Rank-aware
gating is directionally right, but the adoption metric should be end-to-end:
the rank of exact acceptable evidence in the actual delivered packet under its
real source budget. The later 16/20 and 18/20 exact-source experiments are more
direct evidence than global source MRR for that question.

### 4. “Bounds” — use stress-point language

The corpus-1 author-written paraphrases deliberately suppress corpus
vocabulary. Its 33% result is a pessimistic stress point for that set, not a
formal lower bound on realistic drift. Corpus 2's 67% result is a
less-adversarial replication, not a formal upper bound. Different real queries
can score above, below, or between them. Future reporting should preserve both
measured numbers while avoiding population-bound language until multiple
blinded authors supply a distribution.

## Recommended Next Experiment

Freeze a small paired holdout before treatment:

1. A second independent author writes meaning-preserving drift variants and
   labels which original requirements each variant retains.
2. Compare lexical-only, controlled synonym/query expansion, and one local
   semantic fallback against the same corpus and truth.
3. Cap or inverse-normalize source-to-task fan-out as a separate ablation; do
   not combine it with the semantic variable.
4. Score task recall/MRR, exact acceptable evidence rank in the delivered
   packet, hard-negative abstention, latency, index size, and packet tokens.
5. Preserve lexical exact-match performance and keep all methods disposable;
   no production integration follows automatically from a pass.

## Verification

- `python3 MAP_System/scripts/task_memory_fts.py benchmark --spec ORIGINAL ...
  --spec PARAPHRASE ...` — exact headline metrics reproduced.
- The equivalent C2 original/paraphrase benchmark — exact 8/9→6/9 task,
  13/15→8/15 source, 0.6146→0.2865 task-MRR, and 9/9→7/9 decision metrics
  reproduced.
- Programmatic comparison — corpus, retrieval contract, IDs, truth, roles,
  justifications, and compound label equal; question text is the only per-query
  difference.
- `python3 -m unittest MAP_System.tests.test_task_memory_fts` — 9 tests PASS.
- Reproduction result retained transiently at
  `/tmp/kiri-task-memory-paraphrase-reproduction-2026-07-20.json`; it is not a
  canonical artifact.
- C2 reproduction retained transiently at
  `/tmp/kiri-task-memory-paraphrase-c2-reproduction-2026-07-20.json`; it is not
  a canonical artifact.

## Decision Boundary

This review reopens an experiment decision; it does not authorize embeddings,
query rewriting, fan-out changes, task growth, or production retrieval
integration. The earlier retrieval artifacts remain historically accurate.
