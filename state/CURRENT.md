# Current State

**Reconciled: 2026-11-24 — planning refresh, not a live status board.**
For current PR/CI/ownership facts, use [live coordination](../work/coordination/README.md).

## Objective

MAPS_L is a provider-neutral operating system around capable AI workers:
task truth, bounded authority, orchestration, reusable methods, verification,
recovery, durable evidence and controlled learning.

## Direction

**One plan:** [Current development plan in the master roadmap](../work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md#current-development-plan).
**One technical evidence view:** [Capability checklist](../work/roadmaps/CAPABILITY_CHECKLIST.md).
The revised sequence is proposed for owner review; it does not authorize external
execution or waive the normal merge/review rules.

## Baseline and next action

- Baseline: [main 605ce61](https://github.com/BigCatMellow/MAPS_Lean/commit/605ce610e0be3334d1da7af2a7c6f5912b6cc05f).
- Eight PRs integrated (#367, #370, #372, #374, #375, #377, #378, #379).
  [Runtime CI](https://github.com/BigCatMellow/MAPS_Lean/actions/runs/45405604013)
  succeeded on that baseline. Merge was an explicit one-time exception; this
  does not establish fresh independent review or permission for further exceptions.
- Active proposed outcome: stabilize the consolidated baseline (P0), then
  prepare and complete one useful external-project pilot (P1/P2).
- Next action: independent integrated safety/merge-path review, confirm
  deployment prerequisites, reconcile unresolved task/evidence receipts and
  actual recovery paths now that HCOM is not used operationally.
- Blockers: GitHub-native merge configuration/identity governance unverified;
  no external pilot target/task or external write authority selected;
  external local handoff files inaccessible from this audit.
- Remaining open PR: [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341),
  parked benchmark. #371 design is merged into its branch, not evidence
  Gate 1/4/5 or execution authority has been satisfied.

## Retrieval boundaries

Normal work: `AGENTS.md + approved roadmap/task + one relevant playbook method`.
Historical records are evidence, not parallel queues. The replacement-runtime
migration is complete; `legacy/` is intentionally retained as reference and
not an active runtime dependency. The safety fork is not an authority source.
Use [migration routing](../migration/README.md) for specific historical recovery.

Before ending a material work arc, reconcile the master plan and evidence
checklist via [trajectory check](../playbook/ROADMAP_TRAJECTORY_CHECK.md), refresh
this short entry point, and name any inaccessible/unresolved source.
