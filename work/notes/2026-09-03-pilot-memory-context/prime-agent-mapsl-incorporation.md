# Prime Agent / MAPS_L incorporation review

Status: **OPEN supporting design finding and 2026-09-03 implementation snapshot; not implementation authority**.

This note preserves the forward-relevant result of the current Prime Agent / MAPS_L comparison. It does not activate a Prime integration, change roadmap status, authorize vendoring, or replace the existing Prime/harness roadmaps.

## Current meaning

The updated conclusion is stronger than the earlier framing of Prime as either an external execution backend or merely a source of ideas:

> **MAPS_L should evaluate incorporating the strongest Prime Agent execution mechanisms directly into MAPS_L, while preserving MAPS_L as the canonical control/authority/evidence plane.**

That can begin with stock Prime behind the existing MAPS_L `HarnessAdapter`, then progress to vendoring/forking selected MIT-licensed Prime components if evidence shows that direct incorporation is better than maintaining a loose external dependency.

The architectural target is not "MAPS_L becomes Prime" and not "Prime becomes MAPS_L authority." It is closer to:

```text
                    MAPS_L
┌────────────────────────────────────────────┐
│ CONTROL / GOVERNANCE                       │
│ task truth · authority · policy · claims   │
│ routing · acceptance · review · evidence   │
│ outcomes · learning promotion              │
├────────────────────────────────────────────┤
│ EXECUTION                                  │
│ Prime-derived worker/session runtime       │
│ persistent Python · models · subagents     │
│ messaging · autonomous continuation        │
│ process recovery · executable skills       │
├────────────────────────────────────────────┤
│ MAPS_L ENFORCEMENT                         │
│ canonical bindings · hooks · scope · proof │
└────────────────────────────────────────────┘
```

MAPS_L governs **what work exists, who owns it, what is allowed, what counts as evidence, and whether it is accepted**. Prime-derived machinery can own much more of **how an authorized worker actually stays alive and performs the work**.

## Snapshot used for this review

These are volatile implementation facts, not durable status truth.

### MAPS_L snapshot

At review time, current `main` was `5f66b2f0b72c7856bef5523efc787b26485c1b7e`.

Relevant accepted surfaces include:

- [`runtime/harness/protocol.py`](../../../runtime/harness/protocol.py) — provider/runtime lifecycle contract with `start`, `attach`, `send`, `inspect`, `heartbeat`, `resume`, `stop`, and `collect`;
- [`runtime/harness/service.py`](../../../runtime/harness/service.py) — guarded provider-neutral execution surface; consequential operations require deterministic canonical-run enforcement rather than receiving authority from an adapter;
- [`runtime/harness/adapters/hcom.py`](../../../runtime/harness/adapters/hcom.py) — current concrete harness adapter;
- [`runtime/README.md`](../../../runtime/README.md) — current responsibility boundaries for SQLite, LangGraph, hcom, RnS, helpers, integrity, skills, context, outcomes, and read models;
- [`work/roadmaps/CAPABILITY_CHECKLIST.md`](../../roadmaps/CAPABILITY_CHECKLIST.md) — current capability-status evidence surface; as of 2026-09-03, the S6 skill/context integration had been promoted through its accepted evaluation/decision path;
- [`work/roadmaps/agent-harness-capabilities/README.md`](../../roadmaps/agent-harness-capabilities/README.md) — detailed harness/security/skills/environment/learning design rules;
- [`work/roadmaps/prime-agent-capability-roadmap.md`](../../roadmaps/prime-agent-capability-roadmap.md) — earlier Prime-derived roadmap whose central rule remains useful but whose baseline descriptions must be re-verified before implementation.

The accepted MAPS_L invariant that matters most here remains: **capability does not grant authority**. See [`AGENTS.md`](../../../AGENTS.md) and the harness roadmaps.

### Prime Agent snapshot

