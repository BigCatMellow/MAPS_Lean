# Wave 3 progress handoff — 2026-08-15

Status: **ACTIVE DEVELOPMENT / REVIEW PENDING**

This note captures the work completed in the parallel Wave 3 lane while the independent reviewer continued integrating the Wave 1 harness/security stack. It is a handoff/status note only. It does not change runtime authority, roadmap authority, policy, task state, or review outcome.

## Current repository checkpoint

At the time this note was written:

- `main` = `c9e52cfcea2afd6c1fab3956baedcf62117450af`
- PR #20 — harness foundation: **MERGED**
- PR #21 — hcom normalization + Hooks: **MERGED**
- PR #22 — `HarnessService`: **MERGED** at feature head `68224f4e46c585ce232ae20c70a076a132cb2319`
- PR #23 — canonical run guard: **MERGED** at feature head `bec3f78f7e5f2b7ec8fac04c7403452267f2f5d7`, merge commit `c9e52cfcea2afd6c1fab3956baedcf62117450af`
- PR #24 — initial agentic-security baseline: **OPEN DRAFT**, head `4ec42de3398258ebde0e0645516caef953a6a0ed`

The critical integration boundary is now narrow: #24 is the remaining Wave 1 security gate before durable execution-lineage implementation should bind to the accepted harness/security interface.

## Work completed in this lane

### 1. Execution-lineage design — PR #38

PR #38: `Design explicit execution lineage Wave 3`

Branch: `agent/execution-lineage-design-wave3`

Purpose: define the post-harness execution-lineage model without freezing runtime code against moving upstream interfaces.

Core design:

```text
task
  -> immutable run
  -> worker
  -> provider session(s)
  -> helper / recovery / replacement
  -> request / thread / addressee
  -> exact submission attempt
  -> review / outcome
```

Key rules:

- immutable `run_manifests` remain immutable;
- no mutable `tasks.current_session_id`;
- no generic mutable lineage graph/blackboard;
- no mirrored hcom message store;
- no timestamp/name/prose inference;
- missing joins remain `UNKNOWN`;
- session/process liveness is not task authority;
- API/provider readiness is distinct from process/session liveness;
- changing worker identity or materially changing the run contract creates a new run rather than rewriting history.

Proposed append-only relation families:

- `run_session_links`
- `run_recovery_links`
- `run_helper_links`
- `run_request_links`
- `submission_run_links`

Planned execution sequence after the upstream harness/security contract settles:

1. **A1** — run/session lineage core + resolver;
2. **A2** — helper/recovery lineage;
3. **A3** — exact submission-attempt lineage;
4. **A4** — communication correlation;
5. **A5** — operation evidence only if evaluation demonstrates the need;
6. then derive explainable waits.

### 2. Context Builder v2 evidence-integrity foundation — PR #39

PR #39 freezes the evaluation corpus before retrieval work.

It deliberately separates:

```text
Stage 1: evidence-card integrity with a known source set
Stage 2: later retrieval supplementation vs explicit-first control
```

The frozen corpus covers:

- direct current evidence;
- code-symbol evidence;
- paraphrase and vocabulary shift;
- hard negatives;
- current vs retired material;
- authority-status distinction;
- negative boundaries;
- same-path source drift;
- acceptable substitutes;
- operator-visible acquisition-path evidence.

This preserves the useful lesson from legacy `EXP-0006` without reviving its unvalidated lexical claim-card retriever.

### 3. Stage-1 evidence projector/scorer — PR #41

PR #41: `Add Stage 1 Context Builder evidence projector and scorer`

Current head: `c997821c4a5f3d11c2bc7f8a98dd7a33750c3feb`

Last verified full Runtime CI: **passed** (`#211`).

Implements:

```text
explicit source + anchor
  -> verify source hash
  -> mechanically verify anchor
  -> project evidence card
  -> score against frozen corpus
```

The scorer distinguishes:

- wrong evidence -> `FAIL`;
- missing / honest `UNKNOWN` -> `INCOMPLETE`.

It checks:

- exact source;
- SHA-256;
- anchor;
- proof role;
- polarity;
- temporal scope;
- source drift;
- hard-negative abstention;
- acceptable-substitute correctness;
- extra uncredited evidence.

Owner-side hardening added before handoff:

- `UNKNOWN` cannot hide returned cards;
- `UNKNOWN` cannot hide a drift claim;
- acceptable substitutes must explicitly contain `credit_only_if_retrieved: true`;
- missing or false substitute-credit markers fail closed.

Deliberate boundary: **no retrieval, search, ranking, embeddings, vectors, production Context Builder change, routing, or automatic promotion**.

