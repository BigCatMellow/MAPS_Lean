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

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

## Disposition 2026-09-03 (Emergence pass, tuba)

**STALE.** Resolved. `runtime/recovery/production.py::build_canonical_harness_service` is the production composition root (`HcomHarnessAdapter` -> `HookRegistry()` -> `register_canonical_run_guards` -> `HarnessService`) since 2026-08-30; first real production exercise was the `--enforce-canonical-run` pass in PR #277 (`a4f2dc8`), 2026-09-03. The interface-first risk this insight named (contract validated only by tests) held up: no reshaping was needed when a real caller was wired. Kept as history; no re-open.
