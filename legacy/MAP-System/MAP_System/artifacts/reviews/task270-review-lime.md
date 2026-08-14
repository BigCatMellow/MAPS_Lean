# Review: TASK-270

task_id: TASK-270
reviewer: codex-lab-lime
task_owner: claude-lab-gabi
review_date: 2026-07-22

## Verdict

CHANGES_REQUESTED

The live unregistered-reviewer failure is fixed, and the three added regression
tests kill their intended basic mutants. Approval is blocked because the new
exception classifier still flattens a different reachable uniqueness failure
into `False`, contrary to the central acceptance criterion. The task record
also omits its changed test file from `output_paths`, and the updated contract
documentation contradicts the function's actual raising and unknown-task
behavior.

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | An unregistered reviewer can claim through registration consistent with `map_task.py`. | PASS | The review claim for `codex-lab-lime` succeeded on the live database. The focused temp-database test also creates the agent as `core` / `available` and opens the claim. |
| 2 | Only the open-claim uniqueness violation becomes `False`; other integrity failures propagate. | FAIL | `except sqlite3.IntegrityError` tests only whether the message contains `unique`. A collision on the `reviews.review_id` primary key produces `UNIQUE constraint failed: reviews.review_id` and is incorrectly returned as `False`, even with no open review claim. |
| 3 | Already-claimed, self-review, non-SUBMITTED, and unknown-task cases remain `False`. | PASS | Existing and added focused tests cover these branches and pass. |
| 4 | Focused tests cover the required behaviors and unexpected integrity failures. | PARTIAL | Eleven tests pass and all three new tests kill targeted basic mutants. No test distinguishes the partial-index open-claim violation from the reachable `review_id` uniqueness violation. |
| 5 | Review guidance no longer equates every `False` with already claimed. | PARTIAL | The guide now instructs reviewers to inspect the open claim, but says there are "exactly three" false cases while unknown task is a separate false branch, and the function docstring still says "never raises" despite the new propagation contract. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/db/claims.py` | The `"unique" in str(exc).lower()` classifier does not identify the open-claim partial-index constraint. It also matches the `reviews.review_id` primary-key constraint. A forced UUID collision with a completed review reproduced `False` while `get_open_review_claim` was empty. This preserves the same silent stand-down failure for a different integrity error. | Determine the semantic condition, not merely the error class: after an insert integrity failure, return `False` only if an open review claim for the task actually exists; otherwise re-raise. An exact, well-guarded identification of `reviews.task_id` would also satisfy the task, but querying the claimed invariant avoids dependence on SQLite message text. Add a regression test for a completed-row `review_id` collision that must raise. |
| REQUIRED | `MAP_System/db/claims.py`, `MAP_System/notes/review-guide.md` | The function docstring says `False (never raises)`, which contradicts the new requirement to propagate unexpected integrity failures. The guide says there are "exactly three" false cases but omits the function's distinct unknown-task branch, even though the task acceptance criteria explicitly preserve it. | Update the function and guide contracts to state all false-return cases and that unrelated integrity failures raise. Keep the `get_open_review_claim` recovery guidance. |
| REQUIRED | `MAP_System/tasks/TASK-270.json` / SQLite task outputs | `MAP_System/tests/test_review_claims.py` was changed and is part of the submitted scope, but it is absent from the task's registered `output_paths`. That makes the durable ownership/scope record disagree with the implementation and the review packet. | During rework, register `MAP_System/tests/test_review_claims.py` as a task output and export/validate the mirrors before resubmission. |

## Forbidden Changes Check

| Boundary | Status |
|---|---|
| Preserve refusal for self-review, non-SUBMITTED, unknown-task, and genuinely claimed reviews. | NOT BROKEN in the submitted implementation. |
| Do not weaken the one-open-review invariant. | NOT BROKEN; the partial unique index still arbitrates concurrent claims. |
| Do not silently swallow unexpected integrity failures. | BROKEN for non-open-claim uniqueness failures, as reproduced above. |
| Do not expand review claims into a new authority or network surface. | NOT BROKEN. |

## Files Reviewed

- `MAP_System/db/claims.py`
- `MAP_System/notes/review-guide.md`
- `MAP_System/tests/test_review_claims.py`
- `MAP_System/scripts/map_task.py`
- `MAP_System/migration/schema.sql`
- `MAP_System/tasks/TASK-270.json`

## Verification

- Live `claim_review("TASK-270", "codex-lab-lime")` - PASS; created open review claim `REV-TASK-270-codex-lab-lime-7708d2f0`.
- `MAP_System/.venv/bin/python MAP_System/tests/test_review_claims.py` - PASS, 11/11.
- Targeted registration-removal mutant - killed by `test_unregistered_reviewer_can_claim_an_open_review` with a foreign-key failure.
- Targeted re-raise-all-uniqueness mutant - killed by `test_second_claimant_is_still_refused_after_auto_registration`.
- Targeted swallow-all-integrity mutant - killed by `test_non_uniqueness_integrity_error_is_not_swallowed`.
- Forced `uuid4()` collision with a completed `reviews.review_id` and no open claim - FAIL: current implementation returned `False`; the required contract is to propagate the integrity failure.
- `MAP_System/.venv/bin/python -m py_compile MAP_System/db/claims.py MAP_System/tests/test_review_claims.py` - PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` - PASS before verdict transition.
- `MAP_System/scripts/run_tests.sh` - 72 pass / 2 fail. The failures are the established unrelated `validate_events` warning and its Layer-1 aggregate; focused TASK-270 tests pass.

## Notes

Auto-registering an arbitrary non-empty reviewer as `core` is an existing
`map_task.py ensure_agent` convention and is explicitly required by this task,
so this review does not block on changing that authority model. A future
identity-contract task may reasonably centralize registration and reject blank
or malformed IDs, but that is outside this corrective scope.

The `get_open_review_claim` guidance is operationally useful. It would be even
more actionable with an import/call snippet, but that is not required once the
contract contradictions above are corrected.
