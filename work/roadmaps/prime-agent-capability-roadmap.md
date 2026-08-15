# Prime Agent capability adoption roadmap

Status: `PLANNING ONLY — NOT ACTIVE AUTHORITY`

Goal: absorb the most useful Prime Agent harness capabilities into MAPS Lean without rebuilding a second orchestrator, `mapd`, fixed agent roster, or self-modifying control plane.

## Design rule

Prime capabilities are adopted as **small lifecycle guarantees around existing MAPS authorities**:

- SQLite remains task/authority/evidence truth;
- hcom remains communication/session transport;
- LangGraph remains routing/checkpoint machinery;
- RnS remains bounded recovery;
- helpers remain delegated task-scoped work;
- derived context/status/trace views remain read-only.

Do not create a parallel Prime state machine.

## Already absorbed

| Prime-style capability | Lean implementation |
|---|---|
| Durable goals/work | task outcomes, acceptance criteria, dependencies, canonical SQLite lifecycle |
| Guarded ownership/authority | claims, leases, policy metadata, operator approval, review independence |
| Provider-neutral orchestration | worker capability envelopes + routing/adapters rather than provider identity |
| Recovery | RnS bounded retry/backoff against explicit active bindings |
| Delegation | bounded helper lanes that inherit scope but not ownership/authority |
| Context orientation | Context Builder v1 over explicit sources/inputs/dependencies and exact hashes |
| Session/history visibility | trace v1 plus event/review/run/outcome history |
| Real-world feedback | append-only post-completion outcomes |
| Operator visibility | read-only status surface |
| Behavioral constraints | negative operating contract + risk-specific review lenses |

These should not be rebuilt under Prime-specific names.

# Roadmap

## Phase 1 — Provider-neutral Harness API

**Purpose:** recover Prime's useful Host/Runtime API idea without a daemon.

Create a small typed lifecycle interface used by orchestration code for operations such as:

```text
start / attach
send
inspect status
heartbeat
resume / recover
stop when authorized
collect result/evidence
```

The interface delegates to existing hcom/helper/recovery/provider adapters. It owns no task state and grants no authority.

**Done when:** orchestration code can reason about worker/session lifecycle without provider-specific branches, and existing adapters pass the same contract tests.

**Do not build:** network service, `mapd`, remote authority server, second session database.

## Phase 2 — Execution/session lineage and fuller trace

**Purpose:** recover Prime's lossless session/context-tree value.

Join existing explicit identities rather than infer them:

```text
task
→ run manifest
→ worker
→ session
→ helper/recovery lineage
→ review
→ outcome
```

Extend trace/status to correlate hcom, recovery, helper, and escalation evidence only where stable IDs make the relationship provable. Missing coverage remains explicit.

Add explainable waits as a read-only projection when structured request/addressee/thread metadata is available.

**Done when:** an operator can answer “who did what, with which context, what happened next, and what are we waiting for?” without reading several state stores manually.

## Phase 3 — Safe parallel writable execution

**Purpose:** recover Prime's concurrency/isolation benefits.

Add Git worktree isolation for simultaneous writable coding agents:

- one writable worker/run → one attributable worktree;
- bind worktree/base revision to the run manifest;
- preserve writable/forbidden scope checks;
- explicit cleanup only after integration/review;
- never silently reset or discard another worker's work.

**Promotion trigger:** real concurrent writable work becomes common enough that shared-worktree collisions are plausible or observed.

## Phase 4 — Task-scoped persistent helper continuity

**Purpose:** keep useful helper context without inventing permanent personalities.

Allow a helper session to be reused when all of these remain true:

- same task/project;
- same role/capability need;
- compatible task revision/context hash;
- helper/session still healthy;
- explicit TTL/expiry has not elapsed.

Invalidate/rebuild continuity on material task/context changes.

Add advisory `NO PROGRESS` detection before any automatic remediation.

**Do not build:** fixed named agent roster, universal long-lived agents, hidden memory authority.

## Phase 5 — Deterministic lifecycle flows

