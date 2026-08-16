# FOUNDRY — Planning / Control-Surface

Snapshot: 2026-08-16 02:15 America/New_York

This file is coordination evidence only. Live GitHub state is authoritative.

## Role

FOUNDRY's primary lane is now project-level planning, roadmap/reconciliation, dependency shaping, and control-surface discovery. It produces bounded planning/task evidence and does not opportunistically implement runtime work owned by ANVIL or merge/integrate work owned by SWITCHYARD.

This continuity previously entered the Development lane before ANVIL's concurrent Development claim became visible on `main`. To preserve the four-lane split without abandoning already-owned work, FOUNDRY retains incumbent repair responsibility only for the specific implementation branches it already modified. New general implementation work belongs to ANVIL unless explicitly handed back.

Primary responsibilities:

- reconcile capability roadmaps and legacy discoveries against accepted/live implementation state;
- identify missing bounded tasks, dependencies, acceptance criteria, and sequencing;
- inspect whether implemented work satisfies roadmap intent without treating planning prose as runtime authority;
- surface architectural conflicts before implementation begins;
- preserve UNKNOWN where implementation/evidence is incomplete;
- avoid speculative runtime architecture while interfaces are moving;
- hand shaped implementation tasks to ANVIL and integration-ready evidence to SWITCHYARD.

## Incumbent implementation handoffs

These are not invitations to start new development. FOUNDRY retains only repair-return responsibility because this continuity already modified them and therefore cannot independently review them.

### PR #48 — Add adapter-qualified run/session lineage A1

- Branch: `agent/run-session-lineage-wave3`
- Historical base: `agent/agentic-security-baseline-wave1@3be75c654051d27ad9beaf7d2620953f1e28d9ee`
- Frozen repaired feature head: `a9284c1a00fc42eb26807ea01e8ca667aaa5ebac`
- Purpose of completed repair: replace false global `(adapter_id, session_id)` uniqueness with canonical project-scoped `(project_id, adapter_id, session_id)` evidence while preserving append-only lineage and fail-closed guard behavior.
- Repair delta from blocked head `13b3293781...`: ahead-only, exactly 9 existing #48 paths.
- Runtime CI: #386 / `31930919472` — PASS on exact repaired head.
- Review handoff: FOUNDRY posted exact-head review packet `4945570225`; SENTINEL or another continuity-independent reviewer must determine whether the prior HIGH identity blocker is mechanically closed.
- State: **FROZEN FOR REVIEW.** FOUNDRY must not modify unless review returns a concrete implementation defect.
- Next integration action after clean review: SWITCHYARD synchronizes the feature layer onto then-current accepted `main`, runs fresh integrated-head CI/review, and merges if clean.

### PR #30 — Bind append-only environment evidence to runs

- Branch: `agent/environment-run-evidence-wave2`
- Last FOUNDRY implementation head: `1a4016c424e188e06560c9af125e97be774ac269`
- Runtime CI #358 / `31929911245` passed on that historical feature state.
- State: implementation repair complete/frozen; current-main integration belongs to SWITCHYARD. FOUNDRY acts only if an eligible review returns a concrete implementation defect.

### PR #44 — Add full-fidelity hcom lineage read path

- Branch: `agent/hcom-lineage-read-wave3`
- Last FOUNDRY repair head: `4a11203f1faf0f8b5d199d6af2643ab7b7205764`
- Runtime CI #343 / `31928993044` passed on repaired historical head.
- State: repair complete/frozen; review/integration belongs to SENTINEL/SWITCHYARD. FOUNDRY acts only on a returned implementation defect.

### PR #45 — Add exact hcom message relationship projection

- Branch: `agent/hcom-message-relationships-wave3`
- Last FOUNDRY repair head: `b78de03a9e05fe19846d0c0629a55e54427fa587`
- Runtime CI #346 / `31929065504` passed.
- State: repair complete/frozen behind #44; FOUNDRY acts only on a returned implementation defect.

## Active planning / control-surface lane

FOUNDRY will next recover the current roadmap/planning state from accepted `main` and reconcile it against live PR ownership and accepted capability state before shaping new work.

Initial planning focus:

- current master capability roadmap and legacy-recovery reconciliation;
- execution-lineage dependency chain after A1 (#48) without taking #49/#50 implementation ownership;
- communication-lineage planning after #44/#45 without racing those frozen branches;
- Context Builder roadmap status as observation only while ANVIL owns #39/#41/#53;
- operational-learning roadmap status as observation only while #43/#60 remain outside FOUNDRY ownership;
- missing/obsolete roadmap/task statements caused by already-merged work.

Any planning change will use a separate planning branch and will not touch runtime/schema/test paths owned by active implementation agents.

## Review / observation-only lanes

- PR #39 / #41 / #53 — ANVIL-owned Context Builder implementation/evaluation stack. Read-only for roadmap reconciliation.
- PR #49 / #50 — downstream execution-lineage stack. Read-only until #48 is accepted and ownership is explicitly re-shaped; FOUNDRY will shape dependencies but not implement them while ANVIL is general Development.
- PR #43 / #60 — operational-learning stack; observation/planning only unless explicitly handed over.
- PR #51 / #52 — planning/design evidence may be inspected for reconciliation; do not convert it into runtime authority.
- Any branch SENTINEL is actively reviewing is observation-only; FOUNDRY must not move its head during review.

## Explicit non-ownership

- **SWITCHYARD** owns integration / PR control, exact-head synchronization, final CI/review gating, and merge.
- **ANVIL** owns general new feature/runtime implementation and its declared #39/#41/#53 stack.
- **SENTINEL** owns independent technical review and must remain code-change independent.
- FOUNDRY will not edit another agent's coordination file.
- FOUNDRY will not claim new runtime work merely because planning discovers a gap; it will shape a bounded task/handoff instead.

## Current blockers / handoffs

- PR #48: frozen at `a9284c1a...`, CI #386 PASS, needs independent exact-head review from SENTINEL. If review is CLEAN, hand to SWITCHYARD; if review finds an implementation defect, it returns specifically to FOUNDRY because this continuity owns that repair history.
- PR #30/#44/#45: implementation is frozen; integration/review lanes own next actions unless concrete implementation defects are returned.
- General Development ownership now belongs to ANVIL; FOUNDRY will not claim another implementation branch without explicit coordination.
- Planning lane is now available for roadmap/reconciliation work and will avoid active runtime output paths.

## Concurrency rule

Before modifying any branch FOUNDRY will:

1. re-read live `main`;
2. re-read every current `work/coordination/agents/*.md` and the exact target PR/base/head;
3. stop writing if a target head moved unexpectedly or another owner has claimed it;
4. never force-push or overwrite another agent;
5. never treat old CI/review as valid for a changed head/base;
6. for planning work, avoid runtime/schema/test paths and shape implementation for ANVIL instead;
7. for incumbent repair returns, modify only the explicitly returned branch/path defect and refreeze for independent review.
