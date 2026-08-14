# Release Checklist: TASK-289

## Header

```
task_id:      TASK-289
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

Reconciles `ORCHESTRATION_ENTRYPOINT_SYSTEM.md`'s stale `task_tier`
documentation (a TASK-288-review-found drift, `decision_class=POLICY`,
`risk_class=KNOWLEDGE`) with the live enum. Touches
`MAP_System/ORCHESTRATION_ENTRYPOINT_SYSTEM.md` directly, classifies `full`
tier.

**Deliverable verified today** (independent re-check, not copied from the
task record's own claims):

- `ORCHESTRATION_ENTRYPOINT_SYSTEM.md:70,77-105` takes acceptance criterion
  1's second path: rather than rewriting the dispatch-packet table's
  `task_tier` row to match `tasks.task_tier`, it explicitly documents the two
  as different fields sharing a name, with a "`task_tier` naming collision
  (TASK-289)" section and an inline note on the table row itself.
- Re-ran all three cited verifications myself: `grep task_tier
  MAP_System/scripts/pre_dispatch_policy.py` shows `== "architecture"`,
  `in {"mechanical", "bounded", ""}`, `== "operator"`; `grep task-tier
  MAP_System/scripts/map_task.py` shows the `--task-tier` choices list is
  exactly `mechanical, bounded, architecture, policy, operator`; `sqlite3
  map.db "SELECT DISTINCT task_tier FROM tasks"` returns `bounded,
  architecture, policy` (plus NULL) -- a subset of the same five, matching
  the doc's claim exactly.
- Also independently checked the doc's claim about the *other* field:
  `grep task_tier MAP_System/scripts/intake_request.py` shows only literal
  `"core"` and `"shaping"` values assigned anywhere in `classify()` --
  `local`/`helper`/`approval` do not appear, confirming the doc's claim that
  those three are an unimplemented sketch, not live values.

**Shared-file updates complete**: the task's sole output *is* the shared
canonical-doc update; no other shared file needed a change for this
narrowly-scoped drift fix.

**Decisions recorded**: none required beyond the doc's own explicit
recommendation (rename the dispatch-packet field to `dispatch_tier` next time
`intake_request.py` changes) -- a documented recommendation for a future
task, not a new authority question needing a `DEC-` entry now.

**Follow-up tasks created**: none needed now -- the rename recommendation is
explicitly deferred to "the next time `intake_request.py` changes," not an
immediate action this release must spawn; `task_dependencies` confirms
nothing currently depends on TASK-289.

**Event log entry prepared**: appended automatically by `map_task.py
release`.

**Emergence capture considered**: considered, none warranted -- a single
resolved documentation-drift finding from TASK-288's review, already fully
captured in the doc's own "naming collision" section; no separate emergence
entry needed.
