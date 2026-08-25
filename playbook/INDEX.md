# Lean Project Playbook

These are the active, provider-neutral MAPS methods. Use the smallest method
that fits the project. Historical behavior worth retaining is curated under
`migration/`; ordinary agents should not need the old `legacy/` tree.

| Need | Use | Do not confuse it with |
| --- | --- | --- |
| Understand retained runtime controls | [CONTROL_PLANE.md](CONTROL_PLANE.md) | Treating a terminal pane or an agent window as authority. |
| Install/verify SQLite, LangGraph, and hcom on a fresh clone | [Control-Plane Setup](../docs/CONTROL_PLANE_SETUP.md) | Combining their databases or letting transport/routing become task authority. |
| Plan installing/targeting MAPS's control plane at an external project's repo | [Portable Deployment roadmap](../work/roadmaps/agent-harness-capabilities/06-portable-deployment.md) | Assuming `scripts/install_maps.sh` can already target a repo other than the one it ships in — it cannot. |
| Turn a concise operator request into a bounded agent-ready contract | [REQUEST_COMPILATION.md](REQUEST_COMPILATION.md) | Making prompts longer, inventing permission, or creating a second task authority. |
| Decide whether instructions are formally ready for execution | [AGI_STANDARD.md](AGI_STANDARD.md) | Treating a capable model's ability to guess as proof the instruction is good. |
| Check whether self-selected work is the right work before shaping it | [PROGRAM_STEERING.md](PROGRAM_STEERING.md) | Treating an empty issue queue as an empty backlog, or AGI readiness as proof the task itself is worth doing. |
| Step back across a work arc and check the roadmap itself is still on track, or decide to pivot | [ROADMAP_TRAJECTORY_CHECK.md](ROADMAP_TRAJECTORY_CHECK.md) | Re-deriving per-task steering (that's PROGRAM_STEERING.md) or treating a pivot decision as something to wait on approval for. |
| Test a consequential claim that an independent review approved with *no case articulated against it* | [TENTH_SEAT_REVIEW.md](TENTH_SEAT_REVIEW.md) | Ordinary independent review (that already runs on every PR), or treating a minority report as a veto or as a second source of status truth. |
| Write instructions an agent can execute without guessing | [AGENT_GRADE_INSTRUCTIONS.md](AGENT_GRADE_INSTRUCTIONS.md) | Making prompts longer without making outcomes, boundaries, or proof clearer. |
| Freeze context/scope for a consequential run, handle conflicts, or preserve reviewer independence | [EXECUTION_INTEGRITY.md](EXECUTION_INTEGRITY.md) | Turning every tiny edit into a run-manifest ceremony. |
| Apply tool/provider-specific operating guidance | [PROVIDER_AND_TOOL_GUIDANCE.md](PROVIDER_AND_TOOL_GUIDANCE.md) | Making MAPS depend on one vendor's UI or commands. |
| Route by actual model/harness capability | [MODEL_CAPABILITY_ROUTING.md](MODEL_CAPABILITY_ROUTING.md) | Assuming model brand, price, context size, or tool support proves competence. |
| Evaluate a workflow, document set, or usability path | [RESEARCH.md](RESEARCH.md) | Treating a low-risk evaluation as implementation authority. |
| Start a durable project | [PROJECT_BOOTSTRAP.md](PROJECT_BOOTSTRAP.md) | Creating a ticket-only folder. |
| Shape, assign, and finish a task | [TASK_LIFECYCLE.md](TASK_LIFECYCLE.md) | Assigning vague chat intent to an implementer. |
| Route work to the right agent/model | [HPOM_ROUTING.md](HPOM_ROUTING.md) | Giving a capable tool decision authority. |
| Use spawned helpers safely | [HELPERS_AND_COMMUNICATION.md](HELPERS_AND_COMMUNICATION.md) | Creating an unmanaged parallel workforce. |
| Isolate a dispatched agent's writable repo work, sync a branch with `main` mid-PR, or recover from an empty-commit review-evidence break | [WORKTREE_ISOLATION.md](WORKTREE_ISOLATION.md) | Letting a helper `git checkout`/`stash`/`clean` the shared clone, or assuming worktree isolation grants merge authority. |
| Test or tune the active workflow with an agent scenario | [SIMULATION_DESIGN.md](SIMULATION_DESIGN.md) | Treating a plausible output as proof of a usable process. |
| Plan a project or import it into ProjectUpdater | [ROADMAP_AND_PROJECTUPDATER.md](ROADMAP_AND_PROJECTUPDATER.md) | A prose plan that cannot be tracked. |
| Establish facts before acting | [RESEARCH.md](RESEARCH.md) | Model recall presented as verified truth. |
| Track downside and reversibility | [RISK_AND_CHANGE.md](RISK_AND_CHANGE.md) | A generic warning with no owner or mitigation. |
| Make a consequential decision or handle security/destruction | [DECISIONS_AND_SAFETY.md](DECISIONS_AND_SAFETY.md) | Treating access or model capability as authority. |
| Capture a worthwhile discovery | [EMERGENCE.md](EMERGENCE.md) | Silently expanding the current task. |
| Repair drift and learn from repeat failures | [REPAIR_AND_LEARNING.md](REPAIR_AND_LEARNING.md) | Repeating an unrecorded manual fix. |
| Name what kind of information something is (authority, task context, fact, Skill, flow, tool, example) | [INFORMATION_CLASSES.md](INFORMATION_CLASSES.md) | Confusing this with lifecycle state (active/retired/archived), or treating a Skill/fact as authority. |
| Keep a project brain trustworthy over time | [INFORMATION_LIFECYCLE.md](INFORMATION_LIFECYCLE.md) | Deleting history or loading all history by default. |
| Continue across sessions | [Context](../docs/CONTEXT.md) and [handoff template](../templates/handoff.md) | Keeping every old transcript in context. |

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
