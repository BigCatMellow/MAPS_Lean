# Lean Project Playbook

This index is **navigation, not a second operating contract**. Repository-wide
authority/behavior live in [`AGENTS.md`](../AGENTS.md); these files are reusable
methods inside that authority. Historical material lives under `migration/` or
`legacy/` and is not part of the normal read path.

## Authority and reading budget

```text
AGENTS.md → approved roadmap/project → active task
          → ONE relevant playbook method → evidence/review/handoff
```

A playbook may define requirements for the method it owns, but cannot override a
higher authority source. If it appears to conflict, follow the higher source and
repair the lower one. Normal work should not require chain-reading playbooks; if
several routinely overlap, consolidate their owners.

## Core workflow methods

Prefer these for the common project lifecycle.

| Need | Primary owner | Boundary |
| --- | --- | --- |
| Start a durable project | [PROJECT_BOOTSTRAP.md](PROJECT_BOOTSTRAP.md) | Project framing and initial roadmap; not task execution policy. |
| Turn a concise request into a bounded contract | [REQUEST_COMPILATION.md](REQUEST_COMPILATION.md) | Compiles intent and inherited authority; cannot silently expand it. |
| Decide whether a consequential task is agent-ready | [AGI_STANDARD.md](AGI_STANDARD.md) | Single task-readiness standard, including practical shaping guidance. |
| Check whether self-selected work is the right next work | [PROGRAM_STEERING.md](PROGRAM_STEERING.md) | Per-task program steering; not roadmap redesign. |
| Check whether the roadmap itself is still on trajectory | [ROADMAP_TRAJECTORY_CHECK.md](ROADMAP_TRAJECTORY_CHECK.md) | Work-arc/roadmap correction; not routine per-task steering. |
| Shape, assign, execute, review, and finish a task | [TASK_LIFECYCLE.md](TASK_LIFECYCLE.md) | Task lifecycle procedure under inherited roadmap authority. |
| Use helpers and cross-agent communication | [HELPERS_AND_COMMUNICATION.md](HELPERS_AND_COMMUNICATION.md) | Bounded delegation/communication; parent ownership remains with the orchestration operator. |
| Freeze consequential execution context/scope and preserve review independence | [EXECUTION_INTEGRITY.md](EXECUTION_INTEGRITY.md) | Execution binding/proof; does not grant new authority. |
| Make a consequential decision or handle safety/destruction boundaries | [DECISIONS_AND_SAFETY.md](DECISIONS_AND_SAFETY.md) | Decision/safety method under `AGENTS.md` scope-level authorization. |

## Specialized methods

Use only when the specific concern is active.

| Need | Use | Relationship / non-overlap |
| --- | --- | --- |
| Understand retained runtime controls | [CONTROL_PLANE.md](CONTROL_PLANE.md) | Runtime responsibility map; terminals/windows are not authority. |
| Install/verify SQLite, LangGraph, and hcom on a fresh clone | [Control-Plane Setup](../docs/CONTROL_PLANE_SETUP.md) | Setup/migration only; keep databases and authority roles separate. |
| Plan portable control-plane deployment into another repo | [Portable Deployment roadmap](../work/roadmaps/agent-harness-capabilities/06-portable-deployment.md) | Current deployment roadmap, not a general operating rule. |
| Route by demonstrated model/harness capability and cost | [MODEL_CAPABILITY_ROUTING.md](MODEL_CAPABILITY_ROUTING.md) | Single worker-capability/routing method; includes the retained HPOM heuristic. |
| Apply provider/tool-specific operating guidance | [PROVIDER_AND_TOOL_GUIDANCE.md](PROVIDER_AND_TOOL_GUIDANCE.md) | Provider adaptation only; cannot redefine MAPS authority. |
| Test a consequential approved claim with a formal dissent mechanism | [TENTH_SEAT_REVIEW.md](TENTH_SEAT_REVIEW.md) | Formal narrow protocol; ordinary helper challenge does not require this artifact. |
| Audit whether durable records are connected, reconciled, and discoverable across sessions | [SPIDERWEB_AUDIT.md](SPIDERWEB_AUDIT.md) | Treating link count, topic similarity, or the derived graph as authority. |
| Isolate writable dispatched work or recover worktree-specific failures | [WORKTREE_ISOLATION.md](WORKTREE_ISOLATION.md) | Git isolation mechanics; no merge/permission authority. |
| Test or tune a workflow with an agent scenario | [SIMULATION_DESIGN.md](SIMULATION_DESIGN.md) | Simulation/evaluation; plausible output is not production proof. |
| Plan/import a project into ProjectUpdater | [ROADMAP_AND_PROJECTUPDATER.md](ROADMAP_AND_PROJECTUPDATER.md) | ProjectUpdater representation; not the canonical task store. |
| Establish facts or evaluate a workflow/document/usability path | [RESEARCH.md](RESEARCH.md) | Evidence gathering/evaluation; no implementation authority by itself. |
| Track downside, reversibility, and mitigations | [RISK_AND_CHANGE.md](RISK_AND_CHANGE.md) | Risk analysis; does not create a separate approval system. |
| Capture a worthwhile discovery without expanding current scope | [EMERGENCE.md](EMERGENCE.md) | Discovery capture only. |
| Repair drift and learn from repeated failures | [REPAIR_AND_LEARNING.md](REPAIR_AND_LEARNING.md) | Repair/learning loop; findings do not silently become global policy. |
| Classify information as authority, task context, fact, Skill, flow, tool, or example | [INFORMATION_CLASSES.md](INFORMATION_CLASSES.md) | Information type, not lifecycle status or authority creation. |
| Keep project information trustworthy and cheap to retrieve over time | [INFORMATION_LIFECYCLE.md](INFORMATION_LIFECYCLE.md) | Active/retired/archive lifecycle plus routing maintenance; not information classification. |
| Continue across sessions | [Current state](../state/CURRENT.md) and [handoff template](../templates/handoff.md) | Continuation state/evidence only; does not expand task authority. |

## Adding or changing a method

Follow the anti-sprawl invariant in `AGENTS.md`. Before adding a playbook file:

1. Name the existing concept owner and why it cannot coherently own the addition.
2. Give the proposed method one distinct reusable job.
3. Link rather than copy shared rules.
4. Add one index entry that states the non-overlap.
5. Merge/retire any method it supersedes in the same arc.

A new file is not evidence of a new capability. Fewer, clearer owners are preferred.

## Runtime detail

For SQLite/LangGraph/RnS/hcom responsibility boundaries, read
[CONTROL_PLANE.md](CONTROL_PLANE.md). This index does not duplicate that detail.

## Legacy audit and migration sources

Agents needing legacy provenance should start with:

- [Legacy Knowledge Audit](../migration/LEGACY_KNOWLEDGE_AUDIT.md)
- [Legacy Promotion Ledger](../migration/LEGACY_PROMOTION_LEDGER.md)
- [Future Ideas Backlog](../migration/FUTURE_IDEAS_BACKLOG.md)
- [Legacy Removal Checklist](../migration/LEGACY_REMOVAL_CHECKLIST.md)
- [Source catalog](SOURCE_CATALOG.md)

Migration snapshots are reference source only; active runtime code must not import
or execute from them. Newer migration audit/ledger evidence outranks older source
mapping for legacy-removal decisions.
