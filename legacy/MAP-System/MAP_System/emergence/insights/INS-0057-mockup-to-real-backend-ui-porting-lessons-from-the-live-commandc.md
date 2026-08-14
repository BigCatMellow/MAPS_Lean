# Insight Record

Insight ID: INS-0057
Project: MAP
Related task: NONE
Detected by: claude-lab-muza
Date: 2026-07-29
Status: PROMOTED

## Short description


- obs: Mockup-to-real-backend UI porting lessons from the live CommandCenterUI redesign (room.js pattern)

## Trigger


- src: Created from command-center emergence capture.

## The synthesis


- synth: Three operator-confirmed scoping decisions generalize beyond this one port: (1) derive UI groupings from an existing live field (hcom agent tag) instead of inventing a new taxonomy the mockup imagined but the backend does not have; (2) ship new pages alongside existing ones rather than replacing the default entrypoint, so a redesign can be evaluated without a forced cutover; (3) port design-tool markup to the app's existing plain-JS style rather than adopting the mockup tool's own runtime (React/support.js) as a new production dependency.

## Why it might matter


- why: A design-tool mockup's invented concepts (fictional multi-project grouping, a DQ field, a 4-way composer mode) do not necessarily exist in the real backend; confirming what the live API actually serves before porting, and choosing the smallest-diff integration path, avoided building UI for data that does not exist.

## Evidence


- ev: STATE_SNAPSHOT-claude-lab-nene-20260729T052244Z.yaml task_context.recent_events (Explore-agent backend mapping, three AskUserQuestion scoping answers) and active_constraints.

## Risk


- risk: Low: this is a capture-only record; the underlying port work is unaffected and continues in nene's session.

## Scope


- scope: Any future design-comp-to-production porting task in this workspace (CommandCenterUI or otherwise).

## Recommended next action

- [ ] ignore
- [ ] park
- [x] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note: Promoted through IDEA-0034 and PROMO-0018 into reusable task-authoring
  guidance. It does not require React avoidance or side-by-side rollout when
  an operator explicitly chooses otherwise.
