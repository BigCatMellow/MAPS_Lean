# INSIGHT-29a10ad4: check_review_evidence.py's head_sha walk-back stops silently at merge commits, which is correct but easy to trip on

- Kind: `insight`
- Date: `2026-08-19`
- ID: `INSIGHT-29a10ad4`

## Observation

scripts/check_review_evidence.py's module docstring explains that head_sha can't just be git rev-parse HEAD because a reviewer working from a stale checkout could unknowingly claim an old head; the fix walks HEAD backward through evidence-only commits under work/reviews/ but explicitly never walks past a merge commit or root commit (see _current_head_sha, line ~44-72). This is a deliberate, correct design (a merge commit could hide non-evidence changes), but it means every main-sync merge on a long-lived PR branch forces a brand new head_sha and therefore a brand new review-evidence commit -- which is exactly the mechanism that produced PR #109's four-cycle review churn documented in work/notes/2026-08-18-review-evidence-resync-classifier-friction.md.

## Source / context

scripts/check_review_evidence.py lines 19-30, 44-72; observed in practice via PR #109's four rebind cycles

## Potential value

Naming this connection explicitly (walk-back-stops-at-merge is *why* every sync forces a rebind) makes the friction legible as an expected consequence of a correct safety property, not a bug to fix in the walk-back logic itself. That framing heads off a future session mistakingly 'fixing' the walk-back to be more permissive, which would reopen the exact hole the docstring describes (sneaking unreviewed changes in under an old head_sha via a merge commit).

## Smallest next test

If this pattern recurs, write a short note in scripts/check_review_evidence.py's docstring (or a playbook doc) making the merge-forces-rebind consequence explicit, so a future reader who is tempted to loosen the walk-back understands the tradeoff before touching it.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.
