# Handoff: Lean navigation and simulation tuning

- From: Codex
- To: next coordinator / operator
- Status: active work safely paused; recent documentation and simulation work is complete

## What is true now

- MAP Lean is the working copy at `/home/mellow/Projects/MultiAgentProject-Lean`.
  The original MAP project remains untouched at
  `/home/mellow/Projects/MultiAgentProject`.
- The retained operating model is provider-neutral: SQLite is canonical mutable
  task state; LangGraph routes; RnS handles restart/limit recovery using hcom;
  WezTerm is optional presentation. The governing decision is
  [DEC-001](../decisions/DEC-001-target-operating-model-and-wezterm-decoupling.md).
- Active orientation is [README](../../README.md) → [First Run](../../docs/FIRST_RUN.md)
  → [AGENTS](../../AGENTS.md) / [playbook index](../../playbook/INDEX.md).
- Obsidian settings exclude `legacy/` from search/graph-related views and the
  graph filters `legacy/` plus generated work reports, reviews, and handoffs.
  These settings are in `.obsidian/app.json` and `.obsidian/graph.json`.
  Reload the vault if they are not reflected yet.

## Completed simulation evidence

| Simulation | Result | Durable finding |
| --- | --- | --- |
| TASK-001 / TASK-002 | Passed after navigation refinements | README hands first-time agents to First Run; First Run owns orientation. |
| TASK-005 | Passed after fixes | Bootstrap, research, risk, and roadmap methods must link to their exact templates. |
| TASK-006 / TASK-007 | Passed after fixes | Repair and Learning must directly link to the repair-record template; the active route now reaches it without search. |
| TASK-008 | Passed | A returning agent with only an incomplete handoff must not resume, claim, edit, or review without canonical task/evidence. |

- TASK-008 is the first test using the strengthened observability rule: it sent
  four live `question/assumption → next step` updates and independently passed.
  Read [its review](../reviews/TASK-008-independent-review.md) and
  [report](../reviews/TASK-008-returning-agent-report.md) for the exact route
  and authority reasoning.
- The reusable [Simulation Design](../../playbook/SIMULATION_DESIGN.md) method
  is now linked from the index. It defines controlled traps, measurable
  outcomes, failure classes, independent review, regression tests, and
  cold-start/returning-agent modes.
- The latest read-only [Digital Fungus report](../reports/TASK-008-post-simulation-fungus-report.md)
  found **0 broken links in active Lean material** and **30 active notes
  reachable from First Run**. Historical `legacy/` contains 139 unresolved
  candidate links; these are preserved reference material, not an active
  navigation defect.

## Remaining friction and decisions

- Obsidian's graph is now focused, but the vault still physically contains the
  large `legacy/` archive. Do not delete or flatten it without explicit
  operator approval. If the file explorer still feels too noisy, decide whether
  to keep the archive inside the vault, move it outside the vault, or use an
  Obsidian file-explorer solution; each has a different discoverability and
  preservation tradeoff.
- The active audit still reports code-styled file mentions that are not graph
  edges. Most are source-catalog/history references or old handoffs. Review
  them selectively; do not blindly turn every mention into a link.
- The remaining active “orphans” are mostly intentional templates, completed
  task records, and generated reports. Confirm intent before connecting them.
- DEC-001 Phase 0 remains a separate current goal. It has not been advanced by
  the simulations.

## Next action

1. Ask the operator whether the next priority is (a) an Obsidian file-explorer
   information architecture decision, or (b) DEC-001 Phase 0's active-runtime
   manifest and read-only WezTerm-coupling inventory. For either option, create
   a scoped task with owner, output paths, acceptance criteria, and independent
   review proportionate to risk.

## Evidence / paths

- [Current State](../../state/CURRENT.md)
- [Simulation Design](../../playbook/SIMULATION_DESIGN.md)
- [Playbook index](../../playbook/INDEX.md)
- [TASK-008 task](../tasks/TASK-008-returning-agent-recovery-simulation.md)
- [TASK-008 review](../reviews/TASK-008-independent-review.md)
- [Digital Fungus report](../reports/TASK-008-post-simulation-fungus-report.md)
