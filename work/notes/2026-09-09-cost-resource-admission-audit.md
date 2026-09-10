# Cost/resource admission audit — 2026-09-09

Status: `DESIGN GAP IDENTIFIED — NO RUNTIME CHANGE`

Parent process: PR #326 / borrow-before-build integration.

Upstream evidence: LiteLLM budget-reservation behavior/failures and `BigCatMellow/Pilot_Projects@f6d584465e15b0fcf3cd09fea9e056bc23852e94`, especially `complete-ai-work-system/research/competitive-architecture/production-accelerators/P0-COST-RESOURCE-ADMISSION.md`.

## Question

Does MAPS_L already implement the stronger hard-budget correctness property?

```text
authorized spend/resource envelope
→ estimate conservative next operation
→ atomically reserve capacity
→ admit or reject before launch
→ execute
→ settle actual use / release unused reservation
→ reconcile ambiguity
```

This is different from both permission to use a paid capability and retrospective usage reporting.

## Current MAPS_L evidence

### Run budgets are runtime-count integrity limits

`runtime/integrity/budget.py::check_run_budget()` compares caller-supplied measured values against immutable run-manifest limits:

- `max_attempts`
- `max_tool_failures`
- `runtime_seconds`

A limit is exhausted when measured use reaches/exceeds it.

The module explicitly states the check is deterministic/non-authoritative and does not mutate task truth, dispatch work, or halt the system. `write_budget_escalation()` writes exhaustion evidence for a later control-plane/operator decision.

`runtime/integrity/README.md` describes the same model: execute within declared budget, then compare measured use and optionally write an escalation record.

This is useful execution-integrity evidence, but it is not monetary/resource reservation.

### Worker `cost_rank` is preference, not spend accounting

`runtime/policy/models.py::WorkerProfile.cost_rank` is a non-negative integer routing preference. It carries no currency, authorized ceiling, reservation, settled amount, billing identity, or concurrency-safe balance.

It may help choose a cheaper worker relative to another worker, but it cannot prove a task/run stays under a dollar/token/API-request ceiling.

### Assignment policy does not perform monetary admission

The inspected `runtime/policy/evaluator.py::evaluate_assignment()` evaluates availability, environment compatibility, task lifecycle/AGI state, task/risk support, mutation capability, narrow-worker authority restrictions, and explicit human reauthorization.

It does not reserve money/tokens/requests before allowing assignment.

The task policy's `paid_execution` field exists elsewhere in canonical task state, but this audit does not promote that boolean into spend accounting. A permission/classification flag cannot substitute for atomic resource reservation.

## Competitor-derived failure model

The LiteLLM failure history shows why a simple `current_spend < limit` read is insufficient under concurrency:

```text
remaining = $1.00
request A reads $1.00 remaining
request B reads $1.00 remaining
A launches estimated $0.80
B launches estimated $0.80
actual concurrent exposure = $1.60
```

A hard ceiling needs a reservation at the same decision boundary that authorizes launch.

The same distinction applies even if the unit is not money:

- tokens;
- requests;
- tool/API calls;
- provider concurrency slots;
- prepaid credits.

## Disposition

`REAL FUTURE CAPABILITY — DO NOT PATCH INTO CURRENT run-budget CHECK`.

The existing run-budget owner should keep its current meaning: immutable runtime-count limits + deterministic measured-use check. Overloading it with monetary state would blur two distinct truths.

A future resource-admission owner should answer:

1. **Authority:** where is the authorized hard ceiling sourced from?
2. **Unit:** dollars, integer microdollars, tokens, requests, provider credits, or multiple dimensions?
3. **Reservation identity:** what logical operation/run owns a reservation?
4. **Atomicity:** what transaction prevents two concurrent admissions from spending the same remaining capacity?
5. **Estimate:** what conservative maximum is reserved before launch?
6. **Settlement:** how is actual usage recorded and unused capacity released?
7. **Ambiguity:** if the provider may have accepted the request but accounting response is missing, is the reservation retained until reconciliation?
8. **Retry/fallback:** do retries/children/fallback models consume the same authority envelope?
9. **Availability:** when hard-ceiling accounting is unavailable/stale, does paid work fail closed?
10. **No auto-top-up:** does exhaustion remain a durable funds/resource block rather than silently expanding authority?

## Smallest future proof

Do **not** start with provider integration.

First create a provider-free concurrency test around a candidate reservation primitive:

```text
limit = 100 units
A reserves 70
B concurrently attempts reserve 70
exactly one reservation commits
available never becomes negative
```

Then test:

- release unused reservation;
- duplicate reservation identity is idempotent;
- same reservation identity + changed intent fails closed;
- settlement is idempotent;
- ambiguous execution retains reservation;
- no paid authority => zero admissions.

Only after the deterministic primitive is proven should it be wired to a real paid provider path.

## What not to import blindly

Do not adopt LiteLLM as MAPS_L's canonical budget authority merely because it implements reservations. Its own failure history includes stale/distributed counters, concurrency races, attribution problems, temporary-budget inconsistencies, and fail-closed regressions. Use those failures as regression requirements for whichever MAPS owner is chosen.

## Conclusion

MAPS_L currently has **runtime integrity budgets**, not **hard monetary/resource admission**. The existing mechanism should not be relabeled or overloaded. The borrow-before-build evidence supports a separate, atomic pre-launch reservation primitive only when paid/resource-constrained provider execution becomes an active implementation need.
