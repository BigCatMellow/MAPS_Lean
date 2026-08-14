# MAP 2.0 Implementation Research Package

## Executive summary

I converted the research into a **repo-ready set of ten Markdown files** organized for direct placement under:

```text
Source/MAP_System/docs/map2/
```

The complete package is here:

**[Download the full MAP 2.0 implementation guide package](sandbox:/mnt/data/MAP_2.0_Implementation_Guides.zip)**

The guides are intentionally marked **PROPOSAL / IMPLEMENTATION GUIDE**, not canonical MAP policy. That distinction matters because MAP's current project brief makes the operator the authority over policy, scope, high-authority approvals, veto, and stop control, while helpers and control systems do not acquire authority merely by executing or storing state. fileciteturn5file0L2-L2

The main conclusion of the research is that MAP should **not** be rewritten around a new agent framework. The stronger path is to preserve MAP's governance model and progressively strengthen the infrastructure below it:

```text
                     OPERATOR
                        │
                        ▼
                 Command Center
                        │
                        ▼
              ┌─────────────────┐
              │      mapd       │
              │ Host / Control  │
              │      API        │
              └────────┬────────┘
                       │
        identity ─ policy ─ approvals
                       │
                       ▼
              ┌─────────────────┐
              │ Canonical State │
              │    map.db       │
              │ + event stream  │
              └────────┬────────┘
                       │
                 projections
            ┌──────────┼──────────┐
            ▼          ▼          ▼
       task JSON   task graph  current state

                       │
                       ▼
              Durable Execution
              /       |        \
       LangGraph   map-flow   Temporal POC
                       │
                       ▼
                  AgentRuntime
             /         |          \
          Claude     Codex       Prime...
             │         │           │
             └──── isolated ───────┘
                   workspaces

                       │
             skills / context / MCP
                       │
                       ▼
                project/tooling

        Everything observable through OTel
                       │
                       ▼
                 Harness Evals
                       │
                       ▼
               refine.propose
             review / operator gate
```

This direction builds directly on MAP rather than discarding it. MAP already has SQLite-backed claims and leases, a LangGraph router, a custom LangGraph checkpointer, an autonomous agent loop, generated/readable mirrors, mirror validation, and even a fail-closed single-writer authority/mirror mechanism. fileciteturn10file0L2-L2 fileciteturn11file0L2-L2 fileciteturn12file0L2-L2 fileciteturn13file0L2-L2 fileciteturn16file0L2-L2

The **highest-priority architectural change** is not Temporal, Prime Agent, MCP, containers, or additional agents. It is establishing one transactional authority seam. MAP's current architecture still describes synchronization across SQLite, task JSON, task graph, and JSONL events; `submit_task()` currently performs the task transition and then separately performs secondary event writes. That leaves a class of crash/reconciliation problems that a transactional `mapd` command layer plus generated projections can eliminate. fileciteturn7file0L2-L2 fileciteturn10file0L2-L2

The recommended priority is therefore:

| Priority | MAP 2.0 area | Why |
|---|---|---|
| **P0** | State authority + event stream | Removes split-brain and dual-write failure classes |
| **P0** | Typed `mapd` Host API | Creates one enforceable mutation boundary |
| **P0** | Operator approval records | Prevents infrastructure capability from becoming authority |
| **P1** | Generated projections | Makes JSON/Markdown views rebuildable rather than competing writers |
| **P1** | Durable execution | Makes crashes and long waits routine rather than exceptional |
| **P1** | Deterministic `map-flow` | Removes known procedures from repeated LLM reasoning |
| **P1** | `AgentRuntime` + worktrees | Makes workers interchangeable and concurrent edits isolated |
| **P1** | Policy-as-code + budgets | Makes permissions and autonomy limits mechanical |
| **P2** | Agent Skills | Reduces procedural context |
| **P2** | Context Builder/search | Makes context selection an engineered subsystem |
| **P2** | OpenTelemetry + evals | Makes improvements measurable |
| **P3** | `refine.propose` | Enables controlled harness evolution only after evaluation exists |
| **P3** | MCP/A2A/Prime/AgentFile adapters | Adds interoperability without weakening the center |

That ordering is deliberate. Prime Agent demonstrates the value of persistent sessions, detached runtimes, persistent child agents, completion gates, budgets, and harness refinement, but its own Factorio case study also provides a useful warning: a refinement mechanism can learn to improve an exploit when the objective itself is flawed. MAP's stricter authority and independent-review model should therefore sit **above** Prime-style self-improvement rather than be replaced by it. citeturn21view0

