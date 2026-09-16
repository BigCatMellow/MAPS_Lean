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
higher authority source. If it conflicts, follow the higher source and repair
the lower one. Do not chain-read playbooks by default.

## Route by situation

Read only the method triggered by the concern. The trigger is routing, not new
authority or a copy of the procedure.

| Trigger | Route |
| --- | --- |
| Start/frame a durable project | [PROJECT_BOOTSTRAP.md](PROJECT_BOOTSTRAP.md) |
| Compile a concise request into bounded work | [REQUEST_COMPILATION.md](REQUEST_COMPILATION.md) |
| Decide whether consequential work is agent-ready | [AGI_STANDARD.md](AGI_STANDARD.md) |
| Shape, assign, execute, review, or finish a task | [TASK_LIFECYCLE.md](TASK_LIFECYCLE.md) |
| Delegate or communicate across agents | [HELPERS_AND_COMMUNICATION.md](HELPERS_AND_COMMUNICATION.md) |
| Bind/reconstruct run scope, context, evidence, or review independence | [EXECUTION_INTEGRITY.md](EXECUTION_INTEGRITY.md) |
| Choose the right next task inside an approved program | [PROGRAM_STEERING.md](PROGRAM_STEERING.md) |
| Recheck roadmap trajectory after accumulated work/evidence | [ROADMAP_TRAJECTORY_CHECK.md](ROADMAP_TRAJECTORY_CHECK.md) |
| Failure, drift, wrong assumption, friction, or recurrence | [REPAIR_AND_LEARNING.md](REPAIR_AND_LEARNING.md) |
| New idea, improvement, cross-root connection, or challenge | [EMERGENCE.md](EMERGENCE.md) |
| Durable information may be isolated, stale, or weakly connected | [SPIDERWEB_AUDIT.md](SPIDERWEB_AUDIT.md) |
| Consequential consensus needs formal independent dissent | [TENTH_SEAT_REVIEW.md](TENTH_SEAT_REVIEW.md) |
| Distinguish authority, context, facts, Skills, flows, tools, examples | [INFORMATION_CLASSES.md](INFORMATION_CLASSES.md) |
| Keep project information trustworthy and cheap to retrieve over time | [INFORMATION_LIFECYCLE.md](INFORMATION_LIFECYCLE.md) |
| Route by demonstrated model/harness capability and cost | [MODEL_CAPABILITY_ROUTING.md](MODEL_CAPABILITY_ROUTING.md) |
| Apply provider/tool-specific guidance | [PROVIDER_AND_TOOL_GUIDANCE.md](PROVIDER_AND_TOOL_GUIDANCE.md) |
| Locate runtime/control-plane ownership | [CONTROL_PLANE.md](CONTROL_PLANE.md) |
| Consequential decision, destruction, safety, or reauthorization | [DECISIONS_AND_SAFETY.md](DECISIONS_AND_SAFETY.md) |
| Isolate writable dispatched work or recover a worktree failure | [WORKTREE_ISOLATION.md](WORKTREE_ISOLATION.md) |
| Test/tune a workflow with a bounded agent scenario | [SIMULATION_DESIGN.md](SIMULATION_DESIGN.md) |
| Represent/import a project in ProjectUpdater | [ROADMAP_AND_PROJECTUPDATER.md](ROADMAP_AND_PROJECTUPDATER.md) |
| Establish facts or evaluate a workflow/document/usability path | [RESEARCH.md](RESEARCH.md) |
| Analyze downside, reversibility, blast radius, or mitigations | [RISK_AND_CHANGE.md](RISK_AND_CHANGE.md) |
| Trace legacy provenance/original retained guidance | [SOURCE_CATALOG.md](SOURCE_CATALOG.md) |

Do not invoke a mechanism merely because it exists. Diagnostics such as
Spiderweb do not repair; E/I capture does not authorize; Skills/tools do not
grant permission; review does not replace the orchestration operator's
ownership.

### Related non-playbook routes

- Fresh control-plane install/verification → [Control-Plane Setup](../docs/CONTROL_PLANE_SETUP.md)
- Portable deployment planning → [Portable Deployment roadmap](../work/roadmaps/agent-harness-capabilities/06-portable-deployment.md)
- Session continuation → [Current state](../state/CURRENT.md) + [handoff template](../templates/handoff.md)

## Adding or changing a method

Follow the anti-sprawl invariant in `AGENTS.md`. Before adding a playbook file:

1. Name the existing concept owner and why it cannot own the addition.
2. Give the new method one distinct reusable job.
3. Link rather than copy shared rules.
4. Add one trigger route stating the non-overlap.
5. Merge/retire anything it supersedes in the same arc.

A new file is not evidence of a new capability. Fewer, clearer owners are
preferred.

## Legacy audit and migration sources

For historical provenance use [Legacy Knowledge Audit](../migration/LEGACY_KNOWLEDGE_AUDIT.md),
[Legacy Promotion Ledger](../migration/LEGACY_PROMOTION_LEDGER.md),
[Future Ideas Backlog](../migration/FUTURE_IDEAS_BACKLOG.md), and
[Legacy Removal Checklist](../migration/LEGACY_REMOVAL_CHECKLIST.md).
Migration snapshots are reference only; active runtime code must not execute
from them. Newer migration audit/ledger evidence outranks older source mapping
for legacy-removal decisions.
