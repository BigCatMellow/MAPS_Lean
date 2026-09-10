# Competitor borrow-integration log — 2026-09-09

Status: `EVIDENCE / TEST HARDENING — NOT ACTIVE AUTHORITY`

Purpose: preserve how externally researched mechanisms are incorporated into MAPS_L without turning competitor research into a second roadmap, silently replacing established MAPS_L owners, or colliding with active implementation work.

Deep evidence owner: `BigCatMellow/Pilot_Projects` PR #5. The MAPS_L evidence projection is PR #323 / `work/research/`.

## Process contract

For each candidate mechanism or failure lesson:

1. **Recover the current MAPS_L owner first.** Read current code/tests and the owning roadmap/research area before treating external material as a gap.
2. **Pin the upstream evidence.** Prefer immutable source/test/fix-history anchors from the Pilot research corpus.
3. **Translate to one MAPS invariant.** State the behavioral property in MAPS terms rather than copying an upstream abstraction or schema.
4. **Audit current coverage.** Distinguish:
   - already implemented + already tested;
   - implemented but missing a discriminating regression;
   - genuine behavior/design gap;
   - irrelevant to the current MAPS architecture.
5. **Take the smallest non-colliding action.** If current behavior already satisfies the invariant, add only missing regression/evidence. If satisfying it would require a new authority model, schema, runtime dependency, or architectural change, stop and route that through the normal design/roadmap decision path.
6. **Do not flip capability status from competitor evidence alone.** Status still requires MAPS_L's own implementation/exposure/verification evidence.
7. **Keep external-effect claims narrow.** A SQLite ownership test does not prove arbitrary provider/GitHub/filesystem effects are fenced.
8. **Require normal independent review.** Borrowed prior art is evidence, not self-ratifying correctness.
9. **Characterize before changing ambiguous behavior.** When current semantics are intentional but competitor failures expose a risk, first freeze the decision seam with a characterization test if that can be done without declaring the future policy.
10. **Do not manufacture work.** If MAPS already has the invariant and discriminating regression, record `ALREADY SATISFIED` and stop.

## Collision rule

Before each implementation/test slice, re-read live open PR surfaces. Do not edit files owned by active non-coordinated lanes. The active surface grew while this work was running: #319 owns Emergence authority; #320 owns the 6.4 destructive-action exposure; #321 owns Wiki reconciliation; #322 owns Program Steering/roadmap reconciliation; #323 owns the dated competitor research import; #324 owns H4 resume-validation exposure; #325 owns E5 recovery-compatibility design. Borrow-integration slices must stay outside those files unless explicitly coordinated.

Later borrow-integration work uses separate PRs only where the evidence/test slice is independently reviewable and does not collide with these owners. Do not continue opening micro-PRs once a useful review batch already exists; extend the relevant existing lane instead.

---

## Slice 01 — superseded claimant cannot mutate canonical task state

### Upstream evidence

Primary prior art:

- Noriq: expiring claims plus runner-coordination fencing; stale ownership after takeover must not remain effective.
- Restate: old attempt/generation output must not mutate state owned by a newer attempt.

Pinned Pilot evidence snapshot:

- `BigCatMellow/Pilot_Projects@f6d584465e15b0fcf3cd09fea9e056bc23852e94`
- `complete-ai-work-system/research/competitive-architecture/production-accelerators/P0-DURABLE-WORK-CLAIMS-FENCING.md`
- `complete-ai-work-system/research/competitive-architecture/production-accelerators/TEST_CATALOG.md`

### MAPS_L owner and current mechanism

Current owner: canonical SQLite task execution state in `runtime/state/execution.py`, supported by Harness/Recovery roadmaps.

Verified current behavior on `main`:

- `claim_task()` uses `BEGIN IMMEDIATE` and permits exactly one live claimant;
- an expired ACTIVE claim may be recovered by a new worker;
- recovery moves `claimed_by` to the replacement worker and increments `attempt`;
- `heartbeat()` requires the exact current claimant and a live lease;
- `submit_task()` requires the exact current claimant and a live lease.

Existing `tests/test_state_store.py` already proved concurrent claim race, live-lease non-stealing, and expired-lease takeover.

### Coverage gap and change

The existing recovery test stopped after worker B became claimant. PR #326 adds a discriminating regression:

```text
worker A claim
→ lease expires
→ worker B recovers
→ worker A wakes
→ A heartbeat rejected
→ A submission rejected
→ B remains canonical claimant
→ B can continue
```

No runtime/schema change.

### Explicit limitation

This proves fencing of MAPS canonical SQLite mutations through claimant identity + lease checks. It does not prove stale-executor fencing for external effects already dispatched elsewhere.

### Status

`IMPLEMENTED / RUNTIME CI PASS — INDEPENDENT REVIEW PENDING` on PR #326.

---

## Slice 02 — process liveness is not necessarily useful progress

### Upstream evidence

Gas City, Optio, Restate, Symphony, and the Pilot failure catalogue distinguish:

