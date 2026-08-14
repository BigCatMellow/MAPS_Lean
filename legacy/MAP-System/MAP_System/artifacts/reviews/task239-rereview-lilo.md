# Re-review: TASK-239 MAP practice-scenario runbook and queue

- task_id: TASK-239
- reviewer: codex-lab-lilo
- task_owner: codex-lab-kiri
- review_type: re-review after CHANGES_REQUESTED

## Verdict

APPROVED

## Files Reviewed

- `MAP_System/tasks/TASK-239.json`
- `MAP_System/notes/practice-scenario-runbook.md`
- `MAP_System/artifacts/planning/map-practice-scenario-queue-2026-07-18.md`
- `MAP_System/artifacts/reviews/task239-review-lilo.md`

## Forbidden Changes Check

PASS — the rework remains planning/evidence guidance only. It preserves normal
task, decision, review, release, and hcom authority paths.

## Rework Check

PASS — the scenario packet now declares `evidence_paths` for packet, raw,
review, and outcome records, plus `operator_decision_points` for scope
admission and only enumerated in-run gates. The runbook defines STOPPED and
ordinary-routing behavior for missing destinations or unlisted issues. The
queue carries the same rule and identifies scenario-level decision points.

## Acceptance Criteria Check

| Criterion | Result | Evidence |
|---|---|---|
| Reusable packet and bounded lifecycle process | PASS | Packet, role boundaries, lifecycle slice, evidence locations, decision points, stop conditions, and independent review are explicit. |
| Complete scorecard with negative-result rule | PASS | All required measures and preserved-negative-result treatment remain present. |
| At least three bounded scenarios | PASS | Four queued scenarios each include hypothesis, evidence, decision boundary, non-goals, and admission gate. |
| Candidate/negative-result closeout without auto-promotion | PASS | Tuning loop preserves the proposal-only rule and caps follow-up. |

## Verification

- Reviewed all first-review required actions against the reworked runbook and queue.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` — PASS.

## Release Note

The required packet-contract correction is complete. Release remains the
accountable owner’s normal lifecycle action.
