# Roadmap: TOWER current multi-agent dispatch — 2026-08-16

- State: `WORKING`

## Current reality

### Checked facts

- `VERIFIED` — accepted `main` at this refresh is `eccdddaa37e42c93982bedf20d19e4f5096dbcff`.
- `VERIFIED` — former root gates #30, #39, #44, and #48 are accepted; the active product frontier has moved to #41, #45, and #49.
- `VERIFIED` — #41 is synchronized on current main at `6359e9246ef487d40fff60c2fb31b78067728fcb`; Runtime CI #480 / `31972177992` PASS; SENTINEL-A has an advisory exact-head integrated-review claim. #53 remains blocked until actual #41 acceptance.
- `VERIFIED` — #45 is rebuilt/synchronized on current main at `fdf6baf6fe5f0a8b83532bbf79bc3ddfdf834dcb`; Runtime CI #476 / `31971839363` PASS; SENTINEL-B has an advisory exact-head integrated-review claim.
- `VERIFIED` — #49 remains on historical head `ed865be729cf2d15663258fd46c9296ea32d28e7`; SWITCHYARD has explicitly released the A2 rebuild to FOUNDRY on accepted #48/A1. #50 remains blocked until #49 acceptance.
- `VERIFIED` — #73 is synchronized on current main at `7434b08e9343750f5d860070fa4005bcbf2da1e3`; Runtime CI #478 / `31971896322` PASS; SENTINEL-C has an advisory exact-head integrated-review claim.
- `VERIFIED` — #70 is synchronized at `90c2d08ae3f45e176b914487401686f09021ab4f`, Runtime CI #479 PASS, and remains an unclaimed independent-review opportunity at this refresh.
- `VERIFIED` — #71 is synchronized at `cc8917b83c800863f8e3d8b6e0f34901f74b4d1b`, Runtime CI #477 PASS, and remains an unclaimed independent-review opportunity at this refresh.
- `VERIFIED` — #43 has a narrow scope-contract repair only; runtime semantics were independently found clean. ANVIL explicitly declined ownership because no handoff assigns the branch to ANVIL. #60 remains blocked until #43 acceptance.
- `VERIFIED` — #67, #68, and #69 are owner-controlled coordination-note freshness work and must not be rewritten by TOWER/SWITCHYARD/SENTINEL outside their ownership boundaries.
- `VERIFIED` — #51/#52 remain planning/design only; their exact-correlation and evidence-backed-wait rules do not create runtime wait authority.
- `VERIFIED` — proposed PR #73 keeps GitHub coordination derived, requires explicit operator role binding, keeps SENTINEL claims advisory, and gives SWITCHYARD persistent whole-backlog control without new merge authority.

### Sources of truth

- root `AGENTS.md`;
- `work/coordination/README.md`;
- proposed `work/coordination/GITHUB_ASYNC_WORK_PULL.md` from PR #73 until accepted;
- live GitHub PR/base/head/review/CI/comments;
- accepted MAPS state.

This roadmap is a read model only. If it conflicts with those sources, it loses.

### Important unknowns / unresolved decisions

- `UNKNOWN` — final review disposition for claimed #41, #45, and #73 exact heads.
- `UNKNOWN` — whether #49 rebuild on accepted A1 will expose integration-specific conflicts; FOUNDRY must prove the new exact delta and CI.
- `UNKNOWN / OPERATOR BOUNDARY` — which development continuity owns the bounded #43 repair. TOWER does not infer ownership from workload.

## Definition of DONE

Finished result for this dispatch cycle:

1. every active dependency frontier has an exact action, blocker, or owner-bound wait condition;
2. claimed reviews resolve to exact dispositions without branch mutation;
3. direct dependents start only after actual accepted prerequisites;
4. #49 is rebuilt on accepted A1 rather than carried forward from superseded ancestry;
5. #43 either receives an explicit development owner or remains visibly blocked without invented ownership;
6. coordination PRs move through owner/review/integration boundaries without becoming a second task/review database;
7. TOWER refreshes the queue after material live movement rather than preserving stale snapshots.

