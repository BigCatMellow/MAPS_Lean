# Release Checklist: TASK-310

## Header

```
task_id:      TASK-310
released_by:  zeno
release_date: 2026-08-01
review_record: MAP_System/artifacts/reviews/task310-final-rereview-codex-lab-lime.md (APPROVED)
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Evidence

- The authority contract is implemented in the shared gateway/classifier and
  consumed by `map-authority status`, wrapped routing, direct runner output,
  rendered current state, and TASK-314's released Command Center display.
- Existing DEC-036 through DEC-041 authority, sequencing, and Command Center
  decisions remain controlling; no new architecture decision was introduced.
- TASK-315 owns publication and cross-PC convergence. The remaining timer/
  threshold coupling recommendation is nonblocking and recorded in the final
  review rather than silently expanded into this task.
- Direct and wrapped routes fail closed on stale, unavailable, invalid, writer-
  active, and service-manager-unavailable states. Explicit scratch databases
  retain isolated integration behavior without weakening production gating.
- Final independent rereview by `codex-lab-lime` passed focused tests 56/56,
  integration 11/11, the complete release suite 84/84, review validation, and
  diff checks with no BLOCKER or REQUIRED findings.
- The final review artifact was copied to Smalls before approval and matched on
  both hosts at SHA-256
  `15624e7f226c5bd0f3de5427a0f35b9443e5499ec017ec2da687f08565a23418`.

## Rollback

TASK-315's checksummed Biggie pre-convergence backup and Git bundle preserve
the complete pre-publication state. The implementation is also a normal Git
delta that can be reverted after publication without direct database edits.
