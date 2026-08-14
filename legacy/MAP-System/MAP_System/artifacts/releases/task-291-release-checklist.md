# Release Checklist: TASK-291

## Header

```
task_id:      TASK-291
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

Docs-only fix closing a cadence gap: `shared/current-state.md`'s generated
active-lane table drifted from canonical `map.db` for 6 days (TASK-263/265/
274/276 rows all wrong) because nothing ran the existing
`validate_shared_state_tasks.py` check at agent startup. Extends the same
treatment `AGENTS.md` Core Protocol rule 11 already gives the emergence
sentinel to shared-state drift, as a new rule 12. Explicitly does not
introduce silent auto-regeneration of `current-state.md` during another
agent's startup.

**Checklist evidence:**

- **Shared-file updates complete:** `MAP_System/AGENTS.md`, read directly,
  carries rule 12 today: "When you orient off `shared/current-state.md`...
  also run `scripts/validate_shared_state_tasks.py`... If it reports drift,
  regenerate the file... and fix any stale entries..." —
  matching the task's acceptance criteria verbatim, including the explicit
  no-silent-rewrite guard citing the SYN-0001 pattern.
  `MAP_System/notes/command-center-lab-restart-startup.md`, read directly,
  independently states the same command and the same no-silent-rewrite
  reasoning (not just a cross-reference to AGENTS.md).
- **Decisions recorded:** no `decision_class` is set on this task and no
  DEC-NNN/DECISION_RECORDED event exists. Not needed: this is a bounded
  extension of an already-established pattern (rule 11's emergence-sentinel
  cadence, extended by analogy), not a new project-direction call.
- **Follow-up tasks created:** none created directly. Not needed: scope is
  self-contained (one new Core Protocol rule plus matching startup-note
  language in two files).
- **Event log entry prepared:** clean single-pass lifecycle in
  `events.jsonl` — creation (2026-07-28T12:27:09Z, `claude-lab-lili`),
  `SUBMISSION` (12:34:22Z, `mapfinish-rafa`), `APPROVED` (17:00:37Z,
  `mapreview-kuma`), no rework needed. This release appends the canonical
  `RELEASED` event.
- **Emergence capture considered:** considered; no `emergence/` record
  names TASK-291 directly, and none is warranted — the drift this task
  fixes was itself surfaced by an existing, correctly-working validator
  (`validate_shared_state_tasks.py`), not a new systemic finding requiring
  a fresh capture.

## Verification

- Both output paths confirmed to exist and to carry the exact described
  content (read directly, not taken from the submission report).
- Independent review: `artifacts/reviews/task-291-independent-review-
  mapreview-kuma.md` — APPROVED, all 3 acceptance criteria individually
  verified with cited evidence, reviewer confirmed independent of task
  owner (`mapreview-kuma` != `mapfinish-rafa`).
- No test suite applies (docs-only change, no code output paths).
