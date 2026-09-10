# IDEA-497fca2f: Track rows awaiting a first-exposure exercise in a standing list

- Kind: `idea`
- Date: `2026-09-10`
- ID: `IDEA-497fca2f`

## Observation

Across trajectory checks #25-#27, security/harness rows (6.5, H5, E4, L6, 6.16, 6.4, H4) each closed or advanced via a discrete 'first real production exposure' exercise PR, distinct from both the design-note PR and the default-off call-site PR (e.g. 6.4: design 2026-09-06 -> call site #306 -> exercise #320; 6.22: call site #310, exercise still pending 1 arc later). Which rows are 'call site landed, exercise pending' lives only in trajectory-note prose + row text and is re-derived by hand each pass.

## Source / context

trajectory check #27; CAPABILITY_CHECKLIST.md rows 6.4/6.22/H4; PRs #306 #310 #320 #324

## Potential value

A standing mini-list ('awaiting first-exposure exercise') would cut per-pass rediscovery cost and make the design-note -> call-site -> deferred-exercise cadence gap visible before it becomes a 3-arc finding.

## Smallest next test

Add an 'Awaiting first-exposure exercise' subsection to CAPABILITY_CHECKLIST.md §7 (or master roadmap §7); check at trajectory #28 whether 6.22's status was found faster and whether the list stayed accurate.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.
