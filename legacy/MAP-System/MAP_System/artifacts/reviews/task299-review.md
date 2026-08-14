# TASK-299 Review

task_id: TASK-299
reviewer: task299-security-review-todo
task_owner: codex-live
review_date: 2026-07-28

## Verdict

APPROVED.

TASK-299 passes independent security and failure-mode review after the final
fixes and live activation evidence. The review initially found two
release-blocking issues, both resolved before this verdict:

- Mirror snapshot install could leave old `map.db` paired with newer canonical
  mirror files after a late swap failure.
- Installer service switching treated any non-`mirror` mode as standalone or
  authority behavior, which could re-enable local writer services after a valid
  JSON typo such as `mirorr`.

The final reviewed revision fixes both issues and satisfies the acceptance
criteria.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | `MAP_System/db/authority.py` fails closed for mirror-mode direct production DB writes. The activation evidence records RUKI as authority, KUDU as read-only mirror, KUDU `map.db` mode `0444`, guarded production connection raising `RemoteAuthorityRequired`, and raw SQLite write failing with `attempt to write a readonly database`. |
| 2 | PASS | `MAP_System/scripts/map_authority.py` validates snapshot membership, paths, links, sizes, and checksums; stages every file before replacement; backs up existing targets; rolls back prior mirror and DB changes on failure; restores WAL/SHM sidecars on failed DB swap; and replaces `map.db` last. Focused rollback tests pass. |
| 3 | PASS | Forced-command SSH path uses a versioned base64 JSON request, allowlisted operations, bounded argument counts and sizes, NUL rejection, canonical path override rejection, and argv-based subprocess calls. The activation evidence records arbitrary `id` through the authority key returning `invalid forced command`. |
| 4 | PASS | `claim`, `heartbeat`, `claim-review`, `get-open-review`, `release-review`, `route`, and allowlisted `map_task.py` lifecycle operations execute through `map-authority` with structured JSON results. The activation evidence records remote `heartbeat TASK-299 codex-live` succeeding and syncing to the mirror. |
| 5 | PASS | Installer templates add authority and mirror services while retaining standalone as the default absent config. `install-map-system.sh` now accepts only `standalone`, `authority`, or `mirror` before service configuration; unsupported mode exits nonzero before service changes. |
| 6 | PASS | Independent security review ran before activation, found required fixes, rechecked the corrected revision, and then reviewed live activation evidence in `MAP_System/artifacts/operations/cross-pc-authority-2026-07-28.md`. |

## Files Reviewed

- `MAP_System/tasks/TASK-299.json`
- `MAP_System/db/authority.py`
- `MAP_System/db/claims.py`
- `MAP_System/scripts/map_authority.py`
- `MAP_System/scripts/map_task.py`
- `MAP_System/tests/test_map_authority.py`
- `MAP_System/notes/cross-pc-map-authority.md`
- `MAP_System/templates/install/bin/ai`
- `MAP_System/templates/install/bin/ai-command-center-lab-codex`
- `MAP_System/templates/install/bin/map-authority`
- `MAP_System/templates/install/systemd/map-authority-mirror.service`
- `MAP_System/templates/install/systemd/map-authority-mirror.timer`
- `install-map-system.sh`
- `MAP_System/artifacts/operations/cross-pc-authority-2026-07-28.md`

Final reviewed checksums:

- `MAP_System/scripts/map_authority.py`: `635f96f222dbe66c6ad4682f7e2662d20376f98b0c2d6bd967efabbe82989aec`
- `MAP_System/tests/test_map_authority.py`: `51f270e8a090d425407899433cbae5c2f01ab42cd66566abf9d1db753d10e2a3`
- `install-map-system.sh`: `1f545a0c03ad488e53bb361ce097fa9c6440800beaaa9a0de0fb91d7a0ef5262`

## Forbidden Changes Check

PASS. This review did not edit implementation, installer, service, database, or
activation files. The only review-authored file is this review artifact. No
services were activated by the reviewer; live activation evidence was read from
`MAP_System/artifacts/operations/cross-pc-authority-2026-07-28.md`.

## Security And Failure-Mode Review

Initial findings:

- WAL/SHM sidecars were removed before final database replacement. A failed DB
  swap could leave the old database without its sidecars.
- Non-DB canonical mirrors were replaced before `map.db`, with no rollback if a
  later mirror or DB replacement failed.
- Installer authority-mode parsing accepted any valid JSON string and treated
  unsupported modes as the non-mirror branch, which could re-enable local
  writer services on a mirror host.

Fix verification:

- `test_failed_database_swap_restores_old_sidecars` passes.
- `test_failed_mirror_swap_rolls_back_earlier_mirrors` passes.
- `test_installer_rejects_unsupported_mode` passes.
- Full focused suite passes: `PYTHONDONTWRITEBYTECODE=1 MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_map_authority -v` returned 17/17 OK.
- Shell syntax check passes: `sh -n MAP_System/templates/install/bin/ai MAP_System/templates/install/bin/ai-command-center-lab-codex MAP_System/templates/install/bin/map-authority install-map-system.sh`.

Subprocess and parsing checks:

- Remote and local authority commands use argument arrays, not shell strings.
- Gateway requests are encoded as bounded JSON and decoded with protocol,
  operation, argument count, argument byte length, and NUL checks.
- `task` delegation allows only known `map_task.py` verbs and rejects canonical
  `--db`, `--output-dir`, and `--event-log` overrides.
- Snapshot extraction does not call `extractall`; it reads member streams after
  rejecting links, traversal, unknown paths, duplicate members, oversize
  expansion, missing manifest data, and checksum mismatches.

## Live Activation Evidence

`MAP_System/artifacts/operations/cross-pc-authority-2026-07-28.md` records:

- RUKI is `mode=authority`; KUDU is `mode=mirror`.
- RUKI production database is writable; KUDU production database is not
  writable and is mode `0444`.
- KUDU watcher and maintenance services are disabled/inactive; mirror timer is
  active and enabled.
- RUKI watcher and maintenance timer are active/enabled; mirror timer is
  disabled.
- User lingering is enabled on both PCs.
- Snapshot sync installed 294 validated files.
- WAL/SHM sidecars are absent after sync.
- KUDU direct production DB mutation fails closed.
- The dedicated authority SSH key rejects arbitrary command execution.
- Timer-triggered sync completed successfully and scheduled the next run.
