# PR #200 — SEC4 catalog-entrypoint impl slice — independent review evidence

reviewer: maps-lean-hemo
head_sha: f64c60736355b36a97ef43f03738595a3e7fb25f
independent: true
summary: APPROVE. The slice matches `work/notes/2026-08-31-sec4-catalog-entrypoint-design.md` exactly — one `BUNDLED` source at `<repo_root>/.claude/skills/`, `build_project_skill_catalog` wired into `flow_start.py` only. vara's register-then-rebuild impl correction is verified real and correct: a matched QUARANTINED bundled Skill is DENY'd out of the plan on the FIRST `maps flow start` call. The 3 folded pr-197 nits are correct. The new `SKILL_CATALOG_FAILED` failure mode is contained; an absent skills dir is a byte-identical no-op. All 5 mutations against the refusal decision + `_catalog_key` are caught. Diff in-bounds; no schema/status/body-load change.

## Method

Own detached worktree at PR #200 head `cdd9fe84a1a29107081c14c8c276a251a63d3459`
(base `24e0139` = PR #197; reviewed content as-is, coordinator rebased to
`0ad2f0c` onto current `origin/main` for merge — clean rebase, no conflicts,
code identical). `git fetch origin` first. Every callsite re-verified at HEAD
(rule 14). Source of truth: the merged #197 design note (as edited by this PR) +
`work/reviews/pr-197-review-evidence.md`.

## 1. Slice matches the note (item 2)

`runtime/skills/catalog.py::build_project_skill_catalog(repo_root, store, *,
now=None)` — one `SkillCatalogSource(source_id="bundled",
root=Path(repo_root)/".claude"/"skills", kind=BUNDLED)`, no config key, no
multi-source list, no third-party sources. Exported from
`runtime/skills/__init__.py`. Wired into `runtime/flow_start.py` step 2 only.

- `runtime/cli.py` NOT in the diff; `/usr/bin/grep skill_catalog runtime/cli.py`
  → no hit. **`maps context` is untouched.**
