# Idea Card

Idea ID: IDEA-0033
Project: MAP
Source insight or synthesis: INS-0056
Owner: codex-lab-mebo
Date: 2026-07-29
Status: PROMOTED_TO_TASK

## Idea

- idea: Document lightweight emergence capture for reusable lessons from
  operator-directed work that intentionally remains outside MAP task
  governance.

## Problem or opportunity

- gap: Release-triggered capture cannot fire when there is intentionally no
  MAP task, even though `map_emergence.py` already supports
  `Related task: NONE`.

## Why now

- now: INS-0056 and INS-0057 preserve a live example where useful design-port
  decisions would otherwise remain only in session continuity records.

## Expected benefit

- gain: Reusable lessons remain discoverable without retroactively inventing a
  task or expanding MAP authority over out-of-scope work.

## Cost

- cost: One bounded documentation section; no task automation or new agent
  role.

## Reversibility

- [x] yes
- [ ] no
- [ ] partial:

## Smallest safe experiment

- test: INS-0057 demonstrates that a useful `Related task: NONE` record can be
  captured and indexed without changing the underlying work's governance.

## Decision needed

- [ ] task-DRI
- [ ] review-DRI
- [ ] state-steward
- [ ] project-DRI
- [x] human-owner

## Recommendation

- [ ] park
- [ ] reject
- [ ] test
- [x] promote-task
