# Review: TASK-239 MAP practice-scenario runbook and queue

- task_id: TASK-239
- reviewer: codex-lab-lilo
- task_owner: codex-lab-kiri
- risk_tier: low

## Verdict

CHANGES_REQUESTED

## Files Reviewed

- `MAP_System/tasks/TASK-239.json`
- `MAP_System/notes/practice-scenario-runbook.md`
- `MAP_System/artifacts/planning/map-practice-scenario-queue-2026-07-18.md`

## Forbidden Changes Check

PASS — the submission is planning/evidence guidance only. It creates no
authority path, task mutation, runtime service, startup policy, or deployment
behavior.

## Acceptance Criteria Check

| Criterion | Result | Evidence |
|---|---|---|
| Reusable packet, bounded roles/lifecycle, operator points, evidence locations, stops, review | PARTIAL | The packet, role boundaries, lifecycle slice, stop rules, and independent review are strong. It does not explicitly record where the packet, raw evidence, review, and outcome are stored, and it has no explicit operator-decision-points field. |
| Full scorecard including negative-result rule | PASS | The scorecard covers first valid action, retrieval, order/time, handoff friction, attention, review/release, interruption/recovery, and negative-result value. |
| At least three bounded scenarios with hypotheses/gates | PASS | The queue defines four ordered scenarios, each with hypothesis, minimum evidence, non-goals, and admission gate tied to current MAP constraints. |
| Promotion/negative-result handling without auto-promotion | PASS | The tuning loop caps follow-up proposal, preserves PARTIAL/FAIL/STOPPED evidence, and routes decisions through command-center. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/notes/practice-scenario-runbook.md` | The acceptance criterion requires reusable evidence locations and explicit operator decision points. The scenario packet contains `baseline_sources` but no destination for the packet, raw command/results, independent review, or outcome. It also records `operator_scope` but not which later decision points can legitimately reach the operator. A returning reviewer would have to infer both from prose, weakening the durable practice loop the task is meant to test. | Add compact packet fields for `evidence_paths` (packet, raw evidence, review, and outcome locations) and `operator_decision_points` (scope admission plus only specific gates/blockers that may be requested). State that absent/unknown locations or an unlisted decision point triggers a stop/ordinary routing path. Keep the existing authority boundary and do not add an approval mechanism. |

## Verification

- Read the task criteria against both submitted artifacts.
- Verified all four queued scenarios are bounded by admission gates and non-goals.
- Verified the tuning loop preserves negative evidence and prohibits automatic task promotion.

## Notes

This is a narrow documentation rework, not a request for new process layers.
The packet is already close to usable; the missing fields make its evidence and
operator-boundary contracts inspectable after an interruption.
