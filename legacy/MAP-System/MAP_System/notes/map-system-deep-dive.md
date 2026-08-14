<!-- hpom: file: notes/map-system-deep-dive.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-18 -->
<!-- hpom: verified_against: TASK-250 architecture and runtime inspection -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Understanding MAP: A Plain-English Academic Deep Dive

## Purpose of this guide

This guide explains what MAP is *as a whole system*. It is not a list of
features and it is not a short operating checklist. Its purpose is to give a
human owner enough conceptual understanding to question the design, recognize
where it is helping, and decide what should change.

MAP has grown beyond a folder of task files. It is now a **socio-technical
coordination system**: part software, part institutional memory, part workflow,
and part constitution for human–AI collaboration. It coordinates models that
cannot share a mind, may stop unexpectedly, have different strengths, and must
not quietly acquire authority merely because they can act.

The shortest accurate description is:

> MAP is an inspectable operating system for multi-agent work. It turns human
> intent into bounded tasks, assigns work according to capability and
> authority, preserves state outside any model's memory, verifies important
> transitions, and returns unresolved judgment to the human owner.

That sentence contains five distinct jobs:

1. interpret and shape intent;
2. coordinate workers;
3. preserve memory and state;
4. enforce quality and safety boundaries;
5. help the human remain the actual source of direction.

The rest of this document develops those ideas carefully.

---

## 1. The problem MAP is trying to solve

### 1.1 A group of AI agents is not automatically a team

Two capable models working in the same repository do not naturally form a
coherent organization. Without coordination, they can:

- start the same work at the same time;
- edit the same file for different reasons;
- rely on different versions of project history;
- assume a chat message is permanent authority;
- lose their stopping point when a session ends;
- declare success without independent verification;
- create useful ideas that silently redirect the project;
- ask the human to arbitrate routine details, or fail to ask when a real human
  decision is required.

These are not primarily intelligence failures. They are **coordination
failures**. A brilliant worker can still duplicate another worker, read stale
instructions, or exceed its authority.

MAP treats coordination as an engineering problem. Instead of hoping every
agent remembers every rule, it externalizes the important rules and state into
files, a database, validators, and visible operator surfaces.

### 1.2 Model memory is the wrong place for institutional memory

An AI session has temporary context. It can be compacted, exhausted, closed,
or replaced. Therefore a chat transcript cannot safely serve as the project's
only memory.

MAP's foundational move is **externalized cognition**: important project
knowledge is written into inspectable artifacts that survive the worker that
created them. The project remembers through task records, decisions, current
state, events, reviews, handoffs, and artifacts.

This resembles how mature human organizations use tickets, design records,
lab notebooks, source control, and operating procedures. The point is not
bureaucracy for its own sake. The point is that the organization must know
more than any one participant currently remembers.

### 1.3 Capability and authority are different things

An agent may be technically capable of deleting a file, changing a policy, or
launching another model. That does not mean it has the authority to do so.

MAP explicitly separates:

- **capability** — what a worker can physically or intellectually do;
- **assignment** — what work it has been asked to do;
- **ownership** — what output it is accountable for;
- **authority** — what decisions or state changes it is allowed to make;
- **approval** — what another authorized party has accepted.

This separation is one of MAP's most important ideas. It prevents technical
access from quietly becoming governance power.

---

## 2. The complete mental model

MAP is easiest to understand as several interacting planes rather than one
application.

```text
 HUMAN DIRECTION
 goals, priorities, approvals, scope, product judgment
                         │
                         ▼
 INTAKE AND GOVERNANCE
 classify intent → identify risk/authority → shape work
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
 KNOWLEDGE AND DISCOVERY          EXECUTION CONTROL
 research, context, decisions,    tasks, dependencies,
 emergence, shared memory         claims, leases, routing
           │                           │
           └─────────────┬─────────────┘
                         ▼
 WORKERS
 Codex, Claude, visible helpers, local models, Aider
                         │
                         ▼
 VERIFICATION AND CHANGE CONTROL
 tests → review → changes requested → approval → release
                         │
                         ▼
 LEARNING AND RECOVERY
 events, repairs, replay, retrospectives, practice scenarios

 COMMAND CENTER = a human-facing view across these planes
 HCOM           = the live communication bus between participants
```

No single box is MAP by itself. MAP is the relationship among them.

### 2.1 An academic interpretation

MAP combines ideas from several established fields:

- **Distributed systems:** multiple workers act concurrently, so claims and
  transitions need atomic coordination rather than trust alone.
- **Finite-state machines:** work moves through named states with defined
  transition conditions.
- **Event sourcing:** an append-only event history explains how current state
  was reached.
- **Read models:** human-readable JSON and UI views are projections of more
  authoritative state.
- **Capability security and least privilege:** workers receive only the
  authority appropriate to their tier and task.
- **Organizational theory:** roles, ownership, independent review, escalation,
  and institutional memory make a group more reliable than isolated actors.
- **Cybernetics:** MAP observes its own performance, detects drift, and feeds
  learning back into future behavior.
- **Scientific method:** research separates claims from assumptions, while
  experiments test proposed improvements before they become policy.

MAP is not a pure implementation of any one of these traditions. It is a
practical synthesis designed for inspectable AI collaboration.

---

## 3. The three kinds of truth

Many MAP problems become understandable once its three state domains are kept
separate.

### 3.1 SQLite: current coordination truth

`MAP_System/map.db` is authoritative for mutable coordination facts that must
change atomically:

- who has claimed a task;
- whether a lease is still active;
- whether a task is READY, IN_PROGRESS, SUBMITTED, APPROVED, or RELEASED;
- task dependencies, output paths, and acceptance criteria;
- open review claims;
- approval gates and release records;
- agent availability records and canonical MAP events.

“Atomic” means two agents cannot both successfully claim the same READY task
if they use the claim system. The database updates one row under a transaction;
only one attempt wins.

This is the equivalent of the live control ledger.

### 3.2 Files: explanatory and inspectable truth

