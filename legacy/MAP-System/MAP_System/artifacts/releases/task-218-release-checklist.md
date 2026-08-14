<!-- hpom: file: artifacts/releases/task-218-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: HPOM-006 release gate, low-risk lane per MAP_System/notes/review-guide.md -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-218

## Header

```
task_id:      TASK-218
released_by:  claude-lab-gome
release_date: 2026-07-17
reviewed_by:  codex-lab-lilo (light review, low-risk lane)
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

TASK-218 adds a Risk-Tiered Review section to `MAP_System/notes/review-guide.md`
— a reusable MAP-wide convention (not ClearFront-specific) for
calibrating review/release ceremony to actual change risk, adopted from
the independent ClearFront delivery audit's findings. Purely additive
documentation; no existing section changed.

- Files: `MAP_System/notes/review-guide.md`.
- Shared files: none beyond the one file.
- Decisions: implements `Projects/ClearFront/shared/decisions.md`
  DEC-CF-008's MAP-level half; no new decision record needed here.
- Follow-ups: none. TASK-219 is the companion ClearFront-local half of
  the same batch, tracked separately.
- Events: creation, submission, light-review approval, and this release
  in `events/events.jsonl` (trace_id task:TASK-218).
- Emergence: considered — no new card; this is process learning already
  captured in DEC-CF-008 and this task itself.
- Operator-facing friction: none — this directly answers an
  operator-commissioned audit finding.

## Review

- Verdict: APPROVED — light review per the low-risk lane this task
  itself introduces (`MAP_System/artifacts/reviews/task218-light-review-lilo.md`
  by codex-lab-lilo): sanity-checked the three lanes make sense and are
  internally consistent, not a full independent-reproduction cycle.
  Correctly matches the tier — this is documentation with no runtime
  behavior to verify.
- Reviewer independence: claude-lab-gome authored; codex-lab-lilo
  reviewed, no implementation overlap.

## Verification

- Purely additive change confirmed: no existing `review-guide.md`
  section (Claim Before Reviewing, Debate) was altered.
- Cross-references to DEC-CF-008 and the audit are accurate paths.
