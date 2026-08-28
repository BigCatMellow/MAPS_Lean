# Operator Request Compilation

Use this when a normal-language request is clear to a human collaborator but not
yet durable/bounded enough for a fresh agent to execute safely.

This method compiles intent into the existing MAPS task contract. It does not
create a new authority layer. Global authority comes from [`AGENTS.md`](../AGENTS.md);
child work inherits the approved roadmap permission envelope and may narrow it but
must not silently expand it.

## Core transformation

```text
operator request + approved project state
        ↓
resolve referents / recover live truth
        ↓
shape existing MAPS task fields
        ↓
AGI-ready execution contract
        ↓
smallest sufficient worker/context packet
```

The compiled prompt is a derived rendering, never another source of truth.

## Minimum output

Include only fields that materially affect execution:

```text
GOAL
Observable result.

SOURCE OF TRUTH / CURRENT STATE
What must be inspected or trusted before acting.

OUTPUT BOUNDARY / NON-GOALS
What may and may not change.

INHERITED AUTHORITY
Which approved roadmap/task envelope this work inherits and any true
reauthorization boundary.

DEPENDENCIES
What must be true first.

ACCEPTANCE + VERIFICATION
Observable pass/fail and required evidence.

RECOVERY / ESCALATION
What the orchestration operator should research, retry, re-plan, or reassign;
and the exact condition that would require human reauthorization.
```

Do not invent parallel task fields merely for request compilation.

## Rules

### Preserve explicit intent

The request and approved project scope are the strongest sources for intended
outcome. Do not replace a narrow request with a broader project.

### Inherit authority; never expand it silently

A child task does **not** reset permission to zero. It inherits standing authority
from its approved parent roadmap/task.

The compiler may:

- carry that authority into the child contract;
- narrow it for the child;
- make implicit in-scope implementation boundaries explicit; and
- identify consequential actions already preauthorized by the parent envelope.

It may not silently add a new objective, broaden scope, or authorize an action
outside that envelope.

For actions such as merge, publish, delete, spend, grant permissions, or create
material external effects, ask one question: **is this action already inside the
approved permission envelope/preauthorization?**

- **Yes:** carry the authority forward; do not create another human gate.
- **No/unknown:** prepare/research safely as far as authorized, then record the
  exact reauthorization boundary.

Passing CI/review is evidence that conditions are satisfied; it neither creates
missing authority nor revokes inherited authority.

### Resolve references from live state

For requests such as `continue`, `do the next one`, `fix the blocker`, or
`handle these PRs`, recover the current referent from authoritative state before
shaping the task. Do not freeze stale chat summaries into a new contract when
current evidence is available.

### Separate evidence quality

When material, label claims `VERIFIED`, `REPORTED`, `ASSUMED`, or `UNKNOWN`.
Structure may be inferred; consequential facts may not be silently invented.

### Resolve questions internally first

Do not turn concise requests into interviews. Use repository evidence, safe
inspection, focused helpers/research, and an independent challenger when useful.
The orchestration operator decides inside inherited authority.

Human input is required only when the unresolved answer would materially change
the approved objective/scope/permission envelope or requires a human-only
preference/authority decision.

### Keep simple work simple

A small request may compile to a few sentences. Prompt length and artifact count
are not quality metrics.

## Procedure

```text
1. Read the request literally.
2. Recover live referents/current state where needed.
3. Identify the approved parent roadmap/task and inherited permission envelope.
4. Extract outcome, boundary, dependencies, acceptance, and verification.
5. Resolve material in-scope unknowns through evidence/helpers/research.
6. Mark any true authority-envelope crossing explicitly.
7. Run AGI readiness.
8. Render the smallest sufficient worker packet and execute/continue.
```

If the requested work cannot be tied to an approved objective/envelope, keep it
in shaping/research or request the missing scope authorization. Do not ask for
human approval merely because the child task is new or consequential.

## Example

Operator request:

> Get these pull requests under control; they're getting out of hand.

A compiled contract may say:

```text
Goal: reduce and organize the current PR backlog safely.
Current state: inspect live main, open PR heads/bases, CI, review state, and stack dependencies.
Inherited authority: use the already-approved maintenance/integration roadmap envelope.
Allowed: triage, synchronize stacks, repair in-scope review blockers, run CI/review, and merge when merge is already authorized by that envelope and gates pass.
Outside envelope: unrelated features, new architecture, or publication/destructive actions not already authorized.
Success: remaining integration queue is explicit, approved work is advanced as far as authority/evidence allow, and only true boundary blockers remain.
```

The compiler makes existing authority operational; it does not require the human
to re-grant it one child task at a time.

## Future automation boundary

An automated Request Compiler should remain a shaping mechanism, not an authority
store. Evaluate it for intent preservation, false scope expansion, invented
permission, missed boundaries, unnecessary escalation, AGI completeness, context
economy, and continuation/reference resolution.
