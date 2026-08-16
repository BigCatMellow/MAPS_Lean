# MAPS current capability reconciliation — 2026-08-16

Status: `PLANNING STATUS OVERLAY — NOT ACTIVE AUTHORITY`

Snapshot base: `main@7269ce2be25993fa19b172f65c95381328585a35`

This document reconciles the long-form MAPS capability roadmaps with accepted and open repository state at the snapshot above. The master, Prime, and five detailed capability roadmaps remain the architectural/design references, but some historical “current baseline” prose predates substantial accepted work.

**Live GitHub state and accepted MAPS state supersede this snapshot.** Before taking work, re-read current `main`, `work/coordination/agents/*.md`, and the exact target PR/base/head/review/CI. This document is a derived planning read model, not task, policy, review, merge, or runtime authority.

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
- `OPEN_REPAIR` — independent review returned a concrete implementation/evidence/scope defect; repair is required before integration.
- `OPEN_REVIEW` — implementation or synchronization exists but the required exact-head independent review is unresolved.
- `OPEN_INTEGRATION` — implementation/review is clean in-layer but current-main synchronization and/or integration gates remain.
- `BLOCKED_UPSTREAM` — downstream work exists but a required upstream interface is not accepted in the needed form.
- `PLANNING_ONLY` — design/research evidence, not runtime behavior or authority.
- `EVIDENCE_GATED` — preserved candidate still requiring measured evidence and normal review/decision authority.
- `TRIGGERED` — implement only after concrete repeated need/risk demonstrates value.
- `HISTORICAL` — useful context, but no longer an instruction about current state.
- `UNKNOWN` — evidence is insufficient for a stronger claim.

Green CI does not override a semantic review blocker. A clean feature review does not make an unmerged capability `ACCEPTED`. A synchronized current-main head with no fresh independent review is `OPEN_REVIEW`, not merge-ready.

---

# 2. Historical baseline corrections

## 2.1 PR #19 / Prime Phase 0 is historical, not pending

PR #19 **Preserve and implement priority MAPS Lean improvements** is merged. Its accepted foundation includes the negative operating contract, risk-specific review lenses, safer diagnostics/events, read-only trace v1, append-only outcomes, Context Builder v1, status v1, and Runtime PR CI.

> Prime Phase 0 is a completed historical prerequisite. Do not restart the old PR #19 review queue or treat it as an unmerged dependency.

## 2.2 Roadmap “future capability” prose may describe already-accepted v1 work

Accepted foundations now include provider-neutral Harness types/service/hooks, Skills format/catalog/evaluation/static gate, EnvironmentSpec/fingerprint, immutable consequential review-subject binding, Run Record/frozen/comparative evaluation, structured canonical waits, and Operator Intent Compiler request shaping.

Merged code/tests own implemented interfaces. Roadmap prose preserves intent and extension constraints, not duplicate runtime truth.

## 2.3 Planning-only designs remain planning-only

PRs #51 and #52 remain open planning-only design evidence. #51 establishes that exact task/run↔hcom event attribution still needs an exact provider send receipt or equivalent collision-safe correlation contract. #52 preserves the evidence rule for explainable waits.

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
| Operator Intent Compiler request shaping | `ACCEPTED` | PR #57 merged into snapshot main. Compilation shapes explicit intent/constraints; it does not manufacture merge/publish/delete/spend/external-send authority. |
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
#30 run-environment evidence OPEN_INTEGRATION
```

PR #30 exact feature head:

`7bae6d5758619a391c7551ee4589ea2d80d0a5b8`

Runtime CI #415 / `31932277332`: PASS.

SWITCHYARD independent feature-head disposition: `CLEAN IN-LAYER / READY FOR SWITCHYARD INTEGRATION AFTER THE CURRENT #39 GATE`.

The prior HIGH Run Record evidence-integrity defect is mechanically closed:

- source-surface availability is distinct from actual exact-run evidence presence;
- `environment_evidence=[]` yields `MISSING`, `source_available=true`, `included=false`;
- one or more exact-run observations yields `VERIFIED`, `included=true`;
- malformed non-list projected evidence fails explicitly;
- review-subject UNKNOWN and `replay.complete=false` remain intact.

