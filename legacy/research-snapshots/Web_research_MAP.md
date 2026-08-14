# Deep-research conclusion

After looking across current agent frameworks, 2026 research, standards, security work, and newer orchestration systems, I think **Prime Agent is only one example of a much larger shift**.

The important realization is:

> **The model is becoming interchangeable. The harness around the model is increasingly where reliability, cost, memory, security, and long-horizon performance are won or lost.**

AWS now explicitly separates an agent's runtime from its harness; Temporal treats agents as durable workflows; OpenHands builds around immutable events and isolated workspaces; Agent Skills has become a cross-platform standard; and recent research shows orchestration design itself can materially change agent performance. ([AWS Documentation][1])

I also re-checked MAP's current state. MAP already has unusually strong **governance**: atomic claims, independent review, release gates, repair, risk, security policy, context policy, generated state, mirror validation, and operator authority.

So I would **not** spend the next major effort creating more governance documents or simply adding more agents.

The largest opportunities are underneath that layer.

## My technology radar for MAP

| Improvement                              |       Potential | Recommendation                       |
| ---------------------------------------- | --------------: | ------------------------------------ |
| One authoritative lifecycle/event system |     **Extreme** | Build                                |
| Durable agent execution                  |     **Extreme** | Evaluate Temporal / deeper LangGraph |
| Deterministic routine workflows          |     **Extreme** | Borrow or embed Lobster              |
| Isolated per-agent workspaces            |     **Extreme** | Build around containers/worktrees    |
| Standard Agent Skills                    |   **Very high** | Adopt directly                       |
| Dynamic single-vs-multi-agent routing    |   **Very high** | Add to HPOM                          |
| Unified policy-as-code authorization     |   **Very high** | Prototype Cedar                      |
| Full traces + trajectory evaluation      |   **Very high** | Adopt OTel + eval framework          |
| Dedicated Context Builder                |   **Very high** | Build                                |
| Evidence-based harness self-improvement  |   **Very high** | Build carefully                      |
| Persistent typed agent memory            |        **High** | Borrow from Letta/OpenClaw           |
| Provider-neutral runtime adapters        |        **High** | Build                                |
| A2A compatibility                        | **Medium-high** | Adapter, don't replace hcom          |
| MCP tool boundary                        |        **High** | Expand                               |
| Portable agent snapshots                 | **Medium-high** | Borrow AgentFile concepts            |
| More agents by default                   |    **Negative** | Avoid                                |

---

# 1. The biggest change: stop synchronizing multiple writable representations

This is the highest-leverage change I found.

MAP already recognizes this problem. SQLite coordinates state while task JSON and the task graph are synchronized human-readable mirrors, and MAP now validates them against one another. Your generated Active Lanes are already moving toward database-derived projections.

But synchronization creates a fundamental problem:

```text
SQLite
   ↕
TASK-123.json
   ↕
task_graph.json
   ↕
current-state.md
```

Whenever several representations can change, you eventually need:

```text
reconcile
validate
repair
mirror
sync
freshness checks
```

OpenHands takes a stronger approach. Its core is an **immutable append-only event stream**. Actions, observations, state updates, pauses, errors and context condensation all become typed events. Services observe the stream rather than independently modifying state. ([OpenHands Docs][2])

### I would evolve MAP toward this

```text
                   COMMAND
                      │
                      ▼
               MAP AUTHORITY API
                      │
              authorization check
                      │
                      ▼
          ┌───────────────────────┐
          │ SQLite transaction    │
          │                       │
          │ update current state  │
          │ append event          │
          └───────────┬───────────┘
                      │
             authoritative state
                      │
           ┌──────────┼───────────┐
           ▼          ▼           ▼
       task JSON   task graph  current-state
       projection  projection   projection
```

Those bottom files become **generated views**, not alternate writers.

For example:

```text
TASK DEFINITION
title
description
acceptance criteria
risk
inputs/outputs
```

can remain Git-backed human-readable source.

But:

```text
claimed_by
lease
attempt
status
review claim
submission
approval
release
session
heartbeat
```

should have **exactly one runtime authority**.

That means no agent manually changing `status` in JSON and no system trying to infer which copy is newer.

### Add these to every state-changing command

```text
event_id
actor
task_id
operation
timestamp
expected_version
idempotency_key
caused_by
correlation_id
trace_id
```

`expected_version` prevents an agent from writing against stale state.

`idempotency_key` means retrying the same operation after a crash cannot accidentally do it twice.

