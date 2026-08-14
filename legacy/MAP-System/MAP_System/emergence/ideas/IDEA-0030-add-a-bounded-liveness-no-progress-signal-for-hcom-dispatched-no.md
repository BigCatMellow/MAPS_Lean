# Idea Card

Idea ID: IDEA-0030
Project: MAP
Source insight or synthesis: INS-0051
Owner: claude-lab-nora
Date: 2026-07-27
Status: CANDIDATE

## Idea


- idea: Add a bounded liveness/no-progress signal for hcom-dispatched non-core workers (helpers, Haiku agents, local Pi models), mirroring the lease_expires_at + liveness_reaper pattern MAP already uses for tasks -- starting as a narrow observability pilot, not a new standing role

## Problem or opportunity


- gap: Non-core dispatched workers fail silently instead of erroring: no mechanical signal distinguishes 'still working' from 'stuck/failed'. A coordinator only discovers it by manually polling hcom list/term. This recurred three times: TASK-189 review-routing exhaustion (2026-07-15), the 2026-07-18 Pi requalification trials, and this session's renewed Pi trials plus a separate Haiku-approval-blocking finding (2026-07-27).

## Why now


- now: Third occurrence per [[SELF_REPAIR_SYSTEM]]'s own Follow-up Prevention rule ('a third recurrence without a prevention proposal is itself a process gap'). This session alone needed 6+ manual hcom term/list checks to catch two separately stuck Pi sessions live, each costing real turns to diagnose.

## Expected benefit


- gain: A coordinator gets a mechanical 'this dispatch has produced no progress signal in N' flag instead of needing to remember to poll -- same value liveness_reaper already provides for task claims, extended to the dispatch layer.

## Cost


- cost: Real false-positive risk: local model generation speed varies enormously (today's qwen2.5-coder:7b-16k vs qwen3.5:4b showed very different latencies), so a fixed wall-clock timeout would wrongly flag a genuinely-working-but-slow session. Needs a no-progress-signal definition (e.g. no new hcom status event AND no terminal output change), not a naive timer. Also: [[emergence/ideas/IDEA-0013-add-an-idea-scouting-role-a-role-cadence-responsible-for-activel]] was parked twice already for proposing a standing watcher role with unbounded scope -- this must stay a narrow, bounded mechanism on one dispatch surface, not repeat that mistake.

## Reversibility

- [x] yes — read-only observation; does not change dispatch behavior or force any action on a flagged session
- [ ] no
- [ ] partial: TBD

## Smallest safe experiment


- test: Read-only advisory only, no auto-kill/auto-escalate: a small script polling hcom list/events for one dispatch surface (Pi/local-model sessions, the freshest evidence) that flags 'no status-event or terminal-output change in N seconds' and surfaces it the same way emergence_sentinel's queue now surfaces in graph/runner.py -- visible on a routine check, not a new autonomous role. Run it as a pilot on Pi sessions only before considering Haiku/helper dispatch.

## Decision needed

- [ ] task-DRI
- [ ] review-DRI
- [ ] state-steward
- [x] project-DRI — changes how MAP observes non-core dispatch system-wide, but does not change authority/policy, so it stops short of human-owner
- [ ] human-owner

## Recommendation

- [ ] park
- [ ] reject
- [x] test — run the bounded Pi-only pilot from "Smallest safe experiment" before considering promotion to a task; do not skip straight to promote-task given IDEA-0013's twice-parked history for this exact standing-role shape
- [ ] promote-task
