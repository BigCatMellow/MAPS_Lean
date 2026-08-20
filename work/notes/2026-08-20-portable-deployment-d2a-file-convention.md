# Portable Deployment D2a - File-Convention Design

This note defines the v1 target-repo `.maps/` file convention for Portable
Deployment. It implements D2a only: Markdown state shape and templates for a
target repository. It does not implement an installer, sibling-clone adapter,
CI enforcement, or the Chain Shovel pilot.

## Source Decisions

The v1 constraints come from
`work/notes/2026-08-19-portable-deployment-operator-decisions.md`:

- use a lightweight file convention, not a SQLite control-plane port;
- distribute by sibling MAPS_Lean clone plus a lightweight target adapter;
- use best-effort review discipline, not a hard CI gate, for v1;
- keep the convention stack-agnostic;
- store target-project state in the target repository, under `.maps/`.

## Target Layout

A target repository using portable MAPS v1 should own this layout:

```text
.maps/
  README.md
  roadmap.md
  tasks/
    <short-task-name>.md
  reviews/
    <short-task-name>-review-evidence.md
  handoffs/
    <date>-<short-task-name>.md
```

Only `.maps/` in the target repository is mutable target state. The sibling
MAPS_Lean clone may provide templates, playbook guidance, and optional checks,
but it must not become the target repo's task-truth store.

## Status Vocabulary

Portable v1 uses a smaller task vocabulary than MAPS_Lean's internal task
template:

- `NEEDS_SHAPING` - the task lacks enough source truth, boundary, or acceptance
  criteria for a fresh agent to execute.
- `READY` - a fresh agent can execute without consequential guessing.
- `ACTIVE` - one accountable owner is currently executing the task.
- `READY_FOR_REVIEW` - owner says acceptance criteria are met and review is
  required.
- `CHANGES_REQUESTED` - independent review found concrete required fixes.
- `DONE` - acceptance criteria and required review are complete.
- `BLOCKED` - the next action requires missing authority, source truth, access,
  or a dependency outside the task.

`AGI status` remains a separate field because readiness and execution progress
are different facts. The portable values are:

- `UNCHECKED`
- `AGI READY`
- `AGI FAIL - NEEDS_SHAPING`
- `AGI FAIL - NEEDS_RESEARCH`
- `AGI FAIL - NEEDS_OPERATOR_DECISION`
- `AGI FAIL - BLOCKED_ON_DEPENDENCY`

## Task File Requirements

Each target task file must name:

- one accountable owner;
- source truth and evidence labels (`VERIFIED`, `REPORTED`, `ASSUMED`,
  `UNKNOWN`) where the distinction matters;
- write/action boundary;
- decisions the owner may make and decisions reserved for the operator;
- pass/fail acceptance criteria;
- required verification;
- whether independent review is required;
- stop/escalation conditions.

For v1, a task file is the authority surface for that task. If a later adapter
can derive a view from these Markdown files, it should do so without creating a
second mutable status store.

## Review-Evidence Shape

Best-effort review evidence is a Markdown file under `.maps/reviews/`. It must
state:

- reviewer identity or label;
- reviewed revision, branch, or patch reference;
- independence statement;
- task reviewed;
- files/behavior inspected;
- verification reproduced or intentionally skipped with reason;
- verdict: `APPROVED`, `CHANGES_REQUESTED`, or `BLOCKED`;
- concrete findings, if any.

Unlike MAPS_Lean's GitHub-bound `review-evidence` check, portable v1 does not
assume CI can mechanically enforce the reviewed head SHA. The evidence file
must still name the reviewed revision so a human or later adapter can detect
obvious staleness.

## Roadmap Shape

Portable v1 target roadmaps should be short and local to the target project.
They should track only target-repo work, not MAPS_Lean implementation status.
The minimum useful fields are:

- item id;
- status;
- owner or owning task;
- evidence link;
- blocker or next action.

Do not copy MAPS_Lean's full capability checklist into a target repo unless the
target project truly needs that breadth. Portable v1 is meant to move one real
task through shape, implementation, review, and merge.

## Non-Goals

D2a does not:

- define the sibling-clone adapter interface (D2b);
- plan the Chain Shovel pilot (D2c);
- execute against Chain Shovel or any external repository (D3);
- add installer flags such as `--target-repo`;
- port MAPS_Lean's SQLite task state;
- require a specific programming language, package manager, or CI system.

## Template Drafts

The first draft templates live under `templates/portable-deployment/`:

- `target-task.md`
- `target-review-evidence.md`
- `target-roadmap.md`

They are intentionally Markdown-only. D2b may later decide whether a small
adapter copies, validates, or renders them, but D2a does not require that
adapter to exist.
