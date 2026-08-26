reviewer: agent-aa3906d610ac60348 (independent PR #170 reviewer; did not author the code)
head_sha: 50f0f81d97dcb18162e98a26a59b252e7497c291
independent: true
summary: APPROVED — PR #170 implements the corrected (post-#166) design note faithfully and the gate makes a real decision, not an annotation. Verified rather than assumed: the six new/changed Context Builder tests all FAIL against the parent commit's `runtime/` (the old tree emits a `QUARANTINED` Skill with `budget_class: SHOULD_LOAD`, which is exactly the defect the note names), and 13 of 14 hand-applied logic mutations were caught (the one survivor is a provably unreachable defensive branch, §4). `budget_class` and bucket membership are genuinely outputs of `admit_memory_evidence()` — the hardcoded `"budget_class": "SHOULD_LOAD"` literal in `_select_skills` is gone (grep over `runtime/` shows the only remaining SHOULD_LOAD writes are for authority/required/dependencies), a `DENY` `continue`s before the item dict is constructed (`context_builder.py:376-377`) so the entry is absent from the serialized plan, and an already-withheld lesson can never be promoted (`_route_lesson`'s `floor_withheld` → `WITHHELD_UPSTREAM`, which matters because `_withheld_lesson_with_trust_class` defaults unmapped reasons to `REVIEWED_GUIDANCE`, a loadable class). The WITHHOLD-vs-DENY split is implemented exactly and asserted on the constants themselves (`_UNKNOWN_LESSON_ADMISSION` WITHHOLD / `_UNKNOWN_SKILL_ADMISSION` DENY), `unknown_admission=LOAD` raises, and no code path can make the unknown case mean LOAD. Fail-closed is correctly scoped — `authority`/`required`/`boundaries`/`dependencies`/`unresolved` are untouched by the gate and a malformed lesson store still yields a full plan. All §3 non-goals hold, `runtime/trust.py`'s enum and all three mappings are byte-identical (docstring-only diff, permitted by 4g), `project_applicable_lessons()` is unchanged (4h not smuggled in), and roadmap 6.22 stays IN PROGRESS with both §5 clauses intact and narrowed. Full CI suite as a blocking run at this head: Ran 825 tests in 1865.693s, OK (skipped=6), exit 0; `python3 -m compileall -q runtime tests` exit 0. Five non-blocking findings recorded in §9, none of which change the verdict.

# Review: PR #170 — Enforce MemoryTrustClass at the Context Builder seam (roadmap 6.22)

- Branch reviewed: `memory-trust-gate-impl`, head `50f0f81d97dcb18162e98a26a59b252e7497c291`, re-fetched and re-confirmed at the end of the review (`origin/memory-trust-gate-impl` == local HEAD).
- Base for scope: `origin/main` at `d52885c4`; the branch already contains it (`git merge-base --is-ancestor origin/main HEAD` succeeds), so no rebase/head_sha rebind was needed. Scope isolated with `git diff origin/main...HEAD` (three-dot).
- Two commits on the branch: `0adce16` (implementation) and `50f0f81` (docstring-only fix so the new module's prose does not trip SEC3's unwired-guard name scan).
- Spec / source of truth, both read in full: `work/notes/2026-08-25-memory-trust-enforcement-gate-design.md` (421 lines, the corrected note merged as PR #166) and `work/notes/2026-08-21-memory-trust-enforcement-design.md` (142 lines, PR #148 — the seam choice and class/action table, not re-litigated here). Also read `work/reviews/pr-166-review-evidence.md` for what the CHANGES_REQUESTED cycle corrected.
- Structural reference for this file: `work/reviews/pr-164-review-evidence.md`.
- Reviewed in an isolated worktree (`.claude/worktrees/agent-aa3906d610ac60348`). The shared clone at `~/Projects/MAPS_Lean` was never touched. Mutation testing was done in a throwaway `git archive` copy under the session scratchpad so it could not race the full-suite run in the worktree.
- Verdict: `APPROVED`

## 1. Diff scope

```
 runtime/context_builder.py            | 237 ++++++++++++++++++++++++--------
 runtime/policy/__init__.py            |  10 ++
 runtime/policy/memory_trust_gate.py   | 167 +++++++++++++++++++++++
 runtime/trust.py                      |  15 +-
 tests/test_context_builder.py         | 123 ++++++++++++++++-
 tests/test_exp_a_skill_routing.py     |   5 +-
 tests/test_memory_trust_gate.py       | 250 ++++++++++++++++++++++++++++++++++
 work/roadmaps/CAPABILITY_CHECKLIST.md |   4 +-
 8 files changed, 746 insertions(+), 65 deletions(-)
```

Exactly the file set the PR description claims. `runtime/operational_learning.py` is **not** in the diff (see §7, open question 4h). No new roadmap file, no task doc, no persisted state, no migration.

`runtime/policy/__init__.py` is imports plus four `__all__` entries — exports only. `runtime/trust.py` is a single hunk entirely inside the module docstring (§6).

`tests/test_exp_a_skill_routing.py` changes one call site to unpack the new `(items, tally)` tuple and ignores the tally. The benchmark's selection semantics are untouched; the full suite (§8) re-runs that benchmark and reports the same `selection_f1: 0.888…` over 12 cases.

## 2. The new tests are non-tautological (verified, not assumed)

**2a. Against the parent commit's production code.** A `git archive HEAD` copy of the tree was made, its `runtime/` replaced wholesale with `git archive origin/main runtime`, and the new tests run against it with the new `tests/` kept:

```
python3 -m unittest tests.test_memory_trust_gate
ModuleNotFoundError: No module named 'runtime.policy.memory_trust_gate'
Ran 1 test in 0.000s
FAILED (errors=1)
```

i.e. all 14 gate tests are unreachable without this PR's production code. For the Context Builder tests, which import nothing new, the six new/changed methods were run individually against the old runtime:

```
Ran 6 tests in 37.911s
FAILED (failures=3, errors=3)
```

6 of 6 fail. The most instructive failure is the exact defect the note describes — the old tree emits the item the gate now drops:

```
FAIL: test_quarantined_skill_is_denied_and_absent_from_the_plan
AssertionError: Lists differ: [{'skill_id': 'context-plan-builder', ... }] != []
First extra element 0:
{... 'trust_class': 'QUARANTINED', ..., 'budget_class': 'SHOULD_LOAD'}
```

That is `QUARANTINED` **and** `SHOULD_LOAD` on the same item on `main`, which is precisely §1d's "the label asserts trust instead of checking it".

**2b. Mutation testing.** Fourteen logic mutations were applied one at a time (each reverted before the next) to `runtime/policy/memory_trust_gate.py` and `runtime/context_builder.py`, running `tests/test_memory_trust_gate.py` plus nine Context Builder tests (24 tests, baseline `OK` in 55s) after each:

```
M1  OBSERVATION -> LOAD                                    : CAUGHT (failures=4)
M2  unknown case returns LOAD                              : CAUGHT (failures=17)
M3  drop the stale demotion                                : CAUGHT (failures=6)
M4  enum-ordering threshold instead of the dict lookup     : CAUGHT (failures=7)
M5  QUARANTINED DENY -> WITHHOLD                           : CAUGHT (failures=3)
M6  ACTIVE_INSTRUCTION prover carve-out removed            : CAUGHT (failures=1)
M7  non-bool `stale` ignored (`stale is True`)             : CAUGHT (failures=4)
M8  unknown_admission=LOAD no longer rejected              : CAUGHT (failures=1)
M9  skill unknown case WITHHOLD instead of DENY            : CAUGHT (failures=2)
M10 lesson unknown case DENY instead of WITHHOLD           : CAUGHT (failures=1)
M11 drop the withheld floor (allow upstream promotion)     : CAUGHT (failures=2)
M12 skills budget_class hardcoded SHOULD_LOAD again        : CAUGHT (failures=2)
M13 DENY does not drop the skill entry (annotate only)     : CAUGHT (failures=2)
M14 lesson DENY does not drop the item                     : SURVIVED (OK)
TOTAL: 14 tried, 13 caught
```

All four mutations the review brief specifically names (M1, M2, M3, M4) are caught. M4 is the important one: replacing `_ADMISSION_TABLE[resolved]` with a `list(MemoryTrustClass).index(resolved) >= index(REVIEWED_GUIDANCE)` comparison — the exact mistake §2a caveat 1 warns against — is caught by `test_table_is_not_enum_declaration_order` and six others.

M14's survival is honest and expected, not a test gap the author should close: `_route_lesson`'s `if admission is MemoryAdmission.DENY: return` branch is unreachable on the guidance path. `_UNKNOWN_LESSON_ADMISSION` is `WITHHOLD`, and every class `_withheld_lesson_with_trust_class` can produce (`CANDIDATE_LESSON`, `RETIRED`, `SUPERSEDED`, `REVIEWED_GUIDANCE`) is non-`DENY` in the table. It is defensive code, and the PR does not claim it is reachable. Recorded as a non-blocking observation in §9.

Both the scratch copy and the worktree were verified clean afterwards: `diff -q` against the pristine backups of both mutated files returns nothing, and `git status --porcelain` in the worktree is empty.

## 3. The gate makes a real decision, not an annotation

**Budget class and bucket membership are outputs of the gate.** `git diff` confirms the old `"budget_class": "SHOULD_LOAD"` literal in `_select_skills` is deleted. In its place (`runtime/context_builder.py:379-384`):

```python
"budget_class": (
    _BUDGET_SHOULD_LOAD
    if decision.admission is MemoryAdmission.LOAD
    else _BUDGET_ON_DEMAND
),
```

`grep -rn "SHOULD_LOAD" --include=*.py runtime/` returns only the constant definition, the two gate-driven writes (`:252` for admitted lessons, `:381` for admitted Skills), the two non-memory-like writes for `dependencies` (`:487`, `:498`), and docstring prose. No memory-like producer can hand itself a load tag any more. `build_context_plan` no longer re-tags: the two lines `guidance = [dict(item, budget_class=_BUDGET_SHOULD_LOAD) ...]` / `withheld_guidance = [... _BUDGET_ON_DEMAND ...]` are removed and replaced with `guidance, withheld_guidance, memory_trust_tally = _lesson_guidance(store, task)`.

**A `DENY` genuinely removes the item.** `runtime/context_builder.py:376-377` is `if decision.admission is MemoryAdmission.DENY: continue`, placed *before* the `item` dict is constructed — the entry is never built, not built-and-tagged. `test_quarantined_skill_is_denied_and_absent_from_the_plan` proves the observable consequence by serializing the whole plan and asserting the Skill's name does not appear anywhere in it (`assertNotIn("context-plan-builder", json.dumps(plan))`), which also covers leakage into any other bucket. Mutation M13 confirms that assertion actually binds.

**An already-withheld lesson can never be promoted.** This is load-bearing and easy to miss: `_withheld_lesson_with_trust_class` (`:262-272`) maps only three reasons and **defaults everything else to `operational_learning_trust_class("ACTIVE")` = `REVIEWED_GUIDANCE`**, which the admission table marks `LOAD`. So `NOT_APPLICABLE` / `NOT_STARTED` / `APPLICABILITY_UNKNOWN` withheld lessons *would* be admitted to `guidance` were it not for `_route_lesson`'s `floor_withheld` clamp, which rewrites the outcome to `WITHHOLD` with code `WITHHELD_UPSTREAM`. `test_active_lesson_with_non_matching_applicability_is_withheld` asserts exactly that (`withheld_reason == "WITHHELD_UPSTREAM"`, `memory_trust_gate_admitted == 0`), and mutation M11 confirms it. This is a correctness trap the implementation handled properly.

**The tally is a real output, not a log line.** `coverage.memory_trust_gate_admitted/withheld/denied/reasons` are asserted numerically in four tests (e.g. `memory_trust_gate_reasons["TRUST_CLASS_DENIED"] == 1`), and `_AdmissionTally.merge` folds the skills tally into the lessons tally so the coverage numbers cover both producers.

## 4. WITHHOLD-vs-DENY split implemented exactly, not flattened

The split lives in two module constants (`runtime/context_builder.py:139-140`):

```python
_UNKNOWN_LESSON_ADMISSION = MemoryAdmission.WITHHOLD
_UNKNOWN_SKILL_ADMISSION = MemoryAdmission.DENY
```

`test_producer_split_is_preserved` imports both and asserts each `assertIs` *and* `assertIsNot` each other, so collapsing them to one value fails even if both were flipped together. Mutations M9 and M10 confirm each direction independently.

Verified the §2e reasoning against code rather than against the note's prose:

- **Lessons carry no content when withheld.** `runtime/operational_learning.py:410` is `withheld.append({"lesson_id": record["lesson_id"], "reason": reason})` — two keys, no `claim`. The `claim` text appears only on projected items (`:413-422`). WITHHOLD is therefore safe on this path, matching #148's "mark item withheld".
- **Skill entries carry content inline.** `_select_skills` emits `"name": descriptor.name` and `"description": descriptor.description` (`runtime/context_builder.py:365-366`), so a withheld Skill entry in that shape is instruction-bearing text. DENY on the unknown case is the correct half of the split, and 4a's alternative (strip the entry to `skill_id`+`catalog_key`) was explicitly not taken.

**Nothing can make the unknown case mean LOAD.** Three independent barriers, all tested: `admit_memory_evidence` raises `MemoryTrustGateError` if `unknown_admission is MemoryAdmission.LOAD` (`:126-130`, mutation M8 caught) or if it is not a `MemoryAdmission` at all (`:122-125`); `_resolve` returns `None` for `None`, empty/blank strings, unrecognized names, lowercase names, ints, lists, and arbitrary objects, and the `None` path returns the caller's non-LOAD default with code `TRUST_CLASS_UNRESOLVED` (`FailClosedTests.test_unknown_class_never_loads` parametrizes all eight, mutation M2 caught with 17 failures); and both call-site constants are non-LOAD. `runtime/policy/__init__.py` exports the names but constructs nothing.

## 5. Fail-closed, and correctly scoped

`admit_memory_evidence` never returns `LOAD` for anything not explicitly in the table with a `LOAD` value, mirroring `CanonicalRunGuard`'s `BINDING_REQUIRED` and `DestructiveExternalActionGuard`'s deny-on-missing-key. Additional fail-closed details I checked in code:

- `stale is not False` (`:143`) — not `bool(stale)` and not `stale is True`. Any non-`False` value (`None`, `"no"`, `0.0`, an arbitrary object) demotes. `test_non_bool_stale_is_treated_as_stale` parametrizes those four; mutation M7 (`stale is True`) is caught.
- Stale never promotes: `OBSERVATION` + `stale=True` stays `WITHHOLD`, `QUARANTINED` + `stale=True` stays `DENY` (asserted).
- `_LOAD_REQUIRES_PROVEN_ACTIVE_SOURCE` carries #148's `ACTIVE_INSTRUCTION` condition forward instead of widening it: the row is in the table as `LOAD` but is intercepted at `:138-141` and returned as `WITHHOLD`/`TRUST_CLASS_ACTIVE_SOURCE_UNPROVEN`. `AdmissionTableTests.WITHHELD` includes `ACTIVE_INSTRUCTION`; mutation M6 is caught.
- `test_every_class_has_an_explicit_admission` asserts the union of the three expected sets equals `set(MemoryTrustClass)`, so a future enum member added without a table row breaks CI rather than falling through — and `_ADMISSION_TABLE[resolved]` is a bare subscript, so a missing row raises rather than defaulting.

**Scope is "the item does not enter the load set", not "the plan fails."** Verified structurally, not by docstring: the gate is invoked only inside `_lesson_guidance`/`_route_lesson` and `_select_skills`. `build_context_plan`'s construction of `authority`, `required`, `boundaries`, `dependencies`, and `unresolved` is entirely outside the diff — `git diff origin/main...HEAD -- runtime/context_builder.py` contains no hunk touching those blocks. `test_malformed_lesson_record_fails_closed_without_breaking_plan` (unchanged, still passing) builds a plan from a store whose lesson record is invalid and asserts `plan["authority"] == baseline["authority"]` and `plan["required"] == baseline["required"]` with `guidance`/`withheld_guidance` both empty. `admit_memory_evidence` can only raise on a bad `unknown_admission`, and both call sites pass module constants, so no reachable input makes the gate throw.

## 6. Non-goals (§3) checked one at a time

- **No policy engine, DSL, or configurable threshold.** `_ADMISSION_TABLE` is a fixed dict literal. The gate module imports only `dataclasses`, `enum`, and `runtime.trust`. No config file, env var, or constructor parameter exists. `NonGoalTests.test_no_policy_engine_or_configurable_threshold` greps both files for `eval(`/`exec(`/`*Engine`/`threshold`/`configparser`/`os.environ` after stripping comments and string literals via `tokenize` — a genuinely better guard than raw-text grep, since the modules discuss thresholds in prose. Behaviourally, M4 covers the case the name-grep cannot.
- **No second authority database.** No new store, no persistence, no lineage graph. `test_no_second_authority_database` bars `sqlite3`/`sqlalchemy`/`CREATE TABLE`/`.write_text(`/`.mkdir(`/`shelve`/`pickle` in real code. The gate reads only the existing `runtime/trust.py` mappings.
- **No inference, regex sniffing, or LLM judgment.** The gate module contains no `re` import and no content analysis; `_resolve` is an exact enum lookup on a stripped string. Nothing reads `claim`, `name`, or `description` text for classification purposes.
- **No daemon or background scanning.** `test_gate_module_declares_no_daemon_or_hook_plumbing` bars `threading`/`asyncio`/`subprocess`. No thread, timer, or long-lived object anywhere in the diff.
- **No new `HookEvent`/`HookEnforcement`/`HookOutcome`/guard class, no `HarnessService` routing.** `runtime/harness/hooks.py` is not in the diff. `grep -nEi "hook|HarnessService" runtime/context_builder.py` returns **nothing**. `MemoryAdmissionDecision` is a new frozen dataclass, not a `HookOutcome` variant or a guard class — it is never registered with any registry and `runtime/policy/__init__.py` exports it without constructing it. (Commit `50f0f81` exists solely because the class docstring originally named `DestructiveExternalActionGuard`, which SEC3's own anti-wiring source scan forbids appearing elsewhere in `runtime/`; the fix refers to it by module path instead. That is the correct fix, and the SEC3 scan passes in the full suite.)
- **No Skill body loading.** `test_context_builder_never_loads_skill_bodies` asserts `load_skill(` and `load_catalog_skill(` do not appear in `runtime/context_builder.py`; confirmed independently by grep.
- **No promotion of guidance to authority.** `_route_lesson` only sets `budget_class` and `withheld_reason`; the `authority: "GUIDANCE_ONLY"` field is produced upstream by `project_applicable_lessons()` and passed through untouched, and nothing writes into `plan["boundaries"]` or `plan["authority"]`. The unchanged S6 test still asserts `assertNotIn("skills", plan["boundaries"])`.
- **No changes to `runtime/trust.py`'s enum or the three mappings.** The entire `runtime/trust.py` diff is one hunk at `@@ -28,10 +28,17 @@`, wholly inside the module docstring: it replaces the now-false "it is NOT wired into any decision-gating code path" claim with a narrower statement naming the gate and confining the out-of-scope claim to *action/tool-call*-level gating. That is precisely what open question 4g requires, and the docstring's new wording is accurate. `MemoryTrustClass`, `skill_trust_class`, `skill_lifecycle_trust_class`, `operational_learning_trust_class`, and `TrustClassError` are byte-identical. `test_trust_module_enum_and_mappings_are_unchanged_in_shape` pins the 11 member values in order.

## 7. Open behavior questions §4a-4h — answered, and the answers match the code

Each PR-description claim re-derived from the repository:

- **4a (skills unknown case).** Claimed: `DENY`, entry shape unchanged. Code: `_UNKNOWN_SKILL_ADMISSION = MemoryAdmission.DENY`; the emitted Skill dict still carries `name`/`description`. True, tested, and the rejected alternative (stripping the entry) is genuinely not present.
- **4b (DENY audit trail).** Claimed: counted reason under `coverage`, no `denied_memory` list. Code: `coverage.memory_trust_gate_denied` plus `memory_trust_gate_reasons` as a `{code: count}` map; no identifier list, no new plan bucket. True. The note permits this if the implementation confirms a count is sufficient; the confirmation is recorded in the PR body and in `coverage.memory_trust_gate_note`. See §9.2 for the one thing this loses.
- **4c (Skill tests + S6 exit gate).** See §8. True.
- **4d.** Marked RESOLVED in the note; independently re-confirmed at `runtime/operational_learning.py:410`. Not re-opened by the implementation.
- **4e (where decisions are recorded).** Claimed: `coverage` only, no new evidence stream. Code: the five `memory_trust_gate_*` keys under `coverage`; no Run Record change, no `evidence_refs`. True — and correct, since Context Builder is on no Hook path.
- **4f (module placement).** Claimed: `runtime/policy/memory_trust_gate.py`, alongside the existing deterministic guards, rather than private to `context_builder` or inside `trust.py`. The file is where claimed. The justification (existing `runtime/policy/` guard neighbourhood, a known second consumer in the eventual action-level gate, and keeping `trust.py` as read-only vocabulary) is a deliberate answer rather than a guess, and the placement is what makes `tests/test_memory_trust_gate.py`'s 14 pure unit tests possible at all.
- **4g (`trust.py` docstring).** See §6. True; docstring only.
- **4h (`project_applicable_lessons()` per-item status).** Claimed: deliberately NOT changed. Verified the strongest way available: `git diff origin/main...HEAD -- runtime/operational_learning.py` produces **no output at all** — the file is not in the diff. Nothing was smuggled in. The honest consequence the PR states is also verifiable: `test_guidance_and_withheld_guidance_budget_classes` (unchanged) still asserts `guidance` items are `SHOULD_LOAD` and `withheld_guidance` items are `ON_DEMAND`, so the guidance path's *output* is unchanged for every input the projection can produce today, exactly as §2b's honest-scope paragraph says. The guidance path gains only the structural single-derivation fix and the `WITHHELD_UPSTREAM` floor.

## 8. Roadmap row and the S6 exit gate

**6.22 is not flipped.** `work/roadmaps/CAPABILITY_CHECKLIST.md:131` still reads `IN PROGRESS`. Both §5 clauses survive in the "Still missing" sentence: *"no action/tool-call gate consults `MemoryTrustClass` — enforcement so far reaches the Context Builder plan only, not tool calls — and `SkillTrustState`/`SkillLifecycleState`/`operational_learning.py` remain unmigrated, separate systems of record."* The clause is narrowed (the tool-call boundary is now named explicitly) rather than deleted, which is what §3's last bullet demands. The row's new prose is accurate against the code on every claim I checked.

**The 6.11 row edit is accurate.** Its previous "classification only … `budget_class` does not yet drive any actual load/fetch behavior" is now false for the memory-like buckets, and the row records exactly that exception. The remaining claims (no `MAY_LOAD` tier, no new retrieval mechanism, no downstream load/fetch behavior) are still true — `coverage.semantic_retrieval_used` and `repository_scan_used` are untouched by this diff.

**S6 is strengthened, not regressed, and no test was weakened.** The whole `tests/test_context_builder.py` diff removes exactly three lines: the `MemoryTrustClass` import line (replaced with one that also imports `TrustClassError`), the old `def test_matching_skill_budget_class_is_should_load` signature, and its single `assertEqual(item["budget_class"], "SHOULD_LOAD")`. Everything else is additive (+123/-3). Specifically:

- `test_matching_skill_is_selected_and_unrelated_skill_stays_out_of_context` — the actual S6 exit gate — is **byte-unchanged** and still asserts the unrelated Skill is absent from `json.dumps(plan)` including its description text (`assertNotIn("PostgreSQL", serialized)`). PR #166's review flagged `tests/test_context_builder.py:522` as a second assertion a demotion might break; I checked it on `main` and it is the `trust_class == OBSERVATION` assertion inside this same test, which the demotion does not touch. It is correctly left alone.
- The replacement test asserts the *stronger* invariant (`ON_DEMAND` + a specific `withheld_reason` + the three tally counts), not a weaker one.
- The new `test_no_default_loaded_plan_item_carries_a_non_loadable_trust_class` adds a whole-plan invariant across all three memory-like buckets that did not exist before, and guards itself against vacuity with `assertTrue(default_loaded)`.
- `test_guidance_and_withheld_guidance_budget_classes` and `test_malformed_lesson_record_fails_closed_without_breaking_plan` are unchanged and still pass, which is what makes the "guidance-path output is unchanged" claim checkable.

Coverage of the previously-unreachable table rows is honest about its own mechanism: `_plan_with_skill_trust_class` patches `runtime.context_builder.skill_trust_class`, and its docstring says plainly that `SkillTrustState` has only `UNASSESSED` so the LOAD and DENY rows cannot be reached through real catalog data. That is the right way to test an unreachable row — it does not pretend the row is live.

## 9. Non-blocking findings

None of these change the verdict; recording them so they are not lost.

1. **`_route_lesson`'s `DENY` branch is dead code today.** No class reachable on the guidance path maps to `DENY`, and the lesson unknown-case default is `WITHHOLD`, so `context_builder.py:249-250` cannot execute (mutation M14 survived because of this). It is correct defensive code and the PR does not claim otherwise, but it is untested by construction and will stay that way until a producer can emit `QUARANTINED`/`UNTRUSTED_INPUT` on that path.

2. **#148's four distinct fail-closed reason strings are collapsed into one code.** #148 §"Fail-closed rules" names `unknown_trust_class`, `malformed_trust_class`, and `trust_mapping_failed` as separate reasons. The implementation returns `TRUST_CLASS_UNRESOLVED` for all three, so `coverage.memory_trust_gate_reasons` cannot distinguish "the catalog's `trust_state` has no mapping" (a `TrustClassError` at `context_builder.py:355-357`) from "someone stamped a garbage string". The corrected note does not carry those strings forward and §4b leaves the audit shape to the implementation, so this is within bounds — but combined with 4b's decision to record counts only and no identifiers, a future real `DENY` is auditable as "one item was denied for an unresolvable class" and nothing more. Worth revisiting when the first producer can actually emit one.

3. **Two documents now contain stale claims about Skill budget classes.** `work/tasks/context-budget-classification-wave12.md:25` and `:55` still state "Every item in `plan["skills"]` carries `"budget_class": "SHOULD_LOAD"`" as a checked acceptance criterion — now false — and the updated 6.11 checklist row points readers at that file. `work/notes/2026-08-19-exp-a-skill-routing-benchmark.md:153` similarly describes Skill selection as "advisory `SHOULD_LOAD` metadata". Both are historical records rather than live specs, and the checklist row itself is correct, so this is documentation drift rather than a false checklist claim.

4. **`NonGoalTests`' Hook guard is under-broad, and `context_builder` picked up a new transitive import of `runtime.harness`.** `test_gate_module_declares_no_daemon_or_hook_plumbing` reads only `runtime/policy/memory_trust_gate.py`, so it would not catch Hook plumbing added to `context_builder.py`. Separately, `from runtime.policy.memory_trust_gate import …` executes `runtime/policy/__init__.py`, which imports `destructive_action_guard` and `harness_guard`, which import `runtime.harness` — so Context Builder now transitively imports the Hook machinery it previously did not. This is an import side effect, not routing (the direct grep for `hook`/`HarnessService` in `context_builder.py` is empty, and no `HarnessService` call exists), so the §3 non-goal holds; but a narrower `from runtime.policy.memory_trust_gate import …` cannot avoid it while the package `__init__` is eager. Cheap follow-up if the coupling matters.

5. **Two small looseness points in the tests.** `test_no_default_loaded_plan_item_carries_a_non_loadable_trust_class`'s `loadable` set includes `ACTIVE_INSTRUCTION`, which the gate in fact never admits (the prover carve-out), so that test permits slightly more than the gate does — harmless, but M6 is caught by a different test, not this one. And the gate's own tests for the `LOAD` outcome at the real seam depend entirely on `unittest.mock.patch` of `skill_trust_class`; if that mapping's signature ever changes, the patch would silently keep passing. Both are minor.

6. **Design-level tension, already sanctioned by the note.** A `WITHHOLD`-ed `OBSERVATION` Skill stays in `plan["skills"]` with its `name` and `description` inline — the same content-bearing shape §2b.3 cites as the reason `QUARANTINED` must be dropped rather than withheld. The note prescribes exactly this outcome for `OBSERVATION` (§2b.1: "appear as `ON_DEMAND` metadata with a withheld reason"), so the implementation is faithful; but "out of the default load set" and "not present as text in the plan" are different properties, and only the first is achieved for `OBSERVATION`. That is the note's call, not this PR's, and 4a is the place it was already argued.

## 10. Full suite (as CI runs it)

Run in this worktree at `50f0f81`, in the foreground with no timeout, before any mutation work (mutation testing was done in a separate scratch copy so it could not perturb this run):

```
python3 -m compileall -q runtime tests
COMPILEALL_EXIT=0

python3 -m unittest discover -s tests
Ran 825 tests in 1865.693s
OK (skipped=6)
EXIT=0
```

No failures, no errors. 825 tests versus the 806 recorded at PR #166's head is consistent with the 14 new gate tests plus 5 net new Context Builder tests. The `EXP-A` skill-routing benchmark inside the suite still reports `selection_f1 / precision / recall = 0.888…` over 12 cases, i.e. the tuple-unpacking change to `tests/test_exp_a_skill_routing.py` did not alter selection behavior.

## 11. Review lenses applied

- *Smallest change that satisfies the requirement* — one new 167-line pure module, two producers rewired, one docstring corrected. No config surface, no new plan bucket, no upstream projection change. Passes.
- *No duplicate truth (rule 12)* — the stated purpose of the PR, and structurally achieved: bucket and `budget_class` now have exactly one derivation. Verified by grep, not by docstring. Passes.
- *Fail closed by construction* — verified at three levels (table lookup with no default, `unknown_admission` validated and LOAD-rejected, `stale is not False`). Passes.
- *Capability is not permission* — the gate can only *reduce* what enters the load set; it grants nothing and cannot suppress canonical authority. Passes.
- *Don't hide uncertainty* — 4h and 4b are recorded as deliberate deferrals with their consequences stated, including the unflattering one ("this PR changes no guidance-path output"). Passes.
- *Don't outrank source evidence with prose* — every PR-description claim in §6 and §7 was re-derived from the tree; none were taken on the author's word.
- *An owner never approves their own work* — written by an agent that did not author the code, in an isolated worktree, with parent-commit rollback and 14 mutations rather than test-reading alone.

## 12. Evidence checked

- `work/notes/2026-08-25-memory-trust-enforcement-gate-design.md` (all 421 lines) and `work/notes/2026-08-21-memory-trust-enforcement-design.md` (all 142 lines)
- `work/reviews/pr-166-review-evidence.md` (for the corrections the CHANGES_REQUESTED cycle produced), `work/reviews/pr-164-review-evidence.md` (structure)
- `runtime/policy/memory_trust_gate.py` (all 167 lines), `runtime/context_builder.py` (the full diff plus `_withheld_lesson_with_trust_class`, `_select_skills`, `build_context_plan`), `runtime/policy/__init__.py`, `runtime/trust.py` diff, `runtime/operational_learning.py:375-430`
- `tests/test_memory_trust_gate.py` (all 250 lines), the full `tests/test_context_builder.py` diff plus the unchanged S6 test at both `origin/main` and HEAD, `tests/test_exp_a_skill_routing.py` diff
- `work/roadmaps/CAPABILITY_CHECKLIST.md` rows 6.11 and 6.22 (old and new), `scripts/check_review_evidence.py`, `.github/workflows/runtime-stack-tests.yml`
- `gh pr view 170 --repo BigCatMellow/MAPS_Lean --json title,body,headRefName,baseRefName`

## 13. Reviewer limits

- CI additionally runs `ruff check … --select E9,F63,F7,F82`, `bandit -q -r runtime -ll -s B608`, `pip check`, the LangGraph smoke, and the test suite with `PYTHONWARNINGS=error::ResourceWarning` and `-v`. Neither `ruff` nor `bandit` is installed on this box, and I ran the suite without the `ResourceWarning`-as-error env var, so lint-only, bandit-only, and ResourceWarning-only CI failures are outside what I verified. `compileall` I did run (exit 0).
- Mutation testing exercised 24 tests, not the full 825, so a mutation "caught" is caught by the targeted modules; the full suite was run separately and unmutated.
- The `LOAD` and `DENY` rows of the admission table are unreachable through real production data today. My verification that they behave correctly rests on the gate's unit tests and on patched-mapping seam tests, not on any live producer — the same limit the implementation itself documents.
- This review binds to `50f0f81`. Any later push to `memory-trust-gate-impl` other than an evidence-only commit invalidates this file by design of `scripts/check_review_evidence.py`.
