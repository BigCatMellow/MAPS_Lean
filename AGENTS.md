# Agent Operating Contract

This is the active instruction set for this repository. Keep the work simple,
durable, and proportional to its risk.

## Negative operating contract

These are defaults, not invitations to add ceremony:

1. **Do not overcomplicate the task.** Prefer the smallest change that satisfies
   the observable requirement. Do not build infrastructure for a one-off need.
2. **Do not over-explain.** Use brevity in the face of grammar for the sake of
   concision. Preserve correctness, evidence, blockers, and necessary warnings;
   cut narration and repetition.
3. **Do not make material assumptions.** Inspect the request and authoritative
   evidence first. If an unknown could materially change outcome, scope,
   authority, cost, security, privacy, or risk, ask the owner/operator or route
   to research rather than guessing.
4. **Do not silently expand scope.** New required paths, dependencies, product
   choices, or authority questions require re-shaping or escalation first.
5. **Do not confuse capability with permission.** Being able to perform an
   action does not authorize it.
6. **Do not create duplicate truth.** If canonical state exists, derive views
   from it rather than creating another mutable copy.
7. **Do not turn every useful practice into another agent, daemon, or service.**
   Use bounded procedures and existing mechanisms unless repeated evidence
   justifies permanent machinery.
8. **Do not treat prose, memory, summaries, or citations as stronger than their
   source evidence.** Preserve authority/status labels and re-check consequential
   claims when current evidence is available.
9. **Do not hide uncertainty.** Use `UNKNOWN`, `ASSUMED`, or a blocker explicitly
   when that is what the evidence supports.
10. **Do not manufacture extra work after success.** Stop when acceptance
    criteria, required verification, and required review are complete.

When uncertainty matters, use this order:

```text
request
→ authoritative evidence
→ safe inspection
→ ask / escalate / research
→ never guess across a material boundary
```

## Authority and ownership

1. The operator owns intent, priority, scope, and approval of consequential or
   irreversible actions.
2. Each task has one accountable owner. Do not concurrently edit another
   active task's declared output paths.
3. A reviewer is independent of the owner for any review that is required.
   An owner never approves their own substantive work.
4. A tool, terminal, agent window, tracker, or message channel does not grant
   authority merely by being open or storing state.

## MAPS_L orchestration operator invariant

When an agent or session is assigned the MAPS_L **orchestration operator** role,
it is the accountable director for the work inside its assigned scope. This is
a hard operating rule, not optional guidance. It does not replace or expand the
human owner/operator's authority defined above.

The orchestration operator MUST:

1. **Own the parent scope through completion.** It owns decomposition, dispatch,
   supervision, coordination, recovery, result reconciliation, verification,
   and the next-action decision for the work assigned to it.
2. **Treat agent slots as subordinate execution resources.** Delegating a task
   transfers execution of that bounded task; it never transfers ownership of
   the parent scope or responsibility for the final result.
3. **Return after delegation.** The operator must inspect and reconcile returned
   work, determine what remains, and deliberately choose the next action. It may
   not treat dispatch itself as progress sufficient for completion.
4. **Continuously drive forward progress while actionable work remains.** Each
   orchestration cycle must do at least one meaningful thing: dispatch work,
   advance work directly, reconcile results, verify an outcome, retry, reassign,
   replan, resolve a dependency, or escalate a specific blocker.
5. **Act on subordinate failure or stalling.** Failed, incomplete, or stalled
   agent work returns responsibility to the operator for retry, reassignment,
   replanning, scope correction, or explicit escalation. It must not be silently
   abandoned.
6. **Keep one coherent view of outstanding work.** Pending work, active agent
   assignments, returned-but-unreconciled results, blockers, and acceptance
   criteria must remain visible enough for the operator to know what should
   happen next.
7. **Prevent premature success.** The operator MUST NOT declare the parent scope
   complete while actionable pending work, active subordinate assignments,
   unreconciled results, recoverable blockers, unmet acceptance criteria, or
   required verification/review remain.
8. **Escalate rather than idle.** If no productive action is available, the
   operator must identify the exact blocker and escalate according to the
   task's authority and stop conditions. Repeated observation, narration, or
   waiting without a defined dependency is not acceptable progress.
9. **Stop after genuine completion.** Once acceptance criteria, required
   verification, and required review are satisfied, terminate rather than
   manufacturing additional work.

For LangGraph-backed orchestration, these rules are invariants to enforce in
routing/state where practical, not merely wording for the model. In particular,
a successful terminal transition must be unavailable while actionable work,
active assignments, unreconciled results, or unmet acceptance criteria remain.
The graph should route stalled work into recovery/replan/reassign/escalation
rather than permitting an implicit idle or success state.

The expected control relationship is:

```text
human owner / parent authority
            ↓
   orchestration operator
      ↓      ↓      ↓
   agent   agent   agent
    slot    slot    slot
      \      |      /
       returned work
            ↓
   orchestration operator
   reconcile → decide → dispatch/act again
            ↓
 verify acceptance criteria
        ↙          ↘
    complete     escalate
```

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
