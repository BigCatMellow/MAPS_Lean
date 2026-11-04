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

## Community GitHub scan — 2026-11-04

The latest scan broadens beyond well-known vendors to small, independent repositories. Four **research-only** notes cover the existing owner domains. They distinguish upstream README claims from independently reproduced evidence, avoid duplicate task stores, and specify small falsifiable tests:

- [Agent harness / orchestration / progress](agent-harness/2026-11-04-community-mechanisms.md) — Overstory, Beads, Pi, `elementics/ag`, small Pi extensions; lean-vs-swarm and progress-vs-liveness hypotheses.
- [Context / memory / knowledge](skills-and-tools/2026-11-04-community-memory-context.md) — SLICE, Pi Smart Compact, `pi-memory`, Graphiti, an independent memory benchmark, agentplay and Atlas; recoverable citations, stale memory, provenance.
- [Evaluation / failure diagnosis](evaluation-and-reliability/2026-11-04-community-evaluation-mechanisms.md) — TrajDebug, AgentRx, Inspect AI, promptfoo, small edit-loop guards; frozen critical-failure step attribution and matched-arm evaluation.
- [Security / effective permissions](security-and-authority/2026-11-04-community-security-mechanisms.md) — `franklin-ross/sandbox`, Pi hooks, Overstory, promptfoo; transitive host-tool privilege and role/approval regressions.

### First research-to-improvement probes (not implementation authorization)

1. **Source-linked compaction:** existing context/handoff baseline vs compact context with verified links back to source constraints. Count lost/recovered hard constraints, false authoritative claims, and token cost. Owner: context/continuity.
2. **Evidence-grounded failure localization:** existing Run Record/incident analysis vs normalized traces with step-level evidence; score earliest actionable failure accuracy and abstentions against human-labeled failures. Owner: learning/evaluation.
3. **Lean default vs helper deployment:** matched project tasks and tools, one capable worker vs MAPS multi-seat routing; compare correctness, interventions, elapsed time and cost. Owner: harness/orchestration.

All three begin with frozen or synthetic evaluation inputs and do not authorize paid runs, target-repo writes, policy changes, background automation, independent approval, or merges. Community README descriptions are **reported**, not measured MAPS_L improvements. Do not repeat earlier broad research from the [September 2026 competitor tranche](#latest-competitor-evidence-tranche--2026-09-09) when these new notes merely reinforce it.

## Routing rule

Place a research note under the single topic that best owns its main question.
Cross-link instead of duplicating the same finding across folders. Keep source
links direct and distinguish observed evidence from interpretation.

The existing [`agent-harness-patterns-scan-2026-08.md`](agent-harness-patterns-scan-2026-08.md)
pre-dates this router and remains in place to avoid churn; future related scans
should use the topic folders above.
