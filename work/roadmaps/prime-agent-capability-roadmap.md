# Prime Agent capability adoption roadmap

Status: `PLANNING ONLY — NOT ACTIVE AUTHORITY`

Purpose: define, in implementation-ready detail, how MAPS Lean should absorb the most useful capabilities from the Prime Agent / agent-harness concept **without rebuilding Prime as a second orchestrator**.

This is intentionally a long roadmap. It is a design and sequencing document, not an instruction to implement every item immediately. Each phase has explicit entry conditions, boundaries, acceptance criteria, tests, failure behavior, and promotion gates so later agents do not need to rediscover the design.

---

# 1. Executive summary

The useful part of the Prime Agent idea is not a special “Prime” agent. It is the **harness around an agent**:

- give the worker the right task and context;
- give it explicit authority and scope;
- start or attach to it through a provider-neutral interface;
- know which live session corresponds to which task/run;
- preserve continuity through interruption and replacement;
- delegate without losing ownership boundaries;
- isolate concurrent writable work;
- make routine lifecycle operations deterministic;
- know exactly what revision/evidence was reviewed;
- retain real-world outcome feedback;
- learn from repeated failures without turning memory into policy by accident;
- evaluate proposed harness changes against historical evidence before promotion.

MAPS Lean already implements a large fraction of this foundation. The roadmap therefore does **not** propose a new `mapd`, a new workflow engine, a second task database, a fixed agent roster, or an autonomous self-modifying supervisor.

The target is:

> **Prime-style lifecycle guarantees implemented as narrow mechanisms around MAPS's existing canonical authorities.**

The main critical path is:

```text
CURRENT LEAN FOUNDATION
        ↓
0. Review + stabilize the current foundation
        ↓
1. Provider-neutral Harness API
        ↓
2. Explicit execution/session/helper lineage
        ↓
3. Review/evidence revision binding
        ↓
4. Deterministic repeated lifecycle flows
        ↓
5. Capability/skill composition where routing benefits
        ↓
6. Controlled operational learning
        ↓
7. Outcome-driven harness evaluation/refinement
```

Two important capabilities run alongside that path when their trigger conditions are met:

```text
PARALLEL-WRITE TRACK              HELPER-CONTINUITY TRACK
        │                                  │
Git worktree isolation            task-scoped persistent helper sessions
        │                                  │
run/worktree binding              TTL + context compatibility
        │                                  │
clean integration                 advisory NO PROGRESS detection
```

The Prime concept is considered successfully absorbed when MAPS can reliably answer all of the following without guessing:

1. **What is the task and who owns it?**
2. **What exact authority and context did this worker receive?**
3. **Which run/session/helper actually performed the work?**
4. **Is that session healthy, stopped, replaced, or waiting on something?**
5. **Can an interrupted run be recovered without creating duplicate work?**
6. **Can multiple writable agents work without corrupting one another's state?**
7. **What exact revision/artifact did the reviewer approve?**
8. **Did the work succeed in the real world after MAPS marked it complete?**
9. **What recurring lesson, if any, should be proposed for future runs?**
10. **Did a proposed harness change improve outcomes on frozen evidence before it was promoted?**

---

# 2. Non-negotiable architecture rules

These rules apply to every phase.

## 2.1 One authority per fact

Existing MAPS authorities remain authoritative:

| Concern | Authority |
|---|---|
| Task intent, lifecycle, ownership, leases, review, policy, durable evidence | SQLite task DB |
| Frozen execution contract/context | immutable run manifests + context hashes |
| Routing recommendation/checkpoint memory | LangGraph layer |
| Communication/session transport | hcom |
| Recovery retry state | RnS recovery state |
| Helper invocation evidence | helper subsystem |
| Dispatch halt | existing halt mechanism |
| Outcome observations | append-only outcome evidence |
| Human-readable planning/review staging | Markdown, explicitly non-authoritative |

A Prime-derived feature may **read, join, normalize, or call these mechanisms**. It must not create another mutable copy that competes with them.

## 2.2 Capability is not authority

The harness may know that a worker can:

- write files;
- run shell commands;
- stop a process;
- call a provider API;
- deploy something.

That does not mean the worker is authorized to do those things for a particular task.

The separation remains:

```text
capability
≠ assignment
≠ ownership
≠ task scope
≠ policy authority
≠ operator approval
```

## 2.3 Session liveness is not task truth

A live process does not mean:

- it owns the task;
- its lease is valid;
- its context is current;
- it may continue after reshaping;
- it may review its own work;
- it may perform destructive/external actions.

Every lifecycle operation must re-check the canonical task/run relationship when the operation could affect work.

## 2.4 Derived views remain derived

`trace`, `status`, context plans, wait projections, lineage diagrams, dashboards, and future operator surfaces are **read models**.

They may not become the place where task state is edited.

## 2.5 No hidden continuity authority

Conversation memory, helper memory, a long-lived process, or a provider-side thread may preserve useful context. None of those may silently widen task authority or override a changed task revision.

## 2.6 No self-authorizing refinement

The harness may:

- measure itself;
- generate candidate changes;
- compare candidate configurations against frozen evaluations;
- recommend a change.

It may not promote its own policy, routing, instruction, authority, or safety changes without the normal decision/review path.

---

# 3. Current MAPS Lean baseline

The current draft work already covers a substantial portion of the Prime value proposition.

## 3.1 Already implemented or represented

| Prime-style capability | Current Lean mechanism | Roadmap decision |
|---|---|---|
| Durable goals/work | task `outcome`, acceptance criteria, dependencies, project ID, canonical lifecycle | Keep; do not add second goal store |
| Ownership | atomic claims + leases + heartbeat | Keep |
| Explicit authority | task scope + policy + operator approval | Keep |
| Provider-neutral routing | capability envelopes + provider-neutral route decisions | Extend through Harness API |
| Frozen execution context | immutable run manifest + task revision + context hashes | Keep and connect to lineage |
| Recovery | RnS bounded retry/backoff against explicit active bindings | Wrap, do not replace |
| Delegation | bounded helper lanes inheriting task scope, not ownership | Extend with continuity evidence |
| Review independence | durable author identity + continuity-aware exclusion | Keep |
| Criterion evidence | append-only criterion claims/verdicts | Keep |
| Context orientation | Context Builder v1 over explicit references and file hashes | Keep explicit-first |
| History | task events/reviews/runs/criterion evidence | Extend trace across external stores |
| Real-world feedback | append-only outcome observations | Use as future eval foundation |
| Operator attention | read-only status v1 | Extend with explainable waits/lineage |
| Secret-safe diagnostics | redaction boundary for diagnostic/event surfaces | Apply to new diagnostic surfaces |
| Behavioral constraints | negative operating contract | Keep |
| Risk-specific review | explicit review lenses | Keep |
| PR validation | full runtime CI on pull requests | Use for each roadmap tranche |

## 3.2 Important current limitation

