# Review: TASK-284 Source-Aware Fingerprint Pilot

- task_id: TASK-284
- reviewer: codex-lab-romi
- task_owner: command-center
- review_claim: REV-TASK-284-codex-lab-romi-6f35a517
- reviewed_at: 2026-07-26

## Verdict

CHANGES_REQUESTED

The offline/noncanonical boundary, backlinks, raw-evidence marker, frozen
holdout, separate metrics, and no-promotion result are present. One required
acceptance boundary is not implemented: contradictory source state is neither
detected nor identified. The field named
`missing_or_contradictory_sources` contains only missing output paths, while
`build_index()` trusts a task JSON `RELEASED` value without comparing another
canonical/mirrored state source.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PARTIAL | `build_index()` limits records to task JSON marked `RELEASED` and attaches released-task, output/primary, submission, review, and decision backlinks. It does not validate that the JSON release state agrees with canonical/mirrored task state. |
| 2 | PASS | The frozen holdout hash reproduced as `73ce9fbaf346c906cfadb208c1b6f3bff15a83afb6c4830961191089868404b4`; task recall, primary-source recall, negative abstention, and byte reduction are reported separately. |
| 3 | FAIL | Returned results set `raw_evidence_required: true`, and missing output paths are marked. Contradictory state is not detected: a fixture with task JSON `RELEASED` and task-graph status `CHANGES_REQUESTED` was indexed as released with an empty contradiction marker. |
| 4 | PASS | The report predeclares task recall >= 0.90, source recall >= 0.80, abstention == 1.00, and independent review; the projection always sets `production_routing_enabled` false. Reproduced scores fail three thresholds, so no promotion is authorized. |
| 5 | PASS | All four focused deterministic tests pass. The report directly compares the result with TASK-256's 100% task recall@6 and 68.75% source recall while warning that the corpora differ. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/scripts/task_fingerprint_production_pilot.py` | `build_index()` derives `missing_or_contradictory_sources` solely from rows whose file state is `missing`. It accepts the task JSON status as sufficient proof of release and has no contradictory-state input or comparison. A deliberately contradictory task JSON/task-graph fixture was indexed as `RELEASED`, with `missing_or_contradictory_sources: []`. This does not satisfy the explicit requirement to clearly mark contradictory source state and can present a stale release mirror as eligible evidence. | Add a deterministic contradiction check against the declared authoritative/mirror source(s), expose contradiction details distinctly, and fail closed for contradicted records (exclude them or force abstention). Add a focused regression proving that conflicting release state is marked and cannot be returned as an ordinary source-linked candidate. Keep the pilot offline and noncanonical. |
| RECOMMENDED | `MAP_System/artifacts/experiments/task284-source-aware-fingerprint-pilot.md` | The holdout hash and recall/abstention results reproduce, but the corpus is live: review-time byte counts changed from 12,751,354/984,850 to 12,751,473/986,653, yielding 92.26% rather than 92.28% reduction. | Clarify that only the holdout is frozen and byte metrics are point-in-time, or freeze/identify the evaluated corpus if exact replay is intended. |

## Files Reviewed

- `MAP_System/tasks/TASK-284.json`
- `MAP_System/artifacts/experiments/task284-source-aware-fingerprint-pilot.md`
- `MAP_System/scripts/task_fingerprint_production_pilot.py`
- `MAP_System/tests/test_task_fingerprint_production_pilot.py`
- `MAP_System/artifacts/experiments/task-fingerprint-index-pilot-2026-07-19.md`
- `MAP_System/artifacts/experiments/task-fingerprint-holdout-2026-07-19.md`
- `MAP_System/handoffs/STATE_SNAPSHOT-codex-lab-lilo-20260726T191209Z.yaml`
- `MAP_System/shared/context-continuity.md`

## Forbidden Changes Check

- PASS: No startup, runner-routing, Command Center, task-authority, or default
  production integration was enabled.
- PASS: The projection declares `mode: offline_disposable_projection` and
  `production_routing_enabled: false`.
- PASS: Every returned result carries `raw_evidence_required: true` and source
  backlinks.
- PASS: The failed thresholds were not promoted or represented as production
  readiness.
- PASS: This review did not edit implementation; remediation must proceed
  through `CHANGES_REQUESTED`.

## Verification

- `sha256sum MAP_System/handoffs/STATE_SNAPSHOT-codex-lab-lilo-20260726T191209Z.yaml` — exact expected hash `b2fd9b4b17cb346672eefdbc90cc8275288f2e41a5c7cac0d15752146fa27546`.
- `context_rotation.py validate` plus direct ledger inspection — Lilo entry finalized with Romi session `019f9f59-a7ad-76c0-a451-945c62ca0e7c`; entry-local issues, path drift, and task drift are clear. Global validation still reports unrelated pre-existing Zori drift.
- `MAP_System/.venv/bin/python MAP_System/tests/test_task_fingerprint_production_pilot.py` — 4/4 pass.
- `MAP_System/.venv/bin/python -m py_compile ...` — pass.
- `task_fingerprint_production_pilot.py --report /tmp/...` — holdout hash reproduced; task recall 33.33%, source recall 33.33%, abstention 0%, byte reduction 92.26%.
- Contradictory-state fixture — task JSON `RELEASED` plus task-graph `CHANGES_REQUESTED` produced `indexed_status: RELEASED` and an empty contradiction marker.
- `validate_task_schema.py` — pass.
- `validate_task_mirrors.py --db MAP_System/map.db --root MAP_System` — pass.
- `validate_task_graph.py` — pass.

## Notes

The measured negative result is useful and honestly retained offline. The
required change is narrow: make the already-promised contradiction boundary
real and regression-tested; do not tune retrieval scores or promote routing as
part of the rework.
