# PR #221 review evidence — 6.9/S6 progressive Skill-body loading, slice 1

reviewer: maps-lean-nava
head_sha: 7340e03b4e6cc890c99b8498d39e011f79d6e9ec
independent: true
summary: APPROVE — implements exactly the design §3 slice: one `store` param on `_select_skills`, one call-site change, and a `load_catalog_skill` body-attach gated strictly on `MemoryAdmission.LOAD`; fail-closed via `except (SkillCatalogError, SkillParseError)` which (verified) also catches `SkillChangedError`; all 7 §3d acceptance criteria met; no MUST-NOT violated; no checklist status flip; targeted suites + smoke green; exp_a metrics unchanged; 6/6 mutations on the new logic killed. First CI run failed on a stale non-goal test (`tests/test_memory_trust_gate.py::test_context_builder_never_loads_skill_bodies`); fixed in commit `7340e03` (renamed `test_context_builder_body_loading_is_load_gated_and_activation_level_only`) and re-verified by nava as APPROVE-DELTA — the new assertions are a correct, appropriately-tight (arguably stronger) encoding of the slice-1 non-goal (keeps `assertNotIn('load_skill(')`, adds positive `assertIn('load_catalog_skill(')`, pins the LOAD-gate source line, forbids all 4 execution-level `*_paths` attrs); nava's own `grep tests/` sweep found no other stale body/load non-goal assertion (`test_skills_catalog.py:78` is about `build_skill_catalog`, not `_select_skills`, unaffected + green). NB: head_sha rebound by coordinator to the post-rebase code commit (branch predated #217–#220 and #222; `CAPABILITY_CHECKLIST.md` 6.9/6.10-row conflict resolved at merge-prep — evidence-text only, keeps #222's newer manifest-slice-1 text plus this PR's body-loading update, no status moved).

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| §3d.1 | LOAD-classified matched Skill → item `body` == real SKILL.md body | PASS. `test_load_classified_skill_carries_hash_verified_body`: body from `load_catalog_skill(entry, store)` → `SkillDocument.body`; `body_sha256` from `document.descriptor.content_sha256`. |
| §3d.2 | None-state matched Skill → no `body`, `budget_class=="ON_DEMAND"`, `withheld_reason` present | PASS. `test_withheld_skill_has_no_body`. |
| §3d.3 | `coverage.skill_bodies_loaded == 1` for one matched VALIDATED; unrelated contributes 0 | PASS. counter = `sum(1 for item in skills if "body" in item)`. |
| §3d.4 | discovery-then-mutate → `body_withheld_reason` set, plan still returned | PASS. `test_body_activation_failure_is_fail_closed`; `SkillChangedError` caught → `body_withheld_reason` set, plan not None, `skill_bodies_loaded==0`. |
| §3d.5 | `maps context` plan (no catalog) unchanged — `plan["skills"] == []` | PASS. `_select_skills` returns `([], tally)` early when `skill_catalog is None`; body logic never reached. |
| §3d.6 | targeted unittest green + smoke exit 0 | PASS. `test_context_builder` / `test_flow_start` / `test_skills_catalog` / `test_exp_a_skill_routing` green; post-fix incl. `test_memory_trust_gate`. `runtime.smoke` → `"ok": true`, exit 0. |
| §3d.7 | `git diff` touches only §3c MAY-touch files | PASS. `context_builder.py`, `flow_start.py` (docstring), `tests/test_context_builder.py`, `tests/test_flow_start.py` (e2e assertion update §3b item 4 calls for), `tests/test_memory_trust_gate.py` (stale non-goal test update, added at CI-fix), `CAPABILITY_CHECKLIST.md`. No `schema.sql`, no `cli.py`, no runtime module outside the two named. |
| — | `_select_skills` gains `store`; exactly ONE call-site change | PASS. `store` was already a `build_context_plan` param. |
| — | Body attached only for `MemoryAdmission.LOAD` & `store is not None`; fail-closed | PASS. `WITHHOLD` sets only `withheld_reason`; `DENY` `continue`s; `ON_DEMAND`/`None`-state never enter the LOAD branch. Never raises out of `_select_skills`. |
| — | Fail-closed catches all three named exceptions | PASS. `class SkillChangedError(SkillParseError)` and `SkillParseError(ValueError)` — `except (SkillCatalogError, SkillParseError)` catches `SkillChangedError` too. Verified by `test_body_activation_failure_is_fail_closed`. |
| — | MUST NOT — none violated | PASS. No schema change. No new retrieval/file-walk. No `scripts`/`references`/`examples`/`assets` content. `load_catalog_skill`/`load_skill`/`admit_memory_evidence`/trust projection/`_NON_ACTIVATABLE_LIFECYCLE_STATES` unmodified. No `maps context` change. No selection/matching or `budget_class` logic change. |
| — | Checklist status flip | PASS — none. All touched rows read `IN PROGRESS` on both sides. Evidence text only. |
| — | Strict-subset (nava #217 criterion 4) still holds | PASS. Trust chain untouched; `{VALIDATED,APPROVED,ACTIVE}` ⊂ `load_catalog_skill`'s permitted set. |
| — | flow_start quarantine e2e updated correctly | PASS. Still asserts the QUARANTINED Skill dropped + `memory_trust_gate_denied >= 1`; now also asserts the clean VALIDATED Skill carries `body` + 64-char `body_sha256`, `skill_bodies_loaded == 1`, no quarantined body leaks. |
| — | exp_a metrics unchanged | PASS. `test_exp_a_skill_routing` 2/2 OK; `selection_f1` unchanged. |

## Mutation testing (new `context_builder.py` body-attach + fail-closed logic) — 6/6 killed

| # | Mutation | Result |
|---|----------|--------|
| M1 | `admission is LOAD` → `admission is not DENY` | KILLED |
| M2 | `except (SkillCatalogError, SkillParseError)` → `except SkillCatalogError` | KILLED (`SkillChangedError` escapes) |
| M3 | `item["body"] = document.body` → `""` | KILLED |
| M4 | `item["body_withheld_reason"] = type(exc).__name__` → `pass` | KILLED |
| M5 | counter `if "body" in item` → `if "body" not in item` | KILLED (3 tests) |
| M6 | `admission is LOAD` → `admission is WITHHOLD` | KILLED |

## Non-blocking notes

1. `body_withheld_reason` set to `type(exc).__name__` rather than the design's *example* codes — "short stable code" contract met.
2. `tests/test_flow_start.py` + `tests/test_memory_trust_gate.py` edited — both are stale-assertion updates the slice necessitates, within scope.
3. Source-substring style of the non-goal test is brittle but consistent with the existing `NonGoalTests` class.

## Verdict

APPROVE (+ APPROVE-DELTA on the CI-fix commit).
