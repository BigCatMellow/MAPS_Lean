# Handoff: TASK-006 incident triage

- From: lean-triage-helper
- To: coordinator / authorized control-plane owner
- Task: [TASK-006](../tasks/TASK-006-incident-triage-route-simulation.md)
- Status: `BLOCKED` pending read-only canonical evidence

## What is true now

- The export (`IN_PROGRESS`), expired lease, and Agent A handoff (claimed
  submission) conflict; none alone authorizes a lifecycle mutation.
- SQLite is the canonical mutable task ledger. Independent review requires a
  reviewer other than the recorded submitter.

## Decisions and constraints

- Do not directly set `TASK-ALPHA` to `SUBMITTED` from the export or handoff.
- Use an authorized guarded route only after canonical state, evidence, and
  submission authorship are verified. Escalate ambiguity or structural change.

## Next action

1. Read the canonical SQLite task/submission/review records and referenced
   evidence; then route to independent review, authorized recovery, or
   escalation according to the result.

## Evidence / paths

- [Triage report](../reviews/TASK-006-incident-triage-report.md)
- [Control-plane guidance](../../playbook/CONTROL_PLANE.md)
- [Repair guidance](../../playbook/REPAIR_AND_LEARNING.md)
