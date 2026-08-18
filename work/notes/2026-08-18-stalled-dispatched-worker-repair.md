# Repair Record: dispatched background worker did not self-resume after its own task completed

- Severity: `DRIFT`
- Owner: operator-directed session, 2026-08-18
- Trigger and evidence: a dispatched background implementer agent (Recovery Stage 2 `run_id` wiring, `work/tasks/recovery-stage2-run-id-wiring.md`) reported mid-task that it was "waiting for the full background test suite to finish before committing, pushing, and opening the PR." Recorded/assumed state was "it will resume automatically when its own background monitor completes." Verified reality, checked ~7 hours later against live GitHub (no PR existed for that branch): the underlying test suite had actually finished in the normal ~7-11 minute window, but the agent's turn was never resumed — the completion signal did not reliably wake it. The same pattern then recurred on a second, unrelated dispatched agent (SENTINEL review of PR #94) within the same session.

## Finding

Dispatching a background worker and then passively waiting for its own internal completion signal to resume it is not reliable. There was no mechanism actually verifying "is the worker still making progress" versus "is the worker silently idle" — the only signal trusted was the worker's own last self-report, which is exactly the kind of unverified internal-state assumption this repo's durable-vs-live model already warns against for GitHub facts, just not previously applied to dispatched-worker liveness itself.

## Change made

Added a "Stalled-work triage" section to `work/coordination/README.md` (PR #95, merged): if a dispatched worker hasn't reported back and elapsed time is far beyond what the task should plausibly take, check live GitHub evidence directly (PR/commit/comment) rather than keep waiting, proactively resume/re-contact the worker if nothing appropriate exists, and record the incident (not just the fix).

**Process gap in how that change was made, noted here for its own prevention value**: the durable countermeasure was added directly to the coordination README without first going through this repair-record step, even though `playbook/REPAIR_AND_LEARNING.md` already prescribes exactly that path for Drift-or-worse findings ("write a repair note ... use the repair-record template ... then, if a failure repeats, add a durable countermeasure"). This file is that missing step, filed after the fact. The countermeasure itself (PR #95) is not being redone — it was directionally correct and is already live — but the paper trail is being completed now instead of left implicit.

## Verification and rollback

- Verification: re-triggered by manually checking `gh pr view <n> --json comments,mergedAt` / `gh pr list` against a dispatched worker's expected output whenever elapsed time exceeds the task's plausible duration, per the new README section. No automated verification exists yet (see Prevention).
- Rollback: revert the `work/coordination/README.md` section added in PR #95 if it turns out to conflict with a better mechanism later; low risk, docs-only.

## Prevention

The `work/coordination/README.md` addition (PR #95) is the durable countermeasure for the *triage response*. Two follow-on gaps this record deliberately does not resolve, flagged for a future task if they recur enough to justify one:

1. No mechanical timeout/heartbeat exists for dispatched background workers — the triage rule is a manual habit, not an enforced check. A future task could add a lightweight "expected duration" convention to task briefs so a check can be scripted rather than judgment-based.
2. This incident and its fix should also have gone through `playbook/EMERGENCE.md`'s explicit capture shape (observe -> connect -> synthesize -> name -> promote) as a reusable insight, not just a repair — a dispatched worker's own background-task completion not reliably resuming it is a pattern likely to recur beyond this one coordination-protocol context (e.g. any future automation that dispatches and waits on external work). Captured here rather than as a separate `insights/` artifact, since `work/` has no existing `insights/`/`ideas/` folder in use yet and creating one for a single entry would be premature per `EMERGENCE.md`'s own "promote deliberately" rule.

## Naming-taxonomy note (unrelated finding, recorded for completeness, not acted on)

While investigating this repair, a related documentation gap surfaced: `Authority-1`, `Storage-0`, `Conflict-0`, `Injection-0`/`Injection-1`, and `Lifecycle-1` (coined in `work/notes/2026-08-17-operational-learning-authority-design.md`) are ad hoc labels with no tie back to `work/roadmaps/05-learning-and-evaluation.md`'s own documented phase list, where this work is actually **L5** ("Operational-learning lifecycle"). Not fixed retroactively here (low value relative to churn); worth using the sub-roadmap's own prefix (e.g. `L5a`/`L5b`/`L5c`) rather than inventing a new ad hoc scheme the next time this area is touched.
