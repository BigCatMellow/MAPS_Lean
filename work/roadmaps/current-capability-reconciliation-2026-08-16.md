# MAPS current capability reconciliation — 2026-08-16

Status: `PLANNING STATUS OVERLAY — NOT ACTIVE AUTHORITY`

Snapshot base: `main@146f092a63af63b0fd750445e584a39e82ea1442`

This document reconciles the long-form MAPS capability roadmaps with the repository state visible at the snapshot above. It exists because the master and Prime roadmaps intentionally preserve detailed design history, but some of their “current baseline” prose still describes the earlier draft-PR #19 era.

**Live GitHub state and accepted MAPS state supersede this snapshot.** Before taking work, re-read current `main`, `work/coordination/agents/*.md`, and the exact target PR/base/head. Do not treat this document as task, policy, review, merge, or runtime authority.

---

## 1. How to use this document

Use the documents for different questions:

| Question | Source |
|---|---|
| What is actually accepted now? | live `main`, merged code/tests, accepted state |
| What is actively being implemented/reviewed/integrated? | live PRs + `work/coordination/agents/*.md` |
| What is the intended architecture and why? | master / Prime / five detailed capability roadmaps |
| What useful legacy ideas remain preserved? | `migration/LEGACY_IDEA_RECOVERY_AUDIT.md` + `migration/FUTURE_IDEAS_BACKLOG.md` |
| What was the implementation-status picture at this checkpoint? | **this document** |

The reconciliation is deliberately a **derived planning read model**. It must never become a second mutable task/PR authority.

### Status vocabulary

- `ACCEPTED` — merged into `main` at or before the snapshot.
- `OPEN_REVIEW` — implemented/repaired evidence exists, but the capability is not accepted on `main`.
- `OPEN_INTEGRATION` — implementation is substantially complete but still requires current-main synchronization and/or exact-head CI/review/merge.
- `BLOCKED_UPSTREAM` — downstream work exists but its prerequisite has not been accepted in the required form.
- `PLANNING_ONLY` — design/research evidence; not runtime behavior or a required implementation dependency by itself.
- `EVIDENCE_GATED` — preserved candidate whose promotion still requires measured evidence and normal review/decision authority.
- `TRIGGERED` — implement only after a concrete repeated need/risk demonstrates value.
- `HISTORICAL` — useful context, but no longer an instruction about current state.
- `UNKNOWN` — evidence at this snapshot is insufficient for a stronger statement.

An open PR is never upgraded to `ACCEPTED` merely because its CI is green or its design is persuasive.

---

# 2. Obsolete baseline assumptions to retire

## 2.1 Draft PR #19 is no longer the current foundation

The master and Prime roadmaps still contain baseline text saying the major Lean foundation is on draft PR #19 and that Phase 0 must stabilize it before later phases begin.

That is historical now:

- PR #19, **Preserve and implement priority MAPS Lean improvements**, is merged.
- Its accepted foundation includes the negative operating contract, risk-specific review lenses, secret-safer diagnostics/events, read-only trace v1, append-only outcomes, Context Builder v1, status v1, and normal Runtime PR CI.

Therefore:

> **Prime Phase 0 is a completed historical prerequisite, not the current execution gate.**

The detailed Phase 0 reasoning remains useful as a reminder to stabilize foundations before building on them, but future agents must not restart the old review queue or treat PR #19 as an unmerged dependency.

## 2.2 “Future capability” does not necessarily mean “still missing”

Several long-form roadmap sections describe candidate interfaces/mechanisms that now have accepted v1 implementations. The roadmap text remains useful for invariants and future extension, but **merged code/tests own the implemented interface**.

Examples now accepted at least in foundational form:

- provider-neutral Harness types/service/hooks and mandatory canonical enforcement;
- Skills format/catalog/evaluation/static quality gate;
- EnvironmentSpec and EnvironmentFingerprint/compatibility;
- immutable consequential review-subject binding;
- Portable Run Record, frozen regression cases, and comparative regression evaluator;
- structured explainable waits for already-canonical dependency/review/operator-approval evidence.

## 2.3 Planning-only designs do not become runtime prerequisites by citation

PRs #51 and #52 are useful A4 communication/wait design evidence. They are not accepted runtime authority merely because later work cites them.

PR #59 explicitly accepted the safe structured wait subset using already-canonical dependency/review/approval evidence and states that PR #52 is planning evidence, **not** a runtime dependency.

