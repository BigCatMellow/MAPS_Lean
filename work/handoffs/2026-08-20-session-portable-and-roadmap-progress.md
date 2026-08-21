# Handoff: portable deployment designs and roadmap progress

- From: `/root`
- To: next MAPS_Lean agent
- Task: roadmap continuation after 2026-08-19 session handoffs
- Status: portable deployment is blocked at D3; follow-on internal roadmap work is active

## What is true now

- VERIFIED: PRs #133 through #140 were merged to `main` by 2026-08-21 00:15 UTC.
- VERIFIED: portable deployment 6.35 has D0, D1, D2a, D2b, and D2c complete.
- VERIFIED: D3 remains not started and is blocked on Chain Shovel target access/authority plus a separately AGI-ready execution task.
- VERIFIED: roadmap 6.27 is now DONE: outcome read models expose derived `incident_class` while preserving free-text `failure_class`.
- VERIFIED: roadmap 6.24 remains IN PROGRESS: routing can consume explicit caller-supplied compatibility reports, but no live report source/freshness/spec association exists.
- UNKNOWN: Chain Shovel checkout path, reproduction, source scope, verification commands, reviewer, hosting/CI, and merge policy.

## Work completed

- Merged PR #133: D2a portable deployment file convention.
- Merged PR #136: D1 installer targeting design.
- Merged PR #137: D2b sibling-clone adapter design.
- Merged PR #138: D2c Chain Shovel pilot plan.
- Merged PR #139: incident taxonomy projection for outcome read models.
- Merged PR #140: explicit environment compatibility report plumbing through routing.

## Work not completed

- D3 Chain Shovel pilot was not started; no Chain Shovel repo was accessed.
- No portable installer or adapter implementation exists.
- No live environment report sourcing, freshness/cache policy, task-to-`EnvironmentSpec` association, or routing CLI input exists.
- H4/E4 validation-tier production call site remains unresolved; do not wire it without a trusted composition root.

## Decisions and constraints

- Do not build D4-D6 portable deployment work before D3 evidence; Roadmap 06 marks those later/triggered/out of scope.
- D3 requires explicit operator/target-owner authority for target access, writes, command execution, PR publication, review path, and merge.
- For 6.24, the new routing input is an evidence-injection boundary only. Missing reports preserve legacy routing.
- `DRIFTED` and `UNKNOWN` compatibility reports do not reject assignment; only `INCOMPATIBLE` gates.

## Current blocker / risk

- Portable deployment is blocked on external Chain Shovel access/authority.
- Validation-tier production wiring is a risk because no existing composition root both owns an `EnvironmentSpec` and constructs production `HarnessService` hooks.

## Working state

- Changed/uncommitted paths: none in the completed feature worktrees at handoff time.
- Last verification performed:
  - PR #140 CI: `test` passed, `review-evidence` passed.
  - Local PR #140 checks: `python3 -m unittest tests.test_routing_policy -v` passed 21 tests; `python3 -m unittest tests.test_langgraph_routing -v` passed 2 tests, skipped 1 optional LangGraph test.
- Known failing checks: none known on `main` after PR #140 merge.

## Next action

1. Continue from `work/roadmaps/CAPABILITY_CHECKLIST.md`, preferring a bounded non-blocked `IN PROGRESS` gap. The next likely candidate is to shape the H4/E4 validation-tier production call-site decision before implementation, unless a safer roadmap-backed task is selected by program steering.

## Do not redo / do not assume

- Do not redo D0-D2c portable deployment design; they are merged.
- Do not assume D3 authority from the D2c plan.
- Do not assume Chain Shovel target facts that the D2c plan marks `UNKNOWN`.
- Do not mark 6.24 DONE merely because explicit report plumbing exists.
- Do not wire validation hooks into a production path until the spec/source/authority boundary is explicit.

## Evidence / paths

- `work/notes/2026-08-20-portable-deployment-d1-installer-targeting-design.md`
- `work/notes/2026-08-20-portable-deployment-d2a-file-convention.md`
- `work/notes/2026-08-20-portable-deployment-d2b-sibling-adapter-design.md`
- `work/notes/2026-08-20-portable-deployment-d2c-chain-shovel-pilot-plan.md`
- `work/tasks/incident-taxonomy-outcome-wiring.md`
- `work/tasks/router-environment-report-routing.md`
- `work/roadmaps/CAPABILITY_CHECKLIST.md`
- `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`