Files are the readable project brain:

- `shared/` explains current facts, requirements, constraints, decisions, and
  unresolved questions;
- `tasks/` mirrors individual task records in human-readable JSON;
- `workflow/task_graph.json` mirrors the task board as one graph;
- `artifacts/` stores outputs, reviews, research, tests, and planning records;
- `handoffs/` stores continuation context;
- `events/events.jsonl` provides a durable append-only activity history;
- `emergence/` stores observations and ideas that have not yet become
  authorized work.

The files make MAP auditable without requiring a database browser. They also
give future agents scoped context they can read.

### 3.3 hcom: live conversational truth

hcom is the real-time communication bus. It carries messages between the
operator and agents and between agents themselves. Its intents are:

- `inform` — useful information, no reply required;
- `request` — a reply or decision is required;
- `ack` — the request was received or resolved; no further response required.

hcom is excellent for attention and coordination, but it is **not** durable
MAP authority. Its message database remains separate from MAP's event log and
session-replay database. If a conversation produces a lasting decision,
ownership transfer, review verdict, or task change, that result must be
promoted into the appropriate MAP file or database record.

This boundary is deliberate:

```text
hcom says what participants are saying now.
MAP says what the project has durably accepted as true or actionable.
```

### 3.4 Mirrors and why they are both useful and dangerous

MAP keeps SQLite state and file mirrors. This is a form of **command/query
separation**:

- the database is good at safe mutation and concurrency;
- the files are good at inspection, versioning, and model context.

The cost is synchronization risk. If SQLite says SUBMITTED but the JSON mirror
says IN_PROGRESS, two versions of reality exist. `export_to_files.py` rebuilds
the file mirrors from SQLite, and `validate_task_mirrors.py` blocks approval or
release when they disagree.

This dual representation is powerful, but it is also one of MAP's main sources
of complexity. A future simplification should preserve both atomic mutation and
human inspectability without allowing hand-edited mirrors to impersonate the
canonical state.

---

## 4. Human authority and the constitutional layer

### 4.1 The operator is the source of final intent

MAP is “human-paced” because the human does not merely watch the agents. The
human defines goals, priorities, risk tolerance, and authority boundaries.

Routine implementation details should not interrupt the operator. The system
should stop and ask when the answer changes:

- project scope;
- product or story intent;
- privacy or credentials exposure;
- destructive actions;
- external publication;
- agent permissions or MAP-wide policy;
- unresolved ownership conflicts;
- a high-impact tradeoff with no already-approved answer.

The Command Center is intended to concentrate those attention requests rather
than turning the operator into a dispatcher for every small decision.

### 4.2 Decision classes

MAP classifies decisions because different questions require different
authority:

| Class | Plain-English meaning | Typical authority |
|---|---|---|
| `ARCHITECTURE` | How should an approved thing be built? | Core agent may decide within scope. |
| `OWNERSHIP` | Who is accountable for what? | Core agent may decide within scope. |
| `SCOPE` | What is inside or outside this work? | Core agent inside approved scope; human if the boundary expands materially. |
| `AUTHORITY` | Who may act or approve? | Human/command-center required. |
| `POLICY` | What rule governs MAP or all projects? | Human/command-center required. |

If a decision fits several classes, MAP uses the class requiring the higher
authority. An agent may recommend an authority or policy change, but it may not
make that recommendation binding by writing it into the decision log as
approved.

### 4.3 Supersession instead of silent rewriting

Decisions are not quietly overwritten. A new decision supersedes an old one,
and both remain traceable. This preserves the reasoning history: future agents
can learn not only what the current rule is, but what it replaced.

That is a general MAP pattern: **change the present without erasing the past**.

---

## 5. HPOM: choosing the right worker

HPOM means **Human-Paced Orchestration Model**. It sits above the task system
and answers who—or what—should perform a given piece of work.

MAP answers, “What is the work and what state is it in?” HPOM answers, “Who is
the cheapest competent worker with the correct authority?”

### 5.1 Authority tiers

| Tier | Worker | Appropriate role |
|---|---|---|
| 0 | Human / command-center | final intent, approvals, broad tradeoffs, policy and authority |
| 1 | Core agents: Codex and Claude | task ownership, integration, implementation, architecture, independent review |
| 2 | Visible temporary helpers | bounded research, inspection, alternate draft, independent support |
| 3 | Local assistants / Ollama | draft-only summaries, classification, checks, narrow suggestions |
| 4 | Aider with a local model | supervised edits to explicitly named files |

The tiers do not rank intelligence. They rank **authority and accountability**.
A local model may be excellent at a bounded code transformation and still have
no right to approve or release the result.

### 5.2 Worker fit

MAP's current defaults are:

- Codex for repository implementation, scripts, validators, tests, and
  concrete state logic;
- Claude for independent review, architecture critique, task shaping, risk
  analysis, and prose-heavy synthesis;
- local models for bounded drafts, digests, classification, and checks;
- Aider for supervised named-file edits after baseline checks;
- helpers when parallelism provides enough benefit to justify the cost of
  coordination.

The phrase “cheapest competent worker” includes more than money. Cost also
means token use, operator interruption, latency, coordination overhead, and
risk of rework.

### 5.3 Visibility is part of safety

Model-backed work must run in an operator-reachable surface. Visible WezTerm
tabs are the default. A hidden helper is dangerous not merely because it is
invisible, but because the operator cannot inspect, interrupt, approve, or stop
it.

This is why MAP distinguishes deterministic background automation from
model-backed judgment. A deterministic watcher may run as a service if its
state and stop control are visible. If it invokes a model to make judgments,
that invocation becomes agent work and must be visible.

---

## 6. Intake: turning conversation into actionable work

Human requests often arrive as natural language, not as task records. The
intake layer exists to prevent broad conversation from becoming ambiguous
authority.

The conceptual intake sequence is:

```text
human request
  → classify the request
  → identify risk and authority
  → choose worker shape
  → propose outputs and acceptance criteria
  → create a task, bounded message, helper note, or operator question
```

