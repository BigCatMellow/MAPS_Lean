# Scope, sources, and evidence limits

- Record role: RESEARCH / PLANNING ASSESSMENT
- Status: CANDIDATE / NOT APPROVED; evidence checkpoint 2026-10-20
- Parent: [MAPS_L goal remap / direct node index](../2026-10-20-think-plan-maps-goal-remap.md)
- Logical parent: MAPS_L goal remap
- Child files: none
- Cross-branch dependencies: [Dependency and critical-path map](DEPENDENCIES.md)
- Authority: No new MAPS_L, THINK/PLAN, experiment, external target, or merge authority

## 1. Precise purpose and evidence boundary

**Question:** If we derive MAPS_L's next milestone from its actual mission instead of treating all old checklist rows as compulsory, what success conditions, gaps, dependencies, and near-term work result?

**Provisional next milestone (not a replacement for the broader [master final target](../../../roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md#19-final-target)):**

> An operator approves a bounded, real task in a previously unmanaged external repository. MAPS_L's portable method and available mechanisms support the task from shaping through execution, independent verification/review and legitimate integration, with target-isolated truth, observable interruptions and recoveries, preserved authority, and inspectable outcome evidence—without the operator repeatedly steering ordinary in-scope steps.

This tests a meaningful vertical slice, not *all* optional agent infrastructure. The external-pilot subroadmap defines v1's narrower formal DONE and its best-effort review-evidence policy; do **not** silently strengthen that approval envelope. See [Portable Deployment](../../../roadmaps/agent-harness-capabilities/06-portable-deployment.md).

**This is a manual use of documented T&P-style reasoning**; no THINK/PLAN runtime ran or validated this assessment. The recursive Harada concept is a research adaptation, not a feature claimed for Harada's original fixed grid.

**Observed evidence sampled (not exhaustive):**
- Live GitHub on 2026-10-20 showed four open PRs: [#367](https://github.com/BigCatMellow/MAPS_Lean/pull/367), [#370](https://github.com/BigCatMellow/MAPS_Lean/pull/370), [#372](https://github.com/BigCatMellow/MAPS_Lean/pull/372), and [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341). Current `main` CI `test` succeeded at base SHA; PR checks also reported success at selected heads. **Green checks do not establish independent approval or merge authority.** Re-fetch live state before acting.
- [Runtime README](../../../../runtime/README.md), source trees and selected source files verify real task state, harness, recovery, environment validation, Skills, outcome/learning, and CLI code, with corresponding `tests/` files. Sampling source and test presence is not the same as executing or exhaustively auditing them.
- The [capability checklist](../../../roadmaps/CAPABILITY_CHECKLIST.md) records **29 DONE, 6 IN PROGRESS, 10 NOT STARTED** across 45 entries. It contains dated reconciliations (some older) and cannot be interpreted as current verified percentage completion. In particular, L6 is recorded DONE **even while its explanatory evidence says actual run-manifest harness hash persistence is absent**.
- [Current orientation snapshot](../../../../state/CURRENT.md) (2026-10-06) identifies the open integration queue. Some snapshots are stale: e.g. its #371 child reference is now merged; live [#371](https://github.com/BigCatMellow/MAPS_Lean/pull/371) merged 2026-10-07. A merged design does **not** by itself satisfy #341's independent Arm C content-verdict gate.
- Pilot portfolio [PORTFOLIO.md](https://github.com/BigCatMellow/Pilot_Projects/blob/main/PORTFOLIO.md) treats #341's benchmark line as parked/blocked, THINK as monitor-only, and PLAN as primary. Its PR #33 live-status prose is stale (that PLAN PR merged October 13). Reconcile cross-project priority before promoting new research or moving #341.

**Unknown:** Current local deployments, target-project operator permissions, actual successful external runs, complete feature-head review evidence, and effectiveness versus simpler operation were **not** independently reproduced. Do not infer them from documentation or green CI.
