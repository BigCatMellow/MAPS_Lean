# Review: PR #192 — SEC4/6.10 Half 2: wire durable Skill lifecycle store into real behavior

reviewer: independent-reviewer-mavo
head_sha: d84a0811136a34796a8f5db2697489f9ec882203
independent: true
summary: APPROVE - diff matches #190 in-scope table (catalog.py/__init__.py/trust.py/context_builder.py + 4 test files + CAPABILITY_CHECKLIST evidence-text only, no status flip; storage.py + memory_trust_gate.py comment/docstring-only); verified SkillTrustState fully deleted with no dangling import, register_skill_catalog idempotent + gate-driven, build_skill_catalog(store=None) behaviourally identical to old UNASSESSED default, one-directional store->provenance->trust-class projection, fingerprint no longer folds the trust field (round-trip + content-change tests hold via content_sha256), load_catalog_skill refuses QUARANTINED/RETIRED/SUPERSEDED only when store given, unassessed _select_skills admission outcome unchanged from main; 5/5 mutations caught; full target suite (103 tests) + runtime.smoke green.

## Method

Fresh worktree at `origin/impl/sec4-half2-authority-wiring` (`8a0e8f0`), never the
main worktree. Every claim re-derived at the reviewed head with git / grep / a
real temp-file `TaskStore`; nothing taken from the PR body. Source of truth:
`work/notes/2026-08-31-sec4-half2-authority-wiring-design.md` "Half 2 impl — scope
boundary" table + 7-step Resume prompt. Reviewer did not author PR #192 (lire),
PR #190 (fido), or the parent persistence note.

### 1. Scope

`git diff origin/main...HEAD --stat` — 12 files:

| File | In #190 table? |
|---|---|
| `runtime/skills/catalog.py` (+114/-17) | yes |
| `runtime/skills/__init__.py` (+2/-2) | yes (export rename) |
| `runtime/trust.py` (+12/-31) | yes |
| `runtime/context_builder.py` (+33/-9) | yes |
| `runtime/state/skill_lifecycle_storage.py` (+19/-10) | **docstring-only** — permitted ("beyond docstring" is the forbidden part); verified no code/method change |
| `runtime/policy/memory_trust_gate.py` (+6/-4) | **not named**; comment-only correction of a now-stale sentence about `skill_trust_class()` (rule 14). No behavior change. Non-blocking. |
| `tests/test_skills_catalog.py` (+108/-6) | yes (new coverage) |
| `tests/test_trust.py` (-18) | yes (enum-rename) |
| `tests/test_context_builder.py` (+8/-7) | yes (field rename) |
| `tests/test_skill_lifecycle_storage.py` (+21/-12) | consequential — the Half-1 "zero production consumer" guard test necessarily flips to "read-side consumers only"; NOT the forbidden `tests/test_skill_lifecycle.py` contract file |
| `work/roadmaps/CAPABILITY_CHECKLIST.md` (+2/-2) | yes — SEC4 (line 60) and 6.10 (line 119) both stay `IN PROGRESS`, evidence text only, no status flip |
| `work/reviews/pr-192-review-evidence.md` | this file |

No out-of-scope hunk: no operator-identity registry, no capability manifest, no
`cli.py`/`flow_start.py` catalog wiring, no `runtime/state/schema.sql` change, no
`runtime/skills/lifecycle.py` change, no `tests/test_skill_lifecycle.py` edit.
`git diff --check` clean. `python3 -m py_compile` on all 6 changed modules: OK.

### 2. Behavior correctness (vs #190 design)

- **`register_skill_catalog(catalog, store, *, now=None)`** — content-addressed
  `catalog_key` pre-check via `store.get_skill_lifecycle_subject(...)`, then
  `assess_skill(entry.descriptor)` gate, then `store.record_skill_lifecycle_subject`.
  Idempotent (test: 2nd call returns `[]`, one subject row). Matches Q4 shape.
- **`build_skill_catalog(store=None)`** — `catalog_key` computed, then
  `store.get_skill_lifecycle_state(catalog_key) if store is not None else None`.
  With `store=None` every `SkillProvenance.lifecycle_state` is `None`; catalog
  entries/fingerprint byte-identical to `origin/main` behavior (test
  `test_catalog_build_without_store_leaves_lifecycle_state_none`). "No production
  behavior change today" holds.
- **Rule-12 collapse** — `SkillTrustState` enum deleted from `catalog.py`;
  imports removed from `trust.py`, `runtime/skills/__init__.py` (+ `__all__`),
  `context_builder.py`, `tests/*`. `grep -rn SkillTrustState runtime/` → only
  `lifecycle.py` docstring (untouched, known deferred nit) + `trust.py` /
  `context_builder.py` explanatory comments. `SkillProvenance.lifecycle_state:
  SkillLifecycleState | None = None`. `trust.py` keeps only
  `skill_lifecycle_trust_class`; `skill_trust_class` +
  `_SKILL_TRUST_STATE_TO_MEMORY_TRUST_CLASS` gone. The `None -> OBSERVATION`
  guard lives in `context_builder._skill_trust_class` (the call-site module),
  not inside `trust.py` — `trust.py` still takes a real enum member only.
  Derivation strictly one-directional store -> provenance -> trust class;
  nothing writes back.
