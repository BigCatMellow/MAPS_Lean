# Release Checklist: TASK-300

## Header

```
task_id:      TASK-300
released_by:  helper-releases-batch1-mive
release_date: 2026-08-10
```

## Checklist

- [x] Shared-file updates complete
  `artifacts/reviews/task300-review.md`, `notes/cross-pc-map-authority.md`,
  `scripts/map_authority_notify.py`,
  `templates/install/bin/map-authority-sync`,
  `templates/install/systemd/map-authority-mirror.service`,
  `tests/test_map_authority_notify.py`, `install-map-system.sh` — all 7
  cited output-path artifacts confirmed present on disk.
- [x] Decisions recorded
  None new; extends TASK-299's authority gateway with operator notification
  on unavailability, same design.
- [x] Follow-up tasks created
  None required.
- [x] Event log entry prepared
  This checklist's release event.
- [x] Emergence capture considered — mechanism: neither; evidence/reason: routine backlog release of already fully-reviewed work.

## Re-verification (2026-08-10, helper-releases-batch1-mive)

History: created → PROGRESS → SUBMISSION → APPROVED (`task299-security-review-todo`,
same reviewer session as TASK-299). Single clean pass.

Independently ran `MAP_System.tests.test_map_authority_notify` this session
via the project venv (`MAP_System/.venv/bin/python3 -m unittest`) — all 8
tests pass, covering first-failure notification, rate-limiting on repeated
failure, recovery notification exactly once, and retry-when-desktop-notifier-
was-unavailable for both failure and recovery paths.

## Summary

Adds operator desktop notification when the centralized cross-PC MAP
authority (TASK-299) becomes unreachable, with rate-limiting and recovery
notification. Reviewed by the same dedicated security-review session as
TASK-299 (same day, immediately following). All 7 cited artifacts exist and
the test suite passes. No gaps found. Ready to RELEASE.
