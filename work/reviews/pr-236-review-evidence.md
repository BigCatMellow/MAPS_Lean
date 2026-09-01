# PR #236 review evidence — rule-20 safeguard: context-builder coverage-note drift

reviewer: maps-lean-nava
head_sha: a6acc98631c36f2116db83de31bce38e866dbc95
independent: true
summary: APPROVE — implements exactly design §3/§4: Part A (CoverageNoteConsistencyTests, one test covering all 4 context_builder.py coverage notes, verified via mutation to actually catch the #225-shaped regression) + Part B (check_coverage_note_pins.py, AST-scoped to context_builder.py's coverage dict, wired as a third review-evidence.yml step); #229's test generalized and removed (not duplicated); diff is exactly the 5 MAY-touch files with zero runtime/ or checklist change; 6/6 mutations killed across both parts; targeted suites (58+5) + smoke + the checker itself all green.

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| Acceptance 1 — consistency test would have failed PR #225 | PASS, directly verified. Mutated `runtime/context_builder.py`'s `memory_trust_gate_note` back toward the #225-era phrasing → `CoverageNoteConsistencyTests.test_every_coverage_note_is_consistent_with_its_own_plan` FAILED with `AssertionError: 'reaches the trust gate' not found …`. |
| Acceptance 2 — Part B fails on unpinned note; noqa suppresses; wired into review-evidence.yml | PASS. `scripts/check_coverage_note_pins.py` AST-locates the coverage dict in `build_context_plan`, fails any note not referenced by an exact-subscript key literal in the 3 pin files (`tests/test_context_builder.py`, `tests/test_skill_capability_manifest.py`, `tests/test_check_coverage_note_pins.py`). `# noqa: coverage-note-pin` suppresses. `.github/workflows/review-evidence.yml` gained one `run:` step, third alongside `check_review_evidence.py` and `check_stale_no_caller_docstrings.py`. |
| Acceptance 3 — test_check_coverage_note_pins.py covers planted-fail/pass/noqa/clean-tree | PASS. 5 tests, all present and green. |
| Acceptance 4 — runtime.smoke exit 0; checker exit 0 on current tree | PASS. Both confirmed. |
| Acceptance 5 — #229's test generalized + removed, not duplicated | PASS. `tests/test_skill_capability_manifest.py::test_coverage_note_acknowledges_the_pre_trust_gate_capability_deny` deleted, replaced by a comment; equivalent-or-stronger assertions live in `CoverageNoteConsistencyTests`. |
| Acceptance 6 — no checklist edit, no status flip | PASS. `CAPABILITY_CHECKLIST.md` not touched. |
| MUST NOT — golden-matching, scope beyond context_builder.py, new CI infra, touching notes/_select_skills/admit_memory_evidence/SEC4, duplicating #229's test | PASS on all. `git diff 5909169..HEAD -- runtime/` → 0 lines. |
| Diff scope | PASS. Exactly 5 files: `.github/workflows/review-evidence.yml`, `scripts/check_coverage_note_pins.py` (new), `tests/test_check_coverage_note_pins.py` (new), `tests/test_context_builder.py`, `tests/test_skill_capability_manifest.py`. Matches design §4 MAY-touch exactly. |
| Targeted tests + smoke | PASS. `tests.test_check_coverage_note_pins` 5/5; `tests.test_context_builder` + `tests.test_skill_capability_manifest` combined 58/58; `runtime.smoke` exit 0. |

## Mutation testing — 6/6 killed

| # | Mutation | Result |
|---|----------|--------|
| M1 | `_is_note_key`: drop the bare "note" case | KILLED |
| M2 | invert the pinned check | KILLED |
| M3 | drop the noqa window check | KILLED |
| M4 | `_pinned_keys`: never record a subscript key | KILLED |
| M5 | `_coverage_notes`: never detect a note | KILLED |
| M6 | (Part A) revert `memory_trust_gate_note` toward the exact #225-era over-claim | KILLED |

Worktree restored after each mutation (`git status --porcelain` clean throughout).

## Non-blocking

- Per the session-17 test-contention protocol, the full `tests/` tree is delegated to CI; targeted modules + smoke run foreground here.

## Verdict

APPROVE.
