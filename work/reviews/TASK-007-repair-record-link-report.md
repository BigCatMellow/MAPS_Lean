# TASK-007 Repair-record link traversal report

## Route verified

Starting at the Lean repository root, the active Markdown-link route was:

1. [README.md](../../README.md) → [First Run](../../docs/FIRST_RUN.md)
2. First Run → [AGENTS.md](../../AGENTS.md), this task, current state, and the [playbook index](../../playbook/INDEX.md)
3. Playbook index → [Repair and Learning](../../playbook/REPAIR_AND_LEARNING.md)
4. Repair and Learning → [repair-record template](../../templates/repair-record.md)

No directory search, legacy content, or runtime state was used. The template was reached through the active route before any repair action.

## Repair record for the scenario

- Severity: `DRIFT`
- Owner: coordinator responsible for the authorized lifecycle recovery
- Trigger and evidence: the canonical task record is verified as `IN_PROGRESS` with an expired lease; a stale export still identifies the prior owner as active.

### Finding

The export differs from verified canonical task state. The evidence identifies a stale representation, not a conflict over the canonical record or ownership decision.

### Permitted change or proposal

Record the discrepancy, then use the authorized lifecycle recovery path to reconcile the stale representation with the verified canonical record. The repair is limited to that mechanical reconciliation; it does not assign an owner, alter the lifecycle policy, change the task schema, modify review separation, or change approved behavior.

### Verification and rollback

- Verification: re-check the canonical record and confirm the repaired/exported representation agrees that the task is `IN_PROGRESS` with an expired lease; confirm the lifecycle recovery path used the documented evidence.
- Rollback: restore the pre-repair export snapshot or reverse only the reconciliation if the verification fails; leave the verified canonical record unchanged.

### Prevention

Add or use an export-freshness/consistency validator that compares owner and lease fields against the canonical record before an export is relied upon. If this discrepancy recurs, test that validator against this failure mode.

## Mechanical boundary

This is mechanical because the canonical record has already been verified and the proposed action only corrects a stale derivative. It becomes structural if resolving it would change authority or ownership, lifecycle/policy rules, record schema, independent-review separation, or approved behavior. At that boundary, the repair must be proposed and escalated through the decision/change path rather than applied silently.
