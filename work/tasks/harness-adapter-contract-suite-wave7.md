# Task: Harness adapter contract suite (H5, partial)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/harness-adapter-contract-suite-wave7`
- Risk: `LOW`
- Goal: build the shared, reusable `HarnessAdapter` contract test suite that
  `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md` phase
  **H5** calls for ("all supported adapters pass shared contracts"), and
  prove the one currently-supported adapter (`HcomHarnessAdapter`) actually
  satisfies it. `work/roadmaps/CAPABILITY_CHECKLIST.md` (PR #105) marked H5
  `NOT STARTED` citing exactly this gap: no generic adapter-contract test
  file existed anywhere in `tests/`.

## Inputs and source of truth

- `runtime/harness/protocol.py` (`HarnessAdapter`, unmodified) -- the
  `runtime_checkable` Protocol this contract verifies structural conformance
  against.
- `runtime/harness/types.py` (`OperationResult`, unmodified) -- the
  normalized result envelope (H1) every operation must return.
- `runtime/harness/adapters/hcom.py` (`HcomHarnessAdapter`, unmodified) --
  the one adapter exercised against the new contract.
- `runtime/harness/service.py` docstring (unmodified) -- documents that a
  post-start Hook failure can preserve `mutated=True` on a failed
  `OperationResult`; the contract deliberately does not forbid this, since
  outlawing it would contradict `HarnessService`'s own documented behavior.
- `tests/test_harness_hcom_adapter.py` (unmodified) -- existing hcom-specific
  behavioral tests; this task does not duplicate or replace them, only adds
  the separate structural/behavioral contract layer.

## Change boundary

MAY CHANGE / ADD:
- `runtime/harness/contract.py` (new module)
- `runtime/harness/__init__.py` (additive export only: `AdapterContractMixin`)
- `tests/test_harness_adapter_contract.py` (new)
- this task doc

MUST NOT CHANGE:
- `runtime/harness/protocol.py`, `service.py`, `hooks.py`, `types.py`
- `runtime/harness/adapters/hcom.py` and its existing test file
- `runtime/helpers/ollama.py`, `runtime/helpers/aider.py`,
  `runtime/recovery/supervisor.py` -- wrapping these as `HarnessAdapter`
  implementations is explicitly **out of scope** for this task (see Stop /
  escalate below); they are one-shot/synchronous invocation shapes, not the
  session-lifecycle shape (`start`/`attach`/`send`/`inspect`/`heartbeat`/
  `resume`/`stop`/`collect`) `HarnessAdapter` models, and forcing that fit is
  a separate design decision, not a mechanical wrap.

## Required semantics

1. `AdapterContractMixin` is a plain mixin, not itself a `unittest.TestCase`
   subclass, so bare test discovery does not collect/run it without adapter
   fixtures -- only a concrete `TestCase` that also inherits it is runnable.
2. The contract only asserts what a caller needs to treat any adapter
   interchangeably through `HarnessService`: (a) structural `HarnessAdapter`
   protocol conformance, (b) a stable non-empty `adapter_id`, (c) every one
   of the 8 protocol operations returns an `OperationResult` instance and
   never raises, for a structurally valid binding/session/payload.
3. It does not assert adapter-specific business outcomes (what a particular
   provider's `send` should actually do) -- that stays in the adapter's own
   test module, unmodified here.
4. `HcomAdapterContractTests` runs the mixin against a real
   `HcomHarnessAdapter` instance (with a fake in-memory hcom backend, not a
   mock of `HarnessAdapter` itself) with `lineage_writer` left unconfigured
   (default-off) -- `attach()` returning `UNSUPPORTED` in that state must
   still satisfy the contract, since the contract only requires a well-typed
   result, not that every operation be normalized yet.

## Acceptance criteria

- [x] `AdapterContractMixin` is not collected as a runnable test on its own
      (bare mixin, no `TestCase` base).
- [x] `HcomAdapterContractTests` (mixing it into a real `HcomHarnessAdapter`
      fixture) passes: protocol conformance, stable `adapter_id`, and all 8
      operations return `OperationResult` without raising.
- [x] Existing `tests/test_harness_hcom_adapter.py` is unmodified and still
      passes (no duplication/replacement of its adapter-specific coverage).
- [x] `python3 -m unittest tests.test_harness_adapter_contract -v` and the
      full suite (`python3 -m unittest discover -s tests -v`) pass.
- [ ] Independent review remains required before completion.

## Verification

```text
python3 -m unittest tests.test_harness_adapter_contract tests.test_harness_hcom_adapter tests.test_harness_types tests.test_harness_service -v
python3 -m unittest discover -s tests -v
```

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## Stop / escalate

Stop rather than guess if:
- a design would wrap `runtime/helpers/ollama.py`, `aider.py`, or
  `runtime/recovery/supervisor.py` as `HarnessAdapter` implementations --
  their one-shot/synchronous shape does not naturally map onto the
  session-lifecycle protocol, and forcing a fit (e.g. treating a single
  invocation as `start()` immediately followed by `collect()`) is a real
  design decision requiring its own task/roadmap discussion, not a
  mechanical migration. H5 remains only *partially* complete after this
  task -- the "remaining adapters" half is still `NOT STARTED`, only the
  "contract suite" half is done. `work/roadmaps/CAPABILITY_CHECKLIST.md`
  should be updated in a fast-follow docs-only PR to reflect this (H5 moving
  from `NOT STARTED` to `IN PROGRESS`, not `DONE`).
- the contract would need to assert something adapter-implementation-specific
  to pass (a sign the contract is leaking a non-shared assumption).
