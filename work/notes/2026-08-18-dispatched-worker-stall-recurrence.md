# Repair Record: dispatched-worker background-test stall recurred despite the existing fix

- Severity: `DRIFT`
- Owner: operator-directed session, 2026-08-18
- Trigger and evidence: `work/notes/2026-08-18-stalled-dispatched-worker-repair.md` (this same day, earlier) already
  records this exact pattern -- a dispatched agent backgrounds its own test suite and never self-resumes -- and
  its countermeasure (a "Stalled-work triage" section added to `work/coordination/README.md`, PR #95, merged)
  prescribes checking live GitHub evidence and proactively resuming/re-contacting the worker when elapsed time
  exceeds the plausible task duration. Later the same day, the S6 task (Context Builder Skill integration,
  `work/tasks/context-builder-skill-integration-s6.md`, landed as PR #109) stalled this way **three separate
  times in a row** on dispatch attempts for that task, per AGI-03 (`playbook/AGI_STANDARD.md`) labeled
  `REPORTED` — this session's own account of the dispatch attempts, not independently checkable against a
  git/GitHub artifact: a dispatched worker that stalls before committing anything leaves no commit, PR, or
  timestamp trail to verify against, so the count and sequence below rest on the coordinating session's
  contemporaneous observation, not on reproducible evidence:
  1. First attempt: stalled with no explicit instruction against backgrounding tests.
  2. Second attempt: stalled again *despite* an explicit prompt instruction telling the dispatched agent to run
     the test suite as a blocking foreground call rather than background it.
  3. Third attempt: stalled again with the same explicit instruction in place; this attempt used a Monitor-style
     wait (a background/poll construct) on its own test run anyway, reproducing the exact failure mode the
     instruction was meant to prevent.

  In each case the recorded/assumed (`ASSUMED`) state was "the dispatched agent will resume on its own once its
  test run completes." The eventual outcome — that the agent's turn did not resume and the coordinating session
  had to detect the stall and re-dispatch/re-prompt before PR #109 could progress — matches the pattern the PR
  #95 triage habit exists to catch, and is consistent with (though not independently provable from) PR #109's
  own commit history showing multiple distinct review-evidence/re-sync cycles spread across roughly 1h26m
  (`fe7e9b9` 22:36:53Z through `5445513` 23:44:39Z; see the companion record for the full breakdown). That
  commit history corroborates that PR #109's path to merge involved several distinct resumption points; it does
  not, by itself, prove the specific count or cause ("stalled," specifically, versus other friction) claimed for
  each of the three dispatch attempts above, which remains `REPORTED` rather than `VERIFIED`.

## Finding

The existing countermeasure (PR #95) works as a *detection and recovery* habit for the coordinating session --
and it did catch all three stalls here, which is why PR #109 eventually landed rather than silently hanging.
But the countermeasure does nothing to stop the stall from *happening* in the first place, and today's evidence
shows that adding an explicit prompt instruction ("run tests as a blocking foreground call") is not sufficient
either: the same dispatched-worker role (S6 implementer/reviewer instances) stalled on attempts 2 and 3 with
that instruction present, including one attempt that used a wait/monitor construct on its own tests in direct
contradiction of the instruction it had just been given.

This is not a new failure mode -- it is the prior repair record's own flagged residual gap actually
materializing. That record's "Prevention" section said, verbatim: "No mechanical timeout/heartbeat exists for
dispatched background workers -- the triage rule is a manual habit, not an enforced check." Today's three
recurrences on S6 are that exact gap showing up in practice: a prompt-level instruction is a *request*, not an
*enforced* check, and a dispatched agent under load can still choose (or drift into) backgrounding/waiting on
its own tests regardless of what its brief says.

## Change or proposal

No mechanical change is made in this record -- filing the record and naming the durable next step is the scope
of this PR, per `playbook/REPAIR_AND_LEARNING.md`'s instruction to repair mechanically when authorized or
propose/escalate otherwise. Because a fix here would change how dispatched-worker task briefs and the
coordinating session's own wait/check-in behavior work (i.e. it touches process/authority, not just a doc
correction), it is proposed as **STRUCTURAL**, not implemented in this PR:

**Proposal**: adopt a lightweight convention where every dispatched-worker task brief states an expected max
duration (a plain number, e.g. "expect ~10-15 minutes; if you have not reported back by then, treat this as
stalled"), and the *dispatching session* schedules an explicit, active check-in at that duration -- not a
passive wait, and not reliance on the dispatched agent's own completion signal at all. Concretely this could
look like: the dispatching session sets a real wall-clock or poll-loop check (e.g. a Monitor-style until-loop
against `gh pr view`/`gh run list` on the dispatching side, not the worker side) that fires at the stated
duration regardless of whether the worker has said anything, and treats "no live GitHub evidence of progress by
then" as an automatic trigger for the PR #95 triage steps -- rather than waiting for the coordinating agent to
remember to check. This shifts the enforcement point from "the dispatched agent's own behavior" (which prompt
instructions alone did not reliably control today) to "the dispatching session's own scheduling," which is the
side that actually has a mechanical hook (`Monitor`, polling, elapsed-time checks) available to it.

This proposal is not implemented here; it should go through this repo's normal decision path (task doc +
review) as a follow-up if adopted.

## Verification and rollback

- Verification: the specific "three stalls" count and sequence is `REPORTED` (this session's own account, per
  AGI-03) rather than `VERIFIED` against a git/GitHub artifact — a stalled dispatch attempt that never commits
  leaves nothing to check. What is independently checkable is the surrounding shape: PR #109's commit history
  shows multiple distinct resumption points (four review-evidence commits, three merge-sync commits, spanning
  ~1h26m) consistent with a task that needed repeated coordinator intervention to progress, per the companion
  record's verified commit hashes/timestamps. No code or config changes are made by this record, so there is
  nothing to re-run beyond re-reading the incident against the PR #95 triage section it references.
- Rollback: none needed; this is a documentation-only record. If the STRUCTURAL proposal above is later
  implemented and found wrong, revert that follow-up change, not this record.

## Prevention

This record intentionally does not implement a countermeasure -- see "Change or proposal" above. Per
`playbook/REPAIR_AND_LEARNING.md`'s explicit rule ("If a failure repeats, do not merely create another repair
note. Add a durable countermeasure..."), this is a **second** repair note for the same underlying pattern (the
first being `2026-08-18-stalled-dispatched-worker-repair.md`), so the expectation is that the durable
countermeasure step is now overdue and should be picked up as a real follow-up task rather than deferred again.
Filing a third repair note for a third recurrence of the same pattern without a mechanical fix in place would
itself be a process failure this record is trying to head off.
