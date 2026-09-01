# PR #234 review evidence — `maps flow release-check` design note

reviewer: maps-lean-nava
head_sha: 4ef99e3d80a72a61556314cac524f5bccc2b7615
independent: true
summary: APPROVE — verification-only review of a single design/scoping note; both cited dormant evaluators (evaluate_acquisition_evidence, evaluate_benchmark_results) exist at the cited lines with zero production callers, all seven other primitive citations check against merged code, the four §6 OPERATOR DECISIONs are genuine operator-only calls (two schema, two authority) left unresolved, and the note ends PARKED with a Resume prompt that covers both the decisions-made and decisions-not-made branches.

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Both cited dormant evaluators exist with zero prod callers | PASS. `evaluate_acquisition_evidence` — `runtime/acquisition_evidence.py:242`. `evaluate_benchmark_results` — `runtime/benchmark_results.py:406`. `/usr/bin/grep -rn "evaluate_acquisition_evidence\|evaluate_benchmark_results" runtime/ --include=*.py` filtered to non-test, non-defining-module callers → NONE. Both are dormant pure evaluators, exactly as §1b/§1c claim. |
| 2 | The 4 §6 OPERATOR DECISIONs are genuinely operator-only | PASS. (1) summary sink — no existing `release_check*` in `schema.sql`; the three options differ in structure/timing/audit model, recommended option is a schema change → operator sign-off. (2) evaluator-report persistence — same durable-state/schema axis. (3) advisory vs blocking — option (b) adds a new precondition gate to `_validate_review_approval_conn`, an authority-model change → operator-only. (4) who may run the flow — authority/capability question tied to (3). None resolvable by technical judgment; note recommends but does not decide; §7 open questions kept separate. |
| 3 | Note ends PARKED with a Resume prompt covering both branches | PASS. §8 verdict: NOT dispatchable — stays PARKED pending §6. Resume prompt has both branches explicit (decisions not made → surface to operator, do not implement; decisions made → implement per §3, `runtime/flow_release_check.py`) with MUST-NOT and a rule-14 re-verify instruction. |
| — | Boundaries honored; diff scope | PASS. `git show --stat HEAD` = 1 file, `work/notes/2026-09-01-6.21-release-design.md` (+366). No `runtime/`, no `tests/`, no `CAPABILITY_CHECKLIST.md` (6.21 row untouched). |
| — | Other primitive citations (rule 14) | PASS. `common.py:11` `VALID_REVIEW` incl. `OPERATOR_VISIBLE_RELEASE_CHECK`; `review_binding.py:62` `_requires_bound_subject_conn`; `git_scope.py:159` `verify_git_run`; `outcomes.py:31` `record_outcome`; `review.py:112` `summary` param of `record_review`. |

## Non-blocking

- The note recommends a specific answer for each §6 decision — framed as recommendations, not resolutions. Correct for a design note; coordinator carries §6 to the operator as a decision batch.
- Design-only PR, no code — no tests/smoke required per the session-17 contention protocol.

## Verdict

APPROVE.
