# Review: TASK-278 Durable Submission Authorship

- task_id: TASK-278
- reviewer: codex-lab-diro
- task_owner: command-center
- canonical_submission_author: claude-lab-nora
- review_date: 2026-07-27
- review_claim: `REV-TASK-278-codex-lab-diro-656d7a0a`

## Verdict

CHANGES_REQUESTED

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | `release_task(..., status="SUBMITTED")` records authorship in the same SQLite transaction as the guarded status transition. Rejection and rework leave that row intact; resubmission replaces the current author and increments `submission_count`. The focused lifecycle test reproduced these behaviors. |
| 2 | PARTIAL | `claim_review()` and the terminal approve/reject transaction compare the reviewer with canonical SQLite authorship and correctly survive owner drift. However, `validate_review.py` still treats reviewer-authored `task_owner` text as a blocking self-review authority, so canonical independence does not exclusively drive the approval path. |
| 3 | PASS | Missing table/row state returns unknown authorship; claim and terminal verdict gates fail closed with an explicit migration/operator-disposition diagnostic. No owner or artifact value is guessed as the author. |
| 4 | PASS | The partial unique open-review index is unchanged. Reviewer-claim and terminal-verdict race tests each reproduced exactly one winner, and the existing 12 review-claim regressions remain green. |
| 5 | PASS | All submitted focused suites and the task graph, mirror, and schema validators reproduced green. The delivery note records compatibility, rollback, unrelated full-run failures, and residual migration/event risk. |

## Forbidden Changes Check

- PASS: Review work changed only this review artifact plus the required SQLite review claim/verdict records.
- PASS: No submitted implementation, task scope, shared state, decision, or release artifact was edited.
- PASS: No destructive action or network/write-capable component is introduced by TASK-278, so the separate security second pass is not required.

## Files Reviewed

- `MAP_System/tasks/TASK-278.json`
- `MAP_System/artifacts/tests/task278-review-authorship-delivery-note.md`
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
- `MAP_System/artifacts/planning/roles-system-map-improvement-review.md`

## Scope Check

| Changed file | In scope? |
|---|---|
| `MAP_System/db/claims.py` | YES — submission and review claim transitions |
| `MAP_System/db/review_authorship.py` | YES — canonical author authority |
| `MAP_System/migration/schema.sql` | YES — additive authorship storage |
| `MAP_System/scripts/map_task.py` | YES — terminal verdict enforcement |
| `MAP_System/scripts/validate_review.py` | YES — approval-time review validation |
| Focused test files and delivery note | YES — required regression and delivery evidence |

## Findings

| Severity | File | Section | Finding | Required action |
|---|---|---|---|---|
| REQUIRED | `MAP_System/scripts/validate_review.py:52-81,143-146` | Artifact self-review check | `validate()` still parses `reviewer` and `task_owner` from reviewer-authored text and appends a blocking `SELF_REVIEW` issue when those values match or merely contain one another. Reproduction against live TASK-278 used reviewer `codex-lab-diro`, canonical author `claude-lab-nora`, and artifact text `task_owner: codex-lab-diro`; validation returned `SELF_REVIEW` despite canonical independence. Since `map_task.py approve` treats every validator issue as fatal, artifact text remains a review authority. This conflicts with the criterion that gates be keyed to canonical authorship without relying on reviewer-authored text, the TASK-277 P0 design, and the delivery note's statement that `task_owner` prose is advisory only. The submitted test covers only an unrelated artifact owner and therefore misses the false-block case. | Remove the legacy artifact-owner check from the authoritative validation result when canonical `--db` and `--reviewer` inputs are present, or otherwise make it explicitly non-blocking. Add a regression proving an independent canonical reviewer is accepted even when artifact `task_owner` text matches or contains the reviewer ID, while the canonical author remains blocked. |
| RECOMMENDED | `MAP_System/db/claims.py:248-254` | `submit_task()` docstring | The docstring says a post-transition crash “may lose authorship evidence,” but authorship is committed atomically inside `release_task()` before the fallible JSONL append. The delivery note and implementation correctly describe only event reconciliation debt after that commit. | Change the sentence to say a crash may lose the post-commit event append, not canonical authorship evidence. |

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_review_authorship.py` — PASS, 7/7.
- `MAP_System/.venv/bin/python MAP_System/tests/test_submission_event.py` — PASS, 7/7.
- `MAP_System/.venv/bin/python MAP_System/tests/test_task268_lifecycle.py` — PASS, 3/3.
- `MAP_System/.venv/bin/python MAP_System/tests/test_review_claims.py` — PASS, 12/12.
- `MAP_System/.venv/bin/python MAP_System/tests/test_review_gate.py` — PASS, 3/3.
- `MAP_System/.venv/bin/python MAP_System/tests/test_reassign_owner.py` — PASS, 5/5.
- `MAP_System/.venv/bin/python MAP_System/tests/test_no_self_review.py` — PASS, 2/2.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_graph.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_schema.py` — PASS.
- Direct `validate()` false-block reproduction — FAIL as expected; returned `SELF_REVIEW` for canonical-independent `codex-lab-diro` solely from artifact `task_owner` text.

## Risks Identified

- Until the REQUIRED finding is fixed, the new canonical identity closes the self-approval hole but leaves an avoidable denial-of-review path controlled by mutable artifact prose.
- Historical open submissions remain deliberately blocked until authorship is explicitly established or the operator disposes them; this is a documented conservative policy, not a review defect.

## Notes

The SQLite author record, claim gate, terminal verdict guard, conservative legacy behavior, and duplicate-review arbitration are otherwise sound. One narrow validator change and regression should be sufficient for re-review.
