reviewer: agent-ae9d58ddcb9e1b62e (independent PR #164 reviewer; did not author the code)
head_sha: 2cc8e59d9bc5e70f403c1797d7354f4ccdb5f36e
independent: true
summary: APPROVED — PR #164 implements exactly the SEC3 design note's "Decision"/"The second enforcement type" sections (one new HookEnforcement member, one fail-closed read-only guard, exports, tests); the new tests are provably non-tautological (all 18 error out against the parent commit's runtime/, and 6 of 6 hand-applied logic mutations were caught), the guard is genuinely unwired (no production caller anywhere in runtime/ outside the enum declaration, the guard module, and the export list; runtime/recovery/ and runtime/harness/service.py untouched by the diff), every Non-goal in the note is respected (no registry/manifest, no policy engine or severity matrix, zero inferred classification, no new HookOutcome/HookDirective values, no HookRegistry internals changed, no daemon, no roadmap row flipped to DONE), the guard fails closed on missing/non-bool keys and never emits REQUIRE_APPROVAL, and the full CI suite passes (782 tests, OK, skipped=6).

# Review: PR #164 — DestructiveExternalActionGuard + DESTRUCTIVE_EXTERNAL_ACTION (SEC3, unwired)

- Branch reviewed: `sec3-guard-impl`, current head `2cc8e59` (a merge commit bringing the branch up to date with `main`; parents `1b4183e` — the implementation commit — and `f02ed62` — `main`).
- Code state reviewed: identical at both heads. `git diff 1b4183e8a0c0b7407546492015b065fb052edd6b 2cc8e59d9bc5e70f403c1797d7354f4ccdb5f36e --stat -- runtime/ tests/` returns **empty output**; the full delta between the two is only `work/notes/2026-08-24-roadmap-trajectory-check-7.md` (252 lines) and `work/reviews/pr-163-review-evidence.md` (122 lines), i.e. PR #163's docs. Every finding below therefore applies unchanged to the current head. Where this file quotes commands run before the merge, they were re-verified at `2cc8e59`.
- Base for scope: `origin/main` (pre-merge merge-base `ee5e364`); `git diff origin/main...HEAD --stat` (three-dot) isolates this PR's own changes.
- Spec / source of truth: `work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md` (merged in PR #161), read in full
- Structural reference for this file: `work/reviews/pr-161-review-evidence.md`
- Verdict: `APPROVED`
- Reviewed in an isolated worktree checkout; `git rev-parse HEAD` printed `2cc8e59d9bc5e70f403c1797d7354f4ccdb5f36e` after re-fetching `origin/sec3-guard-impl`.

## 1. Diff scope

`git diff origin/main...HEAD --stat` (identical to `git diff ee5e364..1b4183e --stat`):

```
 runtime/harness/hooks.py                        |   1 +
 runtime/policy/__init__.py                      |   6 +
 runtime/policy/destructive_action_guard.py      | 139 ++++++++++++++++
 tests/test_destructive_external_action_guard.py | 212 ++++++++++++++++++++++++
 4 files changed, 358 insertions(+)
```

Four files, all additive, exactly the set the PR description claims — one implementation commit plus the later up-to-date-with-main merge, which adds only the two PR #163 docs noted above. The `runtime/harness/hooks.py` diff is literally one added line inside `class HookEnforcement(str, Enum)`:

```
     CANONICAL_RUN = "CANONICAL_RUN"
+    DESTRUCTIVE_EXTERNAL_ACTION = "DESTRUCTIVE_EXTERNAL_ACTION"
```

The `runtime/policy/__init__.py` diff is an import of the two new names plus two `__all__` entries — exports only, no construction, no registration.

## 2. Non-tautological tests (verified, not assumed)

**2a. Against the parent commit's production code.** With the new test file kept, the production side was rolled back to `ee5e364`:

```
git checkout ee5e364 -- runtime/
python3 -m unittest tests.test_destructive_external_action_guard
```

First pass (`git checkout <sha> -- runtime/` cannot delete a file that does not exist in that tree, so `destructive_action_guard.py` survived and only the enum member was removed) produced `Ran 18 tests ... FAILED (errors=5)`, each with:

```
AttributeError: type object 'HookEnforcement' has no attribute 'DESTRUCTIVE_EXTERNAL_ACTION'
```

Second, stricter pass additionally removed the new module (`rm runtime/policy/destructive_action_guard.py`, plus `runtime/**/__pycache__` cleanup) so the tree matched `ee5e364` exactly. Result:

```
ModuleNotFoundError: No module named 'runtime.policy.destructive_action_guard'
Ran 1 test in 0.000s
FAILED (errors=1)
```

i.e. the entire module fails to import at the parent commit — none of the 18 tests can pass without this PR's production code. Restored with `git checkout 1b4183e... -- runtime/`; `git status --porcelain` empty, tests back to `Ran 18 tests ... OK`.

**2b. Mutation testing.** Six logic mutations were applied one at a time to `runtime/policy/destructive_action_guard.py` (each reverted before the next), running the new test module after each. Every one was caught:

```
M1 missing key -> ALLOW: CAUGHT (FAILED (failures=2))
M2 declared True -> ALLOW: CAUGHT (FAILED (failures=4))
M3 non-bool coerced instead of denied: CAUGHT (FAILED (failures=5))
M4 or -> and (only both-True denies): CAUGHT (FAILED (failures=3))
M5 deny -> REQUIRE_APPROVAL on declared True: CAUGHT (FAILED (failures=4))
M6 invalid-bool branch removed: CAUGHT (FAILED (failures=5))
```

Specifically: making a missing classification key ALLOW instead of DENY (M1) and making a declared `destructive=True` return ALLOW (M2) — the two mutations named in the review brief — are both caught. So is weakening the deny to `REQUIRE_APPROVAL` (M5), which the note's last open question specifically warns against. Mutation score 6/6. Working tree verified clean afterwards (`git status --porcelain` and `git diff --stat` both empty).

## 3. Genuinely unwired (verified)

```
grep -rn "DESTRUCTIVE_EXTERNAL_ACTION\|DestructiveExternalActionGuard\|register_destructive_external_action_guards" --include=*.py .
```

Every hit outside the new test file is confined to exactly three files:

- `runtime/harness/hooks.py:52` — the enum member declaration, nothing else.
- `runtime/policy/destructive_action_guard.py:31,114,116,126,127,138` — the class, the helper's signature, its exact-type check, and the `_register_enforcement()` call inside the helper itself.
- `runtime/policy/__init__.py:2,3,17,26` — import + `__all__` entries only.

No other module in `runtime/` mentions any of the three names. `git diff origin/main...HEAD --name-only` confirms `runtime/recovery/` and `runtime/harness/service.py` are not in the diff at all, so no `_require_destructive_enforcement()` analogue of `_require_canonical_enforcement()` was added and no live stop/kill path changed. Nothing in the repo ever constructs `DestructiveExternalActionGuard()` outside the tests.

The PR also ships three source-scanning tests (`NoAccidentalProductionWiringTest`) that walk `runtime/**/*.py` and fail if the enum member or guard names appear outside those three allowed files, plus one asserting `runtime/harness/service.py` contains no `destructive` substring at all. Those are mechanical CI-level anti-wiring guards, not self-certification prose; I confirmed they pass now and that they are keyed on `Path.read_text` of real files, so a later accidental wiring PR would break them. Minor, non-blocking observation: the service.py substring assertion is broad enough that an unrelated future comment containing the word would trip it — a deliberate false-positive-biased tripwire, which is the safe direction.

## 4. Non-goals respected (checked one by one against the note)

- **No action/tool declaration registry or manifest.** The diff adds no catalog type; classification is read straight off the Hook context mapping. Nothing resembling `ToolSpec`/`ActionType` appears.
- **No policy engine, rules DSL, or configurable severity matrix.** `__call__` is a straight-line function of two booleans. No config file is read, no severity levels exist, no second authority store is introduced.
- **No inferred classification.** The new module imports only `typing` and `runtime.harness` symbols — no `re`, no `ast`, no subprocess/shell-string inspection, no model call. There is no inference helper anywhere in the diff. This was the note's sharpest prohibition and it is honored literally.
- **No new `HookOutcome` variants or `HookDirective` values, no `HookRegistry.run()`/`register()` changes.** The only `runtime/harness/hooks.py` change is the single enum line quoted in §1; `HookOutcome`, `HookDirective`, `HookRegistry.run`, `HookRegistry.register`, and `_register_enforcement` are byte-identical to `ee5e364`.
- **No wiring of a real production call site.** Per §3.
- **No daemon, no background scanning.** No thread, process, timer, or long-lived object is created.
- **No roadmap/checklist row flipped.** `work/roadmaps/CAPABILITY_CHECKLIST.md` does not appear in `git diff origin/main...HEAD --name-only`; neither does any other roadmap file. SEC3/6.4 remain unclaimed by this PR, which is correct — the note itself says this step does not complete them.

## 5. Correctness and missing-key semantics

Read `runtime/policy/destructive_action_guard.py` line by line against `runtime/policy/harness_guard.py`.

Decision table as implemented:

- Key absent from the context → `DENY`, `guard_code` `CLASSIFICATION_REQUIRED`. The `_declared()` helper returns `(None, False)` for `key not in context`, and `__call__` collects every absent key into the deny message. A forgotten declaration can never mean "not destructive" — this is the note's own recommended fail-closed default and mirrors `CanonicalRunGuard`'s `BINDING_REQUIRED`.
- Key present but not a real `bool` → `DENY`, `CLASSIFICATION_INVALID`. The check is `isinstance(value, bool)`, **not** `isinstance(value, int)`, so the classic `isinstance(True, int)` trap is avoided in the safe direction: `1`, `0`, `"true"`, `None`, `[]`, `{}` are all rejected rather than coerced. The test parametrizes over exactly those values.
- Either boolean `True` → `DENY`, `ACTION_AUTHORITY_ABSENT`, with an `action_classes` annotation naming which flags tripped. This is the honest answer to the note's "source of task policy" question: no authority field exists on the task record, `ExecutionBinding`, or the Hook context today, so the PR invents none and denies instead. I independently confirmed the absence — nothing in the diff reads any task/binding state at all; the guard has no constructor and no data source, which is the strongest possible evidence it did not invent a policy source.
- Both explicitly `False` → `ALLOW`, `ACTION_NOT_CONSEQUENTIAL`. The only allowing path.
- `REQUIRE_APPROVAL` is never constructed anywhere in the module (grep confirms the identifier does not appear), and a test asserts it is unreachable across all four boolean combinations.

Defect hunt — none found:

- **No fail-open path.** Every branch of `__call__` returns an explicit `HookOutcome`; there is no implicit `None` return, no `try/except` swallowing anything, and no default-allow tail. The allow is the last statement and is reached only after both booleans are proven present, proven `bool`, and proven falsy.
- **Exception behavior is deny, not bypass.** `_register_enforcement` (hooks.py:207-210) rejects any spec that is not `FAIL_CLOSED` + `READ_ONLY`, and the helper passes `HookSideEffect.READ_ONLY` with `HookSpec`'s default `HookFailurePolicy.FAIL_CLOSED`. `HookRegistry.run` (hooks.py:262) converts a raising `FAIL_CLOSED` callback into a `DENY` outcome. So even a hypothetical crash inside the guard (e.g. a context object whose `__contains__` raises) yields DENY, not silent permission. Verified in the registry-level tests: `run(BEFORE_DESTRUCTIVE_ACTION, {})` returns `permitted=False, denied=True`.
- **The exact-type check is real.** `type(guard) is not DestructiveExternalActionGuard` rejects subclasses, mirroring `register_canonical_run_guards`; a test subclasses the guard and asserts `TypeError`.
- **Shape/style mirrors `CanonicalRunGuard`.** Same `_deny(code, reason)` static helper producing `HookOutcome(DENY, reason, annotations={"guard_code": ...})`; same explicit-context-extraction pattern as `_extract_binding`; same registration loop over events through `_register_enforcement` with `priority=10` and `READ_ONLY`. It diverges only where the note tells it to (no `source` dependency, since there is no policy source to consult).
- The guard emits no `evidence_refs`, unlike `CanonicalRunGuard`'s ANNOTATE path. That is consistent with the note leaving "where the decision is recorded as evidence" explicitly open for the call-site follow-up, so it is not a defect in this PR; it is the correct thing to leave undone here.

Cross-check of the PR description's four claimed answers to the note's open behavior questions against actual code: (1) missing key fails closed — true; (2) no policy source invented, deny by default — true; (3) DENY not REQUIRE_APPROVAL — true, and mechanically tested; (4) one combined guard over both events — true. The description does not overstate the implementation anywhere I could find.

## 6. Full suite (as CI runs it)

`.github/workflows/runtime-stack-tests.yml` sequence, run in this worktree (`ruff`/`pytest` are not installed on this box, so `unittest` was used):

At the merge head `2cc8e59`:

```
python3 -m compileall -q runtime tests
COMPILEALL_EXIT=0

python3 -m unittest discover -s tests
Ran 782 tests in 1280.026s
OK (skipped=6)
SUITE_EXIT=0
```

Previously at the implementation commit `1b4183e`, the same two commands gave `COMPILEALL_EXIT=0` and `Ran 782 tests in 1295.538s / OK (skipped=6) / SUITE_EXIT=0` — identical counts, as expected given the merge changed no code.

No failures, no errors, no regressions attributable to this PR.

## 7. Review lenses applied

- *Smallest change that satisfies the requirement* — 358 added lines, 139 of them the guard, no infrastructure invented. Passes.
- *Capability is not permission* — the PR adds an enforcement capability without granting itself a call site; the anti-wiring tests keep it that way. Passes.
- *Don't hide uncertainty* — the open questions the note left open are left open explicitly (evidence recording, first concrete call site) rather than guessed. Passes.
- *No duplicate truth* — no second authority database or mirrored classification store. Passes.
- *Fail closed by construction* — verified at three levels: guard logic, registration constraints, and registry exception handling. Passes.
- *An owner never approves their own work* — this review was performed by an agent that did not write the code, in a separate worktree, with mutation testing rather than test-reading alone.

## 8. Evidence checked

- `work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md` (all 186 lines)
- `runtime/policy/destructive_action_guard.py`, `runtime/policy/harness_guard.py`, `runtime/policy/__init__.py`
- `runtime/harness/hooks.py` (`HookEnforcement`, `HookSpec`, `_register_enforcement`, `HookRegistry.run` failure handling)
- `tests/test_destructive_external_action_guard.py` (all 212 lines)
- `scripts/check_review_evidence.py`, `work/reviews/pr-161-review-evidence.md`
- `gh pr view 164 --repo BigCatMellow/MAPS_Lean --json title,body,headRefName,baseRefName`

## 9. Reviewer limits

- I did not review the future call-site wiring, because none exists in this PR; the security value of `DESTRUCTIVE_EXTERNAL_ACTION` is entirely latent until a real caller fires `BEFORE_DESTRUCTIVE_ACTION`/`BEFORE_EXTERNAL_ACTION`. This PR should not be read as closing SEC3 or roadmap 6.4, and it does not claim to.
- The full suite was run once on this box; I did not re-run it under the GitHub Actions image, and `ruff` was unavailable here, so lint-only CI failures are outside what I verified.
- The reviewed head is a merge commit. I confirmed it introduces zero changes under `runtime/` or `tests/` relative to the implementation commit, so the merge did not smuggle code past this review; but any later push to `sec3-guard-impl` other than evidence-only commits invalidates this file by design of the evidence checker.
- Mutation testing and the parent-commit revert were executed against the implementation commit's tree, which is byte-identical to the current head under `runtime/` and `tests/` (empty diff, shown above); they were not re-executed after the merge, since there was nothing to re-execute against. The full CI suite *was* re-run at the merge head.
