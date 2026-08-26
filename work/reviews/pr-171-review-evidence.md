reviewer: /root/pr171_reviewer (agent a35187eb3e33771fa, isolated worktree)
head_sha: 51d5fbbbb3279dea330f83cd244fa344e2bb0e2e
independent: true
summary: APPROVED — PR #171 lands exactly Half 1 (durable storage) of the merged design note work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md and nothing else, and I verified this independently rather than from the PR description: the diff is exactly the four expected files (runtime/state/schema.sql +106, runtime/state/skill_lifecycle_storage.py new 445 lines, runtime/state/store.py +2, tests/test_skill_lifecycle_storage.py new 723 lines), runtime/skills/lifecycle.py and tests/test_skill_lifecycle.py are byte-unchanged, runtime/context_builder.py / runtime/skills/catalog.py (SkillTrustState still single-member UNASSESSED) / runtime/trust.py are untouched, CAPABILITY_CHECKLIST.md is untouched with SEC4 (line 60) and 6.10 (line 119) both still IN PROGRESS, and grep confirms zero production callers of the six new store methods anywhere under runtime/ outside the mixin itself, so no Half-2 authority wiring leaked in; every non-goal in the note holds (both tables live in the existing TaskStore schema.sql with no new .sql file, no new connection logic and no sidecar registry, there is no mutable state column — effective state is composed by replaying append-only decisions through the pure validator — no Skill body text reaches SQLite, no daemon/scheduler/watcher, no supersession link or graph column, no auto-approval path since initial_state is derived only from initial_transition_from_gate_report() and is CHECK-restricted to VALIDATED/QUARANTINED, and no CLI/UI surface); I proved the new tests are non-tautological by first restoring the three origin/main non-test files, which made tests/test_skill_lifecycle_storage.py fail 31 of 35 tests, and then by applying six targeted mutations one at a time in a scratch copy — dropping the schema APPROVED-actor CHECK, making _compose_skill_state return initial_state without replaying, replacing the write path's transition() call with an inlined copy of the graph, dropping trg_skill_lifecycle_subjects_no_update, adding "import threading", and adding a body_text column that stores the SKILL.md text — each of which was caught by exactly the test that claims to cover it, with no mutation surviving; I separately confirmed the module's lazy-import workaround is load-bearing by adding a module-level "from runtime.skills.lifecycle import transition" and observing the real circular ImportError through runtime.skills.gate -> runtime.state.observability -> runtime.state.store, and confirmed the write path uses BEGIN IMMEDIATE with a rollback on every early return, FK enforcement via BaseStore's PRAGMA foreign_keys = ON, and read paths that raise loudly rather than return a graph-forbidden state; the full suite run as a single blocking call with CI's PYTHONWARNINGS=error::ResourceWarning gave "Ran 841 tests ... OK (skipped=6)" with exit code 0, gh pr checks 171 shows test pass and review-evidence fail (expected until this file lands), and the only findings are non-blocking nits recorded below.

# Review: PR #171 — Persist Skill lifecycle state (SEC4 / roadmap 6.10, Half 1)

- Branch reviewed: `sec4-skill-lifecycle-impl` @ `51d5fbbbb3279dea330f83cd244fa344e2bb0e2e` (matches `gh pr view 171 --json headRefOid`)
- Base: `main`
- Reviewed by: `/root/pr171_reviewer` — independent agent, did not author the code, worked only in its own isolated worktree
- Verdict: **APPROVED**

## 1. Scope

`git diff --name-only origin/main...HEAD`:

```
runtime/state/schema.sql
runtime/state/skill_lifecycle_storage.py
runtime/state/store.py
tests/test_skill_lifecycle_storage.py
```

`--stat`: `+106`, `+445` (new), `+2`, `+723` (new) = 1276 insertions, 0 deletions. Exactly the four expected files.

Verified unchanged in this diff:

- `runtime/skills/lifecycle.py` — byte-unchanged (empty diff).
- `tests/test_skill_lifecycle.py` — unmodified and still passing (part of the green full suite; also confirmed green in a targeted run of `tests.test_skill_lifecycle`).
- `work/roadmaps/CAPABILITY_CHECKLIST.md` — untouched. Line 60 (SEC4) and line 119 (6.10) both still read `IN PROGRESS`; nothing was marked DONE.
- `runtime/context_builder.py`, `runtime/skills/catalog.py`, `runtime/trust.py` — untouched.

