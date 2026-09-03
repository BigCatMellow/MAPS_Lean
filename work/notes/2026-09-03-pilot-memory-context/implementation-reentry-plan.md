# Implementation / re-entry plan

Status: **deferred sequencing note**. This is not live task authority.

## Purpose

This note explains how to pick up the captured findings later without treating a 2026-09 conversation snapshot as if it were still current.

The two major future arcs are:

1. **Durable Project Memory** — issue #247;
2. **AI instruction/context compilation and wording cleanup** — issue #248.

They are related but should not be collapsed into one implementation because they solve different problems:

```text
Durable Project Memory
= durable, reconciled project knowledge across sessions/providers

AI Context Compilation
= minimum applicable context selected for one agent/task now
```

## General re-entry gate

Before doing implementation work on either arc:

1. Read root `AGENTS.md`.
2. Recover current live GitHub state and active ownership/PR overlap.
3. Recover current `main` and the current owning roadmap/checklist state.
4. Re-read [`playbook/PROJECT_BOOTSTRAP.md`](../../../playbook/PROJECT_BOOTSTRAP.md), [`playbook/INFORMATION_LIFECYCLE.md`](../../../playbook/INFORMATION_LIFECYCLE.md), and the current Portable Deployment design where relevant.
5. Re-read issues #247/#248 plus this packet.
6. Identify which ideas already landed elsewhere while this work was deferred.
7. Re-shape the smallest coherent task from current accepted architecture.
8. Avoid runtime/schema/CLI seams currently owned by another active lane unless coordination explicitly assigns the overlap.
9. Require normal verification and independent review proportional to risk.

## Arc A — Durable Project Memory

### Phase A1 — architecture reconciliation/design

- Determine the current Pilot invocation seam.
- Determine the current Portable Deployment `.maps/` contract.
- Decide whether Durable Project Memory is owned primarily by Portable Deployment, Project Bootstrap, Information Lifecycle, Pilot itself, or a combination with one canonical normative owner.
- Specify project-root resolution/adoption/refusal behavior.
- Specify contracts for `.maps/README.md`, `PROJECT.md`, and `CURRENT.md`.
- Specify non-Git/no-existing-folder behavior.
- Specify procedure/workflow capture behavior without duplicating existing canonical runbooks.
- Specify semantic reconciliation triggers.
- Specify conflict/staleness behavior when `CURRENT.md` disagrees with authoritative state.
- Specify atomicity/failure behavior so a failed durability write cannot falsely imply the work was completed.
- Decide whether `maps resume` is the right surface or whether the current Pilot/context machinery already provides a better seam.

### Phase A2 — minimal implementation

Prefer a narrow first slice:

1. project-root/adoption utility;
2. idempotent minimum `.maps/` initialization;
3. a reconciled `CURRENT.md` update path;
4. integration with the smallest existing Pilot lifecycle seam;
5. no new database or authority source.

Do not start with a broad CLI redesign or a large context compiler unless accepted `main` has already consolidated those seams.

### Phase A3 — prove continuity

Use a real project and demonstrate:

```text
session/model A performs durable Pilot work
  ↓
chat/session disappears
  ↓
new session/model B receives only project + Pilot entrypoint
  ↓
B recovers project/current task/decisions/evidence/next action
  ↓
B continues correctly without reconstructing old chat
```

Test code and non-code/procedure cases.

## Arc B — AI instruction/context architecture

### Phase B1 — baseline before editing

Measure actual current behavior before changing prose:

- root always-loaded context size;
- common-case document count/hops;
- representative role/task routes;
- duplicated normative concepts;
- stale/current-state confusion;
- existing context-builder/Skill behavior;
- Digital Fungus route/read proxies.

Do not optimize against old numbers from these notes.

### Phase B2 — canonical rule ownership

- Identify what truly belongs in root `AGENTS.md` kernel.
- Identify conditional/specialist rules and their triggers.
- Identify actual duplicated normative concepts.
- Decide whether stable IDs (`AUTH-*`, `REV-*`, etc.) improve inheritance for those real duplicates.
- Preserve one canonical owner per rule.

### Phase B3 — routing/context prototype

Prototype an ephemeral context packet without changing authority.

Candidate packet fields:

```text
OBJECTIVE
SUCCESS / ACCEPTANCE
APPLICABLE AUTHORITY
ROLE
TASK / SUBJECT
SCOPE / ACTION BOUNDARY
REQUIRED METHODS
VERIFIED LIVE STATE
RELEVANT PROJECT MEMORY / DECISIONS
STOP CONDITIONS
NEXT LEGITIMATE ACTION
```

Record provenance/freshness/selection reason. Keep Required/Optional/Excluded distinctions where useful.

### Phase B4 — compare to baseline

Use representative scenarios:

- ordinary implementation;
- SENTINEL review;
- integration/SWITCHYARD work;
- research task;
- operator-blocked task;
- external Portable Deployment project;
- fresh continuation using Durable Project Memory.

Compare route correctness, safety/authority equivalence, context cost, and task success.

### Phase B5 — wording consolidation

Only after routing works:

- compress root/kernel prose where semantics are preserved;
- replace unsafe brevity wording with minimum-sufficient-context wording;
- convert repeated operational procedures to `WHEN / READ / DO / VERIFY / STOP` where clearer;
- link subordinate docs to canonical rules instead of restating them;
- keep rationale in design docs when it need not be always loaded.

### Phase B6 — safeguards

Add mechanical checks only for repeated observed failure classes:

- semantic/normative duplication advisory;
- route/read-cost regression;
- broken routing links;
- stale prose/config claims where mechanically detectable;
- context-packet provenance/freshness checks.

Do not create process or CI merely because it can be automated.

## Interaction between the arcs

Potential long-term pipeline:

```text
HUMAN INTENT
    ↓
PROJECT MEMORY ADOPTION / RECOVERY
    ↓
AGENT-GRADE TASK SHAPING
    ↓
AUTHORITY + BOUNDARY
    ↓
TASK CLASS
    ↓
CONTEXT ROUTER
    ↓
MINIMUM CONTEXT PACKET
    ↓
AI EXECUTION
    ↓
VERIFY
    ↓
RECONCILE DURABLE PROJECT MEMORY
    ↓
DONE / HANDOFF
```

This gives the two arcs a clean relationship:

- project memory supplies durable continuity;
- context compilation limits what is loaded now;
- execution changes the world;
- reconciliation makes forward-relevant meaning durable again.

## Collision / parallel-agent rule

Before each implementation slice, compare intended changed files/surfaces with active PRs/branches.

If another lane owns a central seam:

- do not opportunistically stack on it;
- shape a non-overlapping design/test slice if useful;
- otherwise keep the work deferred until accepted `main` exposes a stable seam.

The conversation already demonstrated this pattern when Project Memory implementation was deferred because active PRs were simultaneously editing central CLI/state files.

## Completion criteria for the overall findings

The captured work is not truly resolved merely because these notes exist.

Eventually, reviewers should be able to point from each finding to one of:

- implemented and verified;
- deliberately rejected with rationale;
- superseded by a better accepted mechanism;
- still deferred with a concrete re-entry condition.

This follows the information-lifecycle requirement that old findings need a current **disposition**, not just preservation.
