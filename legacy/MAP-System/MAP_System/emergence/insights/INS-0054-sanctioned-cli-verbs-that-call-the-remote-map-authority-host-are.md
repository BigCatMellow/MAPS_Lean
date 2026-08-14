# Insight Record

Insight ID: INS-0054
Project: MAP
Related task: NONE
Detected by: claude-lab-muza
Date: 2026-07-29
Status: PROMOTED

## Short description


- obs: Sanctioned CLI verbs that call the remote map-authority host are not exempt from classifier blocking; TASK-293's fix does not cover them

## Trigger


- src: Created from command-center emergence capture.

## The synthesis


- synth: TASK-293 fixed classifier blocking for raw-SQL mutations by building a sanctioned CLI verb (extend-attempts). But map_authority.py register-agent is already a sanctioned, mirror-synced verb and still got blocked, because the trigger here is crossing to a remote host over SSH, not raw-SQL-vs-CLI. The two risk shapes are conflated under one classifier policy and one prior fix.

## Why it might matter


- why: DEC-035 already documents that auto mode is not blanket approval and the classifier still blocks unmediated mutations of canonical state; this is a second, distinct instance (remote-authority network call, not local SQL) that the TASK-293 fix does not address, so the next agent hitting it may wrongly assume it is already solved.

## Evidence


- ev: hcom thread with claude-lab-nene, 2026-07-29 (context-rotation ack blocked); [[shared/decisions]] DEC-035 closing paragraph; MAP_System/tasks/TASK-293.json (scope explicitly SQLite-only).

## Risk


- risk: Low: documentation-only proposed fix, no implementation or policy change made by this record itself.

## Scope


- scope: Any sanctioned MAP CLI verb that calls out to the remote authority host (map_authority.py's ssh path): register-agent, rotation-transfer, rotation-restore, claim-review against RUKI.

## Recommended next action

- [ ] ignore
- [ ] park
- [x] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note: Promoted through IDEA-0031 and PROMO-0015 for documentation-only
  handling. The promotion explicitly rejects classifier exemptions and
  automatic retry of policy denials.
