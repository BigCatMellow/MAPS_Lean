# Agent-Grade Instructions (AGI)

AGI means instructions clear enough for a capable agent to act without guessing
intent, authority, boundaries, or proof of success.

AGI is a quality standard, not a larger prompt or a reason to ask the human more
questions.

## Core rule

When material, an executable instruction makes clear:

1. **Goal** — observable result.
2. **Source of truth** — authoritative files/systems/evidence.
3. **Inputs** — what to inspect/use.
4. **Outputs** — what may be produced/changed.
5. **Owner** — one accountable owner.
6. **Inherited authority** — approved roadmap/task permission envelope.
7. **Boundaries** — what may change, must not change, or requires human
   reauthorization.
8. **Procedure** — only where order matters.
9. **Pass/fail** — observable acceptance criteria.
10. **Verification** — proof.
11. **Failure branches** — retry/research/re-plan/reassign/rollback behavior.
12. **Escalation** — true authority-boundary triggers.
13. **Handoff/continuation** — durable state when work spans sessions/tasks.

Not every small task needs thirteen headings.

## Instruction layers and approval inheritance

```text
AGENTS.md
  stable rules + autonomous orchestration invariant
      ↓
approved roadmap/project
  objective + permission envelope + human reauthorization triggers
      ↓
playbook/*.md
  methods inside that authority
      ↓
task record
  exact child contract; inherits and may narrow roadmap authority
      ↓
handoff / evidence
  continuation state and proof
```

A child task does **not** reset authority. If the roadmap already authorized the
work, starting the child task, reaching a checkpoint, completing review, or
moving to the next task does not require another human approval.

## Facts, assumptions, and unknowns

Use `VERIFIED`, `REPORTED`, `ASSUMED`, and `UNKNOWN` when relevant. Never silently
promote uncertainty to verified fact.

For consequential uncertainty:

```text
authoritative evidence
→ safe inspection
→ focused helper/research
→ independent challenge when useful
→ orchestration operator decides inside inherited authority
→ human only for permission-envelope crossing
```

## Outcome instructions beat activity instructions

Prefer observable results:

```text
Weak: Improve login.
Better: Valid credentials create a session and reach the dashboard; invalid
        credentials do not create a session.
```

## Boundaries should be explicit

Useful classes:

- **MAY CHANGE** — inside current authority.
- **MUST NOT CHANGE** — outside task/roadmap boundary.
- **MAY CHANGE IF NECESSARY** — may be added by task amendment when still inside
  inherited roadmap authority.
- **HUMAN REAUTHORIZATION REQUIRED** — would materially leave inherited
  authority.

Human reauthorization is not synonymous with “consequential.” A consequential
choice that the approved roadmap explicitly authorized remains executable after
its required checks/review.

## Verification is part of the instruction

```text
ACT → OBSERVE → COMPARE → CORRECT → REPEAT
```

Examples: named tests, bug reproduction, screenshots against reference,
benchmarks against threshold, migration dry runs, acquisition/install/launch
walkthroughs.

If required proof cannot be produced, the task is not complete. Recover or
record the blocker.

## Failure branches

Examples:

```text
IF a required test cannot run
THEN diagnose/recover; mark BLOCKED only if still unresolved.

IF a new in-scope output path becomes necessary
THEN amend the task, re-check readiness, continue.

IF a key assumption is false
THEN research/re-plan inside the approved envelope.

IF an important in-scope choice remains uncertain
THEN use helper/research + independent challenge; orchestration operator decides.

IF an irreversible action is explicitly preauthorized with bounded target,
impact, recovery, and verification
THEN execute after required checks without asking again.

IF an irreversible action is not preauthorized
THEN obtain human reauthorization for the resolved action.

IF unrelated work is discovered
THEN record it; do not silently expand the approved roadmap.
```

## Agent-ready task gate

A consequential task is `READY` when a suitable worker can answer:

```text
What result am I producing?
What should I trust?
What authority do I inherit?
What may/must I not change?
How is success judged and verified?
What review is required?
How do I recover from likely failures?
When is human reauthorization genuinely required?
What happens after this task is done?
```

If a material answer is missing, shape/research internally first.

## Mission-meeting critique

Participants check for missing dependency, unsupported assumption, likely
failure, weak verification, unnecessary scope, unsafe/useful parallelism, and
hidden authority crossings.

A useful finding:

```text
Concern: <specific issue>
Evidence: <why>
Effect: <risk/failure>
Proposed change: <concrete adjustment>
Authority: <inside approved envelope | needs human reauthorization>
```

Do not invent objections merely to participate.

## Review contract

Review against agreed task/criteria. Do not invent requirements.

```text
Failed criterion: <criterion>
Evidence: <proof>
Required correction: <change>
Do not change: <unaffected work>
```

`APPROVED` returns control to the orchestration operator to close/reconcile and
continue the roadmap. Review is not a request for human permission.

## Tool descriptions should be agent-grade

A state-changing tool should document `USE WHEN`, `DO NOT USE WHEN`, inputs,
result, side effects, failure/recovery, and authority boundary.

Tools mutate state; they do not invent authority beyond the approved envelope.

## Detail without micromanagement

Specify result, context, constraints, authority, acceptance, and proof. Allow
bounded implementation judgment.

Increase procedural detail only when order is important, the tool boundary is
dangerous, the worker is unreliable for the task, prior attempts repeatedly
fail, or mistakes are hard to detect afterward.

## Core MAPS rule

**Clear outcome. Relevant evidence. Approved permission envelope. Autonomous
execution inside it. Internal challenge before human escalation. Observable
proof. Durable continuation.**
