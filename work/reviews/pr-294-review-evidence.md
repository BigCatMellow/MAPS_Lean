reviewer: lara
head_sha: 5e8a8c1e7aff25bf1f8bbe3311ff3b7a525da639
independent: true
summary: AGENTS.md merge-authority wording verified against the design note and scripts/opcmd_merge.py; CI test-budget failure (AGENTS.md 12020 > 11200 byte budget) was a real blocker found in Phase 1, fixed by a separate operator-approved commit (5e8a8c1) raising AGENTS_BYTE_BUDGET to 13000, AGENTS.md content itself untouched by that fix; both CI checks now green except review-evidence which fails only for lack of this file.
verdict: APPROVE

## Scope check
`git diff main...HEAD --stat` at final head touches only `AGENTS.md` (20 lines,
+17/-3) and `tests/test_documentation_sprawl.py` (8 lines, +6/-2, budget constant
only). No scope creep.

## Content consistency
Read AGENTS.md lines ~100-175 (surrounding "decides inside authority -> human
only for a true boundary crossing" language, the MAPS_L orchestration operator
invariant, and the rest of the Merge authority section). The new mandatory-gate
wording is a clean fit: it narrows the previously-soft "or an explicitly
designated coordinator seat" clause into a single legitimate non-operator path
(operator batch-designation via the gate's own staleness bound), consistent
with the rest of the document's fail-closed / operator-decides-boundary-
crossings posture. No contradiction found.

## Mechanism cross-check (doc claims vs. scripts/opcmd_merge.py, full 411-line
read, not just PR body)
- "resolves an operator-authored hcom authorization message" -> `resolve_authz`
  + `check_sender` (`OPERATOR_IDENTITIES = {"bigboss"}`). Confirmed.
- "refuses on a coordinator/agent sender" -> `check_sender` raises `GateError`
  if `from` not in the operator allowlist. Confirmed.
- "refuses on a post-authz HOLD/STOP" -> `check_no_hold` scans events after the
  authz id for HOLD/STOP/"don't merge #N" from an operator identity, plus a
  liveness assertion (`_assert_hcom_live`) so an empty scan can't silently be a
  wrong-store false negative. Confirmed.
- "ledger append to work/coordination/merge-ledger.jsonl" -> `append_ledger`
  writes to `LEDGER_PATH = os.path.join("work", "coordination",
  "merge-ledger.jsonl")`; path is gitignored (`.gitignore` line 14, confirmed
  in clone). Confirmed.
- "prints the same authz quote to stdout" -> `gate()` prints `authz quote:
  "<excerpt>"` before running the merge. Confirmed.
- "single PR-scoped authorization covers only that PR" vs. "batch designation
  dated within the current session window, per the gate's own staleness bound"
  -> `check_scope`: named-pr scope has no expiry; batch-designation scope is
  bounded by `BATCH_DESIGNATION_MAX_AGE_HOURS = 12`. Confirmed, matches AGENTS.md
  text exactly.

## Design note cross-check
`work/notes/2026-09-04-merge-auth-mechanical-backstop-design.md` exists (193
lines) and its §3.1/§3.2/§4 content matches both the AGENTS.md wording and the
shipped script (ledger as local convenience copy, hcom transcript as the real
audit trail, §3.1 step 3b operator-identity allowlist, 12h batch staleness
bound). Confirmed.

## CI-blocking finding (Phase 1, resolved)
At first-reviewed head (`eb0e268`), CI `test` failed for real:
`tests/test_documentation_sprawl.py::test_always_read_entry_surfaces_have_explicit_size_budgets`
— AGENTS.md grew to 12020 bytes against `AGENTS_BYTE_BUDGET = 11_200`. Flagged
to mizo (Phase 1, hcom). Coordinator confirmed with the operator and dispatched
a separate agent (`moge`) to raise the budget (11_200 -> 13_000, PR #294 head
`5e8a8c1`) rather than trim the approved wording. Verified independently here:
`git diff eb0e268 5e8a8c1 -- AGENTS.md` is empty (AGENTS.md byte-for-byte
identical to what I reviewed above); the only other change is the budget
constant + its comment in `tests/test_documentation_sprawl.py`. Re-ran
`gh pr checks 294` after the fix landed: `test` now `pass` (1m20s). This budget
bump was operator-approved and applied by a separate agent (`moge`), not the
PR author or coordinator self-certifying — reviewed independently by me here.

## Verification commands run
- `git diff main...HEAD --stat` (scope)
- `git diff eb0e268 5e8a8c1 -- AGENTS.md` (confirm no drift in reviewed content)
- `git diff eb0e268 5e8a8c1 -- tests/test_documentation_sprawl.py` (confirm only
  budget constant changed)
- `gh pr checks 294` (both before and after the budget fix)
- Full read of `scripts/opcmd_merge.py` (411 lines) and
  `work/notes/2026-09-04-merge-auth-mechanical-backstop-design.md` (193 lines)

## Verdict
APPROVE. Wording is operator-approved verbatim (not re-litigated here per
task scope); scope is clean; doc accurately describes the shipped mechanism;
the one real CI blocker found in Phase 1 was fixed by an independent party and
verified here to not have touched the reviewed AGENTS.md text.
