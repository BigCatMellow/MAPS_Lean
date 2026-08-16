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
- `OPEN_REVIEW` — implemented/repaired evidence exists but independent review is still unresolved.
- `OPEN_INTEGRATION` — implementation/review is clean in-layer but current-main synchronization and integration gates remain.
- `BLOCKED_UPSTREAM` — downstream work exists but a required upstream interface is not accepted in the needed form.
- `PLANNING_ONLY` — design/research evidence, not runtime behavior or authority.
- `EVIDENCE_GATED` — preserved candidate still requiring measured evidence and normal review/decision authority.
- `TRIGGERED` — implement only after concrete repeated need/risk demonstrates value.
- `HISTORICAL` — useful context, but no longer an instruction about current state.
- `UNKNOWN` — evidence is insufficient for a stronger claim.

Green CI, a persuasive design, or an open PR never upgrades a capability to `ACCEPTED`.

---

# 2. Historical baseline corrections

## 2.1 PR #19 / Prime Phase 0 is historical, not pending

The master and Prime roadmaps still contain prose describing draft PR #19 as the current foundation and Phase 0 as waiting for that foundation to stabilize.

Live repository evidence supersedes that prose:

- PR #19 **Preserve and implement priority MAPS Lean improvements** is merged.
- Its accepted foundation includes the negative operating contract, risk-specific review lenses, safer diagnostics/events, read-only trace v1, append-only outcomes, Context Builder v1, status v1, and Runtime PR CI.

Therefore:

> Prime Phase 0 is a completed historical prerequisite. Do not restart the old PR #19 review queue or treat it as an unmerged dependency.

The architectural lesson remains valid: stabilize a foundation before stacking consequential interfaces on it.

## 2.2 Roadmap “future capability” prose may describe already-accepted v1 work

Examples with accepted foundations now include:

- provider-neutral Harness types/service/hooks and mandatory canonical enforcement;
- Skills format/catalog/evaluation/static quality gate;
- EnvironmentSpec and EnvironmentFingerprint/compatibility;
- immutable consequential review-subject binding;
- Portable Run Record, frozen regression cases, and comparative regression evaluator;
- structured explainable waits for canonical dependency/review/operator-approval evidence.

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
| Release/acquisition evidence integrity | `ACCEPTED` | PR #56. Insufficient operator-visible stale-surface evidence remains UNKNOWN rather than guessed N/A/PASS. |
| Structured explainable waits — canonical subset | `ACCEPTED` | PR #59. Dependency/review/operator-approval waits only; no runnable/scheduler authority. |
| Multi-agent coordination bulletin board | `ACCEPTED` | Named coordination files. Collision-avoidance evidence only; GitHub/canonical state remains authoritative. |

These foundations do **not** prove MAPS already has complete replay/lineage, production semantic retrieval, automatic Skill promotion, recovery authority from environment compatibility, communication-response waits, promoted operational learning, autonomous self-refinement, universal worktree/container/snapshot machinery, or deterministic flows for every procedure.

---

# 4. Open capability stacks and dependency constraints

Arrows below mean **dependency**, not merge priority. SWITCHYARD owns live integration order.

## 4.1 Environment evidence

```text
#28 EnvironmentSpec ACCEPTED
        ↓
#29 EnvironmentFingerprint ACCEPTED
        ↓
#30 run-environment evidence OPEN_INTEGRATION
```

PR #30 adds append-only EnvironmentSpec/fingerprint/compatibility observations to exact immutable runs. It remains unaccepted and must be integrated against then-current `main` with fresh exact-state gates.

Compatibility remains bounded evidence. It does not authorize resume, recovery, mutation, or execution.

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

### PR #48 exact clean feature state

Final repaired feature head:

`2f23959afff9525beada28993bad536878310b7f`

Runtime CI:

`#392 / 31931474528 — PASS`

SENTINEL exact-head disposition:

`CLEAN IN-LAYER / NOT INTEGRATION-READY`

Two HIGH identity defects were returned and mechanically closed on that exact head:

1. **False global provider-session identity.** A1 originally uniquified `(adapter_id, session_id)` globally even though accepted `SessionRef` identity is project-scoped. The repaired model derives canonical task `project_id`, stores project-scoped `(project_id, adapter_id, session_id)`, preserves it through resolver/trace, and requires exact project+adapter+session in the guard. Two projects may independently use the same provider-local `hcom/S1`; one project-scoped identity cannot ambiguously bind to two runs.
2. **SQLite raw-string normalization bypass.** Raw uniqueness could distinguish whitespace variants that runtime normalization collapsed. The final repair requires exact canonical task-project equality and constrains SQLite adapter/session keys to the runtime identity grammar: alphanumeric first character, only `[A-Za-z0-9_.:@-]`, length 1–128. Direct-SQL regressions reject project trailing-space, adapter space/tab, and session space/newline aliases.