This directly attacks MAP's recurring `SYN-0001` class of problems instead of merely detecting the next occurrence.

---

# 2. Don't reinvent durable execution unless necessary

Prime Agent made me think MAP needed a custom persistent `mapd`.

After deeper research, I would slightly modify that advice:

> **MAP probably needs `mapd`, but `mapd` does not necessarily need to implement durable workflow execution itself.**

Temporal already solves a remarkable amount of this infrastructure.

Temporal workflows preserve execution state and can resume after process crashes, machine failures and temporary service outages. It supports retries, timers, signals, human intervention and long-running execution, and now explicitly supports AI-agent workloads. ([Temporal][3])

Conceptually:

```text
mapd
 │
 ├── authority
 ├── registry
 ├── API
 ├── policy
 └── operator controls
          │
          ▼
   Durable Executor
     Temporal
        OR
   LangGraph durable state
          │
          ▼
      Agent Runtime
```

MAP already uses LangGraph. LangGraph can persist execution state, pause for human input, checkpoint threads and resume later.

### Decision I would test

**Option A — deepen LangGraph**

Best if MAP remains predominantly a personal/local system.

**Option B — Temporal underneath MAP**

More attractive if MAP is going toward:

```text
Biggie
Smalls
additional machines
many concurrent workers
scheduled jobs
long-running agents
network failures
persistent workflows
```

Temporal would eliminate a large amount of custom retry/resume/watcher logic.

I would run a small proving implementation rather than commit MAP to it immediately.

---

# 3. Add a deterministic workflow engine

This finding may save MAP enormous amounts of agent effort.

OpenClaw's **Lobster** addresses a simple problem: why let the LLM repeatedly reason through a process that has already been decided?

Lobster turns multi-step operations into typed workflows with retries, conditions, timeouts, human approval gates and resumable execution. Its own documentation explicitly describes the benefit as avoiding repeated model re-planning. ([GitHub][4])

MAP has many operations like this.

For example, release currently conceptually requires:

```text
inspect task
→ validate state
→ inspect review
→ validate evidence
→ run appropriate tests
→ verify mirrors
→ evaluate risk checklist
→ release
→ update projection
→ log event
```

Most of those steps do not require intelligence.

Create:

```text
map-flow
```

Then:

```yaml
name: release-task

steps:
  - validate-task
  - validate-mirrors
  - verify-review
  - run-required-tests

  - approval:
      when: high-risk

  - release-task
  - rebuild-projections
  - record-release
```

The LLM only gets called where judgment is needed.

This would make MAP:

**cheaper**, because fewer agent turns are used;

**safer**, because process steps cannot simply be forgotten;

**more predictable**, because the same workflow means the same sequence;

**easier to test**, because a pipeline is inspectable data;

**easier to resume**, because each step has state.

MAP's July state showed **29 independently approved tasks waiting at the release stage**.

That is exactly the kind of situation where deterministic orchestration should absorb the mechanical portion and surface only unresolved factual checks.

Lobster itself is MIT-licensed and embeddable, so this is one of the rare cases where I would seriously investigate **using an existing component**, not merely imitating the idea. ([GitHub][5])

---

# 4. Every coding agent should get its own isolated workspace

This showed up repeatedly.

OpenHands recommends Docker isolation and supports the same workspace API across local, Docker and remote environments. ([OpenHands Docs][6])

AWS AgentCore runs each agent session inside an isolated microVM. ([AWS Documentation][7])

Warren provisions isolated environments for coding-agent runs. ([GitHub][8])

And recent software-engineering research found that **centralized delegation + isolated workspaces + structured merging** materially improved multi-agent performance; Git worktrees and branch-and-merge were identified as important coordination primitives. ([arXiv][9])

MAP should formalize:

```text
TASK-400
   │
   ▼
Agent Runtime
   │
   ▼
Dedicated Git worktree
   │
   ▼
Sandbox/container
   │
   ├── scoped filesystem
   ├── scoped credentials
   ├── scoped network
   ├── resource budget
   └── agent tools
```

Then successful work produces:

```text
commit / branch / patch
```

not uncontrolled edits to the shared checkout.

This would reduce:

```text
agents overwriting each other
dirty working trees
accidental unrelated edits
merge races
half-completed changes contaminating another task
```

The value increases dramatically as MAP scales beyond two main agents.

---

# 5. Create one `AgentRuntime` interface

MAP should stop caring whether the worker happens to be:

```text
Claude Code
Codex
Prime Agent
Gemini
Pi
Aider
OpenHands
future agent X
```

