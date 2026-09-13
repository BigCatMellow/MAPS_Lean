# PR #341 — Protocol Effectiveness Benchmark — focused re-review (r3) evidence

reviewer: claude-opus-5-fresh-rereviewer-pr341-r3
head_sha: dcc064bbc70648bded8f3e944d4f00c46b198fa5
independent: true
verdict: MINOR CORRECTIONS REQUIRED
review_state: CHANGES_REQUESTED
review_layer: FOCUSED DELTA RE-REVIEW (N1–N10 + B/M regression); spec only; nothing executed
prior_review_heads: 465d97300cf021840fb1fe0434656ff3772d1db4 (original); 56c43aa9c176a98b733c32cfb53b182b3c034b9f (r2)
summary: MINOR CORRECTIONS REQUIRED — corpus gate stays closed. Second pass is real: N2 and N10 resolved; N1 and N3–N9 mostly landed. Two MATERIAL defects remain: F1 external-case answers stay run-reachable via upstream sources/network, and the case-secret canary can be placed after copies exist; F2 the second pass deleted the neutral human-response default from both SPEC §16 and RUN §6, regressing M4. Seven MINOR text residuals (F3–F9). No redesign needed.

Delta reviewed: `56c43aa..dcc064b`, 29 commits; paths changed: the seven package files, the task record, and `work/reviews/pr-341-rereview-evidence-56c43aa.md`. No runtime/protocol paths. Merge base with `main`: `7dfcbd0`. Line numbers below are at `dcc064b`.

---

## 1. Verdict

**`MINOR CORRECTIONS REQUIRED`** — corrections are bounded text changes inside existing owners, but F1 and F2 must land before corpus construction.

Keep intact: paired A/B(/C) architecture; outcome-only primary endpoint; Treatment Surface Manifest with pre-corpus bundle freeze; history-free MAPS_HOME snapshots and cross-`work/` scrub; unexposed-only primary population with per-version Standard retirement; holdout builder separation; pre-registration hashes; one-line Smoke→Standard freeze; `PRIMARY_STATUS` + precedence structure; NONE/STRESS/COUNTERWEIGHT bounds; UCB-based blinding pass rule; report schema.

## 2. N1–N10 matrix

| ID | Status | Evidence |
| --- | --- | --- |
| N1 | PARTIALLY RESOLVED | MAPS_HOME history-free default, sanitized-history alternative, all-pool off-repo storage, cross-`work/` scrub all landed. Open: external upstream-resolution/network path and canary timing/scope. See F1. Harness-global state: F7. |
| N2 | RESOLVED | Standard + holdout exposure retirement per protocol version; primary endpoint unexposed-only; bundle frozen before any case; protocol ref frozen before holdout; builder role bar; pre-registration before first scored run. |
| N3 | PARTIALLY RESOLVED | One Threshold Manifest and one Arm-C hash before Smoke, unchanged through Standard/Full; Smoke has no verdict. Residual: empty withholding window, intent-based clause, divergent change lists. See F3. |
| N4 | PARTIALLY RESOLVED | Rule IDs defined and pair-level S4 unit/precedence mostly deterministic. Residuals: text/arithmetic mismatch, repetition-alignment dependence, guardrail wiring, crossing basis, one-sided TRADEOFF, H5 minimum-n. See F4. |
| N5 | PARTIALLY RESOLVED | Declared population and pre-label sampling by independent curator; strata and overlay bounds landed. Residual: counterweight labels not auditable and one sampling source is operator-authored. See F5. |
| N6 | PARTIALLY RESOLVED | Single parser, BLOCKED-after-forbidden-effect, reason-error success, process prose independence, subwork rule landed. Residual: table/§5.1 conflict and missing rows. See F6. |
| N7 | PARTIALLY RESOLVED | Common bootstrap, B/C channel parity, precedence, recursive target inventory, scrubbed-subject ineligibility, write/sidecar scope, no live fetch landed. Residual: harness-level auto-load sources not inventoried. See F7. |
| N8 | PARTIALLY RESOLVED | Deterministic matcher/arm-blind responder and misroute logging landed. Residual: neutral default deleted (M4 regression) and misroute consequence undefined. See F2/F8. |
| N9 | PARTIALLY RESOLVED | Frozen sample size/ceiling, capable guesser, UCB pass rule, per-arm normalization audit landed. Residual: guess task undefined, asymmetry threshold unfrozen, timing. See F9. |
| N10 | RESOLVED | Report covers A/B/C, B−A/B−C, terminal outcomes, strata, S4, UNKNOWN/INVALID, blinding, canary, tokens/context, observed minutes; README/references non-normative. |

