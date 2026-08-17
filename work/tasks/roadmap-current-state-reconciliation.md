# Task: current capability roadmap reconciliation

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `FOUNDRY / Planning-Control-Surface`
- Risk: `MEDIUM`
- Goal: record a truthful dated capability checkpoint and reconcile legacy candidates without turning roadmap prose into runtime, review, merge, or promotion authority.

## Sources of truth

Evidence order:
1. root `AGENTS.md`;
2. live GitHub `main`, exact PR/base/head/review/CI, merged code/tests, canonical MAPS state;
3. current coordination notes for collision avoidance only;
4. accepted task/decision evidence;
5. roadmaps and migration audits/backlog as design/history evidence.

Snapshot checkpoint fixed by this revision:

`main@fc523891d069d5e4c668f4eda0ab3cb86aa3f714`

Later GitHub movement supersedes this snapshot for action but does not make its as-of-checkpoint statements false. Do not churn this planning PR after every rapid integration merge merely to mimic live GitHub.

## Change boundary

Only:
- this task file;
- `work/roadmaps/current-capability-reconciliation-2026-08-16.md`;
- the existing `work/roadmaps/README.md` index edit in this PR.

No runtime, tests, schema/state, provider behavior, feature branch, review disposition, merge, or other agent coordination file may change here.

## Authority / invariants

FOUNDRY may derive planning classifications and dependency constraints from verified evidence. FOUNDRY may not accept unmerged work, choose integration priority, self-approve, promote legacy candidates, or invent architecture for roadmap completeness.

Preserve:
- one fact / one authority;
- capability != authority;
- source evidence > summaries;
- UNKNOWN when evidence is insufficient;
- green CI != semantic clearance;
- clean feature head != merged capability;
- synchronized heads need exact integrated review;
- dependency != merge priority;
- no self-authorizing learning/promotion.

## Acceptance criteria

- [x] #19/Prime Phase 0 represented as historical/complete;
- [x] Harness #20–#24 separated from open lineage;
- [x] Skills #25–#27/#31 separated from automatic routing/promotion;
- [x] Environment #28/#29/#30 represented as accepted evidence without recovery authority;
- [x] review subject #32 and Run Record/evals #33–#35 represented without complete-replay claims;
- [x] wait subset #59 represented without communication-response/scheduler authority;
- [x] Operator Intent Compiler #57 represented as accepted shaping, not action authority;
- [x] Context Builder frozen evidence-integrity #39 represented as accepted evaluation input, not production retrieval;
- [x] dependency stacks explicit: #48→#49→#50, #44→#45, #39→#41→#53, #43→#60;
- [x] #51/#52 remain planning-only;
- [x] legacy candidates classified rather than revived wholesale;
- [x] no runtime/schema/test files modified.

## Verified checkpoint state

### Accepted main

Snapshot main `fc523891d069d5e4c668f4eda0ab3cb86aa3f714` includes:
- PR #57 Operator Intent Compiler request shaping;
- PR #39 Context Builder evidence-integrity foundation, synchronized head `5928abe4550dbf7a75c2a2825e3cda5033ead830`, CI #422 PASS, SENTINEL CLEAN integrated-head review;
- PR #30 append-only run environment evidence, synchronized head `4e158f65a422f14d7d12b2b1b8b0297e9f3ca5d7`, CI #442 PASS, SENTINEL CLEAN integrated-head review.

#30 preserves empty evidence as MISSING, separates source availability from evidence presence, and creates no task/run/recovery/policy/review/operator authority.

### Execution lineage

- #48 `2f23959afff9525beada28993bad536878310b7f`, CI #392 PASS, SENTINEL CLEAN IN-LAYER; `OPEN_INTEGRATION` at checkpoint.
- #49 `ed865be729cf2d15663258fd46c9296ea32d28e7`; no A2-specific blocker on historical ancestry, but rebuild required after accepted #48.
- #50 actual head `832fa4ab2c3e97a8f7cdc22a73baca0d276adfc0`; exact-head CI #274 failed. Immutable UNKNOWN-at-submission and active-runtime `legacy/` token defects remain. Ignore misleading later green-run claims tied to non-resolving/other-PR SHAs.

### Communication lineage

- #44 `6f2b774eee27a0596820b12f080bfd7e60c0f50e`, CI #419 PASS, SENTINEL CLEAN IN-LAYER / FEATURE-HEAD ONLY. Bare local event ID is the configured-store identity; instance is metadata. `OPEN_INTEGRATION` at checkpoint.
- #45 `b78de03a9e05fe19846d0c0629a55e54427fa587`, CI #346 PASS, SENTINEL CLEAN IN-LAYER; blocked until accepted #44 and rebuild/synchronization.

### Context Builder

- #39 is `ACCEPTED` in snapshot main.
- #41 `ec525615fd708610bc3e90e07a95bb6c791d2465`, CI #382 PASS, SENTINEL CLEAN IN-LAYER; with #39 accepted, checkpoint state `OPEN_INTEGRATION` for rebuild/synchronization + fresh gates.
- #53 `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`, CI #348 PASS, own layer clean; blocked until accepted #41.

### Operational learning

- #43 `aeecf1b5775db1d5ac2484819620f476752f3654`: substantive runtime/authority semantics reviewed clean, but declared scope omitted the schema-test path; bounded scope-contract repair remains.
- #60 `cfd758aace44970e7400c005c337be040d367918`, CI #307 PASS, independent CLEAN IN-LAYER; downstream of #43.

### Communication/wait design

#51/#52 remain `PLANNING_ONLY`. Exact provider event receipt/collision-safe correlation remains prerequisite evidence for communication-response lineage. Request + bounded silence does not prove WAITING.

## Legacy reconciliation

Re-read:
- `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`;
- `migration/FUTURE_IDEAS_BACKLOG.md`.

Preserve the governing rule: keep observed problems, invariants, evidence, experiments, and useful techniques; classify as absorbed, partially represented/open, or evidence-triggered; do not revive a legacy subsystem simply because it existed.

## Verification / review

The planning branch remains historical relative to snapshot main; FOUNDRY does not perform integration synchronization. Original-base delta must remain exactly the three declared planning/task paths.

All #71 CI/review evidence before the final checkpoint head is stale. Require:
1. fresh Runtime CI on the final exact head;
2. independent SENTINEL review of snapshot accuracy and authority boundaries;
3. SWITCHYARD synchronization/integration only after clean review.

Reviewer should verify the artifact explicitly behaves as an as-of-main checkpoint rather than a competing mutable live-status database.

Review required: `INDEPENDENT_REVIEW`.
FOUNDRY cannot self-approve.

## Stop / escalate

Stop rather than guess if checkpoint evidence cannot be reproduced, ownership is ambiguous, or roadmap neatness would require new authority/implementation. Route general runtime implementation to ANVIL, integration to SWITCHYARD, independent review to SENTINEL, and only explicit incumbent repair returns to FOUNDRY.