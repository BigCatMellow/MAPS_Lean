# Parallel legacy archaeology — 2026-08-15

Status: `RESEARCH / PLANNING EVIDENCE — NOT ACTIVE AUTHORITY`

This report is an independent, bounded archaeology pass. It does not change runtime behavior, canonical task/session/policy authority, the master roadmap, the legacy-recovery audit/backlog, the reconciliation roadmap, or any implementation PR. The primary roadmap/reconciliation owner must decide whether any recommendation below is adopted.

## 1. Executive summary

Repository truth was re-checked before classification. At the final research snapshot, `main` remained `086e066f723d793273441dd52b500e62ac981deb` (merge of PR #19). PRs #20 through #36 were all open draft PRs and GitHub reported each as mergeable. PR #36 had advanced during this pass to head `e39793ba5580e7311d01b8c7fb767fa9b2849c72`, so the reconciliation file was re-read from that head rather than trusting the earlier snapshot.

The bounded pass found **one genuinely missing Lean-native capability worth recovering as a new candidate**:

- **risk-triggered user-visible acquisition-path verification** for release/package/install surfaces, recovered from `INS-0005 -> IDEA-0005 -> PROMO-0005 -> TASK-078`. The legacy checklist demonstrably addressed a real failure where source was fixed but users could still acquire a stale broken ZIP. PR #32 explicitly does not solve this general release/acquisition-path problem.

Most other useful unresolved legacy material should **fold into existing candidates**, especially:

- execution/session/helper/recovery lineage and explainable waits;
- Context Builder v2 evidence integrity;
- Layer 2/Layer 3 and end-to-end evaluation;
- controlled operational-learning promotion/expiry/supersession;
- bounded, evidence-triggered helper no-progress signaling;
- risk-specific adversarial review.

Several old mechanisms should not be revived: the supervisor/blackboard identity framing, permanent process/discovery roles, the old sentinel heuristics, remote-authority/classifier coupling, and legacy agent-registry mutation machinery. Their useful failure lessons can be retained without restoring their subsystems.

`EXP-0006` is confirmed as a **failed retrieval implementation with useful evidence-integrity techniques**. Its treatment scored only `17/41` exact-source accuracy, `7/41` anchored-evidence accuracy, and `2/5` correct negative abstentions; the decision was `revise`, not adopt. Its later corrections exposed five source files drifting after freeze and a false acceptable-substitute credit. The Lean roadmap should preserve the frozen holdout, exact anchors, hashes/drift, historical attribution, negative boundaries, and honest abstention/evidence scoring — **not** the lexical/TF-IDF claim-card retriever.

Two chains remain explicitly `UNKNOWN`: `SYN-0004`, whose body is mostly `TBD` and does not identify the complete approved/lost-fix chain, and `EXP-0007`, which is still `PROPOSED` with `result: pending` and therefore cannot be treated as validation of a startup discovery cadence.

## 2. Coverage performed

### Current repository / PR truth

Read on current `main`:

- `AGENTS.md`
- `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`
- `migration/FUTURE_IDEAS_BACKLOG.md`
- `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`
- current Lean state code needed to test supersession claims, especially `runtime/state/base.py` and `runtime/state/schema.sql`

Read from current PR #36 head `e39793ba5580e7311d01b8c7fb767fa9b2849c72`:

- `work/roadmaps/legacy-recovery-reconciliation.md`

Final open-PR snapshot used for overlap checking:

| PR | Head | Head SHA | Snapshot state |
|---|---|---|---|
| #20 | `agent/harness-foundation-wave1` | `ecfc2726` | OPEN / DRAFT / MERGEABLE |
| #21 | `agent/hcom-hooks-wave1` | `5d31410f` | OPEN / DRAFT / MERGEABLE |
| #22 | `agent/harness-service-wave1` | `9020476c` | OPEN / DRAFT / MERGEABLE |
| #23 | `agent/harness-canonical-guard-wave1` | `9456d324` | OPEN / DRAFT / MERGEABLE |
| #24 | `agent/agentic-security-baseline-wave1` | `3110457c` | OPEN / DRAFT / MERGEABLE |
| #25 | `agent/skills-format-wave2` | `f2985f3d` | OPEN / DRAFT / MERGEABLE |
| #26 | `agent/skills-catalog-wave2` | `56449828` | OPEN / DRAFT / MERGEABLE |
| #27 | `agent/skills-selection-eval-wave2` | `f6d6685b` | OPEN / DRAFT / MERGEABLE |
| #28 | `agent/environment-spec-wave2` | `6128ef94` | OPEN / DRAFT / MERGEABLE |
| #29 | `agent/environment-fingerprint-wave2` | `93e63fb4` | OPEN / DRAFT / MERGEABLE |
| #30 | `agent/environment-run-evidence-wave2` | `b7599bc7` | OPEN / DRAFT / MERGEABLE |
| #31 | `agent/skills-quality-gate-wave2` | `ace61318` | OPEN / DRAFT / MERGEABLE |
| #32 | `agent/review-subject-binding-wave2` | `489a2524` | OPEN / DRAFT / MERGEABLE |
| #33 | `agent/portable-run-record-wave2` | `3d618a4d` | OPEN / DRAFT / MERGEABLE |
| #34 | `agent/frozen-regression-case-wave2` | `aca786cf` | OPEN / DRAFT / MERGEABLE |
| #35 | `agent/regression-evaluator-wave2` | `5fac110b` | OPEN / DRAFT / MERGEABLE |
| #36 | `agent/legacy-recovery-roadmap-reconciliation` | `e39793ba` | OPEN / DRAFT / MERGEABLE |

This table records PR metadata state, not an independent re-run of every branch's CI.

### Legacy scope inspected

The pass concentrated on unresolved/system-relevant Emergence records and their direct chains, including:

- `INS-0005`, `INS-0007`, `INS-0010`, `INS-0014`, `INS-0016`, `INS-0022`, `INS-0023`, `INS-0032`, `INS-0034`, `INS-0037`, `INS-0042`, `INS-0045`, `INS-0047`, `INS-0050` through `INS-0056`, `INS-0059`, `INS-0061`;
- `SYN-0003`, `SYN-0004`;
- `IDEA-0012`, `IDEA-0013`, `IDEA-0030` and directly linked promotions/tasks where material;
- `EXP-0006`, `EXP-0007`;
- `workflow/task_graph.json` and specific task records needed to establish shipped/closed status.

The aggregate legacy `workflow/task_graph.json` was searched for current task states `RETIRED`, `ABANDONED`, `BLOCKED`, and `READY`; none were present in the checked-in aggregate at this snapshot. Therefore the abandoned-work portion of this pass centered on parked/proposed/unresolved Emergence chains, not on inventing retired task cases that current evidence does not show.

Unrelated project-specific legacy material was intentionally not exhaustively excavated.

## 3. New recoverable candidates

### 3.1 User-visible acquisition-path verification

**Classification: `RECOVER AS CANDIDATE`**

- **Legacy IDs / chain:** `INS-0005 -> IDEA-0005 -> PROMO-0005 -> TASK-078`.
- **Relevant paths:**
  - `legacy/MAP-System/MAP_System/emergence/insights/INS-0005-release-reviews-must-inspect-every-user-visible-acquisition-path.md`
  - `legacy/MAP-System/MAP_System/emergence/ideas/IDEA-0005-add-a-release-path-smoke-checklist-for-user-facing-packages.md`
  - `legacy/MAP-System/MAP_System/emergence/promotions/PROMO-0005-release-path-checklist.md`
  - `legacy/MAP-System/MAP_System/tasks/TASK-078.json`
  - `legacy/MAP-System/MAP_System/notes/release-path-checklist.md`
- **Underlying problem:** validating the source tree is insufficient when a user can acquire a different stale artifact, archive, installer, launcher, or documentation-directed path.
- **Evidence the problem was real:** the DarkMellow wallpaper fix existed in source, but a visible dated ZIP still contained the old installer and remained a plausible user download path. The bug therefore persisted for users despite a correct source fix.
- **Historical mechanism status:** **shipped** as an approved reusable checklist. `PROMO-0005` explicitly kept it advisory rather than a mandatory gate; `TASK-078` is `RELEASED`.
- **Current Lean / PR overlap:** PR #32 binds consequential reviews to immutable subjects and explicitly lists “no release publisher/acquisition-path system” as a deliberate non-feature. The current reconciliation likewise says general user-visible release/acquisition-path verification remains unsolved.
- **Smallest Lean-native capability worth preserving:** for tasks that actually publish or expose an operator/user acquisition path, require review evidence that enumerates the real reachable paths (for example release archive, install command, launcher, download link), verifies each against the intended immutable revision/content, and records explicit `N/A` where no such path exists. This should be derived review evidence, not a second artifact authority store.
- **Placement:** **later / evidence-triggered**, activated by an operator-visible/package/release risk predicate. It does not justify interrupting the current lineage/evaluation critical path or building a general artifact registry.

## 4. Findings that fold into existing roadmap items

### 4.1 Emergence lifecycle closeout

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0007`; linked cleanup/promotion work includes `TASK-065`, `TASK-075`, `TASK-078`, `TASK-081`.
- **Problem/evidence:** capture alone left `RAW`, `CANDIDATE`, and proposed records stale or placeholder-filled; later tasks were needed to close the lifecycle.
- **Historical status:** **partially then substantially shipped** in legacy through stale-record tooling, cleanup, and promotion closeout.
- **Current fit:** `NEXT E — Controlled operational-learning lifecycle` already requires proposal, evidence, review/promotion, expiry, supersession, and retirement.
- **Preserve:** lifecycle completeness and explicit stale/superseded states; do not revive the old Emergence subsystem as a second authority.
- **Placement:** **next**, as an acceptance invariant of NEXT E rather than a new candidate.

### 4.2 Process drift needs bounded verification, not a permanent steward

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0010 -> IDEA-0012 -> PROMO-0007 -> TASK-129`.
- **Problem/evidence:** complex MAP buildouts accumulated process drift that ordinary task-local attention did not reliably catch.
- **Historical status:** the original standing-role idea was narrowed and **shipped only as a bounded audit cycle**, not a new permanent identity.
- **Current fit:** reconciliation section “Bounded audits, not permanent agents” already preserves a periodic system-adherence audit.
- **Preserve:** bounded audit procedure and evidence-backed findings entering normal task/review channels.
- **Do not preserve:** a permanent process-police agent.
- **Placement:** **later / evidence-triggered** after substantial infrastructure change.

### 4.3 Mechanical gates are useful only for proven objective omissions

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0014` (linked to the TASK-129 adherence-audit evidence).
- **Problem/evidence:** mechanisms mechanically represented in release/task flow were actually used; prose-only systems were more easily skipped. The record also warns that gating everything produces box-checking ceremony.
- **Historical status:** **observed and selectively applied**, not a universal gate doctrine.
- **Current fit:** deterministic `maps flow` is already triggered/later; NEXT E needs selective active-guidance projection.
- **Preserve:** convert a repeated, objective, mechanically testable precondition into a narrow gate only after evidence shows the omission recurs.
- **Placement:** **later / evidence-triggered**.

### 4.4 End-to-end evaluation must prove an external workflow, not only inward infrastructure

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0023`.
- **Problem/evidence:** legacy MAP kept building internal infrastructure while lacking a convincing general external workflow that demonstrated the whole system delivered useful work.
- **Historical status:** **RAW observation; not shipped as a mechanism**.
- **Current fit:** `NEXT D` already calls for Layer 2/Layer 3 evaluation and an end-to-end scenario.
- **Preserve:** at least one Layer 3/end-to-end case should be a real operator-visible or externally meaningful workflow with an outcome, not only a synthetic infrastructure round trip.
- **Placement:** **next**, as an acceptance criterion for NEXT D.

### 4.5 Claim-evidence integrity, not the lexical claim-card retriever

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `SYN-0003 -> IDEA-0023 -> EXP-0006`; related vocabulary-shift evidence includes `INS-0035`.
- **Problem/evidence:** evidence attached only at file/task level loses exact claim provenance, historical version, negative boundary, and source-drift information. `EXP-0006` also demonstrated that a lexical/TF-IDF retriever performed poorly under behavior-level/paraphrased wording.
- **Historical status:** **experiment shipped; retrieval failed evaluation and was not promoted**. `EXP-0006` decision is `revise`. Headline results: task recall `12/23`, exact-source `17/41`, anchored-evidence `7/41`, negative abstention `2/5`, historical correctness `2/3`. Independent review found missing source-drift checking and false acceptable-substitute credit; after correction five of 29 frozen files were reported as drifted.
- **Current fit:** `NEXT C — Context Builder v2 evidence integrity` and PRs #27/#34/#35 frozen-evaluation work.
- **Preserve:** exact section/symbol anchors, source hashes/watermarks, drift reporting, task-time/historical attribution, proof role, explicit negative boundaries, frozen acceptable-evidence sets, honest `UNKNOWN`/abstention, and separate substitute scoring.
- **Do not preserve:** the old lexical claim-card retrieval implementation or its aggregate threshold approach.
- **Placement:** **next**, evaluation-first under NEXT C.

### 4.6 Promoted lessons must be selectively projected where applicable

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0032`.
- **Problem/evidence:** a process rule could be promoted into durable prose and still fail to change behavior because the actor never saw it at the applicable task moment.
- **Historical status:** **OPEN; not shipped**.
- **Current fit:** NEXT E plus Context Builder. The correct destination is scoped active guidance/context projection, not another policy database.
- **Preserve:** reviewed/promoted lessons should carry an applicability trigger and only project into task context when relevant; objective repeated predicates may later become deterministic checks.
- **Placement:** **next** as a NEXT E design requirement.

### 4.7 Reviewer drops, duplicate work, and unexplained waits are a lineage/communication problem

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0034`.
- **Problem/evidence:** dropped reviewers, stranded or duplicate reviews, liveness false signals, and unexplained waits repeatedly consumed coordination effort; retrieval was not the bottleneck.
- **Historical status:** **OPEN; not shipped**.
- **Current fit:** `NEXT A — Explicit execution lineage and communication coverage` and `NEXT B — Explainable waits`.
- **Preserve:** reconstructable request/thread/addressee/session/worker lineage and explicit wait reasons; never infer task truth from a live process.
- **Placement:** **next**.

### 4.8 “Process alive” is not “provider/API ready”

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0037`.
- **Problem/evidence:** spawned work could appear active while its first provider/API call was blocked on host firewall approval; parent connectivity checks did not prove child readiness.
- **Historical status:** **RAW; no promoted fix**.
- **Current fit:** NEXT A/B plus the EnvironmentSpec/fingerprint/run-evidence stack (#28-#30).
- **Preserve:** an explicit readiness/first-success or wait/unknown signal that distinguishes process existence from provider capability readiness. Never auto-approve a firewall or privileged capability from this signal.
- **Placement:** **next** as lineage/wait semantics; richer capability handling remains later.

### 4.9 Helper no-progress should be progress-sensitive and advisory

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0051 -> IDEA-0030`.
- **Problem/evidence:** non-core helpers/Haiku/local-model workers repeatedly failed silently, forcing manual polling; a fixed wall-clock timeout would also misclassify legitimately slow local models.
- **Historical status:** `INS-0051` is `LINKED`; `IDEA-0030` remains `CANDIDATE` with a bounded pilot recommendation. No production mechanism was established.
- **Current fit:** reconciliation already lists helper `NO_PROGRESS` as triggered/later and NEXT A as prerequisite lineage.
- **Preserve:** progress-sensitive observation (new status/terminal/evidence), read-only advisory signal, explicit false-positive measurement.
- **Do not preserve:** standing watcher role, auto-kill, or auto-escalation.
- **Placement:** **later / evidence-triggered** after lineage exists and recurrence can be measured.

### 4.10 Operational lessons may originate outside governed tasks without becoming authority

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0056 -> IDEA-0033 -> PROMO-0017`.
- **Problem/evidence:** operator-directed work intentionally outside MAP task governance could still produce reusable lessons, but a release-only capture trigger gave it no intake path.
- **Historical status:** **promoted** as an opt-in lightweight capture rule; the record explicitly says capture does not import the underlying work into task governance or create authority.
- **Current fit:** NEXT E controlled operational learning.
- **Preserve:** proposal/evidence intake may accept an observation from non-task work, but it enters as non-authoritative candidate evidence and needs the normal review/promotion path.
- **Placement:** **next** as a NEXT E boundary condition.

### 4.11 Privileged/cross-host lifecycle mutation deserves an adversarial review lens

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0059`, linked `TASK-307` and its review artifacts.
- **Problem/evidence:** three review rounds found two concrete vulnerabilities: restore state not bound tightly enough to authority-generated transfer state, and a rollback snapshot taken before `BEGIN IMMEDIATE`, creating a race window.
- **Historical status:** **RAW insight based on real review catches; no promotion recorded in the inspected chain**.
- **Current fit:** risk-specific review lenses already exist on `main`; PR #24 adds executable agentic-security adversarial cases.
- **Preserve:** trust-boundary/lifecycle mutation should trigger a security-framed behavioral review, with concurrency/atomicity considered separately from ordinary functional correctness.
- **Placement:** **next/later within the existing security-review candidate**, not a new reviewer bureaucracy.

### 4.12 Evidence references themselves must be regression-tested

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0061` (and as a related prior failure, `INS-0050`).
- **Problem/evidence:** legacy repeated-rework candidates had evidence line references pointing to unrelated events even when the aggregate count happened to be correct. A curator following the refs would inspect the wrong evidence. `EXP-0006` independently exposed another evidence-accounting failure via false substitute credit.
- **Historical status:** **RAW; scanner defect not established as safely fixed in the inspected record**.
- **Current fit:** NEXT C evidence integrity, NEXT D frozen regression cases, and NEXT E proposal evidence.
- **Preserve:** every consequential evidence ref should resolve to the claimed subject/event and be checked against frozen negative cases; count correctness is not sufficient if attribution is wrong.
- **Placement:** **next**, as an evidence-integrity acceptance property.

### 4.13 Prose-only rules need independent review and selective mechanization

**Classification: `FOLD INTO EXISTING CANDIDATE`**

- **Legacy:** `INS-0053`, linked `TASK-288`.
- **Problem/evidence:** even the agent that had just built a rule could miss it when the rule existed only in prose; independent review caught violations that same-actor rereading did not.
- **Historical status:** **OPEN**; the observation is evidence, not a shipped general solution.
- **Current fit:** current Lean already has no-self-review and independent review; NEXT E/triggered deterministic flows provide the remaining path for repeatedly missed objective rules.
- **Preserve:** independent review as the default cognitive-diversity mechanism; mechanize only objective repeated predicates, and selectively project reviewed guidance into applicable context.
- **Placement:** **later / evidence-triggered** except where it directly informs NEXT E design.

## 5. Items already solved in Lean

### 5.1 Validators must exercise live command surfaces

**Classification: `ALREADY SOLVED IN LEAN`**

- **Legacy:** `INS-0016`, linked `TASK-144`.
- **Problem/evidence:** documentation/schema validation could pass while live command surfaces accepted invalid state.
- **Historical status:** **promoted and fixed in legacy**.
- **Current Lean:** root operating rules require validation of real behavior; current runtime tests/CI and the #23/#24 guard/adversarial stack exercise behavioral surfaces rather than treating prose as proof.
- **Smallest preserved capability:** behavioral regression coverage through the actual mutation/guard interface.
- **Placement:** **not a separate candidate**.

### 5.2 Shaping-time contract mistakes are correctable without mutable active-task authority

**Classification: `ALREADY SOLVED IN LEAN`**

- **Legacy:** `INS-0042`, linked `TASK-274`.
- **Problem/evidence:** legacy output-path registration could be write-once, so a mistaken registration was difficult to correct safely and could poison conflict validation.
- **Historical status:** **RAW; no general legacy correction closeout established in the inspected record**.
- **Current Lean:** `runtime/state/base.py:update_contract()` permits transactional replacement of `output_paths` and other contract lists only while a task is `NEEDS_SHAPING` or `BLOCKED`; it resets AGI status and appends a contract-update event. Once active/reviewing/done, the contract is frozen. This is the Lean-native “how corrected” path the old system lacked.
- **Placement:** **not at all** as a new mechanism; preserve as a regression invariant.

### 5.3 Stale observer liveness is not allowed to become task/risk truth

**Classification: `ALREADY SOLVED IN LEAN`**

- **Legacy:** `INS-0045`, linked `TASK-236`.
- **Problem/evidence:** an advisory monitor could not reliably determine whether risk-register owners were live because it read stale roster/task mirrors; extending that monitor would create another liveness authority.
- **Historical status:** **RAW**, and the record itself warns against making the observer authoritative.
- **Current Lean:** the active architecture explicitly separates session liveness from task authority and requires one fact/one authority. Current `tasks` state has a simple `risk` field rather than the old separate risk-owner mirror, so the specific split-brain shape is not part of Lean's authority model.
- **Placement:** **not at all**; remaining session/helper correlation belongs to NEXT A, not a revived monitor.

### 5.4 Contradictory mirrors must not silently choose a winner

**Classification: `ALREADY SOLVED IN LEAN`**

- **Legacy:** `INS-0052`, linked `TASK-284`.
- **Problem/evidence:** indexers/reports reading multiple task mirrors could silently prefer one copy when they disagreed.
- **Historical status:** **promoted** into legacy review guidance.
- **Current Lean:** “one fact, one authority” and derived-view rules are explicit architecture laws; the SQLite task store is canonical and read models are projections.
- **Placement:** **not a separate candidate**; preserve as an invariant and regression review question.

## 6. Historical ideas that should not be revived

### 6.1 MAP as a giant supervisor/blackboard/swarm identity

**Classification: `HISTORICAL / DO NOT REVIVE`**

- **Legacy:** `INS-0022`.
- **Problem/evidence:** the observation described legacy MAP as a hybrid supervisor, durable blackboard, and swarm/handoff system.
- **Historical status:** **RAW architectural characterization**, not evidence that this shape is the minimal correct future architecture.
- **Current Lean:** canonical SQLite state, provider-neutral harness work, and derived projections preserve the useful durability/gate properties without a giant supervisor daemon.
- **Preserve:** durability, explicit gates, handoff evidence.
- **Do not preserve:** the all-encompassing supervisor/blackboard subsystem identity.
- **Placement:** **not at all**.

### 6.2 Legacy agent-registry FK correction machinery

**Classification: `HISTORICAL / DO NOT REVIVE`**

- **Legacy:** `INS-0047`, linked `TASK-273`.
- **Problem/evidence:** legacy `reassign_owner` could set a new owner without first validating/inserting that owner into the separate agents registry, causing a foreign-key failure.
- **Historical status:** **promoted and fixed in legacy** by validating the new owner before the FK update.
- **Current Lean:** `runtime/state/schema.sql` stores `tasks.owner` as task data without a foreign key to an agent registry; fixed roster/session data is explicitly not a second task authority plane.
- **Preserve:** validate sanctioned mutation inputs before committing.
- **Do not preserve:** an agents-table ownership bureaucracy solely to reproduce the old FK relationship.
- **Placement:** **not at all**.

### 6.3 Legacy emergence-sentinel aggregate heuristics

**Classification: `HISTORICAL / DO NOT REVIVE`**

- **Legacy:** `INS-0050`.
- **Problem/evidence:** the repeated-blocker signal attributed events emitted by a mechanism built by a task as if the task itself had been repeatedly blocked, producing false positives.
- **Historical status:** **RAW failure evidence**.
- **Current Lean:** there is no reason to restore this sentinel heuristic; later operational-learning proposals should use typed subject/actor/event attribution and frozen regression cases.
- **Preserve:** event subject/actor semantics and this incident as a possible negative test case.
- **Placement:** **not at all** as a subsystem.

### 6.4 Remote authority-host/classifier coupling

**Classification: `HISTORICAL / DO NOT REVIVE`**

- **Legacy:** `INS-0054 -> IDEA-0031 -> PROMO-0015`.
- **Problem/evidence:** sanctioned CLI verbs calling a remote MAP authority host could be blocked by a classifier; treating the denial as transient/retryable was unsafe.
- **Historical status:** **promoted as documentation**, explicitly rejecting automatic classifier exemptions/retries.
- **Current Lean:** this remote-authority-host/classifier coupling is not part of the Lean control-plane design.
- **Preserve:** a policy denial is not a transient network failure; privileged mutation should not be auto-retried through a safety denial.
- **Placement:** **not at all** as legacy architecture.

### 6.5 Release-time “emergence considered” checkbox as discovery machinery

**Classification: `HISTORICAL / DO NOT REVIVE`**

- **Legacy:** `INS-0055 -> IDEA-0032 -> PROMO-0016`.
- **Problem/evidence:** the mandatory checkbox could be checked without actually performing the intended discovery/analysis method.
- **Historical status:** **promoted as checklist wording/process change**, not validated autonomous discovery.
- **Current Lean:** controlled operational learning is planned separately; reconciliation already rejects permanent discovery/process-police agents.
- **Preserve:** ceremony without evidence is not compliance; use a mechanical gate only where an objective predicate exists.
- **Placement:** **not at all** as a universal release gate/discovery hook.

### 6.6 Permanent idea-scouting / discovery agent

**Classification: `HISTORICAL / DO NOT REVIVE`**

- **Legacy:** `IDEA-0013`; related `EXP-0003`/`EXP-0007` directions.
- **Problem/evidence:** useful observations were missed when discovery depended only on incidental task work, but the idea itself warned that a standing role could create more idea volume than review capacity.
- **Historical status:** **parked, reopened for bounded experimentation, never established as a justified permanent role**.
- **Current Lean:** reconciliation already preserves phase-boundary discovery as a bounded, proposal-only procedure with no idea quota and no automatic implementation.
- **Preserve:** bounded discovery passes, novelty checking, no-finding allowed, evidence-linked proposals.
- **Do not preserve:** permanent staffed discovery agent or autonomous idea generation bureaucracy.
- **Placement:** **not at all** as a permanent role.

## 7. Remaining UNKNOWN / unresolved chains

### 7.1 `SYN-0004` — “coverage debt lost its own fix”

**Classification: `UNKNOWN`**

- **Legacy:** `SYN-0004`.
- **Path:** `legacy/MAP-System/MAP_System/emergence/synthesis/SYN-0004-coverage-debt-lost-its-own-fix.md`.
- **Claim:** MAP approved a fix for losing ideas and later lost that fix, rediscovering it only after building tooling.
- **Why UNKNOWN:** the record is `CLARIFIED` but its pieces are still `TBD`, its second related insight is `TBD`, and its recommended next step is not selected. The inspected file does not identify enough of the promotion/task chain to determine exactly which mechanism was approved, lost, rediscovered, or whether current Lean still lacks it.
- **What is missing:** completed linked IDs, the approved artifact/task, evidence of the loss, and evidence of the rediscovery/closeout.
- **Placement:** no roadmap change until that evidence is located.

### 7.2 `EXP-0007` — idea scouting as startup cadence

**Classification: `UNKNOWN`**

- **Legacy:** `EXP-0007`, source `IDEA-0013`.
- **Path:** `legacy/MAP-System/MAP_System/emergence/experiments/EXP-0007-idea-scouting-as-cadence-not-role.md`.
- **Hypothesis:** a 14-day per-core-agent startup coverage cadence could reduce coverage debt without a staffed scouting role.
- **Why UNKNOWN:** status is `PROPOSED`; `result: pending`; no decision is selected. There is no evidence in this record that the 14-day test completed or that its success/failure criteria were evaluated.
- **What is missing:** actual run evidence, overdue/status-change measurements, and a reviewed decision.
- **Placement:** do not revive or cite this experiment as validation. Current bounded phase-boundary discovery can stand on its own rationale.

## 8. Recommended changes, if any, to the current reconciliation roadmap

These are recommendations to the primary reconciliation owner, not edits made by this branch.

1. **Add one small `TRIGGERED / LATER` candidate for user-visible acquisition-path verification.** Tie it to operator-visible/package/release work, not every task. Preserve the legacy checklist's real failure evidence but keep PR #32's “no general artifact registry” boundary.
2. **Strengthen NEXT C evidence-integrity acceptance criteria** with two concrete legacy failures:
   - an evidence reference must resolve to the event/anchor it claims (`INS-0061`);
   - acceptable-substitute credit is earned only when that substitute was actually retrieved/proven (`EXP-0006`).
   Also retain source-drift reporting against frozen hashes.
3. **Strengthen NEXT E controlled operational learning** with:
   - selective applicability projection (`INS-0032`), so promoted lessons do not remain inert prose;
   - proposal-only intake from operator-directed/non-task work (`INS-0056`), explicitly without importing that work into task authority.
4. **Strengthen NEXT A/B lineage/wait semantics** with the `INS-0037` distinction between process liveness and provider/API readiness, and use `INS-0034` as evidence that reviewer/request/thread lineage is a higher-value near-term problem than new retrieval machinery.
5. **Make NEXT D's end-to-end benchmark include at least one real external/operator-visible workflow** per `INS-0023`, not only a synthetic internal MAPS lifecycle test.
6. **Keep helper NO_PROGRESS triggered/later** and explicitly preserve `IDEA-0030`'s progress-sensitive, advisory-only boundary; do not use a naive fixed timeout or auto-kill behavior.
7. **Do not treat `EXP-0007` as validated evidence.** The bounded phase-boundary discovery procedure can remain, but the proposed startup cadence should stay historically unresolved unless its missing result is found.
8. **No roadmap change is recommended for the historical subsystem forms** in section 6. Their useful invariants are already represented elsewhere; reviving their architecture would add duplicate authority or bureaucracy.

## 9. Exact legacy evidence paths / IDs supporting conclusions

| Classification | Legacy ID(s) | Exact evidence path(s) | Lean/reconciliation overlap |
|---|---|---|---|
| `RECOVER AS CANDIDATE` | `INS-0005`, `IDEA-0005`, `PROMO-0005`, `TASK-078` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0005-release-reviews-must-inspect-every-user-visible-acquisition-path.md`; `legacy/MAP-System/MAP_System/emergence/ideas/IDEA-0005-add-a-release-path-smoke-checklist-for-user-facing-packages.md`; `legacy/MAP-System/MAP_System/emergence/promotions/PROMO-0005-release-path-checklist.md`; `legacy/MAP-System/MAP_System/tasks/TASK-078.json`; `legacy/MAP-System/MAP_System/notes/release-path-checklist.md` | PR #32; reconciliation §4.4 |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0007` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0007-emergence-records-need-lifecycle-closeout-not-just-capture.md` | reconciliation NEXT E |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0010`, `IDEA-0012`, `PROMO-0007`, `TASK-129` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0010-complex-map-system-buildouts-may-need-an-explicit-process-stewar.md`; `legacy/MAP-System/MAP_System/emergence/ideas/IDEA-0012-add-a-process-adherence-watcher-role-a-lightweight-role-that-che.md` | reconciliation §7.2 |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0014` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0014-systems-with-a-mechanical-release-task-gate-get-genuinely-used-r.md` | deterministic flow / NEXT E boundaries |
| `ALREADY SOLVED IN LEAN` | `INS-0016`, `TASK-144` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0016-validator-coverage-must-include-live-command-surfaces-not-only-d.md` | current tests/CI; PRs #23/#24 |
| `HISTORICAL / DO NOT REVIVE` | `INS-0022` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0022-obs-map-is-a-supervisor-durable-blackboard-swarm-handoff-hybrid-.md` | one-authority Lean architecture |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0023` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0023-obs-map-keeps-building-inward-infrastructure-without-a-working-b.md` | reconciliation NEXT D |
| `FOLD INTO EXISTING CANDIDATE` | `SYN-0003`, `IDEA-0023`, `EXP-0006`, `INS-0035` | `legacy/MAP-System/MAP_System/emergence/synthesis/SYN-0003-claim-addressed-evidence-units-connect-task-memory-to-exact-time.md`; `legacy/MAP-System/MAP_System/emergence/ideas/IDEA-0023-add-a-disposable-claim-evidence-projection-with-exact-anchors-ha.md`; `legacy/MAP-System/MAP_System/emergence/experiments/EXP-0006-a-frozen-holdout-can-test-claim-evidence-units-against-capsules-.md`; `legacy/MAP-System/MAP_System/emergence/insights/INS-0035-lexical-retrieval-is-brittle-under-vocabulary-shift.md` | reconciliation NEXT C; PRs #27/#34/#35 |
| `UNKNOWN` | `SYN-0004` | `legacy/MAP-System/MAP_System/emergence/synthesis/SYN-0004-coverage-debt-lost-its-own-fix.md` | audit remains |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0032` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0032-promoted-process-rules-stay-ineffective-unless-mechanically-surf.md` | reconciliation NEXT E / Context Builder |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0034` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0034-the-coordination-friction-this-session-keeps-hitting-reviewers-d.md` | reconciliation NEXT A/B |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0037` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0037-spawned-agent-blocks-on-firewall-approval.md` | NEXT A/B; PRs #28-#30 |
| `ALREADY SOLVED IN LEAN` | `INS-0042`, `TASK-274` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0042-output-paths-are-write-once-with-no-unregister-verb-so-a-mis-reg.md` | `runtime/state/base.py:update_contract()` |
| `ALREADY SOLVED IN LEAN` | `INS-0045`, `TASK-236` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0045-the-advisory-monitor-cannot-see-stale-owners-on-risk-register-en.md` | one-authority/liveness laws; `runtime/state/schema.sql` |
| `HISTORICAL / DO NOT REVIVE` | `INS-0047`, `TASK-273` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0047-reassign-owner-validates-the-task-s-status-but-never-the-new-own.md` | current `tasks.owner` has no agents-table FK |
| `HISTORICAL / DO NOT REVIVE` | `INS-0050` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0050-emergence-sentinel-py-s-repeated-blocker-signal-miscounts-operat.md` | future typed evidence/frozen eval only |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0051`, `IDEA-0030` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0051-non-core-agent-workers-visible-helpers-haiku-agents-local-pi-mod.md`; `legacy/MAP-System/MAP_System/emergence/ideas/IDEA-0030-add-a-bounded-liveness-no-progress-signal-for-hcom-dispatched-no.md` | helper NO_PROGRESS triggered/later; NEXT A |
| `ALREADY SOLVED IN LEAN` | `INS-0052`, `TASK-284` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0052-indexers-reports-reading-multiple-sources-of-truth-task-json-mir.md` | one-fact/one-authority law |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0053`, `TASK-288` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0053-prose-only-rules-get-missed-even-by-the-agent-who-just-built-the.md` | independent review + NEXT E / deterministic flows |
| `HISTORICAL / DO NOT REVIVE` | `INS-0054`, `IDEA-0031`, `PROMO-0015` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0054-sanctioned-cli-verbs-that-call-the-remote-map-authority-host-are.md`; `legacy/MAP-System/MAP_System/emergence/ideas/IDEA-0031-document-that-classifier-blocking-of-remote-map-authority-calls-.md` | old remote authority/classifier shape absent from Lean |
| `HISTORICAL / DO NOT REVIVE` | `INS-0055`, `IDEA-0032`, `PROMO-0016` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0055-the-mandatory-emergence-capture-considered-release-checkbox-neve.md`; `legacy/MAP-System/MAP_System/emergence/ideas/IDEA-0032-change-the-release-checklist-s-emergence-capture-considered-line.md` | no universal discovery gate |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0056`, `IDEA-0033`, `PROMO-0017` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0056-operator-directed-work-explicitly-scoped-outside-map-task-govern.md`; `legacy/MAP-System/MAP_System/emergence/ideas/IDEA-0033-document-lightweight-emergence-capture-outside-task-governance.md` | reconciliation NEXT E |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0059`, `TASK-307` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0059-cross-host-or-otherwise-privileged-gateway-code-that-mutates-lif.md` | risk review; PR #24 |
| `FOLD INTO EXISTING CANDIDATE` | `INS-0061` | `legacy/MAP-System/MAP_System/emergence/insights/INS-0061-emergence-sentinel-py-s-repeated-rework-signal-records-evidence-.md` | reconciliation NEXT C/D/E |
| `HISTORICAL / DO NOT REVIVE` | `IDEA-0013` | `legacy/MAP-System/MAP_System/emergence/ideas/IDEA-0013-add-an-idea-scouting-role-a-role-cadence-responsible-for-activel.md` | reconciliation §7.1 bounded discovery |
| `UNKNOWN` | `EXP-0007` | `legacy/MAP-System/MAP_System/emergence/experiments/EXP-0007-idea-scouting-as-cadence-not-role.md` | no validated result found |

Additional coverage evidence:

- legacy aggregate task state: `legacy/MAP-System/MAP_System/workflow/task_graph.json`
- task-file contract reference: `legacy/MAP-System/MAP_System/tasks/README.md`
- current Lean ownership/status schema: `runtime/state/schema.sql`
- current Lean shaping/correction implementation: `runtime/state/base.py`
- current reconciliation authority boundary and current candidate map: `work/roadmaps/legacy-recovery-reconciliation.md` on PR #36 head `e39793ba5580e7311d01b8c7fb767fa9b2849c72`

---

Research conclusion: the legacy archive still contains useful evidence, but this pass does **not** justify restoring any old subsystem wholesale. The strongest missing behavior is a narrow acquisition-path review capability; the rest of the useful unresolved material primarily sharpens capabilities already present in the current reconciliation roadmap.