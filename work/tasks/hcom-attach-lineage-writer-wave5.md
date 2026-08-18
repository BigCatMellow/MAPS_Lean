# Task: real writer for run_session_links via HcomHarnessAdapter.attach()

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/hcom-attach-lineage-writer-wave5`
- Risk: `MEDIUM`
- Goal: Give `HcomHarnessAdapter.attach()` a real, opt-in implementation that
  calls the existing `record_run_session_link()` writer
  (`runtime/state/run_lineage.py`, merged in `run-session-lineage-wave3`),
  so `run_session_links` actually gets populated in production instead of
  staying permanently empty. This is what makes `RecoverySupervisor`'s
  `resolve_session_run()` reverse lookup (`runtime/recovery/supervisor.py`
  `_resolve_run_id`) stop always returning `None` -- the reader side has
  been merged and consumed since Wave 3/Stage 1, but nothing has ever called
  the writer outside tests.

## Inputs and source of truth

- `runtime/harness/adapters/hcom.py` -- `attach()` currently always returns
  `UNSUPPORTED` ("hcom attachment requires durable run/session lineage
  before it can be represented honestly."). This task removes exactly that
  limitation, and only when the adapter is explicitly configured with a
  lineage writer -- default behavior (no writer configured) is unchanged,
  preserving the existing `UNSUPPORTED` contract test.
- `runtime/state/run_lineage.py` (`RunSessionLineageMixin`, unmodified by
  this task) -- `record_run_session_link()` and `resolve_run_session()` are
  reused exactly as merged; this task does not change their semantics,
  validation, or SQL.
- `runtime/harness/types.py` -- `ExecutionBinding` already carries
  `run_id`, `worker_id`, `project_id`; `SessionRef` carries
  `session_id`/`adapter`/`project_id`/`remote_ref`. No new fields needed.
- `tests/test_harness_hcom_adapter.py` -- existing
  `test_unsupported_operations_are_explicit` constructs the adapter with no
  lineage writer and asserts `attach()` stays `UNSUPPORTED`; this must keep
  passing unmodified (default-off is the safety property).
- `runtime/recovery/supervisor.py` `_resolve_run_id` docstring -- documents
  the exact reverse-lookup contract this task's writer output must satisfy.

## Change boundary

MAY CHANGE / ADD:
- `runtime/harness/adapters/hcom.py` (additive: optional `lineage_writer`
  constructor parameter, new `attach()` body, one private helper)
- `tests/test_harness_hcom_adapter.py` (new tests only; existing tests
  unmodified)
- this task doc

MUST NOT CHANGE:
- `runtime/state/run_lineage.py` (writer/resolver semantics, SQL,
  validation) -- reused as-is
- `runtime/harness/service.py`, `runtime/harness/types.py`,
  `runtime/harness/protocol.py`
- `runtime/recovery/supervisor.py`
- any other harness adapter operation (`start`, `send`, `heartbeat`,
  `resume`, `stop`, `collect`, `inspect` stay exactly as merged)
- default (no-writer-configured) `attach()` behavior

## Required semantics

1. `lineage_writer` is optional (`None` default). With no writer configured,
   `attach()` is byte-for-byte the same `UNSUPPORTED` result as before --
   zero behavior change for any existing caller.
2. With a writer configured, `attach()` still performs the existing
   project/adapter mismatch checks first, unchanged.
3. The writer must expose exactly the two methods this task calls
   (`resolve_run_session(run_id)`, `record_run_session_link(...)`) --
   `TaskStore` already satisfies this by duck typing, matching the existing
   pattern in `RecoverySupervisor._resolve_run_id` (`getattr(...,
   "resolve_session_run", None)`).
4. Before writing, resolve the run's current lineage state:
   - `UNBOUND` or `ADAPTER_UNPROVEN`: record a first `ATTACH`
     (`replaces_link_id=None`). The writer's own manifest-session-conflict
     check (Required semantics #6 in `run_lineage.py`) still applies
     unchanged -- this task does not duplicate that validation.
   - `EXPLICIT` with `current` identity already equal to
     `(adapter_id="hcom", session_id)`: return success without writing a
     duplicate row (idempotent re-attach), never treat this as an error.
   - `EXPLICIT` with a different current identity: record a `REPLACE`
     naming the current link (`replaces_link_id=current["link_id"]`).
   - `INVALID`: fail closed with the resolver's own `INVALID` reason
     surfaced in the result; never attempt a write.
   - resolver returns `None` (run does not exist): fail closed
     (`RUN_NOT_FOUND`); never attempt a write.
5. `created_by` is `binding.worker_id` (the same worker the binding already
   authenticates as, no new identity concept). `evidence_ref` is a
   deterministic, non-secret string derived only from already-known
   identifiers (`session_ref.remote_ref` or `session_ref.session_id`) --
   never derived from message bodies or free text.
6. Any rejection from `record_run_session_link()` (e.g.
   `RUN_WORKER_MISMATCH`, `LEASE_EXPIRED`, `RUN_STALE`,
   `SESSION_ALREADY_BOUND`) is surfaced as a failed `OperationResult` using
   the writer's own `MutationResult.code`/`message` verbatim -- this task
   does not reinterpret or hide those reasons.
7. A successful write is `mutated=True`; the idempotent already-attached
   case is `mutated=False`.
8. No task/session/policy authority is granted anywhere in this path --
   `record_run_session_link()`'s own authority checks (live claim, matching
   worker, live lease, current task revision) are the only gate, unchanged.

## Acceptance criteria

- [ ] `test_unsupported_operations_are_explicit` (existing) still passes
      unmodified -- default-off preserved.
- [ ] With a configured writer and an `UNBOUND` run, `attach()` records an
      `ATTACH` link and returns success with `mutated=True`.
- [ ] Calling `attach()` again with the same session on the same run is
      idempotent: success, `mutated=False`, no second row written.
- [ ] Calling `attach()` with a different session on an already-`EXPLICIT`
      run records a `REPLACE` naming the correct current link.
- [ ] An `INVALID` lineage state fails closed without writing.
- [ ] An unknown `run_id` fails closed with `RUN_NOT_FOUND` without writing.
- [ ] A `record_run_session_link()` rejection (e.g. mismatched worker, or a
      session already bound to a different run) is surfaced verbatim as a
      failed `OperationResult`, not swallowed or reinterpreted.
- [ ] `RecoverySupervisor._resolve_run_id` (unmodified) returns a real
      `run_id` end-to-end when a `TaskStore` instance is used as both the
      supervisor's `task_reader` and the adapter's `lineage_writer` and a
      link was recorded via `attach()` -- one integration-style test proves
      the reader side is now actually reachable, not just independently
      correct.
- [ ] `python -m unittest tests.test_harness_hcom_adapter -v` and
      `python -m unittest tests.test_recovery_supervisor -v` pass.
- [ ] independent exact-head review confirms no new task/session authority
      is granted and the default-off contract genuinely holds.

## Verification

```text
python -m unittest tests.test_harness_hcom_adapter tests.test_recovery_supervisor tests.test_run_session_lineage -v
python -m unittest discover -s tests -v
```

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## Stop / escalate

Stop rather than guess if:
- any change would let this path grant task/session claim authority beyond
  what `record_run_session_link()`'s own checks already gate;
- `HarnessService`/CLI wiring to actually construct a configured
  `HcomHarnessAdapter` in a live entrypoint is needed -- out of scope here;
  this task only makes `attach()` correct and testable when a writer is
  supplied, it does not wire a production call site (no such call site
  exists yet for any harness adapter operation).
