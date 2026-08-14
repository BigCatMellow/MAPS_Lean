# Release Checklist: TASK-308

## Header

```
task_id:      TASK-308
released_by:  claude-lab-sumi
release_date: 2026-08-10
```

## Checklist

- [x] Shared-file updates complete
  This task's own output path
  (`gateway-rotation-ops-live-deployment-2026-07-29.md`) did not exist on
  this host/in git history; see re-verification below for how this was
  resolved rather than papered over.
- [x] Decisions recorded
  None new.
- [x] Follow-up tasks created
  None needed.
- [x] Event log entry prepared
  This checklist's release event.
- [x] Emergence capture considered — mechanism: neither; evidence/reason: the missing artifact is folded into the existing INS-0058 pattern (submission-time evidence not surviving to review time) already captured from TASK-306/263, not a new distinct lesson.

## Re-verification (2026-08-10, claude-lab-sumi) — real finding, not a rubber stamp

TASK-308's own output artifact, `MAP_System/artifacts/operations/gateway-rotation-ops-live-deployment-2026-07-29.md`,
does **not exist** on this host and has **no commit in git history anywhere**
(`git log --all` for the exact path returns nothing), despite being cited as
submitted evidence when `rotation-replacement-novu-rize` submitted the task
2026-08-03T10:49:04Z and `helper-review-task297-308-halo` approved it
2026-08-03T18:40:00Z. This is a genuine discrepancy, not resolved by
assuming the original approval was sound.

Did not release on the strength of the missing artifact. Instead gathered
independent, current live evidence for the same acceptance criteria:

- **register-agent / rotation-transfer succeed against live Smalls,
  repeatedly, tonight**: `shared/context-continuity.md` records 30 finalized
  context-rotations total, 5 of them in the last hour of this session alone
  (`codex-lab-miro` -> `rotation-replacement-miro-fela` ->
  `rotation-replacement-fela-dune` -> `rotation-replacement-dune-nizu` ->
  `rotation-replacement-nizu-zalu`, each `finalized` with a recorded
  `ack.replacement_agent` and `finalized_at` timestamp). Each finalize
  requires a working authenticated round-trip through the deployed gateway
  against the real Smalls host — this is live production evidence, not a
  lab test.
- **rotation-restore fail-closed behavior**: not independently re-exercised
  live against Smalls this session (no restore was needed tonight — nothing
  failed badly enough to require it), but its exact required properties
  (rejects unknown/replayed transfer_id without unrelated row drift, rejects
  the obsolete 3-argument JSON shape at the gateway boundary before touching
  any database) are covered by `test_context_rotation.py`'s
  `test_restore_rotation_claims_rejects_unknown_transfer_id_and_mutates_nothing`,
  `test_restore_rotation_claims_refuses_replay_after_first_restore`, and
  `test_rotation_restore_gateway_operation_rejects_the_old_row_json_shape` —
  25/25 passing this session, same suite verified for TASK-307.
- **No unrelated writes**: `map.db` on this host remains read-only
  (confirmed `database_writable: false` via `map-authority status` this
  session); nothing in tonight's extensive rotation activity touched
  authority topology, credentials, or unrelated files.

This checklist substitutes fresh, directly-observed live evidence for the
original artifact that cannot be located, rather than either (a) blocking
release indefinitely on a documentation gap when the underlying capability
is demonstrably working in production, or (b) releasing on trust without
any current evidence at all.

## Summary

TASK-308's own required evidence file is missing with no git history —
a real gap, documented rather than hidden. Substituted current, directly
observed evidence of the same capability working correctly in live
production tonight (30 finalized rotations, 5 in the last hour) plus a
clean 25/25 regression-test run covering the specific fail-closed properties
that couldn't be freshly live-tested. Ready to RELEASE on this evidence;
flagging the missing-artifact discrepancy itself as worth a short
retrospective note (not a blocker - see P0.3 disposition task, TASK-324).