Most of the new foundation exists on **draft PR #19** until independently reviewed and merged. Future implementation should not treat draft-branch behavior as settled `main` authority.

Therefore Phase 0 is real work, not paperwork.

## 3.3 Persistent runtime goals: explicit decision

Prime's persistent-goal idea is useful, but MAPS already has durable task outcomes and project grouping.

**Default decision:** do not add a separate runtime-goal database.

If later evidence shows that multi-task missions cannot be represented clearly through `project_id`, task dependencies, project decision records, and task outcomes, introduce only a thin **Mission** object with these constraints:

- mission states intent/grouping, not executable authority;
- tasks remain the unit of ownership and execution;
- mission cannot bypass task readiness/policy/review;
- mission references tasks rather than copying their state;
- no mission agent or permanent mission supervisor is created automatically.

That is an evidence-gated extension, not part of the critical path.

---

# 4. Target end-state architecture

```text
                               OPERATOR
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │     MAPS TASK TRUTH     │
                    │        SQLite           │
                    │ task / claim / policy   │
                    │ review / evidence       │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┼────────────────┐
                 │               │                │
                 ▼               ▼                ▼
          Context Builder    Policy/Authority   Routing
          explicit-first      evaluator        LangGraph
                 │               │                │
                 └───────────────┼────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ PROVIDER-NEUTRAL        │
                    │ HARNESS INTERFACE       │
                    │ start/attach/send/      │
                    │ inspect/resume/stop/    │
                    │ collect                 │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
          hcom/provider       Codex/etc.       local/helper
            adapter            adapter           adapter
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ RUN / SESSION LINEAGE   │
                    │ task → run → session    │
                    │ → helper/replacement    │
                    └────────────┬────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
       Recovery              Worktree                Waits
         RnS                 isolation              projection
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 ▼
                            Submission
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ REVISION-BOUND REVIEW   │
                    │ exact subject/evidence  │
                    └────────────┬────────────┘
                                 ▼
                               DONE
                                 │
                                 ▼
                    Post-completion outcome
                                 │
                                 ▼
                    Incident/evaluation corpus
                                 │
                                 ▼
                    Candidate harness changes
                                 │
                                 ▼
                     Frozen comparative eval
                                 │
                                 ▼
                       REVIEW / APPROVAL
```

The Harness Interface is deliberately in the middle rather than above SQLite. It is an **execution abstraction**, not the supreme controller.

---

# 5. Core entity model and terminology

A major source of multi-agent failures is using “agent,” “worker,” “session,” and “task” interchangeably. The roadmap should standardize these terms.

## Task

Canonical unit of work and authority.

Contains intent, outcome, scope, policy, ownership, acceptance, review requirements, dependencies, and lifecycle.

## Worker

An identity/capability record representing something that may execute work.

Examples:

- a Codex-backed worker;
- a Claude-backed worker;
- a local model helper;
- a human/operator-facing worker identity.

Worker identity does not imply a live process.

## Provider / adapter

The mechanism used to interact with the worker runtime.

Provider name is transport/runtime information, not authority.

## Run

Immutable binding between:

- task revision;
- worker;
- execution scope;
- context hashes;
- optional base Git revision;
- runtime limits;
- optional session binding.

A material task/context change should normally produce a new run rather than mutating the old run.

## Session

A live or historical provider-side execution process/thread.

A session can stop while its task remains active. A replacement session may continue a task only through explicit continuity/recovery rules.

## Helper session

A delegated child execution context created for a bounded task-scoped purpose.

It inherits only explicitly allowed scope/capability. It does not inherit task ownership or review authority.

## Continuity link

Evidence that two identities/sessions share inherited execution context or obligations.

Continuity affects review independence and recovery reasoning. It grants no authority by itself.

## Outcome

Post-completion observation about real-world success/failure. It does not rewrite the historical task result.

## Harness

The provider-neutral execution-lifecycle interface and its adapters. The harness is not a task authority store and not an autonomous agent.

---

# 6. Phase 0 — Review and stabilize the current foundation

Priority: **P0 prerequisite**

## 6.1 Why this exists

The current branch adds several foundational features that later phases depend on:

- trace;
- outcome evidence;
- Context Builder v1;
- status surface;
- negative operating contract;
- risk-specific review guidance;
- PR CI.

Building more layers on top of unreviewed foundation would make later review harder and could entrench mistakes.

## 6.2 Work

1. Independently review the packets in `work/review_queue/`.
2. Resolve correctness/security/authority issues.
3. Confirm current integrated CI remains green.
4. Merge or explicitly reject each tranche.
5. Update this roadmap if the accepted baseline differs from the draft assumptions.

## 6.3 Exit gate

Phase 1 starts against `main` only after the foundational mechanisms it relies on are approved/merged or their replacements are explicitly known.

## 6.4 Non-goal

Do not use Phase 0 to reopen every historical MAPS design debate.

---

# 7. Phase 1 — Provider-neutral Harness API

Priority: **P1 / first new Prime-derived build**

## 7.1 Problem

MAPS already has provider-neutral concepts at the routing level, but lifecycle operations can still become tied to specific transport/provider implementations.

Without a stable runtime contract, future features tend to grow provider-specific branches:

```text
if hcom: ...
if codex: ...
if local helper: ...
if remote provider: ...
```

That makes recovery, lineage, testing, and future provider addition harder.

## 7.2 Target behavior

MAPS orchestration code should use one normalized execution interface for common lifecycle operations while adapters handle provider details.

Candidate operations:

```python
start(binding) -> SessionResult
attach(session_ref, binding) -> SessionResult
send(session_ref, message) -> OperationResult
inspect(session_ref) -> SessionStatus
heartbeat(session_ref) -> OperationResult
resume(session_ref, binding) -> SessionResult
stop(session_ref, reason, authorization_context) -> OperationResult
collect(session_ref) -> CollectedEvidence
```

Names are provisional; the contract matters more than method spelling.

## 7.3 Candidate types

```text
ExecutionBinding
- task_id
- task_revision
- run_id
- worker_id
- project_id
- readable_scope
- writable_scope
- forbidden_scope
- runtime_limits

SessionRef
- provider
- session_id
- worker_id
- task_id
- run_id

NormalizedSessionState
- STARTING
- RUNNING
- IDLE
- STOPPED
- FAILED
- UNKNOWN

SessionStatus
- ref
- state
- observed_at
- last_activity_at?
- provider_status_raw?
- recoverable: bool | UNKNOWN
- evidence/source

OperationResult
- ok
- code
- message
- ref?
- evidence_refs[]
```

## 7.4 Authority boundary

The Harness API does **not** decide whether an operation is allowed.

For consequential operations, the caller must pass through existing task/policy/ownership checks before invoking the adapter.

Examples:

- `start` requires a valid executable task/run binding;
- `resume` requires canonical task/run/session compatibility;
- `stop` cannot infer permission merely because the provider exposes a kill endpoint;
- `send` cannot silently widen task scope through instructions.

