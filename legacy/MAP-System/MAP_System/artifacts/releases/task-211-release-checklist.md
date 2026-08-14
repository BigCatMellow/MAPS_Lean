<!-- hpom: file: artifacts/releases/task-211-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-211

## Header

```
task_id:      TASK-211
released_by:  claude-lab-gome
release_date: 2026-07-17
reviewed_by:  claude-lab-gome
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

TASK-211 (replacing misclassified/RETIRED TASK-209) delivers the
phase-1 rules-to-implementation conformance audit required by
`Projects/ClearFront/shared/project-brief.md`: every numbered section of
`clearfront_rules.md` and all 7 core keywords checked against
`baseline/index.html`, with line references. Implemented by
codex-lab-lilo, independently reviewed by claude-lab-gome.

- Files: `Projects/ClearFront/artifacts/research/rules-conformance-audit.md`.
- Shared files: `Projects/ClearFront/shared/current-state.md` updated to
  reflect TASK-209 retirement and TASK-211 completion (done as part of
  this task's owner follow-through, not a separate task).
- Decisions: no new decision — this is analysis, not a rules/architecture
  change. Its findings (Equipment/Mind/Forge/Neutral scope, Rush/Stun
  keyword gaps, undo hidden-info leak, undocumented fatigue) are inputs
  to future decisions, not decisions themselves.
- Follow-ups: none created as separate task records yet — the audit's
  6 "Prioritized Follow-Up Candidates" and INS-0025 are the queue for
  the next game-improvement/bugfix tasks, to be authored when that work
  starts (after the engine/render/input decomposition, per
  `shared/current-state.md`).
- Events: creation (as TASK-211, replacing superseded TASK-209),
  submission, approval, and this release are in `events/events.jsonl`
  (trace_id task:TASK-211), `--fail-on-new` clean.
- Emergence: considered — captured
  `MAP_System/emergence/insights/INS-0025-undo-reveals-hidden-info-in-replacement.md`
  (the one correctness/exploit-shaped finding, distinguished from the
  legitimate scope-gap deviations).
- Operator-facing friction: no new operator-friction candidate found.

## Review

- Verdict: APPROVED —
  `Projects/ClearFront/artifacts/reviews/task211-review-gome.md` by
  `claude-lab-gome`. Reviewer independently re-derived 7 of the audit's
  claims directly from `baseline/index.html` (not from the audit's own
  citations) and found zero inaccuracies.
- Reviewer independence: implementer was codex-lab-lilo; claude-lab-gome
  contributed no part of the audit text.

## Verification

- All 16 rules sections and all 7 keywords individually addressed with
  line-referenced verdicts.
- `baseline/index.html` md5 unchanged (`5124cac23a9bd326bb8dfd00a110af92`);
  `source/SHA256SUMS.txt` verifies 11/11, exit 0; only the one audit file
  exists under `artifacts/research/`.
- `validate_task_graph.py`, `validate_task_schema.py`,
  `validate_task_mirrors.py`, `validate_events.py --fail-on-new`: all
  pass (task-graph collision from superseded TASK-209 resolved via
  RETIRED status per TASK-100 precedent before this release).
