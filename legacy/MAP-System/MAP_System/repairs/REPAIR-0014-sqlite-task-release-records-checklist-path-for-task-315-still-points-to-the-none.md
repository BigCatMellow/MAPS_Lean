# Repair Record

Repair ID: REPAIR-0014
Related task: TASK-315
Found by: helper-task323-p02-tina
Date: 2026-08-10
Severity: BLOCKING
Status: APPLIED

## What was found

SQLite task_release_records.checklist_path for TASK-315 still points to the nonexistent legacy path /home/home/Projects/MultiAgentProject/Source/MAP_System/artifacts/releases/task-315-release-checklist.md. The checklist exists and validates at the current repo path MAP_System/artifacts/releases/task-315-release-checklist.md.

## Surfaced by

Manual observation.

## Severity rationale

BLOCKING: the durable release-record backlink does not resolve, failing the release-path validator for the sole remaining SQLite release row out of 133 (132/133 pass). Not applied directly because this workspace runs in MAP authority mirror mode - the local map.db is not writable per map_authority.py topology rules, and release_task.py's release() only INSERTs a task_release_records row for a task in APPROVED status (TASK-315 is already RELEASED, so no existing verb can re-run or amend it). No SQL UPDATE was attempted locally per instruction (mirror host must not hand-edit map.db).

## Proposed or applied fix

PROPOSED, not applied: the authority host should update task_release_records.checklist_path for task_id='TASK-315' from the legacy /home/home/... path to MAP_System/artifacts/releases/task-315-release-checklist.md (current repo path), then let mirrors sync normally. No map_task.py/release_task.py verb currently exists for correcting a checklist_path on an already-RELEASED task; map_authority.py's task_release_records schema and release_task.release() were inspected and confirmed to offer no amend/repair path other than a direct, authority-side UPDATE. Recommend either a one-off authority-side SQL correction (auditable, single-row, non-destructive) or adding a map_task.py 'fix-release-path' verb if this class of drift recurs.

## Authority check

- [ ] DRIFT or mechanical BLOCKING — core agent applied directly

## Verification

Confirmed via sqlite3 MAP_System/map.db: task_release_records row for TASK-315 has checklist_path=/home/home/Projects/MultiAgentProject/Source/MAP_System/artifacts/releases/task-315-release-checklist.md. Confirmed MAP_System/artifacts/releases/task-315-release-checklist.md exists in the current repo and passes the tier-specific checklist validator (per helper-librarian.md 2026-08-09 rerun: 132/133 release rows pass, TASK-315 is the sole path failure). No mirror files or SQLite rows were modified by this repair record.

## Recurrence check

Fourth consecutive helper-librarian audit (2026-07-29 through 2026-08-09 rerun) surfacing the same unresolved TASK-315 backlink; this is the first repair record filed for it rather than a repeated read-only note.

## Applied fix confirmed on Smalls (2026-08-10, claude-lab-sumi)

While preparing TASK-323 for resubmission, queried the authority host
directly: `ssh smalls "python3 -c \"import sqlite3; c=sqlite3.connect(...); print(c.execute(\"select checklist_path from task_release_records where task_id='TASK-315'\").fetchone())\""`
returned `('MAP_System/artifacts/releases/task-315-release-checklist.md',)`
— the corrected current-repo path, not the legacy `/home/home/...` path.
The proposed single-row UPDATE has been applied at the authority host;
exact actor/timestamp of the authority-side write was not captured in an
events.jsonl entry visible to this check, but the resulting row value is
confirmed correct as of this verification.

## Notes

Filed as bounded support for TASK-323 (owner claude-lab-sumi, who submits/routes to authority). This record documents the finding and proposed fix per TASK-323's instruction to correct via authority/provenance record, not local SQL. Reported to owner via hcom for routing to the authority host (Biggie). Full writeup cross-referenced at MAP_System/artifacts/recovery/p02-validation-debt-repair-2026-08-10.md.
