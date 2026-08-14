# E/I Sentinel Pilot — TASK-224

- Date: 2026-07-17
- Owner: codex-lab-lilo
- Experiment: EXP-0002
- Status: IMPLEMENTED, NOT YET ADOPTED

## Result

The deterministic scan processed the canonical MAP event stream in 12.75 ms
and created seven deduplicated, non-promoted candidates:

- five repeated-rework candidates: TASK-103, 141, 158, 206, 207;
- two repeated-blocker candidates: TASK-083 and TASK-189.

A second scan created zero duplicates. Every candidate contains a signal type,
subject, evidence line references, stable deduplication key, detection time,
and empty curation fields. The state file exposes last run, last success,
errors, runtime, queue totals, and stop-request state for Command Center.

## Retrospective recall

Known recent insights used as the small truth set:

| Insight | Underlying signal found? | Note |
|---|---:|---|
| INS-0024, extraction parity gate | Yes | TASK-207 repeated review failures were detected. |
| INS-0025, undo hidden-information exploit | No | TASK-213 did not produce repeated blocker/rework events. |
| INS-0026, decomposition creates engine seam | No | This was a positive architectural discovery, not a failure transition. |
| INS-0027, notes do not become behavior | No | The decisive evidence was operator correction and helper behavior, not encoded as a typed durable signal. |

Recall is **1/4 (25%)**, below EXP-0002's proposed 3/4 target. This is a useful
failure: task-transition heuristics detect recurring delivery friction but
cannot discover positive design insights or operator corrections that are not
represented in approved durable sources. The pilot must not claim general E/I
coverage yet.

## Noise and duplicates

- Raw candidates: 7.
- Exact duplicate candidates on rerun: 0.
- Human useful-candidate rate: not yet adjudicated; all remain `new` for a
  visible curator.
- The 54 BLOCKED events attached to TASK-083 show why counts need semantic
  curation: they may represent repeated watcher telemetry rather than 54
  distinct systemic failures.

## Safety verification

- The scanner reads only `events/events.jsonl` in this increment.
- It does not read raw hcom or model transcripts.
- It never invokes a model.
- It never creates Insights, Ideas, tasks, decisions, or policy.
- Curation records actor, reason, timestamp, and optional resolution reference.
- Model-backed curation is governed by the visible-agent rule in `AGENTS.md`.

## Tests

`python3 -m unittest MAP_System.tests.test_emergence_sentinel -v`: 3/3 passed.

The tests cover repeated-signal detection, idempotent deduplication,
non-promotion, and attributable visible curation.

### Review remediation

Command Center now contains a dedicated visible E/I Sentinel card with status,
last-run time, candidate totals, runtime/errors, and Scan now / Stop / Resume
controls. While Command Center is open, a deterministic scan runs every 30
minutes. Stop is persisted in sentinel state and blocks both scheduled and
manual scans until explicit Resume. The documented curation command now
includes its required `--actor`, and a CLI-level test executes that path.

## Next experiment boundary

Do not silently expand into raw transcripts. Improve recall using approved
durable sources first: review artifacts, incident records, operator-intake
events with explicit correction markers, and project-local event streams.
Measure candidate usefulness and privacy impact per source. The visible MAP
Steward may summarize queued candidates, but cannot promote them automatically.
