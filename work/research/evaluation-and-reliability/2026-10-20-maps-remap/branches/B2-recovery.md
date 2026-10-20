# Branch B2 — Recovery and safe continuation

- Record role: RESEARCH / PLANNING ASSESSMENT
- Status: CANDIDATE / NOT APPROVED; evidence checkpoint 2026-10-20
- Parent: [MAPS_L goal remap / direct node index](../../2026-10-20-think-plan-maps-goal-remap.md)
- Logical parent: [B — Authorized execution](B-execution.md)
- Child files: B2.1–B2.3, including nested B2.2.1.1 and B2.2.1.2
- Cross-branch dependencies: [Dependency and critical-path map](../DEPENDENCIES.md)
- Authority: No new MAPS_L, THINK/PLAN, experiment, external target, or merge authority

## B2 — Recovery and safe continuation

- **B2. [CHECK] Recovery does not resume under incompatible authority or environment.**
  - B2.1 Recognize interruption, retain task/run/session linkage.
  - B2.2 Recover an incident and decide whether continuation is eligible.
    - B2.2.1 `CANONICAL_RUN` checks task revision, claim/lease and binding before resuming.
      - B2.2.1.1 [PRESENT narrow evidence] Real `LEASE_EXPIRED` denial occurred in the 2026-09-05 real-stall exercise (see checklist H5).
      - B2.2.1.2 [CHECK] Confirm operational coverage across real resume/dispatch paths, not just an opt-in example.
    - B2.2.2 [GAP E5] Environment compatibility is computed *advisory* in `runtime/recovery/supervisor.py`; the old E5 exit criterion (incompatible replacement cannot silently resume) is not established.
    - B2.2.3 [CHECK E6] Worktree identity guard exists; prove the intended enforcement boundary is used in the target workflow and prevents collisions.
    - B2.2.4 [CHECK H4] Validation has a narrow opt-in pre-resume blocking path; do not claim immediate post-mutation validation is broadly enforced.
  - B2.3 [CHECK] Failure classification chooses retry / replace / research / replan / stop without duplicate action or broadening authority.
