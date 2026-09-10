# INSIGHT-f095b669: Outward-facing representations have no reconciliation cadence like the roadmap has

- Kind: `insight`
- Date: `2026-09-10`
- ID: `INSIGHT-f095b669`

## Observation

Arc #27 contains a 3-PR reconciliation wave (#321 Wiki, #322 Pilot evidence, #323 competitor evidence) plus 5 wiki-refresh commits, all correcting outward-facing artifacts that had drifted from actual MAPS_L behavior. The internal roadmap/checklist has a standing periodic reconciliation mechanism (this trajectory check, every arc); the wiki, Pilot-evidence bundle, and research/competitor owners have none - they drift silently until someone notices and runs a batch.

## Source / context

trajectory check #27; PRs #321 #322 #323; wiki commits d042ab2..54869f5; INSIGHT-68a53a28 (trajectory check is now part of the process)

## Potential value

Same failure mode the trajectory check exists to prevent for the roadmap (status claims drifting from evidence), just on the outward surface. A lightweight 'outward-doc reconciliation' checklist item folded into the existing trajectory cadence would catch drift at 1-arc granularity instead of at batch-discovery.

## Smallest next test

At trajectory #28, add one bullet: 'spot-check wiki Development-status page + Pilot-evidence bundle head against origin/main capability status'; measure whether it surfaces any drift and how much time it costs.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.
