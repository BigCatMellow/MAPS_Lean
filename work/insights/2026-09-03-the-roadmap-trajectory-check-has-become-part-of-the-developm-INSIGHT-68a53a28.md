# INSIGHT-68a53a28: The roadmap trajectory check has become part of the development loop, not a periodic sanity check

- Kind: `insight`
- Date: `2026-09-03`
- ID: `INSIGHT-68a53a28`

## Observation

21 trajectory-check passes in ~2.5 weeks (2026-08-19 to 2026-09-03), roughly one per 3-6 PR arc, each producing a ~400-line note and often a checklist edit. ROADMAP_TRAJECTORY_CHECK.md section 'When to run it' describes it as arc-boundary roadmap maintenance ('after a meaningful batch/phase'), but in practice it runs continuously and Tenth-Seat Trigger 2 has been armed since pass #17 (every pass finds something substantive).

## Source / context

git log --oneline --grep='Roadmap trajectory check' main; playbook/ROADMAP_TRAJECTORY_CHECK.md; playbook/TENTH_SEAT_REVIEW.md Trigger 2

## Potential value

A check that runs every arc and always finds something is doing useful work, but it is no longer the thing its own doc describes, and the per-pass cost (dispatch + independent review + evidence rebind, ~2 agent-sessions each) is now a standing overhead. Worth deciding deliberately: is this the intended cadence, or should passes batch to every 2-3 arcs with a lighter per-arc friction-only sweep?

## Smallest next test

At #22, measure: how many of passes #12-#21 changed a trajectory action or caught a status-truth error that a friction-only sweep would have missed? If few, propose a lighter default cadence.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.
