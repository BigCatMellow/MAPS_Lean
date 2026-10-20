# PLAN: backward proof chain, prioritized work, and phase exits

- **Role:** candidate full-system execution roadmap from [goal](README.md), not a live task tracker or additional permission envelope
- **Inputs:** [dependencies](DEPENDENCIES.md), [historical status crosswalk](COVERAGE.md), [method](METHOD.md), current accepted code/task state
- **Replan after:** a completed real demonstration, a failed safety/evidence gate, a changed target or strategy, a new accepted operator boundary, or a repeat real-world incident

## Destination: complete MAPS_L operating-system proof

The [original master §§15–16](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md) sets ten program-level DONE properties and six end-state scenarios. The revised goal retains **all ten**: control, context, reproducibility, safety, coordination, evidence, review integrity, learning, human authority and complexity control. A single portable pilot is **one** early integration milestone, not the endpoint.

For full program acceptance, demonstrate the following **as appropriate to genuinely supported scope**, with immutable artifacts and independent challenge:

1. A fresh operator's ordinary-language objective becomes the **right scoped, testable goal**, with a valid simple-task direct path and proportionate decomposition for a complex task (**H01/H02**).
2. Supported workers execute through the normalized provider-neutral lifecycle, receive accurate minimal context and relevant Skills, and do not create a second task truth (**H02/H03/H05**).
3. A real (or risk-appropriately injected) interruption demonstrates correct lease/policy/environment/worktree compatibility, safe recovery and no duplicate external effect (**H04/H06**).
4. Unauthorized tool/Skill/side-effect attempts fail *at an actual enforcement boundary*; permissions/independent review cannot be laundered by workers or source text (**H06/H07**).
5. A substantive artifact has independently inspected acceptance, exact reviewed revision and retrievable task-to-outcome lineage (**H07**).
6. At least one **real previously unmanaged external repo** completes an accepted bounded task, with target state isolated, legitimate integration and actual outcome proof (**H08**).
7. Run-level configuration/evidence permits credible comparison against a simpler baseline; only supported improvements are proposed and explicitly authorized (**H09**).
8. New agents/operators can reproduce the workflow without repeatedly asking for ordinary steering or searching a giant documentation corpus; unsupported/optional capabilities are honestly `TRIGGERED` or `UNKNOWN`, not falsely completed (**H01/H08/H09**).

This is an **acceptance model**, not a mandate to enable every future API, Skill or fleet feature. A goal fails if its critical safety proof is missing, even when all checklist rows labeled DONE.

## End-state scenario coverage — original A–F plus newly proposed tests

The [original master scenarios A–F](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md) remain baseline acceptance cases. This is a **routing/coverage matrix**, not a claim that each test has been executed or passed.

| End-state scenario | Harada success conditions | Discriminating result / remaining proof |
| --- | --- | --- |
| **A — Ordinary coding task** (original) | H01, H02, H03.3, H04.1, H05, H07 | Correct accepted task, minimal context, real near-mutation validation, artifact-bound independent review, actual outcome; H4 timing still unproven broadly |
| **B — Prompt injection in repository** (original) | H05.1, H06.1–H06.3, H07 | Untrusted text cannot authorize deployment; actual before-external-action guard denies without side effect; SEC3 call-site coverage incomplete in source checklist |
| **C — Interrupted worker** (original) | H02, H04.3, H06.3, H07.5 | Stale lease, environment and scope incompatibility visibly deny/route correctly; no replay of ambiguous external effects; E5 not fully enforced |
| **D — Parallel writable agents** (original) | H02.4, H04.4, H06.2, H07 | Isolated writable worktrees, revision-bound integration, preserved separate work; E6 guard/dispatch coverage needs proof |
| **E — Imported third-party Skill** (original) | H05.2–H05.4, H06.4, H07 | Provenance/hash/activation/quarantine enforced on actual Skill load; a malicious Skill cannot become authoritative; SEC4 partial |
| **F — Repeated real-world failure** (original) | H07.5, H09.1–H09.6 | Outcome → frozen incident → fair config comparison → reviewed proposal/rollback; L6 real-run binding/L7 not yet proven |
| **G — Previously unmanaged external repo** (new) | H01–H08, particularly H08.3 | Real approved target/task, isolated portable discipline, independent review and authorized integration; D3 has no verified real pilot |
| **H — Natural-language goal with missing conditions** (new) | H01.1–H01.5, H02.2, H06.2 | Diagnose only necessary branches, resolve material unknowns, correctly stop at permission boundary and avoid invented task truth |
| **I — Repeat operation by a fresh owner** (new) | H02.4, H04.5, H07.6, H08.1/H08.7 | Fresh operator/agent can resume and reproduce a successful path with limited context and no hidden live-chat dependency |

**Acceptance discipline:** for any currently activated scenario, specify expected behavior, exact source/commit/environment, positive and negative cases, independently checkable evidence, and the limit of that proof. Synthetic fixtures are valid for adversarial checks but do not substitute for the real external task in G. A scenario is `UNKNOWN` until enough evidence supports it; no historical DONE status is upgraded by this mapping.

## Backward proof chain

```text
FULL MISSION PROVEN
 ← reproducible operator experience + reviewed outcome/reversion (H08/H09)
 ← external real task + internal varied tasks reviewed end to end (H07/H08)
 ← right work selected, bounded and executed with correct context (H01/H02/H03/H05)
 ← deterministic actual-boundary security/recovery/validation (H03/H04/H06)
 ← accepted task authority, source provenance and reproducible evidence (H01/H02/H07)
 ← current implemented baseline + inspected deficits (W0)
```

**Security and authority are parallel prerequisites**, not late-phase polish.

## Executable work-horizon plan

