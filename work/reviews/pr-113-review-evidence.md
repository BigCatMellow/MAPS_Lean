---
reviewer: SENTINEL
head_sha: c1475756521d75006b90a025160098a9d57ef0fb
base: main (origin/main at review time, merge-base 4f481826225eb4e0db0ee067d4c275eafc4cdebb)
rebase_note: original review was at code head 8fd683dfb5cde1822f832f90616b0e739acb2100; head_sha updated to merge commit c1475756521d75006b90a025160098a9d57ef0fb (merges origin/main to bring the branch up to date after PR #112 merged) because merge commits are never walked past by the review-evidence check. git diff bf1a125 c1475756 --stat for every file this review covers (runtime/skills/lifecycle.py, runtime/skills/__init__.py, tests/test_skill_lifecycle.py, work/tasks/skill-trust-lifecycle-wave11.md) is empty -- byte-identical, independently confirmed.
independent: true
summary: APPROVE (CLEAN). Independently reviewed PR #113 at exact head 8fd683dfb5cde1822f832f90616b0e739acb2100 against origin/main in an isolated worktree (/tmp/pr113-review-worktree, never touching the shared checkout). Diff is exactly the 4 files claimed -- runtime/skills/lifecycle.py (new, +161), runtime/skills/__init__.py (+10, additive-only), tests/test_skill_lifecycle.py (new, +184), work/tasks/skill-trust-lifecycle-wave11.md (new, +149); `git diff origin/main...HEAD --stat` shows 4 files changed, 504 insertions(+), 0 deletions -- and I separately confirmed `git diff origin/main...HEAD -- runtime/skills/gate.py runtime/skills/catalog.py runtime/context_builder.py runtime/state/schema.sql | wc -l` returns 0, so none of the four named sensitive files are touched. No schema/persistence change anywhere in the diff.
verdict: CLEAN, no changes required
---

## 1. File-list / diff-boundary verification

`git diff origin/main...HEAD --stat` (worktree checked out at exact head `8fd683dfb5cde1822f832f90616b0e739acb2100`):

```
 runtime/skills/__init__.py                 |  10 ++
 runtime/skills/lifecycle.py                | 161 +++++++++++++++++++++++++
 tests/test_skill_lifecycle.py              | 184 +++++++++++++++++++++++++++++
 work/tasks/skill-trust-lifecycle-wave11.md | 149 +++++++++++++++++++++++
 4 files changed, 504 insertions(+)
```

Note: `git diff main...HEAD` (local stale `main`) initially showed extra unrelated files (playbook/, other work/reviews/*.md, wave8/wave9 task docs) because the local `main` ref in the worktree's origin was behind actual `origin/main` by a few merged PRs (#110, #111). Re-fetched `origin main` and diffed against `origin/main` directly, which resolved to the exact 4-file list above with zero deletions -- matches the PR's claimed scope exactly.

Explicitly confirmed the four named "must not touch" files have zero diff lines:
```
git diff origin/main...HEAD -- runtime/skills/gate.py runtime/skills/catalog.py \
  runtime/context_builder.py runtime/state/schema.sql | wc -l
0
```

`runtime/skills/__init__.py` diff read in full: two additive hunks only -- a new `from .lifecycle import (...)` block and 4 new names (`SkillLifecycleError`, `SkillLifecycleState`, `initial_transition_from_gate_report`, `transition`) appended into `__all__`. No existing line removed or reordered.

## 2. `runtime/skills/lifecycle.py` -- transition graph, read and independently exercised

Read the file in full (161 lines). The real transition table, as encoded in code (not docstring):

```python
_ALLOWED_TRANSITIONS = {
    DISCOVERED: {VALIDATED, QUARANTINED},
    VALIDATED:  {APPROVED},
    QUARANTINED:{APPROVED, RETIRED},
    APPROVED:   {ACTIVE},
    ACTIVE:     {SUPERSEDED, RETIRED},
    SUPERSEDED: {},
    RETIRED:    {},
}
_ACTOR_REQUIRED_TRANSITIONS = {(VALIDATED, APPROVED), (QUARANTINED, APPROVED)}
```

`transition()` first type-checks both arguments are real `SkillLifecycleState` enum members (rejects strings -- verified with `transition("DISCOVERED", S.VALIDATED)`, raises), looks up `target` in `_ALLOWED_TRANSITIONS[current]` and raises `SkillLifecycleError` if absent, then separately checks `(current, target) in _ACTOR_REQUIRED_TRANSITIONS` and raises if `actor is None or not actor.strip()`. This is exactly two independent gates, both must pass.

Ran the following directly against this exact head (not trusting the docstring):

- `transition(S.DISCOVERED, S.APPROVED, actor="bob")` -> raised `SkillLifecycleError: illegal Skill lifecycle transition: DISCOVERED -> APPROVED`. Confirmed.
- `transition(S.DISCOVERED, S.ACTIVE, actor="bob")` -> raised, same pattern. Confirmed.
- `transition(S.VALIDATED, S.APPROVED, actor=None/""/"   ")` -> all three raised `... requires a non-empty actor`. `actor="real-operator"` succeeded, returned `APPROVED`.
- `transition(S.QUARANTINED, S.APPROVED, actor=None/"")` -> both raised the same way; `actor="real-operator"` succeeded.
- `transition(S.APPROVED, S.ACTIVE)` (no actor) succeeded -- confirmed no actor requirement on this edge.
- `transition(S.QUARANTINED, S.RETIRED)` (no actor) succeeded -- confirmed no actor requirement on this edge.
- Terminal-state exhaustive check: for each of `SUPERSEDED` and `RETIRED`, attempted a transition to **all 6 other states** (12 calls total) with a valid actor supplied -- every single one raised `SkillLifecycleError: illegal Skill lifecycle transition: ...`. Zero outgoing edges confirmed by direct execution, not by reading the empty-frozenset literal alone.

**Core security property -- no path to `ACTIVE`/`APPROVED` bypassing `VALIDATED`/`QUARANTINED`:** ran a BFS over `_ALLOWED_TRANSITIONS` starting at `DISCOVERED`, and separately asserted no edge `(DISCOVERED, target)` exists where `target in {ACTIVE, APPROVED}`. Result: `bypass_found: False`. The only two first-hop edges out of `DISCOVERED` are `VALIDATED` and `QUARANTINED` (verified directly from the dict, not inferred), and `ACTIVE` is reachable in the graph only via `APPROVED -> ACTIVE`, and `APPROVED` is reachable only via `VALIDATED -> APPROVED` or `QUARANTINED -> APPROVED` (both actor-gated). There is no edge that reaches `APPROVED` or `ACTIVE` from any state other than through this chain. Quarantine review cannot be skipped -- confirmed structurally and by execution.

## 3. `initial_transition_from_gate_report` -- real-class check

`from .gate import SkillGateDisposition, SkillGateReport` at the top of `lifecycle.py` is a genuine relative import; confirmed no shadow/redefinition anywhere in the file (grepped the file's full source for `import`, only two import lines exist, no local `class SkillGateReport`/`class SkillGateDisposition`).

Manually constructed three `SkillGateReport` instances (not via `assess_skill`, to rule out any coupling to the test-file's own construction path) directly using the real dataclass from `runtime/skills/gate.py`:

```python
from runtime.skills.gate import SkillGateReport, SkillGateDisposition
mk(SkillGateDisposition.CLEAR)            -> initial_transition_from_gate_report -> VALIDATED
mk(SkillGateDisposition.REVIEW_REQUIRED)  -> initial_transition_from_gate_report -> VALIDATED
mk(SkillGateDisposition.QUARANTINE)       -> initial_transition_from_gate_report -> QUARANTINED
```
`type(r_clear).__module__ == "runtime.skills.gate"`, `__qualname__ == "SkillGateReport"` -- confirmed it is the real class, not a look-alike. All three assertions passed. Both non-`QUARANTINE` dispositions map identically to `VALIDATED` as claimed (not accidentally split).

## 4. `tests/test_skill_lifecycle.py` -- exhaustiveness check

Read in full (184 lines). This is genuinely exhaustive, not a couple of spot examples:

- `LEGAL_EDGES` is a hand-written 8-edge set, independently authored (comment explicitly notes it does *not* import `_ALLOWED_TRANSITIONS` from the module, to avoid a tautological test).
- `test_every_legal_transition_succeeds` iterates all 8 legal edges.
- `test_every_illegal_transition_raises` iterates the full 7x7=49 state-pair Cartesian product and asserts every pair NOT in `LEGAL_EDGES` raises -- this is the exhaustive negative-space check, covering all 41 illegal pairs including both `DISCOVERED->APPROVED` and `DISCOVERED->ACTIVE`.
- `test_terminal_states_have_zero_outgoing_transitions` iterates both terminal states against all 7 states as target (14 subTests) and asserts every one raises.
- Separate explicit tests for the actor-empty/None/whitespace rejection on both `VALIDATED->APPROVED` and `QUARANTINED->APPROVED`, and separate explicit tests that `APPROVED->ACTIVE` and `QUARANTINED->RETIRED` succeed with no actor.
- `test_transition_rejects_non_enum_values` covers the raw-string-input rejection path.
- `InitialTransitionFromGateReportTests` constructs real Skills on disk via `discover_skills`/`assess_skill` (not stubbed `SkillGateReport`s) for `CLEAR`, `REVIEW_REQUIRED`, and `QUARANTINE` dispositions and asserts the correct `initial_transition_from_gate_report` mapping for each -- this is a stronger test than my own manual construction in step 3, since it exercises the real gate-scanning path end to end.

Ran `python3 -m unittest tests.test_skill_lifecycle -v` at this exact head: **14 tests, OK**, zero failures.

## 5. Test-suite runs (all at exact head `8fd683dfb5cde1822f832f90616b0e739acb2100`, in the isolated worktree)

- `python3 -m unittest tests.test_skill_lifecycle tests.test_skills_quality_gate tests.test_skills_quality_gate_metadata tests.test_skills_catalog -v` -> **Ran 42 tests, OK**. Matches PR's claimed "42 tests, OK" exactly.
- Full suite, run as a backgrounded blocking command and waited on to completion (no polling of partial output beyond confirming progress): `python3 -m unittest discover -s tests -v` -> **Ran 639 tests in 634.696s, OK (skipped=6)**. Matches the PR's claimed "639 tests, OK (skipped=6)" exactly, exit code 0.

## 6. Acceptance-criteria cross-check (`work/tasks/skill-trust-lifecycle-wave11.md`)

All 6 checked boxes map to verified facts:
- "7 specified members" -- confirmed by reading the `Enum` class body (`DISCOVERED, VALIDATED, QUARANTINED, APPROVED, ACTIVE, SUPERSEDED, RETIRED`, exactly 7, no extras).
- The 8 named legal transitions "succeed via `transition()`" -- confirmed by direct execution in step 2 plus `test_every_legal_transition_succeeds`.
- "Every other pair raises... including `DISCOVERED->APPROVED` and `DISCOVERED->ACTIVE`" -- confirmed by direct execution and by `test_every_illegal_transition_raises`'s 49-pair sweep.
- Actor-rejection on both approval edges for `None`/`""`/whitespace -- confirmed by direct execution and by the two dedicated tests.
- Terminal-state exhaustive zero-outgoing-edges claim -- confirmed by direct 12-call execution (all 6 non-self targets x 2 terminal states) and by `test_terminal_states_have_zero_outgoing_transitions`.
- `initial_transition_from_gate_report` mapping via `discover_skills`/`assess_skill` (not stubbed) for all three dispositions -- confirmed by reading `InitialTransitionFromGateReportTests` and by running it (3/3 pass, part of the 14 in test_skill_lifecycle).
- The two required-command boxes ("targeted 42-test run" and "full suite") both pass as re-run above.
- The one remaining unchecked box ("Independent review remains required before completion") is exactly this review -- appropriately left unchecked by the PR author since it can't self-certify.

## 7. Authority-widening / overclaim check

Read the module docstring (lines 1-60) and the task doc's "Required semantics" and "Stop / escalate" sections in full. Both are explicit and consistent that:
- This module "owns no persistence, no task/session authority, and no canonical storage."
- The `actor` non-empty check is described as "a structural reminder -- not an authority check" and that verifying `actor` is "a real, authorized operator identity is a separate concern for a future persistence/authority task" (module docstring, lines 122-125) and identically in the task doc ("it performs no real authority/identity check, since no persistence layer exists yet to check against", acceptance-criteria item 4).
- The task doc's "Stop / escalate" section explicitly defers persistence and operator-authority wiring to future tasks and states SEC4 remains only partially complete.

No enforcement or authority is claimed that the code doesn't provide. `transition()` is pure, stateless, in-memory validation logic over an enum; nothing in the diff writes to disk, a database, or any shared state. This is honest scoping, not overclaiming.

## Verdict

**APPROVE (CLEAN).** The diff is exactly the 4 files claimed, purely additive, and does not touch `runtime/state/schema.sql`, `runtime/skills/gate.py`, `runtime/skills/catalog.py`, or `runtime/context_builder.py` (confirmed via `git diff ... | wc -l` == 0 on all four). The core security property -- that quarantine review can never be bypassed en route to `APPROVED`/`ACTIVE` -- holds under direct execution, not just by reading the docstring: `DISCOVERED -> APPROVED` and `DISCOVERED -> ACTIVE` both genuinely raise, both approval edges genuinely require a real non-empty actor and reject `None`/empty/whitespace, both terminal states genuinely reject all 6 possible outgoing targets, and a BFS over the real transition table confirms no bypass path exists. The gate-report mapping uses the real `SkillGateReport`/`SkillGateDisposition` classes from `runtime/skills/gate.py` with no shadowing, and maps `CLEAR`/`REVIEW_REQUIRED` -> `VALIDATED` and `QUARANTINE` -> `QUARANTINED` correctly. The test suite is genuinely exhaustive (full 49-pair Cartesian sweep, full terminal-state sweep, both actor-rejection edges, real gate-scanning integration test), not a handful of spot checks, and a hand-written independent `LEGAL_EDGES` table avoids a tautological self-referential test. Test counts (42 targeted, 639 full-suite with 6 skipped) match the PR's claims exactly when re-run at this exact head. The module makes no authority claims it doesn't back up -- `actor` is honestly documented as a structural reminder only. No bugs, no scope creep, no masked gaps found.