Define a contract.

```python
start()
resume()
send()
steer()
pause()
cancel()
snapshot()
health()
capabilities()
usage()
artifacts()
```

Each provider gets an adapter.

```text
AgentRuntime
   │
   ├── ClaudeRuntime
   ├── CodexRuntime
   ├── PrimeRuntime
   ├── OpenHandsRuntime
   └── LocalRuntime
```

Warren already demonstrates the general value of a harness-agnostic control plane over different coding agents. ([GitHub][8])

OpenHands similarly exposes common local and remote workspace APIs. ([OpenHands Docs][10])

This is what would make MAP genuinely **model- and vendor-independent**.

HPOM could then ask:

```text
What capability does this task require?
```

instead of:

```text
Which particular program should I launch?
```

---

# 6. Adopt the Agent Skills standard rather than inventing MAP skills

This one has moved from “interesting idea” to something I think MAP should simply adopt.

Agent Skills is now an open folder-based standard where a `SKILL.md` plus supporting scripts/resources teaches an agent a reusable procedure. GitHub Copilot supports it and automatically discovers repository/project skills; Anthropic publishes the specification and examples. ([GitHub Docs][11])

MAP has huge amounts of procedural knowledge currently expressed as documentation.

Instead:

```text
.agents/skills/
    map-task/
        SKILL.md

    map-review/
        SKILL.md

    map-release/
        SKILL.md

    map-repair/
        SKILL.md

    map-context/
        SKILL.md

    map-research/
        SKILL.md

    map-handoff/
        SKILL.md
```

For example:

```text
map-review

Purpose:
Perform an independent MAP review.

Resources:
review schema
severity definitions
review validator

Scripts:
claim-review.py
validate-review.py
```

The agent discovers it when required instead of having thousands of tokens of MAP procedure permanently loaded.

This matches your own Context System almost perfectly.

And because it is an open format, those skills can increasingly travel between agent products rather than MAP maintaining Claude-specific, Codex-specific, Gemini-specific instructions. ([GitHub Docs][11])

---

# 7. HPOM needs a second dimension: orchestration topology

This is one of the most significant research findings.

Google Research tested **180 agent configurations** and found that multi-agent systems improved parallelizable tasks substantially, but all tested multi-agent architectures degraded sequential planning tasks by **39–70%**. Independent agents also amplified errors much more than centrally coordinated agents. Their predictor chose the best architecture for 87% of unseen configurations using task properties such as decomposability and tool usage. ([Google Research][12])

ACL 2026's MAS-BENCH separately found that success drops as agent count increases because agents struggle with shared state, common conventions and termination. ([ACL Anthology][13])

That suggests HPOM currently answers only half the question:

```text
WHO should do this?
```

It should also answer:

```text
HOW MANY workers should do this?
HOW should they be connected?
```

I would add an **orchestration classifier**:

| Task shape                      | MAP topology                         |
| ------------------------------- | ------------------------------------ |
| Sequential, tool-heavy          | One agent                            |
| Sequential + high risk          | One owner + independent reviewer     |
| Clearly decomposable            | Coordinator + parallel workers       |
| Independent research dimensions | Parallel researchers + synthesizer   |
| Highly coupled files            | One implementation agent             |
| Broad independent file groups   | Isolated worktrees + parallel agents |
| Genuine disagreement            | Debate/critique                      |
| Mechanical pipeline             | No agent — `map-flow`                |

This is a major conceptual improvement:

> **Use agents because the task benefits from parallel intelligence, not because agents are available.**

That could reduce both token use and coordination failures.

---

# 8. Add a real authorization engine beneath the agents

MAP already has an excellent conceptual permissions system.

The missing step is making authorization **code-owned**, rather than relying primarily on agents and provider hooks to behave correctly.

NIST's 2026 work on software-agent identity explicitly calls out identification, authorization, auditing, non-repudiation and prompt-injection controls as key agent-system problems. ([NIST][14])

Cedar is particularly interesting for MAP because its authorization question is exactly:

```text
Can this PRINCIPAL
perform this ACTION
on this RESOURCE
in this CONTEXT?
```

It also explicitly documents patterns for AI/software agents acting on behalf of users. ([Cedar Policy Language Reference Guide][15])

Imagine:

```text
principal:
  helper-security-17

action:
  file.write

resource:
  Source/foo.py

context:
  task: TASK-400
  owner: codex
  sandbox: worktree-400
```

MAP policy:

