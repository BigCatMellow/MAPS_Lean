# Methods and Protocols

MAPS_L has many procedures, but they are not all the same kind of thing.

This page is an **orientation map**, not another operating contract. Current
[`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md), the
approved project/roadmap/task, runtime state, and direct evidence remain stronger.
The canonical reusable-method index is
[`playbook/INDEX.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INDEX.md).

## The hierarchy

```text
human authority
→ AGENTS.md global operating contract
→ approved project / roadmap
→ active task contract
→ canonical runtime / task state
→ one relevant MAPS_L method
→ project-specific protocol when needed
→ evidence / review / handoff
```

A protocol or method can define how its own job is performed. It does not create
new project scope merely because it exists or is available.

## Core workflow methods

These form the normal project/task lifecycle:

- [Project Bootstrap](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/PROJECT_BOOTSTRAP.md)
  — frame a durable project, DONE, permission envelope, backward plan, risks, and first wave.
- [Request Compilation](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/REQUEST_COMPILATION.md)
  — turn concise intent into a bounded task contract without silently widening authority.
- [Agent-Grade Instructions Standard](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/AGI_STANDARD.md)
  — test whether consequential work is ready for a fresh worker without material guessing.
- [Program Steering](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/PROGRAM_STEERING.md)
  — decide whether a candidate next task is the right bounded move inside the current program.
- [Roadmap Trajectory Check](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/ROADMAP_TRAJECTORY_CHECK.md)
  — check whether the work arc/roadmap itself has drifted or needs correction.
- [Task Lifecycle](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/TASK_LIFECYCLE.md)
  — shape, assign, execute, review, correct, approve, and finish bounded tasks.
- [Helpers and Communication](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/HELPERS_AND_COMMUNICATION.md)
  — bounded delegation and cross-agent communication while the orchestration operator retains the parent outcome.
- [Execution Integrity](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/EXECUTION_INTEGRITY.md)
  — freeze consequential execution context/scope and preserve exact-revision review independence.
- [Decisions and Safety](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/DECISIONS_AND_SAFETY.md)
  — handle consequential decisions and genuine authority/safety/destruction boundaries.

A common route is:

```text
Project Bootstrap
→ approved roadmap
→ AGI-ready task
→ Task Lifecycle
→ one specialized method only when needed
→ verification / independent review
→ reconcile evidence
→ continue, hand off, merge, or DONE
```

## Specialized methods

Use only when their concern is active:

- [Control Plane](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/CONTROL_PLANE.md)
- [Control-Plane Setup](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/CONTROL_PLANE_SETUP.md)
- [Portable Deployment](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/agent-harness-capabilities/06-portable-deployment.md)
- [Model Capability Routing](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/MODEL_CAPABILITY_ROUTING.md)
- [Provider and Tool Guidance](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/PROVIDER_AND_TOOL_GUIDANCE.md)
- [10th Seat Review](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/TENTH_SEAT_REVIEW.md)
- [Spiderweb Audit](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/SPIDERWEB_AUDIT.md)
- [Worktree Isolation](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/WORKTREE_ISOLATION.md)
- [Simulation Design](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/SIMULATION_DESIGN.md)
- [Roadmap + ProjectUpdater](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/ROADMAP_AND_PROJECTUPDATER.md)
- [Research](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/RESEARCH.md)
- [Risk and Change](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/RISK_AND_CHANGE.md)
- [Emergence](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/EMERGENCE.md)
- [Repair and Learning](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/REPAIR_AND_LEARNING.md)
- [Information Classes](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INFORMATION_CLASSES.md)
- [Information Lifecycle](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INFORMATION_LIFECYCLE.md)
- [Cross-session continuation](https://github.com/BigCatMellow/MAPS_Lean/blob/main/state/CURRENT.md)

For the canonical boundary/relationship description of each method, use the
[playbook index](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INDEX.md).

## Important subprotocols and enforced gates

Some operationally important procedures are owned inside a broader source rather
than being separate top-level playbooks.

### Operational independence

Repeatable work may trigger the operational-independence gate inside
[Task Lifecycle](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/TASK_LIFECYCLE.md).
Parent success must not depend on the originating session being present.

### Independent review and revision binding

Consequential review is bound to the exact substantive revision and must be
genuinely independent when the governing criteria require it. See
[Execution Integrity](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/EXECUTION_INTEGRITY.md)
and [Checks and Balances](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/CHECKS_AND_BALANCES.md).

### MAPS_L merge gate

Every merge to `main` uses `scripts/opcmd_merge.py`, not an ordinary GitHub or
`gh pr merge` path. The canonical merge-authority rules live in
[`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md).

### Handoff loop closure

Forward-looking handoffs must be registered, received/reconciled, continued when
successor work starts, and terminalized when complete or superseded. See
[`work/handoffs/README.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/handoffs/README.md).

### Repeat-failure escalation

The first occurrence is fixed and recorded. A repeated same-root-cause failure
requires an enforced/mechanical countermeasure where feasible, not another
instruction paragraph. See
[Repair and Learning](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/REPAIR_AND_LEARNING.md).

## Project-specific protocols

Experiments and projects may own narrower protocols: frozen eval procedures,
review prompts, execution runners, scoring/evaluator packages, custody rules, or
project-specific state machines.

Those should stay with the project that owns them unless reuse proves a broader
MAPS_L method is justified. Do not promote every experiment prompt into the
playbook.

For cross-repository project/protocol discovery in Pilot Projects, start at the
[project-control map](https://github.com/BigCatMellow/Pilot_Projects/blob/main/project-control/README.md).
That routing surface is navigation only and does not override MAPS_L or project
authority.

## How to choose what to read

Use the shortest route:

```text
AGENTS.md + approved roadmap/task + one relevant method
```

Then add a project-specific protocol, runtime state, evidence, review, or handoff
only when the work actually needs it.

If routine work requires several overlapping methods or repeated directory/search
exploration just to discover the correct procedure, that is an information-routing
failure. Consolidate or repair the route instead of adding another summary.
