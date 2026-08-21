# Task: Task environment contract storage

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root/task_env_storage_impl`
- Risk: `MEDIUM`
- Goal: Persist an optional task-level environment contract that round-trips
  through `TaskStore`, participates in task revision and readiness validation,
  and does not change routing behavior.

## Inputs and source of truth

- Inputs:
  - `work/notes/2026-08-21-task-environment-contract-design.md`.
  - `runtime/state/schema.sql`, `runtime/state/base.py`,
    `runtime/state/policy.py`, `runtime/state/store.py`,
    `runtime/state/integrity.py`, and `runtime/state/readiness.py`.
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.24`.
- Authoritative sources: the merged design note above and the current
  state-store implementation; the design note wins for the environment
  contract's field semantics and non-routing boundary.
- Evidence labels:
  - VERIFIED: `origin/main` is merge commit `12897460`, containing the design
    note and the current state-store extension points.
  - VERIFIED: policy state currently uses one shaping hook in the base
    transaction.
  - ASSUMED: existing focused state and routing tests remain representative
    until run after implementation.
- Dependencies / preconditions: work begins from clean `origin/main` in the
  isolated `task-environment-contract-storage` worktree; no concurrent task
  owns the paths listed below.

## Change boundary

- MAY CHANGE:
  - `runtime/state/schema.sql`
  - `runtime/state/environment_contract.py`
  - `runtime/state/base.py`
  - `runtime/state/store.py`
  - `runtime/state/integrity.py`
  - `runtime/state/readiness.py`
  - `tests/test_task_environment_contract.py`
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.24` evidence text only
  - this task file
- MUST NOT CHANGE:
  - routing decisions or routing report sourcing, freshness selection, cache,
    or environment inspection behavior;
  - persisted report locations/caches or a universal `EnvironmentSpec`;
  - unrelated state contracts or roadmap status (`6.24` remains `IN PROGRESS`);
  - review evidence (an independent reviewer owns it).
- MAY CHANGE IF NECESSARY: no other paths; amend this contract first.
- OPERATOR APPROVAL REQUIRED: publication of a non-draft PR, routing behavior
  changes, new dependencies, or any broadened environment policy.

## Decision authority

- Owner may decide: internal mixin/hook naming, validation implementation, and
  focused test structure when they preserve the approved fields, atomicity,
  partial-update semantics, and no-routing-change boundary.
- Owner must escalate: ambiguity in clearing/partial semantics that conflicts
  with existing contract behavior; any changed external or routing behavior;
  schema migration compatibility issue; new dependency; security/privacy/cost
  decision; destructive or irreversible action.

## Acceptance criteria

- [x] Schema has one optional `task_environment` row per task with the four
  approved fields and constraints from the design.
- [x] `TaskStore.update_contract()` accepts valid optional environment data,
  rejects malformed environment mappings with `INVALID_CONTRACT`, and returns
  `environment: None` when absent or cleared.
- [x] Environment writes and policy writes participate in the same shaping
  transaction; a failed environment write leaves policy state unchanged.
- [x] Environment contract changes alter task revision; a valid contract can
  be promoted to READY and cannot be changed after READY.
- [x] Readiness validates present environment path/TTL/flags but absence does
  not block READY.
- [x] Existing routing behavior remains unchanged, and checklist `6.24`
  records the storage progress while remaining `IN PROGRESS`.

## Verification and evidence

- Verification: `git diff --check`; `python -m py_compile` for each touched
  state module; focused environment/state/routing unittest modules.
- Evidence to preserve: command outcomes in the implementation commit/PR
  description; no separate review-evidence artifact is created by this owner.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Python/SQLite state store; use temporary database
  fixtures only.
- Ordered procedure: add this contract; inspect current state semantics; make
  the bounded implementation; run the named checks; commit only implementation.
- Failure branches: if the design conflicts with verified existing partial
  update or migration behavior, stop and escalate; if a test exposes a routing
  change, revert/reshape the affected implementation before proceeding.
- Rollback / recovery: revert the implementation commit; schema uses
  `CREATE TABLE IF NOT EXISTS` and test databases are temporary.
- Security / privacy controls: do not inspect host environments, network, or
  secret-bearing paths; validate only safe repo-relative specification paths.
- External side effects: pushing the branch and creating a draft PR are allowed
  only if available project policy/tool authorization permits; no merge.
- Effort limit: do not extend work into routing enforcement, report lifecycle,
  or specification selection.
- Approved reference: `work/notes/2026-08-21-task-environment-contract-design.md`.

## Stop / escalate

Stop rather than guess if:

- the approved four-field shape cannot fit existing partial-update semantics;
- atomic hooks require a change outside the listed state-store paths;
- a backward-compatibility or schema migration concern appears; or
- verification indicates routing behavior changed.

Escalate to: `/root`.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- `environment=None` clears the optional environment contract when supplied;
  omission preserves the current value, matching partial contract updates.
- Status is `READY_FOR_REVIEW`; independent review is required before task
  completion.

## Completion / handoff

- Completed: optional environment storage, transaction hooks, task read/revision
  and readiness integration, focused tests, and 6.24 evidence update.
- Not completed: independent review only.
- Current blocker: none.
- Next action if not DONE: independent reviewer checks the implementation
  against this task contract.
