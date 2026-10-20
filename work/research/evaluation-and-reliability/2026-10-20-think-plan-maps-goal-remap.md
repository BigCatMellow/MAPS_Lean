# THINK + PLAN candidate remap: MAPS_L success conditions, dependencies, first wave

- Record role: RESEARCH / PLANNING ASSESSMENT
- Information class: FACT / KNOWLEDGE + TASK CONTEXT (candidate only)
- Status: CANDIDATE FOR INDEPENDENT REVIEW; NOT APPROVED ROADMAP OR TASK AUTHORITY
- Date / evidence checkpoint: 2026-10-20
- Baseline: MAPS_L `main` at `69879cd0375f687c1df753fb5a4b83dda76b562e` (2026-10-06)
- Owner of the real program roadmap: [Master MAPS capability roadmap](../../roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md)
- Controls: [AGENTS.md](../../../AGENTS.md), [Project Bootstrap](../../../playbook/PROJECT_BOOTSTRAP.md), [Coordination](../../coordination/README.md)
- Methods being *manually* test-driven: [Pilot THINK](https://github.com/BigCatMellow/Pilot_Projects/blob/main/ai-creativity-and-ideation/THINK_PROJECT.md), [Pilot PLAN](https://github.com/BigCatMellow/Pilot_Projects/blob/main/complete-ai-work-system/roadmaps/05-PLAN-ORCHESTRATION-AND-TASK-COMPILATION.md), [Harada-inspired recursive candidate](https://github.com/BigCatMellow/Pilot_Projects/blob/main/harada-method/RESEARCH.md)
- Promotion/merge: independent review and ordinary MAPS_L authority/merge rules required; this record approves no implementation, spend, target access, benchmark execution, review, or merge

## 1. Precise purpose and evidence boundary

**Question:** If we derive MAPS_L's next milestone from its actual mission instead of treating all old checklist rows as compulsory, what success conditions, gaps, dependencies, and near-term work result?

**Provisional next milestone (not a replacement for the broader [master final target](../../roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md#19-final-target)):**

> An operator approves a bounded, real task in a previously unmanaged external repository. MAPS_L's portable method and available mechanisms support the task from shaping through execution, independent verification/review and legitimate integration, with target-isolated truth, observable interruptions and recoveries, preserved authority, and inspectable outcome evidence—without the operator repeatedly steering ordinary in-scope steps.

This tests a meaningful vertical slice, not *all* optional agent infrastructure. The external-pilot subroadmap defines v1's narrower formal DONE and its best-effort review-evidence policy; do **not** silently strengthen that approval envelope. See [Portable Deployment](../../roadmaps/agent-harness-capabilities/06-portable-deployment.md).

**This is a manual use of documented T&P-style reasoning**; no THINK/PLAN runtime ran or validated this assessment. The recursive Harada concept is a research adaptation, not a feature claimed for Harada's original fixed grid.

**Observed evidence sampled (not exhaustive):**
- Live GitHub on 2026-10-20 showed four open PRs: [#367](https://github.com/BigCatMellow/MAPS_Lean/pull/367), [#370](https://github.com/BigCatMellow/MAPS_Lean/pull/370), [#372](https://github.com/BigCatMellow/MAPS_Lean/pull/372), and [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341). Current `main` CI `test` succeeded at base SHA; PR checks also reported success at selected heads. **Green checks do not establish independent approval or merge authority.** Re-fetch live state before acting.
- [Runtime README](../../../runtime/README.md), source trees and selected source files verify real task state, harness, recovery, environment validation, Skills, outcome/learning, and CLI code, with corresponding `tests/` files. Sampling source and test presence is not the same as executing or exhaustively auditing them.
- The [capability checklist](../../roadmaps/CAPABILITY_CHECKLIST.md) records **29 DONE, 6 IN PROGRESS, 10 NOT STARTED** across 45 entries. It contains dated reconciliations (some older) and cannot be interpreted as current verified percentage completion. In particular, L6 is recorded DONE **even while its explanatory evidence says actual run-manifest harness hash persistence is absent**.
- [Current orientation snapshot](../../../state/CURRENT.md) (2026-10-06) identifies the open integration queue. Some snapshots are stale: e.g. its #371 child reference is now merged; live [#371](https://github.com/BigCatMellow/MAPS_Lean/pull/371) merged 2026-10-07. A merged design does **not** by itself satisfy #341's independent Arm C content-verdict gate.
- Pilot portfolio [PORTFOLIO.md](https://github.com/BigCatMellow/Pilot_Projects/blob/main/PORTFOLIO.md) treats #341's benchmark line as parked/blocked, THINK as monitor-only, and PLAN as primary. Its PR #33 live-status prose is stale (that PLAN PR merged October 13). Reconcile cross-project priority before promoting new research or moving #341.

**Unknown:** Current local deployments, target-project operator permissions, actual successful external runs, complete feature-head review evidence, and effectiveness versus simpler operation were **not** independently reproduced. Do not infer them from documentation or green CI.

## 2. THINK — necessary success conditions, expanded selectively

This is a **requirements/condition map**, *not* a GitHub-issue list. Each line is tagged:
- `PRESENT` — merged mechanism and some code/test evidence; integration adequacy not necessarily proven;
- `GAP` — documented exit criterion not yet supported by sufficient evidence;
- `CHECK` — condition depends on exact live proof or a material unknown;
- `TRIGGERED` — defer unless project/evidence activates it.

### A. Intent → justified work

- **A1. [PRESENT] Human objective and authority clearly bounded** → `AGENTS.md`, [Project Bootstrap](../../../playbook/PROJECT_BOOTSTRAP.md), canonical tasks.
  - A1.1 `DONE` and externally inspectable acceptance are defined before dispatch.
  - A1.2 Scope, permission, non-goals and consequential side-effect authority are explicit.
- **A2. [CHECK] Objective becomes the smallest necessary work** → current MAPS_L planning and task dependency model are the baseline.
  - A2.1 Existing task sufficient → **DO**, not automatic decomposition.
  - A2.2 Too vague → decompose the problematic branch recursively as far as needed.
  - A2.3 Missing information → investigate, not blindly add subtasks.
  - A2.4 Strategy itself wrong → return to THINK; new objective/authority → human.
- **A3. [GAP for promotion] New T&P/Harada planning adds measurable value** → already documented as unvalidated in Pilot. Compare against MAPS_L baseline; no automatic integration.

### B. Authorized execution and reliable continuity

- **B1. [PRESENT] Task state, routing, harness, workers and run identity** → `runtime/state/`, `runtime/routing/`, `runtime/harness/`, `runtime/integrity/`.
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
- **B3. [TRIGGERED] Full snapshots/rehydration (E7)** only if simpler reconstruction actually fails for the selected task family.

### C. Safety and genuinely independent judgment

- **C1. [PRESENT] Immutable/context-bound manifests, policy, review invariants and security baseline** → `runtime/integrity/`, `runtime/policy/`, `runtime/state/` and `tests/test_agentic_security_baseline.py`.
- **C2. [GAP SEC3] Confirm consequential external/destructive tool paths have *actual* security hook coverage**, not just a guard class and one call site.
- **C3. [GAP SEC4] Imported executable Skill/tool lifecycle is not fully proven end to end**; do not permit unreviewed content to activate in an external pilot.
- **C4. [CHECK] Independent review is bound to exact artifact/base/head; no author self-approval**, no bypass of [operator merge gate](../../../AGENTS.md).
- **C5. [TRIGGERED SEC6] Credential broker** requires genuine secret exposure/remote execution need; don't build for architecture elegance.

### D. Verification and usable evidence

- **D1. [PRESENT] Unit/property/CI, portable Run Record and criterion evidence** → `tests/`, `runtime/run_record.py`, `runtime/evaluation/`.
- **D2. [GAP] Provenance needs a real evaluation configuration.**
  - D2.1 [PRESENT structurally] L6 calculates harness configuration hash and can represent it.
  - D2.2 [GAP] No confirmed production call site consistently persists that hash on real manifests (the L6 DONE / L7 prerequisite inconsistency).
  - D2.3 [GAP L7] Harness-to-harness comparative evaluation has not happened; do not confuse test-case comparison utilities with a valid outcome trial.
- **D3. [CHECK] External acceptance proof reflects a real task outcome**, not only green tests or persuasive post-run prose.
- **D4. [CHECK] A failed review produces correction/retest, not an unearned completion claim.**

### E. Genuine external project operation

- **E1. [PRESENT design]** D0/D1/D2a–D2c: audit, target design, file-convention and sibling-clone adapter decisions.
- **E2. [GAP D3]** First real external pilot is unperformed per checklist and [deployment roadmap](../../roadmaps/agent-harness-capabilities/06-portable-deployment.md).
  - E2.1 [HUMAN BOUNDARY] Name target, real task, permitted repository writes/PR/review/merge, and external resource/tool access.
  - E2.2 [GAP] Establish target-local `.maps/`-style lightweight file discipline without touching MAPS_L's own state.
  - E2.3 [GAP] Demonstrate target task shape → implement → independent review → permitted merge, with inspectable evidence. A toy/synthetic smoke is supporting evidence **only**.
  - E2.4 [CHECK] Explicitly record any human intervention, handoff, stopped recovery, or non-ported feature to avoid overstating independence.
- **E3. [TRIGGERED]** D4 stack packs, D5 alternate-CI enforcement and D6 fleet management are **not** mandatory for one real pilot.

### F. Measurement and improvement without self-authorization

- **F1. [PRESENT]** Incident taxonomy, benchmark fixtures, append-only outcomes, lesson candidate/review storage.
- **F2. [GAP L4]** Experiments C–E not run; each needs its own failure-driven trigger and approved freeze.
- **F3. [GAP L7]** Credible comparison against a simpler baseline, with result/overhead/incident evidence.
- **F4. [TRIGGERED L8/L9]** Harness-level proposal-only refinement workflow and fork/time travel are not prerequisites to the first external task.
- **F5. [CHECK]** If outcomes are poor, evidence chooses the smallest corrective mechanism, not automatic new agents, databases, daemons, or permanent T&P integration.

### Cross-branch edges (not duplicate child trees)

- `A1 + C1/C4` → any consequential execution and independently accepted result.
- `B2.2 environment/worktree/authority compatibility + C2` → safe recovery in a real target; approval cannot be substituted by a planning branch.
- `E2.1` (target permission) + `E2.2` (state isolation) + `D1` (verification) → `E2.3` (real pilot).
- `D2.2` (run-level configuration identity) + `D3` (reliable outcomes) → `F3` (credible harness comparison).
- `F3` + scope-specific benefit + no safety regression → optional `A3` T&P integration and/or selective capability improvements.

No child node may recursively create new authority. **No arbitrary maximum number of levels or siblings.** Stop decomposing a node once its next justified test/action and proof are clear, or when missing evidence—not additional invented substeps—is the blocker. Deep branches may coexist with shallow leaves; do not materialize speculative descendants as tasks.

## 3. PLAN — dependency-informed critical path and dispositions

### Needed for the *next* external proof

`R0: current accepted baseline and PR/review truth`
→ `R1: identify only safety/continuity gaps that genuinely block the selected pilot`
→ `R2: confirm target and authority, scope and external task`
→ `R3: disposable smoke / target-isolation rehearsal`
→ `R4: actual external task + independent review + authorized merge`
→ `R5: outcome/provenance reconciliation and adversarial review`.

`C` (security) runs across R1–R5. `R1` can expose a concrete risk that must be fixed before R4; it does **not** imply implementing all security roadmap candidates first. Work not on this path remains conditional.

**Sequencing differs from the original feature-by-feature master wave model:** the first meaningful next *proof* is integrated external behavior. Conditional scaling or refinement capabilities should not be scheduled merely because a roadmap row remains NOT STARTED.

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

- Inputs: [Portable Deployment](../../roadmaps/agent-harness-capabilities/06-portable-deployment.md), target repository candidate and actual human-authorized scope.
- Existing design decisions: lightweight file convention, sibling clone/adapter, best-effort target review, stack-agnostic v1, target-local state.
- DONE for planning: real repo/task nomination, target access and permissions, non-goals, separate state path, human-only decisions explicitly recorded. No claim of a working pilot before execution.
- **HUMAN BOUNDARY**: target selection/access and side-effect permissions cannot be inferred from generic GitHub accessibility. Do not launch or merge external work from this proposal.

### W0.4 — Define end-to-end proof and comparator *before* a pilot

- Inputs: v1 D3 DONE; review/CI/Run Record capabilities; actual target acceptance.
- DONE: bounded acceptance fixture for: correct task and target, isolated state, no authority regression, independent review, accepted target integration, provenance, operator interventions, detectable recovery if exercised, real outcome, and no duplicate work. Also define a simpler baseline (e.g. standard agent-assisted task workflow with equivalent human authority and review).
- Stop: no valid comparator or no eligible reviewer → report `UNKNOWN`, not "MAPS_L beats baseline".
- No benchmark run, external mutation, model/API call, or research promotion is authorized by the fixture alone.

**Near-wave stopping condition:** Once current claims and risks are correctly classified and the target/authority decision is needed, stop *planning* rather than fabricate deeper detail. The first executable external tasks belong in a separately authorized pilot envelope, with fresh AGI/task readiness and independent verification.

## 5. Self-challenge and possible defects in this remap (not independent review)

1. **Risk of overstating the goal:** One real end-to-end task proves a bounded v1 slice, *not* general agent autonomy, fleet portability, or superior outcomes. Preserve the master's larger target.
2. **Risk of under-solving security:** Optional safety features are not optional when a task actually crosses their trust boundary. Select the pilot's action profile and audit exact call-site enforcement before operation.
3. **Risk of moving the goalposts:** Do not redefine D3 success after seeing an unsuccessful pilot; preserve the operator decisions and evidence contract.
4. **Risk of using Harada to manufacture work:** Broad candidate generation is not automatic scheduling. Keep nodes tagged candidate/unknown until needed; avoid 64 arbitrary tasks or uniformly deep trees.
5. **Risk of a false critical path:** A non-GitHub or multiple-worker pilot could move D5/E6 onto the path, while a simple repo might not. Recompute only affected branches after target selection.
6. **Risk of ignoring prior evidence:** The existing master, checklist, PLAN baseline and open-PR requirements already contain most of this structure. The **incremental** value claimed here is re-ranking toward an outcome proof, explicitly exposing cross-branch conditions and conditional/deferred items, not inventing new capabilities.
7. **Risk of stale status:** The 2026-10-20 PR/checklist observation is a dated snapshot. GitHub/live task truth wins at execution.
8. **Risk of unauthorized changes:** This research changes no runtime, commits no external task, assigns no TOWER/SENTINEL/SWITCHYARD role, merges nothing, and does not consume a parked research slot.

**Independent challenge still required** to test missing success conditions, real code coverage, dependency validity, unacceptable de-scopes, human authority, and whether this remap actually outperforms the old roadmap.

## 6. Test drive: does the T&P / recursive Harada adaptation add value?

For the *manual* test, compare:
- **Baseline:** existing master roadmap + D3 roadmap + capability checklist, without recursive expansion;
- **Candidate:** this goal-first success-condition map, with selective recursion and cross-branch dependencies.

Before crediting the candidate, have an independent reviewer identify and score:
1. **New, material omissions found** that the baseline truly missed (do not count renamed existing requirements).
2. **Incorrect or unsupported claims**, including inflated DONE declarations.
3. **Priority accuracy**: did the first wave focus on real blockers instead of optional capabilities?
4. **Dependency correctness**, particularly security, target authorization, review, and run-provenance.
5. **Planning overhead**: file size, tool calls, review burden, number of speculative tasks.
6. **Restraint**: correctly defers irrelevant features and can return `NO CHANGE`.

**Hypothesis:** a success-condition pass might make critical cross-branch dependencies clearer. **Counterhypothesis:** the existing MAPS_L Project Bootstrap already provides equivalent value; the new method is redundant. No adoption verdict is justified without a reviewed comparison.

## 7. Recommended disposition and next decision

**Candidate direction:** *prioritize a credible single-project external proof* after specific integration/safety prerequisites; maintain independent review; then conduct comparative measurement. Do not build a universal PLAN controller or add Harada directly to runtime. Prefer smallest path to a trustworthy outcome.

**Acceptance of this document means only that a planning proposal was prepared.** Independent review, explicit operator roadmap disposition and any needed target/implementation authority come next. Existing open PRs and project tasks retain their own owners, gates and precedence. This record is subordinate to [master roadmap](../../roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md), not an alternative source of task truth.
