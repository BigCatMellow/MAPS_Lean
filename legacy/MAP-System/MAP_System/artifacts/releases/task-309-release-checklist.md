# Release Checklist: TASK-309

## Header

```
task_id:      TASK-309
released_by:  claude-lab-sumi
release_date: 2026-08-10
review_record: APPROVED (codex-lab-rani, 2026-08-10); see caveat below on the dead evidence citation this record inherited
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered — mechanism: neither; evidence/reason: routine release-checklist authoring for already-approved recovery-epic work (batch2 pass, 2026-08-10); the dead-citation finding below is a documentation defect, not a new implementation pattern.

## Caveat: dead citation, corrected

- History: created (codex-lab-risa) → owner reassigned twice more via
  documented coordinator handoffs (map-coordinator-hobo per DEC-039
  stale-lease reason; then claude-lab-luzo per stale coordinator not in
  live roster; then coordinator-replacement-rose) → SUBMISSION
  (claude-lab-luzo, 2026-08-06) → APPROVED (codex-lab-rani, 2026-08-10).
- **Finding**: the task JSON's own description cites
  `MAP_System_Recovery_2026-07-29/03_kickoff/MAP_RECOVERY_PLAN_REVIEW.md`
  as "Approval evidence." Independently re-confirmed for this checklist:
  that entire `03_kickoff/` subdirectory does not exist anywhere in the
  tree (`find MAP_System_Recovery_2026-07-29 -type d` shows only
  `00_control/` and `01_preserved_snapshot/`). This is a citation to a
  path that was apparently never created/tracked, not a fabricated or
  altered artifact.
- **Correct evidence, independently verified**: operator authorization for
  the recovery effort is real and documented in `MAP_System/shared/decisions.md`
  DEC-036 ("Claude Takes Over MAP Recovery Coordination While Codex Is
  Unavailable," operator-directed 2026-07-30). The actual output artifact,
  `MAP_System_Recovery_2026-07-29/00_control/phase2-status.md`, exists,
  is transparent about a related gap (it was regenerated from live
  canonical state on 2026-08-04 by claude-lab-luzo because the original
  could not be located — no git history for that path), and its
  workstream table cross-references real, independently-checked evidence:
  WS-1 (TASK-310/313/314), WS-2 (TASK-311), WS-3 (TASK-312), each shown
  RELEASED/APPROVED with named reviewers and review-artifact paths.
- **Correction attempted and blocked by design, not bypassed**: attempted
  `map-authority task describe TASK-309 --description ... --actor
  helper-releases-batch2-bela --reason ...` to replace the dead-path
  citation with the correct one. Refused by the tool: `describe only
  accepts a task currently in NEEDS_SHAPING` (TASK-309 is APPROVED).
  Checked `amend-criteria`: it only rewrites `acceptance_criteria` entries,
  not `description`, and requires a recorded DEC-NNN/REPAIR-NNNN authority
  — not applicable here. Checked `add-output-path`: gated to
  `{NEEDS_SHAPING, READY, IN_PROGRESS, CHANGES_REQUESTED}`, also not
  APPROVED-eligible. **No sanctioned map-authority lifecycle verb can edit
  an APPROVED task's description field.** Per instruction, direct SQL was
  not used as a workaround. The dead citation therefore still appears
  verbatim in `TASK-309.json`'s description; this checklist is the
  authoritative correction record until a future decision authorizes a
  lifecycle-appropriate fix (e.g., a small REPAIR task, or a documented
  DEC entry citing this checklist, run through `describe`/`amend-criteria`
  at a stage where the task is editable).
- Substantive gate independently re-confirmed: WS-1/2/3 sequencing before
  WS-4–7 is real and satisfied per phase2-status.md and the corroborating
  TASK-311/313 release evidence in this same batch.

## Follow-up

Recommend a small governance task (or REPAIR-NNNN) to correct the
description text of TASK-309.json directly once a sanctioned editable
lifecycle state is reached, citing this checklist as the authority for the
replacement text.

## Rollback

The single output artifact `00_control/phase2-status.md` is itself a
regenerated status document; prior versions (if any resurface) can be
diffed against it. No irreversible mutation was made to task state by this
release beyond the standard release event.
