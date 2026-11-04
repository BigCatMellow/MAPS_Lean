# Project Bootstrap

Use this for work expected to span sessions, multiple tasks, or multiple agents.
Skip it for a small local fix or throwaway experiment.

This is a planning method under [`AGENTS.md`](../AGENTS.md). It does not create a
second authority model. The human approves the objective, roadmap, and permission
envelope; after that, the orchestration operator executes inside that envelope
without routine approval pauses.

## Bootstrap flow

**Inspect reality → define DONE → plan backward → challenge → approve the roadmap → execute forward → adapt from evidence.**

1. **Inspect reality.** Check the current product, code, data, constraints,
   dependencies, prior attempts, and other direct evidence that matters. Separate
   verified facts from assumptions.
2. **Define DONE.** State the user/operator-visible result and the proof that will
   establish completion.
3. **Set the envelope.** Record in-scope work, explicit exclusions, effort/cost
   limits, important unknowns, consequential actions that are preauthorized, and
   actions that remain outside authority.
4. **Plan backward, then forward.** Work backward from DONE to required conditions,
   then turn those conditions into phases/dependencies and a detailed first wave.
   Keep distant phases broad until evidence makes detail useful.
5. **Challenge once before launch.** For consequential or multi-agent work, use
   relevant helpers/agents to attack assumptions, missing dependencies, risks,
   verification, and sequencing. This is a planning check, not a standing meeting
   requirement.
6. **Approve the working roadmap.** Human approval of the roadmap and permission
   envelope becomes standing execution authority. Record any explicit
   `HUMAN CHECKPOINT` only when one is genuinely desired; ordinary checkpoints are
   orchestration/reconciliation points, not approval gates.
7. **Execute autonomously.** Shape the first-wave tasks to AGI readiness, dispatch
   them, reconcile results, and continue to the next eligible roadmap work.
8. **Adapt from evidence.** At natural phase/trajectory boundaries, choose
   `CONTINUE`, `CHANGE`, `CUT SCOPE`, `RESEARCH`, or `STOP`. The orchestration
   operator makes in-envelope changes; human reauthorization is required only for
   material objective/scope/permission-envelope expansion or a human-only
   preference/authority decision.
9. **Finish on proof.** The project is DONE only when the defined final proof
   passes. Otherwise record the exact blocker and continue recovery or escalate the
   true boundary.

## PLAN — proportional, adaptive planning

The existing bootstrap, program steering, task lifecycle, and trajectory check
are PLAN's native MAPS_L owners. PLAN is an **adopted MAPS_L method**,
not an external dependency or second planner, task ledger, dependency graph,
or approval system.

At bootstrap or a material plan change:

1. **Use existing state first.** Recover the approved objective, canonical
   task/dependency state, current evidence, and scope boundaries.
2. **Plan only to the useful horizon.** Make DONE and its proof precise; give
   the current phase and first wave enough detail to execute; leave uncertain
   later waves directional.
3. **Prefer direct action when sufficient.** If a task is actionable at its
   current granularity, execute it. Decompose only if a real dependency,
   readiness, resource, or verification gap demands it.
4. **Name an expected observation for consequential steps.** What result
   should the next action produce? What evidence would show the assumption
   failed? Skip this extra articulation for routine reversible work.
5. **Route the discrepancy, not the ceremony.** Compare expected with
   observed evidence. Recover a local execution failure locally; reshape a
   too-coarse task; research missing information; revisit the roadmap if the
   plan failed; return to strategy/THINK if the underlying frame failed.
   Escalate only actual authority boundaries.
6. **Keep speculative branches speculative.** Preserve a material conditional
   alternative and its activation evidence in a plan/decision note when useful;
   do not create live child tasks for unselected routes.

A generated plan is advice until projected through MAPS_L's existing task and
authority controls. Useful does not automatically mean executable or
authorized. At execution time, use the existing
[Program Steering](PROGRAM_STEERING.md), [Task Lifecycle](TASK_LIFECYCLE.md),
and [Roadmap Trajectory Check](ROADMAP_TRAJECTORY_CHECK.md) as the continued
PLAN loop; do not bootstrap again merely to adjust a task.

When the strategy itself is wrong, invoke
[THINK](DECISIONS_AND_SAFETY.md#think--reasoning-and-judgment) before replacing
the roadmap. When a local action fails, recover locally first. `NO ACTION`
is valid if desired state already matches observed state.

Historical provenance only: the [Pilot subtraction audit](https://github.com/BigCatMellow/Pilot_Projects/blob/main/ai-planning-and-orchestration/MAPSL_PLAN_BASELINE.md)
and [adaptive topology research](https://github.com/BigCatMellow/Pilot_Projects/blob/main/ai-planning-and-orchestration/agent-planning-systems/25-ADAPTIVE-PLAN-TOPOLOGY.md).
These are not required to operate PLAN in MAPS_L.

## Planning horizon

Plan at different resolutions:

- **Destination:** precise DONE and final proof.
- **Current phase:** enough detail to expose dependencies/integration.
- **First wave:** owned, bounded, testable tasks.
- **Later phases:** directional only; refine as they approach.

Do not turn uncertain future guesses into binding detail.

## Minimum project brain

A fresh orchestration operator should be able to answer:

- What are we making, and for whom?
- What current facts were actually checked?
- What exactly counts as DONE?
- What is deliberately excluded?
- What is the approved permission envelope?
- Which consequential actions, if any, are preauthorized?
- What is the current roadmap and next eligible work?
- What is unknown or risky?
- How will the final result be verified?
- What evidence would cause the roadmap to change or stop?

Use the [project brief](../templates/project-brief.md),
[roadmap](../templates/roadmap.md), [task](../templates/task.md),
[decision](../templates/decision.md), and
[risk register](../templates/risk-register.md) templates only when they add
useful durable structure. Add artifacts/folders because the project needs them,
not because bootstrap demands ceremony.