## Included implementation guides

The ZIP preserves the proposed repo directory structure, so it can be extracted and its `Source/` directory compared or copied into the repository.

| Suggested repo path | Contents | Direct file |
|---|---|---|
| `Source/MAP_System/docs/map2/README.md` | Executive architecture, priorities, hard invariants, directory design, first implementation slice | [Open README](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/Source/MAP_System/docs/map2/README.md) |
| `Source/MAP_System/docs/map2/STATE_AUTHORITY_AND_MAPD.md` | Event stream, projections, idempotency, optimistic versions, JSON-RPC, identity/auth model, CLI and failure injection | [Open state/mapd guide](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/Source/MAP_System/docs/map2/STATE_AUTHORITY_AND_MAPD.md) |
| `Source/MAP_System/docs/map2/DURABLE_EXECUTION_AND_MAP_FLOW.md` | Temporal vs LangGraph, POC plans, checkpoint separation, Lobster vs native flows, release-flow YAML | [Open durable execution guide](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/Source/MAP_System/docs/map2/DURABLE_EXECUTION_AND_MAP_FLOW.md) |
| `Source/MAP_System/docs/map2/AGENT_RUNTIME_AND_ISOLATION.md` | `AgentRuntime`, adapters, runtime registry, Git worktrees, container patterns, persistent helpers, snapshots | [Open runtime/isolation guide](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/Source/MAP_System/docs/map2/AGENT_RUNTIME_AND_ISOLATION.md) |
| `Source/MAP_System/docs/map2/SKILLS_CONTEXT_AND_MEMORY.md` | Agent Skills layout, `SKILL.md`, Context Builder, FTS5/vector search, context packets, noncanonical memory | [Open skills/context guide](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/Source/MAP_System/docs/map2/SKILLS_CONTEXT_AND_MEMORY.md) |
| `Source/MAP_System/docs/map2/SECURITY_POLICY_AND_BUDGETS.md` | Cedar/OPA/Casbin comparison, Cedar examples, operator approvals, capabilities, budgets, circuit breakers | [Open security guide](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/Source/MAP_System/docs/map2/SECURITY_POLICY_AND_BUDGETS.md) |
| `Source/MAP_System/docs/map2/OBSERVABILITY_EVALS_AND_REFINEMENT.md` | OTel traces, metrics, eval formats, historical-case conversion, `refine.propose`, promotion gates | [Open observability/evals guide](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/Source/MAP_System/docs/map2/OBSERVABILITY_EVALS_AND_REFINEMENT.md) |
| `Source/MAP_System/docs/map2/INTEROPERABILITY_AND_ADOPTION.md` | Prime, MCP, A2A, AgentFile, OSS adoption matrix, adapter contracts, dependency strategy | [Open interoperability guide](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/Source/MAP_System/docs/map2/INTEROPERABILITY_AND_ADOPTION.md) |
| `Source/MAP_System/docs/map2/MIGRATION_RUNBOOK.md` | Phase ordering, entrance/exit gates, global checklist, implementation backlog, cutover and rollback | [Open migration runbook](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/Source/MAP_System/docs/map2/MIGRATION_RUNBOOK.md) |
| `Source/MAP_System/docs/map2/SOURCES.md` | Primary research-source registry and re-verification checklist | [Open source registry](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/Source/MAP_System/docs/map2/SOURCES.md) |

A machine-readable manifest with SHA-256 hashes for the generated documents is also included:

[Open manifest.json](sandbox:/mnt/data/MAP_2.0_Implementation_Guides/manifest.json)

The package contains roughly **107 KB of Markdown** across the ten documents.

## Most consequential implementation decisions

### Make runtime state single-authority, with projections below it

The guide deliberately does **not** recommend pure event sourcing in which every read requires replaying the entire event history. Instead, it recommends a practical hybrid:

```text
                 authoritative transaction
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
       current-state rows       append-only
          in SQLite             map_events
             │                       │
             └───────────┬───────────┘
                         ▼
                   projections
```

This gives MAP efficient current-state queries while retaining a durable causal history.

The proposed mutation transaction is approximately:

```python
BEGIN IMMEDIATE

check_idempotency()
check_expected_version()
authorize_authenticated_actor()
validate_lifecycle_transition()

update_current_state()
append_canonical_event()
save_idempotency_result()

COMMIT
```

Then, and only then:

```text
task JSON
task graph
events.jsonl
current-state generated sections
```

are refreshed.

