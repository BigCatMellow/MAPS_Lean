# Task: exact submission-attempt run lineage Wave 3

- Status: `IN_PROGRESS`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/submission-run-lineage-wave3`
- Risk: `MEDIUM`
- Dependency: A2 / PR #49 exact base head `ed865be729cf2d15663258fd46c9296ea32d28e7`

## Goal

Add exact append-only `(task_id, submission_count) -> run_id` attribution when and only when the submitter explicitly supplies a run. Keep legacy submissions without an explicit run valid and unlinked rather than guessing.

## Boundaries

- Do not add mutable `run_id` to the current `task_submissions` row.
- Do not infer a run from timestamps, one-run-only state, worker identity, session identity, or message prose.
- Do not require a run for legacy/existing submit callers.
- Do not change review authority or submission evidence semantics.
- Do not add communication or wait-state logic.
- Do not modify A2/PR #49's branch.

## Required semantics

1. `submission_run_links` is append-only and keyed by exact `(task_id, submission_count)`.
2. `submit_task(..., run_id=None)` preserves current behavior and creates no run link.
3. `submit_task(..., run_id=...)` validates the explicit immutable run inside the existing submission transaction.
4. The supplied run must exist, belong to the same task, and be owned by the submitting worker.
5. The supplied run's immutable task revision must equal the current canonical task revision.
6. Link insertion and submission-count mutation commit or roll back together.
7. Invalid explicit run evidence must leave task status, current submission row, and submission count unchanged.
8. Multiple submission attempts may link to the same run when explicitly supplied; the attempt key remains distinct.
9. Legacy/unlinked attempts remain `UNKNOWN` for run attribution; they are never backfilled heuristically.
10. Trace exposes all explicit submission/run links and states that coverage is incomplete when historical attempts are unlinked.

## Acceptance criteria

- [ ] table is append-only and references canonical task/run rows.
- [ ] SQLite prevents a link whose run belongs to another task.
- [ ] exact first submission link is inserted atomically with submission count 1.
- [ ] explicit retry creates count 2 link without rewriting count 1.
- [ ] omitted run leaves submission valid and unlinked.
- [ ] missing/wrong-task/wrong-worker/stale-revision run is rejected before submission mutation commits.
- [ ] invalid link conflict rolls the submission transaction back.
- [ ] no timestamp or single-run inference exists.
- [ ] trace exposes explicit links with incomplete coverage semantics.
- [ ] focused adversarial tests pass.
- [ ] full Runtime CI passes on exact PR head.

## Verification

```text
python -m unittest tests.test_submission_run_lineage tests.test_state_store -v
```

Review required: `INDEPENDENT_REVIEW` before merge/completion.

## Stop

Stop after exact submission-attempt attribution is durable, atomic, traced, and tested. Communication task/run joins (A4c) and explainable waits (A4d) remain separate tranches.
