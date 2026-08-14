# MAP + Prime Agent — Adoption Brief

## Purpose

Evaluate what MAP can learn from Prime Intellect's **Prime Agent** architecture and identify which ideas are worth adopting without weakening MAP's existing governance, authority, review, and durable-state model.

Prime Agent should **not replace MAP**.

The two systems operate at different layers:

- **MAP is the control plane**: task ownership, canonical state, authority, review separation, acceptance criteria, repair, operator control, and auditable delivery.
- **Prime Agent is primarily an agent-runtime design**: persistent sessions, programmable context, recoverable subagents, bounded autonomy, reusable skills, and harness self-improvement.

The best direction is to use Prime-style runtime ideas **underneath MAP's existing governance layer**.

---

# 1. Recommended Combined Architecture

```text
                         OPERATOR
                            │
                    MAP Command Center
                            │
              ┌─────────────▼─────────────┐
              │     MAP CONTROL PLANE     │
              │                           │
              │ tasks / ownership         │
              │ SQLite claims             │
              │ decisions / authority     │
              │ review / release          │
              │ risk / permissions        │
              │ hcom communication        │
              └─────────────┬─────────────┘
                            │
                Agent Runtime Layer
                            │
          ┌─────────────────┼──────────────────┐
          ▼                 ▼                  ▼
       Codex              Claude          Prime Agent
       worker             worker            worker
          │                 │                  │
     sessions          sessions          persistent runtime
     context           context           subagents
     skills            skills            skills/memory
          └─────────────────┼──────────────────┘
                            │
                       Project files
```

MAP remains responsible for deciding:

- what work is legitimate;
- who owns it;
- what authority each worker has;
- whether work satisfies acceptance criteria;
- whether work is independently approved;
- whether it may be released.

Prime-style machinery improves **how workers execute that work**.

---

# 2. Prime Agent Ideas Worth Adopting

| Prime Agent Idea | MAP Today | Recommendation |
|---|---|---|
| Persistent agent daemon | Partial | **Adopt** |
| Detach/reconnect sessions | Partial | **Adopt** |
| Recover sessions after crashes | Partial | **Adopt** |
| Persistent named subagents | Helpers exist | **Adopt** |
| Programmatic agent control | Mostly scripts/CLI | **Strongly adopt** |
| Progressive skills | Mostly docs/scripts | **Strongly adopt** |
| Persistent goals | Tasks approximate this | **Adopt** |
| Bounded autonomous continuation | Agent loop exists | **Adopt** |
| Automatic quality gates | MAP acceptance/review exists | **Combine** |
| Context as programmable state | Context packets exist | **Borrow selectively** |
| Self-improving harness | Emergence/Self-Repair exists | **Adopt with strict limits** |
| Agent-to-agent messaging | hcom already does this | **Keep hcom** |
| Session JSONL | MAP events/state exist | **Add as runtime history only** |
| IPython as sole model tool | Not necessary | **Do not copy wholesale** |

---

# 3. Build a Persistent MAP Runtime Supervisor

This is one of the strongest architectural improvements.

The terminal should **not be the agent**.

A background MAP runtime should own:

- agent processes;
- model/provider identity;
- active session;
- current task;
- state;
- heartbeats;
- token/runtime limits;
- queued messages;
- child helpers;
- checkpoints;
- recovery state.

Suggested component:

```text
mapd
```

or:

```text
map-runtime-daemon
```

Example state:

```text
Agent
 ├── identity
 ├── provider/model
 ├── PID/process
 ├── status
 │    RUNNING
 │    IDLE
 │    SUSPENDED
 │    DEAD
 ├── current TASK
 ├── context/session ID
 ├── children
 ├── queued messages
 ├── heartbeat
 ├── token usage
 ├── last checkpoint
 └── recovery information
```

Then:

```text
WezTerm
CommandCenterUI
CLI
```

become clients of the runtime.

## Core Rule

> Closing a window should never kill an agent.

A disconnected terminal should simply detach from an active runtime session.

If an agent process crashes, MAP should be able to reconstruct the worker from durable session state.

### Priority

**★★★★★**

---

# 4. Turn MAP Scripts Into Agent-Callable Skills