**Purpose:** recover Prime's “harness does routine orchestration for the model” benefit.

Add `maps flow ...` only for procedures that have become repetitive and stable, likely candidates:

```text
start execution
prepare review
recover interrupted run
release/integration check
handoff/continuity check
```

Flows call existing guarded state transitions; they do not create a second workflow engine.

**Done when:** routine multi-step MAPS procedures are deterministic and auditable while exceptions still escalate to agents/operators.

## Phase 6 — Review/evidence binding

**Purpose:** ensure the harness knows what exact state was reviewed.

For consequential work, bind review evidence to immutable revision/artifact identity or re-derive the property at review time.

Priorities:

- security/authority evidence;
- generated/package/release artifacts;
- parity/checksum claims;
- run/context revision;
- user-visible acquisition path.

This is more valuable than merely adding more reviewers.

## Phase 7 — Capability/skill composition

**Purpose:** recover Prime's progressive skills idea without persona prompting.

Use machine-readable capability requirements and reusable tool/instruction bundles only where routing actually benefits.

Example shape:

```text
capability: python-runtime-edit
requires: filesystem-write + python + tests
optional: git-worktree
forbidden: external-deploy unless policy-approved
```

Keep provider/model names separate from capability and authority.

**Do not build:** “marketing genius”, “architect personality”, or other roleplay-based agent definitions.

## Phase 8 — Operational learning

**Purpose:** carry proven lessons forward without infinite memory.

Use controlled lifecycle:

```text
incident/outcome
→ candidate lesson
→ review
→ scoped active guidance
→ expiry / supersession / retirement
```

Lessons need provenance, applicability, promotion authority, and a review/expiry date.

No lesson may silently rewrite policy or task history.

## Phase 9 — Measured harness evaluation/refinement

**Purpose:** recover Prime's strongest long-term idea: improve the harness from evidence.

Prerequisites:

- enough outcome-linked runs;
- trace completeness good enough for diagnosis;
- frozen regression cases from real incidents;
- mechanical + qualitative + production/outcome evaluation layers.

Candidate changes may include routing thresholds, context composition, helper policy, instructions, recovery parameters, and deterministic-flow behavior.

Refinement remains **proposal-only**. The harness never self-authorizes configuration/policy changes.

Evaluation must include escaped defects, rework, operator intervention, cost/yield, failure taxonomy, paraphrase/hard-negative context tests, and end-to-end lifecycle success.

# Prime ideas intentionally not recreated

| Old/possible Prime mechanism | Lean decision |
|---|---|
| Persistent `mapd` supervisor daemon | Reject by default; existing bounded components are sufficient |
| Second task/session authority store | Reject |
| Fixed permanent agent roster | Reject |
| Persona-heavy specialist definitions | Reject |
| Always-on autonomous self-refinement | Reject |
| Giant knowledge graph/library | Reject unless later evidence demands a narrow projection |
| Semantic retrieval by default | Evidence-gated; Context Builder stays explicit-first |
| Universal microVM/container per worker | Threat-model dependent, not default |

# Priority order

```text
CURRENT LEAN FOUNDATION
        ↓
1. typed provider-neutral Harness API
        ↓
2. explicit session/run/helper lineage + fuller trace/waits
        ↓
3. worktree isolation when parallel writes justify it
        ↓
4. task-scoped helper continuity + advisory no-progress
        ↓
5. deterministic repeated flows
        ↓
6. immutable review/evidence binding
        ↓
7. capability/skill composition if routing needs it
        ↓
8. controlled operational learning
        ↓
9. outcome-driven harness evaluation/refinement
```

## Success condition

MAPS should gain the Prime harness's useful property:

> A worker can enter a well-defined environment, receive the right context and authority, execute through a provider-neutral lifecycle, survive interruption, delegate safely, be independently reviewed, and leave enough evidence for the system to improve later.

It should **not** gain Prime's possible failure mode:

> another large intelligent control system whose internal complexity becomes harder to trust than the agents it is coordinating.
