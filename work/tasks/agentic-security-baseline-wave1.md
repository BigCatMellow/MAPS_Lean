# Task: agentic security baseline — Wave 1

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: make the initial harness security properties behavioral and mechanically fail closed at the public HarnessService mutation boundary without creating a second authority store.

## Inputs and source of truth

- Inputs: `AGENTS.md`, merged PRs #20–#23, master roadmap, Harness Mechanics roadmap, Agentic Security roadmap, current state/policy code, prior independent review findings.
- Authoritative sources: canonical MAPS task/run/review/policy state and current repository instructions.
- Dependencies: merged provider-neutral types, Hook/hcom normalization, HarnessService, CanonicalRunGuard.

## Reshaped change boundary

Independent review found that the original task boundary was too narrow for the useful security regression and too broad in stale operational notes. The final allowed security tranche is explicitly:

- `runtime/harness/hooks.py`
- `runtime/harness/service.py`
- `runtime/policy/harness_guard.py`
- `tests/test_harness_service.py`
- `tests/test_agentic_security_baseline.py`
- `tests/test_agentic_security_hook_context.py`
- `work/security/AGENTIC_THREAT_MODEL.md`
- this task file

The stale checkpoint/handoff files previously carried on the branch are explicitly **out of scope and removed from the final PR delta**.

MUST NOT CHANGE:

- SQLite schema or canonical task/run/review lifecycle;
- run-manifest immutability;
- review independence rules;
- hcom/helper/RnS provider behavior outside the normalized boundary;
- operator approval semantics;
- durable lineage/session authority state.

Any new durable adapter/session join belongs to the planned execution-lineage tranche, not this security patch.

## Acceptance criteria

- [x] `BEFORE_RESUME` is a deterministic Hook event and resume runs it before adapter mutation.
- [x] CanonicalRunGuard treats resume as both continuing and session-bound.
- [x] Continuing start/send/resume requires current revision, ACTIVE claimant, live lease, and non-stale run/context.
- [x] Session-bound send/resume/stop retains merged #23 adapter-qualified durable identity checks.
- [x] Current bare `run_manifests.session_id` is not promoted into provider-neutral identity; missing adapter qualification fails closed.
- [x] Public `HarnessService.start/send/resume/stop` fails closed with `CANONICAL_GUARD_REQUIRED` if the corresponding canonical-run enforcement is not installed.
- [x] Ordinary ALLOW Hooks do not satisfy canonical-run enforcement.
- [x] Enforcement identity is derived from the guard callback (`CanonicalRunGuard.hook_enforcement`), not from a caller-supplied HookSpec authority flag.
- [x] A declared enforcement callback must be READ_ONLY and FAIL_CLOSED at registration.
- [x] Low-level adapters remain capability primitives and do not gain authority.
- [x] Earlier Hooks cannot mutate nested identity/context observed by a later canonical guard.
- [x] Payload text cannot create operator approval.
- [x] Continuity-linked identities cannot claim independent review.
- [x] Provider/session liveness cannot renew task claim/lease or become task truth.
- [x] Peer/message text cannot transfer canonical ownership.
- [x] Threat-model document remains descriptive/test-oriented, not policy authority.
- [x] Stale operational checkpoint/handoff notes are absent from final PR delta.
- [ ] Fresh full Runtime stack CI passes on exact final head.
- [ ] Fresh independent review accepts exact final base/head.

## Reviewer-discovered corrections incorporated

### Mandatory guarded composition

The earlier stack made canonical guard registration opt-in. A caller could instantiate `HarnessService([adapter])` and invoke consequential mutations without canonical task/run checks.

Correction:

- CanonicalRunGuard declares the mechanical callback role `HookEnforcement.CANONICAL_RUN`.
- HookRegistry recognizes that role only from the registered callback and rejects an enforcement callback configured fail-open or with a mutating side-effect declaration.
- HarnessService requires that enforcement role at `RUN_STARTING`, `BEFORE_SEND`, `BEFORE_RESUME`, and `SESSION_STOPPING` before adapter mutation.
- Missing enforcement returns bounded `CANONICAL_GUARD_REQUIRED` and does not invoke the adapter.
- An ordinary ALLOW Hook is insufficient.

This marker proves only that the mandatory mechanical guard was installed. It does not itself grant task authority; the guard still derives its decision from canonical state.

### Adapter-qualified session identity

Merged #23 established that a provider-local session ID alone is not sufficient durable provider-neutral identity. #24 preserves that property for resume as well as send/stop. The current SQLite schema has no durable session-adapter field, so otherwise-valid session-bound operations fail closed until accepted lineage/schema work can prove the relationship.

## Verification

Focused behavioral suites:

- `tests.test_harness_service`
- `tests.test_harness_canonical_guard`
- `tests.test_agentic_security_baseline`
- `tests.test_agentic_security_hook_context`

Full PR-triggered Runtime stack CI is the merge gate.

Review required: `INDEPENDENT_REVIEW`.

## Security / privacy controls

- no raw provider transcript or exception detail is introduced;
- no secret store or credential value is added;
- no text/prose is accepted as task authority;
- no provider state mutates task heartbeat/lease;
- no schema or authority store is introduced;
- tests use fakes/disposable local state.

## Stop / escalate

Stop rather than guess if:

- durable adapter/session identity would require schema/lineage state;
- a consequential service path cannot mechanically require canonical enforcement;
- a proposed fix would move task authority into provider/session state;
- independent review identifies a new authority ambiguity.

## Completion / handoff

- Completed: mandatory guarded HarnessService composition, resume Hook/guard coverage, cross-system adversarial baseline, Hook-context regression, threat-model update, final scope cleanup.
- Not completed: exact-head CI / independent review / merge.
- Next action: assemble clean final tree from current `main`, run CI, independently review exact delta, then merge only if clean.