**Planning state: `OPEN_INTEGRATION`, not `OPEN_REPAIR` and not `ACCEPTED`.** The branch still has historical ancestry. SWITCHYARD owns current-main synchronization, preservation of newer accepted state/Run Record/schema changes, exact integrated-delta verification, fresh integrated-head CI, and fresh independent integrated review.

Compatibility remains bounded evidence and never authorizes resume/recovery/mutation/execution by itself.

## 4.2 Execution lineage

```text
Harness Wave 1 #20–#24 ACCEPTED
        ↓
#48 A1 project/adapter/session lineage OPEN_INTEGRATION
        ↓
#49 A2 helper/recovery lineage BLOCKED_UPSTREAM [own layer previously clean]
        ↓
#50 A3 submission-attempt/run lineage BLOCKED_UPSTREAM + OPEN_REPAIR
```

### #48 A1

Exact repaired feature head:

`2f23959afff9525beada28993bad536878310b7f`

Runtime CI #392 / `31931474528`: PASS. SENTINEL disposition: `CLEAN IN-LAYER / NOT INTEGRATION-READY`.

Closed defects:

1. false global `(adapter_id, session_id)` identity replaced with canonical project-scoped `(project_id, adapter_id, session_id)` evidence;
2. SQLite raw-string whitespace aliases closed with exact canonical project equality and adapter/session lexical identity constraints matching runtime semantics.

**Planning state: `OPEN_INTEGRATION`.** Historical ancestry remains; SWITCHYARD must synchronize onto then-current main and obtain fresh integrated-head CI/review.

### #49 A2

Current head:

`ed865be729cf2d15663258fd46c9296ea32d28e7`

Independent pre-integration review found **no A2-specific blocker** on its historical A1 base. The layer preserves helper/recovery relationship evidence without taking over HelperRunStore/RecoveryStore authority.

Because #49 is built on the pre-repair A1 head and overlaps schema/store/trace, it must be genuinely rebuilt/synchronized on accepted #48 ancestry rather than merely retargeted. Planning state remains `BLOCKED_UPSTREAM`.

### #50 A3

Current branch head:

`832fa4ab2c3e97a8f7cdc22a73baca0d276adfc0`

It remains upstream-blocked and also has two A3-specific blockers:

1. **immutable UNKNOWN attribution** — row absence currently means both “UNKNOWN at submission time” and “available for later insertion,” allowing historical UNKNOWN to be rewritten into EXPLICIT attribution; new A3-era attempts must record immutable `UNKNOWN` or `EXPLICIT` attribution atomically;
2. **active-runtime legacy token / CI** — `runtime/state/run_lineage_trace.py` contains `legacy/` wording that trips the legacy-removal gate; exact-head Runtime CI #274 / `31925491066` failed.

Do not trust later green-run claims in the #50 PR body that refer to non-resolving SHAs / workflow runs belonging to other PRs. Repair must land on the actual #50 branch and receive fresh exact-head CI.

Missing lineage remains UNKNOWN; provider liveness/helper existence/timestamps/prose are not substitutes.

## 4.3 Communication lineage

```text
#44 full-fidelity hcom lineage read OPEN_REVIEW
        ↓
#45 exact message relationships BLOCKED_UPSTREAM [clean in-layer]
        ↓
future exact run/request ↔ provider-event join
```

### #44

Exact repaired feature head:

`6f2b774eee27a0596820b12f080bfd7e60c0f50e`

Runtime CI #419 / `31951668246`: PASS.

FOUNDRY repaired the returned HIGH source-identity defect:

- bare local `event_id` is now the uniqueness key for one configured hcom store/bounded read;
- `instance` remains event metadata and does not qualify identity;
- same `event_id` with different `instance` values fails closed in both lineage read and capability probe;
- task/note wording no longer claims `(instance,event_id)` as the proven source identity.

