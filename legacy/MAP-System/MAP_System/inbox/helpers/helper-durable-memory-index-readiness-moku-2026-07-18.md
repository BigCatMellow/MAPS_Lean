# Helper Assignment - Durable Memory Index Readiness Audit

- status: complete
- owner: codex-lab-lilo
- helper: helper-review-steward-moku
- created_at: 2026-07-18
- authority: evidence and proposal only; no implementation authority

## Purpose

Produce a narrow readiness audit for a future durable-memory index. The goal is
to test whether a small, maintained index can improve fresh-session orientation
without hiding authority, adding a shadow source of truth, or increasing startup
context unnecessarily.

This is not authorization to create MAP_System/notes/INDEX.md or change any
policy. TASK-227's current plan is under changes requested and remains owned by
claude-lab-gome.

## Required reading

- MAP_System/AGENTS.md
- MAP_System/tasks/TASK-227.json
- MAP_System/artifacts/reviews/task227-review-lilo.md
- MAP_System/notes/system-improvement-implementation-plan.md
- MAP_System/shared/current-state.md and MAP_System/shared/decisions.md
- MAP_System/notes/ relevant to agent startup, local helpers, HPOM, and E/I
- MAP_System/emergence/README.md and IDEA_PROMOTION_RULES.md

## Questions to answer

1. Inventory the smallest set of current durable documents a new core agent
   actually needs after AGENTS.md. Distinguish CURRENT from HISTORICAL and
   canonical authority from useful reference.
2. Propose a bounded index schema: required fields, a maximum scope, named
   maintainer/trigger, and how links avoid becoming a second source of truth.
3. Walk two representative fresh-session paths in no more than two hops after
   the index. Identify where each path loses required context or points to stale
   material.
4. Recommend a smallest task and measurable acceptance evidence, including a
   sample owner and review method. Identify any reason not to implement yet.

## Deliverable

Create only this report:

- MAP_System/artifacts/experiments/durable-memory-index-readiness-audit-2026-07-18.md

Make the evidence traceable to actual paths. Preserve a sharp distinction
between a navigational index and new operating policy. Classify each proposal as
essential, likely, optional, or investigate.

## Boundaries

- Read-only audit: do not create an index, change docs, task records, policies,
  or shared state.
- Do not create or claim a MAP task.
- Do not contact the operator; report normal progress to lilo with hcom
  intent=inform.
- Do not use Pi or a local model.

## Completion

When the report is complete, send lilo one concise hcom inform naming the
report path, principal finding, and any blocker. Leave the report durable even
if you also send chat detail.

## Outcome

Completed 2026-07-18. The audit found that shared/memory-map.md already acts
as an index but contains a stale target and conflicts with other startup
routes. Its durable report recommends repairing or explicitly choosing that
host through TASK-227 rework before any notes/INDEX.md is created.
