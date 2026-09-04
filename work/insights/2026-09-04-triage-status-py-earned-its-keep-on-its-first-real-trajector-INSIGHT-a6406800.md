# INSIGHT-a6406800: triage_status.py earned its keep on its first real trajectory-pass use

- Kind: `insight`
- Date: `2026-09-04`
- ID: `INSIGHT-a6406800`

## Observation

tools/triage_status.py merged this arc (#281, slice 2). On its first run inside a trajectory pass (#22) it flagged the 2026-08-18-stalled-dispatched-worker-repair.md DRIFT record as missing a countermeasure/regression case — a record that sat un-actioned through ~13 prior passes' manual friction skims. That record's Prevention 1 ('no mechanical timeout/heartbeat for dispatched background workers') is exactly the gap the session-27 Monitor-polling stalls (rovu, buro) re-hit.

## Source / context

tools/triage_status.py --root . output at check #22; work/notes/2026-08-18-stalled-dispatched-worker-repair.md; FRICTION_LOG 2026-09-03 'dispatched worker stalls on its own full unittest suite'

## Potential value

Mechanical backstops for consumption duties surface long-cold items that human skims normalize away. Argues for keeping the --strict CI slice (slice 3, currently deferred) on the roadmap.

## Smallest next test

Check #23 confirms the 2026-08-18 DRIFT record reached a disposition (countermeasure pointer added or explicit accept) rather than being re-flagged a 2nd pass.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.
