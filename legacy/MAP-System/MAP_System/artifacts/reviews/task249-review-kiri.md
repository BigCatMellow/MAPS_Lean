# Independent Review: TASK-249

- task_id: TASK-249
- reviewer: codex-lab-kiri
- verdict: APPROVED
- reviewed_at: 2026-07-19

## Verdict

APPROVED. The negation-aware classifier change satisfies all acceptance
criteria while preserving the approval gate for genuine destructive intent.

## Scope

Reviewed `MAP_System/scripts/pre_dispatch_policy.py` and
`MAP_System/tests/test_pre_dispatch_policy.py` for the clause-scoped negation
change to destructive-intent detection.

## Files Reviewed

- `MAP_System/scripts/pre_dispatch_policy.py`
- `MAP_System/tests/test_pre_dispatch_policy.py`
- `MAP_System/tests/test_runner_policy_gate.py`

## Acceptance Criteria Check

- **PASS:** A hard-stop phrase occurring only inside a prohibition clause no
  longer causes `REQUIRE_CORE_DESTRUCTIVE_APPROVAL`.
- **PASS:** Period, colon, semicolon, exclamation, question, and newline clause
  boundaries restore destructive detection; unnegated imperatives still
  require approval.
- **PASS:** The focused pre-dispatch and runner policy-gate suites pass.

## Evidence

- `MAP_System/.venv/bin/python -m MAP_System.tests.test_pre_dispatch_policy` — PASS (10 tests).
- `MAP_System/.venv/bin/python -m MAP_System.tests.test_runner_policy_gate` — PASS (3 tests).
- Independent boundary probes — PASS:
  - comma-separated prohibition stays non-destructive;
  - period, colon, and newline boundaries restore detection;
  - an unnegated imperative remains destructive.

## Findings

- PASS — `contains_unnegated()` only suppresses a hard-stop phrase when a
  listed negation cue occurs earlier in the same clause.
- PASS — `.;:!?` and newline reset that scope; commas intentionally do not.
- PASS — explicit `destructive_action` metadata and all other policy gates are
  unchanged by this diff.

## Forbidden Changes Check

PASS. The change is confined to destructive-phrase classification and its
regression coverage. It does not weaken explicit destructive metadata, alter
worker authority tiers, bypass approval outcomes, or change unrelated dispatch
gates.

## Release note

This changes a dispatch safety classifier. Independent implementation review is
complete, but release should retain command-center policy sign-off if the
existing release process requires it.
