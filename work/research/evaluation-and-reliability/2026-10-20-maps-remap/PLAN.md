# PLAN — Open PRs and conditional capability dispositions

- Record role: RESEARCH / PLANNING ASSESSMENT
- Status: CANDIDATE / NOT APPROVED; evidence checkpoint 2026-10-20
- Parent: [MAPS_L goal remap / direct node index](../2026-10-20-think-plan-maps-goal-remap.md)
- Logical parent: MAPS_L proposed next milestone
- Child files: [Dependencies](DEPENDENCIES.md) · [First wave](FIRST-WAVE.md)
- Cross-branch dependencies: [Dependency and critical-path map](DEPENDENCIES.md)
- Authority: No new MAPS_L, THINK/PLAN, experiment, external target, or merge authority

### Existing PRs: distinct dispositions, no invented merge readiness

| PR | Relevance to the critical path | Candidate handling |
| --- | --- | --- |
| [#367](https://github.com/BigCatMellow/MAPS_Lean/pull/367) Protocol discoverability / global contract | High; independently revalidate exact current-head high-risk `AGENTS.md`/playbook semantics and integration before any merge; follow the required OPCMD gate. |
| [#370](https://github.com/BigCatMellow/MAPS_Lean/pull/370) Wiki methods orientation | Depends semantically on canonical protocol structure after #367; draft in the live snapshot. Do not treat it as a prerequisite for a working external pilot. |
| [#372](https://github.com/BigCatMellow/MAPS_Lean/pull/372) DecisionBroker / Jev seam | Valuable *candidate*, **not proven necessary for the external pilot**. Independent exact-head review, including authority, deterministic fallback and cost/privacy boundaries; only integrate if scoped goal/decision supports it. |
| [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341) protocol-effectiveness benchmark | Remains parked/blocked under Pilot portfolio unless deliberately promoted. [#371](https://github.com/BigCatMellow/MAPS_Lean/pull/371) design merged into #341 branch, not evidence that Gate 1 independent Arm C judgment or later hidden-material gates have passed. No benchmark execution authority. |

### All 16 unfinished checklist rows — not a blanket todo list

| ID | Classification in historical checklist | Proposed next-pilot disposition |
| --- | --- | --- |
| H4 | IN PROGRESS | Check actual mutation/validation gate; fix the specific safety gap if the pilot exercises it |
| E5 | IN PROGRESS | High-risk recovery compatibility check; establish fail-closed coverage for the chosen recovery path |
| E6 | IN PROGRESS | Worktree isolation enforcement verification; triggered by observed collisions |
| SEC3 | IN PROGRESS | Audit consequential call sites; repair gaps necessary for approved pilot operations |
| SEC4 | IN PROGRESS | Gate imported executable Skill/tool activation in scope; other supply-chain additions conditional |
| L4 | IN PROGRESS | Preserve prior EXP-A/B evidence; C–E only with an authorized focused research need |
| S7 | NOT STARTED | Defer Capability Packs absent repeated capability packaging need |
| E7 | NOT STARTED | Defer snapshots/rehydration absent reconstruction failure |
| SEC6 | NOT STARTED | Defer credential broker until secret/remote-boundary trigger |
| L7 | NOT STARTED | Outcome-comparison work after configuration/run evidence and pilot data |
| L8 | NOT STARTED | Defer automatic harness-refinement proposal mechanism; use human-reviewed recommendations first |
| L9 | NOT STARTED | Defer fork/time-travel until measured need |
| D3 | NOT STARTED | **Highest-value external validation milestone**, human target/authority required |
| D4 | NOT STARTED | Defer stack-specific packs until a second stack actually needs one |
| D5 | NOT STARTED | Defer alternate-CI portability until non-GitHub target demands it |
| D6 | NOT STARTED | Defer fleet/multi-project orchestration until single-project evidence supports scaling |

**Important contradiction to reconcile:** L6 is recorded `DONE` but its own row says the real-run harness config hash is not actually persisted; L7's dependency states this explicitly. Verify the implementation and amend the evidence status at the owning checklist when authorized, rather than fabricating comparable configurations.