`intake_request.py` and `command_center_intake.py` produce dispatch-shaped
information. A dispatch packet is not automatically a task. It may result in:

- a task record;
- a narrow hcom assignment;
- a visible helper assignment;
- a question to the human;
- no action when the input was informational only.

The intake principle is:

> Human intent should enter once, be shaped once, and then fan out through
> explicit ownership rather than through several agents independently
> interpreting the same sentence.

This layer remains partly behavioral: the scripts exist, but disciplined use
by agents is still important. MAP does not yet guarantee that every broad chat
instruction mechanically passes through intake.

---

## 7. Tasks as contracts, not to-do notes

A MAP task is a small executable contract. It should tell a future worker with
no chat context:

- what outcome is wanted;
- why it matters;
- who owns it;
- what files it may change;
- what it depends on;
- what evidence proves completion;
- whether a specific worker is required;
- what state the work is in.

### 7.1 The task state machine

The practical lifecycle is:

```text
BACKLOG / NEEDS_SHAPING
          │ metadata and intent become concrete
          ▼
        READY
          │ atomic claim
          ▼
     IN_PROGRESS
          │ implementation + evidence
          ▼
      SUBMITTED
          │ independent review
     ┌────┴─────────────┐
     ▼                  ▼
CHANGES_REQUESTED    APPROVED
     │                  │ release checklist
     └─ rework loop      ▼
                      RELEASED
```

`BLOCKED` and `CONFLICT` are exceptional states. BLOCKED means progress needs
external input or a changed condition. CONFLICT freezes work when ownership,
scope, or interpretation is contested.

### 7.2 READY is supposed to mean executable

A task should not become READY merely because someone wrote a title. It needs
concrete output paths and acceptance criteria. `promote_task.py` and the claim
gate defend this boundary.

This matters because an underspecified task forces the execution agent to
invent intent. MAP's design treats that as unsafe. If intent is missing, the
right action is shaping, not implementation.

### 7.3 Output paths are ownership boundaries

`output_paths` are not only a file list. They are a concurrency-control
mechanism.

If TASK-A owns `scripts/foo.py`, TASK-B should not independently edit that file
while TASK-A is active. `validate_task_graph.py` reports collisions so agents
cannot quietly create two conflicting versions of the same output.

This rule applies to every touched file, including small test changes or
cross-links. It creates discipline, but rapid iterative UI work has shown its
cost: many tiny tasks touching the same shared files can create a serial review
backlog. The solution is usually to batch closely related low-risk iterations
under one active task or release them in a deliberate sequence—not to disable
the collision detector.

### 7.4 Acceptance criteria turn intent into evidence

Good criteria are observable. “Improve the UI” is not a useful criterion.
“The popup preserves line breaks, the live and template files match, and the
focused test passes” is reviewable.

Acceptance criteria do not guarantee quality. They make the claimed definition
of success inspectable and contestable.

### 7.5 Claims, leases, and heartbeats

Claims prevent duplicate ownership. A successful claim moves READY to
IN_PROGRESS and records the claimant. A lease gives that claim an expiration
time. Heartbeats extend it while work continues.

If an agent disappears, reconciliation can expire the lease and return the
task to a claimable state. This is a classic distributed-systems lease: it
avoids permanent locks while reducing simultaneous ownership.

Leases do not prove useful work is occurring. They prove only that the owner
is still renewing its claim. Durable progress still belongs in artifacts,
events, or handoffs.

---

## 8. Orchestration: advice, routing, and optional execution

### 8.1 LangGraph is the router, not the brain

`graph/runner.py` loads task state, runtime policy, agent status, helper notes,
and halt state. It then computes the next route:

- `review` when submitted tasks need reviewers;
- `policy_gate` when work requires approval;
- `wait_for_agent` when a task explicitly requires an unavailable worker;
- `propose_helper` when a bounded helper is appropriate and capacity exists;
- `claim_or_assign` when normal ready work exists;
- `wait_or_reconcile` when the system is idle or state needs cleanup.

By default, the runner is read-only. It recommends a next action; it does not
silently rewrite the project or automatically launch helpers.

This is an important design choice. LangGraph supplies structured branching
and possible human pauses, but durable truth remains in SQLite and files.

### 8.2 Dependency routing

A task's dependencies are considered satisfied only when predecessor tasks are
in terminal success states such as DONE, APPROVED, or RELEASED. This prevents a
downstream task from starting merely because the upstream worker says it is
almost finished.

### 8.3 Pre-dispatch policy

Before assignment, `pre_dispatch_policy.py` asks whether the proposed worker
and task shape are allowed. It detects such concerns as:

- destructive actions;
- policy or authority decisions;
- trust-boundary crossings;
- unsafe worker tiers;
- broad rewrites or final review assigned to the wrong type of worker.

The result is `allow`, `require_approval`, or `reject`. This is a dispatch
guard, not a substitute for human judgment. Some detection uses explicit
metadata; some uses conservative text heuristics. Heuristics can produce false
positives, so they are tested and reviewed as policy code.

### 8.4 The autonomous agent loop

`agent_loop.py` can repeatedly:

1. reconcile expired leases;
2. run the router;
3. claim a selected task;
4. execute a trusted configured handler;
5. heartbeat during work;
6. submit and export state;
7. pause at human or review gates.

It uses a lock file to prevent two loops for the same agent/database pair.

The handler command is trusted operator configuration and is shell-executed.
This makes the loop flexible, but it also means untrusted input must never be
allowed to construct the handler string.

In ordinary lab use, core agents still perform much of the work interactively.
The autonomous loop is a capability, not evidence that MAP is a fully
unattended autonomous organization.

---

## 9. Communication, events, handoffs, and continuity

### 9.1 Use the lightest channel that preserves the needed meaning

MAP uses different channels for different temporal scales:

| Channel | Best use |
|---|---|
| hcom | immediate coordination and operator attention |
| `events/events.jsonl` | short durable facts about progress and transitions |
| `inbox/` | scoped questions or notes to a particular agent |
| `inbox/helpers/` | helper scope, findings, and capacity state |
| `handoffs/` | transfer or continuation of responsibility |
| `artifacts/reviews/` | formal independent verdicts |
| `shared/unresolved-questions.md` | project-level open questions |
| `shared/decisions.md` | binding durable decisions |

A live conversation is fast. A durable artifact is retrievable. MAP uses both
and requires promotion when a conversation becomes project truth.

### 9.2 Events as an audit trail

The JSONL event log is append-only. Each line records a small fact such as
PROGRESS, SUBMISSION, CHANGES_REQUESTED, APPROVED, RELEASED, BLOCKED, HANDOFF,
or DECISION_RECORDED.

An event is not the whole task. It is a breadcrumb that answers, “What happened
next, when, and where is the evidence?”

`validate_events.py` checks event shape while preserving an accepted baseline
of historical irregularities. This allows MAP to become stricter going forward
without rewriting old history.

### 9.3 Handoffs and STATE_SNAPSHOTs

A handoff transfers responsibility. It names changed files, current status,
remaining work, and known limitations.

A STATE_SNAPSHOT is broader session-resume context. It helps a future agent
recover its place after a limit or session end. It is orientation, not
canonical authority: current SQLite state, decisions, task records, and actual
files still win if the snapshot is stale.

### 9.4 Context routing and selective reading

MAP deliberately discourages loading the entire repository into every model
context. The reading order is:

1. operating rules;
2. current state and memory map;
3. assigned task;
4. task input/output paths;
5. only directly relevant artifacts and handoffs.

This is both a token-efficiency rule and an epistemic safety rule. Historical
documents can contradict current truth. More context is not always better;
the right context is better.

---

## 10. Review, approval, and release

### 10.1 Why implementation and acceptance are separate roles

The task owner cannot independently prove that its own interpretation is
correct. MAP therefore separates production from verification.

An independent reviewer checks:

- the task's acceptance criteria;
- the listed outputs;
- actual behavior or evidence;
- conflicts with current state and decisions;
- safety issues proportionate to risk.

Review findings use four severities:

- BLOCKER — unsafe, data-losing, or fundamentally unusable;
- REQUIRED — task intent or acceptance criteria are not met;
- RECOMMENDED — worthwhile but not required for approval;
- OPTIONAL — polish or future consideration.

Only BLOCKER and REQUIRED findings prevent approval.

### 10.2 Atomic review claims

Reviewers can atomically claim a submitted task so two agents do not both spend
time performing the same review. The no-self-review gate prevents the task
owner from claiming its own review.

### 10.3 Review is risk-tiered

MAP no longer treats every change as equally dangerous:

- high-risk security, persistence, policy, extraction, and network changes
  receive full independent evidence and release ceremony;
- medium-risk interaction or cross-module changes receive focused automated
  evidence and one independent review at completion;
- low-risk styling, documentation, or mechanical work can be batched and
  owner-verified, with review calibrated to actual consequence.

This correction matters. Excess ceremony can make a safety system less safe by
creating fatigue and enormous queues. The right goal is not maximum process;
it is sufficient evidence for the risk.

### 10.4 Approval and release are different

APPROVED means an independent reviewer accepted the task. RELEASED means the
approved change passed the release checklist and was recorded as delivered.

`validate_review.py` requires a structurally valid review record before an
approval transition. `release_task.py` requires a completed checklist and
release record before RELEASED.

For operator-facing packages, the release path may also require checking all
ways a user acquires the software—not merely the developer's source copy.

### 10.5 Security second pass

A network-facing or write-capable component requires a security-framed review
separate from ordinary functional review. It checks authentication, same-origin
controls, injection, path traversal, identity attribution, malformed input,
and failure modes.

This rule exists because “works correctly” and “is safe across a trust
boundary” are different questions.

---

## 11. Knowledge: research, context, and decisions

### 11.1 Research prevents assumptions from becoming architecture

MAP's Research System governs factual uncertainty. The full flow is:

```text
research question
  → brief
  → source map
  → source evaluation
  → claim/evidence matrix
  → assumption register
  → research summary
  → decision or task
```

Sources are rated PRIMARY, SECONDARY, COMMUNITY, UNVERIFIED, or STALE. Claims
are tied to specific locators. Contradictions are recorded rather than averaged
away. Date-sensitive claims must be rechecked.

Research does not directly change code or policy. It creates verified input
for a decision or task.

### 11.2 Context is curated, not accumulated

The Context System defines what a worker needs for a particular task type and
what it should not load by default. Archive material and old artifacts are
historical unless a current source points to them.

When current and historical sources disagree, MAP prefers, in order:

1. explicit current human instruction;
2. operating rules;
3. current state;
4. approved decisions;
5. current task/database state;
6. executable code and validator results;
7. recent handoffs;
8. historical artifacts.

This ordering is a conflict-resolution policy for knowledge.

### 11.3 Shared state is active institutional memory

Files in `shared/` contain the compact truth that every agent may need:
project brief, requirements, constraints, architecture, current state,
decisions, unresolved questions, risks, and improvements.

These files carry HPOM metadata such as status, last verification date,
confidence, and supersession. `validate_shared_state.py` checks that the
metadata exists. The metadata does not prove the prose is true; it makes
staleness and ownership visible.

---

## 12. Discovery and learning: the Emergence System

Execution answers, “How do we safely do known work?” Emergence answers, “What
new possibility or recurring problem is appearing because we are working?”

The lifecycle is:

```text
Insight → Synthesis → Idea → Experiment → Promotion → Task/Decision
```

The central rule is:

> Ideas may emerge freely. Only promoted ideas may redirect the project.

This protects creativity from bureaucracy while protecting the project from
scope drift.

### 12.1 Artifact types

- **Insight:** a concrete observation.
- **Synthesis:** a connection among observations that produces a larger
  interpretation.
- **Idea:** a possible change or capability.
- **Experiment:** the smallest safe test of that idea.
- **Promotion:** a proposal to turn the surviving idea into governed work.

