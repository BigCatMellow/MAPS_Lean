# Release Checklist: TASK-272

## Header

```
task_id:      TASK-272
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

Operator-authorized follow-up to TASK-271: makes every AI Command Center Lab
startup orientation validate the continuity ledger, run current-agent
context advice, and include checkpoint/rotation state in the single startup
status/resume-plan message, without changing the verified rotation protocol
itself.

**Checklist evidence:**

- **Shared-file updates complete:** `MAP_System/AGENTS.md`'s "Verified
  Context Rotation" section, read directly, includes the exact startup
  sequence this task added: "At every AI Command Center Lab startup,
  continuity checks happen before task routing... run `context_rotation.py
  validate`... `advise --agent <exact-current-hcom-identity>`... The agent
  includes the continuity validation result and the exact
  checkpoint/rotation recommendation in its single initial status/resume-
  plan message to `@bigboss`." This is live in the canonical file today.
- **Decisions recorded:** no DEC-NNN/DECISION_RECORDED event; not needed —
  this is a direct, narrow follow-up to TASK-271's already-decided rotation
  protocol, adding a startup checkpoint rather than a new project-direction
  call.
- **Follow-up tasks created:** none created directly by this task. Not
  needed: it is itself the closing follow-up to TASK-271, and its own
  acceptance criteria (startup validation, launcher templates, focused
  tests) are fully self-contained.
- **Event log entry prepared:** `events.jsonl` shows a clean single-pass
  lifecycle — creation (2026-07-22T20:34:34Z), `SUBMISSION`
  (20:38:34Z, `codex-lab-veto`), `APPROVED` (22:31:32Z, `claude-lab-gabi`),
  no rework needed. This release appends the canonical `RELEASED` event.
- **Emergence capture considered:** considered; no `emergence/` record
  names TASK-272 directly, and none is warranted — it is a narrow, already-
  reviewed extension of TASK-271 with no new systemic finding of its own.

## Verification

- All 5 output paths confirmed to exist, including
  `tests/test_startup_context_rotation.py`.
- `test_startup_context_rotation.py` passes as part of the full
  `run_tests.sh` run (73/79; unrelated pre-existing failures noted in
  TASK-268's checklist).
- Independent review: `APPROVED` by `claude-lab-gabi`, 2026-07-22T22:31:32Z,
  no rework cycle needed.
- The launcher template (`templates/install/bin/ai-command-center-lab-
  codex`, read directly) carries this exact startup-orientation language
  live today, confirming the mechanism ships, not just documents.