MAP already contains strong executable machinery such as:

```text
promote_task.py
map_task.py
validate_task_graph.py
validate_review.py
release_task.py
map_status.py
map_metrics.py
reconcile_agents.py
map_emergence.py
```

Agents currently need to learn much of this through Markdown documentation.

Instead, expose common MAP operations as discoverable skills or functions:

```python
await map.task.claim()
await map.task.submit()
await map.review.claim()
await map.review.approve()
await map.context.build()
await map.handoff.create()
await map.health.check()
await map.emergence.capture()
```

Skills should use **progressive disclosure**.

Keep only a compact skill description in normal context:

```text
map-task
  Manage MAP task lifecycle.

map-review
  Review and approve submitted MAP work.

map-context
  Construct the minimum context packet for a task.

map-repair
  Diagnose and repair MAP consistency problems.
```

Load detailed instructions only when the capability is actually invoked.

This fits MAP's existing Context System principle:

> Every task should have a context packet, not a context dump.

### Priority

**★★★★★**

---

# 5. Add a Typed MAP Host API

Canonical MAP state should eventually have a single authoritative write boundary.

Instead of allowing many scripts or agents to directly modify state, expose typed operations such as:

```python
result = await map.task.claim("TASK-331")
```

Internally:

```text
agent
   │
   │ claim TASK-331
   ▼
MAP Host API
   │
   ├─ authenticate agent
   ├─ verify authority
   ├─ check lifecycle state
   ├─ check dependencies
   ├─ perform SQLite transaction
   ├─ update mirrors
   └─ emit event
```

The model's ability to call Python or shell commands must **not grant additional authority**.

Recommended architecture:

```text
Model-facing interface
        ↓
MAP Host API
        ↓
Authority / Governance layer
        ↓
SQLite + durable files
```

A local JSONL-RPC or Unix-socket service would be sufficient initially.

Possible API surface:

```text
task.create
task.describe
task.claim
task.submit
task.approve
task.reject
task.release

review.claim
review.submit

agent.register
agent.status
agent.spawn
agent.stop

context.build
context.expand

message.send

handoff.create

health.check
repair.propose

refine.propose
```

This would also help solve MAP's recurring problem of multiple readers/writers without a clearly declared authority seam.

### Priority

**★★★★★**

---

# 6. Separate MAP Tasks From Runtime Goals

MAP tasks and agent runtime goals should be separate objects.

A **task** defines what MAP needs completed.

Example:

```text
TASK-331

Implement feature X.

Acceptance:
- A
- B
- C
```

A **runtime goal** defines what one agent session is actively trying to finish.

Example:

```text
Session: claude-kiri-784
Task: TASK-331

Goal:
Complete TASK-331 and satisfy acceptance criteria A, B and C.

Limits:
- 120,000 tokens
- 30 autonomous turns
- 2 hours

Completion gate:
pytest tests/foo
```

Possible runtime record:

```json
{
  "task": "TASK-331",
  "session": "claude-kiri-784",
  "goal": "Complete TASK-331 acceptance criteria",
  "status": "active",
  "token_budget": 120000,
  "turn_budget": 30,
  "verification_gate": "python -m pytest tests/foo",
  "continuations": 7
}
```

This creates three separate concepts:

```text
TASK
= what MAP wants accomplished

GOAL
= what this agent session is currently pursuing

CONTINUATION POLICY
= whether the runtime should let it keep trying
```

An agent saying:

```text
Done.
```

should not automatically terminate the run.

The runtime should first check:

```text
Did the acceptance / verification gate pass?
```

If not:

```text
Continue.
```

This could substantially reduce agents stopping halfway through complex tasks.

### Priority

**★★★★★**

---

# 7. Persistent Helpers Without Persistent Authority

MAP's HPOM authority model should remain.

However, helpers can gain **persistent identity and context**.

Example:

```text
codex-main
 ├── security-reviewer
 ├── test-specialist
 └── docs-specialist
```

Each helper may have:

```text
stable name
persistent session ID
independent context
session history
message address
lifecycle state
specialization
parent/core owner
```

Later, the owner can send:

```text
security-reviewer:
"Recheck the authentication code after TASK-331's changes."
```

The helper can resume its previous investigation rather than rebuilding all context.

## Important Authority Boundary

Persistent identity does not mean persistent authority.

```text
Persistent context        YES
Persistent identity       YES
Persistent task rights    NO
Persistent review rights  NO
Persistent release rights NO
```

HPOM Tier 2/3 rules still apply.

### Priority

**★★★★☆**

---

# 8. Add Lossless Context Compaction

MAP's Context System already correctly emphasizes bounded context packets.

The next improvement is to make context compaction **lossless and reversible**.

Instead of:

```text
old context
     ↓ summarize
summary
     ↓
raw history effectively disappears
```

use:

```text
RAW SESSION TREE
│
├─ segment 001
├─ segment 002
├─ segment 003
│
└─ compact-01
      ├─ summary
      └─ references:
           segment 001
           segment 002
```

The model normally receives:

```text
compact-01
segment 003
current task
```

but can explicitly expand old material:

```python
context.expand("segment-002")
```

Recommended properties:

- append-only raw session record;
- summaries reference source segments;
- compaction never destroys history;
- branches/forks retain parent references;
- old context is retrievable on demand;
- the active model context stays small.

This fits MAP's existing rule:

> Compress forward, don't delete backward.

### Priority

**★★★★☆**

---

# 9. Add Harness Refinement, But Keep MAP Governance

Prime Agent's self-improvement system is worth adapting carefully.

MAP already has:

```text
Emergence
Retrospectives
Self-Repair
Improvement backlog
Repair records
```

Add:

```text
MAP Harness Refinement
```

A repeated success or failure could produce a refinement proposal:

```text
Observed trajectory
        ↓
Repeated success/failure?
        ↓
REFINEMENT PROPOSAL
        ↓
Classify change
        │
        ├─ local memory          → automatic
        ├─ helper tactic         → automatic/reviewable
        ├─ skill improvement     → review
        ├─ task workflow change  → core review
        └─ authority/policy      → OPERATOR ONLY
```

Each proposal should record:

```text
trigger
previous behavior
proposed change
evidence
expected benefit
scope
author
approval
version
rollback ID
```

Suggested API:

```python
await map.refine.propose(...)
```

## Critical Safety Rule

MAP must **not freely rewrite its own governance**.

The existing Self-Repair principle should remain:

```text
MAP can repair structure automatically.
MAP can propose repairs to authority.
MAP cannot silently rewrite its own authority.
```

Self-improvement should be permitted for:

- memory;
- tactics;
- context routing;
- skill descriptions;
- helper prompts;
- validation heuristics.

It should require review or operator approval for:

- task lifecycle rules;
- authority;
- permissions;
- review policy;
- security policy;
- release policy;
- destructive action rules.

### Priority

**★★★★☆**

---

# 10. Keep hcom as the Communication Bus

Prime-style parent/child messaging is useful internally.

It should **not replace hcom**.

MAP needs communication between:

```text
independent reviewers
coordinators
helpers
operator
different model providers
different machines
```

hcom is already provider-neutral and well matched to this problem.

Recommended relationship:

```text
Persistent helper/session messaging
            ↓
           hcom
            ↓
MAP durable outcome promotion
```

Live messages remain transient coordination.

Important outcomes still become:

```text
decision       → shared/decisions
open question  → shared/unresolved-questions
scope change   → task record
review         → artifacts/reviews
handoff        → handoffs/
progress       → events/events.jsonl
```

---

# 11. Do Not Make Session Memory Canonical

Agent session history is useful runtime state.

It is not project truth.

MAP's authoritative information should remain in:

```text
shared/
tasks/
decisions
SQLite
review records
release records
```

An agent remembering something does not make it true.

Session memory should be treated as:

```text
runtime assistance
historical context
debug/recovery material
```

not:

```text
canonical project state
```

---

# 12. Do Not Give Every Agent Unrestricted Runtime Authority

Prime Agent uses a powerful persistent Python environment.

MAP should be more restrictive where authority matters.

Preferred model:

```text
Agent
 ↓
restricted workspace / worktree
 ↓
typed MAP API
 ↓
permission checks
 ↓
canonical operations
```

