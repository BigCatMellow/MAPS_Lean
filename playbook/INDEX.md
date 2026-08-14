# Lean Project Playbook

These are active, provider-neutral methods harvested from the original MAP
system. Use the smallest method that fits the project. They govern work in this
repository; `legacy/` provides the full historical source material.

| Need | Use | Do not confuse it with |
| --- | --- | --- |
| Understand retained runtime controls | [CONTROL_PLANE.md](CONTROL_PLANE.md) | Treating a terminal pane or an agent window as authority. |
| Write instructions an agent can execute without guessing | [AGENT_GRADE_INSTRUCTIONS.md](AGENT_GRADE_INSTRUCTIONS.md) | Making prompts longer without making outcomes, boundaries, or proof clearer. |
| Apply tool/provider-specific operating guidance | [PROVIDER_AND_TOOL_GUIDANCE.md](PROVIDER_AND_TOOL_GUIDANCE.md) | Making MAPS depend on one vendor's UI or commands. |
| Route by actual model/harness capability | [MODEL_CAPABILITY_ROUTING.md](MODEL_CAPABILITY_ROUTING.md) | Assuming model brand, price, context size, or tool support proves competence. |
| Evaluate a workflow, document set, or usability path | [RESEARCH.md](RESEARCH.md) | Treating a low-risk evaluation as implementation authority. |
| Start a durable project | [PROJECT_BOOTSTRAP.md](PROJECT_BOOTSTRAP.md) | Creating a ticket-only folder. |
| Shape, assign, and finish a task | [TASK_LIFECYCLE.md](TASK_LIFECYCLE.md) | Assigning vague chat intent to an implementer. |
| Route work to the right agent/model | [HPOM_ROUTING.md](HPOM_ROUTING.md) | Giving a capable tool decision authority. |
| Use spawned helpers safely | [HELPERS_AND_COMMUNICATION.md](HELPERS_AND_COMMUNICATION.md) | Creating an unmanaged parallel workforce. |
| Test or tune the active workflow with an agent scenario | [SIMULATION_DESIGN.md](SIMULATION_DESIGN.md) | Treating a plausible output as proof of a usable process. |
| Plan a project or import it into ProjectUpdater | [ROADMAP_AND_PROJECTUPDATER.md](ROADMAP_AND_PROJECTUPDATER.md) | A prose plan that cannot be tracked. |
| Establish facts before acting | [RESEARCH.md](RESEARCH.md) | Model recall presented as verified truth. |
| Track downside and reversibility | [RISK_AND_CHANGE.md](RISK_AND_CHANGE.md) | A generic warning with no owner or mitigation. |
| Make a consequential decision or handle security/destruction | [DECISIONS_AND_SAFETY.md](DECISIONS_AND_SAFETY.md) | Treating access or model capability as authority. |
| Capture a worthwhile discovery | [EMERGENCE.md](EMERGENCE.md) | Silently expanding the current task. |
| Repair drift and learn from repeat failures | [REPAIR_AND_LEARNING.md](REPAIR_AND_LEARNING.md) | Repeating an unrecorded manual fix. |
| Keep a project brain trustworthy over time | [INFORMATION_LIFECYCLE.md](INFORMATION_LIFECYCLE.md) | Deleting history or loading all history by default. |
| Continue across sessions | [Context](../docs/CONTEXT.md) and [handoff template](../templates/handoff.md) | Keeping every old transcript in context. |

## Retained control plane and optional presentation

- **SQLite:** canonical mutable task state—atomic claims, leases, submission,
  independent review records, and LangGraph checkpoints.
- **LangGraph:** deterministic route selection from the task graph, policy,
  availability, helpers, and gates. It recommends; accountable agents act.
- **RnS:** deterministic restart/limit recovery. It relies on durable handoffs
  and currently uses hcom for session inspection, resume, and nudging.
- **hcom:** cross-provider messages, session control, and RnS transport.
- **WezTerm Command Center:** optional terminal presentation. Replace or omit
  it without removing the above controls.

## Original sources

The original full specifications and templates are retained under:

- `legacy/MAP-System/MAP_System/shared/hpom.md`
- `legacy/MAP-System/MAP_System/{PROJECT_BOOTSTRAPPING_SYSTEM.md,NEW_PROJECT_WIZARD.md,RESEARCH_SYSTEM.md,RISK_SYSTEM.md,CHANGE_CONTROL_SYSTEM.md}`
- `legacy/MAP-System/MAP_System/emergence/`
- `legacy/MAP-System/Projects/ProjectUpdater/shared/steps-outline-guide.md`

See [the source catalog](SOURCE_CATALOG.md) for the complete audit, including each portable source
that informed this playbook and the presentation/runtime separation.
