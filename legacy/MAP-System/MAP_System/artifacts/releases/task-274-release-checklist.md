# Release Checklist: TASK-274

## Header

```
task_id:      TASK-274
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

Fixes `db/claims.py submit_task()` so a SUBMISSION event is appended with the
correct submitting agent recorded, closing a gap where 50 approved tasks had
no SUBMISSION event and one task (TASK-236) durably misattributed authorship.
Scope explicitly excludes review-guard changes and historical backfill.

**Checklist evidence:**

- **Shared-file updates complete:** not applicable — this task's registered
  outputs are code and tests (`db/claims.py`, `scripts/map_task.py`,
  `scripts/run_tests.sh`, a delivery note, a test file), not a
  shared/canonical doc. `MAP_System/AGENTS.md`'s Communication section
  already listed `SUBMISSION` as a canonical event type before this task, so
  no doc update was needed to describe the event type itself — only the
  emission bug needed fixing.
- **Decisions recorded:** yes, three separate `DECISION_RECORDED` events tied
  directly to this task in `events.jsonl`: (1) 2026-07-23T09:00:40Z,
  `claude-lab-deli` — PROMO-0013/IDEA-0027 approved independent of author,
  re-deriving and confirming the gap size (51 vs. stated 50; 37/70=53% vs.
  stated 36/69=52%); (2) same timestamp — RISK-0005 independent fairness
  check, verdict FAIR; (3) 2026-07-26T19:43:51Z, `bigboss` — explicit
  operator pre-dispatch authorization clearing this task's structural
  approval for its registered scope.
- **Follow-up tasks created:** none created directly. Not needed: this
  task's scope explicitly excludes follow-on review-guard work, which was
  already independently tracked as TASK-278 (created earlier from the same
  TASK-277 roadmap) and is being released alongside it in this batch.
- **Event log entry prepared:** full lifecycle in `events.jsonl` — creation
  (2026-07-23T03:55:36Z), the two DECISION_RECORDED entries above,
  operator authorization, output-path registration, `SUBMISSION`
  (19:53:16Z), `APPROVED` (19:57:02Z, `codex-lab-feta`). This release
  appends the canonical `RELEASED` event.
- **Emergence capture considered:** yes — IDEA-0027, IDEA-0028, INS-0042,
  INS-0044, INS-0046, EXP-0008, EXP-0009, and PROMO-0013 all name TASK-274
  directly, capturing the submission-authorship gap, the fairness/promotion
  process itself, and follow-on parked ideas (IDEA-0028, IDEA-0026).

## Verification

- All 5 output paths confirmed to exist.
- `test_submission_event.py` passes as part of the full `run_tests.sh` run
  (73/79; unrelated pre-existing failures noted in TASK-268's checklist).
- Independent review: `APPROVED` by `codex-lab-feta`, 2026-07-26T19:57:02Z,
  after `claude-lab-deli`'s independent re-derivation of the measured gap
  (PROMO-0013/RISK-0005) found the numbers accurate and the fix fair.
- Explicit sequencing note in the task's own description ("db/claims.py is
  a contended output path of TASK-268 and TASK-273") is resolved: both
  TASK-268 and TASK-273 have already released (TASK-268 earlier in this same
  batch; TASK-273 previously), so no live collision remains.
