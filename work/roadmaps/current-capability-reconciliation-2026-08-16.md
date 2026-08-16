# MAPS current capability reconciliation — 2026-08-16

Status: `PLANNING STATUS OVERLAY — NOT ACTIVE AUTHORITY`

Snapshot base: `main@8397cbc2941a706440cabd0ffb93cac4ab1bdf6d`

This is a dated planning read model of accepted and open MAPS capability work. The master, Prime, and detailed capability roadmaps remain design references; live GitHub, merged code/tests, canonical MAPS state, and explicit operator/task authority supersede this file.

Before acting, re-read current `main`, all `work/coordination/agents/*.md`, and the exact target PR/base/head/review/CI.

---

## 1. Status vocabulary

- `ACCEPTED` — merged into `main` at or before this snapshot.
- `OPEN_REPAIR` — a concrete implementation/evidence/scope defect remains.
- `OPEN_REVIEW` — implementation or synchronized integration head exists, but required exact-head independent review is unresolved.
- `OPEN_INTEGRATION` — own layer is clean, but synchronization/integration gates remain.
- `BLOCKED_UPSTREAM` — a required upstream interface is not yet accepted in the needed form.
- `PLANNING_ONLY` — design/research evidence only.
- `EVIDENCE_GATED` — preserved option requiring evidence and normal approval/review before implementation or promotion.
- `TRIGGERED` — implement only after repeated concrete need/risk justifies it.
- `HISTORICAL` — useful context, not current execution state.
- `UNKNOWN` — evidence is insufficient for a stronger claim.

Green CI does not erase semantic blockers. A clean feature-head review does not make an unmerged capability accepted. Synchronization invalidates older review/CI evidence unless the exact integrated state is independently re-established.

---

# 2. Historical baseline corrections

## PR #19 / Prime Phase 0

PR #19 is merged. Prime Phase 0 is therefore a completed historical prerequisite, not an active queue. Do not restart the old draft-PR-19 sequence.

Accepted #19-era foundations include the negative operating contract, risk-specific review lenses, safer evidence/diagnostic boundaries, trace v1, outcomes, Context Builder v1, status v1, and Runtime PR CI.

## Roadmap “future” prose may describe accepted v1 work

Merged code/tests now own the implemented interfaces for Harness v1, Skills foundations, EnvironmentSpec/fingerprint, immutable review-subject binding, Portable Run Record/frozen/comparative evaluation, structured canonical waits, Operator Intent Compiler shaping, and Context Builder evidence-integrity evaluation input.

Roadmaps preserve intent and extension constraints; they are not duplicate runtime truth.

## Planning-only communication/wait designs remain planning-only

PR #51 and #52 remain design evidence. Accepted #59 covers only the safe canonical dependency/review/operator-approval wait subset. Communication-response waits still require exact communication correlation plus explicit response-required/progress-blocking evidence.

---

# 3. Accepted capability baseline

| Capability | State | Accepted boundary |
|---|---|---|
| Lean operating/state/context foundation | `ACCEPTED` | #19; explicit-first context, derived trace/status, no duplicate authority. |
| Provider-neutral Harness contract | `ACCEPTED` | #20. |
| hcom normalization + Hook registry | `ACCEPTED` | #21; Hooks constrain, never grant task authority. |
| HarnessService / call-time correlation | `ACCEPTED` | #22. |
| Canonical run guard | `ACCEPTED` | #23. |
| Mandatory anti-spoof Harness enforcement | `ACCEPTED` | #24. |
| Skills format/catalog/evaluation/static gate | `ACCEPTED` | #25/#26/#27/#31; evidence/procedural packaging, not policy/promotion authority. |
| EnvironmentSpec / fingerprint | `ACCEPTED` | #28/#29; compatibility is evidence, not continuation authority. |
| Consequential immutable review-subject binding | `ACCEPTED` | #32. |
| Portable Run Record / frozen case / comparative evaluator | `ACCEPTED` | #33/#34/#35; incomplete replay remains explicit and promotion stays external. |
| Release/acquisition evidence integrity | `ACCEPTED` | #56. |
| Structured explainable waits — canonical subset | `ACCEPTED` | #59; no scheduler/runnable authority. |
| Operator Intent Compiler request shaping | `ACCEPTED` | #57; shaping does not manufacture consequential authority. |
| Context Builder v2 frozen evidence-integrity foundation | `ACCEPTED` | #39 merged at this snapshot; evaluation truth only, no production retrieval authority. |
| Multi-agent coordination bulletin board | `ACCEPTED` | Collision-avoidance evidence only; live GitHub/canonical state wins. |

