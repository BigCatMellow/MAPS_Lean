# Emergence may target established mechanisms for redesign / supersession

Design note for the "Change 2" half of the former PR #302. Change 1 (the bounded
cross-root synthesis pass) ships separately on branch
`emergence/cross-root-synthesis-c1only` and carries no authority change. This
note is the companion justification the original PR was missing, per
`playbook/INDEX.md` §"Adding or changing a method". Operator approved splitting
this change out and requiring this doc (relayed 2026-09-07).

## What changes

`playbook/EMERGENCE.md` gains explicit permission for the emergence lifecycle to
*question, compare, redesign, or propose replacement of* an established MAPS_L
mechanism — including the emergence lifecycle itself — rather than only
generating ideas that sit inside the current process:

- Top-of-doc clause: the lifecycle is the "current operating method, not a
  design ceiling"; being established is not itself evidence a mechanism should
  remain; current authority still governs execution until deliberately changed.
- Phase 1 (Imagine): a new question — "which established mechanism survives
  mainly because it is already established, and what alternative would
  outperform it?" — and the trajectory-check cadence is named as itself open to
  a better triggering/search mechanism.
- Phase 1 cross-root synthesis: "established mechanisms/processes" added as a
  comparison root; two asks about whether another root exposes a better
  mechanism or suggests changing the emergence/search/evaluation process; a
  "current baseline when an established mechanism is challenged" line in the
  Capture bar; incumbency named as insufficient grounds for Capture on its own;
  a paragraph that an apparent improvement is compared *against* the incumbent,
  which may still win, with no automatic preference for novelty.
- Phase 2 (Capture): a candidate may explicitly target an existing MAPS_L
  process for adaptation or supersession; current process gets no immunity from
  evaluation.
- Phase 3 (Promote): promotion may authorize work whose purpose is to replace or
  supersede an existing mechanism, preserving lineage and the reason;
  "only a promoted item may expand implementation scope" is softened to
  "...under the current operating model".
- Closing Rule line: adds "challenge precedent" and "supersede when earned".

## What does NOT change

- **No execution authority is added.** Redesigning or replacing a mechanism is
  still real work: it requires a captured record and a deliberate **Promote**
  into a `work/tasks/` contract, `work/decisions/DEC-NNN`, or a roadmap line.
  Emergence still *recommends dispositions, it does not authorize work*.
- **Current authority still governs until deliberately changed.** An in-flight
  task cannot be hijacked to rewrite a mechanism; the standing mechanism remains
  in force until a Promote (and, where consequential, an operator decision under
  `AGENTS.md`) changes it.
- **No new machinery, no daemon, no automated step.** The cadence is still the
  trajectory check.
- **Consequential changes still route through `DECISIONS_AND_SAFETY.md` /
  `AGENTS.md` scope-level authorization.** Replacing a load-bearing mechanism is
  a consequential decision; this change lets emergence *propose* it, not
  *ratify* it.

## `playbook/INDEX.md` §"Adding or changing a method" — 5-point check

This is a change to an existing method, not a new file, so the anti-sprawl test
is applied to the *scope expansion*:

1. **Existing concept owner.** `EMERGENCE.md` already owns "elicit, capture, and
   route improvement ideas". Proposing that an improvement idea targets a
   standing mechanism is the same job pointed at a target it previously excluded
   by omission — it is not a new concept. `DECISIONS_AND_SAFETY.md` owns
   *deciding* a consequential change and `REPAIR_AND_LEARNING.md` owns
   *drift/incident-driven* countermeasures; neither owns *deliberate generative
   questioning of a mechanism that is working as designed*, which is what this
   is. `ROADMAP_TRAJECTORY_CHECK.md` owns route correction, not mechanism
   redesign. So no other owner can coherently take it.
2. **One distinct reusable job.** Unchanged: generate → capture → route
   improvement ideas. The change widens the candidate space, not the number of
   jobs.
3. **Link, not copy.** The note and the doc link to `AGENTS.md` /
   `DECISIONS_AND_SAFETY.md` for execution authority rather than restating
   decision procedure; the "current authority governs until deliberately
   changed" clause defers to those sources rather than duplicating them.
4. **One index entry stating non-overlap.** The `EMERGENCE.md` row in
   `playbook/INDEX.md` is updated to state that emergence may propose mechanism
   supersession but still only recommends — decision/authorization stays with
   `DECISIONS_AND_SAFETY.md` / `AGENTS.md`, drift-driven repair stays with
   `REPAIR_AND_LEARNING.md`.
5. **Merge/retire what it supersedes.** Nothing is retired. The prior implicit
   reading — that emergence ideas live *inside* the current process and cannot
   question it — was never written as a rule; this change makes the boundary
   explicit in the same edit. The closing Rule line is superseded in place
   (old: "imagine widely, file cheaply, promote deliberately, sweep every arc";
   new adds "challenge precedent" / "supersede when earned").

## Risk / reversibility

- **Downside:** the "design ceiling" framing could be read as license to
  relitigate settled mechanisms mid-task. Mitigation: the "current authority
  governs execution until deliberately changed" clause and the unchanged
  Promote gate; a candidate that skips Capture/Promote is out of process.
- **Reversibility:** fully reversible by reverting the doc hunks; no code, no
  data, no state migration.

## Stacking

The EMERGENCE.md hunks in this PR sit on top of the Change-1 cross-root
synthesis section. This PR is stacked on the Change-1 PR (#302 head, branch
`emergence/cross-root-synthesis-c1only`). Land Change 1 first, then rebase this
PR onto main so its diff reduces to the Change-2 hunks only.
