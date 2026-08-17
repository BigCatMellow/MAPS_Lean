# Roadmap: TOWER dispatch checkpoint — 2026-08-16

- State: `WORKING`
- Semantics: `DERIVED_AS_OF_CHECKPOINT`
- Checkpoint accepted main: `c4c93e52edd961802c7c203035f0bc272f196b59`

## Checkpoint rule

This roadmap records a verified routing snapshot. It is **not** a second live task/PR/review database. Later GitHub movement automatically supersedes this checkpoint for action; future agents must re-read live GitHub rather than editing historical facts merely to keep this snapshot looking current.

## Current reality at checkpoint

- `VERIFIED` — accepted foundations: #30, #39, #44, #45, #48.
- `VERIFIED` — #41 exact current-main head `6e4d59b2a5d8a9650af83b867f10becfdcb48de3`, Runtime CI #485 PASS, SENTINEL-C `CLEAN INTEGRATED-HEAD`; next role SWITCHYARD expected-head merge gate; #53 still blocked until actual merge/acceptance.
- `VERIFIED` — #49 historical head `ed865be729cf2d15663258fd46c9296ea32d28e7`; SWITCHYARD explicitly released a genuine rebuild to FOUNDRY on accepted #48/A1/latest main; #50 blocked until #49 acceptance.
- `VERIFIED` — #70 exact current-main head `fe5119c2977e21009f7cfeb3e9befb3adb5c0db7`, Runtime CI #487 PASS, SENTINEL-A advisory claim active at checkpoint.
- `VERIFIED` — #71 exact current-main head `71a9d7a51086c6a4b3a6aa0c48bd826310eadd0d`, Runtime CI #490 PASS, SENTINEL-C advisory claim active at checkpoint.
- `VERIFIED` — #73 exact current-main head `f3f182e8fb11102a0d2674fa0f5001dc5113bec2`, Runtime CI #493 PASS; prior old-base CLEAN review is stale; no current exact-head claim observed at checkpoint.
- `VERIFIED` — #43 has a narrow scope-contract repair only but unresolved development ownership; ANVIL explicitly declined ownership because no transfer exists; #60 blocked until #43 acceptance.
- `VERIFIED` — #67/#68/#69 remain owner-controlled coordination freshness work.
- `VERIFIED` — #51/#52 remain planning/design only and create no runtime wait authority.

## Sources of truth

1. operator / policy authority;
2. canonical MAPS task and ownership state;
3. live GitHub repository, PR, review, CI, and branch evidence;
4. this checkpoint only as derived routing evidence.

## Definition of DONE for this checkpoint

- [x] live main recovered;
- [x] AGENTS.md, coordination README, and proposed #73 protocol read;
- [x] current product and coordination frontiers recovered from live GitHub;
- [x] downstream holds expressed from actual acceptance dependencies;
- [x] unresolved #43 ownership preserved as UNKNOWN rather than guessed;
- [x] no other role's owner-controlled note modified;
- [x] only three TOWER files changed;
- [ ] fresh exact-head #72 CI passes after this final checkpoint write;
- [ ] eligible independent review of this exact #72 checkpoint;
- [ ] if clean, SWITCHYARD handles any then-current main synchronization/integration.

## Boundaries

### In scope

- derived NOW/NEXT/BLOCKED/PARKED checkpoint;
- dependency release conditions;
- routing among already-authorized roles;
- explicit UNKNOWN ownership/authority blockers;
- TOWER-owned planning files/comments.

### Out of scope

- runtime implementation;
- independent review by TOWER;
- synchronization/merge by TOWER;
- cross-owner coordination-note edits;
- inventing #43 ownership;
- speculative infrastructure.

## First wave at checkpoint

- [ ] `#41` — SWITCHYARD expected-head merge gating on CLEAN exact head `6e4d59b2...`.
- [ ] `#49` — FOUNDRY genuine A2 rebuild on accepted A1/latest main.
- [ ] `#70` — SENTINEL-A exact-head review of `fe5119c2...`.
- [ ] `#71` — SENTINEL-C exact-head review of `71a9d7a5...`.
- [ ] `#73` — eligible SENTINEL exact-head review of `f3f182e8...`.
- [ ] `whole backlog` — SWITCHYARD keeps persistent PR-control scan active.

## Accepted foundations

- [x] #30
- [x] #39
- [x] #44
- [x] #45
- [x] #48

## Product frontier

### Context Builder

- [x] #41 current-main synchronization.
- [x] #41 Runtime CI #485 PASS.
- [x] #41 independent CLEAN integrated-head review.
- [ ] SWITCHYARD expected-head merge gate.
- [ ] only after accepted #41: rebuild #53, preserve Stage-2 evaluation-only scope, strict source precision and exact `overlay_sha256`, fresh CI/review/integration.

### Execution lineage

- [ ] #49 FOUNDRY rebuild on accepted #48/A1/latest main.
- [ ] exact intended A2 delta + fresh Runtime CI + independent exact-head review + SWITCHYARD integration.
- [ ] only after accepted #49: repair/rebuild #50.

### Operational learning

- [ ] resolve #43 owner from operator/canonical evidence.
- [ ] legitimate owner performs bounded change-contract repair unless new evidence returns substantive defect.
- [ ] fresh CI/review/integration.
- [ ] only after accepted #43: rebuild/review/integrate #60.

## Coordination/protocol frontier

- [x] #70 current-main synchronization.
- [x] #70 Runtime CI #487 PASS.
- [ ] #70 SENTINEL-A review; then SWITCHYARD if clean.
- [x] #71 current-main synchronization.
- [x] #71 Runtime CI #490 PASS.
- [ ] #71 SENTINEL-C review; then SWITCHYARD if clean.
- [x] #73 current-main synchronization to `f3f182e8...`.
- [x] #73 Runtime CI #493 PASS.
- [ ] #73 fresh independent exact-head review; then SWITCHYARD if clean.
- [ ] #67 ANVIL owner-note freshness repair.
- [ ] #68 FOUNDRY owner-note freshness repair preserving FOUNDRY development role.
- [ ] #69 SENTINEL owner-note refresh.

## PARKED / design-only

- [ ] #51 exact task/run ↔ hcom event correlation design.
- [ ] #52 evidence-backed wait design stacked on #51.

No runtime communication-response wait inference from provider silence, timestamps, identity coincidence, text, or same-thread traffic.

## Checkpoints

### #41

Exact base/head/CI/review are clean. Release #53 only after actual accepted merge.

### #49

Rebuild must preserve accepted A1 and every newer accepted-main change; do not carry the historical A2 tree forward unchanged.

### #70 / #71 / #73

Review only exact current-main synchronized heads. Claims are duplicate-work hints only, never review authority.

### #43 ownership

No explicit binding means no mutation. Idle capacity is not permission.

## Future refresh rule

A later TOWER session should create/record a new live checkpoint when routing value justifies it. Do not treat this dated checkpoint as canonical live truth or rewrite another role's state to match it.

## Core rule

**TOWER decides what is worth attempting next from a derived view. SENTINEL decides whether evidence survives independent testing. SWITCHYARD decides what is safe to integrate. The operator resolves authority evidence cannot.**
