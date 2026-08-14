# Helper Assignment - Independent review of TASK-316 and TASK-317 diffs

- status: complete
- owner: coordinator-replacement-rose
- provider: claude
- model: sonnet
- created_at: 2026-08-03
- scope: Independently review two unreviewed, uncommitted local diffs on
  Biggie implemented by helper-fix-authority-316-bume. Neither has been
  self-reviewed or claimed in SQLite. Do not implement, only review.

## Why an independent reviewer, not the implementer

`helper-fix-authority-316-bume` implemented both changes and explicitly
flagged it should not self-review: TASK-316 touches TASK-310's
AUTHORITY-classified, trust-boundary-crossing contract code
(`map_authority.py`'s writer-service/mirror-sync logic), and its own
acceptance criteria require independent review before release.

Full context: `MAP_System/handoffs/HANDOFF-TASK-316-TASK-317-bume-blocked-on-deploy.md`
(read this first, it has root cause, fix rationale, and verification detail).

## What to review

**TASK-316** (`MAP_System/scripts/map_authority.py`,
`MAP_System/tests/test_map_authority.py`): `active_local_writer_services()`
now only flags `map-rns-watcher.service` as a disqualifying writer if its one
mirrored write target (`events/events.jsonl`) was modified within a 15s quiet
window, instead of on bare process-liveness. Any other writer service is
still blocked unconditionally on liveness alone. Check:
- Does this actually preserve TASK-310's original protection intent (see
  `MAP_System/artifacts/recovery/ws1-truthful-authority-state.md` lines
  364-367), or does it quietly weaken it?
- Fails closed on stat errors / missing file? Verify the test actually proves
  this, don't just take the summary's word for it.
- Race window: is 15s defensible, or could a slow/delayed write outside that
  window still collide with a sync that already passed the check?
- Any other writer service still blocks on liveness alone, unchanged from the
  original code? Confirm no unintended widening there.

**TASK-317** (`MAP_System/db/claims.py`, `MAP_System/scripts/map_task.py`,
`MAP_System/scripts/map_authority.py`'s `ALLOWED_TASK_VERBS`,
`MAP_System/tests/test_map_task_describe.py`): new `describe` verb sets a
`NEEDS_SHAPING` task's description and promotes to `READY` in the same
transaction if the existing create-time gate (non-empty description, >=1
output path, >=1 criterion) now passes. Check:
- Can this be misused to promote a task that shouldn't be claimable yet
  (e.g. does it bypass any review/authority check `create_task` itself
  relies on)?
- Refuses on every non-NEEDS_SHAPING status, as claimed?
- This is a new ALLOWED_TASK_VERBS entry on AUTHORITY-classified gateway
  code (`map_authority.py`) -- same trust-boundary review bar as TASK-316.

## Deployment question -- do not decide, just note in your review

TASK-317 is implemented locally on Biggie only (uncommitted); Smalls' own
installed copy doesn't have it yet, so the sanctioned gateway can't use it to
promote TASK-316 remotely today. That's a separate open question (how it
reaches Smalls -- normal review->commit->deploy cycle, likely following the
TASK-308 pattern) that the coordinator will route once your review lands. No
urgency: the mirror is currently FRESH via an existing stopgap
(map-rns-watcher.service stopped), so nothing is blocked in the meantime.

## Output

Post your verdict (findings, BLOCKER/REQUIRED/RECOMMENDED/OPTIONAL per
`MAP_System/AGENTS.md` Review Standard) back to
`helper-fix-authority-316-bume` and `coordinator-replacement-rose` via hcom
when done. Do not approve/claim/submit anything yourself -- review only.