## 7.5 Adapter strategy

Start by wrapping existing mechanisms rather than rewriting them.

Likely structure:

```text
runtime/harness/
  types.py
  protocol.py
  controller.py        # thin composition/normalization, not authority store
  adapters/
    hcom.py
    helper.py
```

Provider-specific logic should remain close to existing transport/helper code where practical. Avoid duplicating the same process-management code into a new tree merely for aesthetics.

## 7.6 Idempotency requirements

Lifecycle calls must have documented duplicate-call behavior.

Examples:

- duplicate `inspect` is harmless;
- duplicate `send` may not be harmless, so caller-supplied message/request IDs should support deduplication where transport supports it;
- duplicate `start` for the same run must not silently produce two competing sessions;
- repeated `stop` on an already-stopped session returns a stable no-op result rather than corrupting state.

## 7.7 Failure cases

The contract must explicitly cover:

- provider unavailable;
- session not found;
- provider reports ambiguous state;
- task/run no longer matches session;
- start succeeds remotely but local acknowledgement fails;
- local record exists but remote start failed;
- stop requested for session no longer owned by task;
- partial send failure;
- timeout with unknown remote result.

Unknown remote result must be represented as **UNKNOWN**, not guessed into success/failure.

## 7.8 Tests

### Contract tests

Every adapter should run the same behavioral suite:

- normalized start/inspect/stop lifecycle;
- unknown session;
- duplicate operations;
- timeout/transport error;
- task/run mismatch rejection at orchestration boundary;
- provider raw state mapped to normalized state;
- no task mutation merely because session changes.

### Regression tests

Existing hcom/helper/recovery behavior must remain valid through the adapter.

## 7.9 Acceptance criteria

Phase complete when:

- orchestration code can perform common lifecycle operations through a typed provider-neutral interface;
- at least current hcom and helper/session paths satisfy shared contract tests;
- no new daemon or persistent authority store exists;
- session state changes cannot mark tasks `DONE`, assign ownership, or grant policy approval;
- errors preserve UNKNOWN/ambiguous outcomes instead of fabricating state.

## 7.10 Kill criteria

Stop and redesign if the “thin interface” starts requiring its own independent task/session truth database or large supervisor loop merely to function.

---

# 8. Phase 2 — Explicit execution/session/helper lineage and fuller trace

Priority: **P1**

Depends on: Phase 1 normalized session concepts; existing run manifests/trace.

## 8.1 Problem

MAPS currently has evidence spread across several stores:

- task DB;
- run manifests;
- hcom;
- recovery state;
- helper-run evidence;
- escalation artifacts.

Trace v1 correctly reports that these external sources are not yet fully correlated.

The Prime harness's strongest observability idea is a **lossless-enough execution lineage**: not more logs, but reliable relationships among the records we already have.

## 8.2 Target lineage

```text
Task
 ├─ Run A
 │   ├─ Session S1
 │   │   ├─ messages/requests
 │   │   └─ Helper H1
 │   └─ replacement Session S2
 │       └─ recovery incident R1
 ├─ Submission #2
 ├─ Review #4
 └─ Outcome #1
```

Every edge must be supported by explicit identifiers or recorded provenance.

## 8.3 Stable ID policy

Where possible, extend existing evidence records with explicit references:

- `task_id`;
- `run_id`;
- `worker_id`;
- `session_id`;
- `parent_run_id` / `parent_session_id` for helpers or replacements;
- `request_id` / thread/message ID for waits;
- artifact/evidence IDs.

Do not infer lineage from timestamps, prose similarity, terminal title, or “probably the only active worker.”

## 8.4 Candidate lineage evidence mechanism

Preferred order:

1. derive relationships from existing explicit fields;
2. add missing stable IDs to the owning evidence record;
3. only if cross-store relationships still cannot be represented, add a small append-only lineage relation table.

Candidate table if necessary:

```text
execution_links
- id
- task_id
- parent_kind       # run/session/helper/recovery/request
- parent_id
- child_kind
- child_id
- relation          # spawned/replaced/recovered/delegated/waits_on/etc.
- source
- created_at
```

If created, this table is **audit evidence**, not task authority, and must be immutable.

## 8.5 Trace v2

Extend `trace TASK-ID` to show:

- canonical task/policy/submission/review/outcome data;
- run manifests and exact context hashes;
- normalized sessions;
- helper child runs;
- recovery incidents/retries;
- escalation evidence;
- structured requests/waits where provable;
- explicit missing-source markers.

Trace should distinguish:

```text
VERIFIED LINK      explicit stable identifiers agree
SOURCE-LOCAL       evidence exists but cannot be joined safely
MISSING            expected source unavailable
UNKNOWN            source checked, state cannot be determined
```

## 8.6 Explainable waits

A wait projection is useful only if based on structured metadata.

Target shape:

```text
waiting_on:
  request_id
  requester
  addressee
  thread_id
  created_at
  resumes_when
  timeout_action
  impact
```

Do not derive “waiting for Alice” from arbitrary chat text if addressee/thread metadata exists.

## 8.7 Recovery lineage

When a replacement session is created after interruption:

- predecessor session remains historical evidence;
- replacement gets its own session ID;
- continuity link records inherited context/obligation;
- task ownership must still be valid;
- if task revision changed materially, create/rebind a new run rather than pretending the old immutable run remained current.

## 8.8 Privacy/secret boundary

Trace v2 may join more diagnostic metadata, which increases exposure risk.

Requirements:

- use existing redaction boundary on text surfaces;
- do not dump arbitrary provider transcripts by default;
- include identifiers/timestamps/status before raw bodies;
- expose raw communication only through explicit diagnostic mode if later justified;
- never put provider credentials/tokens into lineage records.

## 8.9 Tests

- run ↔ session exact binding;
- replacement-session continuity;
- helper parent binding;
- recovery incident binding;
- missing source reported, not silently ignored;
- ambiguous source remains unjoined;
- no timestamp/prose-only inference;
- trace remains read-only;
- secret patterns redacted in diagnostic text;
- continuity still disqualifies independent review where applicable.

## 8.10 Acceptance criteria

An operator can answer, from one trace:

> Who executed this task, with which run/context, which sessions existed, which helper/recovery events occurred, what happened to each session, what submission/review followed, and what sources are still missing?

without manually reading multiple state stores.

---

# 9. Phase 3 — Review/evidence revision binding

Priority: **P1 correctness/safety**

Depends on: immutable task/run revisions already available; lineage helps identify reviewed execution.

## 9.1 Problem

Submission evidence can be correct when recorded and stale when reviewed.

Examples:

- tests passed, then code changed;
- checksum captured, then artifact regenerated;
- package source reviewed, but user downloads a different built artifact;
- security property verified on one run/context revision, then task changed;
- reviewer sees old submission evidence and approves current state.

The harness should know **what exact subject is being approved**.

## 9.2 Target model

