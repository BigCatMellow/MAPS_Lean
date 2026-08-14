# Idea Card

Idea ID: IDEA-0024
Project: MAP
Source insight or synthesis: INS-0031
Owner: claude-lab-lure
Date: 2026-07-19
Status: OPEN

## Idea


- idea: A design-port task should freeze the approved mockup as the acceptance reference and require a screenshot-vs-reference fidelity check in its acceptance criteria, not just tests-green and structural completion.

## Problem or opportunity


- gap: Design-port tasks currently accept on tests-green + 'ported structure', which lets an agent declare 'matches the design' while visual fidelity still lags -- causing operator-detected divergence and rework (see [[emergence/insights/INS-0031-on-visual-fidelity-tasks-verify-by-screenshot-vs-reference-befor]]).

## Why now


- now: The Command Center Lab is actively testing emergence workflow.

## Expected benefit


- gain: Makes visual fidelity mechanically checkable and stops premature 'done' claims: the frozen mockup is the reference, and a screenshot of the real build must be compared to it before submission.

## Cost


- cost: Requires capturing/attaching a reference image and a real-build screenshot per design-port task; light for the author, but adds an artifact to store.

## Reversibility

- [ ] yes
- [ ] no
- [ ] partial: TBD

## Smallest safe experiment


- test: Create and validate file-backed emergence records.

## Decision needed

- [ ] task-DRI
- [ ] review-DRI
- [ ] state-steward
- [ ] project-DRI
- [ ] human-owner

## Recommendation

- [ ] park
- [ ] reject
- [ ] test
- [ ] promote-task
