# Task: recovery run-id binding + advisory environment evidence, Stage 1/2 Wave 4

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/recovery-run-binding-stage1-wave4`
- Risk: `LOW`
- Goal: Implement Stage 1 (bind `RecoveryIncident` to an optional `run_id`) and
  Stage 2 Option A (pure read-only environment-compatibility evidence
  surfacing in `RecoverySupervisor.tick()`'s action output) from
  `work/notes/2026-08-17-recovery-equivalence-authority-design.md`, per the
  operator decisions recorded there. No recovery decision changes.

## Inputs and source of truth

- `work/tasks/recovery-equivalence-authority-design-wave4.md` and
  `work/notes/2026-08-17-recovery-equivalence-authority-design.md` (merged
  PR #80) — this task implements exactly Stage 1 and Stage 2 Option A from
  its "Unblocked next step" section, and only those. Stage 3 (any gating of a
  recovery action) is explicitly `BLOCKED_ON_OPERATOR_DECISION` and is not
  touched here.
- `runtime/recovery/store.py` and `runtime/recovery/supervisor.py` at current
  `main` (read in full before this task; verified no existing `run_id` field
  or environment-evidence consultation anywhere in either file).
- `runtime/state/environment.py`'s `list_run_environment_evidence(run_id)` —
  reused as the evidence source, not modified.
- `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §4.2 ("capability is
  not authority").

## Change boundary

MAY CHANGE:
- `runtime/recovery/store.py` (additive: `run_id` field + kwarg only)
- `runtime/recovery/supervisor.py` (additive: `environment_reader` kwarg +
  `_advisory_environment_evidence` + `environment_evidence` key on every
  action dict)
- `tests/test_recovery_supervisor.py` (additive: new test class)
- this task doc and its note

MUST NOT CHANGE:
- any existing recovery decision branch in `tick()` (suppress/resolve/fail/
  resume conditions and their triggers are byte-for-byte unchanged; only a
  new dict key is added to already-existing action dicts)
- `runtime/state/environment.py`
- `runtime/state/schema.sql`
- any other runtime file
- any other agent's branch

## What this does NOT do

- Does not populate `run_id` automatically anywhere. `observe_silent_stops()`
  is unchanged and still calls `store.schedule()` without a `run_id`, so in
  current production usage every incident's `run_id` remains `None` today.
  This lands the binding capability for a future caller that has the run
  context; it does not invent a lookup that guesses which run an incident
  concerns.
- Does not wire any `environment_reader` into default `RecoverySupervisor`
  construction. It defaults to `None`, so `environment_evidence` is `None`
  in every action dict for every current real caller until something
  explicitly opts in.
- Does not gate, suppress, delay, or otherwise change any recovery action
  based on environment compatibility. `test_incompatible_evidence_never_changes_the_recovery_decision`
  proves this directly: identical scenario, with vs. without `INCOMPATIBLE`
  evidence present, produces byte-identical actions apart from the evidence
  field itself.

## Acceptance criteria

- [x] `RecoveryIncident` has an optional `run_id: str | None = None` field.
- [x] `RecoveryStore.schedule()` accepts an optional `run_id` kwarg, defaulting
  to `None`, threaded through unchanged to the stored incident.
- [x] `RecoverySupervisor` accepts an optional `environment_reader` kwarg,
  defaulting to `None`.
- [x] Every action dict `tick()` returns includes an `environment_evidence`
  key: `None` when no `run_id` is bound or no reader is configured; the
  reader's return value when both are present; `None` (not a propagated
  exception) if the reader raises.
- [x] The evidence lookup never runs when no `run_id` is bound (proven by
  `reader.calls == []` in that case).
- [x] No existing test in `tests/test_recovery_supervisor.py` required any
  change to keep passing.
- [x] A test proves the advisory property directly: identical inputs produce
  identical actions regardless of what environment evidence says, evidence
  field aside.
- [x] `python scripts/check_legacy_removal_readiness.py` passes.
- [x] `git diff --stat main` shows only the four files listed in the change
  boundary.

## Verification

```text
python -m unittest tests.test_recovery_supervisor -v
python -m unittest discover -s tests
python scripts/check_legacy_removal_readiness.py
```

Review required: `INDEPENDENT_REVIEW`.

## Stop / escalation

Stop rather than extend scope if:
- a caller needs `run_id` auto-populated from task/run state (that requires
  a "runs for task" lookup that does not exist today and is a separate
  bounded task, not this one);
- any gating/suppression behavior is proposed based on evidence (Stage 3,
  explicitly not authorized);
- `DRIFTED` vs `INCOMPATIBLE` treatment needs a decision (deferred per the
  operator decision record; no gating exists yet for that decision to apply
  to).

## Continuation

Per the design note: this stays inert-until-adopted infrastructure. The next
bounded step, if ever pursued, is a separate task binding a real caller (e.g.
`observe_silent_stops` or its caller) to an actual run lookup and wiring a
real `environment_reader` into production `RecoverySupervisor` construction
-- itself still Stage 2, still advisory-only, still requiring independent
review before Stage 3 (any gating) could even be proposed.
