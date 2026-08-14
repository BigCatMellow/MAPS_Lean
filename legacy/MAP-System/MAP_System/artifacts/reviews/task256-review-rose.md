# Review: TASK-256 Pilot token-budgeted task-fingerprint retrieval with a fresh helper

task_id: TASK-256
reviewer: claude-lab-rose
task_owner: codex-lab-kiri

## Verdict

APPROVED

A genuine, honestly-reported experiment. The truth set was frozen before the
helper was exposed to anything, the measured numbers reproduce, and the
conclusion ("continue experimenting; do not integrate") is more conservative
than the topline recall number alone would justify — the report actively
surfaces its own negative result (source-evidence ranking) instead of
burying it under the strong task-recall number.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| Corpus, frozen queries, expected sources, scoring method, and token budget recorded before the evaluator saw the packet. | PASS | `task-fingerprint-index-pilot-queries-2026-07-19.json` has `frozen_at: 2026-07-19T13:45:00-04:00`, 37 `corpus_task_ids`, explicit `scoring` and `retrieval_contract` fields. File mtimes confirm ordering: queries file 13:49:23, helper packet + generated index 13:52:18 (both after freeze). |
| Compact fingerprints link to resolvable primary evidence; pilot is disposable, not authority. | PASS | Report §7: "All 16 frozen expected source paths resolved." Report is explicit that the design is a "disposable projection" (task description) and §10 explicitly withholds integration. |
| A fresh visible helper evaluates the compact index without broad repository search, writes nothing, reports uncertainty and source expansions, monitored through hcom. | PASS | `inbox/helpers/helper-index-neko-2026-07-19.md` bounds the helper to packet-only reads, no writes, no repo search. Report §6 states terminal/events showed only `cat`/bounded `sed` on the packet and the three authorized confirmation reads — no repo search, index read, or writes. hcom events 6894 (packet delivered), 6915 (initial report), 6946 (confirmation) cited as evidence, not just asserted. |
| Final report measures recall, precision/usefulness, discovery size, source-expansion choices, latency, stale/broken references, and limitations including negative results. | PASS | §3 (task recall/precision tables), §3.3 (missing best-evidence paths — the negative result), §4 (token/size), §6 (98s latency), §7 (staleness: TASK-237's unresolved paths), §8 (six explicit limitations, e.g. designer bias, curated subset, strong-model-only evaluator). |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Integrating the prototype into startup, MAP routing, the Command Center, or external services | NOT BROKEN — no references to startup, `graph/runner.py`, or Command Center integration in `task_fingerprint_pilot.py`; the script is a standalone experiment script only invoked by its own test suite. |

## Files Reviewed

- `MAP_System/artifacts/experiments/task-fingerprint-index-pilot-2026-07-19.md` (full)
- `MAP_System/artifacts/experiments/task-fingerprint-index-pilot-queries-2026-07-19.json` (frozen truth set)
- `MAP_System/inbox/helpers/helper-index-neko-2026-07-19.md`
- `MAP_System/scripts/task_fingerprint_pilot.py`, `MAP_System/tests/test_task_fingerprint_pilot.py`

## Verification

- `python -m py_compile MAP_System/scripts/task_fingerprint_pilot.py MAP_System/tests/test_task_fingerprint_pilot.py` — passes.
- `python -m unittest MAP_System.tests.test_task_fingerprint_pilot -v` — 5/5 passed, matching the report's claimed verification.
- Cross-checked queries JSON `frozen_at` and file mtimes against the report's claim that the truth set predates helper exposure — confirmed order: freeze (13:45) → queries file written (13:49) → packet/index generated (13:52).
- Spot-checked Q1 in the queries file against report §3.2: `expected_task_ids: [TASK-211, TASK-213]`, matches reported "2/2 exact expected sources" row.
- Report's central claim (100% recall@6, 68.75% source recall) is stated as an upper-bound, curated-corpus result, not a general capability claim — matches how the report itself frames it in §8. No claim of readiness for integration is made; §10 explicitly says the opposite.

## Notes

No blocking findings. This is the first task in the TASK-256→262 retrieval
chain; later tasks are expected to build on and in places supersede this
one's design (typed evidence ranking, uncurated holdout, etc., all flagged
here in §9 as follow-on work already scoped by this report).
