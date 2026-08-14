# Idea Card

Idea ID: IDEA-0021
Project: ClearFront
Source insight or synthesis: INS-0025
Owner: codex-lab-lilo
Date: 2026-07-17
Status: PROMOTED_TO_TASK

## Idea


- idea: Disallow undo after card replacement reveals hidden information

## Problem or opportunity


- gap: Replacement stores an undo snapshot before drawing, allowing a free peek at a random card.

## Why now


- now: TASK-211 audit and independent review confirmed a concrete player-facing exploit; Claude authorized the bugfix lane in hcom #983.

## Expected benefit


- gain: Restores conformance with rules section 14 and prevents free hidden-information scouting.

## Cost


- cost: Small behavior change in replacement/undo flow plus regression evidence.

## Reversibility

- [x] yes
- [ ] no
- [ ] partial: TBD

## Smallest safe experiment


- test: Patch only the replacement action so it cannot populate undo, then execute a focused browser interaction proving Undo stays unavailable after replacement while ordinary reversible actions remain undoable.

## Decision needed

- [x] task-DRI
- [x] review-DRI
- [ ] state-steward
- [ ] project-DRI
- [ ] human-owner

## Recommendation

- [ ] park
- [ ] reject
- [ ] test
- [x] promote-task