```text
helper may write
only if:
task output_paths includes resource
AND helper owner matches task owner
AND workspace == task sandbox
```

Another:

```text
principal: codex
action: release
resource: TASK-400
```

Policy engine determines:

```text
DENY
reason:
independent review missing
```

The model doesn't get to negotiate with that rule.

### This changes security from

```text
"Claude was instructed not to do X."
```

to:

```text
"X is impossible through MAP's authority API."
```

That distinction matters.

---

# 9. Treat provider permission hooks as defense-in-depth only

Related to the above, recent security research increasingly emphasizes that agent security is contextual: who requested the action, what objective the agent is authorized to pursue, whether the action serves that objective, and where data may flow. ([arXiv][16])

Google's multi-agent security research also found prompting helps but does not eliminate multi-turn attacks, arguing for dynamic runtime state and intent analysis. ([Google Research][17])

Therefore MAP's trust hierarchy should be:

```text
Provider prompt/hooks
        ↓
useful guardrail

MAP API authorization
        ↓
real authority

Sandbox permissions
        ↓
hard execution boundary

OS/network permissions
        ↓
ultimate boundary
```

Not:

```text
"Claude/Codex says this helper isn't allowed."
```

---

# 10. Make observability a first-class MAP subsystem

MAP already logs a lot.

But logs are not quite the same thing as a **causal trace**.

OpenTelemetry now has GenAI conventions covering operations such as:

```text
invoke_agent
invoke_workflow
execute_tool
retrieval
```

as well as provider, model, tokens, conversation IDs and other agent telemetry. ([OpenTelemetry][18])

Every MAP operation should share one trace:

```text
TASK-400
  trace=abc123

operator request
      │
      ├── routing decision
      │
      ├── agent invocation
      │    ├── LLM call
      │    ├── tool call
      │    ├── file edit
      │    └── tests
      │
      ├── submission
      │
      ├── review
      │
      └── release
```

Then CommandCenter can answer:

```text
Why did TASK-400 take so long?

32% model latency
18% tool execution
21% waiting on reviewer
12% context rebuilding
9% retries
8% other
```

or:

```text
Why did it fail?

agent attempted the same tool sequence
six times after an identical error
```

This leads directly into the next major improvement.

---

# 11. MAP needs a harness evaluation suite

Right now, MAP tests whether its **software** works.

It should also test whether its **agents behave better** after MAP changes.

LangSmith's current evaluation model is instructive: use offline datasets to test before release, evaluate live traces online, turn production failures into new offline cases, and use those cases to ensure fixes don't regress. ([Docs by LangChain][19])

MAP has something unusually valuable already:

**months of real failures.**

Examples from its own history include:

```text
stale mirrors
self-review attempts
bad task metadata
unclaimed review work
incomplete releases
agents continuing too long
context rotation problems
duplicate state authorities
helper communication failures
```

Those should become:

```text
MAP_System/evals/
    mirror-drift.yaml
    self-review.yaml
    stale-context.yaml
    output-path-violation.yaml
    duplicate-claim.yaml
    runaway-helper.yaml
    premature-done.yaml
```

Now suppose you change:

```text
map-review skill
```

Run the historical eval suite.

Compare:

```text
old harness
new harness
```

on:

```text
task success
tokens
turns
tool calls
retries
policy violations
operator interruptions
duplicate work
time to completion
```

Then MAP development becomes empirical rather than:

```text
"This new rule sounds like an improvement."
```

---

# 12. Create a dedicated Context Builder

Your file-first decision is supported by recent research.

ACL 2026's **FS-Researcher** used a dedicated Context Builder that writes a durable filesystem knowledge base, with another agent consuming it. The work found report quality correlated positively with compute devoted to the Context Builder. ([ACL Anthology][20])

In plain terms:

> Spending intelligence deciding **what the worker should know** may be more valuable than adding another worker.

MAP already has context packets. I would operationalize them.

```text
TASK
  │
  ▼
Context Builder
  │
  ├── canonical docs
  ├── applicable decisions
  ├── relevant history
  ├── related code
  ├── known failures
  └── acceptance evidence
       │
       ▼
   CONTEXT PACKET
```

And the packet should explicitly record:

```text
Required
Optional
Excluded
Why included
Why excluded
Source
Freshness
Canonicality
```

Then give execution agents that packet.

Not access to "all MAP knowledge by default."

---

# 13. Add hybrid search over MAP's knowledge

OpenClaw's current built-in memory system combines SQLite FTS5 keyword retrieval with vector/semantic retrieval. ([GitHub][21])

