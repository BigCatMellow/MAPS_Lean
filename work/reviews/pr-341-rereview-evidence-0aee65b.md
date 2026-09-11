# PR #341 — Protocol Effectiveness Benchmark — focused re-review (r5) evidence

reviewer: claude-opus-5-fresh-rereviewer-pr341-r5
head_sha: 0aee65b4b6ecc31cd3ac4042e1a47786d9490b06
independent: true
verdict: MINOR CORRECTIONS REQUIRED
review_state: CHANGES_REQUESTED
review_layer: FOCUSED DELTA RE-REVIEW (G1–G10 + anchor safeguard + B/M/N/F regression); spec only; nothing executed
prior_review_heads: 465d97300cf021840fb1fe0434656ff3772d1db4 (original); 56c43aa9c176a98b733c32cfb53b182b3c034b9f (r2); dcc064bbc70648bded8f3e944d4f00c46b198fa5 (r3); 7ec7e1d43e4252e3e6995cd83fc3ed6631a10e14 (r4)
summary: MINOR CORRECTIONS REQUIRED — corpus gate stays closed. G1, G3, G4, G5, G7, G8, G9, G10 resolved; G2 and G6 partially resolved. Anchor check passes locally and in CI (run 34589077692, step 6). New MATERIAL H1: the G6 comparator-side S4 clause reverses accepted semantics — comparator-exclusive S4s now soften the tested arm's WORSE to TRADEOFF and lift its own-S4 bar on BETTER/EQUIVALENT; 14 of 72 verdict input combinations change, all toward the tested arm (always B); regresses M6/N4/F4 and passed the anchor check because those anchors are headings. New MATERIAL H2: the added "unless COUNTERWEIGHT" exception lets seeded MAPS-favored conditions leave the STRESS ceiling via cost/latency-only harm paths. MINOR: H3 anchor coverage gap (third fix-pass regression occurrence), H4 report-template drift, H5 training-cutoff reference model unpinned before sampling. All bounded text/manifest edits; no redesign.

Head check: `git ls-remote` → `refs/pull/341/head` = `0aee65b4b6ecc31cd3ac4042e1a47786d9490b06` (match). Delta `7ec7e1d..0aee65b`: four owner files, README, task, anchor manifest, anchor script, workflow step, friction carrier, r4 evidence. No runtime/protocol paths. Line numbers at `0aee65b`.

---

## 1. Verdict

**`MINOR CORRECTIONS REQUIRED`.** H1–H5 land before corpus construction (H4 is report-schema only and would not alone hold the corpus gate).

Keep intact: everything r4 listed, plus this pass's genuine gains — restored Arm C block (SPEC §3), every-class overlay review (SPEC §7.4, CASE §6.4), all-channel retrieval deny-all and enabled-tool exercise (SPEC §4.5, RUN §4.3), exact run-visible field set (CASE §1), task-facing status definitions (CASE §2), fixture + bootstrap precedence (CASE §2, SPEC §4.2), `s3_crossing_basis` and all-fields-critical rule (SPEC §11), arm-masked Smoke evidence (SPEC §12), package-first-commit request cutoff (SPEC §7.1), env/shell/VCS/runner parity (SPEC §4.3, RUN §3), cutoff-relation strata (SPEC §7.1), anchor manifest/check/CI step.

## 2. G1–G10 matrix

| ID | Status | Evidence |
| --- | --- | --- |
| G1 | RESOLVED | SPEC §3: mandatory for Standard/Full; competent generic behaviors; no MAPS concepts; independent author/approver; same channel/position; A/B/C length/context disclosure; B−C and B−A scoping. Generic control text/hash in manifest frozen before any case. Pre-corpus gate explicitly checks Arm C. |
| G2 | PARTIALLY RESOLVED | Every class reviewed, reclassifications recorded; bounds retained. NONE cannot carry a seeded condition. Open: new exception lets seeded stress escape via COUNTERWEIGHT → H2. |
| G3 | RESOLVED | SPEC §4.5 names provider-hosted search/fetch/retrieval/browsing/code-exec/remote MCP; enabled tools listed and mechanically tested. CASE §1 exact run-visible set + exclusions. Env/runner metadata covered. |
| G4 | RESOLVED | CASE §2 definitions inside neutral output contract, identical across arms; BLOCK rule uses common semantics. |
| G5 | RESOLVED | SPEC §4.2 common bootstrap plus CASE §2 full INSTRUCTION_PRECEDENCE line. |
| G6 | PARTIALLY RESOLVED | Determinism achieved, but new comparator-side S4 clause reverses accepted semantics → H1. |
| G7 | RESOLVED | Arm-masked Smoke evidence; unmasked treatment-identifying material counts as per-arm exposure. |
| G8 | RESOLVED | Operator-request cutoff is objective/time-role based. |
| G9 | RESOLVED | Env/shell/VCS/runner parity and cache reset covered. |
| G10 | RESOLVED | Resolution-date/cutoff strata defined and frozen at pre-corpus gate; sequencing detail → H5. |

