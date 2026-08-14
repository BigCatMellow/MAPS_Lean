# Insight Record

Insight ID: INS-0027
Project: MAP
Related task: NONE
Detected by: codex-lab-lilo
Date: 2026-07-17
Status: CLARIFIED

## Short description


- obs: Operational notes are durable but not automatically promoted into behavior-changing memory.

## Trigger


- src: A temporary Claude-to-Codex fallback rule was written only in a task-scoped helper note and agent status, which future sessions are not guaranteed to load.

## The synthesis


- synth: Operational notes are durable but not automatically promoted into behavior-changing memory.

## Why it might matter


- why: Durability is not learning unless the record is routed into future orientation and later retired when conditions change.

## Evidence


- ev: The operator had to explicitly ask that the fallback be remembered; the original Claude reviewer and helper both stopped without responding.

## Risk


- risk: Scattered notes become dead memory, causing repeated incidents, contradictory guidance, and operator re-explanation.

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
