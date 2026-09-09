# Competitive systems mechanisms — agent harness — 2026-09-04 to 2026-09-09

Status: `RESEARCH — NOT ACTIVE AUTHORITY`

Main question: **Which implementation-backed orchestration, durability, recovery, and context-history mechanisms should strengthen MAPS_L's existing Harness Mechanics without creating a second control plane?**

## Evidence snapshot

Deep extraction owner: `BigCatMellow/Pilot_Projects` PR #5, pinned here at `f6d584465e15b0fcf3cd09fea9e056bc23852e94`.

- Source index: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/SOURCE_INDEX.md
- Machine-readable sources: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/SOURCES.yaml
- Fix history: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/FIX_HISTORY.md
- Test catalogue: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/TEST_CATALOG.md

The Pilot corpus pins source/test paths for Noriq, Gas City, OpenAI Symphony, Hermes, Optio, Taskplane, DeepSeek Harness (DSH), DBOS, Restate, LangGraph, Letta V2, LiteLLM, Temporal, and supporting standards. Treat that corpus as deep provenance; this note records only the MAPS_L-relevant delta.

## Findings that strengthen existing MAPS_L design

### 1. Durable work identity and executor ownership need separate generations

Noriq's claim/runner-coordination model provides direct prior art for:

- durable logical work identity;
- expiring claims/heartbeats;
- monotonic fencing tokens;
- dependency-aware claimability;
- rejecting stale owners after takeover.

Restate independently demonstrates generation/attempt fencing in a durable runtime: output from an older attempt must not mutate state owned by a newer attempt.

**MAPS_L implication:** this supports current SQLite claim/lease/lineage architecture. It is not evidence for replacing SQLite. When strengthening recovery/continuation, preserve the property:

```text
logical task/run identity
!=
current executor generation
```

A stale session/process being alive must never be sufficient authority to commit.

Relevant current areas: 6.6 lineage, 6.19 helper continuity, 6.21 flow/recovery, 6.24 least privilege.

### 2. Reconciliation should reason from current truth, not replay missed turns

Gas City and Kubernetes-style controllers reinforce a convergent model:

```text
current desired/canonical state
+
current observed runtime state
→ deterministic reconciliation action
```

Important failure history includes duplicate dispatch paths, controller hot loops, stale/runtime divergence, and dead agents leaving work claimed when no lease/TTL sweep exists.

Optio provides useful structure for a fully materialized `WorldSnapshot -> TypedAction` policy with no I/O/clock hidden inside the decision function. Incomplete observations should defer rather than act destructively.

OpenAI Symphony adds retry/backoff, stall detection, current-issue reread before retry, and restart reconstruction from durable tracker/workspace truth rather than exact scheduler memory.

**MAPS_L implication:** strengthen current recovery/flow/no-progress behavior with pure-policy and convergence tests. Do not add another scheduler merely to copy these systems.

Relevant current areas: 6.20 NO_PROGRESS, 6.21 deterministic flow lifecycle.

### 3. `INTENT`, persisted `CONTROL`, observed `RUNTIME`, and verified external reality are distinct

Across Optio, Taskplane, Hermes, Gas City, DBOS, LangGraph, and Restate, serious failures repeatedly occur when one layer is treated as proof of another:

- configured reviewer model differs from spawned subprocess model;
- DB says canceled while an old process continues acting;
- process is alive but makes no useful progress;
- persisted checkpoint is current but an older execution later writes over it;
- controller restart is mistaken for executor death;
- provider/UI status is mistaken for externally verified completion.

**MAPS_L implication:** traces/status should preserve these as separate facts. Reconciliation, not prose inference, should close the gaps.

Candidate vocabulary for evidence, not a new state machine:

```text
INTENT      — what should happen
CONTROL     — what MAPS currently authorizes/believes
RUNTIME     — what an executor is observed doing
EXTERNAL    — what the target system proves happened
```

### 4. Durable substrate does not remove application idempotency

Temporal, DBOS, and Restate all provide strong durable execution semantics, but arbitrary external operations remain at-least-once in the meaningful failure case:

```text
external effect succeeds
→ worker/process loses acknowledgement
→ retry may happen
```

Temporal's mature model explicitly separates deterministic workflow control from side-effecting Activities and expects Activities to be idempotent where retries are possible.

**MAPS_L implication:** DBOS/Restate/Temporal are reference bars and possible future evaluation candidates, not current substrate recommendations. Any MAPS external-effect path still needs stable operation identity, effect evidence, and reconcile-before-retry behavior.

### 5. DSH gives implementation-backed rooted history and continuation primitives

DeepSeek Harness exposes useful concrete mechanisms:

- append-only typed Session events;
- single-writer persistence handles;
- explicit flush/durability barriers;
- pure projections into model-visible history;
- compaction as auditable `start -> replacement -> end` events rather than silent transcript mutation;
- task DAGs with CAS revisions;
- durable queued-minus-delivered mailboxes;
- continuable subagent settlement protected by renewed observation-token identity (`activation.poke`), so an old idle observation cannot settle a newly reactivated child.

**MAPS_L implication:** these are strong references for #247 durable project-memory work, #248 context compilation, 6.19 helper continuity, and any future rooted-conversation implementation. They support MAPS_L's existing rule that durable truth should outlive model context.

They do **not** imply importing DSH wholesale.

## Portable regression cases worth importing when the owning mechanism is touched

1. stale owner completes after lease takeover -> commit rejected;
2. heartbeat/claim expires during host sleep -> recovery does not infer ownership from process liveness;
3. controller restarts while executor survives -> no duplicate executor is launched without reconciliation;
4. old attempt produces output after new generation begins -> stale output rejected;
5. missed scheduler ticks -> reconcile current state once rather than replay every missed turn;
6. process alive but no useful progress -> liveness and progress remain separate signals;
7. incomplete runtime observation -> deterministic policy returns defer/unknown rather than destructive guess;
8. stale checkpoint writer races newer checkpoint -> old writer cannot roll state backward;
9. child becomes active after an earlier idle observation -> stale settlement observation cannot terminate the new activity;
10. context compaction crash between start/end -> history remains reconstructable and explicitly incomplete rather than silently corrupted.

The detailed test IDs and upstream anchors live in the pinned Pilot test catalogue and DSH packets.

## Disposition

`STRENGTHEN_EXISTING_OWNER`.

Use this evidence to sharpen current Harness Mechanics/recovery/context tests when those rows are worked. No dependency adoption, roadmap status change, or second task/workflow authority follows from this note.