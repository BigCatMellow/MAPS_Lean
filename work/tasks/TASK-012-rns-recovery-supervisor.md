# Task: Promote deterministic RnS recovery

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `implementation-agent`
- Risk: `HIGH`
- Goal: Add a durable, deterministic recovery supervisor that can resume a known hcom session for already-active MAPS work after a scheduled reset or detected stop, with capped backoff and no WezTerm dependency.

## Inputs and source of truth

- Inputs: active SQLite task store, hcom adapter, preserved `limit_watcher.py`/liveness/recovery tests and audit findings.
- Authoritative sources: canonical MAPS task state for whether work is still active; recovery incident state for retry timing; hcom only for session liveness/control.
- Dependencies: TASK-009 state and TASK-011 hcom adapter branches.

## Acceptance criteria

- [x] Recovery incidents persist outside hcom state in `.maps/state/recovery.json`.
- [x] Due recovery checks canonical task status/claimant before any resume.
- [x] Changed/missing/non-active claims suppress recovery rather than stealing work.
- [x] Live sessions resolve incidents without resume.
- [x] Stopped sessions may be resumed headlessly with capped backoff.
- [x] Terminal/superseded sessions are never resumed.
- [x] Silent-stop detection requires a known prior-live session and explicit worker→session binding.
- [x] RnS source contains no task mutation calls.
- [x] No WezTerm dependency.
- [ ] Recovery regression suite executed on a configured checkout.

## Verification and evidence

- Verification: `tests/test_recovery_supervisor.py` covers scheduled/due recovery, live resolution, claim-change suppression, inactive-task suppression, terminal sessions, retry exhaustion, silent-stop detection, liveness, and source-boundary checks.
- Evidence: test output remains pending because the current sandbox cannot clone the branch.
- Review required: `INDEPENDENT_REVIEW`

## Important behavior

```text
known ACTIVE task + existing claim + explicit worker/session binding
→ prior-live session stops OR scheduled resume becomes due
→ verify task still ACTIVE and claimant unchanged
→ terminal? suppress
→ already live? resolve
→ stopped + due? resume headlessly
→ verify later; bounded backoff; eventually fail loudly
```

First observation of an already-dead session does not invent a recovery incident.

## Stop / escalate

Stop if recovery would require changing task truth, inventing a task, or guessing session ownership.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Completion / handoff

- Completed: durable incident store, liveness classifier, silent-stop observer, deterministic supervisor, bounded retry/backoff, terminal suppression, docs, regression tests.
- Not completed: configured-checkout test execution and independent review.
- Current blocker: current sandbox cannot clone/fetch the branch for local execution.
- Next action: run recovery tests later; continue helper/installer migration separately.