| Wave | Required outcome and minimum deliverable | Exit gate | Scope decision |
| --- | --- | --- | --- |
| **W0 — Truth** | Resolve baseline mismatches and all branch capability/permission evidence for selected near-term work, including L6's primitive-vs-real-run ambiguity; identify live owner/scope and critical gates | For chosen workflows, conditions classified `EVIDENCED/PARTIAL/UNKNOWN/UNMET/TRIGGERED`, with no unsupported DONE claim | Planning/research only; no blanket re-opening 45 items |
| **W1 — Trustworthy vertical control** | Audit actual H03.3/H04.3/H06.3/H07 call sites; close only safety/recovery/evidence defects shown to block approved high-value tasks; reconcile ongoing accepted PR integrations | Negative tests visibly block disallowed effects and invalid resumes; intended good path still functions | Scoped repairs under existing approved MAPS_L task/envelope and independent review |
| **W2 — Real external proof** | H08.3 first real external-project task, using accepted lightweight sibling-clone design, isolated target state, independent review and target outcome | D3 [portable subroadmap](../agent-harness-capabilities/06-portable-deployment.md) exact v1 DONE is met; failures/interventions recorded | Requires an operator-selected real target and explicit target write/PR/merge authority |
| **W3 — Broader integrated operation** | Exercise H01/H02 on complex multi-condition goal and repeated continuation, and H05 context/Skill correctness; prove operator-facing repeatability and H07 evidence | More than one representative task type works end-to-end without ad-hoc task-truth/permission exceptions; inspected failure and recovery coverage | Activate only tested branches and maintain normal concurrency/WIP limits |
| **W4 — Comparative results** | H09.2 true real-run configuration identity; freeze meaningful comparator; run approved L4/L7 relevant experiment; summarize operator friction, reliability, quality/cost and incidents | Independently reviewed outcome and disposition: accept/narrow/reject/no-change, with no unsafe auto-promotion | Experiment execution/scope/funding and independent evidence gates still apply |
| **W5 — Selective extensions / sustainment** | Fill remaining genuinely blocking program goal conditions; select triggered S7/E7/SEC6/L8/L9/D4–D6, H01.6/H05.5 etc **only when justified**; repeat real outcomes and reproducibility check | Full destination proof above holds; every deliberate omission is explained as not required / triggered | No automatic "implement all remaining rows" mandate |

Waves are a **rolling plan**, not a one-way waterfall. In W0/W1, read only the relevant branch and source; W3 can advance some authorized work while unrelated W2 target permission is pending, provided safety prerequisites and portfolio WIP permit it.

## Near-term first wave in implementable planning resolution

1. **W0.1 — Reconcile the actual code-to-requirement graph.** Read current accepted `main`/tests/CI and canonical task state; inspect the chosen active PR contract(s) only where they affect full-system dependencies. Acceptance: current and unverified facts separated; no stale PR ordering promoted to program law.
2. **W0.2 — Verify enforcement reality.** Inspect H03.3/H04.3/H06.3 and their tests; run/reproduce defined positive and negative scenarios using accepted available test environment. Acceptance: a bounded matrix listing each affected call site, expected effect, actual proof, source SHA, missing gap and shortest corrective path. **Do not treat a test name alone as a live test.**
3. **W0.3 — Audit intent and planning behavior.** On existing representative accepted tasks, compare direct/no decomposition and selective branch decomposition for correctness, omissions, complexity, intervention and decision quality. Acceptance: keep, narrow or reject the new method, with documented uncertainty.
4. **W0.4 — Identify external pilot eligibility.** Recover [D2c](../agent-harness-capabilities/06-portable-deployment.md) decisions; if no operator-nominated target/permission envelope exists, record exact boundary and continue *other authorized* work. No assumed external writes.
5. **W0.5 — Define outcome/control cases.** Retain original master Scenario A–F tests, clarify which paths are supported versus simulated, and set per-case evidence so the next wave can prove/falsify them.
6. **W0.6 — Plan accepted cross-project slots.** Reconcile portfolio stabilization and live MAPS_L priorities; full-roadmap inclusion does not authorize parallel activation of THINK, PLAN, benchmark and runtime refactors.

Each W0 item is a **candidate result**. An actual executable task inherits the accepted roadmap/permission envelope, one owner, bounded write paths, AGI readiness, independent reviewer when appropriate and stop conditions. No new permanent bureaucracy or nightly roadmap reports are requested.

## Wave-by-wave priority logic

- **P0 safety/authority correctness:** an actually exercised path can change, leak, destroy, falsely approve or wrongfully resume work.
- **P0 proof blockers:** without the result there is no meaningful real outcome/independent verification.
- **P1 integration/reliability:** removes a measured blocker for already-approved work.
- **P2 efficiency/portability expansion:** proven repeatable value, permitted after current proof.
- **TRIGGERED:** exact condition absent; remain parked; no success penalty for not implementing.
- **REJECT/SUPERSEDED:** preserve evidence and decision, do not re-queue.

Do not assign a permanent rank from branch number (H09 is not automatically later than H02). Critical-path rank is recomputed from **observed next-goal needs**.

## Finish / stop / strategy-reversal rules

- If an observed deficiency is merely a missing test or stale note, correct the evidence; don't rebuild working code.
- If a task can proceed under an accepted scope, do it; don't recursively plan every distant descendant.
- If a shared strategy assumption is falsified, route back to H01/THINK instead of indefinitely patching PLAN.
- If a permission/resource/subjective decision is outside the envelope, record the human boundary precisely; do not infer yes/no.
- If outcome/verification/review/operational independence is met, declare the bounded outcome DONE and stop inventing new subtasks.
- If the full-system destination cannot be proven, keep the exact failed condition and a minimal recovery/decision route visible; no unsupported global completion percentage.
