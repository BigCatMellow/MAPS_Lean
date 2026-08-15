# MAPS Lean Future Ideas Backlog

Status: `PRESERVED IDEA BACKLOG — NOT ACTIVE AUTHORITY`

Purpose: preserve promising system ideas discovered while reviewing the legacy
MAPS implementation and the current Lean runtime, without treating their mere
existence as a reason to build them.

This is a **future-options document**, not a roadmap and not an execution
instruction. Active behavior continues to be defined by `AGENTS.md`, the active
playbooks, runtime code, task state, and approved project decisions.

Related sources:

- [Legacy Knowledge & Implementation Audit](LEGACY_KNOWLEDGE_AUDIT.md)
- [Legacy Promotion Ledger](LEGACY_PROMOTION_LEDGER.md)
- [Active Runtime](../runtime/README.md)
- [Execution Integrity](../playbook/EXECUTION_INTEGRITY.md)
- [Repair and Learning](../playbook/REPAIR_AND_LEARNING.md)
- [Helpers and Communication](../playbook/HELPERS_AND_COMMUNICATION.md)
- [Information Lifecycle](../playbook/INFORMATION_LIFECYCLE.md)

---

## Preservation rule

The legacy audit already established the governing rule:

> Preserve invariants, evidence, tests, and useful implementation techniques.
> Do not preserve a subsystem merely because it existed.

Apply the same rule here.

Before promoting any item in this document, answer:

```text
What real problem are we solving?
        ↓
Does Lean already solve it?
        ↓
What evidence says the problem is material?
        ↓
What is the smallest behavior that solves it?
        ↓
Can success and failure be measured?
        ↓
Can it remain provider-neutral and authority-safe?
        ↓
Can it be added without creating another source of truth?
```

If those questions cannot be answered, keep the idea here rather than turning
it into runtime machinery.

---

# Current Lean baseline

These ideas should be judged against what MAPS Lean already has. Do not build a
second version of an existing control.

The active runtime already provides:

- SQLite canonical task truth;
- structural AGI readiness gates;
- atomic claims and leases;
- submission and review evidence;
- policy metadata and operator approvals;
- worker capability envelopes;
- durable halt state;
- deterministic route selection through LangGraph;
- separate LangGraph checkpoint state;
- project-isolated hcom transport;
- RnS recovery with bounded retry/backoff;
- bounded helper lanes;
- immutable run manifests;
- execution-time context/scope binding;
- staleness checks;
- writable/forbidden Git scope proof;
- run budgets;
- continuity-aware review support;
- criterion-level evidence where justified.

Future work should therefore focus primarily on **observability, outcome
measurement, context efficiency, parallel-work isolation, deterministic routine
flows, and controlled learning** rather than rebuilding basic orchestration.

---

# Candidate summary

| Priority | Candidate | Main value | Default disposition |
|---|---|---|---|
| P1 | Session replay / trace reconstruction | Explain exactly what happened | Preserve and simplify |
| P1 | Outcome feedback and eval corpus | Distinguish passing MAPS from real success | Preserve and measure |
| P1 | Context builder | Supply the smallest trustworthy context packet | Preserve principle; build narrowly |
| P1 | Git worktree isolation | Prevent parallel agents colliding in one worktree | Lean synthesis; prototype when concurrency warrants |
| P1 | Deterministic `maps flow` procedures | Remove routine bureaucracy from LLM reasoning | Add only for repeated stable procedures |
| P2 | Small Mission Control / `maps status` | Give the operator one truthful attention surface | Read-only and minimal |
| P2 | Persistent helper continuity | Resume useful specialist context without durable authority | Defer until repeated need |
| P2 | Controlled harness evaluation/refinement | Improve routing/instructions from measured history | Proposal-only; never self-authorizing |
| P2 | Cost/yield and escaped-defect metrics | Optimize for useful outcomes, not activity | Add when enough runs exist to measure |

---

# P1 — Session replay / trace reconstruction

## Problem