### 4. End-to-end Layer 2 / Layer 3 benchmark protocol — PR #40

PR #40 freezes the next MAPS benchmark protocol.

Layer 2 permits controlled representative fixtures executed through real agent/model behavior.

Layer 3 requires real eligible task/run/outcome evidence and forbids synthetic substitutes.

Frozen scenarios cover:

1. orientation + safe first action;
2. interruption/recovery + duplicate-work prevention;
3. independent review + fresh evidence;
4. context sufficiency under paraphrase/negative/authority boundaries;
5. real external/operator-visible delivery;
6. real completed-run outcome + operator-friction sample.

Scoring rules:

- required `FAIL` fails a scenario;
- blocker failures are non-tradeable;
- `UNKNOWN` / `NOT_RUN` cannot become PASS;
- quality, safety, operator friction, cost, and outcome are not collapsed into a weighted score;
- activity volume is measurement, not success.

### 5. Benchmark result validator — PR #42

PR #42: `Add MAPS end-to-end benchmark result validation`

Current head: `beeef987e25509136ff3de5b79263c984cc501da`

Last verified full Runtime CI: **passed** (`#200`).

It validates externally produced benchmark evidence only.

Layer 3 requires:

- `REAL_PRODUCTION` fixture class;
- verified task provenance;
- verified run provenance;
- verified real outcome provenance.

`E2E-L3-001` additionally requires:

- verified operator/user-visible result;
- verified existing task authority for the external effect.

Operator intervention counts require attributable provenance when the protocol says they matter.

Owner-side hardening:

- count-like measurements (`tool_calls`, `messages`, `agent_count`, operator interventions, rework) must be non-negative integers;
- duration/cost remain bounded finite numeric measurements.

Deliberate boundary: the validator **does not execute the benchmark, sample production, create outcomes, authorize external effects, or promote a candidate**.

### 6. Operational-learning guidance projection — PR #43

PR #43: `Add guidance-only operational learning projection`

Current head: `aeecf1b5775db1d5ac2484819620f476752f3654`

Last verified full Runtime CI: **passed** (`#202`).

Lifecycle modeled:

```text
CANDIDATE
  -> external promotion decision required
ACTIVE
  -> applicability check
GUIDANCE_ONLY projection
```

Guidance is withheld when:

- candidate/not promoted;
- not started;
- expired;
- review due;
- superseded;
- retired;
- not applicable;
- applicability is unknown.

Important design choice: there is **no lesson database and no `promote()` function** in this tranche.

An ACTIVE record must already contain an external promotion decision reference, actor, start time, and review timing.

Owner-side hardening:

- lesson snapshots now reject unknown/missing top-level fields instead of silently ignoring them.

Deliberate boundary:

```text
lesson != policy
lesson != task authority
lesson != approval
```

### 7. Full-fidelity hcom lineage read — PR #44

PR #44: `Add full-fidelity hcom lineage read path`

Head: `4e10f8dadcd64e7b91fb8d608b92f268fde00821`

Last verified full Runtime CI: **passed** (`#192`).

Upstream hcom `v0.7.25` stores the communication facts needed for exact lineage, but normal event output deliberately removes some of them.

PR #44 adds a dedicated bounded read path using:

```text
hcom events --full --type message
```

It preserves structured correlation evidence:

- event ID;
- timestamp;
- provider instance;
- sender;
- `delivered_to`;
- optional `mentions`;
- optional `intent`;
- optional `thread`;
- optional `reply_to`;
- optional `reply_to_local`.

Optional fields preserve explicit presence/absence instead of inventing defaults.

Message bodies are excluded from the lineage projection.

Capability semantics:

- no returned message rows -> capability remains `UNKNOWN`;
- valid message metadata -> core lineage support is `SUPPORTED`;
- optional field support is reported only when actually observed.

No runtime decision trusts an hcom version string alone.

### 8. Provider-local message relationships — PR #45

PR #45: `Add exact hcom message relationship projection`

Head: `803db6e404a7a5256acda1c4b90648afb8e17933`

Last verified full Runtime CI: **passed** (`#196`).

This builds exact provider-local communication relationships from #44 metadata.

Rules:

- only explicit `reply_to_local` creates a reply edge;
- same-thread membership does not imply a reply;
- exact `delivered_to` creates delivery edges;
- requests require explicit `intent=request`;
- acknowledgements require exact reply linkage plus `intent=ack`;
- reply parent outside the bounded input is `PARENT_NOT_IN_INPUT`;
- absence of a reply/ack in the bounded input is `NOT_OBSERVED_IN_INPUT`.

