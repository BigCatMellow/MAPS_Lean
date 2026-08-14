# Repair Record

Repair ID: REPAIR-0008
Related task: TASK-268
Found by: codex-lab-zori
Date: 2026-07-26
Severity: STRUCTURAL
Status: APPLIED

## What was found

TASK-268 could not register its required map_task.py implementation output because READY successor TASK-278 prematurely registered the same path, causing validate_task_graph.py to fail.

## Surfaced by

MAP_System/scripts/validate_task_graph.py after sanctioned TASK-268 add-output-path

## Severity rationale

Changing approved task output ownership is STRUCTURAL. The repair is narrow and reversible but changes durable task scope, so it required command-center approval.

## Proposed or applied fix

With direct bigboss approval, removed
`MAP_System/scripts/map_task.py` from TASK-278 `output_paths` while TASK-278
was READY and unclaimed. Updated TASK-278's description to require sanctioned
re-registration only after predecessor ownership clears, appended durable
SQLite/JSONL event `events.id=1699` (`trace_id=task:TASK-278`), and exported
the task and graph mirrors.

## Authority check

STRUCTURAL repair approved directly by bigboss in the active hcom/user turn on 2026-07-26; coordinator codex-lab-kazu acknowledged proceed within exact scope in hcom #15784.

## Verification

- `validate_task_schema.py --tasks-dir MAP_System/tasks`: PASS.
- `validate_task_mirrors.py --db MAP_System/map.db --root MAP_System`: PASS.
- `validate_task_graph.py`: PASS; the TASK-268/TASK-278 collision is gone.
- `tests/test_exporter_invariants.py`: PASS, 2/2.
- `validate_repair_artifacts.py`: PASS.
- `tests/test_task268_lifecycle.py`: PASS, 3/3.
- Full `scripts/run_tests.sh`: 73 pass / 4 fail. Three failures are the
  disclosed pre-existing research/event baseline (`validate_research_artifacts`,
  `validate_events_no_new_warnings`, and derivative `validate_layer1_test`).
  The fourth is the expected transient active-lane snapshot drift:
  `current-state.md` still says TASK-268 READY while the canonical claim is
  IN_PROGRESS. That file is reserved by READY TASK-279 and was not silently
  modified as part of this repair.

## Recurrence check

First recorded structural output-registration sequencing repair; related missing unregister-verb class already captured by INS-0042.

## Notes

Rollback: re-register MAP_System/scripts/map_task.py on TASK-278 through map_task.py add-output-path only after predecessor ownership clears.
