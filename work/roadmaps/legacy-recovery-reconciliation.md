# Legacy recovery reconciliation map

Status: `PLANNING / RECONCILIATION — NOT ACTIVE AUTHORITY`

Last reconciled: `2026-08-15`

Purpose: connect the mechanisms and lessons recovered from legacy MAPS to the current MAPS Lean program so useful discoveries are neither lost nor blindly rebuilt.

This document is subordinate to `00-MASTER-MAPS-CAPABILITY-ROADMAP.md`. It owns only the **legacy-derived reconciliation view**: what is already merged, what is represented in current draft PRs, what should be next, what is evidence/usage-triggered, what remains historically unresolved, and what should not be revived.

Current behavior and authority remain defined by `AGENTS.md`, canonical task/policy/review state, merged code/tests, accepted task requirements, and explicit operator decisions.

---

# 1. Reconciliation rule

For every legacy mechanism or lesson, use the smallest honest classification:

```text
MERGED
= accepted behavior already exists on current main

IN OPEN PR
= current draft work implements or materially advances the recovered capability

NEXT
= recovered capability remains materially useful and prerequisites are now strong enough to plan the next tranche

TRIGGERED / LATER
= useful but should exist only after a measurable usage/risk/repetition trigger

DO NOT REVIVE
= legacy direction was invalidated, superseded, or conflicts with Lean architecture

AUDIT REMAINS
= historical evidence is incomplete enough that implementation disposition is still UNKNOWN
```

A candidate may be split across classifications. For example, `trace` can be `MERGED` at v1 while communication-complete lineage remains `NEXT`.

Never infer promotion from repeated citation. A legacy proposal, audit note, roadmap entry, or passing benchmark is not runtime authority.

---

# 2. Verified current baseline

At this reconciliation checkpoint:

- `main` is the merged PR #19 baseline (`086e066f723d793273441dd52b500e62ac981deb` when this task started);
- PRs #20-#35 are open draft development;
- review remediation found during the 2026-08-15 pass was fixed on the affected branches and current-head Runtime CI passed;
- those draft PRs still require valid independent review before their behavior can be treated as accepted `main` authority.

Do not trust the SHA/status lines above after time has passed; re-check GitHub before implementation.

---

# 3. Legacy-derived capabilities already merged

These should not be rebuilt as new systems. Future work should extend the accepted Lean mechanism only when a concrete gap exists.

| Recovered lesson/candidate | Current Lean result | Status | Follow-up boundary |
|---|---|---|---|
| Negative operating contract | root `AGENTS.md` prohibitions against overcomplexity, guessing, duplicate truth, silent scope growth, unnecessary permanent agents | `MERGED` | Preserve; do not grow into bureaucracy |
| Risk-specific review lenses | explicit functional/security/privacy/destructive/release/authority review framing | `MERGED` | Measure review quality before adding mandatory reviewer count |
| Telemetry/event secret-safety boundary | secret-safer event/diagnostic handling with explicit redaction markers | `MERGED` foundation | Re-audit each new durable telemetry surface |
| Outcome feedback | append-only SUCCESS/PARTIAL/FAILURE/UNKNOWN post-completion observations with provenance | `MERGED` foundation | Use for later incident/eval metrics; never rewrite historical task truth |
| Context Builder | explicit-first disposable context plan with exact file hashes and missing/outside boundaries | `MERGED` v1 | Exact evidence-card/retrieval refinement remains separate |
| Operator status surface | small read-only `status` view over canonical state | `MERGED` v1 | Wait/helper/lineage enrichments must remain derived |
| Task trace | secret-safer read-only trace over canonical task/review/policy/run/context/criterion/outcome evidence | `MERGED` v1 | External communication/helper/recovery correlation remains incomplete |
| PR Runtime CI | normal PR-triggered validation of runtime stack | `MERGED` | Green CI is evidence, not independent approval |
| Atomic review claiming / durable authorship / continuity-aware independence | current review lifecycle already mechanically protects these properties | `MERGED / SOLVED` | Preserve as regression invariant |
| RnS suppression of invalid/terminal recovery | current recovery already respects canonical task/claim reality | `MERGED / SOLVED` | Preserve as regression invariant |
| One-fact/one-authority rule | active operating/architecture invariant | `MERGED / SOLVED` | New subsystems must derive or reference rather than duplicate |

