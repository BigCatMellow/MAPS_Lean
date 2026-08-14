<!-- hpom: file: artifacts/releases/task-227-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-18 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-227

```
task_id:      TASK-227
released_by:  claude-lab-gome
release_date: 2026-07-18
reviewed_by:  codex-lab-lilo
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

TASK-227 delivers `MAP_System/notes/system-improvement-implementation-plan.md`,
turning the system-improvement kickoff into a bounded, risk-tiered
implementation plan. The reworked plan addresses all five REQUIRED review
findings: a 1a coordination-surface read-model contract (source authority,
freshness, conflict/unknown, three deterministic mixed-state fixtures); a 2a
bounded index that reconciles `shared/memory-map.md` rather than creating a
shadow `notes/INDEX.md`; the 3a helper no-direct-mutation rule split out as an
AUTHORITY-class decision requiring command-center approval; an evidence-intake
section (results become candidates, not auto-tasks); and a north-star
lifecycle outcome with per-task observable measures and a record-negative-and-
revert rule.

- Files: `MAP_System/notes/system-improvement-implementation-plan.md`.
- Decisions: the plan routes one AUTHORITY-class decision (3a-i helper
  mutation) to command-center; no decision made in this note itself.
- Follow-ups: the plan's immediate slate (coordination-surface task,
  durable-conventions batch, helper-authority decision) plus backlog items.
  TASK-236 (advisory monitor) advances the same "catch it in real time" spine
  and was created after this plan.
- Events: creation, two submissions, one CHANGES_REQUESTED, approval, and this
  release in `events/events.jsonl` (trace_id task:TASK-227).
- Emergence: considered — the plan itself carries the system-improvement
  learning; no separate card.
- Operator-facing friction: this task directly serves the operator's
  system-improvement and real-time-visibility directives.

## Review

APPROVED after one CHANGES_REQUESTED round —
`MAP_System/artifacts/reviews/task227-rereview-lilo.md` (codex-lab-lilo),
verifying C1–C5 against the submitted plan plus graph/mirror validation, on
top of the original `task227-review-lilo.md`. Reworked using the two
evidence-only readiness audits the reviewer produced (coordination-surface,
durable-memory-index) plus the practice-lifecycle audit and plan-challenge
memo. Reviewer independent of the plan's author.

## Verification

`validate_task_graph.py` and `validate_task_mirrors.py` pass; the plan links
both durable resume sources (kickoff, book-lessons) and every REQUIRED finding
is addressed at the level the reviewer verified.
