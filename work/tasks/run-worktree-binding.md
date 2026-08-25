# Task: Run worktree binding

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: bind Git-scoped run manifests to the exact Git worktree identity used
  at run creation and make Git verification fail closed when a different
  worktree is supplied.

## Inputs and source of truth

- Inputs:
  - `work/notes/2026-08-24-worktree-run-binding-design.md`
  - `work/tasks/worktree-run-binding-design.md`
  - `runtime/state/integrity.py`
  - `runtime/state/schema.sql`
  - `runtime/integrity/git_scope.py`
  - `runtime/state/observability.py`
  - `runtime/run_record.py`
  - `tests/test_execution_integrity.py`
  - `tests/test_run_manifest_immutability.py`
  - `tests/test_run_record.py`
- Authoritative sources: merged E6 design note and current runtime/state code.
- Evidence labels:
  - VERIFIED: Git-scoped runs are identified by readable Git identity at
    `repo_root`; `base_revision` alone is not sufficient because existing
    non-Git fixtures use placeholder revisions.
  - VERIFIED: non-Git fixture runs, including runs with placeholder
    `base_revision`, currently work and must remain compatible.
  - VERIFIED: `verify_git_run()` currently verifies changed paths but not exact
    worktree identity.
- Dependencies / preconditions: PR #156 merged to `origin/main`; no RnS or
  external target work.

## Change boundary

- MAY CHANGE:
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
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` rows E6 and 6.16
  - this task file
- MUST NOT CHANGE:
  - worktree creation or cleanup behavior
  - destructive Git commands
  - task ownership, review authority, or merge authority
  - RnS/recovery/harness behavior
  - Chain Shovel or external target behavior
- MAY CHANGE IF NECESSARY: adjacent tests documenting the same run-manifest
  projection behavior.
- OPERATOR APPROVAL REQUIRED: any automatic worktree creation/deletion,
  destructive cleanup, or authority change.

## Decision authority

- Owner may decide:
  - exact helper names and payload keys;
  - compatibility behavior for non-Git/unbound runs;
  - test fixture shape.
- Owner must escalate:
  - path privacy policy changes beyond local runtime evidence;
  - failure semantics that would block legacy/unbound runs automatically;
  - any automation that mutates Git state.

## Acceptance criteria

- [x] Schema adds immutable `run_worktree_bindings`.
- [x] Run creation binds readable Git worktree identity in the same transaction
      as `run_manifests`.
- [x] `get_run_manifest()`, trace, and Run Record expose worktree binding or
      explicit missing coverage.
- [x] `verify_git_run()` reports `worktree_mismatch` or `worktree_unavailable`
      before changed-path scope evaluation for bound runs.
- [x] Existing non-Git/unbound run fixtures remain compatible.
- [x] No worktree creation, cleanup, destructive Git repair, RnS, external
      target, or authority behavior is added.

## Verification and evidence

- Verification:
  - `git diff --check`
  - `python3 -m py_compile runtime/state/integrity.py runtime/state/observability.py runtime/integrity/git_scope.py runtime/integrity/__init__.py runtime/run_record.py`
  - `python3 -m unittest tests.test_execution_integrity tests.test_run_manifest_immutability tests.test_run_record tests.test_runtime_review_hardening -v`
- Evidence to preserve: passing command output and review evidence.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: local Git repositories and SQLite task DB.
- Ordered procedure: schema/helper, state binding/projection, verifier, Run
  Record coverage, tests, roadmap.
- Failure branches: if Git identity cannot be read for a Git-scoped run, return
  explicit failure and do not create the run manifest.
- Rollback / recovery: revert this branch; no destructive Git operation is used.
- Security / privacy controls: store local absolute paths only as local runtime
  evidence; do not treat them as portable replay authority.
- External side effects: GitHub PR publication/merge only after review.
- Effort limit: first runtime slice only.
- Approved reference: `work/notes/2026-08-24-worktree-run-binding-design.md`.

## Stop / escalate

Stop rather than guess if:

- implementation would require creating/removing/cleaning worktrees;
- exact identity storage requires a broader privacy policy;
- verifier semantics would change task/review authority.

Escalate to: operator or a follow-up design task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Bind readable Git worktrees in this first slice. Existing non-Git fixtures
  with placeholder `base_revision` remain unbound for compatibility.

## Completion / handoff

- Completed: schema/runtime/projection/verifier/test implementation and owner
  verification.
- Not completed: independent review.
- Current blocker: independent review.
- Next action if not DONE: review PR branch.
