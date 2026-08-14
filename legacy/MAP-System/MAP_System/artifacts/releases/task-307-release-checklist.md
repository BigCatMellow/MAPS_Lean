# Release Checklist: TASK-307

## Header

```
task_id:      TASK-307
released_by:  claude-lab-sumi
release_date: 2026-08-10
```

## Checklist

- [x] Shared-file updates complete
  `db/claims.py`, `migration/schema.sql`, `scripts/context_rotation.py`,
  `scripts/map_authority.py`, `tests/test_context_rotation.py` all carry
  the reviewed patch.
- [x] Decisions recorded
  None new; implements the existing single-writer gateway design, doesn't
  change it.
- [x] Follow-up tasks created
  TASK-308 (deploy/live-verify) exists and is being released alongside this
  task in the same checklist batch.
- [x] Event log entry prepared
  This checklist's release event.
- [x] Emergence capture considered — mechanism: neither; evidence/reason: routine backlog release of already fully-reviewed work.

## Re-verification (2026-08-10, claude-lab-sumi)

Found and resolved a real discrepancy before releasing, not released on the
original approval alone: the deployment evidence artifact's own header said
"review not yet performed... nothing deployed," apparently contradicting
this task's `APPROVED` status. Checked `events.jsonl`'s full history rather
than trusting either the stale header or the bare status field — confirmed
two further rework rounds happened after that header was written (two real
security findings from `codex-lab-vumo`: unbound `rotation-restore` state,
then a non-atomic snapshot/lock ordering bug), each fixed, and a final
`APPROVED` recorded 2026-07-29T18:33:52Z. Updated the artifact's header with
a currency note pointing to this finding rather than silently leaving stale
text or silently rewriting history.

Independently confirmed the code itself is sound:
`MAP_System/tests/test_context_rotation.py` — 25/25 passing this session,
including the exact regression tests for both rework rounds
(`test_transfer_rotation_claims_locks_before_reading_snapshot_rows`,
`test_restore_rotation_claims_rejects_unknown_transfer_id_and_mutates_nothing`,
`test_rotation_restore_gateway_operation_rejects_the_old_row_json_shape`).

## Summary

Deployed the damo-nivo gateway patch (register-agent/rotation-transfer/
rotation-restore) to Smalls after 2 rounds of real security rework
(unbound restore state, non-atomic snapshot ordering) and final approval.
Found and fixed a stale status header in the deployment artifact that made
the approval look premature on a surface read; the underlying approval
history and current test suite both hold up under independent
re-verification. Ready to RELEASE.
