# Legacy Knowledge & Implementation Audit

Status: `ACTIVE MIGRATION RECORD`

Purpose: mine `legacy/` before it is removed, preserve behavior and lessons that
still matter to MAPS Lean, and explicitly reject historical complexity that no
longer earns its cost.

This document is an audit of the legacy MAP material, not a declaration that
all legacy behavior should return.

## Audit rule

Preserve **invariants, evidence, tests, and useful implementation techniques**.
Do not preserve a subsystem merely because it existed.

Use this decision order:

```text
What problem did this solve?
        ↓
Was the problem real or hypothetical?
        ↓
Is there incident/test/measurement evidence?
        ↓
Does Lean already solve it?
        ↓
If not, what is the smallest behavior worth preserving?
```

## Coverage model

The legacy repository contains unique design/code as well as very large stores
of generated historical state. Those require different kinds of review.

### `DEEP_READ`

Content was inspected for its rules, behavior, failure modes, and relationship
to Lean. This includes the root system documents, the active operating rules,
major runtime components, important notes, representative repairs/retros,
important audits/experiments, and the control-plane/migration code.

### `INVENTORIED_AND_TEST_MAPPED`

The full directory/file set was inventoried and implementations were matched to
regression tests/specs. Individual files were deep-read where they exposed a
unique invariant or behavior not already understood.

This applies especially to the large `scripts/` and `tests/` trees.

### `DATASET_CLASSIFIED`

Large generated or historical datasets were treated as evidence corpora, not
as unique specifications. They were not misleadingly described as
line-by-line semantic reads.

Examples:

- hundreds of historical `tasks/TASK-*.json` records;
- the multi-megabyte `events/events.jsonl` history;
- historical handoffs and state snapshots;
- old inbox/helper conversations;
- old review/release artifacts;
- emergence records and experiment datasets.

Their useful lessons were recovered through validators, tests, repairs,
retrospectives, audits, measurements, and representative examples.

### `PRESENTATION_ONLY_CLASSIFIED`

Old Command Center, Mission Control, WezTerm, desktop launcher, tab, screenshot,
and fixed-roster material was inspected enough to determine whether it carried
unique authority/runtime behavior. Presentation assumptions are not being
promoted. Useful content contracts are recorded separately below.

## Executive findings

The legacy system contains substantial useful engineering. It also contains
substantial accidental complexity caused by multiple mutable mirrors, fixed
agent/window assumptions, historical UI machinery, and systems that were built
before their value was measured.

The strongest reusable ideas are not the old cockpit. They are the rules that
made independent agents safe and recoverable:

1. **Context packet, not context dump.**
2. **Capability, assignment, ownership, authority, and approval are different.**
3. **A rule that has no durable field and no check is not enforceable.**
4. **Checks must run at the transition they protect.**
5. **Use deterministic validation for structure; use independent judgment for substance.**
6. **Return explicit failure reasons; do not flatten distinct failures into one Boolean.**
7. **Review is risk-calibrated, but meaningful work retains independent challenge.**
8. **Network/write-capable work gets a separate security question from functional correctness.**
9. **Repeated failure becomes a validator, template/default, test, or decision.**
10. **Derived state is rebuildable and never authority.**
11. **Authoritative contradictions are surfaced and frozen; agents do not silently choose a winner.**
12. **Research distinguishes evidence, source quality, recency, assumptions, and unknowns.**
13. **Broad human intent must be shaped before it becomes executable task authority.**
14. **Session continuity transfers frozen obligations, not new authority.**
15. **Helpers remain bounded; one core owner integrates their work.**
16. **Shared/repo-global mutations need real concurrency protection.**
17. **Safe migrations are additive, validated, checkpointed, and reversible where possible.**
18. **Agent-grade readiness should be frozen again at run time when the exact task/context/scope matters.**
19. **An implementer's completion claim is not the same thing as independent verification.**
20. **Reviewer independence is semantic; a rotated continuation of the author is not automatically independent.**
21. **Negative experiment results are project knowledge and should prevent repeated dead ends.**
22. **Measure escaped defects and validator blind spots, not only activity or throughput.**

## What the evidence says was genuinely useful

### Atomic coordination

Legacy repeatedly experienced ID-allocation and state-race problems. The repair
history includes duplicate/colliding record IDs, and real concurrency testing
showed unlocked allocation failures. The later robustness audit concluded that
atomicity/idempotency was the best real-evidenced part of the architecture.

