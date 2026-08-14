<!-- hpom: file: artifacts/releases/task-078-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-28 -->
<!-- hpom: verified_against: DEC-032 release-backlog authority -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-078

## Header

```
task_id:      TASK-078
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

All 8 `output_paths` verified present today. Release tier is `full`
(`classify_release()`: output is `AGENTS.md`, a canonical root doc).

- **Shared-file updates complete**: `MAP_System/AGENTS.md` line 449 has the
  live "Security Second Pass" subsection this task added;
  `notes/release-path-checklist.md` exists with real content (not a stub).
- **Decisions recorded**: this task's deliverable is itself two emergence
  promotion records functioning as the decision artifacts — `PROMO-0004`
  (Status: APPROVED, approved by codex-lab-limo via TASK-078 peer review)
  and `PROMO-0005`, both fully filled with no dangling boxes/TBDs per the
  SUBMISSION event. No separate `DEC-NNN` was required or created for a
  process/tooling addition of this kind, and none is claimed here.
- **Follow-up tasks created**: `tasks/TASK-112.json` explicitly builds on
  this task's output ("AGENTS.md already has a Security Second Pass rule...
  do not duplicate, reference and extend it," acceptance criterion requires
  cross-linking it); `tasks/TASK-181.json` lists `PROMO-0005-release-path-checklist.md`
  as required context. Both are genuine later tasks that consume TASK-078's
  deliverables, not just text mentions.
- **Event log entry prepared**: `events/events.jsonl:273` (PROGRESS/created),
  `:274` (SUBMISSION, 2026-07-02T01:15:00-04:00, names both promotions and
  confirms peer review not self-approval), `:277` (APPROVED, codex-lab-limo)
  all exist for TASK-078.
- **Emergence capture considered**: this task's entire purpose is emergence
  promotion — `IDEA-0004`/`INS-0004` and `IDEA-0005`/`INS-0005` (verified
  `Status: PROMOTED` in both insight files) were closed via
  `map_emergence.py promote` into `PROMO-0004`/`PROMO-0005`, cited by source
  incident (CommandCenterUI CSRF gap; DarkMellow stale-ZIP release incident)
  per the task description and SUBMISSION event.

Rollback: reversible by normal means — `AGENTS.md`'s added subsection and
`notes/release-path-checklist.md` are ordinary source files (`git revert` or
supersede via a new task). No special rollback steps required.

This task is ready to be RELEASED: both promoted artifacts are live in
canonical docs today and are actively extended by later tasks (TASK-112,
TASK-181), and all five checks above are independently verifiable in the
repo, not merely asserted.
