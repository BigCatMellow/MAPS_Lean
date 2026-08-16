# MAPS current capability reconciliation — 2026-08-16

Status: `PLANNING STATUS OVERLAY — NOT ACTIVE AUTHORITY`

Snapshot base: `main@146f092a63af63b0fd750445e584a39e82ea1442`

This document reconciles the long-form MAPS capability roadmaps with accepted and open repository state at the snapshot above. The master, Prime, and five detailed capability roadmaps remain the architectural/design references, but some historical “current baseline” prose predates substantial accepted work.

**Live GitHub state and accepted MAPS state supersede this snapshot.** Before taking work, re-read current `main`, `work/coordination/agents/*.md`, and the exact target PR/base/head. This document is a derived planning read model, not task, policy, review, merge, or runtime authority.

---

## 1. Reading order and status vocabulary

| Question | Strongest source |
|---|---|
| What is accepted now? | live `main`, merged code/tests, canonical MAPS state |
| Who owns current work? | live PR state + `work/coordination/agents/*.md` |
| What architecture/invariants are intended? | master / Prime / detailed capability roadmaps |
| Which legacy ideas remain worth preserving? | migration audit/backlog, rechecked against current state |
| What did the capability program look like at this checkpoint? | this reconciliation |

Status labels:

- `ACCEPTED` — merged into `main` at or before this snapshot.
- `OPEN_REPAIR` — independent review returned a concrete implementation/evidence defect; repair is required before integration.
- `OPEN_REVIEW` — implementation/repair exists but independent review is still unresolved.
- `OPEN_INTEGRATION` — implementation/review is clean in-layer but current-main synchronization and/or integration gates remain.
- `BLOCKED_UPSTREAM` — downstream work exists but a required upstream interface is not accepted in the needed form.
- `PLANNING_ONLY` — design/research evidence, not runtime behavior or authority.
- `EVIDENCE_GATED` — preserved candidate still requiring measured evidence and normal review/decision authority.
- `TRIGGERED` — implement only after concrete repeated need/risk demonstrates value.
- `HISTORICAL` — useful context, but no longer an instruction about current state.
- `UNKNOWN` — evidence is insufficient for a stronger claim.

Green CI does not override a semantic review blocker, and a clean feature review does not make an unmerged capability `ACCEPTED`.

---

# 2. Historical baseline corrections

## 2.1 PR #19 / Prime Phase 0 is historical, not pending

The master and Prime roadmaps still contain prose describing draft PR #19 as the current foundation and Phase 0 as waiting for that foundation to stabilize.

Live repository evidence supersedes that prose:

- PR #19 **Preserve and implement priority MAPS Lean improvements** is merged.
- Its accepted foundation includes the negative operating contract, risk-specific review lenses, safer diagnostics/events, read-only trace v1, append-only outcomes, Context Builder v1, status v1, and Runtime PR CI.

Therefore:

> Prime Phase 0 is a completed historical prerequisite. Do not restart the old PR #19 review queue or treat it as an unmerged dependency.

## 2.2 Roadmap “future capability” prose may describe already-accepted v1 work

Accepted foundations now include provider-neutral Harness types/service/hooks, Skills format/catalog/evaluation/static gate, EnvironmentSpec/fingerprint, immutable consequential review-subject binding, Run Record/frozen/comparative evaluation, and structured canonical waits.

Merged code/tests own implemented interfaces. Roadmap prose preserves intent and extension constraints, not duplicate runtime truth.

## 2.3 Planning-only designs remain planning-only

PRs #51 and #52 preserve useful communication/wait design evidence. They are not runtime authority merely because later work cites them.

PR #59 already accepted the safe structured-wait subset from canonical dependency/review/approval evidence. Future communication-response waits remain separate and require exact communication correlation plus explicit response-required/progress-blocking evidence.

---

# 3. Accepted capability baseline

