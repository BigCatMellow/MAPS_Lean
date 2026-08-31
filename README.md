# MultiAgentProject Lean

MAPS_L is a provider-neutral operating system around capable AI workers: task
truth, bounded authority, orchestration, reusable methods, verification,
recovery, and durable evidence without requiring a specific model or terminal UI.

## Start here

For repository work, follow [`docs/FIRST_RUN.md`](docs/FIRST_RUN.md). It begins
with [`AGENTS.md`](AGENTS.md), the **single repository-wide operating contract**,
then routes you to the approved roadmap/task and one relevant method.

Do **not** read the repository tree broadly as orientation.

### Fast routes

- New durable project/work arc → [Project Bootstrap](playbook/PROJECT_BOOTSTRAP.md)
- Select a reusable method → [Playbook index](playbook/INDEX.md)
- Find a durable `work/` record class → [Work routing index](work/README.md)
- Resume cross-session work → [Current State](state/CURRENT.md), then its linked handoff and live GitHub
- Role-bound browser coordination / current PR state → [Coordination](work/coordination/README.md), then live GitHub
- Runtime/control-plane setup → [Fresh Clone Setup](docs/FRESH_INSTALL.md)
- Capability/roadmap question → [Roadmap router](work/roadmaps/README.md)

## Documentation model

```text
AGENTS.md              = global operating contract
approved roadmap/task  = scoped authority + exact work
runtime task state     = mutable task/execution truth
playbook/docs          = subordinate methods/guidance
work/state             = evidence + continuation
migration/legacy       = reference/history
```

Normal work should need:

```text
AGENTS.md + approved roadmap/task + one relevant method
```

Add other material only when the task actually needs it. Repeated chain-reading
is a routing/consolidation defect, not normal process.

## Core responsibility boundaries

| Component | Owns |
| --- | --- |
| SQLite task state | task truth, ownership, evidence, lifecycle |
| LangGraph | routing recommendation/checkpoint state |
| hcom | communication/session transport |
| RnS | bounded recovery of known active sessions |
| helpers | bounded delegated work |
| execution integrity | frozen execution contract + proof |
| Markdown | durable human/agent-readable records |
| terminal UI | optional presentation only |

Capability never grants authority. Verify current production wiring in code,
tests, CI, and the relevant capability evidence rather than trusting a dated
README inventory.

## Repository layout

| Path | Purpose |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Sole repository-wide operating contract |
| [`docs/FIRST_RUN.md`](docs/FIRST_RUN.md) | Lowest-cost onboarding route |
| [`playbook/INDEX.md`](playbook/INDEX.md) | Reusable-method router |
| [`work/README.md`](work/README.md) | Durable-record router |
| [`work/roadmaps/README.md`](work/roadmaps/README.md) | Roadmap/capability router |
| [`work/coordination/README.md`](work/coordination/README.md) | Role-bound coordination entry; live state remains on GitHub |
| [`state/CURRENT.md`](state/CURRENT.md) | Compact cross-session orientation snapshot |
| `runtime/` | Active provider-neutral runtime implementation |
| `tests/` | Active regression/evaluation tests |
| `templates/` | Record structures; not authority |
| `migration/` | Curated promotion/removal evidence |
| `legacy/` | Historical source; not an active execution dependency |

For the visual relationship graph, see [`obsidian/README.md`](obsidian/README.md).
Links are navigation claims, not proof of authority, freshness, or truth.
