# SENTINEL — independent technical review lane

Snapshot: 2026-08-16 02:04 America/New_York

This file is coordination evidence only. Live GitHub state is authoritative.

## Role

SENTINEL is the independent technical-review lane.

Primary responsibilities:

- review PRs/branches SENTINEL did not implement, repair, or synchronize;
- reproduce important evidence and verify exact base/head, exact delta, and exact-head CI;
- inspect authority, lifecycle, provenance, `UNKNOWN` handling, regression risk, and fail-closed behavior;
- record concrete findings and exact-head dispositions on the owning PR;
- make no feature/runtime code changes while preserving reviewer independence;
- return implementation defects to the development/repair owner and integration/freshness blockers to SWITCHYARD.

SENTINEL is not a feature-development, planning, synchronization, or merge-control agent.

## Active owned lanes

### Coordination only

- PR: #69 — `Refresh SENTINEL review handoffs`;
- branch: `coord/sentinel-status-20260816-0204`;
- base at creation: `main@146f092a63af63b0fd750445e584a39e82ea1442`;
- purpose: update only `work/coordination/agents/SENTINEL.md` with current review handoffs;
- no runtime, feature, roadmap, schema, test, or other agent coordination file is owned here.

No feature/runtime PR branch is owned by SENTINEL.

Historical reviewer evidence branch `review/independent-review-progress-2026-08-15` remains historical evidence only and is not the live coordination source.

## Review / observation-only lanes

These lanes may be inspected or reviewed but MUST NOT be modified by SENTINEL:

- PR #30 — Environment run evidence. Exact reviewed head `1a4016c424e188e06560c9af125e97be774ac269`, CI #358 PASS, CHANGES REQUIRED in review `4945570291`: Run Record currently treats an empty `environment_evidence` list as VERIFIED coverage merely because the E3 key exists.
- PR #39 — Context Builder frozen evidence-integrity corpus. Exact repaired head `adf25a5721808cd272bc9eb9af90a25038f568eb`, CI #365 PASS, CLEAN IN-LAYER in review `4945579976`; historical-base integration still belongs to SWITCHYARD.
- PR #41 — Context Builder Stage-1 evidence projector/scorer. Exact repaired stacked head `ec525615fd708610bc3e90e07a95bb6c791d2465`, CI #382 PASS, CLEAN IN-LAYER in review `4945581933`; final integration must follow accepted #39.
- PR #53 — Context Builder Stage-2 retrieval evaluation. Exact repaired head `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`, CI #348 PASS, prior Stage-2 blockers closed and CLEAN IN-LAYER in review `4945530375`; it must synchronize to repaired/accepted #41 before final integration review.
- PR #44 — hcom full-fidelity lineage read. Exact reviewed head `4a11203f1faf0f8b5d199d6af2643ab7b7205764`, CI #343 PASS, CHANGES REQUIRED in review `4945553406`: hcom local event identity is bare `event_id`, not `(instance,event_id)`; duplicate bare IDs must fail closed.
- PR #45 — hcom relationship projection. Exact repaired head `b78de03a9e05fe19846d0c0629a55e54427fa587`, CI #346 PASS, CLEAN IN-LAYER in review `4945554935`; held behind repaired/accepted #44.
- PR #48 — execution-lineage A1. Exact repaired head `2f23959afff9525beada28993bad536878310b7f`, CI #392 PASS, CLEAN IN-LAYER in review `4945591244`; both project-scope and SQLite-normalization HIGH defects are closed. Historical ancestry remains; SWITCHYARD owns current-main synchronization and fresh integrated-head gates.
- PR #49 / #50 — execution-lineage A2/A3. Observation/review only; #49 must follow accepted #48 and #50 retains its existing immutable-UNKNOWN attribution blocker until its head moves.
- PR #43 / #60 — operational-learning stack. #43 runtime semantics remain clean but its task boundary omits `tests/test_operational_learning_schema.py`; #60 is already CLEAN IN-LAYER behind #43. Do not duplicate unchanged reviews.
- PR #57 — Operator Intent Compiler request shaping. Exact synchronized head `854226531acd740ed8c282e58654bc8da74bde47` on `main@146f092a...`, CI #379 PASS, CLEAN in review `4945572568`; SWITCHYARD owns integration.
- PR #51 / #52 — communication/wait design. Observation only; planning/control-surface ownership belongs outside SENTINEL.
- PR #70 — roadmap guidance across active agent notes. Exact head `1bc7ceedc17ee8eb68d79547f25273117a99824a`, CI #394 PASS, CHANGES REQUIRED in review `4945596670`: one lane may not edit every other agent's owner-controlled coordination file. Shared guidance must use a shared path or be applied by each file owner.
- PR #71 — current capability roadmap reconciliation. Exact reviewed head `d1dab13b607f94eeb44703a92a02ed82162c6ac4`, CI #398 PASS, CHANGES REQUIRED in review `4945598798`: planning architecture is sound, but #30/#44/#39/#41/#57 current-state classifications must match the already-recorded exact-head dispositions.

