# Insight Record

Insight ID: INS-0050
Project: MAP
Related task: TASK-083
Detected by: claude-lab-nora
Date: 2026-07-27
Status: RAW

## Short description


- obs: emergence_sentinel.py's repeated_blocker signal miscounts operational-log noise from infrastructure tasks as if the task's own progress were blocked

## Trigger


- src: TASK-083 (the reconciliation/liveness system) showed 54 BLOCKED events, but every one is a routine 'presumed down, probing' log entry about OTHER agents that the system TASK-083 built emits as part of its normal function, not TASK-083's own progress being blocked.

## The synthesis


- synth: The repeated_blocker heuristic counts any BLOCKED-type event sharing a task_id, but a task that builds a monitoring/logging system will legitimately emit many BLOCKED events under its own task_id forever after release, since those events describe what the system it built is observing, not the task's own state. This produces a permanent false-positive outlier (54 vs. the next-highest count of 4) that a curator has to manually recognize and dismiss every scan cycle unless it is deduplicated once.

## Why it might matter


- why: First curation pass on the sentinel's backlog (12 candidates, none previously curated since 2026-07-18/23) found this as the single largest false positive. Left uncorrected, it will keep resurfacing on every future scan and erode trust in the queue -- the same 'the system isn't actually working' problem the sentinel exists to prevent.

## Evidence


- ev: MAP_System/events/events.jsonl entries for TASK-083, all type=BLOCKED, summary pattern 'RnS: TBD presumed down...' or 'giving up on TBD after 6 probes'.

## Risk


- risk: Acting without promotion could bypass HPOM governance.

## Scope


- scope: Any task whose deliverable is itself a system that emits BLOCKED-type events (liveness/reconciliation, watchers, sentinels) will trip this heuristic permanently.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