That's appropriate for MAP because MAP has both:

**exact identifiers**

```text
TASK-316
DEC-028
map_authority.py
```

and conceptual queries:

```text
"What previously went wrong when two agents wrote shared state?"
```

Keyword search is better for the first.

Semantic search is often better for the second.

So:

```text
map-search
```

could combine:

```text
BM25 / FTS
+
vector similarity
+
canonicality
+
freshness
+
project scope
```

Critically, **canonicality must outweigh semantic similarity**.

A very relevant obsolete artifact should not outrank the current policy.

---

# 14. Typed persistent memory, but never canonical memory

Letta's AgentFile standard serializes stateful agents including model config, current context state, memory blocks and tool rules, while intentionally excluding live secrets on export. ([Letta Docs][22])

I would borrow the structure.

A MAP agent might have:

```text
Agent Memory

obligations
working hypotheses
recent failures
learned repository conventions
preferred tools
unfinished investigations
specialist knowledge
```

But every block carries:

```text
authority: NONCANONICAL
source:
last_verified:
scope:
expires:
```

The distinction remains:

```text
MAP truth        != agent memory
```

Agent memory improves continuity.

MAP files/DB determine reality.

---

# 15. Build a portable MAP Agent Snapshot

Borrowing Prime Agent + AgentFile:

```text
foo.mapagent
```

could contain:

```text
identity
runtime adapter
model/provider
skill versions
current task
runtime goal
checkpoint
memory references
context summary
sandbox manifest
resource budget
child helper registry
capabilities
```

Never:

```text
API keys
OAuth tokens
canonical decisions
authority by implication
```

That gives MAP real portability:

```text
Biggie agent
       ↓ snapshot
Smalls
       ↓
resume
```

or:

```text
Claude unavailable
       ↓
same MAP Agent Snapshot
       ↓
Codex-compatible runtime
```

It pushes MAP farther toward **worker independence from model provider**.

---

# 16. Harness self-improvement should become scientific

Prime Agent's `/refine` idea is part of a broader research direction.

The 2026 **Agentic Harness Engineering** work represents harness components explicitly, compresses trajectories into usable evidence, and—most importantly—pairs each harness modification with a prediction that is tested against later outcomes. Its reported Terminal-Bench improvement came primarily from tools, middleware and long-term memory rather than simply rewriting the system prompt. ([DOI][23])

Continual Harness likewise evolves memory, skills, subagents and prompts from experience. ([Continual Harness][24])

MAP already has Emergence + Self-Repair.

The missing part is an experimental contract:

```text
REFINE-0042

Observation:
Agents repeatedly re-read five MAP documents before review.

Hypothesis:
A map-review skill containing those rules will reduce
review context cost by >=25% without increasing missed findings.

Change:
map-review/SKILL.md v4 → v5

Evaluation:
50 historical review cases

Before:
42k average tokens
94% acceptance-finding recall

After:
30k average tokens
95% acceptance-finding recall

Decision:
PROMOTE
```

That would make MAP **learn from itself without blindly rewriting itself**.

And your existing authority system remains the safeguard:

```text
skills/tactics      → evidence + review
workflow changes    → core review
security/authority  → operator approval
```

I think this could eventually become one of MAP's defining capabilities.

---

# 17. Turn repeated prose rules into executable guardrails

A recurring theme in current harness research is moving guarantees out of prompts and into code.

A recent study on auditable harness design found that code-owned enforcement survived model substitutions much better than prompt-only constraints in its evaluation. ([arXiv][25])

So if MAP keeps encountering:

```text
"Agents sometimes forget X."
```

the progression should be:

```text
first occurrence
→ instruction

second recurrence
→ skill

repeated recurrence
→ executable check

safety-critical invariant
→ hard policy
```

Examples:

```text
"Do not self-review."
```

should not primarily be documentation.

You already correctly made it a mechanical gate.

Apply that philosophy everywhere.

---

# 18. Add resource budgets and circuit breakers

The runtime needs explicit budgets:

| Budget               | Example        |
| -------------------- | -------------- |
| Tokens               | 100k           |
| Agent turns          | 25             |
| Wall-clock execution | bounded        |
| Helpers              | max 3          |
| Helper depth         | max 1–2        |
| Concurrent agents    | task-dependent |
| Tool retries         | 3              |
| Network calls        | scoped         |
| Disk                 | bounded        |
| Cost                 | task budget    |

Recent multi-agent research gives a strong reason: coordination overhead grows with tool count and agent count. ([Google Research][12])

