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

Before each implementation/test slice, re-read live open PR surfaces. Do not edit files owned by active non-coordinated lanes. As of this first slice, PRs #319–#323 own Emergence, the 6.4 exposure exercise, Wiki reconciliation, Program Steering/roadmap reconciliation, and the dated competitor research import respectively. This slice intentionally touches none of those paths.

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

The existing recovery test stops after asserting that worker B became the claimant. It does **not** explicitly freeze the competitor-derived stale-owner property:

```text
worker A claim
→ lease expires
→ worker B recovers
→ worker A wakes
→ A heartbeat rejected
→ A submission rejected
→ B remains canonical claimant
```

The runtime already appears to satisfy this. Therefore this slice is **test hardening only**, not a runtime change and not evidence that MAPS needs a new fencing-token schema.

### Intended change

Add one focused regression to `tests/test_state_store.py` proving that after takeover:

- old worker heartbeat returns `NOT_CLAIM_OWNER`;
- old worker submission returns `NOT_CLAIM_OWNER`;
- replacement worker remains canonical claimant;
- replacement worker can still renew its lease and submit.

### Explicit limitation

This test proves fencing of **MAPS canonical SQLite mutations** through claimant identity + lease checks. It does not prove stale-executor fencing for arbitrary external effects already dispatched to GitHub, providers, filesystems, or other systems. Those require operation identity/effect receipts/reconciliation and remain a separate evidence/design lane.

### Status

`IN PROGRESS` — test to be added and independently reviewed. No roadmap/checklist status change.

### Next candidate after this slice

Inspect 6.20 / `tests/test_no_progress.py` against the competitor-derived property `process alive != useful progress != valid ownership`. Add only a discriminating regression if current semantics already implement the property; otherwise route the gap to the existing 6.20 owner.
