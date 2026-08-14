# Release Checklist: TASK-174

## Header

```
task_id:      TASK-174
released_by:  mapfinish2-zemi
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Builds `librarian.py` (wikilink resolution, disambiguation, broken/ambiguous
link validation) and applies wikilinks to all 16 root `*_SYSTEM.md`/policy
docs, with real compression-ratio and file-churn measurements. First
submission was CHANGES_REQUESTED for not declaring the 16 edited docs as
output paths (a real ownership-visibility gap, not a code defect); fixed by
registering them and resubmitting with no implementation changes.

## Evidence Per Check

- **Shared-file updates complete** — this task's canonical-file update *is*
  the deliverable classify_release() itself keys "full" tier on: all 16
  root system/policy docs are declared output paths and carry live
  wikilinks today. Re-verified directly: `python3
  MAP_System/scripts/librarian.py validate` currently reports 19 findings
  repo-wide, but every one is in `artifacts/`, `emergence/`, or `inbox/`
  content added after this task — **none are in any of the 16 TASK-174
  output docs**. The task's own scope is still clean.
- **Decisions recorded** — no new `DEC-NNN` required; this is tooling +
  mechanical doc annotation, not a policy/authority decision. N/A is the
  correct answer.
- **Follow-up tasks created** — not a new task, but genuine ongoing
  build-on: `librarian.py`'s wikilink mechanism is still actively
  referenced by `map_emergence.py` (line 218, verified directly) and
  `notes/orchestration-notes.md` today.
- **Event log entry prepared** — `events/events.jsonl` carries 36 events for
  this task (PROGRESS, CHANGES_REQUESTED, a burst of PROGRESS entries from
  registering 16 output paths, APPROVED — `codex-lab-mozu`,
  2026-07-14T05:54:17Z), consistent with `map.db`'s pre-release `APPROVED`
  status.
- **Emergence capture considered** — Considered; the CHANGES_REQUESTED
  finding (undeclared output paths) is a recurring, already-tracked pattern
  documented elsewhere (`INS-0042` — output paths are write-once with no
  unregister verb) rather than a novel insight this release needs to
  capture separately.

## Verification

- Independent reviews (2 rounds): `artifacts/reviews/task174-review-mozu.md`
  (CHANGES_REQUESTED — missing output-path declarations),
  `task174-rereview-mozu.md` (APPROVED) — all 4 acceptance criteria PASS in
  the final pass; scope check confirms all 16 previously-undeclared docs are
  now declared and no new implementation scope was introduced during
  rework.
- `python3 MAP_System/tests/test_librarian.py` — 18/18 PASS, re-run today.
- `python3 MAP_System/scripts/librarian.py validate` — re-run today; 19
  repo-wide findings, none in the 16 declared output docs (see above).
- `python3 MAP_System/scripts/validate_task_mirrors.py` — pass.