A completed review should be bound to a concrete subject:

```text
review
  task_id
  submission_count
  task_revision
  run_id?              # if relevant
  artifact_refs[]      # hashes/immutable IDs when relevant
  evidence_freshness_mode
  completed_at
```

## 9.3 Candidate schema strategy

Prefer a separate append-only subject/binding record over making review rows carry many mutable fields.

Candidate:

```text
review_subjects
- review_id PRIMARY KEY
- task_id
- submission_count
- task_revision
- run_id nullable
- artifact_refs JSON
- freshness_mode
- created_at
```

Immutable triggers should prevent update/delete after binding.

## 9.4 Freshness modes

Possible explicit modes:

```text
REVISION_BOUND
  evidence is inherently tied to an immutable revision/hash

REDERIVED_AT_REVIEW
  reviewer reran/recomputed the consequential property

NON_CONSEQUENTIAL
  evidence freshness does not materially affect approval
```

Avoid a meaningless checkbox such as `fresh=true` with no proof model.

## 9.5 Critical evidence classes

Prioritize mechanical binding/rederivation for:

- security/authorization properties;
- destructive/data-loss safety;
- built/generated artifacts;
- installer/package/release parity;
- user-visible acquisition path;
- checksums/digests;
- high-risk run context;
- deployment configuration.

## 9.6 Approval rule

For work that requires bound evidence, approval fails if:

- current submission count differs from the review subject;
- current task revision differs and no valid new binding exists;
- required artifact hash/identity is missing;
- required rederivation was not performed;
- run/context evidence references a superseded execution.

## 9.7 Tests

- evidence valid on revision A, task changes to B → approval rejected;
- artifact hash changes → old review cannot approve new artifact;
- reviewer rederives required property → approval allowed;
- ordinary low-risk task remains simple;
- criterion evidence and overall review binding agree;
- no exact-source-text test substitutes for behavior-level security property.

## 9.8 Acceptance criteria

For consequential work, the system can answer:

> Exactly what revision/artifact/evidence did this reviewer approve?

and mechanically reject approval when that subject has materially changed.

---

# 10. Parallel-write track — Git worktree isolation

Priority: **P1 when concurrent writable execution is real**

Promotion trigger: simultaneous writable agents are common enough that shared-worktree collisions are plausible, or one real collision/attribution failure occurs.

This track does not need to block Phase 3/4 if the trigger has not occurred.

## 10.1 Problem

Multiple agents sharing one working tree can:

- overwrite each other's uncommitted files;
- accidentally stage unrelated changes;
- make attribution impossible;
- cause one agent's tests to run against another agent's partial edit;
- tempt destructive reset/clean operations.

## 10.2 Target model

```text
writable run
   ↓
unique worktree
   ↓
bound base revision
   ↓
worker edits/tests
   ↓
review/integration
   ↓
explicit cleanup
```

## 10.3 Candidate run metadata

Bind or derive:

- worktree path/ID;
- branch/ref;
- base revision;
- run ID;
- worker ID;
- writable scope;
- created_at;
- integration status.

Do not make the worktree registry a new task authority store.

## 10.4 Safety rules

- no silent `git reset --hard` on another run;
- no automatic deletion of dirty worktrees;
- no branch reuse across active writable runs;
- scope proof still applies inside the worktree;
- integration must explicitly identify source run/worktree;
- cleanup occurs after integration/review or explicit abandonment decision.

## 10.5 Failure cases

- worktree creation fails;
- base ref disappeared/changed;
- worktree becomes dirty outside declared scope;
- worker stops unexpectedly leaving dirty worktree;
- two runs try to claim same branch;
- integration conflict;
- cleanup requested while unmerged changes remain.

Each should produce evidence and an operator/reviewer-visible state, not destructive auto-recovery.

## 10.6 Tests

- two concurrent runs edit same source file independently without collision;
- scope violations caught separately;
- dirty abandoned worktree preserved;
- integration conflict surfaced;
- cleanup refuses unintegrated dirty work;
- run manifest/base revision corresponds to worktree.

## 10.7 Acceptance criteria

Parallel writable agents can execute independently and the final Git changes are attributable to specific runs without hidden cross-contamination.

---

# 11. Helper-continuity track — task-scoped persistent helpers

Priority: **P2 initially; becomes P1 if helper reorientation cost is material**

Depends on: session lineage and normalized Harness API.

## 11.1 Problem

Stateless helper invocation repeatedly spends effort rebuilding orientation. Prime's persistent-agent idea can help, but permanent named agents introduce stale context, identity confusion, and hidden authority.

## 11.2 Target rule

Reuse a helper session only when all compatibility checks pass:

```text
same project
AND same task
AND same helper purpose/capability
AND compatible task revision
AND compatible context fingerprint
AND session healthy
AND TTL not expired
AND parent task still ACTIVE / allowed
```

Otherwise create a fresh helper session.

## 11.3 Continuity record

Useful fields:

- helper/session ID;
- parent task ID;
- parent run ID;
- helper purpose/capability;
- task revision;
- context fingerprint;
- created_at;
- last_used_at;
- expires_at;
- invalidation reason;
- provider/session health.

Prefer evidence owned by the helper/session subsystem. Do not create a global permanent-agent directory unless repeated cross-task reuse proves valuable.

## 11.4 Invalidation triggers

Invalidate helper continuity on:

- task reshaped materially;
- scope changes;
- relevant context hash changes;
- helper purpose changes;
- helper session stops/fails;
- TTL expiry;
- policy/authority changes affecting the helper;
- parent run superseded where compatibility is not provable.

## 11.5 Advisory NO PROGRESS

Before any automated remediation, add only a read-only/advisory signal.

Candidate condition:

```text
session is live
AND task is still eligible
AND no meaningful event/status/output/progress change
FOR worker-aware threshold
→ NO_PROGRESS advisory
```

No-progress must **not** automatically kill, reassign, or modify the task in v1.

## 11.6 False-positive protection

Long reasoning, compilation, model latency, or a legitimate wait can look idle.

Signal should incorporate where available:

- explicit wait/request state;
- provider/session activity;
- recent tool/process output;
- worker-specific expected duration;
- heartbeat/status changes.

## 11.7 Acceptance criteria

Helper reuse demonstrably reduces repeated orientation without allowing stale context to survive material task changes, and no-progress remains advisory until measured precision supports stronger behavior.

---

# 12. Phase 4 — Deterministic lifecycle flows

Priority: **P1/P2 depending repetition evidence**

Depends on: stable Harness API; task/run lineage; review binding for flows involving approval/release.

## 12.1 Problem

LLMs should not repeatedly improvise procedures that are already known, mechanical, and stable.

The original Prime harness concept correctly moved routine lifecycle mechanics out of free-form reasoning.

## 12.2 Promotion rule for a flow

Do not create `maps flow X` because a procedure sounds useful.

Promote only when:

