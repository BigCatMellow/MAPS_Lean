# Task: EXP-A Skill-routing frozen-corpus benchmark

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `EVALUATION`
- Owner: `Claude / implementation agent`
- Risk: `LOW`
- Goal: run the real production Skill-selection logic
  (`runtime/context_builder.py::_select_skills`, merged via PR #109 as part
  of S6) through the real Skill-routing eval harness
  (`runtime/skills/evaluation.py::evaluate_skill_selection`, merged via
  PR #27 as part of S4) against a new frozen corpus, and report the results
  — this is what L4's EXP-A ("Skill selection reliability") calls for, and
  until S6 landed there was no real selector for the S4 harness to evaluate.

## Inputs and source of truth

- Inputs: `work/roadmaps/agent-harness-capabilities/05-learning-and-evaluation.md`
  section "10. Core experiment program" / "EXP-A — Skill selection
  reliability" (corpus/metrics spec) and task-backlog item 12 ("Build EXP-A
  Skill-selection frozen eval corpus"); `work/roadmaps/CAPABILITY_CHECKLIST.md`
  L4 row (prior state: "no code is labeled EXP-A..E"); `runtime/context_builder.py`
  (`_select_skills`, `_skill_task_signal_tokens`, `_path_segment_tokens`,
  `_text_tokens`); `runtime/skills/evaluation.py` (all
  `SkillSelection*`/`SkillEvalCandidate` types, `load_skill_selection_corpus`,
  `evaluate_skill_selection`); `runtime/skills/catalog.py`
  (`build_skill_catalog`, `SkillCatalogSource`); `runtime/skills/format.py`
  (`SkillDescriptor` field shape, discovered via `discover_skills` rather
  than hand-built); `tests/test_skills_selection_evaluation.py` and
  `tests/test_context_builder.py` (construction idioms reused, not
  duplicated).
- Authoritative sources: the roadmap's EXP-A corpus/metric spec (positive
  cases, paraphrases, vocabulary shifts, near misses, hard negatives,
  multi-skill cases, no-skill cases; precision/recall/false
  activation/missed activation) and the existing S4 eval-harness contract
  (`SkillSelectionCorpus`/`SkillSelectionPrediction`/`SkillSelectionEvalReport`
  shapes) are unmodified specs this task exercises, not extends.

## Design note: what "run EXP-A" means given the harness/selector mismatch

The S4 eval harness (`evaluate_skill_selection`) keys predictions and
expectations by Skill *name* strings (`SkillEvalCandidate.name`). The S6
selector (`_select_skills`) operates on a real `SkillCatalog` of
`SkillCatalogEntry`/`SkillDescriptor` objects and a task-fixture dict
(`task_type`/`project_id`/`output_paths`), and has no notion of "candidate
name list" as an input — it just walks the whole catalog. The adapter this
task adds (`tests/test_exp_a_skill_routing.py`) is thin and one-directional:
build a real `SkillCatalog` whose descriptor names equal the corpus's
candidate names (via real on-disk `SKILL.md` files + `build_skill_catalog`,
not hand-built descriptor stubs), run `_select_skills(catalog, task)` per
case, and map the returned list's `name` field into a
`SkillSelectionPrediction.selected_skills` set. No routing logic lives in
the adapter; it only translates one real component's output into another
real component's expected input shape.

