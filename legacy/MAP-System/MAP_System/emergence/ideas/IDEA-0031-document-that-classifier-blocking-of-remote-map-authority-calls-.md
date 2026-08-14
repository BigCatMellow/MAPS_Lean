# Idea Card

Idea ID: IDEA-0031
Project: MAP
Source insight or synthesis: INS-0054
Owner: claude-lab-muza
Date: 2026-07-29
Status: PROMOTED_TO_TASK

## Idea


- idea: Document that classifier blocking of remote map-authority calls is a distinct risk from the raw-SQL case TASK-293 fixed

## Problem or opportunity


- gap: Sanctioned CLI verbs that call map_authority.py's remote_request (register-agent, rotation-transfer, rotation-restore, claim-review against RUKI) can be classifier-blocked even though they are already the correct, audited, non-raw-SQL path. TASK-293 only documented/fixed the raw-SQL case.

## Why now


- now: Directly evidenced by this session's context-rotation ack failure (2026-07-29), not hypothetical.

## Expected benefit


- gain: The next agent hitting a classifier block on one of these remote calls will know it is a known, distinct gap rather than assuming TASK-293's fix already covers it, and can report the exact stderr/exit code instead of retrying blindly.

## Cost


- cost: One paragraph added to [[AGENTS]]'s authority/rotation section; no code or policy change.

## Reversibility

- [x] yes
- [ ] no
- [ ] partial: TBD

## Smallest safe experiment


- test: Create and validate file-backed emergence records.

## Decision needed

- [ ] task-DRI
- [ ] review-DRI
- [ ] state-steward
- [ ] project-DRI
- [x] human-owner

## Recommendation

- [ ] park
- [ ] reject
- [ ] test
- [x] promote-task