- **`_select_skills`** — projects via `_skill_trust_class(lifecycle_state)`;
  unassessed (`None`) Skill still -> `OBSERVATION` -> `ON_DEMAND` metadata with
  `withheld_reason`, class/action unchanged from `main` (test
  `test_context_builder`, baseline green). Emitted field `trust_state` ->
  `lifecycle_state` (`.value` or `None`), consistent in the one reader
  (`tests/test_context_builder.py:639`); `tests/test_skills_selection_evaluation.py`
  passes unmodified.
- **Fingerprint** — `entry.provenance.trust_state.value` removed from the
  `SkillCatalog.__post_init__` digest tuple. `content_sha256` still hashed.
  `test_fingerprint_is_content_only_not_lifecycle_sensitive` (store-populated
  vs plain catalog -> equal fingerprint) + round-trip equality + content-change
  tests hold. Confirmed zero `.fingerprint` readers outside `catalog.py` +
  2 test assertions.
- **`load_catalog_skill(entry, store=None)`** — when `store` given, raises
  `SkillCatalogError` iff composed state in
  `{QUARANTINED, RETIRED, SUPERSEDED}`; `VALIDATED`/`APPROVED`/`ACTIVE`/`None`
  pass. `store=None` -> unconditional `load_skill(entry.descriptor)`, unchanged
  (tests `test_load_catalog_skill_refuses_non_activatable_state`,
  `..._allows_activatable_and_unassessed`).

### 3. Mutation testing — 5/5 caught

One blocking foreground `python3 -m unittest <target module>` per mutation;
mutation reverted before the next; `git status` clean after.

| # | Mutation | Target module | Result | Caught by |
|---|---|---|---|---|
| 1 | `catalog.py:245` idempotency pre-check `is not None` -> `is None` | `tests.test_skills_catalog` | FAILED (3 failures) | `test_register_skill_catalog_records_subjects_and_is_idempotent` (`0 != 1`) |
| 2 | `context_builder.py:38` `if lifecycle_state is None` -> `is not None` (drop `None->OBSERVATION`) | `tests.test_context_builder` | FAILED (2 failures) | unassessed-Skill load-set assertion (`[] is not true`) |
| 3 | `catalog.py` remove `SkillLifecycleState.RETIRED` from `_NON_ACTIVATABLE_LIFECYCLE_STATES` | `tests.test_skills_catalog` | FAILED (1 failure) | `test_load_catalog_skill_refuses_non_activatable_state` (`SkillCatalogError not raised`) |
| 4 | `catalog.py:283` `load_catalog_skill` guard `if store is not None` -> `if store is None` | `tests.test_skills_catalog` | FAILED (1 failure, 1 error) | refusal test + `store=None` path |
| 5 | `catalog.py:202` `build_skill_catalog` projection `if store is not None` -> `if store is None` | `tests.test_skills_catalog` | FAILED (12 errors) | `AttributeError` on `None.get_skill_lifecycle_state` across store-path tests |

### 4. Full target suite

- `python3 -m unittest tests.test_skills_catalog tests.test_trust
  tests.test_context_builder tests.test_skill_lifecycle
  tests.test_skill_lifecycle_storage tests.test_skills_selection_evaluation`
  -> `Ran 103 tests ... OK` (exit 0), one blocking foreground call.
- `python3 -m runtime.smoke` -> `"ok": true` (exit 0).
- Worktree `git status` clean after all mutations reverted.

### 5. Non-blocking observations (reported to gobi, not merge blockers)

1. `runtime/policy/memory_trust_gate.py` comment edit is outside the #190
   in-scope table. Comment-only, factually corrects a sentence the rename
   would otherwise leave false. Acceptable under rule 14.
2. `build_skill_catalog` reconstructs `catalog_key` as an inline f-string
   rather than reusing the `SkillCatalogEntry.catalog_key` property (provenance
   is built before the entry). String form is identical; mild duplicate-truth
   smell.
3. Known deferred nit per dispatch: `runtime/skills/lifecycle.py` docstring
   still names `SkillTrustState` (MUST-NOT-touch). Left untouched. Non-blocking.
4. `register_skill_catalog` return annotation is bare `-> list` (design showed
   `list[MutationResult]`); avoids an import cycle, acceptable.

## Verdict

**APPROVE.** The diff implements exactly the #190 Half-2 in-scope table and
nothing outside it (bar two comment/docstring-only touches that keep prose
truthful). All seven behavior points verified against the design; the
"no production behavior change today" claim holds because every production
caller passes `store=None`. 5/5 load-bearing mutations caught by the test
suite; full target suite + smoke green. No scope breach, no behavior
divergence from #190. gobi handles rebase / head_sha re-bind / merge.
