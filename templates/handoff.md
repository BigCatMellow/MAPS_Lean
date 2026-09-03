# Handoff: <topic>

- From: <agent or person>
- To: <agent or person, if known>
- Task: <link>
- Status: <current state>

## What is true now

Separate evidence from assumptions.

- VERIFIED: <directly checked fact>
- ASSUMED / UNKNOWN: <anything the next worker must not treat as proven>

## Work completed

- <finished change/result>

## Work not completed

- <remaining work, failed attempt, or `none`>

## Decisions and constraints

- <decision, scope boundary, non-goal, authority limit, or important convention>

## Merge authority for this handoff

- Coordinator/merge seat: <name, or "none active — merge-prep fallback to
  longest-running peer lane per AGENTS.md; `gh pr merge` stays operator-only">
- APPROVED PRs awaiting merge: <none or #Ns, with rebase/evidence state>

## Current blocker / risk

- <none or specific blocker/risk>

## Working state

- Changed/uncommitted paths: <none or paths>
- Last verification performed: <command/test/inspection and result>
- Known failing checks: <none or details>

## Next action

1. <single concrete next action>

## Do not redo / do not assume

- <work already proven, discarded approach, or assumption to avoid repeating>

## Evidence / paths

- <relevant path, command, screenshot, log, decision, or artifact>

## Before finalizing / self-clearing

- Append this session's friction signals to
  [`work/coordination/FRICTION_LOG.md`](../work/coordination/FRICTION_LOG.md) —
  one entry each, with a `countermeasure` and a `verified:` field. A
  `FRICTION_LOG` entry is REQUIRED for any of: a run/command that failed with
  rework cost; a dispatched worker that stalled or had to be re-dispatched; a
  wrong assumption discovered (recorded state / doc / plan did not match
  reality); a tool or environment gap; operator-expressed friction; a
  review-caught defect *class*. See
  [Repair and Learning](../playbook/REPAIR_AND_LEARNING.md) §"Triage procedure
  (mandatory)" for the full trigger taxonomy and not-in-scope list.
- If any captured signal is the **Nth** occurrence of a known pattern, the entry
  MUST name a mechanical safeguard or an operator escalation — not a second
  instruction — and record why the first fix did not hold (invariant 13).

If responsibility is actually transferring, ensure the receiving worker has a
valid task/ownership record; a handoff note alone does not grant authority.