`map_emergence.py` creates, indexes, validates, and reports stale emergence
records. Creation is not approval. A promotion record without an approving
authority remains a proposal.

### 12.2 Why the experiment boundary matters

Behavior-changing ideas should normally be tested before promotion. A failed
experiment is still useful evidence. MAP preserves negative results so the
system does not repeatedly rediscover the same bad idea.

### 12.3 The Emergence Sentinel and MAP Steward

The Emergence Sentinel is a deterministic signal scanner. It can identify
candidate patterns without automatically promoting them.

The MAP Steward is a read-oriented advisory layer that assembles attention
signals and may optionally ask a local model for a summary. It proposes; it
does not acquire task ownership or policy authority.

These tools attempt to make improvement opportunities visible without turning
every observation into a task.

---

## 13. Risk, security, permissions, and destructive actions

### 13.1 Risk is standing exposure, not merely a problem that already happened

The Risk System classifies risks such as PROCESS, KNOWLEDGE, SECURITY, DATA,
and AVAILABILITY. A risk record identifies severity, owner, mitigation,
acceptance, and review cadence.

The human accepts risks that exceed agent authority. Agents may identify and
mitigate bounded risks within task scope, but they cannot silently decide that
a major exposure is acceptable.

### 13.2 Permission tiers map authority onto actions

Core agents may read broadly and write within registered task outputs. Helpers
have bounded delegated write scope. Local models are draft-only. Aider is
restricted to named files.

Read access does not imply write access, and write access does not imply
decision authority.

### 13.3 Trust boundaries

A trust boundary is crossed when data or control moves between domains with
different assumptions—for example:

- local repository to an external network service;
- browser to a write-capable server;
- one agent's task outputs to another active owner's files;
- private material to a public remote;
- untrusted text into a shell command.

MAP requires stronger review and often human approval at these boundaries.

### 13.4 Destructive actions

An action is destructive when it is difficult to reverse or may discard state
that another participant values: deletion, force-push, hard reset, service
termination, dependency removal, safety-check bypasses, and similar actions.

Core agents require explicit current authorization or an approved decision.
The preferred response is a reversible alternative: move instead of delete,
supersede instead of overwrite, rework instead of reset.

---

## 14. Recovery and resilience

MAP assumes workers and processes will fail. Recovery is therefore a normal
system function, not an exceptional embarrassment.

### 14.1 Lease reconciliation

Expired claims can be reconciled back to READY. This prevents a dead session
from owning work forever.

### 14.2 Agent status and RnS

Agent availability is stored durably. The Rise & Shine limit watcher monitors
agents marked `out_of_tokens` with a `resume_after` time and attempts to resume
them in a visible terminal after the limit resets.

RnS is a recovery mechanism, not a scheduler of arbitrary future work. It
should not fabricate unavailable state merely to create a reminder.

MAP has also learned that stale agent records can create noise. Terminal or
superseded sessions must be suppressed so the watcher does not repeatedly
probe agents that should never return.

### 14.3 Liveness reaping

The liveness reaper evaluates stale agents and related claims. Its purpose is
to prevent “registered” from being mistaken for “alive.” Durable state and
actual process state are different facts and must be reconciled.

### 14.4 Halt state and circuit breakers

`halt_state.py` represents durable dispatch restrictions such as repair-only or
global halt modes. `resilience_controls.py` adds idempotency tracking and
circuit-breaker signals.

The concept is borrowed from fault-tolerant systems:

- repeated failures should first produce accounting and warnings;
- then pause the affected scope;
- then restrict work to repair;
- only severe systemic conditions justify a global halt.

The escalation should be proportional. A single failed helper should not stop
all project work.

### 14.5 Idempotency

An idempotent operation can be attempted again without applying the same side
effect twice. MAP records operation keys and content hashes so duplicate
delivery can be ignored and conflicting re-use can be detected.

This matters for resumed sessions: “try again” must not create two tasks,
apply the same migration twice, or record two logically identical state
changes.

### 14.6 Durable execution and dead letters

Durable execution checkpoints preserve resumable progress. A dead-letter queue
captures work that repeatedly fails or cannot be safely processed so it does
not disappear or poison the normal queue.

A dead letter is not success and not deletion. It is an explicit quarantine
state requiring diagnosis.

### 14.7 Session replay

`session_replay.py` builds a disposable read model from MAP-canonical events
and task state. It helps reconstruct what happened and detect drift without
changing the authoritative sources.

hcom messages are intentionally not copied into this index. hcom owns its own
message history; analyses that need both sources join them at query time.

### 14.8 Self-Repair

The Self-Repair System separates:

- mechanical repair, which an authorized core agent may perform and verify;
- blocking repair, which requires explicit analysis and often escalation;
- structural repair, which changes system design or authority and must be
  proposed before application.

Repeated repair classes should become validators, template changes, or
decisions. Fixing the same drift three times without preventing recurrence is
itself a system failure.

---

## 15. Observability: knowing what MAP is doing

### 15.1 Status and metrics

`map_status.py` reports live claims, submitted tasks, gates, and agent status.
`map_metrics.py` reports aggregate task counts, change-request rate, conflicts,
stale shared state, event counts, and outcome feedback.

`cost_yield.py` and cost-governance utilities ask a harder question: not only
how much work occurred, but how much became productive, shipped output rather
than parked or abandoned work.

Metrics are signals, not goals. Optimizing for fewer review changes could cause
agents to avoid difficult reviews. Optimizing for more released tasks could
encourage tiny task fragmentation. Human interpretation remains necessary.

### 15.2 Validators as executable institutional knowledge

Validators convert recurring lessons into mechanical checks. Current validator
families include:

- task graph shape, dependencies, metadata, and output collisions;
- SQLite/file mirror agreement;
- task schema;
- review artifact structure;
- shared-state metadata;
- decision record structure;
- event log shape and warning baselines;
- context packets;
- research, repair, and risk artifacts;
- cross-links and wikilinks;
- protocol conformance;
- canonical repository paths.

A validator cannot decide whether a product idea is good. It can prevent a
known structural failure from recurring silently.

### 15.3 Librarian

The Librarian checks MAP's knowledge graph: links, related-file references,
and ambiguous document names. It improves navigability and detects broken
references, but it does not decide which document should be canonical.

### 15.4 Operational lessons

Promoted operational lessons can be validated and projected into startup
context. This is a mechanism for turning repeated experience into future
behavior without forcing every agent to rediscover the lesson from old event
logs.

---

## 16. The Command Center UI

The Command Center is the operator's attention and control surface. It is a
view across MAP and hcom, not a replacement source of truth.

Its current functions include:

- live hcom conversation and presence;
- agent type, model, status, and token/rate-limit information;
- operator message sending with inform/request/acknowledgment semantics;
- unanswered-request, approval-gate, and terminal-prompt attention queues;
- reply popups with snooze, dismiss, open, and reply behavior;
- terminal inspection and controlled input;
- task queue counts;
- MAP health checks for runner route, Librarian, replay, RnS, tokens,
  cost/yield, and outcome feedback;
- MAP Steward and Emergence Sentinel summaries;
- Project Updater integration;
- lab state, timers, and selected agent launch/control surfaces.

The Human Interface System defines the design principle:

> Show the human decisions, risks, and next actions—not raw system noise.

This distinction matters. A dashboard can be technically accurate yet still
fail if it does not explain what the numbers mean or makes routine status look
like an emergency.

If the UI disagrees with SQLite or canonical files, the UI is wrong. The
disagreement becomes a drift finding; it does not make the UI authoritative.

---

## 17. Project bootstrapping and reuse

MAP is designed to be reusable across projects. A new project should establish
before its first task:

- a project brief and success condition;
- requirements and constraints;
- decision and unresolved-question locations;
- current state and memory map;
- task, artifact, handoff, and event locations;
- risk and research conventions appropriate to the project;
- emergence folders for insights, ideas, experiments, and synthesis;
- agent instructions and review boundaries.

Projects such as Pathwell can have project-local MAP state while the top-level
`MAP_System/` remains the reusable framework. This is analogous to a platform
and an application: the framework supplies coordination machinery; the project
supplies domain truth.

Bootstrapping should not copy stale facts from the reusable system. It copies
structure and rewrites current truth for the new domain.

---

## 18. Archive, compaction, and long-term memory

MAP preserves history but tries not to force every future agent to read it.

### 18.1 Retirement versus archiving

- **Retirement** says an artifact is no longer valid or active. It stays in
  place with a status such as superseded or retired.
- **Archiving** says the content is no longer part of active working memory. It
  is moved or summarized into `archive/` while remaining retrievable.

These are different questions: “Is it still valid?” versus “Should ordinary
work load it by default?”

### 18.2 Brain compaction

Compaction summarizes detailed completed history into structural memory:
durable outcomes, decisions, still-open risks, and links to raw records.

Raw history is not deleted. Active files become smaller so agents stop paying
the token and confusion cost of rereading old narrative.

This is analogous to memory consolidation: detailed experience becomes a
smaller set of durable concepts while the original evidence remains available.

---

## 19. Retrospectives and practice scenarios

### 19.1 Retrospectives

Self-Repair asks whether one failure recurred. A retrospective asks what
patterns appeared across an entire work cycle.

A retrospective examines:

- what worked;
- what failed;
- what caused rework;
- what agents misunderstood;
- what rules were unclear;
- what should become a validator, template change, or decision.

The output should change future behavior, not merely describe the past.

### 19.2 Practice scenarios

Practice scenarios test one bounded lifecycle claim with preserved evidence.
For example: “Can an interrupted agent resume the correct task without reading
chat history?”

A scenario has a frozen baseline, explicit roles, allowed paths, stop rules,
raw evidence, independent review, and a verdict such as PASS, PARTIAL, FAIL,
or STOPPED.

Scenarios do not grant authority to perform the lifecycle action they mention.
A scenario about release cannot release a real task unless ordinary release
authority already exists.

Their value is scientific: they convert “MAP seems helpful” into falsifiable
claims about correctness, retrieval cost, operator burden, and recovery.

---

## 20. A complete end-to-end example

Suppose the human says:

> “Make unanswered agent questions easier to notice without filling the
> sidebar.”

### Step 1: intake and shaping

The request is classified as a low-to-medium-risk UI interaction change. It
does not change authority. A task is created with exact live/template files and
acceptance criteria: popup behavior remains, alert history becomes collapsible,
and the list remains accessible.

### Step 2: claim

Codex atomically claims the READY task. SQLite records IN_PROGRESS, claimant,
lease, and heartbeat. File mirrors are exported.

### Step 3: implementation

Codex reads the existing sidebar-section behavior, changes the markup and
client logic, updates live and installer copies, and adds focused regression
tests. Routine progress is an hcom `inform`, not an operator request.

### Step 4: evidence

JavaScript syntax checks, focused tests, and live/template parity are run. A
submission event points to the evidence.

### Step 5: independent review

Claude claims the review, checks the acceptance criteria, reproduces the test,
and verifies the source paths. If the list disappears when empty contrary to
intent, Claude records a REQUIRED finding and returns CHANGES_REQUESTED.

### Step 6: rework

Codex uses the rework transition, reclaims the task, fixes the behavior, and
resubmits. The history shows both attempts rather than pretending the first was
correct.

### Step 7: approval and release

Claude approves with a valid review record. The owner prepares the release
checklist. Release records the delivered state.

### Step 8: learning

If several tiny UI tasks repeatedly collide on the same `chat.js` and
`chat.css`, that pattern becomes an insight or retrospective finding: rapid
operator-guided polish should be batched under one iterative task before one
review. A future task might improve the workflow—not because one agent felt
annoyed, but because durable evidence showed repeated collision and queue cost.

This example illustrates MAP's full purpose: it coordinates work *and* teaches
the organization from the friction of doing the work.