As MAPS becomes more capable, failures can span task state, routing, helper
work, communication, retries, review, recovery, and Git changes. Looking at the
final task row is not enough to answer:

> What exactly happened?

The legacy system had `session_replay.py` and a design for a disposable,
rebuildable diagnostic read model. The promotion ledger already marks that
behavior as worth preserving and simplifying.

## Smallest Lean version

Start with a read-only command:

```text
maps trace TASK-042
```

Example output:

```text
TASK-042

10:14  created
10:15  AGI passed
10:16  routed -> codex
10:16  claimed by codex-1
10:17  run RUN-91 started
10:18  helper qwen-3 spawned
10:23  helper returned
10:31  verification passed
10:32  submitted
10:35  review claimed by claude-2
10:39  changes requested
10:52  resubmitted
10:56  approved
10:57  DONE
```

A deeper form could expose the execution contract:

```text
maps trace RUN-91 --full
```

Potential fields:

- task revision;
- run manifest ID;
- instruction/context hash;
- worker/model/harness;
- tools and permissions;
- writable and forbidden scope;
- budget;
- helper activity;
- policy decisions;
- verification evidence;
- recovery events;
- review events;
- final outcome if known.

## Hard boundaries

The replay layer MUST:

- be read-only;
- derive from canonical sources;
- be disposable/rebuildable;
- never grant authority;
- never become a second mutable task history;
- report missing or contradictory evidence rather than silently repairing it.

## Promotion trigger

Promote when debugging a failed or confusing run repeatedly requires manually
joining multiple SQLite/event/hcom/runtime sources.

## Proof

A trace should be reconstructable from canonical records after deleting the
replay index/cache.

---

# P1 — Outcome feedback and historical eval corpus

## Problem

A task can pass MAPS structural checks and review while still failing in the
real world later.

Examples:

```text
verification: PASS
review: PASS
outcome: SUCCESS
```

and:

```text
verification: PASS
review: PASS
outcome: FAILURE
reason: regression discovered later
```

must not be treated as equivalent.

The legacy audit specifically preserves the lesson to measure escaped defects
and validator blind spots rather than only activity or throughput. The
promotion ledger also retains `map_metrics.py` as a possible future eval/health
source.

## Smallest Lean version

Add a small outcome record linked to a completed task/run, without changing the
original immutable evidence.

Candidate fields:

```text
outcome_status
outcome_recorded_at
outcome_source
failure_class
rework_count
operator_intervention_count
escaped_defect
notes/provenance
```

Do not require an outcome for every trivial task. Unknown is a valid state.

## Why it matters

Without real outcome feedback MAPS can accidentally optimize for:

> Agents are good at satisfying MAPS.

The desired target is:

> Agents are good at accomplishing the operator's actual goal.

## Eval corpus

Once enough outcome-linked runs exist, create a reproducible historical eval
set containing representative:

- successful tasks;
- failed tasks;
- tasks requiring rework;
- escaped defects;
- routing mistakes;
- context failures;
- helper failures;
- recovery events;
- review catches;
- false-positive/false-negative validators.

The corpus should use frozen historical inputs and expected properties so that
changes to prompts, routing, policies, helpers, and validators can be compared
against the same cases.

## Hard boundaries

Outcome data MUST NOT rewrite the original task history.

Later knowledge is appended as later knowledge.

An outcome label should record provenance because many outcomes require human
or downstream-system judgment.

## Promotion trigger

Promote once Lean has enough completed runs that recurring failure/rework
patterns can be measured instead of discussed anecdotally.

---

# P1 — Context builder

## Problem

Agents should receive the information necessary to do the task, not the entire
repository and not an arbitrary semantic-search dump.

The legacy audit's strongest retained context principle is:

> Context packet, not context dump.

The promotion ledger preserves the context packet shape:

- Required;
- Optional/triggered;
- Excluded;
- staleness information.

## Smallest Lean version

A command such as:

```text
maps context TASK-042
```

could resolve an explicit packet:

```text
REQUIRED
AGENTS.md
TASK-042
runtime/state/sqlite_store.py
tests/test_state.py
DEC-007

OPTIONAL — trigger only if needed
CONTROL_PLANE.md
TASK-031 handoff

EXCLUDED
legacy/
unrelated tasks
superseded decisions
obsolete architecture notes
```

The packet should be assembled primarily from **known relationships and active
authority**, not merely vector similarity.

Conceptually:

```text
TASK
 +
explicit inputs
 +
applicable authority
 +
applicable decisions
 +
current state
 +
relevant prior evidence
        ↓
   CONTEXT PACKET
```

## Ranking principle

Prefer:

1. explicit task references;
2. active authority/policy;
3. canonical project state;
4. dependency relationships;
5. exact paths/symbols;
6. provenance-backed prior evidence;
7. semantic retrieval only as a bounded supplement.

## What not to revive

Do **not** recreate the old full Library/knowledge-management subsystem merely
because retrieval is useful. The legacy evidence did not justify that amount of
machinery.

## Promotion trigger

Promote when agents repeatedly receive too much irrelevant context, miss known
required project information, or spend significant time rediscovering the same
canonical inputs.

## Proof

Evaluate against historical tasks:

- required-fact recall;
- irrelevant-context reduction;
- source visibility;
- stale/superseded-source rejection;
- task success/rework impact.

---

# P1 — Git worktree isolation for parallel coding

Provenance: `LEAN SYNTHESIS FROM MULTI-AGENT FAILURE MODE`

## Problem

Git scope proof tells MAPS whether a run changed allowed files. It does not
physically stop two coding agents from interfering with the same working tree
while they execute.

As true parallel implementation increases, that becomes a separate isolation
problem.

## Smallest Lean version

For coding tasks that need writable repository access:

```text
claim task
   ↓
create dedicated Git worktree
   ↓
run agent inside that worktree
   ↓
verify changes/tests/scope
   ↓
review
   ↓
integrate or discard
   ↓
remove worktree
```

Example layout:

```text
repo/
worktrees/
  TASK-041/
  TASK-042/
  TASK-043/
```

## Hard boundaries

Worktree isolation MUST NOT imply authority to merge.

It should integrate with existing:

- task ownership;
- run manifests;
- writable/forbidden scope;
- review independence;
- repo-global mutation locks;
- recovery/cleanup.

Shared resources outside the worktree still require explicit concurrency
control.

## Promotion trigger

Prototype when two or more implementation workers are intentionally allowed to
modify the same repository concurrently often enough that worktree collisions
or branch hygiene become a material risk.

## Proof

Parallel integration tests should demonstrate that independent workers cannot
silently modify one another's uncommitted working state.

---

# P1 — Deterministic `maps flow` procedures

Provenance: `LEAN SYNTHESIS FROM REPEATED ORCHESTRATION`

## Problem

LLMs should reason about uncertain work. They should not repeatedly improvise
stable administrative procedures whose transitions are already known.

For example, release is mostly procedural:

```text
verify task state
↓
verify required evidence
↓
verify independent review
↓
verify approval/policy
↓
perform permitted integration/release action
↓
record result
```

## Smallest Lean version

Introduce a deliberately small deterministic flow layer only for mature,
repeated procedures:

```text
maps flow release TASK-042
maps flow review TASK-042
maps flow recover RUN-091
maps flow handoff TASK-042
```

A flow is a named sequence of existing guarded runtime operations. It should
not become a second workflow engine or a second task state machine.

## Good early candidates

- review preparation/routing;
- release/integration checks;
- recovery sequence;
- handoff/continuity checks;
- projection/read-model repair;
- possibly project bootstrap after the procedure stabilizes.

## Bad candidates

Do not encode genuinely creative or uncertain implementation/research work into
procedures simply to make everything look uniform.

## Promotion trigger

Promote a flow when the same multi-step procedure is performed frequently, its
branches are well understood, and operator/agent mistakes come mostly from
forgetting steps rather than from hard reasoning.

