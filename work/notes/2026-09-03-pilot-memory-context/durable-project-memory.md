# Durable Project Memory for Pilot-managed work

Status: **deferred design finding**. Related issue: **#247**.

## Problem

When Pilot/MAPS_L is used through Claude, Codex, ChatGPT, or another session-bound interface, useful project knowledge can remain trapped in the chat:

- what was changed;
- why it was changed;
- what failed and should not be retried;
- what decisions still govern;
- what remains incomplete;
- what was verified;
- what procedure was discovered;
- what the next worker should do.

The operator's desired behavior is that durable work should be recoverable from the **project**, not require locating the original conversation.

This applies beyond code repositories. The requirement includes:

- software/code projects;
- research/planning projects;
- documentation/work-product projects;
- repeatable procedures/workflows where the durable result is how something is done.

## Core guarantee

> **Pilot leaves the project, not the conversation, holding the information required to understand and continue the work.**

A durable Pilot project should not be successfully handed back while consequential state exists only in transient chat/session memory.

## Proposed invariant

**PERSIST-01 — Durable Project Memory**

When Pilot performs work whose result, reasoning, procedure, or continuation may matter after the current session, Pilot MUST identify a durable project root. If the project does not already have MAPS project memory, initialize/adopt an appropriate project-memory surface. During work and before handback, reconcile that memory with what is actually true.

This should be automatic for durable work, not dependent on the human remembering to ask for a handoff or summary.

## Relationship to existing MAPS_L architecture

Do not invent a second documentation or authority system. Reuse existing ideas:

- [`playbook/PROJECT_BOOTSTRAP.md`](../../../playbook/PROJECT_BOOTSTRAP.md) already defines a **minimum project brain** a fresh operator should recover: objective, checked facts, DONE, scope, permission envelope, roadmap/next work, unknowns/risks, and proof.
- Portable Deployment already chose project-local `.maps/` Markdown state for external projects rather than a second SQLite task-truth instance.
- The Portable Deployment layout already includes roadmap/tasks/reviews/handoffs.
- Existing handoff/task/decision formats already capture much of the information needed for continuity.
- [`playbook/INFORMATION_LIFECYCLE.md`](../../../playbook/INFORMATION_LIFECYCLE.md) already requires `capture → review → disposition → reconcile when reality changes` and says durable information should not be an island.

The missing feature is **automatic adoption/initialization + reconciliation + resume**, not raw storage capability.

## Project-root/adoption behavior

Candidate precedence:

1. If an applicable `.maps/` exists in the current directory or a valid ancestor, adopt it.
2. Otherwise, if the work is inside a Git repository, default to the Git root.
3. Otherwise, use an explicitly supplied project directory/root when available.
4. If an existing MAPS project-memory binding clearly identifies the target, adopt it rather than creating another project.
5. If durable work has **no existing project folder**, the future design must decide how Pilot establishes one instead of allowing the work to remain chat-only. The global parent workspace/naming policy is not decided here.
6. Do not create duplicate `.maps-2`, `project-again`, or per-chat project folders merely because a new session starts.
7. Throwaway/local experiments should stay lightweight; durability must not become ceremony for trivial work.

The exact root-selection algorithm must explicitly handle nested repositories, worktrees, malformed/foreign `.maps/` directories, non-Git projects, and refusal/ambiguity cases.

## Candidate project-memory layout

```text
<project>/
  ... project-native files ...
  .maps/
    README.md
    PROJECT.md
    CURRENT.md
    roadmap.md
    tasks/
    decisions/
    handoffs/
    reviews/
    evidence/
```

Not every directory/file must exist or contain content. Create durable structure only where it adds forward value.

For procedures/workflows, prefer the project's existing canonical runbook/README/docs when one already owns the procedure. If no canonical owner exists and a procedure is reusable, the design may add a procedure-oriented memory surface or link a project-native document, but **one concept still gets one owner**. Do not duplicate an existing runbook merely to have a copy under `.maps/`.

## `.maps/README.md` — front door

This should be a very short router for a fresh agent, for example:

```text
Project identity
Read PROJECT.md for stable purpose/boundaries
Read CURRENT.md for reconciled current state
Current task: <link>
Chat history is not authoritative project state
```

A fresh session should be able to receive an instruction such as:

```text
Use Pilot on this project. Read `.maps/README.md` and continue where the project left off.
```

The old chat should be optional historical context, not required operational state.

## `.maps/PROJECT.md` — stable project brain

Capture durable, relatively stable facts:

- goal / intended user or operator;
- checked current reality where it matters;
- Definition of DONE and final proof;
- scope / non-goals;
- constraints / quality bar;
- permission/authority envelope where relevant;
- important risks/unknowns;
- roadmap pointer;
- durable history only when it changes how future work should proceed.

Do not rewrite this file for routine session chatter.

## `.maps/CURRENT.md` — fast resume surface

This was identified as the key missing artifact.

It should answer, in minimum sufficient context:

- last reconciled revision/time;
- what is true now;
- what was completed;
- what remains;
- current task/status;
- verification performed and result;
- current blocker/risk;
- consequential decisions and links;
- exact next action;
- important `do not redo` / `do not assume` guidance.

Example shape:

```text
# Current State

Last reconciled: <revision/date>

## What is true
- ...

## Work completed
- ...

## Current task
- ...

## Verification
- ...

## Remaining
1. ...

## Important decisions
- ...

## Resume
Next action: ...
```

`CURRENT.md` is a **reconciled view**, not a new authority island. Source/tests own code behavior; Git/GitHub own branch/PR/CI facts; accepted task/control-plane state owns task authority; decision records own consequential rationale. `CURRENT.md` explains the current implication and links to those owners.

## The deeper finding: reconciliation, not storage

MAPS_L already stores a large amount of history across code, state, playbooks, roadmaps, tasks, reviews, handoffs, research, decisions, migration/history, branches, and PRs.

The larger continuity failure is **memory reconciliation and disposition drift**: a project can remember many artifacts and still force a fresh agent to reconstruct:

- what is true now;
- why it is true;
- what changed the older understanding;
- what was only proposed versus actually decided;
- what was fully versus partially implemented;
- what remains unresolved;
- what was rejected/superseded/dormant;
- when an older idea should be revisited.

Preserve these principles:

> **Preserve history deeply, surface current meaning shallowly.**

> **MAPS does not need to remember more; it needs to get better at knowing what its remembered information means now.**

The project memory should preserve the relationship:

```text
proposal
  → decision
  → implementation
  → partial/full resolution
  → remaining work
  → rejected / dormant / superseded disposition
```

A file existing is not enough evidence that its old wording is still current.

## Reconciliation lifecycle

Candidate flow:

```text
Pilot invoked
  → resolve/adopt project root
  → initialize `.maps/` only if needed
  → recover PROJECT + CURRENT + relevant task/decisions
  → perform work
  → reconcile forward-relevant durable state
  → preserve/link decision, evidence, procedure, or handoff when needed
  → run chat-loss durability check
  → hand back
```

Reconcile at semantic boundaries, not after every command/tool call. Useful triggers include:

- first project-memory adoption/creation;
- meaningful task-state transition;
- consequential decision made/reversed;
- verified evidence materially changes current understanding;
- responsibility/session transfer;
- Pilot is about to report durable work complete/paused/blocked;
- a resume/context packet is requested or context loss is imminent.

## What to preserve

Preserve when forward-relevant:

- what materially changed;
- why consequential decisions were made;
- failed approaches only when avoiding them later matters;
- current state;
- unresolved work;
- verification performed;
- constraints/boundaries;
- evidence/source references;
- exact next action;
- reusable procedure/workflow knowledge when no stronger canonical owner already exists.

Do not preserve by default:

- full conversation transcripts;
- repeated explanations;
- tool narration;
- routine status chatter;
- dead speculation;
- every failed command;
- one session-log file per chat.

## Session/handoff behavior

Do **not** create a durable session log for every conversation.

- Routine session: reconcile `CURRENT.md` and active task as necessary.
- Consequential decision: create/update the canonical decision record if durable rationale is needed.
- Responsibility/session transfer: use the existing handoff shape.
- Evidence: preserve only evidence needed to establish state/verification/decision.

## Resume/context surface

Explore a future surface such as:

```text
maps resume <project>
```

or an equivalent Pilot entrypoint.

It should compile an **ephemeral, non-authoritative** context packet from durable/authoritative sources:

```text
PROJECT
CURRENT STATE
CURRENT TASK
IMPORTANT DECISIONS
VERIFIED EVIDENCE
NEXT ACTION
```

Durable Project Memory and Context Compilation are distinct layers:

```text
Durable Project Memory
= what the project durably knows and how current meaning is reconciled

Context Compilation
= which minimum subset of that knowledge this agent needs now
```

## Completion/durability gate

Central acceptance question:

> **If this chat disappeared right now, what material project knowledge would be lost?**

Candidate `PMEM-DONE` checks:

- [ ] current project state is durable;
- [ ] consequential decisions are durable;
- [ ] unresolved work is durable;
- [ ] verification/evidence needed later is durable;
- [ ] exact next action is recoverable;
- [ ] no important fact exists only in chat/session memory.

This does **not** mean storing the chat. It means storing or linking the forward-relevant fact in its canonical durable place.

## Verification cases to require later

- existing `.maps/` is adopted, never duplicated;
- fresh project receives minimum useful memory only once;
- new chat continues correctly without original transcript;
- Claude ↔ Codex ↔ ChatGPT switch does not require provider-specific history;
- non-code durable project with no Git repository;
- durable procedure/workflow with no code change;
- existing canonical runbook is linked/adopted rather than duplicated;
- partially completed work distinguishes DONE from remaining;
- rejected/superseded old proposal is not surfaced as current truth;
- stale `CURRENT.md` is reconciled when authoritative state changed;
- worktrees/nested repos are handled safely;
- throwaway work remains lightweight;
- failure to persist memory cannot falsely imply completed work;
- independent review verifies that the feature did not create a second authority store.

## Non-goals

- automatic full-chat archival;
- one durable file per AI session;
- a second mutable task/status database;
- replacing source/Git/GitHub/accepted task state as authority;
- copying all internal MAPS_Lean control-plane files into every project;
- forcing full project bootstrap for every trivial Pilot interaction.
