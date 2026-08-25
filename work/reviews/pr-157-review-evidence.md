reviewer: /root/pr157_reviewer
head_sha: 8f10a01f6cb069061db485a9aa753024f44da507
independent: true
summary: APPROVED. Re-reviewed PR #157 exact updated code head 8f10a01f6cb069061db485a9aa753024f44da507 against current origin/main ee7d14c5c10773f41c9dc8947804e258a619cab9 in isolated clone /tmp/pr157-review.UDfBgi/MAPS_Lean. The repair from prior reviewed head b42888635d1a9051814327d4d7b63be9d43f5485 is bounded: create_run_manifest() now binds worktree identity when Git identity is readable and leaves unreadable/non-Git placeholder-base_revision runs unbound for compatibility, with regression test_non_git_placeholder_base_revision_remains_unbound. The original acceptance still holds for bound Git runs: immutable run_worktree_bindings are added, binding is inserted in the same SQLite transaction as run_manifests, get_run_manifest()/trace_task()/Portable Run Record expose binding or missing coverage, and verify_git_run() reports worktree_mismatch/worktree_unavailable before changed-path scope evaluation for bound runs. No worktree creation/cleanup, destructive Git repair, RnS, Chain Shovel, external target, or task/review/merge authority changes were found. Verification passed: git diff --check origin/main...HEAD; py_compile touched runtime modules; python3 -m unittest tests.test_execution_integrity tests.test_run_manifest_immutability tests.test_run_record tests.test_runtime_review_hardening tests.test_run_environment_evidence -v (55 tests OK in 246.475s). Additional targeted probe confirmed bound Git mismatch short-circuits before scope evaluation and non-Git placeholder base_revision creates an unbound manifest. No blocking findings.

# Review: Run worktree binding

- Task: `work/tasks/run-worktree-binding.md`
- Reviewer: `/root/pr157_reviewer`
- Verdict: `APPROVED`

## Acceptance criteria check

- `PASS` — Schema adds immutable `run_worktree_bindings`.
  - Evidence: `runtime/state/schema.sql` adds `run_worktree_bindings` keyed by `run_id` with repo/worktree identity fields and immutable update/delete triggers. `tests/test_run_manifest_immutability.py` verifies update/delete rejection for the new binding table.
- `PASS` — Run creation binds readable Git worktree identity in the same transaction as `run_manifests`.
  - Evidence: `runtime/state/integrity.py::create_run_manifest()` attempts `collect_git_worktree_identity(root)` when `base_revision` is supplied, proceeds unbound if identity is unreadable, and for readable identity inserts `run_manifests` plus `run_worktree_bindings` under one `BEGIN IMMEDIATE` transaction before the single commit.
- `PASS` — `get_run_manifest()`, trace, and Run Record expose worktree binding or explicit missing coverage.
  - Evidence: `runtime/state/integrity.py::get_run_manifest()` adds `record["worktree"]`; `runtime/state/observability.py::trace_task()` adds `run["worktree"]`; `runtime/run_record.py` includes the run binding and adds `coverage.worktree_identity` with verified/missing coverage states. `tests/test_run_record.py` covers deterministic projection and verified coverage.
- `PASS` — `verify_git_run()` reports `worktree_mismatch` or `worktree_unavailable` before changed-path scope evaluation for bound runs.
  - Evidence: `runtime/integrity/git_scope.py::verify_git_run()` reads expected worktree binding before `collect_git_changes()` and returns mismatch/unavailable with empty `changed_paths`/`out_of_scope`; `tests.test_execution_integrity.IntegrityTests.test_git_scope_verifier_rejects_different_clone_before_scope_check` covers mismatch. Targeted probe reconfirmed bound Git mismatch short-circuits before scope evaluation.
- `PASS` — Existing non-Git/unbound run fixtures remain compatible.
  - Evidence: `tests.test_execution_integrity.IntegrityTests.test_non_git_placeholder_base_revision_remains_unbound` passed and asserts a non-Git repo with `base_revision="placeholder"` creates a manifest with `worktree is None`. Targeted probe reproduced the same compatibility path.
- `PASS` — No worktree creation, cleanup, destructive Git repair, RnS, external target, or authority behavior is added.
  - Evidence: Touched production paths are limited to runtime state/projection/git-scope/readme/run-record surfaces. `rg -n "reset|restore|checkout|clean|worktree (add|remove|prune)|rm -rf|shutil\\.rmtree|unlink\\(" runtime/state runtime/integrity runtime/run_record.py` found no production worktree creation/cleanup/destructive repair calls beyond documentation text and unrelated existing helper names.

## Applicable review lenses

- `[x]` Functional / acceptance
- `[x]` Destructive / data-loss
- `[x]` Authority / permission boundary

Functional / acceptance evidence: inspected all changed runtime, schema, test, task, README, and roadmap files; compared the repair diff from stale reviewed head `b42888635d1a9051814327d4d7b63be9d43f5485` to updated head `8f10a01f6cb069061db485a9aa753024f44da507`; ran the expanded owner-stated verification set; added targeted probes for bound mismatch and non-Git placeholder-base compatibility.

Destructive / data-loss evidence: source inspection found verifier/reporting logic only; no production `git reset`, `git restore`, `git checkout`, `git clean`, worktree removal, file deletion, or cleanup behavior was added.

Authority / permission boundary evidence: changes are evidence/projection/verifier behavior only and do not alter task ownership, review authority, merge authority, RnS/recovery, Chain Shovel, or external target paths.

## Findings

No blocking findings.

## Evidence checked

- `git fetch origin main run-worktree-binding`
- `git checkout -B review-pr-157 origin/run-worktree-binding`
- `git rev-parse HEAD` → `8f10a01f6cb069061db485a9aa753024f44da507`
- `git rev-parse origin/main` → `ee7d14c5c10773f41c9dc8947804e258a619cab9`
- `git diff --stat origin/main...HEAD`
- `git diff --name-status origin/main...HEAD`
- `git diff --check origin/main...HEAD`
- `python3 -m py_compile runtime/state/integrity.py runtime/state/observability.py runtime/integrity/git_scope.py runtime/integrity/__init__.py runtime/run_record.py`
- `python3 -m unittest tests.test_execution_integrity tests.test_run_manifest_immutability tests.test_run_record tests.test_runtime_review_hardening tests.test_run_environment_evidence -v` → 55 tests OK in 246.475s
- `git diff --unified=80 b42888635d1a9051814327d4d7b63be9d43f5485..HEAD -- runtime/state/integrity.py tests/test_execution_integrity.py runtime/integrity/README.md work/tasks/run-worktree-binding.md work/roadmaps/CAPABILITY_CHECKLIST.md`
- Targeted Python probe for bound Git `worktree_mismatch` pre-scope failure and non-Git placeholder `base_revision` unbound compatibility.
- Source inspection:
  - `runtime/state/schema.sql`
  - `runtime/state/integrity.py`
  - `runtime/state/observability.py`
  - `runtime/integrity/git_scope.py`
  - `runtime/integrity/__init__.py`
  - `runtime/run_record.py`
  - `runtime/integrity/README.md`
  - `tests/test_execution_integrity.py`
  - `tests/test_run_manifest_immutability.py`
  - `tests/test_run_record.py`
  - `work/tasks/run-worktree-binding.md`
  - `work/roadmaps/CAPABILITY_CHECKLIST.md`

## High-risk completion / release summary

N/A.

## Reviewer limits

- Missing context/evidence: none.
- New requirements discovered: none.