These do **not** prove complete replay/lineage, production semantic retrieval, automatic Skill/lesson/routing promotion, recovery authority from environment compatibility, communication-response waits, or autonomous self-refinement.

---

# 4. Open capability stacks and dependency constraints

Arrows mean dependency, not merge priority. SWITCHYARD owns live integration order.

## 4.1 Environment evidence

```text
#28 EnvironmentSpec ACCEPTED
        ↓
#29 EnvironmentFingerprint ACCEPTED
        ↓
#30 run-environment evidence OPEN_REVIEW [synchronized]
```

PR #30 feature repair `7bae6d5758619a391c7551ee4589ea2d80d0a5b8` closed the prior HIGH Run Record defect and received CLEAN IN-LAYER review.

SWITCHYARD has now genuinely synchronized #30 to snapshot main:

- base `main@8397cbc2941a706440cabd0ffb93cac4ab1bdf6d`;
- head `4e158f65a422f14d7d12b2b1b8b0297e9f3ca5d7`;
- Runtime CI #442 / `31965641572`: PASS.

The synchronized head still needs a fresh continuity-independent exact-head review before merge. Therefore #30 is `OPEN_REVIEW`, not accepted.

Preserved semantics: source availability is separate from exact-run evidence presence; empty evidence stays non-VERIFIED; malformed projected evidence fails explicitly; compatibility never grants resume/recovery/execution authority.

## 4.2 Execution lineage

```text
Harness #20–#24 ACCEPTED
        ↓
#48 A1 project/adapter/session lineage OPEN_INTEGRATION
        ↓
#49 A2 helper/recovery lineage OPEN_INTEGRATION after accepted A1
        ↓
#50 A3 submission-attempt/run lineage BLOCKED_UPSTREAM + OPEN_REPAIR
```

### #48 A1

Feature head `2f23959afff9525beada28993bad536878310b7f`, Runtime CI #392 PASS, SENTINEL CLEAN IN-LAYER.

Closed defects:
- durable identity is project-scoped `(project_id, adapter_id, session_id)`, not falsely global;
- SQLite rejects runtime-equivalent whitespace/normalization aliases.

State remains `OPEN_INTEGRATION` on historical ancestry; SWITCHYARD must synchronize, preserve accepted schema/state/runtime, run fresh CI, and obtain integrated-head review.

### #49 A2

Head `ed865be729cf2d15663258fd46c9296ea32d28e7`. Independent review found no A2-specific semantic blocker on its historical A1 base.

It overlaps schema/store/trace and must be genuinely rebuilt on accepted #48 rather than retargeted. It is not ready to integrate before #48, but no separate repair is currently known.

### #50 A3

Actual branch head `832fa4ab2c3e97a8f7cdc22a73baca0d276adfc0` remains blocked by #48/#49 and has two A3-specific defects:

1. omitted attribution is represented only by row absence, allowing an old UNKNOWN attempt to be retroactively changed into EXPLICIT attribution; new A3-era submissions must atomically record immutable `UNKNOWN` or `EXPLICIT` attribution;
2. active-runtime `legacy/` wording trips the legacy-removal gate; exact-head Runtime CI #274 / `31925491066` failed.

Do not trust later green-run claims in #50 PR prose that cite non-resolving SHAs or workflow runs belonging to other PRs. A real repair must land on #50 and receive its own fresh exact-head CI/review.

Missing lineage remains UNKNOWN; liveness, timing, helper existence, or prose are not substitutes.

## 4.3 Communication lineage

```text
#44 full-fidelity hcom lineage read OPEN_INTEGRATION
        ↓
#45 exact message relationships BLOCKED_UPSTREAM [clean in-layer]
        ↓
future exact run/request ↔ provider-event join
```

### #44

Repaired feature head `6f2b774eee27a0596820b12f080bfd7e60c0f50e`, Runtime CI #419 PASS.

