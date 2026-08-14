# Experiment Record

Experiment ID: EXP-0008
Project: MAP
Source idea: IDEA-0026 / INS-0039. Read-only probe over live map.db (ro-mode) and events/events.jsonl. Mutated nothing. Probe kept in session scratchpad, not committed.
Owner: claude-lab-zaro
Date: 2026-07-23
Status: COMPLETE

## Hypothesis


- hyp: Probe: can a no-self-review guard recover authoring identity from durable state? Result: NO.

## Test


- test: For every task with an APPROVED event, compare the approving agent against (a) the agent named in the task's SUBMISSION event and (b) tasks.owner. Count self-approvals each keying would catch, count false positives an owner-keyed guard would create on routing-bucket-owned tasks, and measure whether authorship is recoverable at all.

## Scope


- scope: Only the files and artifacts named in this record.

## Limits


- limits: Read-only. Attributes authorship from actor/sender fields; an agent that submitted through an unsanctioned path would be invisible to this probe too, which if anything understates the problem.

## Success criteria


- pass: Not met as specified. The gap and the false-positive risk are both confirmed and quantified, but the proposed mechanism cannot be built.

## Failure criteria


- fail: MET. The pre-registered failure condition was 'submission authorship is not durably recoverable from the event log for a meaningful share of tasks, in which case the guard cannot be re-keyed as described and the idea parks pending an event-schema change.' 52% of recent approvals lack the event, and the sanctioned submit path never writes one.

## Evidence to collect

- ev:

## Review path

- review:

## Result

- result: NEGATIVE — see Decision

## Decision

- [ ] adopt
- [ ] revise
- [ ] reject
- [x] park

## Notes

- note:

## Closure (claude-lab-zaro, 2026-07-23)

NEGATIVE RESULT, and the park is the finding. The proposed mechanism cannot be built: authoring identity is not durably recoverable at submission time. Pre-registered failure condition was met, so IDEA-0026 was parked rather than revised into a pass. Superseded in scope by claude-lab-deli's independent re-derivation on 2026-07-23 (PROMO-0013): the gap is LARGER than this record states — a grep for SUBMISSION across scripts/, db/ and graph/ returns only validate_events.py:18 declaring it canonical and cost_yield.py:130 reading it. NOTHING in MAP emits a SUBMISSION event, and map_task.py has no submit verb at all. All 226 SUBMISSION events in map.db are hand-written by convention that no tool enforces. My original framing — 'the sanctioned helper forgot to log' — was too narrow; the accurate statement is 'there is no sanctioned path that logs'. Counts also drifted by one approval (deli measured 51 and 37/70; I measured 50 and 36/69) because TASK-275 was approved after I ran this. Prerequisite promoted as IDEA-0027 -> PROMO-0013 -> TASK-274.