### Landing Half 1 alone is correct

The design note's own boundary section ("What 'durable storage + real authority wiring' means as an implementation boundary") states the two halves "should be two PRs, the same way `#154 -> #160` and the operational-learning storage/authority tasks were split." This PR implements the note's Half-1 in-scope list item for item: two tables + triggers in `schema.sql`; the mixin with record-subject / record-transition / get-state / list-decisions / list-subjects-by-state; mixin registration on `TaskStore`; and round-trip / illegal-edge / direct-SQL-CHECK / immutability-trigger / content-edit tests. It implements none of the Half-2 list.

## 2. Non-goals — each checked

| Non-goal | Result |
| --- | --- |
| No second authority database | Both tables appended to the existing `runtime/state/schema.sql`. `runtime/state/*.sql` still contains only `schema.sql`. No `sqlite3.connect(` in the new module (only `BaseStore._connect()`); no sidecar JSON/YAML registry — a test walks the whole temp tree for stray `.db/.sqlite/.json/.yaml` files. |
| No mutable state column | `skill_lifecycle_subjects` stores `initial_state` only, on a row locked by `BEFORE UPDATE`/`BEFORE DELETE` triggers. Effective state is composed by `_compose_skill_state()`. `PRAGMA table_info` assertions confirm no `state` / `current_state` / `lifecycle_state` column exists. |
| No Skill content in SQLite | Subject columns are identity, hashes and `gate_report` only. I checked `SkillGateReport.to_dict()` and `_finding()` in `runtime/skills/gate.py` directly: every finding `summary` is a fixed literal string and no matched body text is ever embedded, so the one JSON blob really is verdict metadata. The sentinel test scans the raw DB bytes. |
| No daemon / background sync / watcher | Token-level source guard over the module (comments and string literals stripped by `tokenize`) rejects `threading`/`multiprocessing`/`asyncio`/`concurrent`/`sched`/`signal`/`subprocess`/scheduler libs plus `daemon`, `time.sleep`, `while True`, `sqlite3.connect(`, `attach database`. The guard has both positive and negative self-tests. |
| No knowledge graph / supersession link | No `superseded_by` column on either table (asserted); the module docstring resolves note question 8 by declining the pointer. |
| No change to the pure module | `runtime/skills/lifecycle.py` byte-unchanged; `tests/test_skill_lifecycle.py` unmodified and green. |
| No auto-approval | `record_skill_lifecycle_subject()` takes no caller-supplied starting state; `initial_state` comes only from `initial_transition_from_gate_report()` and is `CHECK`-restricted to `VALIDATED`/`QUARANTINED` at the schema level too. Every `-> APPROVED` needs a non-empty actor (pure validator) and a non-null `decided_by` (schema `CHECK`). |
| No CLI/UI surface | `runtime/cli.py` untouched; no new entry points. |

## 3. No Half-2 leakage

`grep -rn` for the six method names across `runtime/**/*.py` returns hits only inside `runtime/state/skill_lifecycle_storage.py`. `runtime/state/store.py` changes are exactly one import line and one MRO entry. `SkillTrustState` still has the single member `UNASSESSED`, and `runtime/skills/catalog.py` contains no `skill_lifecycle` reference. The test suite pins all of this structurally, so a future Half-2 PR must consciously update the guard.

## 4. Non-tautological test verification

All mutation work was done in a throwaway copy of the tree under the session scratchpad; the reviewed worktree was never modified (`git status --porcelain` empty before the evidence commit).

**Revert check (parent-state baseline).** Restored the `origin/main` versions of `runtime/state/schema.sql` and `runtime/state/store.py` and deleted `runtime/state/skill_lifecycle_storage.py`, leaving the new test file in place: `Ran 35 tests ... FAILED (failures=2, errors=29)`. The suite cannot pass without the change.

**Targeted mutations** (each applied alone to a pristine copy, relevant class run, then reverted):

