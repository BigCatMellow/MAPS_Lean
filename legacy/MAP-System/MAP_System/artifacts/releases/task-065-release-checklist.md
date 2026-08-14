<!-- hpom: file: artifacts/releases/task-065-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-28 -->
<!-- hpom: verified_against: DEC-032 release-backlog authority -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-065

## Header

```
task_id:      TASK-065
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

All 17 `output_paths` verified present and substantive today (e.g.
`map_emergence.py` 1185 lines, `map_task.py` 886 lines, `validate_events.py`
258 lines, plus matching test files). Release tier is `full`
(`classify_release()`: output touches `shared/`).

- **Shared-file updates complete**: `shared/approval-calibration.md` (52
  lines), `shared/canonical-repo.md` (75 lines), `shared/current-state.md`
  (261 lines), `shared/improvement-backlog.md` (289 lines) all exist and are
  actively maintained — `canonical-repo.md` carries `last_verified:
  2026-07-22` and is still extended by later tasks (TASK-090, TASK-267,
  DEC-014).
- **Decisions recorded**: `shared/canonical-repo.md` (a TASK-065 output)
  documents DEC-012 (originally) and DEC-014 (current), per its own header
  (`Decision: DEC-014. Supersedes... DEC-012`) and per
  `events/events.jsonl:272` (`DECISION_RECORDED`, TASK-077, explicitly
  "Companion to TASK-065's shared/canonical-repo.md").
- **Follow-up tasks created**: `tasks/TASK-079.json` and
  `tasks/TASK-080.json` both list `TASK-065` in `dependencies`;
  `tasks/TASK-081.json` describes itself as "the tooling-domain follow-ups
  from the MAP full report after TASK-065/080."
- **Event log entry prepared**: `events/events.jsonl:275` (`SUBMISSION`,
  2026-07-02T03:39:42Z) and `events/events.jsonl:295` (`APPROVED`,
  2026-07-02T04:47:38Z) both exist for TASK-065.
- **Emergence capture considered**: `emergence/insights/INS-0006` and
  `emergence/ideas/IDEA-0006` (sequential task-ID collision under
  concurrent agents) were promoted directly into TASK-065's atomic
  task-ID acceptance criterion; `emergence/insights/INS-0007` (emergence
  lifecycle closeout) was promoted into TASK-065's `map_emergence.py`
  stale-reporting work. Both closed during TASK-075.

Rollback: reversible by normal means — the scripts/tests are ordinary
source files (`git revert`), and the shared docs can be reworked by a new
task if a fault is found. No special rollback steps required.

This task is ready to be RELEASED: its deliverable exists, is still
actively depended upon (canonical-repo.md extended by TASK-090/TASK-267/
DEC-014; the atomic task-ID and emergence-stale mechanisms it built are
load-bearing across the rest of the backlog), and all five checks above
are independently verifiable in the repo today, not merely asserted.
