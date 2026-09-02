# PR #246 review evidence — 6.9/S6 EXP-B expanded frozen Skill-selection evaluation

reviewer: maps-lean-luve
head_sha: ebfe1c3a8f7254c1a284babe80a7dd6b34d337c4
independent: true
summary: Independent review by maps-lean-luve (did not author — gela did; vame co-authored the EXPB-P/V cases so is not independent there). The corpus meets §6.9's coverage+existence promotion-gate bar: `exp_a_skill_routing_v2.json` (25 cases, 7 concept-controlled candidate Skills) has ≥4 deliberate cases in every one of §6.9's six categories (DIRECT 5, PARAPHRASE 4, VOCABULARY_SHIFT 4, MULTI_SKILL 2 + AMBIGUOUS 2 = "overlapping Skills" 4, HARD_NEGATIVE 4, NO_SKILL 4); `test_exp_b_skill_routing.py` runs the real `runtime.context_builder._select_skills` against a real on-disk `SkillCatalog` through the real `runtime.skills.evaluation.evaluate_skill_selection` — no stubs — and pins `version` + `sha256` (`2cff0e40…`) + the category composition + four observed metrics. The frozen `sha256` catches any corpus content change (mutation-proven). NO selector/harness touch (`context_builder.py` / `evaluation.py` / `catalog.py` / `format.py` byte-identical — diff = 4 new/changed files only). NO status flip — 6.9 stays IN PROGRESS; both the note and the test docstring are explicit that flipping 6.9/S6 to DONE (optionally against the note's proposed §criterion) is a separate reviewer gate step, not asserted here. The selector's genuine weaknesses (0.00 on VOCABULARY_SHIFT / HARD_NEGATIVE / AMBIGUOUS; 15/25 exact; f1 0.722) are documented transparently, "pinned not tuned". Own mutation pass on the corpus + run module: 5 killed / 6 (M4 near-equivalent — one of four redundant metric asserts loosened in isolation). ONE blocking finding: the recording note's "Authoring discipline" section claims PARAPHRASE cases have "no Skill-name synonyms" and overlap "only via concept words unique to [the target Skill's] description (verified against the per-Skill token sets)" — a spot-check contradicts this for 2 of the 4: EXPB-P01's deciding token `migration` (carried by the output path `ops/migration_backfill_plan.md`) is in the target Skill's name `data-migration-runbook`, and EXPB-P03's `dependency` (in `task_type=transitive_dependency_advisory`) is in `dependency-upgrade-review`. So PARAPHRASE=1.00 was partly a name-token match for those two. Round 1 verdict was REQUEST_CHANGES (narrow — note accuracy); the round-2 delta (`7e29280`, option b) reworded that note paragraph to name EXPB-P01/P03 explicitly and state the constraint actually applied ("overlap must not rest solely on Skill-name tokens"), plus the two non-blocking fixes (`_NON_OVERLAPPING_CATEGORIES` rename; the no-DIRECT-case acknowledgement). No corpus change — sha256 stays `2cff0e40…`, all four metrics unchanged. FINAL VERDICT: APPROVE.

## Verified (against origin/main `891045e` — current HEAD, no rebase needed)

Worktree off `origin/s6-frozen-eval-v2-corpus`; clean. Diff = 4 files, +786:
`runtime/skills/eval_corpora/exp_a_skill_routing_v2.json` (new),
`tests/test_exp_b_skill_routing.py` (new),
`work/notes/2026-09-01-exp-b-skill-selection-frozen-eval.md` (new),
`work/roadmaps/CAPABILITY_CHECKLIST.md` (+2/-1).

### §6.9 category coverage — MET
`Counter(case.category.value)` on the loaded corpus: `DIRECT 5, PARAPHRASE 4,
VOCABULARY_SHIFT 4, MULTI_SKILL 2, AMBIGUOUS 2, HARD_NEGATIVE 4, NO_SKILL 4` =
25. `test_corpus_covers_every_6_9_category_with_depth` asserts ≥4 for each of
the 5 non-overlapping categories, ≥4 for `MULTI_SKILL + AMBIGUOUS` together
("overlapping Skills" per §6.9 / design §4a), no unexpected category, exactly
25 cases + 7 candidates. §6.9's promotion gate (roadmap 706–708) is a coverage
+ existence bar with no numeric threshold — this corpus + test establish it.

