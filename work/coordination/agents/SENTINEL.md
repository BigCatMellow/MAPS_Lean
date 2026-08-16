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
- return implementation defects to the development owner and integration/freshness blockers to SWITCHYARD.

SENTINEL is not a feature-development, planning, synchronization, or merge-control agent.

## Active owned lanes

### Coordination only

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
- PR #53 — Context Builder Stage-2 retrieval evaluation. Exact repaired head `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`, CI #348 PASS, prior Stage-2 blockers closed and CLEAN IN-LAYER in review `4945530375`; it must synchronize to accepted/repaired #41 before final integration review.
- PR #44 — hcom full-fidelity lineage read. Exact reviewed head `4a11203f1faf0f8b5d199d6af2643ab7b7205764`, CI #343 PASS, CHANGES REQUIRED in review `4945553406`: hcom local event identity is bare `event_id`, not `(instance,event_id)`; duplicate bare IDs must fail closed.
- PR #45 — hcom relationship projection. Exact repaired head `b78de03a9e05fe19846d0c0629a55e54427fa587`, CI #346 PASS, CLEAN IN-LAYER in review `4945554935`; held behind repaired/accepted #44.
- PR #48 — execution-lineage A1. Exact reviewed repair head `a9284c1a00fc42eb26807ea01e8ca667aaa5ebac`, CI #386 PASS, CHANGES REQUIRED in review `4945577113`: project-scoped identity is conceptually correct, but raw SQLite uniqueness can be bypassed by trim-equivalent direct-SQL identity variants.
- PR #49 / #50 — execution-lineage A2/A3. Observation/review only; #49 remains downstream of #48 and #50 retains its existing immutable-UNKNOWN attribution blocker until its head moves.
- PR #43 / #60 — operational-learning stack. #43 runtime semantics remain clean but its task boundary omits `tests/test_operational_learning_schema.py`; #60 is already CLEAN IN-LAYER behind #43. Do not duplicate unchanged reviews.
- PR #57 — Operator Intent Compiler request shaping. Exact synchronized head `854226531acd740ed8c282e58654bc8da74bde47` on `main@146f092a...`, CI #379 PASS, CLEAN in review `4945572568`; SWITCHYARD owns integration.
- PR #51 / #52 — communication/wait design. Observation only; planning/control-surface ownership belongs outside SENTINEL.

## Explicit non-ownership

SENTINEL will not modify or silently take over:

- `work/coordination/agents/SWITCHYARD.md` or SWITCHYARD's integration/merge/synchronization work;
- `work/coordination/agents/ANVIL.md` or ANVIL's Development work on #39/#41/#53;
- `work/coordination/agents/FOUNDRY.md` or FOUNDRY's planning/control-surface work and incumbent repair-return responsibility;
- feature branches #30, #39, #41, #43, #44, #45, #48, #49, #50, #53, #57, or #60;
- planning/design lanes #51/#52;
- any branch whose live owner/coordination note conflicts with this snapshot.

SENTINEL may leave review comments on these PRs, but review does not transfer branch ownership.

## Current blockers / handoffs

- **To SWITCHYARD:** PR #57 is CLEAN on exact current-main base/head `146f092a... -> 85422653...`, CI #379 PASS, review `4945572568`; integration is ready if the exact state remains unchanged.
- **To ANVIL / then SWITCHYARD:** #39 is CLEAN IN-LAYER at `adf25a57...` and #41 is CLEAN IN-LAYER at `ec525615...`. ANVIL may now synchronize #53 onto repaired #41; SWITCHYARD must serialize current-main integration in dependency order with fresh integrated-head CI/review.
- **To FOUNDRY repair-return responsibility:** #30 review `4945570291`, #44 review `4945553406`, and #48 review `4945577113` each contain one concrete remaining HIGH blocker. SENTINEL will not patch them. #45 is already clean in-layer behind #44.
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
