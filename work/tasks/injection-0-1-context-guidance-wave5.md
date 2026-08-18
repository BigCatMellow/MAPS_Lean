# Task: attributed GUIDANCE_ONLY lesson evidence in Context Builder, Injection-0/1

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/injection-0-1-context-guidance-wave5`
- Risk: `MEDIUM`
- Goal: Implement `Injection-0` and `Injection-1` from
  `work/notes/2026-08-17-operational-learning-authority-design.md` --
  surface already-promoted `ACTIVE` operational lessons into Context
  Builder's output as one more attributed, `GUIDANCE_ONLY`-labeled evidence
  item, per the operator decision recorded there (design note line ~536:
  "Safe context injection: authorized, bounded to operator-promoted ACTIVE
  lessons only, as an attributed `GUIDANCE_ONLY` Context Builder evidence
  item -- never spliced into instructions").

## Inputs and source of truth

- `work/notes/2026-08-17-operational-learning-authority-design.md` (merged
  PR #79), section 5 "Safe context injection" -- exact interface shape to
  reuse: `lesson_id`, `claim`, `source_kind`, `source_refs`,
  `promotion_decision_ref`, `authority: "GUIDANCE_ONLY"`.
- `runtime/operational_learning.py` (merged PR #43, unmodified by this task)
  -- `project_applicable_lessons()` already produces this exact shape plus
  a top-level `authority` block (`can_grant_task_authority: False`,
  `can_grant_policy_authority: False`, `can_promote_candidates: False`).
  This task reuses it as-is; it does not reimplement projection logic.
- `runtime/state/operational_learning_storage.py` (merged PR #98/Authority-1
  wave4) -- has `get_operational_lesson`/`list_operational_lesson_candidates`
  but no "list all promoted lessons" read. This task adds exactly one new
  read method, reusing the existing `_compose`/`_lesson_row` helpers.
- `runtime/context_builder.py` (merged, unmodified structurally by this
  task except one additive section) -- `build_context_plan()` is the only
  place a worker's context is assembled from explicit, attributed sources
  (roadmap law 4.7, "derived views stay derived"); guidance must follow the
  same pattern as `authority`/`required`/`dependencies`, not be spliced into
  any instruction text.
- Roadmap law 4.2 ("capability is not authority").

## Change boundary

MAY CHANGE / ADD:
- `runtime/state/operational_learning_storage.py` (additive: one new
  read-only method, `list_active_operational_lessons()`)
- `runtime/context_builder.py` (additive: one new `guidance` section in the
  returned context plan, built by calling `project_applicable_lessons()`
  with the task's own `project_id`/`task_type`/`risk`/`output_paths` as
  context; `withheld` lessons are never surfaced)
- `tests/test_operational_learning_storage.py`, `tests/test_context_builder.py`
- this task doc

MUST NOT CHANGE:
- `runtime/operational_learning.py` (projection logic, `GUIDANCE_ONLY`
  labeling, `authority` block)
- promotion/retirement/candidate-recording mutation paths
- task/session/review/policy authority of any kind
- `build_context_plan()`'s existing `authority`/`required`/`dependencies`/
  `boundaries`/`unresolved` sections and their meaning

## Required semantics

1. Only `ACTIVE` lessons (promoted, not retired, not expired/not-yet-started
   per `project_applicable_lessons()`'s own time/status gating) can appear in
   `guidance`. `CANDIDATE` and `RETIRED` lessons are never surfaced, matching
   existing `project_applicable_lessons()` behavior -- this task supplies the
   read path, it does not change the gating.
2. Each surfaced item preserves the full existing projected shape verbatim,
   including `"authority": "GUIDANCE_ONLY"` -- this task must not strip,
   rename, or "flatten" that label anywhere between storage and the returned
   plan.
3. `guidance` is a sibling of `authority`/`required` in the returned dict,
   never merged into task instructions, `boundaries`, or any field an agent
   could plausibly read as a directive.
4. Context passed to `project_applicable_lessons()` is derived only from the
   task's own already-canonical fields (`project_id`, `task_type`, `risk`,
   `output_paths` as `paths`) -- no inference, no cross-task lookups.
5. `withheld` lessons (and the reason they were withheld) are available in
   the plan for traceability but are clearly namespaced apart from
   `guidance` and never presented as applicable.
6. If no lessons exist at all (empty candidate/lesson table), `guidance` is
   an empty list, not omitted -- callers should not need to branch on key
   presence.
7. Lesson read failure (e.g. a malformed stored record fails
   `validate_lesson_record()` during projection) must fail closed for that
   one lesson without breaking the rest of context-plan assembly for tasks
   that don't depend on it -- `build_context_plan()`'s other sections
   (authority/required/dependencies/boundaries) must still be returned.

## Decision authority

- Owner may decide: exact key name (`guidance`), read-method name/signature,
  how `withheld` is surfaced, `at` timestamp source (current UTC time at
  build time).
- Owner must escalate: any automatic worker-context inclusion mechanism
  beyond Context Builder's existing plan output (e.g. injecting into a
  system prompt directly) -- out of scope, not authorized by Injection-1.

## Acceptance criteria

- [ ] `list_active_operational_lessons()` returns only composed rows whose
      effective status is `ACTIVE` (has a `PROMOTE` decision, no `RETIRE`
      decision), reusing `_compose`.
- [ ] `build_context_plan()` output includes a `guidance` list built from
      `project_applicable_lessons()`'s `projected` output for the task's own
      context, with `authority: "GUIDANCE_ONLY"` intact on every item.
- [ ] No `CANDIDATE` or `RETIRED` lesson, and no lesson `project_applicable_lessons()`
      places in `withheld`, ever appears in `guidance`.
- [ ] `guidance` is present (possibly empty) even when zero lessons exist.
- [ ] A malformed persisted lesson record does not raise out of
      `build_context_plan()` and does not block the rest of the plan.
- [ ] Focused tests cover: empty-lessons case, one ACTIVE lesson matching
      context, one ACTIVE lesson excluded by non-matching applicability, one
      CANDIDATE lesson never surfaced, one RETIRED lesson never surfaced.
- [ ] `python -m unittest tests.test_operational_learning_storage tests.test_context_builder -v` passes.
- [ ] independent exact-head review confirms the `GUIDANCE_ONLY` label and
      non-instruction placement are mechanically preserved end to end.

## Verification

```text
python -m unittest tests.test_operational_learning_storage tests.test_context_builder -v
python -m unittest discover -s tests -v
```

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## Stop / escalate

Stop rather than guess if:
- any change would let a lesson's claim text reach a worker anywhere other
  than this one attributed, labeled evidence item;
- context derivation for `project_applicable_lessons()` would require
  inferring a field not already canonical on the task row;
- `project_applicable_lessons()` itself needs to change (out of scope --
  escalate back to the design note).
