# INSIGHT-651d8c62: The 7-row security cluster has been 'one step from DONE' for ~13 trajectory passes

- Kind: `insight`
- Date: `2026-09-03`
- ID: `INSIGHT-651d8c62`

## Observation

Trajectory check #8 (2026-08-26) framed the harness-enforcement cluster (6.4/6.5/6.16/6.22/H5/E4/L6) as 'one enforced pass away' from DONE. Check #21 (2026-09-03) still frames it as one step away — now 'runbook OPTION B'. Each pass the last step recedes: no prod caller -> composition root default-off -> lineage-bootstrap deadlock -> hcom 0.7.25 adapter defect -> synthetic session opens no incident -> OPTION B lineage wiring. The exit criterion ('first real production exposure of an enforced pass producing a routable resume_denied') has not moved closer in 13 passes despite ~8 PRs of real work against it.

## Source / context

work/notes/2026-09-0[123]-roadmap-trajectory-check-{8..21}.md; CAPABILITY_CHECKLIST.md H5/6.16 evidence-cell history; work/notes/2026-09-03-item5-enforced-pass-results.md; this session's #278 review

## Potential value

If a roadmap exit criterion survives 13 maintenance passes without measurable progress toward it, the criterion itself is a candidate defect, not just the work. Naming this lets the operator make an explicit call (accept OPTION-A instantiation evidence as DONE-with-caveat / run a controlled real-stall exercise / hold indefinitely) instead of the roadmap implicitly assuming the gap closes itself.

## Smallest next test

At trajectory check #22, if OPTION B has not produced a real resume_denied, put the three options to the operator as an explicit decision item rather than recording a 14th 'one step away'.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.
