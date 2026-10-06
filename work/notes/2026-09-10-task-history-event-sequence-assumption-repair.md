# Repair Record: task-history event-sequence assumption

- Severity: `DRIFT`
- Owner: `orchestration-operator`
- Trigger and evidence: PR #339 Runtime stack tests #1650 failed only `tests.test_task_history_retention.TaskHistoryRetentionTests.test_normal_lifecycle_still_appends_new_events`; actual event sequence included `TASK_POLICY_UPDATED`, while the new regression omitted it. An earlier owner-side assertion draft had also used the wrong READY event name before source inspection corrected it to `TASK_PROMOTED_READY`.

## Finding

The retention guards themselves behaved as intended, but the new exact event-sequence regression was written from an incomplete mental model of contract shaping. `update_contract()` participates in registered shaping hooks; the policy hook appends `TASK_POLICY_UPDATED` before `TASK_CONTRACT_UPDATED`. Therefore the expected normal path is:

```text
TASK_CREATED
→ TASK_POLICY_UPDATED
→ TASK_CONTRACT_UPDATED
→ TASK_PROMOTED_READY
→ TASK_CLAIMED
```

The failed assertion was test drift, not accepted-runtime drift.

## Change or proposal

Corrected only `tests/test_task_history_retention.py` to bind the assertion to the canonical event vocabulary and include `TASK_POLICY_UPDATED`. No runtime or schema behavior was changed by this repair.

## Verification and rollback

- Verification: exact repaired head `977a6a6be7f6ec7491246e2e9d477fb721204e34`; Runtime stack tests #1651 completed `SUCCESS`. The direct event UPDATE/DELETE and canonical-task DELETE regressions also pass in that run.
- Rollback: revert the test-only correction commit if the underlying accepted shaping/event contract changes through a separately authorized change; do not alter runtime merely to satisfy this assertion.

## Prevention

First occurrence of this root-cause class in this lane. For exact semantic-event sequence assertions, inspect the canonical lifecycle method **and every active contract-shaping hook** before freezing expected vocabulary/order. The repaired regression now mechanically exposes future drift in this particular normal shaping → READY → claim path; no broader checker is justified from one incident.
