# Task: explainable waits Wave 3 design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `agent/explainable-waits-design-wave3`
- Risk: `MEDIUM`
- Goal: Define a read-only, evidence-backed wait/block explanation model that derives from canonical MAPS state and exact communication lineage without creating a second task lifecycle, polling service, or inferred pending state.

## Inputs and source of truth

- Root `AGENTS.md`.
- Current merged task/readiness/review/policy semantics inspected from `main`.
- `runtime/state/readiness.py`:
  - explicit task dependencies;
  - dependency must exist and be `DONE` for readiness;
  - dependency-only readiness failures surface `BLOCKED_ON_DEPENDENCY`.
- `runtime/state/review.py`:
  - `READY_FOR_REVIEW` is canonical reviewable state;
  - at most one open review;
  - structured verdict `BLOCKED` moves task to `BLOCKED`.
- `runtime/state/policy.py` and `runtime/policy/evaluator.py`:
  - operator-gated policy flags and durable approval evidence;
  - assignment may return `require_approval` when an otherwise eligible task lacks required approval.
- PR #45 prospective exact hcom message relationships:
  - `reply_to_local` only for reply ancestry;
  - bounded absence = `NOT_OBSERVED_IN_INPUT`, not global pending/waiting.
- PR #51 prospective A4c exact task/run -> provider-event correlation design.
- A1/A2/A3 PRs #48/#49/#50 are active parallel-agent work and MUST NOT be modified by this task.

Source ordering:

1. canonical task/review/policy/dependency rows;
2. accepted exact execution-lineage relationships when available;
3. accepted exact provider communication relationships when available;
4. derived wait projection;
5. prose/event summaries are diagnostic only and never a substitute for structured causal evidence.

## Change boundary

MAY CHANGE:

- `work/tasks/explainable-waits-wave3.md`
- `work/notes/2026-08-15-explainable-waits-design.md`

MUST NOT CHANGE:

- runtime code;
- `schema.sql` or `store.py`;
- task status transitions;
- review/policy semantics;
- A1/A2/A3 branches;
- PR #44/#45/#51 implementation/design branches;
- hcom/provider behavior;
- recovery/helper stores.

No automatic blocking/unblocking, timers, polling, notifications, or provider calls are authorized by this planning task.

## Core rule

**A wait explanation is a derived claim about why progress cannot currently continue. It is not task authority.**

A reason may be reported as `WAITING` only when:

1. a structured source proves the unresolved prerequisite;
2. the same source or an accepted contract proves that prerequisite is required for forward progress;
3. the prerequisite has not already been satisfied or invalidated;
4. the evidence is current for the relevant task/run state.

If any required join is missing, the explanation is `UNKNOWN` / `NO_VERIFIED_WAIT`, not an inferred wait.

## Evidence classes

### VERIFIED_WAIT

A structured unresolved prerequisite with a mechanically established progress dependency.

Initial candidate reasons:

- `WAIT_DEPENDENCY`
- `WAIT_REVIEW_UNCLAIMED`
- `WAIT_REVIEW_IN_PROGRESS`
- `WAIT_OPERATOR_APPROVAL`
- future `WAIT_COMMUNICATION_RESPONSE` only after A4c plus an explicit response-required/progress-blocking contract exists
- future `WAIT_RECOVERY_RETRY` only if RecoveryStore exposes an exact not-before/next-attempt prerequisite tied to the run

### STRUCTURED_BLOCKER

Canonical state proves execution is blocked, but the condition is not merely a wait for an external prerequisite or the exact causal prerequisite is not structured.

Examples:

- `BLOCKED_BY_REVIEW` when the current/most relevant structured review verdict is `BLOCKED`;
- stale run / stale task revision where accepted execution evidence says continuation is invalid;
- exhausted attempt/recovery limit if exact canonical/recovery state proves it.

A blocker is not automatically a wait.

### NO_VERIFIED_WAIT

No active wait condition can be established from available structured evidence. This does **not** mean the task is runnable.

### UNKNOWN

The task appears blocked or non-progressing, but the cause cannot be derived without parsing prose, inferring from timing/liveness, or crossing an incomplete lineage join.

## Initial wait rules

### WAIT_DEPENDENCY

Evidence:

- task has explicit `task_dependencies` entries;
- one or more dependencies are missing or not `DONE`.

Projection may identify exact dependency IDs and canonical statuses.