Final proof comes from live GitHub exact-head evidence, not this roadmap.

## Boundaries

### In scope

- derived NOW / NEXT / BLOCKED / PARKED planning;
- dependency release conditions;
- role routing from existing authority;
- explicit unresolved ownership/authority blockers;
- TOWER-owned planning/dispatch files and coordination comments.

### Out of scope

- runtime implementation by TOWER;
- independent review by TOWER;
- synchronization or merge by TOWER;
- edits to `ANVIL.md`, `FOUNDRY.md`, `SENTINEL.md`, or `SWITCHYARD.md`;
- assigning #43 to a development lane without operator/canonical authority;
- speculative new services, labels, inbox databases, or automation.

## Backward plan

1. Immediately before this dispatch cycle is complete, #41/#45/#73 have exact review outcomes, #49 has a verified rebuilt state or concrete returned blocker, and #43 ownership is resolved or explicitly remains blocked.
2. Before that, the SENTINEL pool works distinct claimed review heads while FOUNDRY rebuilds #49 and SWITCHYARD continues whole-backlog control.
3. Before that, accepted roots #39/#44/#48 establish stable ancestry for #41/#45/#49.
4. Current state: review throughput and one development rebuild are the main executable bottlenecks; #43 is an ownership decision bottleneck.

## Mission/checkpoint result

- Required: `YES` — TOWER refreshed live state before editing.
- `ACCEPTED` — old root-centric #72 queue is obsolete because #30/#39/#44/#48 are accepted.
- `ACCEPTED` — #41 and #45 are no longer development waits; they are exact integrated-head reviews in progress.
- `ACCEPTED` — #49 is no longer blocked by #48; FOUNDRY has a legitimate rebuild release.
- `ACCEPTED` — multiple SENTINEL continuities can review distinct exact heads concurrently when explicitly operator-bound and individually independent.
- `REJECTED` — #43 should be assigned to ANVIL merely because ANVIL is idle; current evidence does not transfer ownership.
- `REJECTED` — coordination-note freshness should displace the higher-leverage #49 dependency root unless a real authority/safety reason requires it.

## First wave — current

- [ ] `TOWER-R1 / #41` — SENTINEL-A independently review `eccdddaa... -> 6359e924...`; exact CI #480 PASS; return exact disposition — Owner: `SENTINEL-A`
- [ ] `TOWER-R2 / #45` — SENTINEL-B independently review `eccdddaa... -> fdf6baf6...`; exact CI #476 PASS; return exact disposition — Owner: `SENTINEL-B`
- [ ] `TOWER-R3 / #73` — SENTINEL-C independently review `eccdddaa... -> 7434b08e...`; exact CI #478 PASS; return exact protocol disposition — Owner: `SENTINEL-C`
- [ ] `TOWER-D1 / #49` — genuinely rebuild A2 on accepted #48/A1/current main, preserve relationship-only authority, run fresh CI, and hand exact state to independent review — Owner: `FOUNDRY`
- [ ] `TOWER-I1 / backlog control` — continuously consume clean review returns and re-scan all open PRs after every accepted merge — Owner: `SWITCHYARD`
- [ ] `TOWER-Q1 / queue watch` — refresh this roadmap on material state change; do not release downstream work from claims or unmerged heads — Owner: `TOWER`

## Phase 0 — accepted foundations

- [x] #30 accepted.
- [x] #39 accepted.
- [x] #44 accepted.
- [x] #48 accepted.

These are no longer current work items; they are the accepted ancestry for later layers.

## Phase 1 — direct dependents

### Context Builder

- [ ] #41 exact integrated-head review.
- [ ] If CLEAN and unchanged, SWITCHYARD final merge gate.
- [ ] Only after accepted #41: rebuild #53 on current accepted ancestry; preserve evaluation-only scope, strict source precision, and exact `overlay_sha256`; fresh CI/review/integration.

