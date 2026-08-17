# Explainable waits — derived evidence design

Date: 2026-08-15/16
Owner: `agent/explainable-waits-design-wave3`
Status: planning evidence only

## Problem

MAPS can increasingly explain **what happened**:

- canonical task lifecycle;
- exact run/session lineage;
- helper/recovery lineage;
- submission-attempt attribution;
- exact provider communication events and reply relationships.

The next temptation is to turn those facts into a generic `WAITING` state.

That would be dangerous if done loosely. A silent task, a live session, a missing reply in the last 100 events, an open helper run, and a human-readable review note are all observations. None independently proves:

> forward progress is currently impossible until X happens.

A4d should therefore be an **explanation layer over existing authorities**, not another scheduler/state machine.

## Design principle

```text
structured prerequisite
+ proof that prerequisite gates progress
+ proof prerequisite remains unresolved
= explainable wait
```

Anything weaker stays a blocker, a provider observation, or `UNKNOWN`.

## Existing structured sources

### Task dependencies

Merged readiness logic already treats declared task dependencies as real prerequisites. A dependency that does not exist or is not `DONE` blocks readiness.

This is the cleanest wait evidence in the current system because both halves are structured:

1. dependency relationship exists;
2. dependency's current status is known.

No new wait table is needed.

### Review gate

`READY_FOR_REVIEW` already means implementation has reached a mandatory review phase. Reviews have structured identity and completion state.

Two distinct explanations can therefore be derived:

```text
READY_FOR_REVIEW + no open review
→ waiting at unclaimed review gate
```

and:

```text
READY_FOR_REVIEW + open review R
→ waiting at active review gate R
```

This does not imply the reviewer is late, available, online, or expected to respond by a particular time.

### Operator approval

Policy already has explicit operator-gated flags plus durable approval evidence. Assignment policy can distinguish an otherwise eligible task that needs approval from a task rejected for unrelated reasons.

That supports a narrow approval wait:

```text
otherwise executable
+ approval required
+ approval absent
→ WAIT_OPERATOR_APPROVAL
```

It should not hide unrelated readiness blockers.

### Review BLOCKED verdict

A completed review verdict of `BLOCKED` is structured causal evidence that review blocked the task.

It is not necessarily a wait. The task may require redesign, operator intervention, abandonment, or some other resolution.

A4d should report:

```text
BLOCKED_BY_REVIEW
```

and preserve the review record reference.

It should not parse the review summary to manufacture a more specific code.

## Why generic task BLOCKED is not enough

The task lifecycle has a `BLOCKED` status, but the current schema does not require a typed blocker relationship for every way a task can reach that state.

Therefore:

```text
task.status = BLOCKED
```

proves the lifecycle state but may not prove the causal reason.

If no structured source supplies the cause, the correct projection is approximately:

```json
{
  "summary_state": "UNKNOWN",
  "reasons": [
    {
      "code": "BLOCKED_CAUSE_UNPROVEN",
      "state": "UNKNOWN"
    }
  ]
}
```

Reading `task_events.summary`, review prose, chat, or handoff prose to guess the cause would downgrade source quality and create accidental authority from text.

## Communication is the hardest wait source

PR #45 deliberately uses:

```text
NOT_OBSERVED_IN_INPUT
```

when no response appears in a bounded set of hcom events.

That is exactly right.

Even once PR #51's A4c design is implemented and MAPS can prove:

```text
run R
→ request event E
→ addressee A
```

we still know only that R sent a request to A.

We do **not** yet know that R must stop all useful work until A replies.

### Required extra fact

A future communication wait needs a structured progress dependency, conceptually something like:

```text
operation/request Q
response_required = true
blocks_progress = true
```

or another accepted contract expressing the same semantic fact.

This design intentionally does not freeze that schema/API. A1/A2/A3 are moving quickly, and adding a new request lifecycle before the exact operation interface settles would violate the smallest-change rule.

### Exact communication ancestry still matters

If request event `E` is exactly linked to run `R`, then an hcom event with:

```text
reply_to_local = E
```

can be treated as an exact response descendant.

But:

- same thread is not enough;
- same sender is not enough;
- same recipient is not enough;
- later timestamp is not enough;
- similar text is not enough.

Thus communication wait evaluation eventually needs both:

```text
exact root correlation
+ explicit progress dependency
```

not one or the other.

## Bounded observation semantics

A future communication wait evaluator must declare what its observation boundary means.

Example distinction:

```text
read last 100 events
→ no reply observed
```

is only a bounded observation.

It cannot establish that a reply does not exist outside the window.

A trustworthy implementation might instead query by exact parent/reply relationship or maintain a provider-supported exact lookup. Until the accepted provider interface proves sufficient coverage, the response state stays `UNKNOWN` / `NOT_OBSERVED_IN_INPUT`.

