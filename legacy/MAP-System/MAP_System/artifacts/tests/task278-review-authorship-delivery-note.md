# MAP Delivery Note — TASK-278 Durable Review Authorship

- task: `TASK-278`
- implementer: `task278-levi` (core implementation); finished, validated, and
  submitted by `claude-lab-nora` after the weekly-limit shutdown handoff
- authority evidence: SQLite `events.id=1727` and `events.id=1743`
  (`DECISION_RECORDED`, `bigboss`)
- risk: structural process integrity
- review requirement: independent reviewer; neither `task278-levi` nor
  `claude-lab-nora` may review

## Delivered Behavior

- `task_submission_authorship` stores the canonical author of the current
  submission independently from `tasks.owner`, review prose, and lease state.
- The guarded `IN_PROGRESS` → `SUBMITTED` transaction records author identity
  atomically. Event emission remains post-commit under TASK-274's contract.
- Rejection and rework preserve the prior author. A successful resubmission
  atomically replaces the current author and increments `submission_count`.
- Review claims compare the reviewer with canonical submission authorship.
  Owner drift cannot permit the actual author to claim review.
- Both `approve` and `reject` enforce the same canonical identity at the
  terminal verdict transaction. Their status update remains guarded by
  `status='SUBMITTED'`, so concurrent terminal verdicts have one winner.
- `validate_review.py` can verify a named reviewer against canonical SQLite
  authorship. Reviewer-authored `task_owner` prose remains advisory only.

## Legacy and Migration Rule

Absence of a `task_submission_authorship` row means **UNKNOWN SUBMISSION
AUTHOR**. Review claim and terminal verdict gates fail closed with a diagnostic
that requires explicit migration evidence or operator disposition. Missing
history, current owner, and reviewer-authored artifact text are never treated
as proof of independence.

The schema change is additive. Existing databases create the table inside the
first sanctioned successful submission transaction; fresh databases receive it
from `migration/schema.sql`. No historical identity is guessed or backfilled.

## Race and Lifecycle Evidence

`MAP_System/tests/test_review_authorship.py` covers:

- atomic author recording and owner drift;
- author refusal and genuinely independent reviewer acceptance;
- unknown legacy claim and terminal-verdict refusal;
- rejection, rework, and resubmission by a replacement author;
- atomic duplicate review-claim arbitration;
- atomic duplicate terminal-verdict arbitration;
- validator use of canonical state instead of artifact owner text.

The existing TASK-199/TASK-270 review-claim fixture now declares its submission
author explicitly. Its 12 arbitration and integrity-error regressions remain
unchanged in intent and green.

## Verification

- `test_review_authorship.py`: 7/7 pass.
- `test_submission_event.py`: 7/7 pass.
- `test_task268_lifecycle.py`: 3/3 pass.
- `test_review_claims.py`: 12/12 pass.
- `test_review_gate.py`: 3/3 pass.
- `test_reassign_owner.py`: 5/5 pass.
- `test_no_self_review.py`: 2/2 pass.
- Python compilation: pass.
- Task schema validator: pass.
- Task mirror validator: pass.
- Event validator: no TASK-278 warning; the known historical
  `TASK_SUBMITTED` warning remains at JSONL line 2145.

The TASK-278/TASK-280 `map_task.py` and TASK-280/TASK-283
`pre_dispatch_policy.py` output collisions were resolved via
`MAP_System/repairs/REPAIR-0009-task280-output-path-defer.md` (structural
repair, direct bigboss approval, 2026-07-27): both paths were deferred off
TASK-280's registration, restoring TASK-278's and TASK-283's prior
ownership. `scripts/validate_task_graph.py` now passes cleanly.

After that repair, the full runner completed 74 pass / 5 fail. No failure
originates in TASK-278 behavior; all five are pre-existing and unrelated:

- `role_registry_test`: TASK-280's role-registry test environment lacks
  `langgraph`;
- `validate_research_artifacts`: the historical malformed
  `SUMMARY-herdr-comparison-2026-07-22.md`;
- `validate_shared_state_tasks`: stale `current-state.md` still says
  TASK-274 is READY;
