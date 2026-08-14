# TASK-006 Incident-triage report

- Task: [TASK-006](../tasks/TASK-006-incident-triage-route-simulation.md)
- Evaluator: lean-triage-helper
- Verdict: `BLOCKED` pending authoritative, read-only evidence

## Incident classification

This is **blocking drift** (and an unverified lifecycle conflict), not proof
that `TASK-ALPHA` is submitted. The status export says `IN_PROGRESS`; the
handoff claims an implementation submission; and the expired lease permits a
recovery decision to be considered. None is the canonical mutable task truth.
Under the active control-plane guidance, that truth is the SQLite ledger.

The proposed direct edit to `SUBMITTED` is **disallowed now**. It would replace
unverified secondary-state claims with a lifecycle mutation and could bypass
claim/submission provenance and the independent-review gate. An expired lease
does not itself establish that Agent A submitted work, and RnS/hcom recovery
does not auto-claim, reassign, or invent work.

## Required authoritative check

Perform a read-only inspection of the canonical SQLite record for
`TASK-ALPHA`, preserving the result as evidence. Confirm:

- current lifecycle state and task identity;
- successful claimant/owner, lease expiry, and relevant heartbeat/claim
  history;
- a canonical submission record, its submitter, timestamp, and associated
  evidence/artifact references; and
- any review record or gate, especially whether a proposed reviewer is
  independent of the recorded submitter.

Also inspect the cited implementation evidence/artifacts and reconcile the
handoff's assertion with the ledger. The export and handoff should be retained
as conflicting inputs, not used to overwrite canonical state.

## Safe route after inspection

1. If the ledger records a valid submission by Agent A with sufficient
   evidence, route the task to an independent reviewer through the canonical
   review path. Agent A must not review or approve their own submission.
2. If the ledger remains active with an expired lease and has no verified
   submission, use the authorized recovery/claim-or-assign route; do not label
   the task submitted. Preserve Agent A's handoff for the recovering owner to
   evaluate.
3. If the ledger and evidence cannot establish a coherent, authorized state,
   keep the incident `BLOCKED` and escalate rather than selecting a state from
   the export or handoff.

A status correction is conditionally permissible only after authoritative
evidence establishes the exact intended state and an authorized actor uses the
ledger's guarded lifecycle process. It is a **mechanical repair** only when it
reconciles a verified state without changing ownership, review separation,
authority, data shape, or approved behavior; record trigger/evidence, change,
verification, rollback, and prevention. Changing lease semantics, allowing
secondary records to set lifecycle state, altering review separation, or
changing the ledger/schema is a **structural change**: propose it through a
decision/change path and obtain the required approval.

## Escalation boundary and records

Escalate to the operator/control-plane owner if canonical evidence is missing
or contradictory, submission authorship is ambiguous, a forced/history-
overriding mutation is proposed, or any policy/schema/authority rule must
change. Do not perform a database mutation while that boundary is unresolved.

Use the existing task record as scope and acceptance evidence; use the
[handoff template](../../templates/handoff.md) to preserve the next route and
facts; use the [review template](../../templates/review.md) when an independent
review is initiated (required by the task scenario, and the active template
also governs medium/high-risk review); and create a repair note for any actual
drift repair. The ledger inspection and linked evidence are the required proof.

## Verification

Owner check: this report makes no runtime/database change, treats SQLite as
canonical, retains `BLOCKED` until evidence is inspected, and preserves the
no-self-review requirement.
