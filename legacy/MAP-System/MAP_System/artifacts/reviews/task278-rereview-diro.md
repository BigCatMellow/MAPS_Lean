# Review: TASK-278 Rework Round 2

- task_id: TASK-278
- reviewer: codex-lab-diro
- task_owner: command-center
- canonical_submission_author: claude-lab-venu
- review_date: 2026-07-27
- review_claim: `REV-TASK-278-codex-lab-diro-332583c5`

## Verdict

APPROVED

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Canonical submission author survives lifecycle and owner drift | PASS | Authorship remains transactional with submission, persists through rejection/rework, changes only on successful resubmission, and now records `claude-lab-venu` with submission count 2 for the live task. |
| 2 | Claim and terminal review gates use the actual submission author | PASS | Claim and approve/reject paths use `require_independent_reviewer()`. Rework now skips the mutable artifact heuristic whenever canonical DB/task/reviewer inputs are available, so canonical authorship is the sole production authority. |
| 3 | Unknown legacy authorship fails closed | PASS | Missing canonical authorship still raises the explicit unknown-author diagnostic at claim and terminal verdict gates; offline artifact validation retains its legacy heuristic without substituting it for production authority. |
| 4 | Duplicate-review arbitration remains atomic | PASS | Existing partial unique index is unchanged; 12 review-claim regressions and the focused claim/verdict race cases pass. |
| 5 | Focused validators and delivery evidence pass | PASS | Seven focused suites plus graph, mirror, and schema validators reproduced green. The delivery note documents compatibility, rollback, residual risk, original review, and round-2 correction. |

## Prior Required Correction Check

| Required correction | Result | Evidence |
|---|---|---|
| Make reviewer-authored `task_owner` text non-authoritative when canonical inputs exist | PASS | `validate_review.py:143-174` runs `check_self_review()` only when the canonical check cannot run. With DB/task/reviewer present, only `require_independent_reviewer()` can add the self-review finding. |
| Add a false-block regression and preserve the inverse self-review guard | PASS | `test_canonical_independence_overrides_artifact_owner_text_false_block` proves an independent reviewer passes when artifact owner text equals the reviewer, the canonical author remains blocked when artifact text does not name them, and the legacy offline heuristic still fires. |
| Correct the submission crash-window docstring | PASS | `claims.py:248-256` now states that authorship commits with the status transition and only the later event append can be lost. |

## Forbidden Changes Check

- PASS: The rework is confined to the reviewed TASK-278 implementation, regression test, and delivery note.
- PASS: Canonical authorship, atomic review arbitration, conservative legacy handling, and event ordering were not weakened.
- PASS: No destructive, network-facing, or external write-capable surface was introduced.

## Files Reviewed

- `MAP_System/tasks/TASK-278.json`
- `MAP_System/artifacts/tests/task278-review-authorship-delivery-note.md`
- `MAP_System/artifacts/reviews/task278-independent-review-diro.md`
- `MAP_System/db/claims.py`
- `MAP_System/db/review_authorship.py`
- `MAP_System/migration/schema.sql`
- `MAP_System/scripts/map_task.py`
- `MAP_System/scripts/validate_review.py`
- `MAP_System/tests/test_review_authorship.py`
- `MAP_System/tests/test_review_claims.py`
- `MAP_System/tests/test_review_gate.py`
- `MAP_System/tests/test_submission_event.py`
- `MAP_System/tests/test_task268_lifecycle.py`
- `MAP_System/tests/test_reassign_owner.py`
- `MAP_System/tests/test_no_self_review.py`

## Scope Check

| Changed file | In scope? |
|---|---|
| `MAP_System/scripts/validate_review.py` | YES — exact REQUIRED finding |
| `MAP_System/tests/test_review_authorship.py` | YES — required false-block/inverse regression |
| `MAP_System/db/claims.py` | YES — recommended documentation correction only |
| `MAP_System/artifacts/tests/task278-review-authorship-delivery-note.md` | YES — rework evidence |

## Findings

No BLOCKER or REQUIRED findings.

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_review_authorship.py` — PASS, 8/8.
- `MAP_System/.venv/bin/python MAP_System/tests/test_submission_event.py` — PASS, 7/7.
- `MAP_System/.venv/bin/python MAP_System/tests/test_task268_lifecycle.py` — PASS, 3/3.
- `MAP_System/.venv/bin/python MAP_System/tests/test_review_claims.py` — PASS, 12/12.
- `MAP_System/.venv/bin/python MAP_System/tests/test_review_gate.py` — PASS, 3/3.
- `MAP_System/.venv/bin/python MAP_System/tests/test_reassign_owner.py` — PASS, 5/5.
- `MAP_System/.venv/bin/python MAP_System/tests/test_no_self_review.py` — PASS, 2/2.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_graph.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_schema.py` — PASS.

## Risk Identification

| Risk | Severity | Recommended action |
|---|---|---|
| Historical submissions without canonical authorship remain unreviewable | LOW / intentional | Preserve the documented fail-closed migration or operator-disposition rule. |
| Post-commit event append can fail after canonical submission commits | LOW / pre-existing contract | Retain TASK-274 reconciliation handling; do not weaken transactional authorship. |

## Notes

The prior REQUIRED and RECOMMENDED findings are closed. TASK-278 now satisfies its acceptance criteria without conflating mutable owner prose, canonical author identity, or duplicate-review arbitration.
