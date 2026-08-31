# PR #191 review evidence

reviewer: PLACEHOLDER — pending independent reviewer assignment
head_sha: PLACEHOLDER
independent: true
summary: PLACEHOLDER — awaiting independent review. Do not merge until this file carries a real reviewer, the reviewed code head_sha (currently 2562913c6b564b682159a6f563cb997f9784c868), and an APPROVE verdict.

## Scope to verify

- `git diff --stat origin/main...HEAD` = only
  `work/notes/2026-08-31-sec3-guard-impl-readiness-design.md` and this file.
- `git diff --check` clean.
- No `runtime/` code, no test, no `runtime/state/schema.sql`, no
  `work/roadmaps/CAPABILITY_CHECKLIST.md`.

## Claims for the independent reviewer to re-derive at HEAD

- `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION` exists (`runtime/harness/hooks.py`).
- `runtime/policy/destructive_action_guard.py` defines the guard + the
  both-events registration helper; current decision table denies
  `ACTION_AUTHORITY_ABSENT` unconditionally for any declared destructive/external.
- `runtime/state/policy.py` `PolicyStateMixin.get_task()["policy"]` carries
  `destructive_action` / `external_side_effect` / `requires_operator_approval` /
  `approved_by` / `approved_at`; `runtime/state/integrity.py` snapshots the six
  booleans (not the approval fields) into the run manifest.
- `record_operator_approval` exists in `runtime/state/policy.py` and is reachable
  as `maps … approve` (`runtime/routing/cli.py`).
- `runtime/policy/evaluator.py` provides `_approved` /
  `task_needs_human_reauthorization`.
- `HarnessService` fires exactly five events; none is
  `BEFORE_DESTRUCTIVE_ACTION` / `BEFORE_EXTERNAL_ACTION`. `stop()` currently
  fires `SESSION_STOPPING` and gates on `_require_canonical_enforcement`.
- `build_canonical_harness_service` does not register the destructive guard and
  its docstring says so.

## Decision soundness to assess

Q1 policy-source choice + decision table; Q2 first firing site (`stop()`) and the
flagged UNKNOWN (no production caller of `stop()` yet); Q3 keep-combined; Q4
fail-closed; Q5 evidence parity with `CanonicalRunGuard`; Q6 DENY-only + the
named-not-designed async approval bridge. Confirm the in/out scope table holds
the impl to one guard + one enum member + one firing event, and that the Resume
prompt is self-contained.

## Checks performed

_(to be filled by the independent reviewer)_