SENTINEL has now independently returned `CLEAN IN-LAYER / FEATURE-HEAD ONLY / NOT INTEGRATION-READY`.

Verified source identity:
- one configured hcom SQLite store uses bare local event `id` identity;
- `instance` is metadata, not an ID namespace;
- same `event_id` with different instances fails closed;
- body-free, bounded, optional-field-presence, and no-message UNKNOWN semantics remain intact.

State is now `OPEN_INTEGRATION`. SWITCHYARD must synchronize the exact four-file layer onto then-current main, rerun CI, and obtain fresh integrated-head review.

### #45

Head `b78de03a9e05fe19846d0c0629a55e54427fa587`, CI #346 PASS, SENTINEL CLEAN IN-LAYER.

Its field-presence consistency defect is closed, but it remains on pre-repair #44 ancestry. After accepted #44, rebuild/synchronize #45 and repeat CI/review. Same-thread membership never substitutes for reply evidence; bounded silence never becomes wait state.

## 4.4 Exact communication correlation and communication waits

PR #51 is `PLANNING_ONLY`: current MAPS send success does not prove which exact hcom event was created. Timestamp/name/text/latest-event heuristics remain insufficient under concurrency/retry. Preferred prerequisite remains an exact provider send receipt or equivalent collision-safe correlation contract.

PR #52 is `PLANNING_ONLY`: a wait exists only when structured evidence proves an unresolved prerequisite that blocks progress and remains unresolved.

Current split:
- dependency/review/operator-approval waits → accepted #59;
- generic BLOCKED-cause inference → UNKNOWN without typed evidence;
- `WAIT_COMMUNICATION_RESPONSE` → unimplemented pending exact event correlation + explicit response-required/progress-blocking semantics.

`request + bounded silence != WAITING`.

## 4.5 Context Builder v2 evaluation stack

```text
Context Builder v1 ACCEPTED
        ↓
#39 frozen evidence-integrity corpus ACCEPTED
        ↓
#41 structural evidence projector/scorer OPEN_INTEGRATION
        ↓
#53 Stage-2 source-selection evaluation BLOCKED_UPSTREAM [clean in-layer]
        ↓
production retrieval candidate only if evidence justifies it
```

### #39

Accepted in snapshot main via merge `8397cbc2941a706440cabd0ffb93cac4ab1bdf6d` from synchronized head `5928abe4550dbf7a75c2a2825e3cda5033ead830` after Runtime CI #422 PASS and SENTINEL CLEAN integrated-head review.

The CBI-010 authority-truth defect remains closed: implementation state cannot substitute for proposal authorization evidence.

### #41

Feature head `ec525615fd708610bc3e90e07a95bb6c791d2465`, Runtime CI #382 PASS, SENTINEL CLEAN IN-LAYER. Exact AST ownership closes the old CODE_SYMBOL provenance defect.

Because #39 is now accepted, #41 no longer waits for an unaccepted upstream capability; its remaining work is genuine synchronization/rebuild onto accepted #39/current main plus fresh CI/review. Planning state: `OPEN_INTEGRATION`.

### #53

Head `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`, Runtime CI #348 PASS; independent remediation review found the Stage-2 layer clean after closing drift-source-pollution and overlay-content-identity defects.

It remains `BLOCKED_UPSTREAM` until #41 is accepted and #53 is rebuilt/synchronized on that ancestry.

Evaluation success is evidence for considering a candidate, not authorization to activate production retrieval.

## 4.6 Operational learning

```text
accepted outcomes + Run Record + frozen evaluation foundations
        ↓
#43 guidance-only projection OPEN_REPAIR [scope contract]
        ↓
#60 outcome lesson candidate BLOCKED_UPSTREAM [clean in-layer]
        ↓
future promotion/storage/injection authority design
```

### #43

Head `aeecf1b5775db1d5ac2484819620f476752f3654`. Independent review found no substantive runtime/authority defect: candidates never project, ACTIVE guidance needs external promotion evidence, lifecycle/applicability withholding is fail-closed, and output remains `GUIDANCE_ONLY`.

One scope-contract defect remains: the declared four-file task/PR boundary omitted the existing `tests/test_operational_learning_schema.py` path. Repair only that bounded contract (or fold the tests into an authorized file), then synchronize and re-review.

