# Roadmap Trajectory Check: Are We Still On Track

[PROGRAM_STEERING.md](PROGRAM_STEERING.md) answers "is this one candidate task
the right work" before shaping it. This file answers a different, larger
question that per-task steering does not cover: **stepping back across a
multi-task work arc, is the roadmap itself still pointing the right
direction, or has evidence accumulated that the plan should change.**

A session can pass every per-task PROGRAM_STEERING check and still drift at
the arc level — each individual task traces cleanly back to the checklist,
yet nobody has stopped to ask whether the checklist's own priority ordering,
scope boundaries, or blocked items still make sense given what was actually
learned while doing the work.

## 1. When to run this check

Run it at natural arc boundaries, not after every single task:

- After a meaningful batch of merged PRs (roughly every 3-6, or whenever the
  session notices the easily-startable backlog has thinned).
- Whenever a task's own findings surface something the roadmap didn't
  anticipate — a root cause that explains several stalled phases at once, an
  experiment result that contradicts an assumption, a discovered blocker.
- Before picking the next self-selected task once `work/roadmaps/
  CAPABILITY_CHECKLIST.md`'s remaining `NOT STARTED` rows are all
  `TRIGGERED`/conditional or depend on unmerged prerequisites — that state is
  itself a signal worth naming, not silently working around.

## 2. The check

1. **Re-verify, don't re-read.** Spot-check a sample of `CAPABILITY_CHECKLIST.md`
   rows (favor ones marked `DONE` and any marked `IN PROGRESS` for a while)
   against actual current `main` — merged PRs, `git log`, running tests —
   the same way the checklist itself was originally built. A stale label is
   not evidence the underlying work state matches it.
2. **Name what changed the picture.** List anything learned this arc that the
   checklist didn't already say: a phase turning out to depend on something
   bigger than scoped (e.g. discovering zero production callers of a whole
   subsystem), an experiment's real numbers, a design note's conclusion, a
   repeated friction pattern. Evidence like this is exactly what should
   update the plan — plans are allowed to change when reality disagrees with
   the roadmap's original assumptions.
3. **Ask directly: pivot or continue?** For each named change, decide out
   loud (in the trajectory note, see §3) whether it means: continue as
   planned (the finding doesn't change priority), reprioritize (something
   else is now more valuable to do next), or open a new roadmap item (the
   finding revealed real unscoped work the checklist doesn't cover at all).
   Decide this the same way any other design question gets decided —
   reason it through using the roadmap's own stated priorities (`P1`/`P2`/`TRIGGERED`/
   `EVIDENCE-GATED` tags in `00-MASTER-MAPS-CAPABILITY-ROADMAP.md`) and this
   arc's actual evidence, then act. Get a second agent's opinion first if
   genuinely torn between two directions; don't default to leaving it open.
4. **Check the Tenth Seat triggers.** Before treating a trajectory result or a
   consequential status claim as settled, evaluate the two narrow triggers in
   [TENTH_SEAT_REVIEW.md](TENTH_SEAT_REVIEW.md). If one fires, dispatch the
   bounded fresh-agent challenge and preserve its minority report. The minority
   report is evidence, not a veto or a second source of roadmap truth.
5. **Write it down.** Record the outcome as a short trajectory note under
   `work/notes/` (e.g. `work/notes/<date>-roadmap-trajectory-check.md`):
   what was re-verified, what changed the picture, what the Tenth-Seat check
   concluded if relevant, and what was decided. This is evidence for the *next*
   trajectory check, not a new authority surface — it does not itself grant or
   change task/policy authority, and it is not a second source of roadmap truth
   (`CAPABILITY_CHECKLIST.md` remains that). If a pivot changes what the
   checklist should say, update the checklist itself in the same or a following
   docs PR.

## 3. What this is not

- Not a replacement for `CAPABILITY_CHECKLIST.md` — that file stays the one
  place cross-roadmap status lives. This check *maintains* trust in that
  file; it does not duplicate it.
- Not a new mutable task/authority store. A trajectory note is a durable
  human-readable record like a repair note or design note, not a database.
- Not permission to abandon `PROGRAM_STEERING.md`'s per-task check — the two
  operate at different altitudes and both apply.
- Not a reason to pause and wait for approval before continuing. A named
  pivot is acted on, not merely proposed — see `docs/CHECKS_AND_BALANCES.md`
  for what remains a genuine hard-wall escalation versus a decision this
  check is meant to resolve on its own.
- Not a blanket adversarial-review step. Tenth-Seat review remains rare and
  trigger-based; ordinary independent review already covers routine PRs.

## 4. Relationship to the other steering docs

```text
AGI_STANDARD.md              → is this one task clear enough to execute?
PROGRAM_STEERING.md          → is this the right task, right now?
ROADMAP_TRAJECTORY_CHECK.md  → is the roadmap itself still pointing right,
                                given everything learned so far?
TENTH_SEAT_REVIEW.md         → when consensus is unusually clean, did anyone
                                construct the strongest credible case against it?
```
