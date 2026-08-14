# Helper Assignment - KICK-01 Architecture Participant (replacement)

- status: complete
- owner: codex-lab-lilo
- helper: helper-review-steward-moku
- provider: codex
- created_at: 2026-07-18
- scope: evidence-only architecture contribution to TASK-233 kickoff

## Reason for replacement

The original visible Hana participant terminal closed at delivery, before it
could produce an artifact. This is a scenario observation, not an error to
hide. Moku is now a visible, available replacement after independently
reviewing and closing TASK-232.

## Shared kickoff packet

Read MAP_System/artifacts/experiments/map-kickoff-alignment-scenario-2026-07-18.md
before forming a view. The practice scenario shapes a future read-only Command
Center coordination card; it does not authorize code, policy, or task-plan
edits.

## Required contribution

Create one report at:

- MAP_System/artifacts/experiments/kickoff-architecture-contribution-moku-2026-07-18.md

Answer independently:

1. The smallest implementation boundary and exact likely source/UI/test seams.
2. The minimal acceptance test matrix required to avoid misleading the
   operator.
3. Scope risks, dependencies, and questions that should prevent immediate
   implementation.

Use concrete evidence from the kickoff packet and existing source paths. Mark
each recommendation essential, likely, optional, or investigate. Do not edit
the Command Center, tasks, policy, shared state, or TASK-227 plan. Report
completion to lilo via hcom intent=inform.

## Outcome

Completed 2026-07-18. The durable contribution is
MAP_System/artifacts/experiments/kickoff-architecture-contribution-moku-2026-07-18.md.
It defines a four-source read-only projection and confirms deployable
CommandCenterUI source/parity as the readiness stop condition.
