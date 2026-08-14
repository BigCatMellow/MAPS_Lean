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
[Control-Plane Setup](docs/CONTROL_PLANE_SETUP.md). The SQLite/AGI state slice
is now active under `runtime/`; LangGraph, hcom, and RnS promotion remain later
migration work.

## What is deliberately retained

- A named owner, scope, output paths, and observable acceptance criteria.
- Independent review for medium- and high-risk changes.
- Risk-proportionate evidence and release checks.
- Compact handoffs and durable decisions when work spans sessions or tools.

## Runtime status

- **SQLite — active:** `runtime/state/` is the canonical mutable task ledger for
  the promoted slice. It enforces the structural AGI `READY` gate, atomic
  claims/leases, durable submission authorship, review separation, rework, and
  task events. Local mutable state defaults to `.maps/state/maps.db`.
- **LangGraph — retained, not yet promoted:** planned read-first routing over
  canonical task state. Its checkpoints remain separate from MAPS task truth.
- **RnS (Rise & Shine) — retained, not yet promoted:** deterministic
  restart/provider-limit recovery based on durable handoff state.
- **hcom — retained, not yet promoted:** cross-provider communication/session
  transport. Its own state is not MAPS task authority.

The active state runtime imports nothing from `legacy/` or migration snapshots.
Those directories are evidence/reference until the remaining runtime layers are
promoted and the removal checklist is satisfied.

## What is deliberately removed from the active default

- A required WezTerm multiplexer and fixed visible startup roster.
- The assumption that every control-plane signal must become operator-facing
  terminal noise.
- Ceremony for small, low-risk, single-agent edits.

Use native Codex or Claude agent spawning where possible. hcom remains the
retained session-control transport design; WezTerm is optional presentation.
Neither grants authority.

## Layout

| Path | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | The active operating contract. |
| `runtime/` | Active provider-neutral runtime; currently SQLite task state + AGI gate. |
| `tests/` | Active runtime regression tests. |
| `docs/` | Short workflow, setup, and quality guidance. |
| `playbook/` | Active reusable methods: project bootstrap, task lifecycle, research, risk, discovery, and routing. |
| `templates/` | Task, review, handoff, decision, context, and task-contract examples. |
| [state/CURRENT.md](state/CURRENT.md) | Compact shared continuation context. |
| `work/` | Active task records and durable outputs. |
| `migration/` | Curated source/evidence retained while active runtime promotion continues. |
| `legacy/` | Historical original source; not an active runtime dependency. |

`legacy/` is intentionally still present. Delete it only after the migration
removal checklist confirms that required behavior, tests, provenance, and
privacy/dependency checks have safe destinations.
