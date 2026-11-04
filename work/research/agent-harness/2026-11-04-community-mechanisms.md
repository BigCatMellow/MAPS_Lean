# Community GitHub mechanisms — orchestration, execution, progress (2026-11-04)

Status: **RESEARCH — NOT ACTIVE AUTHORITY**. Source: public repository docs/README inspected 2026-11-04, not a runtime audit or independent performance validation. Compare against [the existing September competitor scan](2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md) before proposing implementation. Neither stars nor demos establish reliability.

## Candidate A — Overstory: layered health signals and worker integration
- Source: https://github.com/jayminwest/overstory (primary repository).
- Observed in upstream description: per-agent Git worktrees; typed SQLite coordination messages; mechanical watchdog followed by optional AI triage; integration/merge queue and role-specific tool hooks. Project itself warns against default swarms.
- Existing MAPS_L: separate task truth, claims, isolation, recovery, advisory `NO_PROGRESS`, review; prior scan already covers Gas Town and related coordination systems.
- **New useful seam:** distinguish `alive`, `claim still valid`, `forward progress`, and `integration readiness` in one correlated **read-only** status view. Do not import mail store, tmux fleet, or second task tracker.
- Experiment/falsifier: replay a frozen case with live-but-stalled worker, and a finished-but-unmerged worker; measure correct state classification, false alerts, operator time vs current status/recovery. Reject if no reduction in incorrect recovery or operator effort.
- Risk: layered monitors create extra cost and competing authority; project-reported properties only. **Disposition: TEST selected progress signals; no framework adoption.**

## Candidate B — Beads: dependency graph survives compaction
- Source: https://github.com/gastownhall/beads (formerly steveyegge/beads).
- Upstream description: Git-backed task/issues and dependency relationships persist across context resets.
- Existing MAPS_L: canonical SQLite task/dependency graph plus Markdown work records. This is **mostly already covered**.
- Distinguishing experiment: measure whether after compaction/restart an agent can recover the right next actionable task using a compact dependency projection versus its existing context plan. Do not copy Beads issue storage.
- Risk: two stores create inconsistent task authority. **Disposition: REFERENCE ONLY unless current recovery fails a frozen case.**

## Candidate C — Pi agent: intentionally narrow agent core and opt-in extensions
- Source: https://github.com/earendil-works/pi (formerly badlogic/pi-mono; redirect verified).
- Upstream: distinct multi-provider API, agent core, coding CLI, TUI and extension seams. Focus on small composable units rather than one mandatory full-stack orchestration.
- Existing MAPS_L: provider-neutral harness/adapter intent with several heavier coordination layers.
- Useful hypothesis: a small capability-appropriate agent loop with optional MAPS support may produce equal task results with fewer handoffs and less setup for simple tasks.
- Experiment: pair simple/medium/parallel tasks, same models/context/tool scope; compare completion, interventions, tool calls, wall time. Reject simplification only if guardrail or result quality suffers.
- Risk: Pi alone does not replace MAPS durable task authority or review. **Disposition: TEST SMALLER DEFAULT EXECUTION PATH.**

## Candidate D — elementics/ag: mechanical repeated-edit loop stop
- Source: https://github.com/elementics/ag.
- Upstream README reports a compact per-turn ledger of writes/reads/verification and a guard when the same file is repeatedly edited without new inspection or tests; also lazy masking/retrieval of older tool output and local checkpoints.
- Existing MAPS_L: progress adviser and integrity checks, but not necessarily a repeated-edit-without-evidence invariant.
- **Smallest extract:** add a nonblocking diagnostic over existing trace/evidence that recognizes repeated edits without intervening read/test. Do not force an arbitrary universal edit-count threshold from this project's README.
- Experiment: replay genuine correction loops and intentional multi-edit tasks; measure avoidable tool calls and harmful false interventions. **Disposition: TEST; code/behavior not independently reproduced.**

## Candidate E — corporealshift/pi-extensions: tiny event-specific safeguards
- Source: https://github.com/corporealshift/pi-extensions.
- Upstream: single-purpose extensions for command guardrails, pre-edit checkpoint, turn-end lint, task/progress persistence, and tool-call veto.
- Existing MAPS_L: already has hooks, policy guards, and validation tiers. The **lesson is narrower integration**: evidence-triggered hooks close to the action, rather than another universal planning stage.
- Experiment: compare immediate validation on actual relevant writes vs late omnibus checks, with failure catch latency and unnecessary runs as metrics.
- Risk: ad hoc command matching is not sufficient security. **Disposition: STUDY implementation ergonomics, not permissions policy.**

## Cross-cutting decision
Priority in this area: **(1) compare lean single-agent path; (2) progress-vs-liveness replay; (3) unnecessary repeat-edit diagnostic**. None authorizes new agents, schedulers, merges, or target-project actions. MAPS_L `6.19–6.21` and harness areas remain the implementation owners.
