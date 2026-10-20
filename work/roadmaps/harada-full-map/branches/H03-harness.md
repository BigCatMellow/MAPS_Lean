# H03 — Provider-neutral execution, tools, and deterministic hooks

- **Record:** candidate success-condition branch, not a new task or authority source
- **Parent:** [Full MAPS_L goal map](../README.md) · **Dependencies:** [cross-branch graph](../DEPENDENCIES.md)
- **Coverage:** [45 checklist rows + 35 master capability areas](../COVERAGE.md)
- **Children stored separately:** [H03.3 — immediate validation](H03.3-validation.md)
- **Evidence checkpoint:** 2026-10-20, main `69879cd0375f687c1df753fb5a4b83dda76b562e`; current runtime and task evidence supersedes status prose

## Required outcome
Approved worker operations are portable, observable, precisely typed and deterministically constrained, independent of which AI provider supplies judgment.

## Recursive conditions
- **H03.1 — Normalized operation semantics.** Result shape distinguishes failure, no matches, missing response, partial pagination, mutation, complete success and retry uncertainty. **Proof:** adapter-contract tests agree on semantics for misleading provider responses.
- **H03.2 — Stable Harness lifecycle.** Start, attach, send, inspect, heartbeat, resume, stop, collect are bound to task/run/session identity and provider adapters. **Proof:** the same lifecycle contract works on multiple supported adapters without changing task authority.
- **H03.3 — Deterministic hooks and immediate validation.** [Open child H03.3](H03.3-validation.md) to inspect the current opt-in versus enforced gap.
- **H03.4 — Tools as bounded operations, not authority.** Least capability, explicit effects, structured bounded outputs, correct retry and idempotency class. **Proof:** ambiguous external effect is reconciled rather than blindly repeated.
- **H03.5 — Operations preserve correlation and redacted diagnostics.** Tool and adapter telemetry links to real task/run/session and permits an UNKNOWN state without invented success.
- **H03.6 — Separate harness from execution compute.** The control plane does not assume a persistent daemon, a universal microVM/container, or provider-specific chat topology.

## Baseline / source owner
Checklist **H1–H3 and H5–H6 = DONE**, **H4 = IN PROGRESS** at last reconciled snapshot. Concrete owners: [Harness mechanics roadmap](../../agent-harness-capabilities/01-harness-mechanics.md), `runtime/harness/`, `runtime/environment/validation.py`. **DONE is source-reported**, not proof of every live caller being covered.

## Proportionate next tests
Select one real mutation and one ambiguous-side-effect scenario, record expected validation/guard behavior, and inspect actual call sites. Fix only the gap required by its authority and quality impact; do not add speculative adapters or permanent services.
