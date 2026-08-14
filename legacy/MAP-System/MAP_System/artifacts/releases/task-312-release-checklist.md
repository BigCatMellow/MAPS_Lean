# Release Checklist: TASK-312

## Header

```
task_id:      TASK-312
released_by:  zeno
release_date: 2026-08-01
review_record: MAP_System/artifacts/reviews/task312-independent-review-codex-lab-lime.md (APPROVED)
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Evidence

- `MAP_System/artifacts/recovery/ws3-green-baseline.md` records the single
  canonical baseline command and traces all seven recovery failures.
- The authority and sequencing decisions DEC-038 through DEC-041 remain in
  force; no new architecture decision was introduced.
- TASK-294 separately owns its final assertion rework and TASK-315 owns GitHub
  publication/Smalls convergence, so no hidden follow-up is folded into this
  release.
- Independent review reproduced the full suite at 84/84 plus focused graph,
  research, events, shared-state, Layer-1, local-lane, liveness, and chaos
  checks. Biggie's production database remained `0444` and no local writer
  workaround was added.
- The review and baseline artifacts were placed on Smalls before approval.
  Review SHA-256:
  `21733569f356458a3a4b0a68d5d96a61bff172d452342afa4caea52182cb42c7`.

## Rollback

TASK-315's checksummed pre-convergence archives preserve both hosts. The two
fixture permission changes affect disposable copies only; repository deltas can
be reverted normally after publication.
