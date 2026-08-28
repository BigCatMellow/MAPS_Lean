# Lean Project Playbook

This index is **navigation, not a second operating contract**. Repository-wide
agent authority and behavior are defined only in [`AGENTS.md`](../AGENTS.md).
Playbook files are reusable methods inside that authority.

Historical behavior worth retaining is curated under `migration/`; ordinary
agents should not need the old `legacy/` tree.

## Authority and reading budget

Use this chain:

```text
AGENTS.md
  global operating contract
      ↓
approved roadmap/project
  objective + standing permission envelope
      ↓
active task
  exact child scope
      ↓
ONE relevant playbook method in the common case
  procedure only; no new authority
      ↓
evidence / review / handoff
```

A playbook may use `MUST`/`MUST NOT` for the method it owns, but it may not
create or override repository-wide authority, permission, or orchestration rules.
If a method appears to conflict with `AGENTS.md` or the approved task/roadmap,
the higher source wins and the lower document should be repaired rather than
blended into a new interpretation.

Normal work should not require chain-reading the playbook. Start with one method.
Follow a second only when the first explicitly delegates a distinct concern to
it. If routine work repeatedly requires stitching several overlapping methods
together, treat that as documentation sprawl and consolidate the owners.

## Core workflow methods

These own the common project lifecycle. Prefer these before specialized methods.

| Need | Primary owner | Boundary |
| --- | --- | --- |
| Start a durable project | [PROJECT_BOOTSTRAP.md](PROJECT_BOOTSTRAP.md) | Project framing and initial roadmap; not task execution policy. |
| Turn a concise request into a bounded contract | [REQUEST_COMPILATION.md](REQUEST_COMPILATION.md) | Compiles intent; does not invent permission. |
| Decide whether a consequential task is agent-ready | [AGI_STANDARD.md](AGI_STANDARD.md) | Normative task-readiness standard; [AGENT_GRADE_INSTRUCTIONS.md](AGENT_GRADE_INSTRUCTIONS.md) is guidance/examples, not a second standard. |
| Check whether self-selected work is the right next work | [PROGRAM_STEERING.md](PROGRAM_STEERING.md) | Per-task program steering; not roadmap redesign. |
| Check whether the roadmap itself is still on trajectory | [ROADMAP_TRAJECTORY_CHECK.md](ROADMAP_TRAJECTORY_CHECK.md) | Work-arc/roadmap correction; not routine per-task steering. |
| Shape, assign, execute, review, and finish a task | [TASK_LIFECYCLE.md](TASK_LIFECYCLE.md) | Task lifecycle procedure under inherited roadmap authority. |
| Use helpers and cross-agent communication | [HELPERS_AND_COMMUNICATION.md](HELPERS_AND_COMMUNICATION.md) | Bounded delegation/communication; parent ownership remains with the orchestration operator. |
| Freeze consequential execution context/scope and preserve review independence | [EXECUTION_INTEGRITY.md](EXECUTION_INTEGRITY.md) | Execution binding/proof; does not grant new authority. |
| Make a consequential decision or handle safety/destruction boundaries | [DECISIONS_AND_SAFETY.md](DECISIONS_AND_SAFETY.md) | Decision/safety method under `AGENTS.md` scope-level authorization. |

## Specialized methods

Use these only when their specific concern is active.