## 3. Regression matrix

- B1 B2 B3 — STILL RESOLVED
- M1 M2 M3 M4 M5 — STILL RESOLVED
- M6 — REGRESSED — H1
- M7 M8 M9 M10 M11 M12 — STILL RESOLVED
- N1 N2 N3 — STILL RESOLVED
- N4 — REGRESSED — H1
- N5 N6 N7 N8 N9 N10 — STILL RESOLVED (N10 report drift noted as H4)
- F1 F2 F3 — STILL RESOLVED
- F4 — REGRESSED — H1
- F5 F6 F7 F8 F9 — STILL RESOLVED

### M6/N4/F4 regression

Accepted semantics before the latest rewrite:

- `T_excl > K_excl` → tested arm WORSE.
- `T_excl > 0` and `T_excl <= K_excl` → tested arm ineligible for BETTER/EQUIVALENT.
- Comparator-exclusive S4s never block a WORSE label for the tested arm.
- One-sided registered harm under EQUIVALENT/INCONCLUSIVE → WORSE.

At `0aee65b`, rule 2 narrows to equal counts and rule 3 makes comparator S4 excess a benefit for the tested arm. Exhaustive enumeration of T_excl/K_excl 0..2 × PRIMARY B/E/I/W × HARM true/false yields 14/72 changed outcomes, all toward T.

## 4. Mechanical safeguard result

- Manifest completeness: 44 unique entries = B1–B3, M1–M12, N1–N10, F1–F9, G1–G10.
- Checker: hard-coded expected ID set; fails on missing/unexpected/duplicate IDs, empty fields, unsafe paths, missing owner, missing anchor. Local run passes.
- Mutation tests failed as intended for deletion/addition/duplicate/missing-owner cases.
- CI: anchor step passed on run 34589077692; exact-head review-evidence step failed as expected because no exact-head review evidence existed yet.
- False-negative probes passed: semantic body rewrites under preserved headings/weak anchors are not caught.
- Twelve anchors are headings only; live H1 is a demonstrated false negative.
- Invariant 13 is satisfied for silent deletion but not semantic rewrite; this is the third fix-pass regression occurrence.

The friction carrier accurately records earlier regressions and anchor countermeasure, but needs the r5 semantic-rewrite occurrence added. Canonical friction-log append remains housekeeping, not benchmark validity.

## 5. New findings

### H1 — MATERIAL — comparator-side S4 clause reverses accepted S4 semantics

**Where:** `SCORING-AND-ANALYSIS.md` S4_RULE_V1, TRADEOFF_RULE_V1, VERDICT_PRECEDENCE_V1.

**Defect:** comparator S4 excess can convert tested-arm primary WORSE or harm to TRADEOFF and can lift the bar created by the tested arm's own S4s.

**Validity impact:** every reported comparison tests B as T; this systematically softens MAPS losses and critical failures.

**Smallest correction:** restore the accepted semantics explicitly:
1. `T_excl > K_excl` → WORSE.
2. `T_excl > 0` and `T_excl <= K_excl` → T ineligible for BETTER/EQUIVALENT: PRIMARY_BETTER → TRADEOFF; PRIMARY_WORSE or HARM_CROSSED → WORSE; otherwise INCONCLUSIVE with S4 qualifier.
3. `K_excl > T_excl` is a mandatory report qualifier only. It never blocks, softens, or converts a WORSE label for T; never creates BETTER/EQUIVALENT/TRADEOFF; and never lifts rule 2. Comparator-side consequences arise only by reversing the comparison.
Delete the comparator-benefit branches elsewhere and pin these rule bodies mechanically.

### H2 — MATERIAL — seeded stress can escape STRESS ceiling through COUNTERWEIGHT

**Where:** SPEC §7.4; CASE §6.2/§6.4.

**Defect:** seeded stress may become COUNTERWEIGHT on cost/latency/burden-only harm paths, letting MAPS-favored primary traps escape the STRESS ceiling.

