# Task Lifecycle: Shape, Own, Verify, Close

Every consequential task should be executable by a future agent with no access
to the original chat.

## Shape before claiming

Use a shaper (the owner or a separate planning agent) when intent is vague,
output paths are unknown, criteria are missing, dependencies are unclear, or a
task exists only in chat. Do not start implementation merely to discover what
the task should have said.

The task record must state:

- an action-oriented title and concise observable outcome;
- type: implementation, review, architecture, planning, research, maintenance,
  or repair;
- one accountable owner and risk tier;
- relevant inputs and authoritative sources;
- dependencies and preconditions;
- every allowed output path and explicit non-goals/boundaries;
- the owner's bounded decision authority and escalation boundary;
- observable, pass/fail acceptance criteria;
- verification and evidence expected;
- review required for that risk tier; and
- stop/escalation conditions for material unknowns or changed assumptions.

If these cannot be written without guessing, record the missing decision and
shape, research, or escalate before execution. Split work when ownership or
output paths overlap.

For the formal readiness requirements, use
[AGI_STANDARD.md](AGI_STANDARD.md). Use
[the AGI check template](../templates/agi-check.md) when a durable validation
record is useful.

## AGI gate

A consequential task may enter `READY` only when it is `AGI READY` under the
MAPS Agent-Grade Instructions standard.

`READY` therefore means:

- the execution contract is sufficiently specified;
- a suitable fresh agent can act without the original chat;
- consequential intent, scope, permission, and success do not require guessing;
- verification and review are defined; and
- applicable failure/continuation behavior is defined.

AGI readiness is pass/fail, not a percentage score. One missing material
requirement keeps the task in `NEEDS_SHAPING`, `BLOCKED`, or the appropriate
research/operator-decision state.

Worker suitability is a separate gate. After AGI passes, use
[HPOM routing](HPOM_ROUTING.md) and
[model capability routing](MODEL_CAPABILITY_ROUTING.md) to select a worker that
can reliably execute the contract.

## Ownership rules

Output paths are a write boundary, not a retrospective report. Register every
file that will be edited—including a small backlink or one-line configuration
change—before touching it. If new files become necessary, amend the task or
handoff the addition before editing.

Only one active owner edits a given output path. Parallel agents may research,
review, or prepare non-overlapping artifacts; name one integration owner.

## Execution integrity for consequential runs

Use [EXECUTION_INTEGRITY.md](EXECUTION_INTEGRITY.md) when drift, recovery,
reviewer independence, or exact context/scope matters.

- Select context deliberately: required, optional-with-trigger, and excluded
  material when the distinction is material. Use the
  [context-packet template](../templates/context-packet.md) only when this is
  clearer than keeping the fields in the task.
- For long, high-risk, resumable, or heavily parallel work, freeze a run
  binding when task/context/repository drift would otherwise be hard to
  diagnose. A run binding freezes the approved contract; it does not grant
  new authority.
- State-changing APIs should return explicit failure reasons rather than one
  ambiguous Boolean when the caller needs different recovery behavior.

## State model

```text
NEEDS_SHAPING --AGI PASS--> READY --> ACTIVE --> READY_FOR_REVIEW --> DONE
                                      |                    |
                                      v                    |
                                   BLOCKED                 |
                                      ^                    |
                                      |                    v
                                CHANGES_REQUESTED <--------
```

`READY` means `AGI READY`, not merely desirable or assigned.

`ACTIVE` means a suitable worker has legitimately claimed/received the task and
may act within its contract.

`READY_FOR_REVIEW` means implementation work is complete enough for the
specified review and required evidence is available.

`DONE` means the acceptance criteria, required verification, and proportional
review are complete. Do not report a task done because time ended or the first
implementation attempt looks plausible.

## Conflicts

When current authoritative sources materially disagree about scope, ownership,
lifecycle state, an approved decision, or a load-bearing fact:

1. stop only the affected work;
2. record the conflicting claims/sources and affected scope;
3. identify the authority or evidence that can resolve the conflict; and
4. resume only after the conflict is explicitly resolved.

Do not silently choose whichever source appears more plausible. A conflict
record reports the problem; it does not grant authority to resolve it.

## Review independence and evidence

When independent review is required, a different session name is not enough.
The reviewer must not be the submission author or a direct continuation of the
author for the reviewed work, such as a rotation successor that inherited the
same in-flight claims/context.

For higher-risk work, keep the implementer's criterion/evidence claim separate
from the reviewer's verdict. Review may confirm or reject the claim; it should
not rewrite the original claim as if the reviewer made it.

Functional review and security review answer different questions. Work that
creates or changes network-facing/write-capable surfaces, permissions, secret
handling, or other trust boundaries should receive a security-focused check
proportional to the risk.

## When the contract changes during execution

If execution discovers a material new requirement, output path, dependency,
authority question, safety issue, or failed assumption:

1. stop the affected work before crossing the existing boundary;
2. record the new fact as `VERIFIED`, `REPORTED`, `ASSUMED`, or `UNKNOWN` as
   appropriate;
3. amend/re-shape the task or create the required research/decision record;
4. re-run the applicable AGI readiness check; and
5. resume only when the task is again ready.

Do not preserve `READY` by silently widening the contract after work starts.

## Special acceptance checks

- For visual work, freeze the approved reference, compare a screenshot of the
  real build at the target viewport, and name the integration/rollout path.
- For a design port, inspect live data/API fields before inventing new ones.
- For user-acquired releases, walk the full acquisition/install/launch path,
  not only the development entrypoint.
