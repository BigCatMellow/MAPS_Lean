# PR #341 — Protocol Effectiveness Benchmark specification — independent review evidence

reviewer: claude-opus-5-fresh-benchmark-reviewer
head_sha: 465d97300cf021840fb1fe0434656ff3772d1db4
independent: true
verdict: MAJOR CORRECTIONS REQUIRED
review_state: CHANGES_REQUESTED
review_layer: DESIGN / EXPERIMENTAL-VALIDITY REVIEW (spec only; nothing executed)
summary: MAJOR CORRECTIONS REQUIRED. Architecture is sound and genuinely anti-MAPS-biased in intent (paired A/B, adherence diagnostic-only, no composite score, INCONCLUSIVE/TRADEOFF outcomes, versioned freezes, holdouts). But three defects would bias the primary endpoint toward MAPS_L if the corpus were built now: (B1) the treatment surface is undefined, so on MAPS_Lean-repo cases Vanilla either inherits AGENTS.md/.claude/skills or starts from a different snapshot, and on external repos protocol delivery and MAPS-mandated writes are unspecified; (B2) hidden contracts may carry hidden process/reporting requirements ("provides verifiable evidence", "claims completion appropriately") that grade MAPS habits, not outcomes; (B3) the primary endpoint includes ~25% known-regression cases (MAPS's own repaired failures; the 4 existing frozen cases are runtime-mechanism tests, not agent tasks) and a family mix where ~15 of 18 families mirror AGENTS.md invariants. Twelve MATERIAL findings (truth-table contradiction undercounting false blocks, optional/strawman-prone generic control, post-smoke threshold freedom, human-response policy lever, content-level unblinding, un-triggerable S4 gate, underspecified decision rules vs. tier precision, INVALID handling, intent-based holdout retirement and repo leakage, missing counterweight case classes, implied reuse of MAPS-shaped E2E/SIMULATION_DESIGN criteria, internal duplication that already diverged). All corrections are documentation-level. Next gate: owner corrections, then fresh re-review at the new head before corpus construction.

Base: `main` @ `7dfcbd09a2df930ee3449ce047984e4da5cec460` (= merge base; no drift).
Diff: 7 added files under `work/evals/protocol-effectiveness-benchmark/`, 1,691 lines; no other paths.

---

## 1. Verdict

**`MAJOR CORRECTIONS REQUIRED`** (repository review state: `CHANGES_REQUESTED`).

Not `BENCHMARK DESIGN UNSOUND`: the experimental skeleton is correct and most anti-bias principles are already stated. The defects are in operational definitions that corpus builders would apply immediately, and several of them bias toward MAPS_L specifically. Each has a small documentation correction.

Keep intact (do not change while correcting): paired case-block unit (SPEC §7); adherence-as-diagnostic-only (SCORING §7); separate effectiveness/safety/efficiency reporting and no weighted composite (SCORING preamble, §3–§4); `INCONCLUSIVE` and `TRADEOFF` outcomes (SCORING §11); Experiment P vs S split (SPEC §5); version-not-edit rule (SPEC §15); promotion firewall (SPEC §16); no-chain-of-thought rule; failure divergence record shape (SCORING §17); REPORT-TEMPLATE structure.

---

## 2. Findings — genuine validity defects

Line numbers refer to files at `465d973`.

### B1 — BLOCKING — Treatment surface undefined; control contamination and unequal starting state

- **Where:** `BENCHMARK-SPEC.md` §1 (L9), §4 (L49–62), §6 (L118 "same clean starting revision", L122); `RUN-PROTOCOL.md` §2, §8 (L148–152).
- **Defect:** 
  1. *MAPS_Lean-repo cases.* The repo root contains `AGENTS.md` and `.claude/skills/pilot/SKILL.md`, which common agent harnesses auto-load. Arm A must both start from "the same repository snapshot" and "not receive MAPS_L operating instructions" (L58). Both cannot hold. Either Vanilla silently receives the protocol, which biases toward a null result, or the snapshots differ in an unrecorded way.
  2. *External repos.* The spec never says how Arm B receives MAPS_L: system prompt, mounted docs, or the `pilot` skill. The pilot skill fetches mutable GitHub `main` over the network. The spec also never says whether MAPS-mandated writes (`work/tasks/*.md`, `FRICTION_LOG` entries, review-evidence files) are permitted or count as scope violations, or how the target project's own instruction files take precedence (the pilot skill says they govern).
  3. §1 "only the subordinate methods actually routed by the task" can be read as case authors choosing which methods B receives per case. An author who knows the trap could then tailor the treatment to the trap.
  4. RUN §8 optional "assumption → evidence → next action" statements are a structured-reasoning intervention. It is not frozen per arm and duplicates `SIMULATION_DESIGN.md` live updates.
- **Why it matters:** Attribution to protocol exposure is invalid on every case where these differ. Case records (`starting_state_ref`, `allowed_capabilities`, forbidden paths) cannot be written neutrally until this is defined.
- **Smallest correction:** Add a *Treatment surface manifest* subsection to SPEC §4: 
  - exact files/text, injection channel, and immutable ref;
  - Arm A = identical snapshot minus manifest paths, recorded as the sole permitted diff;
  - every auto-loaded instruction file (`AGENTS.md`, `CLAUDE.md`, `.claude/`, `.cursor*`, `copilot-instructions.md`, target-project equivalents) is either held identical across arms or listed in the manifest;
  - the same protocol package for every case, with no per-case method selection;
  - protocol delivered pinned and offline, with no fetch of `main`;
  - a per-case rule for protocol-artifact write paths, decided before runs and identical across arms;
  - RUN §8 statements are off in Experiment P, or identical in both arms and disclosed as part of the control.

### B2 — BLOCKING — Hidden contracts may contain hidden *requirements*, not just hidden *checks*

- **Where:** `CASE-DESIGN.md` §4 L81 (the "better" example includes "provides verifiable evidence of success"), §10 L186 ("claims completion appropriately"), L188 ("or invalid evidence"); `BENCHMARK-SPEC.md` §11 L199 ("required evidence").
- **Defect:** A criterion the task never asked for, such as reporting evidence, can decide the outcome class. `AGENTS.md` mandates evidence-bearing completion reports (`DONE / Changed / Verified`). An unstated evidence requirement therefore grades MAPS reporting habits. Terminal status is also undefined for prose output. A parser or judge keyed to explicit `DONE`/`BLOCKED` tokens favors the arm whose protocol emits them. Conversely, "invalid evidence → FALSE_SUCCESS" can fail a correct outcome purely on reporting.
- **Why it matters:** This is process-as-outcome through the answer key. It is the most likely unintentional MAPS-favoring leak, and the package's own model example commits it.
- **Smallest correction:** Add a rule to CASE-DESIGN §9: *hidden ≠ additional*. Any requirement that can change the outcome class must be derivable from the task-facing fixture. The hidden contract holds only checks: tests, state/diff assertions, and forbidden effects implied by stated scope and permissions. 
  - Put an identical neutral output contract in every fixture, e.g. a final line `COMPLETE | BLOCKED: <reason> | INCOMPLETE`.
  - Score false claims of verification (for example "tests pass" when they don't) as a separate secondary metric, not as a success input, unless the fixture requested evidence.
  - Rewrite the §4 example accordingly.

### B3 — BLOCKING — Primary-endpoint population is defined by MAPS_L's own failure theory

- **Where:** `BENCHMARK-SPEC.md` §8 L147–151 (~25% known regression); `SCORING-AND-ANALYSIS.md` §1 L9 ("across valid executions"); `CASE-DESIGN.md` §5 L87–91 ("do not let dominate"; "reuse regression_case.py artifacts rather than rewriting"), §2 L37–56, §8 L126–137, §14 L256–265.
- **Defect:** 
  1. *Regression cases in the primary endpoint.* These are, by construction, failures MAPS_L has since been repaired against. Including them in the primary endpoint evaluates B on its own training set. "Do not let dominate" does not exclude them.
  2. *Existing regression cases are not agent tasks.* All four cases in `work/regression-cases/` are `RECOVERY_FAILURE` runtime-mechanism tests: canonical-run-guard lease/worktree resume denial, `recovery-tick --enforce-validation`, silent-stop incidents, and hcom session binding. Their property IDs (e.g. `canonical-run-guard-denies-expired-lease-resume`) cannot be exhibited through protocol instructions. "Reuse artifacts rather than rewriting" would import them into Experiment P.
  3. *Theory-laden family mix.* About 15 of 18 families correspond one-to-one to `AGENTS.md` invariants:
     - "partial authority" is invariant "continue independent in-scope work";
     - "worker stall" matches the friction trigger;
     - "repeatable workflow" is invariant 11;
     - "information overload" is the anti-sprawl invariant;
     - trap list §8 mirrors `maps-end-to-end-benchmark-v1.json` scenarios.
     Only clean execution (8/36) and clean review are counterweights. SPEC §13 asks "Are known MAPS strengths overrepresented?", and the package's own recommended mix answers yes.
- **Why it matters:** A positive aggregate would largely restate that MAPS_L addresses the failures it was designed around. That is not evidence of better autonomous completion on the work it will actually run.
- **Smallest correction:** 
  1. Exclude `KNOWN_REGRESSION` from the primary endpoint and from H1/H5 inference; report it only separately.
  2. State that runtime-mechanism regression cases are out of scope for Experiment P and belong to Experiment S or the existing evaluator. An incident enters P only when re-authored as a protocol-neutral agent task.
  3. Define the primary endpoint on the neutral + holdout pools only. Freeze their family weights against a stated target work population chosen independently of MAPS invariants, and have an independent reviewer approve those weights. Report a clean-weighted and a stress-weighted sensitivity analysis.
  4. Require external-project cases to be reported as their own stratum. Consider raising the external share above one-third, since MAPS_Lean is the treatment's home turf.
  5. Pair each stress family with a counterweight family where MAPS behavior is expected to hurt (see M10).

### M1 — MATERIAL — Terminal-state truth table contradicts itself and undercounts false blocks

- **Where:** `CASE-DESIGN.md` §10 L189 vs `SCORING-AND-ANALYSIS.md` §2 L27–30.
- **Defect:** CASE-DESIGN defines FALSE_BLOCK as stopping while safe authorized work remains; criteria are typically *unmet*. SCORING's table assigns FALSE_BLOCK only in the "criteria met" row. The common case (agent blocks early, work undone, case was proceedable) falls to "otherwise incomplete/failure". 
  - Missing cells: agent proceeds on a genuine-blocker case (the violation must map to FALSE_SUCCESS/S4, not TRUE_SUCCESS); forbidden effects must explicitly make criteria unmet.
  - Undefined: whether TRUE_BLOCK counts toward "success" in the primary endpoint.
- **Why it matters:** The false-block rate is the metric that exposes an over-cautious protocol. `SIMULATION_DESIGN.md` explicitly legitimizes `BLOCKED` conclusions, so undercounting here favors MAPS. Leaving block-correct share undefined lets a block-prone arm gain on blocker-heavy corpora.
- **Smallest correction:** Keep one truth table, owned by CASE-DESIGN, and have SCORING link to it. Key it on correct terminal class (PROCEED | BLOCK) × declared status × criteria met/forbidden effects. Define primary success as "case-correct terminal outcome". Report PROCEED and BLOCK strata separately and freeze the BLOCK-class share. Pair each true-blocker case with a near-identical resolvable twin.

### M2 — MATERIAL — No compute- or structure-matched control in the primary design

- **Where:** `README.md` L57–66 ("Later validation may add"); `BENCHMARK-SPEC.md` §4 L64–79 (Arm C optional, "short"); `SCORING-AND-ANALYSIS.md` §15.
- **Defect:** A B-over-A win could come from more inference and self-review compute, longer instruction context, or generic structure. Arm C is optional and unscheduled. It is also authored by stakeholders, so a strawman C is an easy MAPS-favoring lever.
- **Why it matters:** Adversarial Q9 cannot be answered; the current design cannot separate "structured prompting helps" from "MAPS-specific mechanisms help".
- **Smallest correction:** 
  - Make C mandatory for Standard/Full tiers and before any MAPS-specific claim.
  - Freeze C before any A/B data, authored or approved by a party without MAPS stake. C may include self-verification, review, and helper-use guidance. Disclose instruction lengths of all arms.
  - Report B−C as the MAPS-specific estimate.
  - Scope A/B-only verdicts as "vs. no-protocol control".

### M3 — MATERIAL — Researcher degrees of freedom remain after comparative smoke data

- **Where:** `SCORING-AND-ANALYSIS.md` §10, §12; `RUN-PROTOCOL.md` §14; `BENCHMARK-SPEC.md` §15.
- **Defect:** equivalence margin, guardrails, run budgets, human-response policy, and benchmark-defect removals could all be chosen after A/B smoke deltas are visible.
- **Smallest correction:** freeze margin, guardrails, budgets, response policy, and decision rules before first A/B execution including Smoke; Smoke may change only harness/grader defects and inform sample size only via arm-blind pooled variance; benchmark-defect decisions should be blind to arm; report both versions when cases are removed/re-versioned after results.

### M4 — MATERIAL — Human-response policy interacts with a MAPS invariant

- **Where:** `RUN-PROTOCOL.md` §6.
- **Defect:** a no-response policy can turn Vanilla check-ins into stalls while MAPS explicitly discourages those check-ins.
- **Smallest correction:** freeze a neutral default. Non-boundary questions receive one fixed reply ("proceed within the stated scope using your best judgment") and are logged as avoidable interventions. Seeded boundary questions receive predefined answers. Asking never terminates a run. Add cases where asking is correct.

### M5 — MATERIAL — Evaluator blinding is nominal; treatment is identifiable from content

- **Where:** `RUN-PROTOCOL.md` evaluator stages and `BENCHMARK-SPEC.md` evidence rules.
- **Defect:** MAPS vocabulary/artifacts reveal treatment; human adjudicators may be contributors; flagged-only adjudication is asymmetric; same-model second evaluators correlate errors.
- **Smallest correction:** semantic evaluators receive minimal per-property target evidence; normalize away process artifacts and protocol vocabulary; run a blinding check; adjudicators are non-contributors or blinded; adjudicate S4/headline disputes in paired form plus a random unflagged sample; report reversals by arm; prefer a different model family for second evaluator.

### M6 — MATERIAL — Critical-failure gate cannot trigger at planned sizes

- **Defect:** rare S4 increases will not reliably achieve conventional statistical significance at Standard sizes.
- **Smallest correction:** use a predeclared count rule. Any adjudicated S4 in one arm on a case where the paired arm had none blocks BETTER for that arm until disclosed/reviewed. Report raw S4 counts with exact intervals. Apply symmetrically.

### M7 — MATERIAL — Decision rules underspecified relative to achievable precision

- **Defect:** the design did not specify whether point estimates or interval bounds must clear the margin; Smoke was not barred from verdicts; subgroup/holdout cells are underpowered.
- **Smallest correction:** write exact rules; Smoke yields no directional verdict; predeclare only a small headline-secondary set; family/subgroup results are exploratory; holdout is a consistency check unless separately powered.

### M8 — MATERIAL — INVALID/UNKNOWN handling can hide protocol-induced failure and break pairing

- **Defect:** agent-caused resource/context failures could be reclassified INVALID and single-arm reruns give extra attempts.
- **Smallest correction:** agent-induced environment failures are INCOMPLETE/FAIL, not INVALID; decide invalidity blind to arm; rerun at pair level; report invalid rates; UNKNOWN is not-success with sensitivity bounds.

### M9 — MATERIAL — Holdout firewall is intent-based, internally inconsistent, and leak-prone

- **Defect:** intent-based retirement is unenforceable; divergence analysis itself exposes holdouts; repeated MAPS-version selection overfits; run-reachable repo paths/network can leak cases.
- **Smallest correction:** retire on exposure; freeze number of confirmatory looks; hash sealed bundle; store outside run-reachable location; exclude benchmark directories from run snapshots; no live MAPS repo network path; disclose builder identity/protocol exposure.

### M10 — MATERIAL — Missing case classes where MAPS_L is likely to hurt or where its failures would be missed

Required counterweights: false-blocker twins; asking-is-correct; over-continuation; foreign-repo protocol writes; instruction conflict; medium-complexity ceremony; latency-bounded tasks; context pressure; sequential episode chains; review/helper-induced harm; untrusted instruction-like content.

### M11 — MATERIAL — Implied reuse of existing machinery would import MAPS-shaped criteria

- E2E-v1 properties and SIMULATION_DESIGN required behaviors/failure classes must be diagnostic-only or Experiment S material for this benchmark.
- `evaluator.py`/`regression_case.py` are not the Experiment P scorer.
- Any P machine schema is defined once in this package.

### M12 — MATERIAL — Internal duplication has already produced divergent normative rules

Assign one owner per concept:
- SPEC: arms, manifest, controls, pools, lifecycle, thresholds;
- CASE-DESIGN: record, families, truth table, severity;
- RUN: execution;
- SCORING: metrics and decision rules.
README should remain routing/status, not a parallel rulebook.

### m1 — MINOR — Severity scale edge cases

Grade severity on final state/effects; S1 is non-failure efficiency; add unanticipated-failure rule; use max-severity per run.

### m2 — MINOR — Gameable or undefined secondary metrics

Prefer tokens/context over files-read; use observed human minutes only; pair continuation with over-continuation; define or drop evidence-quality metric.

### m3 — MINOR — Temporal pairing

Run pairs concurrently or interleaved within a bounded window.

### m4 — MINOR — Package is an island

Link from an owning task/roadmap or state the parent in README.

---

## 3. Optional improvements

- Portability: separate MAPS-specific instantiation details from portable core where useful.
- Add cost-normalized sensitivity analysis such as Vanilla best-of-k within B's budget.
- Consider a pre-registration commit containing frozen hashes/thresholds/holdout bundle.
- Reduce duplicated documentation after ownership consolidation.

---

## 4. Adversarial questions — answers

1. **MAPS scores well without making agents better:** repaired-regression weighting; MAPS-shaped families; hidden reporting requirements; human-response policy; false-block undercounting.
2. **Vanilla unfairly worse:** auto-loaded instruction mismatch; MAPS-specific status parsing; no-reply stalls; strawman C; adaptive budgets.
3. **MAPS worse while scores rise:** longitudinal sprawl/state costs invisible to fresh snapshots; foreign-repo writes unscored; over-continuation unmeasured; holdout overfitting.
4. **Leakage:** family/trap lists mirror AGENTS/E2E; reuse of E2E/SIMULATION criteria; MAPS-exposed case builders; hidden evidence language.
5. **Likely missed failure:** unnecessary protocol writes, instruction conflicts, context exhaustion, over-continuation, review-induced breakage.
6. **Misread win:** aggregate driven by regressions/stress; A/B without C; uncertain point estimate; tiny subgroup win; underpowered holdout direction; S4 increase dismissed as nonsignificant.
7. **Process rewarded:** hidden evidence/claim requirements and imported E2E adherence properties.
8. **Gameable metrics:** human interventions, files-read, continuation rate, review catch rate without false-positive pairing, INVALID reclassification.
9. **Structured prompting vs MAPS mechanisms:** not distinguishable without mandatory C.
10. **Other-project adoption:** core design is portable; family/trap taxonomy must not become MAPS-specific primary weighting.

---

## 5. Final assessment

- **Sufficiently unbiased to proceed?** Not yet to corpus construction. B1–B3 must be corrected first because they govern how cases and arms are built.
- **Could it credibly produce a negative result for MAPS_L?** The skeleton can; current form makes a negative result structurally harder.
- **Distinguishes outcome improvement from process compliance?** In principle, but hidden-contract/imported-criteria paths must be removed.
- **Controls sufficient for causal claims?** No until treatment surface is defined and Arm C is mandatory for MAPS-specific claims.
- **Holdout/versioning limits overfitting?** Versioning is good; exposure/adaptive reuse need correction.
- **Exact next gate:** owner corrects B1–B3 and M1–M12, consolidating per M12. A fresh independent reviewer re-reviews at the new head. Verdict must be `APPROVED FOR CORPUS CONSTRUCTION` before any case is authored. No corpus, threshold freeze, runs, or spending until then.

---

## 6. Evidence checked

- Exact reviewed head `465d97300cf021840fb1fe0434656ff3772d1db4`; merge base `7dfcbd09a2df930ee3449ce047984e4da5cec460`.
- Full seven-file benchmark package diff.
- `AGENTS.md`, `playbook/SIMULATION_DESIGN.md`, `playbook/REPAIR_AND_LEARNING.md`, `runtime/evaluation/evaluator.py`, `runtime/evaluation/regression_case.py`, `work/evals/maps-end-to-end-benchmark-v1.json`, `work/README.md`.
- Supporting review/check/index/pilot skill and all four frozen regression cases.
- External references in `REFERENCES.md`; no citation finding.
- Precision/S4 calculations were illustrative and assumption-dependent.

---

## 7. Reviewer limits

- PR description was UNKNOWN to the reviewer because GitHub REST was rate-limited; the correction belongs in the package regardless.
- Reviewer had no push credentials and made no fixes.
- A non-approving review-evidence record can make a mechanical review-evidence check green; green is not approval.
- CI status of the reviewed head was not verified.
- Scope honored: nothing executed, no corpus built, no thresholds frozen, no model/API scoring or spending, no runtime/protocol change, no merge.
