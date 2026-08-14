# Experiment Record

Experiment ID: EXP-0007
Project: MAP
Source idea: IDEA-0013
Owner: claude-lab-niko
Date: 2026-07-21
Status: PROPOSED

## Hypothesis


- hyp: EXP: implement [[emergence/ideas/IDEA-0013-add-an-idea-scouting-role-a-role-cadence-responsible-for-activel]] as a startup cadence rather than a staffed scouting role, and measure whether it drains coverage debt or just gets gamed

## Test


- test: For 14 days (2026-07-21 to 2026-08-04) every core agent runs 'map_emergence.py coverage' as part of startup orientation, acts on what it finds, and marks only records it actually read via --mark-reviewed. No new role, no new agent, no new cadence owner. Measure the overdue count and, separately, the status-change rate of records that get marked.

## Scope


- scope: MAP emergence records only. Adds one command to the existing startup orientation sequence; changes no authority, no routing, no schema.

## Limits


- limits: Does not implement [[emergence/ideas/IDEA-0013-add-an-idea-scouting-role-a-role-cadence-responsible-for-activel]]'s judgment half as a staffed role. Does not sweep other projects (4 Riftbound insights remain unswept and are excluded from success criteria). Coverage debt for non-emergence durable records (handoffs, shared/, artifacts) is out of scope.

## Success criteria


- pass: Overdue count falls to <=2 and stays there across the window, AND at least three marked records change status (PROMOTED/DISMISSED/PARKED/task-promoted) -- proving judgment was applied, not just bookkeeping.

## Failure criteria


- fail: KILL if marking rate is high while status-change rate is ~zero: that means agents are clearing the list to make it green rather than doing the thinking, and the ledger has become the metric-gaming failure it was built to prevent -- redesign or drop it, do not tune the threshold. KILL if overdue count has not fallen by 2026-08-04, which would mean startup orientation is not a strong enough hook and [[emergence/ideas/IDEA-0013-add-an-idea-scouting-role-a-role-cadence-responsible-for-activel]] genuinely needs a named owner after all.

## Evidence to collect

- ev:

## Review path

- review:

## Result

- result: pending

## Decision

- [ ] adopt
- [ ] revise
- [ ] reject
- [ ] park

## Notes

- note:
