# PR #260 review evidence — 6.9/S6 `_select_skills` match-strength gate (path (a))

reviewer: maps-lean-luve
head_sha: b50c6a96bda2e212fb127858c8a53a9041182cd1
independent: true
summary: Independent review by maps-lean-luve (gela authored; luve independent of the impl — luve reviewed #246 which built EXP-B and #250 the NO-FLIP gate step). `_select_skills` replaces "any shared token selects" with a match-strength gate (`1/df` token weighting across the candidate catalog + a small hand-curated `_SKILL_ROUTING_STOPWORDS` set + an anchor requirement + a strength-or-coverage floor; no retrieval / synonym map / semantic layer / new dependency). Independently reproduced EXP-B at HEAD: exact 15→19, `false_activation_cases` 4→0, `selection_precision` 0.684→1.0, `selection_recall` 0.7647 unchanged, `selection_f1` 0.722→0.867, `corpus_sha256` 2cff0e40…4565 UNCHANGED; DIRECT/PARAPHRASE/MULTI_SKILL/NO_SKILL all hold at 1.00; HARD_NEGATIVE 0.00→1.00. EXP-A (v1) also improved (EXPA-008 false activation closed). Full #254/#260-scoping MUST-NOT list holds — corpus/sha256 untouched (`test_corpus_is_frozen` passes), no semantic layer, no runtime dependency, no numeric-threshold promotion gate, SEC4 `capabilities_within_envelope` check stays BEFORE the new strength gate (a security DENY is still counted for every token-matched Skill), 6.22 trust gate / body-resource loading / `maps context` path all untouched, NO checklist STATUS flip (S6 + 6.9 stay IN PROGRESS, evidence prose only). Diff = exactly the MAY-touch files. luve's own 9-mutation set: 7 killed outright; the delta commit 1c335e2 (test-only, `runtime/` byte-unchanged, +3 tests) closes the 2 remaining (empty-stopword-set + anchor-count-boundary now killed by `SelectSkillsMatchStrengthGateTests` alone). Scope note: the PR closes only HARD_NEGATIVE of the 3 gaps the scoping note targeted — AMBIGUOUS + VOCABULARY_SHIFT V01 are shown lexically indistinguishable from hard negatives / a margin rule would regress MULTI_SKILL, so they are accepted as documented reviewer-accepted residuals (scoping note acceptance #1 permits this) and routed to the existing path-(b) §17.3 ruling; whoever re-runs the promotion gate step must know 1 of 3 gaps closed. VERDICT: APPROVE. Committer must be independent of gela (author) and luve (reviewer).
delta: rebound from 32cfbc7 to 1c335e2 — one test-only commit (`#260 delta: pin stopword set + anchor-count boundary`). `git diff 32cfbc7..1c335e2` = `tests/test_context_builder.py` +95, `runtime/` byte-unchanged. Adds 3 tests to `SelectSkillsMatchStrengthGateTests` (`test_stopword_set_is_load_bearing`, `test_stopwords_contribute_zero_to_match_strength`, `test_anchor_admits_a_df_two_token_not_only_df_one`) that directly close non-blocking note 1. Re-verified: M8 (empty `_SKILL_ROUTING_STOPWORDS`) and M9 (anchor `<=`→`<`) are now both KILLED by that class alone (baseline green, `test_context_builder` 39 OK). Verdict unchanged: APPROVE. (The original M8 in the table below was a no-op mutation — `frozenset() or frozenset({...})` evaluates to the non-empty set; the correct empty-set mutation is killed by the delta.)

_This evidence file was committed by maps-lean-vame, who is independent of gela (author) and luve (reviewer). Content is luve's verbatim review. Rebased onto #258+#259 (main 5f2e459) by session-20 coordinator maps-lean-mika; `head_sha` rebound to the rebased delta tip `b50c6a9` (was `1c335e2` pre-rebase; range-diff patch-identical)._

## Independent reproduction (real `_select_skills` → real `evaluate_skill_selection`, at HEAD)

`python3 -m unittest tests.test_exp_b_skill_routing tests.test_exp_a_skill_routing tests.test_skills_selection_evaluation tests.test_context_builder` → **Ran 51, OK** (foreground). `python3 -m runtime.smoke` → exit 0.

EXP-B report, my run, every figure matches the PR body + results note:
```
exact_cases 19  exact_rate 0.76  false_activation_cases 0  missed_activation_cases 4
ambiguity_misses 2  selection_precision 1.0  selection_recall 0.7647058823529411
selection_f1 0.8666666666666666  corpus_sha256 2cff0e40…4565  total_cases 25
category_accuracy: DIRECT 1.0 PARAPHRASE 1.0 MULTI_SKILL 1.0 NO_SKILL 1.0
                   HARD_NEGATIVE 1.0  VOCABULARY_SHIFT 0.0  AMBIGUOUS 0.0
```
EXP-A (v1): `exact 11  false_activation 0  precision 1.0  missed_activation 1  sha256 e5a87ec2…` — matches. EXPA-008 (marketing launch / lone word "release") now ABSTAINs; EXPA-007 unchanged miss.

## Acceptance criteria

| # | Criterion | Result |
|---|---|---|
| 1 | HARD_NEGATIVE false activations → 0 (**or a documented, reviewer-accepted residual**); AMBIGUOUS → both emit AMBIGUOUS; V01 → now routes | **PARTIAL — accepted.** HARD_NEGATIVE: fully MET, 4→0. AMBIGUOUS + V01: NOT delivered; documented as §6.33-class and accepted here as reviewer-accepted residuals (see "Scope reduction" below). |
| 2 | DIRECT / PARAPHRASE / MULTI_SKILL / NO_SKILL exact rate stays 1.00 | **MET** — all four hold at 1.00 (my run). No regression. |
| 3 | precision rises, recall does not fall | **MET** — precision 0.684→1.0; recall 0.7647→0.7647 (unchanged). |
| 4 | 4 modules foreground + smoke exit 0 | **MET** — Ran 51 OK; smoke 0. |
| 5 | ≥5 mutations on the score gate | **MET** — luve's 9-mutation set below, 7 killed + 2 closed by the delta. |
| 6 | Independent review; PR into main; author ≠ reviewer; coordinator merge-prep; no self-merge | **MET for review** — luve independent (gela authored). |

## Scope reduction from the scoping note's acceptance #1/#3 — ACCEPTED

The scoping note (`work/notes/2026-09-02-6.9-s6-selector-quality-scoping.md` §4) optimistically listed AMBIGUOUS and V01 alongside HARD_NEGATIVE. This PR closes **only HARD_NEGATIVE** and argues the other two are not lexically closeable. Verified against the frozen corpus:

- **V01** (`EXPB-V01`): the corpus note records V01 as a *zero-intersection ABSTAIN for the pre-PR selector too* — VOCABULARY_SHIFT was already 0.00 in #246, so this PR **does not regress it**. A plural/tense lemmatiser (the scoping note's proposal) would turn V01's match into the single distinctive token `credential`→`credentials`, weight 1.0 — **lexically identical** to hard-negatives `EXPB-H02` (`rotation`→`secrets-rotation`, 1.0) and `EXPB-H03` (`api`→`api-contract-review`, 1.0). Any strength floor admitting V01 re-admits H02/H03 → HARD_NEGATIVE regresses → violates acceptance #2. Adding the lemmatiser without lowering the floor is dead normalisation (MUST-NOT: no scope creep). **Not adding it is correct.**
- **AMBIGUOUS** (`EXPB-A01`/`A02`): not score-ties — `A01`'s token evidence favours `dependency-upgrade-review` (library+bump+version). A margin rule loose enough to flag A01 would also flag `EXPB-M01`, which *is* a genuine 3.0==3.0 tie where both Skills legitimately apply → MULTI_SKILL regresses from 1.00 → violates acceptance #2. **Not adding the margin rule is correct.**

The scoping note's acceptance #1 explicitly permits "a documented, reviewer-accepted residual." The pre-impl scoring simulation was confirmed by soda (coordinator, since dropped). Both residuals now route to the **same** path-(b) §17.3 reviewer/operator DONE ruling that #250's NO-FLIP already established for VOCABULARY_SHIFT — no new decision surface is created. **Whoever re-runs the promotion gate step must be aware the impl closed 1 of 3 targeted gaps, not 3.** That is noted in the results note §"Net effect" and the checklist evidence text.

## MUST-NOT walk — ALL HOLD

| MUST-NOT | Result |
|---|---|
| Edit `exp_a_skill_routing_v2.json` / its sha256 | HOLD — `test_corpus_is_frozen` passes unchanged; sha256 `2cff0e40…` in my run; JSON absent from `git diff --stat`. |
| Semantic / embedding / vector / thesaurus / learned expansion / synonym map beyond lemmatisation | HOLD — the gate is pure catalog-local `1/df` counting (`Counter` over `_text_tokens` of name+description). No lemmatiser was even added (see above). |
| Add a runtime dependency | HOLD — only `from collections import Counter` (stdlib). |
| Numeric pass threshold as the promotion gate | HOLD — the gate is a per-Skill surfacing filter, not a corpus-score threshold; no `f1 ≥ x` anywhere; no STATUS flip. |
| Tune floor / margin / stopword list to a specific EXP-B number | HOLD (see note 2 below). Floors are 2.0 / 0.5 / 2, round intent-values; the module comment states they are "not fitted to an EXP-A/B number." |
| Flip 6.9 / S6 / L4 / any checklist STATUS | HOLD — `git diff origin/main -- CAPABILITY_CHECKLIST.md`: S6 `IN PROGRESS`→`IN PROGRESS`, 6.9 `IN PROGRESS`→`IN PROGRESS`; only evidence prose appended. L4 untouched. |
| Touch 6.22 trust gate / SEC4 capability intersection / body-resource loading / `maps context` no-catalog path | HOLD — the new gate sits **after** `capabilities_within_envelope` (SEC4 DENY still counted for every token-matched Skill regardless of strength) and **before** the trust gate / body load. `_skill_trust_class`, `load_catalog_skill`, `load_skill_resource`, the `maps context` path — all absent from the diff. |

## Diff scope — CLEAN

`git diff --stat origin/main` = 6 files, all on the MAY-touch list:
`runtime/context_builder.py` (+97/-5), `tests/test_context_builder.py` (+ new `SelectSkillsMatchStrengthGateTests` class), `tests/test_exp_a_skill_routing.py` (pinned numbers), `tests/test_exp_b_skill_routing.py` (pinned numbers + structural asserts flipped: HARD_NEGATIVE now asserts ABSTAIN), `work/notes/2026-09-02-6.9-s6-selector-quality-results.md` (new), `work/roadmaps/CAPABILITY_CHECKLIST.md` (6.9 + S6 evidence text). No `runtime/skills/evaluation.py` change (the scoping note's "only if needed" — not needed).

## luve's mutation set (target: the gate block + its 3 constants; oracle: `SelectSkillsMatchStrengthGateTests` + `test_exp_a_skill_routing` + `test_exp_b_skill_routing`)

| # | Mutation | Result |
|---|----------|--------|
| M1 | `_SKILL_MATCH_STRENGTH_FLOOR` 2.0 → 0.0 | **KILLED** (FAILED 2) |
| M2 | `_SKILL_MATCH_COVERAGE_FLOOR` 0.5 → 1.1 | **KILLED** (FAILED 2) |
| M3 | `_SKILL_ANCHOR_MAX_SKILL_COUNT` 2 → 999 | **KILLED** (FAILED 1) |
| M4 | drop the anchor requirement | **KILLED** (FAILED 1) |
| M5 | remove df-weighting (`else 1.0 / token_skill_count[token]` → `else 1.0`) | **KILLED** by `test_df_weighting_is_load_bearing` (the author's synthetic test) |
| M6 | coverage denominator `len(matched) / len(signals)` → `/ len(matched)` | **KILLED** (FAILED 2) |
| M7 | strength/coverage floor `and` → `or` | **KILLED** (FAILED 2) |
| M8 | empty `_SKILL_ROUTING_STOPWORDS` | **CLOSED by delta** `1c335e2` (`test_stopword_set_is_load_bearing`) |
| M9 | anchor `token_skill_count[token] <= MAX` → `< MAX` | **CLOSED by delta** `1c335e2` (`test_anchor_admits_a_df_two_token_not_only_df_one`) |

**9 / 9 killed** after the test-only delta.

## Non-blocking notes

1. (Closed by the delta.) Stopword set + anchor-count boundary are now pinned by `SelectSkillsMatchStrengthGateTests`.
2. **Floor-not-fitted claim** — re-derived: STRENGTH_FLOOR 2.0 is cleared by any 2 distinctive tokens or 1 distinctive + strong corroboration; COVERAGE_FLOOR 0.5 is "most of the task's signal words." Defensible round intent-values; no corpus case sits within ±0.25 of a floor such that a small nudge flips it. Consistent with the MUST-NOT.
3. **`missed_activation_cases` stays 4** — V02–V04 were misses before and after; V01 joins them for a *principled* reason now (below the relevance floor) rather than synonym-blind-by-accident. Recall genuinely unchanged, not masked.

## Verdict: APPROVE
The headline safety failure (HARD_NEGATIVE false activation) is eliminated 4→0 with the four already-perfect categories held at 1.00 and recall unchanged; corpus/sha256 untouched; the full MUST-NOT list holds including the SEC4-check-before-strength-gate ordering; the diff is exactly the MAY-touch files; 9/9 mutations killed after the test-only delta. The AMBIGUOUS + VOCABULARY_SHIFT scope reduction is real but soundly argued and permitted by acceptance #1's "documented, reviewer-accepted residual" clause, routing to the existing path-(b) §17.3 ruling with no new decision surface — accepted, with the flag that the promotion-gate-step re-run must know 1 of 3 targeted gaps closed. Bound to `1c335e2be03ea9ade0ed9471f5319a9f67f4ae43`.
