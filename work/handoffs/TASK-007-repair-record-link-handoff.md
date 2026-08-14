# Handoff: TASK-007 repair-record link traversal

- From: lean-repair-route-helper
- To: coordinator
- Task: [TASK-007](../tasks/TASK-007-repair-record-link-traversal.md)
- Status: complete

## What is true now

- The active link route from the repository root reaches the repair-record template: README → First Run → playbook index → Repair and Learning → repair-record template.
- The scenario is `DRIFT`; its evidence is the verified canonical `IN_PROGRESS` record with an expired lease and the contradictory stale export.

## Decisions and constraints

- Only a mechanical reconciliation of the stale derivative is permitted after the repair record is captured.
- Any change to authority, ownership, policy, schema, review separation, or approved behavior is structural and requires the decision/change path.
- No legacy content or runtime state was accessed.

## Next action

1. Coordinator may use the authorized lifecycle recovery path, using the report as the durable repair record.

## Evidence / paths

- [Repair report](../reviews/TASK-007-repair-record-link-report.md)
- [Repair and Learning](../../playbook/REPAIR_AND_LEARNING.md)
- [Repair-record template](../../templates/repair-record.md)