**Lean consequence:** preserve guarded SQLite transitions, leases, atomic claim
semantics, and real repo-global locking where a database transaction does not
own the resource.

Do not preserve a lock implementation merely because it is named `lock`; a
lock must itself be atomic and tested.

### Independent review

Real measurements found that 36 of 156 submitted tasks (23.1%) received
`CHANGES_REQUESTED` and recovered before release. This is material evidence
that review was doing useful defect-catching work in the measured system.

A separate security-framed review also caught a real CSRF issue after the
functional review had passed.

**Lean consequence:** do not remove independent review on the theory that a
future validator will replace it. Reduce review weight for low-risk work, but
weaken gates only after replacement verification is real and measured.

### Strict readiness

Legacy's state-machine work identified that allowing incomplete LLM-authored
records to look executable caused downstream failures. The resulting
promotion/claim gates are the direct predecessor of Lean's AGI readiness rule.

**Lean consequence:** `READY` remains a hard execution contract, not a casual
status.

### Context engineering

Legacy explicitly developed `Required`, `Optional (trigger-gated)`, and
`Excluded` context packets. A frozen orientation-manifest experiment retained
all required facts/boundaries while reducing a 44,432-byte full control to a
2,619-byte treatment (about 94% smaller).

**Lean consequence:** context packets are evidence-backed. Agents should load
the smallest sufficient context and follow pointers only when triggered.

### Recovery and rotation

The mature RnS work discovered that provider-limit sessions can stop without a
final turn, that hcom status can become stale, and that resume attempts need
bounded backoff. Context rotation developed a stronger continuity invariant:

```text
checkpoint → verify → resume → supersede
```

Never clear first and reconstruct later.

**Lean consequence:** preserve recovery detection/backoff and frozen handoff
integrity. Remove the mandatory WezTerm terminal destination.

### Durable but separate communication

hcom was useful as cross-provider/session transport. Legacy correctly learned
that hcom's SQLite data is communication/session evidence, not MAP task truth.
Important conversation outcomes were promoted into durable task/decision/
review/handoff state.

**Lean consequence:** retain hcom behind an adapter, but never let message
presence or transport state grant task authority.

### Outcome feedback

Legacy eventually started measuring whether validators/reviews failed to catch
problems that later escaped. The metric design distinguishes validator blind
spots, review blind spots, stale context, requirement gaps, integration gaps,
operator mismatch, and external change.

**Lean consequence:** later runtime metrics should measure quality of the
control system, especially escaped defects, rather than optimize for number of
tasks/messages/artifacts.

## High-value rules to merge into active Lean

### 1. AGI context contract

For consequential work, the context side of AGI should support:

```text
Required
Optional — with explicit trigger
Excluded — when an agent might reasonably assume it should be loaded
Staleness/conflict check
```

This does not mean every small task needs a separate context file. The fields
may live directly in the task.

### 2. AGI-to-run binding

AGI answers whether a task is ready. A **run manifest** answers exactly what a
specific worker received.

Useful legacy fields:

- task revision/hash;
- worker/session identity;
- readable/writable/forbidden paths;
- context references plus hashes;
- permitted skills/tools when material;
- base revision;
- runtime/attempt limits.

This is valuable for long, high-risk, multi-agent, or resumable execution. It
should not become mandatory ceremony for tiny local edits.

### 3. Typed failures

A claim/review/routing API should distinguish conditions such as:

```text
already_claimed
not_ready
missing_acceptance_criteria
self_review
policy_rejected
approval_required
dependency_blocked
stale_contract
```

Do not return one generic `False` when callers need different recovery paths.

### 4. Semantic reviewer independence

Independent review must account for continuity lineage. A replacement session
that inherited the author's exact context/claims through rotation is a
continuation holder, not automatically an independent reviewer because its
agent ID changed.

### 5. Criterion-level evidence where warranted

For higher-risk tasks, preserve the distinction:

```text
implementer claim
  criterion X = complete
  evidence = ...

reviewer verdict
  criterion X = confirmed / rejected
```

The review record should not mutate or rewrite the implementer's original
claim. This makes disagreements auditable.

### 6. Conflict freeze

When current authoritative sources materially disagree about scope, ownership,
state, decision, or a load-bearing fact:

- record the conflict;
- block only affected work;
- identify the decision/evidence needed;
- resume after explicit resolution.

Do not let an agent choose whichever source seems most plausible.

