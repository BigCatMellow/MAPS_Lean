# PR #205 — SEC4/6.10 A1+A2: `maps skill` operator-transition CLI — independent review evidence

reviewer: maps-lean-kimi
head_sha: 9c3157ae2e9f8bd237aa6d74d360a352b34e44b1
independent: true
verdict: APPROVE (rebase required before merge — see §8; no code change requested)
summary: Slices A1 (`maps skill list|show`) + A2 (`approve|activate|retire|supersede`) of the merged design note are implemented exactly as specified: a thin `runtime/cli.py` subcommand group that resolves a `catalog_key` and delegates every write to `store.record_skill_lifecycle_transition()` with no edge pre-check, the store's in-transaction replay deciding the `from_state` and rejecting illegal edges. All 13 MUST-NOTs hold — no touch to `runtime/skills/lifecycle.py` / `runtime/state/skill_lifecycle_storage.py` / `runtime/state/schema.sql` / `tests/test_skill_lifecycle.py`; no identity registry (`--actor` stays a structural `required=True` string); no `superseded_by` column; no auto-transition; `maps context` not wired; no existing-caller behaviour change (`runtime/cli.py` is the only changed runtime file, +151/-0). No STOP condition triggered. gina's 3 folded findings all present: CAPABILITY_CHECKLIST SEC4 **and** 6.10 evidence text updated with no status flip, exact result-code strings asserted, B5.4 CLI-side check placement left open. Guard/isolation glob green (87 tests), `runtime.smoke` exit 0, 8/8 mutants caught (min 5). One non-blocking note (resolver step-3 uses `startswith` where the note's prose says "substring" — `startswith` is the safer reading of "prefix" and matches note step 2). Not the author (author = maps-lean-pogo).

## 1. Method

Reviewer's own detached `git worktree` at PR #205 head `8442d8b0b9eccf59b734607757cff5911aa743f7` (`git worktree add --detach`), `git fetch origin main` first. `git status` clean, no staged reverts.

Rebase check: `git merge-base --is-ancestor origin/main 8442d8b` → **false**. `origin/main` is `e7d93ca`; commits on main not in head: `e7d93ca` (#204, SEC/6.24) and `306904c` (#202, SEC/6.22). `git merge-tree $(merge-base) 8442d8b origin/main` → **no textual conflict markers** (both land in `runtime/routing/*` + `runtime/policy/*` + `runtime/context_builder.py`; PR #205 touches only `runtime/cli.py`, and #205's `runtime/cli.py` region is `build_parser` + `main` dispatch, untouched by #202/#204). Rebase is mechanical.

Every callsite re-verified at HEAD with `/usr/bin/grep` (rule 14). Sources of truth: `work/notes/2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md` (Item A Q A1–A8, MUST-NOT list, STOP conditions, A3 resolver spec), parents `2026-08-31-sec4-half2-authority-wiring-design.md` and `2026-08-25-sec4-skill-lifecycle-persistence-design.md`, `runtime/skills/lifecycle.py`, `runtime/state/skill_lifecycle_storage.py`, `reference_committee_review`.

Diff: `git diff origin/main...HEAD` — 4 files, +412/-13:
| File | +/- | Content |
|---|---|---|
| `runtime/cli.py` | +151/-0 | `skill` subparser group, `_SKILL_TRANSITION_TARGETS`, `_resolve_skill_catalog_key`, `_dispatch_skill`, one dispatch line in `main` |
| `tests/test_cli_skill.py` | +236 (new) | 19 tests |
| `tests/test_skill_lifecycle_storage.py` | +23/-11 | one rewritten guard test |
| `work/roadmaps/CAPABILITY_CHECKLIST.md` | +2/-2 | SEC4 + 6.10 evidence text |

`git diff --stat -- runtime/` → `runtime/cli.py` only. `runtime/state/schema.sql`, `runtime/skills/lifecycle.py`, `runtime/state/skill_lifecycle_storage.py`, `tests/test_skill_lifecycle.py` — **not in the diff** (verified via `git diff --stat` naming each path).

## 2. A1/A2 scope — implemented as specified

### 2a. Thin CLI, no re-composition (Q A1, rule 12, STOP condition 1) — PASS

`_dispatch_skill` (`runtime/cli.py:430-471`): `list` → `_emit(store.list_skill_lifecycle_subjects(state))`; `show` → `_emit({subject, decisions})` from `get_skill_lifecycle_subject` + `list_skill_lifecycle_decisions`; write verbs → `_emit(store.record_skill_lifecycle_transition(resolved, target, decision_ref=…, decided_by=getattr(args,'actor',None)))`. No lifecycle-state composition, no caching, no replay in the CLI. `/usr/bin/grep -n "transition\|_compose\|replay\|from_state" runtime/cli.py` → only the `_SKILL_TRANSITION_TARGETS` map, the `record_skill_lifecycle_transition` call, and the docstring/comment. `SkillLifecycleState` is imported only to (a) validate a `--state` filter string and (b) construct the `to_state` argument. STOP condition 1 not triggered.

### 2b. One verb per legal edge, store decides `from_state` (Q A2) — PASS

`_SKILL_TRANSITION_TARGETS = {'approve':'APPROVED','activate':'ACTIVE','retire':'RETIRED','supersede':'SUPERSEDED'}` (`cli.py:387`). The CLI never inspects current state before calling the store; the comment at `cli.py:463-466` states this explicitly ("let the store's in-transaction replay decide the from_state and reject an illegal edge. The CLI never pre-checks the transition."). `test_illegal_edge_exits_non_zero_and_writes_nothing` proves the property end-to-end: `activate` on a `VALIDATED` subject → exit 2, `payload['code'] == 'ILLEGAL_SKILL_TRANSITION'` (a **store** code, not a CLI code), and `list_skill_lifecycle_decisions(...) == []` afterwards (nothing written).

### 2c. `--decision-ref` required on every write; `--actor` required only on `approve` (Q A2, Q A6) — PASS

`--decision-ref` added with `required=True` inside the `for verb in (...)` loop (`cli.py:365-369`), so all four write verbs carry it. `--actor` added with `required=True` **only** when `verb == 'approve'` (`cli.py:370-375`). `list`/`show` take neither. `test_approve_without_actor_is_rejected_by_argparse` → `SystemExit(2)`. Read verbs never require them: `test_list_is_empty_before_any_subject`, `test_show_returns_subject_and_decision_history`.

### 2d. `_resolve_skill_catalog_key` — the three Q A3 cases only (Q A3, STOP condition 2) — PASS

`cli.py:395-427`. Case 1: `'@sha256:' in text` → return `text` unchanged (`test_full_catalog_key_passes_through_untouched`). Case 2: `<source_id>:<skill_id>` → filter `list_skill_lifecycle_subjects()` on `source_id` + `skill_id`; exactly one → its `catalog_key` (`test_unique_pair_resolves_to_its_catalog_key`); zero → `SKILL_SUBJECT_NOT_FOUND` (`test_pair_with_no_recorded_subject_is_not_found`); >1 → `MULTIPLE_REVISIONS` listing 12-char `content_sha256` candidates (`test_multiple_revisions_are_refused_with_multiple_revisions`). Case 3: `<pair>@<sha-prefix>` → same filter plus `content_sha256.startswith(sha_prefix)`; >1 → `AMBIGUOUS_SHA_PREFIX` (`test_ambiguous_sha_prefix_code_is_distinct_from_multiple_revisions`). Malformed (`not a pair`, blank) → `INVALID_SKILL_REFERENCE` (`test_bare_string_without_a_pair_is_invalid_reference`, `test_empty_reference_is_invalid`). Read-only: the function only calls `list_skill_lifecycle_subjects()`. No fuzzy matching, no cross-source dedupe — STOP condition 2 not triggered.

### 2e. Failure modes surfaced not swallowed (Q A6) — PASS

`_emit` returns `2` for any `MutationResult`/`ValidationResult` with `ok is False` (`cli.py:44-52`, pre-existing convention shared with `create`/`promote`/`outcome-record`). Every resolver failure and every store failure code reaches the operator as JSON on stdout + exit 2. Tests pin the exact strings (`INVALID_LIFECYCLE_STATE`, `SKILL_SUBJECT_NOT_FOUND`, `ILLEGAL_SKILL_TRANSITION`, `MULTIPLE_REVISIONS`, `AMBIGUOUS_SHA_PREFIX`, `INVALID_SKILL_REFERENCE`, and success `SKILL_TRANSITION_RECORDED`), not just non-zero exit — gina finding 3.

### 2f. Nothing wired into an automated path (Q A7, MUST-NOT "no existing-caller behaviour change") — PASS

`runtime/cli.py` is the only changed runtime file. `git diff` touches neither `runtime/flow_start.py`, `runtime/context_builder.py`, nor `runtime/skills/catalog.py`. `/usr/bin/grep -rn "record_skill_lifecycle_transition\|record_skill_lifecycle_subject" runtime/ --include=*.py` → subject recording still only in `runtime/skills/catalog.py:292` (`register_skill_catalog`), transition calling only new at `runtime/cli.py:469`. `maps flow start` / `build_project_skill_catalog` / `_select_skills` / `load_catalog_skill` paths byte-identical.

## 3. MUST-NOT audit — all 13 hold

| # | MUST-NOT | Result |
|---|---|---|
| 1 | Re-implement/pre-compose lifecycle state in the CLI | PASS — §2a, §2b |
| 2 | Touch `runtime/skills/lifecycle.py`; `tests/test_skill_lifecycle.py` stays green unmodified | PASS — not in diff; 184-line contract file untouched; module runs green (§7) |
| 3 | Change `record_skill_lifecycle_subject()` or subject/decision schema | PASS — `schema.sql` and `skill_lifecycle_storage.py` not in diff |
| 4 | Add a mutable `active`/`state` column | PASS — no schema change; `list`/`show` compose from `list_skill_lifecycle_subjects` (which already replays append-only rows) |
| 5 | Make any existing caller's behaviour change; identity check opt-in never default-on | PASS — §2f; no identity check exists at all in this PR |
| 6 | Build an operator-identity registry (config file / IdP / OS-user / signed payloads) | PASS — no registry; `--actor` is `argparse required=True` free string, passed straight to `decided_by` |
| 7 | Add login / session-auth / credential machinery | PASS — none |
| 8 | Make the identity check implicit / default-on | PASS — N/A, no check introduced (Slice B1 deferred) |
| 9 | Retroactively validate `decided_by`/`actor` on existing rows | PASS — no migration, no backfill |
| 10 | Auto-approve / auto-activate / auto-retire on any signal | PASS — only operator-typed verbs; no gate/age/source logic |
| 11 | Wire `maps context` to build a catalog | PASS — `maps context` dispatch untouched |
| 12 | Add a `superseded_by` FK/column | PASS — no schema change; `supersede`'s successor rides `--decision-ref` free text (`test_supersede_decision_ref_can_name_the_successor`) |
| 13 | Expand Item A into the capability-declaration manifest | PASS — no manifest code |

## 4. STOP conditions — none triggered

CLI composes/caches no state (delegates every write) · resolver stays within the 3 Q A3 cases · Item B (registry) correctly **not** attempted — the design says "build Slice A1 + A2 and flag the coordinator for the operator decision", which is exactly what this PR does (`--actor` left structural, PR body + checklist both flag Half 3 as design-pending on an unmade operator decision) · no default/expected-output change · no schema migration.

## 5. gina's 3 folded design-review findings — all present

1. **CAPABILITY_CHECKLIST updated, no status flip** — PASS. SEC4 row: new "Re-verified 2026-08-31 (impl of … Slices A1+A2)" sentence describing the CLI, the no-pre-check delegation, `--decision-ref`/`--actor`, and the resolver codes; `| IN PROGRESS |` unchanged. 6.10 row: "operator-driven transitions landed 2026-08-31 — `maps skill list|show|approve|activate|retire|supersede` CLI … thin over the store with no edge pre-check"; `| IN PROGRESS |` unchanged. Both still list the remaining gaps (no operator-identity check, `maps context` not wired, no Skill-body loading, no capability manifest).
2. **B5.4 CLI-side identity-check placement not precluded** — PASS. `decided_by=getattr(args, 'actor', None)` is computed in `_dispatch_skill` immediately before the store call; a future opt-in `is_authorized_operator(actor)` check drops in at that point with no structural change. A2 adds nothing that would have to be unwound.
3. **Exact result-code strings asserted** — PASS. §2e; every `assertEqual(payload['code'], '…')` / `assertEqual(result.code, '…')` in `test_cli_skill.py`.

## 6. The rewritten storage guard test — not loosened to a no-op

`tests/test_skill_lifecycle_storage.py::test_half_2_read_side_consumers_only_no_operator_transition_caller` → `test_skill_lifecycle_store_consumers_are_the_known_seams`.

(a) **Still bars every other module.** The rewrite keeps the `for path in (REPO_ROOT/"runtime").rglob("*.py")` sweep. For `record_skill_lifecycle_transition` it changed `assertEqual(path, storage.py)` → `assertIn(path, {storage.py, cli.py})` — i.e. it admits exactly `runtime/cli.py` as the new caller and nothing else. For the subject/read-side API (`record_skill_lifecycle_subject`, `get_skill_lifecycle_state`, `get_skill_lifecycle_subject`) it added `cli.py` to the `allowed` skip-set and still `assertNotIn`s those names in every other file. **Meta-check (M9):** appending a `record_skill_lifecycle_transition` reference to `runtime/policy/evaluator.py` → the test FAILS (`evaluator.py … calls the operator-transition API; the only production caller is runtime/cli.py`), then reverted. The guard bites.
(b) **`tests/test_skill_lifecycle.py` untouched** — confirmed absent from `git diff --stat`; the 184-line pure-graph contract file is byte-identical to `origin/main`.

Note (non-blocking): the guarded read-side tuple never included `list_skill_lifecycle_subjects` / `list_skill_lifecycle_decisions` — that was already true on `origin/main`, not a regression introduced here.

## 7. Verify commands (blocking foreground, reviewer worktree)

```
python3 -m unittest tests.test_skill_lifecycle_storage tests.test_skill_lifecycle tests.test_skills_catalog tests.test_cli_skill
  → Ran 87 tests ... OK
  (dispatch named tests.test_cli — no such module exists in the repo; the
   `maps skill` CLI is covered by the new tests.test_cli_skill, and cli.main
   is additionally exercised by tests.test_flow_start / tests.test_routing_cli)
python3 -m runtime.smoke
  → {"ok": true, ...}  exit 0
```

87 targeted tests green; smoke exit 0.

## 8. Mutation testing — 8 mutants, 8 caught (min 5 required)

Each: single textual substitution at HEAD in `runtime/cli.py`, `python3 -m unittest tests.test_cli_skill`, then `git checkout --`.

| # | Target | Mutation | Killing test(s) | Observed |
|---|--------|----------|-----------------|----------|
| M1 | verb→state map | `'activate': 'ACTIVE'` → `'APPROVED'` | `test_full_operator_chain_composes_after_every_verb` | CAUGHT — `activate` now hits `APPROVED→APPROVED`, exit 2 ≠ 0; `FAILED (failures=2)` |
| M2 | verb→state map | `'approve': 'APPROVED'` → `'ACTIVE'` | `test_full_operator_chain_…`, `test_transition_on_unknown_subject_is_typed` | CAUGHT — `VALIDATED→ACTIVE` illegal; `to_state != 'APPROVED'`; `FAILED (failures=2)` |
| M3 | verb→state map | `'retire': 'RETIRED'` → `'SUPERSEDED'` | `test_quarantined_skill_can_be_approved_or_retired_by_the_cli` | CAUGHT — `'SUPERSEDED' != 'RETIRED'` and `QUARANTINED→SUPERSEDED` illegal; `FAILED (failures=2)` |
| M4 | verb→state map | `'supersede': 'SUPERSEDED'` → `'RETIRED'` | `test_supersede_decision_ref_can_name_the_successor` | CAUGHT — `'RETIRED' != 'SUPERSEDED'`; `FAILED (failures=1)` |
| M5 | `_resolve_skill_catalog_key` | `if '@sha256:' in text:` → `not in text` | `test_full_catalog_key_passes_through_untouched` (+ show/transition tests) | CAUGHT — full key no longer passes through, resolver returns a `MutationResult`; `AttributeError: 'str' object has no attribute 'code'` / `KeyError: 'subject'` |
| M6 | resolver ambiguity code | swap `'AMBIGUOUS_SHA_PREFIX' if sha_prefix else 'MULTIPLE_REVISIONS'` | `test_multiple_revisions_are_refused_…`, `test_ambiguous_sha_prefix_code_is_distinct_…` | CAUGHT — codes cross-assert; `FAILED (failures=2)` |
| M7 | `approve` actor guard | `--actor` `required=True` → `required=False` | `test_approve_without_actor_is_rejected_by_argparse` | CAUGHT — `AssertionError: SystemExit not raised`; `FAILED (failures=1)` |
| M8 | failure surfacing (`_emit`) | `return 0 if ok else 2` → `… else 0` | `test_illegal_edge_exits_non_zero_and_writes_nothing`, `test_list_rejects_an_unknown_state_string`, `test_show_unknown_subject_is_a_typed_failure`, `test_transition_on_unknown_subject_is_typed` | CAUGHT — `AssertionError: 0 != 2` ×4 |
| M9 | guard-test efficacy (meta, in `runtime/policy/evaluator.py`) | append `# record_skill_lifecycle_transition` | `test_skill_lifecycle_store_consumers_are_the_known_seams` | CAUGHT — `evaluator.py … calls the operator-transition API`; `FAILED (failures=1)` |

No surviving mutants. M1–M4 pin the verb→state map; M5–M6 pin the resolver's three cases + ambiguity codes; M7 pins the `approve --actor` requirement; M8 pins "illegal edge → non-zero exit"; M9 (with `test_illegal_edge_…`'s post-state assertion) pins "store replay decides, nothing written on an illegal edge" and confirms the rewritten guard still bars non-seam callers.

## 9. Non-blocking findings

1. **Resolver step-3 wording** — the design note Q A3 step 3 says "substring match on `content_sha256`", but step 2 calls it "disambiguate with `<source_id>:<skill_id>@<sha-prefix>`". The impl uses `content_sha256.startswith(sha_prefix)` (prefix, not substring). `startswith` is the safer and more conventional reading of "sha prefix" and matches step 2's own phrasing; a substring match would let a middle-of-hash fragment resolve, which is almost certainly not intended. No change requested — flag only so the note's step-3 prose can be tightened to "prefix" in a later doc pass.
2. **Dispatch test glob** — `tests.test_cli` named in the dispatch does not exist; used `tests.test_cli_skill` (the PR's own new module) + the guard glob. Recording so the next SEC4 dispatch cites the right module.

## 10. Verdict

**APPROVE.** A1+A2 implemented exactly to the merged design note; all 13 MUST-NOTs hold; no STOP condition triggered; gina's 3 findings folded in; the rewritten guard test still enforces; 87 targeted tests green; `runtime.smoke` exit 0; 8/8 mutants caught.

**Merge-prep note for @niko:** the branch is behind `origin/main` (#202, #204) — rebase required. No textual conflict (`merge-tree` clean; #205 touches only `runtime/cli.py` `build_parser`/`main`, which #202/#204 do not). After rebase, the code SHA changes and this file's `head_sha` goes stale by design (fail-closed) — re-commit this evidence content bound to the rebased non-evidence SHA, or have the reviewer re-bind. No self-merge.
