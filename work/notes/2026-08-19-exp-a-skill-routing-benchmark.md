# EXP-A: Skill-routing frozen-corpus benchmark

Status: `EVIDENCE — EXP-A RUN AND LABELED, EXP-B..E STILL NOT RUN`

## What this is

Roadmap `work/roadmaps/agent-harness-capabilities/05-learning-and-evaluation.md`
phase L4 ("Research experiments A-E") defines EXP-A ("Skill selection
reliability") and the phase's task backlog lists "Build EXP-A Skill-selection
frozen eval corpus" (item 12). `work/roadmaps/CAPABILITY_CHECKLIST.md`'s L4
row previously said no code was labeled `EXP-A`, only "adjacent
infrastructure" (`runtime/skills/evaluation.py`'s eval harness, from phase S4
/ PR #27, with no real selector to run it against).

That gap closed with S6 (PR #109): `runtime/context_builder.py::_select_skills`
is the first real production Skill-selection logic in the repo. This
benchmark runs that real selector through the real
`evaluate_skill_selection` eval harness against a new frozen corpus, and is
therefore the first artifact that can honestly be labeled EXP-A.

This is **evaluation only**. No production file changed behavior:
`runtime/context_builder.py`, `runtime/skills/evaluation.py`,
`runtime/skills/catalog.py`, and `runtime/skills/format.py` are all
byte-for-byte unmodified by this work. New files only:

- `runtime/skills/eval_corpora/exp_a_skill_routing_v1.json` — the frozen corpus.
- `tests/test_exp_a_skill_routing.py` — builds a real `SkillCatalog` from
  on-disk `SKILL.md` files (same idiom as `tests/test_context_builder.py`),
  runs `_select_skills` per case, and calls `evaluate_skill_selection`.

## Corpus composition

12 cases across 5 candidate Skills, spanning 6 of the framework's 8
`SkillSelectionCategory` values:

| Category | Cases | Case IDs |
|---|---|---|
| DIRECT | 5 | EXPA-001..005 |
| PARAPHRASE | 1 | EXPA-006 |
| VOCABULARY_SHIFT | 1 | EXPA-007 |
| HARD_NEGATIVE | 2 | EXPA-008, EXPA-009 |
| NO_SKILL | 2 | EXPA-010, EXPA-011 |
| MULTI_SKILL | 1 | EXPA-012 |

`NEAR_MISS` and `AMBIGUOUS` were left out of this pass deliberately (bounded
scope, per the task's MVP framing) rather than omitted by oversight:
`_select_skills` has no notion of "ambiguous" outcome at all (it always
returns either an empty list or a flat list of matches — there's no
confidence signal to make an `AMBIGUOUS` case meaningful yet), and a
`NEAR_MISS` case is largely redundant with the `HARD_NEGATIVE` design used
here given the same literal-token-overlap mechanism drives both. A future
corpus revision could add both once the selector (or its eval framing)
grows a concept of confidence/ambiguity.

Each case carries a human-readable `task` string (satisfying the
`SkillSelectionCorpus` schema) *and* the literal `task_type` / `project_id`
/ `output_paths` fixture fields `_select_skills` actually reads — the two
were hand-designed to agree, but only the fixture fields drive the real
selector under test. `load_skill_selection_corpus` ignores the extra
fixture keys (not part of its schema); `tests/test_exp_a_skill_routing.py`
reads them straight from the raw JSON.

## How the corpus was designed against the real matcher

`_select_skills` selects a Skill iff `task_signal_tokens & skill_tokens` is
non-empty, where:

- `task_signal_tokens` = tokens (lowercase, `[a-z0-9]+`, length >= 3) from
  `task_type`, `project_id`, and every output-path filename segment.
- `skill_tokens` = tokens from the Skill descriptor's `name` + `description`.

This is a literal any-token-overlap match with **no** stopword filtering —
words like "for", "and", "service", "review", "planning", "writing" all
count as ordinary tokens if they appear in both a Skill description and a
task signal. Every DIRECT/PARAPHRASE/MULTI_SKILL/NO_SKILL/one HARD_NEGATIVE
case in this corpus was hand-verified token-by-token against all 5
candidate descriptions to either guarantee or deliberately avoid overlap
(see each case's `note` field in the corpus JSON for the specific reasoning,
e.g. EXPA-003's project_id uses "auth-platform" instead of "auth-service" to
avoid an accidental collision with load-test-planning's description, which
contains the bare token "service").

Two cases were deliberately designed to demonstrate the matcher's real
behavior rather than an idealized one:

- **EXPA-007 (VOCABULARY_SHIFT)**: intent is genuinely "rotate expiring
  access keys", matching `secrets-rotation`, but every fixture token is a
  synonym ("key" singular vs. "keys" plural, "cycling" vs. "rotation",
  "identity"/"platform"/"refresh"/"tokens" vs. the Skill's vocabulary) with
  zero literal overlap. Expected a miss going in.
- **EXPA-008 (HARD_NEGATIVE)**: a marketing blog post recap, unrelated to
  any Skill's actual purpose, but `task_type=blog_post_writing` contributes
  the token "writing", which also appears in `changelog-authoring`'s
  description ("Guidance for **writing** a clear customer-facing changelog
  entry..."). Expected a false activation going in.

## Results

Full report (`SkillSelectionEvalReport.to_dict()`), corpus
`sha256=e5a87ec260e540b241bb5a6e1f985c42ca4e9f8e1511c0477761b41268eaa884`:

| Metric | Value |
|---|---|
| total_cases | 12 |
| exact_cases | 10 |
| exact_rate | 0.833 (10/12) |
| selection_precision | 0.889 (8/9) |
| selection_recall | 0.889 (8/9) |
| selection_f1 | 0.889 |
| abstention_accuracy | 0.75 (3/4 ABSTAIN cases correct) |
| ambiguity_accuracy | null (no AMBIGUOUS cases in this corpus) |
| false_activation_cases | 1 (EXPA-008) |
| missed_activation_cases | 1 (EXPA-007) |
| ambiguity_misses | 0 |

Category accuracy: `DIRECT 1.0`, `PARAPHRASE 1.0`, `VOCABULARY_SHIFT 0.0`,
`HARD_NEGATIVE 0.5`, `NO_SKILL 1.0`, `MULTI_SKILL 1.0`.

Both non-exact cases were the two deliberately-designed ones above — no
case failed for a reason that wasn't anticipated at corpus-design time.

## Interpretation

**Precision risk is real, not hypothetical.** `_select_skills`'s
any-token-overlap rule with no stopword filtering means an unrelated task
can activate a Skill purely because a single common word ("writing",
"review", "planning", "service", "for", "and", ...) happens to appear in
both the task's structured fields and the Skill's description. EXPA-008
demonstrates this directly with real production code, not a synthetic
example: a marketing blog-post task activated `changelog-authoring` solely
via the shared word "writing". Any Skill catalog with descriptions using
common English words (which essentially all natural-language descriptions
do) will have some non-zero false-activation rate under this matcher,
proportional to Skill-catalog size and description length/genericness.

**Recall risk on vocabulary shift is also real.** EXPA-007 shows the
selector cannot see a Skill that's semantically clearly relevant but
described with different words than the task's structured fields use. This
is an inherent limitation of literal-token matching, not a corpus artifact.

**On production readiness (descriptive, not a decision):** this experiment's
findings say the current S6 selector functions correctly for its stated,
narrow contract — a highly precise "did this task and Skill share any
vocabulary at all" signal that fails closed on catalog/error edge cases
(per its own docstring). It is not, on this evidence, a semantically
reliable router: at 5 candidate Skills it already produced one false
activation and one missed activation on a 12-case corpus designed by a
human who knew the exact matching rule and was still only able to keep
10/12 cases clean. Precision/recall would very plausibly degrade further
as the real Skill catalog grows past 5 entries, since token-collision
probability rises with catalog size and description vocabulary overlap.
Whether that precision/recall level is acceptable for the selector's actual
use (advisory `SHOULD_LOAD` metadata in a context plan, not an
autonomous action-taking decision) is a product/policy judgment this
experiment does not make. This note reports what was measured; the
selector itself was not modified as part of this task, per its change
boundary.

## How to reproduce

```
python3 -m unittest tests.test_exp_a_skill_routing -v
```

The full report JSON prints to stdout as part of the run.