---

# 4. Legacy-derived work represented by current open PRs

These are **implementation evidence in progress**, not accepted authority until independently reviewed/merged.

## 4.1 Harness, lifecycle and authority enforcement — PRs #20-#24

Recovered legacy/Prime problems addressed:

- provider-specific lifecycle behavior;
- ambiguous worker/session terminology;
- session liveness being mistaken for task truth;
- authority checks depending on agent memory;
- stale recovery/session continuation;
- adversarial authority/identity manipulation.

Current draft sequence:

```text
#20 provider-neutral harness types/protocol
  ↓
#21 hcom normalization + deterministic Hook registry
  ↓
#22 HarnessService execution surface
  ↓
#23 canonical run/task guard before consequential harness operations
  ↓
#24 executable agentic-security/adversarial baseline
```

Reconciliation status: `IN OPEN PR`.

Still not solved by this stack:

- complete durable task → run → provider session → helper → recovery/replacement lineage;
- communication-complete replay/trace;
- explainable waits;
- broad ACI normalization for every tool surface;
- general immediate post-mutation validation coverage.

Those belong in later focused tranches, not scope creep into #20-#24.

## 4.2 Procedural knowledge / Skills — PRs #25-#27 and #31

Recovered problems addressed:

- reusable expertise being encoded as persona-heavy permanent agents;
- procedural content lacking provenance;
- unsafe imported instructions/scripts;
- lexical/vocabulary-sensitive routing claims being accepted without frozen evaluation.

Current draft sequence:

```text
#25 Agent Skills format/discovery foundation
  ↓
#26 provenance-aware derived Skill catalog
  ↓
#27 frozen Skill selection evaluation corpus
  ↓
#31 static Skill quality/security gate
```

Reconciliation status: `IN OPEN PR`.

Still not solved:

- reviewed Skill trust/promotion/retirement lifecycle;
- persistent quarantine workflow if it proves necessary;
- Context Builder integration;
- production Skill selection/routing;
- behavioral sandbox/evaluation of executable Skill resources;
- capability intersection when a Skill requests tools/network/credentials.

No `CLEAR` static scan may become automatic trust or production activation.

## 4.3 Environment and reproducibility — PRs #28-#30

Recovered problems addressed:

- model/agent failure being confused with environment drift;
- recovery occurring without explicit environment compatibility evidence;
- reproducibility relying on implied host assumptions.

Current draft sequence:

```text
#28 EnvironmentSpec v1
  ↓
#29 local EnvironmentFingerprint + compatibility
  ↓
#30 append-only environment evidence bound to runs
```

Reconciliation status: `IN OPEN PR`.

Still not solved:

- recovery decisions that consume compatibility evidence safely;
- environment-declared validation execution;
- worktree/container/remote environment implementation;
- snapshots/rehydration;
- credential brokering.

Environment compatibility remains evidence, not task authority.

## 4.4 Review-time evidence freshness — PR #32

Recovered problem addressed:

- submission-time evidence becoming stale before consequential review;
- reviewers approving a different revision/evidence set than the one claimed.

Current draft:

- immutable review subjects;
- exact task/submission/revision binding;
- immutable artifact/evidence refs;
- revision-bound or re-derived freshness modes.

Reconciliation status: `IN OPEN PR`.

Still not solved:

- user-visible release/acquisition-path verification as a general system;
- broader artifact registry (not automatically desirable).

Do not add an artifact registry merely for convenience unless repeated need demonstrates it.

## 4.5 Run Records, incident freezing and comparative evaluation — PRs #33-#35

Recovered problems addressed:

- no portable black-box-style execution evidence;
- incidents remaining anecdotes rather than regression cases;
- candidate harness changes being judged without a frozen baseline;
- evaluation success being able to drift toward implicit promotion authority.