| # | Mutation | Test class run | Observed |
| --- | --- | --- | --- |
| i | Removed the `CHECK (NOT (to_state = 'APPROVED' AND (decided_by IS NULL OR ...)))` table constraint | `SkillLifecycleSqlEnforcementTests` | FAIL `test_approved_without_actor_is_refused_by_the_check_constraint` (subTest `actor=None`) — `AssertionError: IntegrityError not raised`. `FAILED (failures=1)` |
| ii | `_compose_skill_state()` returns the subject's `initial_state` without replaying decisions | whole module | 8 failures, including `test_full_decision_chain_composes_after_every_write`, `test_corrupt_decision_chain_fails_loudly_on_read`, `test_terminal_state_refuses_further_decisions`, `test_quarantined_to_retired_needs_no_actor`, `test_decision_rows_are_append_only`. `FAILED (failures=8)` |
| iii | Replaced the write path's `_lifecycle.transition(...)` call with an inlined copy of the graph + actor rule (behaviour-identical, delegation removed) | whole module | Exactly one failure: `test_storage_delegates_to_the_pure_validator` — `AssertionError: True is not false` (the write succeeded despite the canonical `transition` being patched to raise). `FAILED (failures=1)` |
| iv | Dropped `trg_skill_lifecycle_subjects_no_update` | `SkillLifecycleSqlEnforcementTests` | FAIL `test_subject_rows_are_immutable` — `AssertionError: IntegrityError not raised`. `FAILED (failures=1)` |
| v | Added `import threading` to `runtime/state/skill_lifecycle_storage.py` | `SkillLifecycleSourceGuardTests` | FAIL `test_storage_module_has_no_daemon_scheduler_or_own_connection` — "must not spawn machinery or open its own DB". `FAILED (failures=1)` |
| vi | Added a `body_text` subject column and wrote `SKILL.md`'s text into it | `SkillLifecycleNonGoalGuardTests` | FAIL `test_skill_body_content_is_never_stored_in_sqlite` — `b'ZZQUUXSENTINEL42' unexpectedly found` in the DB bytes. `FAILED (failures=1)` |

No mutation survived a test that claims to cover it. Mutation iii is the strongest signal: it is a *semantically equivalent* reimplementation, so the delegation test is detecting duplicated truth rather than wrong behaviour, which is precisely what the note's rule-12 requirement needs.

**Import-cycle probe (extra).** The module's lazy-import comment claims a module-level `from runtime.skills...` would close a cycle. I added `from runtime.skills.lifecycle import transition` at module level and ran `python3 -c "import runtime.skills"`: `ImportError: cannot import name 'SkillGateDisposition' from partially initialized module 'runtime.skills.gate' (most likely due to a circular import)`. The claim is accurate and the workaround is load-bearing, not cargo-culted. Because the call-time imports resolve the canonical module object (`from runtime.skills import lifecycle as _lifecycle` + attribute access), `mock.patch("runtime.skills.lifecycle.transition")` is genuinely observable through it — mutation iii confirms this empirically.

## 5. Code correctness

- **Transactions.** Both writers open `BEGIN IMMEDIATE` and `rollback()` on *every* early return I could find: subject-exists, `IntegrityError` on subject insert, subject-not-found, `SkillLifecycleError` from replay/validation, and `IntegrityError` on decision insert. Connections are wrapped in `closing()`. Recomputing the current state by replay *inside* the same immediate transaction that inserts is the right choice — the `RESERVED` lock is taken before the read, so two writers cannot both append from the same stale state.
- **FK / CHECK.** `BaseStore._connect()` issues `PRAGMA foreign_keys = ON`, so the `catalog_key` FK is enforced (a direct-SQL test proves a decision for a `'ghost'` subject is rejected). State vocabularies are `CHECK`-restricted on both columns, `from_state <> to_state` is enforced, `content_sha256` is length-64, `gate_report` is `json_valid`, `initial_state` cannot be `APPROVED`, and a terminal-state insert trigger blocks post-`SUPERSEDED`/`RETIRED` rows on the direct-SQL path.
- **Replay semantics.** `_compose_skill_state()` rejects a row whose recorded `from_state` disagrees with the replayed state *and* re-validates each edge through `transition()`, so a hand-inserted decision row cannot produce a state the graph forbids — confirmed live by `test_corrupt_decision_chain_fails_loudly_on_read`.
- **Read paths.** I found no path that can return a graph-forbidden state: `get_skill_lifecycle_state`, `get_skill_lifecycle_subject` and `list_skill_lifecycle_subjects` all route through the same composer and propagate `SkillLifecycleError` rather than swallowing it.

