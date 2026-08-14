# Repair Record

Repair ID: REPAIR-0009
Related task: TASK-280
Found by: claude-lab-nora
Date: 2026-07-27
Severity: STRUCTURAL
Status: APPLIED

## What was found

TASK-280 registered MAP_System/scripts/map_task.py and MAP_System/scripts/pre_dispatch_policy.py as output paths after TASK-278 and TASK-283 (respectively) already owned them, breaking validate_task_graph.py and blocking the entire roles-roadmap READY queue.

## Surfaced by

validate_task_graph.py output-path collision; confirmed by direct SQL query against task_output_paths

## Severity rationale

Changing approved/registered task output ownership is STRUCTURAL per SELF_REPAIR_SYSTEM.md; narrow, reversible, but changes durable task scope.

## Proposed or applied fix

Remove the two colliding rows from TASK-280's output_paths (task_output_paths table), append a durable PROGRESS event per path referencing this repair, and resync file mirrors. TASK-278 and TASK-283 keep their prior registrations unchanged. TASK-280 may re-register both paths after its predecessors reach a terminal state, same rollback pattern as REPAIR-0008.

## Authority check

Direct bigboss approval in active chat turn on 2026-07-27 ("Im good with all three"), covering: this repair, TASK-263 orphan recovery, and claude-lab-nora taking TASK-278.

## Verification

- `scripts/validate_task_graph.py`: PASS ("Task graph validation passed."); the TASK-278/TASK-280 and TASK-283/TASK-280 collisions are gone. TASK-280's remaining output_paths are `artifacts/tests/task280-role-registry-delivery-note.md`, `graph/runner.py`, `notes/role-contracts.md`, `scripts/run_tests.sh`, `scripts/validate_task_schema.py`, `tests/test_role_registry.py`, `workflow/role_registry.yaml`.
- `scripts/validate_task_mirrors.py --db MAP_System/map.db --root MAP_System`: PASS.
- `tests/test_exporter_invariants.py` (run directly, no pytest in venv): PASS, 2/2 (`test_task_statuses_match_sqlite_in_task_files_and_graph`, `test_agent_status_export_is_filtered_operational_view`).
- Full `scripts/run_tests.sh` not re-run this pass (venv lacks pytest for some suites); the three targeted validators above are the ones this repair could affect and all pass.

## Recurrence check

Second occurrence of the output-path write-once collision class first recorded in REPAIR-0008 (TASK-268/TASK-278) and originally observed in INS-0042. No remove-output-path verb exists yet; this is the second manual one-off repair of the same shape. Flagging for a permanent fix (a sanctioned defer/remove verb) rather than a third silent repeat.

## Notes

Rollback: re-register both paths on TASK-280 via map_task.py add-output-path only after TASK-278 and TASK-283 both reach a terminal status.
