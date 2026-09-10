# External-effect idempotency audit — 2026-09-09

Status: `DESIGN GAP IDENTIFIED — CHARACTERIZATION ADDED, NO RUNTIME CHANGE`

Parent process: PR #326 / `work/notes/2026-09-09-competitor-borrow-integration-log.md`.

Deep prior-art evidence: `BigCatMellow/Pilot_Projects@f6d584465e15b0fcf3cd09fea9e056bc23852e94`.

## Question

Does MAPS_L already have the stronger external-effect correctness property implied by the competitor/mature-system corpus?

```text
one logical consequential operation
→ one stable operation identity before dispatch
→ retries reuse that identity
→ ambiguous provider outcome is preserved as ambiguous
→ reconciliation or provider idempotency decides whether to retry
→ no blind duplicate effect
```

Target is **not** universal exactly-once execution. The relevant correctness target remains:

```text
at-least-once attempt delivery
+ stable logical operation identity
+ idempotent/reconciled consequential effects
+ fail-closed treatment of ambiguity where duplicate effect is unsafe
```

## Current MAPS_L evidence

### 1. Good groundwork already exists

`runtime/harness/types.py::OperationResult` already records:

- `operation_id`;
- `mutated`;
- `complete`;
- `RetryDisposition.SAFE | UNSAFE | UNKNOWN`.

`tests/test_harness_types.py` proves callers can supply an explicit `operation_id`, serialization preserves it, and otherwise each result gets a fresh opaque `op-*` value. This is useful result correlation and explicit retry-safety vocabulary.

The hcom adapter also avoids pretending retry safety is known. Provider/transport failures return `retry=UNKNOWN`; successful `send`, `resume`, and `stop` likewise return `retry=UNKNOWN` after a side-effecting provider call.

### 2. `operation_id` is not currently logical intent identity

`runtime/harness/protocol.py::HarnessAdapter` accepts no operation/idempotency identity on `start`, `send`, `resume`, or `stop`.

`runtime/harness/service.py` likewise does not mint a logical operation ID before calling the adapter or include one in hook context as a required dispatch identity.

Therefore an `OperationResult.operation_id` can identify the returned result, but the current protocol cannot require the same ID to:

- exist before the external call;
- be stored before the external call;
- be presented to a provider/idempotency layer;
- survive caller/session restart;
- be reused by a retry of the same logical intent;
- detect same-ID/different-intent misuse.

Calling this field an idempotency key would overclaim its current semantics.

### 3. Recovery currently discards the retry/operation metadata it would need

`runtime/recovery/supervisor.py` projects a harness resume result into:

```text
attempted
ok
code
summary
```

It does **not** preserve `result.operation_id` or `result.retry` in `harness_resume`.

More importantly, when a harness resume fails for a non-canonical reason (adapter/provider failure, missing guard, etc.), the code intentionally falls through to the legacy direct `self.hcom.resume(...)` path in the same tick.

So the current shape can be:

```text
guarded HarnessService.resume()
→ adapter invokes provider
→ provider/transport outcome ambiguous
→ adapter returns failure with retry=UNKNOWN
→ supervisor does not retain UNKNOWN
→ supervisor immediately calls direct hcom.resume()
```

That behavior was intentionally retained to avoid suppressing resumes during harness rollout, but it means the stronger competitor-derived invariant is not presently true.

This audit does **not** assert that hcom resume necessarily duplicates harmful work; it asserts that the current control plane lacks the evidence needed to prove a second attempt is safe after an ambiguous first attempt.

### 4. Current authority guard and operation correctness are different concerns

6.4/H3/SEC3 answer questions such as:

- is this consequential action within the task envelope?
- is canonical run/session identity current?
- has required operator authorization been recorded?

They do not by themselves answer:

- did this exact logical external effect already happen?
- was the provider response lost after acceptance?
- is repeating this exact operation safe?

Capability/authority and idempotency/reconciliation must remain separate.

## Characterization added on PR #327

`tests/test_recovery_external_effect_ambiguity.py` now freezes the exact current seam without changing its expectation:

```text
real canonical task/run/session binding
→ HarnessService-like resume returns failure
   code=PROVIDER_TIMEOUT
   mutated=true
   operation_id=op-ambiguous-resume-1
   retry=UNKNOWN
→ RecoverySupervisor records only attempted/ok/code/summary
→ operation_id is absent from harness_resume
→ retry is absent from harness_resume
→ direct hcom.resume() is called once in the same tick
→ outward recovery action is resume
```

This is deliberately a **characterization test**, not an endorsement of the behavior. Its purpose is to give the owning Harness/Recovery design a concrete, executable decision case before changing policy or adding a general operation ledger.

If the future owner decides `UNKNOWN` must block immediate repeat, this test should be deliberately changed or replaced as part of that design change rather than silently preserved as permanent desired behavior.

## Disposition

`REAL DESIGN GAP — ROUTE TO HARNESS / RECOVERY; DO NOT PATCH POLICY IN RESEARCH LANE`.

No runtime, schema, or status change in this PR.

A proper solution must answer these questions together rather than add a cosmetic field:

1. **Identity boundary:** who creates the logical operation ID, and at what point before dispatch?
2. **Intent binding:** what task/run/revision/action/payload digest is bound to that ID?
3. **Persistence:** which existing owner records operation intent/attempt/result without becoming a second task database?
4. **Provider propagation:** which adapters/providers can receive a native idempotency key, and what is the fallback when they cannot?
5. **Ambiguous outcomes:** what durable state represents “effect may have happened; do not blindly retry”?
6. **Retry policy:** how does `RetryDisposition.UNKNOWN` constrain fallback and later retry?
7. **Reconciliation:** what observation can prove effect applied/not applied before another attempt?
8. **External-effect class:** which operations are naturally idempotent, compensatable, queryable, or non-reconcilable?

## Smallest future proof after characterization

Do **not** start with a general operation ledger.

The characterization test now establishes the current behavior. The next bounded owner decision is only:

```text
for recovery resume specifically,
should an attempted harness operation with retry=UNKNOWN
permit an immediate direct fallback in the same tick?
```

If **yes**, the owner must state what evidence makes that second attempt acceptable for this operation class.

If **no**, the narrowest implementation is to preserve the ambiguity metadata and stop immediate fallback for this seam before generalizing operation identity across every adapter action.

Only after that decision should MAPS design durable pre-dispatch operation identity, provider propagation, receipts, or reconciliation across broader external-effect classes.

## What not to import blindly

Do not copy Noriq/Restate/Temporal/Stripe schemas wholesale. MAPS_L already has canonical task/run identity and an `OperationResult` abstraction. Reuse the invariant and failure tests first; add persistence/protocol only where the existing owner cannot express the required fact.

## Conclusion

MAPS_L already names operation results and retry uncertainty honestly, which is useful groundwork. It does **not** yet provide durable pre-dispatch logical operation identity or ambiguity-aware external-effect reconciliation. The current recovery fallback can perform another resume attempt after a harness result whose retry safety is unknown.

PR #327 now makes that exact behavior executable and reviewable rather than leaving it as prose-only analysis. This remains a routed Harness/Recovery design gap, not a runtime-policy change.
