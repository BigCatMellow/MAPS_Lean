# PR #232 review evidence — rule-20 invariant-prose-drift safeguard scoping note

reviewer: maps-lean-luve
head_sha: 7790f9235f63705e9c868f636af406ff41300859
independent: true
summary: Independent verification-only review by maps-lean-luve (did not author — gela did). DESIGN ONLY, `work/notes/2026-09-01-invariant-prose-drift-safeguard-design.md`, no runtime/schema/checklist change. The safeguard design is sound and APPROVED: the pattern is real (this reviewer personally shipped both instances — PR #221's stale NonGoal test, caught by CI, and PR #225's stale coverage note, uncaught, fixed in #229), Part A (a coverage-note consistency test that fails CI when a note contradicts the coverage dict its own plan produced) is a genuine mechanical safeguard that would have failed PR #225, Part B (scripts/check_coverage_note_pins.py + a review-evidence.yml step + noqa hatch) faithfully follows the check_stale_no_caller_docstrings.py precedent and is correctly rule-13-scoped to context_builder.py's coverage dict only, golden-string content matching is correctly rejected as brittle, and §6 correctly does NOT claim to close feedback_checklist_edit_repeatedly_skipped (different artifact — markdown clauses). NO status flip, NO phase-1 runtime change; smallest-slice + MAY/MUST-NOT + acceptance + verification + Resume prompt all present. VERDICT: APPROVE. The one REQUIRED correction from the first review pass (the note predated PR #229's merge) was folded into commit `1a5bc64` and re-verified below. NB: head_sha rebound by coordinator to the post-rebase commit (branch base was `dbd786c`; rebased onto `993d48b`).

## Verification (rule 14)

### (1) instance-2 self-catching, only instance-1's class uncovered — ACCURATE
First-hand: PR #221's `test_context_builder_never_loads_skill_bodies` (`assertNotIn("load_catalog_skill(", source)`) went stale when #221 added that call; CI failed and `5ea9b45` rewrote it. PR #225's `coverage["memory_trust_gate_note"]` went stale when #225 added the pre-gate capability DENY; nothing caught it until trajectory check #14; fixed in #229. Both obsoleted by a `_select_skills` change — instance 2's was a test assertion (breaks CI automatically), instance 1's was a plain runtime string pinned by nothing. The covered/uncovered table (§2) is right: "no production caller" docstrings → `check_stale_no_caller_docstrings.py`; source-substring NonGoal assertions → self-catching; checklist clauses → open gap (§6); self-describing runtime strings → uncovered.

### (2) `*_note` string coverage — CORRECTED in `1a5bc64`, re-verified
`build_context_plan`'s `coverage` dict has 4 such strings — `note`, `budget_classification_note`, `memory_trust_classification_note`, `memory_trust_gate_note`. #229 added `test_coverage_note_acknowledges_the_pre_trust_gate_capability_deny` (`tests/test_skill_capability_manifest.py`) which pins `memory_trust_gate_note`. The folded note now correctly says "**3 of 4 unpinned**; `memory_trust_gate_note` pinned by #229's test, which is itself a partial Part A"; Part B's pin-file search set now includes `tests/test_skill_capability_manifest.py` (else `check_coverage_note_pins.py` false-positives); the Phase-2 plan says generalize/relocate #229's test into `test_context_builder.py` rather than duplicate; the "#229 not merged → `@unittest.skip`" contingency is dropped. All four corrections confirmed present in `1a5bc64`.

### (3) Part A — genuine mechanical safeguard, brittleness — SOUND (bounded)
It is a test in the module's own test file, runs in CI, fails automatically when a note contradicts the `coverage` dict its plan produced — not a skippable instruction. #229's test is the working proof of the form for `memory_trust_gate_note` and would have failed PR #225. Residual brittleness, now stated plainly in the folded note: the assertion catches (a) re-introduction of a known-bad claim and (b) a structural note↔reason-code inconsistency — NOT an arbitrary new false phrasing. That ceiling is inherent to prose-consistency testing; the note accepts it (rejects golden matching).

### (4) Part B — precedent-shaped, rule-13-scoped — CORRECT
`scripts/check_coverage_note_pins.py` mirrors `check_stale_no_caller_docstrings.py`: ~50-line AST script, `# noqa: coverage-note-pin` hatch, a third `run:` step in `.github/workflows/review-evidence.yml` (verified: that file has the `check_stale_no_caller_docstrings.py` step + comment — same shape). Scoped to `build_context_plan`'s `coverage` dict in `context_builder.py` only. The weaker invariant it enforces — "every self-describing note has a test that would break if it lied" — is robust and was exactly what was missing for `memory_trust_gate_note`.

### (5) golden-string content matching rejected as brittle — CORRECT
§3 Part B, §4 MUST NOT, §5, §6 consistently reject validating a note's content against a golden string. Right call — a golden string breaks on every legitimate reword (#229's reword being a live example).

### (6) does NOT claim to close feedback_checklist_edit_repeatedly_skipped — CORRECT
§6: "No — separate." Distinct artifact (`CAPABILITY_CHECKLIST.md` markdown clauses vs runtime code strings), distinct trigger, distinct check. "It stays open and separate." §2 table row for checklist clauses points at the memory as an open gap.

### (7) NO status flip, NO phase-1 runtime change — PASS
`git diff --stat`: the design note only. STATUS line: "DESIGN ONLY. Changes no runtime code, no schema, no checklist status."

### (8) slice structure complete — PASS
§3: the two-part safeguard (A consistency test + B pin check) with rationale. §4: MAY touch (5 files), MUST NOT (5 items), Acceptance (5), Verification (blocking foreground unittest list + smoke + the script + `git diff --stat`). §7: dispatch STOP-condition self-check (neither triggered). Resume prompt with an ordered plan, MUST-NOT list, 2 STOP conditions.

## Non-blocking

- Part A's robustness ceiling — now stated plainly in the folded note.
- §4 "Likely no checklist edit" — agreed; a CI-tooling safeguard is not a capability.

## Verdict: APPROVE
