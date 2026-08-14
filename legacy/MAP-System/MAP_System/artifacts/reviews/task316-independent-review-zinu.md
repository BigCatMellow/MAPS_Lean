# TASK-316 Independent Review

task_id: TASK-316
reviewer: helper-review-task316-317-zinu
task_owner: helper-fix-authority-316-bume
review_date: 2026-08-03

Full technical review detail lives in the paired record,
`task316-317-independent-review-zinu.md` (covers both TASK-316 and
TASK-317, since both diffs landed in the same uncommitted files and were
reviewed together). This file exists only because the review-record
validator requires an exact `task_id` match per approved task; the
substantive review is not duplicated here, only summarized.

## Verdict

APPROVED. No BLOCKER or unresolved REQUIRED findings remain.

Initial pass found one REQUIRED finding: a TOCTOU race in
`active_local_writer_services()`'s writer-service quiet-check --
`install_snapshot()` probed liveness before acquiring `DEFAULT_LOCK` and
before the real `events.jsonl` replace, so a watcher write could land in
that gap and be silently clobbered. Implementer (bume) fixed it by adding a
second, narrower re-check immediately before that file's `os.replace()`,
inside the lock, aborting via the existing tested rollback path if a write
landed since the first probe. New test:
`test_install_aborts_when_watcher_writes_between_probe_and_replace`.
Follow-up pass confirmed the fix's placement and the race-simulation test's
validity; approved with one OPTIONAL note explicitly waived as unnecessary
(see paired record for detail).

Verification re-run independently, not just trusted from the handoff:
41/41 `test_map_authority.py` (36 pre-existing + 5 writer-service + 1 race
test), `_recently_written()`'s fail-closed/missing-file cases read and
exercised directly, `install_snapshot()`'s lock/staging/replace order traced
by hand against the original TOCTOU concern.

## Acceptance Criteria Check

TASK-316 acceptance criteria, from `map-authority task show TASK-316`:

| # | Result | Evidence |
|---|---|---|
| `active_local_writer_services()` no longer treats `map-rns-watcher.service` as a disqualifying writer on bare liveness; confirm `limit_watcher.py`'s actual write targets before changing the check | PASS | Read `limit_watcher.py`'s `append_event()` directly (not assumed): it only writes `events/events.jsonl`, one of `map_authority.py`'s `MIRROR_FILES`, never `map.db`. Check narrowed to `_recently_written()` on that one overlapping target, 15s quiet window (`RNS_WATCHER_WRITE_QUIET_SECONDS`). Any other writer service still blocks unconditionally on liveness alone, unchanged. |
| Root cause documented: `map-rns-watcher.service` restarted 2026-08-03T14:20:42-04:00, breaking `map-authority-mirror.service`, pinning `graph/runner.py` at STALE_AUTHORITY | PASS | Documented in `HANDOFF-TASK-316-TASK-317-bume-blocked-on-deploy.md` and this review's paired record, with the exact `journalctl`/`systemctl` evidence. |
| Fix preserves TASK-310's original protection intent (no second lifecycle-writing authority on the mirror) | PASS | Checked against `MAP_System/artifacts/recovery/ws1-truthful-authority-state.md` lines 364-367 (TASK-310's original design). Any writer service other than the specifically-scoped `map-rns-watcher.service` exception still blocks unconditionally. TOCTOU follow-up (below) closes the one gap this review itself found. |
| After the fix, mirror sync succeeds while the watcher is active; freshness reports OK, not INVALID | PASS | Live-reverified on Biggie: watcher started, `map-authority-mirror.service` triggered manually -- first attempt correctly still failed (watcher's startup poll wrote within the 15s window, proving the check still catches genuine recent writes); after quiet, retried: `ok: true`, `freshness: FRESH`, `topology_valid: true`, watcher still active. Two further naturally-timer-triggered cycles also succeeded. |
| Focused test added; writer-list still blocks a genuine second-authority writer; independent review before release | PASS | `WriterServiceTests` (5 tests) plus `test_install_aborts_when_watcher_writes_between_probe_and_replace` (the TOCTOU-fix test), all in `test_map_authority.py`. 41/41 total pass. This review. |

## Files Reviewed

- `MAP_System/scripts/map_authority.py` (diff: `active_local_writer_services()`, new `_recently_written()`, new constants, `install_snapshot()`'s in-lock re-check)
- `MAP_System/tests/test_map_authority.py` (diff: new `WriterServiceTests` class, the TOCTOU race-simulation test)
- `MAP_System/scripts/limit_watcher.py` (`append_event()`, read directly to independently verify the write-target claim rather than trusting the handoff)
- `MAP_System/artifacts/recovery/ws1-truthful-authority-state.md` (lines 340-381, TASK-310's original writer-service protection intent)
- `MAP_System/handoffs/HANDOFF-TASK-316-TASK-317-bume-blocked-on-deploy.md` (root cause, fix rationale, and both review passes' detail)
- Ran `map-authority task show TASK-316` directly to cross-check declared `output_paths`/`acceptance_criteria` against the actual diff

## Forbidden Changes Check

PASS. This review added only its own artifact files (this record and its paired
`task316-317-independent-review-zinu.md`); no task, database, event, or
implementation file was modified while reviewing. `limit_watcher.py` was read
for verification only, not edited, per the coordinator's explicit direction to
keep it out of scope for this fix.

## Deployment note (2026-08-04)

TASK-316's approval was deliberately held pending TASK-317's `describe`
verb reaching Smalls (the authority host), since the sanctioned gateway
path executes Smalls' own installed copy of `map_task.py`, which lacked the
verb until then. That deployment (backup, stage, checksum-verify, compile,
test, atomic activate) is now complete and independently checksum-confirmed
against Biggie's reviewed hashes; see
`task316-317-describe-verb-smalls-deployment-plan-2026-08-03.md` for the
executed plan.