### 7. Diagnostics are not repairs

A validator/health check may report drift. It should not thereby acquire
permission to rewrite policy, intent, ownership, or architecture.

```text
detect → classify → repair mechanically OR propose/escalate → verify
```

### 8. Risk-tiered process weight

Legacy learned that heavyweight release ceremony on every low-risk change
created large queues/artifact volume. Keep the important gate, but scale the
proof/review/release mechanism to actual risk.

### 9. Security as a distinct review dimension

When work crosses repo/machine/network trust boundaries, handles secrets,
changes permissions, or adds a write-capable external surface, ask security
questions separately from ordinary functional acceptance.

### 10. Learning promotion

Repeated failures should be converted into the smallest durable behavior
change. A useful promotion ladder is:

```text
incident evidence
→ reusable lesson
→ validator/test/template/default/decision if needed
→ scoped startup/context rule only if recurrence justifies it
```

Do not load the entire incident archive into every future session.

## Useful code or test behavior not fully captured by PR #7

The first extraction preserved the obvious control plane. This audit identified
a second set whose **source/test behavior should survive legacy deletion**:

- `scripts/run_manifest.py` + run/scope tests;
- `scripts/submission_records.py` + criterion evidence tests;
- `scripts/review_routing.py` + continuity-aware reviewer tests;
- `scripts/session_replay.py` + read-model design/tests;
- `scripts/intake_request.py` + intake/decomposer tests, as rewrite reference;
- deterministic context/decision/event/research/review validators and tests;
- `scripts/flag_conflict.py`, as behavior reference only;
- `scripts/git_operation_lock.py` + test/formal invariant, as rewrite reference;
- `scripts/cost_governance.py` + tests, as optional future safety reference;
- the Context Packet template;
- selected audits/experiments proving context compression, review value,
  concurrency invariants, threat boundaries, and rejected architecture ideas.

These files are preserved as migration source. Active Lean code must not import
from the migration snapshots.

## Useful knowledge already absorbed by Lean

The following legacy ideas are already substantially represented in active Lean
and should not be reintroduced as separate systems:

- human/operator consequential authority;
- one accountable task owner;
- owner != independent reviewer;
- output paths as prospective write boundaries;
- task shaping before execution;
- AGI `READY` gate;
- `VERIFIED / REPORTED / ASSUMED / UNKNOWN`;
- explicit dependencies, verification, evidence, review, and escalation;
- project bootstrap from current reality → DONE → backward plan → working plan;
- checkpoints and re-planning;
- bounded helpers;
- model capability vs authority separation;
- SQLite/LangGraph/hcom responsibility separation;
- repair severity and repeat-failure learning;
- durable handoffs;
- no WezTerm authority.

Do not duplicate these into additional root-level policy files.

## Valuable ideas that should remain optional or experimental

### Full Library / Librarian layer

Legacy measured high compression but low steady-state churn and an unmeasured
`detail-needed` rate. Its robustness report concluded the full Library layer
was **not justified for the measured corpus yet**.

Keep simple links/indexes if useful. Do not revive a large summarization/library
subsystem without new evidence.

### Task fingerprint / memory retrieval systems

The retrieval work was serious and had holdout tests, but at least one local
packet-verifier experiment explicitly concluded that its packet format was not
viable at acceptable recall/precision/source visibility.

Preserve the negative result and evaluation method. Do not promote the old
experimental code into production merely because it exists.

### Continuous model-backed discovery

A later philosophical re-evaluation explicitly rejected a continuous paid/model
scout. Model-backed discovery should be bounded and event-triggered by a real
decision/phase/anomaly, with useful-new yield measured.

### Cost governance

Useful when MAPS begins assigning paid work autonomously at enough scale that a
budget/circuit breaker solves a real problem. It is not required for AGI or a
small local deployment.

### Formal methods

The useful recommendation was narrow: model only safety-critical concurrency
invariants such as unique IDs, single claims, and real mutual exclusion. Start
with executable state-machine/property tests; use TLA+ only when the risk and
concurrency justify it.

## What should not be promoted

### Fixed roster / permanent agent identities

Old named lab sessions and permanent role bindings are historical runtime
state. Provider/model/session identity does not confer authority.

### WezTerm cockpit assumptions

Tabs, panes, desktop launchers, fixed startup layouts, and WezTerm-specific
resume destinations are presentation choices, not MAPS architecture.

### CommandCenterUI implementation

