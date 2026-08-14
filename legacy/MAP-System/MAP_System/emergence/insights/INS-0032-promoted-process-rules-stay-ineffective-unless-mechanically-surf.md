# Insight Record

Insight ID: INS-0032
Project: MAP
Related task: NONE
Detected by: claude-lab-lure
Date: 2026-07-19
Status: OPEN

## Short description


- obs: Promoted process rules stay ineffective unless mechanically surfaced into task context; prose buried in guides gets skipped. The visual-fidelity rule now lives only in review-guide.md/task-authoring-guide.md, so it inherits the exact weakness that caused the original failure.

## Trigger


- src: Reviewing the ClearFront prototype process: the failure in [[emergence/insights/INS-0031-on-visual-fidelity-tasks-verify-by-screenshot-vs-reference-befor]] happened even though MAP already had task-authoring and review guides. Those guides did not change my behavior because nothing surfaced the relevant rule when I started the design work. The freshly promoted rule ([[emergence/promotions/PROMO-0012-idea-0024]]) has the same gap.

## The synthesis


- synth: Promoted process rules stay ineffective unless mechanically surfaced into task context; prose buried in guides gets skipped. The visual-fidelity rule now lives only in review-guide.md/task-authoring-guide.md, so it inherits the exact weakness that caused the original failure.

## Why it might matter


- why: MAP already has operational_lessons.py which can project promoted lessons into startup/task context. Without that projection, a promoted rule is just more prose competing for attention. This gates the value of the whole E/I promotion loop: promotion into a doc is necessary but not sufficient to change behavior.

## Evidence


- ev: ClearFront UI port: both guides existed before the failure; the failure still occurred, then recurred across 3 operator rounds. Fix path: register design-fidelity as an operational lesson projected into design-task context, or a mechanical checklist gate at submission.

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
