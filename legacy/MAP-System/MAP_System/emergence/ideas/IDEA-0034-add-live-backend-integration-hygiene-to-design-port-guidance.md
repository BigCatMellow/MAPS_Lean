# Idea Card

Idea ID: IDEA-0034
Project: MAP
Source insight or synthesis: INS-0057
Owner: codex-lab-mebo
Date: 2026-07-29
Status: PROMOTED_TO_TASK

## Idea

- idea: Extend design-port task guidance with live-backend integration
  hygiene: verify the real data contract, prefer existing grouping fields,
  stage alongside current entrypoints, and preserve the established runtime
  unless a migration is explicitly approved.

## Problem or opportunity

- gap: Existing guidance covers visual fidelity but not the architectural
  mismatch between design-tool mockups and production data/runtime contracts.

## Why now

- now: INS-0057 records three operator-confirmed choices from a live
  CommandCenterUI port, and the existing task-authoring guide already owns the
  neighboring visual-port guidance.

## Expected benefit

- gain: Future design ports avoid inventing unsupported backend concepts or
  importing unnecessary framework dependencies.

## Cost

- cost: A short guidance subsection with explicit operator-override language.

## Reversibility

- [x] yes
- [ ] no
- [ ] partial:

## Smallest safe experiment

- test: Apply the guidance as an acceptance-criteria prompt on the next
  design-port task and verify that the task names its backend mapping and
  rollout/runtime choices.

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
