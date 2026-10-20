# H02 — Planning, task truth, coordination, and controlled action

- **Record:** candidate success-condition branch, not a new task or authority source
- **Parent:** [Full MAPS_L goal map](../README.md) · **Dependencies:** [cross-branch graph](../DEPENDENCIES.md)
- **Coverage:** [45 checklist rows + 35 master capability areas](../COVERAGE.md)
- **Children stored separately:** none
- **Evidence checkpoint:** 2026-10-20, main `69879cd0375f687c1df753fb5a4b83dda76b562e`; current runtime and task evidence supersedes status prose

## Required outcome
MAPS_L selects and coordinates the **next eligible authorized work** through completion without duplicate ownership, hidden waiting, unbounded delegation or a parallel planning database.

## Recursive conditions
- **H02.1 — One authoritative task/lifecycle store.** Accepted task revision, owner, claim/lease, dependencies, policy, evidence and review remain canonical. **Proof:** concurrent claims/failures do not create conflicting owners or DONE without criteria.
  - **H02.1.1** Material dependency cycle or missing prerequisite is detected before action.
  - **H02.1.2** Multiple helpers cannot silently change the parent task's acceptance or authority.
- **H02.2 — Proportional planning.** Destination has precise DONE; current phase reveals dependencies; first wave has bounded testable actions; distant future stays directional. **Proof:** executor can act and reviewer can judge without speculative task explosion.
  - **H02.2.1** Diagnose lack of progress: poor decomposition versus missing evidence, capability, invalid dependencies, invalid strategy or absent authorization.
  - **H02.2.2** Recurse on the **affected condition only**, with arbitrary useful depth and fan-out.
  - **H02.2.3** Cross-branch requirements are links, not duplicate children or separate state.
- **H02.3 — Route work by eligibility and capability.** Worker selection, deterministic flows, bounded helpers and wait/reconcile reason are inspectable. **Proof:** injected failures route to correct owner/next action and do not silently idle.
- **H02.4 — Owner continuity across delegation.** Parent operator receives and reconciles evidence, repairs failures and continues eligible work, without self-approval. **Proof:** no unresolved assignment can be silently counted as parent DONE.
- **H02.5 — No-progress diagnosis** is advisory/triggered; never use a daemon solely to police a process. **Proof:** bounded incident test shows fewer unproductive stalls without false takeover.
- **H02.6 — Deterministic flow extraction** only for a stable, repeated sequence; otherwise reuse the task lifecycle and ordinary method. **Proof:** measured reliability or cost benefit.
- **H02.7 — Finish on proof.** Once accepted DONE, final verification and required independent review complete, stop creating descendant work.

## Existing baseline
[Master roadmap](../../00-MASTER-MAPS-CAPABILITY-ROADMAP.md) §6.1, §6.19–6.21 and [coordination](../../../coordination/README.md) describe canonical state, helper transport, LangGraph, and bounded recovery. Tests demonstrate many primitives, **not** fully autonomous projects under arbitrary failure.

## First challenges
Test parent-to-child handoff, realistic failure recovery, eligibility after changed dependencies, and no-authority-expansion after decomposition. Do not implement a universal planner by default; treat Pilot PLAN E1+ experiments as research outside MAPS_L authority.