## 6. Design-note behaviour questions

Explicitly resolved in the module docstring (not silently): **1** `catalog_key` as PK, content-addressed, `BUNDLED` gets no special rule and the ergonomics question is handed to Half 2; **2** a vanished Skill keeps its row, no read-time downgrade, no inferred `RETIRED`, no deletion; **3** `DISCOVERED` is never persisted and `None` means "not assessed yet"; **4** no production caller exists in Half 1, by design; **8** no `superseded_by` pointer, successor named in `decision_ref` free text if wanted. Questions **5** (real actor check), **6** (`SkillTrustState`'s future) and **7** (fingerprint sensitivity) are correctly absent from the docstring and left to Half 2 — and the source guard test actively enforces that 6 has not been pre-empted.

## 7. Full suite

Run as a single blocking call with CI's setting, redirected so the real exit status is captured:

```
PYTHONWARNINGS=error::ResourceWarning python3 -m unittest discover -s tests > <log> 2>&1; echo EXIT=$?
Ran 841 tests in 1332.151s
OK (skipped=6)
EXIT=0
```

Matches the author's reported 841 / OK / 6 skipped. `gh pr checks 171`: `test` **pass**, `review-evidence` **fail** (expected — this file had not landed yet).

`main` advanced from `4ece9b1` to `d22036b` (PR #172) during this review. Its diff touches `runtime/cli.py`, `runtime/recovery/production.py`, `runtime/recovery/supervisor.py` and two recovery test files — disjoint from all four files reviewed here, so no rebase or `head_sha` rebind was required and this evidence stays bound to the PR head `51d5fbb`.

## 8. Findings

### Blocking

None.

### Non-blocking

1. **Schema state vocabulary can drift from the enum.** `schema.sql` hardcodes the seven state strings in two `CHECK`s. If `SkillLifecycleState` ever gains or loses a member, nothing fails: no test asserts that the `CHECK` vocabulary equals `set(SkillLifecycleState)`. The defense-in-depth duplication is sanctioned by the note, but a one-line test parsing the `CHECK` list and comparing it to the enum would make the duplication self-policing. Suggest for Half 2.
2. **A malformed persisted state string raises bare `ValueError`, not `SkillLifecycleError`.** In `_compose_skill_state()`, `SkillLifecycleState(str(row[...]))` raises `ValueError` for an unknown value, bypassing the module's own error type. Unreachable today (both `CHECK`s constrain the vocabulary) and harmless in practice since `SkillLifecycleError` subclasses `ValueError`, but the failure mode would read as a crash rather than a lifecycle refusal.
3. **Error-surfacing style is inconsistent between reads and writes.** Writes return `MutationResult(False, ...)` for bad input; `list_skill_lifecycle_subjects()` *raises* `SkillLifecycleError` for a non-enum `state` argument. Both are defensible; worth settling once when Half 2 adds callers.
4. **Redundant clause in the actor `CHECK`.** `length(trim(decided_by)) = 0` can never be reached, because the `decided_by` column `CHECK` already requires `length(trim(decided_by)) BETWEEN 1 AND 128` for any non-NULL value. Harmless belt-and-braces; noting it only so it is not read as a second, distinct rule.
5. **`list_skill_lifecycle_subjects()` is N+1.** One decisions query per subject inside the loop. Irrelevant at Skill-catalog cardinality; flagged only in case Half 2 calls it on a hot catalog-build path.
6. **`test_subject_cannot_be_created_already_approved` leans partly on a Python signature.** The `assertRaises(TypeError)` half only proves the keyword does not exist. The test is saved by its companion schema-level assertion (`initial_state` `CHECK`) and by `test_subject_initial_state_cannot_be_approved_at_the_schema_level`, so the intent is genuinely covered — the `TypeError` line just carries no independent weight.
