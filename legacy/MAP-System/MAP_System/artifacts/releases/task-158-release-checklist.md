# Release Checklist: TASK-158

## Header

```
task_id:      TASK-158
released_by:  mapfinish2-zemi
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Builds the liveness reaper: a seven-state classifier
(alive/working/blocked/idle/suspect/broken/standby), a reclaim path for
stale claims that exports and validates mirrors before returning success,
and a replayable dead-letter path with a documented replay command. Went
through two CHANGES_REQUESTED rounds (missing mirror export/validate on
reclaim; then a real defect where the fix's own fixture-backed test wrote
`TASK-FIXTURE` events into the *canonical* event log) before a clean
APPROVED.

## Evidence Per Check

- **Shared-file updates complete** — `shared/liveness-state.md` exists and
  was regenerated as recently as today (verified via file listing/mtime).
  `liveness_reaper.py` is actively imported by `mission_control_tui.py`
  (`from ...liveness_reaper import ...`, line 33, verified directly) and by
  `dead_letter_queue.py` — not a standalone, unused module.
- **Decisions recorded** — no standalone `DEC-NNN` required; the
  fixture-pollution defect found during review was handled through
  `repairs/REPAIR-0007-fixture-event-pollution.md` instead, which is the
  correct durable record for an already-written-history repair (confirmed
  by the second re-review's explicit "Repair Record Check" section). N/A
  for a new decision is correct here — the repair record *is* the durable
  record this check is asking about.
- **Follow-up tasks created** — not a new task, but a real durable
  build-on: `dead_letter_queue.py` and `mission_control_tui.py` both
  actively import from `liveness_reaper.py` today (verified directly), so
  this task's output is load-bearing infrastructure other shipped work
  depends on, not an isolated deliverable nobody built on.
- **Event log entry prepared** — `events/events.jsonl` carries the full
  6-event trail: PROGRESS, CHANGES_REQUESTED ×2, PROGRESS ×2, APPROVED
  (`codex-lab-mozu`, 2026-07-14T01:17:29Z), consistent with `map.db`'s
  pre-release `APPROVED` status.
- **Emergence capture considered** — Actively considered, not skipped: an
  emergence candidate (`emergence/candidates/CAND-E2DC97B8A022D8C6.json`)
  was auto-detected for this task's 2 rework cycles, reviewed by
  `claude-lab-nora` on 2026-07-27, and explicitly dismissed with reasoning
  ("2 changes-requested cycles, within normal review variance... no
  distinct reusable pattern beyond ordinary review back-and-forth") rather
  than silently ignored.

## Verification

- Independent reviews (2 rounds): `artifacts/reviews/task158-review-mozu.md`
  (CHANGES_REQUESTED), `task158-rereview-mozu.md` (CHANGES_REQUESTED — new
  finding, fixture events polluting canonical log),
  `task158-second-rereview-mozu.md` (APPROVED) — all 5 acceptance criteria
  PASS in the final pass, with a before/after canonical-event-count probe
  proving the fixture-pollution fix (`TASK-FIXTURE` count unchanged at 8
  across the test run).
- `python3 MAP_System/tests/test_liveness_reaper.py` — 18/18 PASS, re-run
  today.
- Re-verified today: all 3 declared output paths exist; `liveness_reaper.py`
  is genuinely imported by two other live modules.
- `python3 MAP_System/scripts/validate_task_mirrors.py` — pass.
