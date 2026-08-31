# PR #179 review evidence

## Superseded prior review

`SENTINEL-CHATGPT` filed `CHANGES_REQUESTED` at head `826afc90387a8f825b9147a0b121475086f59257`
with four blocking defects, then the author appended a "fixes applied" note. That
disposition is stale. The fields below are the binding review-evidence record for
PR #179 at its current head.

## Fresh independent review

reviewer: FRESH-REVIEWER-CLAUDE-20260830 (independent; did not author PR #179, the SENTINEL review, or the fix commit `fe989da`)
head_sha: fe989da2309af35fce44151807f0f2f85cb801d2
independent: true
summary: APPROVE (content) with two mandatory pre-merge conditions. All four SENTINEL blocking defects are fixed at head fe989da and verified. The AGENTS.md compaction (13,554 -> 9,939 bytes, under the 10,000 guard) preserves every hard invariant, the scope/authorization boundary, the orchestration-operator invariant, helper/tenth-seat routing, and reporting rules; dropped enumerations (retained control-plane list, LangGraph state-invariant sentence) survive in their canonical owners (README.md responsibility table, playbook/CONTROL_PLANE.md, AGENTS.md invariant 9 SUCCESS-gating). Retired docs/WORKFLOW.md and docs/CONTEXT.md are genuinely redundant with TASK_LIFECYCLE.md / templates/task.md / INFORMATION_LIFECYCLE.md / AGENTS.md. The two dangling docs/CONTEXT.md references were repaired (playbook/SIMULATION_DESIGN.md, work/reviews/TASK-005-...). Digital Fungus confirms the after-state numbers exactly (5/5 nav targets reachable, 1 hop, 1688 max added-token proxy) and active_broken_links == 2, both pre-existing and unrelated to this PR (a legacy wikilink and pr-132-review-evidence.md). Targeted doc/route test files pass (19 tests) and exact-head CI "Runtime stack tests" run 33349444137 is green (active tests + LangGraph smoke + security static analysis). MANDATORY BEFORE MERGE: (1) the branch is CONFLICTING/behind main - rebase on main (PR #178) and resolve the single purely-additive conflict in tests/test_documentation_sprawl.py by keeping BOTH the wiki/pilot test block from #178 and the routing/OIG test block from #179, plus both sets of module-level path constants; (2) re-run full CI green on the rebased head. No substantive contradiction with PR #178 (wiki/pilot) was found. Non-blocking nit: task file prose says "Two roadmap/hub targets" while the table and PR body correctly say three went from UNREACHABLE to one-hop.

## Per-defect verification (SENTINEL head 826afc9 -> fixed at fe989da)

1. **Global task-owner invariant restored** - PASS. `AGENTS.md` hard invariant 12:
   "One owner, independent review. Each active task has one accountable owner; no
   owner approves their own substantive work." Also retained in Scope-level
   authorization ("keep independent review genuinely independent") and Verification
   and review. Regression-guarded by
   `test_agents_keeps_single_owner_independent_review_invariant`.

2. **Operational-independence N/A loophole closed** - PASS. `playbook/TASK_LIFECYCLE.md`
   "Gate rules" section adds stable IDs:
   - `OIG-DONE` - triggered gate is part of `DONE` and parent success.
   - `OIG-NA-WHOLE` - whole-gate `N/A` reserved for genuinely non-repeatable / one-off
     work; "Automation being infeasible or disproportionate is **not** a valid
     whole-gate `N/A` reason for otherwise-repeatable work."
   - `OIG-NA-AUTO` - repeatable work keeps the gate `REQUIRED`; only the automation
     component may be `N/A - reason`, and the package "MUST still carry the best
     available manual reproduction instructions ... proportional verification.
     `N/A` never licenses leaving nothing behind or an AI-/session-only dependency."
   `templates/task.md` adds `Operational independence: REQUIRED | N/A - <reason>` and
   `Reproduction package:` fields citing `OIG-NA-WHOLE` / `OIG-NA-AUTO`. `DONE`
   definition updated to cite `OIG-DONE`. Regression-guarded by
   `test_na_escape_hatch_cannot_silently_become_permissive` and
   `test_repeatable_work_requires_operational_independence`.

3. **Regression tests re-anchored on structure, not prose** - PASS.
   `tests/test_documentation_sprawl.py::test_repeatable_work_requires_operational_independence`
   now asserts headings (`## Operational independence gate`, `### Gate rules`,
   `## Hard operating invariants`), rule IDs (`OIG-DONE/OIG-NA-WHOLE/OIG-NA-AUTO`),
   the marked term `**REQUIRED**`, and the `OIG-DONE` citation in the `DONE`
   definition - not full sentences. New completion-semantic tests added
   (`test_na_escape_hatch_cannot_silently_become_permissive`,
   `test_agents_keeps_single_owner_independent_review_invariant`).
   `tests/test_digital_fungus_routes.py` (4 tests) was already structural.

4. **Before -> after route/read-cost evidence present** - PASS. Both the PR body
   ("Before -> after route / read-cost evidence" section) and
   `work/tasks/pilot-information-routing-housekeeping-20260829.md` carry the
   single-analyzer-run comparison table: nav targets reachable 2/5 -> 5/5, max hops
   1 -> 1, max added-token proxy 2112 -> 1688 (-20%), per-target routes, and
   "active broken links 2 -> 2 (unchanged)". Independently reproduced: current
   `python3 tools/digital_fungus.py --root .` reports
   `navigation_targets_reachable: 5`, `max_navigation_route_hops: 1`,
   `max_navigation_route_added_estimated_tokens: 1688`, `active_broken_links: 2`.

## Independent pass findings

- **AGENTS.md compaction semantics** - no material loss. All 10 prior hard
  invariants map forward (1..10 preserved with tightened wording) plus 2 added
  (11 operational independence, 12 owner/review). Scope-level authorization keeps
  every boundary-crossing trigger. Orchestration-operator invariant condensed from
  a 10-item MUST list to a loop diagram + 6 MUSTs; the retained semantics
  (accountability after delegation, bounded helper outputs, auto-continuation,
  retry/reassign, independent review, `SUCCESS` gating) are all present. The old
  "retained control plane is SQLite/LangGraph/RnS/hcom" enumeration moved to the
  README "Core responsibility boundaries" table and `playbook/CONTROL_PLANE.md`
  (canonical owner) - no duplicate-truth violation.
- **AGENTS.md byte guard** - 9,939 / 10,000. New test
  `test_always_read_entry_surfaces_have_explicit_size_budgets` also guards
  README (<=4,000; actual 3,511) and FIRST_RUN (<=3,000; actual ~2,267).
- **Retired docs** - `docs/WORKFLOW.md` content is covered by `TASK_LIFECYCLE.md`,
  `templates/task.md`, and AGENTS.md orchestration (non-overlapping write
  boundaries, integration owner). `docs/CONTEXT.md` content is covered by
  `playbook/INFORMATION_LIFECYCLE.md` (states + compaction + arc-closeout
  question). Retirement is justified; both were islands.
- **Broken links** - the 2 active broken links are
  `migration/legacy-knowledge-source/.../map-real-parameter-calibration-results-2026-07-14.md`
  -> `shared/operator-identities` (legacy wikilink) and
  `work/reviews/pr-132-review-evidence.md` -> truncated markdown link. Both
  pre-date this PR; neither involves the retired docs. `playbook/SOURCE_CATALOG.md`
  still *mentions* `docs/CONTEXT.md` in a legacy-mapping table cell (code-styled,
  not a link) - a pre-existing unlinked mention, not a new broken link; minor
  tidy-up candidate, non-blocking.
- **Digital Fungus changes** - `tools/digital_fungus.py` remains read-only;
  the only filesystem writes are to an explicit `--output-dir`.
- **PR #178 overlap** - #178 (wiki/pilot entry surface, merged to main) and #179
  both touch entry surfaces but do not contradict: #178 adds a wiki/pilot
  onboarding layer that routes to `AGENTS.md`/`FIRST_RUN.md`; #179 compacts those
  targets while keeping every heading/string #178's tests assert. The only
  mechanical collision is additive test methods in
  `tests/test_documentation_sprawl.py` (see mandatory pre-merge condition 1).

## Verification performed

- `python3 -m unittest tests.test_documentation_sprawl tests.test_digital_fungus_routes -v` -> `OK` (19 tests).
- Full suite: exact-head CI is authoritative and green. GitHub Actions "Runtime stack tests"
  workflow, run `33349444137`, job `test`, conclusion `success` on head
  `fe989da2309af35fce44151807f0f2f85cb801d2` - includes "Run active tests", fatal-error
  lint, medium/high security static analysis, dependency consistency, "Run disposable
  smoke with LangGraph", and installer preview. Per the review instruction, exact-head
  CI having fired green means no local full-suite re-run is required; a local
  `unittest discover` was started, confirmed not needed once CI was found, and terminated.
- `python3 tools/digital_fungus.py --root .` -> after-state numbers match PR claims exactly.
- `git merge-tree --write-tree origin/main pr179` -> one conflict, `tests/test_documentation_sprawl.py`, additive-only.
- `gh pr view 179 --json mergeable` -> `CONFLICTING` / `DIRTY` (branch behind main).

## Disposition

APPROVE on content; exact-head CI ("Runtime stack tests" run 33349444137) is green.
Do NOT merge until: (1) rebased on current main with the additive
`tests/test_documentation_sprawl.py` conflict resolved keeping BOTH the #178
wiki/pilot test block and the #179 routing/OIG test block (plus both module-level
path-constant groups), and (2) the "Runtime stack tests" workflow re-run green on
the rebased head.
