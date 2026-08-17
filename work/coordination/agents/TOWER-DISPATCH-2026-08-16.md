# TOWER dispatch checkpoint — 2026-08-16

This file is a **derived as-of checkpoint**, not a mutable authority surface.

Checkpoint accepted-main boundary:

`main@c4c93e52edd961802c7c203035f0bc272f196b59`

The facts below were re-read from live GitHub at this checkpoint. **Later GitHub movement supersedes this file for action without making its as-of statements false.** Any agent using this file must first re-read live GitHub, canonical MAPS task/ownership state, and applicable review/CI evidence.

Core rule:

**TOWER prioritizes. Assigned agents pull. GitHub coordinates. SENTINEL reviews. SWITCHYARD integrates. The operator resolves authority that evidence cannot.**

## Accepted foundations at checkpoint

- #30 — ACCEPTED
- #39 — ACCEPTED
- #44 — ACCEPTED
- #45 — ACCEPTED
- #48 — ACCEPTED

## NOW at checkpoint

### #41 — CLEAN integrated head; SWITCHYARD merge gate

- base: `main@c4c93e52edd961802c7c203035f0bc272f196b59`
- head: `6e4d59b2a5d8a9650af83b867f10becfdcb48de3`
- Runtime CI #485 / `31976928359`: PASS
- SENTINEL-C disposition: `CLEAN INTEGRATED-HEAD`
- next legitimate role: SWITCHYARD expected-head merge gating if base/head remain unchanged
- #53 remains blocked until #41 is actually accepted

### #49 — FOUNDRY rebuild on accepted A1/latest main

- historical head: `ed865be729cf2d15663258fd46c9296ea32d28e7`
- #48/A1 is accepted; latest accepted main also includes #45
- SWITCHYARD explicitly released #49 to FOUNDRY/development
- required: genuine rebuild on accepted A1/latest main; preserve project-scoped run/session identity and all newer accepted behavior; add only intended A2 helper/recovery relationship evidence; exact delta; fresh Runtime CI; independent exact-head review; then SWITCHYARD
- #50 remains blocked until #49 is actually accepted

### #70 — independent review in progress

- base: `main@c4c93e52edd961802c7c203035f0bc272f196b59`
- head: `fe5119c2977e21009f7cfeb3e9befb3adb5c0db7`
- Runtime CI #487 / `31976981585`: PASS
- SENTINEL-A advisory exact-head review claim observed
- review focus: TOWER/role separation, owner-file boundaries, evidence-testing semantics, no hidden task/review/merge authority

### #71 — independent review in progress

- base: `main@c4c93e52edd961802c7c203035f0bc272f196b59`
- head: `71a9d7a51086c6a4b3a6aa0c48bd826310eadd0d`
- Runtime CI #490 / `31977031772`: PASS
- SENTINEL-C advisory exact-head review claim observed
- review focus: exact three-file planning scope, historical/as-of checkpoint semantics, no hidden live-state/task/review/integration/promotion authority

### #73 — fresh review-ready protocol packet

- base: `main@c4c93e52edd961802c7c203035f0bc272f196b59`
- head: `f3f182e8fb11102a0d2674fa0f5001dc5113bec2`
- Runtime CI #493 / `31977080050`: PASS
- prior CLEAN review on `eccdddaa... -> 7434b08e...` is historical/stale for merge authority
- no current exact-head review claim observed at this checkpoint
- next legitimate role: eligible independent SENTINEL review

### SWITCHYARD — persistent PR-control lane

- consume clean exact-head review returns;
- preserve latest accepted main forward;
- after every merge, re-evaluate remaining integration candidates;
- do not wait on one PR when another independent PR-control action is eligible.

### TOWER — derived queue watch only

TOWER does not implement runtime work, independently approve, synchronize, or merge. Priority here is routing evidence only.

## NEXT

- #53 — ANVIL rebuild only after actual #41 acceptance; preserve Stage-2 evaluation-only scope, strict source precision, exact `overlay_sha256`, fresh CI/review/integration.
- #50 — repair/rebuild only after actual #49 acceptance.
- #68 — FOUNDRY owner-note freshness repair when it does not interfere with higher-leverage #49; preserve FOUNDRY development role.
- #67 — ANVIL owner-note freshness repair when product work permits.
- #69 — SENTINEL owner-note refresh when review throughput permits.

## BLOCKED / HOLD

- #53 — blocked on accepted #41.
- #50 — blocked on accepted #49.
- #60 — blocked on accepted #43.
- #43 — bounded repair is understood, but **development-owner continuity is unresolved**. The known defect is the declared change-boundary mismatch around `tests/test_operational_learning_schema.py`; runtime semantics were independently clean. ANVIL explicitly declined ownership because no transfer exists. TOWER does not infer FOUNDRY ownership either. Operator/canonical ownership evidence must bind a development continuity before mutation.
- #67/#68/#69 — owner-controlled coordination freshness; no cross-lane rewrite.

## PARKED

- #51 -> #52 — planning/design only. Preserve exact-correlation and no-heuristic wait rules; no runtime communication-response wait authority without accepted prerequisites and explicit provider correlation evidence.

## Dependency frontier

```text
accepted #39
  -> #41 CLEAN integrated head
  -> SWITCHYARD merge gate
  -> accepted #41
  -> #53 rebuild/review/integration

accepted #44 -> accepted #45

accepted #48
  -> #49 FOUNDRY rebuild on latest accepted main
  -> independent review + SWITCHYARD integration
  -> accepted #49
  -> #50 repair/rebuild

#43 explicit owner binding
  -> bounded repair
  -> independent review + integration
  -> accepted #43
  -> #60 rebuild/review/integration
```

## Coordination/protocol frontier

```text
#70 fe5119c2... / CI #487 PASS / SENTINEL-A claimed
  -> review disposition -> SWITCHYARD

#71 71a9d7a5... / CI #490 PASS / SENTINEL-C claimed
  -> review disposition -> SWITCHYARD

#73 f3f182e8... / CI #493 PASS / unclaimed at checkpoint
  -> SENTINEL -> SWITCHYARD

#67/#68/#69 owner-note freshness
  -> respective owner -> review/integration as applicable
```

## Operator decision unresolved

**PR #43 development ownership.** Evidence establishes a narrow repair but does not bind ANVIL or FOUNDRY. TOWER records `UNKNOWN` rather than manufacturing assignment.

## Re-plan trigger

A later TOWER session should recover live state and issue a new checkpoint when useful. It must not mutate this checkpoint merely to pretend it is a canonical live queue. Later main/head/review/CI movement supersedes these routing facts automatically.
