# Task: Context budget classification for Context Builder (6.11)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `Claude / implementation agent`
- Risk: `LOW`
- Goal: classify the items `build_context_plan()` already explicitly gathers into the roadmap's MUST/SHOULD/MAY/ON-DEMAND context-budget classes, as advisory metadata, without adding any new retrieval, file search, or content-fetching mechanism.

## Inputs and source of truth

- Inputs: `AGENTS.md`; `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section "6.11 Context budgets / progressive context" (lines ~759-796); `work/roadmaps/CAPABILITY_CHECKLIST.md` (6.11 row); `runtime/context_builder.py`; `tests/test_context_builder.py`.
- Authoritative sources: roadmap 6.11's target classes (`MUST LOAD` / `SHOULD LOAD` / `MAY LOAD` / `ON DEMAND`) and guardrail ("Explicit-first Context Builder remains preferred until retrieval methods prove value in frozen evaluations") are the spec for this task. `runtime/context_builder.py`'s existing `guidance`/`withheld_guidance`/`skills` sibling-key pattern (from the operational-learning and S6 Skill-integration work, PR #109) is the structural precedent: this task adds a per-item `budget_class` field to items that are already present, never a new field that triggers fetching anything new.

## Design note: mapping and where 1:1 breaks down

The roadmap's four classes don't map cleanly onto `build_context_plan()`'s existing keys, so each mapping decision is documented in the module docstring on `build_context_plan()` itself (not just here) for anyone reading the code later:

- `authority` (AGENTS.md) -> `MUST_LOAD`. Direct match to the roadmap's own "active authority" example.
- `required` (task `inputs`/`sources`) -> `MUST_LOAD` for every item regardless of resolution `status`. Everything in `required` came from the task's own declared inputs/sources by construction, so importance is set by declaration, not by whether the file currently resolves.
- `boundaries` (decision_authority, output_paths, non_goals, acceptance_criteria, stop_conditions, verification, evidence_expected, review_required, escalation) -> conceptually `MUST_LOAD` as a whole ("task contract" / "policy"), but **not itemized** with a per-field tag. `boundaries` is always present in full on every plan (there is no partial case), so a uniform per-field tag would add no information beyond stating it once in the docstring/coverage note. This was an explicit choice to avoid inventing a distinction the data doesn't actually carry.
- `dependencies` -> `SHOULD_LOAD`. Direct match to the roadmap's own "direct dependencies" example.
- `guidance` (GUIDANCE_ONLY lesson projections) -> `SHOULD_LOAD` ("relevant decisions").
- `withheld_guidance` -> `ON_DEMAND`. These lessons were explicitly withheld (not applicable / superseded / expired), so they are not part of the default load set; `ON_DEMAND` best matches "material only pulled in if specifically pursued."
- `skills` (S6 addition, PR #109) -> `SHOULD_LOAD`. Direct match to the roadmap's own "applicable Skill" example.
- `unresolved` -> **not independently reclassified**. This list is built by filtering `[*authority, *required]` by resolution status, so each entry is literally the same dict object as its `authority`/`required` counterpart and already carries that item's `MUST_LOAD` tag by the time `unresolved` is computed. `budget_class` answers "how important would this be if available", not "is it currently loadable" — a missing MUST_LOAD input doesn't become less important for being missing. This is documented as a deliberate choice (not an oversight) in the module docstring.
- The roadmap's `MAY LOAD` ("secondary references") class has no current counterpart in `build_context_plan()`'s output — nothing the function gathers today fits that bucket, so no key is tagged `MAY_LOAD` in this pass. That's expected: v1 gathers only explicit, high-confidence relationships (its own `coverage.note`: "it does not search for unreferenced context"), so it has no "secondary reference" tier to classify yet.

## Guardrail compliance (explicit Stop/escalate note)

This task is metadata classification only:

- No new file search, directory scan, semantic retrieval, or external fetch was added. `_describe_reference`, `_lesson_guidance`, `_select_skills`, and the dependency lookup are unchanged in what they gather — only a `budget_class` string is attached to each item they already return.
- `coverage.semantic_retrieval_used` and `coverage.repository_scan_used` remain `False`; a new `coverage.budget_classification_present: True` (with a short `budget_classification_note`) documents that classification is present while retrieval stays explicit-first, per roadmap 6.11's guardrail.
- If a future task were to propose auto-loading MUST_LOAD items, auto-fetching SHOULD_LOAD items, or otherwise making `budget_class` change what gets read/searched, that would cross into new retrieval-mechanism territory and requires operator approval under 6.11's guardrail — out of scope here and explicitly not done.

## Change boundary

- MAY CHANGE: `runtime/context_builder.py` (add `budget_class` field to `authority`/`required`/`dependencies`/`guidance`/`withheld_guidance`/`skills` items, add `coverage.budget_classification_present`/`coverage.budget_classification_note`, extend the `build_context_plan()` docstring), `tests/test_context_builder.py`, `work/roadmaps/CAPABILITY_CHECKLIST.md` (6.11 row), this task file.
- MUST NOT CHANGE: any existing dict key removed or renamed in the plan's returned shape; `runtime/skills/*`; `runtime/operational_learning.py`; any new retrieval/search/fetch code path; CLI contract.
- OPERATOR APPROVAL REQUIRED: any change that makes `budget_class` drive actual loading/searching behavior (this task keeps it purely advisory/informational).

## Decision authority

- Owner may decide: exact mapping of existing keys to budget classes (documented above), exact `budget_class` string values (`MUST_LOAD`/`SHOULD_LOAD`/`ON_DEMAND`), whether to itemize `boundaries` (decided: no, documented instead), whether to reclassify `unresolved` (decided: no, documented instead).
- Owner must escalate: any design where `budget_class` is read by other code to decide what to load/fetch, or where a `MAY_LOAD` tier is invented without a corresponding data source to justify it.

## Acceptance criteria

- [x] Every item in `plan["authority"]` carries `"budget_class": "MUST_LOAD"`.
- [x] Every item in `plan["required"]` carries `"budget_class": "MUST_LOAD"`, regardless of resolution status.
- [x] Every item in `plan["dependencies"]` (including a missing/`UNKNOWN` dependency) carries `"budget_class": "SHOULD_LOAD"`.
- [x] Every item in `plan["guidance"]` carries `"budget_class": "SHOULD_LOAD"`.
- [x] Every item in `plan["withheld_guidance"]` carries `"budget_class": "ON_DEMAND"`.
- [x] Every item in `plan["skills"]` carries `"budget_class": "SHOULD_LOAD"`.
- [x] `plan["unresolved"]` items retain the `MUST_LOAD` tag inherited from their `authority`/`required` source item (documented, not independently tagged).
- [x] `plan["coverage"]["budget_classification_present"]` is `True` with an explanatory note; `semantic_retrieval_used`/`repository_scan_used` remain `False`.
- [x] No existing key in the returned plan dict shape was removed or renamed; all pre-existing tests in `tests/test_context_builder.py` pass unmodified.
- [x] No new retrieval/search/fetch mechanism was introduced anywhere in `runtime/context_builder.py`.
- [x] Full test suite passes.

## Follow-up (not in this PR)

- A `MAY_LOAD` tier has no current data source in `build_context_plan()`'s output; if a future task adds a "secondary references" concept to the plan, it should be classed `MAY_LOAD` at that point.
- Whether/how `budget_class` should influence an actual downstream context-loading step (a worker prompt assembler) is explicitly out of scope and would need its own task with operator approval, per the roadmap's guardrail.