The unimplemented communication-response wait remains a later problem with stricter prerequisites.

---

# 3. Accepted capability baseline at this snapshot

This table is not an exhaustive commit ledger. It maps the roadmap capabilities that materially affect next-work planning.

| Capability | Planning state | Accepted evidence / boundary |
|---|---|---|
| Lean foundation: task truth, trace/status, outcomes, Context Builder v1, operating/review safeguards | `ACCEPTED` | PR #19 merged. Context Builder remains explicit-first; trace/status remain derived/read-only. |
| Provider-neutral Harness contract | `ACCEPTED` | PR #20 merged: normalized types/results, explicit `UNKNOWN`, authority-neutral adapter contract. |
| hcom normalization + deterministic Hook registry | `ACCEPTED` | PR #21 merged. Hooks may deny/narrow/require approval; they do not grant task authority. |
| HarnessService / call-time correlation | `ACCEPTED` | PR #22 merged. Explicit adapter registration and binding/session correlation; no durable lineage claim. |
| Canonical run guard | `ACCEPTED` | PR #23 merged. Re-checks canonical task/run/claim/revision/lease; bare provider-local session IDs fail closed. |
| Mandatory anti-spoof Harness enforcement | `ACCEPTED` | PR #24 merged. Consequential Harness mutation requires trusted canonical guard composition. Durable adapter-qualified session lineage remains the intentional next gap. |
| Portable Run Record v1 | `ACCEPTED` | PR #33 merged. Exact run selection, deterministic identity, privacy-aware derived export, explicit incomplete replay/coverage. |
| Frozen regression case v1 | `ACCEPTED` | PR #34 merged. Sanitized deterministic evaluation evidence; no automatic classification/promotion. |
| Comparative regression evaluator v1 | `ACCEPTED` | PR #35 merged. Read-only baseline/candidate comparison over frozen cases; promotion remains external/reviewed. |
| Agent Skills format foundation | `ACCEPTED` | PR #25 merged. Procedural packaging, not policy authority. |
| Skills catalog/provenance read model | `ACCEPTED` | PR #26 merged. Provenance/catalog remains derived rather than a new policy store. |
| Frozen Skill selection evaluation | `ACCEPTED` | PR #27 merged. Evaluation evidence only; no automatic production selection authority. |
| Static Skill quality/security gate | `ACCEPTED` | PR #31 merged. Static CLEAR is advisory evidence, not approval. |
| EnvironmentSpec v1 | `ACCEPTED` | PR #28 merged. Declarative requirements; no secret values and no task authority. |
| EnvironmentFingerprint + compatibility | `ACCEPTED` | PR #29 merged. Observed evidence with explicit compatible/drifted/unknown semantics; compatibility does not authorize recovery. |
| Consequential immutable review-subject binding | `ACCEPTED` | PR #32 merged. Consequential review must bind exact immutable reviewed-output/evidence identity; run identity alone is insufficient. |
| Structured explainable waits — canonical subset | `ACCEPTED` | PR #59 merged. Dependency/review/operator-approval waits only from structured canonical evidence; no runnable/scheduler authority. |
| Release/acquisition evidence integrity repair | `ACCEPTED` | PR #56 merged. Operator-visible N/A does not silently prove stale visible surfaces are gone; insufficient evidence remains `UNKNOWN`. |
| Multi-agent coordination bulletin board | `ACCEPTED` | PR #63 plus named lane files. Coordination is collision-avoidance evidence only; GitHub/canonical state remains authoritative. |

### What this does **not** prove

The accepted foundations above do not imply that MAPS already has:

- complete execution/session/helper/recovery/submission/communication lineage;
- complete portable replay;
- production semantic Context Builder retrieval;
- automatic Skill routing/promotion;
- automatic environment setup/rehydration/recovery authorization;
- communication-response wait inference;
- promoted operational learning;
- autonomous harness self-refinement;
- worktree isolation for every parallel writable run;
- deterministic flows for every repeated procedure.

Those distinctions remain important even when their prerequisite foundations are accepted.

---

# 4. Open capability stacks and real dependency constraints

The arrows below are **dependency constraints**, not a merge-priority instruction to SWITCHYARD.

## 4.1 Environment evidence

```text
#28 EnvironmentSpec ACCEPTED
        ↓
#29 EnvironmentFingerprint ACCEPTED
        ↓
#30 run-environment evidence OPEN_INTEGRATION
```