Current draft sequence:

```text
#33 portable Run Record v1
  ↓
#34 frozen regression case v1 + recovered incident taxonomy
  ↓
#35 deterministic baseline-vs-candidate comparative evaluator
```

Reconciliation status: `IN OPEN PR`.

Preserved promotion path:

```text
frozen cases
→ candidate results
→ comparative report
→ proposal
→ independent review/operator gate where required
→ promotion
```

Never:

```text
better score → automatic production change
```

Still not solved:

- complete operation/session/helper/recovery trajectories;
- production incident sampling/triage into cases;
- Layer 2 qualitative agent-quality evaluation;
- Layer 3 real-world outcome comparison;
- proposal/promotion lifecycle;
- operational lesson lifecycle.

---

# 5. What should come next

The next work should close evidence/lineage gaps **before** adding broader autonomy or self-refinement.

## NEXT A — Explicit execution lineage and communication coverage

Priority: `NEXT / P1` after relevant harness branches are accepted or their final interfaces are known.

Problem:

Current evidence can identify task/run facts, but full reconstruction still cannot reliably answer which provider session/helper/recovery replacement produced each action without gaps.

Smallest target:

```text
task
→ immutable run
→ worker
→ provider session binding
→ helper/child invocation
→ recovery/replacement link
→ operation/evidence refs
→ submission
```

Requirements:

- reuse canonical run/task/session/helper sources; no second authority database;
- explicit stable identifiers rather than timestamp/name inference;
- late attachment/replacement needs explicit reconciliation semantics;
- Run Record/trace must state `MISSING`/`UNKNOWN` coverage honestly;
- communication coverage must say which source was queried and whether attribution is complete.

Unlocks:

- trustworthy explainable waits;
- stronger replay/Run Records;
- safe recovery compatibility;
- helper NO_PROGRESS evidence;
- better Layer 3 evaluation.

## NEXT B — Explainable waits as a derived projection

Priority: `NEXT/P2` once authoritative request/addressee/thread/session correlation exists.

Target:

```text
what is waiting
who/what it is waiting on
source request/thread/message ID
request time
known resume condition
UNKNOWN where not derivable
```

Do not create a new wait authority plane or infer human intent from arbitrary message prose.

## NEXT C — Context Builder v2 evidence integrity

Priority: `NEXT/P2`, evaluation-first.

Preserve from legacy:

- exact Markdown section/code-symbol anchors;
- source hashes/watermarks;
- temporal/historical attribution;
- proof role;
- positive evidence and negative boundaries separately;
- source-drift reporting;
- frozen holdouts;
- paraphrase/vocabulary-shift cases;
- abstention/no-answer quality.

Start with evidence-card **integrity**, not another retrieval algorithm.

The legacy lexical claim-card retriever is explicitly not the solution; see `DO NOT REVIVE` below.

## NEXT D — Complete the three-layer evaluation discipline

Priority: `NEXT/P2` after #33-#35 foundation is accepted.

Layer 1 is becoming strong through tests/frozen mechanical cases.

Still needed:

```text
Layer 2 — agent-quality regression
- implementation quality
- review quality
- context sufficiency
- Skill procedure quality
- recovery decision quality

Layer 3 — production/outcome sampling
- escaped defects
- rework
- operator-friction interventions
- recovery success
- duplicate work
- environment drift failures
- cost/runtime only when measured reliably
```

A major future benchmark should exercise an end-to-end MAPS scenario:

```text
orientation
→ safe first action
→ execution/delegation
→ interruption/recovery
→ independent review
→ completion/release
→ post-completion outcome
```

No single metric/layer proves the system improved.

## NEXT E — Controlled operational-learning lifecycle

Priority: `NEXT AFTER EVALUATION FOUNDATION`, not before.

Recovered target:

```text
operational observation/outcome
→ candidate lesson
→ evidence/provenance
→ independent review/promotion
→ scoped active guidance
→ expiry/review-at
→ supersession/retirement
```

Required fields should include provenance, applicability/trigger, promotion authority, start, expiry/review date, supersession, and status.