- `validate_events_no_new_warnings`: historical noncanonical
  `TASK_SUBMITTED` JSONL line 2145 (no new warnings introduced);
- `validate_layer1_test`: derives from the events/shared-state findings
  above.

An initial `review_gate_test` run correctly failed because its historical
SUBMITTED fixture had no author. After registering that compatibility test as
a TASK-278 output and declaring its explicit fixture author, it passes 3/3.
Final graph, mirror, and schema validation all pass now that the
TASK-280 shared-path collision is cleared.

## Compatibility, Rollback, and Residual Risk

Compatibility:

- `submit_task()` keeps its Boolean contract, submitted row shape, event type,
  and post-commit event ordering.
- The partial unique index on open review claims is unchanged.
- Owner reassignment semantics remain unchanged; owner is no longer an
  independence authority.

Rollback:

- Revert the TASK-278 code gates and schema declaration. The additive table can
  remain inert without affecting pre-TASK-278 readers; dropping it is not
  required and would discard useful audit state.

Residual risk:

- Historical open submissions remain intentionally unreviewable until author
  evidence is explicitly migrated or an operator disposes them.
- A committed submission whose later JSONL event append fails still retains
  canonical SQLite authorship. This differs deliberately from TASK-274's event
  reconciliation debt: review safety uses the transactional row, not the
  fallible post-commit event.

## Rework Round 2 — codex-lab-diro Independent Review (CHANGES_REQUESTED)

Reworked by `claude-lab-venu` (nora's context-rotation replacement session)
after independent review `REV-TASK-278-codex-lab-diro-656d7a0a` returned
`CHANGES_REQUESTED`; see
`MAP_System/artifacts/reviews/task278-independent-review-diro.md`.

REQUIRED finding fixed: `validate_review.py`'s legacy artifact-text
self-review check (`check_self_review`, matching `reviewer:`/`task_owner:`
prose in the review record) ran unconditionally, so it could append a
blocking `SELF_REVIEW` issue even when the canonical DB/reviewer check
already confirmed the reviewer was independent of the true submission
author. Diro reproduced this with reviewer `codex-lab-diro`, canonical
author `claude-lab-nora`, and artifact text `task_owner: codex-lab-diro` —
a false block driven entirely by mutable prose. `validate()` now only runs
the legacy heuristic when canonical inputs (`--db`, `--task-id`,
`--reviewer`) are absent; whenever the canonical check can run, it is the
sole self-review authority and the legacy heuristic is skipped. The legacy
path is unchanged and still fires when no canonical DB/reviewer identity is
available (fully offline validation of a review record).

RECOMMENDED finding fixed: `submit_task()`'s docstring in
`MAP_System/db/claims.py` previously said a post-transition crash "may lose
authorship evidence"; authorship is committed in the same transaction as the
guarded status update, so only the subsequent JSONL `SUBMISSION` event
append can be lost. Docstring corrected to say so.

New regression:
`test_canonical_independence_overrides_artifact_owner_text_false_block` in
`test_review_authorship.py` reproduces diro's exact false-block scenario
(artifact `task_owner` text equal to the reviewer id) and asserts: (1) an
independent canonical reviewer is accepted despite the matching artifact
text, (2) the canonical author is still blocked even when artifact text
never names them, and (3) the legacy heuristic still fires when no
canonical DB/reviewer inputs are supplied at all.

Verification (round 2): `test_review_authorship.py` 8/8,
`test_submission_event.py` 7/7, `test_task268_lifecycle.py` 3/3,
`test_review_claims.py` 12/12, `test_review_gate.py` 3/3,
`test_reassign_owner.py` 5/5, `test_no_self_review.py` 2/2;
`validate_task_graph.py`, `validate_task_mirrors.py`, and
`validate_task_schema.py` all pass.

Residual risk (round 2): none newly introduced. The legacy artifact-text
heuristic remains load-bearing only for review records validated without a
canonical DB/reviewer identity (e.g. ad hoc offline checks); production
`approve`/`reject` calls always supply `--db`/`--reviewer` and therefore
always use the canonical, non-spoofable authority.
