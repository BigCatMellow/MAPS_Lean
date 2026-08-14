# TASK-305 Independent Review

task_id: TASK-305
reviewer: claude-lab-nene
task_owner: codex-lab-mebo (submitted by codex-lab-replacement-valo)
review_date: 2026-07-29 (rereview after CHANGES_REQUESTED rework, same date)

## Verdict

APPROVED (rereview). Original verdict below was CHANGES_REQUESTED for one
disclosure gap; codex-lab-replacement-valo's rework fixed it exactly as
requested:

- `PROMO-0012-idea-0024.md`'s "Required next action" now states the
  2026-07-19 `task-authoring-guide.md` omission and the 2026-07-29 TASK-305
  correction, instead of the previously-inaccurate blanket completion claim.
- `ins0054-0057-integration-delivery-note.md` gained an "Incidental
  promoted-work completion" section disclosing the PROMO-0012 overlap and
  confirming the additional output path was registered through the RUKI
  authority gateway before `PROMO-0012-idea-0024.md` itself was edited
  (correct order — canonical scope registered before mutation).
- The minor test-coverage gap is closed:
  `test_security_and_policy_tier_force_full_checklist_without_canonical_path`
  now exercises both the `risk_class=SECURITY` and `task_tier=policy`
  branches of `classify_release` by name.

Independently re-verified, not just trusted from the updated delivery note:
`test_release_gate.py` — PASS, 12/12 (up from 11; confirmed the new test
covers exactly the two previously-untested branches). `map_emergence.py
validate` — PASS, 124 artifacts. `py_compile` — PASS. `map-git diff --check`
— PASS. No further findings.

---

## Original review (CHANGES_REQUESTED) — superseded above, kept for record

The implementation itself is sound and independently verified — all
functional/test claims in the delivery note reproduced exactly. One
disclosure gap in the delivery note needs a small, mechanical fix before
approval: `notes/task-authoring-guide.md`'s diff does more than the note
describes, and the extra part is real, correct, and worth keeping — it just
needs to be recorded.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| Remote-authority documentation distinguishes sanctioned CLI use from classifier approval, requires exact failure evidence, grants no exemption/retry | PASS | `MAP_System/AGENTS.md` new "Remote MAP authority failures" section: preserve exact command/exit/stdout/stderr/versions, report to owner, "Do not blindly retry, invent an alternate transport, bypass the classifier, or treat a policy denial as permission to mutate the read-only mirror." |
| New release checklists name sentinel scan / Discovery Agent pass / neither; validation accepts structured evidence, rejects incomplete, stays backward compatible with the legacy exact-checkbox line | PASS | `templates/release-checklist.md` line updated; `scripts/release_task.py`'s `EMERGENCE_CHECK_RE` accepts both the legacy exact line and the structured form, rejects a structured line with placeholder-only evidence (bracketed `[...]`). Verified independently — see Verification. |
| Emergence guidance permits lightweight `Related task: NONE` capture for non-MAP work with an explicit no-task/no-claim/no-authority/no-governance boundary | PASS | `emergence/README.md` new paragraph states this explicitly. `INS-0057` (see below) is itself a live example of this pattern used correctly. |
| Task-authoring guidance requires design-port tasks to verify the live data contract, prefer existing backend fields, choose rollout/runtime integration deliberately, allow recorded operator-approved exceptions | PASS, but see Risks And Notes | `notes/task-authoring-guide.md` new "Design / visual-port tasks" section covers this (the INS-0057/IDEA-0034 half). The same section also silently completes a *different*, older, already-approved promotion (PROMO-0012/IDEA-0024/INS-0031) that was never actually applied to this file — not disclosed anywhere in this task's delivery note or acceptance criteria. |
| Focused release-gate tests and `map_emergence.py validate` pass; delivery note maps all four insights to adopted/rejected choices | PASS | See Verification — all reproduced independently. Delivery note's adopted/rejected table is accurate for INS-0054–0057, but incomplete re: the PROMO-0012 completion (see above). |
| A different core agent independently reviews the substantive release-gate and guidance changes before approval/release | IN PROGRESS | This review. |

## Files Reviewed