There is **no fresh independent disposition on this repaired head yet**. Therefore the planning state is `OPEN_REVIEW`, not clean/integration-ready. If independent feature-head review is clean, SWITCHYARD must still synchronize the four-file layer onto current accepted main and repeat integrated-head CI/review.

### #45

Exact head:

`b78de03a9e05fe19846d0c0629a55e54427fa587`

Runtime CI #346 / `31929065504`: PASS. SENTINEL disposition: `CLEAN IN-LAYER / NOT INTEGRATION-READY`.

The prior optional-field-presence defect is closed. Exact `reply_to_local` remains the only reply edge; same-thread membership is not reply evidence; bounded absence is not WAITING/PENDING.

#45 is still built on historical pre-repair #44 ancestry, so it remains `BLOCKED_UPSTREAM`. After accepted #44, rebuild/synchronize the four-file #45 layer and obtain fresh CI/review.

Communication evidence does not become task/run/wait authority merely because relationships can be derived.

## 4.4 Exact communication correlation and communication waits

PR #51 remains `PLANNING_ONLY`. Direct provider inspection established that current MAPS send success does not receive the exact newly created hcom event ID; timestamp/name/text/latest-event correlation is insufficient under concurrency/retry. Preferred prerequisite remains an exact provider send receipt or equivalent collision-safe correlation contract.

PR #52 remains `PLANNING_ONLY`. Its safe structured subset is partly represented by accepted #59.

Current split:

- canonical dependency/review/operator-approval waits → accepted in #59;
- generic BLOCKED-cause inference → UNKNOWN without typed causal evidence;
- `WAIT_COMMUNICATION_RESPONSE` → not implemented; requires exact run↔provider-event correlation plus explicit response-required/progress-blocking semantics.

`request + bounded silence != WAITING`.

## 4.5 Context Builder v2 evaluation stack

```text
Context Builder v1 (#19) ACCEPTED
        ↓
#39 frozen evidence-integrity corpus OPEN_REVIEW [synchronized to snapshot main]
        ↓
#41 structural evidence projector/scorer BLOCKED_UPSTREAM [clean in-layer]
        ↓
#53 Stage-2 source-selection evaluation BLOCKED_UPSTREAM [clean in-layer]
        ↓
production retrieval candidate only if evidence justifies it
```

ANVIL owns this development stack; SWITCHYARD owns integration.

### #39

Current synchronized head:

`5928abe4550dbf7a75c2a2825e3cda5033ead830`

Base: `main@7269ce2be25993fa19b172f65c95381328585a35`.

Runtime CI #422 / `31951875209`: PASS. Exact current-main→head delta remains the intended four frozen-evaluation/task files.

Historical feature head `adf25a5721808cd272bc9eb9af90a25038f568eb` received SENTINEL `CLEAN IN-LAYER`, but that review predates SWITCHYARD synchronization. The synchronized head still requires fresh independent exact-head review.

**Planning state: `OPEN_REVIEW`.** Do not call it accepted or merge-ready until the integrated-head reviewer clears this exact state.

### #41

Exact head:

`ec525615fd708610bc3e90e07a95bb6c791d2465`

Runtime CI #382 / `31930788766`: PASS. SENTINEL: `CLEAN IN-LAYER / NOT INTEGRATION-READY`.

The CODE_SYMBOL provenance blocker is closed via exact AST ownership rather than substring matching. However this head is stacked on the historical repaired #39 feature head, not accepted #39. Planning state remains `BLOCKED_UPSTREAM`; after #39 acceptance, genuinely rebuild/synchronize #41 and rerun CI/review.

### #53

Exact head:

`d5c03a8e09bc5c49b884bc452d3c487a04ce5974`

Runtime CI #348 / `31929616706`: PASS. Independent remediation review found the Stage-2 layer clean after closing drift-source-pollution and exact overlay-content identity defects.

#53 remains `BLOCKED_UPSTREAM` until #39/#41 are accepted/stable and #53 is rebuilt/synchronized/reviewed on that ancestry.

These are evaluation mechanisms, not production retrieval authority. Passing evaluation makes a production retrieval candidate worth considering; it does not activate retrieval.

## 4.6 Operational learning