SQLite documents that `BEGIN IMMEDIATE` begins the write transaction immediately, making it useful for controlling contention in this local-first design, although callers still have to handle `SQLITE_BUSY`. citeturn15search1

The guide adds:

```text
tasks.runtime_version
map_events
command_dedup
projection_cursors
```

and supplies concrete SQL schemas for each.

The important shift is:

```text
TODAY

SQLite ↔ JSON ↔ graph ↔ JSONL
       synchronization problem

MAP 2.0

mapd → SQLite + canonical event
             ↓
         projections
        ↙    ↓     ↘
      JSON graph JSONL
```

That is directly aligned with the recurring state-authority problem MAP itself identifies and with its existing move toward database-generated active state. fileciteturn5file0L2-L2 fileciteturn6file0L2-L2

### Make `mapd` an application authority boundary, not merely another daemon

The guide recommends first extracting:

```text
mapd.commands
mapd.queries
mapd.lifecycle
mapd.authz
mapd.events
mapd.idempotency
```

as an **in-process application layer**.

Only after existing scripts are routed through that seam should MAP add:

```text
Unix socket
    ↓
JSON-RPC 2.0
    ↓
same mapd.commands
```

That avoids the common mistake of building a network daemon while leaving five old code paths writing the database directly.

JSON-RPC 2.0 is suitable as a lightweight transport-independent RPC envelope, but its request `id` is only request/response correlation; the guide therefore adds a distinct business idempotency key for retry safety. citeturn21view1

The server constructs authenticated identity:

```python
RequestContext(
    actor_id=...,
    actor_kind=...,
    session_id=...,
    runtime_id=...,
    workspace_id=...,
    scopes=...,
    trace_id=...,
)
```

The model cannot obtain authority by saying:

```json
{"actor_id": "bigboss"}
```

That value is never trusted.

This builds naturally on MAP's existing `map_authority.py` and fail-closed mirror guard instead of discarding those investments. fileciteturn13file0L2-L2 fileciteturn16file0L2-L2

### Test Temporal rather than prematurely migrating to it

The guide does **not** say “replace LangGraph with Temporal.”

MAP already has LangGraph routing and a custom persisted agent loop. fileciteturn11file0L2-L2 fileciteturn12file0L2-L2

LangGraph's persistence/checkpoint model supports durable graph state and human-in-the-loop interrupts; importantly, its interrupt semantics mean a node can begin again on resume, so side effects around an interrupt must be idempotent or placed in appropriately separated tasks/nodes. citeturn16search3turn16search1turn16search10

Temporal offers a stronger dedicated durable-execution model around persisted workflows, Activities, retries, signals, timers, task queues, and recovery after worker/process failures. citeturn17search0turn17search9

So the guide specifies an actual experiment:

```text
same workflow
same failure injections
same acceptance criteria

          ┌──────────────┐
          │ crash matrix │
          └──────┬───────┘
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
 LangGraph POC         Temporal POC
       │                   │
       └─────────┬─────────┘
                 ▼
       measured scorecard
                 │
                 ▼
         operator decision
```

The failure scenarios include:

```text
worker killed before claim
worker killed after commit but before reply
orchestrator restart
provider outage
long operator pause
duplicate signal/message
budget exhaustion
stale authority host
review → changes → rework
```

One concrete cleanup should happen even before that decision: MAP's current custom LangGraph checkpointer stores framework-specific checkpoint blobs inside `map.db`. The guide recommends moving those into a runtime database and retaining only a MAP execution reference in canonical state. fileciteturn14file0L2-L2

### Move routine ceremony into deterministic flows

The research strongly supports separating “judgment” from “known procedure.”

The proposed division is:

```text
Needs judgment?
      │
   yes│                 no
      ▼                  ▼
    Agent             map-flow
```

Good `map-flow` candidates include:

```text
release verification sequence
projection rebuild
sandbox lifecycle
health/reconciliation
archive jobs
context rotation mechanics
fresh-install verification
```

OpenClaw's Lobster is worth prototyping because it already provides workflow primitives for commands/pipelines, conditions, retries, timeouts, errors, and human approvals. citeturn16search9

But the guide does not assume Lobster should win. It specifies a direct comparison:

```text
release flow in Lobster
vs.
release flow in thin MAP-native executor
```

using the same Host API and correctness tests.

That is especially relevant to MAP because the repository's own current-state snapshot documented a large set of independently approved work waiting at release. fileciteturn6file0L2-L2 The goal is not to weaken the release gate; it is to automate the deterministic mechanics and preserve human/agent judgment only where a factual judgment is genuinely needed.

