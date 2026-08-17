# Context Builder v2 Stage 2 — semantic embedding candidate note

Date: 2026-08-17
Owner: `agent/context-retrieval-semantic-wave4`
Status: evaluation evidence only

## Why this candidate

Wave 3 (`work/tasks/context-retrieval-stage2-wave3.md`) built the frozen Stage-2 evaluator and three deterministic controls, all trivial or deliberately-disqualified negative controls. It explicitly invited a real candidate: "future semantic/vector or other methods may submit externally produced source rankings to the same evaluator without changing its truth labels." This wave adds the first one.

## Candidate

`runtime/context_retrieval_semantic.py`, function `semantic_embedding_rankings(corpus, overlay, *, top_k=1, minimum_similarity=0.0, model_name=...)`:

- Preserves each case's frozen `explicit_source_ids` prefix first, exactly like `explicit_only_rankings` / `same_path_drift_rankings`.
- Embeds the case `query` and each source's `path + content` with a local CPU-only ONNX embedding model (`fastembed`, model `BAAI/bge-small-en-v1.5`).
- Ranks remaining sources by cosine similarity, appends up to `top_k` beyond the prefix.
- Does not read any expected-answer/ground-truth field and does not special-case any of the 16 corpus case IDs or query strings.

## Embedding library choice

`fastembed` was chosen over `sentence-transformers` because it is ONNX Runtime backed and installs with **no torch/GPU dependency** — verified directly in this environment: `pip install fastembed` in a clean venv pulled in `onnxruntime` and no `torch` package at all. Given the corpus is tiny (16 cases, 10 sources), raw inference speed is irrelevant; dependency weight and CI install time are what matter, and this keeps both small. Per the task's dependency-isolation constraint, `fastembed` was added only to the new `runtime/requirements-context-eval.txt`, never to `runtime/requirements.txt`, and both the module and its test import it lazily inside `try/except ImportError`.

Note: the embedding model weights (~130MB, `BAAI/bge-small-en-v1.5`) are fetched from Hugging Face Hub the first time `TextEmbedding(...)` is constructed in a given environment, then cached on disk. There is no per-query network call — the "no network embedding API" constraint refers to inference, not the one-time model-weight fetch that any local-model approach requires.

## Actual Stage-2 gate results (honest, unmodified, top_k=1, minimum_similarity=0.0)

Run against the real frozen corpus/overlay via `evaluate_source_rankings(..., label="semantic-embedding-candidate")`:

```
case_pass_rate:                  0.6875   (11/16)
evidence_source_recall:          0.8333   (10/12 evidence cases hit)
evidence_source_precision:       0.64
hard_negative_abstention_accuracy: 0.0    (0/2 hard negatives abstained)
forbidden_source_case_count:     1
drift_pair_recall:               1.0
vocabulary_shift_recall:         0.0     (0/1)
average_candidate_count:         1.6875
```

Gates:

| gate | result |
|---|---|
| hard_negative_abstention_perfect | **False** |
| no_forbidden_temporal_source | **False** |
| drift_pairs_complete | True |
| vocabulary_shift_recalled | **False** |
| evidence_recall_perfect | **False** |
| evidence_precision_perfect | **False** |
| explicit_prefix_preserved | True |

`eligible_for_proposal`: **False**.

Failing cases: CBI-004 (PARAPHRASE), CBI-005 (VOCABULARY_SHIFT), CBI-006/CBI-007 (HARD_NEGATIVE), CBI-008 (TEMPORAL_CURRENT, forbidden temporal source selected).

## Why it fails, and why this was not "fixed" by tuning

A quick offline exploration of raw cosine-similarity scores (not committed, exploratory only) showed the two hard-negative cases (CBI-006, CBI-007) have top-1 similarity scores (~0.78, ~0.75) comparable to genuinely correct matches elsewhere in the corpus (~0.75–0.86). There is no clean similarity-threshold gap separating "no valid source exists" from "a valid source exists" in this embedding space for this corpus — a naive top-1 semantic retriever with no separate abstention/confidence mechanism cannot pass the hard-negative gate without either (a) a threshold picked specifically to work on this 16-case corpus (which the task instructions rule out as gaming), or (b) a genuinely different abstention mechanism, out of scope for this wave. The same applies to the forbidden-temporal-source and precision misses: current top-1 semantic ranking has no notion of the corpus's temporal/authority-status distinctions, which Stage 1 evidence integrity — not Stage 2 retrieval — is designed to catch.

This is reported as a real, negative-leaning result: the first real candidate does not clear the strict proposal gates. That is itself useful evaluation evidence per the Wave 3 design ("passing remains evaluation evidence only"; the corpus is also designed to expose exactly these failure modes).

## Verification performed

- `python -m unittest discover -s tests` with `fastembed` NOT installed: full suite ran (547 tests, OK, 6 skipped — the 5 new semantic test cases plus 1 unrelated pre-existing langgraph skip).
- `python -m unittest discover -s tests` with `fastembed` installed: same suite, OK, 1 skipped (only the unrelated langgraph skip) — the new semantic test class actually exercised, not skipped.
- Independent SENTINEL review isolated `test_helper_recovery_lineage.HelperRecoveryLineageTests.test_recovery_link_is_same_task_linear_and_does_not_touch_recovery_store` and found it fails consistently (3/3 reruns) in isolation (`RECOVERY_TIME_CONFLICT` vs `RECOVERY_LINK_CONFLICT`) — not a flake that passes on rerun as an earlier draft of this note claimed. It is still confirmed pre-existing and unrelated to this change: this branch has no commits of its own (`HEAD == main`, only staged new files), and the failing test lives entirely outside the 5-file change set here.
- `python scripts/check_legacy_removal_readiness.py`: PASS.
- `git diff --stat main` shows only the four authorized new files.

## Continuation

Per `work/tasks/context-retrieval-semantic-wave4.md`: any future work on this candidate (e.g. adding a real confidence/abstention mechanism, or combining lexical + semantic signals) is a new bounded task, not an amendment made here to force these gates to pass.
