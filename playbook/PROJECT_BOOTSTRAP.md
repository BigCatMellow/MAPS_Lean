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
