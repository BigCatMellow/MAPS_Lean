# Final Re-review: TASK-284 Source-Aware Fingerprint Pilot

- task_id: TASK-284
- reviewer: codex-lab-romi
- task_owner: command-center
- review_claim: REV-TASK-284-codex-lab-romi-51f832fa
- reviewed_at: 2026-07-26
- prior_reviews:
  - MAP_System/artifacts/reviews/task284-review-romi.md
  - MAP_System/artifacts/reviews/task284-rereview-romi.md

## Verdict

APPROVED

The final rework closes the remaining three-source contradiction gap. Candidate
selection uses the union of task JSON, read-only SQLite, and task-graph
identities. Whenever any source says `RELEASED`, all three statuses are
compared before eligibility. Each single-source mismatch is recorded with a
typed, source-specific contradiction, excluded from searchable records, and
causes search to abstain. Consistently non-released tasks remain ordinary
noncandidates.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | Searchable fingerprints require task JSON, read-only SQLite, and task graph to agree on `RELEASED`; eligible records retain released-task, submission, review, decision, and primary-source backlinks. |
| 2 | PASS | Frozen holdout SHA-256 remains `73ce9fbaf346c906cfadb208c1b6f3bff15a83afb6c4830961191089868404b4`; task recall, primary-source recall, negative abstention, and byte reduction are separate. |
| 3 | PASS | Returned results require raw evidence. Missing sources remain marked. Independent task-JSON, SQLite, and task-graph mismatch fixtures each produce typed `excluded_records`, zero searchable records, and abstention. |
| 4 | PASS | Promotion thresholds remain predeclared; `production_routing_enabled` remains false; the unchanged failed retrieval scores authorize no production routing. |
| 5 | PASS | Five focused and 22 adjacent tests pass. The report directly compares TASK-284 with TASK-256 while distinguishing corpora and clarifying that only the holdout is frozen. |

## Findings

No `BLOCKER` or `REQUIRED` findings remain.

## Files Reviewed

- `MAP_System/tasks/TASK-284.json`
- `MAP_System/artifacts/experiments/task284-source-aware-fingerprint-pilot.md`
- `MAP_System/scripts/task_fingerprint_production_pilot.py`
- `MAP_System/tests/test_task_fingerprint_production_pilot.py`
- `MAP_System/artifacts/reviews/task284-review-romi.md`
- `MAP_System/artifacts/reviews/task284-rereview-romi.md`

## Forbidden Changes Check

- PASS: The submission event names exactly the three registered outputs.
- PASS: No startup, runner-routing, Command Center, task-authority, or
  production integration was enabled.
- PASS: The projection remains `offline_disposable_projection` with
  `production_routing_enabled: false`.
- PASS: Returned results retain backlinks and
  `raw_evidence_required: true`.
- PASS: Contradicted release candidates cannot enter searchable records.
- PASS: Retrieval scores were not tuned, promoted, or represented as
  production readiness.
- PASS: This review did not edit implementation.

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_task_fingerprint_production_pilot.py` — 5/5 pass.
- `python -m unittest test_task_fingerprint_pilot test_task_fingerprint_holdout test_task_fingerprint_source_holdout` — 22/22 pass.
- `python -m py_compile` on implementation and focused test — pass.
- Independent task JSON mismatch — source `task_json`, actual
  `CHANGES_REQUESTED`, one structured excluded record, zero searchable
  records, abstention.
- Independent SQLite mismatch — source `sqlite`, actual
  `CHANGES_REQUESTED`, one structured excluded record, zero searchable
  records, abstention.
- Independent task-graph mismatch — source `task_graph`, actual
  `CHANGES_REQUESTED`, one structured excluded record, zero searchable
  records, abstention.
- Consistently non-released control — zero searchable records and zero
  contradiction exclusions.
- Rebuilt report — holdout hash unchanged; task recall 33.33%, source recall
  33.33%, negative abstention 0%, point-in-time byte reduction 92.27%.
- `validate_task_schema.py` — pass.
- `validate_task_mirrors.py --db MAP_System/map.db --root MAP_System` — pass.
- `validate_task_graph.py` — pass.

## Notes

Approval accepts a correctly bounded negative experiment, not a production
retrieval system. The report's failed thresholds and explicit decision still
prohibit promotion or default routing.
