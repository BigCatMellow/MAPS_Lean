# Current State

- Current goal: Decide and execute the WezTerm-decoupled target operating model.
- Active tasks: [DEC-001](../work/decisions/DEC-001-target-operating-model-and-wezterm-decoupling.md) is proposed and awaiting Phase 0 execution.
- Latest coordination handoff: [Lean navigation and simulation tuning](../work/handoffs/2026-08-13-lean-navigation-and-simulation-tuning.md).
- Task relevance: For unrelated tasks, this state is a constraints/orientation
  source only; do not claim, modify, or advance DEC-001 without an explicit
  assignment.
- Decisions that matter now: The active workflow is provider-neutral. It
  retains SQLite, LangGraph, RnS, and hcom as its control plane; WezTerm and
  the fixed startup roster are optional presentation. The portable methods are
  active in `playbook/`, while the detailed runtime source remains preserved
  under `legacy/` until Phase 2 promotes it to an unambiguous active location.
- Blockers: None.
- Next action: The operator may either create the Phase 0 active-runtime
  manifest and read-only WezTerm-coupling inventory described by DEC-001, or
  make the explicit Obsidian file-explorer/archive decision recorded in the
  latest coordination handoff.
