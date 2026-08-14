# Insight Record

Insight ID: INS-0056
Project: MAP
Related task: NONE
Detected by: claude-lab-muza
Date: 2026-07-29
Status: PROMOTED

## Short description


- obs: Operator-directed work explicitly scoped outside MAP task governance has no emergence-capture trigger at all, not even a skipped checkbox

## Trigger


- src: Created from command-center emergence capture.

## The synthesis


- synth: This differs from [[emergence/insights/INS-0013-emergence-insight-capture-was-skipped-entirely-for-an-entire-pro]] (capture accidentally skipped inside a governed project): here there is no governed task to skip capture on in the first place, because MAP's only capture trigger (the release checklist) fires on task release. Real, reusable decisions made in ungoverned operator-directed work (like the three scoping choices already made in this UI port) currently have zero path into the emergence system.

## Why it might matter


- why: Those lessons will be lost once the session/handoff chain ends and rediscovered from scratch next time similar work happens, unless capture is explicitly decoupled from task governance.

## Evidence


- ev: MAP_System/handoffs/STATE_SNAPSHOT-claude-lab-nene-20260729T052244Z.yaml active_constraints and forward_tasks sections; MAP_System/emergence/insights/[[emergence/insights/INS-0013-emergence-insight-capture-was-skipped-entirely-for-an-entire-pro]]-*.md as the nearest but distinct existing pattern.

## Risk


- risk: Low: map_emergence.py insight already accepts --related-task NONE, so no CLI change is required, only documenting that this is an accepted, intended use.

## Scope


- scope: Any operator-directed work explicitly kept outside a project's MAP governance.

## Recommended next action

- [ ] ignore
- [ ] park
- [x] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note: Promoted through IDEA-0033 and PROMO-0017 as an opt-in lightweight
  capture rule. Capture does not import the underlying work into MAP task
  governance or create authority.
