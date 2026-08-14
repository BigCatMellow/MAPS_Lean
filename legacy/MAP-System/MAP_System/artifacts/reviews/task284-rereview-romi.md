# Re-review: TASK-284 Source-Aware Fingerprint Pilot

- task_id: TASK-284
- reviewer: codex-lab-romi
- task_owner: command-center
- review_claim: REV-TASK-284-codex-lab-romi-fae3c535
- reviewed_at: 2026-07-26
- prior_review: MAP_System/artifacts/reviews/task284-review-romi.md

## Verdict

CHANGES_REQUESTED

The rework correctly detects and excludes SQLite and task-graph release-state
conflicts, preserves offline/noncanonical routing, and clarifies that only the
holdout is frozen. One required three-source case is still silently discarded:
when task JSON is non-`RELEASED` while SQLite and task graph are `RELEASED`,
`build_index()` exits through its initial `continue` before `release_state()`.
The record is unsearchable, but `excluded_records` contains no structured
contradiction, contrary to the stated boundary and acceptance requirement.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PARTIAL | Eligible records now require agreement among task JSON, read-only SQLite, and task graph and retain typed backlinks. A non-`RELEASED` task JSON is silently skipped before the three-way comparison, so not every disagreement is recorded. |
| 2 | PASS | Holdout SHA-256 remains `73ce9fbaf346c906cfadb208c1b6f3bff15a83afb6c4830961191089868404b4`; task recall, source recall, abstention, and point-in-time byte reduction remain separate. |
| 3 | FAIL | Graph and SQLite `CHANGES_REQUESTED` conflicts produce structured `excluded_records` and abstention. Task JSON `CHANGES_REQUESTED` against SQLite/graph `RELEASED` produces `records: []`, `abstained: true`, but `excluded_records: []`, so the contradictory state is not clearly marked. |
| 4 | PASS | `production_routing_enabled` remains false; thresholds and failure criteria remain explicit; unchanged scores fail promotion gates. |
| 5 | PASS | Five focused and 22 adjacent fingerprint tests pass; the artifact retains its direct, qualified TASK-256 comparison. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/scripts/task_fingerprint_production_pilot.py` | `build_index()` checks `if task.get("status") != "RELEASED": continue` before calling `release_state()`. Therefore a task JSON/SQLite/task-graph disagreement where JSON is non-released is fail-closed for retrieval but invisible in `excluded_records`. This contradicts the report's claim that missing or non-`RELEASED` status in any of the three sources is recorded as a structured contradiction. | Run the three-source release-state comparison for every candidate task represented in the authority sources, record the task JSON mismatch in `excluded_records`, retain exclusion/abstention, and extend the focused regression to cover task JSON, SQLite, and graph conflicts independently. |

## Files Reviewed

- `MAP_System/tasks/TASK-284.json`
- `MAP_System/artifacts/experiments/task284-source-aware-fingerprint-pilot.md`
- `MAP_System/scripts/task_fingerprint_production_pilot.py`
- `MAP_System/tests/test_task_fingerprint_production_pilot.py`
- `MAP_System/artifacts/reviews/task284-review-romi.md`

## Forbidden Changes Check

- PASS: Only the three registered implementation outputs were submitted for
  re-review.
- PASS: No startup, routing, Command Center, task-authority, or production
  integration was enabled.
- PASS: Searchable results retain backlinks and
  `raw_evidence_required: true`.
- PASS: Contradicted graph/SQLite records are excluded and cannot be returned.
- PASS: Retrieval scores were not tuned or promoted.
- PASS: This re-review did not edit implementation.

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_task_fingerprint_production_pilot.py` — 5/5 pass.
- `python -m unittest test_task_fingerprint_pilot test_task_fingerprint_holdout test_task_fingerprint_source_holdout` — 22/22 pass.
- `python -m py_compile` on the implementation and focused test — pass.
- Independent graph conflict fixture — structured mismatch, excluded record, and abstention pass.
- Independent SQLite conflict fixture — structured mismatch, excluded record, and abstention pass; SQLite is opened with `mode=ro`.
- Independent task JSON conflict fixture — record is excluded from search and search abstains, but `excluded_records` is empty.
- Rebuilt report — task recall 33.33%, source recall 33.33%, negative abstention 0%, point-in-time byte reduction 92.26%; holdout hash unchanged.
- `validate_task_schema.py` — pass.
- `validate_task_mirrors.py --db MAP_System/map.db --root MAP_System` — pass.
- `validate_task_graph.py` — pass.

## Notes

The remaining fix is narrow and does not require retrieval tuning or any
production integration. Preserve the current fail-closed exclusion while
making the task-JSON disagreement visible and regression-tested.
