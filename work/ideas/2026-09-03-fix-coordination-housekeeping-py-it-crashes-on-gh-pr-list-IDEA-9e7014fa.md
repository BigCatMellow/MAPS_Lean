# IDEA-9e7014fa: Fix coordination_housekeeping.py — it crashes on gh pr list

- Kind: `idea`
- Date: `2026-09-03`
- ID: `IDEA-9e7014fa`

## Observation

scripts/coordination_housekeeping.py raises CalledProcessError on its gh pr list call (--json field set includes comments,commits which gh rejects in that combination in this environment). The script is entirely non-functional right now.

## Source / context

Ran scripts/coordination_housekeeping.py BigCatMellow/MAPS_Lean this session, 2026-09-03; traceback at line 62 open_prs -> gh_json

## Potential value

A coordination-housekeeping script that always crashes is worse than none - it looks like a safety net that is not there. The trajectory pass and coordinators could use it if it worked.

## Smallest next test

Split the gh pr list --json field set (fetch comments/commits in a second call, or drop them if unused); add a smoke test; file a FRICTION_LOG tool-gap entry per REPAIR_AND_LEARNING mandatory-capture.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

- 2026-09-03: promoted → PR "coordination tooling fixes" (branch `fix/coordination-tooling`), bundled from the 2026-09-03 E/I Emergence pass. Append-only disposition; the "Not promoted." line above is the original capture state.