The old UI code is not being promoted. The useful content contract survives:
show status, owner, blockers, decisions, review queue, risks, recovery state,
and next useful action from canonical/read-only sources.

### Multiple mutable task mirrors

The old database + per-task JSON + giant task graph produced synchronization
risk. Lean should preserve human inspectability without making several
hand-editable lifecycle stores equally authoritative.

### Historical task/event/inbox state as startup context

History is evidence. It is not default context and does not become authority by
being old or verbose.

### Universal ceremony

Do not recreate a separate subsystem, record type, committee, or checklist for
every historical rule. A rule belongs in the smallest active artifact and gate
that actually changes behavior.

## Directory-level disposition

| Legacy area | Audit disposition |
|---|---|
| Root `*_SYSTEM.md` / authority docs | `DEEP_READ`; merge useful rules into Lean; do not preserve as parallel policy stack. |
| `db/` | `DEEP_READ`; first extraction preserved core source; promote behavior/tests. |
| `graph/` | `DEEP_READ`; preserve routing behavior, remove old roster/UI coupling. |
| `migration/` | `DEEP_READ`; preserve proven schema/migration knowledge. |
| `scripts/` | `INVENTORIED_AND_TEST_MAPPED`; core + second tranche preserved selectively. |
| `tests/` | `INVENTORIED_AND_TEST_MAPPED`; tests are the strongest evidence for behavior worth keeping. |
| `workflow/` | preserve policy/schema knowledge; do not preserve giant historical task graph as active state. |
| `notes/` | `DEEP_READ` for unique operating guides; merge principles, not whole manual tree. |
| `shared/` | historical/current-state corpus; extract durable decisions/lessons, not runtime values. |
| `artifacts/audits/` | preserve selected measured conclusions/invariants; most remain historical evidence in Git. |
| `artifacts/experiments/` | preserve decisive positive/negative results; do not ship experiment code by default. |
| `artifacts/research/` | representative research workflow/evidence; current vendor facts should be reverified. |
| `repairs/` | mine recurring failure classes; preserve lesson ledger rather than every repair as active context. |
| `retros/` | mine process failures and evidence-backed rules; historical afterward. |
| `events/` | `DATASET_CLASSIFIED`; preserve schema/validator, not the full log as Lean runtime. |
| `tasks/` | `DATASET_CLASSIFIED`; useful benchmark/history, not Lean active task state. |
| `handoffs/` | `DATASET_CLASSIFIED`; preserve handoff/rotation invariants and templates. |
| `inbox/` | `DATASET_CLASSIFIED`; preserve communication promotion rules, not transient conversations. |
| `emergence/` | experimental corpus; preserve useful conclusions, avoid mandatory subsystem. |
| `runtime/` | derived/rebuildable state; never authority. |
| Command Center / Mission Control / WezTerm | `PRESENTATION_ONLY_CLASSIFIED`; do not promote implementation. |
| installers | preserve user-local, dry-run, backup, credential-boundary lessons; rewrite Lean installer. |

## Important negative lessons

Legacy is particularly valuable because it records things MAPS should **not**
repeat:

- Do not build checks that are not invoked at the protected transition.
- Do not use regex/prose inference as the only authority classifier when
  structured fields can exist.
- Do not make a required policy field optional in the artifact schema.
- Do not use ambiguous success/failure booleans for operationally different
  states.
- Do not treat an agent/session rename as independent review.
- Do not use shared mutable files as locks without proving atomic exclusion.
- Do not let test fixtures append to canonical event/state stores.
- Do not build a full knowledge/library layer because compression alone looks
  impressive.
- Do not keep model-backed discovery running merely to create more ideas.
- Do not weaken review based on a hypothetical semantic validator that has not
  demonstrated replacement catch rate.
- Do not delete or compact away the only recoverable handoff before a
  replacement has verified it.
- Do not equate UI visibility, hcom presence, provider identity, or technical
  access with project authority.

## Removal conclusion

The large `legacy/` tree does **not** need to remain permanently once:

1. the migration snapshots contain the unique code/test/evidence selected by
   the promotion ledger;
2. active Lean documents contain the missing behavioral rules;
3. active runtime replacements exist for P0 control-plane behavior or the
   migration snapshot remains intentionally available until they do;
4. no active Lean file requires a live `legacy/` path;
5. the removal checklist passes.

Git history remains historical provenance. Active MAPS should not require
historical archaeology for ordinary execution.
