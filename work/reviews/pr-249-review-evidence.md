# PR #249 review evidence — 6.21 release-check 3b approval-gate scoping note

Independent verification-only review by maps-lean-nava (gela authored). Design
only, 1 file (`work/notes/2026-09-02-release-check-3b-approval-gate-scoping.md`).
One REQUEST_CHANGES round (the "operator pre-authorized 3b" framing), fixed in
the delta commit, then APPROVE. `head_sha` below is the rebased branch tip.

## Round 1 — the four dispatch checks

### (1) The "operator pre-authorized 3b" claim — FAILED (fixed in the delta)

The committed operator answer (`work/notes/OPERATOR_ASK_2026-08-31-session13.md`,
SESSION 17 block, `flow release-check` batch item 3): *"`composite == BLOCKED`
→ advisory to start … The approval-blocking variant (3b) is a later hardening
slice **with its own callout** — not this one."* The original §1 quoted this but
dropped "with its own callout" — the load-bearing clause — and concluded only
*timing* was deferred. In that same doc "callout" means an operator-decision
callout (line 186). `work/notes/2026-09-01-6.21-release-design.md` §6 decision 3
independently calls the exact 3b mechanism (a new `record_review APPROVED`
precondition in `_validate_review_approval_conn`) *"an authority-model change"*
that *"adds an approval-path dependency on the release-check having run."* A new
precondition on the approval path is a material boundary — a route-back-to-operator
question (rules 9/11). So 3b is NOT pre-authorized; the operator settled the
interim behaviour (advisory now) and the timing (3b is a later slice), not the
advisory→hard-blocking decision itself.

### (2) Does it smuggle an authority/schema change that would need a fresh decision? — NO

The note is explicit: no schema DDL (only the `schema.sql` L847 comment prose),
no CLI change, no `flow_release_check.py` change beyond a docstring clause. §5
MUST-NOT bars a `--force`/config bypass, a verdict-recording change, and
touching the criterion/bound-subject gates. The 3b gate itself *is* the
authority-model change, but the note names it plainly (the round-1 problem was
mis-framing it as pre-authorized, not hiding it). The stale-release-check
hardening that would need schema (2 new columns) is correctly forked out to §4
as a separate later slice.

### (3) Smallest-slice spec — clean one-shot. YES

§3 gives the exact terminal-check SQL snippet, the 2 new codes
(`RELEASE_CHECK_REQUIRED`, `RELEASE_CHECK_COMPOSITE_BLOCKED`), the file list
(`review_binding.py` ~8 lines + 2 codes; `flow_release_check.py` docstring;
`schema.sql` comment; tests; one checklist clause), a 6-mutation set on the new
gate, and explicit `feedback_review_test_set_too_narrow` handling (grep `tests/`
for `OPERATOR_VISIBLE_RELEASE_CHECK`, run every hit, fix fixtures that now need a
recorded READY check before `record_review(APPROVED)`). Seam facts re-verified
at HEAD `070dc65`: `_validate_review_approval_conn` (`review_binding.py:496`),
`_requires_bound_subject_conn:68` True for the review type, `latest_release_check`
(`release_check.py:188`), `operator_ack_ref` nullable text — all accurate.

### (4) Checklist status flip — NONE

1 file (the scoping note only); no `CAPABILITY_CHECKLIST.md` change. §3 Files and
§5 boundaries both state the eventual impl's checklist clause is prose-only, no
status flip (6.21 stays IN PROGRESS, Recover still unimplemented).

## Delta re-check (`6f9c49a`) — the blocking finding is fully addressed

- §1 title is now "Is a fresh operator decision required? — YES (one question)"
  (was NO).
- The pre-auth claim is gone: *"The operator did NOT pre-authorize the
  advisory→hard-blocking flip: 'with its own callout' reserves that as its own
  operator-decision callout"* + cites #234 §6 "authority-model change" + rule 11.
- A proper operator callout is drafted: the exact decision block (hard-block
  `APPROVED` for `OPERATOR_VISIBLE_RELEASE_CHECK`, `operator_ack_ref` override,
  no-row → `RELEASE_CHECK_REQUIRED`; recommended YES; explicit NO/YES branches).
- Verdict reframed: "SCOPED — READY TO DISPATCH ONCE THE OPERATOR CONFIRMS 3b".
- §3′ sub-decisions now "reviewer's call GIVEN an operator YES on §1".
- Resume prompt has a hard PRECONDITION: the operator must have answered the §1
  callout YES; if unanswered, stop and surface it.
- grep for residual bad pre-auth claims: 0 (the one "pre-authorize" hit is "did
  NOT pre-authorize" — correct).

Delta = 1 file, no status flip, smoke exit 0. The scoping content (seam, 8-line
gate, 6 mutations, test plan, boundaries) was sound in round 1 and unchanged.

## Verdict: APPROVE

This note is now correctly a scoping-note-plus-drafted-callout, not a claim of
pre-authorization. The 3b IMPL stays blocked until the operator answers the §1
callout.

reviewer: maps-lean-nava
head_sha: c4a4a27391704c4f7ab9da93c4ce76c279189347
independent: true
summary: APPROVE after a REQUEST_CHANGES round — the release-check 3b scoping note's seam analysis, 8-line gate spec, 6-mutation set, test plan and boundaries are all sound and it smuggles no silent schema/authority change, but its original §1 claimed the operator pre-authorized the advisory→hard-blocking flip; the committed #243 answer defers 3b "with its own callout" (an operator-decision callout) and #234 §6 calls the mechanism "an authority-model change", so the fix commit reframes §1/the verdict as "scoped; needs the operator's one-question confirmation first" and drafts that callout (recommended YES); no checklist status flip.