It deliberately does **not** infer:

- pending/waiting state;
- task/run attribution;
- human intent;
- authority or approval.

This decomposes future A4 into:

```text
A4a full-fidelity hcom read              -> #44 COMPLETE
A4b provider-local message relationships -> #45 COMPLETE
A4c task/run <-> communication join       -> waits for A1
A4d explainable waits                     -> waits for trustworthy A4c coverage
```

## Owner-side adversarial hardening pass

Before handing these branches to later independent review, a separate owner-side pass was performed over #41–#45.

Concrete fixes made:

- #41: UNKNOWN cannot conceal evidence/drift; substitute credit must be explicitly gated;
- #42: count metrics cannot be fractional;
- #43: lesson schema fails closed on unknown/missing top-level fields.

No additional safe defect was found in the bounded #44/#45 communication semantics during that pass.

This owner-side pass is **not independent review** and should not be treated as approval.

## What is now unblocked vs still blocked

### Already prepared

- execution-lineage architecture;
- Context Builder evidence-integrity corpus;
- Stage-1 evidence projector/scorer;
- Layer 2/3 benchmark protocol;
- benchmark result validation;
- guidance-only operational-learning projection;
- full-fidelity hcom communication read;
- exact provider-local request/reply/thread/delivery projection.

### Remaining Wave 1 dependency

PR #24 remains open.

Its current important limitation is also the reason durable lineage matters: current `run_manifests` can carry a bare provider-local `session_id`, but provider-neutral exact identity also needs adapter qualification. The guard correctly fails closed when the adapter-qualified durable relationship is unproven.

That is the direct bridge into A1.

## Recommended continuation

When work resumes:

1. re-read root `AGENTS.md`;
2. recheck current `main` and PR heads — do not trust the hashes in this note if branches moved;
3. inspect #24 review state and final accepted interface;
4. if #24 is accepted/merged, perform a fresh A0 interface preflight against current main;
5. implement **A1 execution-lineage session binding** on a new branch/PR;
6. teach the canonical guard to resolve accepted adapter-qualified session lineage rather than relying on bare `run_manifests.session_id`;
7. then continue A2 helper/recovery lineage;
8. A3 exact submission-attempt lineage;
9. A4c task/run communication join using #44/#45 evidence;
10. only then derive A4d explainable waits;
11. keep A5 operation trajectory deferred until evaluation proves it is needed.

## A1 implementation constraints

A1 should preserve these rules:

- append-only extension of immutable run manifests;
- exact run/worker/project/session correlation;
- adapter-qualified provider identity;
- no task ownership or permission inferred from session liveness;
- no heuristic backfill from timestamps, names, message text, or “only one run” assumptions;
- legacy/no-link evidence remains `UNKNOWN`;
- session replacement must not branch ambiguously;
- different worker or materially changed run contract => new run, not mutation of old run identity;
- trace and Run Record remain derived/read-only projections;
- no hcom message-body mirroring;
- no permanent supervisor/blackboard architecture.

## Active open PRs created/advanced in this lane

| PR | Purpose | Current head at note time |
|---|---|---|
| #38 | execution-lineage design | `bbb300e8ad55e70b81e54529310db3484f6aadc2` |
| #39 | Context Builder evidence-integrity corpus | `57b42557af1db2d7d23849766b0841c3a0395460` |
| #40 | Layer 2/3 end-to-end benchmark protocol | `85ca58db52c81dd250b89316ecbc54785aeb9e18` |
| #41 | evidence projector/scorer | `c997821c4a5f3d11c2bc7f8a98dd7a33750c3feb` |
| #42 | benchmark result validator | `beeef987e25509136ff3de5b79263c984cc501da` |
| #43 | operational-learning projection | `aeecf1b5775db1d5ac2484819620f476752f3654` |
| #44 | full-fidelity hcom lineage read | `4e10f8dadcd64e7b91fb8d608b92f268fde00821` |
| #45 | exact hcom message relationships | `803db6e404a7a5256acda1c4b90648afb8e17933` |

Treat all open-PR interfaces as prospective until independently reviewed/accepted.

## Short version

The parallel lane successfully moved the project from “we still need to design several major capabilities” to “most surrounding evidence, evaluation, learning, and communication primitives are prepared.”

The central missing structural piece is now durable execution lineage itself.

Once the final Wave 1 security interface is accepted, the next high-value implementation should be:

```text
adapter-qualified run/session lineage
  -> helper/recovery lineage
  -> submission lineage
  -> task/run communication join
  -> explainable waits
```

Everything above remains subordinate to canonical task/policy/operator authority and the one-fact/one-authority rule.