## 3. B/M regression matrix

| ID | Status |
| --- | --- |
| B1 | STILL RESOLVED |
| B2 | STILL RESOLVED |
| B3 | STILL RESOLVED |
| M1 | STILL RESOLVED |
| M2 | STILL RESOLVED |
| M3 | STILL RESOLVED |
| M4 | **REGRESSED** — see F2 |
| M5 | STILL RESOLVED |
| M6 | STILL RESOLVED |
| M7 | STILL RESOLVED |
| M8 | STILL RESOLVED |
| M9 | STILL RESOLVED |
| M10 | STILL RESOLVED |
| M11 | STILL RESOLVED |
| M12 | STILL RESOLVED |

**M4 regression:** at `56c43aa`, SPEC §16 and RUN §6 fixed the neutral policy content: non-boundary question → fixed reply "Proceed within the stated scope using your best judgment."; seeded boundary question → predefined answer; asking never terminates a run; avoidable questions count as burden. At `dcc064b`, RUN §6 defers content to SPEC, and SPEC §16 defers content to the Threshold Manifest. No text in the package now constrains policy content.

---

## 4. Findings

### F1 — MATERIAL — external answers remain run-reachable; the canary proves storage location, not recoverability (N1)

**Defect:** upstream resolution may remain reachable via network (upstream repo/forks, issue/PR threads, later package releases). The canary can be placed after earlier copies exist and may cover only the hidden contract rather than every answer-bearing artifact/environment component.

**Smallest correction:** default network to no network except a frozen per-case allowlist; exclude upstream/forks/issues/PRs/post-snapshot releases and any source containing the resolution. Cases whose required sources necessarily contain the resolution are ineligible. Embed canaries at hidden-material creation in every hidden artifact and scan the fully assembled execution environment (target snapshot + VCS, treatment bundle, sidecar, harness home/config, image) for canaries and frozen case-distinctive resolution identifiers.

### F2 — MATERIAL — neutral human-response default deleted (M4 regression; N8)

**Defect:** a no-reply/stall policy is freezable again, making Vanilla check-ins disproportionately costly.

**Smallest correction:** restore mandatory constraints: non-boundary question → fixed reply `Proceed within the stated scope using your best judgment.`; seeded boundary question → predefined answer; asking never terminates a run; avoidable questions count as burden.

### F3 — MINOR — Smoke withholding window is empty in the no-change path (N3)

**Smallest correction:** withhold per-arm Smoke outcome/overhead deltas from anyone with edit/freeze authority over this or any successor line until that line's Standard analysis is locked; anyone who has seen them becomes ineligible to author successor-line changes. Include treatment bundle and corpus/case composition in material-change list. RUN should link to SPEC rather than duplicate the list.

### F4 — MINOR — residual verdict-rule discretion (N4)

**Smallest corrections:**
1. Reword S4 rule text to match net-exclusivity arithmetic.
2. Compute exclusivity per case: `T_excl = Σ_case max(0, S4runs_T − S4runs_K)`.
3. Wire every `*_guardrail` into `TRADEOFF_RULE_V1` or remove it.
4. Freeze `crossing_basis` per headline metric.
5. Define one-sided harm under PRIMARY_EQUIVALENT/INCONCLUSIVE deterministically (WORSE or mandatory qualifier) in rule text.
6. Add `h5_min_valid_cases_per_stratum` to the manifest.

### F5 — MINOR — counterweight labels are not auditable (N5)

**Smallest correction:** add hidden `counterweight_tendency` and `counterweight_harm_path` fields checked by the independent overlay reviewer; treat sequential-chain and untrusted-instruction cases as harm-detection only, with overlay assigned by the prevalence test; operator-authored requests must pre-exist the sampling freeze or be authored by non-stakeholders.

### F6 — MINOR — truth-table gaps (N6)

