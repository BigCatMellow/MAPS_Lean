# Task: Outcome feedback

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT`
- Risk: `MEDIUM`
- Goal: Record real-world post-completion task outcomes as append-only evidence
  so MAPS can distinguish process success from actual success without changing
  task authority or rewriting historical records.

## Inputs and source of truth

- Inputs: `runtime/state/schema.sql`, `runtime/state/store.py`,
  `runtime/state/observability.py`, `runtime/cli.py`, active tests and runtime
  documentation.
- Authoritative sources: canonical SQLite task state and immutable/append-only
  evidence patterns already used by the Lean runtime.
- Evidence labels: current runtime `VERIFIED`; future eval use is a design goal,
  not evidence that the corpus already exists.
- Dependencies / preconditions: task must exist and be `DONE` before an outcome
  observation is recorded.

## Change boundary

- MAY CHANGE: `runtime/state/schema.sql`, `runtime/state/outcomes.py`,
  `runtime/state/store.py`, `runtime/state/observability.py`, `runtime/cli.py`,
  `runtime/README.md`, `tests/test_outcomes.py`, review-queue packet, this task.
- MUST NOT CHANGE: task lifecycle, review verdict semantics, policy authority,
  routing/recovery/helper behavior.
- MAY CHANGE IF NECESSARY: outcome field vocabulary inside this task only.
- OPERATOR APPROVAL REQUIRED: none; no external/destructive action is required.

## Decision authority

- Owner may decide: minimal append-only schema/API/CLI shape.
- Owner must escalate: new task statuses, automatic task reopening, automatic
  harness refinement, or outcome data changing authorization/routing directly.

## Acceptance criteria

- [ ] Outcomes are append-only and cannot update/delete historical observations.
- [ ] Recording an outcome does not change task status, ownership, review, or
  policy state.
- [ ] Outcome records preserve explicit actor class/identity (or UNKNOWN),
  source provenance, task revision, optional run binding, failure class,
  escaped-defect/rework/intervention metrics, and timestamp.
- [ ] Later corrections can explicitly supersede an earlier outcome record
  without deleting it.
- [ ] Outcome text crosses the diagnostic secret-safety boundary.
- [ ] CLI can record/list outcomes and task trace includes them.
- [ ] Tests cover authority isolation, immutability, supersession/provenance,
  run/task validation, redaction, and CLI/read projection.

## Verification and evidence

- Verification: pull-request CI plus focused behavior tests.
- Evidence to preserve: CI result and PR diff.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Python 3.12 / SQLite.
- Ordered procedure: append-only schema → store API → trace/CLI → tests/docs.
- Failure branches: reject outcome records for unfinished tasks, mismatched run
  IDs, invalid actor provenance, or cross-task supersession.
- Rollback / recovery: revert commit; table is additive and does not alter the
  task lifecycle.
- Security / privacy controls: concise source/notes are redacted best-effort;
  callers still must not intentionally place secrets in diagnostic metadata.
- External side effects: GitHub branch/PR only.
- Effort limit: no eval engine or automatic learning in this tranche.
- Approved reference: preserved P1 Outcome Feedback candidate.

## Stop / escalate

Stop rather than guess if outcome storage would need to mutate task authority or
if a field cannot be represented without creating another source of task truth.

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

- Outcome observations are later knowledge. They append to history; they never
  rewrite the original task/review result.
- Evaluation/corpus construction remains future work after enough observations
  exist.

## Completion / handoff

- Completed: task shaped.
- Not completed: implementation and review.
- Current blocker: none.
- Next action if not DONE: implement append-only outcome evidence.