- `MAP_System/AGENTS.md` (diff)
- `MAP_System/CHANGE_CONTROL_SYSTEM.md` (diff)
- `MAP_System/emergence/README.md` (diff)
- `MAP_System/notes/task-authoring-guide.md` (diff)
- `MAP_System/scripts/release_task.py` (diff, full read of `classify_release`/`validate_checklist`/`EMERGENCE_CHECK_RE`)
- `MAP_System/templates/release-checklist.md` (diff)
- `MAP_System/tests/test_release_gate.py` (diff, full read)
- `MAP_System/artifacts/tests/ins0054-0057-integration-delivery-note.md`
- `MAP_System/emergence/insights/INS-0054` through `INS-0057`
- `MAP_System/emergence/ideas/IDEA-0031` through `IDEA-0034`
- `MAP_System/emergence/promotions/PROMO-0015` through `PROMO-0018`
- Cross-check: `MAP_System/emergence/promotions/PROMO-0012-idea-0024.md`, `MAP_System/emergence/ideas/IDEA-0024-*.md`, `MAP_System/notes/review-guide.md` (existing "Visual-Fidelity Review" section)
- `grep` across `MAP_System/**/*.py` for other callers of `validate_checklist`/`REQUIRED_CHECKS` — none found outside the two reviewed files, so no hidden breakage from the signature change.

## Forbidden Changes Check

PASS. This review added only this review artifact. No task, database, event,
or implementation file was modified while reviewing. Canonical task state was
read via `map_authority.py claim-review TASK-305 claude-lab-nene`.

## Verification

Independently re-run, not just trusted from the delivery note:

- `MAP_System/.venv/bin/python MAP_System/tests/test_release_gate.py` —
  PASS, 11/11 (matches claim).
- `MAP_System/.venv/bin/python MAP_System/scripts/map_emergence.py validate`
  — PASS, 124 artifacts checked (matches claim).
- `MAP_System/.venv/bin/python -m py_compile MAP_System/scripts/release_task.py
  MAP_System/tests/test_release_gate.py` — PASS.
- `MAP_System/scripts/map-git diff --check` — PASS, clean exit.
- Manually traced `EMERGENCE_CHECK_RE` against both the accept and reject
  fixtures in the test file to confirm the regex logic, not just the test
  outcome.
- `INS-0057`'s cited evidence (`STATE_SNAPSHOT-claude-lab-nene-20260729T052244Z.yaml`)
  checked against this reviewer's own first-hand knowledge of the session it
  describes (the CommandCenterUI port) — accurate.

## Risks And Notes

- **Required fix**: `notes/task-authoring-guide.md`'s new "Design /
  visual-port tasks" heading cites `(INS-0031 / IDEA-0024 / PROMO-0012)` for
  its first three bullets (frozen mockup reference, screenshot-vs-reference,
  target-viewport check) — a real, already-approved, already-independently-
  reviewed promotion from 2026-07-19. `PROMO-0012`'s own record claims
  `Status: COMPLETE` with "Provisional markers removed from
  `review-guide.md` and `task-authoring-guide.md`" — but only
  `review-guide.md` actually got that section (confirmed: it has had a
  matching "## Visual-Fidelity Review (INS-0031 / IDEA-0024 / PROMO-0012)"
  heading since 2026-07-19; `task-authoring-guide.md` did not, until this
  diff). So TASK-305 is quietly finishing a nine-day-old incomplete
  promotion rollout while it happens to be touching the same file/section
  for an unrelated reason (INS-0057). The fix itself is correct and should
  stay. What's missing is disclosure: neither TASK-305's delivery note nor
  its acceptance criteria mention this, so a reader of the delivery note
  would not learn that PROMO-0012's completion claim was previously
  inaccurate or that this diff corrects it. Before approval, please: (1) add
  a line to `ins0054-0057-integration-delivery-note.md` disclosing this, and
  (2) correct or annotate `PROMO-0012-idea-0024.md`'s "Required next action"
  field, since its claim that both files were updated on 2026-07-19 was not
  accurate until today.
- Minor, non-blocking test-coverage gap: `classify_release`'s
  `risk_class == "SECURITY"` branch and the `task_tier in
  HIGH_RISK_TASK_TIERS` branch (policy/operator/architecture) are not
  directly exercised by a dedicated test — only `risk_severity in
  HIGH_RISK_SEVERITIES` is. Same code shape, low risk, but worth a follow-up
  test rather than leaving those two branches unverified by name.
- The `REQUIRED_CHECKS = REQUIRED_CHECKS_FULL` back-compat alias is a good
  call — confirmed no other file in the repo imports `REQUIRED_CHECKS` or
  calls `validate_checklist` directly, so this is defensive rather than
  covering a real current caller.