The exact second-repair delta `a9284c1a... -> 2f23959a...` is four existing A1 files: schema, focused lineage test, task record, and implementation note.

**Planning state is `OPEN_INTEGRATION`, not ACCEPTED.** Historical ancestry remains. SWITCHYARD must genuinely synchronize the independently reviewed feature layer onto then-current accepted `main`, preserve newer accepted schema/state/runtime changes, verify the exact integrated delta, run fresh integrated-head Runtime CI, and obtain fresh exact integrated-head independent review before merge.

### Downstream A2/A3

PR #49 still depends on accepted A1. It must not inherit an old A1 identity contract by retargeting alone.

PR #50 depends on accepted/synchronized A2. Historical submission/run attribution that cannot be proven must remain UNKNOWN rather than inferred.

Do not substitute provider liveness, helper existence, timestamps, or prose for explicit lineage.

## 4.3 Communication lineage

```text
#44 full-fidelity hcom lineage read OPEN_INTEGRATION/REVIEW
        ↓
#45 exact message relationships BLOCKED_UPSTREAM
        ↓
future exact run/request ↔ provider-event join
```

PR #44's repaired feature layer validates provider-local `(instance, event_id)` uniqueness before claiming stable lineage evidence. It remains unaccepted.

PR #45 requires exact `coverage.field_presence` consistency before deriving reply/thread/request/ack relationships. It remains stacked behind #44 and unaccepted.

Communication evidence never becomes task/run authority merely because exact relationships can be derived.

## 4.4 Exact communication correlation and communication waits

PR #51 is `PLANNING_ONLY`. Current MAPS send success does not receive the exact newly created hcom event ID, so timestamp/name/text/latest-event correlation is insufficient under concurrency/retry. The preferred prerequisite is an exact provider send receipt or equivalently collision-safe correlation contract.

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
#39 frozen evidence-integrity corpus OPEN_REVIEW
        ↓
#41 structural evidence projector/scorer OPEN_REVIEW
        ↓
#53 Stage-2 source-selection evaluation BLOCKED_UPSTREAM
        ↓
