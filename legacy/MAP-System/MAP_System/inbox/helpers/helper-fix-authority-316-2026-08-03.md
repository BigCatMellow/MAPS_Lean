# Helper Assignment - Fix TASK-316 map-authority mirror-sync writer-service scope bug

- status: complete
- owner: coordinator-replacement-rose
- provider: claude
- model: sonnet
- created_at: 2026-08-03
- scope: Fix map_authority.py's active_local_writer_services() so it stops
  treating map-rns-watcher.service as a disqualifying local writer, without
  weakening the real dual-writer-authority protection.

## Context

`map-authority-mirror.service` (Biggie, systemd --user) failed roughly every
60s from 2026-08-03T14:21 onward with "local writer services must be disabled
before mirror sync: map-rns-watcher.service", pinning
`graph/runner.py`'s route at STALE_AUTHORITY / review-only system-wide.
`map-rns-watcher.service` is the always-on RnS/limit-watcher
(Restart=always, WantedBy=default.target) and is legitimately supposed to run
continuously. It only ever writes `MAP_System/agents/limit-watcher-state.json`,
never `map.db` -- this looks like an overly broad writer-service scope bug in
`active_local_writer_services()` (added by TASK-310), not a real dual-writer
hazard.

A stopgap has already been applied (map-rns-watcher.service stopped on
Biggie with bigboss's approval, same known-good pattern used once before on
2026-08-02 / TASK-315): mirror freshness is FRESH again and the route is
unblocked as of this note. TASK-316 is still open because the stopgap loses
context-rotation monitoring while the watcher is down -- the permanent fix
is to correct the check so mirror sync succeeds with the watcher running.

## Task record

`MAP_System/.venv/bin/python MAP_System/scripts/map_authority.py task show TASK-316`
has the full acceptance criteria (5 items). Summary: confirm
`limit_watcher.py`'s actual write targets, narrow the writer-service check to
stop flagging `map-rns-watcher.service` specifically, preserve the check's
original intent (still block a genuine second lifecycle-writing authority),
add a focused test, and get independent core-agent review before release
since this touches TASK-310's AUTHORITY-classified, trust-boundary-crossing
contract code (do not self-review).

## Known wrinkle

TASK-316 landed `status=NEEDS_SHAPING` (empty description field) even though
its acceptance criteria are fully specified. No gateway-allowlisted
`map_task.py` verb currently promotes NEEDS_SHAPING -> READY remotely from
Biggie (mirror) to Smalls (authority) -- `ALLOWED_TASK_VERBS` in
`map_authority.py` has no such verb, and `promote_task.py` writes directly to
`map.db`, which is not writable from Biggie. This is the same shape as the
missing `recover-orphan` path luzo hit on TASK-296. You'll need to find the
correct sanctioned way to get this task claimable (e.g. determine whether
promotion is expected to run on the authority host, or whether this is
itself a small follow-up worth naming) rather than working around the
mirror's read-only boundary directly.

## Boundary

Coordinator (coordinator-replacement-rose) is dispatching this per direct
operator instruction and is not implementing it -- do not wait on the
coordinator for engineering judgment calls within TASK-316's acceptance
criteria; use your own judgment and escalate only a genuine
ownership/irreversible/novel call.