| Capability | State | Accepted boundary |
|---|---|---|
| Lean operating/state/context foundation | `ACCEPTED` | PR #19. Context Builder remains explicit-first; trace/status remain derived/read-only. |
| Provider-neutral Harness contract | `ACCEPTED` | PR #20: normalized types/results, explicit UNKNOWN, authority-neutral adapter contract. |
| hcom normalization + Hook registry | `ACCEPTED` | PR #21. Hooks may deny/narrow/require approval; they do not grant task authority. |
| HarnessService / call-time correlation | `ACCEPTED` | PR #22. Explicit adapter registration and binding/session correlation; no durable lineage claim. |
| Canonical run guard | `ACCEPTED` | PR #23. Rechecks canonical task/run/claim/revision/lease; bare provider-local session IDs fail closed. |
| Mandatory anti-spoof Harness enforcement | `ACCEPTED` | PR #24. Consequential Harness mutation requires trusted canonical guard composition. |
| Skills format | `ACCEPTED` | PR #25. Procedural packaging, not policy authority. |
| Skills catalog/provenance | `ACCEPTED` | PR #26. Derived catalog/provenance, not a new policy store. |
| Frozen Skill selection evaluation | `ACCEPTED` | PR #27. Evaluation evidence only; no production promotion authority. |
| Static Skill quality/security gate | `ACCEPTED` | PR #31. Static CLEAR is evidence, not approval. |
| EnvironmentSpec | `ACCEPTED` | PR #28. Declarative requirements; no secret values or task authority. |
| EnvironmentFingerprint/compatibility | `ACCEPTED` | PR #29. Observed evidence with explicit compatible/drifted/UNKNOWN semantics. |
| Consequential immutable review-subject binding | `ACCEPTED` | PR #32. Exact immutable reviewed-output/evidence identity required; run identity alone is insufficient. |
| Portable Run Record | `ACCEPTED` | PR #33. Exact run selection, deterministic identity, privacy-aware export, explicit incomplete replay/coverage. |
| Frozen regression case | `ACCEPTED` | PR #34. Sanitized deterministic evaluation evidence; no auto-promotion. |
| Comparative regression evaluator | `ACCEPTED` | PR #35. Read-only candidate/baseline comparison; promotion remains external/reviewed. |
| Release/acquisition evidence integrity | `ACCEPTED` | PR #56. Insufficient stale-surface evidence remains UNKNOWN rather than guessed N/A/PASS. |
| Structured explainable waits — canonical subset | `ACCEPTED` | PR #59. Dependency/review/operator-approval waits only; no runnable/scheduler authority. |
| Multi-agent coordination bulletin board | `ACCEPTED` | Named coordination files. Collision-avoidance evidence only; GitHub/canonical state remains authoritative. |

These foundations do **not** prove complete replay/lineage, production semantic retrieval, automatic Skill promotion, recovery authority from environment compatibility, communication-response waits, promoted operational learning, autonomous self-refinement, universal worktree/container/snapshot machinery, or deterministic flows for every procedure.

---

# 4. Open capability stacks and dependency constraints

Arrows mean **dependency**, not merge priority. SWITCHYARD owns live integration order.

## 4.1 Environment evidence

```text
#28 EnvironmentSpec ACCEPTED
        ↓
#29 EnvironmentFingerprint ACCEPTED
        ↓
#30 run-environment evidence OPEN_REPAIR
```

PR #30 exact reviewed feature head:

`1a4016c424e188e06560c9af125e97be774ac269`

Runtime CI #358 / `31929911245`: PASS, but SENTINEL returned **CHANGES REQUIRED** on that exact head.

The remaining HIGH evidence-integrity defect is in Run Record coverage semantics:

- the E3 trace surface always projects an `environment_evidence` key, including an empty list when no observation exists;
- Run Record currently treats key presence as sufficient to mark environment coverage `VERIFIED`;
- therefore a run with zero environment observations can be reported as verified merely because the capability/read surface exists.

Required repair boundary:

- distinguish “environment evidence source surface available” from “this exact run has one or more environment observations”;
- an empty evidence list must not produce VERIFIED environment coverage;
- add paired adversarial coverage: no observation → non-VERIFIED; exact recorded E3 observation → VERIFIED;
- preserve review-subject UNKNOWN where exact selected-run binding is unproven and keep `replay.complete = false`.

The E3 storage model otherwise remains sound in review: append-only exact-run evidence, immutable snapshots/hashes, compatibility recomputation, sensitive-evidence rejection, and no task/run/recovery authority mutation.

**Planning state is `OPEN_REPAIR`, not integration-only.** After repair: fresh exact-head CI + independent feature review, then current-main synchronization/integrated-head gates by SWITCHYARD.