And MCP's durable-task guidance similarly recommends concurrency and lifetime limits for long-running tasks. ([Model Context Protocol][26])

An agent that hits a budget should not automatically receive more.

It produces:

```text
BUDGET_EXHAUSTED

Progress: 83%
Blocker: failing integration test
Suggested extension: 20k tokens
```

MAP or the operator decides.

---

# 19. Adopt MCP as a tool interface, not as MAP's brain

MCP continues to mature rapidly. The July 28, 2026 specification moved long-running Tasks into an explicit extension and further hardened authorization. ([Model Context Protocol][27])

MCP is good for:

```text
GitHub
filesystem
browser
database
email
testing
external APIs
specialized tools
```

MAP could expose:

```text
MAP MCP server
```

but I would initially make much of it read-only:

```text
map.task.get
map.task.search
map.context
map.agent.status
map.artifact.get
```

State-changing operations should still funnel through MAP's explicit authority API.

MCP is a **tool protocol**.

It should not become the canonical lifecycle authority.

---

# 20. A2A is worth supporting at MAP's boundary

A2A 1.0 is now a released interoperability standard. It defines Agent Cards for identity/capabilities/authentication and separates Tasks, Messages and Artifacts. ([GitHub][28])

This maps remarkably well onto MAP.

```text
A2A Agent Card
      ↕
MAP agent capability record

A2A Task
      ↕
MAP task adapter

A2A Message
      ↕
hcom

A2A Artifact
      ↕
MAP artifacts/
```

I would **not replace hcom**.

I would build:

```text
hcom adapter
A2A adapter
```

over the same MAP messaging layer.

That would eventually let an external compliant agent participate in MAP without becoming a MAP-native program.

---

# What I would reuse versus build

| Technology                          | My recommendation                                               |
| ----------------------------------- | --------------------------------------------------------------- |
| **Agent Skills**                    | Adopt standard directly                                         |
| **OpenTelemetry GenAI conventions** | Adopt directly                                                  |
| **MCP**                             | Adopt for tool integration                                      |
| **A2A**                             | Support as external interoperability layer                      |
| **Temporal**                        | Serious proof-of-concept as durable executor                    |
| **Lobster**                         | Investigate embedding/forking rather than rewriting immediately |
| **Cedar**                           | Prototype as MAP policy engine                                  |
| **OpenHands**                       | Borrow event/workspace architecture; don't replace MAP          |
| **Warren**                          | Borrow runtime adapter + sandbox patterns                       |
| **Letta AgentFile**                 | Borrow snapshot/memory schema concepts                          |
| **OpenClaw memory**                 | Borrow hybrid local retrieval approach                          |
| **Beads**                           | Do not replace MAP task system; borrow dependency patterns      |
| **Prime Agent**                     | Runtime adapter + borrow persistence/refinement ideas           |
| **AWS AgentCore**                   | Architecture reference unless you want MAP cloud-hosted         |

---

# A MAP 2.0 architecture suggested by the research

```text
                           OPERATOR
                              │
                              ▼
                    ┌───────────────────┐
                    │  CommandCenterUI  │
                    └─────────┬─────────┘
                              │
                              ▼
             ┌─────────────────────────────┐
             │            mapd             │
             │                             │
             │ Identity                    │
             │ Authority                   │
             │ Policy Engine               │
             │ Task API                    │
             │ Agent Registry              │
             │ Runtime Goals               │
             │ Budgets                     │
             └──────────────┬──────────────┘
                            │
                      COMMAND BUS
                            │
                     authorize action
                            │
                            ▼
                ┌──────────────────────┐
                │ Canonical MAP State  │
                │                      │
                │ task runtime         │
                │ claims / leases      │
                │ reviews              │
                │ events               │
                │ sessions             │
                └──────────┬───────────┘
                           │
                       projections
             ┌─────────────┼──────────────┐
             ▼             ▼              ▼
          task JSON     task graph    current-state
             │
             │
       ┌─────▼──────────────────────────┐
       │ Durable Workflow Engine       │
       │                               │
       │ Temporal / LangGraph          │
       │ map-flow deterministic flows  │
       └─────────────┬─────────────────┘
                     │
              topology selection
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Claude      Codex     Prime/etc.
          │          │          │
          ▼          ▼          ▼
       isolated   isolated   isolated
       worktree   worktree   worktree
       sandbox    sandbox    sandbox
          │
          └──────────┬──────────┘
                     │
                    hcom
                     │
                A2A adapter
                     │
          ┌──────────▼──────────┐
          │   MAP Tool Gateway  │
          │                     │
          │ MCP                 │
          │ scoped credentials  │
          │ policy enforcement  │
          └─────────────────────┘

       Everything emits OpenTelemetry traces
                     │
                     ▼
             Harness Evaluation
                     │
                     ▼
             Refinement Proposals
```

