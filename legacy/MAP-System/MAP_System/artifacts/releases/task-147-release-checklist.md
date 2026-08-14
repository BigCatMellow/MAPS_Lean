# Release Checklist: TASK-147

## Header

```
task_id:      TASK-147
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

Defines MAP's single operator-intent entrypoint (`scripts/intake_request.py`)
and the decomposer contract (`map-decomposer-spec.md`): subtasks, dependency
edges, output paths, acceptance criteria, risk class, approval gates, routing
lane, rollback expectation. First submission was CHANGES_REQUESTED for an
incomplete `subsystem-apis.md` table (missing Allocator/Validators/Status
rows); fixed same-day and re-approved.

## Evidence Per Check

- **Shared-file updates complete** — `shared/subsystem-apis.md` exists and
  (per the second review, re-verified today) contains all 8 required
  category rows including the 3 that were the CHANGES_REQUESTED finding.
  `ORCHESTRATION_ENTRYPOINT_SYSTEM.md` is still actively maintained —
  it carries an uncommitted addition dated "Confirmed 2026-07-28
  (TASK-289)" (verified directly: line 77/94 today), i.e. this is a live
  document other work is still building on, not an abandoned artifact.
- **Decisions recorded** — no standalone `DEC-NNN` was required for this
  task; it is the implementation of an architecture already scoped by
  earlier planning, not itself a new authority/policy decision. N/A is the
  correct, considered answer here, not an omission.
- **Follow-up tasks created** — `TASK-148` ("MAP 6.13: Plan cold-start
  migration for runtime changes"), cross-checked against TASK-147 in the
  original review for output-path/dependency overlap, exists and is
  `RELEASED` today.
- **Event log entry prepared** — `events/events.jsonl` carries the full
  trail: PROGRESS ×2, CHANGES_REQUESTED (claude-lab-zera,
  2026-07-13T20:52:35Z), PROGRESS (fix), SUBMISSION, APPROVED
  (claude-lab-zera, 2026-07-13T20:55:52Z) — 7 events total, consistent with
  `map.db`'s pre-release `APPROVED` status.
- **Emergence capture considered** — Considered; nothing to capture beyond
  what the review record already carries. The one substantive finding
  (incomplete subsystem table) was mechanical and immediately fixed, not a
  reusable process lesson.

## Verification

- Independent review: `artifacts/reviews/task147-review-zera.md` — APPROVED
  after fix; all 4 acceptance criteria PASS, scope check confirms only the
  6 declared output paths changed.
- `python3 MAP_System/tests/test_intake_request.py` — 4/4 PASS, re-run today.
- Re-verified today: all 6 declared output paths exist;
  `ORCHESTRATION_ENTRYPOINT_SYSTEM.md` has current, live content (TASK-289
  addition dated today references it).
- `python3 MAP_System/scripts/validate_task_mirrors.py` — pass.
