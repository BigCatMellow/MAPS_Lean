<!-- hpom: file: artifacts/releases/task-219-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: HPOM-006 release gate, medium-risk lane per MAP_System/notes/review-guide.md -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-219

```
task_id:      TASK-219
released_by:  claude-lab-gome
release_date: 2026-07-17
reviewed_by:  claude-lab-gome
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

TASK-219 delivers `Projects/ClearFront/scripts/test_all.mjs` (one-command
test runner with self-managed Chromium lifecycle — launches, allocates a
free port, guaranteed cleanup via `finally` even on failure — running JS
syntax checks, extractor regressions, and all three registered browser
harnesses under one exit code) and
`Projects/ClearFront/templates/delivery-note-template.md` (one combined
evidence template for future low/medium-risk changes). Companion to
TASK-218; both implement DEC-CF-008 per the operator-directed
process-improvement batch (hcom thread clearfront-map #1851) responding
to the independent delivery audit.

- Files: `scripts/test_all.mjs`, `templates/delivery-note-template.md`.
- Decisions: implements DEC-CF-008; no new decision needed.
- Follow-ups: none. Future low/medium-risk ClearFront tasks use the new
  template and runner going forward — not retrofitted onto TASK-207–217.
- Events: recorded in both `MAP_System/events/events.jsonl` and, per
  DEC-CF-008 point 3, `Projects/ClearFront/events/events.jsonl`.
- Emergence: considered — no new card; this batch itself is the
  process-learning artifact (DEC-CF-008 + the audit it responds to).
- Operator-facing friction: none — directly answers an
  operator-commissioned audit finding (P1: harnesses fail without
  externally managed Chromium/arguments).

## Review

APPROVED — `Projects/ClearFront/artifacts/reviews/task219-review-gome.md`
by claude-lab-gome, medium-risk lane (one review, live-verified
including a forced-failure cleanup test, not a reproduce-everything
cycle). Reviewer independent of implementer (codex-lab-lilo).

## Verification

Runner exercised live (9/9 pass, exit 0) and its failure path forced
live (exit 1, confirmed no leftover Chromium process or temp profile
dir). `source/`/`baseline/` integrity unchanged. Task graph/schema/mirror
validators pass.
