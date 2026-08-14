# Insight Record

Insight ID: INS-0039
Project: MAP
Related task: TASK-267
Detected by: claude-lab-bima
Date: 2026-07-22
Status: RAW

## Short description


- obs: Both no-self-review guards key on tasks.owner, so owner/claimant drift silently disables review separation

## Trigger


- src: Assigned as independent reviewer for TASK-267 under operator option A (hcom #12415). TASK-267 is IN_PROGRESS with owner='codex-lab-lime' (inactive, session_superseded) and claimed_by='codex-lab-kula' (the live agent actually doing the rework). Checking that my own review claim would work exposed that both self-review guards compare against tasks.owner, which is now stale on this exact task.

## The synthesis


- synth: MAP has two mechanical no-self-review guards and both key on tasks.owner, never on tasks.claimed_by or the recorded submitter. When durable owner drifts from the live claimant -- the normal result of reassigning work off an inactive agent -- both guards pass for the actual author, and [[AGENTS]] rule 9 falls back to reviewer honesty alone.

## Why it might matter


- why: Review separation is the load-bearing integrity gate in MAP: it is what makes agent-produced work trustworthy without operator re-verification. The drift that defeats it is not exotic; it is produced by the ordinary recovery path for a superseded session, which is exactly when oversight matters most. TASK-267 is a live instance: its rework author could approve their own work today and neither guard would fire, and the review record making that pass would not even be dishonest.

## Evidence


- ev: 1) db/claims.py claim_review(): guard is 'if owner and owner.lower() == reviewer_id.lower(): return False' -- owner only, no claimed_by check. 2) The same file documents claim_review as optional: set_review_state()'s comment states 'a reviewer who never called claim_review() can still approve/reject normally.' 3) scripts/map_task.py set_review_state() (the approve/reject verb) has no self-review comparison at all. 4) scripts/validate_review.py check_self_review() parses reviewer_id and task_owner from the review record's own text[:500] via regex and never opens map.db, so both operands are reviewer-authored. 5) Empirically probed: a structurally valid review record with reviewer_id=codex-lab-kula and task_owner=codex-lab-lime for TASK-267 returns 'OK review record valid', exit 0 -- and task_owner=codex-lab-lime is what map.db actually says. Probe file kept out of the repo in session scratchpad. 6) Event history: 4 tasks were APPROVED by the same agent that submitted them (TASK-019, TASK-020, TASK-030 pre-TASK-199; TASK-055 on 2026-07-01), so the gap has been exercised, though none show reviewer==tasks.owner.

## Risk


- risk: Fixing this by simply comparing reviewer against claimed_by is not sufficient on its own: set_review_state() clears claimed_by on transition, and claim_review() runs while the task is SUBMITTED, so the authoring identity must be read from the durable submission event rather than from a field that is cleared. A naive fix could also wrongly block legitimate reviewers on tasks whose owner is a routing bucket such as command-center.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
