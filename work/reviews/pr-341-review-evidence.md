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

### B1 — BLOCKING — Treatment surface undefined; control contamination and unequal starting state

- **Defect:** MAPS_Lean cases risk auto-loading `AGENTS.md`/skills into Vanilla, while external repos do not define how MAPS is delivered. Protocol-artifact writes and target-project instruction precedence are also unspecified; per-case method selection can tailor treatment to traps; optional live-update statements introduce an extra intervention.
- **Smallest correction:** Add a treatment-surface manifest: exact pinned files/text and injection channel; Arm A differs only by removal of manifest paths; every auto-loaded instruction source is held identical or declared; one fixed protocol package for all cases; offline pinned delivery; predeclared protocol-artifact write rule; live-update requirement off in Experiment P or identical across arms.

### B2 — BLOCKING — Hidden contracts may contain hidden requirements, not just hidden checks

- **Defect:** Unstated evidence/reporting requirements or parser expectations for MAPS-style `DONE/BLOCKED` can make process compliance affect outcome classification.
- **Smallest correction:** Hidden ≠ additional. Any criterion that changes outcome class must derive from the task-facing fixture. Add one identical neutral final-status contract to every fixture. False claims of verification become a separate secondary metric unless evidence was requested.

### B3 — BLOCKING — Primary-endpoint population is defined by MAPS_L's own failure theory

- **Defect:** Known regression cases are MAPS's repaired failures and should not contribute to the primary endpoint. Existing frozen regression cases are runtime-mechanism tests, not protocol-neutral agent tasks. The family mix mirrors MAPS invariants too closely.
- **Smallest correction:** Exclude `KNOWN_REGRESSION` from H1/H5 primary inference; keep runtime-mechanism regressions under Experiment S; define primary endpoint on neutral + holdout pools with independently approved target-population weights; report clean/stress sensitivity; stratify external projects; pair stress families with counterweight families.

### M1 — MATERIAL — Terminal-state truth table contradicts itself and undercounts false blocks

- Keep one truth table in CASE-DESIGN. Key on correct terminal class (`PROCEED | BLOCK`) × declared status × criteria/forbidden effects. Define primary success as case-correct terminal outcome. Report PROCEED and BLOCK separately, freeze BLOCK share, and pair true blockers with resolvable twins.

### M2 — MATERIAL — No compute- or structure-matched control in the primary design

- Make Arm C mandatory for Standard/Full before any MAPS-specific claim. Freeze it before A/B data and have it authored/approved independently. It may include generic self-verification/review/helper guidance. Report B−C as MAPS-specific estimate; A/B alone is only “vs no-protocol control.”

### M3 — MATERIAL — Researcher degrees of freedom remain after comparative smoke data

- Freeze equivalence margin, guardrails, run budgets, human-response policy, and decision rules before first A/B execution including Smoke. Smoke may only repair harness/grader defects and may inform sample size using arm-blind pooled variance. Evaluate benchmark defects blind to arm. Report pre/post-version results if a case is dropped after results.

### M4 — MATERIAL — Human-response policy interacts with a MAPS invariant

- Freeze a neutral default: non-boundary questions receive one fixed reply (“proceed within the stated scope using your best judgment”) and are logged as avoidable interventions; seeded boundary questions receive predefined answers; asking never terminates a run. Include cases where asking is correct.

### M5 — MATERIAL — Evaluator blinding is nominal; treatment is identifiable from content

- Give semantic evaluator minimal per-property evidence, normalize away protocol vocabulary/process artifacts, run a blinding check, use non-contributor or blinded adjudicators, adjudicate paired headline/S4 disputes plus a random unflagged sample, and prefer a different model family for second evaluation.

### M6 — MATERIAL — Critical-failure gate cannot trigger at planned sizes

- Replace statistical-significance dependence with a predeclared count guardrail: any adjudicated S4 in one arm where its paired comparator has none blocks BETTER for that arm until disclosed/reviewed. Apply symmetrically. Report exact raw counts and intervals.

### M7 — MATERIAL — Decision rules underspecified relative to achievable precision

- Define exact directional/equivalence rules. Smoke produces no directional verdict. Predeclare only a handful of secondary endpoints tied to guardrails. Treat subgroup/family findings as exploratory and holdout as a consistency check unless adequately powered.

### M8 — MATERIAL — INVALID/UNKNOWN handling can hide protocol-induced failure and break pairing

- Agent-induced environment failures are not INVALID. Decide invalidity blind to arm. Invalidate/rerun at pair level. Report per-arm invalid rates. Count UNKNOWN as not-success in primary analysis and provide best/worst-case bounds.

### M9 — MATERIAL — Holdout firewall is intent-based, internally inconsistent, and leak-prone

- Retire holdouts on exposure to anyone who can influence the protocol. Predeclare confirmatory looks. Commit a sha256 of the sealed bundle. Store holdouts outside any run-reachable path; run snapshots exclude `work/evals/`; no network path to live MAPS repo; disclose builder identity and protocol exposure.

