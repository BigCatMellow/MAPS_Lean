# MultiAgentProject Lean

A provider-neutral workspace for building with Codex, Claude, or other coding
agents. It keeps MAP's durable methods and control plane while removing the
requirement for WezTerm as the agent-window cockpit.

## Start here

For your first task, [follow the canonical first-run route](docs/FIRST_RUN.md).
It starts with [AGENTS.md](AGENTS.md) and tells you exactly when to read current
state, the control plane, and a playbook method. Do not construct a second
orientation sequence from this README.

Resuming after a session break? Read [Current State](state/CURRENT.md) first.

For a project that spans sessions, multiple tasks, or multiple agents, use
[Project Bootstrap](playbook/PROJECT_BOOTSTRAP.md) before creating the first
implementation task. It follows a simple planning rule: inspect reality, define
DONE, plan backward, challenge the draft, then execute forward and adapt from
evidence.

Once oriented, create a task record from [the task template](templates/task.md)
before a multi-agent or consequential change and put reviews, decisions, and
handoffs in `work/` using the templates.

For a fresh runtime setup, start with [Fresh Clone Setup](docs/FRESH_INSTALL.md).
For component-level installation and migration details, use
[Control-Plane Setup](docs/CONTROL_PLANE_SETUP.md).

## Active runtime

PR #16 promoted the reviewed replacement runtime to `main`.

- **SQLite task truth + AGI gate** — canonical task lifecycle, atomic claims,
  leases, durable submission authorship, scoped reservations, review separation,
  rework, and explicit policy state.
- **LangGraph routing** — read-first recommendations using explicit worker
  capability profiles and policy gates; checkpoint DB is separate from task truth.
- **hcom adapter** — project-isolated messaging/session transport; no task authority.
- **RnS recovery** — deterministic recovery of already-active, explicitly bound
  sessions with bounded retries and no WezTerm requirement.
- **Bounded local helpers** — Ollama text/draft work and scoped Aider editing;
  helpers cannot approve or complete parent tasks.
- **Fresh-clone setup/smoke** — preview-first installer and disposable end-to-end
  lifecycle verification.
- **Execution integrity** — immutable run/context binding, task/context staleness,
  writable/forbidden Git scope proof, run-budget checks, continuity-aware review,
  and optional criterion-level evidence.

The integration review is recorded in
[`work/reviews/RUNTIME_INTEGRATION_REVIEW.md`](work/reviews/RUNTIME_INTEGRATION_REVIEW.md).
The final active dependency sweep is recorded in
[`migration/FINAL_LEGACY_DEPENDENCY_SWEEP.md`](migration/FINAL_LEGACY_DEPENDENCY_SWEEP.md).

Latest removal-readiness verification on the cleanup branch passed **93/93 unit
tests**, SQLite/LangGraph smoke, installer checks, static/security/dependency
checks, and a mechanical scan of 50 active executable/config files with no
active dependency on `legacy/` or the curated migration snapshots.

## Core responsibility boundaries

```text
SQLite      = task truth / ownership / evidence
LangGraph   = routing recommendation + checkpoint memory
hcom        = communication / session control
RnS         = recovery of known active sessions
helpers     = bounded delegated work
integrity   = frozen execution contract + proof; no new authority
Markdown    = durable human-readable project record
WezTerm     = optional presentation
```

Capability never grants authority. A router recommendation, active hcom session,
helper result, recovery command, or run manifest does not by itself change MAPS
task truth.

## What is deliberately retained

- A named owner, scope, output paths, and observable acceptance criteria.
- Independent review where the active task/risk policy requires it.
- Risk-proportionate evidence and operator gates.
- Compact handoffs and durable decisions when work spans sessions or tools.

## What is deliberately removed from the active default

- A required WezTerm multiplexer and fixed visible startup roster.
- The assumption that every control-plane signal must become operator-facing
  terminal noise.
- Ceremony for small, low-risk, single-agent edits.
- A universal second `APPROVED → RELEASED` lifecycle.

## Layout

| Path | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Active operating contract. |
| `runtime/` | Provider-neutral active runtime implementation. |
| `tests/` | Active runtime regression tests. |
| `docs/` | Workflow, setup, and quality guidance. |
| `playbook/` | Reusable methods: planning, task lifecycle, research, risk, routing, repair. |
| `templates/` | Task, review, handoff, decision, context, worker/task examples. |
| [state/CURRENT.md](state/CURRENT.md) | Compact shared continuation state. |
| `work/` | Task records and durable outputs. |
| `migration/` | Curated source/evidence retained during promotion and removal proof. |
| `legacy/` | Historical original source; no longer an active execution dependency. |

`legacy/` is intentionally still present. The runtime is merged, current
preservation/privacy and active dependency gates pass, and the only remaining
migration action is a **separate explicit operator-approved deletion of
`legacy/`**.
