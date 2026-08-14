# Release Checklist: TASK-295

## Header

```
task_id:      TASK-295
released_by:  helper-releases-batch1-mive
release_date: 2026-08-10
```

## Checklist

- [x] Shared-file updates complete
  `db/claims.py`, `scripts/map_task.py`, `scripts/run_tests.sh`,
  `tests/test_map_task_retire.py` all carry the reviewed patch adding the
  sanctioned `retire` verb. Delivery note at
  `artifacts/tests/task295-retire-verb-delivery-note.md`. All 5 cited
  output-path artifacts confirmed present on disk.
- [x] Decisions recorded
  None new; implements the retire verb per the existing missing-lifecycle-verb
  pattern, no policy change.
- [x] Follow-up tasks created
  None required; this closes the "retire" instance of the pattern (TASK-293
  already closed the attempt-budget instance).
- [x] Event log entry prepared
  This checklist's release event.
- [x] Emergence capture considered — mechanism: neither; evidence/reason: routine backlog release of already fully-reviewed work.

## Re-verification (2026-08-10, helper-releases-batch1-mive)

History shows a real rework cycle, not a rubber stamp:
SUBMISSION (mapfinish-guru) → CHANGES_REQUESTED (claude-lab-mimi: missing
output-path registration for `db/claims.py`) → reworked, path registered →
re-submitted (codex-lab-vumo) → APPROVED (claude-lab-mimi). Independently
ran `MAP_System.tests.test_map_task_retire` this session via the project
venv (`MAP_System/.venv/bin/python3 -m unittest`) — passes as part of the
combined 59-test run alongside TASK-299/300's suites.

## Summary

Adds the sanctioned `retire` verb to `map_task.py`, closing the
missing-lifecycle-verb pattern for retirement. One real CHANGES_REQUESTED
round over a missing output-path registration, fixed and re-approved. All
cited artifacts exist and the test suite passes. Ready to RELEASE.
