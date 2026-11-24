# Branch C — Security, authority, and independent review

- Record role: RESEARCH / PLANNING ASSESSMENT
- Status: CANDIDATE / NOT APPROVED; evidence checkpoint 2026-10-20
- Parent: [MAPS_L goal remap / direct node index](../../2026-10-20-think-plan-maps-goal-remap.md)
- Logical parent: MAPS_L proposed next milestone
- Child files: C1–C5 below
- Cross-branch dependencies: [Dependency and critical-path map](../DEPENDENCIES.md)
- Authority: No new MAPS_L, THINK/PLAN, experiment, external target, or merge authority

### C. Safety and genuinely independent judgment

- **C1. [PRESENT] Immutable/context-bound manifests, policy, review invariants and security baseline** → `runtime/integrity/`, `runtime/policy/`, `runtime/state/` and `tests/test_agentic_security_baseline.py`.
- **C2. [GAP SEC3] Confirm consequential external/destructive tool paths have *actual* security hook coverage**, not just a guard class and one call site.
- **C3. [GAP SEC4] Imported executable Skill/tool lifecycle is not fully proven end to end**; do not permit unreviewed content to activate in an external pilot.
- **C4. [CHECK] Independent review is bound to exact artifact/base/head; no author self-approval**, no bypass of [operator merge gate](../../../../../AGENTS.md).
- **C5. [TRIGGERED SEC6] Credential broker** requires genuine secret exposure/remote execution need; don't build for architecture elegance.