```text
process/session alive
!=
valid ownership
!=
useful forward progress
```

### Current MAPS_L design

Capability 6.20 / `runtime/no_progress.py::no_progress_advisory` deliberately treats heartbeat change as one progress signal. The original durable task explicitly accepts task, artifact, heartbeat, or explicit-wait progress.

### Competitor-derived challenge

A worker can keep heartbeating while stuck in an unproductive loop. Treating heartbeat as useful progress may therefore hide a class of stalls.

Changing that behavior would alter an accepted 6.20 design rather than harden an existing invariant.

### Disposition

`CHALLENGE / ROUTE — NO CODE CHANGE`.

When 6.20 is actively shaped, compare the current policy against a candidate that separates liveness from work-progress using frozen/real stall incidents. Do not smuggle the policy change through a regression test.

---

## Slice 03 — resolve filesystem target before scope authorization

### Upstream evidence

DeepSeek Harness and the Pilot sandbox/path packet preserve:

```text
lexical path inside allowed prefix
!=
resolved filesystem target inside allowed boundary
```

### Current mechanism and change

`runtime/state/integrity.py::_repo_relative` already resolves both repository root and candidate path before requiring `relative_to(root)`.

PR #326 adds a public-surface symlink regression:

```text
repo/src/escape -> symlink outside repo
writable scope requests src/escape
→ resolved target outside repo
→ INVALID_SCOPE
→ no run manifest persisted
```

This proves run-scope path containment only, not a complete process/network/credential sandbox.

### Status

`IMPLEMENTED / RUNTIME CI PASS — INDEPENDENT REVIEW PENDING` on PR #326.

---

## Slice 04 — reviewer label/config is not effective reviewer execution identity

### Upstream evidence

Taskplane's reviewer-model propagation failure and Optio's separate review topology reinforce:

```text
requested reviewer role/model/config
!=
proof of the actual process/session/model that performed review
```

### What MAPS already does well

MAPS already enforces substantial review independence and freshness:

- submission author cannot self-review;
- continuity-linked replacement identities are disqualified;
- final approval rechecks continuity;
- consequential review can bind exact task/run/artifact revision;
- stale review subjects reject approval;
- review subjects are immutable.

### Remaining evidence gap

The canonical `reviews` row records `reviewer_id`, verdict, summary, and timestamps. Task execution lineage exists separately in `run_manifests` / `run_session_links`, but a review decision is not mechanically bound to the run/session/provider/effective-model execution that performed an agent review.

### Disposition

`GAP / ROUTE — NO SCHEMA OR RUNTIME CHANGE`.

The Review/Harness owner should decide whether consequential machine review needs an optional immutable execution reference. Human/manual review must remain representable without inventing fake machine lineage. Missing lineage should fail closed only where policy explicitly requires machine-verifiable independence.

---

## Slice 05 — edited Skill content must not inherit prior approval

### Evidence and current mechanism

Supply-chain prior art reinforces:

```text
approved artifact identity
!=
future bytes at the same path/name
```

MAPS already content-addresses Skill subjects and stores lifecycle approval against the immutable catalog identity.

`tests/test_skill_lifecycle_storage.py::SkillLifecycleContentAddressingTests::test_editing_a_skill_creates_a_new_unapproved_subject` explicitly proves edited Skill bytes get a new catalog identity and do not inherit APPROVED/ACTIVE state. `tests/test_skills_catalog.py` also rejects activation through stale on-disk content.

### Disposition

`ALREADY SATISFIED — NO DUPLICATE TEST / NO CODE CHANGE`.

---

## Slice 06 — external-effect ambiguity must survive the retry decision seam

### Upstream evidence

Noriq, Restate, Temporal and mature idempotency practice distinguish:

```text
request failed to receive acknowledgement
!=
effect definitely did not happen
```

The stronger target is not universal exactly-once execution. It is stable logical operation identity + honest ambiguous outcome + reconciliation/idempotency before unsafe repeat.

### Current MAPS evidence

MAPS already has useful groundwork in `OperationResult`:

- `operation_id`;
- `mutated`;
- `complete`;
- `RetryDisposition.SAFE | UNSAFE | UNKNOWN`.

But `HarnessAdapter`/`HarnessService` do not establish and propagate a durable logical operation identity before dispatch. `RecoverySupervisor` projects a harness resume into only `attempted/ok/code/summary` and drops `operation_id` + `retry` before its fallback decision.

For every non-canonical harness failure, recovery intentionally falls through to direct `hcom.resume()` so the harness rollout would not suppress a resume that the old path attempted.

### Discriminating characterization

PR #327 now contains `tests/test_recovery_external_effect_ambiguity.py`:

```text
real canonical task/run/session binding
→ harness resume returns PROVIDER_TIMEOUT
   mutated=true
   operation_id=op-ambiguous-resume-1
   retry=UNKNOWN
→ recovery action omits operation_id/retry
→ direct hcom.resume() fires once in the same tick
→ outward action remains resume
```

