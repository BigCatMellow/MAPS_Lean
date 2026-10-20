# Branch D — Verification, configuration provenance, and outcomes

- Record role: RESEARCH / PLANNING ASSESSMENT
- Status: CANDIDATE / NOT APPROVED; evidence checkpoint 2026-10-20
- Parent: [MAPS_L goal remap / direct node index](../../2026-10-20-think-plan-maps-goal-remap.md)
- Logical parent: MAPS_L proposed next milestone
- Child files: D1–D4 below
- Cross-branch dependencies: [Dependency and critical-path map](../DEPENDENCIES.md)
- Authority: No new MAPS_L, THINK/PLAN, experiment, external target, or merge authority

### D. Verification and usable evidence

- **D1. [PRESENT] Unit/property/CI, portable Run Record and criterion evidence** → `tests/`, `runtime/run_record.py`, `runtime/evaluation/`.
- **D2. [GAP] Provenance needs a real evaluation configuration.**
  - D2.1 [PRESENT structurally] L6 calculates harness configuration hash and can represent it.
  - D2.2 [GAP] No confirmed production call site consistently persists that hash on real manifests (the L6 DONE / L7 prerequisite inconsistency).
  - D2.3 [GAP L7] Harness-to-harness comparative evaluation has not happened; do not confuse test-case comparison utilities with a valid outcome trial.
- **D3. [CHECK] External acceptance proof reflects a real task outcome**, not only green tests or persuasive post-run prose.
- **D4. [CHECK] A failed review produces correction/retest, not an unearned completion claim.**