**Smallest correction:** a seeded §6.2 case may be COUNTERWEIGHT only when its named harm path can worsen the primary case-correct outcome (`FALSE_BLOCK`, `INCOMPLETE`, `FALSE_SUCCESS`, or forbidden effect). Cost/latency/burden-only harm leaves it STRESS. Add hidden `seeded_stress_families[]` and report the share of primary cases containing seeded §6.2 conditions.

### H3 — MINOR — anchor safeguard misses semantic rewrites

**Where:** anchor manifest/checker/friction carrier.

**Smallest correction:** allow multiple anchors per finding; replace heading-only anchors with rule-bearing clauses; minimally pin H1 rule bodies, harm→WORSE, H2 primary-harm-path condition, and full precedence sentence; add H1–H5 to expected IDs; record r5 occurrence and why deletion-only anchors failed.

### H4 — MINOR — REPORT-TEMPLATE drift

Align H5 labels with SCORING (`SUPPORTED_BETTER | SUPPORTED_WORSE | SUPPORTED_EQUIVALENT | INCONCLUSIVE`); correct the TRADEOFF sentence to include S4 rule branches; add A/B/C instruction length/context cost, overlay reclassifications, cutoff-relation strata, and crossing-basis slots.

### H5 — MINOR — training-cutoff reference model not pinned before sampling

Sampling manifest must declare the reference model/provider version and latest documented cutoff (UNKNOWN if none). If executed model differs, recompute relation deterministically from resolution date at pre-run freeze and report both.

## 6. Adversarial answers

1. Weak C inflating B−C: no.
2. Stress labeled NONE: no; relabeled COUNTERWEIGHT: yes via H2.
3. Provider-side retrieval: controlled.
4. Metadata/provenance revealing answer: controlled.
5. Env/runner leaks: controlled.
6. INCOMPLETE vs BLOCKED vocabulary bias: controlled.
7. Unseen precedence rule: controlled.
8. Analysts diverging on verdict: no, but current deterministic rule is biased via H1.
9. S3 crossing analyst choice: no.
10. Unmasked Smoke pre-lock: treated as exposure.
11. Exposed person designing successor: prohibited.
12. New stakeholder operator requests: prohibited.
13. Shell/global config/cache contamination: controlled.
14. Pre-cutoff fixes: disclosed as sensitivity strata; reference sequencing needs H5.
15. MAPS can lose on over-process etc.: yes, weakened by H1.
16. Vanilla/C can beat MAPS through simpler correct execution: yes, weakened by H1.
17. Silent deletion detectable: yes; semantic rewrite under preserved anchor: no.

## 7. Final assessment

- Treatment/control causally interpretable: yes for design; verdict mapping not neutral until H1.
- Vanilla fair capable control: yes.
- Arm C credible generic comparator: yes.
- External-answer leakage adequately controlled: yes.
- Selection/overlay resists MAPS-favoring bias: not yet (H2).
- Smoke firewalled from tuning: yes.
- Verdict machinery deterministic: yes, but deterministically tilted toward tested arm (H1).
- Global environment parity: yes.
- Parametric recall handled for corpus construction: yes, subject to H5.
- MAPS_L can credibly win: yes.
- MAPS_L can credibly lose: yes, weakened by H1.
- Simpler agent can outperform MAPS: yes, weakened by H1.
- Repeat regression mechanically guarded: deletion yes; semantic rewrite no (H3).
- Ready for corpus construction: **No**.

## 8. Exact next gate

1. Apply H1–H5 as targeted edits.
2. Extend the anchor manifest/check per H3, including H1–H5 IDs.
3. Update friction carrier/canonical log with the r5 occurrence.
4. Fresh independent re-review verifies H1–H5, reruns anchor check plus a semantic S4 branch check, and repeats bounded B/M/N/F/G regression check.

No corpus/holdout authoring, threshold freeze, Smoke/Standard runs, model/evaluator calls, spending, runtime/protocol change, or merge until `APPROVED FOR CORPUS CONSTRUCTION`.

## 9. Evidence checked and reviewer limits

Evidence checked: exact head; `AGENTS.md`; task; all four prior reviews; all package files; anchor manifest/checker/workflow/friction carrier; owner diffs; prior S4 semantics; local anchor check and mutation probes; exhaustive S4 enumeration; Actions results.

Reviewer limits: no push credentials; REST rate-limited; shallow fetch; same model family as prior reviewers; nothing built, run, called, spent, changed, or merged.