### #60

Head `cfd758aace44970e7400c005c337be040d367918`, Runtime CI #307 PASS, independent review CLEAN IN-LAYER. It remains blocked behind corrected/accepted #43.

Preserve:

```text
observation/outcome
→ candidate lesson
→ external review/promotion
→ applicable guidance
```

Never collapse this to `outcome prose → instruction/policy`.

---

# 5. Prime roadmap phase reconciliation

| Prime phase | Current interpretation |
|---|---|
| 0. Stabilize foundation | `HISTORICAL / COMPLETE`. |
| 1. Provider-neutral Harness API | `ACCEPTED V1` through #20–#24. |
| 2. Explicit execution/session/helper lineage | `PARTIAL / OPEN`: #48 integration, #49 rebuild after A1, #50 repair; #44 integration then #45 rebuild. |
| 3. Review/evidence revision binding | `ACCEPTED V1` through #32. |
| 4. Deterministic repeated lifecycle flows | `TRIGGERED`; add only for stable repeated procedures. |
| 5. Capability/Skill composition | `FOUNDATION ACCEPTED; PRODUCTION COMPOSITION GATED`. |
| 6. Controlled operational learning | `OPEN / UNACCEPTED` via #43→#60; promotion/storage/injection authority unresolved. |
| 7. Outcome-driven harness refinement | `FOUNDATION ACCEPTED; REFINEMENT EVIDENCE-GATED`; no autonomous promotion. |

Environment E1/E2 are accepted; E3 #30 is synchronized/CI-green and review-pending. Context Builder frozen integrity input #39 is now accepted; #41 is the next dependency layer but integration priority still belongs to SWITCHYARD.

---

# 6. Detailed-roadmap reconciliation

## Harness Mechanics

Accepted v1: normalized Harness types/results, hcom normalization, Hook registry, HarnessService, canonical task/run/claim/revision/lease checks, and mandatory anti-spoof composition.

Open/gated: A1/A2/A3 lineage, #44/#45 integration, exact communication correlation, fuller trajectory evidence, and new adapters/operations only when concrete need exists.

## Procedural Knowledge & Skills

Accepted: Skill format, provenance/catalog read model, frozen selection evaluation, static quality/security gate.

Still gated: automatic production routing/activation, third-party promotion lifecycle, bundles that silently widen authority, and using Skills as policy/always-on context.

## Environment & Reproducibility

EnvironmentSpec/fingerprint are accepted. #30 is synchronized and CI-green but still unaccepted until exact integrated review/merge completes. Compatibility remains evidence, never continuation authority.

Later/evidence-triggered: authorized setup/mutation, worktree/container provisioning, recovery equivalence/rehydration, and snapshots only if justified.

## Agentic Security

Accepted: negative operating contract, risk lenses, canonical Harness guards, anti-spoof tests, static Skill gate, secret-aware environment boundaries, immutable review-subject identity, and Operator Intent Compiler shaping.

Attach future security work to concrete capability boundaries rather than building a second orchestrator.

## Learning & Evaluation

Accepted: outcomes, Portable Run Record, frozen regression case, comparative evaluator, Skill selection evaluation foundation, and Context Builder frozen evidence-integrity corpus.

Still gated: #41/#53 integration, fuller communication/environment/trajectory coverage, operational-learning lifecycle, aggregate metrics after comparable sample size, and externally reviewed promotion.

---

# 7. Legacy recovery reconciliation

The migration audit/backlog are evidence/options, not execution queues.

## Absorbed / materially represented

- negative operating contract → #19;
- risk review lenses → #19;
- trace/outcomes → #19;
- immutable evidence/review freshness → #32;
- frozen comparative evaluation → #33–#35 plus focused eval corpora;
- Context Builder explicit-first/evidence integrity → v1 + accepted #39, with #41/#53 open;
- canonical prerequisite waits → #59;
- Operator Intent Compiler shaping → #57;
- authority provenance / citation-is-not-ratification → cross-system invariant.

## Partially represented / open

- exact anchors/source drift → #41/#53 after accepted #39;
- communication-complete trace → #44/#45 + future exact join;
- execution/helper/recovery/submission lineage → #48→#49→#50;
- run-bound environment evidence → #30;
- controlled operational learning → #43→#60;
- communication-backed response waits → after exact communication correlation.

