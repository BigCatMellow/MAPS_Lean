# Insight Record

Insight ID: INS-0042
Project: MAP
Related task: TASK-274
Detected by: claude-lab-zaro
Date: 2026-07-23
Status: RAW

## Short description


- obs: Output paths are write-once with no unregister verb, so a mis-registered path is stuck until the task goes terminal

## Trigger


- src: I created TASK-274 with MAP_System/db/claims.py registered as an output path while TASK-273 (SUBMITTED) already owned it. validate_task_graph immediately began failing with 'Output path collision: MAP_System/db/claims.py owned by TASK-273 and TASK-274', a repo-global validator break caused by a single create call.

## The synthesis


- synth: tasks.output_paths has exactly the write-once defect that TASK-273 exists to fix for tasks.owner. map_task.py exposes add-output-path but no remove; there is no retire verb and no set-status verb, and [[AGENTS]] forbids hand-editing SQLite. So a path registered in error, or registered prematurely on a contended file, cannot be withdrawn by any sanctioned means. The only exits are to wait for the task to reach a terminal status or to abandon the task, and neither is a repair. This is the same shape as [[INS-0039]] and the stale-owner problem: a field that is load-bearing for a mechanical gate can only be written, never corrected.

## Why it might matter


- why: The collision check in validate_task_graph.py skips tasks in terminal|BLOCKED status, so a mis-registered path breaks a global validator for every agent until the owning task goes terminal. That creates a second-order hazard which actually occurred here: I was asked to review TASK-273, and because the collision clears the moment TASK-273 reaches APPROVED, my own broken state gave me a direct interest in approving the task I was judging. A write-once field thus manufactured a conflict of interest out of a clerical mistake. I disclosed and recused (hcom #13282); mubo chose to route the review elsewhere.

## Evidence


- ev: 1) map_task.py --help subcommand list: create, approve, reject, rework, release, recover-orphan, add-output-path, show, log — add only, no remove, no retire, no set-status. 2) validate_task_graph.py lines 107-116: active_outputs skips only status in terminal|{BLOCKED}, where terminal = {DONE, APPROVED, RELEASED, RETIRED}. 3) Live: validate_task_graph fails on TASK-273/TASK-274 sharing MAP_System/db/claims.py. 4) TASK-273 is itself the sanctioned reassign-owner verb, added because tasks.owner was write-once — the identical defect, already recognised for a different column.

## Risk


- risk: A naive fix is dangerous: a remove-output-path verb that anyone can call would let an agent quietly narrow its own registered scope after the fact, which is worse than the current rigidity — registered output paths are part of what a reviewer checks work against. Any verb needs --actor and --reason, must append a durable event naming the removed path, and should probably refuse once the task has been submitted at least once.

## Scope


- scope: Observation only. No verb proposed, no task created, nothing promoted.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
