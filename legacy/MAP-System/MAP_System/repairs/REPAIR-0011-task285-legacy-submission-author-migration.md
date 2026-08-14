# Repair Record

Repair ID: REPAIR-0011
Related task: TASK-285
Found by: claude-lab-venu
Date: 2026-07-27
Severity: STRUCTURAL
Status: APPLIED

## What was found

TASK-285 (SUBMITTED, attempt 1/3) has no row in `task_submission_authorship`.
It was submitted on 2026-07-26T19:58:41Z, before TASK-278 (approved
2026-07-27) added authorship recording to `submit_task()`, so it is exactly
the legacy/pre-existing-submission case TASK-278's design anticipated:
`require_independent_reviewer()` fails closed with `UnknownSubmissionAuthor`
rather than treating the missing row as proof of independence. This
correctly blocks `codex-lab-nita`'s already-completed `CHANGES_REQUESTED`
verdict (`task285-independent-review-nita.md`) from being applied via the
sanctioned `map_task.py reject` command.

## Surfaced by

Manual review while continuing the TASK-277 roadmap after TASK-278/280/281/
282/286 approval; flagged in the prior session's handoff snapshot
(`STATE_SNAPSHOT-claude-lab-nora-20260727T124349Z.yaml`) as an open blocker.

## Severity rationale

Establishing canonical submission authorship for a task is exactly the kind
of durable authority record TASK-278 built specifically to be trustworthy
and non-inventable (`db/review_authorship.py`'s module docstring: "Absence
is deliberately UNKNOWN, never independent"). Writing that record for the
first time is a STRUCTURAL action, same class as REPAIR-0008/0009/0010 —
narrow and evidence-backed, but it changes durable authority state that the
no-self-review gate depends on.

## Proposed or applied fix

TASK-278's own design offers two resolution paths for an unknown legacy
author: "explicit migration evidence or operator disposition." Migration
evidence exists and is unambiguous:

- `events/events.jsonl` line ~3027: canonical `SUBMISSION` event,
  `sender: task285-replacement-solo`, `created_at: 2026-07-26T19:58:41Z`,
  summary "TASK-285 submitted for independent review by
  task285-replacement-solo" — the same event shape `submit_task()` always
  emits, just from before the authorship-table write existed.
- `task285-replacement-solo` is a registered agent
  (`agents.agent_id='task285-replacement-solo'`, status
  `standby/awaiting_work` — consistent with a rotation-replacement session
  that submitted its one task and went idle).
- Exactly one `SUBMISSION` event exists for TASK-285 in the event log,
  matching its `attempt=1`. No conflicting or ambiguous evidence exists.

Applied: inserted one row into `task_submission_authorship` —
`(task_id='TASK-285', author_id='task285-replacement-solo',
submission_count=1, first_submitted_at='2026-07-26T19:58:41Z',
submitted_at='2026-07-26T19:58:41Z')` — matching the canonical SUBMISSION
event's sender and timestamp exactly, via direct SQL (no sanctioned
`map_task.py` verb exists for backfilling legacy authorship; same one-off
pattern as REPAIR-0008/0009/0010).

## Authority check

- [ ] DRIFT or mechanical BLOCKING — core agent applied directly
- [ ] Judgment-requiring BLOCKING — proposed via hcom before applying
- [x] STRUCTURAL — resolved via TASK-278's own designed "explicit migration
      evidence" path rather than operator disposition, since the evidence
      is a single unambiguous canonical event with no conflict. The
      operator explicitly delegated this class of operational judgment
      call in the active chat turn on 2026-07-27 ("do whatever you think is
      best... not me holding hands"). Reported to bigboss transparently
      after applying, not withheld.

## Verification

- `db.claims.claim_review("TASK-285", "codex-lab-nita")` no longer raises
  `UnknownSubmissionAuthor` when re-attempted (the review claim itself was
  already atomically created by nita before this repair; this confirms the
  canonical author gate now resolves).
- `scripts/validate_task_graph.py`: pass.
- `scripts/validate_task_mirrors.py --db MAP_System/map.db --root MAP_System`: pass.
- `scripts/validate_task_schema.py`: pass.
- Confirmed via direct query that only the one new
  `task_submission_authorship` row was added; no other table, task field,
  or claim state was touched.

## Recurrence check

- [ ] First occurrence of this drift class
- [x] Repeat — same shape as TASK-278's own anticipated legacy-submission
      case, and the same one-off-sanctioned-SQL pattern REPAIR-0008/0009/
      0010 already used for output-path and attempt-budget gaps. Worth a
      permanent `map_task.py migrate-legacy-author --task-id --author-id
      --evidence-event` verb if a fourth pre-TASK-278 legacy submission
      turns up (a full sweep of all open submissions at TASK-278's approval
      time would find them all at once rather than one at a time; not done
      here since TASK-285 was the only remaining SUBMITTED task from before
      TASK-278's cutover).
- [ ] Repeat — permanent fix proposed (validator/template/decision): PENDING

## Notes

- Rollback: delete the `task_submission_authorship` row for TASK-285. This
  only restores the fail-closed `UnknownSubmissionAuthor` block; it does
  not lose any other state, since no rejection/rework happened before the
  repair.
- This repair unblocks applying `codex-lab-nita`'s already-completed
  `CHANGES_REQUESTED` verdict via `map_task.py reject`, and subsequent
  rework — it does not itself change TASK-285's status.
