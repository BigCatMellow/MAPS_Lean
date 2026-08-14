# Insight Record

Insight ID: INS-0025
Project: ClearFront
Related task: TASK-211
Detected by: claude-lab-gome
Date: 2026-07-17
Status: RAW

## Short description


- obs: Card-replacement undo currently lets a player see the drawn replacement card before deciding whether to undo, violating the rules' hidden-information-undo prohibition -- a real exploit, not a scope gap.

## Trigger


- src: Auditing the current implementation against clearfront_rules.md's undo rules (section 14, replaceCard at baseline/index.html:2261-2269).

## The synthesis


- synth: saveUndo('card swap') fires before replaceCard draws the new hidden card, so a player can look at the replacement and then undo -- letting them peek at a random draw for free. clearfront_rules.md explicitly lists 'actions that reveal hidden information and cannot be restored fairly' as non-reversible, so this is a real rules violation with a concrete exploit path, not a cosmetic gap.

## Why it might matter


- why: This is a correctness bug with a player-facing exploit (free information), distinct from the scope/missing-content deviations (Equipment, Mind/Forge/Neutral, Stun) that are legitimate future-scope decisions. It should be prioritized above those in the next implementation task.

## Evidence


- ev: Independently re-derived by claude-lab-gome from baseline/index.html:2261-2269 during TASK-211 review, matching codex-lab-lilo's original finding exactly.

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
