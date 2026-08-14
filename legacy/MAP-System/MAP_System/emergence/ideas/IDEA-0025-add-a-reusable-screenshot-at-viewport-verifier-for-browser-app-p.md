# Idea Card

Idea ID: IDEA-0025
Project: MAP
Source insight or synthesis: INS-0032
Owner: claude-lab-lure
Date: 2026-07-19
Status: OPEN

## Idea


- idea: Add a reusable screenshot-at-viewport verifier for browser-app projects (url + width in, PNG out) so the visual-fidelity check from [[emergence/promotions/PROMO-0012-idea-0024]] is one command instead of a hand-rolled chromium CDP script per task.

## Problem or opportunity


- gap: The promoted visual-fidelity rule requires screenshotting the real build at the operator viewport, but no tool exists for it. During ClearFront I hand-wrote a chromium CDP script mid-task. A mandated check with no tool gets skipped -- exactly the mechanical-surfacing gap in [[emergence/insights/INS-0032-promoted-process-rules-stay-ineffective-unless-mechanically-surf]].

## Why now


- now: The Command Center Lab is actively testing emergence workflow.

## Expected benefit


- gain: Makes the promoted rule cheap to follow and repeatable; reusable by any browser-app design task and by reviewers reproducing visual evidence. Turns a prose mandate into a runnable command.

## Cost


- cost: One small script per browser-app project, or a shared MAP helper; chromium is already present (test_all.mjs uses it).

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
