# Task: Promote deterministic RnS recovery

- Status: `READY`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `implementation-agent`
- Risk: `HIGH`
- Goal: Add a durable, deterministic recovery supervisor that can resume a known hcom session for already-active MAPS work after a scheduled reset or detected stop, with capped backoff and no WezTerm dependency.

## Inputs and source of truth

- Inputs: active SQLite task store, hcom adapter, preserved `limit_watcher.py`/liveness/recovery tests and audit findings.
- Authoritative sources: canonical MAPS task state for whether work is still active; recovery incident state for retry timing; hcom only for session liveness/control.
- Dependencies: TASK-009 state and TASK-011 hcom adapter branches.

## Change boundary

- MAY CHANGE: `runtime/recovery/**`, targeted hcom resume prompt support, tests, runtime docs, this task record.
- MUST NOT CHANGE: task ownership/status through RnS, routing decisions, review/approval state, legacy source.
- OPERATOR APPROVAL REQUIRED: none for fake tests; production resume is only for pre-existing explicitly bound work.

## Decision authority

- Owner may decide: incident schema, backoff, liveness classification, deterministic prompts.
- Owner must escalate: any design where RnS creates/claims/reassigns tasks or guesses new work.

## Acceptance criteria

- [ ] Recovery incidents persist outside hcom state.
- [ ] Due recovery checks canonical task status/claimant before any resume.
- [ ] Changed/missing/non-active claims suppress recovery rather than stealing work.
- [ ] Live sessions resolve incidents without resume.
- [ ] Stopped sessions may be resumed headlessly with capped backoff.
- [ ] Terminal/superseded sessions are never resumed.
- [ ] Silent-stop detection requires a known prior-live session and explicit worker→session binding.
- [ ] No RnS code calls task mutation methods.
- [ ] No WezTerm dependency.

## Verification and evidence

- Verification: pure/fake adapter tests; source-boundary assertions.
- Evidence: test output and PR diff.
- Review required: `INDEPENDENT_REVIEW`

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

- Completed: task shaped.
- Not completed: implementation/tests/docs.
- Current blocker: none.
- Next action: implement recovery record/store and supervisor.