### Isolate work before trying to sandbox everything

The implementation path is intentionally staged:

```text
L0 shared checkout        legacy
          ↓
L1 per-task Git worktree  first target
          ↓
L2 rootless container     stronger isolation
          ↓
L3 remote container/VM    high-risk option
```

Git worktrees give concurrent agents separate working trees and index/HEAD state. Rootless Docker/Podman can then add process, capability, filesystem, resource, and network boundaries without requiring rootful container operation. Docker explicitly supports a rootless daemon/container mode and also warns that ordinary access to the Docker daemon can carry root-level consequences, which is why the guide bans mounting the Docker socket into workers. citeturn14search0turn14search4turn14search12

The guide makes `output_paths` mechanically enforceable at submit time:

```text
base commit
    ↓
git diff + untracked files
    ↓
normalize changed paths
    ↓
all inside task.output_paths?
     /                  \
   yes                  no
    ↓                    ↓
submit              SCOPE_VIOLATION
```

That turns an existing MAP task convention into a hard runtime property.

## Skills, context, policy, and evaluation

### Adopt Agent Skills directly

The guide recommends standard:

```text
Source/.agents/skills/
```

folders rather than another MAP-specific skill format.

The Agent Skills specification uses a `SKILL.md` with optional supporting scripts, references, and assets, and is designed around progressive disclosure so an agent can first discover lightweight metadata and load the heavier procedural content only when needed. citeturn16search0turn16search5

That aligns almost exactly with MAP's existing Context System, which already says each task should receive a bounded context packet and defines Required, Optional, and Excluded material. fileciteturn8file0L2-L2

The package includes a concrete `map-task/SKILL.md` example and recommends beginning with:

```text
map-task
map-review
map-release
map-context
map-repair
map-research
map-handoff
```

Skills tell the worker **how to use MAP**.

They never tell MAP **what the worker is authorized to do**.

### Make Context Builder a real subsystem

The proposed retrieval stack is:

```text
exact ID / path lookup
        +
SQLite FTS5
        +
optional semantic retrieval
        +
canonicality/freshness metadata
        ↓
bounded context packet
```

SQLite FTS5 provides the baseline full-text search capability, while `sqlite-vec` is recommended only as an optional experiment because its project currently identifies itself as pre-v1 and subject to breaking changes. citeturn15search2turn15search0

Every source gets a class such as:

```text
CANONICAL_POLICY
CANONICAL_DECISION
CANONICAL_TASK
CURRENT_DERIVED
VERIFIED_RESEARCH
HISTORICAL
NONCANONICAL_MEMORY
UNTRUSTED_EXTERNAL
```

The critical rule is:

> `NONCANONICAL_MEMORY` can improve retrieval, but it can never satisfy a requirement for canonical evidence.

That directly preserves MAP's existing distinction between context compression and decisions about what is canonical. fileciteturn8file0L2-L2

Letta's AgentFile provides useful design ideas for portable agent/session state, including packaging memory/tool/session configuration while excluding live secret values from exported state, but the guide deliberately borrows the portability idea **without making imported memory authoritative**. citeturn20search0

### Put policy under agents, not only in their instructions

MAP already has a strong least-permission conceptual security model and explicitly states that permission changes require command-center authority. fileciteturn9file0L2-L2

The guide converts that into:

```text
principal
action
resource
request context
     ↓
PolicyEngine
     ↓
ALLOW / DENY / APPROVAL_REQUIRED
```

Cedar is the preferred semantic POC because its authorization model is explicitly organized around principal/action/resource/context and its documentation addresses software agents acting on behalf of users. OPA is the recommended comparison/fallback because it is a general-purpose policy engine with a mature policy/testing model. citeturn19search0turn19search7

The included Cedar examples cover:

```text
self-review prohibition
helper release prohibition
operator-only authority changes
```

but they are labeled conceptual and should be validated against the actual Cedar toolchain before production use.

High-impact decisions also require a canonical approval object:

```text
operator approval
    │
    ├── exact proposal SHA-256
    ├── scope
    ├── expiry
    └── single-use/consumption
```

So even possession of an operator-class identity cannot accidentally approve a different policy payload.

### Bound autonomy explicitly

The package includes schemas for:

```text
token limits
turn limits
wall-clock limits
tool-call limits
helper count
helper depth
concurrency
known provider cost
```

and separates:

```text
retry
```

from:

```text
circuit breaker
```

