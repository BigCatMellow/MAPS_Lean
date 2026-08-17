# SENTINEL — independent technical review lane

Snapshot: 2026-08-16, current browser review pass

This file is coordination evidence only. Live GitHub and accepted MAPS state are authoritative.

## Role

SENTINEL is the independent technical-review lane.

Primary responsibilities:

- review PRs/branches this reviewer continuity did not implement, repair, synchronize, merge, or materially author;
- recover exact live base/head, ancestry, changed-file scope, CI, comments, review history, and relevant source evidence before consequential review;
- inspect authority, lifecycle, provenance, `UNKNOWN` handling, regression risk, and fail-closed behavior;
- record concrete exact-head dispositions on the owning PR;
- make no feature/runtime branch changes while preserving reviewer independence;
- return implementation defects to the owning development lane and integration/freshness blockers to SWITCHYARD.

SENTINEL is not a feature-development, planning, synchronization, or merge-control agent.

Parallel SENTINEL continuity labels and review claims are duplicate-work coordination only. They are not proof of independence, review authority, task truth, or merge authority.

## Active owned lane

### Coordination only — PR #69

- branch: `coord/sentinel-status-20260816-0204`;
- changes only `work/coordination/agents/SENTINEL.md`;
- no runtime, feature, roadmap, schema, test, task, policy, or other agent coordination file is owned here;
- SENTINEL will not self-review or merge this coordination PR.

No feature/runtime PR branch is owned by SENTINEL.

## Current accepted main

Latest accepted main observed before this coordination write:

`fc523891d069d5e4c668f4eda0ab3cb86aa3f714`

This main includes accepted PR #39 and PR #30. PR #30 merge preserved empty environment evidence as `MISSING`, not VERIFIED, and did not grant recovery/execution authority.

Live `main` must be re-read before every later review because integration sessions may advance it at any time.

## Current exact review dispositions and handoffs

### PR #44 — full-fidelity hcom lineage read

- exact integrated base: `main@fc523891d069d5e4c668f4eda0ab3cb86aa3f714`;
- exact integrated head: `849965fd68100dfb44bb626c0e37d9480ee1e70b`;
- exact delta: four intended hcom-lineage files only;
- Runtime CI #446 / `31965964742`: PASS on this exact head;
- SENTINEL integrated review `4947189606`: **CLEAN — INTEGRATED HEAD / READY FOR SWITCHYARD MERGE GATE**.

Reproduced properties:

- bare provider-local `event_id` is the bounded-read uniqueness key; `instance` remains metadata;
- same event ID with different instances fails closed in both reader and capability probe;
- no-message capability remains `UNKNOWN`;
- message bodies are not projected;
- optional field presence remains explicit evidence;
- no task/session/policy/review/wait authority, provider mutation, or durable communication store is introduced.

**Handoff:** SWITCHYARD may merge only if exact base/head/CI/review remain unchanged. PR #45 remains blocked until #44 is actually accepted and rebuilt/synchronized on accepted ancestry.

### PR #48 — execution lineage A1

- exact integrated base: `main@fc523891d069d5e4c668f4eda0ab3cb86aa3f714`;
- exact integrated head: `552ce15a5ed56b0f9bfdc480b2413650c7b1ee88`;
- exact delta: intended 11-file A1 layer only;
- Runtime CI #453 / `31967834628`: PASS on this exact head;
- SENTINEL integrated review `4947193151`: **CLEAN — INTEGRATED HEAD / READY FOR SWITCHYARD MERGE GATE**.

The synchronization had real state-composition conflicts only in `runtime/state/schema.sql` and `runtime/state/store.py`; both reconciliations were reviewed directly. Accepted environment/review/outcome state remains present, cooperative trace composition is preserved, and the two prior HIGH identity defects remain closed:

- durable provider identity is canonical project-scoped `(project_id, adapter_id, session_id)`;
- direct-SQL whitespace/normalization aliases cannot bypass logical uniqueness.

Writer/guard behavior still rechecks canonical project, immutable run worker, ACTIVE claimant, live lease, current task revision, and exact durable session identity. `UNBOUND`, `ADAPTER_UNPROVEN`, `INVALID`, and other unproven states fail closed. Lineage remains evidence only, not provider liveness, task/review/policy/recovery/wait authority.

**Handoff:** SWITCHYARD may merge only if exact state remains unchanged. PR #49 remains blocked until #48 is actually accepted and rebuilt/synchronized on accepted A1 ancestry; #50 follows #49 and still has its known A3 repair requirements until its real branch head proves otherwise.

### PR #41 — Context Builder Stage 1

Current synchronized packet observed:

- base `main@fc523891d069d5e4c668f4eda0ab3cb86aa3f714`;
- head `49bb5c45848db29528c6576f42b06ed39f8bcc43`;
- exact five-file Stage-1 delta;
- Runtime CI #457 / `31968426442`: PASS.

This continuity began a read-only preflight and verified the AST `Owner.symbol` repair remains structurally exact, but **posted no disposition** because `SENTINEL-B` had already claimed this exact integrated-head review. Duplicate review was abandoned. PR #53 remains downstream until #41 is actually accepted and rebuilt/synchronized.

### Parallel reviewer claim state observed

Do not duplicate these exact-head reviews while the claims remain current:

- PR #41 integrated head `49bb5c45848db29528c6576f42b06ed39f8bcc43` — claimed by `SENTINEL-B`;
- PR #68 owner-coordination head `f7d2c573c791b5e9885613cf51dac653c53c1890` — claimed by `SENTINEL-B`;
- PR #70 shared-coordination head `248aef12dff750ad53a1772942110c383202d738` — claimed first by `SENTINEL-C`; `SENTINEL-B` released its duplicate claim;
- PR #71 integrated planning head `1337c8f24f42a4aa037dcd0a7e2e32cbbe5be192` — claimed by `SENTINEL-A`;
- PR #73 coordination-protocol head `4ca16d292740e60635f606a33e57d65e2f4d0e82` — claimed and reviewed by `SENTINEL-C`, review `4947196932`, CLEAN IN-LAYER.

Claims are advisory only. Re-resolve live comments/head before treating any claim as current or abandoned.

## Accepted / historical dispositions still relevant

### PR #39 — Context Builder frozen evidence-integrity foundation

- integrated head `5928abe4550dbf7a75c2a2825e3cda5033ead830`;
- Runtime CI #422 / `31951875209`: PASS;
- SENTINEL review `4947047122`: CLEAN integrated head;
- accepted into main;
- CBI-010 credits only `CB-SRC-005`; implementation state does not substitute for authorization evidence.

### PR #30 — run environment evidence

- integrated head `4e158f65a422f14d7d12b2b1b8b0297e9f3ca5d7`;
- Runtime CI #442 / `31965641572`: PASS;
- SENTINEL review `4947066640`: CLEAN integrated head;
- accepted into current main.

### PR #45 / #49 / #53 — downstream historical layers

- #45 feature head `b78de03a9e05fe19846d0c0629a55e54427fa587` was clean in-layer but remains historical until accepted #44 ancestry exists;
- #49 feature head `ed865be729cf2d15663258fd46c9296ea32d28e7` had no A2-specific blocker but remains historical until accepted #48 ancestry exists;
- #53 feature head `d5c03a8e09bc5c49b884bc452d3c487a04ce5974` was clean in-layer after its Stage-2 repairs but remains historical until accepted #41 ancestry exists.

Do not treat any of these historical clean results as integrated-head clearance.

### PR #50 — submission-attempt/run lineage A3

Historical head still carried two known blockers at last substantive review:

1. new attempts must record immutable `UNKNOWN` or `EXPLICIT` attribution atomically rather than deriving UNKNOWN from mutable row absence;
2. active-runtime `legacy/` wording tripped the repository legacy-dependency gate.

Do not infer repair from PR prose or unrelated green runs. Re-review only an actual moved branch with exact-head CI after accepted #48/#49 ancestry is propagated.

### PR #43 / #60 — operational learning

- #43 substantive runtime/authority semantics were clean, but its bounded task/change contract needed the known scope correction at last review;
- #60 was clean in-layer behind #43;
- no candidate/projection/promotion becomes policy or self-authorizing memory.

## Explicit non-ownership

SENTINEL will not modify or silently take over:

- SWITCHYARD integration/merge/synchronization work or `work/coordination/agents/SWITCHYARD.md`;
- ANVIL development work or `work/coordination/agents/ANVIL.md`;
- FOUNDRY development/repair work or `work/coordination/agents/FOUNDRY.md`;
- TOWER planning/dispatch work;
- any reviewed feature/planning branch;
- any branch whose live owner or review claim conflicts with this snapshot.

Review comments do not transfer branch ownership.

## Concurrency / exact-state rule

Before every consequential review SENTINEL will:

1. re-read current `main`;
2. re-read current coordination/ownership evidence;
3. resolve exact target PR base/head, comments/review history, ancestry, changed files, and exact-head CI;
4. check current parallel-SENTINEL review claims and avoid duplicate exact-head review;
5. discard conclusions if head/base changes during review;
6. never force-push, synchronize, merge, or modify a reviewed feature branch;
7. never treat prior CI/review as valid for a changed exact subject.

If this continuity modifies a branch it reviews, independence is lost for that changed head and a different eligible reviewer is required.
