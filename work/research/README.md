# Research routing index

Status: `NAVIGATION — NOT ACTIVE AUTHORITY`

Use this directory for source investigation, external mechanism scans, papers,
benchmarks, and evidence that may inform MAPS Lean. Research does not become MAPS
policy or implementation merely because it recommends an action.

Prefer a few broad topic folders over a flat pile or a deep taxonomy. Create a
new topic only when it has a distinct recurring research job.

## Current topics

| Topic | Scope |
| --- | --- |
| [`agent-harness/`](agent-harness/) | Agent harnesses, orchestration, lifecycle, state, worker control, hooks, context delivery, and execution boundaries. |
| [`skills-and-tools/`](skills-and-tools/) | Skills, MCP/tool interfaces, capability packaging, tool schemas, retrieval interfaces, and integration portability. |
| [`evaluation-and-reliability/`](evaluation-and-reliability/) | Benchmarks, ablations, verification methods, adversarial tests, failure injection, and experimental methodology. |
| [`security-and-authority/`](security-and-authority/) | Permission/authority boundaries, containment, supply-chain risks, approvals, ambiguous targets, and consequential-action controls. |

## Latest competitor-evidence tranche — 2026-09-09

A deep public-source extraction in `BigCatMellow/Pilot_Projects` was projected into the existing MAPS_L research topics rather than copied as a parallel dossier/packet hierarchy.

- [`agent-harness/2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md`](agent-harness/2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md) — durable ownership/fencing, reconciliation, runtime truth, durable-execution reference semantics, DSH rooted/session mechanisms.
- [`skills-and-tools/2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md`](skills-and-tools/2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md) — MCP/A2A boundaries, provider/runtime adapters, effective-runtime evidence, Git-backed working-memory provenance.
- [`evaluation-and-reliability/2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md`](evaluation-and-reliability/2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md) — upstream incident/fix history and portable regression cases.
- [`security-and-authority/2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md`](security-and-authority/2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md) — fail-closed approvals, review lineage, sandbox/path enforcement, scoped credentials, hard-budget semantics, external-effect ambiguity, supply-chain provenance.

These notes are **evidence inputs only**. They deliberately strengthen existing MAPS_L owners instead of adopting DBOS/Restate/Temporal/DSH/Letta/LiteLLM/etc. or creating another task/workflow authority.

## Routing rule

Place a research note under the single topic that best owns its main question.
Cross-link instead of duplicating the same finding across folders. Keep source
links direct and distinguish observed evidence from interpretation.

The existing [`agent-harness-patterns-scan-2026-08.md`](agent-harness-patterns-scan-2026-08.md)
pre-dates this router and remains in place to avoid churn; future related scans
should use the topic folders above.
