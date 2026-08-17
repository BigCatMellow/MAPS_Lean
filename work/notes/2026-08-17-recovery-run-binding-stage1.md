# Recovery run-id binding + advisory evidence, Stage 1/2 implementation note

Date: 2026-08-17
Owner: `agent/recovery-run-binding-stage1-wave4`
Status: implementation evidence

## Why

`work/notes/2026-08-17-recovery-equivalence-authority-design.md` found that
`RecoveryIncident` had no `run_id` field at all, so there was no way to even
look up which environment-compatibility evidence applied to a given recovery
incident -- a concrete prerequisite gap, separate from the bigger policy
questions in that design. The operator approved Stage 1 (the binding) and
Stage 2 Option A (advisory-only surfacing) explicitly, while declining to
approve any gating (Stage 3) for now.

## What changed

`runtime/recovery/store.py`:
- `RecoveryIncident` gained `run_id: str | None = None`.
- `RecoveryStore.schedule()` gained an optional `run_id` kwarg, defaulting to
  `None`, passed straight through to the incident.

`runtime/recovery/supervisor.py`:
- `RecoverySupervisor.__init__` gained an optional `environment_reader`
  kwarg, defaulting to `None`. When set, it must expose
  `list_run_environment_evidence(run_id) -> list[dict]` (the exact existing
  method on `EnvironmentEvidenceMixin` in `runtime/state/environment.py` --
  reused, not reimplemented).
- A new private helper, `_advisory_environment_evidence(run_id)`, returns
  `None` if no `run_id` is bound or no reader is configured, returns `None`
  (not a propagated exception) if the reader raises, and otherwise returns
  exactly what the reader returned.
- Every action dict `tick()` already returned (`suppress`/`resolve`/`fail`/
  `resume`/`resume_failed`) now carries one additional key,
  `environment_evidence`, computed once per incident before any of the
  existing decision branches run. No existing branch condition, ordering, or
  side effect changed.

## Why this is genuinely inert today, and that's intentional

No current caller populates `run_id`. `observe_silent_stops()` -- the only
place `RecoveryStore.schedule()` is called in production code -- was not
touched and still calls it without a `run_id`. This means every incident
scheduled by the real system today still gets `run_id=None`, and therefore
`environment_evidence` is `None` in every real `tick()` action for the
foreseeable current caller, exactly as before this change from an external
observer's point of view.

That is the correct, honest outcome for "Stage 1 + Stage 2 Option A" as
scoped: this task lands the binding and the advisory-surfacing plumbing so a
future task can wire a real caller to it, without that future task also
having to touch `RecoveryIncident`'s schema or `RecoverySupervisor`'s
decision loop. It does not claim to have connected anything to a live run
lookup, because no such lookup exists yet (see "Stop / escalation" in the
task doc).

## Proof of the advisory-only property

`test_incompatible_evidence_never_changes_the_recovery_decision` runs the
identical scenario (a due, stopped session, with `run_id="RUN-1"` bound)
twice: once with no `environment_reader` configured, once with a reader that
returns `INCOMPATIBLE` evidence. Every field of the resulting action is
identical between the two runs except `environment_evidence` itself and the
random per-run `incident_id`. The `resume` call to the (fake) hcom adapter
fires identically in both cases. This is the actual safety property Stage 2
Option A exists to guarantee, tested directly rather than only asserted in
prose.

`test_evidence_lookup_failure_does_not_break_tick` proves the same
resilience property under a failure mode: if the environment-evidence reader
itself raises, the incident's existing recovery action still completes
exactly as it would have with no reader configured at all -- an advisory
lookup can never become a new way for recovery to break.

## Verification performed

- `python -m unittest tests.test_recovery_supervisor -v`: 18 tests (11
  pre-existing, unmodified and still passing verbatim; 7 new), all pass.
- `python -m unittest discover -s tests`: full suite passes.
- `python scripts/check_legacy_removal_readiness.py`: PASS.
- `git diff --stat main`: exactly `runtime/recovery/store.py`,
  `runtime/recovery/supervisor.py`, `tests/test_recovery_supervisor.py`,
  plus this task doc and note.

## Continuation

Per the task doc: wiring a real caller (e.g. giving `observe_silent_stops`
or its caller an actual run lookup, and constructing production
`RecoverySupervisor` instances with a real `environment_reader`) is a
separate future task, still Stage 2, still advisory-only. Any gating
behavior (Stage 3) remains `BLOCKED_ON_OPERATOR_DECISION` and is not
proposed here.
