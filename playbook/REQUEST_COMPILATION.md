# Operator Request Compilation

Use this method when an operator gives a normal-language request that is clear to a
human collaborator but not yet durable or bounded enough for a fresh agent to
execute safely.

The purpose is not to make prompts longer. It is to preserve operator intent while
turning conversational shorthand into the existing MAPS task/AGI contract.

## Core transformation

```text
operator request
    ↓
request compilation / task shaping
    ↓
AGI-ready execution contract
    ↓
Context Builder selects execution evidence
    ↓
worker packet / provider prompt
```

The compiled prompt is a **derived rendering** of the execution contract. It is not
another authority store.

## Request Compiler versus Context Builder

Keep these responsibilities separate:

- **Request Compiler / shaper:** determines what the operator is asking for, what
  boundaries follow from that request, what remains unknown, and what an executable
  task contract must say.
- **Context Builder:** determines which sources/evidence a worker needs to execute
  the already-shaped contract.

The compiler may inspect authoritative project/task state when that state is needed
to resolve a reference such as "continue this", "fix the PRs", or "do the next
one". It must not turn retrieved context into new intent or permission.

## Inputs

Use the smallest sufficient set:

1. the operator's request;
2. the current canonical task/project state when the request refers to ongoing work;
3. applicable `AGENTS.md`, policy, accepted decisions, and existing task contract;
4. directly relevant live evidence needed to resolve references or current state.

Do not load broad history merely because it exists.

## Output contract

A compiled request should make these fields available when material:

```text
GOAL
Observable result the operator wants.

SOURCE OF TRUTH
What must be inspected or trusted before acting.

INPUTS / CURRENT STATE
Live facts needed to begin.

ALLOWED ACTIONS / OUTPUT BOUNDARY
What the worker may change or do.

NON-GOALS / MUST NOT CHANGE
Scope explicitly outside the request.

AUTHORITY
Decisions delegated to the worker versus reserved to the operator/policy.

DEPENDENCIES / ORDER
What must happen first.

ACCEPTANCE CRITERIA
Observable pass/fail conditions.

VERIFICATION / EVIDENCE
How the worker proves completion.

STOP / ESCALATION
Material unknowns or conditions that require reshaping, research, or approval.

CONTINUITY
What must be left for a future worker if execution stops.
```

These map to the existing Agent-Grade Instructions standard and task lifecycle. Do
not create parallel task fields just for request compilation.

## Compilation rules

### 1. Preserve explicit intent

Operator wording is the strongest source for intent and requested outcome. Do not
replace a narrow request with a broader "better" project.

### 2. Inherit constraints, not authority

Stable repository rules and existing task boundaries may narrow the compiled task.
They do not grant permissions the operator did not grant.

```text
request + known constraints → bounded task

not

request + agent inference → expanded authority
```

Action-specific consequential authority must be traceable to either the operator's
request or already-canonical authority. A compiler must not infer permission to
merge, publish, delete, spend, send externally, or perform another consequential
action merely because that action would help achieve the requested outcome. Passing
review, policy, or CI gates constrains the use of authority when it exists; those
gates do not create the missing authority. When consequential permission is absent,
compile the task to prepare the action/evidence and stop or escalate at that boundary.

### 3. Resolve references from live state

For continuation language such as:

- "continue";
- "do what you need to make progress";
- "handle these PRs";
- "fix the next blocker";

recover the live referent before compiling the task. Do not freeze stale chat
summaries into the new contract when current evidence is available.

### 4. Separate explicit, derived, and unknown

When material, label claims as:

- `VERIFIED` — directly established from authoritative/current evidence;
- `REPORTED` — supplied by a source but not reproduced here;
- `ASSUMED` — provisional and safe enough for the bounded work;
- `UNKNOWN` — unresolved and not safe to invent.

A compiler may infer structure. It may not silently infer consequential facts.

### 5. Ask only when the missing fact is material

Do not turn every short request into an interview. If repository evidence can resolve
an ambiguity safely, inspect it. If a bounded default is harmless and reversible,
use it and state it when relevant.

Escalate when the missing answer can materially change:

- intent;
- scope;
- cost;
- security/privacy;
- external behavior;
- irreversible action;
- operator approval;
- acceptance criteria.

### 6. Keep simple work simple

A small request may compile to a few sentences. A long-running integration task may
need a full contract. Prompt length is not a quality metric.

### 7. Prompt rendering comes last

Do not make provider prose the canonical object. Shape the execution contract first,
then render the smallest worker-facing prompt that carries the necessary contract
and pointers to context.

## Procedure

```text
1. Read the operator request literally.
2. Identify the requested outcome and referents.
3. Recover live authoritative state only where needed.
4. Extract explicit constraints and permissions.
5. Apply repository/task constraints that narrow the work.
6. Identify material unknowns or conflicts.
7. Draft the execution contract using existing MAPS task fields.
8. Run the AGI readiness questions.
9. If material intent/authority remains unknown, keep NEEDS_SHAPING/BLOCKED.
10. Otherwise render the bounded worker prompt/packet.
```

## Example

Operator request:

> Get these pull requests under control; they're getting out of hand.

A correct compilation may derive:

```text
Goal: reduce and organize the existing PR backlog safely.
Current-state requirement: inspect live main, open PR heads/bases, CI, review state,
and stack dependencies before acting.
Allowed: triage, synchronize accepted stacks within existing task authority, fix exact
review blockers within scope, run CI, and prepare review/merge-ready evidence.
Consequential boundary: merge only when the operator request or existing canonical
task authority separately permits merge; otherwise stop at merge-ready evidence and
escalate. Passing CI/review gates does not itself grant merge permission.
Not allowed: invent new architecture, start unrelated feature work, race another
active branch owner, infer consequential permission from the backlog-reduction goal,
or treat a passing gate as authorization.
Success: the backlog is classified and reduced where existing authority permits,
merge-ready work is clearly identified where authority is absent, ancestry is clean,
stale/superseded work is identified, and the remaining integration queue is explicit.
```

The compiler did not invent a new product goal or consequential permission. It
expanded the operational contract needed to pursue the stated goal while keeping
any separately required authority explicit.

## Explain mode

When the operator wants to learn rather than immediately dispatch work, expose the
same structure as a reusable prompt recipe:

```text
I need [OUTCOME].
First recover [CURRENT STATE].
You may [ALLOWED ACTIONS].
Do not [BOUNDARIES].
Preserve [INVARIANTS].
Success means [ACCEPTANCE CRITERIA].
Verify with [EVIDENCE].
Stop/escalate if [MATERIAL CONDITIONS].
Leave [HANDOFF/CONTINUITY].
```

Explain mode teaches the contract; it does not require the operator to become a
"prompt engineer."

## Future automation boundary

Today this can be performed by an owner/shaper using the existing task lifecycle and
AGI standard. A future automated Request Compiler should remain a **proposal/shaping
mechanism**, not an authority layer.

Before automatic compilation is promoted into normal task intake, evaluate it on a
frozen request corpus for at least:

- operator-intent preservation;
- false scope expansion;
- invented permission/approval;
- missed material boundaries;
- unnecessary clarification/escalation;
- AGI completeness;
- prompt/context economy;
- continuation/reference resolution against live state.

A better score may justify a proposal. It may not self-authorize a production
change.