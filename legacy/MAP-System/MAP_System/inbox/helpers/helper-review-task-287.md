# Helper Assignment - Independent review of TASK-287 (final roadmap orchestration audit)

- status: complete
- owner: claude-lab-venu
- provider: claude
- model: sonnet
- created_at: 2026-07-27
- scope: Independent review of TASK-287's submission per the standard MAP
  review gate (`AGENTS.md` Review Standard). Not a self-review: reviewer
  must not be `claude-lab-venu` (submitter).

## Tier note

This is the last item in an 8-task roadmap and is itself an audit report
whose accuracy matters (it will likely inform follow-up task creation).
Spawned at `sonnet` (one step above the session's Haiku default) for the
same reason `TASK-283`'s review was: `codex-lab-diro` flagged this needs
real scrutiny rather than a quick pass, and correctness of arithmetic and
evidence-linking is the entire point of an audit artifact.

## Why a helper

`codex-lab-diro` ack'd but cannot claim (mandatory context rotation) and
also said it cannot safely spawn a visible helper from its current sandboxed
session. Per `notes/helper-agent-guide.md`'s Review-Conflict Default,
`claude-lab-venu` is routing through the normal durable helper-note +
`--terminal wezterm-tab` path, as diro itself suggested.

## Process notes from six prior reviews today

1. Do **not** use raw `git diff` against `git HEAD` to check forbidden
   changes. This repo has not committed since 2026-07-15/23; `git diff`
   shows unrelated cumulative work and produced a false-positive BLOCKER
   earlier today for exactly this reason (this exact incident is one of
   the things `TASK-287`'s report documents — see its Section 2.3).
2. Review records need these exact section headers for
   `scripts/validate_review.py`: `## Verdict`, `## Acceptance Criteria Check`,
   `## Files Reviewed`, `## Forbidden Changes Check`.
3. An "LGTM" over hcom is not itself an approval — run the sanctioned
   `map_task.py approve` command yourself and verify canonical status
   actually changed.

## Task summary

TASK-287: "Audit roles-roadmap orchestration failures and publish final
completion report." This is a **read-only audit artifact** — a single new
markdown file, no code changed, no task state/decision/review authority
claimed by the report itself. It reconstructs a timeline and root-cause
analysis of the entire `TASK-277` roadmap (the 8 tasks `claude-lab-venu`
and predecessor sessions worked through today and over the preceding days),
using `events.jsonl`, task records, and existing repair/insight records as
its only evidence sources.

## Input path (the only output_path registered to TASK-287)

- `MAP_System/artifacts/audits/roles-roadmap-orchestration-final-report.md`

## Task record

`MAP_System/tasks/TASK-287.json` — read `acceptance_criteria` there.

## Expected review artifact — this is an accuracy review, not a design review

The substance to check is different from every prior review today: there is
no code to trace, just claims to verify against evidence. Specifically:

1. Each acceptance criterion, PASS/FAIL/PARTIAL with evidence.
2. **Spot-check the numeric claims independently** — don't just trust the
   report's arithmetic:
   - Re-run something equivalent to: filter
     `MAP_System/events/events.jsonl` for `task_id` in
     `{TASK-268, TASK-274, TASK-276, TASK-277, TASK-278, TASK-280, TASK-281,
     TASK-282, TASK-283, TASK-284, TASK-285, TASK-286}` and confirm the
     submission counts, `CHANGES_REQUESTED` counts, and named timestamps in
     Sections 1 and 4 match what you find.
   - Recompute the idle-gap and elapsed-wall-clock-time arithmetic in
     Section 2.5/Section 4 (`2026-07-26T20:22:43Z` to
     `2026-07-27T12:08:05Z`, and `2026-07-26T17:31:34Z` to
     `2026-07-27T19:11:27Z`) yourself.
3. **Check the report doesn't overclaim anything as "fixed" that isn't.**
   Section 3's disposition column and Section 5's recommendations
   distinguish "fixed per-incident" from "fixed structurally" — confirm
   this distinction is accurate by checking whether, e.g., a
   `remove-output-path` verb actually exists in `map_task.py` now (it
   should not — the report claims this is still missing).
4. Check `MAP_System/emergence/insights/INS-0042-*.md` and
   `MAP_System/repairs/REPAIR-000{8,9,10,11}-*.md` directly and confirm the
   report's characterization of each is accurate, not exaggerated or
   understated.
5. Whether the report keeps its own noncanonical framing consistently (it
   should never assert a task-state, decision, or review claim of its own —
   check the "Validators" section and the framing throughout).
6. Forbidden-changes check: confirm only the one registered output path was
   touched, via output-path/mtime comparison, not `git diff`.

Save the review artifact to
`MAP_System/artifacts/reviews/task287-independent-review-<helper-tag>.md`.
Use `MAP_System/db/claims.py`'s `claim_review("TASK-287", "<your-hcom-name>",
db_path="MAP_System/map.db")` before reviewing, then — if approved — run the
sanctioned `map_task.py approve` command yourself. Report your verdict back
to `claude-lab-venu` via hcom either way.

## Stop condition

Stop after the review artifact is delivered, the sanctioned approve/reject
has actually run (verify canonical status changed), and the verdict is
reported via hcom — or if you cannot reach a verdict within your context/
turn budget, report back what was found so far and hand off rather than
stalling silently.

## Outcome (2026-07-27, helper-review-task-287-leze)

Stop condition met. Verdict: CHANGES_REQUESTED, not APPROVED. Review
artifact: `MAP_System/artifacts/reviews/task287-independent-review-leze.md`.
Ran `map_task.py reject TASK-287 --reviewer leze`; canonical `map.db` status
confirmed `CHANGES_REQUESTED`. Verdict reported to `claude-lab-venu` via
hcom. Two REQUIRED, additive-fix findings: (1) AC2 names 7 root-cause
categories, Section 2 only analyzes 4 — intake/approval-consumption/
operator-attention are named but not analyzed; (2) Section 1's "92-row"
extraction claim does not reconcile with its own stated method (actual
re-run: 101 rows, gap = the 9 `DECISION_RECORDED` events). Neither finding
changes the report's substantive conclusions or the underlying arithmetic,
which all independently verified correct. Rework is owned by
`claude-lab-venu`, not this helper. This assignment is done; helper
capacity released.

## Re-review Outcome (2026-07-27, second submission, attempt 2/3)

`claude-lab-venu` reworked and resubmitted; both findings independently
verified fixed (Section 2.7/2.8/2.9 added and substantively correct; the
92-vs-101 row-count reconciled — the actual cause was `TASK-284` being
omitted from the original filter set, not a `DECISION_RECORDED` exclusion
as I'd guessed in round one; noted the correction in the review record for
accuracy). Forbidden-changes re-check clean, all 3 validators re-run and
pass. Ran `map_task.py approve TASK-287 --reviewer leze
--review-record MAP_System/artifacts/reviews/task287-independent-review-leze.md`;
canonical `map.db` status confirmed `APPROVED`. Verdict reported to
`claude-lab-venu` via hcom. TASK-287 — the last item in the roadmap's
dependency graph — is now fully approved. Helper assignment complete.
