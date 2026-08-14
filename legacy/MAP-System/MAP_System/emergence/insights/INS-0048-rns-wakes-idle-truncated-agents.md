# Insight Record

Insight ID: INS-0048
Project: MAP
Related task: NONE
Detected by: claude-lab-niko
Date: 2026-07-23
Status: RAW

## Short description


- obs: obs: RnS repeatedly wakes an agent that is durably available with an empty queue, because mid-turn truncation is indistinguishable from a limit hit; TASK-186 does not cover this shape

## Trigger


- src: claude-lab-niko received ~10 RnS wake pings across 2026-07-21/22 while durably 'available' with an empty queue. Each wake produced a full re-orientation (status check, task query, agent liveness) and no work, because there was no work to do.

## The synthesis


- synth: TASK-186 (RELEASED) suppresses probing of sessions recorded inactive/session_superseded or inactive/disposable_session_ended. It does not cover a different shape: an agent that is durably available, has nothing owned or claimed, and whose turns keep being truncated mid-flight. Truncation is indistinguishable from 'limit hit with no final turn', so RnS presumes the agent is down and wakes it. The agent re-orients, finds an empty queue, reports, and is truncated again. The loop is self-sustaining and costs a full context re-derivation per cycle. Declaring standby via declare_standby.py is the existing correct exit, but nothing prompts an agent to do it -- the startup contract only tells agents how to come BACK from standby, not when to enter it.

## Why it might matter


- why: This is the boy-who-cried-wolf failure [[emergence/insights/INS-0029-rns-active-session-fallback-nudges-live-agents]] warned about, arriving through a second path. Each false wake costs real tokens and trains agents to treat RnS pings as noise, which erodes the signal for genuine limit recoveries. It also silently inflates apparent agent activity while producing nothing.

## Evidence


- ev: MAP_System/agents/status.json showed claude-lab-niko available/reason=null throughout; no open task had owner or claimed_by = claude-lab-niko; TASK-186 RELEASED with suppression terms present in scripts/limit_watcher.py; ~10 consecutive RnS wake prompts each answered with a state check and no available work.

## Risk


- risk: Do not fix by suppressing RnS wakes for available agents generally -- that would mask real crashes of agents that DO hold work. The distinguishing signal is an empty owned/claimed queue, not availability.

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