PR #30 adds append-only EnvironmentSpec/fingerprint/compatibility observations to exact immutable runs. Its implementation has historical green evidence, but it is not accepted at this snapshot and must be synchronized/gated against then-current `main` before merge.

Do not treat environment compatibility as permission to resume, recover, mutate, or execute. A later recovery/environment automation tranche must consume canonical task/policy authority separately.

## 4.2 Execution lineage

```text
Harness Wave 1 #20–#24 ACCEPTED
        ↓
#48 A1 project/adapter/session lineage OPEN_REVIEW
        ↓
#49 A2 helper/recovery lineage BLOCKED_UPSTREAM
        ↓
#50 A3 submission-attempt/run lineage BLOCKED_UPSTREAM
```

At this snapshot, FOUNDRY has frozen repaired PR #48 head:

`a9284c1a00fc42eb26807ea01e8ca667aaa5ebac`

with Runtime CI #386 / `31930919472` passing. The previous false-global-session-identity defect was repaired by scoping durable provider identity to canonical `(project_id, adapter_id, session_id)`. It still requires an eligible independent review and later current-main integration; therefore it remains **unaccepted**.

PR #49 still targets the older A1 head and cannot be treated as integration-ready until A1 is accepted and #49 is genuinely synchronized/revalidated.

PR #50 similarly waits on accepted/synchronized A2. Its exact-attribution principle remains sound: omitted historical submission/run attribution stays `UNKNOWN`, not inferred.

### Planning invariant

Do not “simplify” the stack by making provider/session liveness, helper existence, or timestamps stand in for explicit lineage. That would erase the evidence boundary the stack exists to create.

## 4.3 Communication lineage

```text
#44 full-fidelity hcom lineage read OPEN_REVIEW/INTEGRATION
        ↓
#45 exact message relationships BLOCKED_UPSTREAM
        ↓
future task/run ↔ provider-event join
```

PR #44's repaired historical feature head validates bounded provider-local `(instance, event_id)` uniqueness before claiming the read surface can support stable lineage evidence. It is still unaccepted.

PR #45 is intentionally stacked behind #44 and requires `coverage.field_presence` consistency before deriving reply/thread/request/ack relationships. It remains unaccepted until #44 is accepted and #45 is rebuilt/revalidated on that state.

No current communication relationship should be promoted into task/run authority.

## 4.4 Exact task/run ↔ communication correlation and communication waits

PR #51 is `PLANNING_ONLY`. Its key unresolved prerequisite is provider-side exact send identity: MAPS must receive an exact created hcom event ID (or an equivalently collision-safe correlation mechanism). Timestamp/name/text/latest-event heuristics remain insufficient under concurrency/retry.

PR #52 is also `PLANNING_ONLY`. Its safe structured subset is now partly superseded by accepted PR #59.

Current split:

- dependency/review/operator-approval waits from canonical structured evidence → **accepted in #59**;
- generic BLOCKED-cause inference → still deliberately `UNKNOWN` without typed causal evidence;
- `WAIT_COMMUNICATION_RESPONSE` → **not implemented** and must wait for exact run↔provider-event correlation plus an explicit response-required/progress-blocking contract.

A request plus bounded silence is not proof of waiting.

## 4.5 Context Builder v2 evidence/retrieval evaluation

```text
Context Builder v1 (#19) ACCEPTED
        ↓
#39 frozen evidence-integrity corpus OPEN_REVIEW
        ↓
#41 deterministic evidence projector/scorer OPEN_REVIEW
        ↓
#53 Stage-2 source-selection evaluation BLOCKED_UPSTREAM
        ↓
future production retrieval only if evaluation justifies it
```

ANVIL owns this development stack.

Live repaired evidence at this snapshot includes:

- #39 head `adf25a5721808cd272bc9eb9af90a25038f568eb`, Runtime CI #365 PASS;
- #41 head `ec525615fd708610bc3e90e07a95bb6c791d2465`, Runtime CI #382 PASS and synchronized to repaired #39;
- #53 head `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`, Runtime CI #348 PASS on its historical upstream and therefore still blocked until the repaired #39/#41 chain is accepted/stable and #53 is resynchronized/reviewed.

These PRs are **evaluation mechanisms**, not production semantic retrieval authority. In particular:

- proposal authorization status cannot be substituted by implementation state;
- `CODE_SYMBOL` proof must resolve structurally rather than by approximate substring matching;
- retrieval/source selection must be evaluated for precision, hard-negative abstention, drift, and vocabulary/paraphrase shift;
- passing an eval creates a proposal/evidence basis, not automatic activation.

## 4.6 Operational learning

```text
accepted outcome evidence / Run Record / frozen-eval foundations
        ↓
#43 guidance-only operational-learning projection OPEN
        ↓
#60 canonical outcome lesson candidate builder BLOCKED/STACKED ON #43
        ↓
future promotion/storage/injection only through explicit authority design
```

These remain unaccepted at the snapshot.

Preserve the central boundary:

> observation/outcome → candidate lesson → external review/promotion → applicable guidance

must never collapse into:

> outcome text → automatic instruction/policy.

PR #43 deliberately has no lesson store or `promote()` function. PR #60 packages a candidate from exact canonical outcome evidence but likewise cannot promote it. Any future durable lesson lifecycle must define who may promote/retire, applicability, expiry/review, supersession, and conflict precedence against canonical task/policy authority before startup/context injection is considered.

## 4.7 Operator Intent Compiler

PR #57 is an open planning/manual request-shaping tranche under SWITCHYARD control at this snapshot.

Its intended placement is:

```text
operator request
→ request compilation / task shaping
→ AGI readiness
→ canonical task/policy state
→ Context Builder
→ worker/harness
```

The compiler is not permission authority. Broad desired outcomes may not manufacture merge/publish/delete/spend/external-send permission. Until merged, #57 is not accepted process behavior.

---

# 5. Prime roadmap phase reconciliation

The original Prime sequence remains useful as an architectural dependency model, but it is no longer a linear “start at Phase 0” execution list.

| Prime phase | Current planning interpretation |
|---|---|
| **0. Review/stabilize foundation** | `HISTORICAL / COMPLETE` for the PR #19-era foundation. Continue normal per-tranche exact-head review; do not restart Phase 0. |
| **1. Provider-neutral Harness API** | `ACCEPTED V1` through #20–#24. Future provider operations/adapters remain incremental. |
| **2. Explicit execution/session/helper lineage** | `PARTIAL / OPEN`. A1 #48 under review; A2 #49 and A3 #50 blocked upstream; communication lineage #44/#45 separate supporting track. |
| **3. Review/evidence revision binding** | `ACCEPTED V1` through #32 for consequential immutable reviewed-output identity. Later evidence freshness extensions must preserve this authority boundary. |
| **4. Deterministic repeated lifecycle flows** | `TRIGGERED / NOT GENERALLY IMPLEMENTED`. Add only for procedures demonstrated stable/repetitive; do not create flow machinery to satisfy the roadmap. |
| **5. Capability/Skill composition** | `FOUNDATION ACCEPTED, PRODUCTION COMPOSITION STILL GATED`. Format/catalog/eval/static gate are on main; automatic production selection/promotion is not implied. |
| **6. Controlled operational learning** | `OPEN / UNACCEPTED` via #43→#60; promotion/storage/injection authority intentionally unresolved. |
| **7. Outcome-driven harness evaluation/refinement** | `FOUNDATION ACCEPTED, REFINEMENT EVIDENCE-GATED`. Outcomes + Run Record + frozen cases + comparative evaluator exist; autonomous promotion does not. |

Parallel environment/reproducibility work has also advanced independently: E1/E2 are accepted, E3 remains open, and setup/rehydration/recovery automation is later work.

---

# 6. Detailed roadmap reconciliation

## 6.1 Harness Mechanics

Treat the roadmap's candidate API/types as design history where accepted runtime contracts now exist.

Current accepted mechanical foundation:

- normalized types/results and explicit `UNKNOWN`;
- hcom adapter normalization;
- Hook registry;
- HarnessService;
- canonical run/claim/revision/lease checks;
- mandatory anti-spoof canonical enforcement.

Still open/gated:

- durable execution/session/helper/recovery/submission lineage;
- exact communication correlation;
- broader deterministic operation telemetry/trajectory;
- additional provider adapters/operations when concrete need exists.

## 6.2 Procedural Knowledge & Skills

Accepted foundation:

- Agent Skills-compatible packaging;
- provenance/catalog read model;
- frozen selection evaluation;
- static quality/security gate.

Still gated:

- production automatic skill routing/activation beyond accepted explicit mechanisms;
- imported third-party trust/promotion lifecycle beyond evidence already defined;
- capability bundles that could silently widen task authority;
- turning Skills into policy or always-on context.

## 6.3 Environment & Reproducibility

The roadmap statement that EnvironmentSpec/fingerprint are missing first-class concepts is now stale.

Accepted:

- EnvironmentSpec v1;
- EnvironmentFingerprint + explicit compatibility states.

Open:

- #30 exact run-bound environment evidence.

Later/evidence-triggered:

- authorized setup/mutation;
- workspace/worktree/container provisioning;
- recovery equivalence/rehydration decisions;
- snapshotting only if reproducibility evidence justifies it.

Compatibility remains evidence, never continuation authority by itself.

## 6.4 Agentic Security

Accepted foundations now include:

- negative operating contract and risk lenses;
- mandatory Harness canonical guard composition;
- adversarial authority/liveness/continuity regressions;
- static Skill gate;
- secret-aware EnvironmentSpec boundaries;
- immutable consequential review-subject identity.

Open security work should be attached to concrete capability boundaries rather than creating a parallel security orchestrator. Examples include lineage identity correctness, Skill/import provenance, persistent-guidance promotion, and future external/destructive action hooks where real operations require them.

## 6.5 Learning & Evaluation

Accepted foundations:

- append-only real-world outcomes;
- Portable Run Record v1;
- frozen regression case v1;
- comparative regression evaluator v1;
- Skill selection eval foundation.

Open/gated:

- fuller trajectory/communication/environment coverage as their evidence sources become accepted;
- operational-learning candidate/promotion lifecycle;
- aggregate cost/yield/escaped-defect metrics when enough comparable runs exist;
- candidate harness/routing/Skill/environment changes evaluated on frozen evidence;
- promotion remains external/reviewed, never automatic.

---

# 7. Legacy recovery reconciliation

The migration audit/backlog should not be copied wholesale into “next work.” The useful current classification is:

## 7.1 Already absorbed or materially represented

- **negative operating contract** → accepted in PR #19;
- **risk-specific review lenses** → accepted in PR #19;
- **secret-safer diagnostic/event boundaries** → partially accepted in PR #19 and reinforced in later environment/evidence work;
- **trace / outcome evidence** → accepted foundation in #19;
- **review-time evidence freshness / immutable subject identity** → materially addressed by #32;
- **three-layer/frozen evaluation discipline** → materially represented by #33–#35 plus focused eval corpora;
- **Context Builder explicit-first/evidence-integrity direction** → v1 accepted in #19, v2 evaluation stack open;
- **explainable waits from exact structured prerequisites** → core subset accepted in #59;
- **authority provenance / citation is not ratification** → preserved as a cross-system invariant and exercised by review/evidence work.

## 7.2 Partially represented / current open work

- **exact evidence anchors, temporal/source-drift discipline** → #39/#41/#53 evaluation stack;
- **communication-complete replay/trace** → #44/#45 plus future #51-style exact correlation;
- **explicit execution/helper/recovery/submission lineage** → #48→#49→#50;
- **run-bound environment evidence** → #30;
- **controlled operational learning** → #43→#60, still no promotion authority;
- **communication-backed explainable response waits** → not implemented; #51/#52 preserve design constraints.

## 7.3 Still evidence-triggered; do not manufacture work

- Git worktree isolation for parallel writable runs;
- deterministic `maps flow` procedures beyond demonstrated repeated routines;
- helper live-but-no-progress advisory;
- persistent helper continuity;
- cost/yield and escaped-defect optimization once sample size is meaningful;
- bounded phase-boundary discovery/system-adherence audits as occasional methods;
- scoped temporary halt delegation;
- universal sandbox/container/snapshot machinery;
- autonomous semantic retrieval;
- autonomous harness/policy/routing/lesson promotion.

The governing recovery rule remains:

> preserve the observed problem, invariant, evidence and useful technique; do not revive the legacy subsystem by default.

---

# 8. Dependency map for future shaping

This is a **planning dependency graph**, not a directive to integrate everything immediately.