---

## 21. Functional catalog of the current implementation

This section explains what the executable tool families do. Not every tool is
a continuously running service; many are operator or agent-invoked utilities.

### 21.1 Intake, allocation, and task lifecycle

| Tool | Function |
|---|---|
| `intake_request.py` | Classifies an operator request and drafts a worker-fit dispatch packet. |
| `command_center_intake.py` | Wraps broad intake with visible hcom inform and runner output. |
| `map_task.py` | Creates tasks, shows/logs them, registers paths, records review results, reworks, and synchronizes mirrors. |
| `promote_task.py` | Refuses READY promotion until required HPOM/task metadata is complete. |
| `db/claims.py` | Atomically claims tasks and reviews, renews leases, submits work, and expires stale claims. |
| `pre_dispatch_policy.py` | Checks whether worker tier, task risk, and required authority permit dispatch. |
| `release_task.py` | Moves approved work to RELEASED only with a complete checklist and release record. |

### 21.2 Orchestration and continuity

| Tool | Function |
|---|---|
| `graph/runner.py` | Computes the next route from tasks, dependencies, policy, agent availability, helper capacity, and halt state. |
| `agent_loop.py` | Optionally automates reconcile → route → claim → handler → heartbeat → submit cycles. |
| `reconcile.py` | Expires stale task leases and logs reconciliation. |
| `declare_standby.py` | Records agent work-state transitions through the durable status path. |
| `reconcile_agents.py` | Compares durable agent status with live hcom process state. |
| `limit_watcher.py` | Resumes usage-limited agents after reset and reports failed recovery. |
| `liveness_reaper.py` | Detects stale/dead agent sessions and reconciles their operational consequences. |

### 21.3 Resilience and safety controls

| Tool | Function |
|---|---|
| `halt_state.py` | Stores and evaluates durable dispatch halt or repair-only state. |
| `resilience_controls.py` | Provides idempotency records and escalating circuit-breaker signals. |
| `durable_execution.py` | Stores resumable execution checkpoints. |
| `dead_letter_queue.py` | Quarantines repeatedly failing or unsafe-to-process work. |
| `flag_conflict.py` | Records a conflict and freezes the affected task. |
| `git_operation_lock.py` | Coordinates repository-global Git operations. |
| `redaction.py` | Guards capture pipelines against leaking sensitive content. |

### 21.4 Knowledge, learning, and advisory tools

| Tool | Function |
|---|---|
| `map_emergence.py` | Creates, indexes, compacts, validates, and reports emergence records. |
| `emergence_sentinel.py` | Deterministically identifies candidate improvement signals without promotion. |
| `map_steward.py` | Builds a read-only attention/advice packet, optionally summarized locally. |
| `map_repair.py` | Creates uniquely numbered repair records. |
| `operational_lessons.py` | Validates and projects learned operational rules into startup context. |
| `librarian.py` | Resolves and validates wikilinks and related-file knowledge structure. |

### 21.5 Local and supervised helper tools

| Tool | Function |
|---|---|
| `local_assistant_health.py` | Checks whether local assistant capabilities are actually usable. |
| `local_runner.py` | Runs a scoped Ollama helper and records its bounded output. |
| `aider_wrapper.py` | Prepares supervised Aider editing with file and Git safety checks. |

### 21.6 Observability and measurement

| Tool | Function |
|---|---|
| `map_status.py` | Shows live claims, review queue, gates, and durable agent state. |
| `map_metrics.py` | Reports aggregate workflow health and outcome indicators. |
| `agent_token_status.py` | Reads agent token/rate-limit information. |
| `cost_governance.py` | Applies spend and budget governance helpers. |
| `cost_yield.py` | Compares work/cost proxies with shipped, parked, and abandoned outcomes. |
| `session_replay.py` | Builds and queries a disposable replay index from MAP-canonical sources. |
| `mission_control_tui.py` | Provides a read-only terminal mission-control view. |
| `advisory_monitor.py` | Proposal-only coordination-health scanning; it must not silently mutate MAP state. |

### 21.7 Validation tools

| Tool family | What it protects |
|---|---|
| `validate_task_graph.py`, `validate_task_schema.py` | Task structure, dependencies, metadata, and file ownership collisions. |
| `validate_task_mirrors.py` | SQLite/file consistency. |
| `validate_review.py` | Review identity, verdict, and required evidence shape. |
| `validate_events.py` | Event syntax and new drift beyond the historical warning baseline. |
| `validate_shared_state.py`, `validate_decisions.py` | Metadata, authority records, and supersession structure. |
| `validate_context_packets.py` | Minimum bounded context for execution. |
| `validate_research_artifacts.py`, `validate_repair_artifacts.py`, `validate_risk_registers.py` | Domain-specific governance artifact quality. |
| `validate_protocol.py`, `validate_layer1.py` | Deterministic protocol and validator cascades. |
| `check_system_crosslinks.py`, `librarian.py` | Knowledge-graph links and discoverability. |
| `validate_canonical_repo_paths.py` | Prevents active docs from reintroducing obsolete repository paths. |

---

## 22. What MAP does not currently guarantee

Understanding limits is as important as understanding features.

### 22.1 It is not fully autonomous

MAP can route and loop, but much work is still interactive. It deliberately
pauses at review, policy, and human gates. It does not safely turn any broad
human sentence into unattended execution.

### 22.2 A green validator does not prove good judgment

Validators prove structural properties they know how to check. They do not
prove that a requirement was wise, a design is elegant, or the human actually
wants the result.

### 22.3 The agent registry can overstate real capacity

Durable status may contain historical agents that are not live. Reconciliation
and liveness tools reduce this discrepancy, but “available” in a database is
not identical to “usable session now.”

### 22.4 The file/database duality remains operationally expensive

Mirror validation catches drift, but repairing metadata can still be awkward.
Some lifecycle edits have dedicated commands; others may require a carefully
recorded canonical database correction and export.

### 22.5 Rapid shared-file iteration can overload the task model