1. the procedure occurs repeatedly;
2. steps are stable;
3. success/failure conditions are mechanically observable;
4. exceptional branches are known;
5. authority checks already exist;
6. deterministic implementation reduces real operator/agent friction.

## 12.3 Candidate flows

### `flow start`

Possible sequence:

```text
validate READY/claimability
→ claim
→ construct/verify context plan
→ create run manifest
→ choose eligible worker
→ start/attach through Harness API
→ bind session
→ report result
```

Must stop before guessing if worker/session creation is ambiguous.

### `flow review`

```text
confirm READY_FOR_REVIEW
→ determine eligible independent reviewer
→ bind review subject/revision
→ claim review
→ surface applicable review lenses
→ record verdict
```

### `flow recover`

```text
confirm task still ACTIVE
→ validate claimant/run/session
→ inspect session
→ apply bounded RnS decision
→ resume or create explicit replacement
→ record lineage
```

### `flow release-check`

For tasks that require operator-visible release/acquisition verification:

```text
verify approved subject
→ validate built/acquired artifact identity
→ run release-path smoke
→ record operator-visible summary
```

### `flow handoff`

```text
validate replacement need
→ freeze current state/context
→ create continuity link
→ ensure review-independence consequence
→ attach/start replacement session
```

## 12.4 Implementation principle

Flows are composition code over existing guarded operations.

They do not introduce another workflow state machine. If a flow needs a new state, that state must first justify itself in the canonical task model.

## 12.5 Resumability

A flow should be idempotent/restartable where possible:

- already completed step recognized;
- no duplicate claim/session/review created;
- partial failure returns exact blocking step;
- unknown external side effect remains UNKNOWN rather than retried blindly.

## 12.6 Acceptance criteria

At least one repeated procedure demonstrates lower coordination burden and equal-or-better correctness through deterministic flow execution before additional flows proliferate.

---

# 13. Phase 5 — Capability and skill composition

Priority: **P2 unless routing complexity demands earlier work**

## 13.1 Problem

Prime-style progressive capabilities are useful when expressed as machine-readable capabilities. They are much less useful when expressed as personas.

MAPS should answer:

> What can this worker actually do, what does this task require, and what is it authorized to do here?

## 13.2 Target representation

Candidate capability bundle:

```yaml
id: python-runtime-edit
requires:
  capabilities:
    - filesystem.read
    - filesystem.write
    - python.execute
    - test.run
optional:
  capabilities:
    - git.worktree
constraints:
  - no_external_deploy_without_policy_approval
context_requirements:
  - task_contract
  - repo_authority
  - referenced_source_files
verification:
  - unit_tests
```

## 13.3 Separate three concepts

### Worker capability

What the runtime can technically do.

### Task requirement

What capability is needed to perform the task.

### Authority

What operations are permitted for this task/run.

Never encode authority into a capability name such as `admin-agent`.

## 13.4 Skill bundles

A skill bundle may contain:

- instructions/procedure;
- required tools;
- verification expectations;
- known safety boundaries;
- context requirements.

It should not contain fake identity claims or “act like a genius” roleplay.

## 13.5 Versioning

If skills affect behavior materially, version them so run/evaluation evidence can identify what configuration was used.

Candidate metadata:

- skill ID;
- version/hash;
- provenance;
- active/superseded state;
- applicability;
- required capabilities;
- instruction source refs.

Do not create a complex skill registry until more than a few real reusable bundles exist.

## 13.6 Routing integration

Routing should prefer workers where:

```text
required capabilities ⊆ available capabilities
AND authority permits execution
AND availability/cost/risk rules permit assignment
```

Provider/model name is a property, not the route rule itself.

## 13.7 Tests

- incapable worker excluded;
- capable but unauthorized worker/action still blocked;
- provider identity alone grants nothing;
- skill version preserved in run/evaluation evidence where used;
- task with no special skill remains simple.

---

# 14. Phase 6 — Controlled operational learning

Priority: **P1 after outcome/trace corpus begins accumulating**

Depends on: outcomes; useful trace/incident provenance; normal review/decision path.

## 14.1 Problem

MAPS needs to remember repeated operational lessons, but unrestricted memory creates folklore, stale rules, contradictions, and accidental policy.

Prime's adaptive-harness idea is valuable only if learning has a lifecycle.

## 14.2 Learning lifecycle

```text
incident / outcome / repeated friction
        ↓
candidate lesson
        ↓
evidence + applicability
        ↓
review / approval
        ↓
scoped active guidance
        ↓
review date / expiry
        ↓
retain | revise | supersede | retire
```

## 14.3 Candidate lesson fields

```text
lesson_id
claim
source_task_ids[]
source_run_ids[]
source_outcome_ids[]
evidence_refs[]
applicability
trigger
promoted_by
promoted_at
starts_at
review_at / expires_at
supersedes[]
status: CANDIDATE | ACTIVE | SUPERSEDED | RETIRED
```

## 14.4 What a lesson can do

A promoted lesson may:

- appear in Context Builder when applicability matches;
- appear in a deterministic flow warning/check;
- influence a routing/configuration proposal if explicitly wired and reviewed;
- become a mechanical check if recurrence proves the prose rule insufficient.

## 14.5 What a lesson cannot do

It may not silently:

- modify task scope;
- change policy;
- authorize destructive/external action;
- override current operator decision;
- become permanent merely because it was once useful;
- rewrite historical outcomes.

## 14.6 Promotion evidence

One anecdote may justify a candidate. Stronger active guidance should usually require one of:

- repeated incidents;
- a high-severity incident with clear causal mechanism;
- controlled test showing prevention;
- operator decision that the rule is deliberately normative.

## 14.7 Mechanical promotion

If an active lesson repeatedly catches the same failure and can be checked deterministically, consider converting it from prose guidance into:

- validator;
- flow precondition;
- typed constraint;
- test.

Then retire/simplify the redundant prose where possible.

## 14.8 Acceptance criteria

MAPS can carry a proven lesson into the next relevant task with explicit provenance and expiry while preventing the lesson from becoming hidden policy.

---

# 15. Phase 7 — Measured harness evaluation and refinement

Priority: **P1 long-term / evidence-gated**

This is the strongest long-term Prime capability and the one most dangerous to implement prematurely.

## 15.1 Entry conditions

Do not begin automatic comparative refinement until all are true:

- enough completed runs exist to form meaningful comparisons;
- outcomes are being recorded often enough to distinguish process completion from real success;
- trace/lineage is complete enough to identify likely failure mechanisms;
- configuration versions can be attributed to runs;
- real incidents can be frozen as regression cases;
- evaluation can run without modifying production authority.

## 15.2 Three-layer evaluation discipline

### Layer 1 — Mechanical

Examples:

- state transitions;
- authority checks;
- recovery idempotency;
- lineage consistency;
- context hash behavior;
- worktree isolation;
- security properties;
- deterministic-flow behavior.

### Layer 2 — Agent/model qualitative regression

