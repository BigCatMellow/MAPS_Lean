# Rule-20 safeguard — invariant-describing prose drift (design)

**STATUS: DESIGN ONLY. Changes no runtime code, no schema, no checklist status.**
Phase 1 scoping — do not implement until this note lands and the coordinator
confirms the safeguard.

CLAUDE.md **rule 20**: a failure that repeats gets a *mechanical* countermeasure,
not another instruction. This pattern has now hit **twice**. Rule 13: bounded
first — two instances (one already self-catching) justify one small safeguard,
not a static-analysis framework.

All facts re-verified against `origin/main` `dbd786c` (rule 14).

---

## 1. The pattern and its two instances

**Pattern:** code changes; a human-readable claim about what that code
*guarantees* — living somewhere other than right next to the change — goes
stale; the independent review does not catch it because the prose is far from
the diff.

### Instance 1 — `coverage["memory_trust_gate_note"]` (PR #225, uncaught)

`runtime/context_builder.py::_select_skills` (PR #225) added a
`SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE` DENY (lines ~398–406) that `continue`s
**before** `admit_memory_evidence()` is called, recording into the shared
`memory_trust_tally`. The `coverage["memory_trust_gate_note"]` string 230+ lines
away (lines 633–641) still reads:

> "**every** memory-like item passed `admit_memory_evidence()`; its
> **MemoryTrustClass alone** decides bucket membership … Denied items are …
> counted here"

— now false: a capability-DENY'd Skill is counted in `memory_trust_gate_denied`
/ `memory_trust_gate_reasons` without ever reaching `admit_memory_evidence()`.
nava's #225 review verified the DENY placement and ran 8/8 mutations on the
logic, but did not re-read a coverage note in a different function.
**Nothing caught this** — surfaced by trajectory check #14 (§2).

### Instance 2 — `test_context_builder_never_loads_skill_bodies` (PR #221, caught by CI)

A `NonGoalTests` assertion `self.assertNotIn("load_catalog_skill(",
context_builder_source)` went stale the moment PR #221 added that exact call.
**CI caught it** (the test failed); the follow-up commit renamed + rewrote it.
The gap was review-side — the `tests/` grep sweep for now-obsolete assertions
was incomplete (memory `feedback_review_test_set_too_narrow`, which nava updated
with this 2nd instance).

### What the two share, and where they differ

Both: a claim-about-code far from the code, obsoleted by a `_select_skills`
change. **Different in one decisive way:** instance 2's claim was a **test
assertion**, so obsoleting it **broke CI automatically**. Instance 1's claim was
a **plain string inside runtime code**, pinned by **nothing**.

---

## 2. What is already covered

| Prose class | Example | Covered by |
|---|---|---|
| "no production caller" docstrings | `record_skill_lifecycle_transition` | `scripts/check_stale_no_caller_docstrings.py` + `review-evidence.yml` (memory `feedback_stale_no_production_caller_docstrings`, RESOLVED) |
| source-substring `NonGoal` test assertions | `assertNotIn("load_catalog_skill(", …)` | **the test itself** — obsoleting the invariant fails the assertion (instance 2 proved this works). Residual gap is review-sweep completeness, a checklist item not a CI script. |
| `CAPABILITY_CHECKLIST.md` evidence clauses naming `runtime/` files | "no capability-declaration manifest" (stale after #219, fixed #13) | **nothing** — memory `feedback_checklist_edit_repeatedly_skipped` records this as an **open gap**. Out of scope here (see §6). |
| **self-describing prose STRINGS inside `runtime/` code** (coverage notes, behavior-enumerating docstrings) | `coverage["memory_trust_gate_note"]` | **NOTHING** — this is instance 1's class and the only genuinely-uncovered one |

`runtime/context_builder.py`'s `coverage` dict carries **4** such strings —
`note`, `budget_classification_note`, `memory_trust_classification_note`,
`memory_trust_gate_note` (lines 607, 613, 622, 633) — and
`/usr/bin/grep -n "_note\|memory_trust_gate_note" tests/test_context_builder.py
tests/test_memory_trust_gate.py` → **zero test assertions reference any of
them.** All 4 are unpinned; `memory_trust_gate_note` is merely the one that
actually drifted.

---

## 3. The chosen safeguard

Two parts, both small, both precedent-shaped. Part A is the mechanical catch for
instance 1; Part B is the "will it recur" forcing function.

### Part A — a coverage-note consistency test (the mechanical safeguard)

`tests/test_context_builder.py` gains a test that builds a plan **exercising
every admission path a note describes**, then asserts each note string is
consistent with the `coverage` dict that same plan produced. Concretely for
`memory_trust_gate_note`:

- build a plan where one matched Skill is DENY'd by the **capability**
  intersection (`process-stop` declared, `destructive_action` false) and another
  is DENY'd / WITHHELD by the **trust** gate;
- assert: if `coverage["memory_trust_gate_reasons"]` contains any key that is
  **not** a `MemoryAdmission`/`MemoryTrustClass`-derived code (i.e. the SEC4
  `SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE`), then
  `coverage["memory_trust_gate_note"]` must **not** assert "every memory-like
  item passed `admit_memory_evidence()`" or "MemoryTrustClass alone decides".
- one assertion per note key, each checking the claim it can actually verify
  against a built plan (the other three notes get lighter checks — e.g.
  `note`'s "does not search" ↔ `coverage["semantic_retrieval_used"] is False and
  coverage["repository_scan_used"] is False`; `budget_classification_note`'s "no
  new retrieval mechanism" ↔ same flags).

This is a **test** (the precedent form), **co-located** in the module's own test
file, and **fails CI** the moment a `_select_skills` (or coverage-assembly)
change makes a note lie. It directly catches instance 1's failure and would have
failed on PR #225.

**Scope note:** deliberately `context_builder.py`-only. Rule 13 — this is the
one file the pattern has bitten twice (both instances are `_select_skills`
prose). Widening to "all `runtime/` self-describing strings" now is the
over-build the STOP condition warns against.

### Part B — `scripts/check_coverage_note_pins.py` (optional forcing function)

A small CI check in the `check_stale_no_caller_docstrings.py` mould (~50 lines,
AST):

1. Locate the `coverage` dict literal returned by
   `runtime/context_builder.py::build_context_plan` (AST: the `dict` value of
   the `"coverage"` key in the function's `return`).
2. Collect every string-valued key whose name is `note` or ends `_note`.
3. **Fail** if any such key name does not appear as a string literal somewhere
   in `tests/test_context_builder.py` or `tests/test_memory_trust_gate.py`
   (i.e. "this note is referenced by at least one test").
4. Escape hatch: `# noqa: coverage-note-pin` on the note's line.

Wired as a third step in `.github/workflows/review-evidence.yml` (alongside
`check_stale_no_caller_docstrings.py`). It does **not** validate a note's
*content* (that is option (a) from the dispatch — brittle golden-string
matching, explicitly rejected). It enforces the weaker but robust invariant:
*every self-describing coverage note has a test that would break if the note
became a lie* — which is exactly what was missing for `memory_trust_gate_note`.

### Recommendation

Ship **A + B as one small PR**. A is the catch; B is cheap insurance that the
next note added to `coverage` cannot be born unpinned. If a reviewer judges A
sufficient, B can be dropped — but B is the part that makes this *mechanical*
rather than "remember to test your notes".

---

## 4. Slice — impl surface (Phase 2, NOT this note)

### MAY touch
- `tests/test_context_builder.py` — the Part A consistency test (+ a helper to
  build the multi-DENY plan; may reuse `test_skill_capability_manifest.py`'s
  fixtures).
- `scripts/check_coverage_note_pins.py` (new, Part B).
- `.github/workflows/review-evidence.yml` — one `run:` step for Part B.
- `tests/test_check_coverage_note_pins.py` (new) — planted-unpinned-note fails,
  pinned passes, `noqa` suppresses, repo tree is clean.
- `work/roadmaps/CAPABILITY_CHECKLIST.md` — **only if** a reviewer wants a
  one-line mention under a process/tooling row; no status flip. (Likely no
  checklist edit — this is a CI-tooling safeguard, not a capability.)

### MUST NOT
- validate coverage-note *content* against a golden string (dispatch candidate
  (a), rejected — brittle);
- extend the check to `runtime/` files beyond `context_builder.py` (rule 13);
- add a static-analysis pass / new CI infrastructure beyond a script + one yaml
  step (STOP condition);
- touch `runtime/context_builder.py`'s coverage notes themselves — the
  `memory_trust_gate_note` fix is a **separate** PR (rozo dispatched it); this
  safeguard PR should *land after or alongside* it, and Part A's assertion is
  written against the **fixed** note (if this PR races ahead, Part A's
  `memory_trust_gate_note` assertion is `xfail`/skipped with a `# TODO(fix PR)`
  until the fix lands — flag to coordinator);
- change `_select_skills` / `admit_memory_evidence` / the SEC4 intersection.

### Acceptance
1. A consistency test in `tests/test_context_builder.py` that fails on a plan
   whose `memory_trust_gate_reasons` contains a non-trust-class reason while the
   note claims "every … passed `admit_memory_evidence()`" — i.e. it would have
   failed PR #225.
2. (Part B) `check_coverage_note_pins.py` fails when a `*_note` key in
   `build_context_plan`'s `coverage` is not referenced by any
   `test_context_builder.py` / `test_memory_trust_gate.py` string literal;
   `# noqa: coverage-note-pin` suppresses; wired into `review-evidence.yml`.
3. `tests/test_check_coverage_note_pins.py` covers planted-fail / pass / noqa /
   clean-tree.
4. `python3 -m runtime.smoke` exit 0; `python3 scripts/check_coverage_note_pins.py`
   exit 0 on the current tree (after the note fix lands).
5. No checklist status flip.

### Verification
One blocking foreground `python3 -m unittest tests.test_context_builder
tests.test_check_coverage_note_pins tests.test_skill_capability_manifest`.
`python3 -m runtime.smoke` exit 0. `python3 scripts/check_coverage_note_pins.py`
exit 0. `git diff --stat origin/main` = only the MAY-touch files.

---

## 5. Out of scope

- **Instance 2's class (source-substring `NonGoal` assertions)** — already
  self-catching (the assertion fails CI). The residual is review-sweep
  completeness, addressed by memory `feedback_review_test_set_too_narrow` (a
  review-process note), not a CI script. A `scripts/list_nongoal_source_assertions.py`
  "here are the assertions a PR touching file X might obsolete" helper is
  *possible* but is a review aid, not a safeguard — defer unless it recurs.
- **Docstrings elsewhere in `runtime/` that enumerate callers/behavior** — not
  yet a repeat offender beyond the "no production caller" class already covered.
  Rule 13: wait for evidence.
- **Behavior-content validation** of note strings (golden matching) — brittle,
  rejected.

---

## 6. Does this close `feedback_checklist_edit_repeatedly_skipped`? **No — separate.**

That gap is: `CAPABILITY_CHECKLIST.md` **evidence clauses** (markdown, not
runtime code) that name `runtime/` files go stale when those files change
(3 PRs in one arc shipped code without updating the checklist; #13 found a 4th
stale clause). Closing it needs a **different** check: diff a PR's `runtime/`
changes, find checklist rows whose evidence text names the changed files,
require a checklist edit or a reviewer ack in the PR. Trajectory check #13
called that "non-trivial". It is a distinct artifact (markdown vs. code prose),
a distinct trigger (checklist-names-file vs. code-describes-itself), and a
distinct check. **It stays open and separate.** This note's safeguard is
`context_builder.py` coverage-note strings only.

(A future unification — one `scripts/check_prose_drift.py` covering both
docstring-callers, coverage-notes, and checklist-clauses — is conceivable once
each has independently earned its check, but building it now, for 2+1
half-covered instances, is the over-build rule 13 forbids.)

---

## 7. STOP-condition check (dispatch)

- *The only real safeguard is a broad static-analysis pass?* — **No.** Part A is
  one test; Part B is a ~50-line AST script scoped to one dict in one file.
- *Needs new CI infrastructure beyond a script + yaml step?* — **No.** Part B is
  literally a third `run:` line in the existing `review-evidence.yml`, same as
  `check_stale_no_caller_docstrings.py`.

No STOP condition triggered. The safeguard (§3) is dispatchable.

---

## Resume prompt

You are implementing the **coverage-note drift safeguard** for MAPS_Lean —
Phase 2 of `work/notes/2026-09-01-invariant-prose-drift-safeguard-design.md`
§3/§4. Worktree off `origin/main`; `git fetch origin main` first; re-verify at
your HEAD (rule 14).

Source of truth: this note §3/§4, `scripts/check_stale_no_caller_docstrings.py`
(the precedent — script shape, `noqa` hatch, `review-evidence.yml` wiring),
`runtime/context_builder.py::build_context_plan` (the `coverage` dict, lines
~601–642), `tests/test_context_builder.py`, `tests/test_skill_capability_manifest.py`
(fixtures for a capability-DENY plan).

**Order:** land after / alongside the separate `memory_trust_gate_note` fix PR
(rozo's). If that PR has not merged, write Part A's `memory_trust_gate_note`
assertion but mark it `@unittest.skip("pending memory_trust_gate_note fix PR")`
with a TODO and flag the coordinator.

Implement §4: (A) a `tests/test_context_builder.py` consistency test — build a
plan with a capability-DENY'd Skill and a trust-gate-DENY'd/WITHHELD Skill,
assert each `coverage` `*_note` string is consistent with the `coverage` dict
that plan produced (esp: a non-trust reason in `memory_trust_gate_reasons` ⇒ the
note must not claim "every … passed `admit_memory_evidence()`"). (B)
`scripts/check_coverage_note_pins.py` — AST-locate `build_context_plan`'s
returned `coverage` dict, fail if any `note`/`*_note` string key is not
referenced by a string literal in `test_context_builder.py` /
`test_memory_trust_gate.py`; `# noqa: coverage-note-pin` hatch; wire a third
`run:` step into `.github/workflows/review-evidence.yml`. (C)
`tests/test_check_coverage_note_pins.py` — planted-fail / pass / noqa /
clean-tree. No `runtime/` change; no checklist status flip.

MUST NOT: validate note *content* against a golden string; extend beyond
`context_builder.py`; add CI infra beyond the one yaml step; touch the coverage
notes themselves or `_select_skills` / `admit_memory_evidence` / the SEC4
intersection.

Tests: one blocking foreground `python3 -m unittest tests.test_context_builder
tests.test_check_coverage_note_pins tests.test_skill_capability_manifest`.
`python3 -m runtime.smoke` exit 0. `python3 scripts/check_coverage_note_pins.py`
exit 0. Push before any full-suite run; rely on CI.

PR into `main` (never push). Do NOT spawn your own reviewer — ping the
coordinator with the PR number. Independent review; reviewer commits the
evidence file. No self-merge.

STOP + flag the coordinator if: Part B's AST cannot reliably locate the
`coverage` dict without fragile assumptions; or Part A's consistency assertions
require re-deriving `admit_memory_evidence`'s logic in the test (they should
only need to read the built `coverage` dict).
