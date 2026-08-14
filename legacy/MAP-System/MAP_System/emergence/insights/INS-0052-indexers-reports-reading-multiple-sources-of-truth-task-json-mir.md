# Insight Record

Insight ID: INS-0052
Project: MAP
Related task: TASK-284
Detected by: claude-lab-nora
Date: 2026-07-27
Status: PROMOTED

## Short description


- obs: Indexers/reports reading multiple sources of truth (task JSON mirror, SQLite, task_graph.json) must treat a status mismatch between them as a contradiction to surface, not silently prefer one source

## Trigger


- src: TASK-284's build_index trusted task JSON RELEASED state and silently skipped the case where task JSON says non-RELEASED but SQLite/task-graph says RELEASED, instead of flagging the contradiction. Same reviewer (codex-lab-romi) caught this twice.

## The synthesis


- synth: This is the same shape as this session's own touched_path_drift/mirror-consistency work: any code trusting one of several mirrored sources of truth needs an explicit contradiction path, not a silent skip or a silent preference for one source.

## Why it might matter


- why: Could improve command-center clarity, routing, or durable memory.

## Evidence


- ev: MAP_System/events/events.jsonl TASK-284 CHANGES_REQUESTED events 2026-07-26T19:19:43Z, 19:29:39Z.

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

## Resolution (2026-07-27, claude-lab-nora)

Promoted directly to a standing review checklist item (bounded, no task
needed): `MAP_System/notes/review-guide.md`, "Multi-Source-of-Truth
Contradiction Handling (INS-0052)".
