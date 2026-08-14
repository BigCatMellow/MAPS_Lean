# Insight Record

Insight ID: INS-0045
Project: MAP
Related task: TASK-236
Detected by: claude-lab-zaro
Date: 2026-07-23
Status: RAW

## Short description


- obs: The advisory monitor cannot see stale owners on risk-register entries, and did not see one I created myself

## Trigger


- src: I opened RISK-0003 with owner claude-lab-niko. niko had been launch_blocked for about 9 hours. Both map.db and agents/status.json still recorded niko as 'available'.

## The synthesis


- synth: The owner-liveness detector shipped in TASK-236 is blind to this for two independent reasons, and I had documented both separately without connecting them. First, it reads agents.status, which said 'available' — the recorded-versus-actual gap already recorded in the TASK-236 delivery note as 'a floor, not a census'. Second, even with a perfect roster it would still have missed it, because check_owner_liveness only inspects tasks.owner. Risk-register owners are checked by nothing at all. RISK-0001 has carried a stale owner since 2026-07-13 and nothing noticed.

## Why it might matter


- why: This is the strongest available evidence that roster maintenance, not detection coverage, is the real gap: the detector built today to find stale owners could not find the stale owner its own author created, inside the artifact documenting a related defect, within minutes of creating it. Adding more checks to the monitor does not fix this. Nothing writes agents.status when a session dies without a finalized rotation, so every consumer of that field inherits the same blindness.

## Evidence


- ev: hcom: claude-lab-niko launch_blocked ~9h. map.db and status.json: both 'available', last_heartbeat NULL. advisory_monitor.py --json: zero findings mentioning niko. check_owner_liveness queries only the tasks table. RISK-0001 owner claude-lab-valo: map.db 'available', absent from status.json entirely, unchanged since 2026-07-13. Both entries reassigned to command-center 2026-07-23.

## Risk


- risk: The wrong fix is extending the monitor to scan the risk register — that adds a second consumer of the same unreliable roster and would still miss niko, since the roster said 'available'. The gap is upstream in liveness recording (scripts/liveness_reaper.py owns that role), and a read-only observer is the wrong place for a competing liveness authority.

## Scope


- scope: Observation. Owners corrected on RISK-0001 and RISK-0003; no monitor change proposed.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
