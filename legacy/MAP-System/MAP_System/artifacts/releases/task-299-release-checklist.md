# Release Checklist: TASK-299

## Header

```
task_id:      TASK-299
released_by:  helper-releases-batch1-mive
release_date: 2026-08-10
```

## Checklist

- [x] Shared-file updates complete
  `artifacts/operations/cross-pc-authority-2026-07-28.md`,
  `db/authority.py`, `db/claims.py`, `notes/cross-pc-map-authority.md`,
  `scripts/map_authority.py`, `scripts/map_task.py`,
  `templates/install/bin/ai`,
  `templates/install/bin/ai-command-center-lab-codex`,
  `templates/install/bin/map-authority`,
  `templates/install/systemd/map-authority-mirror.service`,
  `templates/install/systemd/map-authority-mirror.timer`,
  `tests/test_map_authority.py`, `install-map-system.sh` — all 13 cited
  output-path artifacts confirmed present on disk.
- [x] Decisions recorded
  Establishes RUKI/Smalls as sole writable MAP SQLite authority; consistent
  with the direction TASK-298's evidence doc already flagged as the next
  required step.
- [x] Follow-up tasks created
  TASK-300 (operator notification on authority unavailability) already
  exists and is released alongside this task in the same batch.
- [x] Event log entry prepared
  This checklist's release event.
- [x] Emergence capture considered — mechanism: neither; evidence/reason: routine backlog release of already fully-reviewed work.

## Re-verification (2026-08-10, helper-releases-batch1-mive)

History: 6x PROGRESS (output paths registered) → SUBMISSION → APPROVED by
`task299-security-review-todo`. Confirmed this is a real dedicated review
session (visible in context-rotation/watchdog events, crashed shortly after
completing the approval) rather than a placeholder name. Its review artifact
(`task299-review.md`) names 2 real pre-fix issues (WAL/SHM sidecar loss,
installer mode-typo fallback), cites fix-verification tests, checksums
reviewed files, and cross-checks live activation evidence.

Independently ran `MAP_System.tests.test_map_authority` this session via the
project venv (`MAP_System/.venv/bin/python3 -m unittest`) — all tests pass,
including snapshot/writer-service coverage (checksum mismatch, path
traversal/symlink rejection, TOCTOU watcher-write races, systemd/cgroup
writer-probe fallback paths). Running the plain system `python3` fails this
suite with `ModuleNotFoundError: langgraph` — an environment issue (missing
dependency outside the venv), not a code regression; the project's own venv
is the correct interpreter and passes cleanly.

## Summary

Centralizes cross-PC MAP SQLite authority on RUKI/Smalls with a dedicated
gateway (`map_authority.py`/`authority.py`), atomic snapshot install with
checksum and path-traversal protection, and systemd mirror units. Reviewed
by a genuine dedicated security-review session that found and required fixes
for 2 real issues before approving. All 13 cited artifacts exist; test suite
passes under the correct interpreter. No gaps found. Ready to RELEASE.
