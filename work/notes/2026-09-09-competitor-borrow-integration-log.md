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

## Collision rule

Before each implementation/test slice, re-read live open PR surfaces. Do not edit files owned by active non-coordinated lanes. The active surface grew while this work was running: #319 owns Emergence authority; #320 owns the 6.4 destructive-action exposure; #321 owns Wiki reconciliation; #322 owns Program Steering/roadmap reconciliation; #323 owns the dated competitor research import; #324 owns H4 resume-validation exposure; #325 owns E5 recovery-compatibility design. Borrow-integration slices must stay outside those files unless explicitly coordinated.

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

Existing `tests/test_state_store.py` already proves:

- concurrent claim race has one winner;
- a live lease cannot be stolen;
- an expired lease can be recovered by another worker.

### Coverage gap found

The existing recovery test stopped after asserting that worker B became the claimant. It did **not** explicitly freeze the competitor-derived stale-owner property:

```text
worker A claim
→ lease expires
→ worker B recovers
→ worker A wakes
→ A heartbeat rejected
→ A submission rejected
→ B remains canonical claimant
```

The runtime already satisfied this. Therefore this slice is **test hardening only**, not a runtime change and not evidence that MAPS needs a new fencing-token schema.

### Change made

PR #326 adds `test_superseded_claimant_cannot_heartbeat_or_submit_after_takeover` to `tests/test_state_store.py`, proving:

- old worker heartbeat returns `NOT_CLAIM_OWNER`;
- old worker submission returns `NOT_CLAIM_OWNER`;
- replacement worker remains canonical claimant at attempt 2;
- replacement worker can renew its lease and submit successfully.

### Verification

- GitHub Runtime stack tests on PR #326 head `6c2df5e6a35ac8375738bc614533b3d4738e7360`: `SUCCESS`.
- Review-evidence workflow: expected failure because exact-head independent review evidence is not yet present.
- No `runtime/`, schema, capability-status, or roadmap change.

### Explicit limitation

This test proves fencing of **MAPS canonical SQLite mutations** through claimant identity + lease checks. It does not prove stale-executor fencing for arbitrary external effects already dispatched to GitHub, providers, filesystems, or other systems. Those require operation identity/effect receipts/reconciliation and remain a separate evidence/design lane.

### Status

`IMPLEMENTED / CI PASS — INDEPENDENT REVIEW PENDING` on PR #326. No roadmap/checklist status change.

---

## Slice 02 — process liveness is not necessarily useful progress

### Upstream evidence

Gas City, Optio, Restate, Symphony, and the Pilot failure catalogue repeatedly distinguish:

```text
process/session alive
!=
valid ownership
!=
useful forward progress
```

Relevant Pilot evidence is routed through PR #323's `evaluation-and-reliability` and `agent-harness` notes plus the pinned production `TEST_CATALOG.md`.

### Current MAPS_L design

Current owner: capability 6.20 and `runtime/no_progress.py::no_progress_advisory`.

The implementation is deliberately advisory/read-only. It currently treats any of these caller-supplied changes as a progress signal that clears `NO_PROGRESS`:

- heartbeat changed;
- task status changed;
- output changed.

This is not an accidental coding shortcut. The original durable task `work/tasks/no-progress-advisory.md` explicitly defines the goal as detecting repeated equivalent activity without **task, artifact, heartbeat, or explicit-wait progress**. Its acceptance criteria likewise require `CLEAR` when a progress signal changes.

### Competitor-derived challenge

The upstream incidents suggest heartbeat/liveness should not automatically be equivalent to *useful* progress. A worker can continue heartbeating while stuck in an unproductive loop.

However, changing `heartbeat_changed` from a progress signal to a liveness-only signal would alter an explicitly accepted 6.20 behavior. That is a design change, not test hardening.

### Disposition

`CHALLENGE / ROUTE — NO CODE CHANGE IN BORROW-INTEGRATION LANE`.

Do not smuggle this change through a regression test. When 6.20 is actively shaped again, the smallest discriminating evaluation should compare at least:

```text
same activity + same progress key + heartbeat changes only
```

under:

- current policy: `CLEAR / HEARTBEAT_CHANGED`;
- candidate policy: heartbeat proves liveness but repeated unchanged work still yields advisory `NO_PROGRESS`.

Use frozen/real stall incidents to evaluate false positives before changing semantics. The advisory-only nature means this can be tested safely, but the owning capability should make the decision.

### Status

`DESIGN ASSUMPTION IDENTIFIED — DEFERRED TO 6.20 OWNER`. No implementation, test, or capability-status change.

### Next candidate

Audit independent-review/effective-runtime evidence against the Taskplane/Optio lesson that a requested reviewer role/model/config is not proof of what process actually performed the review. Prefer test-only strengthening if MAPS already records sufficient lineage; otherwise route the missing evidence field to the existing review/harness owner.
