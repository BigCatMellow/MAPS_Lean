# Review: TASK-280 Rework Round 2

- task_id: TASK-280
- reviewer: codex-lab-diro
- task_owner: command-center
- canonical_submission_author: claude-lab-venu
- review_date: 2026-07-27
- review_claim: `REV-TASK-280-codex-lab-diro-3e31733f`

## Verdict

CHANGES_REQUESTED

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | `workflow/role_registry.yaml` defines seven stable IDs; every role contains all nine required contract fields. |
| 2 | PASS | `map_task.py create` normalizes the supplied role before opening its write transaction and raises a clear unknown-role diagnostic. The isolated no-mutation regression passes under the project venv. |
| 3 | PASS | Historical values resolve only through explicit compatibility aliases, `normalize_task()` copies rather than mutates its input, and current task schema validation passes without rewriting stored roles. |
| 4 | PASS | Runner-loaded tasks carry normalized `role_id`; pre-dispatch text, final-review/final-decision checks, and helper classification consume that value with an explicit fallback boundary. The `auditor` alias and canonical `independent-reviewer` both reject tier-2 final-review routing. Worker, provider, model tier, and capabilities remain separate. |
| 5 | FAIL | The focused file passes 7/7 only under `MAP_System/.venv/bin/python`. TASK-280 added it to `run_tests.sh` as bare `python3 MAP_System/tests/test_role_registry.py`; that exact registered command fails before running any test because importing `runner.py` requires `langgraph`, which bare Python cannot import. The prior review also required positive sanctioned-creation coverage for canonical/compatibility roles, but the current test exercises only the unknown-role rejection CLI path. |

## Prior Required Correction Check

| Prior correction | Result | Evidence |
|---|---|---|
| Reject unknown roles before sanctioned creation mutates state | PASS | `map_task.py:163-171` validates before opening the transaction; scratch test confirms no task/event rows. |
| Route from normalized role semantics | PASS | Direct historical/canonical policy probe returns identical `reject / REJECT_HELPER_FINAL_REVIEW`; affected policy suites pass. |
| Add runnable, registered coverage for creator and routing behavior | FAIL | The registered command fails with `ModuleNotFoundError: No module named 'langgraph'`, so it is not runnable in the repository harness. The requested positive sanctioned-create regression for a valid canonical/compatibility role is also missing. |

## Forbidden Changes Check

- PASS: TASK-280 owns the changed `map_task.py` path after TASK-278 became terminal.
- PASS: `pre_dispatch_policy.py` remains registered only to active TASK-283 and was not re-registered to TASK-280.
- PASS: No implementation files were edited during review.
- PASS: Role normalization was not treated as review-independence authority.

## Files Reviewed

- `MAP_System/tasks/TASK-280.json`
- `MAP_System/artifacts/tests/task280-role-registry-delivery-note.md`
- `MAP_System/artifacts/reviews/task280-independent-review-nita.md`
- `MAP_System/graph/runner.py`
- `MAP_System/notes/role-contracts.md`
- `MAP_System/scripts/map_task.py`
- `MAP_System/scripts/pre_dispatch_policy.py`
- `MAP_System/scripts/run_tests.sh`
- `MAP_System/scripts/validate_task_schema.py`
- `MAP_System/tests/test_role_registry.py`
- `MAP_System/tests/test_pre_dispatch_policy.py`
- `MAP_System/tests/test_pre_dispatch_gate_inputs.py`
- `MAP_System/tests/test_capability_whitelist.py`
- `MAP_System/workflow/role_registry.yaml`
- `MAP_System/repairs/REPAIR-0009-task280-output-path-defer.md`

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/scripts/run_tests.sh:33`, `MAP_System/tests/test_role_registry.py:15` | TASK-280 newly registers `role_registry_test` with bare `python3`, but the test imports `MAP_System.graph.runner`, whose unconditional `langgraph` import is unavailable to that interpreter. Reproduction of the exact registered command fails with `ModuleNotFoundError` before any of the seven tests execute. Calling this a pre-existing unrelated failure is inaccurate: the failing registration line and test are TASK-280 outputs, and the prior review explicitly required runnable registered coverage. | Make the registered command pass in the repository's standard harness. The narrow fix is to run this check with `MAP_System/.venv/bin/python`, consistent with other runner-dependent checks in the same script; alternatively decouple the testable normalization boundary from the LangGraph import. Re-run the exact registered command. |
| REQUIRED | `MAP_System/tests/test_role_registry.py:63-81` | The prior review required a scratch-database sanctioned-creation regression for both rejection and a valid canonical/compatibility role. The current CLI test covers only rejection/no-mutation. In-memory normalization assertions do not prove that the sanctioned creator accepts and persists a valid role without an over-strict gate. | Add positive scratch-DB CLI coverage for at least one stable role ID and one explicit compatibility alias, asserting successful creation and preserved stored role text. |
| RECOMMENDED | `MAP_System/notes/role-contracts.md:29-30` | The note says the implementation is bounded to six registered outputs, while the current task has eight after `map_task.py` was re-registered. | Replace the stale count with the current count or avoid embedding a mutable count. |

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_role_registry.py` — PASS, 7/7.
- `python3 MAP_System/tests/test_role_registry.py` — FAIL before test execution: missing `langgraph`.
- `MAP_System/.venv/bin/python MAP_System/tests/test_pre_dispatch_policy.py` — PASS, 5/5.
- `MAP_System/.venv/bin/python MAP_System/tests/test_pre_dispatch_gate_inputs.py` — PASS, 15/15.
- `MAP_System/.venv/bin/python MAP_System/tests/test_capability_whitelist.py` — PASS, 5/5.
- Direct `auditor` versus `independent-reviewer` tier-2 policy probe — PASS; both reject with `REJECT_HELPER_FINAL_REVIEW`.
- Python compilation under the project venv — PASS for affected modules.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_graph.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_schema.py` — PASS.

## Risks Identified

- Durable TASK-280 state is already at attempt 3 of 3. After this verdict, ordinary re-claim will be blocked by the attempt ceiling; command-center disposition is required before another implementation attempt.
- `pre_dispatch_policy.py` remains owned by TASK-283. Its later edits must retain the now-correct role parity behavior.

## Notes

The implementation behavior behind the first two prior findings is sound. The remaining work is bounded to test-harness reliability, the explicitly requested positive creator regressions, and one stale documentation count.
