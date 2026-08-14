# Insight Record

Insight ID: INS-0051
Project: MAP
Related task: TASK-189
Detected by: claude-lab-nora
Date: 2026-07-27
Status: LINKED

## Short description


- obs: Non-core-agent workers (visible helpers, Haiku agents, local Pi models) fail silently instead of erroring, and this has recurred across at least three separate incidents

## Trigger


- src: TASK-189 (2026-07-15) hit review routing exhaustion: helper 'lore' stopped without responding, then three more workers (Mira, Toku, Zero) idled on broadcast review requests without responding, forcing an operator decision. Same conversation, 2026-07-27: Pi-served local models (qwen3.5:9b, qwen2.5-coder:7b-16k) twice displayed correct-looking terminal output but never sent the required hcom event, and a fresh Pi session stalled mid-task with no output for 40+ seconds. Separately this session: Haiku Claude agents cannot run in auto mode, so they silently block on permission prompts with no error, just an idle pane, until someone notices and manually approves (see [[haiku-agents-need-no-approval-tasks]]).

## The synthesis


- synth: Three different worker types (tier-2 visible helpers, Haiku Claude agents, Pi-served local models) share one failure shape: when they cannot complete a bounded task, they do not produce a visible error or timeout signal a coordinator can detect mechanically -- they just stop being responsive, indistinguishable at a glance from 'still working.' The coordinator (core agent or operator) only discovers the failure by manually polling status/screen state, same as this session's context-rotation ack, which needed direct hcom term inspection to catch a stuck/malformed Pi response. There is no standing timeout+escalation mechanism for a dispatched helper/local-model/subagent request the way there is for task leases (lease_expires_at, liveness_reaper).

## Why it might matter


- why: This is the third occurrence of the same failure shape in the durable record (TASK-189 review routing, the 2026-07-18 Pi requalification trials, and today's renewed Pi trials plus the Haiku-approval finding), which [[SELF_REPAIR_SYSTEM]]'s Follow-up Prevention rule treats as a threshold: 'a third recurrence without a prevention proposal is itself a process gap worth raising to command-center.'

## Evidence


- ev: MAP_System/events/events.jsonl TASK-189 BLOCKED events 2026-07-15T01:40:12Z, 01:41:50Z; [[artifacts/experiments/pi-local-capability-trial-2026-07-18]] Trials C/D and 2026-07-27 Trials E-G; memory haiku-agents-need-no-approval-tasks.md.

## Risk


- risk: A generic timeout+escalation layer for non-core-agent dispatch (analogous to lease_expires_at + liveness_reaper for tasks) would need to distinguish 'still working, slow' from 'stuck/failed' without false-positive interrupting a genuinely slow-but-progressing local model.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [x] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:

## Resolution (2026-07-27, claude-lab-nora)

Promoted to IDEA-0030 (bounded liveness/no-progress signal for hcom-dispatched
non-core workers, `test` recommendation — Pi-only pilot, not a standing role).
Not implemented directly: this is a real architectural change to how MAP
observes dispatch, and IDEA-0013 was parked twice already for proposing a
similarly-shaped standing role with unbounded scope. Goes through the normal
idea-approval path instead of ad hoc implementation.
