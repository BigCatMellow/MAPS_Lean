# Review: TASK-280 Independent Review

- task_id: TASK-280
- reviewer: codex-lab-nita
- task_owner: command-center
- submitter: codex-lab-feta
- reviewed_at: 2026-07-26
- review_claim: `REV-TASK-280-codex-lab-nita-8c502980`

## Verdict

CHANGES_REQUESTED

Two required execution paths still bypass normalized role semantics:
sanctioned task creation accepts an unknown role, and pre-dispatch policy
decisions reread the historical raw role after the runner has normalized it.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | `workflow/role_registry.yaml` defines seven stable role IDs. Every contract contains `mission`, `owns`, `may`, `must`, `must_not`, `required_input`, `required_output`, `escalate`, and `complete_when`. |
| 2 | FAIL | `validate_task_schema.py` rejects `invented-role` with the required clear diagnostic, but `map_task.py create` never calls the registry or schema validator. An isolated copied-database probe returned `{"created":"TASK-9999"}` and stored `role='invented-role'`. New task creation therefore does not reject unknown role IDs. |
| 3 | PASS | All 42 distinct historical roles currently stored in `map.db` normalize through canonical IDs or explicit compatibility aliases; none is unknown. Running the live schema validator and runner left the aggregate hash of every `tasks/TASK-*.json` unchanged (`24df067cacddc57344544662da034cbd8ecfc21cec0e0281f59ed93bfe1cf454` before and after), so compatibility loading did not rewrite mirrors. |
| 4 | FAIL | `runner.normalize_task()` keeps `role_id`, `worker_id`, `provider`, `model_tier`, and `capability_requirements` as separate fields, and the focused field-separation assertion passes. However, `evaluate_pre_dispatch()` still derives review/decision routing from raw `task["role"]`. An `auditor` task normalized to `independent-reviewer` was allowed for a tier-2 visible helper (`ALLOW_WITHIN_TIER`) and became a helper candidate, because policy did not consume `role_id`. |
| 5 | PARTIAL | The five submitted role-registry test functions and eleven existing runner regression tests pass, and the delivery note correctly states that normalization does not enforce review independence. The submitted tests do not exercise sanctioned CLI creation or a normalized historical role through the real pre-dispatch decision path, so they miss both required failures above. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/scripts/map_task.py:161` and `MAP_System/scripts/map_task.py:666` | The sanctioned creation command accepts and commits arbitrary `--role` values. The new registry is only consulted later by file schema validation, after canonical SQLite state and mirrors have already been created. The registered TASK-280 output list does not include the creation path that acceptance criterion 2 requires changing. | Through sanctioned TASK-280 rework, register the creation path, load the role registry before the insert, and reject an unknown role with a clear nonzero diagnostic and no database/event/mirror mutation. Add a scratch-database regression test for both rejection and a valid canonical/compatibility value. |
| REQUIRED | `MAP_System/graph/runner.py:382`, `MAP_System/scripts/pre_dispatch_policy.py:167`, and `MAP_System/scripts/pre_dispatch_policy.py:181` | Runner normalization is not authoritative for runner decisions. `evaluate_tasks()` passes a normalized task into pre-dispatch policy, but `task_text()`, `is_final_review()`, and `is_final_decision()` still inspect raw `role`. Consequently, historical aliases can receive different policy decisions from their normalized canonical role. | Make runner/pre-dispatch decisions consume `role_id` (with one explicit normalization boundary for non-runner callers) instead of role keyword fragments. Preserve worker/provider/model/capability fields independently. Add routing tests proving historical aliases and their canonical IDs receive the same decision, including `auditor -> independent-reviewer`. Register any additionally changed output path before editing. |
| REQUIRED | `MAP_System/tests/test_role_registry.py` | The focused tests assert helper classification metadata on a directly normalized dictionary, but do not cover the sanctioned creator or the actual policy decision that follows normalization. The file is also not registered in `scripts/run_tests.sh`; the project venv has no `pytest`, and direct execution currently runs zero tests because the file has no `main()`. | Add executable, registered coverage for unknown-role creation rejection, no-mutation failure behavior, historical mirror preservation, and canonical-versus-compatibility routing parity. Use the repository's available test harness or supply a runnable `main()` consistent with existing MAP tests. |

## Files Reviewed

- `MAP_System/tasks/TASK-280.json`
- `MAP_System/events/events.jsonl` (TASK-280 `SUBMISSION` at `2026-07-26T19:51:42Z`)
- `MAP_System/artifacts/tests/task280-role-registry-delivery-note.md`
- `MAP_System/graph/runner.py`
- `MAP_System/notes/role-contracts.md`
- `MAP_System/scripts/validate_task_schema.py`
- `MAP_System/tests/test_role_registry.py`
- `MAP_System/workflow/role_registry.yaml`
- `MAP_System/scripts/map_task.py` (sanctioned creation path required by criterion 2)
- `MAP_System/scripts/pre_dispatch_policy.py` (policy consumer called by the runner)
- `MAP_System/artifacts/planning/roles-system-map-improvement-review.md` (TASK-277 role-semantics source)

## Verification

- `claim_review("TASK-280", "codex-lab-nita")` — PASS; atomically created `REV-TASK-280-codex-lab-nita-8c502980` before the review artifact was written.
- Manual execution of all five functions in `test_role_registry.py` with the repository on `PYTHONPATH` — PASS, 5/5.
- `python MAP_System/tests/test_validate_task_schema.py` — PASS, 9/9 including all real task files.
- `python MAP_System/scripts/validate_task_schema.py` — PASS.
- `python MAP_System/scripts/validate_task_mirrors.py --db MAP_System/map.db --root MAP_System` — PASS.
- `python MAP_System/graph/runner.py` — PASS; routed current submitted work to review and surfaced separated metadata in policy results.
- Historical role audit — PASS; 42 distinct stored role values, zero unmapped values.
- Historical mirror preservation — PASS; aggregate task-file hash was identical before and after schema validation and runner loading.
- Isolated copied-database creation probe with `--role invented-role` — FAIL as an acceptance probe: command exited successfully, emitted `{"created":"TASK-9999"}`, and stored the unknown role.
- Normalized routing probe with raw `auditor` — FAIL as an acceptance probe: `role_id=independent-reviewer`, but tier-2 helper policy returned `allow` / `ALLOW_WITHIN_TIER`.
- Existing pre-dispatch tests — PASS, 10/10.
- Existing runner task-classification, policy-gate, and helper-note tests — PASS, 11/11.

## Pre-existing Validator Drift

`scripts/run_tests.sh` confirmed the TASK-280-adjacent compile, task-mirror,
task-graph, task-schema, schema-test, decision, repair, context, risk, claim,
submission, exporter, review-gate, and other reached checks pass. It also
reported two unrelated live baselines:

- `validate_research_artifacts` reports eight missing template fragments in
  `artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md`.
- `validate_shared_state_tasks` reports `TASK-274` as `READY` in
  `shared/current-state.md` while current SQLite state is `APPROVED`.

Neither path is a TASK-280 registered output, neither failure was introduced by
the role-registry changes, and neither is used to block this verdict. The
project venv also lacks `pytest`; this is a tool-availability limitation, not a
TASK-280 regression. The submitted test functions were therefore invoked
directly with available Python tooling.

## Forbidden Changes Check

- PASS: The reviewer did not edit any TASK-280 implementation output.
- PASS: All mutation probes used an isolated copied database and temporary
  export/event paths; canonical task state and historical role strings were not
  rewritten by those probes.
- PASS: Role normalization was not treated as proof of review independence.
  This review was claimed by `codex-lab-nita`, who did not implement or submit
  TASK-280.
- PASS: No helpers were spawned and no unrelated work was taken.

