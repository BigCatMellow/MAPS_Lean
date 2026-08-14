<!-- hpom: file: artifacts/releases/task-077-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-28 -->
<!-- hpom: verified_against: DEC-032 release-backlog authority -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-077

## Header

```
task_id:      TASK-077
released_by:  mapfinish-rafa
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Sole output path `shared/decisions.md` exists and is current. Release tier
is `full` (`classify_release()`: output touches `shared/`).

- **Shared-file updates complete**: `shared/decisions.md` contains
  `## DEC-012: Canonical Repo Is Downloads/MultiAgentProject` (line 164) plus
  its later supersession note (`DEC-014 supersedes DEC-012's...`, line 198;
  `Supersedes: DEC-012`, line 226; `TASK-079 completed the DEC-012
  reconciliation plan`, line 233). The freeze-marker path this task also
  covered no longer exists post-migration, but that is documented
  end-of-lifecycle cleanup (TASK-079 executed the reconciliation and DEC-014
  superseded the path rule), not an open gap.
- **Decisions recorded**: this task's entire acceptance criterion *is*
  recording DEC-012 — done, and confirmed live in `decisions.md` today.
- **Follow-up tasks created**: `events/events.jsonl:282` (SUBMISSION) states
  "remaining criterion satisfied by TASK-079"; `tasks/TASK-079.json`'s title
  is literally "Execute DEC-012 git sequence" and its description names DEC-012
  by ID — a direct, verifiable follow-up.
- **Event log entry prepared**: `events/events.jsonl:270` (PROGRESS/created),
  `:272` (DECISION_RECORDED, DEC-012), `:282` (SUBMISSION), `:283` (APPROVED)
  all exist for TASK-077.
- **Emergence capture considered**: `emergence/synthesis/SYN-0001-two-readers-one-truth.md`
  cites DEC-012 by name as the worked example of its first fix pattern
  ("Declare one view authoritative and write it down — DEC-012 (repo A
  canonical)...") — this task's decision was captured into a durable
  cross-task synthesis insight, not merely logged and forgotten.

Rollback: reversible by normal means — a decision is superseded by a later
decision (as DEC-014 already did for the path-specific portion), not
force-reverted. No special rollback steps required.

This task is ready to be RELEASED: the decision it recorded is still live
and cited by name in later canonical docs (`canonical-repo.md`) and a
cross-task synthesis record, and all five checks above are independently
verifiable in the repo today.
