# PR #237 review evidence — 6.9/S6 slice 2: execution-resource manifest + on-demand loader

Two-part review. The slice-2 implementation (`_execution_resource_manifest`,
`load_skill_resource`, LOAD-branch attach, `SkillDescriptor.resource_sizes`) was
independently reviewed and APPROVED by maps-lean-nava (min-5 mutation, 7/7
killed + 1 non-blocking equivalent mutant; hcom #79366). The later test-only
commit that re-scopes `tests/test_memory_trust_gate.py::NonGoalTests` for the
intentional slice-1→slice-2 boundary move was independently delta-reviewed and
APPROVED by maps-lean-vame (hcom #79679). Both reviewers reproduced the
targeted suites green. Full head_sha below is the rebased branch tip carrying
both commits.

## Part 1 — slice-2 implementation (maps-lean-nava, APPROVE)

- Implements design §3 exactly: manifest attached only in the LOAD branch after
  the body, no resource content ever loaded. `load_skill_resource` is a
  declared-path-only allowlist read with whole-directory hash verification and
  fail-closed drift handling.
- Diff matches the MAY-touch list; no `schema.sql` / `catalog.py` /
  `admit_memory_evidence` / SEC4-intersection change. No checklist status flip
  (6.9 and 6.11 rows stay IN PROGRESS).
- §4 body-ceiling correctly omitted — the design explicitly leaves it an
  optional implementer/coordinator call (§4, §OPERATOR-DECISION).
- Mutation: M1 (drop size key), M2 (only script kind), M3 (attach when empty),
  M4 (swallow build errors), M5 (sizes → empty dict), M6 (disable allowlist
  check), M8 (snapshot path-match → first entry) all KILLED. M7 (drop
  `resource_sizes` from the explicit `SkillChangedError` identity tuple)
  SURVIVED as an equivalent mutant — `_verified_snapshot`'s upstream digest
  check already fails on any byte change; non-blocking, same class as the #231
  `status == "ACTIVE"` equivalent mutant.
- One non-blocking naming deviation: manifest key is `size_bytes`, not the
  design's literal `bytes` — functionally identical, consistently applied,
  arguably safer given the design's emphasis on never conflating manifest
  metadata with resource bytes. No downstream consumer expects the literal
  `bytes` key.
- Targeted suites (`tests.test_skills_format` + `tests.test_skills_catalog` +
  `tests.test_skill_capability_manifest` = 74/74; `tests.test_context_builder`
  = 31/31) + `python3 -m runtime.smoke` (exit 0) green.

Verdict: APPROVE.

## Part 2 — 66e108d NonGoalTests re-scope (maps-lean-vame, APPROVE-DELTA)

- The commit renames the test to `..._loading_is_load_gated_and_never_reads_content`,
  keeps the `load_skill(` / `load_catalog_skill(` / LOAD-gate asserts, flips
  `assertNotIn`→`assertIn` for `script_paths` / `reference_paths` /
  `example_paths` / `asset_paths`, and adds `assertNotIn("load_skill_resource(", text)`.
- Judgment: design-sanctioned scope move, NOT a dropped live non-goal. Slice
  1 (#221) banned those attr names from `context_builder.py` outright; slice
  2's core deliverable IS attaching a manifest built from exactly those attrs
  (verified `_EXECUTION_RESOURCE_KINDS` / `_execution_resource_manifest` /
  LOAD-branch attach in the slice-2 code). The slice-2 design note §3/§3c lists
  those attr names as what `_select_skills` reads and forbids reading resource
  *content*. The non-goal moved from "no path names" to "no content read"; the
  new `load_skill_resource(` ban encodes §3c's MUST-NOT precisely (`load_skill_resource`
  is a real symbol at `runtime/skills/format.py:457`, absent from
  `context_builder.py`).
- Sibling scan for `feedback_stale_slice_boundary_nongoal_test` (this test class
  broke on #221 and #237 — 3rd-occurrence watch): `/usr/bin/grep -rn` for the
  attr names + `load_skill_resource` across `tests/` (excl. this file) hits only
  `tests/test_skills_format.py`, which are positive behavior tests, not
  source-scan boundary asserts. NO 3rd stale sibling. `test_helper_recovery_lineage.py`'s
  `output_paths` assert independently cleared as an unrelated DB-column object.
- Verification (both reviewers, independently reproduced):
  `python3 -m pytest -q tests/test_memory_trust_gate.py tests/test_context_builder.py`
  → 47 passed, 38 subtests passed, exit 0.
- Non-blocking residual: NonGoalTests stays source-substring style; a future
  slice 3 that legitimately calls `load_skill_resource` in `_select_skills` will
  break it again (tracked by `feedback_review_test_set_too_narrow`), not a
  defect in this delta.

Verdict: APPROVE-DELTA.

reviewer: maps-lean-nava (slice-2 impl, min-5 mutation) + maps-lean-vame (66e108d delta-review)
head_sha: 8a842e93e5c91dea37b67e627444a300e0fd980c
independent: true
summary: APPROVE — nava independently reviewed + mutation-tested the slice-2 manifest/loader implementation (7/7 killed, 1 non-blocking equivalent mutant, size_bytes-vs-bytes naming deviation non-blocking); vame independently delta-reviewed commit 66e108d and confirmed the NonGoalTests assertNotIn→assertIn flip is a design-sanctioned slice-1→slice-2 boundary move (manifest is a listing, content-read stays the new non-goal via load_skill_resource) with no 3rd stale sibling test; both reproduced the targeted suites green (47 passed, exit 0).