Prime Agent had advanced materially from the earlier 0.7.x review. Its coding-agent package declared `0.9.1`, while `main` already contained newer 2026-09-03 changes.

Important current Prime characteristics observed from its repository:

- persistent Python is now a lightweight CPython REPL rather than the older Jupyter/ipykernel mechanism;
- daemon-backed sessions, detached/reattached workers, state snapshots, direct session transport, process recovery, and an event-driven agent roster have received substantial hardening;
- RLM subagents are persistent child sessions with direct agent messaging and bounded recursion;
- autonomous continuation, quality gates, goals, heartbeats, schedules, compaction, skills, provider abstraction, RPC, and ACP are all first-class surfaces;
- `/refine` can change supplemental harness state, but the immutable base system prompt is not rewritten;
- model-generated Python and shell commands still execute with the user's OS permissions; Prime's worker/process boundaries are lifecycle/recovery boundaries, **not a security sandbox**.

Prime sources for re-verification:

- [Prime Agent repository](https://github.com/PrimeIntellect-ai/prime-agent)
- [README](https://github.com/PrimeIntellect-ai/prime-agent/blob/main/README.md)
- [coding-agent package](https://github.com/PrimeIntellect-ai/prime-agent/blob/main/packages/coding-agent/package.json)
- [changelog](https://github.com/PrimeIntellect-ai/prime-agent/blob/main/packages/coding-agent/CHANGELOG.md)
- [ACP mode](https://github.com/PrimeIntellect-ai/prime-agent/blob/main/packages/coding-agent/docs/acp.md)

Re-check all Prime implementation/version claims before consequential work; the project is changing quickly.

## What changed from the earlier Prime roadmap

The existing [`prime-agent-capability-roadmap.md`](../../roadmaps/prime-agent-capability-roadmap.md) already made an important decision:

> absorb useful Prime-style lifecycle guarantees without rebuilding Prime as a second orchestrator.

That remains correct.

What has changed is the practical implication.

Earlier, the natural interpretation was largely:

```text
study Prime
  → reproduce transferable mechanisms in MAPS_L
```

Current evidence supports testing a different path:

```text
study Prime
  → use stock Prime through a MAPS_L adapter
  → determine which mechanisms are genuinely better
  → vendor/fork selected Prime components where justified
  → wrap them in MAPS_L authority/evidence semantics
```

MAPS_L now has enough of its own control plane that it does not need Prime to define task truth, authority, lifecycle meaning, review, or learning governance. Conversely, Prime has invested heavily in execution-runtime machinery that MAPS_L should avoid reimplementing merely to own every line of code.

## Responsibility split

A useful current boundary is:

| Concern | Preferred owner | Reason |
| --- | --- | --- |
| Human objective / roadmap permission envelope | MAPS_L | Prime session goals must not create authority. |
| Canonical task truth / lifecycle | MAPS_L SQLite | One fact / one authority. |
| Claims, leases, accountable owner | MAPS_L | Session liveness is not task ownership. |
| Policy / operator approval | MAPS_L | Capability is not permission. |
| Frozen run/task/context binding | MAPS_L integrity | Needed for review/recovery correctness. |
| Model/provider invocation | Prime-derived execution | Commodity execution plumbing already implemented broadly. |
| Persistent Python worker state | Prime-derived execution | Prime has current REPL/snapshot/recovery engineering. |
| Session worker / daemon lifecycle | Prime-derived execution candidate | Strong current implementation; avoid rebuilding without evidence. |
| Native subagent process/session mechanics | Prime-derived execution candidate | RLM already provides persistent child sessions and communication. |
| Child authority/scope/lineage | MAPS_L wrapper | A Prime child must not silently become a MAPS owner. |
| Agent messaging transport | Experiment / merge | Prime messaging is strong; hcom remains accepted MAPS transport today. |
| Skill trust/provenance/routing | MAPS_L | Current MAPS skill gate/eval owns trust and selection meaning. |
| Skill executable Python implementation | Prime-derived execution candidate | Prime's executable package model is useful. |
| Autonomous work loop / local command gate | Prime-derived execution candidate | Good worker-level mechanism; not final MAPS acceptance. |
| Independent review / acceptance | MAPS_L | Prime saying "done" is not task completion. |
| Outcome observations | MAPS_L | Real-world success remains separate from execution confidence. |
| Harness-learning promotion | MAPS_L | No self-authorizing policy/guidance changes. |
| Refinement candidate generation | Prime-derived analysis candidate | Prime `/refine` can propose lessons without owning promotion. |
| Security sandbox | External restricted environment | Prime explicitly is not a sandbox. |

## Prime components worth incorporating

The next technical review should classify each candidate as `KEEP MAPS_L`, `ADOPT PRIME`, `MERGE`, `REJECT PRIME`, or `EXPERIMENT FIRST` rather than defaulting to a rewrite.

### 1. Persistent CPython REPL — strong `ADOPT / MERGE` candidate

Prime 0.9 moved to a smaller persistent CPython runtime with state snapshot/restore, interrupt handling, command execution, process cleanup, and recovery work already implemented.

Potential MAPS_L value:

```text
worker starts
  → Python state accumulates
  → context compacts without losing execution variables
  → terminal/client detaches
  → worker survives
  → process/session is recovered
  → state is restored
```

Reimplementing this from scratch would recreate a large class of edge cases Prime is already discovering and fixing.

### 2. Daemon/session supervision — strong `EXPERIMENT → ADOPT` candidate

Prime has built substantial machinery for resident workers, detach/attach, session catalogs, worker identity, reconnects, process ownership, dead-worker recovery, and retained child sessions.

MAPS_L should test whether this can become execution infrastructure beneath RnS rather than building a parallel MAPS daemon.

Desired layering:

```text
MAPS RnS: "Should this known run/session still be allowed to continue?"
       ↓ authorized
Prime runtime: "Can I reconnect/recover the actual worker safely?"
```

### 3. RLM subagent lifecycle — strong `MERGE` candidate

Prime provides real parent/child agent sessions, bounded recursion, child handles, retained sessions, direct messaging, and background work.

MAPS_L should reuse those mechanics where useful but add explicit lineage and authority ceilings:

```text
MAPS task owner / run
       ↓ delegates
Prime child session
       ↓ MAPS wrapper records
child_run_id · parent_run_id · scope · worker/session identity · result/evidence
```

A Prime child is an execution mechanism, not automatically a MAPS task owner or eligible reviewer.

Read-only exploratory children may remain internal execution detail when risk/evidence requirements do not justify durable child-run records. Consequential writable or review-relevant children should be observable in MAPS lineage rather than becoming hidden work.

### 4. Agent messaging — `EXPERIMENT / MERGE`, not immediate hcom replacement

Prime's parent/sibling/child messaging and daemon roster are now substantial. This overlaps hcom.

Do not remove hcom merely because Prime has a cleaner local agent-family API. Current MAPS_L recovery and communication behavior is built around hcom and accepted boundaries in [`playbook/CONTROL_PLANE.md`](../../../playbook/CONTROL_PLANE.md).

Instead compare:

- project isolation;
- explicit session/run correlation;
- delivery/retry semantics;
- restart recovery;
- cross-provider reach;
- observability/evidence;
- message authorization and trust boundaries;
- whether Prime messaging can be wrapped beneath the current harness contract without creating a second source of session truth.

### 5. Provider/model abstraction — strong `ADOPT` candidate

Prime already supports a broad provider/model set. MAPS_L should not spend disproportionate effort maintaining equivalent OpenAI/Anthropic/Gemini/OpenRouter/Bedrock/Azure/etc. invocation plumbing unless a MAPS-specific requirement is unmet.

MAPS_L can continue to describe capability/cost/availability and choose a worker class while Prime-derived runtime code performs provider-specific execution.

### 6. Autonomous continuation + local quality gates — strong `ADOPT` candidate

Prime can keep working through local failure loops within turn/token/time budgets and run an explicit command gate before settling.

That maps well to:

```text
MAPS task/run
  → scope + budget + local verification command
  → Prime autonomous execution
  → edit/test/fix loop
  → local gate passes or budget/stop condition reached
  → MAPS collects evidence
  → independent MAPS review/acceptance
```

A Prime gate proves only what that command proves. It must not replace MAPS acceptance criteria, evidence binding, or independent review.

### 7. Skills — `MERGE`

MAPS_L now has accepted Agent Skills-format discovery, provenance/trust gating, routing evaluation, progressive body loading, and execution-resource discovery. Prime adds a useful executable Python-package model and skill creator.

Target direction:

```text
canonical skill id/version/hash
        ↓
MAPS provenance + trust + routing decision
        ↓
Prime-derived executable skill package
        ↓
run-bound evidence/result
```

Avoid a separate "MAPS skill truth" and "Prime skill truth" when a shared canonical skill artifact/version can be referenced by both layers.

### 8. `/refine` — `ADOPT ANALYSIS`, reject self-promotion

Prime's continual harness can generate evidence-backed candidate changes to supplemental prompt notes, memories, skill descriptions, and subagent specs.

MAPS_L should not copy the automatic-promotion authority model wholesale.

Preferred flow:

```text
Prime trajectory
   ↓ refinement analysis
candidate lesson/configuration
   ↓
MAPS CANDIDATE
   ↓ frozen eval / historical evidence
independent review / decision
   ↓
ACTIVE guidance or accepted implementation
```

Prime can be a high-quality candidate generator; MAPS_L remains the promotion governor.

### 9. ACP / RPC — use as an integration seam before internal coupling

Prime exposes standardized ACP plus a richer Prime RPC surface. These are preferable initial boundaries to importing unstable internal TypeScript classes directly.

The first Prime adapter should likely use the narrowest public protocol that can satisfy the MAPS lifecycle contract. Prime-specific lifecycle needs may require RPC initially; ACP remains valuable as the standardized long-term worker boundary.

### 10. Security isolation — do **not** inherit a false assumption

Prime's model-generated code executes with the user's OS permissions. Incorporating Prime does not provide a sandbox.

Any MAPS_L move toward greater autonomy should keep environment/worktree/container/VM restrictions as a separate security problem. Prime process isolation is useful for lifecycle and failure containment, not sufficient least privilege.

## Three incorporation models

### A. External Prime adapter

```text
MAPS_L HarnessService
        ↓
PrimeHarnessAdapter
        ↓ RPC/ACP/CLI
stock prime-agent
```

Advantages:

- smallest experiment;
- easy to update/remove;
- verifies semantics before code import;
- preserves MAPS_L's current language/runtime boundary.

Weakness:

- external lifecycle/version dependency;
- some Prime internals may not be exposed cleanly enough;
- integration evidence may require extra mapping.

### B. Vendor/fork selected Prime components

```text
MAPS_L repository/package set
   ├─ Python control plane
   └─ Prime-derived TS/Python execution packages
```

Advantages:

- direct control of selected execution behavior;
- can replace Prime assumptions with MAPS canonical bindings/hooks;
- avoids rebuilding complex proven machinery.

Costs:

- upstream-sync responsibility;
- polyglot build/install surface;
- license/dependency inventory;
- must prevent forked execution state from becoming a competing authority.

Prime Agent itself is MIT licensed, which permits reuse/modification/distribution with required notices. Before vendoring, audit the exact copied files and bundled/transitive dependencies rather than assuming the repository-level license settles every dependency obligation.

### C. Reimplement Prime concepts in MAPS_L Python

This should be the least-preferred default.

Use it only where:

- Prime's implementation cannot satisfy MAPS invariants;
- the required slice is genuinely small;
- external/vendor coupling costs exceed implementation cost; or
- security/portability constraints demand a different implementation.

Do not translate a large, rapidly changing TypeScript execution runtime into Python merely for language uniformity.

## Recommended progression

The current recommended sequence is:

```text
1. ADAPTER
   Drive stock Prime from MAPS_L through the existing harness boundary.

2. EVIDENCE
   Run a bounded lifecycle experiment and map every mismatch.

3. CLASSIFY
   For each Prime subsystem: KEEP MAPS_L / ADOPT / MERGE / REJECT / EXPERIMENT.

4. INCORPORATE
   Vendor/fork only the components whose direct reuse beats external coupling.

5. MAPS-NATIVE WRAPPING
   Bind adopted execution mechanisms to MAPS authority, lineage, evidence,
   review, learning, and recovery invariants.
```

This path preserves replaceability. MAPS_L must not become "a collection of Prime patches" that cannot survive Prime disappearing or changing direction.

## First end-to-end experiment

Before making Prime strategic, one disposable MAPS_L task should demonstrate the complete integration path.

### Positive lifecycle

```text
MAPS task READY
  ↓ claim
run manifest / exact task revision
  ↓
Prime adapter start
  ↓
Prime worker/session created
  ↓
MAPS context delivered
  ↓
Prime performs work
  ↓
Prime spawns at least one RLM child
  ↓
child identity/lineage observed as required
  ↓
edit in disposable clean worktree
  ↓
Prime local verification gate
  ↓
detach client
  ↓
reattach to same session
  ↓
simulate recoverable worker interruption
  ↓
MAPS RnS re-checks canonical eligibility
  ↓
Prime adapter resume
  ↓
collect bounded result/evidence
  ↓
independent MAPS review
  ↓
DONE only through canonical MAPS transition
```

### Required negative cases

The same experiment should prove at least:

1. **task revision changed** → old Prime session cannot silently continue under the stale contract;
2. **lease/ownership invalid** → Prime resume is blocked even if Prime can technically resume;
3. **Prime claims completion but MAPS acceptance/evidence fails** → task is not `DONE`;
4. **Prime child attempts scope expansion** → child capability does not widen parent/task authority;
5. **local Prime gate passes but independent review fails** → work returns through normal MAPS correction/reverification;
6. **Prime worker/process dies** → recovery preserves known lineage without inventing or duplicating work.

Success means the Prime execution layer can be removed/replaced without changing the meaning of MAPS task truth or authority.

## Why this is potentially better than either project alone

Prime is increasingly strong at **worker execution**:

- keeping a model-backed worker alive;
- giving it a persistent programming environment;
- coordinating subagents;
- talking to models/providers;
- managing background work;
- recovering sessions and process state;
- running iterative local quality gates.

MAPS_L is increasingly strong at **governance and evidence**:

- explicit human objective / roadmap envelope;
- canonical mutable task truth;
- ownership/claims/leases;
- capability-versus-authority separation;
- exact run/context bindings;
- bounded recovery decisions;
- independent review;
- acceptance/criterion evidence;
- post-completion outcomes;
- trust/provenance-aware skills;
- evaluated rather than self-authorizing learning.

The high-value combination is therefore:

> **Prime-grade execution mechanics under MAPS-grade authority, evidence, review, and learning governance.**

That should be evaluated before MAPS_L invests in parallel execution infrastructure merely to avoid a dependency.

## Risks / failure modes to guard against

### Duplicate state

Do not let Prime session state become a second mutable copy of task ownership, task lifecycle, policy approval, or acceptance state.

Prime identifiers should be bound into MAPS run/session lineage, not promoted into task truth.

### Rapid Prime architectural churn

Prime moved from the earlier 0.7.x review through 0.8.x to 0.9.x quickly, including replacing the Python kernel implementation. Build against public protocol/adapter seams first. Vendor only after the target component and upstream-sync strategy are understood.

### Fork maintenance

Direct incorporation creates a maintenance obligation. Prefer narrow reusable packages/components over an undifferentiated fork when practical.

### Polyglot complexity

MAPS_L's active control plane is Python while much of Prime's host/runtime is TypeScript/Node with Python beneath it. That is acceptable if the boundary is explicit and independently testable. Do not hide cross-language lifecycle semantics inside ad hoc shell calls.

### hcom / Prime messaging overlap

Avoid two equally authoritative session/message models. Run a deliberate comparison and choose/wrap responsibilities rather than accumulating both indefinitely.

### Hidden subagent work

Prime makes child spawning cheap. MAPS_L must decide when child work is implementation detail versus when it requires durable child lineage for authorship, scope, review independence, cost, or recovery.

### Security

Prime is not a sandbox. Increased execution capability must not be mistaken for least privilege.

### Self-improvement authority drift

Prime refinement output is useful evidence/candidate material, not permission to modify MAPS policy, routing, safety, or persistent guidance automatically.

## Open design questions

1. Should MAPS_L eventually vendor a coherent Prime execution package set, or only selected runtime components?
2. What is the upstream-sync policy if Prime-derived code is forked?
3. Can the current `HarnessAdapter` semantics map cleanly to Prime RPC/ACP without Prime-specific leakage into the control plane?
4. Which Prime child activities require durable `child_run_id` lineage versus remaining local execution detail?
5. Does Prime messaging eventually replace part of hcom, or should hcom remain the provider-neutral transport above/beside Prime?
6. Can MAPS skill trust/version identities be consumed directly by Prime's executable skill loader without duplicate catalogs?
7. What environment/sandbox boundary should surround Prime for consequential writable work?
8. Which Prime autonomous/gate signals should become MAPS evidence refs, and which are only transient execution detail?
9. How should Prime `/refine` candidates enter existing MAPS operational-learning/evaluation flows without bypassing promotion rules?
10. At what point does vendoring reduce risk compared with depending on Prime's rapidly moving public releases?

## Connections

- Parent / current Prime-derived design owner: [Prime Agent capability adoption roadmap](../../roadmaps/prime-agent-capability-roadmap.md)
- Parent / broader mechanism owner: [MAPS agent-harness capability roadmaps](../../roadmaps/agent-harness-capabilities/README.md)
- Current status/evidence route: [Capability Checklist](../../roadmaps/CAPABILITY_CHECKLIST.md)
- Control-plane boundaries: [Control Plane](../../../playbook/CONTROL_PLANE.md)
- Existing execution abstraction: [Harness protocol](../../../runtime/harness/protocol.py) and [Harness service](../../../runtime/harness/service.py)
- Related packet snapshot: [Implementation and Collision State](implementation-and-collision-state.md)
- Re-entry method for this packet: [Implementation / Re-entry Plan](implementation-reentry-plan.md)
- Source implementation: [Prime Agent](https://github.com/PrimeIntellect-ai/prime-agent)

## Re-entry

Before converting any finding here into implementation:

1. recover current MAPS_L `main` and live GitHub ownership/PR overlap;
2. read the current owning roadmap/status entries rather than trusting this snapshot;
3. recover current Prime release and `main`, especially protocol/runtime changes since 0.9.1;
4. re-check the live `HarnessAdapter` / `HarnessService` contract and accepted hcom/RnS paths;
5. inspect current skill/environment/security/learning status where the candidate component touches them;
6. choose the smallest disposable adapter experiment that answers one unresolved integration question;
7. keep Prime/MAPS state responsibilities explicit in tests; and
8. require normal MAPS review/evidence before any component is promoted from experiment to accepted execution dependency.

Current disposition: **OPEN — strong case for an adapter-first experiment followed by evidence-based selective incorporation; no implementation is authorized by this note itself.**
