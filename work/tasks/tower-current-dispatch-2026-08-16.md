# Task: TOWER dispatch checkpoint — 2026-08-16

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `TOWER`
- Risk: `MEDIUM`
- Semantics: `DERIVED_AS_OF_CHECKPOINT`
- Checkpoint accepted main: `c4c93e52edd961802c7c203035f0bc272f196b59`

## Goal

Record a bounded, evidence-backed NOW/NEXT/BLOCKED/PARKED routing checkpoint for the multi-agent repository without becoming a second task/review/ownership/merge database.

Later GitHub movement supersedes this checkpoint for action. Future agents must re-read live GitHub before acting and must not interpret historical checkpoint facts as current authority.

## Inputs / source of truth

- root `AGENTS.md`;
- `work/coordination/README.md`;
- proposed `work/coordination/GITHUB_ASYNC_WORK_PULL.md` from PR #73 until accepted;
- live accepted `main`;
- live PR/base/head/review/CI/comment evidence;
- canonical MAPS task/ownership state.

Authority order:

1. operator / policy authority;
2. canonical MAPS task and ownership state;
3. live GitHub evidence;
4. this checkpoint as derived routing evidence only.

## Change boundary

### MAY CHANGE

- `work/tasks/tower-current-dispatch-2026-08-16.md`;
- `work/roadmaps/tower-current-dispatch-2026-08-16.md`;
- `work/coordination/agents/TOWER-DISPATCH-2026-08-16.md`;
- top-level coordination comments on relevant PR threads.

### MUST NOT CHANGE

- `ANVIL.md`, `FOUNDRY.md`, `SENTINEL.md`, `SWITCHYARD.md`;
- runtime, tests, schemas, policies, feature branches, other feature task records, canonical project roadmaps;
- canonical lifecycle/ownership;
- SENTINEL findings;
- SWITCHYARD integration/merge state or authority.

## Decision authority

TOWER may derive priority/order/hold conditions from verified dependencies. TOWER may not invent ownership, independently approve, synchronize, implement, or merge.

Unresolved material ownership/authority is surfaced to the operator.

## Acceptance criteria

- [x] live main recovered before consequential edits;
- [x] root AGENTS, coordination README, and proposed #73 protocol read;
- [x] checkpoint explicitly marked derived/as-of rather than mutable live truth;
- [x] accepted #30/#39/#44/#45/#48 recorded as foundations;
- [x] #41 recorded at exact current-main head `6e4d59b2...`, CI #485 PASS, SENTINEL-C CLEAN integrated-head; #53 held until actual #41 acceptance;
- [x] #49 recorded as explicit FOUNDRY rebuild release on accepted A1/latest main; #50 held until #49 acceptance;
- [x] #70 recorded at `fe5119c2...`, CI #487 PASS, SENTINEL-A claim;
- [x] #71 recorded at `71a9d7a5...`, CI #490 PASS, SENTINEL-C claim;
- [x] #73 recorded at `f3f182e8...`, CI #493 PASS, fresh exact-head review required;
- [x] #43 ownership preserved as UNKNOWN instead of assigned from convenience; #60 held;
- [x] #67/#68/#69 kept owner-controlled;
- [x] #51/#52 kept planning/design only;
- [x] branch delta limited to the three TOWER Markdown files;
- [ ] fresh exact-head CI passes on the final checkpoint head;
- [ ] eligible independent review completes on the final checkpoint head;
- [ ] if clean, SWITCHYARD performs then-current synchronization/integration; TOWER does not.

## Exact routing evidence at checkpoint

### Product frontier

- #41: `main@c4c93e52... -> 6e4d59b2a5d8a9650af83b867f10becfdcb48de3`; Runtime CI #485 / `31976928359` PASS; SENTINEL-C `CLEAN INTEGRATED-HEAD`; next SWITCHYARD expected-head merge gate; #53 blocked until actual acceptance.
- #49: historical `ed865be729cf2d15663258fd46c9296ea32d28e7`; explicit SWITCHYARD release to FOUNDRY for genuine rebuild on accepted #48/A1/latest main; #50 blocked.
- #43: `aeecf1b5775db1d5ac2484819620f476752f3654`; narrow change-contract defect only; ANVIL explicitly declined claim because ownership was not transferred; #60 blocked.

### Coordination/protocol frontier

- #70: `main@c4c93e52... -> fe5119c2977e21009f7cfeb3e9befb3adb5c0db7`; Runtime CI #487 / `31976981585` PASS; SENTINEL-A claim.
- #71: `main@c4c93e52... -> 71a9d7a51086c6a4b3a6aa0c48bd826310eadd0d`; Runtime CI #490 / `31977031772` PASS; SENTINEL-C claim.
- #73: `main@c4c93e52... -> f3f182e8fb11102a0d2674fa0f5001dc5113bec2`; Runtime CI #493 / `31977080050` PASS; prior old-base CLEAN review stale; fresh independent review required.
- #67/#68/#69: owner-controlled freshness work only.

## Conditional execution rules

1. Read live state before using this checkpoint.
2. If live state moved, use live evidence; do not mutate another owner's outputs to make the checkpoint look current.
3. Release downstream work only from actual accepted prerequisites.
4. Treat SENTINEL claims as advisory duplicate-work avoidance only.
5. Preserve accepted main forward; no historical branch may regress later accepted behavior.
6. If ownership is unresolved, preserve UNKNOWN and escalate rather than assign.
7. Change only the three TOWER files/comments.
8. Require fresh CI and independent review of this checkpoint before integration.
9. Stop at TOWER boundary.

## Stop / escalate

- operator — unresolved #43 ownership or other material role/intent decisions;
- SENTINEL — independent review;
- SWITCHYARD — synchronization/integration/merge safety;
- legitimate development owner — implementation repair.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Completion / handoff

TOWER completion requires:

1. exact three-file scope;
2. fresh Runtime CI on the final checkpoint head;
3. durable independent-review handoff;
4. TOWER freeze after handoff.

Independent review should test factual correctness at the checkpoint boundary, safe live-state supersession semantics, dependency ordering, hidden authority, unsafe parallelism, UNKNOWN handling for #43, and exact scope.

If CLEAN, SWITCHYARD owns any required synchronization to then-current main and normal integration gates.