```text
accepted outcomes + Run Record + frozen evaluation foundations
        ↓
#43 guidance-only projection OPEN_REPAIR [runtime semantics otherwise clean]
        ↓
#60 canonical outcome lesson candidate builder BLOCKED_UPSTREAM [clean in-layer]
        ↓
future promotion/storage/injection only through explicit authority design
```

### #43

Current head:

`aeecf1b5775db1d5ac2484819620f476752f3654`

Independent review found no substantive runtime/authority blocker: candidates do not project, externally supplied promotion evidence is required for ACTIVE guidance, lifecycle/applicability withholding is fail-closed, and output remains `GUIDANCE_ONLY`.

One explicit scope-contract defect remains: the task/PR declared four changed paths while the actual layer also includes `tests/test_operational_learning_schema.py`. Smallest repair is to amend the bounded task/PR change boundary (or fold the tests into an already-authorized file), then synchronize to current main, rerun CI, and re-review. Planning state is `OPEN_REPAIR` for that scope-contract issue.

### #60

Exact head:

`cfd758aace44970e7400c005c337be040d367918`

Runtime CI #307 / `31927126075`: PASS. Independent technical review: `CLEAN IN-LAYER`.

The candidate builder binds exact canonical outcome/task/revision/optional-run evidence, never converts outcome prose into lesson text, and always returns an unpromoted candidate. It remains `BLOCKED_UPSTREAM` behind corrected/accepted #43.

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
| 0. Stabilize foundation | `HISTORICAL / COMPLETE` for PR #19-era foundation. Do not restart Phase 0. |
| 1. Provider-neutral Harness API | `ACCEPTED V1` through #20–#24. |
| 2. Explicit execution/session/helper lineage | `PARTIAL / OPEN`. A1 #48 is clean in-layer and awaiting integration; A2 #49 waits accepted A1; A3 #50 also requires repair. Communication #44 is repaired but still in review; #45 waits accepted #44. |
| 3. Review/evidence revision binding | `ACCEPTED V1` through #32. |
| 4. Deterministic repeated lifecycle flows | `TRIGGERED`. Add only for demonstrably stable/repetitive procedures. |
| 5. Capability/Skill composition | `FOUNDATION ACCEPTED; PRODUCTION COMPOSITION GATED`. |
| 6. Controlled operational learning | `OPEN / UNACCEPTED` via #43→#60; promotion/storage/injection authority remains unresolved. |
| 7. Outcome-driven harness refinement | `FOUNDATION ACCEPTED; REFINEMENT EVIDENCE-GATED`. Autonomous promotion does not follow from evaluation success. |

Environment/reproducibility advanced in parallel: E1/E2 are accepted; E3 #30 is clean in-layer and awaiting integration; setup/rehydration/recovery automation remains later/evidence-triggered work.

---

# 6. Detailed roadmap reconciliation

## Harness Mechanics

Accepted v1: normalized Harness types/results, hcom normalization, Hook registry, HarnessService, canonical run/claim/revision/lease checks, and mandatory anti-spoof canonical enforcement.

Open/gated: A1 integration, A2/A3 lineage, #44 review/integration, exact communication correlation, fuller trajectory evidence, and new adapters/operations only when concrete need exists.

## Procedural Knowledge & Skills

Accepted: Skill format, provenance/catalog read model, frozen selection evaluation, and static quality/security gate.

Still gated: automatic production routing/activation, third-party promotion lifecycle beyond accepted evidence mechanisms, capability bundles that silently widen task authority, and turning Skills into policy/always-on context.

## Environment & Reproducibility

EnvironmentSpec and EnvironmentFingerprint are accepted first-class concepts. #30's prior Run Record coverage defect is repaired and independently clean in-layer, but #30 is not accepted until current-main integration and fresh integrated-head review complete.

Later/evidence-triggered: authorized setup/mutation, worktree/container provisioning, recovery equivalence/rehydration, and snapshots only if justified.

Compatibility remains evidence, never continuation authority.

## Agentic Security

