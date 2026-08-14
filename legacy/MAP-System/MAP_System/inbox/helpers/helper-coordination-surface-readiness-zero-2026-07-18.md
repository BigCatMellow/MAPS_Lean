# Helper Assignment - Coordination-Surface Readiness Audit

- status: complete
- owner: codex-lab-lilo
- helper: helper-discovery-clearfront-zero
- created_at: 2026-07-18
- authority: evidence and proposal only; no implementation authority

## Purpose

Produce a bounded, evidence-based readiness audit for a future Command Center
operator coordination-surface task. This is deliberately not a UI task and does
not authorize changes to the Command Center, agent state, task records, or
system policy.

The audit must help resolve the source-authority and mixed-state questions that
were raised in the TASK-227 review before a UI change is admitted.

## Required reading

- MAP_System/AGENTS.md
- MAP_System/tasks/TASK-227.json
- MAP_System/artifacts/reviews/task227-review-lilo.md
- MAP_System/notes/system-improvement-implementation-plan.md
- MAP_System/agents/status.json and MAP_System/agents/README.md
- MAP_System/shared/current-state.md
- Existing Command Center status-related source files, read only

## Questions to answer

1. What existing source is authoritative for each proposed operator field:
   durable agent status, active claim, latest meaningful action, and needs
   attention? Record its freshness limitation and conflict behavior.
2. What does the present Command Center already show, and what exact operator
   question remains unanswered?
3. Specify three minimal staged mixed-state fixtures that a later UI task must
   demonstrate. At least one must cover stale durable status, one a live action
   newer than durable state, and one an invalid/expired claim or pending review.
4. Recommend the smallest independently implementable task shape, its exact
   output paths, and concise acceptance checks. Separate established facts from
   unverified assumptions.

## Deliverable

Create only this report:

- MAP_System/artifacts/experiments/coordination-surface-readiness-audit-2026-07-18.md

Use observation -> evidence -> implication. Include specific file and line
references where useful. Classify recommendations as essential, likely,
optional, or investigate; do not turn optional ideas into requirements.

## Boundaries

- Do not edit implementation files, task records, shared state, status files,
  policy, or the TASK-227 plan.
- Do not create or claim a MAP task.
- Do not contact the operator; report normal progress to lilo with hcom
  intent=inform.
- Do not use Pi or a local model for this audit.

## Completion

When the report is complete, send lilo one concise hcom inform naming the
report path, principal finding, and any blocker. Leave the report durable even
if you also send chat detail.

## Outcome

Completed 2026-07-18. The audit identifies map.db as the sole claim authority;
durable status and live hcom presence require distinct source labels because
the durable status export has no per-entry freshness timestamp. The resulting
read-model contract, mixed-state fixtures, and minimal task shape are recorded
in the linked report.
