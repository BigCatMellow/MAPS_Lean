# Task: TOWER current dispatch — 2026-08-16

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `TOWER`
- Risk: `MEDIUM`
- Goal: maintain a shared, evidence-backed multi-agent dispatch packet and working roadmap that identify the current dependency frontier, eligible actions, exact waits, and unresolved authority without changing canonical task/review/ownership/merge authority.

## Inputs and source of truth

- root `AGENTS.md`;
- `work/coordination/README.md`;
- proposed `work/coordination/GITHUB_ASYNC_WORK_PULL.md` from PR #73 until accepted;
- live accepted `main`;
- live open PR/base/head/review/CI/comment evidence;
- accepted MAPS task/ownership state.

Authority order:

1. operator / policy authority;
2. canonical MAPS task and ownership state;
3. live GitHub repository/PR/review/CI evidence;
4. this TOWER packet as derived routing evidence only.

## Change boundary

### MAY CHANGE

- `work/tasks/tower-current-dispatch-2026-08-16.md`;
- `work/roadmaps/tower-current-dispatch-2026-08-16.md`;
- `work/coordination/agents/TOWER-DISPATCH-2026-08-16.md`;
- top-level coordination comments on relevant PR threads.

### MUST NOT CHANGE

- owner-controlled `ANVIL.md`, `FOUNDRY.md`, `SENTINEL.md`, `SWITCHYARD.md`;
- runtime, tests, schemas, policies, feature branches, existing feature task records, canonical project roadmaps;
- canonical lifecycle/ownership;
- SENTINEL findings;
- SWITCHYARD integration/merge state or authority.

## Decision authority

TOWER may derive priority/order/hold conditions from verified dependencies. TOWER may not invent ownership, approve reviewed work, synchronize branches, implement features, or merge.

Unresolved material ownership/authority is escalated to the operator.

## Acceptance criteria

- [x] Live state recovered before edits.
- [x] Root AGENTS, coordination README, and proposed PR #73 protocol read.
- [x] Accepted main refreshed after concurrent movement.
- [x] Accepted #30/#39/#44/#45/#48 represented as foundations.
- [x] #41 represented at fresh current-main head `6e4d59b2...`, CI #485 PASS, SENTINEL-C exact-head review in progress; #53 held until actual #41 acceptance.
- [x] #49 represented as released to FOUNDRY for genuine rebuild on accepted A1/latest main; #50 held until #49 acceptance.
- [x] #70 represented at current-main head `fe5119c2...`, CI #487 PASS, fresh independent review next.
- [x] #71 represented at current-main head `71a9d7a5...`, CI #490 running, review only after exact-head PASS.
- [x] #73 prior CLEAN review represented as stale after #45 main movement; current gate remains latest-main SWITCHYARD resynchronization then fresh CI/review.
- [x] #43 represented as bounded repair-ready but owner-unresolved; TOWER does not assign it without authority.
- [x] #60 remains blocked behind accepted #43.
- [x] #67/#68/#69 remain owner-controlled coordination freshness work.
- [x] #51/#52 remain planning/design only with no runtime wait authority.
- [x] Branch changes remain limited to the three TOWER Markdown files.
- [ ] Fresh exact-head CI completes on the final refreshed #72 head.
- [ ] Eligible independent review completes on the final refreshed #72 head.
- [ ] If clean, SWITCHYARD performs current-main synchronization/integration; TOWER does not.

## Verification evidence at final refresh

### Accepted main

`c4c93e52edd961802c7c203035f0bc272f196b59`

PR #45 is merged at that commit.

### Product frontier

- #41: base `main@c4c93e52...`, head `6e4d59b2a5d8a9650af83b867f10becfdcb48de3`; Runtime CI #485 / `31976928359` PASS; SENTINEL-C exact-head claim observed. #53 blocked pending acceptance.
- #49: historical head `ed865be729cf2d15663258fd46c9296ea32d28e7`; explicit SWITCHYARD release to FOUNDRY for rebuild on accepted #48/A1/latest main. #50 blocked.
- #43: head `aeecf1b5775db1d5ac2484819620f476752f3654`; narrow change-contract defect only; ANVIL explicitly declined claim because ownership was not transferred. #60 blocked.

### Coordination/protocol frontier

- #70: base `main@c4c93e52...`, head `fe5119c2977e21009f7cfeb3e9befb3adb5c0db7`; Runtime CI #487 / `31976981585` PASS; fresh independent review next.
- #71: base `main@c4c93e52...`, head `71a9d7a51086c6a4b3a6aa0c48bd826310eadd0d`; Runtime CI #490 / `31977031772` running at checkpoint; review after PASS.
- #73: old head `7434b08e9343750f5d860070fa4005bcbf2da1e3`; prior CLEAN review/CI on `eccdddaa...` explicitly stale after #45 advanced main. Next: SWITCHYARD resync + fresh CI/review.
- #67/#68/#69: owner-controlled freshness work only.

## Conditional execution rules

1. Recover live state.
2. Compare it with the TOWER packet.
3. Update only verified derived facts.
4. Move work to NOW only when ownership/dependency/role/authority permit it.
5. Invalidate merge-authoritative review assumptions when accepted main moves.
6. Keep downstream work blocked until actual prerequisite acceptance.
7. If ownership is unresolved, record blocker rather than assign from convenience.
8. Change only the three TOWER files/comments.
9. Verify exact branch delta.
10. Require fresh CI and independent review.
11. Stop at TOWER boundary; SWITCHYARD owns synchronization/integration.

## Stop / escalate

Stop rather than guess on unresolved ownership, stale exact-head evidence, material main movement, or authority conflicts.

Escalate:

- operator — #43 ownership or other material intent/role decisions;
- SENTINEL — independent review;
- SWITCHYARD — integration/merge safety;
- legitimate development owner — implementation repair.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Checkpoint decision: `CHANGE` repeatedly during this run because concurrent lanes legitimately advanced live state.
- #45 is accepted and therefore no longer an active review item.
- #41 resynchronization completed and fresh exact-head review is now in progress.
- #70 resynchronization and fresh CI completed; independent review is next.
- #71 resynchronization completed; fresh CI is in progress.
- #73 old CLEAN packet remains stale and awaits latest-main resynchronization.
- #49 remains valid FOUNDRY parallel development.
- #43 remains explicit owner-unresolved blocker.

## Completion / handoff

TOWER refresh is complete when:

1. all three TOWER files reflect the same `main@c4c93e52...` frontier;
2. exact branch delta is still only those three files;
3. fresh Runtime CI passes on the final #72 head;
4. a durable independent-review handoff is posted to PR #72.

TOWER then freezes. It does not independently review, synchronize, or merge #72.