The frozen corpus (`runtime/skills/eval_corpora/exp_a_skill_routing_v1.json`)
was hand-designed against `_select_skills`'s actual (very permissive,
any-token-overlap, no-stopword-filtering) matching rule, verified
token-by-token per case (see each case's `note` field). Two cases were
deliberately built to demonstrate the matcher's real failure modes rather
than to make the corpus report a perfect score: EXPA-007 (VOCABULARY_SHIFT,
a genuine missed activation — the selector cannot see a pure synonym shift)
and EXPA-008 (HARD_NEGATIVE, a genuine false activation — the selector
fires on the shared common word "writing"). Full reasoning and results are
in `work/notes/2026-08-19-exp-a-skill-routing-benchmark.md`.

## Change boundary

- MAY CHANGE: `runtime/skills/eval_corpora/exp_a_skill_routing_v1.json` (new
  file), `tests/test_exp_a_skill_routing.py` (new file),
  `work/notes/2026-08-19-exp-a-skill-routing-benchmark.md` (new file),
  `work/roadmaps/CAPABILITY_CHECKLIST.md` (L4 row only), this task file.
- MUST NOT CHANGE: `runtime/context_builder.py`, `runtime/skills/evaluation.py`,
  `runtime/skills/catalog.py`, `runtime/skills/format.py`, any other
  existing test file, `work/evals/skill-selection-v1.json` (the existing S4
  corpus — this task adds a new, separate corpus rather than editing it).
- OPERATOR APPROVAL REQUIRED: any change that would tune, extend, or
  otherwise modify `_select_skills`'s matching behavior in response to this
  experiment's findings. This task reports evidence; it is not authorized
  to act on it.

## Decision authority

- Owner may decide: exact corpus case design/count (12 cases, 6 of 8
  categories — documented rationale for the two omitted categories in the
  results note), whether to encode the report assertions as exact expected
  numbers (decided: yes, so a future selector change is caught as a
  deliberate regression-review trigger rather than silently drifting).
- Owner must escalate: any proposal to change `_select_skills`'s matching
  rule based on this experiment's findings (out of scope here); any
  decision about whether the measured precision/recall is "acceptable" for
  a specific downstream use of Skill selection (this task reports
  evidence, not a go/no-go judgment).

## Acceptance criteria

- [x] `runtime/skills/eval_corpora/exp_a_skill_routing_v1.json` exists,
  validates via `load_skill_selection_corpus`, and covers DIRECT,
  PARAPHRASE, VOCABULARY_SHIFT, HARD_NEGATIVE, NO_SKILL, and MULTI_SKILL
  categories (12 cases total).
- [x] `tests/test_exp_a_skill_routing.py` builds a real `SkillCatalog` from
  on-disk `SKILL.md` files, runs the real `_select_skills` per case, and
  calls the real `evaluate_skill_selection` — no stub/synthetic selector.
- [x] The resulting `SkillSelectionEvalReport` is printed and asserted
  against in the test (precision/recall/F1/category accuracy/false and
  missed activation counts).
- [x] `work/notes/2026-08-19-exp-a-skill-routing-benchmark.md` reports the
  full numbers, corpus composition, and an honest interpretation
  (permissive-matcher precision risk called out explicitly, since this
  corpus surfaced a real false activation).
- [x] `work/roadmaps/CAPABILITY_CHECKLIST.md` L4 row updated to state EXP-A
  specifically has been run/labeled, while L4 overall remains IN PROGRESS
  (EXP-B..EXP-E untouched).
- [x] None of `runtime/context_builder.py`, `runtime/skills/evaluation.py`,
  `runtime/skills/catalog.py`, `runtime/skills/format.py` changed.
- [x] `python3 -m unittest tests.test_exp_a_skill_routing -v` passes.
- [x] Full suite (`python3 -m unittest discover -s tests -v`) passes.

## Follow-up (not in this task)

- EXP-B (hook control/treatment comparison), EXP-C (ACI comparison), EXP-D
  (EnvironmentSpec reproducibility comparison), and EXP-E (malicious Skill
  red-team suite) remain unrun; L4 stays IN PROGRESS until they are.
- If a future task wants to reduce `_select_skills`'s demonstrated
  false-activation risk (e.g. stopword filtering, minimum overlap count, or
  a confidence/ambiguity signal), that is a deliberate, reviewed change to
  `runtime/context_builder.py` requiring operator approval — this task only
  measured and reported the current behavior.
- A `NEAR_MISS`/`AMBIGUOUS`-category extension to this corpus would need
  the selector to grow some confidence/ambiguity concept first (or a
  redefinition of what those categories mean against a binary
  select/abstain selector); noted but out of scope here.