## Evidence-triggered; do not manufacture work

- telemetry/event secret-safety expansion after auditing real durable write surfaces;
- Git worktree isolation for parallel writable runs;
- deterministic `maps flow` procedures for demonstrated stable routines;
- helper no-progress advisory;
- persistent helper continuity;
- cost/yield and escaped-defect metrics after meaningful sample size;
- bounded phase-boundary discovery;
- bounded system-adherence audits;
- scoped temporary halt delegation;
- universal sandbox/container/snapshot machinery;
- autonomous semantic retrieval;
- autonomous Harness/policy/routing/lesson promotion.

Recovery rule:

> preserve the observed problem, invariant, evidence, and useful technique; do not revive the legacy subsystem by default.

---

# 8. Dependency map

```text
ACCEPTED HARNESS / SECURITY V1
  ├── #48 A1 [clean feature; integration]
  │     ↓
  │   #49 A2 [clean historically; rebuild after A1]
  │     ↓
  │   #50 A3 [repair + upstream]
  │
  └── #44 hcom full read [clean feature; integration]
        ↓
      #45 message relationships [clean feature; rebuild after #44]
        ↓
      exact run ↔ provider event receipt/join
        ↓
      communication-response waits

CONTEXT BUILDER V1 + #39 ACCEPTED
        ↓
#41 structural projector/scorer [clean feature; integration]
        ↓
#53 Stage-2 selection evaluator [clean feature; rebuild after #41]
        ↓
production retrieval candidate only if evidence justifies it

ENVIRONMENT E1/E2 ACCEPTED
        ↓
#30 run-bound evidence [synchronized + CI green; review pending]
        ↓
recovery/setup equivalence only after explicit authority design

OUTCOMES + RUN RECORD + EVAL ACCEPTED
        ↓
#43 guidance projection [scope-contract repair]
        ↓
#60 outcome candidate [clean feature; upstream]
        ↓
explicit promotion/storage/injection authority design
```

A downstream stack must be genuinely synchronized to the **accepted** upstream interface before historical CI/review can support integration.

---

# 9. Bounded next planning questions

- After A1/A2/A3 acceptance: can trace/Run Record mechanically join exact provider-session, helper/recovery, and submission-attempt lineage? Missing older joins stay UNKNOWN.
- After #44/#45 acceptance: revalidate #51’s provider-receipt premise. If exact event identity is still unavailable, shape the smallest collision-safe provider receipt; never use timestamp/name/body heuristics.
- After #41/#53 acceptance: use frozen evaluation to decide whether any production retrieval experiment is justified. Passing evaluation is a proposal prerequisite, not a mandate.
- After #30 acceptance: define evidence needed for recovery equivalence without turning COMPATIBLE into permission.
- Before operational-learning promotion/persistence: resolve canonical storage ownership, promotion/retirement authority, expiry/supersession, applicability conflict, precedence, and safe context injection.

---

# 10. Do not build for roadmap completeness

Absent evidence, do not create a Prime supervisor, second mutable authority store, permanent discovery/process-policing agent, global mutable task session truth, automatic policy/lesson/routing/Skill promotion, heuristic lineage, silence/liveness waits, a vector database merely because retrieval is discussed, universal containers/snapshots, deterministic flows for unstable procedures, or dashboards that become mutation/control surfaces.

The roadmap succeeds when it prevents duplicate work and makes the next bounded question clear.

---

# 11. Four-lane handoff

- **SWITCHYARD** — integration order, real ancestry, exact delta, fresh synchronized-head CI/review, merge.
- **ANVIL** — general new runtime implementation and assigned bounded defect repair.
- **SENTINEL** — independent exact-head review; no feature edits while reviewing.
- **FOUNDRY** — planning/legacy reconciliation and bounded task shaping; runtime only for explicit incumbent repair returns.

Dependency constraints in this document are not SWITCHYARD merge-priority commands.

---

# 12. Snapshot limitations

This file is intentionally dated and becomes stale whenever relevant `main` or PR state moves. At each planning pass: recover live main, coordination, exact PR heads/reviews/CI; move only merged work to ACCEPTED; preserve UNKNOWN; refresh the overlay when material state changes.