Especially for:

- helpers;
- local models;
- experimental agents;
- automated recovery processes.

Model capability and MAP authority must remain separate.

---

# 13. Target Architecture

A useful long-term MAP architecture would look like:

```text
                         bigboss
                            │
                            ▼
                  ┌──────────────────┐
                  │ CommandCenterUI  │
                  └────────┬─────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │          mapd          │
              │                        │
              │ Authority              │
              │ Tasks                  │
              │ Claims                 │
              │ Reviews                │
              │ Goals                  │
              │ Agent registry         │
              │ Runtime supervisor     │
              │ Scheduler              │
              │ Event stream           │
              └───────────┬────────────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
       Codex worker   Claude worker   Prime worker
           │              │              │
           ├── helper     ├── helper     ├── helper
           └── helper     └── helper     └── helper

                provider-neutral hcom
           ◄──────────────────────────►

                          │
             ┌────────────▼───────────┐
             │     MAP Host API       │
             │                        │
             │ task.claim()           │
             │ task.submit()          │
             │ context.get()          │
             │ review.submit()        │
             │ message.send()         │
             │ helper.spawn()         │
             │ memory.search()        │
             │ refine.propose()       │
             └────────────┬───────────┘
                          │
                   SQLite + files
```

---

# 14. Recommended Implementation Order

Do **not** begin by replacing MAP's orchestrator with Prime Agent.

Implement these concepts incrementally.

## Phase 1 — Persistent Runtime Supervisor

Build:

```text
mapd
agent registry
session registry
heartbeat
detach/reconnect
crash recovery
```

### Milestone

Closing CommandCenterUI or WezTerm does not terminate active agents.

---

## Phase 2 — Typed MAP API

Centralize canonical operations behind one authority boundary.

Build:

```text
task API
review API
agent API
message API
context API
health API
```

### Milestone

Agents no longer need direct SQLite or multi-file lifecycle writes.

---

## Phase 3 — MAP Skills Layer

Wrap common MAP workflows as discoverable skills.

Examples:

```text
map-task
map-review
map-context
map-health
map-handoff
map-repair
map-emergence
```

### Milestone

Agents need significantly less static MAP documentation in their normal context.

---

## Phase 4 — Persistent Runtime Goals

Connect task acceptance criteria to:

```text
session goal
verification gate
turn budget
token budget
time budget
continuation policy
```

### Milestone

Agents cannot stop autonomous work merely because they believe they are done; completion must pass the configured gate.

---

## Phase 5 — Persistent Helper Registry

Give helpers:

```text
stable identity
persistent context
resumable sessions
specialization
named owner
```

while retaining HPOM authority restrictions.

### Milestone

A core agent can resume the same specialist helper later without rebuilding its entire context.

---

## Phase 6 — Lossless Session Tree

Add:

```text
append-only session log
context segments
compaction summaries
parent references
on-demand expansion
session forks
```

### Milestone

Long-running sessions can compact aggressively without permanently losing prior context.

---

## Phase 7 — Harness Refinement

Build:

```text
refine.propose()
refinement records
evidence
versioning
rollback
approval classification
```

### Milestone

MAP can learn from repeated operating experience while governance-changing improvements still require proper authority.

---

# 15. Final Recommendation

Prime Agent should be treated as a source of ideas for **MAP's agent execution layer**, not as a replacement for MAP itself.

MAP should continue to own:

```text
intent
authority
tasks
ownership
review
risk
approval
release
canonical state
```

Prime-style runtime concepts can improve:

```text
session persistence
crash recovery
context handling
subagents
skills
long-running autonomy
goal continuation
runtime programming
self-improvement
```

The central design rule should be:

> **MAP governs the work. The runtime helps agents perform the work.**

That preserves MAP's strongest features while adopting the strongest ideas from Prime Agent.

---

## References

- Prime Intellect — Prime Agent overview: https://www.primeintellect.ai/blog/prime-agent
- Prime Agent GitHub repository: https://github.com/PrimeIntellect-ai/prime-agent
- MAP repository: https://github.com/BigCatMellow/MultiAgentProject
