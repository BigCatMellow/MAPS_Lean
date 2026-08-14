# Re-review: TASK-270

task_id: TASK-270
reviewer: codex-lab-lime
task_owner: claude-lab-gabi
review_date: 2026-07-22

## Verdict

APPROVED

All three required findings from the initial review are resolved. The insert
failure path now classifies the semantic open-claim invariant rather than
SQLite error text, the primary-key collision regression is covered and
mutation-sensitive, the four-case contract is consistent in code and guidance,
and the changed test file is registered in durable task scope. No `BLOCKER` or
`REQUIRED` finding remains.

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Unregistered reviewer can claim through consistent agent registration. | PASS | Live TASK-270 claim succeeded for the reviewer; focused unregistered-agent test passes and its registration-removal mutant fails with a foreign-key error. |
| 2 | Only an actual open-claim conflict returns `False`; other integrity failures raise. | PASS | The exception path queries `reviews` for `task_id` with `completed_at IS NULL`. Synthetic non-uniqueness and forced `review_id` primary-key collisions both raise when no open claim exists. |
| 3 | Already-claimed, self-review, non-SUBMITTED, and unknown-task cases remain `False`. | PASS | Focused suite covers all four cases; the second-claimant test kills a re-raise-all mutant. |
| 4 | Focused tests cover the required behaviors and are mutation-sensitive. | PASS | 12/12 focused tests pass. Registration removal, swallow-all, re-raise-all, and the rejected text-classifier mutants are each killed by the intended test. |
| 5 | Review guidance does not equate every `False` with already claimed. | PASS | Guide enumerates four false cases, states other integrity failures raise, and directs ambiguous queue cases to `get_open_review_claim`. |

## Findings

No `BLOCKER` or `REQUIRED` findings.

## Forbidden Changes Check

| Boundary | Status |
|---|---|
| Preserve refusal for self-review, non-SUBMITTED, unknown-task, and genuinely claimed reviews. | NOT BROKEN. |
| Preserve the one-open-review invariant. | NOT BROKEN; the partial unique index remains authoritative and the post-failure query observes it. |
| Do not silently swallow unexpected integrity failures. | NOT BROKEN; unexpected failures re-raise when no open claim exists. |
| Do not expand review claims into a network, write-external, or alternate authority surface. | NOT BROKEN. |

## Files Reviewed

- `MAP_System/db/claims.py`
- `MAP_System/notes/review-guide.md`
- `MAP_System/tests/test_review_claims.py`
- `MAP_System/scripts/map_task.py`
- `MAP_System/migration/schema.sql`
- `MAP_System/tasks/TASK-270.json`
- `MAP_System/workflow/task_graph.json`

## Verification

- Live `claim_review("TASK-270", "codex-lab-lime")` - PASS; open claim created for this re-review.
- `MAP_System/.venv/bin/python MAP_System/tests/test_review_claims.py` - PASS, 12/12.
- Rejected `"unique"` text-classifier mutant - killed by `test_review_id_primary_key_collision_raises_not_false`.
- Swallow-all-integrity mutant - killed by `test_non_uniqueness_integrity_error_is_not_swallowed`.
- Re-raise-all-integrity mutant - killed by `test_second_claimant_is_still_refused_after_auto_registration`.
- Registration-removal mutant - killed by `test_unregistered_reviewer_can_claim_an_open_review`.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` - PASS.
- `MAP_System/scripts/run_tests.sh` - 72 pass / 2 fail, matching the established baseline. Both failures remain the unrelated non-canonical event at `events.jsonl:2145` and its Layer-1 aggregate.

## Notes

The task remains bounded to the existing `map_task.py` identity-registration
convention. Potential future tightening of reviewer-ID validation is outside
this task and is not required for approval.
