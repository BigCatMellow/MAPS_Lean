# W0 — Bounded first-wave planning tasks

- Record role: RESEARCH / PLANNING ASSESSMENT
- Status: CANDIDATE / NOT APPROVED; evidence checkpoint 2026-10-20
- Parent: [MAPS_L goal remap / direct node index](../2026-10-20-think-plan-maps-goal-remap.md)
- Logical parent: [Proposed critical path](DEPENDENCIES.md)
- Child files: W0.1, W0.2, W0.3, W0.4
- Cross-branch dependencies: [Dependency and critical-path map](DEPENDENCIES.md)
- Authority: No new MAPS_L, THINK/PLAN, experiment, external target, or merge authority

## 4. First wave — proposed task contracts, not created/approved tasks

Focus on **proof and decisions**, not speculative subsystem implementations. Parent scope remains the existing MAPS_L roadmap; create/assign child tasks only under current accepted authority.

### W0.1 — Reconcile actual accepted state and work queue

- Inputs: current `main`; PR #367/#370/#372/#341 exact heads and changed paths; CI; review receipts; relevant accepted task/roadmap.
- Work: resolve stale #371 references and compare merged interface behavior to the claimed design; distinguish open review work from parked benchmark.
- DONE: one **evidence-backed** dependency/priority recommendation on relevant PR threads, stating exact outstanding independent review/integration gates and no unsupported merge-ready claims.
- Stop: independent review/merge authorization or owned branch mutation would cross a boundary. Use the proper reviewer/integration roles.

### W0.2 — Pilot-path safety/recovery readiness inspection

- Inputs: `runtime/recovery/`, `runtime/policy/`, `runtime/environment/`, `runtime/integrity/`, their unit tests and checklist H4/E5/E6/SEC3/SEC4; chosen pilot action class if known.
- Work: build a narrow **risk-to-enforcement** matrix identifying protected vs unprotected real call sites, and evidence required for each exercised path.
- DONE: pass/fail/UNKNOWN per critical path; each material gap becomes a bounded candidate repair with an expected behavioral regression case, not a broad security rewrite.
- Stop: absent target or call path → leave conditional, not assumed safe or assumed universally broken.

### W0.3 — Recover external-pilot scope and choose the smallest real task

- Inputs: [Portable Deployment](../../../roadmaps/agent-harness-capabilities/06-portable-deployment.md), target repository candidate and actual human-authorized scope.
- Existing design decisions: lightweight file convention, sibling clone/adapter, best-effort target review, stack-agnostic v1, target-local state.
- DONE for planning: real repo/task nomination, target access and permissions, non-goals, separate state path, human-only decisions explicitly recorded. No claim of a working pilot before execution.
- **HUMAN BOUNDARY**: target selection/access and side-effect permissions cannot be inferred from generic GitHub accessibility. Do not launch or merge external work from this proposal.

### W0.4 — Define end-to-end proof and comparator *before* a pilot

- Inputs: v1 D3 DONE; review/CI/Run Record capabilities; actual target acceptance.
- DONE: bounded acceptance fixture for: correct task and target, isolated state, no authority regression, independent review, accepted target integration, provenance, operator interventions, detectable recovery if exercised, real outcome, and no duplicate work. Also define a simpler baseline (e.g. standard agent-assisted task workflow with equivalent human authority and review).
- Stop: no valid comparator or no eligible reviewer → report `UNKNOWN`, not "MAPS_L beats baseline".
- No benchmark run, external mutation, model/API call, or research promotion is authorized by the fixture alone.

**Near-wave stopping condition:** Once current claims and risks are correctly classified and the target/authority decision is needed, stop *planning* rather than fabricate deeper detail. The first executable external tasks belong in a separately authorized pilot envelope, with fresh AGI/task readiness and independent verification.
