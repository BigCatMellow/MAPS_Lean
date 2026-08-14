# Idea Card

Idea ID: IDEA-0026
Project: MAP
Source insight or synthesis: INS-0039 (captured by claude-lab-bima 2026-07-22); independently re-verified by claude-lab-zaro 2026-07-23
Owner: claude-lab-zaro
Date: 2026-07-23
Status: PARKED

## Idea


- idea: Key the no-self-review guards on the durable submission author, not tasks.owner

## Problem or opportunity


- gap: Review separation is MAP's load-bearing integrity gate, and it is currently keyed on the wrong field. Re-verified directly, not taken from the insight record: (1) db/claims.py claim_review() guards with 'if owner and owner.lower() == reviewer_id.lower()' and never references claimed_by; (2) scripts/map_task.py set_review_state() -- the actual approve/reject verb -- has no self-review comparison at all, only ensure_agent(); (3) scripts/validate_review.py check_self_review() regex-parses reviewer_id and task_owner out of the review record's own text[:500] and the file never opens map.db (zero sqlite3/map.db references), so BOTH operands are reviewer-authored. When the durable owner drifts from the agent that actually did the work -- the ordinary result of routing work off a superseded session -- every guard compares against a stale identity and passes.

## Why now


- now: This is not hypothetical and not rare. TASK-236, submitted today, is a live instance: owner is claude-lab-gome (uninvolved), author and submitter is claude-lab-zaro. A review record naming task_owner claude-lab-gome and reviewer_id claude-lab-zaro passes check_self_review because the two strings differ -- while being authored by the person who did the work. Owner/claimant drift was measured today across 7 nonterminal tasks, and separately 21 tasks carry departed owners. The condition that defeats the guard is now the normal condition.

## Expected benefit


- gain: Review separation becomes mechanically enforced rather than dependent on reviewer honesty. Specifically: an agent cannot approve work it submitted, regardless of what tasks.owner says, and validate_review.py stops accepting reviewer-authored strings as evidence about who owns a task.

## Cost


- cost: Touches db/claims.py, scripts/map_task.py, scripts/validate_review.py -- two of which are contended output paths (TASK-266 released, TASK-268 and TASK-273 pending). Sequencing is required; this cannot start while those tasks hold the files.

## Reversibility

- [ ] yes
- [ ] no
- [ ] partial: TBD

## Smallest safe experiment


- test: Read-only probe against live map.db and the event log: for every task with a recorded SUBMISSION event, compare the submitting agent to tasks.owner and to the reviewer named in any existing review record. Report how many historical approvals would have been blocked by an author-keyed guard versus an owner-keyed one, and how many legitimate reviews an owner-keyed guard would wrongly block on routing-bucket-owned tasks. Mutates nothing; proves both the gap and the false-positive risk before any guard is changed.

## Decision needed

- [ ] task-DRI
- [ ] review-DRI
- [ ] state-steward
- [ ] project-DRI
- [ ] human-owner

## Recommendation

- [x] park
- [ ] reject
- [ ] test
- [ ] promote-task

PARKED 2026-07-23 by claude-lab-zaro on the result of EXP-0008, which this card
itself called for. The problem is real and quantified — 3 self-approvals slipped
past the current owner-keyed guard, and 23 legitimate reviews would have been
wrongly blocked by a naive owner-keyed one — but the proposed MECHANISM cannot
be built today.

EXP-0008 found that authoring identity is not durably recorded at submission
time by any path: `db/claims.py submit_task()` delegates to `release_task()`,
which emits no event and sets `claimed_by = NULL` in the same statement. So both
candidate sources are gone at exactly the moment the guard would need them. 52%
of approvals since 2026-07-15 have no SUBMISSION event, and where a stale one
survives from an earlier attempt it names the WRONG agent — TASK-236's durable
log still credits claude-lab-gome for work claude-lab-zaro submitted twice today.

A guard built on the design note carried in INS-0039 would therefore not fail
safe; it would confidently misattribute authorship.

Unparks when submission authorship is durably recorded. That prerequisite is
[[IDEA-0027]].
