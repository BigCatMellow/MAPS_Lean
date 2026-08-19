# Task: Harness configuration identity primitive (L6, partial)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/harness-config-identity-wave10`
- Risk: `LOW`
- Goal: build the deterministic identity/hashing primitive that
  `work/roadmaps/agent-harness-capabilities/05-learning-and-evaluation.md`
  phase **L6 -- Harness configuration identity** calls for ("Version/hash
  consequential harness configurations. Exit gate: each evaluated run can
  identify which configuration produced it"). `work/roadmaps/CAPABILITY_CHECKLIST.md`
  marked L6 `NOT STARTED`: no `HarnessConfigRef`/config-hash/config-version
  concept existed anywhere. `runtime/run_record.py`'s `_coverage()` already
  hardcodes a `"harness_configuration"` entry to `MISSING` with the reason
  "current run manifest does not bind harness/hook configuration identity" --
  this task builds the identity primitive that reason anticipates, and wires
  the coverage projection to honestly report `VERIFIED` once a run manifest
  does carry the hash, without inventing any new source of that binding yet.

## Inputs and source of truth

- `runtime/harness/hooks.py` (`HookRegistry`, `HookSpec`, `HookEvent`,
  unmodified) -- what "hook configuration" consists of; `HookRegistry.list_for`
  is the existing public read path this task uses, one call per `HookEvent`
  member.
- `runtime/harness/service.py` (`HarnessService`, unmodified) -- how adapters
  and Hooks compose into one running configuration; `adapter_ids` and `hooks`
  are the two existing public surfaces this task reads.
- `runtime/harness/types.py` (`ExecutionBinding`) -- already has an optional
  `environment_spec_hash: str | None = None` field as the precedent pattern
  for referencing a spec/config identity from a binding without owning
  canonical storage. This task adds an analogous `harness_config_hash` field,
  validated and serialized the same way.
- `runtime/run_record.py` (`_coverage()`, `build_run_record()`) -- the
  existing `environment` coverage entry (driven by
  `environment_source_available` / `environment_evidence_present`, both
  sourced from what the trace's `run` dict exposes) is the exact shape this
  task mirrors for `harness_configuration`.
- `runtime/environment/spec.py` / `runtime/evaluation/regression_case.py`
  (`_canonical_hash`, unmodified) -- the canonical-JSON/sha256 hashing
  convention this task's own `_canonical_hash` in `config_ref.py` follows
  (sorted keys, compact separators, independently defined per module rather
  than imported, matching how `run_record.py` and `regression_case.py`
  already each define their own copy).

## Change boundary

MAY CHANGE / ADD:
- `runtime/harness/config_ref.py` (new module: `HarnessConfigRef`,
  `harness_config_ref()`)
- `runtime/harness/types.py` (additive: `ExecutionBinding.harness_config_hash`
  field + validation + `to_dict()` key, mirroring `environment_spec_hash`
  exactly)
- `runtime/harness/__init__.py` (additive export only: `HarnessConfigRef`,
  `harness_config_ref`)
- `runtime/run_record.py` (`_coverage()` gains a `harness_config_hash_available`
  parameter and honest VERIFIED/MISSING branching for `harness_configuration`,
  mirroring the `environment` branch; `build_run_record()` computes that flag
  from `"harness_config_hash" in run`, the same style as
  `environment_source_available = "environment_evidence" in run`)
- `tests/test_harness_config_ref.py` (new)
- `tests/test_harness_types.py` (additive: `harness_config_hash` coverage)
- `tests/test_run_record.py` (additive: one coverage test)
- this task doc

MUST NOT CHANGE:
- `runtime/state/schema.sql` -- no new canonical persistence; this task is
  identity/hashing only, matching how the H4/E4 validation-tier task and the
  H5 adapter-contract task ("the pieces exist and are correct; no production
  call site invokes it yet") were scoped.
- `runtime/harness/hooks.py`, `service.py`, `protocol.py`,
  `runtime/harness/adapters/*` -- read-only inputs to this task.
- Any existing `runtime/run_record.py` behavior for the common case where a
  trace's `run` dict does not carry `harness_config_hash` (today's exact
  `MISSING` reason string stays byte-for-byte the same until a real caller
  supplies the field).

## Required semantics

1. `HarnessConfigRef` is a frozen dataclass with `adapter_ids: tuple[str, ...]`
   (sorted), `hooks: tuple[dict[str, object], ...]` (one canonical descriptor
   per registered Hook: `hook_id`, `event`, `priority`, `side_effect`,
   `failure_policy` -- never the callback itself, which is not stable/hashable
   across processes), and a `sha256` field computed over canonical JSON
   (sorted keys, `separators=(",", ":")`) of `{adapter_ids, hooks}`.
2. `harness_config_ref(service)` builds one `HarnessConfigRef` from a live
   `HarnessService`: `service.adapter_ids` for adapters, and
   `service.hooks.list_for(event)` for every `HookEvent` member (not just
   one) for hooks. Hook descriptors are sorted deterministically
   (`event`, `hook_id`, `priority`) before hashing so registration order
   never changes the digest.
3. Two `HarnessService`s with equivalent declared adapter/Hook metadata but
   different callback function objects hash identically -- the hash is a
   configuration identity, not a code identity.
4. `ExecutionBinding.harness_config_hash` accepts `None` (default) or
   non-empty text; empty/whitespace-only text raises `ValueError`, exactly
   like `environment_spec_hash`. `to_dict()` includes the key.
5. `_coverage()`'s `harness_configuration` entry reports `VERIFIED` (with a
   reason mirroring the `environment` branch's wording) when the trace's
   `run` dict contains a `harness_config_hash` key, and keeps today's exact
   `MISSING` reason text otherwise -- no behavior change for existing callers
   until a future task actually writes that key onto a real run manifest.

## Acceptance criteria

- [x] `HarnessConfigRef`/`harness_config_ref` hash deterministically: same
      configuration -> same hash across independent builds.
- [x] Different adapter sets and different Hook sets each change the hash.
- [x] Hash excludes callback identity (two registries with equivalent
      declared metadata but distinct callback functions hash identically).
- [x] Hooks from every `HookEvent`, not just one, are included.
- [x] `ExecutionBinding.harness_config_hash` validates like
      `environment_spec_hash` (`None` ok, empty string raises `ValueError`).
- [x] `build_run_record()` reports `harness_configuration` coverage as
      `VERIFIED` when the trace's `run` dict carries `harness_config_hash`,
      and preserves today's `MISSING` behavior otherwise.
- [x] `python3 -m unittest tests.test_harness_config_ref tests.test_run_record tests.test_harness_types tests.test_harness_service -v` passes.
- [x] Full suite `python3 -m unittest discover -s tests -v` passes.
- [ ] Independent review remains required before completion.

## Verification

```text
python3 -m unittest tests.test_harness_config_ref tests.test_run_record tests.test_harness_types tests.test_harness_service -v
python3 -m unittest discover -s tests -v
```

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## Stop / escalate

Stop rather than guess if:
- a design would have `harness_config_hash` actually get written onto a real
  run manifest at run-start time (e.g. inside `HarnessService.start()` or
  `TaskStore.create_run_manifest()`), or would add a `harness_config_hash`
  column/table to `runtime/state/schema.sql`. That is real schema/call-site
  wiring risk and a separate, larger task -- this task deliberately stops at
  "the pieces exist and are correct; no production call site invokes it yet,"
  the same boundary the H4/E4 validation-tier task and the H5
  adapter-contract-suite task (`work/tasks/harness-adapter-contract-suite-wave7.md`)
  used. L6 remains only *partially* complete after this task; a fast-follow
  task should wire `harness_config_ref()` into the real run-start path and
  persist its `sha256` onto the run manifest, then flip
  `work/roadmaps/CAPABILITY_CHECKLIST.md`'s L6 entry from `NOT STARTED`/
  `IN PROGRESS` to `DONE` only once that binding is real and covered.
- a Hook's structured value contract (`_freeze_hook_value` in `hooks.py`)
  needs to become part of the identity -- this task deliberately hashes only
  `hook_id`/`event`/`priority`/`side_effect`/`failure_policy`, not any
  per-invocation context/annotations, since those are runtime data, not
  configuration identity.