That is much closer to what I think **MAP could ultimately become**.

---

# What I would build next

1. **Write a new state-authority design** separating immutable task specification from canonical runtime lifecycle state; make JSON, task graph and generated current-state runtime fields projections rather than alternate writers.
2. **Build the typed `mapd` command API** with actor identity, idempotency keys, expected versions, audit events and one authorization seam.
3. **Prototype durable execution** using the same representative MAP workflow in deeper LangGraph persistence and Temporal, then choose based on complexity and recovery behavior.
4. **Add `map-flow`** and move release, review setup, reconciliation, context rotation and helper lifecycle into deterministic resumable workflows.
5. **Define `AgentRuntime`** and put coding workers in isolated Git worktrees/sandboxes rather than allowing concurrent work in one mutable checkout.
6. **Convert MAP's operational knowledge into Agent Skills**, beginning with task, review, release, context, research and repair.
7. **Instrument MAP with OpenTelemetry and build a historical harness-evaluation corpus** from real failures already recorded in the repository.
8. **Extend HPOM into an orchestration selector** that chooses single agent, owner+reviewer, parallel workers or deterministic workflow based on decomposability, tool density, coupling, risk and cost.
9. **Put policy-as-code below the agents**, testing Cedar-style `principal/action/resource/context` authorization and giving agents short-lived scoped capabilities.
10. **Build Context Builder + hybrid MAP search**, followed by typed noncanonical agent memory and portable session snapshots.
11. **Add evidence-driven `refine.propose()` only after evaluation exists**, so MAP can improve skills, middleware and runtime behavior against measurable outcomes without autonomously changing authority.

That order matters. **Self-improvement before observability/evaluation would let MAP optimize itself without being able to tell whether it actually improved.**

---

## One thing I would specifically avoid

I would resist the temptation to turn MAP into:

```text
20 agents
talking constantly
with enormous contexts
and elaborate hierarchies.
```

The evidence is pointing the other way.

The strongest emerging architecture is more like:

```text
very strong durable control plane
+
small number of capable agents
+
excellent context
+
isolated execution
+
deterministic routine workflows
+
hard verification
+
selective parallelism
```

Google's results on coordination penalties, ACL's scaling failures, and the recent success of isolated branch-and-merge approaches all point in that direction. ([Google Research][12])

## Research confidence

I weighted **standards and primary documentation** such as MCP, A2A, OpenTelemetry, NIST, Temporal, OpenHands and Cedar most heavily. I also weighted peer-reviewed ACL/ICLR work relatively strongly. The 2026 harness-evolution literature is particularly interesting, but much of it is still preprint/arXiv research, so I would treat its numerical results as promising evidence rather than established engineering law. ([DOI][23])

The overall direction, however, is unusually consistent across independent sources: **durable execution, isolation, deterministic enforcement, selective context, standardized capabilities, traceability and evaluation are becoming the core infrastructure around capable models.** AWS's newly released managed harness independently bundles almost exactly those concerns—runtime isolation, state, skills, memory, identity, observability and versioning—which is a useful outside validation of the direction MAP is already heading. ([AWS Documentation][29])

I would consider the **canonical state redesign + `mapd` authority API + deterministic `map-flow` + runtime isolation + evaluation system** the five most consequential findings from this research. They are more important to MAP's long-term capability than simply plugging Prime Agent into it.

