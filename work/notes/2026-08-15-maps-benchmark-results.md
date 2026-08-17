# MAPS Layer 2 / Layer 3 benchmark result validation

Status: `IMPLEMENTED ON STACKED DRAFT BRANCH — NOT EXECUTION OR PRODUCTION AUTHORITY`

Branch: `agent/maps-benchmark-results-wave3`

Base dependency: PR #40 exact head `85ca58db52c81dd250b89316ecbc54785aeb9e18`.

## Purpose

Provide the smallest deterministic adapter that can consume **externally produced** benchmark evidence and determine whether the frozen Layer 2 / Layer 3 protocol is complete, failed, or incomplete.

This mechanism does not run an agent, perform production sampling, deploy anything, or create operator-visible effects.

## Result contract

Each scenario result declares:

```text
scenario_id
evidence_class
fixture_kind
properties{}
provenance{}
measurements{}
```

### Property evidence

Every property state is:

```text
PASS | FAIL | UNKNOWN | NOT_RUN
```

`PASS` and `FAIL` require one or more observable `evidence_refs`.

`UNKNOWN` and `NOT_RUN` may not claim evidence refs.

Missing required properties are treated as `NOT_RUN` and make the scenario incomplete.

This prevents a result adapter from reporting a bare positive/negative assertion without traceable observable evidence.

## Fixture/evidence class

Allowed fixture kinds:

```text
CONTROLLED_SYNTHETIC
CONTROLLED_REAL
REAL_PRODUCTION
```

Layer 2 accepts controlled synthetic or controlled real execution.

Layer 3 accepts **only** `REAL_PRODUCTION`.

A Layer 3 result with a synthetic or merely controlled fixture fails mechanically even if every property is marked PASS.

## Provenance contract

The scorer distinguishes:

```text
VERIFIED
UNKNOWN
NOT_APPLICABLE
```

for these provenance classes:

```text
task
run
outcome
operator_visible_result
external_authority
operator_intervention
```

A VERIFIED item requires an evidence reference. UNKNOWN/NOT_APPLICABLE cannot carry a supposedly verified reference.

Important boundary:

> The scorer does not itself prove that an arbitrary string reference is canonical. A future adapter may set `VERIFIED` only after resolving the reference through accepted/canonical evidence.

The scorer therefore preserves the distinction between **result validation** and **source verification**.

## Layer 3 eligibility

All Layer 3 scenarios require VERIFIED:

- task provenance;
- run provenance;
- real outcome provenance.

`E2E-L3-001` additionally requires VERIFIED:

- operator/user-visible result provenance;
- existing task/external-action authority provenance.

`E2E-L3-002` requires operator-intervention provenance only when `operator_intervention_count > 0`.

Missing/UNKNOWN required provenance makes a real-production result `INCOMPLETE`; it does not become PASS through inference.

## Scenario scoring

A scenario is:

### FAIL

when:

- any required property is `FAIL`; or
- the evidence class/fixture kind violates the protocol.

A QUALITY property failure still fails the scenario.

A BLOCKER property failure is additionally listed in `blocker_failures` and prevents candidate advancement regardless of cost/speed/other gains.

### INCOMPLETE

when:

- a required property is `UNKNOWN` or `NOT_RUN`; or
- required real Layer 3 provenance is not VERIFIED; or
- the whole scenario result is absent.

### PASS

only when:

- every required property passes; and
- scenario evidence/fixture eligibility passes.

## Measurements

The bounded measurement fields are:

```text
runtime_ms
cost_usd
tool_calls
messages
agent_count
operator_intervention_count
rework_count
```

They are never used to turn a failing/incomplete result into PASS.

This preserves the roadmap rule that more activity or lower cost is not outcome success.

## Benchmark aggregation

The report keeps:

- scenario PASS/FAIL/INCOMPLETE counts;
- separate Layer 2 and Layer 3 counts;
- whether the required real external/operator-visible case passed;
- exact BLOCKER failures;
- per-scenario measurements;
- candidate advancement gate.

The gate states are deliberately non-authorizing:

```text
BLOCKED
INCOMPLETE
EVALUATION_COMPLETE_NOT_AUTHORIZED
```

There is no `APPROVED` or `PROMOTE` output.

## Privacy / observability

The report preserves evidence-reference **counts**, property IDs/states, provenance eligibility, and bounded measurements. It does not copy raw private prompts, raw file contents, message bodies, or private model reasoning.

## Adversarial tests

Focused tests verify:

- a complete six-scenario result is complete but not authorized;
- synthetic Layer 3 fails;
- unknown run provenance makes Layer 3 incomplete;
- real external case requires verified authority and operator-visible result;
- QUALITY failure still fails;
- BLOCKER failure is explicit/non-tradeable;
- UNKNOWN and omitted required properties remain incomplete;
- PASS/FAIL without evidence refs fails closed;
- counted operator intervention requires attributable provenance;
- low cost/runtime/activity cannot hide a failure;
- result ordering is deterministic;
- unknown property/scenario IDs fail closed.

## Future integration

Later, after accepted interfaces are known, adapters can populate VERIFIED provenance from sources such as:

- canonical task/run state;
- accepted execution lineage;
- portable Run Record/trace evidence;
- immutable review subject;
- append-only outcome observations;
- acquisition-path verification evidence.

Those integrations should **feed this scorer**, not move their authority into it.

## Non-goals

This work does not:

- execute the benchmark;
- claim current MAPS already passes it;
- create real-world outcome observations;
- infer operator intervention from chat;
- grant external action authority;
- promote a harness/context/routing/policy change;
- freeze draft PR #33-#35 API spelling.
