# Task: current capability roadmap reconciliation

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `FOUNDRY / Planning-Control-Surface`
- Risk: `MEDIUM`
- Goal: reconcile current accepted/open capability state and legacy-recovery candidates without converting roadmap prose into runtime, review, merge, or promotion authority.

## Sources of truth

Use this order:

1. root `AGENTS.md`;
2. live GitHub `main`, exact PR/base/head/review/CI, merged code/tests, canonical MAPS state;
3. `work/coordination/agents/*.md` for collision avoidance only;
4. accepted task/decision evidence;
5. roadmaps and migration audits/backlog as non-authoritative design/history evidence.

Current snapshot: `main@8397cbc2941a706440cabd0ffb93cac4ab1bdf6d`.

## Change boundary

Only:
- this task file;
- `work/roadmaps/current-capability-reconciliation-2026-08-16.md`;
- the existing `work/roadmaps/README.md` index edit in this PR.

No runtime, tests, schema/state, provider behavior, feature branch, review disposition, merge, or other agent coordination file may be changed here.

## Authority / invariants

FOUNDRY may derive planning classifications and dependency constraints from verified live evidence. FOUNDRY may not accept unmerged work, choose integration priority, independently approve its own work, promote legacy candidates, or invent architecture to make the roadmap complete.

Preserve:
- one fact / one authority;
- capability != authority;
- source evidence > summaries;
- UNKNOWN when evidence is insufficient;
- green CI != semantic clearance;
- feature-head CLEAN != merged capability;
- synchronized head requires its own exact-head review;
- dependency != merge priority;
- no self-authorizing learning/promotion.

## Acceptance criteria

- [x] merged #19/Phase-0 foundation is historical/accepted, not pending;
- [x] accepted Harness #20–#24 separated from open lineage work;
- [x] accepted Skills #25–#27/#31 separated from future automatic routing/promotion;
- [x] Environment #28/#29 separated from unmerged #30 and recovery authority;
- [x] review-subject #32 and Run Record/eval #33–#35 represented without complete-replay claims;
- [x] wait subset #59 represented without communication-response/scheduler authority;
- [x] Operator Intent Compiler #57 represented as accepted shaping, not consequential-action authority;
- [x] Context Builder evidence-integrity #39 represented as accepted evaluation input, not production retrieval;
- [x] dependency stacks remain explicit: #48→#49→#50, #44→#45, #39→#41→#53, #43→#60;
- [x] #51/#52 remain planning-only;
- [x] legacy candidates classified rather than automatically revived;
- [x] no runtime/schema/test files modified.

## Live verification — latest refresh

### Accepted main

Current main is `8397cbc2941a706440cabd0ffb93cac4ab1bdf6d` after exact reviewed/tested PR #39 merged. PR #57 is also already accepted in this ancestry.

### Environment — #30

SWITCHYARD synchronized the independently clean feature layer after #39 merged:
- base `main@8397cbc2941a706440cabd0ffb93cac4ab1bdf6d`;
- head `4e158f65a422f14d7d12b2b1b8b0297e9f3ca5d7`;
- Runtime CI #442 / `31965641572` PASS.

Prior feature repair closed the empty-environment-evidence VERIFIED defect. The synchronized head now needs fresh independent exact-head review. Planning state: `OPEN_REVIEW`.

### Execution lineage — #48/#49/#50

- #48 `2f23959afff9525beada28993bad536878310b7f`, CI #392 PASS, SENTINEL CLEAN IN-LAYER; historical ancestry, `OPEN_INTEGRATION`.
- #49 `ed865be729cf2d15663258fd46c9296ea32d28e7`; no A2-specific blocker on historical ancestry, but must be rebuilt after accepted #48.
- #50 actual head `832fa4ab2c3e97a8f7cdc22a73baca0d276adfc0`; exact-head CI #274 failed. Two A3 blockers remain: immutable UNKNOWN-at-submission must be recorded rather than a backfillable absence, and active-runtime `legacy/` wording trips the removal gate. Do not rely on PR-body green-run claims tied to non-resolving/other-PR SHAs.

### Communication — #44/#45

- #44 repaired head `6f2b774eee27a0596820b12f080bfd7e60c0f50e`, CI #419 PASS; SENTINEL now `CLEAN IN-LAYER / FEATURE-HEAD ONLY / NOT INTEGRATION-READY`. Bare local event ID is the configured-store identity; instance remains metadata. Planning state: `OPEN_INTEGRATION`.
- #45 `b78de03a9e05fe19846d0c0629a55e54427fa587`, CI #346 PASS, SENTINEL CLEAN IN-LAYER; still `BLOCKED_UPSTREAM` until accepted #44 and rebuild/synchronization.

### Context Builder — #39/#41/#53

- #39 synchronized head `5928abe4550dbf7a75c2a2825e3cda5033ead830` passed CI #422 and SENTINEL CLEAN integrated-head review, then merged as current `main@8397cbc2...`; state `ACCEPTED`.
- #41 `ec525615fd708610bc3e90e07a95bb6c791d2465`, CI #382 PASS, SENTINEL CLEAN IN-LAYER. With #39 now accepted, its remaining work is rebuild/synchronization onto accepted ancestry + fresh CI/review: `OPEN_INTEGRATION`.
- #53 `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`, CI #348 PASS and own-layer review clean; remains `BLOCKED_UPSTREAM` until #41 acceptance/rebuild.

### Operational learning — #43/#60

- #43 `aeecf1b5775db1d5ac2484819620f476752f3654`: substantive runtime/authority review clean, but declared task/PR scope omitted `tests/test_operational_learning_schema.py`; `OPEN_REPAIR` for that bounded contract issue.
- #60 `cfd758aace44970e7400c005c337be040d367918`, CI #307 PASS, independent CLEAN IN-LAYER; `BLOCKED_UPSTREAM` behind #43.

### Communication/wait design

#51 and #52 remain `PLANNING_ONLY`; exact provider send receipt/correlation is still a prerequisite for communication-response evidence, and request + bounded silence does not prove WAITING.

## Legacy reconciliation

Re-read:
- `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`;
- `migration/FUTURE_IDEAS_BACKLOG.md`.

Preserve their governing rule: retain observed problems, invariants, evidence, experiments, and useful techniques; classify candidates as absorbed, partially represented/open, or evidence-triggered; do not revive a legacy subsystem merely because it existed.

## Verification / review

The planning branch remains intentionally historical relative to current main; FOUNDRY does not perform integration synchronization. Exact original-base delta must remain limited to the three declared planning/task paths.

All #71 CI/review evidence before the final factual-refresh head is stale. Require:
1. fresh Runtime CI on the final exact planning head;
2. independent SENTINEL review of factual classifications/authority boundaries;
3. SWITCHYARD synchronization/integration only after clean review.

Reviewer should especially verify #39 ACCEPTED, #30 synchronized/review-pending, #44 clean feature/integration-pending, #41 now integration-pending rather than upstream-blocked, and no unmerged work promoted to ACCEPTED.

Review required: `INDEPENDENT_REVIEW`.
FOUNDRY cannot self-approve.

## Stop / escalate

Stop rather than guess if live state invalidates a material claim, ownership becomes ambiguous, or roadmap neatness would require new authority/implementation. Route general runtime implementation to ANVIL, integration to SWITCHYARD, independent review to SENTINEL, and only explicit incumbent repair returns to FOUNDRY.