Compatibility remains bounded evidence and never authorizes resume/recovery/mutation/execution by itself.

## 4.2 Execution lineage

```text
Harness Wave 1 #20–#24 ACCEPTED
        ↓
#48 A1 project/adapter/session lineage OPEN_INTEGRATION
        ↓
#49 A2 helper/recovery lineage BLOCKED_UPSTREAM
        ↓
#50 A3 submission-attempt/run lineage BLOCKED_UPSTREAM
```

PR #48 final repaired feature head:

`2f23959afff9525beada28993bad536878310b7f`

Runtime CI #392 / `31931474528`: PASS.

SENTINEL exact-head disposition: `CLEAN IN-LAYER / NOT INTEGRATION-READY`.

Two HIGH identity defects were mechanically closed:

1. false global `(adapter_id, session_id)` identity was replaced with canonical project-scoped `(project_id, adapter_id, session_id)` evidence;
2. SQLite raw-string whitespace aliases were closed with exact canonical project equality and adapter/session lexical identity constraints matching runtime semantics.

**Planning state is `OPEN_INTEGRATION`, not ACCEPTED.** Historical ancestry remains. SWITCHYARD must synchronize onto then-current main, preserve newer accepted schema/state/runtime, verify exact delta, run fresh integrated-head CI, and obtain fresh integrated-head independent review.

PR #49 had no A2-specific blocker on its historical A1 base, but it overlaps schema/store/trace and must be rebuilt on accepted A1 rather than retargeted. PR #50 remains downstream and has separate A3 defects: immutable UNKNOWN-at-submission must be recorded rather than represented as a backfillable absence, and its active-runtime `legacy/` token currently fails the legacy-removal CI gate.

Missing lineage remains UNKNOWN; provider liveness/helper existence/timestamps/prose are not substitutes.

## 4.3 Communication lineage

```text
#44 full-fidelity hcom lineage read OPEN_REPAIR
        ↓
#45 exact message relationships BLOCKED_UPSTREAM
        ↓
future exact run/request ↔ provider-event join
```

PR #44 exact reviewed head:

`4a11203f1faf0f8b5d199d6af2643ab7b7205764`

Runtime CI #343 / `31928993044`: PASS, but SENTINEL returned **CHANGES REQUIRED**.

The remaining HIGH identity defect comes from pinned upstream hcom storage semantics:

- the configured hcom store has one local SQLite `events` table with bare `id INTEGER PRIMARY KEY AUTOINCREMENT`;
- `instance` is event metadata, not the event-ID namespace;
- therefore stable identity for one bounded provider read is the bare local `event_id`, not `(instance, event_id)`;
- the current repair can accept two rows with the same `event_id` when `instance` differs and may incorrectly report capability `SUPPORTED`.

Required repair boundary:

- enforce bare `event_id` uniqueness across the bounded projected sample;
- add an adversarial case with same event ID + different instance and require both lineage read and capability probe to fail closed;
- update task/note wording so the composite identity is no longer described as the proven identity.

**Planning state is `OPEN_REPAIR`.** #45 remains `BLOCKED_UPSTREAM`; its own downstream duplicate checks cannot make #44's provider-boundary identity claim true.

Communication evidence does not become task/run/wait authority merely because relationships can later be derived.

## 4.4 Exact communication correlation and communication waits

PR #51 is `PLANNING_ONLY`. MAPS send success currently does not receive the exact newly created hcom event ID, so timestamp/name/text/latest-event correlation is insufficient under concurrency/retry. Preferred prerequisite: exact provider send receipt or equivalently collision-safe correlation contract.

PR #52 is `PLANNING_ONLY`. Its safe structured subset is partly represented by accepted #59.

Current split:

- canonical dependency/review/operator-approval waits → accepted in #59;
- generic BLOCKED-cause inference → UNKNOWN without typed causal evidence;
- `WAIT_COMMUNICATION_RESPONSE` → not implemented; requires exact run↔provider-event correlation plus explicit response-required/progress-blocking semantics.

`request + bounded silence != WAITING`.

## 4.5 Context Builder v2 evaluation stack