If every small UI adjustment becomes a separate submitted task touching the
same files, output collision checks correctly report conflicts and the review
queue grows. MAP needs disciplined batching and risk-tiered review, not one
task per conversational micro-adjustment.

### 22.6 Not every documented subsystem is equally mature

Some components are long-established gates; others are advisory utilities,
prototypes, or draft-active contracts. Current state, executable code, and
tests must be checked before assuming a design document describes deployed
behavior.

### 22.7 Outcome measurement is immature

MAP measures events, task states, review changes, and cost/yield proxies, but
its explicit outcome-feedback event count is currently sparse. It knows a
great deal about process and less about whether released work produced the
human's desired real-world result.

This is a major improvement frontier: distinguish “the workflow completed”
from “the project became better.”

---

## 23. How to reason about proposed MAP improvements

When considering an improvement, ask these questions in order.

### 23.1 What failure is being prevented?

Name an observed failure: duplicate ownership, stale context, missed operator
decision, unsafe action, bad review, recovery loss, or unnecessary attention.
Do not add a subsystem only because it sounds mature.

### 23.2 Which layer owns the problem?

- factual uncertainty → Research;
- new possibility → Emergence;
- task execution → HPOM/task lifecycle;
- binding choice → Decision/Authority;
- recurrent state drift → Self-Repair or validator;
- operator comprehension → Human Interface;
- worker death or duplicate delivery → Resilience;
- old context overload → Compaction/Archive.

Putting a problem in the wrong layer creates duplication.

### 23.3 Can the improvement be tested mechanically?

If yes, write a validator or focused test. If not, define the human or
independent review judgment required. Do not pretend a subjective question is
mechanical.

### 23.4 Does it preserve authority?

Automation may recommend, detect, or prepare. It should not quietly convert an
advisory result into a policy, approval, or expanded scope.

### 23.5 What is the operator-attention cost?

A safe system that asks the human about every implementation detail has failed
as an interface. Requests should be reserved for real decisions, approvals,
blockers, conflicts, and scope/privacy risks.

### 23.6 What new failure mode does the improvement introduce?

Examples:

- mirrors improve readability but create drift risk;
- leases prevent permanent locks but can reassign genuinely active slow work;
- helpers reduce latency but add coordination and visibility costs;
- more validators prevent recurrence but increase repair burden and false
  positives;
- richer dashboards improve awareness but can overwhelm the operator with
  noise or stale projections.

Every MAP mechanism is a tradeoff, not a free guarantee.

### 23.7 Does evidence justify permanence?

Prefer a bounded scenario or experiment before changing MAP-wide policy.
Promote successful lessons deliberately. Preserve negative results.

---

## 24. Where the human owner has the most leverage

The human does not need to understand every Python function to improve MAP.
The highest-leverage questions are:

1. **Purpose:** Is MAP helping complete real projects, or mostly improving
   itself?
2. **Attention:** Does the Command Center show the decisions and risks that
   matter, or merely expose internal machinery?
3. **Friction:** Which steps repeatedly require manual cleanup or explanation?
4. **Trust:** Which actions should agents perform autonomously, and which must
   always return to the human?
5. **Evidence:** What would prove MAP improved speed, quality, recovery, or
   outcome—not just task counts?
6. **Simplicity:** Which subsystem can be removed or combined without losing a
   real safety property?
7. **Workflow:** What real project should MAP prove itself on next?

These questions keep MAP subordinate to the human's goals. The system is not
the product unless the human chooses it to be.

---

## 25. Canonical references

Use this guide for understanding. Use the following sources for current
operating authority:

- `MAP_System/AGENTS.md` — binding operating rules;
- `MAP_System/shared/current-state.md` — live capabilities and known issues;
- `MAP_System/shared/architecture.md` — concise architecture;
- `MAP_System/shared/hpom.md` — worker routing and authority tiers;
- `MAP_System/shared/decisions.md` — approved decisions;
- `MAP_System/shared/memory-map.md` — context authority and reading order;
- `MAP_System/graph/runner.py` and `graph/README.md` — routing behavior;
- `MAP_System/db/claims.py` and `migration/schema.sql` — atomic task state;
- `MAP_System/notes/task-authoring-guide.md` — task contracts and ownership;
- `MAP_System/notes/review-guide.md` — review and risk calibration;
- `MAP_System/HUMAN_INTERFACE_SYSTEM.md` — operator-facing information model;
- `MAP_System/DECISION_AUTHORITY_SYSTEM.md` — decision rights;
- `MAP_System/SECURITY_PERMISSIONS_SYSTEM.md` — trust and permissions;
- `MAP_System/SELF_REPAIR_SYSTEM.md` — repair boundaries;
- `MAP_System/RESEARCH_SYSTEM.md` — factual knowledge discipline;
- `MAP_System/emergence/README.md` — discovery and promotion;
- `MAP_System/notes/practice-scenario-runbook.md` — controlled learning runs;
- `MAP_System/notes/brain-compaction-guide.md` — long-term memory hygiene.

When this guide conflicts with one of those current sources or with executable
behavior, the current source or executable evidence wins and this guide should
be updated.

---

## Closing interpretation

MAP's deepest function is not “letting several AIs work at once.” Its deepest
function is **maintaining coherent human-directed action across workers that do
not share persistent memory, authority, or availability**.

It does this by making normally invisible organizational concepts explicit:
ownership, evidence, authority, state, risk, memory, review, and recovery.

The design succeeds when:

- agents can act without constant supervision inside clear boundaries;
- the human sees only meaningful attention requests;
- another worker can reconstruct why the project is in its current state;
- failures become evidence and then prevention;
- useful ideas remain possible without silently becoming commitments;
- completed process correlates with real project outcomes.

The design fails when its machinery becomes harder to understand than the work
it coordinates, when process metrics substitute for human outcomes, or when
the operator must manage the system at a finer level than the project itself.

That tension—between reliability and comprehensibility—is the central design
problem for MAP's next phase.
