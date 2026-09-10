# Task, Run and Flow Lifecycle

MAPS_L separates a task, a run, a provider session, and a review. They are
related, but they are not interchangeable.

- A **task** states the work, authority, lifecycle, and acceptance criteria.
- A **run** freezes the execution contract for one worker attempt.
- A **provider session** is the actual hcom/provider process used to execute.
- A **review** records an independent decision about a submitted result.

Back to [[Home]].

## Canonical task lifecycle

```text
NEEDS_SHAPING --AGI pass--> READY --claim--> ACTIVE
     ^                                      |
     |                                      v
BLOCKED <--------------------------- READY_FOR_REVIEW
                                             |
                         APPROVED ---------> DONE
                         CHANGES_REQUESTED -> CHANGES_REQUESTED -> ACTIVE
                         BLOCKED ----------> BLOCKED
```

`DONE` means the task's acceptance criteria, evidence, required review, and any
triggered operational-independence requirement are satisfied. It does not mean
the parent roadmap is complete. The orchestration operator reconciles the child
result and continues with the next eligible work inside the approved scope.

Canonical lifecycle details live in
[`playbook/TASK_LIFECYCLE.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/TASK_LIFECYCLE.md).

## Task contract and AGI readiness

A consequential task records its outcome, sources of truth, owner, allowed and
forbidden scope, inherited authority, dependencies, acceptance criteria,
verification, review requirement, and stop/escalation conditions.

The AGI gate asks whether a suitable fresh worker can execute without material
guessing and prove success. It is different from run binding:

- **AGI readiness:** is the task sufficiently specified?
- **Run binding:** what exact task revision, context, scope, worker, Git base,
  worktree, and limits did this attempt receive?

## Runs and session lineage

For consequential, resumable, or drift-sensitive work, `maps flow start`
creates an immutable run manifest. It can include context hashes, readable and
writable paths, forbidden paths, runtime limits, a Git base revision, and
worktree identity.

`maps run bind-session RUN_ID` then records the first explicit run-to-provider
session link. It does not launch anything. It self-gates to the run's current
`ACTIVE` claimant and live lease. The supplied hcom `session_id` is the
provider's durable identifier, not necessarily the display name used by
`recovery-tick --binding`.

That link lets recovery resolve the canonical run behind a stopped session and
route a resume through guarded `HarnessService` behavior.

## Current `maps flow` verbs

Capability row 6.21 remains **IN PROGRESS** because the family is not a full
end-to-end lifecycle. The following verbs are implemented on `main`.

| Verb | What it does | Intentional stop boundary |
| --- | --- | --- |
| `flow start` | claims an explicit worker, discovers/catalogs project Skills, builds the context plan, creates an immutable run manifest, and records environment evidence when the task has a contract | does not choose a worker, launch a provider, attach a session, or send a message |
| `flow review-start` | checks review-subject requirements, claims review for an explicit reviewer, and optionally binds the immutable subject | does not choose a reviewer, write review evidence, or record a verdict |
| `flow review-record` | runs the canonical review transition and supports re-derived evidence for `REDERIVED_AT_REVIEW` | does not record later real-world outcomes or dispatch follow-on work |
| `flow handoff` | verifies the outgoing worker is the recorded claimant and appends a worker-continuity link | does not release the old claim, select/claim the replacement, create a new run, or launch a session |
| `flow release-check` | evaluates caller-supplied artifact-identity and release-smoke evidence and appends a release-check record | does not acquire an artifact, run a benchmark itself, or record the review verdict |

There is no implemented `flow recover` verb. Review/recovery lifecycle
composition remains one reason row 6.21 is not DONE.

## Review-subject freshness

Consequential review can bind the exact subject using one of three modes:

- `REVISION_BOUND` — approve the named immutable run/artifact state.
- `REDERIVED_AT_REVIEW` — the reviewer must supply newly derived immutable
  artifact/evidence references before an `APPROVED` verdict.
- `NON_CONSEQUENTIAL` — used only where exact revision binding is not required.

`flow review-record` checks only the caller's own open review before exposing
the re-derivation preflight. The underlying store still enforces review
ownership, independence, acceptance-criterion evidence, and final status.

## Handoffs and review independence

`flow handoff` records that one worker continues another worker's work. The
continuity relationship is global and undirected in the current schema, not
task-scoped. As a result, the incoming worker and the connected continuity
component cannot later act as an independent reviewer of work authored by that
component.

The handoff accepts an expired-but-still-recorded outgoing claim because a dead
session is a normal reason to hand work off. The incoming worker must still
claim-recover the task after the outgoing lease expires and create its own run.

## Release checks

`flow release-check` applies only to a task whose review requirement is
`OPERATOR_VISIBLE_RELEASE_CHECK` and whose open review has the required bound
subject. It records an append-only assessment of:

- expected versus observed artifact identity; and
- caller-supplied release-smoke evidence.

The composite becomes `BLOCKED` when either evaluator reports failure. An
`APPROVED` review is then refused unless the latest release-check row carries a
non-empty `operator_ack_ref`. This is a recorded, auditable override—not a
`--force` flag. A missing release check is also approval-blocking for this
review type.

The check can report `READY_FOR_OPERATOR_VERDICT` with incomplete or unknown
evidence; the reviewer/operator must still judge those gaps. The flow does not
create a separate universal `RELEASED` task state.

Source: current CLI and
[`CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md).
