# Roadmap: TOWER current multi-agent dispatch — 2026-08-16

- State: `WORKING`

## Current reality

### Checked facts

- `VERIFIED` — accepted `main` is `c4c93e52edd961802c7c203035f0bc272f196b59` after accepted #45.
- `VERIFIED` — accepted foundations include #30, #39, #44, #45, and #48.
- `VERIFIED` — #41 has been genuinely resynchronized by SWITCHYARD to current main at `6e4d59b2a5d8a9650af83b867f10becfdcb48de3`; Runtime CI #485 / `31976928359` PASS; SENTINEL-C has an advisory independent-review claim on that exact packet. #53 remains blocked until actual #41 acceptance.
- `VERIFIED` — #49 remains historical at `ed865be729cf2d15663258fd46c9296ea32d28e7`; SWITCHYARD explicitly released the rebuild to FOUNDRY on accepted #48/A1/latest main. #50 remains blocked until #49 acceptance.
- `VERIFIED` — #70 is resynchronized on current main at `fe5119c2977e21009f7cfeb3e9befb3adb5c0db7`; Runtime CI #487 / `31976981585` PASS; fresh independent review is now the next gate.
- `VERIFIED` — #71 is resynchronized on current main at `71a9d7a51086c6a4b3a6aa0c48bd826310eadd0d`; Runtime CI #490 / `31977031772` is running at this checkpoint; review becomes eligible only after exact-head PASS.
- `VERIFIED` — #73 remains at old head `7434b08e9343750f5d860070fa4005bcbf2da1e3`; SENTINEL-C's prior CLEAN review on `eccdddaa...` is explicitly stale after #45 acceptance. SWITCHYARD must resynchronize before fresh review.
- `VERIFIED` — #43 has a narrow scope-contract repair only; runtime semantics were independently clean. ANVIL explicitly declined ownership because no handoff binds it. #60 remains blocked until #43 acceptance.
- `VERIFIED` — #67/#68/#69 remain owner-controlled coordination freshness work.
- `VERIFIED` — #51/#52 remain planning/design only and create no runtime wait authority.

### Sources of truth

- root `AGENTS.md`;
- `work/coordination/README.md`;
- proposed PR #73 protocol until accepted;
- live GitHub PR/base/head/review/CI/comments;
- accepted MAPS state.

This roadmap is derived only and loses to those sources.

### Unknowns / decisions

- `UNKNOWN` — outcome of current #41 independent review.
- `UNKNOWN` — outcome of future #70/#71/#73 current-head reviews.
- `UNKNOWN` — whether #49 rebuild exposes integration defects.
- `UNKNOWN / OPERATOR BOUNDARY` — legitimate development continuity for #43 repair.

## Definition of DONE

This dispatch cycle is complete when:

1. #41 has exact current-head review/integration outcome;
2. #49 is genuinely rebuilt on accepted A1/latest main and has exact CI/review/integration evidence or concrete blocker;
3. #70/#71/#73 have current-main exact evidence and move through fresh review/integration gates;
4. #53/#50 release only after actual upstream acceptance;
5. #43 is explicitly assigned by legitimate authority or remains visibly blocked without invented ownership;
6. coordination owner-note work stays with its owners;
7. TOWER refreshes after material accepted-main movement.

## Boundaries

### In scope

- derived NOW/NEXT/BLOCKED/PARKED planning;
- dependency release conditions;
- role routing under existing authority;
- explicit unknown/ownership blockers;
- TOWER-owned planning files/comments.

### Out of scope

- feature/runtime implementation by TOWER;
- independent review by TOWER;
- synchronization/merge by TOWER;
- other agents' owner-controlled notes;
- assigning #43 without operator/canonical authority;
- speculative coordination machinery.

## Backward plan

1. Immediately before DONE, current dependency heads have exact proof and downstream releases reflect actual acceptance.
2. Before that, SENTINEL reviews immutable current packets; SWITCHYARD consumes clean results and resynchronizes after accepted main moves; FOUNDRY rebuilds #49.
3. Before that, accepted #45 advanced main and stale old integration packets were discarded rather than reused.
4. Current state: #41/#70 review throughput plus #49 development are executable bottlenecks; #71 waits only on fresh CI; #73 waits on SWITCHYARD resync; #43 is an ownership bottleneck.

## Mission/checkpoint result

- Required: `YES` — TOWER repeatedly re-read live state while concurrent lanes advanced.
- `ACCEPTED` — #41 resynchronization is complete; fresh review is now in progress.
- `ACCEPTED` — #70 resynchronization and exact-head CI are complete; fresh review is next.
- `ACCEPTED` — #71 resynchronization is complete; exact-head CI is in progress.
- `ACCEPTED` — #73 old CLEAN review remains stale; current-main resync is still required.
- `ACCEPTED` — #49 remains legitimate FOUNDRY parallel development.
- `REJECTED` — using superseded integration-head reviews as current merge authority.
- `REJECTED` — assigning #43 from idle capacity.

