# Re-review: TASK-288 (Reconcile release-checklist requirement with risk-tiered review policy, F5)

```
task_id:     TASK-288
reviewer:    task288-review-valo
task_owner:  lili-replacement-nisa
```

## Verdict

APPROVED

## Prior review

`MAP_System/artifacts/reviews/task288-independent-review-task288-review-valo.md`
(CHANGES_REQUESTED) — one REQUIRED finding: `touches_canonical_paths()` missed
real MAP_System root-level canonical governance docs (`DECISION_CLASSES.md`,
`DESTRUCTIVE_ACTION_POLICY.md`, `AGENT_PERMISSION_LEVELS.md`,
`NEW_PROJECT_WIZARD.md`) that don't match the `AGENTS.md`/`CLAUDE.md`/
`*_SYSTEM.md` naming convention and aren't under `shared/`/`templates/`.

## Fix verified

- `MAP_System/scripts/release_task.py`: added `CANONICAL_ROOT_DOC_BASENAMES`
  (explicit set of the four flagged filenames) and an `elif basename in
  CANONICAL_ROOT_DOC_BASENAMES` branch in `touches_canonical_paths()`. Read
  the code directly — this is a real behavioral fix, not a comment-only
  patch.
- `MAP_System/tests/test_release_gate.py`: new
  `test_non_conforming_canonical_root_doc_forces_full_checklist` exercises
  exactly the case my finding named (`MAP_System/DESTRUCTIVE_ACTION_POLICY.md`
  with an incomplete checklist must still block on "full"-tier grounds). Ran
  `MAP_System/.venv/bin/python3 MAP_System/tests/test_release_gate.py`
  myself: 9/9 PASS, including this one and the two pre-existing no-regression
  tests.
- `MAP_System/CHANGE_CONTROL_SYSTEM.md`: the Release tier section now states
  the explicit `CANONICAL_ROOT_DOC_BASENAMES` list by name instead of relying
  silently on the naming convention, and tells a future author to add a new
  non-conforming root doc to that set deliberately. This closes the
  "silent assumption" half of my finding, not just the code half.
- Independently re-derived the "zero live misclassification" claim rather
  than trusting the report: queried every historical `task_output_paths` row
  for the four filenames (5 hits: TASK-108, TASK-112, TASK-115, TASK-126,
  TASK-174) and re-ran `classify_release()` against the fixed code for each.
  All 5 now classify `"full"`. TASK-108/112/115/126 are old `RELEASED` tasks
  with no `task_release_records` row (they predate the `release_tier`
  tracking added by TASK-288, released under the pre-existing all-five-checks
  regime, not part of the 61-task batch). TASK-174 is still `APPROVED`
  (already correctly held back before this fix, for an unrelated
  `*_SYSTEM.md` hit, and now also independently caught by the new branch).
  No overlap with the 61 low-tier batch releases. Confirms the fix without
  requiring any of the 61 already-released tasks to be revisited.

## Acceptance Criteria Check

| # | Criterion | Result |
|---|---|---|
| 1 | review-guide.md / CHANGE_CONTROL_SYSTEM.md reconciled into one rule, referenced identically | PASS (unchanged from prior review; this fix only tightens the shared rule's implementation) |
| 2 | REQUIRED_CHECKS enforcement matches the rule in code | PASS — the fix is exactly this: code now implements the canonical-file part of the rule more completely (`CANONICAL_ROOT_DOC_BASENAMES`) |
| 3 | Tests updated/extended, pass, no regression on STRUCTURAL/canonical case | PASS — 9/9 reproduced green, including the new regression test for the exact gap found |
| 4 | Documented path clears the backlog without hand-authoring 90 checklists | PASS (unchanged; re-verified zero overlap between the newly-covered filenames and the 61-task low-tier batch) |
| 5 | Finding F5 marked resolved, referencing the decision record | PASS (unchanged) |

## Files Reviewed

- `MAP_System/scripts/release_task.py` (diff: `CANONICAL_ROOT_DOC_BASENAMES` + `touches_canonical_paths()` branch)
- `MAP_System/tests/test_release_gate.py` (diff: `test_non_conforming_canonical_root_doc_forces_full_checklist`)
- `MAP_System/CHANGE_CONTROL_SYSTEM.md` (diff: Release tier section now names the explicit list)
- `MAP_System/map.db` (live re-query of `task_output_paths`/`classify_release()` for the 5 historical touches of the 4 newly-covered filenames)

## Forbidden Changes Check

Fix is confined to the three files named above, all within TASK-288's
registered `output_paths`. No task status/DB rows were touched by this
fix itself (it's a pure code+doc change); the 61-task batch release and
its `task_release_records`/mirror side effects were already reviewed and
approved-in-substance in the prior review pass and are unaffected by this
follow-up patch. No scope violation found.

## Outstanding, non-blocking

RECOMMENDED finding from the prior review (stale `task_tier` enum
documented in `ORCHESTRATION_ENTRYPOINT_SYSTEM.md`, out of TASK-288's scope)
was correctly left untouched per that review's own scoping and is being
filed as a separate follow-up, per hcom. Not a condition of this approval.

## Verification

- `MAP_System/.venv/bin/python3 MAP_System/tests/test_release_gate.py` — 9/9 PASS (reproduced).
- Live `map.db` query re-deriving `classify_release()` for all 5 historical
  touches of the four newly-covered filenames — all now `"full"`, zero
  overlap with the 61-task low-tier batch.
- Read the actual diff to `release_task.py` and `CHANGE_CONTROL_SYSTEM.md`,
  not just the hcom summary of it.

## Notes

All acceptance criteria from the original review remain PASS; the single
REQUIRED finding is resolved with a real code fix, a regression test named
after the exact failure mode, and an explicit doc update. Approving.
