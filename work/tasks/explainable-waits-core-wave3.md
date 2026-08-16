# Task: explainable waits core Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/explainable-waits-core-wave3`
- Risk: `MEDIUM`
- Goal: Implement the first read-only explainable-waits projection over existing canonical dependency, review, and operator-approval evidence without adding wait state, schema, polling, communication inference, or task authority.

## Inputs / source of truth

- root `AGENTS.md`;
- current merged `main@4b2b1910062024ab182ed73c600efe7d983e9761`;
- `runtime/state/base.py` public `get_task()` / `list_reviews()` reads;
- `runtime/state/readiness.py` dependency readiness semantics;
- `runtime/state/policy.py` durable policy/approval fields;
- `runtime/policy/evaluator.py` operator-approval trigger semantics;
- PR #52 explainable-waits design as prospective planning evidence only.

Canonical source ordering:

1. current task lifecycle + declared dependencies;
2. current referenced dependency task status;
3. current durable review rows;
4. current durable task policy/approval fields;
5. this derived projection.

Free-text task/review/event prose is never causal authority for this implementation.

## Change boundary

MAY CHANGE:

- `runtime/wait_projection.py`
- `tests/test_wait_projection.py`
- `work/tasks/explainable-waits-core-wave3.md`
- `work/notes/2026-08-15-explainable-waits-core.md`

MUST NOT CHANGE:

- SQLite schema;
- `runtime/state/store.py` or any TaskStore mixin;
- task/review/policy mutation semantics;
- provider/hcom code;
- helper/recovery code;
- A1/A2/A3 branches or state tables;
- communication lineage;
- external actions;
- monitoring/polling/notification behavior.

## Initial supported explanations

### `WAIT_DEPENDENCY`

May be emitted only when:

- task is in a non-terminal execution/preparation lifecycle where dependencies can gate progress;
- dependency is explicitly declared by task ID;
- referenced dependency is missing or canonical status is not `DONE`.

The projection records only exact dependency ID/status facts.

### `WAIT_REVIEW_UNCLAIMED`

May be emitted only when:

- canonical task status is `READY_FOR_REVIEW`;
- a durable submission exists;
- no open review exists.

### `WAIT_REVIEW_IN_PROGRESS`

May be emitted only when:

- canonical task status is `READY_FOR_REVIEW`;
- durable submission exists;
- exactly one open review exists.

The projection may expose review ID/reviewer/timestamps but does not infer availability, ETA, or responsiveness.

### `WAIT_OPERATOR_APPROVAL`

May be emitted only when:

- canonical task status is `READY` or `CHANGES_REQUESTED`;
- task AGI status is `AGI READY`;
- one or more accepted operator-approval trigger flags are true;
- both canonical `approved_by` and `approved_at` are absent.

It reports trigger codes from the same policy fields used by assignment policy. It does not request or record approval.

## Unknown / blocker semantics

- `DONE` is terminal and not a wait.
- `NEEDS_SHAPING` without an unresolved explicit dependency is not a wait.
- `ACTIVE` without an unresolved explicit dependency is not automatically waiting.
- generic canonical `BLOCKED` does not expose a typed causal relationship in the accepted schema; if no exact supported wait exists, return causal `UNKNOWN` / `BLOCKED_CAUSE_UNPROVEN`.
- malformed/inconsistent review evidence at `READY_FOR_REVIEW` returns `UNKNOWN`, not a guessed review wait.
- historical review verdicts are not used to infer current `BLOCKED` cause because accepted review-subject/freshness lineage is still separate/open work.

## Explicit non-features

No:

- `tasks.waiting` / mutable wait row;
- automatic task block/unblock;
- `RUNNABLE` result;
- message/reply wait;
- provider/session liveness inference;
- helper/recovery wait;
- timeout/stuck detection;
- review reminders;
- operator reminders;
- task/review prose parsing;
- external action.

## Projection contract

The module returns a deterministic read model with:

- `task_id`;
- current lifecycle status;
- summary: `WAITING`, `BLOCKED`, `NO_VERIFIED_WAIT`, or `UNKNOWN`;
- sorted structured reasons;
- source coverage labels;
- `authority = DERIVED_READ_ONLY`.

`NO_VERIFIED_WAIT` explicitly does not mean runnable/executable.

## Acceptance criteria

- [x] No schema/store/state mutation is introduced.
- [x] Dependency wait derives only from declared dependency IDs + canonical dependency status.
- [x] Review wait derives only from `READY_FOR_REVIEW`, durable submission, and open-review rows.
- [x] Operator approval wait derives only from exact policy flags + absent durable approval on executable lifecycle states.
- [x] Multiple verified wait reasons may coexist without one hiding another.
- [x] Generic `BLOCKED` cause remains UNKNOWN unless an independently supported exact wait exists.
- [x] `DONE` never reports waiting.
- [x] No review/task/event prose is parsed for cause.
- [x] No session/provider/helper/recovery observation can create waiting.
- [x] Output is deterministic for unchanged source state.
- [x] Reads do not mutate canonical state.

## Verification

Focused:

```text
python -m unittest tests.test_wait_projection -v
```

Full PR Runtime CI is the repository validation gate.

Review required: `INDEPENDENT_REVIEW`.

## Stop / escalation

Stop rather than infer if:

- a wait cause requires prose or timestamp/name heuristics;
- communication response dependency would be needed;
- recovery/helper wait would require state not exposed by its owning source;
- another agent claims the same `runtime/wait_projection.py` path;
- accepted policy/review interfaces materially change before integration.

## Continuation

After A4c/execution-lineage interfaces settle:

1. keep this structured-gate projection as the baseline;
2. add communication waits only if exact run↔event correlation plus explicit response-required progress dependency exist;
3. add recovery/helper waits only from exact authoritative eligibility contracts;
4. expose through Trace/Run Record as derived evidence;
5. evaluate usefulness before considering any notification/monitoring behavior.