Frozen tasks/scenarios evaluating:

- orientation quality;
- plan correctness;
- scope discipline;
- context sufficiency;
- review quality;
- paraphrase/vocabulary-shift robustness;
- hard negatives / appropriate abstention.

### Layer 3 — Production/outcome sampling

Measure real runs:

- escaped defects;
- rework;
- operator intervention;
- recovery success/failure;
- cost/yield;
- time/steps to useful completion;
- review catch rate;
- false-positive blockers;
- context volume;
- helper usefulness;
- user/operator outcome.

## 15.3 Incident taxonomy

At minimum classify:

- tool failure;
- provider/session failure;
- context omission;
- context overload;
- routing error;
- ownership/authority error;
- scope drift;
- runaway loop;
- helper failure;
- no-progress false positive/negative;
- recovery failure;
- duplicate execution;
- review miss;
- stale evidence;
- validator false positive/negative;
- release/acquisition mismatch;
- operator friction/intervention;
- real-world post-completion regression.

## 15.4 Candidate configuration changes

The refinement system may propose changes to:

- routing thresholds;
- context composition;
- skill selection;
- helper reuse policy;
- no-progress threshold;
- recovery retry/backoff parameters;
- deterministic flow ordering;
- instruction wording;
- review lens selection;
- model/provider selection rules;
- cost budgets.

## 15.5 Frozen comparative evaluation

For a candidate change:

```text
freeze corpus before treatment
        ↓
run current config
        ↓
run candidate config
        ↓
blind/independent scoring where practical
        ↓
compare correctness + safety + cost + abstention
        ↓
proposal only
        ↓
normal review/approval
```

Never generate the evaluation set after seeing candidate results.

## 15.6 Regression cases from incidents

When a real incident reveals a mechanism:

1. preserve a sanitized minimal reproduction;
2. freeze expected behavior;
3. add it to the regression corpus;
4. require future candidate harness changes not to reintroduce it.

## 15.7 Context retrieval evaluation

If semantic/query-expanded retrieval is proposed later, compare it against explicit Context Builder v1 with:

- paraphrase queries;
- vocabulary shift;
- historical-version traps;
- hard negatives;
- explicit abstention requirements;
- exact-source accuracy;
- anchored-evidence accuracy;
- source-hash drift reporting.

Legacy evidence already demonstrated that vocabulary-matched lexical retrieval can look much better than it is.

## 15.8 Promotion rule

A candidate harness change should not be promoted because it “seems smarter.”

Promotion needs:

- stated hypothesis;
- frozen evaluation;
- measurable benefit on the target problem;
- no unacceptable safety/authority regression;
- understandable tradeoff;
- review/approval.

## 15.9 Automatic self-modification: rejected

MAPS must never enter:

```text
observe failure
→ edit own policy/instructions
→ deploy change
```

without review.

The allowed loop is:

```text
observe
→ propose
→ evaluate
→ review
→ approve
→ deploy
→ monitor
```

---

# 16. Cross-phase failure model

These cases should be treated as first-class test scenarios across the roadmap.

## 16.1 Session alive, task no longer authorized

Example: task reshaped or operator halted work while provider process remains alive.

Required behavior:

- session liveness visible;
- harness does not infer continued permission;
- further action blocked/flagged according to current task/policy;
- operator can stop/inspect through authorized path;
- trace preserves mismatch evidence.

## 16.2 Task ACTIVE, session missing

Required behavior:

- status shows stranded active task/session gap;
- recovery checks explicit binding;
- no blind creation of duplicate session;
- if recovery cannot determine remote state, represent UNKNOWN and escalate.

## 16.3 Start succeeds remotely, acknowledgment lost

Required behavior:

- retry first inspects/deduplicates using stable request/session identifiers;
- do not assume start failed and create another worker blindly.

## 16.4 Helper context stale after reshaping

Required behavior:

- compatibility check fails;
- old helper retained as history but not reused;
- new helper/run created if still needed.

## 16.5 Recovery replacement would self-review

Required behavior:

- continuity lineage makes replacement ineligible for independent review if it inherited implementation context.

## 16.6 Worktree contains unintegrated changes during cleanup

Required behavior:

- cleanup refuses destructive deletion;
- status/trace points to dirty worktree and owning run.

## 16.7 Review evidence stale

Required behavior:

- approval rejected or consequential evidence rederived;
- old evidence retained historically.

## 16.8 Outcome says FAILURE after task DONE

Required behavior:

- task historical completion not rewritten;
- current status can surface post-completion failure attention;
- candidate repair/lesson may be proposed separately.

## 16.9 Harness adapter disagrees with transport

Required behavior:

- preserve raw provider status/evidence;
- normalized state may be UNKNOWN;
- no fabricated certainty.

---

# 17. Security and privacy requirements

Prime-derived lifecycle integration increases the number of joined records. That makes data minimization more important.

## 17.1 Secrets

- credentials live outside task/event/trace text;
- diagnostic text uses shared redaction boundary;
- provider adapter errors are sanitized before durable logging;
- raw provider request/response payloads are not stored by default;
- worktree/session metadata must not include tokens.

## 17.2 Authority tests

Security/authority tests assert executed behavior, not exact source wording.

Examples:

- unauthorized stop rejected;
- session cannot approve task;
- helper cannot gain ownership;
- stale run cannot execute changed scope;
- capability metadata cannot bypass policy;
- proposal/lesson citation cannot ratify itself.

## 17.3 Privacy

Joined traces should prefer identifiers and concise metadata over complete conversation bodies.

If raw communication replay becomes necessary, it should be explicit diagnostic access with its own retention/privacy policy rather than an automatic default trace field.

---

# 18. Observability and metrics

The purpose of metrics is to tell whether the harness is helping, not to reward activity.

## 18.1 Reliability metrics

- percentage of active tasks with unambiguous run/session binding;
- recovery success rate;
- duplicate-session incidents;
- orphaned-session incidents;
- session-state UNKNOWN rate;
- worktree collision/attribution incidents;
- stale review evidence rejections;
- release-path mismatches.

## 18.2 Quality metrics

- escaped defects;
- rework count;
- review `CHANGES_REQUESTED` catch rate;
- post-completion failure outcomes;
- operator intervention count;
- task success/partial/failure outcomes.

## 18.3 Efficiency metrics

- context bytes/files supplied per run;
- repeated helper orientation avoided;
- helper reuse success vs invalidation;
- cost per successful outcome where cost is measurable;
- number of manual orchestration steps eliminated by deterministic flows;
- no-progress signal precision/recall once enough labeled incidents exist.

## 18.4 Anti-metrics

Do not optimize for:

- number of agents spawned;
- number of messages;
- number of lessons generated;
- number of tasks created;
- number of ideas promoted;
- raw token volume;
- “agent utilization” detached from outcome.

---

# 19. Detailed implementation backlog

These are candidate implementation tasks, not authorized tasks. They are ordered enough that fresh agents can shape them when each phase is promoted.

