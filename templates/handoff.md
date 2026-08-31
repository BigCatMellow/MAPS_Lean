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

- Append this session's friction/request items (errors, stalls, tool-gaps,
  operator asks) to
  [`work/coordination/FRICTION_LOG.md`](../work/coordination/FRICTION_LOG.md) —
  one entry each, with a `countermeasure` and a `verified:` field.

If responsibility is actually transferring, ensure the receiving worker has a
valid task/ownership record; a handoff note alone does not grant authority.
