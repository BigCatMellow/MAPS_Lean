# Release Checklist: TASK-223

## Header

```
task_id:      TASK-223
released_by:  mapfinish-guru
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Operational-learning promotion loop (IDEA-0022/PROMO-0011): converts
incident-derived notes into scope-matched active startup guidance. Touches
`templates/install/bin/...` so classifies `full` tier under
`classify_release()` regardless of risk fields.

**Deliverable verified today** (independent check, not copied from the
2026-07-28 backlog triage table):

- All 7 output paths exist on disk (checked directly).
- `MAP_System/notes/command-center-lab-restart-startup.md:76-77` documents
  the live startup-orientation command:
  `python3 MAP_System/scripts/operational_lessons.py orientation --scope
  startup --scope helper-routing --scope review-routing --pretty` — this is
  acceptance criterion 3 (startup orientation surfaces scope-matched active
  lessons), confirmed wired into the actual restart runbook agents read, not
  just implemented in isolation.
- `grep -c operational_lessons MAP_System/scripts/map_steward.py` → 1: the
  later TASK-225 steward consumes this task's output, confirming it's a real
  dependency chain, not a dead-end module.
- `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_operational_lessons -v`:
  **5/5 pass** — covers live-store validation/fallback routing, missing-
  source/conflict rejection, overdue review-due marking, and retired/
  superseded lesson exclusion from projection (the lifecycle/expiry/
  supersession acceptance criterion).

**Shared-file updates complete**: `MAP_System/notes/operational-learning-guide.md`
documents migration/usage as required by acceptance criterion 5; no MAP
canonical doc (`AGENTS.md`, `decisions.md`) required a change for this task's
own scope.

**Decisions recorded**: none required — this is a bounded implementation of
an already-approved idea/promotion (IDEA-0022/PROMO-0011), not a new
authority or policy question; no `REQUIRE_*` pre-dispatch gate applies
(`decision_class=null`, `requires_operator_approval=false` on the task
record, unchallenged since creation).

**Follow-up tasks created**: `task_dependencies` confirms TASK-224 and
TASK-225 both depend on TASK-223 and were created as its direct
continuations; TASK-225 (this batch) is the visible steward assistant built
on top of this task's lesson store.

**Event log entry prepared**: appended automatically by `map_task.py
release`.

**Emergence capture considered**: considered, none warranted — this task
itself *is* the emergence-to-guidance promotion mechanism (E/I → active
lesson), not a new pattern needing separate capture.