## Phase 0 tasks

### P0-01 — Independent review of current foundation

Review PR #19 packets, resolve findings, establish accepted baseline.

### P0-02 — Baseline architecture update

After merge/rejection, update roadmap references to actual `main` behavior.

---

## Phase 1 tasks — Harness API

### H1-01 — Inventory current lifecycle operations

Document current hcom/helper/recovery start/inspect/send/stop/resume operations and their error semantics.

### H1-02 — Define normalized harness types

Create provisional typed structures for execution binding, session ref, state, status, operation result, collected evidence.

### H1-03 — Define Harness protocol

Small provider-neutral interface; explicitly no authority store.

### H1-04 — hcom adapter

Wrap current hcom lifecycle behavior without changing semantics.

### H1-05 — helper adapter

Normalize helper session lifecycle where compatible with the protocol.

### H1-06 — adapter contract test suite

Same lifecycle/error/idempotency tests for each adapter.

### H1-07 — integrate one real orchestration path

Route one existing start/inspect/recover path through the interface and prove no behavior regression before broad migration.

### H1-08 — remove duplicated provider branches only after parity

Do not refactor everything at once.

---

## Phase 2 tasks — Lineage/trace

### H2-01 — Stable identifier audit

For task/run/session/helper/recovery/escalation/request records, inventory which exact IDs already exist and where links are missing.

### H2-02 — Add missing explicit parent/run/session references

Modify owning records, not a global graph, where possible.

### H2-03 — Replacement-session continuity evidence

Ensure recovery-created replacements have explicit predecessor linkage.

### H2-04 — Helper lineage

Bind helper evidence to parent task/run/session where available.

### H2-05 — Recovery lineage

Expose incident/retry/replacement evidence to trace.

### H2-06 — Escalation lineage

Join escalation artifacts by explicit task/run IDs.

### H2-07 — Trace v2 coverage model

Add VERIFIED/SOURCE-LOCAL/MISSING/UNKNOWN source/link states.

### H2-08 — Explainable wait projection

Only after structured request/addressee/thread IDs are verified.

### H2-09 — Cross-store trace tests

Frozen synthetic lifecycle scenarios including partial/missing stores.

---

## Phase 3 tasks — Review binding

### H3-01 — Define review subject schema

Submission count + task revision + optional run/artifact refs + freshness mode.

### H3-02 — Immutable review-subject persistence

Additive migration with update/delete protection.

### H3-03 — Approval freshness enforcement

Reject consequential approval against stale subject.

### H3-04 — Artifact binding

Hash/immutable artifact refs for package/release/generated outputs where relevant.

### H3-05 — Re-derivation hooks

Permit reviewer-time mechanical checks for security/release properties.

### H3-06 — Historical compatibility

Old reviews remain readable; absence of binding is explicit rather than fabricated.

---

## Parallel-write tasks

### HW-01 — Concurrency incident/need confirmation

Confirm promotion trigger from real or imminent usage.

### HW-02 — Worktree lifecycle design

Create/bind/inspect/integrate/cleanup states without new task authority.

### HW-03 — Run/worktree binding

Attach exact base revision and worktree identity to execution evidence.

### HW-04 — Parallel isolation tests

Two writable agents, same source paths, independent worktrees.

### HW-05 — Safe cleanup/integration

No destructive cleanup of dirty/unintegrated work.

---

## Helper continuity tasks

### HC-01 — Helper compatibility fingerprint

Task/project/purpose/revision/context/TTL criteria.

### HC-02 — Reuse decision projection

Return REUSE / REBUILD / UNKNOWN with reasons.

### HC-03 — TTL and invalidation

Mechanical expiry and material-change invalidation.

### HC-04 — Advisory no-progress signal

No task mutation.

### HC-05 — Label real no-progress incidents

Build precision/recall evidence before stronger actions.

---

## Deterministic-flow tasks

### HF-01 — Procedure repetition inventory

Find actually repeated stable multi-step procedures.

### HF-02 — First flow pilot

Choose one procedure with clear mechanical boundaries.

### HF-03 — Idempotency/restart tests

Partial execution must resume safely.

### HF-04 — Flow audit evidence

Record which existing guarded operations were called and their results.

### HF-05 — Additional flows only after pilot outcome

No flow explosion.

---

## Capability/skill tasks

### HS-01 — Capability vocabulary audit

Normalize existing worker capability envelope names before adding more structure.

### HS-02 — Task requirement representation

Add only if routing needs mechanical matching beyond current fields.

### HS-03 — First reusable skill bundle

Choose one demonstrated repeatable procedure/context bundle.

### HS-04 — Skill version attribution

Make evaluation able to identify which skill version a run used.

---

## Operational-learning tasks

### HL-01 — Candidate lesson schema

Provenance, applicability, promotion, expiry, supersession.

### HL-02 — Outcome/incident → candidate workflow

Candidate only, no automatic activation.

### HL-03 — Context Builder integration

Surface only applicable ACTIVE lessons.

### HL-04 — Expiry/review job or deterministic check

No immortal lessons.

### HL-05 — Mechanical promotion path

Convert repeated proven prose lessons into validators/flows/tests when practical.

---

## Harness-evaluation tasks

### HE-01 — Configuration attribution

Runs must identify relevant harness/config versions.

### HE-02 — Incident taxonomy implementation

Consistent outcome/failure classification.

### HE-03 — Frozen regression corpus

Begin with real incidents plus existing mechanical tests.

### HE-04 — Qualitative eval set

Orientation/context/routing/review cases, including paraphrases/hard negatives.

### HE-05 — Comparative runner

Current vs candidate config with isolated outputs.

### HE-06 — Scorecard

Correctness, safety, cost/yield, escaped defects, operator intervention.

### HE-07 — Proposal generator

Produces change proposal/evidence, not deployment.

### HE-08 — Promotion workflow

Normal review/approval before active harness config changes.

---

# 20. Dependency graph

```text
P0 current foundation accepted
│
├── H1 Harness API
│    │
│    ├── H2 lineage/trace
│    │    │
│    │    ├── H3 review/evidence binding
│    │    │    │
│    │    │    └── HF deterministic flows
│    │    │
│    │    ├── HC helper continuity
│    │    │
│    │    └── HW worktree isolation (when concurrency trigger exists)
│    │
│    └── HS capability/skill composition
│
├── current outcomes + H2 trace
│    └── HL operational learning
│          │
│          └── HE measured harness refinement
│
└── H3/HF/HS/HC improvements feed additional HE evaluation dimensions
```

Important: not every branch must finish before operational learning starts. The actual gate is **enough trustworthy provenance/outcome evidence**, not completion of every feature.

---

# 21. Promotion gates by phase