Accepted foundations include the negative operating contract, risk lenses, mandatory Harness canonical guard composition, anti-spoof/adversarial regressions, static Skill gate, secret-aware environment boundaries, immutable consequential review-subject identity, and accepted Operator Intent Compiler shaping.

Attach future security work to concrete capability boundaries rather than creating a second security orchestrator.

## Learning & Evaluation

Accepted: outcomes, Portable Run Record, frozen regression case, comparative regression evaluator, and Skill selection evaluation foundation.

Still gated: fuller communication/environment/trajectory coverage; operational-learning lifecycle; aggregate cost/yield metrics when comparable samples exist; candidate Harness/routing/Skill/environment refinements; external/reviewed promotion only.

---

# 7. Legacy recovery reconciliation

Do not copy the migration audit/backlog wholesale into “next work.” The legacy recovery audit remains an audit checkpoint, and the future-ideas backlog remains options evidence rather than execution authority.

## Absorbed / materially represented

- negative operating contract → #19;
- risk-specific review lenses → #19;
- safer diagnostics/evidence boundaries → #19 and later environment/evidence work;
- trace/outcome evidence → #19;
- immutable reviewed-subject/evidence freshness → #32;
- frozen comparative evaluation discipline → #33–#35 and focused eval corpora;
- Context Builder explicit-first/evidence-integrity direction → v1 accepted, v2 evaluation stack open;
- exact structured prerequisite waits → core subset #59;
- authority provenance / citation-is-not-ratification → preserved cross-system invariant;
- Operator Intent Compiler request shaping → #57 accepted.

## Partially represented / open

- exact evidence anchors/source drift → #39/#41/#53;
- communication-complete replay/trace → #44/#45 plus future exact join;
- explicit execution/helper/recovery/submission lineage → #48→#49→#50;
- run-bound environment evidence → #30;
- controlled operational learning → #43→#60;
- communication-backed response waits → later, after exact communication correlation.

## Evidence-triggered; do not manufacture work

- telemetry/event secret-safety expansion after auditing actual durable write surfaces;
- Git worktree isolation for parallel writable runs;
- deterministic `maps flow` procedures beyond demonstrated repeated routines;
- helper live-but-no-progress advisory;
- persistent helper continuity;
- cost/yield and escaped-defect optimization after meaningful sample size;
- bounded phase-boundary discovery;
- bounded system-adherence audit;
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
        │     #49 A2 [own layer clean historically; rebuild after A1]
        │       ↓
        │     #50 A3 [upstream-blocked + repair required]
        │
        └── #44 hcom full read [repaired; independent review pending]
                ↓
              #45 message relationships [clean in-layer; upstream-blocked]
                ↓
       exact run ↔ provider event receipt/join
                ↓
       communication-response wait evidence

ACCEPTED CONTEXT BUILDER V1
        ↓
#39 frozen evidence integrity [synchronized; integrated-head review pending]
        ↓
#41 structural projector/scorer [clean in-layer; upstream-blocked]
        ↓
#53 Stage-2 source-selection evaluation [clean in-layer; upstream-blocked]
        ↓
production retrieval candidate only if evidence justifies

ACCEPTED ENVIRONMENT E1/E2
        ↓
#30 run-bound environment evidence [clean in-layer; integration pending]
        ↓
recovery/setup equivalence only after explicit authority design

ACCEPTED OUTCOMES + RUN RECORD + FROZEN EVAL
        ↓
#43 guidance-only learning projection [scope-contract repair]
        ↓
#60 outcome-derived candidate builder [clean in-layer; upstream-blocked]
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

Recheck whether trace/Run Record can mechanically join exact provider-session, helper/recovery, and submission-attempt lineage. Missing older joins remain UNKNOWN.

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

Own new runtime implementation and bounded review-returned defects on ANVIL-assigned lanes. Do not take FOUNDRY incumbent branches merely because planning mentions them.

## SENTINEL — Independent Review

Verify exact heads it did not implement/synchronize. Current high-value gates include #39's synchronized head and #44's repaired feature head. Repaired-but-unmerged states in this document are claims to reproduce, not approvals.

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