Do not create new dependencies from messages, task prose, or inferred sequencing.

### WAIT_REVIEW_UNCLAIMED

Evidence:

- task canonical status is `READY_FOR_REVIEW`;
- durable submission exists;
- no open review exists.

Meaning:

- implementation has reached the review gate;
- no reviewer currently owns that gate.

This is a workflow wait explanation, not a request to auto-assign a reviewer.

### WAIT_REVIEW_IN_PROGRESS

Evidence:

- task is `READY_FOR_REVIEW`;
- an open review exists with an exact reviewer ID.

Projection may identify the review record/reviewer and creation time.

Do not infer reviewer availability, responsiveness, or ETA.

### WAIT_OPERATOR_APPROVAL

Evidence:

- task is otherwise at an executable gate (`READY` or `CHANGES_REQUESTED`, subject to final accepted policy semantics);
- AGI readiness is valid/current;
- structured policy says approval is required;
- canonical approval evidence is absent.

Do not call a task waiting for approval merely because an operator-gated flag exists while the task is also unready for independent reasons. Report all verified blockers/waits or use precedence without hiding the stronger cause.

### BLOCKED_BY_REVIEW

Evidence:

- canonical task status is `BLOCKED`;
- a structured completed review verdict is `BLOCKED` for the current relevant submission/review state.

The projection may say review blocked the task. It MUST NOT parse the free-text review summary to invent a more specific causal reason.

If task status is `BLOCKED` but no structured blocker relationship can be proven, causal explanation is `UNKNOWN`.

## Communication wait rule

A hcom request is not automatically a task wait.

Even after A4c can prove:

```text
run R -> exact request event E -> exact addressee(s)
```

that proves only that a request exists.

To report `WAIT_COMMUNICATION_RESPONSE`, MAPS additionally needs structured evidence that:

- this request/operation is an unresolved prerequisite for progress;
- the task/run has not chosen another valid path that removes the dependency;
- observation coverage is sufficient for the declared wait semantics.

`NOT_OBSERVED_IN_INPUT` from PR #45 is never enough by itself.

Therefore:

```text
request event + no reply in bounded window != WAITING
```

and:

```text
exact request event
+ exact run attribution
+ explicit response-required progress dependency
+ no satisfying exact reply under declared observation semantics
= candidate WAIT_COMMUNICATION_RESPONSE
```

The explicit progress-dependency primitive is not designed here because A4c provider correlation and A1/A2/A3 interfaces are still settling. Do not invent another request lifecycle prematurely.

## Provider/session rule

Provider/session liveness is evidence about provider state only.

These are prohibited inferences:

- `RUNNING` session => task making progress;
- inactive session => task waiting;
- provider session exists => API/provider readiness;
- no provider activity for N minutes => task blocked;
- helper process exists => task waiting on helper.

Only accepted structured progress dependencies may create wait explanations.

## Recovery/helper rule

A2 relationship evidence alone says which helper/recovery lineage belongs to which run. It does not prove a wait.

Future recovery wait projection may be valid only if the authoritative recovery source exposes something like:

```text
retry allowed
next eligible attempt = T
current time < T
```

or another exact unresolved recovery prerequisite.

A helper invocation with no result yet is not automatically a wait; bounded helpers may be synchronous, failed, abandoned, or advisory. Use the helper/recovery source semantics, not mere existence.

## Projection shape

Conceptual read model:

```json
{
  "task_id": "TASK-1",
  "summary_state": "WAITING",
  "reasons": [
    {
      "code": "WAIT_DEPENDENCY",
      "state": "VERIFIED_WAIT",
      "source_refs": ["task:TASK-2"],
      "details": {"dependency_status": "ACTIVE"}
    }
  ],
  "coverage": {
    "task_state": "VERIFIED",
    "dependencies": "VERIFIED",
    "review": "VERIFIED",
    "operator_approval": "VERIFIED",
    "execution_lineage": "UNKNOWN",
    "communication": "UNKNOWN",
    "recovery": "UNKNOWN"
  },
  "authority": "DERIVED_READ_ONLY"
}
```

Suggested summary states:

- `WAITING` — at least one `VERIFIED_WAIT` exists;
- `BLOCKED` — no verified wait, but at least one `STRUCTURED_BLOCKER` exists;
- `NO_VERIFIED_WAIT` — no verified wait/blocker is found and coverage is sufficient for the checked sources, without claiming runnable;
- `UNKNOWN` — causal coverage is materially incomplete or canonical state implies blockage but no structured cause can be proven.