| Phase | Entry gate | Exit evidence |
|---|---|---|
| 0 Foundation | PR #19 reviewable | approved/merged baseline or explicit replacement |
| 1 Harness API | current provider operations understood | shared adapter contract tests + one real integration path |
| 2 Lineage | stable run/session concepts | cross-store trace reconstructs lifecycle without inference |
| 3 Review binding | immutable revision/artifact identity available | stale consequential evidence mechanically rejected |
| Worktrees | concurrent writes plausible/observed | isolated parallel runs + safe integration/cleanup |
| Helper continuity | repeated helper reorientation cost | measured useful reuse without stale-context leakage |
| 4 Flows | repeated stable procedure | pilot reduces coordination without correctness loss |
| 5 Skills | routing repeatedly needs reusable capabilities | mechanical capability matching improves route clarity |
| 6 Learning | enough incidents/outcomes | promoted lesson has provenance + expiry and appears only when applicable |
| 7 Refinement | enough attributed outcome-linked runs | candidate beats current config on frozen eval and is independently approved |

---

# 22. Prime ideas explicitly rejected or heavily gated

| Prime/agent-harness idea | Decision | Reason |
|---|---|---|
| Persistent `mapd` supervisor daemon | Reject by default | existing bounded components already own lifecycle pieces; daemon creates new central failure/complexity |
| Second task/session authority database | Reject | violates one-fact/one-authority principle |
| Fixed permanent named agent roster | Reject | stale identities/personas create bureaucracy without granting useful capability |
| Persona-heavy specialist prompts | Reject | capabilities/procedures are clearer and testable |
| Always-on discovery agent | Reject | bounded phase-boundary discovery already provides benefit with less drift |
| Always-on process/adherence police | Reject | bounded audits are enough unless recurrence proves otherwise |
| Autonomous self-modification | Reject | refinement remains proposal/evaluation/review |
| Giant knowledge graph/library | Reject by default | Context Builder should remain explicit-first and evidence-driven |
| Legacy lexical claim-card retriever | Reject as validated solution | experiment did not validate it |
| Semantic retrieval by default | Evidence-gated | must beat explicit-first baseline on frozen paraphrase/hard-negative eval |
| Universal microVM per worker | Threat-model gated | cost/complexity unjustified without stronger isolation requirement |
| Temporal/Cedar/A2A/MCP-everywhere rewrites | Need-driven only | adopt only if a current limitation cannot be solved simply |
| Separate Prime “goal” store | Reject by default | task outcomes/project grouping already persist goals; add Mission only if evidence shows gap |

---

# 23. End-state scenarios

These scenarios define what “Prime's useful functions are in MAPS” should feel like in practice.

## Scenario A — Normal implementation

1. Operator creates/shapes task.
2. AGI readiness confirms no material ambiguity.
3. Router identifies eligible worker by capability, not provider prestige.
4. Context Builder produces explicit context plan.
5. Run manifest freezes task revision/context/scope.
6. Harness starts worker session through provider adapter.
7. Run/session linkage appears in trace/status.
8. Worker submits evidence.
9. Independent reviewer gets applicable risk lenses and exact review subject.
10. Approval binds to current revision/artifact.
11. Task becomes DONE.
12. Later outcome can record SUCCESS/PARTIAL/FAILURE without rewriting history.

No Prime daemon is required.

## Scenario B — Agent interrupted mid-task

1. Session becomes unreachable.
2. Task remains ACTIVE with known run/session binding.
3. Status surfaces stranded/unknown session.
4. Recovery inspects normalized session state.
5. If safely recoverable, resume.
6. If replacement required, create explicit replacement session and continuity link.
7. Replacement inherits obligations but does not become independent reviewer.
8. Trace shows predecessor → recovery incident → replacement.

No duplicate agent is spawned merely because a timeout occurred.

## Scenario C — Two coding agents work in parallel

1. Two independent tasks/runs require writable access.
2. Each run receives its own worktree and base revision.
3. Both may edit the same source path independently.
4. Scope checks apply independently.
5. Review/integration sees exact source run/worktree.
6. Conflict is resolved explicitly.
7. Dirty unintegrated worktree cannot be silently deleted.

## Scenario D — Helper reused intelligently

1. Parent task asks helper for repeated bounded analysis.
2. Helper session is alive, same task/purpose, same compatible context hash, TTL valid.
3. Harness reuses it rather than paying reorientation cost.
4. Task is later reshaped.
5. Compatibility check invalidates old helper continuity.
6. Fresh helper receives new context if still needed.

## Scenario E — Real-world failure becomes a lesson

1. Task passes review and becomes DONE.
2. Operator later records FAILURE outcome: generated package differed from reviewed source.
3. Incident classification marks release/acquisition mismatch and escaped defect.
4. Candidate lesson proposes release-artifact hash binding.
5. Review promotes the lesson for relevant release tasks.
6. Later evidence shows this should become a mechanical release-flow check.
7. Prose lesson is superseded by deterministic enforcement.

## Scenario F — MAPS evaluates a harness change

1. Many outcome-linked runs show context omissions on paraphrased tasks.
2. Candidate semantic supplementation is proposed.
3. Frozen corpus includes vocabulary-shift and hard-negative cases.
4. Current explicit Context Builder and candidate are run separately.
5. Candidate must improve useful recall/anchoring without unacceptable false positives or authority mistakes.
6. Results become a proposal.
7. Reviewer/operator approves or rejects.
8. Only approved configuration becomes active.

This is harness improvement without autonomous self-rule.

---

# 24. Final definition of done

The Prime Agent capability adoption effort is complete enough when MAPS provides these guarantees:

## Orientation

A fresh worker can obtain a compact, trustworthy description of:

- task intent;
- current authority;
- explicit sources/context;
- dependencies;
- output/non-goal boundaries;
- applicable proven guidance.

## Execution

A worker can be started/attached/inspected/resumed/stopped through a provider-neutral lifecycle interface while task authority remains in canonical MAPS state.

## Continuity

Runs, sessions, replacements, helpers, and recovery events have explicit lineage and can survive interruption without relying on prose guesses.

## Isolation

When parallel writes are used, each writable run is attributable and isolated enough that agents cannot silently corrupt one another's work.

## Delegation

Helpers may preserve useful task-scoped continuity but cannot become permanent hidden authorities or review their inherited implementation context independently.

## Determinism

Repeated stable orchestration procedures can be executed as bounded flows instead of being re-invented by an LLM every time.

## Review

Consequential approval identifies the exact task revision/run/artifact/evidence subject and rejects materially stale evidence.

## Outcomes

MAPS distinguishes “workflow completed” from “real-world result succeeded.”

## Learning

Repeated real failures can become scoped, reviewed, expiring lessons and eventually mechanical checks.

## Refinement

Harness changes can be compared on frozen historical evidence and real outcome metrics, but remain proposal-only until normal review/approval.

## Complexity boundary

The system achieves all of the above **without** creating a second giant intelligent control system whose maintenance and internal state are harder to trust than the agents it coordinates.

That complexity boundary is part of the definition of done, not an optional aesthetic preference.
