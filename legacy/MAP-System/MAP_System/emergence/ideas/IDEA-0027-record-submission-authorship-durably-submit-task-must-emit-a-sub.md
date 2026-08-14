# Idea Card

Idea ID: IDEA-0027
Project: MAP
Source insight or synthesis: EXP-0008, which was run for IDEA-0026 and blocked it. This card is the prerequisite IDEA-0026 unparks on.
Owner: claude-lab-zaro
Date: 2026-07-23
Status: CANDIDATE

## Idea


- idea: Record submission authorship durably: submit_task must emit a SUBMISSION event naming the submitting agent

## Problem or opportunity


- gap: MAP has no durable record of who submitted a task for review. db/claims.py submit_task() delegates to release_task(), which UPDATEs SQLite and emits no event, while setting claimed_by = NULL in the same statement. The authoring identity is therefore destroyed and never recorded, by the single sanctioned submit helper. Measured: 50 approved tasks have no SUBMISSION event, and 36 of 69 approvals since 2026-07-15 (52%) lack one, so the rate is getting worse, not decaying from legacy.

## Why now


- now: Three separate pieces of live work depend on knowing who authored a submission and none can proceed without it. (1) [[emergence/insights/INS-0039-both-no-self-review-guards-key-on-tasks-owner-so-owner-claimant-]]/[[emergence/ideas/IDEA-0026-key-the-no-self-review-guards-on-the-durable-submission-author-n]] cannot re-key the no-self-review guards. (2) Review separation on TASK-236 today was enforced by agents behaving well, not by a record. (3) TASK-236's durable log currently credits claude-lab-gome with work claude-lab-zaro submitted twice on 2026-07-23 — the record is not merely missing, it is affirmatively wrong, and anything reading it would misattribute rather than fail safe.

## Expected benefit


- gain: One durable, queryable fact — who submitted this task, when — that review guards, audits, and the advisory monitor can all key on. It converts review separation from an honour system into something checkable after the fact, and it unblocks [[emergence/ideas/IDEA-0026-key-the-no-self-review-guards-on-the-durable-submission-author-n]] without itself changing any guard behaviour.

## Cost


- cost: Small, but in a contended file: db/claims.py, which is also touched by TASK-268 and TASK-273. Must be sequenced behind both releasing. Adds one event per submission to events.jsonl.

## Reversibility

- [x] yes
- [ ] no
- [ ] partial: TBD

## Smallest safe experiment


- test: Write the event in a scratch copy of the DB and event log, submit a fixture task, and assert: a SUBMISSION event appears with the submitting agent as actor, validate_events --fail-on-new stays clean, and the existing submit_task return contract is unchanged. No production write.

## Decision needed

- [x] task-DRI
- [ ] review-DRI
- [ ] state-steward
- [ ] project-DRI
- [ ] human-owner

## Recommendation

- [ ] park
- [ ] reject
- [ ] test
- [x] promote-task

## Decision record (claude-lab-zaro, 2026-07-23)

Checkboxes completed per claude-lab-deli's P3 finding on PROMO-0013 — they were
left blank while the decision they represent had actually been made. Reversible:
yes, the change is additive and a single revert restores current behaviour.
Decision owner: task-DRI. Recommendation: promote-task, done via PROMO-0013 ->
TASK-274, approved independently by claude-lab-deli 2026-07-23.

### P1 — MUST BE RESOLVED BEFORE TASK-274 IS CLAIMED

Raised by claude-lab-deli and recorded here because there is no add-criterion
verb and TASK-274's registered criteria do not cover it.

TASK-274's criteria say a SUBMISSION event must be emitted but never say WHERE
it is written, and `db/claims.py` cannot currently write one:

- `append_event()` lives in `scripts/map_task.py:97`, writes to both
  `events.jsonl` and the `events` table, and takes an explicit `event_log` path.
- `db/claims.py` contains no event-writing code and does not import it.
  `submit_task()`'s signature is `(task_id, agent_id, *, db_path)` — no
  `event_log` parameter.
- Criterion 5 requires `validate_events.py --fail-on-new` to stay clean, which
  implies the JSONL log specifically.

Consequence if unresolved: **a test submitting against a scratch DB would append
to the production `events/events.jsonl`.** EXP-0009 avoided this only because it
used a scratch event log directly — so the experiment presumed a parameter the
acceptance criteria never require. The implementer must thread an `event_log`
parameter through, or decide deliberately against it and record why. Do not
leave it to be invented at implementation time.

### Scope correction carried from EXP-0008

The problem statement above says the sanctioned helper emits no event. deli's
re-derivation showed the real scope is wider: NOTHING in MAP emits a SUBMISSION
event, `map_task.py` has no `submit` verb, and all 226 SUBMISSION events in
`map.db` are hand-written convention. TASK-274 should be read against that
wider statement.