### M10 — MATERIAL — Missing case classes where MAPS_L is likely to hurt or failures would be missed

Add counterweights including: false-blocker twins; asking-is-correct; over-continuation; protocol-artifact writes in foreign repos; instruction conflict; medium-complexity ceremony; latency-bounded tasks; context pressure; sequential episode chains; review/helper-induced harm; untrusted instruction-like content. Pair stress families with counterweights and revise the 36-case target.

### M11 — MATERIAL — Implied reuse of existing machinery would import MAPS-shaped criteria

- Add a relationship boundary: E2E-v1 properties and SIMULATION_DESIGN required behaviors/failure classes are diagnostic-only or out of scope for Experiment P primary outcomes; `evaluator.py`/`regression_case.py` are not the Experiment P scorer; any benchmark machine schema is defined once in this package.

### M12 — MATERIAL — Internal duplication has already produced divergent normative rules

Assign one owner per concept:
- SPEC: arms, manifest, controls, pools, lifecycle, thresholds;
- CASE-DESIGN: record, families, truth table, severity;
- RUN: execution;
- SCORING: metrics and decision rules.
Reduce README to question, status, index, relationship. Other files link instead of restating.

### Minor findings

- Severity should be based on final state/effects; S1 should not double-count efficiency; define unanticipated failures and max-severity-per-run.
- Make token/context consumption primary reading-cost measure; human minutes observed, not estimated; pair continuation with over-continuation; define/drop evidence quality.
- Run pairs concurrently or interleaved within a bounded time window.
- Add an inbound route from an owning task/roadmap or state the parent in README.

---

## 3. Optional improvements

- Put MAPS-specific instantiation details in a short appendix for portability.
- Add cost-normalized sensitivity analysis (e.g. Vanilla best-of-k within MAPS spend).
- Consider one confirmatory pre-registration commit per batch.
- Reduce duplicated documentation after ownership consolidation.

---

## 4. Adversarial questions — answers

1. MAPS can score well without becoming better through repaired-regression weighting, MAPS-shaped families, hidden process requirements, human-response policy, and false-block undercounting.
2. Vanilla can be unfairly weakened by auto-loaded instruction mismatch, MAPS-specific status parsing, no-reply stalls, strawman C, and adaptive budgets.
3. MAPS can worsen in practice while benchmark scores rise if longitudinal sprawl, foreign-repo writes, over-continuation, and holdout overfitting remain invisible.
4. Leakage can enter through trap/family lists mirroring AGENTS/E2E, reuse of E2E/SIMULATION criteria, MAPS-seat case authors, and hidden contract language.
5. Likely missed failures: unnecessary protocol artifact writes, instruction conflicts, context exhaustion, over-continuation, and review-induced breakage.
6. Misread wins include aggregate gains driven by regression/stress families, A/B without C, uncertain point estimates, tiny subgroup wins, underpowered holdout “persistence,” or S4 increases dismissed as nonsignificant.
7. Process can be rewarded via hidden evidence/claim requirements and imported E2E adherence properties.
8. Gameable metrics include human interventions, files-read, continuation, review catch without false-positive pairing, and INVALID classification.
9. Current design cannot yet distinguish structured prompting from MAPS-specific mechanisms without mandatory C.
10. Core structure is portable, but current families/traps still carry MAPS's theory of failure.

---

## 5. Final assessment

- **Sufficiently unbiased to proceed?** Not yet to corpus construction.
- **Could it credibly produce a negative MAPS_L result?** The skeleton can, but current form structurally favors a positive result.
- **Outcome improvement vs process compliance?** Correct in principle, not yet enforced through hidden contracts/imported criteria.
- **Causal controls sufficient?** No until treatment surface is fixed and Arm C becomes mandatory for MAPS-specific claims.
- **Holdout/versioning sufficient?** Versioning good; holdout exposure and adaptive reuse need correction.
- **Exact next gate:** Owner corrects B1–B3 and M1–M12, consolidating ownership. Fresh independent reviewer re-reviews at the new head. Verdict must be `APPROVED FOR CORPUS CONSTRUCTION` before any case is authored. No corpus, threshold freeze, runs, or spending until then.

---

## 6. Evidence checked

The reviewer inspected the exact head, full seven-file diff, AGENTS.md, SIMULATION_DESIGN.md, REPAIR_AND_LEARNING.md, runtime evaluator/regression machinery, existing end-to-end benchmark, work routing, review/checks/index/pilot-skill material, and all four frozen regression cases. External methodology references were checked and no citation finding was raised.

---

## 7. Reviewer limits

The PR description was not accessible in the review environment because of rate limits; the review relied on the exact diff and repository evidence. No reviewer-authored fixes were made. Nothing was executed, no corpus built, no thresholds frozen, no model/API scoring performed, no spending, runtime/protocol changes, or merge.
