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

Authority order for this task:

1. operator / policy authority;
2. canonical MAPS task and ownership state;
3. live GitHub repository/PR/review/CI evidence;
4. this TOWER task/roadmap/dispatch as derived routing evidence only.

Evidence labels:

- `VERIFIED` — directly re-read from current GitHub/repository evidence during this refresh;
- `REPORTED` — preserved source claim not mechanically reproduced by TOWER;
- `UNKNOWN` — not safely established; route or block rather than guess.

## Change boundary

### MAY CHANGE

- `work/tasks/tower-current-dispatch-2026-08-16.md`;
- `work/roadmaps/tower-current-dispatch-2026-08-16.md`;
- `work/coordination/agents/TOWER-DISPATCH-2026-08-16.md`;
- top-level coordination comments on relevant PR threads.

### MUST NOT CHANGE

- owner-controlled `ANVIL.md`, `FOUNDRY.md`, `SENTINEL.md`, `SWITCHYARD.md`;
- runtime, tests, schemas, policies, feature branches, existing feature task records, or canonical project roadmaps;
- canonical task lifecycle or ownership;
- SENTINEL review findings;
- SWITCHYARD integration/merge state or authority.

Any new repository path requires task amendment first.

## Decision authority

TOWER may decide:

- derived `NOW / NEXT / BLOCKED / PARKED` ordering from verified dependencies and operator priority;
- which existing role should inspect an already-authorized gate;
- hold/resume wording and dependency release conditions;
- when stale TOWER planning evidence must be refreshed.

TOWER must not decide:

- assignment across an unresolved canonical ownership boundary;
- independent review outcome;
- integration safety/merge approval;
- feature scope or runtime behavior outside an existing owner task.

Escalate unresolved material ownership/authority to the operator.

## Acceptance criteria

- [x] Live `main` is recovered before refresh.
- [x] Root `AGENTS.md`, coordination README, and current proposed PR #73 protocol are read before consequential TOWER edits.
- [x] The stale root-centric queue is replaced with the current dependency frontier.
- [x] Accepted roots #30/#39/#44/#48 are represented as foundations, not active waits.
- [x] #41 is represented as exact integrated-head review in progress; #53 remains blocked until actual #41 acceptance.
- [x] #45 is represented as exact integrated-head review in progress.
- [x] #49 is represented as released to FOUNDRY for genuine rebuild on accepted #48/A1; #50 remains blocked until #49 acceptance.
- [x] #73 is represented as exact integrated-head review in progress.
- [x] #70/#71 are represented as distinct CI-green independent-review opportunities.
- [x] #43 is represented as bounded repair-ready but owner-unresolved; TOWER does not invent an ANVIL/FOUNDRY transfer.
- [x] #60 remains blocked behind accepted #43.
- [x] #67/#68/#69 remain owner-controlled coordination freshness work rather than cross-lane rewrite targets.
- [x] #51/#52 remain planning/design only and do not create runtime wait authority.
- [x] TOWER priority is explicitly routing evidence only; SENTINEL review and SWITCHYARD merge authority remain separate.
- [x] This branch changes only the three TOWER planning/coordination Markdown files.
- [ ] Fresh exact-head CI completes on the refreshed #72 head.
- [ ] Eligible independent review completes on the refreshed #72 head.
- [ ] If clean, SWITCHYARD performs current-main synchronization/integration; TOWER does not.

## Verification evidence at refresh

### Accepted main

`eccdddaa37e42c93982bedf20d19e4f5096dbcff`

### Current product frontier

- #41: `main@eccdddaa... -> 6359e9246ef487d40fff60c2fb31b78067728fcb`; Runtime CI #480 / `31972177992` PASS; SENTINEL-A exact-head claim observed.
- #45: `main@eccdddaa... -> fdf6baf6fe5f0a8b83532bbf79bc3ddfdf834dcb`; Runtime CI #476 / `31971839363` PASS; SENTINEL-B exact-head claim observed.
- #49: historical head `ed865be729cf2d15663258fd46c9296ea32d28e7`; explicit SWITCHYARD release to FOUNDRY for rebuild on accepted A1; #50 held until acceptance.
- #43: exact head `aeecf1b5775db1d5ac2484819620f476752f3654`; returned defect is bounded change-contract mismatch only; ANVIL explicitly declined claim because no ownership transfer exists; #60 held until acceptance.

### Current coordination/review frontier

- #73: `main@eccdddaa... -> 7434b08e9343750f5d860070fa4005bcbf2da1e3`; Runtime CI #478 PASS; SENTINEL-C exact-head claim observed.
- #70: `main@eccdddaa... -> 90c2d08ae3f45e176b914487401686f09021ab4f`; Runtime CI #479 PASS; independent review still required.
- #71: `main@eccdddaa... -> cc8917b83c800863f8e3d8b6e0f34901f74b4d1b`; Runtime CI #477 PASS; independent review still required.
- #67: ANVIL owner-note freshness repair required.
- #68: FOUNDRY owner-note freshness repair required while preserving FOUNDRY development role.
- #69: SENTINEL owner-note refresh required.

## Conditional execution rules

1. Recover live state.
2. Compare it with the current TOWER packet.
3. Update only legitimately derived facts.
4. Move work to NOW only if ownership, dependencies, role, and authority are satisfied.
5. Preserve blocked downstream work until actual prerequisite acceptance.
6. If ownership is unresolved, record the blocker rather than assign from convenience.
7. Update only the three TOWER files/comments.
8. Verify exact branch delta.
9. Require fresh CI and independent review.
10. Stop at the TOWER boundary; SWITCHYARD owns synchronization/integration.

Failure rules:

- IF `main` or a claimed exact review target moves THEN re-read before further dispatch.
- IF CI/review cannot be bound to the exact head THEN mark the gate unproven.
- IF canonical ownership conflicts with TOWER routing THEN canonical ownership wins.
- IF TOWER would need to implement, independently review, synchronize, or merge THEN hand off and stop.
- IF #43 ownership remains unresolved THEN keep it blocked and surface the operator decision.

## Stop / escalate

Stop rather than guess when:

- exact ownership is unresolved;
- a review or CI claim is stale/ambiguous;
- a new output path is required;
- operator intent would materially change role/priority/scope;
- branch movement occurs while writing.

Escalate:

- operator — material ownership/intent/priority/role decisions;
- SENTINEL — independent review;
- SWITCHYARD — integration/merge safety;
- legitimate development owner — concrete implementation repairs.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Checkpoint decision: `CHANGE` — the old #72 queue was materially stale.
- Former roots #30/#39/#44/#48 are accepted and removed from NOW.
- #41/#45 moved to integrated-head review in progress.
- #49 moved from blocked to FOUNDRY rebuild released.
- #53/#50 remain strict downstream holds.
- #43 moved from generic parked work to explicit owner-unresolved blocker; runtime scope remains narrow.
- #73 review is actively claimed; #70/#71 remain distinct review opportunities.
- Coordination-note freshness #67/#68/#69 remains owner-controlled and cannot be repaired cross-lane.

## Completion / handoff

TOWER refresh is complete when:

1. the three TOWER files contain the same live-state model;
2. exact branch delta is still only those three files;
3. fresh #72 exact-head CI is requested/observed;
4. a durable independent-review handoff is left on PR #72.

After that TOWER stops. It does not independently review, synchronize, or merge #72.
