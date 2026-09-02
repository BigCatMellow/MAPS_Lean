# 6.21 — release-check 3b: `composite == BLOCKED` as an approval gate — scoping

Follows `work/notes/2026-09-01-6.21-release-design.md` §6 decision 3 and the
session-17 operator answer to that batch (`ffbf71c` / PR #243). `maps flow
release-check` shipped in **PR #244** (`7a466eb`) with `composite == "BLOCKED"`
**advisory only**. This note scopes the "later 3b slice" that makes it
approval-blocking.

Verdict: **READY-TO-DISPATCH** — the direction is operator-pre-authorized; two
narrow sub-decisions are resolvable by the reviewer at impl time (recommended
answers below), not the operator.

## 1. Is a fresh operator decision required? — NO

`work/notes/2026-09-01-6.21-release-design.md` §6 decision 3 put the choice to
the operator: `composite == BLOCKED` **advisory (3a)** vs **hard-block
`record_review APPROVED` (3b)**. The operator's answer (memory
`project_maps_lean` / the #243 batch): *"`composite==BLOCKED` advisory-only for
now, **approval-blocking is a later 3b slice**"*. So the end state — 3b makes it
blocking — is already chosen. What was deferred was **timing**, not the
decision. #244 built 3a; this is the deferred 3b.

Rule 14 re-check against current evidence at HEAD `070dc65`:
- `runtime/state/schema.sql` L847 comment: *"`composite_state = 'BLOCKED'` is
  advisory input to `maps flow review-record`, not an approval gate (that is a
  later hardening slice)."* — consistent.
- `runtime/flow_release_check.py:57` docstring: *"`BLOCKED` is **advisory** —
  this flow records no review verdict and does not gate `record_review`."* —
  consistent; this flow still records no verdict after 3b (the gate lives in the
  store's approval hook, not the flow).
- `tests/test_flow_release_check.py::test_blocked_composite_does_not_prevent_review_approval`
  (the M3-era test) explicitly asserts today's advisory behaviour — **3b
  inverts this test** for the un-acked case. That is the expected, reviewed
  behaviour change, flagged here per memory `feedback_review_test_set_too_narrow`.

**No operator sign-off needed to dispatch.** An operator *decision* only
re-enters if the reviewer picks a non-recommended answer on §3 below.

## 2. The seam (verified at HEAD `070dc65`)

`record_review(task_id, reviewer_id, verdict, summary, *,
rederived_artifact_refs)` (`runtime/state/review.py`), on `verdict ==
"APPROVED"`, after the criterion-verification gate, calls the optional hook
`self._validate_review_approval_conn(conn, task=…, submission=…, review=…,
rederived_artifact_refs=…)` (`runtime/state/review_binding.py:496`). The hook
returns `None` to allow, or `(code, message)` → `conn.rollback()` +
`MutationResult(False, code, message)`.

The hook already branches on `self._requires_bound_subject_conn(conn, task)`,
which is `True` for `task["review_required"] ==
"OPERATOR_VISIBLE_RELEASE_CHECK"` (`review_binding.py:68`). So the 3b gate is a
**new terminal check inside the existing hook**, reached only for that review
type, analogous to the bound-subject and criterion gates already there.

Data the gate needs is already persisted by #244:
`store.latest_release_check(task_id, review_id)` →
`{composite_state, operator_ack_ref, …}` (id-keyed, latest-by-id is current;
`idx_release_checks_task` on `(task_id, review_id, id)`).

## 3. Smallest slice

In `_validate_review_approval_conn`, after the existing bound-subject / run /
criterion / rederivation checks, add (only when
`task["review_required"] == "OPERATOR_VISIBLE_RELEASE_CHECK"`):

```
row = conn.execute(
    "SELECT composite_state, operator_ack_ref FROM release_checks "
    "WHERE task_id = ? AND review_id = ? ORDER BY id DESC LIMIT 1",
    (task["task_id"], review["id"]),
).fetchone()
if row is None:
    return ("RELEASE_CHECK_REQUIRED",
            "OPERATOR_VISIBLE_RELEASE_CHECK approval requires a recorded release check")
if row["composite_state"] == "BLOCKED" and not (row["operator_ack_ref"] or "").strip():
    return ("RELEASE_CHECK_COMPOSITE_BLOCKED",
            "release check composite is BLOCKED and not operator-acknowledged")
```

(In-hook raw SQL matches the rest of `_validate_review_approval_conn`, which
never calls store methods on `self` — it works on the passed `conn`.)

No schema change. No CLI change. No `flow_release_check.py` change (its
docstring's "advisory" line gets a one-clause update: advisory *unless
un-acknowledged and composite is BLOCKED*). `record_release_check` and
`flow_release_check` already plumb `operator_ack_ref` end to end (#244), so the
override path needs no new code — an operator re-runs `maps flow release-check
… --operator-ack-ref <ref>` (or a follow-up appends an acked row) and the
latest row then carries the ack.

### Files
- `runtime/state/review_binding.py` — the ~8-line gate + 2 new codes.
- `runtime/flow_release_check.py` — docstring clause only.
- `runtime/state/schema.sql` — comment L847 updated (no DDL).
- `tests/test_flow_release_check.py` — invert
  `test_blocked_composite_does_not_prevent_review_approval` → un-acked BLOCKED now
  refuses APPROVED (`RELEASE_CHECK_COMPOSITE_BLOCKED`); add: acked BLOCKED
  approves; no-row refuses (`RELEASE_CHECK_REQUIRED`); READY row approves;
  re-run BLOCKED→READY unblocks; the gate does **not** fire for
  `INDEPENDENT_REVIEW` / `OWNER_CHECK` tasks (isolation).
- `tests/test_review*.py` / `tests/test_flow_review*.py` — grep for
  `OPERATOR_VISIBLE_RELEASE_CHECK` and run every hit (memory
  `feedback_review_test_set_too_narrow`); a bare
  `record_review(APPROVED)` on such a task in an existing test with no
  release_checks row will now get `RELEASE_CHECK_REQUIRED` — fix those fixtures
  to record a READY check first.
- `work/roadmaps/CAPABILITY_CHECKLIST.md` — 6.21 evidence clause: `flow
  release-check` `composite==BLOCKED` is now approval-gating (un-acked);
  `operator_ack_ref` is the override. **No status flip** — 6.21 stays IN
  PROGRESS (Recover still unimplemented).

### ≥5 mutations
On the new gate: (M1) drop the `is None` branch; (M2) drop the `== "BLOCKED"`
branch; (M3) invert the `operator_ack_ref` emptiness test; (M4) remove the
review-type guard so it fires for every review type; (M5) `ORDER BY id DESC` →
`ASC` (stale-row selection); (M6) `AND review_id = ?` dropped (cross-review
leak).

## 3′. Residual sub-decisions — reviewer's call at impl time (recommended answers)

**(a) No `release_checks` row at all for an `OPERATOR_VISIBLE_RELEASE_CHECK`
task at approval time — refuse or allow?**
Recommend **refuse** (`RELEASE_CHECK_REQUIRED`). If a task carries the
"operator-visible release check" review type, the operator-visible evidence
should exist before the verdict — symmetric with the bound-subject gate that
already hard-requires a subject for this type. Allowing would let the whole
check be skipped silently. *Operator decision only if the reviewer wants
"allow" instead* (that weakens the review type's contract).

**(b) Operator-acknowledged BLOCKED — still block, or advisory?**
Recommend **advisory when `operator_ack_ref` is a non-empty string on the
latest row**. This is the escape hatch: the operator has seen the BLOCKED
composite and chosen to proceed (recorded, auditable, append-only). Without it,
a legitimately-acknowledged release failure could never be approved and the
task would be permanently stuck — no config flag, no `--force`. The ack ref is
already a first-class column and CLI flag (#244).

**(c) Stale release check (bound to an earlier submission / task revision) —
does it still satisfy the gate?**
**DEFER to a follow-up.** `release_checks` records `subject_run_id` but not
`task_revision` / `submission_count`, so the gate as scoped honours the
*latest* row regardless of whether the task changed after it was recorded. A
strict version (reject a release check older than the current submission,
mirroring `REVIEW_SUBMISSION_CHANGED`) needs 2 new columns on `release_checks`
+ `record_release_check` capturing them from the bound subject — a schema
change, out of the smallest slice. Note it as `§4 fork`; the advisory→blocking
step is the operator-pre-authorized piece and stands alone.

## 4. Fork — stale-release-check hardening (separate later slice)

Add `task_revision INTEGER` + `submission_count INTEGER` to `release_checks`,
populated by `record_release_check` from the bound review subject; the 3b gate
then also returns `RELEASE_CHECK_STALE` when the latest row's revision/count
lags the current submission. Design-only until 3b lands and a real stale-row
dodge is observed.

## 5. Boundaries

MUST (the slice): the ~8-line gate in `_validate_review_approval_conn` for the
`OPERATOR_VISIBLE_RELEASE_CHECK` review type only; the 2 new refusal codes; the
inverted + added tests; the docstring/comment updates; one checklist clause.

MUST NOT: change `schema.sql` DDL; change the CLI surface; make
`flow_release_check` record a verdict; add a `--force` / config bypass (the ack
ref *is* the bypass); flip 6.21 status; touch the criterion or bound-subject
gates; resolve sub-decision (a) as "allow" or (b) as "still block" without
routing that back as an operator question.

Verification: `python3 -m unittest tests.test_flow_release_check
tests.test_review_binding tests.test_flow_review_record` (+ every
`OPERATOR_VISIBLE_RELEASE_CHECK` hit from the grep) foreground; `python3 -m
runtime.smoke` exit 0; ≥5 mutations on the new gate; full `tests/` to CI.
Worktree off `origin/main`; PR into `main`; independent reviewer (not whoever
implements; the #244 author is fine as reviewer here since this is a distinct
seam); ping the coordinator; no self-merge.

Re-verify at dispatch HEAD (rule 14): the hook signature, the
`_requires_bound_subject_conn` review-type mapping, `latest_release_check`, and
that `operator_ack_ref` is still nullable text with no CHECK.

## Resume prompt

You are implementing **6.21 release-check slice 3b** for MAPS_Lean. Source of
truth: this note + `work/notes/2026-09-01-6.21-release-design.md` §6 decision 3
+ the operator answer in the #243 batch (advisory now, "approval-blocking is a
later 3b slice"). No fresh operator decision is needed to proceed.

Make `composite == BLOCKED` from `maps flow release-check` **hard-block
`record_review` APPROVED** for an `OPERATOR_VISIBLE_RELEASE_CHECK` task, unless
the latest `release_checks` row carries a non-empty `operator_ack_ref`. Add the
gate as a terminal check inside `_validate_review_approval_conn`
(`runtime/state/review_binding.py`), reached only for that review type
(`_requires_bound_subject_conn` is already `True` there). New codes:
`RELEASE_CHECK_REQUIRED` (no row) and `RELEASE_CHECK_COMPOSITE_BLOCKED`
(un-acked BLOCKED). No schema DDL, no CLI change. See §3 for the exact snippet,
§3′ for the two recommended sub-decision answers (route back to the operator
only if you choose differently), §4 for the deferred stale-row fork.

Tests: invert
`tests/test_flow_release_check.py::test_blocked_composite_does_not_prevent_review_approval`,
add acked-BLOCKED-approves / no-row-refuses / READY-approves / rerun-unblocks /
other-review-types-unaffected; grep `tests/` for `OPERATOR_VISIBLE_RELEASE_CHECK`
and fix every fixture that now needs a recorded READY check before its
`record_review(APPROVED)`. ≥5 mutations on the new gate (§3). Update the
`schema.sql` L847 comment and the `flow_release_check.py` "advisory" docstring
clause. One `CAPABILITY_CHECKLIST.md` 6.21 evidence clause, **NO status flip**.

Verification: `python3 -m unittest tests.test_flow_release_check
tests.test_review_binding tests.test_flow_review_record` + the grep hits,
foreground; `python3 -m runtime.smoke` → exit 0; full `tests/` to CI. Worktree
off `origin/main`, PR into `main`, independent reviewer, ping the coordinator,
no self-merge.
