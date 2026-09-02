# PR #254 review evidence — 6.9/S6 _select_skills selector-quality scoping note

Independent verification-only review by maps-lean-vame (gela authored). Design
note, 1 file (`work/notes/2026-09-02-6.9-s6-selector-quality-scoping.md`), no
runtime change. Verdict SCOPE-FOR-IMPL (HARD_NEGATIVE + AMBIGUOUS + V01
morphology); PARK the VOCABULARY_SHIFT synonym cases V02–V04.

## Method

Re-verified every mechanism claim against `origin/main` `e1e4467` (rule 14):
`_select_skills` / `_skill_task_signal_tokens` / `_text_tokens` /
`_MIN_TOKEN_LEN` in `runtime/context_builder.py`, `_run_predictions` in
`tests/test_exp_b_skill_routing.py`, `SkillSelectionOutcome` in
`runtime/skills/evaluation.py`. Read the 4 VOCABULARY_SHIFT cases (EXPB-V01–V04)
in the frozen corpus. Read roadmap §6.33 (line 1375) + §13.4 (line 1959).

## THE KEY CHECK — is parking V02–V04 as §6.33 correct, or dodging in-scope work?

**Correct. Not dodging.**

- §6.33 verbatim: *"Semantic retrieval / query expansion — EVIDENCE-GATED.
  Context Builder stays explicit-first. Promotion gate: a frozen evaluation
  containing paraphrases, vocabulary shifts, hard negatives and no-answer cases
  must demonstrate meaningful improvement over explicit/baseline."* So
  "vocabulary shifts closed by a retrieval/expansion mechanism" is *literally*
  the §6.33 gate — a separate EVIDENCE-GATED roadmap item, not 6.9 scope.
- The 4 cases confirm the split is real:
  - **V01** (`credential_renewal_cycle` → a Skill whose text has `credentials`):
    the miss is `credential` vs `credentials` — pure morphology. A deterministic
    ~10-line plural/tense normaliser closes it with zero semantic knowledge.
    SCOPED.
  - **V02–V04** (`brownout`≈`outage`, `surge/soak/spike`≈`load`,
    `payload shape`≈`contract`): zero shared stem, no morphological path — the
    task string never contains a lemma of any Skill concept word. Closing them
    needs a synonym map / thesaurus / embedding — all query expansion, all
    §6.33. A curated synonym map would (i) pre-empt §6.33's own evidence gate,
    (ii) be unbounded reviewer curation, (iii) risk HARD_NEGATIVE regressions.
    The note names all three. PARK is right.

## Sub-checks

(i) **HARD_NEGATIVE score + threshold is explicit-first (no embeddings).**
CONFIRMED. §2: distinctiveness = `1 / (#candidate Skills whose name|description
contains the token)` + a coverage fraction — computed from the candidate
catalog alone, no index/model/external data. A curated
`_SKILL_ROUTING_STOPWORDS` constant (like the existing `_MIN_TOKEN_LEN`).

(ii) **No operator-only decision in the impl.** CONFIRMED. §3 enumerates every
tunable (score floor, AMBIGUOUS margin, stopword list, lemmatiser rules) — all
"reviewer judgment / reviewer-curated constants", chosen from the mechanism's
intent, explicitly NOT fitted to an EXP-B number. The synonym map (the one thing
that could carry an authority question) is PARK.

(iii) **"DONE still needs path (b) §17.3 ruling on the residual synonym gap" is
flagged, not resolved.** CONFIRMED. §Verdict / §3 / §5: a recommendation
("narrowed bar is likely sufficient") but "that is the reviewer's / operator's
call" — the note does not assume the ruling.

(iv) **Frozen corpus untouched.** CONFIRMED. The PR touches one file. The
MUST-NOT list bans editing `exp_a_skill_routing_v2.json` / its sha256 and
requires `test_corpus_is_frozen` to still pass.

(v) **No status flip.** CONFIRMED. §6 "No checklist status changed." MUST-NOT
bans flipping 6.9 / S6 / L4. The impl slice's checklist change is deferred to
the separate reviewer gate step after the impl re-runs EXP-B.

## Non-blocking observations

1. `SkillSelectionOutcome.AMBIGUOUS` already exists (`evaluation.py:30`), so the
   AMBIGUOUS closure is adapter-only (`_run_predictions` emits the existing enum
   + the structural asserts flip) — the note's hedge is accurate.
2. §4 correctly flags that `test_exp_a_skill_routing.py` (v1) pinned *behaviour*
   numbers may legitimately shift with a reviewed selector change (v1 content
   frozen, its selector behaviour not) — consistent with
   `feedback_stale_slice_boundary_nongoal_test`.
3. The impl-slice acceptance criteria (§4) are AGI-standard-shaped — ready to
   dispatch on a YES to path (a).

## Verdict: APPROVE

`python3 -m runtime.smoke` → exit 0.

reviewer: maps-lean-vame
head_sha: ebff0928417000788fd059063459f3e6e77fc428
independent: true
summary: APPROVE — verification-only review of the 6.9/S6 selector-quality scoping note; the V02–V04 park is roadmap-correct (§6.33 explicitly gates query expansion / vocabulary shifts closed by a retrieval mechanism as a separate EVIDENCE-GATED item, and those cases have no morphological path), the V01 lemmatiser + HARD_NEGATIVE distinctiveness score + AMBIGUOUS margin are all genuinely explicit-first and computable from the catalog alone, no operator-only decision is buried in the impl (floor/margin values = reviewer judgment, not corpus-fitted), and the residual-gap §17.3 ruling is flagged with a recommendation rather than resolved; frozen corpus and all statuses untouched.
