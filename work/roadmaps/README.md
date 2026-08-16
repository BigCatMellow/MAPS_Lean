# MAPS roadmaps

Status: `PLANNING INDEX — NOT ACTIVE AUTHORITY`

Start here:

## [MASTER MAPS capability roadmap](00-MASTER-MAPS-CAPABILITY-ROADMAP.md)

This is the top-level planning orientation for the MAPS capability program. It owns the overall capability inventory, dependency graph, implementation waves, promotion gates, program-level definitions of done, and links to detailed roadmaps.

## [Current capability reconciliation — 2026-08-16](current-capability-reconciliation-2026-08-16.md)

Read this **after the master roadmap and before acting on historical “current baseline” or phase-status prose**. It is a dated planning-status overlay that reconciles the long-form design with accepted `main`, open capability stacks, real dependency constraints, and recovered legacy candidates.

The reconciliation is not canonical state. Live GitHub, accepted MAPS state, and current coordination evidence must still be re-checked before taking work. If the reconciliation and live state disagree, live state wins.

Detailed roadmaps:

- [Prime Agent capability adoption roadmap](prime-agent-capability-roadmap.md) — detailed Prime-derived lifecycle/harness concepts and their Lean translation. Its architecture remains useful, but historical phase/baseline text may predate the current reconciliation.
- [Operator Intent Compiler / Request Normalizer](operator-intent-compiler.md) — operator-facing intake layer that turns concise natural-language requests into proposed AGI-ready task contracts before Context Builder, without creating new authority.
- [Agent-harness capability roadmap set](agent-harness-capabilities/README.md) — five coordinated detailed roadmaps:
  1. Harness Mechanics
  2. Procedural Knowledge & Skills
  3. Environment & Reproducibility
  4. Agentic Security
  5. Learning & Evaluation

Supporting research/context:

- `work/research/agent-harness-patterns-scan-2026-08.md`
- `work/context/README.md`
- `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`
- `migration/FUTURE_IDEAS_BACKLOG.md`

Authority reminder: roadmaps are planning artifacts. `AGENTS.md`, canonical task/policy/review state, accepted task requirements, merged code/tests, and explicit operator decisions remain authoritative.