```text
Context Builder v1 (#19) ACCEPTED
        ↓
#39 frozen evidence-integrity corpus OPEN_INTEGRATION
        ↓
#41 structural evidence projector/scorer BLOCKED_UPSTREAM [clean in-layer]
        ↓
#53 Stage-2 source-selection evaluation BLOCKED_UPSTREAM
        ↓
production retrieval candidate only if evidence justifies it
```

ANVIL owns this development stack.

### #39

Exact head `adf25a5721808cd272bc9eb9af90a25038f568eb`, Runtime CI #365 PASS, SENTINEL `CLEAN IN-LAYER / NOT INTEGRATION-READY`.

The prior authority-truth blocker is closed: proposal authorization status must be proved by the proposal's own `PROPOSED — NOT ACTIVE AUTHORITY` evidence, not inferred from implementation state.

**State: `OPEN_INTEGRATION`.** SWITCHYARD must synchronize to current main, verify exact delta, rerun CI, and obtain fresh integrated-head review.

### #41

Exact head `ec525615fd708610bc3e90e07a95bb6c791d2465`, stacked exactly on repaired #39, Runtime CI #382 PASS, SENTINEL `CLEAN IN-LAYER / NOT INTEGRATION-READY`.

The prior CODE_SYMBOL provenance blocker is closed via exact AST ownership rather than substring matching.

Because #41 depends on #39's feature layer, its planning state is **`BLOCKED_UPSTREAM` despite being clean in-layer**. Integrate #39 first; then genuinely rebuild/synchronize #41 on accepted #39/current main, run fresh CI, and re-review the integrated head.

### #53

Exact historical head `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`, Runtime CI #348 PASS on historical upstream. It remains `BLOCKED_UPSTREAM` until #39/#41 are accepted/stable and #53 is resynchronized/reviewed.

These are evaluation mechanisms, not production retrieval authority. Passing evaluation makes a production retrieval candidate worth considering; it does not activate retrieval.

## 4.6 Operational learning

```text
accepted outcomes + Run Record + frozen evaluation foundations
        ↓
#43 guidance-only projection OPEN
        ↓
#60 canonical outcome lesson candidate builder BLOCKED/STACKED ON #43
        ↓
future promotion/storage/injection only through explicit authority design
```

PR #43 deliberately has no lesson store and no `promote()` function. PR #60 packages a candidate from exact canonical outcome evidence and likewise cannot promote, persist, or inject guidance.

Preserve:

```text
observation/outcome
→ candidate lesson
→ external review/promotion
→ applicable guidance
```

Never collapse this to `outcome prose → instruction/policy`.

## 4.7 Operator Intent Compiler

PR #57 exact current state:

- base `main@146f092a63af63b0fd750445e584a39e82ea1442`;
- head `854226531acd740ed8c282e58654bc8da74bde47`;
- Runtime CI #379 / `31930751899`: PASS;
- exact five-file planning/playbook delta, ahead-only from accepted main;
- SENTINEL disposition: `CLEAN / technically ready for SWITCHYARD integration`.

The prior authority-expansion defect is closed: action-specific consequential authority must trace to the operator request or already-canonical authority; review/CI/policy gates constrain authority when it exists but do not manufacture merge/publish/delete/spend/external-send permission.

**Planning state: `OPEN_INTEGRATION`, not ACCEPTED.** SWITCHYARD owns the remaining integration decision on that unchanged exact state.

---

# 5. Prime roadmap phase reconciliation

| Prime phase | Current interpretation |
|---|---|
| 0. Stabilize foundation | `HISTORICAL / COMPLETE` for PR #19-era foundation. Do not restart Phase 0. |
| 1. Provider-neutral Harness API | `ACCEPTED V1` through #20–#24. |
| 2. Explicit execution/session/helper lineage | `PARTIAL / OPEN`. A1 #48 is clean in-layer and awaiting integration; A2 #49/A3 #50 remain upstream-blocked. Communication lineage #44 is back in repair and #45 remains behind it. |
| 3. Review/evidence revision binding | `ACCEPTED V1` through #32. |
| 4. Deterministic repeated lifecycle flows | `TRIGGERED`. Add only for demonstrably stable/repetitive procedures. |
| 5. Capability/Skill composition | `FOUNDATION ACCEPTED; PRODUCTION COMPOSITION GATED`. |
| 6. Controlled operational learning | `OPEN / UNACCEPTED` via #43→#60. Promotion/storage/injection authority remains unresolved. |
| 7. Outcome-driven harness refinement | `FOUNDATION ACCEPTED; REFINEMENT EVIDENCE-GATED`. Autonomous promotion does not follow from evaluation success. |

