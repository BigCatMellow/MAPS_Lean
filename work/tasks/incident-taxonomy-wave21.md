# Task: Outcome-linked incident-class vocabulary (roadmap 6.27, expansion)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/incident-taxonomy-wave21`
- Risk: `LOW`
- Goal: define the full 19-member `IncidentClass` vocabulary that
  `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section "6.27
  Outcome-linked incident taxonomy" lists as "Future incident classes",
  as a real enum type, matching `runtime.trust.MemoryTrustClass` (roadmap
  6.22, wave19) in style and level of ambition.
  `work/roadmaps/CAPABILITY_CHECKLIST.md`'s 6.27 row marked this
  `DONE (foundation)`, citing exactly this gap: append-only outcomes exist
  (`runtime/state/outcomes.py`, `tests/test_outcomes.py`), but the
  roadmap's expanded incident-class vocabulary was not encoded as a
  distinct type anywhere.

## Inputs and source of truth

- `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` (section "6.27
  Outcome-linked incident taxonomy") -- the exact 19-member vocabulary and
  its explicit rule: "Classification must preserve uncertainty; do not
  force every incident into a confident story." Not modified by this task.
- `runtime/state/outcomes.py` (`OutcomeMixin.record_outcome`; unmodified,
  not imported from) -- its `failure_class: str = ""` parameter is
  free-text and unvalidated against any taxonomy today. This task does not
  change that.
- `runtime/trust.py` (`MemoryTrustClass`, merged via PR #127, wave19) --
  the strongest existing precedent: a plain-vocabulary `str, Enum`, pure
  and read-only, explicitly not wired into any decision-gating path.

## Change boundary

MAY CHANGE / ADD:
- `runtime/incident_taxonomy.py` (new module)
- `tests/test_incident_taxonomy.py` (new)
- `work/roadmaps/CAPABILITY_CHECKLIST.md` (6.27 row evidence text only)
- this task doc

MUST NOT CHANGE:
- `runtime/state/outcomes.py`'s `OutcomeMixin.record_outcome` signature or
  validation logic -- unmodified. `failure_class` remains free-text,
  fully backward compatible with existing/out-of-vocabulary values.
- `runtime/policy/evaluator.py`, `tests/test_routing_policy.py` -- owned
  by a concurrent, unrelated roadmap-6.24 task; not touched.
- No decision-gating code path anywhere is wired to `IncidentClass` in
  this task.

## Required semantics

1. `IncidentClass(str, Enum)` in `runtime/incident_taxonomy.py` has exactly
   the 19 members the roadmap names, in roadmap order, member values equal
   to member names: `TOOL_FAILURE`, `CONTEXT_OMISSION`,
   `CONTEXT_POISONING`, `ROUTING_ERROR`, `SKILL_ROUTING_ERROR`,
   `HELPER_FAILURE`, `HELPER_NO_PROGRESS`, `RECOVERY_FAILURE`,
   `DUPLICATE_EXECUTION`, `ENVIRONMENT_DRIFT`, `REVIEW_MISS`,
   `STALE_REVIEW_EVIDENCE`, `VALIDATOR_FALSE_POSITIVE`,
   `VALIDATOR_FALSE_NEGATIVE`, `AUTHORITY_VIOLATION_ATTEMPT`,
   `ACI_AMBIGUITY`, `SUPPLY_CHAIN_DEFECT`,
   `OPERATOR_FRICTION_INTERVENTION`, `UNKNOWN`.
2. `UNKNOWN` is a first-class vocabulary member, not an error/fallback
   case bolted on afterward -- this preserves the roadmap's explicit
   uncertainty rule.
3. `classify_failure_text(text: str) -> IncidentClass` is a pure,
   read-only convenience helper: exact-match (case/whitespace-insensitive)
   lookup against the enum, returning `IncidentClass.UNKNOWN` for any
   non-match or non-string input rather than raising. It is never called
   from `record_outcome` or any other decision path.
4. The module is pure/read-only: no persistence, no task/session
   authority, no canonical storage, not wired into any decision-gating
   code path. Stated explicitly in the module docstring.

## Acceptance criteria

- [x] `IncidentClass` has exactly the 19 specified members with correct
      string values, verified by set-equality against the roadmap's own
      list.
- [x] `classify_failure_text` exact-match and `UNKNOWN`-fallback behavior
      covered by tests, including non-string input never raising.
- [x] `record_outcome`'s existing behavior/signature is completely
      unchanged -- `runtime/state/outcomes.py` not modified; existing
      `tests/test_outcomes.py` (if present) pass unmodified.
- [x] `python3 -m unittest tests.test_incident_taxonomy -v` and the full
      suite (`python3 -m unittest discover -s tests -v`) pass.
- [ ] Independent review remains required before completion.

## Verification

```text
python3 -m unittest tests.test_incident_taxonomy -v
python3 -m unittest discover -s tests -v
```

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not
eligible to supply that review
(`work/reviews/pr-<N>-review-evidence.md` required before merge per
`scripts/check_review_evidence.py`).

## Stop / escalate

This task defines the vocabulary (and one pure exact-match helper) only.
It deliberately does NOT:

- Change `OutcomeMixin.record_outcome`'s signature or validation in any
  way. `failure_class` stays free-text; existing and out-of-vocabulary
  values keep working exactly as before.
- Wire `IncidentClass` into any decision-gating code path (e.g. nothing
  in `outcomes.py` or elsewhere actually validates or classifies incoming
  `failure_class` values against this enum). Doing so -- e.g. adding real
  validation, migrating historical data, or gating recovery/routing
  decisions on incident class -- is separate, larger future work, exactly
  as 6.22's wave19 `MemoryTrustClass` left decision-gating wiring out of
  its own scope.
- Claim 6.27 is `DONE` on the roadmap checklist. It moves from
  `DONE (foundation)` to `IN PROGRESS`: the append-only outcome foundation
  and the expanded incident-class vocabulary now both exist, but nothing
  consumes or validates against this enum yet -- that remains future work.
