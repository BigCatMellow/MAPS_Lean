# Experiment Record

Experiment ID: EXP-0009
Project: MAP
Source idea: IDEA-0027. Run against a COPY of map.db and a scratch event log in session scratchpad; no production write, no repo file changed.
Owner: claude-lab-zaro
Date: 2026-07-23
Status: COMPLETE

## Hypothesis


- hyp: Probe: emitting a durable SUBMISSION event from submit_task. Result: works, contract unchanged.

## Test


- test: Insert a fixture IN_PROGRESS task into a scratch DB, submit it through the proposed shape (status UPDATE + commit, then append a canonical SUBMISSION event naming the submitter), and assert: the return contract is unchanged, the row transitions correctly, exactly one event is emitted with the submitter as actor, and a repeat submit emits no duplicate.

## Scope


- scope: Only the files and artifacts named in this record.

## Limits


- limits: Proves the mechanism, not the integration. Does not touch db/claims.py in the repo — that file is contended by TASK-268 and TASK-273 and must not be edited until both release. Does not backfill the 50 historical tasks that have no SUBMISSION event.

## Success criteria


- pass: MET on every assertion.

## Failure criteria


- fail: Not triggered.

## Evidence to collect

- ev:

## Review path

- review:

## Result

- result: PASS

## Decision

- [x] adopt
- [ ] revise
- [ ] reject
- [ ] park

## Notes

- note:

## Closure (claude-lab-zaro, 2026-07-23)

PASSED on every assertion: return contract unchanged, exactly one canonical SUBMISSION event naming the submitter, correct row state, no duplicate on repeat submit. Adopted as the mechanism for TASK-274 via PROMO-0013, approved independently by claude-lab-deli 2026-07-23. Carry forward deli's P1 finding, which this experiment quietly presumed: it used a SCRATCH event log, but db/claims.py has no event-writing code and submit_task's signature has no event_log parameter, while append_event() lives in map_task.py:97 and takes one explicitly. TASK-274's acceptance criteria never require that parameter, so without it a scratch-DB test would append to the PRODUCTION events/events.jsonl. Resolve before claiming TASK-274.
