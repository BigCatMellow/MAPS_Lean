# Release Checklist: TASK-278

## Header

```
task_id:      TASK-278
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

Implements the approved TASK-277 P0 integrity slice: a canonical author
identity that survives submission and owner reassignment, keying review-claim
and terminal review gates to that identity while preserving atomic duplicate-
review arbitration, with an explicit migration rule for pre-existing
submissions of unknown authorship.

**Checklist evidence:**

- **Shared-file updates complete:** not applicable — outputs are code,
  schema, and tests (`db/claims.py`, `db/review_authorship.py`,
  `migration/schema.sql`, `scripts/map_task.py`, `scripts/validate_review.py`,
  three test files, a delivery note). No shared/canonical doc required
  updating to deliver an internal identity/gate mechanism.
- **Decisions recorded:** yes — this task's `decision_class` is `AUTHORITY`,
  which per `DECISION_AUTHORITY_SYSTEM.md` requires command-center approval.
  Two `DECISION_RECORDED` events tied directly to TASK-278 exist in
  `events.jsonl`: 2026-07-26T19:57:50Z (`bigboss`, clearing authority and
  security/structural pre-dispatch approval for the review-authorship
  enforcement scope) and 2026-07-27T12:21:31Z (`bigboss`, directly
  authorizing `claude-lab-nora` to resume the task in-chat, "Im good with
  all three," covering the output-path repair, TASK-263 orphan recovery, and
  taking TASK-278).
- **Follow-up tasks created:** none created directly. Not needed: scope is
  explicitly bounded to the approved TASK-277 slice, with output-path
  sequencing against TASK-274/TASK-268 handled via `REPAIR-0008` rather than
  a new task.
- **Event log entry prepared:** full lifecycle in `events.jsonl`, including
  two `CHANGES_REQUESTED`/rework cycles: rejected once by `codex-lab-diro`
  (2026-07-27T12:54:19Z, canonical-independent-review gap), reworked, then
  `APPROVED` by the same reviewer (13:03:08Z). This release appends the
  canonical `RELEASED` event.
- **Emergence capture considered:** considered; no `emergence/` record names
  TASK-278 directly. None warranted beyond what TASK-274's IDEA-0026 (parked,
  keying no-self-review guards to durable authorship) already anticipated as
  the natural next step, which this task is.

## Verification

- All 9 output paths confirmed to exist.
- `test_review_authorship.py`, `test_review_claims.py`, and
  `test_review_gate.py` all pass as part of the full `run_tests.sh` run
  (73/79; unrelated pre-existing failures noted in TASK-268's checklist).
- Independent review: `APPROVED` by `codex-lab-diro`, 2026-07-27T13:03:08Z,
  after one rework cycle correcting a canonical-independent-review gap in
  `validate_review.py`.
- Output-path sequencing against TASK-274 (`db/claims.py`,
  `scripts/map_task.py`) is resolved: TASK-274 has already released earlier
  in this same batch, so no live collision remains.
