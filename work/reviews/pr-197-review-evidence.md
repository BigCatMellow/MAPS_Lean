# PR #197 — SEC4 catalog-entrypoint design + #192 nits — independent review evidence

reviewer: maps-lean-vara
head_sha: 8e69a73ce856ce3d935062d27b160beea9d132bc
independent: true
verdict: PASS (APPROVE)
summary: The design note answers all three questions soundly and respects #190's scope boundary (it makes exactly the decision #190 deferred, authorised by trajectory-check-10 §5a.3). All four #192 nits are correct — nit1 is genuinely a no-op (no `SkillTrustState` ref in `runtime/policy/memory_trust_gate.py`; `runtime/memory/memory_trust_gate.py` does not exist), nit2 is a byte-identical pure refactor with both call sites updated, nit3's docstring is factually accurate, nit4's `-> list[MutationResult]` is the real return type. 83 target tests pass, `runtime.smoke` exit 0. Two non-blocking items for the impl PR (below). Not the author (lola).

## Method

Reviewer's own worktree at PR #197, rebased onto `origin/main` `d810509` →
code commit `8e69a73`. `git fetch origin` first; every callsite re-derived at
that HEAD with `/usr/bin/grep` (rule 14). Sources of truth:
`work/notes/2026-08-31-sec4-half2-authority-wiring-design.md` (#190) "Half 2
impl — scope boundary", `work/notes/2026-08-31-roadmap-trajectory-check-10.md`
§5a.3, PR #192 (`ae0d1ed`) + its four handoff nits. Reviewer did not author
PR #197, #192, #190, or the persistence note.

## 1. Diff in bounds

`git diff origin/main...8e69a73 --stat` — 3 files:

| File | Content |
|---|---|
| `work/notes/2026-08-31-sec4-catalog-entrypoint-design.md` (+239) | the design note |
| `runtime/skills/catalog.py` (+26/-11) | nit2 (`_catalog_key` helper) + nit4 (`-> list["MutationResult"]` + TYPE_CHECKING import) |
| `runtime/skills/lifecycle.py` (+18/-15) | nit3 (module docstring prose only) |

No `CAPABILITY_CHECKLIST.md` change (the note leaves the one-line evidence
annotation to the impl PR). No capability STATUS change, no `schema.sql`, no new
hook event, no entrypoint wired (`build_project_skill_catalog` is designed, not
added; `flow_start.py` untouched). `git diff --check` clean.

## 2. Design half

### (a) skills root / sources — SOUND

Decision: one `BUNDLED` `SkillCatalogSource` rooted at
`<repo_root>/.claude/skills/`, discovered fresh per entrypoint call, no config
key.

Verified: `.claude/skills/` holds exactly one Skill (`.claude/skills/pilot/SKILL.md`);
no `skills/` root, no `MAPS_SKILLS_ROOT`-style key anywhere.
`discover_skills(root)` returns `()` for a missing root (`format.py`:
`if not root.exists(): return ()` — does not raise), so a checkout without the
dir yields an empty catalog and a byte-identical flow. `SkillCatalogSource`
carries `source_id` / `root` / `kind` and `SkillSourceKind.BUNDLED` exists; the
note's constructor call is accurate. Third-party sources are correctly deferred
to SEC4's capability-declaration-manifest half.

### (b) which entrypoint — SOUND

Decision: new thin `build_project_skill_catalog(repo_root, store, *, now=None)`
on `catalog.py`, wired into `flow_start.py` only; `maps context` (`cli.py:373`)
untouched.

Verified: `build_context_plan` has **exactly two** production callers —
`runtime/cli.py:373` (`maps context`) and `runtime/flow_start.py:80`
(`maps flow start`), both passing no `skill_catalog` today. So the note's
reasoning holds: wiring inside `build_context_plan` would hit both callers at
once (the "forces a production catalog into existence" move #190 deferred),
whereas passing `skill_catalog=` from `flow_start` alone keeps the plan builder
a pure consumer. `flow_start(store: TaskStore, …, repo_root=".")` already holds
both a store (Skill-lifecycle mixin) and a repo_root and already calls
`build_context_plan` at step 2 — the wiring is ~2 lines. The `maps context`
write-on-read concern is real: `register_skill_catalog` inserts
`record_skill_lifecycle_subject` rows, a surprising side effect of an ad-hoc
read-only inspection command; deferring it is the right call. Rejecting a new
module/daemon (rule 13) and "inside build_context_plan" is well-argued.

### (c) roadmap-6.11 interaction — SOUND, does NOT stray into 6.9/6.11

Bounded answer: the slice loads no Skill body, changes no budget-class
semantics; it only makes `lifecycle_state` real so the existing trust gate acts
on it.

Verified against `_select_skills` (`context_builder.py`): it reads only
descriptor/provenance metadata, never calls `load_skill` / `load_catalog_skill`
— no Skill body can enter a plan. The trust table is exactly as the note states:
`_SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS` maps `QUARANTINED → QUARANTINED`,
and `_ADMISSION_TABLE[QUARANTINED] = DENY`; `_select_skills` `continue`s past a
`DENY` and tallies it under coverage. So a matched `QUARANTINED` Skill is
genuinely dropped from a real `maps flow start` plan — the first refusal
reachable in a real run. `None`/`DISCOVERED → OBSERVATION → WITHHOLD` (ON_DEMAND
metadata), `VALIDATED/APPROVED → LOAD` (metadata only), `SUPERSEDED/RETIRED →
WITHHOLD`. The note explicitly defers progressive body loading to 6.9/S6 and
names the three sub-questions it does not answer. No 6.11 budget territory is
entered.

Minor (non-blocking): the note's (c) line "`ACTIVE` → `ACTIVE_INSTRUCTION` →
LOAD" is imprecise — `_LOAD_REQUIRES_PROVEN_ACTIVE_SOURCE` withholds
`ACTIVE_INSTRUCTION` absent a prover. `ACTIVE` is unreachable in this slice, so
cosmetic only.

### #190 boundary — RESPECTED

#190's out-of-scope fences off "committing `cli.py`/`flow_start.py` to build a
`SkillCatalog` and deciding the catalog composition root". #197 makes exactly
that decision — which is its stated purpose and is authorised by
trajectory-check-10 §5a.3. #190 also fences off "any change to
`runtime/skills/lifecycle.py` — transition graph, actor rules, public
functions". nit3 touches only the module docstring prose (verified: the diff
stops above "Design notes on the transition graph:"; the graph, actor rules and
functions are untouched, `tests/test_skill_lifecycle.py` is not in the diff and
passes). No operator-identity registry / SEC4 Half 3, no
`record_skill_lifecycle_transition` caller, no schema change — all correctly in
the note's "Explicitly NOT in the impl PR" list.

### smallest-first slice — GENUINELY SMALL

`build_project_skill_catalog` ≈8 lines + `flow_start` ~2 lines + tests. Defers
`maps context` wiring, body loading, multi-source, operator identity cleanly.
Rule 8 satisfied.

## 3. Nit half

| # | Finding | Verdict |
|---|---|---|
| 1 | `runtime/memory/memory_trust_gate.py` comment refs deleted `SkillTrustState` | **No-op confirmed.** That path does not exist; the real file is `runtime/policy/memory_trust_gate.py` and `/usr/bin/grep -rn SkillTrustState runtime/` shows zero refs there (the only three tree-wide hits — `trust.py:74`, `context_builder.py:32`, `lifecycle.py:18` — are accurate historical mentions). Nit misattributed, as the note says. |
| 2 | `_catalog_key` helper extraction | **Pure refactor.** New `_catalog_key(source_id, descriptor)` f-string is byte-identical to both former inline copies. `SkillCatalogEntry.catalog_key` now calls `_catalog_key(self.provenance.source_id, self.descriptor)`; `build_skill_catalog` calls `_catalog_key(source.source_id, descriptor)`. `provenance.source_id` is set to `source.source_id` at build time (`catalog.py:214`), so the two produce the identical key. Both call sites updated; no third copy remains. |
| 3 | `lifecycle.py` docstring refresh | **Accurate.** "SEC4 Half 1, PR #171" — confirmed (`git log`: `44ab61f Merge pull request #171 … sec4-skill-lifecycle-impl`). `runtime.state.skill_lifecycle_storage` exists; `SkillProvenance.lifecycle_state: SkillLifecycleState | None` exists (`catalog.py:92`); `SkillTrustState` collapsed by #192 (corroborated by `trust.py:74` comment); `runtime.trust.skill_lifecycle_trust_class` is the projection to `MemoryTrustClass` (`trust.py:115`). Prose-only; transition graph section untouched. |
| 4 | `register_skill_catalog -> list` bare annotation | **Correct fix.** `register_skill_catalog` returns `results`, a list of `store.record_skill_lifecycle_subject(...)` values; that method is annotated `-> MutationResult` (`skill_lifecycle_storage.py:194`). `MutationResult` is in `runtime.state.common` (`common.py:33`), imported under `TYPE_CHECKING` matching the existing `SkillLifecycleStorageMixin` pattern in the same file. `-> "list[MutationResult]"` is right. |

### nit2 mutation testing — `tests.test_skills_catalog`

| # | Mutation to `_catalog_key` | Result |
|---|---|---|
| M1 | drop `descriptor.content_sha256` from the key (→ constant) | **CAUGHT** — FAILED (failures=1); `test` at `test_skills_catalog.py:74` asserts the content hash is a substring of `catalog_key` |
| M2 | swap `source_id` / `descriptor.skill_id` order | **SURVIVED** — suite OK |
| M3 | change the `:` separator to `/` | **SURVIVED** — suite OK |

**Assessment:** M2/M3 surviving is a *pre-existing* test-coverage thinness, not
a defect introduced by nit2. The only format assertion
(`assertIn(content_sha256, catalog_key)`) checks the hash is present, not the
exact layout; the store round-trip tests use `entry.catalog_key` for both write
and read within one process, so any *self-consistent* format round-trips. nit2
is behaviour-preserving (M1, the semantically load-bearing "is it
content-addressed" property, is caught). But `catalog_key` **is** a persistence
key (`get_skill_lifecycle_subject(entry.catalog_key)`), and the refactor
collapses the last place two independent formulas could be cross-checked — so
the note's claim of "test coverage via the existing round-trip tests" is
partially over-stated. → **Non-blocking recommendation 1** below.

## 4. Suite + smoke

- `python3 -m unittest tests.test_skills_catalog tests.test_skill_lifecycle
  tests.test_memory_trust_gate tests.test_context_builder
  tests.test_skills_selection_evaluation tests.test_trust` → **Ran 83 tests …
  OK** (one blocking foreground call).
- `python3 -m runtime.smoke` → `"ok": true`, exit 0.
- Worktree `git status` clean after all mutations reverted.

## 5. Non-blocking items for the impl PR (not merge blockers)

1. **Pin the `_catalog_key` format.** Since the key is a persistence key and
   M2/M3 mutations survive today, the impl PR (which touches this file for
   `build_project_skill_catalog`) should add one assertion of the exact output,
   e.g. `_catalog_key("bundled", d) == f"bundled:{d.skill_id}@sha256:{d.content_sha256}"`.
2. **`runtime/policy/memory_trust_gate.py:47-49` comment** says
   `ACTIVE_INSTRUCTION`/`CANONICAL_POLICY` are unreachable "until a durable
   store is wired into `build_skill_catalog()`" — post-#192 the `store=` param
   exists; the impl PR that adds `build_project_skill_catalog` should reword to
   "until a production entrypoint builds a catalog with a store" (which is
   precisely what that PR does).
3. Design note (c): "`ACTIVE` → `ACTIVE_INSTRUCTION` → LOAD" — imprecise
   (withheld absent an active-source prover); cosmetic, `ACTIVE` unreachable in
   the slice.

## Verdict

**PASS / APPROVE.** The three design questions are answered soundly; the
decisions respect #190's boundary (and are the decision #190 explicitly
deferred to a note like this); the slice is genuinely ~10 lines and defers the
open questions cleanly without straying into 6.9/6.11. All four nits are correct
— nit1 a real no-op, nit2 a byte-identical pure refactor, nit3/nit4 accurate.
Tests + smoke green. Three non-blocking items recorded for the impl PR. `miga`
handles rebase already done here / merge.