Do not introduce `RUNNABLE` here. Existing readiness/policy/assignment mechanisms own execution eligibility.

## Multiple reasons / precedence

Do not collapse evidence into one guessed cause.

Projection should retain every current verified reason. The summary is only a convenience:

1. any verified wait -> `WAITING` unless a stronger canonical terminal/blocker state makes `BLOCKED` more accurate;
2. otherwise any structured blocker -> `BLOCKED`;
3. otherwise material causal uncertainty -> `UNKNOWN`;
4. otherwise `NO_VERIFIED_WAIT`.

A future implementation must define exact precedence against terminal `DONE`, `NEEDS_SHAPING`, etc. It should not label terminal/non-executable lifecycle states as waits merely to fit this model.

## Freshness

Wait explanations are read-time derived. They should not be durable mutable state that requires synchronization.

Every read should resolve current canonical sources. If a dependency becomes `DONE`, review closes, or approval arrives, the next projection changes accordingly without an explicit "clear wait" mutation.

This avoids a second `waiting` state machine drifting from task/review/policy truth.

## Privacy

Projection may contain stable IDs, reason codes, statuses, bounded timestamps, and evidence references.

Do not copy:

- message bodies;
- review summaries as machine reason text;
- task free-text prose as causal authority;
- secrets/provider transcripts;
- helper raw output.

## Acceptance criteria

- [x] Wait explanation is defined as a derived read model, not task state.
- [x] Explicit dependency waits use canonical dependency/status evidence.
- [x] Review wait states use structured review ownership/status evidence.
- [x] Operator approval wait uses canonical policy/approval evidence.
- [x] Review `BLOCKED` is distinguishable from a wait.
- [x] Generic task `BLOCKED` without structured cause preserves `UNKNOWN`.
- [x] Message/request absence cannot create waiting.
- [x] Session/provider liveness cannot create waiting.
- [x] Helper/recovery relationship existence cannot create waiting.
- [x] Future communication wait requires exact A4c root correlation plus an explicit progress dependency.
- [x] No `RUNNABLE` claim is introduced.
- [x] No runtime/schema/other-agent branch is modified.

## Future tests

When implementation is shaped, minimum cases should include:

1. unresolved explicit dependency -> `WAIT_DEPENDENCY`;
2. dependency becomes DONE -> wait disappears without wait-state mutation;
3. READY_FOR_REVIEW + no open review -> `WAIT_REVIEW_UNCLAIMED`;
4. READY_FOR_REVIEW + open review -> `WAIT_REVIEW_IN_PROGRESS`;
5. completed BLOCKED review -> `BLOCKED_BY_REVIEW`, not parsed summary reason;
6. generic BLOCKED task without structured cause -> `UNKNOWN`;
7. otherwise-ready operator-gated task without approval -> `WAIT_OPERATOR_APPROVAL`;
8. same task with approval -> approval wait disappears;
9. hcom request with no reply in bounded input -> no communication wait;
10. same-thread unrelated response -> no communication wait;
11. exact reply without explicit progress dependency -> no communication wait;
12. provider RUNNING/INACTIVE state alone -> no wait;
13. helper lineage alone -> no wait;
14. multiple structured reasons remain visible simultaneously;
15. projection mutates no canonical table;
16. repeated unchanged read is deterministic except explicitly current-time-sensitive recovery eligibility.

## Verification and review

Verification:

- source modules above inspected directly;
- PR #45/#51 constraints checked;
- branch diff contains only the two planning files approved here.

Review required: `INDEPENDENT_REVIEW`.

## Stop / escalation

Stop rather than infer if:

- wait cause requires parsing task/review/message prose;
- communication run attribution is not exact;
- response-required/progress dependency is not structured;
- provider liveness is the only evidence;
- recovery/helper authoritative state lacks exact eligibility semantics;
- implementation would collide with active A1/A2/A3 work.

## Continuation

After A4c and execution-lineage interfaces settle:

1. re-check accepted task/review/policy/run/communication interfaces;
2. implement a pure/read-only wait projection over existing sources;
3. add communication wait only if an explicit progress-dependency contract exists;
4. enrich Trace/Run Record coverage without creating durable `waiting` state;
5. evaluate whether the explanation improves operator/agent decisions before adding any monitoring/notification behavior.
