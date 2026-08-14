# Agent Operating Contract

This is the active instruction set for this repository. Keep the work simple,
durable, and proportional to its risk.

## Authority and ownership

1. The operator owns intent, priority, scope, and approval of consequential or
   irreversible actions.
2. Each task has one accountable owner. Do not concurrently edit another
   active task's declared output paths.
3. A reviewer is independent of the owner for any review that is required.
   An owner never approves their own substantive work.
4. A tool, terminal, agent window, tracker, or message channel does not grant
   authority merely by being open or storing state.

## Before changing files

For a task involving multiple agents, a risky change, or work likely to outlive
this session, create `work/tasks/<short-name>.md` from [the task template](templates/task.md).
State the goal, owner, inputs/source of truth, output boundary, decision
authority, risk tier, pass/fail acceptance criteria, verification, required
review, and stop/escalation conditions.

A consequential task must be `AGI READY` under the
[formal Agent-Grade Instructions standard](playbook/AGI_STANDARD.md) before it
enters `READY` or begins execution. A capable model's ability to infer missing
intent does not make weak instructions ready.

For a small local edit, keep the necessary contract in the prompt or PR rather
than creating ceremony.

Read the task and only its relevant inputs before editing. Ask the operator
when a decision would materially change scope, cost, risk, security, privacy,
external behavior, or user-visible behavior.

## During work

- Prefer the smallest change that satisfies the acceptance criteria.
- Keep decisions in `work/decisions/` when another agent or later session needs
  them.
- Use native agent spawning when parallel work has clear, non-overlapping
  outputs. Do not spawn agents just to create process activity.
- When another session must continue the work, write a compact handoff using
  [the handoff template](templates/handoff.md) and update [current state](state/CURRENT.md).
- If execution reveals a material new dependency, output path, authority
  question, safety issue, or failed assumption, stop the affected work and
  re-shape/re-check the task rather than silently widening it.
- Never perform destructive actions without explicit operator approval.

## Verification and review

Follow [Checks and Balances](docs/CHECKS_AND_BALANCES.md). Match proof to risk:

- **Low:** owner verifies the stated result; batch routine documentation or
  mechanical changes when sensible.
- **Medium:** run relevant tests or reproduction steps and obtain independent
  review before calling the work complete.
- **High:** use explicit acceptance criteria, independent review with
  reproduced evidence, and an operator-visible release note/checklist.

Review findings must name the affected path, the observable issue, its risk,
and the required correction. Do not block work on vague preferences or invent
new requirements during review.

## Reusable methods

For work beyond a small edit, use the [playbook index](playbook/INDEX.md) to select the method.
The active playbook preserves the useful MAP practices—AGI readiness,
HPOM-style routing, research and risk discipline, project bootstrapping,
roadmap/checklist design, and emergence capture. The retained control plane is
SQLite task state, LangGraph routing, RnS recovery, and hcom
messaging/session control. WezTerm and the fixed startup roster are optional
presentation choices, not authority or workflow prerequisites.

## Completion

Stop when the acceptance criteria are satisfied and the required verification
and review are complete. Report changed paths and the verification performed.
Preserve only forward-relevant state; do not use long chat transcripts as
project memory.