A policy rejection, scope violation, version conflict, missing authority approval, or destructive-action confirmation requirement is **not** a transient failure and therefore should not enter an automatic retry loop.

### Instrument first, refine later

OpenTelemetry provides the vendor-neutral observability layer, including current GenAI semantic-convention fields for model/tool/token-related operations. The guide recommends standard OTel fields where applicable plus a stable `map.*` namespace for task, runtime, event, flow, context, skill, policy, budget, and approval identity. citeturn18search9turn18search10

The key separation is:

```text
map_events = canonical audit/lifecycle history
OTel       = noncanonical behavioral telemetry
```

Losing telemetry must never make MAP incorrect.

Then the guide creates a real harness eval system using:

```text
control-plane deterministic cases
fault-injection cases
runtime cases
context/retrieval cases
agentic verifier cases
historical MAP regressions
```

The highest-value move is converting actual MAP failures into permanent regression cases:

```text
orphan task
self-review
stale mirrors
ID collision
missing acceptance criteria
output-path violation
release friction
budget-limit continuation
helper authority attempt
stale authority
dual-write crash
```

Only after that foundation does the guide enable:

```text
refine.propose
```

whose lifecycle is:

```text
observation
   ↓
proposal + explicit hypothesis
   ↓
evaluation
   ↓
independent review
   ↓
operator approval if authority/security/policy
   ↓
apply
   ↓
verify
   ↓
retain or rollback
```

This is the safer version of the continual-harness idea demonstrated by Prime Agent. citeturn21view0

## Migration and safety posture

The generated runbook recommends this migration order:

```text
Foundation
    ↓
mapd command seam
    ↓
projection cutover
    ↓
durable execution + map-flow
    ↓
AgentRuntime + worktree isolation
    ↓
policy + budgets
    ↓
Agent Skills + Context Builder
    ↓
OpenTelemetry + evaluation
    ↓
refinement + MCP/A2A/Prime interoperability
```

That order prevents several dangerous inversions.

In particular, it avoids:

```text
self-improvement before evaluation
containers before runtime interface
Temporal before defining authority
MCP mutation before Host API
vector memory before canonicality rules
more agents before workspace isolation
```

MCP and A2A are treated as **boundary protocols**, not control-plane replacements. Current MCP explicitly separates its stateless core from a Tasks extension for long-running calls; therefore an MCP Task should be treated as an external tool-job handle, not a MAP task. A2A can expose Agent Cards and agent task/message/artifact interoperability, but advertised capability must still pass MAP's local identity and authorization layer. citeturn18search5turn18search6turn18search0

The package consequently keeps hcom rather than replacing it:

```text
                 MAP communication layer
                   /               \
                 hcom             A2A
             native/local       external adapter
```

The most important safety rules appear repeatedly throughout the package because they should survive implementation changes:

> **Agent memory is never canonical.**

> **Workflow checkpoints are never canonical task state.**

> **A client cannot declare its own authoritative identity.**

> **Projections are never independent lifecycle writers.**

> **Runtime capability does not imply MAP authority.**

> **An authority or permission expansion requires explicit operator approval tied to the exact change.**

> **A harness may propose its own improvement; it may not silently expand the rules governing itself.**

Those principles are consistent with MAP's existing project brief, Context System, and Security/Permissions System rather than being a competing governance model. fileciteturn5file0L2-L2 fileciteturn8file0L2-L2 fileciteturn9file0L2-L2

## Recommended starting point

The package intentionally narrows the first coding effort to one end-to-end proof:

```text
                    MAP2-SLICE-1

        add tasks.runtime_version
                  +
             map_events
                  +
            command_dedup
                  │
                  ▼
       in-process mapd task.claim
                  │
                  ▼
      Unix-socket JSON-RPC client
                  │
                  ▼
       one deterministic projector
                  │
                  ▼
  crash + retry + concurrency testing
```

I would **not** begin MAP 2.0 by installing Temporal, integrating A2A, adding vector memory, or turning Prime Agent into the coordinator.

The first milestone should be much more concrete:

> **Kill `mapd` after a claim commits but before the caller receives the response, resend the same request, and prove that MAP has exactly one task transition, exactly one canonical event, the same returned result, and a projection that can be rebuilt afterward.**

Once MAP can guarantee that property, the same foundation supports durable agents, distributed execution, deterministic flows, isolated workspaces, external protocols, and controlled harness evolution without multiplying sources of truth.

**[Download the complete MAP 2.0 implementation package](sandbox:/mnt/data/MAP_2.0_Implementation_Guides.zip)**