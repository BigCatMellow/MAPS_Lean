# H09 — Evaluation, outcomes, and controlled improvement

- **Record:** candidate success-condition branch, not a new task or authority source
- **Parent:** [Full MAPS_L goal map](../README.md) · **Dependencies:** [cross-branch graph](../DEPENDENCIES.md)
- **Coverage:** [45 checklist rows + 35 master capability areas](../COVERAGE.md)
- **Children stored separately:** [H09.3 — comparative outcome proof](H09.3-comparison.md)
- **Evidence checkpoint:** 2026-10-20, main `69879cd0375f687c1df753fb5a4b83dda76b562e`; current runtime and task evidence supersedes status prose

## Required outcome
MAPS_L detects actual failures, learns only from trustworthy outcome evidence, and advances a new mechanism only when the improvement is evaluated, reviewed, reversible, and proportionate to cost and risk.

## Recursive conditions
- **H09.1 — Reconstruct portable run/incident evidence.** Stable task/run/session/operation IDs, redacted Run Records, frozen incident cases and outcome reports rather than hidden model reasoning. **Proof:** an independent evaluator can re-check relevant claims without private runtime state.
- **H09.2 — Identify actual harness configuration.** L6 hashing exists, but the checklist explicitly says the production run-manifest wiring was missing; `DONE` for the primitive is not proof of persisted identity. **Proof:** real run records contain the correct effective harness config with stable hash.
- **H09.3 — Compare mechanisms against a credible baseline.** [Open H09.3](H09.3-comparison.md). L7 requires real-run identity and cost/quality/defect outcome evidence.
- **H09.4 — Preserve and verify incidents.** A repeated error earns a frozen regression case/test. Keep outcomes append-only with provenance, trust and revision linkage.
- **H09.5 — Operational lessons are proposals before promotion.** Review author/authority, evidence, failure modes, expiry and rollback; no automatic policy or Skill upgrade.
- **H09.6 — Controlled harness refinement.** L8 only after L7 demonstrates a real comparative improvement. No always-on self-modifying orchestrator.
- **H09.7 — Research experiments selectively.** Prior EXP-A/B outcomes are recorded; C–E require explicit questions, frozen cases and authority. L9 fork/time travel only after reproducible fixture and practical debugging need.
- **H09.8 — Measure results, not activity.** Escaped defects, operator interventions, repair time, successful task outcomes, unnecessary context, API/compute costs, regressions and false security blocks matter. Agent count, tool call count and automation count do not define success.

## Existing baseline
Checklist L1–L3, L5 and L6 primitive marked DONE; **L4 IN PROGRESS**; **L7–L9 NOT STARTED**. L6/L7 inconsistency requires independent current-state reconciliation. [Learning/evaluation technical roadmap](../../agent-harness-capabilities/05-learning-and-evaluation.md) owns detailed methods; Pilot THINK/PLAN experiment adoption remains separately gated.

## First comparison question
Given a properly identified configuration and frozen cases, does a candidate planning/selector/harness change improve task outcomes against the current MAPS_L baseline after accounting for safety, compute cost, review and operator effort? If not, keep the simpler mechanism.
