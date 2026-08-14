# MultiAgentProject Lean

A provider-neutral workspace for building with Codex, Claude, or other coding
agents. It keeps MAP's durable methods and control plane while removing the
requirement for WezTerm as the agent-window cockpit.

## Start here

For your first task, [follow the canonical first-run route](docs/FIRST_RUN.md).
It starts with [AGENTS.md](AGENTS.md) and tells you exactly when to read current state,
the control plane, and a playbook method. Do not construct a second orientation
sequence from this README.

Resuming after a session break? Read [Current State](state/CURRENT.md) first;
it points to the latest durable coordination handoff.

For a project that spans sessions, multiple tasks, or multiple agents, use
[Project Bootstrap](playbook/PROJECT_BOOTSTRAP.md) before creating the first
implementation task. It follows a simple planning rule: inspect reality, define
DONE, plan backward, challenge the draft, then execute forward and adapt from
evidence.

Once oriented, create a task record from [the task template](templates/task.md) before a
multi-agent or consequential change and put reviews, decisions, and handoffs
in `work/` using the templates.

Setting up the retained runtime on a fresh clone? Follow
[Control-Plane Setup](docs/CONTROL_PLANE_SETUP.md) for SQLite, LangGraph, and
hcom installation, smoke tests, local state layout, and implementation
boundaries.

## What is deliberately retained

- A named owner, scope, output paths, and observable acceptance criteria.
- Independent review for medium- and high-risk changes.
- Risk-proportionate evidence and release checks.
- Compact handoffs and durable decisions when work spans sessions or tools.

## Runtime architecture retained

- **SQLite** is the canonical mutable task ledger: atomic claims, leases,
  submissions, review separation, and task events. It prevents two agents from
  successfully claiming the same task at once.
- **LangGraph** is the read-first dispatcher: it evaluates the task graph,
  policy, availability, helper capacity, and approval gates, then recommends
  the next route (`review`, `claim_or_assign`, `wait`, or `policy_gate`). Its
  checkpoint state is kept separately from MAPS task truth. It does not replace
  the Markdown roadmap or make autonomous product decisions.
- **RnS (Rise & Shine)** is the deterministic, reboot-safe limit/restart
  supervisor. Durable handoffs remain its foundation; it resumes or nudges a
  stopped session after provider limits reset.
- **hcom** remains the live communication and session-control bus required by
  the current RnS implementation and useful for cross-provider coordination.
  hcom's own local state is transport/session state, not MAPS task authority.

## What is deliberately removed from the active default

- A required WezTerm multiplexer and fixed visible startup roster.
- The assumption that every control-plane signal must become operator-facing
  terminal noise.
- Ceremony for small, low-risk, single-agent edits.

Use native Codex or Claude agent spawning where possible. hcom remains the
current durable session-control transport; WezTerm is optional presentation.
Neither grants authority.

## Layout

| Path | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | The active operating contract. |
| `docs/` | Short workflow, setup, and quality guidance. |
| `playbook/` | Active reusable methods: project bootstrap, roadmap/checklists, research, risk, discovery, and routing. |
| `templates/` | Task, review, handoff, and decision records. |
| [state/CURRENT.md](state/CURRENT.md) | Compact shared continuation context. |
| `work/` | Active task records and durable outputs. |
| `legacy/` | Original source, historical evidence, installer, and reference material. |

The original project working state was copied intact as far as filesystem
consistency allowed; a transient SQLite temporary file disappeared during the
copy and is not needed by this lean workflow. `legacy/` is a source library,
not a dismissal of the original work: the MAP runtime remains retained while
the startup cockpit is being decoupled from WezTerm.