- `runtime/context_builder.py` NOT in the diff. `build_context_plan` already
  carried the `skill_catalog=None` param (PR #192); its body/signature are
  unchanged — `flow_start` now passes the arg, that is the only change.
  **`build_context_plan` is untouched.**

## 2. Impl correction verified — refusal fires on the FIRST call (item 3)

vara changed both the note snippet and the impl from store-first to
register-then-rebuild:

```python
register_skill_catalog(build_skill_catalog([source]), store, now=now)
return build_skill_catalog([source], store=store)
```

- **(a) the bug was real.** The note's original snippet
  (`catalog = build_skill_catalog([source], store=store); register_skill_catalog(catalog, …); return catalog`)
  reads `store.get_skill_lifecycle_state(catalog_key)` for every entry *before*
  `register_skill_catalog` records any subject, so on a first-ever
  `maps flow start` every `lifecycle_state` comes back `None` → `OBSERVATION` →
  WITHHOLD (not DENY). The QUARANTINED subject is only created by the trailing
  `register_skill_catalog`. So the refusal would not fire until the *second*
  flow-start call. **Mutation M-a (reverting to store-first) fails
  `test_flow_start_drops_a_matched_quarantined_bundled_skill`** — confirms the
  deferral bug.
- **(b) vara's fix makes it DENY on the first call.**
  `test_flow_start_drops_a_matched_quarantined_bundled_skill` performs exactly
  one `flow_start(...)` call and asserts the QUARANTINED Skill is absent from
  `plan["skills"]`, `coverage["memory_trust_gate_denied"] >= 1`, and the durable
  subject really recorded `QUARANTINED`. The test passes at HEAD. Traced:
  register runs first → QUARANTINED subject exists → rebuild reads it →
  `_select_skills` → `admit_memory_evidence` → DENY → `continue`.
- **(c) the note text was corrected.** The note diff updates the §(b) snippet
  (with a "(Impl correction, PR after #197: …)" comment) and smallest-slice
  item 2 to match. `_ADMISSION_TABLE` §(c) "ACTIVE → LOAD" imprecision also
  fixed to "WITHHOLD in practice".

## 3. First real refusal — metadata only, no body (item 4)

`_select_skills` (`context_builder.py:328+`) builds a metadata dict per admitted
entry and **never calls `load_skill` / `load_catalog_skill`** — no Skill
body/procedure text enters the plan.
`test_flow_start_drops_a_matched_quarantined_bundled_skill` asserts `"body"` and
`"procedure"` are absent from every `plan["skills"]` item. No `budget_class`
semantics changed — the DENY path is the pre-existing `admit_memory_evidence`
output; this PR touches neither `_ADMISSION_TABLE` nor the budget-class mapping.

## 4. Three folded pr-197 nits (item 5)

- **(a) `_catalog_key` format pinned by a test.** Now covered by
  `CatalogKeyFormatTests` in `test_skills_catalog.py`:
  `test_catalog_key_exact_format_is_pinned` asserts the full string
  `f"{source_id}:{skill_id}@sha256:{content_sha256}"`;
  `test_catalog_key_orders_source_id_before_skill_id` asserts ordering + `:`
  count. **Mutations M-c (id-order swap) and M-d (`:`→`/` separator) are both
  caught** — previously-surviving mutations now die.
- **(b) `memory_trust_gate` comment reworded.**
  `runtime/policy/memory_trust_gate.py:45-53` — comment-only change; updates the
  stale "`lifecycle_state` is `None` until a durable store is wired" text. No
  code.
- **(c) note "(c) ACTIVE → LOAD" imprecision.** Fixed in the note diff.

## 5. New failure mode — contained + correctly labelled (item 6)

`flow_start` wraps `build_project_skill_catalog` in its own `try` catching
`(SkillCatalogError, SkillParseError)` → `_failed("skills",
MutationResult(False, "SKILL_CATALOG_FAILED", str(exc)))` — a **dedicated step**
distinct from the `context` step's `ValueError` → `INVALID_REPO_ROOT`, so a
malformed `.claude/skills/` is reported as a skills-catalog failure, not
mislabelled or swallowed. Contained.

- **Absent `.claude/skills/` is a clean no-op.** `discover_skills` returns `()`
  for a missing root → empty catalog → `register_skill_catalog` no-ops →
  `_select_skills` iterates zero entries → `plan["skills"] == []`.
  `test_flow_start_without_a_skills_dir_is_unchanged` asserts `skills == []` and
  `list_skill_lifecycle_subjects() == []` (zero writes). Byte-identical to the
  pre-slice flow.

## 6. Diff-in-bounds + no status flip (item 7)

Changed: `runtime/skills/catalog.py` (+`build_project_skill_catalog` only),
`runtime/skills/__init__.py` (export), `runtime/flow_start.py` (wiring + `try`),
`runtime/policy/memory_trust_gate.py` (comment only), `tests/test_flow_start.py`,
`tests/test_skills_catalog.py`, the design note,
`work/roadmaps/CAPABILITY_CHECKLIST.md` (6.10 + SEC4 evidence text).

- **No `runtime/state/schema.sql`.** Not in the diff.
- **No `runtime/context_builder.py` / `runtime/cli.py`** — `build_context_plan`
  / `maps context` untouched.
- **No `record_skill_lifecycle_transition` caller, no operator-identity store,
  no Skill-body load, no `budget_class` change.**
- **No status flip:** the SEC4 row and the 6.10 row each keep `| IN PROGRESS |`;
  the only change is appended evidence text.

## 7. Mutation testing — 5/5 CAUGHT

| # | Mutation | Test | Result |
|---|---|---|---|
| M-a | register-then-rebuild reverted to store-first | `tests.test_flow_start` | **CAUGHT** — FAILED (failures=1); QUARANTINED refusal deferred to the 2nd call |
| M-b | `SkillLifecycleState.QUARANTINED` → `MemoryTrustClass.REVIEWED_GUIDANCE` (out of the DENY class) | `tests.test_flow_start` | **CAUGHT** — FAILED (failures=1) |
| M-c | `_catalog_key`: `f"{source_id}:{skill_id}"` → `f"{skill_id}:{source_id}"` | `tests.test_skills_catalog` | **CAUGHT** — FAILED (failures=2) |
| M-d | `_catalog_key`: separator `:` → `/` | `tests.test_skills_catalog` | **CAUGHT** — FAILED (failures=2) |
| M-e | drop `if decision.admission is MemoryAdmission.DENY: continue` from `_select_skills` | `tests.test_flow_start` | **CAUGHT** — FAILED (failures=1) |

## 8. Suite + smoke

- `python3 -m runtime.smoke` → exit 0.
- `python3 -m unittest`: `tests.test_skills_catalog` 18, `tests.test_skill_lifecycle` 14,
  `tests.test_context_builder` 21, `tests.test_flow_start` 9 — all pass.

## Verdict

APPROVE. No CHANGES REQUESTED. Slice matches the note; the register-then-rebuild
correction is verified real and the QUARANTINED refusal fires on the first
`maps flow start` call; the 3 pr-197 nits are folded correctly; the
`SKILL_CATALOG_FAILED` failure mode is contained and an absent skills dir is a
byte-identical no-op; 5/5 mutations caught; diff in-bounds with no schema, no
status flip, no Skill-body load.
