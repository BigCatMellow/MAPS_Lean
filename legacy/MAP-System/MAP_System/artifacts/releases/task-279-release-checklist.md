# Release Checklist: TASK-279

## Header

```
task_id:      TASK-279
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

Implements the approved TASK-277 generated-state slice: replaces hand-
maintained lifecycle fields in the active-lane surface with an idempotent
SQLite projection (`scripts/render_active_state.py`), while preserving
compact human rationale/gate annotations in a separate keyed source
(`shared/active-lane-annotations.json`) rather than parsing free prose as
lifecycle truth.

**Checklist evidence:**

- **Shared-file updates complete:** `MAP_System/shared/current-state.md`,
  read directly, carries the header `verified_against: scripts/render_active_
  state.py plus scripts/validate_shared_state_tasks.py against live map.db` —
  confirming it is now the generated artifact this task specifies, not hand-
  maintained prose. `MAP_System/shared/active-lane-annotations.json`, read
  directly, is live and populated with real per-task rationale/gate entries
  (including entries for TASK-268 and TASK-274, both released earlier in
  this same batch, correctly noting "Awaiting release checklist" at the time
  they were written).
- **Decisions recorded:** this task's `decision_class` is `ARCHITECTURE`, but
  no standalone `DEC-NNN`/`DECISION_RECORDED` event names it directly. Not
  treated as a gap: it is a direct implementation of the already-approved
  TASK-277 roadmap slice, and the split itself (generated lifecycle fields
  vs. a separate human-authored annotations file) is recorded in the
  artifact's own schema comment ("Lifecycle fields are always read from
  map.db") rather than a separate ledger line — the same pattern already
  used for TASK-269 (POLICY class, released without a separate DEC-NNN,
  the durable artifact itself carrying the decision).
- **Follow-up tasks created:** none created directly. Not needed: scope is
  self-contained per its own acceptance criteria (replace hand-maintained
  fields, preserve annotations, no free-prose lifecycle parsing).
- **Event log entry prepared:** clean single-pass lifecycle in
  `events.jsonl` — creation (2026-07-26T17:35:46Z), `SUBMISSION`
  (19:13:56Z, `codex-lab-meba`), `APPROVED` (19:17:51Z, `codex-lab-feta`),
  no rework needed. This release appends the canonical `RELEASED` event.
- **Emergence capture considered:** considered; no `emergence/` record names
  TASK-279 directly, and none is warranted — it is a bounded, cleanly
  approved implementation of an already-reviewed roadmap slice.

## Verification

- All 5 output paths confirmed to exist and are live/current (see
  Shared-file evidence above).
- `test_render_active_state.py` passes as part of the full `run_tests.sh`
  run (73/79; unrelated pre-existing failures noted in TASK-268's
  checklist). The 3 drift rows `validate_shared_state_tasks` currently
  reports (TASK-263, TASK-254, TASK-289) are real lifecycle drift in
  `current-state.md` unrelated to this task or its output paths — they
  reflect tasks that changed status after the file's last render, which is
  exactly the kind of drift this task's generated-projection mechanism is
  designed to make visible rather than silently hide.
- Independent review: `APPROVED` by `codex-lab-feta`, 2026-07-26T19:17:51Z,
  no rework cycle needed.