## Proof

The deterministic flow should produce the same guarded transitions as manual
use of the underlying runtime operations, with explicit failure reasons at the
step that failed.

---

# P2 — Small Mission Control / operator status surface

## Problem

The operator needs a compact answer to:

- what is running;
- what is blocked;
- what needs attention;
- which workers are active;
- whether the control plane is healthy;
- what recently completed or failed.

The old Command Center/Mission Control implementation carried too much UI and
fixed-roster baggage, but its **read-only operator-content contract** remains
useful. The promotion ledger explicitly drops the old UI while retaining this
possibility.

## Smallest Lean version

Start with CLI text, not an application:

```text
maps status
```

Example:

```text
MAPS
────────────────────────────────

TASKS
Active       3
Ready        5
Review       2
Blocked      1

WORKERS
Codex-1      TASK-041   14m
Claude-1     REVIEW-42   3m
Qwen-local   helper      1m

SYSTEM
SQLite       OK
LangGraph    OK
hcom         OK
RnS          OK

ATTENTION
TASK-038     lease stale
TASK-042     review requested
TASK-051     budget 88%

RECENT
TASK-037     DONE
TASK-036     DONE
TASK-035     FAILED -> recovered
```

## Design rule

Mission Control is a **read model**, not a control authority.

It may invoke explicit existing commands, but the screen itself must never
become canonical state.

## Promotion trigger

Promote when normal operation regularly requires several commands/files just to
understand current system state.

---

# P2 — Persistent helper continuity without persistent authority

## Problem

Some bounded specialists may benefit from remembering recent work across tasks:

- security helper;
- test helper;
- docs helper;
- repository-specific local helper.

Respawning them from zero can waste context, but giving them durable ownership
or authority would undermine Lean's helper model.

## Core distinction

```text
persistent identity/context     MAYBE
persistent resumable session    MAYBE
persistent task authority       NO
persistent ownership            NO
persistent review authority     NO
```

A resumed helper still receives a fresh bounded request from the current task
owner and remains subordinate to that request's scope.

## Promotion trigger

Promote only after repeated evidence that rebuilding a specialist's context is
costly and that bounded resumable context improves outcomes enough to justify
the lifecycle complexity.

## Proof

Tests must show that old helper context cannot expand a new request's scope or
inherit authority from a prior task.

---

# P2 — Controlled harness evaluation and refinement

## Problem

Once MAPS records runs and real outcomes, it can compare alternative operating
configurations rather than relying on intuition about which prompt, routing
rule, model/harness pairing, context packet, or validator is better.

This is the useful core of a "continual harness" idea.

## Safe architecture

```text
historical runs + outcomes
          ↓
reproducible eval corpus
          ↓
compare candidate configuration
          ↓
report measured differences
          ↓
refine.propose
          ↓
operator/review approval
          ↓
normal change process
```

The key operation is **propose**, not silently mutate.

## Candidate things to evaluate

- AGI instruction templates;
- context packet construction;
- worker/model/harness routing;
- helper use thresholds;
- validation rules;
- review routing;
- retry/recovery thresholds;
- deterministic flow designs.

## Hard boundaries

The refinement system MUST NOT:

- grant itself new permissions;
- weaken safety/review gates without normal approval;
- rewrite historical expected outcomes;
- optimize only for speed/cost while hiding defects;
- train against the same eval examples in a way that makes the benchmark
  meaningless;
- change active configuration simply because a candidate scores better on one
  metric.

## Promotion trigger

Promote after outcome feedback and a representative eval corpus exist. Before
that, "self-improvement" would mostly be speculation.

---

# P2 — Cost/yield and escaped-defect metrics

## Problem

Raw task counts, token use, elapsed time, or agent utilization can produce a
misleading picture of system performance.

Useful measurement should connect resource use to outcomes.

## Candidate metrics

