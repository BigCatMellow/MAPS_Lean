# Insight Record

Insight ID: INS-0053
Project: MAP
Related task: TASK-288
Detected by: lili-replacement-nisa
Date: 2026-07-27
Status: OPEN

## Short description


- obs: Prose-only rules get missed even by the agent who just built the mechanism to catch that exact failure shape

## Trigger


- src: Created from command-center emergence capture.

## The synthesis


- synth: Writing a rule down more thoroughly, or in more places, does not make it more likely to be followed -- what changed the outcome both times was a second, independent check (a human catching the headless spawn; a spawned independent reviewer catching the canonical-path gap), not better documentation. An agent implementing a fix for 'rules get silently violated because nothing checks them' is not thereby immune to the same failure mode on its own work, because the fix and the awareness live in the same pass, subject to the same blind spots.

## Why it might matter


- why: Directly motivates the operator's question this session ('do we need better role contracts?') and the finding that role_registry.yaml already exists but didn't help here: the gap isn't contract format, it's that mechanical enforcement (independent review, a second agent, a code check) is what actually catches these, not documentation quality or a first-person re-read.

## Evidence


- ev: [[artifacts/reviews/task288-independent-review-task288-review-valo]] (REQUIRED finding); [[artifacts/reviews/task288-rereview-task288-review-valo]] (confirms fix); this session's hcom transcript for the --headless catch; [[AGENTS]], DEC-006, [[notes/operator-autonomy-expectation]], [[notes/command-center-lab-restart-startup]], [[notes/discovery-agent-guide]] (5 independent statements of the same never-headless rule, none enforced in code before this session).

## Risk


- risk: Could overgeneralize to 'documentation is worthless' -- it isn't; the docs are what let the independent reviewer and the operator recognize the violation as a violation. The risk is specifically in relying on the same actor's own re-read to catch its own blind spot.

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
