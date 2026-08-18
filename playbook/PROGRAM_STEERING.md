# Program Steering: Is This the Right Task at All

[AGI_STANDARD.md](AGI_STANDARD.md) answers "is this one task clear enough to
execute." This file answers a different question that AGI readiness does not
cover: **is this the task the program actually needs right now**, or is a
session about to spend a clear, well-specified contract on the wrong work.

A task can pass every AGI test and still be program-level drift: real effort
spent on low-value busywork while genuine unstarted capability work sits
untouched. AGI_STANDARD cannot catch this — it only inspects the instruction
in front of the worker, not what else exists in the program.

## 1. When to run the check

A session MUST run the check in this file before starting any **self-selected**
work — work that is not explicitly directed by the operator and is not an
already-scoped, open task doc it has been assigned or has claimed.

The check MUST run, at minimum, immediately after `gh issue list --state
open` (or an equivalent query of the tracker) returns empty and the session
is about to decide what to do next. An empty issue queue is the single most
common moment a session picks up filler work instead of consulting the actual
roadmap.

The check MAY be skipped when the work is explicitly operator-directed, or
when it is execution of an already-`READY` task doc shaped and assigned
through [TASK_LIFECYCLE.md](TASK_LIFECYCLE.md) — those cases already carry
traced authority and do not need re-deriving.

## 2. The check

Before writing a task doc for self-selected work, a session MUST answer:

1. **Does this trace back?** Does the candidate task correspond to an entry
   marked `NOT STARTED` or `IN PROGRESS` in
   `work/roadmaps/CAPABILITY_CHECKLIST.md` (the consolidated capability
   status tracker), or to an explicit operator request?
   - If neither, that is a flag, not an automatic stop. The gap MUST be
     named explicitly in the new task doc's own inputs/reasoning section
     (for example, under `Inputs and source of truth`) — never silently
     assumed reasonable and left unstated.
2. **Is this "document what already works"?** Is the task closing an
   issue/ticket primarily by describing or documenting behavior that is
   already shipped, rather than building something new?
   - This is sometimes legitimate — a genuine documentation gap is real
     work. It MUST be named as exactly that ("this closes the issue via a
     documentation fix for already-shipped behavior, not new capability
     work") in the task doc, not disguised as capability progress.
3. **Is the checklist itself trustworthy right now?** Has
   `work/roadmaps/CAPABILITY_CHECKLIST.md` been cross-checked against real
   merged state recently — within the current multi-session work arc — or is
   it plausibly stale?
   - If plausibly stale, the session MUST re-verify the specific item it is
     about to pick up against actual code/tests before trusting the
     checklist's status label. A stale `NOT STARTED` label is not
     verification that the work is actually unstarted.

A session MAY proceed once these three questions are answered and, where a
flag was raised, the flag is written into the task doc rather than resolved
by silent assumption.

## 3. Drift smell list

These are recognizable patterns of program-level drift — a session doing
technically-clean work that is nonetheless the wrong work. Any of these
appearing MUST trigger re-reading this file before continuing:

- **Easiest over most valuable.** Picking the smaller, simpler, or more
  comfortable available task when a more valuable one is also available and
  traceable.
- **Empty queue treated as empty backlog.** Reading "0 open GitHub issues" as
  "nothing to do" instead of consulting
  `work/roadmaps/CAPABILITY_CHECKLIST.md` for unstarted or in-progress
  capability work.
- **Documentation instead of implementation.** Writing docs about behavior
  that already works instead of building behavior that does not exist yet,
  when the latter is what the program actually needs.
- **Re-deriving "what's next" from scratch.** Reasoning about program
  priority each session as if no roadmap existed, instead of consulting the
  existing checklist.
- **Scope creep.** A task quietly growing beyond its own task doc's `Change
  boundary` — touching files, decisions, or outcomes the task record never
  named.

## 4. When drift is caught

Whether drift is caught by the session itself or by the operator, the
response is corrective, not punitive:

1. Name the drift plainly, in the current handoff or task doc — state which
   smell from §3 applies and what was actually happening.
2. Redirect to the item the work should have traced back to under §2, or
   obtain an explicit operator decision if no traceable item exists.
3. If the same drift pattern seems likely to recur (not a one-off slip),
   consider whether it rises to Drift or worse under
   [REPAIR_AND_LEARNING.md](REPAIR_AND_LEARNING.md)'s severity table, and
   file a repair record there if so. This file does not define its own
   severity tiers or repair-note format — use REPAIR_AND_LEARNING.md's.

## 5. Relationship to AGI_STANDARD.md

[AGI_STANDARD.md](AGI_STANDARD.md) and this file are complementary gates, not
substitutes for each other:

```text
PROGRAM_STEERING.md → is this the right task at all?
AGI_STANDARD.md      → is this one task clear enough to execute?
```

A task can be AGI READY and still be program-level drift (clear instructions
for the wrong work). A task can trace correctly to real roadmap need and
still fail AGI readiness (right work, badly specified). Self-selected work
SHOULD pass the check in this file before being shaped into an AGI-ready task
doc, not after.