```text
successful outcome / run
rework rate
escaped defect rate
review catch rate
validator blind-spot rate
operator intervention rate
recovery success rate
cost per successful outcome
time per successful outcome
context bytes/tokens per successful outcome
helper yield
routing correction rate
```

These should be interpreted together rather than collapsed prematurely into one
magic score.

## Promotion trigger

Add only once enough homogeneous runs exist for the metric to mean something.
A dashboard over five incomparable tasks is not evidence.

---

# Ideas intentionally not revived by default

The following may contain useful concepts but should **not** return simply
because the old system or external tools supported them.

| Idea | Default decision | Reason |
|---|---|---|
| Large always-running `mapd` daemon rewrite | Skip | Adds a new central service before proven need |
| Full Library / giant knowledge graph | Skip | Retrieval principle is useful; old subsystem cost was not justified |
| Old Command Center / Mission Control UI | Drop implementation | Preserve only read-only content contract |
| Fixed agent roster | Drop | Conflicts with capability-based provider-neutral routing |
| WezTerm-dependent orchestration | Drop | Terminal is presentation, not authority |
| Provider-specific permanent identities | Drop | Runtime should remain provider-neutral |
| Debate-agent bureaucracy | Optional experiment only | Independent review is valuable; staged debate is not automatically valuable |
| More role/persona prompting | Skip | Specify outcome, authority, evidence, and capability instead |
| Temporal | Defer | Consider only if current LangGraph/RnS durability proves insufficient |
| Cedar/policy-language rewrite | Defer | Current policy should be replaced only by demonstrated complexity need |
| A2A interoperability | Defer | Useful only when cross-system interoperability becomes real work |
| MCP-everywhere architecture | Defer | Use adapters where valuable; do not make protocol adoption the architecture |
| Firecracker/microVM per worker | Threat-model dependent | Isolation cost should match actual threat model |
| Large-scale formal-methods program | Optional | Prefer executable invariants/tests first; formalize only high-risk state/concurrency rules |
| Continuous discovery/emergence agents | Do not revive | Favor bounded/event-triggered discovery |

---

# Suggested development order if these become necessary

This is an ordering of dependency/value, **not an approved roadmap**.

```text
CURRENT MAPS LEAN
       │
       ▼
1. trace / session replay
       │
       ▼
2. real outcome recording
       │
       ▼
3. historical eval corpus + useful metrics
       │
       ├───────────────┐
       ▼               ▼
4. context builder   worktree isolation
       │               │
       └───────┬───────┘
               ▼
5. deterministic flows for mature procedures
               │
               ▼
6. small operator status surface
               │
               ▼
7. controlled harness evaluation
               │
               ▼
          refine.propose
```

Persistent helper continuity can be evaluated independently when helper reuse
becomes common enough to justify it.

---

# Promotion template

When one of these ideas becomes a real candidate, create a normal project/task
rather than implementing directly from this file.

Use this minimum record:

```markdown
## Candidate

### Problem observed
What happened, how often, and what evidence exists?

### Existing Lean behavior
What currently handles this problem? Why is it insufficient?

### Smallest proposed behavior
What is the minimum change worth testing?

### Authority boundary
What may the new component read, write, recommend, or execute?

### Source of truth
Which existing canonical state remains authoritative?

### Verification
How will we prove the behavior works?

### Outcome metric
What measurable result would justify keeping it?

### Failure / rollback
How can the experiment fail safely or be removed?

### Decision
PROMOTE / KEEP EXPERIMENTAL / REJECT / DEFER
```

---

# Final principle

The useful unfinished direction is not "more agents" or "more orchestration."

It is making MAPS increasingly able to:

```text
reconstruct what happened
        ↓
measure whether it actually worked
        ↓
provide better bounded context
        ↓
isolate parallel execution
        ↓
automate stable procedure
        ↓
compare alternative configurations
        ↓
propose evidence-backed improvements
```

while retaining the existing rule:

> Capability does not create authority.

MAPS should become easier to inspect and improve **without becoming harder to
trust**.
