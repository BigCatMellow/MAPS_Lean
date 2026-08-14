# Insight Record

Insight ID: INS-0033
Project: MAP
Related task: NONE
Detected by: claude-lab-lure
Date: 2026-07-19
Status: OPEN

## Short description


- obs: Design work destined for an existing app should be prototyped in the target codebase structure, not a standalone artifact; a vacuum-mockup turns the port into a re-implementation with built-in drift.

## Trigger


- src: The ClearFront mockup was a self-contained HTML artifact using tile markup, while the app uses card markup plus a 1400-line legacy stylesheet. Porting was re-implementation, and visual details drifted repeatedly (champion fit, wordmark, breakpoints), each needing a new operator round.

## The synthesis


- synth: Design work destined for an existing app should be prototyped in the target codebase structure, not a standalone artifact; a vacuum-mockup turns the port into a re-implementation with built-in drift.

## Why it might matter


- why: A standalone mockup is cheap to iterate but the fidelity it earns does not transfer; the target codebase constraints (legacy CSS, existing class contracts, element-selector leaks) only surface during the port. Prototyping against the real components earns transferable fidelity.

## Evidence


- ev: ClearFront: mockup v1-v6 in the cheap medium was efficient; then 3 port-rework rounds in the real app. The legacy aside-selector leak only appeared in the real app at the operator viewport, never in the artifact.

## Risk


- risk: Acting without promotion could bypass HPOM governance.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
