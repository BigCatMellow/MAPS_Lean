# Methods and Protocols

MAPS_L has many procedures, but they do not all carry the same authority.

This page is **orientation only**, not another operating contract. Current
[`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md),
approved project/roadmap/task scope, canonical runtime/task state, and direct
evidence remain stronger.

The canonical reusable-method router is
[`playbook/INDEX.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INDEX.md).
Use its **Route by situation** table rather than treating this wiki page as a
second method catalog.

## Authority hierarchy

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

A method may define how its own job is performed. It does not create new project
scope merely because it exists.

## Choosing a method

Start with the concern, then use the one trigger row in the
[playbook index](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INDEX.md)
that matches it.

Typical examples:

| Situation | Canonical method |
| --- | --- |
| Frame a durable project | [Project Bootstrap](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/PROJECT_BOOTSTRAP.md) |
| Turn concise intent into bounded work | [Request Compilation](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/REQUEST_COMPILATION.md) |
| Decide whether consequential work is ready | [AGI Standard](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/AGI_STANDARD.md) |
| Execute/review/finish a bounded task | [Task Lifecycle](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/TASK_LIFECYCLE.md) |
| Delegate or communicate across agents | [Helpers and Communication](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/HELPERS_AND_COMMUNICATION.md) |
| Preserve exact run/review integrity | [Execution Integrity](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/EXECUTION_INTEGRITY.md) |
| Choose the next task | [Program Steering](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/PROGRAM_STEERING.md) |
| Recheck the roadmap itself | [Roadmap Trajectory Check](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/ROADMAP_TRAJECTORY_CHECK.md) |
| Handle failure, friction, drift, or recurrence | [Repair and Learning](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/REPAIR_AND_LEARNING.md) |
| Test consequential consensus with formal dissent | [10th Seat Review](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/TENTH_SEAT_REVIEW.md) |

This table is illustrative, not exhaustive. The playbook index owns the complete
trigger/boundary map.

Do not invoke a method merely because it exists. Capability, tools, diagnostics,
review, and historical precedent do not create permission.

## Important subprotocols and enforced gates

Some operationally important procedures live inside broader owners rather than as
separate top-level methods.

### Operational independence

Repeatable work may trigger the operational-independence gate inside
[Task Lifecycle](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/TASK_LIFECYCLE.md).
Parent success must not depend on the originating session still being present.

### Independent review and revision binding

Consequential review must be genuinely independent when required and bound to the
exact substantive revision. See
[Execution Integrity](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/EXECUTION_INTEGRITY.md)
and [Checks and Balances](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/CHECKS_AND_BALANCES.md).

### MAPS_L merge gate

Every merge to `main` uses `scripts/opcmd_merge.py`, not an ordinary GitHub
merge path. The canonical rule lives in
[`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md).

### Handoff loop closure

Forward-looking handoffs are registered and reconciled through
[`work/handoffs/README.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/handoffs/README.md).
A handoff transfers continuation context, not authority.

### Repeat-failure escalation

Failures and friction route through
[Repair and Learning](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/REPAIR_AND_LEARNING.md).
A repeated same-root-cause failure requires a stronger mechanical countermeasure
where feasible rather than another instruction paragraph.

## Project-specific protocols

A project or experiment may own narrower procedures such as frozen evaluation
rules, review prompts, execution runners, scoring packages, custody rules, or a
project-specific state machine.

Those stay with the owning project unless reuse and evidence justify promotion to
a broader MAPS_L method. Project-specific protocol text cannot outrank
`AGENTS.md` or expand approved scope.

For cross-repository project/protocol discovery in Pilot Projects, start at the
[project-control map](https://github.com/BigCatMellow/Pilot_Projects/blob/main/project-control/README.md).
That surface is navigation only.

## Shortest useful read path

Normal work should usually need:

```text
AGENTS.md + approved roadmap/task + one relevant method
```

Add a project-specific protocol, runtime state, evidence, review, or handoff only
when the work actually requires it.

If routine work requires chain-reading several overlapping methods or searching
directories just to find the correct procedure, treat that as a routing or
consolidation defect rather than normal operating cost.