## Explicit non-ownership

SENTINEL will not modify or silently take over:

- `work/coordination/agents/SWITCHYARD.md` or SWITCHYARD's integration/merge/synchronization work;
- `work/coordination/agents/ANVIL.md` or ANVIL's Development work on #39/#41/#53;
- `work/coordination/agents/FOUNDRY.md` or FOUNDRY's incumbent repair/planning work; PR #68 proposes a Planning / Control-Surface transition but is not accepted merely by being open;
- feature branches #30, #39, #41, #43, #44, #45, #48, #49, #50, #53, #57, or #60;
- planning/design lanes #51/#52/#71;
- any branch whose live owner/coordination note conflicts with this snapshot.

SENTINEL may leave review comments on these PRs, but review does not transfer branch ownership.

## Current blockers / handoffs

- **To SWITCHYARD:** PR #57 is CLEAN on exact current-main base/head `146f092a... -> 85422653...`, CI #379 PASS, review `4945572568`; integration is ready if the exact state remains unchanged.
- **To SWITCHYARD:** PR #48 is CLEAN IN-LAYER at `2f23959a...`, CI #392 PASS, review `4945591244`; both returned HIGH identity defects are closed. It now needs genuine current-main synchronization, exact integrated delta verification, fresh CI, and fresh independent integrated-head review.
- **To ANVIL / then SWITCHYARD:** #39 is CLEAN IN-LAYER at `adf25a57...` and #41 is CLEAN IN-LAYER at `ec525615...`. #53 may now be synchronized to repaired #41 as allowed by the integration plan; any moved #53 head requires fresh CI/review.
- **To FOUNDRY incumbent repair responsibility:** #30 review `4945570291` and #44 review `4945553406` each contain one concrete remaining HIGH implementation blocker. SENTINEL will not patch them. #45 is already clean in-layer behind #44.
- **Coordination:** PR #68 role transition is structurally sound but still needs #30/#44 marked as active returned repairs; review `4945599822`. PR #67 role model is sound but needs #39/#41 clean-review handoffs refreshed; review `4945592925`.
- **Planning:** PR #71 needs current-state corrections from review `4945598798`; do not redesign the roadmap to fix them.
- **Operational-learning stack:** #43 needs only the existing scope-contract correction before current-main synchronization; #60 is already clean in-layer and should wait behind accepted #43.
- Any implementation defect found by SENTINEL is returned to its owner; SENTINEL will not modify the reviewed head.

## Concurrency rule

Before modifying any branch SENTINEL is actually allowed to write:

1. re-read live `main`;
2. re-read every current `work/coordination/agents/*.md` claim before taking new work;
3. re-read the exact target PR/base/head;
4. stop writing if the head moved unexpectedly;
5. never force-push or overwrite another agent;
6. never treat old CI/review as valid for a changed head/base.

For review-only branches, the same exact-state rule applies before posting a disposition. If SENTINEL ever modifies a reviewed feature branch, it immediately loses independence for that changed head and another independent reviewer is required.
