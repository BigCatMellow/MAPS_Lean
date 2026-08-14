# Source Audit Catalog

Audit scope: the original MAP root systems, operating notes, templates,
Guidelines, ProjectUpdater documentation, emergence materials, and proven
artifacts were inventoried on 2026-08-13. This catalog makes the selection
traceable rather than claiming the active playbook is the whole source tree.

## Promoted as active, condensed practice

| Original source | Active destination | Portable value |
| --- | --- | --- |
| `shared/hpom.md`, `AGENT_PERMISSION_LEVELS.md` | `HPOM_ROUTING.md`, `DECISIONS_AND_SAFETY.md` | Model/cost routing separated from authority. |
| `PROJECT_BOOTSTRAPPING_SYSTEM.md`, `NEW_PROJECT_WIZARD.md`, `notes/brain-organization-guide.md` | `PROJECT_BOOTSTRAP.md` | Build intent, standards, assumptions, risks, decision paths, and discovery capacity before tasks. |
| `notes/task-authoring-guide.md`, `notes/architect-agent-guide.md`, `notes/state-machine-guardrails.md` | `TASK_LIFECYCLE.md`, `templates/task.md` | Shape task records, write ownership boundaries, READY gate, testable completion. |
| `notes/helper-agent-guide.md`, `notes/communication-guide.md`, `notes/communication-architecture.md`, `notes/role-contracts.md` | `HELPERS_AND_COMMUNICATION.md` | Bounded helpers, accountable ownership, direct-but-recorded communication. |
| `notes/review-guide.md`, `templates/review*.md`, `notes/release-path-checklist.md` | `docs/CHECKS_AND_BALANCES.md`, `TASK_LIFECYCLE.md`, `templates/review.md` | Independent, risk-tiered evidence; visual and release-path checks. |
| `RESEARCH_SYSTEM.md`, `templates/research/*` | `RESEARCH.md` | Evidence-led claims, source quality, assumptions, time sensitivity. |
| `RISK_SYSTEM.md`, `CHANGE_CONTROL_SYSTEM.md`, `templates/RISK_REGISTER_TEMPLATE.md`, `templates/release-checklist.md` | `RISK_AND_CHANGE.md`, `DECISIONS_AND_SAFETY.md` | Risk ownership, proportional release evidence, rollback. |
| `DECISION_AUTHORITY_SYSTEM.md`, `DECISION_CLASSES.md`, `DESTRUCTIVE_ACTION_POLICY.md`, `SECURITY_PERMISSIONS_SYSTEM.md` | `DECISIONS_AND_SAFETY.md`, `templates/decision.md` | Proper escalation, explicit decisions, safety boundaries. |
| `emergence/*`, `RETROSPECTIVE_SYSTEM.md`, `SELF_REPAIR_SYSTEM.md`, `notes/operational-learning-guide.md` | `EMERGENCE.md`, `REPAIR_AND_LEARNING.md` | Discovery without scope creep; repair and prevention loops. |
| `CONTEXT_SYSTEM.md`, `notes/context-routing-guide.md`, `notes/brain-compaction-guide.md`, `ARCHIVE_RETENTION_SYSTEM.md`, `notes/retrieval-capsule-guide.md`, `notes/documentation-style-guide.md` | `docs/CONTEXT.md`, `INFORMATION_LIFECYCLE.md` | Small, trustworthy continuation context and retained history. |
| `Projects/ProjectUpdater/shared/steps-outline-guide.md` | `ROADMAP_AND_PROJECTUPDATER.md` | Markdown plan as both roadmap and import-ready checklist. |

## Retained as reference-only implementation

| Area | Why not active by default |
| --- | --- |
| SQLite claims, task graph, migrations, validators, and release scripts | Retained control plane; preserve canonical state and prevent concurrent lifecycle races. |
| LangGraph runner | Retained read-first dispatcher; it turns task/roadmap state into an operational next-route recommendation. Autonomous mutation loops remain optional. |
| RnS and limit/context rotation supervisors | Retained recovery plane; RnS wakes/nudges sessions after limits and relies on handoffs. |
| hcom | Retained current message/session-control transport, including RnS resume/nudge operations. |
| WezTerm, Command Center UI, fixed roster, terminal watchers | Presentation/cockpit choices. WezTerm is the component intentionally made optional. |
| Cross-PC authority/gateway and remote-host notes | Specific to the former deployment topology. |
| Simulation papers, task artifacts, event logs, historical research | Provenance and examples, not startup instructions. |

## Templates intentionally added next

The condensed starter templates cover task, review, handoff, and decision.
When a project invokes the corresponding playbook method, add the matching
specialized record from `templates/`: project brief, requirements, risk,
research brief, claim-evidence matrix, roadmap, repair record, or retrospective.
