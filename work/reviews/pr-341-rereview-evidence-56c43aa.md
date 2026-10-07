# PR #341 — Protocol Effectiveness Benchmark — fresh re-review evidence

reviewer: claude-opus-5-fresh-rereviewer-pr341-r2
head_sha: 56c43aa9c176a98b733c32cfb53b182b3c034b9f
independent: true
verdict: MINOR CORRECTIONS REQUIRED
review_state: CHANGES_REQUESTED
review_layer: DESIGN / EXPERIMENTAL-VALIDITY RE-REVIEW after corrections
prior_review_head: 465d97300cf021840fb1fe0434656ff3772d1db4

## Summary

`MINOR CORRECTIONS REQUIRED` — corpus-construction gate remains closed.

The re-review found that the first correction pass was real and mostly sound. No BLOCKING defect remains. The paired A/B(/C) architecture, outcome-only primary endpoint, Treatment Surface Manifest, pool split, neutral `FINAL_STATUS`, mandatory Standard/Full Arm C, pre-Smoke threshold freeze, neutral human-response policy, agent-caused exhaustion handling, exposure-based holdout retirement, counterweight families, and Experiment-P/runtime-evaluation boundary are substantially correct.

Original correction status:

- Resolved: B2, M1, M4, M8, M10, M11.
- Partially resolved: B1, B3, M2, M3, M5, M6, M7, M9, M12.
- Unresolved/regressed: none.

Five MATERIAL residuals (N1–N5) and five MINOR residuals (N6–N10) remain. The reviewer judged all to be bounded text corrections inside existing owners; no redesign is required.

## Residual findings

### N1 — MATERIAL — run snapshots can expose benchmark material through VCS history and records outside `work/evals/`

Current-tree scrubbing is insufficient for MAPS_HOME because git history can expose prior benchmark files, and sibling `work/` records can describe cases/reviews/freezes. Hidden contracts for FROZEN_STANDARD are not explicitly kept off-repo.

Required correction:

1. Store hidden contracts/oracles/seed keys for all pools outside every repository used to seed run snapshots, at every commit.
2. Use history-free MAPS_HOME exports or sanitize history of benchmark material.
3. Scrub benchmark-related records across `work/`, not only `work/evals/`.
4. Add a frozen pre-run canary proving a unique case-secret token is unreachable from the snapshot, including `.git`.

### N2 — MATERIAL — exposure accounting stops at the sealed holdout

The treatment bundle can still be selected after corpus/traps are visible; holdout builders may modify the protocol before the seal interval; FROZEN_STANDARD cases can remain in the primary endpoint for later protocol versions after their trajectories are exposed; hashes are recorded but not required to be committed before execution.

Required correction:

1. Freeze the protocol bundle and hash before corpus construction starts, defaulting to the complete deployed protocol surface at the pinned ref; any subset is selected without case access.
2. Fix the tested protocol ref before holdout construction; holdout builders have no protocol-modifying role from construction start through the confirmatory look.
3. Apply exposure-based retirement to FROZEN_STANDARD per protocol version. Later versions must win on unexposed/refreshed primary cases.
4. Commit corpus/holdout/manifest/threshold hashes before the first scored run.

### N3 — MATERIAL — Smoke opens a re-freeze window after arm-level data exist

`RUN-PROTOCOL.md` currently permits a Smoke freeze, arm-level Smoke results, then a new Standard A/B/C freeze. That leaves budgets, guardrails, Arm C, and other rules open to tuning after comparative data exist.

Required correction:

- One Threshold Manifest and one Arm C text are frozen before Smoke and carry unchanged into Standard/Full for that benchmark line.
- Any post-Smoke change to margins, guardrails, safety/tradeoff rules, headline secondaries, budgets, human policy, Arm C, or verdict rules starts a new benchmark line or is made only by a party exposed solely to arm-pooled Smoke evidence.
- Anyone able to edit the Standard package receives pooled—not per-arm—Smoke metrics until the Standard package is frozen.

### N4 — MATERIAL — verdict labels retain post-result discretion

The S4 unit, critical-safety mapping, TRADEOFF trigger, label precedence, and H5 consistency test are not fully operationalized.

Required correction:

- Add exact frozen safety/tradeoff rules to the threshold manifest.
- Define S4 on the matched case-repetition pair and compare arm-exclusive events.
- An arm's exclusive S4s restrict only that arm's favorable labels and never shield it from an unfavorable label.
- Add explicit verdict precedence.
- Freeze the external/holdout consistency rule.

### N5 — MATERIAL — theory-laden trap density is unconstrained inside primary strata

The target work population is not actually declared, seeded MAPS-stress overlays have no prevalence ceiling, and counterweights need not be at parity inside the primary pools.

Required correction:

1. Declare a target work population sourced independently of MAPS failure categories.
2. Freeze a maximum stress-overlay share and minimum trap-free share.
3. Require primary counterweight cases at least as numerous as primary stress cases (or parity per stress label).
4. Require independent review of overlay prevalence as well as strata weights.

### N6 — MINOR — truth-table edge rows

Add a common final-status parse rule; classify `BLOCKED` after a forbidden effect; state whether blocker-reason error remains primary success; and make separable subwork outcome-relevant only when the task-facing request asks for it.

### N7 — MINOR — treatment-surface clarifications

Make writable paths and sidecar path task-facing; freeze precedence between injected workflow guidance and target-project instructions; inject B and C through the same channel/position and give the neutral bootstrap to all arms; recursively inventory auto-load files; make MAPS_HOME cases requiring scrubbed treatment files ineligible; align/disclose snapshot-vs-bundle ref skew.

### N8 — MINOR — human-response delivery and asking-is-correct grading

Use a frozen matcher or arm-blind responder on normalized text; log/adjudicate misrouted replies by arm; grade asking-is-correct cases on the preference-dependent product, not the act of asking.

### N9 — MINOR — blinding check can pass by low power

Freeze blinding sample size and an accuracy ceiling; pass only when the upper confidence bound on treatment-guess accuracy is at or below the ceiling; use a guesser at least as capable as the semantic evaluator; audit normalized packets by arm for dropped relevant evidence.

### N10 — MINOR — report template and residual duplication

Update `REPORT-TEMPLATE.md` for A/B/C, B−A/B−C language, case-correct terminal outcome, PROCEED/BLOCK and external strata, S4/UNKNOWN/INVALID/blinding sections, over-continuation, token/context cost, observed human minutes, and current work-characteristic strata. Remove duplicated normative rules from README/CASE/RUN and reword S3 so efficiency/rework is not double-counted as failure severity.

## Final assessment

- No blocking defect remains.
- MAPS_L can now credibly lose in the core scoring path, but N1, N2 and N5 must land before corpus construction.
- N3, N4 and N9 must land before pre-run freeze.
- N6–N8 and N10 are bounded clarity/reporting corrections that should land now to avoid contaminating case authoring.

## Exact next gate

Owner applies N1–N10, then a **focused fresh independent re-review of that delta at the new head**.

No corpus construction, holdout authoring, benchmark execution, model/evaluator calls, spending, runtime/protocol modification, or merge before that review returns:

`APPROVED FOR CORPUS CONSTRUCTION`
