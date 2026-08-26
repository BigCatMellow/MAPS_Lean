# INSIGHT-75785aae: The Harness layer (H4/H5/L6/SEC4 waves) has zero production callers of HarnessService despite substantial test-only build-out

- Kind: `insight`
- Date: `2026-08-19`
- ID: `INSIGHT-75785aae`

## Observation

grep -rn 'HarnessService(' across the repo (excluding legacy/ and tests/) finds no matches outside tests/test_harness_service.py -- HarnessService, ExecutionBinding, and the adapter protocol (runtime/harness/protocol.py, service.py, hooks.py) are exercised only by unit tests (test_harness_types.py, test_harness_hcom_adapter.py, test_harness_adapter_contract.py, test_agentic_security_baseline.py, test_recovery_supervisor.py, etc.) across several merged waves (PRs #100, #101, #106, #107, #112). No CLI command, runtime/cli.py entry point, or scheduled/dispatched code path constructs a HarnessService and drives an adapter through it in this Lean runtime.

## Source / context

grep -rn 'HarnessService(' . (excluding legacy/); runtime/harness/service.py; runtime/harness/protocol.py; PRs #100, #101, #106, #107, #112 (merged 2026-08-14 through 2026-08-18)

## Potential value

This isn't necessarily wrong -- building the contract/adapter layer ahead of wiring a real execution target is a defensible sequencing choice -- but it means several roadmap phases (H4/H5/L6/SEC4) were scoped and partially implemented without ever validating the abstraction against a real caller. The risk is the classic one for interface-first work: the contract could need reshaping once something actually drives it end-to-end, and that reshaping cost gets paid later, across more call sites, than if a minimal real caller had been wired earlier.

## Smallest next test

Before adding more Harness surface area (a hypothetical H6/L7 wave), check whether any concrete task actually needs a HarnessService instance wired to a live dispatch path yet; if not, that's worth flagging in the roadmap as a named risk (interface validated only by tests, not by a real caller) rather than silently continuing to add adapter surface.

## Promotion

Not promoted at capture time. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

## Current disposition — 2026-08-26

`PARTIALLY RESOLVED / PRINCIPLE PRESERVED`

Later RnS work introduced real HarnessService resume routing in
`RecoverySupervisor.tick()` when an appropriate service/binding is supplied,
and later production recovery composition made `tick()` explicitly invokable.
The original claim that the Harness layer had *zero* production-facing seams is
therefore historical.

The remaining gap is narrower and still important: the default production
recovery composition does not yet establish the full real HarnessService /
worker-session evidence path needed to prove the abstraction end-to-end on an
external workflow.

Related current artifacts:

- [Harness production-wiring gap analysis](../notes/2026-08-19-harness-production-wiring-gap.md)
- [RnS production trigger-loop design](../notes/2026-08-24-rns-production-trigger-loop-design.md)
- [current reconciliation handoff](../handoffs/2026-08-26-project-reconciliation-and-proof-phase.md)

Preserve the original warning as a standing design principle: **do not add more
Harness surface merely because the interface permits it; require a real caller
or a concrete external test.**
