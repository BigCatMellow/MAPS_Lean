# PR #231 review evidence — `maps flow handoff` impl (6.21)

reviewer: maps-lean-nava
head_sha: 67980d140d757755da52b71018c53365b920c593
independent: true
summary: APPROVE (initial REQUEST_CHANGES resolved in commit `3d71935`). The runtime code is correct and every design-§6 constraint is honored (same-task pure composition over the unchanged `record_continuity_link`, claimant read-guard with an explicit no-lease-liveness docstring, no schema / no claim-release / no status flip, e2e `CONTINUITY_REVIEW_FORBIDDEN` proven), 5 of 7 mutations on `flow_handoff.py` were killed on first pass, M1 is a verified equivalent mutant, and the one non-equivalent survivor (M4 — continuity-link direction unasserted) is now KILLED after the re-push added two direction assertions (link message `"worker-a -> worker-b"` AND a direct `SELECT predecessor_id, replacement_id` == `("worker-a", "worker-b")`). Re-ran M4 myself: FAILED (failures=1). No other mutation opened up (delta is purely additive assertions to one test). NB: head_sha rebound by coordinator to the post-rebase commit (branch predated #228–#232; rebase clean, `CAPABILITY_CHECKLIST.md` 6.21 clause updates prose only — "handoff needs a design note" → "handoff implemented" — no status flip).

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | `flow_handoff` = same-task composition: `get_task` read + claimant guard (`status == "ACTIVE"` and `claimed_by == from_worker` → `HANDOFF_NOT_CLAIMANT`; explicitly NO lease-liveness check) + `record_continuity_link(from, to, reason=)` (existing primitive, unchanged) + `next_step {STOPPED_BEFORE_REPLACEMENT_CLAIM, reason}` | PASS. Code matches exactly. `get_task` returns `status` + `claimed_by` (real `tasks` columns). Guard: `if task.get("status") != "ACTIVE" or task.get("claimed_by") != from_worker: → HANDOFF_NOT_CLAIMANT`. Docstring states verbatim the no-lease-liveness rationale and "`from_worker` is a declaration the flow checks against `store.get_task`, not a lookup". `record_continuity_link` is not in the diff — unchanged. `next_step.state == "STOPPED_BEFORE_REPLACEMENT_CLAIM"`. Primitive errors (`INVALID_CONTINUITY_LINK`, `CONTINUITY_CONFLICT`) surfaced verbatim via `_failed("continuity_link", link)`. |
| 2 | MUST NOT (§6, 8 items) | PASS. `git diff --stat` = `runtime/flow_handoff.py` (NEW), `runtime/cli.py` (one subparser + one dispatch branch), `tests/test_flow_handoff.py`, `CAPABILITY_CHECKLIST.md` (one clause). No claim-release primitive. No `schema.sql`. No `claim_task` / run-manifest / session touch. No `reviews`/`review_subjects` touch (only `continuity_links` via the existing primitive). No replacement task / `update_contract`. No `recover`/`release`. `flow_review.py` not modified (only imports `_failed` / `_mutation_payload`). Checklist 6.21 stays IN PROGRESS. |
| 3 | e2e `CONTINUITY_REVIEW_FORBIDDEN` | PASS. `test_continuation_worker_cannot_claim_independent_review`: `flow_handoff(worker-a → worker-b)`, then `store.claim_review(task_id, "worker-b")` → `.code == "CONTINUITY_REVIEW_FORBIDDEN"`, and independent `store.claim_review(task_id, "reviewer-c").ok`. Automatic via the unchanged `_continuity_component_conn` walk — no review-table write in `flow_handoff`. |
| 4 | `outgoing_run_id` omitted — documented + acceptable | PASS. The docstring justifies it (no lightweight task→runs accessor; `trace_task` + immutable run manifests + `continuity_links` carry the lineage; nothing is "frozen" by this verb). Consistent with the design note + vame's #227 non-blocking note. |
| 5 | The 4 vame #227-review notes honored | PASS. (a) claimant-guard-not-lease — explicit in the docstring. (b) `outgoing_run_id` — documented. (c) `--from-worker` is a declaration checked, not a lookup — docstring + code (`get_task` then compare, never enumerate claimants). (d) line-drift — references by name (`record_continuity_link`, `_continuity_component_conn`, `claim_task`). |
| 6 | Foreground unittest green + smoke 0 | PASS. `tests.test_flow_handoff` 11/11 (re-confirmed post-rebase); `tests.test_flow_review` 28/28; `tests.test_flow_start` + `tests.test_review_subject_binding` 28/28. `python3 -m runtime.smoke` → `"ok": true`, exit 0. |
| 7 | Own min-5 mutation on `flow_handoff.py` | PASS (after re-push). |

## Mutation testing (`runtime/flow_handoff.py`)

| # | Mutation | Result |
|---|----------|--------|
| M2 | claimant guard `or` → `and` | KILLED |
| M3 | `claimed_by != from_worker` → `== from_worker` | KILLED |
| M4 | swap link direction: `record_continuity_link(from_worker, to_worker)` → `(to_worker, from_worker)` | **KILLED after re-push** — the two new direction assertions in `test_handoff_records_continuity_link_and_stops` (link message == `"worker-a -> worker-b"` AND `SELECT predecessor_id, replacement_id` == `("worker-a", "worker-b")`) pin direction unambiguously. Re-ran M4: FAILED (failures=1). |
| M5 | `if not link.ok: return _failed(…)` → swallow, fall through | KILLED |
| M6 | drop the `task is None` guard | KILLED |
| M7 | `next_step.state` string → other | KILLED |
| M1 | drop the `status != "ACTIVE"` half of the guard | SURVIVED — **equivalent mutant.** `claim_task` (`execution.py:82`) is the only setter of `claimed_by`; `submit_task` (`execution.py:312`), the only ACTIVE exit, sets `claimed_by = NULL` in the same statement; `review.py`'s BLOCKED/DONE transitions come from `READY_FOR_REVIEW` where `claimed_by` is already NULL. So `claimed_by == from_worker` ⟹ `status == "ACTIVE"` today. The `status` check is correct defensive code (kept + noted in the commit message); killing it would need a synthetic DB state. Non-blocking. |

## Verdict

APPROVE — initial REQUEST_CHANGES (M4 direction gap) resolved in `3d71935`, re-verified: M4 now KILLED, no other mutation opened up, `test_flow_handoff` 11/11 green. Code correct, all §6 MUST-NOTs honored, no status flip, e2e proven, sibling verbs + smoke green.
