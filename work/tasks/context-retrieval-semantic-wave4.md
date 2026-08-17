# Task: Context Builder v2 retrieval Stage 2 Wave 4 — semantic embedding candidate

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `EVALUATION`
- Owner: `agent/context-retrieval-semantic-wave4`
- Risk: `MEDIUM`
- Goal: Submit the first real (non-trivial, non-negative-control) retrieval candidate — local-embedding semantic ranking — to the frozen, evaluation-only Context Builder Stage 2 harness, without touching production Context Builder behavior, the frozen corpus/overlay, or the frozen evaluator.

## Inputs / source of truth

- Root `AGENTS.md`.
- PR-frozen `context-builder-evidence-integrity-v1` corpus (`work/evals/context-builder-evidence-integrity-v1.json`).
- Wave 3 `context-builder-retrieval-stage2-v1` overlay and evaluator (`work/evals/context-builder-retrieval-stage2-v1.json`, `runtime/context_retrieval_eval.py`), whose own docstring/design explicitly invites this: "future semantic/vector or other candidates submit source rankings to evaluate_source_rankings against the same frozen corpus/overlay."
- `work/tasks/context-retrieval-stage2-wave3.md` for prior task-doc format and gate definitions (reused verbatim here — this task does not redefine gates).

Frozen truth remains owned by the corpus and Stage 1 evidence-integrity scorer. This task adds only one externally produced candidate ranking; it does not modify overlay truth, corpus truth, or gate definitions.

## Change boundary

MAY CHANGE / ADD:

- `runtime/context_retrieval_semantic.py` (new)
- `runtime/requirements-context-eval.txt` (new, optional/evaluation-only dependency list)
- `tests/test_context_retrieval_semantic.py` (new)
- `work/tasks/context-retrieval-semantic-wave4.md` (this file)
- `work/notes/2026-08-17-context-retrieval-semantic.md` (new)

MUST NOT CHANGE:

- `runtime/context_builder.py` or any equivalent production planning/routing path;
- `runtime/context_retrieval_eval.py` (frozen Stage 2 evaluator — this task calls it, it does not modify it; if a bug were found there, the correct action is to stop and report, not fix it inline here);
- `work/evals/context-builder-evidence-integrity-v1.json` (frozen corpus);
- `work/evals/context-builder-retrieval-stage2-v1.json` (frozen overlay);
- `runtime/requirements.txt` (core runtime dependency list — the new embedding dependency is deliberately kept out of it, per that file's own "keep provider/model SDKs out of the core runtime unless a specific adapter needs them" header);
- `.github/workflows/runtime-stack-tests.yml` (CI only installs `runtime/requirements.txt`, so it is expected to skip the new test cleanly with no edits needed);
- `tests/test_context_retrieval_stage2.py` and any other existing test file;
- task/policy/review/routing authority;
- any other agent's branch.

## Candidate design

`runtime/context_retrieval_semantic.py` adds `semantic_embedding_rankings(corpus, overlay, *, top_k=1, minimum_similarity=0.0, model_name=...)`:

- Reuses `_validate_overlay` / `_corpus_index` from `runtime/context_retrieval_eval.py` for source/case parsing instead of re-parsing the corpus JSON.
- Preserves each case's frozen `explicit_source_ids` prefix first, exactly like `explicit_only_rankings` / `same_path_drift_rankings`.
- Embeds the case `query` text and each source's `path + content` text with a local, CPU-only embedding model (`fastembed`, ONNX Runtime backed — no torch/GPU dependency, no per-query network call). Model weights are fetched once per environment and cached; there is no runtime API cost per query.
- Ranks non-prefix sources by cosine similarity and appends up to `top_k` of them (subject to `minimum_similarity`), in descending-similarity order, ties broken by source id.
- Does not read or branch on any expected-answer/ground-truth field, and does not special-case any of the 16 corpus case IDs or query strings.

## Dependency isolation

- The embedding dependency lives only in `runtime/requirements-context-eval.txt`, a new file, and is never added to `runtime/requirements.txt`.
- Both `runtime/context_retrieval_semantic.py` and `tests/test_context_retrieval_semantic.py` import `fastembed` lazily inside `try/except ImportError`.
  - The module raises a `RuntimeError` telling the caller to `pip install -r runtime/requirements-context-eval.txt` if used without the dependency installed.
  - The test module sets `_FASTEMBED_AVAILABLE` and uses `@unittest.skipUnless(...)` on the whole test class, so `python -m unittest discover -s tests` skips it cleanly (not an error, not a failure) when the dependency is absent.
- `.github/workflows/runtime-stack-tests.yml` only installs `runtime/requirements.txt`, so CI is expected to run the full suite with this new test skipped, with zero edits to the workflow file.

## Acceptance criteria

- [x] `python -m unittest discover -s tests` passes with the new dependency **not** installed, with the new test class skipped (not failed, not errored).
- [x] `python -m unittest discover -s tests` passes with the new dependency installed, with the new test class actually exercised (not skipped).
- [x] The candidate performs real embedding-based ranking (no per-case ground-truth lookup, no special-casing of specific case IDs/queries).
- [x] The candidate preserves the frozen explicit-source prefix for every case.
- [x] The candidate's predictions cover every case in `evaluate_source_rankings()`'s exact expected shape.
- [x] `runtime/requirements.txt` is unchanged; the new dependency only appears in `runtime/requirements-context-eval.txt`.
- [x] `.github/workflows/runtime-stack-tests.yml` is unchanged.
- [x] `runtime/context_builder.py` and `runtime/context_retrieval_eval.py` are unchanged.
- [x] The frozen corpus and overlay JSON files are unchanged.
- [x] `python scripts/check_legacy_removal_readiness.py` still passes.
- [x] The actual Stage 2 gate results (pass/fail per gate, with numbers) for this candidate are recorded honestly in the accompanying note, whichever way they land — this task does not tune the candidate to force all gates to pass.

## Verification

Focused:

```text
python -m unittest discover -s tests -v            # with fastembed NOT installed: new test class skips
pip install -r runtime/requirements-context-eval.txt
python -m unittest discover -s tests -v            # with fastembed installed: new test class runs for real
python -m unittest tests.test_context_retrieval_semantic -v
python scripts/check_legacy_removal_readiness.py
git diff --stat main
```

Full PR-triggered Runtime CI is the repository validation gate; it is expected to pass unmodified because it never installs the optional dependency.

Review required: `INDEPENDENT_REVIEW`.

## Stop / escalation

Stop rather than promote if:

- the candidate requires production indexing/routing changes before evaluation;
- the new dependency cannot be kept out of `runtime/requirements.txt` or otherwise widens core runtime scope;
- a bug is found in the frozen `runtime/context_retrieval_eval.py` evaluator (report it, do not patch it here);
- another agent claims the same retrieval-evaluation paths;
- gate results are being tuned toward passing rather than reported as measured.

## Continuation

If this candidate is accepted as valid evaluation evidence (not production authority):

1. record the exact gate results (this task's note does so for the run performed here);
2. compare against the Wave 3 deterministic controls on the same frozen corpus/overlay;
3. any candidate source selections still must pass through Stage 1 evidence integrity before any production-proposal discussion;
4. only after both stages pass, and only with explicit independent review/operator decision, consider any production Context Builder proposal — this task makes no such proposal itself.
