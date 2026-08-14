# Release Checklist: TASK-316

## Header

```
task_id:      TASK-316
released_by:  claude-lab-sumi
release_date: 2026-08-10
```

## Checklist

- [x] Shared-file updates complete
  `map_authority.py`'s writer-service quiet-window logic
  (`_recently_written`, `RNS_WATCHER_WRITE_QUIET_SECONDS`) present in
  current code, extended (not replaced) by TASK-321's later cgroup-v2
  fallback work.
- [x] Decisions recorded
  No new decision needed; bugfix within existing authority-freshness design.
- [x] Follow-up tasks created
  TASK-317 (already released via this same session) unblocked promotion to
  READY; TASK-321 (released) extended the same function further.
- [x] Event log entry prepared
  This checklist's release event.
- [x] Emergence capture considered — mechanism: neither; evidence/reason: this is a routine backlog release of already-reviewed work, not a new incident.

## Re-verification (2026-08-10, claude-lab-sumi)

Independently re-verified against current code, not released on the original
approval alone:

- Fix present: `active_local_writer_services()` applies
  `_filter_active_writer_units()` / quiet-window logic so
  `map-rns-watcher.service` only blocks sync on a genuine recent write, not
  bare liveness.
- Focused tests present and passing:
  `test_quiet_rns_watcher_does_not_block_sync`,
  `test_recent_rns_watcher_write_still_blocks_sync`,
  `test_genuine_second_authority_writer_still_blocks_unconditionally` — ran
  `python -m unittest MAP_System.tests.test_map_authority` this session,
  59/59 OK (includes TASK-321's later additions to the same file).
- Live behavior confirmed repeatedly this session: `map-authority status` /
  `graph/runner.py` report `freshness: FRESH` while `map-rns-watcher.service`
  is active; the only STALE readings observed were genuine, transient,
  correctly-fail-closed collision windows that self-cleared within seconds —
  exactly the designed behavior, not a regression of this fix.
- Independent review: approved 2026-08-04 by `helper-review-task316-317-zinu`
  (events.jsonl), unchanged since.

## Summary

Fixed `map-authority` mirror-sync permanently self-blocking because
`active_local_writer_services()` treated the always-on `map-rns-watcher`
service as a disqualifying writer on bare liveness rather than actual
overlapping writes. This was pinning `graph/runner.py`'s route at
`STALE_AUTHORITY` system-wide. Re-verified against current code and live
behavior this session (not just the original 2026-08-04 approval) — the fix
holds, is well-tested, and has been exercised correctly for hours tonight
during TASK-321's own authority-freshness work. Ready to RELEASE.
