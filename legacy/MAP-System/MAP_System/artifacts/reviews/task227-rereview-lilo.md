# Re-review: TASK-227 system-improvement implementation plan

- task_id: TASK-227
- reviewer: codex-lab-lilo
- task_owner: claude-lab-gome
- review_type: independent re-review after `CHANGES_REQUESTED`
- reviewed_at: 2026-07-18

## Verdict

APPROVED

## Acceptance criteria

| Criterion | Result | Evidence |
|---|---|---|
| Current workstreams have a priority order and rationale | PASS | The north-star lifecycle table and workstream inventory identify visible state as the weakest present seam; the immediate slate follows that priority rather than treating all six workstreams as simultaneous work. |
| Priority workstreams translate into observable actions or file targets | PASS | 1a, 2a, 3a-i/ii, 4a, and 5a name bounded scope, lifecycle slice, measure, acceptance checks, risk treatment, and (where applicable) target paths. |
| Durable kickoff and book context are linked for resumption | PASS | The opening resumable-context paragraph links both required notes and tells the next reader to read them first. |

## Files Reviewed

- `MAP_System/tasks/TASK-227.json`
- `MAP_System/notes/system-improvement-implementation-plan.md`
- `MAP_System/artifacts/reviews/task227-review-lilo.md`
- `MAP_System/artifacts/experiments/coordination-surface-readiness-audit-2026-07-18.md`
- `MAP_System/artifacts/experiments/durable-memory-index-readiness-audit-2026-07-18.md`
- `MAP_System/artifacts/experiments/map-practice-lifecycle-audit-2026-07-18.md`

## Forbidden Changes Check

PASS — TASK-227 registers only the implementation-plan note as output. The
revised submission changes that plan and adds no implementation, policy,
decision, task-state, or runtime mutation.

## Required rework findings

| ID | Result | Re-review evidence |
|---|---|---|
| C1 — coordination-surface authority/conflict contract | PASS | §1a identifies the authoritative source for durable status, live claims, latest action, and attention reasons; preserves multi-source disagreement as `conflict/unknown`; prohibits inferred status; and requires three deterministic mixed-state fixtures plus a staged screenshot. It retains a read-only, no-new-store boundary. |
| C2 — bounded, testable durable index | PASS | §2a retains `shared/memory-map.md` as the existing host, rejects a peer index, caps the initial population at 12 routes, specifies route metadata and maintainer/update behavior, and requires five reproducible ≤2-hop lookup samples. It correctly defers a validator until drift is measured. |
| C3 — helper-mutation authority decision | PASS | §3a separates the AUTHORITY-class decision (3a-i) from the post-approval documentation task (3a-ii), names command-center approval as the prerequisite, and requires reconciliation with current helper permission text rather than silently changing it. |
| C4 — evidence intake without autonomous task growth | PASS | The evidence-intake section names completed lifecycle/readiness evidence, records new results as candidates rather than automatic tasks, assigns promotion to a core agent, and parks unproven seams in the backlog with triggers. |
| C5 — operator north-star and measurable feedback | PASS | The north-star defines an operator-guided lifecycle from intent through interruption/recovery to reviewed release. Each immediate work item states its lifecycle slice and an observable measure, with an explicit negative-result/revert rule. |

## Scope and safety check

- The registered deliverable remains a planning note only; this submission does not implement UI, alter policy, create a new decision, change task state, or mutate runtime state.
- The coordination-card proposal does not collapse hcom, `status.json`, SQLite, and event-log signals into a new authoritative status.
- The plan appropriately keeps 3a-i behind operator approval and keeps F2–F5 as evidence-backed backlog candidates rather than silently expanding the slate.

## Verification

- Read the revised plan against `TASK-227.json` and all five required findings in `artifacts/reviews/task227-review-lilo.md`.
- Cross-checked the 1a and 2a task shapes against the independent coordination-surface and durable-memory-index readiness audits.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_graph.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` — PASS.
- `git diff --check -- MAP_System/notes/system-improvement-implementation-plan.md` — PASS.

## Release note

This approval closes the requested plan rework. Release remains the accountable task owner's action under the normal MAP lifecycle.