Environment/reproducibility advanced in parallel: E1/E2 are accepted, E3 #30 is currently back in repair, and setup/rehydration/recovery automation is later work.

---

# 6. Detailed roadmap reconciliation

## Harness Mechanics

Accepted v1: normalized Harness types/results, hcom normalization, Hook registry, HarnessService, canonical run/claim/revision/lease checks, and mandatory anti-spoof canonical enforcement.

Open/gated: A1 integration, A2/A3 lineage, #44 identity repair, exact communication correlation, fuller trajectory evidence, and new adapters/operations only when concrete need exists.

## Procedural Knowledge & Skills

Accepted: Skill format, provenance/catalog read model, frozen selection evaluation, and static quality/security gate.

Still gated: automatic production routing/activation, third-party promotion lifecycle beyond accepted evidence mechanisms, capability bundles that silently widen task authority, and turning Skills into policy/always-on context.

## Environment & Reproducibility

EnvironmentSpec and EnvironmentFingerprint are accepted first-class concepts. #30 is not yet accepted because its Run Record coverage integration currently confuses source-surface availability with actual exact-run evidence presence.

Later/evidence-triggered: authorized setup/mutation, worktree/container provisioning, recovery equivalence/rehydration, and snapshots only if justified.

Compatibility remains evidence, never continuation authority.

## Agentic Security

Accepted foundations include the negative operating contract, risk lenses, mandatory Harness canonical guard composition, anti-spoof/adversarial regressions, static Skill gate, secret-aware environment boundaries, and immutable consequential review-subject identity.

Attach future security work to concrete capability boundaries rather than creating a second security orchestrator.

## Learning & Evaluation

Accepted: outcomes, Portable Run Record, frozen regression case, comparative regression evaluator, and Skill selection evaluation foundation.

Still gated: fuller communication/environment/trajectory coverage; operational-learning lifecycle; aggregate cost/yield metrics when comparable samples exist; candidate Harness/routing/Skill/environment refinements; external/reviewed promotion only.

---

# 7. Legacy recovery reconciliation

Do not copy the migration audit/backlog wholesale into “next work.” Reconcile each candidate against current accepted/open state.

## Already absorbed or materially represented

- negative operating contract → #19;
- risk-specific review lenses → #19;
- safer diagnostics/evidence boundaries → #19 and later environment/evidence work;
- trace/outcome evidence → #19;
- immutable reviewed-subject/evidence freshness → #32;
- frozen comparative evaluation discipline → #33–#35 and focused eval corpora;
- Context Builder explicit-first/evidence-integrity direction → v1 accepted, v2 eval stack open;
- exact structured prerequisite waits → core subset #59;
- authority provenance / citation-is-not-ratification → preserved as cross-system invariant.

## Partially represented / open

- exact evidence anchors/source drift → #39/#41/#53;
- communication-complete replay/trace → #44/#45 plus future exact join;
- explicit execution/helper/recovery/submission lineage → #48→#49→#50;
- run-bound environment evidence → #30;
- controlled operational learning → #43→#60;
- communication-backed response waits → later, after exact communication correlation.

## Evidence-triggered; do not manufacture work

- Git worktree isolation for parallel writable runs;
- deterministic `maps flow` procedures beyond demonstrated repeated routines;
- helper live-but-no-progress advisory;
- persistent helper continuity;
- cost/yield and escaped-defect optimization after meaningful sample size;
- bounded phase-boundary/system-adherence audits;
- scoped temporary halt delegation;
- universal sandbox/container/snapshot machinery;
- autonomous semantic retrieval;
- autonomous Harness/policy/routing/lesson promotion.

Recovery rule:

> preserve the observed problem, invariant, evidence, and useful technique; do not revive the legacy subsystem by default.

---

# 8. Dependency map for future shaping