This prevents a small read window from silently becoming global truth.

## Session and process liveness are not wait causes

The following facts can be useful operational evidence:

- session exists;
- session reports RUNNING;
- process is alive;
- helper process exists;
- no provider heartbeat recently;
- provider session stopped.

They do not prove why task progress is or is not happening.

Examples of invalid projections:

```text
session RUNNING
→ WAITING_ON_AGENT        # invalid
```

```text
session STOPPED
→ WAITING_FOR_RECOVERY    # invalid without recovery prerequisite
```

```text
helper invocation exists
→ WAITING_ON_HELPER       # invalid without helper state/progress contract
```

Liveness and wait causality must remain separate evidence dimensions.

## Recovery wait

A2 links runs to recovery relationships but intentionally leaves RecoveryStore as authority for recovery state.

A future recovery wait could be legitimate if RecoveryStore exposes a precise condition such as:

```text
incident I
retry_state = ELIGIBLE_AFTER
not_before = 2026-08-16T04:30:00Z
```

Then, while current time precedes that boundary, a read model may explain:

```text
WAIT_RECOVERY_RETRY
```

with the exact incident and eligibility references.

No such claim should be derived merely from:

- a recovery link existing;
- an incident existing;
- a helper failing;
- elapsed time since failure.

## Helper wait

Bounded helper runs complicate generic waiting because the caller may be synchronous or asynchronous, and helper results can be advisory.

The existence of a helper relationship says:

```text
run R invoked helper H
```

not:

```text
R cannot progress until H finishes
```

If a future helper contract explicitly marks a helper result as required for a particular operation, that could become a wait prerequisite. Until then, helper lineage is context, not causal wait evidence.

## Proposed read-model vocabulary

### Reason states

`VERIFIED_WAIT`
: Structured prerequisite is proven, progress dependency is proven, prerequisite is unresolved.

`STRUCTURED_BLOCKER`
: Structured evidence proves an execution blocker but not a mere wait condition.

`UNKNOWN`
: A causal explanation cannot be established from the structured sources available.

### Summary states

`WAITING`
: At least one current `VERIFIED_WAIT` is active, subject to terminal/blocker precedence.

`BLOCKED`
: Structured blocker exists and a wait summary would be misleading.

`NO_VERIFIED_WAIT`
: Checked sources contain no verified wait. This explicitly does **not** mean runnable.

`UNKNOWN`
: Coverage or causal attribution is materially incomplete.

There is deliberately no `RUNNABLE` summary state. Assignment/readiness/policy already own that question.

## Candidate reason codes

Initial codes that can be implemented from current structured evidence:

```text
WAIT_DEPENDENCY
WAIT_REVIEW_UNCLAIMED
WAIT_REVIEW_IN_PROGRESS
WAIT_OPERATOR_APPROVAL
BLOCKED_BY_REVIEW
BLOCKED_CAUSE_UNPROVEN
```

Future evidence-gated codes:

```text
WAIT_COMMUNICATION_RESPONSE
WAIT_RECOVERY_RETRY
WAIT_HELPER_RESULT
```

The future codes should not be implemented until their authoritative prerequisite contracts exist.

## Multi-reason behavior

A task can have more than one unresolved prerequisite.

For example:

```text
explicit dependency A not DONE
+ operator approval missing
```

The projection should preserve both source-backed reasons rather than selecting whichever happened to be checked first.

Likewise, a stronger blocker should remain visible even if a wait also exists.

The read model should therefore return a reason collection plus a summary, not a single mutable `wait_reason` field.

## Suggested projection

```json
{
  "task_id": "TASK-42",
  "summary_state": "WAITING",
  "reasons": [
    {
      "code": "WAIT_DEPENDENCY",
      "classification": "VERIFIED_WAIT",
      "source_refs": ["task:TASK-17"],
      "details": {
        "dependency_status": "ACTIVE"
      }
    },
    {
      "code": "WAIT_OPERATOR_APPROVAL",
      "classification": "VERIFIED_WAIT",
      "source_refs": ["policy:TASK-42"],
      "details": {
        "approval_required": true,
        "approval_present": false
      }
    }
  ],
  "coverage": {
    "task": "VERIFIED",
    "dependencies": "VERIFIED",
    "review": "VERIFIED",
    "operator_approval": "VERIFIED",
    "run_lineage": "UNKNOWN",
    "communication": "UNKNOWN",
    "recovery": "UNKNOWN",
    "helpers": "UNKNOWN"
  },
  "authority": "DERIVED_READ_ONLY"
}
```

The exact JSON spelling should remain provisional until implementation is shaped against accepted interfaces.

## Source references instead of copied truth

Wait reasons should point to their sources rather than duplicating mutable truth.

Examples:

- task dependency ID/status should be read from task state;
- review ownership from review rows;
- approval from task policy;
- communication event/reply state from hcom-derived communication evidence;
- recovery eligibility from RecoveryStore.

The projection can include bounded current values for usability, but canonical sources remain authoritative and are re-read on the next projection.

## No durable WAITING state

A durable wait table would immediately introduce synchronization questions:

- who sets it when a dependency becomes incomplete?
- who clears it when the dependency finishes?
- what if approval arrives while the wait row is stale?
- what if the reviewer changes?
- what if communication coverage changes?

Those are signs that wait is a view, not a new authority.

Preferred architecture:

```text
canonical sources
      ↓
pure wait projector
      ↓
trace / CLI / operator UI
```

No separate mutation is required when the reason appears or disappears.

## Lifecycle handling

Not every non-executing task is waiting.

Examples:

- `DONE`: terminal, not waiting;
- `NEEDS_SHAPING`: needs contract work, not necessarily waiting;
- `READY`: may be executable or approval-gated;
- `ACTIVE`: may be working, blocked inside execution, or have no verified wait;
- `READY_FOR_REVIEW`: review-gate waits can be derived;
- `CHANGES_REQUESTED`: may be executable again; do not label waiting without another prerequisite;
- `BLOCKED`: blocker is known at lifecycle level, but cause may be structured or `UNKNOWN`.

A future implementation should keep lifecycle state separate from wait summary instead of remapping every lifecycle status into a wait code.

## Review semantics

`WAIT_REVIEW_UNCLAIMED` should not cause automatic review assignment.

`WAIT_REVIEW_IN_PROGRESS` should not cause reviewer reminders or timeout enforcement.

Those are separate orchestration/notification behaviors and would require their own evidence/authority decisions.

Likewise, review duration alone must not cause a transition from "in progress" to "stuck" without an explicit service-level expectation or operator rule.

## Operator approval semantics

Operator approval is particularly important to keep non-automated.

A wait projector may explain:

> Task cannot pass the assignment gate because required operator approval has not been recorded.

It may not:

- infer approval from chat text;
- request approval automatically unless separately authorized;
- record approval;
- weaken the underlying policy requirement;
- turn elapsed time into implicit approval.

## Explainability vs diagnosis

This capability should answer:

> Which structured prerequisite currently prevents progression?

It is not a general diagnosis engine for:

- why an agent is slow;
- whether a model is confused;
- whether a human forgot something;
- whether network/provider health is bad;
- why no files changed recently.

Those might later become operational observations, but they require separate evidence and must not contaminate the wait model.

## A4c dependency

Communication waits stay disabled until A4c can produce exact root event attribution.

PR #51 established the precise provider gap: current hcom creates the exact event ID but does not expose it at the CLI send boundary.

Therefore the future chain is:

```text
hcom structured send receipt
→ exact run ↔ event root link
→ exact reply descendants
→ explicit response-required progress dependency
→ explainable communication wait
```

Skipping any link yields `UNKNOWN`, not a probabilistic wait.

## Trace / Run Record integration

Once implemented, trace can expose the wait projection as a derived section.

Run Record should preserve:

- reason codes;
- source/evidence refs;
- coverage status;
- projection version;
- no raw message/review/helper prose.

Replay should not claim a wait was globally true beyond the source snapshot available to that record.

## Evaluation questions

Before building monitoring around waits, evaluate whether this read model actually improves decisions:

1. Can a new agent identify the next legitimate action faster?
2. Does it reduce duplicate outreach/retries?
3. Does it avoid false "waiting" diagnoses?
4. Are `UNKNOWN` cases understandable enough to trigger the right inspection?
5. Does it preserve operator/reviewer boundaries?
6. Does it remain useful without a new daemon?

If the answers are weak, do not add permanent monitoring machinery.

## Future implementation sequence

```text
accepted A1/A2/A3
accepted A4a/A4b
A4c exact root communication join
        ↓
pure wait projector for existing structured gates
        ↓
trace/Run Record projection
        ↓
add communication wait only with explicit progress dependency
        ↓
evaluate usefulness
        ↓
consider notifications/monitoring only if evidence warrants
```

## Non-goals

- no `tasks.waiting` column;
- no `wait_reason` mutable column;
- no polling daemon;
- no timeout-based stuck detector;
- no automatic reviewer/operator reminders;
- no provider liveness inference;
- no message-body parsing;
- no review-summary parsing;
- no automatic block/unblock mutation;
- no helper auto-kill;
- no automatic recovery action;
- no `RUNNABLE` replacement for existing policy/readiness evaluation.

## Handoff

This design is intentionally independent from the active A1/A2/A3 branches. Runtime implementation should wait until those interfaces plus A4c settle, then use current accepted sources rather than copying this draft's provisional field names blindly.
