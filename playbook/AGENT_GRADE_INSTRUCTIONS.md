# Agent-Grade Instructions (AGI)

AGI means **Agent-Grade Instructions**: instructions clear enough for a capable
agent to act without guessing the project's intent, authority, boundaries, or
proof of success.

AGI is not a larger prompt. It is a quality standard for the instructions MAPS
already uses.

## Core rule

An executable instruction should make the following explicit whenever they
materially affect the work:

1. **Goal** — the observable result to produce.
2. **Source of truth** — which files, systems, decisions, or evidence are
   authoritative.
3. **Inputs** — what the agent should inspect or use.
4. **Outputs** — what must be produced, changed, or reported.
5. **Owner** — who is accountable for the result.
6. **Authority** — which decisions the agent may make itself.
7. **Boundaries** — what may be changed, what must not be changed, and what
   requires escalation.
8. **Procedure** — ordered steps only where order matters.
9. **Pass/fail** — observable acceptance criteria.
10. **Verification** — tests, screenshots, commands, reproduction steps, or
    other evidence the agent can use to check itself.
11. **Edge cases** — expected failure branches that should not be improvised.
12. **Stop/escalate** — conditions that require research, clarification,
    re-planning, or operator approval instead of guessing.
13. **Handoff** — the durable state another agent needs if work stops.

Not every small task needs thirteen headings. The information must simply be
available at the level where it matters.

## Instruction layers

Do not put every rule into one giant file. Use progressive disclosure:

```text
AGENTS.md
  stable authority, safety, ownership, and navigation rules
      ↓
playbook/*.md
  method-specific instructions
      ↓
project / roadmap
  project intent, constraints, decisions, and current plan
      ↓
task record
  exact execution contract for the current work
      ↓
handoff / evidence
  continuation state and proof
```

The agent should read the smallest sufficient set of instructions for the task.
Large instruction dumps consume context and make important rules harder to
identify.

## Facts, assumptions, and unknowns

Use explicit epistemic labels when a distinction matters:

- **VERIFIED** — directly inspected or reproduced.
- **REPORTED** — stated by a source but not independently verified here.
- **ASSUMED** — being used provisionally without proof.
- **UNKNOWN** — insufficient information to make the claim.

Never silently promote `ASSUMED`, `REPORTED`, or `UNKNOWN` to `VERIFIED`.

## Outcome instructions beat activity instructions

Prefer a result the agent can observe:

```text
Weak:
Build authentication.

Better:
A new user can create an account, sign in, sign out, restart the application,
and sign in again with the same account.
```

Tasks may describe implementation work, but project goals and acceptance
criteria should describe the state that must become true.

## Boundaries should be explicit

When useful, classify change authority as:

- **MAY CHANGE** — within the task owner's authority.
- **MUST NOT CHANGE** — outside the task boundary.
- **MAY CHANGE IF NECESSARY** — allowed only if the task record is amended
  before editing.
- **OPERATOR APPROVAL REQUIRED** — consequential choice that must be escalated.

Being assigned a task does not grant authority to change product intent, scope,
security policy, external behavior, cost, or irreversible state.

## Plan conditions before tasks

Backward planning should first describe conditions, not implementation guesses.

```text
Weak backward step:
Write the save system.

Better backward condition:
Saved game state survives a process restart and reloads without corruption.
```

After the required conditions are clear, shape the work needed to create them.

## Verification is part of the instruction

Give an agent something objective to compare its work against whenever
practical:

```text
ACT → OBSERVE → COMPARE → CORRECT → REPEAT
```

Examples:

- code change → run named test → inspect result;
- bug fix → reproduce bug → apply fix → repeat reproduction;
- UI change → render target viewport → screenshot → compare to reference;
- performance work → run named benchmark → compare to threshold;
- migration → execute dry run or fixture → verify resulting state.

If the required proof cannot be produced, the task is not complete. Record the
blocker rather than claiming success.

## Define failure branches

For important workflows, state what happens when normal assumptions fail.
Examples:

```text
IF a required test cannot run
THEN mark BLOCKED and record why.

IF a new output path becomes necessary
THEN amend the task boundary before editing it.

IF a key assumption is false
THEN stop implementation and re-plan.

IF an irreversible action becomes necessary
THEN obtain operator approval first.

IF an unrelated problem is discovered
THEN record it separately; do not silently expand scope.
```

These branches are more useful than telling an agent to "be careful."

## Agent-ready task gate

A consequential execution task is `READY` only when the agent can answer:

```text
What result am I producing?
What should I trust and inspect?
What may I change?
What must I not change?
What depends on this or blocks it?
How is success judged?
How do I verify it?
What review is required?
When must I stop or escalate?
```

If a material answer is missing, shape, research, or escalate before execution.

## Mission-meeting critique contract

Do not give meeting participants pretend personalities. Give them bounded
questions.

Each relevant participant checks for:

- missing dependency;
- unsupported assumption;
- likely failure mode;
- weak or impossible verification;
- unnecessary scope;
- unsafe parallel work;
- useful parallel work;
- operator decision that has been hidden inside an implementation choice.

A useful finding should be recorded as:

```text
Concern: <specific issue>
Evidence: <why we believe it>
Effect: <what fails or becomes risky>
Proposed change: <concrete adjustment>
```

If no material issue is found, record `NO ISSUE FOUND`. Do not invent objections
merely to participate.

## Review contract

Review against the agreed task and acceptance criteria.

A reviewer should not invent new requirements during review. A new improvement
idea becomes a future task unless it reveals a real correctness, safety,
security, scope, or acceptance-criteria failure.

For requested changes, state:

```text
Failed criterion: <criterion>
Evidence: <observable proof>
Required correction: <what must change>
Do not change: <unaffected work that should remain intact>
```

## Tool descriptions should also be agent-grade

A tool exposed to an agent should explain its operational boundary, not only
its function signature.

Recommended shape:

```text
Tool: maps.claim_task

USE WHEN:
Claiming a READY task that has no valid owner.

DO NOT USE WHEN:
Another valid owner already holds the task.

INPUT:
task_id, agent_id

RESULT:
claim accepted or rejected

SIDE EFFECT:
Changes canonical task ownership.

FAILURE / ESCALATION:
If state is ambiguous or stale, do not force ownership; reconcile state first.
```

This is especially important for tools that mutate task state, files, external
systems, permissions, or irreversible resources.

## Detail without micromanagement

Clear instructions do not require prescribing every implementation choice.
For a capable worker, specify the result, constraints, evidence, and decision
boundary; allow bounded implementation judgment inside that envelope.

Increase procedural detail when:

- the worker is less capable or less reliable for the task;
- the tool boundary is dangerous;
- the workflow is brittle or order-dependent;
- prior runs repeatedly fail in the same way; or
- verification cannot cheaply catch a mistake afterward.

Do not add instructions merely because a failure is imaginable. Add or tighten
rules when evidence shows ambiguity, context, tooling, routing, or safety needs
improvement.

## Sources and design basis

Vendor guidance changes over time. These were checked on 2026-08-14:

- OpenAI, Codex and repository harness guidance:
  - https://openai.com/business/guides-and-resources/how-openai-uses-codex/
  - https://openai.com/index/harness-engineering/
  - https://openai.com/index/introducing-codex/
- Anthropic, Claude Code best practices and agent loop:
  - https://code.claude.com/docs/en/best-practices
  - https://code.claude.com/docs/en/how-claude-code-works

The MAPS rule is provider-neutral: **clear outcome, relevant context, bounded
authority, observable proof, defined failure behavior, durable continuation.**