```text
ACCEPTED HARNESS / SECURITY V1
        │
        ├── #48 A1 [clean feature layer; integration pending]
        │       ↓
        │     #49 A2 [upstream-blocked]
        │       ↓
        │     #50 A3 [upstream-blocked + repair required]
        │
        └── #44 hcom full read [repair required]
                ↓
              #45 message relationships [upstream-blocked]
                ↓
       exact run ↔ provider event receipt/join
                ↓
       communication-response wait evidence

ACCEPTED CONTEXT BUILDER V1
        ↓
#39 frozen evidence integrity [clean; integration pending]
        ↓
#41 structural projector/scorer [clean in-layer; upstream-blocked]
        ↓
#53 Stage-2 source-selection evaluation [upstream-blocked]
        ↓
production retrieval candidate only if evidence justifies

ACCEPTED ENVIRONMENT E1/E2
        ↓
#30 run-bound environment evidence [repair required]
        ↓
recovery/setup equivalence only after explicit authority design

ACCEPTED OUTCOMES + RUN RECORD + FROZEN EVAL
        ↓
#43 guidance-only learning projection
        ↓
#60 outcome-derived candidate builder
        ↓
promotion/storage/injection authority design
        ↓
controlled activation after review/decision gates
```

A downstream stack must be genuinely synchronized to the **accepted** upstream interface before historical CI/review can support integration.

---

# 9. Bounded next planning questions

These are questions to shape after prerequisites stabilize, not implementation assignments.

### After A1/A2/A3 acceptance

Recheck whether trace/Run Record can mechanically join exact provider-session, helper/recovery, and submission-attempt lineage. Missing legacy joins remain UNKNOWN.

### After #44/#45 acceptance

Revalidate PR #51's provider-receipt premise against then-current hcom. If exact created-event identity is still unavailable, shape the smallest provider/API receipt needed for collision-safe run↔event correlation. Do not use timestamp/name/body heuristics.

### After #39/#41/#53 acceptance

Use frozen evaluation results to decide whether any production retrieval candidate deserves an implementation experiment. Passing evaluation is a proposal prerequisite, not a mandate to build vector/semantic infrastructure.

### After #30 acceptance

Define evidence needed for recovery-equivalence questions without turning `COMPATIBLE` into permission. Recovery still requires current task/run/policy/ownership authority.

### Before operational-learning persistence/promotion

Resolve canonical storage ownership if needed, promotion/retirement authority, review/expiry/supersession, applicability conflicts, precedence against task/policy/operator authority, and safe Context Builder/startup integration.

---

# 10. Do not build merely to make the roadmap look complete

Absent new evidence, do not create:

- a Prime supervisor or second orchestrator;
- a second mutable task/session/review/policy store;
- a permanent discovery/process-policing agent;
- global mutable “current session” truth on tasks;
- automatic policy/lesson/routing/Skill promotion;
- lineage inferred from timestamps/names/prose;
- waits inferred from silence/liveness;
- a knowledge graph/vector database merely because retrieval appears in planning;
- universal containers/snapshots merely because environment planning discusses them;
- deterministic flows for unstable procedures;
- dashboards that quietly become mutation/control surfaces.

The roadmap succeeds when it prevents duplicate work and makes the next bounded question obvious, not when every candidate box is implemented.

---

# 11. Four-lane handoff

## SWITCHYARD — Integration / PR Control

Own live integration order, real ancestry, exact deltas, fresh synchronized-head CI/review, and merge. This document supplies dependency constraints only.

## ANVIL — Development

Own new runtime implementation and bounded review-returned defects. Current concrete returned repairs include #30 environment coverage semantics and #44 bare-event-ID uniqueness when ANVIL/coordination explicitly accepts those lanes.

## SENTINEL — Independent Review

Verify exact heads it did not implement/synchronize. Repaired-but-unmerged states in this document are claims to reproduce, not approvals.

## FOUNDRY — Planning / Control-Surface

Maintain roadmap/legacy reconciliation, shape missing bounded tasks, and check accepted/open work against roadmap intent. Avoid active runtime outputs except explicit incumbent repair returns, then refreeze for independent review.

---

# 12. Snapshot limitations

This document is intentionally dated. It becomes stale whenever relevant `main` or PR state moves.

At the next planning pass:

1. recover live `main`;
2. re-read all coordination files;
3. re-check exact PR/base/head/review/CI for every discussed stack;
4. move only truly merged capabilities to `ACCEPTED`;
5. preserve UNKNOWN rather than guessing from old notes;
6. update this reconciliation or create a newer dated checkpoint when material program state changes.
