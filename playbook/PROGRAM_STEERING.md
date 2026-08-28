# Program Steering: Is This the Right Task at All

[AGI_STANDARD.md](AGI_STANDARD.md) asks whether one task is clear enough to
execute. This file asks whether it is the right work now.

A task can be AGI-ready and still be low-value drift.

## 1. When to run the check

Run this check before self-selected work that is not already an assigned/scoped
approved-roadmap task.

Run it especially when the issue/task queue is empty. An empty queue does not
mean the roadmap is done.

Skip the check for explicitly directed work or an already-`READY` task with
traceable approved-roadmap authority.

## 2. Select the next task autonomously

Before creating self-selected work, answer:

1. **Does it trace back?** Prefer a `NOT STARTED`/`IN PROGRESS` item in
   [`work/roadmaps/CAPABILITY_CHECKLIST.md`](../work/roadmaps/CAPABILITY_CHECKLIST.md),
   another approved roadmap item, or an explicit human request.
2. **Is this documentation for behavior that already exists?** If yes, name it
   honestly as documentation work rather than capability progress.
3. **Is the roadmap/checklist trustworthy?** If plausibly stale, verify the
   candidate item against real code/tests before acting.
4. **What is the highest-value eligible item?** Choose based on dependencies,
   roadmap priority, unblock value, risk reduction, and progress toward DONE —
   not merely what is easiest.

If a traceable eligible item exists inside approved authority, the orchestration
operator selects it, shapes it, and continues. **Do not ask the human what to do
next merely because the queue is empty.**

If no traceable item exists, first determine whether useful work can be derived
without expanding the approved objective: reconciliation, verification, fixing a
known blocker, completing an incomplete criterion, or correcting stale roadmap
state. If yes, shape that bounded work and continue.

Human reauthorization is required only when the proposed next work would create
a materially new objective/scope outside the approved roadmap.

## 3. Drift smells

- **Easiest over most valuable.** Comfortable work over higher-value eligible
  roadmap work.
- **Empty queue = empty backlog.** Ignoring roadmap/checklist because tracker has
  zero open issues.
- **Documentation instead of implementation.** Describing shipped behavior while
  required capability remains unbuilt.
- **Re-deriving what's next from scratch.** Ignoring existing roadmap priority.
- **Scope creep.** Work no longer traces to the approved objective/envelope.
- **Human dependency by habit.** Asking the human to pick/approve the next
  already-authorized task instead of steering the program.

## 4. When drift is caught

1. Name the drift briefly in the task/handoff when it matters to continuation.
2. Redirect to the highest-value traceable approved-roadmap item.
3. If no traceable in-envelope work exists, distinguish `roadmap complete` from
   `new scope needed`.
4. Only `new scope needed` requires a human scope decision.
5. Repeated drift may warrant a repair record under
   [REPAIR_AND_LEARNING.md](REPAIR_AND_LEARNING.md).

## 5. Relationship to AGI

```text
PROGRAM_STEERING.md → is this the right task now?
AGI_STANDARD.md      → is this task clear enough to execute?
```

Both are orchestration gates. Neither is a routine human approval gate.

## Core rule

**When approved roadmap work exists, select and execute the next useful item.
Do not idle and do not ask permission to continue.**