### Real selector through real harness — no stubs
`test_real_selector_through_real_eval_harness` builds a real `SkillCatalog`
from on-disk `SKILL.md` files (`build_skill_catalog` on a `LOCAL` source), calls
the real `_select_skills(catalog, {task_type, project_id, output_paths})` per
case, and passes the predictions to the real `evaluate_skill_selection`. The
module docstring pledges no modification to the four production files and the
diff confirms it. Modeled on `test_exp_a_skill_routing.py` per design §4b.
Mutation M5 (stub `_select_skills` → always-empty) is killed.

### Frozen
`test_corpus_is_frozen` pins `version == "exp-a-skill-routing-v2"` and
`corpus.sha256 == "2cff0e405c2f0201759ad8d23ed84fbb60bc1ec7d5513be2ad9b4c54fe5f4565"`.
The loader (`evaluation.py:290`) computes the sha256 as a pure function of the
canonical file bytes, so any content edit changes it — mutations M2 (relabel a
case), M3 (add a 26th case), M6 (drop 2 cases) are all killed by the sha256
assertion even when a downstream assertion is also loosened. `v1.json` /
`test_exp_a_skill_routing.py` untouched (frozen historical artifact).

### No selector tuning
Observed: `exact 15/25`, `missed_activation 4`, `false_activation 4`,
`ambiguity_misses 2`, `f1 0.722` (matches gela's report). The test pins these
as a regression detector and structurally asserts every AMBIGUOUS case is
non-exact (S6 has no `AMBIGUOUS` outcome) and every HARD_NEGATIVE case
`SELECT`s (accidental token overlap). VOCABULARY_SHIFT cases carry
`expected_outcome = SELECT` (what a robust selector *should* do) and the
selector's `ABSTAIN` is recorded as the recall gap — not tuned away. Consistent
with `test_exp_a`'s docstring rule ("update the assertions only alongside a
deliberate, reviewed selector change").

### No status flip
`CAPABILITY_CHECKLIST.md` 6.9 row `IN PROGRESS` → `IN PROGRESS` (verified both
`-`/`+`). One evidence clause added — "the frozen selection evaluation … now
**exists**", records the 6-category coverage, the observed 15/25 + per-category
1.00/0.00 split, "gaps the frozen test pins, not tunes away", and "flipping
6.9/S6 to DONE … is a separate reviewer gate step — **no status flip here**".
The test docstring and note §6 say the same.

### Mutation testing — 5/6 killed
| # | Mutation | Result |
|---|----------|--------|
| M1 | drop a `VOCABULARY_SHIFT` case (V04) from the corpus | KILLED (covers-depth: count 3 < 4) |
| M2 | relabel a `DIRECT` case as `PARAPHRASE` | KILLED (sha256 freeze) |
| M3 | append a 26th case | KILLED (sha256 + `len == 25`) |
| M4 | loosen `assertEqual(report.exact_cases, 15)` → `>= 0` (alone) | **SURVIVED — near-equivalent** |
| M5 | stub `_select_skills` → `selected = []` | KILLED (metrics shift) |
| M6 | loosen the ≥4 covers-depth assert **and** drop 2 vocab cases | KILLED (sha256 freeze) |
**M4**: `exact_cases` / `missed_activation_cases` / `false_activation_cases` /
`ambiguity_misses` are four separately-pinned metrics; a single real case flip
trips ≥2 of them, so loosening one in isolation (with the corpus unchanged)
breaks nothing. Redundant-by-design regression detection, not a coverage gap.

## Required change (narrow)

The recording note's **"Authoring discipline"** paragraph:
> "**PARAPHRASE** cases reword the intent (no Skill-name synonyms) and the
> fixture tokens overlap the *target* Skill only via **concept words unique to
> its description** (verified against the per-Skill token sets…)"

is inaccurate for **2 of the 4** PARAPHRASE cases (checked: query tokens
[`task_type` + `project_id` + `output_paths` segments] ∩ target-Skill-**name**
tokens):
- **EXPB-P01** → `data-migration-runbook`: overlap `{migration}` — carried by
  the output path `ops/migration_backfill_plan.md`. `migration` is in the
  Skill **name**, not "unique to its description".
- **EXPB-P03** → `dependency-upgrade-review`: overlap `{dependency}` — in
  `task_type=transitive_dependency_advisory`. `dependency` is in the Skill
  **name**.
- EXPB-P02 / P04 and all four VOCABULARY_SHIFT cases are clean (no
  name-token overlap — verified).

Effect: PARAPHRASE scoring 1.00 is, for P01/P03, partly attributable to a
Skill-name token match — the §4a anti-pattern ("synonyms of the Skill name …
would just test tokenization"). Those two are closer to DIRECT than to a
paraphrase, which dilutes what a reviewer running the 6.9 gate step can
conclude from "selector: 1.00 on paraphrase".

**Fix — either:**
(a) re-author EXPB-P01 / EXPB-P03 so the deciding overlap is a description-only
   concept word absent from the Skill name (e.g. P01 lean on "cutover" /
   "dual-write" / "backfill" and drop `migration` from the path; P03 lean on
   "third-party library" / "version bump" / "transitive" and drop `dependency`),
   then re-pin `sha256` + the four observed metrics; **or**
(b) if `migration` / `dependency` are judged unavoidable domain vocabulary,
   correct the note's Authoring-discipline claim to state that EXPB-P01 / P03
   retain one token shared with the target Skill's name, so PARAPHRASE=1.00 is a
   partial floor for those two.

## Non-blocking notes
1. `_SIX_CATEGORIES` in `test_exp_b_skill_routing.py` is a 5-element set (the
   non-overlapping categories; overlapping is handled by the separate
   `MULTI_SKILL + AMBIGUOUS` assert). The name reads as "all six" — rename to
   `_NON_OVERLAPPING_CATEGORIES` or similar.
2. `changelog-authoring` and `dependency-upgrade-review` have **no DIRECT
   case** (DIRECT covers 5 of the 7 candidate Skills). §6.9 "direct matches ≥4"
   is met (5 cases) and the gate does not require one per Skill — worth a
   one-line acknowledgement in the note.
3. `smoke` exit 0; `tests.test_exp_b_skill_routing tests.test_exp_a_skill_routing
   tests.test_skills_selection_evaluation` → 15 tests OK.

## Round 1 verdict: REQUEST_CHANGES (note's PARAPHRASE Authoring-discipline claim inaccurate for EXPB-P01/P03).

## Round 2 (delta `6c995cf..7e29280`, option b) — verified

- **Note "Authoring discipline" PARAPHRASE bullet reworded** to the constraint
  actually applied — *"the overlap must not rest solely on tokens shared with
  the Skill name"* — and it now **names EXPB-P01 (`migration` via output path)
  and EXPB-P03 (`dependency` via `task_type`)** as the two cases that retain one
  Skill-name token, states the selection is *additionally* carried by
  description-unique concept words (P01: `schema`/`backfill`/`cutover`/`database`;
  P03: `transitive`/`advisory`/`lockfile`/`bump`), and concludes
  *"PARAPHRASE = 1.00 is a partial floor for those two, not a pure name-token
  match."* The VOCABULARY_SHIFT bullet already correctly identifies those as the
  cases that avoid every name+description token. Accurate now.
- **Non-blocking note 1** — `_SIX_CATEGORIES` → `_NON_OVERLAPPING_CATEGORIES`
  (+ clarified comment).
- **Non-blocking note 2** — the note now acknowledges `changelog-authoring` /
  `dependency-upgrade-review` have no DIRECT case, with the §6.9 rationale
  (≥4 direct matches, not one per Skill).
- **No corpus change** — `exp_a_skill_routing_v2.json` byte-identical
  (`git diff 6c995cf..HEAD -- …v2.json` empty), so `sha256` stays
  `2cff0e40…` and all four pinned metrics are unchanged. Delta = 2 files
  (test symbol rename + note prose).
- Re-verified: `tests.test_exp_b_skill_routing` 3/3 OK; `runtime.smoke` exit 0.

## Final verdict: APPROVE
All round-1 "verified" findings hold (coverage+existence bar met, real selector
through real harness no stubs, genuinely frozen, no selector/harness touch, no
status flip, §criterion proposed not asserted, 0.00 categories documented not
tuned, 5/6 mutations killed). The one blocking item — note↔corpus accuracy on
the PARAPHRASE cases — is fixed (option b, note reword only, no re-freeze
needed). Bound to `7e29280e23e24b3fb73eb19d992fffcd2cef25e6`. @coordinator
commits this evidence file. NB the 6.9/S6 → DONE status flip is a separate
reviewer gate step, out of this PR's scope.
