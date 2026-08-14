# Task Lifecycle: Shape, Own, Verify, Close

Every consequential task should be executable by a future agent with no access
to the original chat.

## Shape before claiming

Use a shaper (the owner or a separate planning agent) when intent is vague,
output paths are unknown, criteria are missing, dependencies are unclear, or a
task exists only in chat. Do not start implementation merely to discover what
the task should have said.

The task record must state:

- an action-oriented title and concise outcome;
- type: implementation, review, architecture, planning, research, maintenance,
  or repair;
- one accountable owner and risk tier;
- relevant inputs and every allowed output path;
- dependencies and boundaries/non-goals;
- observable, pass/fail acceptance criteria; and
- verification and review required for that risk tier.

If these cannot be written without guessing, record the missing decision and
ask for it. Split work when ownership or output paths overlap.

## Ownership rules

Output paths are a write boundary, not a retrospective report. Register every
file that will be edited—including a small backlink or one-line configuration
change—before touching it. If new files become necessary, amend the task or
handoff the addition before editing.

Only one active owner edits a given output path. Parallel agents may research,
review, or prepare non-overlapping artifacts; name one integration owner.

## State model

```text
NEEDS_SHAPING → READY → ACTIVE → READY_FOR_REVIEW → DONE
                       ↘ BLOCKED
                 ↖ CHANGES_REQUESTED
```

`READY` means the task is sufficiently specified, not merely desirable.
`DONE` means the required evidence and proportional review are complete. Do
not report a task done because time ended or the first implementation attempt
looks plausible.

## Special acceptance checks

- For visual work, freeze the approved reference, compare a screenshot of the
  real build at the target viewport, and name the integration/rollout path.
- For a design port, inspect live data/API fields before inventing new ones.
- For user-acquired releases, walk the full acquisition/install/launch path,
  not only the development entrypoint.

