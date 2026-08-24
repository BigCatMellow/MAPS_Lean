# Task: Worktree run binding design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: design the additive run-manifest surface that binds a writable run to
  its exact Git worktree identity so E6/6.16 can move beyond convention-only
  isolation without adding worktree creation or cleanup automation.

## Inputs and source of truth

- Inputs:
  - `playbook/WORKTREE_ISOLATION.md`
  - `work/tasks/worktree-isolation-convention-wave16.md`
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` rows E6 and 6.16
  - `work/roadmaps/prime-agent-capability-roadmap.md` section `10`
  - `runtime/state/integrity.py`
  - `runtime/state/schema.sql`
  - `runtime/integrity/git_scope.py`
  - `runtime/flow_start.py`
  - `tests/test_runtime_review_hardening.py`
  - `tests/test_run_manifest_immutability.py`
- Authoritative sources: current run-manifest code and worktree-isolation
  playbook.
- Evidence labels:
  - VERIFIED: `run_manifests` already bind task revision, scope, context refs,
    runtime limits, and optional Git base revision.
  - VERIFIED: `verify_git_run()` compares current worktree changes against a
    run manifest but does not check that the caller supplied the same worktree.
  - VERIFIED: E6 remains `IN PROGRESS` because isolation is documented as a
    convention but not bound into run evidence.
- Dependencies / preconditions: current `origin/main`; no RnS or external
  target work.

## Change boundary

- MAY CHANGE:
  - `work/notes/2026-08-24-worktree-run-binding-design.md`
  - this task file
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` rows E6 and 6.16 evidence text only
- MUST NOT CHANGE:
  - `runtime/*.py`
  - `tests/*.py`
  - SQLite schema
  - worktree creation/cleanup behavior
  - task/review/merge authority
  - RnS/recovery/harness behavior
  - external project / portable deployment behavior
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: none for this design; implementation of schema or
  workflow automation requires its own reviewed task.

## Decision authority

- Owner may decide:
  - which fields belong in the future run/worktree binding;
  - where verifier mismatch reporting belongs;
  - which automation stays explicitly out of scope.
- Owner must escalate:
  - automatic worktree creation/deletion;
  - destructive cleanup;
  - merge/integration authority changes;
  - broad task-state or run-lifecycle changes.

## Acceptance criteria

- [x] Design note names the current E6 gap with direct source paths.
- [x] Design note proposes additive immutable run/worktree binding fields.
- [x] Design note defines create/read/verify behavior and failure semantics.
- [x] Design note excludes worktree creation, cleanup, merge authority, and
      broad registries.
- [x] Design note leaves a bounded implementation follow-up with tests.
- [x] No runtime or test files change.

## Verification and evidence

- Verification:
  - `git diff --check`
  - direct read of changed docs
- Evidence to preserve: design note, task doc, checklist update.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: repository docs only.
- Ordered procedure: inspect current run manifest and verifier surfaces, write
  design, verify.
- Failure branches: if runtime already binds exact worktree identity, update the
  finding instead of preserving stale gap language.
- Rollback / recovery: revert docs-only commit.
- Security / privacy controls: do not store secrets or system-global user paths
  beyond explicit repo/worktree identity decisions in the design.
- External side effects: GitHub PR publication/merge only after review.
- Effort limit: no implementation in this task.
- Approved reference: `playbook/WORKTREE_ISOLATION.md`.

## Stop / escalate

Stop rather than guess if:

- worktree identity would require automatic creation/cleanup;
- exact identity storage would expose sensitive local path data without a
  safer alternative;
- verifier mismatch semantics would alter task authority or review authority.

Escalate to: operator or separate implementation task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This is the next agent-OS lane after deterministic review-start flow. It is
  intentionally unrelated to RnS and external pilot work.

## Completion / handoff

- Completed: design note and implementation-ready follow-up.
- Not completed: schema/runtime implementation.
- Current blocker: independent review.
- Next action if not DONE: review this architecture task.
