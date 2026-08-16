# Explainable waits core — structured gates only

Date: 2026-08-15/16  
Owner: `agent/explainable-waits-core-wave3`  
Status: implementation evidence, pending independent review

## Scope

This tranche implements only wait explanations already provable from accepted canonical task state:

- explicit task dependencies;
- review-gate ownership;
- operator-approval policy.

It does not implement communication, recovery, helper, provider-liveness, timeout, or "stuck" inference.

## Architecture

`runtime/wait_projection.py` is a standalone read model. It depends on only two source methods:

```text
get_task(task_id)
list_reviews(task_id)
```

Current `TaskStore.get_task()` already includes:

- declared dependency IDs;
- canonical lifecycle + AGI status;
- policy flags and durable approval identity;
- current submission metadata.

No schema or TaskStore composition change is required.

The data flow is therefore:

```text
canonical task/review/policy rows
        ↓
read-only public source methods
        ↓
wait projection
```

There is no reverse mutation path.

## Supported reasons

### `WAIT_DEPENDENCY`

Emitted from explicit dependency IDs when the referenced task is missing or not `DONE`.

A missing dependency is a verified unresolved prerequisite because the parent task explicitly names that ID and the canonical source confirms no task exists.

Dependency waits are checked only in lifecycle states where dependencies can still gate preparation/execution:

```text
NEEDS_SHAPING
READY
ACTIVE
CHANGES_REQUESTED
BLOCKED
```

`DONE` and `READY_FOR_REVIEW` are not relabeled as dependency waits.

### `WAIT_REVIEW_UNCLAIMED`

Requires:

```text
status = READY_FOR_REVIEW
+ durable submission
+ zero open reviews
```

The projection does not assign a reviewer or infer who should review.

### `WAIT_REVIEW_IN_PROGRESS`

Requires:

```text
status = READY_FOR_REVIEW
+ durable submission
+ exactly one open review
```

It may expose review ID, reviewer ID, and structured timestamp. It never exposes/uses review summary text for causal inference and says nothing about reviewer availability or ETA.

If the source presents multiple open reviews or missing review identity, the result is `UNKNOWN` rather than choosing one.

### `WAIT_OPERATOR_APPROVAL`

Requires:

```text
status in {READY, CHANGES_REQUESTED}
+ AGI READY
+ existing policy helper says operator approval required
+ approved_by absent
+ approved_at absent
```

The module calls the accepted `task_needs_operator_approval()` helper rather than duplicating trigger-field logic.

If only one of `approved_by` / `approved_at` exists, approval evidence is inconsistent and the projection returns `UNKNOWN` rather than treating it as either approved or unapproved.

## Summary states

### `WAITING`

At least one supported `VERIFIED_WAIT` exists on a non-`BLOCKED` lifecycle state.

### `BLOCKED`

Canonical lifecycle is `BLOCKED` and at least one exact supported unresolved prerequisite is visible. The canonical lifecycle label is preserved rather than rewritten to `WAITING`.

### `UNKNOWN`

Used when causal evidence is materially inconsistent/incomplete, including generic `BLOCKED` where no supported structured prerequisite proves the cause.

### `NO_VERIFIED_WAIT`

No supported wait was found.

This **does not mean runnable**. Every projection carries:

```text
runnable_claimed = false
```

Readiness/assignment policy remains the authority for execution eligibility.

## Generic `BLOCKED` deliberately stays uncertain

Current accepted task schema has a `BLOCKED` lifecycle state but no universal typed blocker relationship.

It is tempting to inspect:

- task title/outcome;
- event summary;
- review summary;
- handoff prose;
- timestamps.

This tranche does none of that.

If a task is `BLOCKED` and no exact supported current prerequisite exists, it returns:

```text
BLOCKED_CAUSE_UNPROVEN / UNKNOWN
```

Even an old review with verdict `BLOCKED` is not used as current causal authority here. Review-subject/freshness work is still separate and a contract may have changed after that review.

## Multiple reasons are retained

A task can simultaneously have:

```text
unresolved dependency
+ missing operator approval
```

Both reasons remain visible. The projection does not select whichever one happened to be checked first.

Reason ordering is deterministic for unchanged source state.

## Coverage is explicit

The report labels source coverage independently:

```text
task_state
dependencies
review
operator_approval
communication
recovery
helpers
```

The first four are `VERIFIED`, `NOT_APPLICABLE`, or `UNKNOWN` according to the current lifecycle/evidence shape.

Communication, recovery, and helpers remain `UNKNOWN` in this tranche because no wait semantics are implemented for them.

This prevents absence of those reasons from being misread as completeness.

## No communication wait yet

Even once A4c proves:

```text
run -> exact request event -> addressee
```

that still proves only a request exists.

A future `WAIT_COMMUNICATION_RESPONSE` additionally needs an explicit structured fact that this response is required for forward progress, plus sufficient exact observation semantics.

Therefore this runtime tranche continues to enforce:

```text
no reply observed != WAITING
```

## No provider/helper/recovery inference

The module does not consume session/process/helper/recovery evidence.

These remain invalid deductions:

```text
session RUNNING -> waiting on agent
session stopped -> waiting for recovery
helper exists -> waiting on helper
elapsed time -> stuck
```

Those require their own authoritative progress-dependency contracts.

## Read-only proof

The focused tests use both fake evidence sources and a real temporary `TaskStore`.

For the real store test:

1. snapshot task state;
2. snapshot task events;
3. call `project_task_waits()`;
4. re-read task/events;
5. assert exact equality.

The projection creates no event and mutates no canonical row.

## Adversarial tests

The suite covers:

- missing task;
- terminal `DONE`;
- unresolved and missing dependencies;
- dependency completion removing the wait;
- review unclaimed/in-progress;
- ambiguous/missing review evidence;
- operator approval required/satisfied/inconsistent;
- non-AGI-ready task not mislabeled as approval wait;
- multiple simultaneous waits;
- generic `BLOCKED` with misleading task/review prose remaining `UNKNOWN`;
- `BLOCKED` plus exact dependency retaining canonical BLOCKED summary;
- ACTIVE task with no structured prerequisite not inferred waiting;
- deterministic unchanged projection;
- real TaskStore read-only behavior.

## Non-goals

No:

- `tasks.waiting` column;
- mutable wait record;
- polling daemon;
- notifications/reminders;
- timeout/stuck classification;
- `RUNNABLE` claim;
- provider/session liveness inference;
- communication/recovery/helper waits;
- review/task/event prose parsing;
- automatic reviewer/operator actions;
- automatic block/unblock mutation.

## Continuation

After A1–A4c interfaces settle, future wait sources can be added only when their owning systems expose exact progress prerequisites.

Expected sequence:

```text
structured-gate baseline (this tranche)
        ↓
exact communication root correlation
        ↓
explicit response-required dependency
        ↓
possible communication wait
        ↓
exact recovery/helper eligibility contracts
        ↓
possible recovery/helper waits
        ↓
Trace / Run Record projection
        ↓
evaluate usefulness before any monitoring machinery
```
