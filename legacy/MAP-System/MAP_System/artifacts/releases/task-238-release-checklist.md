# TASK-238 Release Checklist

task_id: TASK-238
released_by: claude-lab-lure
review_record: MAP_System/artifacts/reviews/task238-review-lilo.md
release_date: 2026-07-19

## Release checks

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Evidence

- Independent review APPROVED (lilo, `artifacts/reviews/task238-review-lilo.md`),
  independently re-verified by kiri; all 18 focused Librarian tests PASS,
  repo-wide wikilink validation reports 0 findings, and task mirrors validate.
- The fix makes the related-section autofixer emit a resolver-accepted
  `[[./stem]]` form for ROOT-top-level files sharing a stem, and threads `root`
  through `validate_wikilinks_in_file`/`validate_all_wikilinks` (a latent bug
  the regression test exposed).
- No shared-state or decision change: this is a bounded tooling correctness fix.
- No follow-up task required: the bonus root-threading defect was fixed inline
  and is covered by the new regression tests.
- Emergence capture considered: the fix plus regression tests convert the
  recurring "top-level stem collision" lesson into a mechanical guard, which is
  the intended emergence outcome; no separate emergence record is required.
- Normal release writes the durable lifecycle event.
