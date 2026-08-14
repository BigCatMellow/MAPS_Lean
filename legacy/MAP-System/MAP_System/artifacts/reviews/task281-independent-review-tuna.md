# Independent Review: TASK-281 (Immutable Run Manifests Pilot)

- reviewer: helper-review-task-281-tuna
- date: 2026-07-27
- status: APPROVED (no blocking findings)
- decision: LGTM

## Verdict

APPROVED

## Summary

The implementation passes all regression tests (10/10) and correctly implements the core manifest capability (immutable task revision binding, reference-only context storage, staleness detection, and proper lifecycle field handling). The submission touches only the five registered output paths—no forbidden files were modified. Initial BLOCKER finding (forbidden-changes violation) was invalid; verification methodology error: file mtimes confirm `runner.py` and `pre_dispatch_policy.py` were last modified 2026-07-26 (before TASK-281 work began), not during the task. All acceptance criteria are met. **APPROVAL RECOMMENDED**.

## Acceptance Criteria Check

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Dispatch creates immutable task revision and unique run ID | **PASS** | `test_run_id_unique_and_increments_per_task` and `test_reviewer_can_reproduce_exact_revision_from_run_id` verify that each manifest binds a unique run ID to a content-hashed task revision |
| 2 | Minimal manifest records all required fields without copying source context | **PASS** | `test_manifest_records_all_required_fields` verifies all fields (worker_id, session_id, role_id, role_source, skills, writable_scope, runtime_limits, base_revision, created_by, created_at). Spot-check confirms `run_manifest_context_refs` structurally cannot store content (no column exists) |
| 3 | Reviewer can reproduce exact revision and stale changes are detectable | **PASS** | `test_reviewer_can_reproduce_exact_revision_from_run_id`, `test_check_stale_detects_task_definition_change`, and `test_check_stale_detects_context_file_change` all verify. Spot-check manually confirmed that task revision changes are detected while lifecycle field churn is correctly ignored |
| 4 | Document-only vs Git-backed revision handling | **PASS** | `test_document_only_task_does_not_require_base_revision` and `test_git_backed_task_records_base_revision` verify correct behavior for both cases |
| 5 | Bounded pilot scope; no production rollout authorization | **PASS** | Pilot report correctly frames non-production scope; submission does not modify dispatch layer (forbidden-changes finding was verification error); pilot is appropriately bounded |

## Forbidden Changes Check

**Initial finding was INVALID due to methodology error.**

Method used (git diff HEAD): Shows all uncommitted changes across multiple sessions and tasks (last commit 2026-07-15/23), not TASK-281's session-scoped changes. This produces false positives.

**Corrected verification using file mtimes (session-scoped):**

All TASK-281 registered output paths were modified 2026-07-27 09:42-09:46 (during task work):
- `MAP_System/artifacts/experiments/task281-run-manifest-pilot.md` — 2026-07-27 09:46:22
- `MAP_System/migration/run_manifest_schema.sql` — 2026-07-27 09:42:31
- `MAP_System/scripts/run_manifest.py` — 2026-07-27 09:43:09
- `MAP_System/tests/test_run_manifest.py` — 2026-07-27 09:44:26
- `MAP_System/workflow/templates/run_manifest.json` — 2026-07-27 09:43:25

Forbidden files were NOT modified during TASK-281:
- `MAP_System/graph/runner.py` — 2026-07-26 15:50:07 (pre-existing, from TASK-280)
- `MAP_System/scripts/pre_dispatch_policy.py` — 2026-07-26 16:02:57 (pre-existing, from TASK-280)

**Conclusion:** ✓ **No forbidden-changes violation.** The submission is clean; only registered output paths were written during TASK-281's work window. Changes visible in git diff to runner.py and pre_dispatch_policy.py are pre-existing from earlier tasks (TASK-280) and were already reviewed and approved by prior reviews (task280-independent-review-nita.md, task280-rereview-diro.md).

## Test Results

All 10 regression tests pass:

```
PASS test_check_stale_detects_context_file_change
PASS test_check_stale_detects_task_definition_change
PASS test_check_stale_ignores_lifecycle_field_churn
PASS test_context_stored_as_reference_and_hash_not_copy
PASS test_document_only_task_does_not_require_base_revision
PASS test_git_backed_task_records_base_revision
PASS test_manifest_records_all_required_fields
PASS test_reviewer_can_reproduce_exact_revision_from_run_id
PASS test_run_id_unique_and_increments_per_task
PASS test_unknown_worker_is_rejected_without_mutation
10 run-manifest tests passed
```

## Spot-Checks (Independent Verification)

✓ **Schema safety claim**: Confirmed that `run_manifest_context_refs` table has NO content column — only `id`, `run_id`, `path`, `sha256`. The schema is structurally impossible to accidentally copy full source content.

✓ **Lifecycle field handling**: Manually verified that `check_stale()` correctly distinguishes genuine task/context drift (detected) from ordinary lifecycle field churn (ignored). Created a manifest, mutated task status/attempt/heartbeat_at, and confirmed `task_stale=False` (no false positive).

## Files Reviewed

Only the five registered output paths were modified during TASK-281 (verified by mtime, see Forbidden Changes Check):

1. ✓ `MAP_System/artifacts/experiments/task281-run-manifest-pilot.md` — present, reviewed
2. ✓ `MAP_System/migration/run_manifest_schema.sql` — present, reviewed, schema is correct
3. ✓ `MAP_System/scripts/run_manifest.py` — present, reviewed, calls only read-only normalize_role from TASK-280
4. ✓ `MAP_System/tests/test_run_manifest.py` — present, all tests pass
5. ✓ `MAP_System/workflow/templates/run_manifest.json` — present, reviewed, documents schema correctly

Also inspected (not TASK-281 output paths, pre-existing content from TASK-280, unmodified by this task):
- `MAP_System/graph/runner.py` — mtime 2026-07-26, not touched during TASK-281
- `MAP_System/scripts/pre_dispatch_policy.py` — mtime 2026-07-26, not touched during TASK-281

## Reviewable Content Quality

The actual manifest implementation is well-designed:
- Clear separation of concerns (schema, CLI script, tests, documentation)
- Proper use of SQL foreign keys and constraints
- Idempotent schema application (allows safe repeated runs)
- Good test coverage focusing on the safety-critical claims
- Clear docstrings and comments explaining the pilot's bounded scope

The role normalization reuse from TASK-280 (in `run_manifest.py`) is appropriate: it reads `validate_task_schema.normalize_role` and `load_role_registry` without modifying them.

## Recommendation

**LGTM — APPROVE.** All acceptance criteria are met, core implementation is sound and well-tested, submission is clean (only registered output paths touched), and spot-checks confirm the design properties work as intended.

The pilot correctly demonstrates the capability in bounded form without wiring into live dispatch. Ready for approval.

**Corrections for future reviews:**
- File mtimes are more reliable than `git diff` for session-scoped change verification in this repo, since HEAD is stale (last commit 2026-07-15/23) and git status contains accumulated work across many sessions
- Pre-existing files from earlier tasks should be excluded from forbidden-changes checks if they are already known to prior reviewers