| Need | Use | Relationship / non-overlap |
| --- | --- | --- |
| Understand retained runtime controls | [CONTROL_PLANE.md](CONTROL_PLANE.md) | Runtime responsibility map; terminals/windows are not authority. |
| Install/verify SQLite, LangGraph, and hcom on a fresh clone | [Control-Plane Setup](../docs/CONTROL_PLANE_SETUP.md) | Setup/migration only; keep databases and authority roles separate. |
| Plan portable control-plane deployment into another repo | [Portable Deployment roadmap](../work/roadmaps/agent-harness-capabilities/06-portable-deployment.md) | Current deployment roadmap, not a general operating rule. |
| Route by demonstrated model/harness capability | [MODEL_CAPABILITY_ROUTING.md](MODEL_CAPABILITY_ROUTING.md) | Full capability-evidence method. |
| Use a lightweight manual worker-routing heuristic | [HPOM_ROUTING.md](HPOM_ROUTING.md) | Lightweight companion to Model Capability Routing, not a separate authority model. |
| Apply provider/tool-specific operating guidance | [PROVIDER_AND_TOOL_GUIDANCE.md](PROVIDER_AND_TOOL_GUIDANCE.md) | Provider adaptation only; cannot redefine MAPS authority. |
| Test a consequential approved claim with a formal dissent mechanism | [TENTH_SEAT_REVIEW.md](TENTH_SEAT_REVIEW.md) | Formal narrow protocol; ordinary helper challenge does not require this artifact. |
| Isolate writable dispatched work or recover worktree-specific failures | [WORKTREE_ISOLATION.md](WORKTREE_ISOLATION.md) | Git isolation mechanics; no merge/permission authority. |
| Test or tune a workflow with an agent scenario | [SIMULATION_DESIGN.md](SIMULATION_DESIGN.md) | Simulation/evaluation; plausible output is not production proof. |
| Plan/import a project into ProjectUpdater | [ROADMAP_AND_PROJECTUPDATER.md](ROADMAP_AND_PROJECTUPDATER.md) | ProjectUpdater representation; not the canonical task store. |
| Establish facts or evaluate a workflow/document/usability path | [RESEARCH.md](RESEARCH.md) | Evidence gathering/evaluation; no implementation authority by itself. |
| Track downside, reversibility, and mitigations | [RISK_AND_CHANGE.md](RISK_AND_CHANGE.md) | Risk analysis; does not create a separate approval system. |
| Capture a worthwhile discovery without expanding current scope | [EMERGENCE.md](EMERGENCE.md) | Discovery capture only. |
| Repair drift and learn from repeated failures | [REPAIR_AND_LEARNING.md](REPAIR_AND_LEARNING.md) | Repair/learning loop; findings do not silently become global policy. |
| Classify information as authority, task context, fact, Skill, flow, tool, or example | [INFORMATION_CLASSES.md](INFORMATION_CLASSES.md) | Information type, not lifecycle status or authority creation. |
| Keep project information trustworthy over time | [INFORMATION_LIFECYCLE.md](INFORMATION_LIFECYCLE.md) | Active/retired/archive lifecycle; not information classification. |
| Continue across sessions | [Context](../docs/CONTEXT.md) and [handoff template](../templates/handoff.md) | Continuation state/evidence only; does not expand task authority. |

## Adding or changing a method

Follow the anti-sprawl invariant in `AGENTS.md`.

Before creating a new active playbook file:

1. Name the existing document that would otherwise own the concept.
2. Show why extending that owner would make it less coherent.
3. Give the proposed method one distinct reusable job.
4. Link rather than copy shared rules from `AGENTS.md` or another owner.
5. Add one index entry that makes the non-overlap explicit.
6. If the new method supersedes an older one, merge useful material and retire or
   narrow the older file in the same work arc.

A new file is not evidence of a new capability. Fewer, clearer owners are
preferred to a larger library of partially overlapping instructions.

## Retained control plane and optional presentation

- **SQLite:** canonical mutable task state—atomic claims, leases, submissions,
  reviews, and task events.
- **LangGraph:** deterministic route selection from task/dependency state,
  policy, availability, helpers, and gates. Its checkpoint database is
  separate from MAPS task truth. It recommends; accountable agents act.
- **RnS:** deterministic restart/limit recovery. It relies on durable handoffs
  and hcom/session adapters rather than terminal authority.
- **hcom:** cross-provider messages, session control, and current RnS transport.
  Its own local state is not MAPS task authority.
- **WezTerm or any other terminal UI:** optional presentation only.

## Legacy audit and migration sources

The full legacy archive is temporary. Durable findings and selected source/tests
are being moved into:

- [Legacy Knowledge Audit](../migration/LEGACY_KNOWLEDGE_AUDIT.md)
- [Legacy Promotion Ledger](../migration/LEGACY_PROMOTION_LEDGER.md)
- [Future Ideas Backlog](../migration/FUTURE_IDEAS_BACKLOG.md) — promising deferred ideas preserved without making them active commitments
- [Legacy Removal Checklist](../migration/LEGACY_REMOVAL_CHECKLIST.md)
- `migration/legacy-runtime-source/` — first control-plane extraction
- `migration/legacy-knowledge-source/` — second execution/knowledge extraction

Migration snapshots are reference source only. Active runtime code must not
import or execute from them.

See [the source catalog](SOURCE_CATALOG.md) for earlier source mapping; where it
conflicts with the newer migration audit, the newer audit/ledger governs the
legacy-removal decision.