```text
ACCEPTED HARNESS / SECURITY V1
        │
        ├── #48 A1 session identity
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
#41 structural evidence projector/scorer
        ↓
#53 Stage-2 source-selection evaluation
        ↓
production retrieval candidate only if evidence justifies

ACCEPTED ENVIRONMENT E1/E2
        ↓
#30 run-bound environment evidence
        ↓
recovery/setup equivalence decisions only after explicit authority design

ACCEPTED OUTCOMES + RUN RECORD + FROZEN EVAL
        ↓
#43 guidance-only learning projection
        ↓
#60 outcome-derived candidate builder
        ↓
promotion/storage/injection authority design
        ↓
controlled activation only after review/decision gates
```

Cross-cutting rule: a downstream stack must be genuinely synchronized to the **accepted** upstream interface before its old CI/review can support integration.

---

# 9. Bounded next planning questions

These are questions to shape when their prerequisite evidence becomes stable. They are **not implementation assignments**.

## 9.1 After A1/A2/A3 are accepted

Recheck whether trace/Run Record can mechanically join:

- exact provider session lineage;
- helper/recovery lineage;
- exact submission attempt attribution.

Do not infer missing legacy joins. Preserve coverage as `UNKNOWN` where exact relation evidence does not exist.

## 9.2 After #44/#45 are accepted

Revalidate PR #51's provider receipt premise against the then-current hcom contract. If exact created-event identity is still not returned, shape the smallest provider/API receipt change required for collision-safe run↔event correlation.

Do not implement timestamp/name/body-hash correlation as a shortcut.

## 9.3 After #39/#41/#53 are accepted

Use their frozen results to decide whether **any** production retrieval candidate deserves an implementation experiment. A passing frozen corpus is a prerequisite for proposal, not proof that semantic/vector infrastructure must be built.

## 9.4 After #30 is accepted

Define the evidence needed to answer recovery-equivalence questions without turning `COMPATIBLE` into permission. Recovery still requires current task/run/policy/ownership checks.

## 9.5 Before operational-learning persistence/promotion

Resolve, explicitly:

- canonical storage owner, if storage is needed at all;
- promotion and retirement authority;
- review/expiry/supersession lifecycle;
- applicability conflict resolution;
- precedence against task/operator/policy authority;
- how guidance reaches Context Builder/startup without becoming a hidden instruction plane.

## 9.6 Periodic legacy recovery

Continue the audit only for unresolved MAP-relevant ideas/promotions/retired tasks that may expose a still-missing Lean problem. Do not perform exhaustive archaeology merely to increase coverage numbers.

---

# 10. What not to build merely to satisfy the roadmap

Do not create, absent new evidence:

- a Prime supervisor or second orchestrator;
- a second mutable task/session/review/policy database;
- a permanent discovery/process-policing agent;
- a global “current session” truth copied onto tasks;
- automatic policy/lesson/routing/Skill promotion;
- inferred lineage from timestamps/names/prose;
- inferred waits from silence/liveness;
- a knowledge graph or vector database because the roadmap mentions retrieval;
- universal containers/snapshots because the environment roadmap discusses them;
- deterministic flows for procedures that have not actually stabilized;
- dashboards that quietly become mutation/control surfaces.

The roadmap is successful when it prevents duplicate work and makes the next bounded question obvious—not when every candidate box has been implemented.

---

# 11. Handoff by operating lane

## SWITCHYARD — Integration / PR Control

Use live state to choose merge/integration order. Preserve exact ancestry/deltas and require fresh CI/review after synchronization. This document supplies dependency constraints only.

## ANVIL — Development

Own new runtime implementation and review-returned defects after a bounded task is shaped. Do not implement planning candidates merely because they appear in this document.

## SENTINEL — Review

Independently verify exact heads it did not implement/synchronize. In particular, treat repaired-but-unmerged statuses here as claims to reproduce, not as approval.

## FOUNDRY — Planning / Control-Surface

Maintain roadmap/recovery reconciliation, shape missing bounded tasks, and inspect whether accepted/open work still matches roadmap intent. Avoid active runtime output paths and return concrete implementation tasks to ANVIL.

---

# 12. Snapshot limitations

This reconciliation is intentionally dated. It becomes stale whenever relevant `main` or PR state moves.

At the next planning pass:

1. recover current `main`;
2. re-read all agent coordination files;
3. re-check exact PR/base/head/review/CI for every stack being discussed;
4. move only truly merged capabilities to `ACCEPTED`;
5. preserve `UNKNOWN` rather than guessing from an old note;
6. update this document or create a newer dated reconciliation if material program state has changed.
