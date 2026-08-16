# Task: canonical harness run guard

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: add a read-only canonical-state Hook guard so harness continuation operations cannot rely on session liveness or stale/ambiguous run identity instead of current MAPS task/run evidence.

## Inputs and source of truth

- Inputs: `AGENTS.md`, merged PRs #20–#22, `runtime/state/execution.py`, `runtime/state/integrity.py`, `runtime/state/schema.sql`, master roadmap, Prime roadmap Phase 2, Harness Mechanics roadmap.
- Authoritative sources: canonical SQLite task/run state and active repository instructions win.
- Dependencies / preconditions: merged HarnessService/Hook contracts; existing immutable run manifests and task leases.

## Change boundary

- MAY CHANGE: `runtime/policy/harness_guard.py`, `runtime/policy/__init__.py`, focused tests, this task file.
- MUST NOT CHANGE: SQLite schema, task lifecycle/claim mutation behavior, run-manifest immutability, hcom/helper/RnS behavior, review semantics, external systems.
- MAY CHANGE IF NECESSARY: none without re-shaping.
- OPERATOR APPROVAL REQUIRED: any new durable authority/join state or destructive/external behavior.

## Decision authority

- Owner may decide: read-only guard checks, Hook registration points, denial codes/messages, and operation-specific freshness requirements consistent with existing canonical state.
- Owner must escalate: any need to mutate leases/task state, create a second session authority store, or add new durable join state.

## Acceptance criteria

- [x] Guard verifies explicit task/run/worker/project identity against canonical task and immutable run manifest.
- [x] `start`/`send` require current task revision, ACTIVE claimant, live lease, and non-stale run/context evidence.
- [x] Session-bound operations require exact session ID **and adapter-qualified durable identity** before provider mutation.
- [x] A bare `run_manifests.session_id` is not treated as provider-neutral proof; current schema therefore fails closed with `SESSION_ADAPTER_UNPROVEN` for otherwise-valid `send`/`stop` rather than guessing.
- [x] Same session ID on a different adapter is denied mechanically.
- [x] Historical `stop` can retain the relaxed lease/revision semantics only when the canonical source can actually prove adapter-qualified historical session identity; current schema does not yet provide that proof.
- [x] Guard fails closed when canonical evidence is missing, mismatched, stale, unsupported, or underqualified.
- [x] Guard is read-only and grants no policy/operator authority.
- [x] Registration covers pre-mutation lifecycle events only.
- [x] Focused adversarial tests cover bare-ID ambiguity and same-ID/different-adapter collision.
- [ ] Fresh full Runtime stack CI and independent review remain required on the final integrated head.

## Reviewer-discovered correction

Independent pre-integration review identified that the original guard compared only `run_manifests.session_id` with `SessionRef.session_id`, while provider routing is adapter-specific. Two adapters can legitimately expose the same provider-local session ID, so the bare ID was insufficient evidence for the claimed exact durable binding.

The correction deliberately does **not** add a mutable session store or silently expand the SQLite schema. `_require_durable_session()` now checks:

1. explicit routed adapter and `SessionRef.adapter` agree;
2. durable session ID exists and matches;
3. the canonical source also provides a durable session adapter;
4. that adapter matches the routed/session-ref adapter.

The current SQLite `run_manifests` table has no session-adapter field. Therefore current real manifests fail closed for session-bound provider mutation until the planned durable-lineage/schema work supplies an accepted adapter-qualified relationship. This is an explicit limitation, not an inferred success.

## Verification and evidence

- Verification target: focused `tests.test_harness_canonical_guard` plus full PR-triggered Runtime stack CI.
- Evidence to preserve: exact PR base/head, CI run, independent review result.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: existing MAPS Lean Python runtime.
- Ordered procedure: read-only canonical guard → focused tests → CI → independent review.
- Failure branches: IF adapter-qualified durable session identity is absent THEN deny rather than infer it from provider state or bare session ID; IF stale task/run state is found for continuation THEN deny and require recovery/rebinding.
- Rollback / recovery: revert isolated PR; no schema/data migration.
- Security / privacy controls: no raw provider transcript/logging; concise reason codes only; source reads are canonical and read-only.
- External side effects: Git branch/PR publication only; tests use fakes.
- Effort limit: one narrow guard tranche; durable late session attachment and adapter-qualified persisted lineage remain separate design work.

## Stop / escalate

Stop rather than guess if:

- durable late session attachment becomes necessary to satisfy a provider mutation;
- canonical evidence cannot distinguish adapter-qualified session identity;
- stopping stale sessions would require reviving expired authority.

Escalate durable join/schema work to the planned execution-lineage tranche/operator gate rather than creating a hidden second authority.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Session liveness is intentionally not used to renew or prove task authority.
- Provider capability remains distinct from permission/authority.
- Bare provider-local identifiers are not promoted into global/durable identity by convention.
- Late session attachment and adapter-qualified durable lineage remain deferred rather than being smuggled into this guard.

## Completion / handoff

- Completed: read-only canonical task/run guard, operation-specific continuation checks, adapter-qualified fail-closed session semantics, focused adversarial coverage.
- Not completed: final exact-head CI / independent review / merge.
- Next action: validate the integrated head and hand it to independent review.
