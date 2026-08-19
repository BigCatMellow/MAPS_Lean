# Task: HcomHarnessAdapter.resume() normalization (wave17)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/hcom-adapter-resume-wave17`
- Risk: `LOW`
- Goal: normalize `HcomHarnessAdapter.resume()` so it actually calls the real
  hcom backend instead of returning `UNSUPPORTED`. `work/notes/2026-08-19-harness-production-wiring-gap.md`
  documents zero production callers of `HarnessService` anywhere and
  recommends migrating RnS's hcom resume calls through
  `HcomHarnessAdapter`/`HarnessService` ("Option B") as the best first wiring
  target. The SENTINEL second-opinion review
  (`work/reviews/pr-119-review-evidence.md`) flagged that
  `HcomHarnessAdapter.resume()` needs to be built as an explicit first
  sub-step before any RnS migration is attempted. This task is exactly that
  sub-step, and nothing more.

## Inputs and source of truth

- `runtime/harness/adapters/hcom.py` (`HcomHarnessAdapter.stop()`, unmodified
  in shape) -- the existing `send`/`stop` methods are the structural
  template `resume()` now follows: resolve the session via
  `self._binding_session(binding)`, call the backend, catch
  `(HcomError, ValueError)` with `HcomError` mapped through
  `self._provider_failure(exc)` and `ValueError` mapped to a structured
  `INVALID_ARGUMENT` failure, then return `OperationResult.success(...)`
  with `mutated=True` and `retry=RetryDisposition.UNKNOWN`.
- `runtime/communication/hcom_adapter.py` (`HcomAdapter.resume(name, *,
  headless=False, terminal=None, go=True)`, unmodified) -- the real backend
  method now being wired up, matching RnS's current real usage
  (`headless=True, go=True`).
- `runtime/harness/service.py` (`HarnessService.resume()`, unmodified) --
  already called `adapter.resume(binding)`; it previously always got back an
  `UNSUPPORTED` result from the hcom adapter. No change was needed here.

## Change boundary

MAY CHANGE / ADD:
- `runtime/harness/adapters/hcom.py` (`resume()` method body only)
- `tests/test_harness_hcom_adapter.py` (new resume test coverage, plus the
  `FakeHcom` fixture's `resume()` method, plus removing `resume` from
  `test_unsupported_operations_are_explicit`'s expected-unsupported list)
- `tests/test_harness_adapter_contract.py` (`_FakeHcomBackend` fixture gained
  a `resume()` method -- once `HcomHarnessAdapter.resume()` stopped being
  `UNSUPPORTED` it started calling `self.backend.resume(...)` for real, so
  the shared contract's fake backend needed the method too; the shared
  contract logic in `runtime/harness/contract.py` itself was not touched)
- this task doc

MUST NOT CHANGE:
- `runtime/harness/protocol.py`, `types.py`, `hooks.py`, `contract.py`
- `runtime/harness/service.py`
- `runtime/communication/hcom_adapter.py`
- `runtime/recovery/supervisor.py` -- migrating RnS's hcom resume call sites
  through this adapter is explicitly **out of scope** for this task (see
  Stop / escalate below); that is a separate follow-up task.
- `work/roadmaps/CAPABILITY_CHECKLIST.md` -- this task is an internal
  sub-step preparing for the RnS migration, not itself closing any roadmap
  phase; the checklist is intentionally left untouched here.

## Required semantics

1. `resume()` resolves the session the same way `stop()`/`send()` do, via
   `self._binding_session(binding)` -- no reimplementation of session/project
   lookup.
2. `resume()` calls `self.backend.resume(str(record["name"]), headless=True,
   go=True)`, matching RnS's real current usage of the backend method.
3. `HcomError` from the backend maps through `self._provider_failure(exc)`
   (same as `stop()`/`send()`); the raw provider message must not leak into
   the returned `OperationResult.summary`.
4. `ValueError` from the backend maps to a structured `INVALID_ARGUMENT`
   failure carrying `data={"error_type": "ValueError"}`, not the raw
   exception text, matching `stop()`/`send()`.
5. On success, `resume()` returns `OperationResult.success("SESSION_RESUMED",
   "hcom resume request completed.", data={"session_id": ...,
   "remote_name": ...}, mutated=True, retry=RetryDisposition.UNKNOWN)`,
   mirroring `stop()`'s real success-result shape.
6. `test_unsupported_operations_are_explicit` no longer asserts `resume`
   returns `UNSUPPORTED` -- it now only covers `start`/`attach`/
   `heartbeat`/`collect`.

## Acceptance criteria

- [x] `HcomHarnessAdapter.resume()` resolves the session via
      `_binding_session`, calls `self.backend.resume(name, headless=True,
      go=True)`, and maps `HcomError`/`ValueError` the same way `stop()`
      does.
- [x] `FakeHcom` (the test fixture in `tests/test_harness_hcom_adapter.py`)
      gained a `resume()` method matching its existing `send`/`stop`
      fake-method style.
- [x] New tests cover: success, session-not-found, project-mismatch,
      backend-error (`HcomError`), and invalid-argument (`ValueError`) cases
      for `resume()`.
- [x] `test_unsupported_operations_are_explicit` updated to drop `resume`
      from its expected-unsupported list.
- [ ] Independent review remains required before completion.

## Verification

```text
python3 -m unittest tests.test_harness_hcom_adapter tests.test_harness_adapter_contract -v
python3 -m unittest discover -s tests -v
```

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## Stop / escalate

Stop rather than guess if:
- a design here would require touching `runtime/recovery/supervisor.py` or
  any RnS call site -- that migration (plus its shadow-mode rollout) is
  explicitly deferred to a follow-up task, not folded into this one.
- `HarnessService.resume()` did not already call `adapter.resume()` -- it
  does (verified in `runtime/harness/service.py`), so no service-layer
  wiring was needed in this task.
