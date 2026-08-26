# MAPS_Lean audits

Status: `EVIDENCE / RECONCILIATION INDEX — NOT TASK OR ROADMAP AUTHORITY`

Purpose: preserve bounded audits that materially affect how current MAPS work
should be interpreted or tested. These records are evidence and navigation,
not an execution queue. A finding becomes work only through an authorized task,
roadmap item, operator decision, or other existing authority surface.

## Current audits

- [Proof Phase Audit & External Test Plan](2026-08-26-maps-proof-phase-audit-and-test-plan.md)
  - Defines the external comparative test plan for determining which MAPS
    mechanisms earn their complexity.
  - Primary roadmap relationship: [Roadmap 06 — Portable Deployment](../roadmaps/agent-harness-capabilities/06-portable-deployment.md).
- [Deep Project Archaeology Audit](2026-08-26-deep-project-archaeology-audit.md)
  - Reconciles loose ends, ghost gaps, stale orientation, historical ideas,
    review debt, branch archaeology, and information-lifecycle drift.
  - Written after the first Proof Phase plan; where the two disagree about
    whether a specific historical item remains unfinished, this later audit
    controls as the newer evidence record, subject to current `main`.

## Connections

- [Current reconciliation task](../tasks/reconcile-project-truth-20260826.md)
- [Current reconciliation / Proof Phase handoff](../handoffs/2026-08-26-project-reconciliation-and-proof-phase.md)
- [Roadmap index](../roadmaps/README.md)
- [Capability checklist](../roadmaps/CAPABILITY_CHECKLIST.md)
- [Information lifecycle](../../playbook/INFORMATION_LIFECYCLE.md)
- [Roadmap trajectory check](../../playbook/ROADMAP_TRAJECTORY_CHECK.md)
- [Tenth-Seat review](../../playbook/TENTH_SEAT_REVIEW.md)

## Use rule

Preserve history deeply; surface current meaning shallowly. Before turning an
audit finding into implementation work, reconcile it against current code,
current checklist evidence, merged PR history, and live GitHub state.