* [TechRadar](https://www.techradar.com/pro/why-cybersecurity-must-evolve-for-the-age-of-ai-agents?utm_source=chatgpt.com)
* [TechRadar](https://www.techradar.com/pro/the-infrastructure-debt-ai-creates-isnt-in-the-code-its-in-the-operations?utm_source=chatgpt.com)

[1]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-vs-runtime.html?utm_source=chatgpt.com "AgentCore harness vs. Runtime - Amazon Bedrock AgentCore"
[2]: https://docs.openhands.dev/sdk/arch/events?utm_source=chatgpt.com "Events - OpenHands Docs"
[3]: https://temporal.io/ai/agentic-ai?utm_source=chatgpt.com "Talk to an Expert: How Temporal Powers Agentic AI | Temporal"
[4]: https://github.com/openclaw/lobster?utm_source=chatgpt.com "GitHub - openclaw/lobster: Lobster is a Openclaw-native workflow shell: a typed, local-first “macro engine” that turns skills/tools into composable pipelines and safe automations—and lets Openclaw call those workflows in one step. · GitHub"
[5]: https://github.com/openclaw/lobster/blob/main/package.json?utm_source=chatgpt.com "lobster/package.json at main · openclaw/lobster · GitHub"
[6]: https://docs.openhands.dev/openhands/usage/architecture/runtime?utm_source=chatgpt.com "Runtime Architecture - OpenHands Docs"
[7]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-sessions.html?utm_source=chatgpt.com "Use isolated sessions for agents - Amazon Bedrock AgentCore"
[8]: https://github.com/jayminwest/warren?utm_source=chatgpt.com "GitHub - jayminwest/warren: Coolify for coding agents. Control plane for your agents that operate in isolation, self-manage, self-repair, and self-improve all on your infrastructure. · GitHub"
[9]: https://arxiv.org/abs/2603.21489?utm_source=chatgpt.com "Effective Strategies for Asynchronous Software Engineering Agents"
[10]: https://docs.openhands.dev/sdk/guides/agent-server/overview?utm_source=chatgpt.com "Overview - OpenHands Docs"
[11]: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills?utm_source=chatgpt.com "About agent skills - GitHub Docs"
[12]: https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/?utm_source=chatgpt.com "Towards a science of scaling agent systems: When and why agent systems work"
[13]: https://aclanthology.org/2026.findings-acl.1698/?utm_source=chatgpt.com "When 20 Agents Fail to Sort: The Distributed Sorting Benchmark for Scalable Multi-Agent Systems - ACL Anthology"
[14]: https://www.nist.gov/news-events/news/2026/02/new-concept-paper-identity-and-authority-software-agents?utm_source=chatgpt.com "New Concept Paper on Identity and Authority of Software Agents | NIST"
[15]: https://docs.cedarpolicy.com/bestpractices/bp-using-the-context.html?utm_source=chatgpt.com "Using the context | Cedar Policy Language Reference Guide"
[16]: https://arxiv.org/abs/2607.22024?utm_source=chatgpt.com "Agent Security Needs Redefinition through a Holistic Framework"
[17]: https://research.google/pubs/securing-multi-agent-systems-an-empirical-analysis-of-security-prompt-hardening-and-residual-risks/?utm_source=chatgpt.com "Securing Multi-Agent Systems: An Empirical Analysis of Security Prompt Hardening and Residual Risks"
[18]: https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/?utm_source=chatgpt.com "Gen AI | OpenTelemetry"
[19]: https://docs.langchain.com/langsmith/engine?utm_source=chatgpt.com "Find and fix your agent's failures with LangSmith Engine - Docs by LangChain"
[20]: https://aclanthology.org/2026.acl-long.288/?utm_source=chatgpt.com "FS-Researcher: Test-Time Scaling for Long-Horizon Research Tasks with File-System-Based Agents - ACL Anthology"
[21]: https://github.com/openclaw/openclaw/blob/main/docs/concepts/memory-builtin.md?utm_source=chatgpt.com "openclaw/docs/concepts/memory-builtin.md at main · openclaw/openclaw · GitHub"
[22]: https://docs.letta.com/guides/core-concepts/agent-file?utm_source=chatgpt.com "AgentFile (.af) | Letta Docs"
[23]: https://doi.org/10.48550/arXiv.2604.25850?utm_source=chatgpt.com "[2604.25850] Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"
[24]: https://continual-harness.github.io/?utm_source=chatgpt.com "Continual Harness: An Efficient Self-Improving Agent on ARC-AGI-3"
[25]: https://arxiv.org/abs/2607.08028?utm_source=chatgpt.com "From Prompts to Contracts: Harness Engineering for Auditable Enterprise LLM Agents"
[26]: https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks?utm_source=chatgpt.com "Tasks - Model Context Protocol"
[27]: https://modelcontextprotocol.io/seps/2663-tasks-extension?utm_source=chatgpt.com "SEP-2663: Tasks Extension - Model Context Protocol"
[28]: https://github.com/a2aproject/A2A/blob/main/docs/topics/agent-discovery.md?utm_source=chatgpt.com "A2A/docs/topics/agent-discovery.md at main · a2aproject/A2A · GitHub"
[29]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness.html?utm_source=chatgpt.com "AgentCore harness - Amazon Bedrock AgentCore"