**Smallest correction:** add requested-separable-subwork satisfaction to TRUE_BLOCK rows; add `BLOCKED_WRONG_CLASS` as not-success; freeze `accepted_blocker_classes` in the hidden contract; classify `INCOMPLETE` + correct blocker class deterministically.

### F7 — MINOR — harness-level and cross-run state (N1/N7 edge)

**Smallest correction:** extend recursive auto-load inventory to harness user/global instructions, skills, persistent memory, MCP/config sources; require them empty or byte-identical across arms. Require sidecar and harness memory fresh per execution except declared episode chains.

### F8 — MINOR — misroute consequence undefined (N8)

**Smallest correction:** outcome-affecting responder misroute => pair `INVALID` and rerun under frozen policy; non-affecting misroute => log only.

### F9 — MINOR — blinding test not fully specified (N9)

**Smallest correction:** freeze `blinding_guess_task` (e.g. balanced B vs non-B), `normalization_loss_asymmetry_threshold`, and run the guess/audit before per-arm semantic grades are unmasked. Re-normalization decisions must occur without per-arm grade access and apply to the full batch.

### Optional

- State explicit BLOCK-share ceiling.
- Include bootstrap seed and replicate count in `analysis_rule_hash`.

---

## 5. Adversarial pass

1. MAPS_HOME history/records leakage closed on paper; external upstream resolution, late canary placement, and harness-global state remain open.
2. Task-selection bias largely closed; counterweight labeling and operator-authored requests remain minor residuals.
3. Standard exposure retirement across later protocol versions is resolved.
4. Smoke-to-Standard tuning mostly closed; withholding window/intent wording remains.
5. Narrow verdict ambiguity remains in guardrail wiring/crossing basis/S4/H5/blinding-asymmetry details.
6. Exclusive S4s cannot be averaged away, with a repetition-alignment edge remaining.
7. TRADEOFF is registered-threshold based but one-sided crossing interpretation is soft.
8. Stress density is bounded; counterweight classification remains auditable only after F5.
9. Vanilla can tie on correctness and beat MAPS on cost/latency, though current one-sided TRADEOFF handling should be fixed.
10. MAPS can lose through false block, scope writes, context/budget exhaustion, over-continuation, latency/context pressure, review/helper harm, and asking-too-little cases. F2 currently lets MAPS regain an unfair advantage if Vanilla check-ins stall.
11. Arm C can outperform MAPS without artifact penalty.
12. Evaluator treatment-identification can be tested once F9 fully freezes the guess task/timing.
13. No hidden process-compliance requirement remains.
14. New problems introduced by second pass: M4 regression (F2), wrong-class truth-table gap (F6), and duplicated Smoke change lists (F3).

## 6. Final assessment

- **Can MAPS_L credibly win?** Yes.
- **Can MAPS_L credibly lose?** Yes, once F2 is restored; primary endpoint already punishes false blocks, scope writes, exhaustion, and other harms.
- **Can a simpler agent win through equal correctness and lower overhead?** It can deny MAPS a favorable label; one-sided harm classification needs F4.5.
- **Does Arm C support a MAPS-specific comparison?** Yes.
- **Do selection and exposure controls resist overfitting?** Exposure controls: yes. Selection: yes subject to F1/F5.
- **Is verdict machinery deterministic enough?** Nearly; F4/F9 text fixes remain.
- **Ready for corpus construction?** **No.** F1/F2 must land first; F5–F7 shape authoring and should land with them. F3/F4/F8/F9 are cheap to land now.

## 7. Exact next gate

1. Owner applies F1–F9.
2. A focused fresh independent re-review checks that delta at the new head, including a regression check for F2.

Until that review returns `APPROVED FOR CORPUS CONSTRUCTION`, no corpus/holdout authoring, threshold freeze, Smoke/Standard runs, model/evaluator calls, spending, runtime/protocol change, or merge.

After approval, next gate is corpus construction plus independent corpus review — not benchmark execution.

## 8. Evidence checked and reviewer limits

Evidence checked: exact head `dcc064b`; `AGENTS.md`; task record; both prior review records; all seven package files; removed-line diffs `56c43aa..dcc064b`; `work/README.md`; `scripts/check_review_evidence.py`.

Reviewer limits: PR description and CI status were unavailable in reviewer environment; same model family as prior reviewers; no push credentials. No cases built, nothing run, no evaluator/API calls, no spend, no runtime/protocol change, no merge.
