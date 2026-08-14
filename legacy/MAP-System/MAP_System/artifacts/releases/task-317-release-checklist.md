# Release Checklist: TASK-317

## Header

```
task_id:      TASK-317
released_by:  claude-lab-sumi
release_date: 2026-08-10
```

## Checklist

- [x] Shared-file updates complete
  `describe` verb present in `map_task.py`, `ALLOWED_TASK_VERBS` in
  `map_authority.py`, `describe_task()` in `db/claims.py`.
- [x] Decisions recorded
  None needed; additive lifecycle verb within existing gateway allowlist
  pattern.
- [x] Follow-up tasks created
  None needed; this verb is now in routine use (used directly by this
  session while writing TASK-322/325's tasks).
- [x] Event log entry prepared
  This checklist's release event.
- [x] Emergence capture considered — mechanism: neither; evidence/reason: routine backlog release, not a new incident.

## Re-verification (2026-08-10, claude-lab-sumi)

Independently re-verified against current code, not released on the original
approval alone:

- `map-authority task describe --help` confirms the verb is live and
  remotely callable through the gateway from this mirror host (criterion 2).
- Ran `MAP_System/tests/test_map_task_describe.py` directly this session:
  10/10 tests pass, covering the happy-path promotion, every refusal case
  (wrong status, missing output_paths/criteria/description/reason/actor),
  and the CLI wrapper's exit codes.
- Criterion "TASK-316 itself is promoted to READY using the new verb" —
  confirmed via events.jsonl: "TASK-316 described by
  helper-fix-authority-316-bume ... Promoted to READY", 2026-08-04.
- Independent review: approved 2026-08-04 by `helper-review-task316-317-zinu`
  (same review as TASK-316), unchanged since.

## Summary

Added the sanctioned `describe` lifecycle verb so a task shaped incrementally
(output_paths/criteria filled in, description left blank) has a route back
to READY instead of being permanently stuck in NEEDS_SHAPING. Used
successfully in production, including by this very session. Re-verified
against current code and a full passing test run, not just the original
approval. Ready to RELEASE.
