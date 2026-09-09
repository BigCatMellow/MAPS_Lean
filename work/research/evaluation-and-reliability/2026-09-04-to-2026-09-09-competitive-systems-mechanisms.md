# Competitive systems mechanisms — evaluation and reliability — 2026-09-04 to 2026-09-09

Status: `RESEARCH — NOT ACTIVE AUTHORITY`

Main question: **Which real upstream failures, fixes, and regression patterns should MAPS_L add to its evaluation discipline so it does not rediscover reliability bugs in production?**

## Evidence snapshot

Deep extraction owner: `BigCatMellow/Pilot_Projects` PR #5 at `f6d584465e15b0fcf3cd09fea9e056bc23852e94`.

- Test catalogue: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/TEST_CATALOG.md
- Fix-history ledger: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/FIX_HISTORY.md
- Deep durability bake-off: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/SUBSTRATE-DURABILITY-BAKEOFF-DEEP.md

## Findings that strengthen MAPS_L evaluation

### 1. Public incident history is more valuable than feature matrices

Across DBOS, Restate, Gas City, Optio, Taskplane, LangGraph, Hermes, Letta, and LiteLLM, documentation often describes the intended invariant while issue/fix history reveals the actual boundary.

Useful evaluation pattern:

```text
claim/design
→ observed failure
→ root cause
→ attempted fix
→ merged fix/current status
→ regression test
→ residual limitation
```

The Pilot fix-history pass also corrected earlier research when upstream evidence disproved or narrowed a claimed defect. MAPS_L should preserve this discipline: do not freeze an issue report into a permanent belief after the system changed.

### 2. Exactly-once execution is the wrong universal target

Repeated upstream evidence supports a more realistic correctness target for arbitrary side effects:

```text
at-least-once attempt delivery
+
stale-executor fencing
+
stable logical operation identity
+
idempotent/reconcilable effects
+
explicit ambiguous outcome
```

This is directly testable and avoids false guarantees.

### 3. Progress is distinct from liveness

Restate, Gas City, Optio, Hermes, and MAPS_L's own stall history converge on the same failure class:

```text
process/session/service appears alive
but useful state is not advancing
```

Therefore evaluation should test at least three separate questions:

- is the executor alive?
- does it still own the work?
- is useful progress occurring?

This directly strengthens 6.20 NO_PROGRESS and recovery evaluation.

### 4. Recovery needs failure injection at lifecycle boundaries

High-value incidents occurred at boundaries such as:

- crash before first durable write;
- crash after external effect but before acknowledgement;
- transient storage outage during recovery;
- rolling restart while old executor still exists;
- old attempt completing after takeover;
- background cleanup continuing after resource generation changed;
- stale timer/event replay after upgrade;
- host sleep causing leases/heartbeats to age;
- checkpoint write from old execution after newer checkpoint exists.

These belong in MAPS_L's frozen reliability corpus when the relevant mechanism exists.

### 5. Hard-budget tests require concurrency and unknown-cost cases

LiteLLM public failure/fix history shows that a budget feature can appear correct in serial tests while failing under:

- concurrent reservation;
- stale/cached spend state;
- omitted entity scope;
- unknown/unpriceable route;
- temporary multi-window budget changes;
- reservation shrunk to remaining headroom even though maximum request cost still exceeds the hard cap.

If MAPS_L later implements paid-resource admission, the key property should be:

```text
conservative maximum next-operation cost > remaining hard budget
→ reject
```

and budget-state uncertainty should fail closed for explicitly hard-ceiling work.

This is future test input, not a current requirement to build a budget subsystem.

### 6. Configuration/runtime mismatch deserves its own regression class

Taskplane and Optio show a recurring class where requested configuration, persisted configuration, and effective subprocess behavior diverge.

Candidate MAPS incident class/property:

```text
CONFIG_RUNTIME_DIVERGENCE

PROPERTY: consequential run evidence must identify effective runtime/configuration sufficiently to detect material mismatch.
```

No new enum is proposed by this note; use the existing incident taxonomy unless a real MAPS case justifies extending it.

## Portable regression families

The pinned Pilot catalogue contains implementation-ready cases. Highest-value candidates for MAPS_L when applicable:

### Ownership / recovery

- two concurrent claimants -> at most one current owner;
- lease expires -> stale worker later commits -> rejected;
- old controller disappears but worker survives -> no duplicate launch without runtime reconciliation;
- host sleeps past lease -> recovery does not confuse elapsed time with safe takeover;
- current owner changes while old attempt is in flight -> old result cannot mutate current state.

### External effects

- external effect succeeds, acknowledgement lost -> retry first reconciles operation identity;
- same operation ID + changed intent -> fail closed;
- cancellation/timeout after dispatch -> effect state becomes unknown unless externally verified;
- compensation fails -> original operation does not become falsely "rolled back."

### Scheduling / no-progress

- eight missed hourly ticks -> one current reconciliation rather than eight stale agent turns;
- duplicate wakeups -> coalesce/reconcile same work identity;
- process alive but no useful progress -> no-progress signal remains independent of liveness;
- incomplete observations -> defer rather than destructive retry.

### Review / artifact verification

- producer self-review / same hidden continuity -> ineligible;
- requested reviewer model differs from actual subprocess -> mismatch visible;
- stale artifact revision reviewed -> cannot approve current artifact;
- agent reports artifact/PR URL but target system cannot verify it -> result unknown/failed, not success.

### Context / memory

- low-authority retrieved text cannot override canonical fact;
- hostile memory is data/evidence, not authority;
- branch/stale checkpoint cannot overwrite current root truth;
- compaction interruption is reconstructable and explicit;
- independent eval runs do not inherit persistent memory unless the fixture intentionally includes it.

## MAPS_L roadmap mapping

- 6.20 NO_PROGRESS -> progress-vs-liveness and stall fault injection;
- 6.21 flow/recovery -> ownership/retry/reconciliation cases;
- 6.31 controlled refinement -> fix-history/evidence-before-promotion discipline;
- 6.32 fork debugging -> use observable checkpoints/fixtures, not hidden reasoning replay;
- 6.33 semantic retrieval -> continue frozen-eval gating;
- 6.35 portable deployment -> use the first external pilot as a source of real frozen incidents, not merely a demo.

## Disposition

`PORTABLE_TEST_INPUT / STRENGTHEN_EXISTING_OWNER`.

The main value is to import failure cases and repaired invariants into MAPS_L evaluation when their owning mechanisms are touched. Do not create work merely to make the test catalogue larger.