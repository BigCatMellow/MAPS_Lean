# Repair Record

Repair ID: REPAIR-0010
Related task: TASK-280
Found by: claude-lab-venu
Date: 2026-07-27
Severity: STRUCTURAL
Status: APPLIED

## What was found

TASK-280 reached `attempt=3` with `max_attempts=3` after its second
CHANGES_REQUESTED verdict (`REV-TASK-280-codex-lab-diro-3e31733f`). SQLite
`claim_task()` guards every claim with `AND attempt < max_attempts`
(`MAP_System/db/claims.py:160`), so `rework` can still move the task
CHANGES_REQUESTED -> READY, but no further claim can succeed. No sanctioned
`map_task.py` verb exists to raise `max_attempts` on an existing task.

## Surfaced by

Manual observation while routing TASK-280's second re-review verdict; the
reviewer's own Risks Identified section flagged the same durable ceiling and
recommended operator disposition before further attempts
(`MAP_System/artifacts/reviews/task280-rereview-diro.md`).

## Severity rationale

Raising a task's durable attempt budget changes what the claim gate will
allow going forward — a lifecycle-authority parameter, not a content or
mirror fix. Narrow (one integer, one task) and fully reversible (can be
lowered back or left as-is once the task reaches a terminal state), but per
`SELF_REPAIR_SYSTEM.md`'s table this is the same class as REPAIR-0008/0009's
output-path ownership changes: `STRUCTURAL`, propose-only.

## Proposed or applied fix

Raise `TASK-280.max_attempts` from 3 to 4 via direct SQL
(`UPDATE tasks SET max_attempts=4 WHERE task_id='TASK-280'`), since no
sanctioned CLI verb exists for this, then re-export file/graph mirrors. This
grants exactly one additional attempt to close the three narrow findings
from the second re-review (harness interpreter for `role_registry_test`,
missing positive sanctioned-create regression, stale output count in
`role-contracts.md`) — no other task field, claim state, or output-path
ownership is touched.

## Authority check

- [ ] DRIFT or mechanical BLOCKING — core agent applied directly
- [ ] Judgment-requiring BLOCKING — proposed via hcom before applying
- [x] STRUCTURAL — explicit bigboss approval obtained before applying:
      requested via hcom with the exact fix and rationale, bigboss replied
      "go for it" in the active chat turn on 2026-07-27.

## Verification

- `scripts/validate_task_graph.py`: pass after mirror re-export.
- `scripts/validate_task_mirrors.py --db MAP_System/map.db --root MAP_System`: pass.
- `scripts/validate_task_schema.py`: pass.
- Confirmed via direct query that only `TASK-280.max_attempts` changed
  (3 -> 4); `attempt` (3), `status` (CHANGES_REQUESTED), and all other
  fields unchanged by this repair.

## Recurrence check

- [x] First occurrence of this drift class
- [ ] Repeat — logged in `shared/improvement-backlog.md`: NONE yet
- [ ] Repeat — permanent fix proposed (validator/template/decision): PENDING

## Notes

- No `map_task.py` verb exists to raise `max_attempts` on an existing task,
  matching the gap REPAIR-0009 already flagged for output-path removal: a
  third structural class (after output-path collisions and this
  attempt-budget ceiling) has now needed the same one-off sanctioned-SQL
  pattern. Worth a permanent `map_task.py extend-attempts` verb if this
  recurs a second time, per the same recurrence logic REPAIR-0009 applied.
- Rollback: lower `max_attempts` back to 3, or leave as-is once TASK-280
  reaches a terminal status (APPROVED/REJECTED/RELEASED) — the extra budget
  slot has no effect after that point.
