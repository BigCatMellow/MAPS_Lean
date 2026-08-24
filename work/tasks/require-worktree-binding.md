# Task: Require worktree binding option

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: add an opt-in fail-closed switch so dispatch can require exact Git
  worktree binding when starting a writable run.

## Inputs and source of truth

- Inputs:
  - `work/tasks/run-worktree-binding.md`
  - `runtime/state/integrity.py`
  - `runtime/flow_start.py`
  - `runtime/cli.py`
  - `runtime/integrity/cli.py`
  - `tests/test_execution_integrity.py`
  - `tests/test_flow_start.py`
- Authoritative sources: current `origin/main` after PR #157.
- Evidence labels:
  - VERIFIED: default run creation preserves non-Git placeholder-base fixtures.
  - VERIFIED: readable Git repos already store worktree identity.
  - VERIFIED: dispatch currently cannot require that binding.
- Dependencies / preconditions: PR #157 merged.

## Change boundary

- MAY CHANGE:
  - `runtime/state/integrity.py`
  - `runtime/flow_start.py`
  - `runtime/cli.py`
  - `runtime/integrity/cli.py`
  - `runtime/integrity/README.md`
  - `tests/test_execution_integrity.py`
  - `tests/test_flow_start.py`
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` rows E6 and 6.16
  - this task file
- MUST NOT CHANGE: worktree creation/cleanup, destructive Git repair, RnS,
  Chain Shovel, external targets, merge authority, task/review authority.
- MAY CHANGE IF NECESSARY: adjacent CLI tests for the same option.
- OPERATOR APPROVAL REQUIRED: none for this opt-in guard.

## Decision authority

- Owner may decide option naming and exact error code.
- Owner must escalate any default-on behavior or Git mutation.

## Acceptance criteria

- [x] `create_run_manifest()` accepts opt-in required binding.
- [x] Required binding fails closed when Git identity cannot be read.
- [x] Default behavior remains compatible for unbound/non-Git runs.
- [x] `flow start` and integrity `run-create` expose the option.
- [x] No worktree creation, cleanup, destructive Git repair, RnS, external
      target, or authority behavior is added.

## Verification and evidence

- Verification:
  - `git diff --check`
  - `python3 -m py_compile runtime/state/integrity.py runtime/flow_start.py runtime/cli.py runtime/integrity/cli.py`
  - `python3 -m unittest tests.test_execution_integrity tests.test_flow_start -v`
- Evidence to preserve: passing command output and review evidence.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: local SQLite and Git/non-Git temp repos.
- Ordered procedure: state option, flow/CLI threading, tests, docs/roadmap.
- Failure branches: if option would need worktree creation or cleanup, stop.
- Rollback / recovery: revert branch.
- Security / privacy controls: no new path storage beyond PR #157 evidence.
- External side effects: GitHub PR only after verification.
- Effort limit: opt-in enforcement only.
- Approved reference: PR #157 behavior.

## Stop / escalate

Stop rather than guess if this becomes default-on or mutates Git state.

Escalate to: operator.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Option name: `require_worktree_binding`; CLI flag:
  `--require-worktree-binding`.

## Completion / handoff

- Completed: implementation and owner verification.
- Not completed: independent review.
- Current blocker: independent review.
- Next action if not DONE: review PR branch.
