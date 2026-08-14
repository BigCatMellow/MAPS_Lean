# Release Checklist: TASK-281

## Header

```
task_id:      TASK-281
released_by:  mapfinish2-dove
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Implements the approved TASK-277 bounded run-manifest experiment: at
dispatch, binds one immutable task revision to a run ID and records worker
and session identity, normalized role ID, selected skills, context
references with hashes, writable scope, and runtime limits — storing
references/hashes rather than copied context, after TASK-280's role IDs
exist.

**Checklist evidence:**

- **Shared-file updates complete:** `MAP_System/workflow/templates/
  run_manifest.json`, read directly, is a complete, current schema
  document (not a stub): it documents `run_id`, `task_id`, `task_revision`,
  `worker_id`, `role_id`/`role_source` (consuming TASK-280's normalized
  registry directly), `writable_scope`, `runtime_limits`, `context_refs`
  with hashes, and a worked example, explicitly noting the SQLite tables
  are canonical and this file is documentation only.
- **Decisions recorded:** this task's `decision_class` is `ARCHITECTURE`,
  but no standalone `DEC-NNN`/`DECISION_RECORDED` event names it. Not
  treated as a gap: it is a direct, bounded-pilot implementation of the
  already-approved TASK-277 slice, explicitly sequenced after TASK-280
  (role IDs) released — the "store hashes, not copied content" design
  choice is recorded in the schema document itself, matching the pattern
  already used for TASK-279 and precedented by TASK-269's release (a
  decision-class task released on the durable artifact's own record,
  without a separate ledger line).
- **Follow-up tasks created:** none created directly. Not needed: this is
  explicitly a bounded pilot per its own acceptance criteria; TASK-282
  (structured submission claims) consumes its `run_id`/`task_revision`
  fields as a dependency, not as a task this release spawned.
- **Event log entry prepared:** clean single-pass lifecycle in
  `events.jsonl` — creation (2026-07-26T17:35:47Z), `SUBMISSION`
  (2026-07-27T13:54:02Z), one disclosed review-conflict note
  (`codex-lab-diro` ack'd but could not claim due to a mandatory context-
  rotation boundary), then `APPROVED` (17:22:48Z) by a freshly spawned
  helper reviewer (`helper-review-task-281-tuna`) per the Routine Reviewer
  Conflict Routing convention in `AGENTS.md`. This release appends the
  canonical `RELEASED` event.
- **Emergence capture considered:** considered; no `emergence/` record
  names TASK-281 directly, and none is warranted — a cleanly approved,
  explicitly-scoped pilot with no rework and no new systemic finding beyond
  what its own review covered.

## Verification

- All 5 output paths confirmed to exist.
- `test_run_manifest.py` passes as part of the full `run_tests.sh` run
  (73/79; unrelated pre-existing failures noted in TASK-268's checklist).
- Independent review: `APPROVED` by helper reviewer
  `helper-review-task-281-tuna`, 2026-07-27T17:22:48Z, spawned per the
  documented conflict-routing convention after the primary candidate
  reviewer was unavailable — routing is disclosed in the event log, not
  silent.
- Dependency on TASK-280 (role IDs) is satisfied: TASK-280 released earlier
  in this same batch.