### Communication lineage

- [ ] #45 exact integrated-head review.
- [ ] If CLEAN and unchanged, SWITCHYARD final merge gate.

### Execution lineage

- [ ] #49 FOUNDRY rebuild on accepted A1/current main.
  - preserve accepted project-scoped run/session identity;
  - preserve helper/recovery source authorities;
  - add only A2 relationship evidence;
  - exact intended delta;
  - fresh Runtime CI;
  - independent exact-head review;
  - SWITCHYARD integration.
- [ ] Only after accepted #49: repair/rebuild #50 and re-prove A3 semantics on current ancestry.

### Operational learning

- [ ] Resolve #43 development ownership from operator/canonical evidence.
- [ ] Owner performs only the bounded change-contract repair unless new evidence returns a substantive defect.
- [ ] Fresh CI/review/integration.
- [ ] Only after accepted #43: rebuild/review/integrate #60.

## Phase 2 — coordination/protocol

- [ ] #73 exact integrated-head independent review in progress; if clean, SWITCHYARD integration.
- [ ] #70 independent review of exact synchronized head `90c2d08a...`; if clean, SWITCHYARD integration.
- [ ] #71 independent review of exact synchronized head `cc8917b8...`; if clean, SWITCHYARD integration.
- [ ] #67 ANVIL owner-note freshness repair, then independent handling/integration as required.
- [ ] #68 FOUNDRY owner-note freshness repair preserving FOUNDRY development role; then independent handling/integration as required.
- [ ] #69 SENTINEL owner-note refresh; then independent handling/integration as required.

Coordination hygiene remains subordinate to accepted product dependency roots unless it becomes load-bearing for safe routing.

## PARKED / design-only

- [ ] #51 exact task/run ↔ hcom event correlation design.
- [ ] #52 evidence-backed wait design stacked on #51.

Do not infer communication-response waiting from provider silence, timestamps, names, text, or same-thread traffic. Runtime implementation requires accepted exact correlation evidence and explicit authority.

## Checkpoints

### A — #41

- Evidence: exact base/head, CI #480, SENTINEL-A disposition.
- CLEAN + unchanged -> SWITCHYARD -> accepted #41 -> release #53.
- Defect -> return exact defect to legitimate development owner; keep #53 blocked.

### B — #45

- Evidence: exact base/head, CI #476, SENTINEL-B disposition.
- CLEAN + unchanged -> SWITCHYARD final merge gate.
- Defect -> return to legitimate owner; do not infer broader communication authority.

### C — #49

- Evidence: new rebuilt exact head on accepted A1, exact intended delta, fresh Runtime CI, independent review.
- CLEAN + accepted -> release #50.
- Defect -> return to FOUNDRY and keep #50 blocked.

### D — #43 ownership

- Evidence: explicit operator/canonical ownership handoff.
- If bound -> narrow repair may proceed.
- If unbound -> remain blocked; do not use idle capacity as permission.

### E — coordination protocol

- Evidence: #73 independent exact-head review and SWITCHYARD integration result.
- Requirement: operator-bound roles, derived GitHub coordination, advisory reviewer claims, independent review, dependency-first anti-regression integration, no duplicate task/review/merge authority.

## Re-plan immediately if

- `main` moves;
- a claimed #41/#45/#73 target moves or receives a disposition;
- #49 branch moves to a rebuilt head;
- #43 gets an explicit owner;
- a review exposes an interface-changing defect;
- canonical ownership/task state contradicts this roadmap;
- operator priority/role architecture changes.

## Core rule

**TOWER decides what is worth attempting next from the derived dependency view. SENTINEL decides whether reviewed evidence survives independent testing. SWITCHYARD decides what is safe to integrate. The operator resolves authority that evidence cannot.**