## First wave — current

- [ ] `TOWER-R1 / #41` — SENTINEL-C independently review `main@c4c93e52... -> 6e4d59b2...`, CI #485 PASS, and return exact disposition — Owner: `SENTINEL-C`
- [ ] `TOWER-D1 / #49` — genuinely rebuild A2 on accepted #48/A1/latest accepted main, preserve newer accepted behavior, fresh CI/review/handoff — Owner: `FOUNDRY`
- [ ] `TOWER-R2 / #70` — fresh independent review of `main@c4c93e52... -> fe5119c2...`, CI #487 PASS — Owner: `SENTINEL pool`
- [ ] `TOWER-C1 / #71` — complete exact-head CI #490 on `71a9d7a5...`; if PASS, independent review — Owner: `SWITCHYARD -> SENTINEL`
- [ ] `TOWER-I1 / #73` — resynchronize protocol layer onto latest accepted main, fresh CI/review — Owner: `SWITCHYARD`
- [ ] `TOWER-I2 / whole backlog` — consume clean returns and re-scan after every merge — Owner: `SWITCHYARD`
- [ ] `TOWER-Q1 / queue watch` — refresh after material movement; release only from acceptance — Owner: `TOWER`

## Phase 0 — accepted foundations

- [x] #30 accepted.
- [x] #39 accepted.
- [x] #44 accepted.
- [x] #45 accepted.
- [x] #48 accepted.

## Phase 1 — product frontier

### Context Builder

- [x] #41 current-main resynchronization on `6e4d59b2...`.
- [x] fresh Runtime CI #485 PASS.
- [ ] fresh independent exact-head review.
- [ ] SWITCHYARD merge gate.
- [ ] Only after accepted #41: rebuild #53; preserve Stage-2 evaluation-only scope, strict source precision, exact `overlay_sha256`; fresh CI/review/integration.

### Execution lineage

- [ ] #49 FOUNDRY rebuild on accepted A1/latest main.
  - preserve accepted project-scoped run/session identity;
  - preserve helper/recovery authorities;
  - relationship evidence only;
  - exact delta + fresh CI + independent review + SWITCHYARD integration.
- [ ] Only after accepted #49: repair/rebuild #50 on accepted ancestry.

### Operational learning

- [ ] Resolve #43 development ownership from operator/canonical evidence.
- [ ] Owner performs bounded change-contract repair unless new evidence returns substantive defect.
- [ ] Fresh CI/review/integration.
- [ ] Only after accepted #43: rebuild/review/integrate #60.

## Phase 2 — coordination/protocol

- [x] #70 current-main resynchronization at `fe5119c2...`.
- [x] #70 fresh Runtime CI #487 PASS.
- [ ] #70 fresh independent review; then SWITCHYARD integration if clean.
- [x] #71 current-main resynchronization at `71a9d7a5...`.
- [ ] #71 exact-head Runtime CI #490 completion.
- [ ] #71 fresh independent review; then SWITCHYARD integration if clean.
- [ ] #73 latest-main resynchronization; fresh CI and independent review; SWITCHYARD integration.
- [ ] #67 ANVIL owner-note freshness repair.
- [ ] #68 FOUNDRY owner-note freshness repair preserving FOUNDRY development role.
- [ ] #69 SENTINEL owner-note refresh.

## PARKED / design-only

- [ ] #51 exact task/run ↔ hcom event correlation design.
- [ ] #52 evidence-backed wait design stacked on #51.

No runtime communication-response wait inference from provider silence, timestamps, identity coincidence, text, or same-thread traffic.

## Checkpoints

### A — #41

- Evidence: base `c4c93e52...`, head `6e4d59b2...`, CI #485 PASS, SENTINEL-C claim.
- CLEAN + accepted -> release #53.
- Defect -> return exact defect to legitimate owner; keep #53 blocked.

### B — #49

- Next proof: rebuilt exact head on accepted A1/latest main, intended A2 delta, fresh CI, independent review.
- CLEAN + accepted -> release #50.

### C — #70/#71/#73

- #70 current exact packet is review-ready.
- #71 waits on current exact-head CI.
- #73 still requires latest-main synchronization because prior CLEAN review is stale.

### D — #43 ownership

- Required evidence: explicit operator/canonical ownership handoff.
- No binding -> remain blocked; idle capacity is not permission.

## Re-plan immediately if

- `main` moves;
- #41/#49/#70/#71/#73 heads move;
- exact review dispositions land;
- #43 ownership becomes explicit;
- an interface-changing defect appears;
- canonical state contradicts this plan.

## Core rule

**TOWER decides what is worth attempting next from the derived dependency view. SENTINEL decides whether reviewed evidence survives independent testing. SWITCHYARD decides what is safe to integrate. The operator resolves authority evidence cannot.**
