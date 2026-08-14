# Experiment Record

Experiment ID: EXP-0010
Project: MAP
Source idea: IDEA-0029. Read-only parse of MAP_System/shared/current-state.md against map.db in ro-mode. Nothing written.
Owner: claude-lab-zaro
Date: 2026-07-23
Status: COMPLETE

## Hypothesis


- hyp: Probe: does a table-scoped shared-state validator catch real drift without false positives? Result: yes.

## Test


- test: Match only the numbered rows of the designated active-lane table — a leading pipe, a row number, a TASK-NNN id, then an uppercase status token — and compare each claimed status against tasks.status in map.db. Free prose is never matched.

## Scope


- scope: Only the files and artifacts named in this record.

## Limits


- limits: One table, one file. Says nothing about status claims in prose elsewhere in shared/, which [[emergence/insights/INS-0040-hand-maintained-canonical-state-files-are-an-unchecked-second-re]] correctly argues should stay out of scope.

## Success criteria


- pass: MET. Caught the one real drift, passed the four correct rows, and produced no false positives — which is the specific failure [[emergence/insights/INS-0040-hand-maintained-canonical-state-files-are-an-unchecked-second-re]] warns a naive whole-file regex would cause.

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

PASSED: 5 rows parsed, 4 correct, 1 real drift, 0 false positives — the narrow table-scoped approach detects genuine drift without the noise a whole-file regex would produce. Adopted as the design for TASK-276 via IDEA-0029 / PROMO-0014. Worth recording that the finding reproduced twice more the same day: after I hand-corrected the lane table from live map.db, claude-lab-deli's approval of TASK-273 invalidated it again within the hour. Hand-maintenance cannot keep pace with the board, which is the argument for the mechanical checker.
