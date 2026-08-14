# Release Checklist: TASK-288

## Header

```
task_id:      TASK-288
released_by:  lili-replacement-nisa
release_date: 2026-07-28
review_record: MAP_System/artifacts/reviews/task288-independent-review-task288-review-valo.md (CHANGES_REQUESTED),
                MAP_System/artifacts/reviews/task288-rereview-task288-review-valo.md (APPROVED)
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Reconciles finding F5: `scripts/release_task.py`'s release gate previously
demanded all five `REQUIRED_CHECKS` for every release regardless of risk,
which contradicted both `notes/review-guide.md`'s risk-tiered review policy
and `CHANGE_CONTROL_SYSTEM.md`'s own output-path-scoped rule, neither of
which was implemented in code. Real-world effect: zero releases for 5 days,
90 tasks stuck APPROVED (some since 2026-07-17).

`classify_release()` now implements one rule, checked in this order: (1)
output touches `shared/`, `templates/`, or a canonical file (`AGENTS.md`,
`CLAUDE.md`, `*_SYSTEM.md`, or the explicit `CANONICAL_ROOT_DOC_BASENAMES`
set added after independent review found the naming-convention regex alone
missed `DECISION_CLASSES.md`/`DESTRUCTIVE_ACTION_POLICY.md`/
`AGENT_PERMISSION_LEVELS.md`/`NEW_PROJECT_WIZARD.md`); (2)
`risk_class=SECURITY`/`risk_severity` STRUCTURAL-or-BLOCKING/`task_tier`
policy-operator-architecture; (3) otherwise low-risk, requiring only the
Emergence-capture-considered checklist line. `review-guide.md` and
`CHANGE_CONTROL_SYSTEM.md` now state and cross-reference the identical
rule instead of two drifted descriptions.

`scripts/batch_release_low_risk.py` (new) used this rule, in small
operator-confirmed chunks, to release 61 of the 90 backlogged APPROVED
tasks as low-risk; the other 29 correctly remain APPROVED pending real
hand-written checklists (they touch canonical paths or carry explicit
high-risk fields).

## Verification

- `MAP_System/.venv/bin/python3 MAP_System/tests/test_release_gate.py` — 9/9 PASS (includes
  the regression test added for the independent reviewer's REQUIRED finding).
- Independent review: `task288-review-valo`, initial CHANGES_REQUESTED (one
  REQUIRED finding: canonical-file detection under-coverage), fix applied,
  re-review APPROVED. Reviewer independently reproduced tests, spot-checked
  7+5 of the released/held-back tasks against live `map.db`, and
  independently re-queried the 4 previously-missed filenames after the fix
  — zero misclassification, before or after.
- `MAP_System/scripts/validate_task_mirrors.py` passed on every release call
  in this task's own delivery.
- DEC-032 (`shared/decisions.md`) is the command-center approval evidence
  `pre_dispatch_policy.py` required before a core agent could execute this
  POLICY-class task at all.
- Follow-up: TASK-289 filed for the reviewer's separate RECOMMENDED, non-blocking
  finding (a stale, unrelated `task_tier` enum documented in
  `ORCHESTRATION_ENTRYPOINT_SYSTEM.md`) — out of this task's scope, not a
  release blocker.
- Emergence: `emergence/insights/INS-0053-...md` — this task's own first
  implementation reproduced the same under-coverage failure shape (a
  naming-convention heuristic silently missing real cases) that F5 itself
  was about, caught only by independent review, not self-review. Recorded
  as an open insight, not silently skipped.

## Rollback

Reversible by normal means: `classify_release()` and the two checklist sets
are additive/pure-function changes to `release_task.py` with no destructive
migration (the `release_tier`/`tier_reason` columns are additive with safe
defaults). The 61 batch-released tasks each have a real
`task_release_records` row and a generated checklist file under
`artifacts/releases/`; reverting the code does not un-release them, and
they were independently spot-checked as correctly classified, so no
rollback of the batch release is indicated.