production retrieval candidate only if evidence justifies it
```

ANVIL owns this development stack.

Live feature evidence at this checkpoint:

- #39 `adf25a5721808cd272bc9eb9af90a25038f568eb`, Runtime CI #365 PASS;
- #41 `ec525615fd708610bc3e90e07a95bb6c791d2465`, Runtime CI #382 PASS, synchronized to repaired #39;
- #53 `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`, Runtime CI #348 PASS on historical upstream and still blocked until repaired #39/#41 are accepted/stable and #53 is resynchronized/reviewed.

These are **evaluation mechanisms**, not production retrieval authority.

Important repaired invariants:

- authorization status cannot be proved merely by implementation/capability state;
- `CODE_SYMBOL` ownership is structural/exact rather than approximate substring matching;
- source selection is judged on precision, hard-negative abstention, drift, and vocabulary/paraphrase shift;
- passing an eval makes a candidate worth considering; it does not activate retrieval.

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

PR #43 deliberately has no lesson store and no `promote()` function. Only externally promoted, applicable, current records can project as `GUIDANCE_ONLY`.

PR #60 packages a candidate from exact canonical outcome evidence; it likewise cannot promote, persist, or inject guidance.

Preserve:

```text
observation/outcome
→ candidate lesson
→ external review/promotion
→ applicable guidance
```

Never collapse this to `outcome prose → instruction/policy`.

## 4.7 Operator Intent Compiler

PR #57 remains open/unaccepted at this checkpoint. Its intended placement is request shaping before canonical task/policy state, not a permission engine. Broad desired outcomes may not manufacture merge/publish/delete/spend/external-send authority.

---

# 5. Prime roadmap phase reconciliation

| Prime phase | Current interpretation |
|---|---|
| 0. Stabilize foundation | `HISTORICAL / COMPLETE` for PR #19-era foundation. Do not restart Phase 0. |
| 1. Provider-neutral Harness API | `ACCEPTED V1` through #20–#24. |
| 2. Explicit execution/session/helper lineage | `PARTIAL / OPEN`. A1 #48 is clean in-layer and awaiting current-main integration; A2 #49 and A3 #50 remain upstream-blocked. Communication lineage #44/#45 is a separate supporting track. |
| 3. Review/evidence revision binding | `ACCEPTED V1` through #32 for exact consequential reviewed-output identity. |
| 4. Deterministic repeated lifecycle flows | `TRIGGERED`. Add only for demonstrably stable/repetitive procedures. |
| 5. Capability/Skill composition | `FOUNDATION ACCEPTED; PRODUCTION COMPOSITION GATED`. Format/catalog/eval/static gate exist; automatic activation/promotion is not implied. |
| 6. Controlled operational learning | `OPEN / UNACCEPTED` via #43→#60. Promotion/storage/injection authority remains unresolved. |
| 7. Outcome-driven harness refinement | `FOUNDATION ACCEPTED; REFINEMENT EVIDENCE-GATED`. Outcomes + Run Record + frozen cases + comparative evaluator exist; autonomous promotion does not. |

Environment/reproducibility advanced in parallel: E1/E2 are accepted, E3 remains open, and setup/rehydration/recovery automation is later work.

---

# 6. Detailed roadmap reconciliation

## Harness Mechanics

Accepted v1: normalized Harness types/results, hcom normalization, Hook registry, HarnessService, canonical run/claim/revision/lease checks, and mandatory anti-spoof canonical enforcement.

Open/gated: durable execution/helper/recovery/submission lineage after A1 integration, exact communication correlation, fuller provider-operation trajectory evidence, and additional adapters/operations only when concrete need exists.

## Procedural Knowledge & Skills

Accepted: Skill format, provenance/catalog read model, frozen selection evaluation, and static quality/security gate.

Still gated: automatic production routing/activation, third-party trust/promotion lifecycle beyond accepted evidence mechanisms, capability bundles that silently widen task authority, and turning Skills into policy/always-on context.

## Environment & Reproducibility

The roadmap statement that EnvironmentSpec/fingerprint are missing first-class concepts is stale.

Accepted: EnvironmentSpec v1 and EnvironmentFingerprint/compatibility.

Open: #30 exact run-bound environment evidence.

Later/evidence-triggered: authorized setup/mutation, worktree/container provisioning, recovery equivalence/rehydration, and snapshots only if evidence justifies them.

Compatibility remains evidence, never continuation authority.

## Agentic Security

Accepted foundations include the negative operating contract, risk lenses, mandatory Harness canonical guard composition, anti-spoof/adversarial regressions, static Skill gate, secret-aware environment boundaries, and immutable consequential review-subject identity.

Attach future security work to concrete capability boundaries rather than creating a second security orchestrator.

## Learning & Evaluation

Accepted: outcomes, Portable Run Record, frozen regression case, comparative regression evaluator, and Skill selection evaluation foundation.

Still gated: fuller communication/environment/trajectory coverage; operational-learning lifecycle; aggregate cost/yield/escaped-defect metrics when comparable samples exist; candidate Harness/routing/Skill/environment refinements; external/reviewed promotion only.

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
- Context Builder explicit-first/evidence-integrity direction → v1 accepted, v2 eval open;
- exact structured prerequisite waits → core subset #59;
- authority provenance / citation-is-not-ratification → preserved as cross-system invariant.

## Partially represented / open

- exact evidence anchors and source-drift discipline → #39/#41/#53;
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
        ├── #48 A1 session identity [clean feature layer; integration pending]
        │       ↓
        │     #49 A2 helper/recovery lineage
        │       ↓
        │     #50 A3 submission/run lineage
        │
        └── #44 full hcom evidence
                ↓
              #45 message relationships
                ↓
       exact run ↔ provider event receipt/join
                ↓
       communication-response wait evidence

ACCEPTED CONTEXT BUILDER V1
        ↓
#39 frozen evidence integrity
        ↓
#41 structural projector/scorer
        ↓
#53 Stage-2 source-selection evaluation
        ↓
production retrieval candidate only if evidence justifies

ACCEPTED ENVIRONMENT E1/E2
        ↓
#30 run-bound environment evidence
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

Resolve canonical storage ownership if needed, promotion/retirement authority, review/expiry/supersession, applicability conflicts, precedence against authoritative task/policy/operator instructions, and safe Context Builder/startup integration.

### Periodic legacy recovery

Continue audit only where unresolved MAP-relevant ideas/promotions/retired tasks expose a still-missing Lean problem. Do not perform archaeology merely to increase coverage numbers.

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

Own new runtime implementation and bounded review-returned defects. Do not implement planning candidates simply because they appear here.

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
