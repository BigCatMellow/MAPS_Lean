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

The replacement runtime landed on `main` via PR #16 and has continued to grow
since. **Do not trust a PR number or test count in this README as current —
recover live state from GitHub and `work/coordination/README.md`, the durable
coordination entry point.** As of this edit, `main` carries the following
capability areas (non-exhaustive; see `runtime/` and `tests/` for the current
ground truth):

- **SQLite task truth + AGI gate** — canonical task lifecycle, atomic claims,
  leases, durable submission authorship, scoped reservations, review separation,
  rework, and explicit policy state.
- **LangGraph routing** — read-first recommendations using explicit worker
  capability profiles and policy gates; checkpoint DB is separate from task truth.
- **hcom adapter** — project-isolated messaging/session transport; no task authority.
- **RnS recovery** — deterministic recovery of already-active, explicitly bound
  sessions with bounded retries, `run_id` binding, and advisory (non-gating)
  environment-equivalence evidence surfacing; no WezTerm requirement.
- **Bounded local helpers** — Ollama text/draft work and scoped Aider editing;
  helpers cannot approve or complete parent tasks.
- **Fresh-clone setup/smoke** — preview-first installer and disposable end-to-end
  lifecycle verification.
- **Execution integrity** — immutable run/context binding, task/context staleness,
  writable/forbidden Git scope proof, run-budget checks, continuity-aware review,
  and optional criterion-level evidence.
- **Operational learning (Storage-0)** — append-only, CANDIDATE-only lesson
  persistence; promotion/retirement authority is operator-only and not yet
  mechanically implemented (design record: `work/notes/2026-08-17-operational-learning-authority-design.md`).
- **Context Builder Stage 2 retrieval** — evaluated candidates including a
  local `fastembed` embedding-based retriever, excluded from core CI (see
  `runtime/requirements.txt` and the review finding on a missing semantic-eval
  CI lane).
- **Branch protection on `main`** — PR-only, required Runtime CI status check,
  no force-push/delete. Independent-review enforcement beyond CI is not yet
  mechanically enforced; see issue #61.

The original integration review is recorded in
[`work/reviews/RUNTIME_INTEGRATION_REVIEW.md`](work/reviews/RUNTIME_INTEGRATION_REVIEW.md).
The final active dependency sweep is recorded in
[`migration/FINAL_LEGACY_DEPENDENCY_SWEEP.md`](migration/FINAL_LEGACY_DEPENDENCY_SWEEP.md).
Both describe `main` as of PR #16, not current `main` — check `tests/` and CI
for the current test count rather than trusting a number here.

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