Hard boundaries:

- observation is not policy;
- candidate lesson is not active guidance;
- temporary workarounds must expire;
- superseded guidance must stop projecting into startup/context;
- do not create a second policy database in disguise.

---

# 6. Triggered / later work

These capabilities remain useful options, but building them now would violate Lean's evidence/repetition/usage rules.

| Candidate | Trigger before implementation | Initial boundary |
|---|---|---|
| Git worktree isolation | concurrent writable agents become common or collisions are observed | one writable run → one attributable worktree; explicit integration/cleanup |
| Helper continuity | repeated same-task specialist reuse saves meaningful setup/context | task-scoped, TTL-bound, invalidated by incompatible revision/context |
| Helper `NO_PROGRESS` | real alive-but-stuck cases recur enough to measure | advisory only; no auto-kill |
| Deterministic `maps flow` | a lifecycle sequence is repeated, stable and well understood | fixed guarded sequence, not another workflow engine |
| Capability Packs | repeated Skill+tools+hooks+environment combinations become stable | packaging only; does not grant authority |
| Credential broker | remote/external execution needs secrets often enough for ad-hoc injection to become material risk | short-lived capability grants after canonical policy/scope checks |
| Sandboxes/containers/remote compute | reproducibility/isolation/resource-control need exceeds complexity cost | satisfy EnvironmentSpec; compute remains disposable |
| Snapshots/rehydration | environment startup/recovery cost justifies durable reconstruction | task truth remains outside snapshot |
| Time-travel/fork debugging | Run Records/transition semantics become complete enough to replay honestly | partial replay must remain explicitly partial |
| Semantic retrieval/query expansion | frozen paraphrase/hard-negative/no-answer eval beats explicit-first Context Builder materially | never promote because embeddings are fashionable |
| Thin Mission object | project/task dependencies demonstrably fail to represent multi-task intent | grouping/intent only; tasks remain execution authority |
| Scoped temporary halt delegation | concrete safety case requires bounded non-operator halt authority | disabled by default; explicit scope/grantor/expiry/reason |

---

# 7. Bounded audits, not permanent agents

Two recovered legacy mechanisms are worth keeping as **procedures**, not standing autonomous roles.

## 7.1 Phase-boundary discovery

Use after major phases/releases when useful:

- proposal-only;
- evidence-linked;
- distinguish fact/inference/proposal;
- check existing records before claiming novelty;
- no idea quota;
- no automatic implementation.

## 7.2 System-adherence audit

Use periodically after substantial infrastructure changes to ask:

```text
Was it built as intended?
Is it cross-linked coherently?
Is production work actually using it?
Is a documented mechanism silently bypassed?
```

Findings enter normal task/review channels. The auditor does not silently repair or become process authority.

The parallel legacy-archaeology agent is an example of a bounded pass, not a proposal for a permanent archaeology/discovery worker.

---

# 8. Design/review invariants recovered from legacy

These do not need a dedicated subsystem unless repeated failure proves one necessary.

## 8.1 Authority provenance

Citation does not ratify a proposal. Anything used as a consequential gate needs explicit decision/approval provenance.

## 8.2 Source-of-truth reconciliation

When one fact has multiple readers/copies, require one of:

1. one declared authority;
2. atomic mutation;
3. mechanical reconciliation/cross-check of derived views.

Review question:

> Who else reads this state, and which copy wins?

## 8.3 Durable state reachability

For every new durable state/field, define:

```text
how entered
how exited
how corrected
what happens after interruption/owner loss/session loss
how superseded/retired
```

## 8.4 Security/authority tests should assert behavior

Prefer executed/computed behavioral properties in isolation. Do not rely on source-string spelling unless the text itself is the property.

## 8.5 Review policy changes require measurement

Do not weaken or strengthen independent review because of hypothetical validators or intuition. Use review-catch rate, escaped defects, rework, intervention, and validator-quality evidence.

## 8.6 Precondition ordering should become deterministic only when real

If a repeated process genuinely requires A before B, make the ordering mechanically visible. Do not add ceremony for dependencies Lean has already eliminated.