This is a characterization of current behavior, not an endorsement of it.

### Disposition

`REAL DESIGN GAP / CHARACTERIZED — ROUTE TO HARNESS + RECOVERY`.

The next bounded decision is only whether `retry=UNKNOWN` may permit immediate direct fallback for recovery resume. Do not design a universal operation ledger before that seam is decided.

PR: #327.

---

## Slice 07 — hard cost/resource admission is not retrospective run-budget checking

### Upstream evidence

LiteLLM's failure history demonstrates the concurrency problem with read/check-only budgets:

```text
remaining = 100
A reads 100
B reads 100
A launches 70
B launches 70
→ exposure 140
```

A hard ceiling requires an atomic reservation at the launch-authority boundary.

### Current MAPS evidence

Current MAPS runtime budgets freeze and check:

- max attempts;
- max tool failures;
- runtime seconds.

`WorkerProfile.cost_rank` is relative routing preference. `paid_execution` is permission/classification. None is an atomic monetary/token/request/provider-slot reservation.

### Disposition

`REAL FUTURE CAPABILITY — DO NOT OVERLOAD CURRENT RUN-BUDGET OWNER`.

The first implementation proof, when this becomes active work, should be provider-free:

```text
limit=100
A reserves 70
B concurrently reserves 70
→ exactly one commits
→ available never negative
```

Then prove duplicate reservation identity, changed-intent reuse rejection, idempotent settlement, retained reservation under ambiguous execution, and zero admission without paid authority.

PR: #329.

---

## Slice 08 — task state and semantic event must share one commit boundary

### Upstream evidence

Durable workflow systems repeatedly rely on atomic canonical-state + history writes inside one local transaction so a crash/failure cannot report a transition that did not commit or commit state without its semantic history.

### Current MAPS mechanism

`claim_task()` already runs task mutation and `_append_event()` inside one explicit SQLite transaction.

### Missing regression and change

PR #330 injects an `sqlite3.OperationalError` from `_append_event` after the claim update path has begun and proves the open transaction rolls back:

- task stays READY;
- claimant/lease/heartbeat stay unset;
- attempt stays 0;
- task-event count is unchanged;
- exception remains observable.

### Disposition

`IMPLEMENTED AS FAULT-INJECTION TEST HARDENING`.

This proves same-SQLite-transaction atomicity only. It does not prove distributed outbox/event-delivery semantics.

PR: #330.

---

## Slice 09 — semantic history immutability/deletion contract is not yet explicit

### Current MAPS evidence

`task_events` is append-only through normal `BaseStore._append_event()` usage, but the schema currently defines:

```text
task_events.task_id REFERENCES tasks(task_id) ON DELETE CASCADE
```

and, unlike several immutable lineage tables (`run_manifests`, `run_session_links`, `run_helper_links`, etc.), there are no observed `BEFORE UPDATE` / `BEFORE DELETE` immutability triggers on `task_events`.

Therefore two facts must not be conflated:

```text
application code only appends events
!=
database-enforced immutable event history
```

### Why no patch was made

Adding no-update/no-delete triggers casually would interact with the current parent-task `ON DELETE CASCADE` contract. A trigger that rejects event deletion could also reject deletion of the owning task, which may or may not be intended. That is a retention/authority decision, not test hardening.

### Disposition

`DESIGN CONTRACT QUESTION — NO SCHEMA CHANGE`.

The State/History owner should decide explicitly among at least:

1. task events are immutable while task exists, but task deletion may cascade them;
2. task events survive task deletion through archival/tombstone semantics;
3. task deletion itself is forbidden once semantic history exists;
4. current best-effort append-only application behavior is intentionally sufficient.

Only after that decision should an immutability regression or trigger be added.

---

## Current integration frontier

The highest-value unresolved questions are now narrow rather than exploratory:

1. **External effects:** should `RetryDisposition.UNKNOWN` block immediate recovery fallback, and what durable operation identity/reconciliation follows from that decision?
2. **Resources/cost:** when paid/resource-constrained execution becomes active, add atomic pre-launch reservation rather than overloading retrospective run budgets.
3. **Review lineage:** decide when consequential agent review must be bound to actual execution/session/provider/effective-model lineage.
4. **NO_PROGRESS:** decide whether heartbeat is liveness only or useful progress for 6.20.
5. **Semantic history:** define the database-level update/delete/retention contract for `task_events` before adding immutability triggers.

Do not resume broad competitor feature hunting until these findings have either been reviewed, pulled forward by roadmap work, or shown irrelevant by real exposure evidence.

## Open integration batch

- #323 — competitor evidence projected into MAPS research owners.
- #326 — stale-owner + symlink containment regressions and this process log.
- #327 — external-effect ambiguity audit + characterization test.
- #328 — reachable dependency-cycle detection.
- #329 — hard cost/resource admission audit.
- #330 — task/event transaction atomicity fault-injection regression.

No capability/checklist status has been changed by this work and no merge authority is claimed.