---

# 9. Do not revive

These directions are explicitly excluded absent new evidence strong enough to reopen architecture review.

## 9.1 Legacy lexical claim-card retriever

Legacy `EXP-0006` ended `REVISE` and did not validate the old lexical retrieval implementation. Preserve exact anchors, hashes, drift reporting, temporal attribution, explicit negatives, frozen holdouts and blind scoring—not the retriever.

## 9.2 Permanent discovery/process-police agents

Bounded discovery/adherence audits were useful. Continuous watcher roles are not justified.

## 9.3 Second task/session/review/policy authority store

Rejected. New mechanisms must reference/derive from existing canonical facts or explicitly reconcile them.

## 9.4 Large persistent `mapd`/Prime supervisor

Rejected by default. Provider-neutral harness mechanisms live below canonical task/policy authority.

## 9.5 Fixed permanent personality roster

Rejected as system architecture. Select workers/capabilities for tasks; procedures belong in Skills.

## 9.6 Giant knowledge graph/library by default

Rejected without a narrow measured retrieval/evidence problem.

## 9.7 Universal container/microVM per worker

Rejected until a threat/reproducibility requirement justifies the cost.

## 9.8 Automatic self-refinement/promotion

Rejected absolutely for policy/authority/safety/routing/persistent guidance changes.

```text
measurement → proposal
not
measurement → authority
```

---

# 10. Historical audit work still open

The legacy audit explicitly does **not** claim every legacy file/task was deep-read.

A parallel non-conflicting archaeology pass should continue to inspect:

1. unresolved MAP-relevant Insights/Syntheses marked RAW/OPEN/CANDIDATE/PARKED;
2. ambiguous/incomplete promotions and whether downstream tasks actually shipped;
3. RETIRED/abandoned MAP-system task chains for lost versus superseded behavior;
4. referenced research/planning/artifacts only when they support an unresolved reusable MAPS claim.

Every new result must resolve to one of:

```text
RECOVER AS CANDIDATE
FOLD INTO EXISTING CANDIDATE
ALREADY SOLVED IN LEAN
HISTORICAL / DO NOT REVIVE
```

Until that bounded pass reports, unknown historical items remain `AUDIT REMAINS`; they do not block the already-evidenced next steps unless they reveal a material conflicting invariant.

---

# 11. Recommended implementation order from here

Assuming current open PR interfaces survive independent review materially intact:

```text
A. review/merge or explicitly reshape current #20-#35 stacks
        ↓
B. explicit run/session/helper/recovery + communication lineage
        ↓
C. derived explainable waits / fuller trace + Run Record coverage
        ↓
D. Context Builder v2 evidence-integrity experiment
        ↓
E. complete Layer 2 + Layer 3 evaluation and end-to-end benchmark
        ↓
F. controlled operational-learning lifecycle
        ↓
G. candidate harness improvements only through frozen comparison + review
```

Triggered scaling tracks (worktrees, persistent helpers, snapshots, credentials, capability packs, deterministic flows) branch off only when their own activation evidence exists.

This ordering deliberately puts **truth/evidence before autonomy**.

---

# 12. Definition of legacy-recovery completion

Legacy idea recovery is complete enough to stop active archaeology when all of the following are true:

- [ ] major idea-bearing legacy collections have been reconciled to a durable classification;
- [ ] unresolved MAP-relevant chains are either classified or explicitly `UNKNOWN` with a reason;
- [ ] every surviving candidate is represented in this reconciliation map or explicitly folded into the master/detailed capability roadmaps;
- [ ] already-solved behavior is marked so later agents do not rebuild it;
- [ ] rejected/failed historical directions are named so they are not accidentally resurrected;
- [ ] remaining implementation work has evidence/usage/repetition triggers and prerequisite order;
- [ ] deletion/preservation of the top-level legacy tree remains a separate explicit operator decision and is not implied by roadmap completion.

When the parallel archaeology report lands, reconcile only genuinely new evidence into this map and the master roadmap. Do not restart the entire audit from chat history.
