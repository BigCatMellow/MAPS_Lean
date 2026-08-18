# Recovery Stage 2 — wire a real `run_id` into `observe_silent_stops`

Owner: investigative + bounded implementation task
Status: authorized by `work/notes/2026-08-17-recovery-equivalence-authority-design.md` operator decision #3 ("Approved: bind `RecoveryIncident` to `run_id`")

## Where things stand (verified by direct read, do not re-derive)

- `runtime/recovery/store.py`'s `RecoveryStore.schedule(...)` already accepts an optional `run_id: str | None = None` parameter and stores it on `RecoveryIncident` (PR #82 landed this plumbing).
- `runtime/recovery/supervisor.py`'s `observe_silent_stops()` calls `self.store.schedule(task_id=..., worker_id=..., session_name=..., reason="silent_stop", resume_after=...)` **without** passing `run_id` — this is the actual gap. `tick()` already reads `incident.get("run_id")` and feeds it to `_advisory_environment_evidence()`, which is a no-op today because `run_id` is always `None` in practice.
- The design note's Area 1 (point 4) explicitly warned: **do not resolve this with a heuristic** ("guessing the most-recent run for a task would be exactly the kind of heuristic AGENTS.md and roadmap 4.4 prohibit"). This task must find (or conclude there is no) exact, non-heuristic binding — it must not invent a "most recent run_manifest for this task_id" fallback, even though that might look tempting.

## The promising candidate binding (investigate, verify, don't assume)

`runtime/state/schema.sql`'s `run_session_links` table has `UNIQUE(project_id, adapter_id, session_id)`, plus `idx_run_session_one_attach` (a partial unique index ensuring at most one `ATTACH` row per `run_id`) and `idx_run_session_one_replacement`. This looks like it may provide an **exact** reverse lookup: given the right `(project_id, adapter_id, session_id)` triple, there should be at most one matching row, and it names a `run_id`. `runtime/state/run_lineage.py`'s `resolve_run_session()` / `_resolve_run_session_conn()` currently only goes the forward direction (`run_id` -> session info) — there is no existing reverse (`session` -> `run_id`) method as of this task's writing; you may need to add a small, narrowly-scoped query method (e.g. `resolve_session_run(project_id, adapter_id, session_id)`), following the existing style in that file, rather than inline SQL inside `supervisor.py`.

**Before assuming this is the answer**, verify:
1. What `observe_silent_stops()` actually has in scope at the point it calls `schedule()` — it has `worker_id`, `session_name` (from `self.hcom.list_sessions(...)`, i.e. an hcom-domain session name, not necessarily the same string as `run_session_links.session_id`), and the `task` dict (which has `task_id`, `claimed_by`, and whatever else `task_reader.list_tasks(...)` returns — check what fields are actually available, e.g. `project_id`).
2. Whether hcom's `session_name` (as returned by `HcomAdapter.list_sessions()`) is the same identifier space as `run_session_links.session_id`/`adapter_id`, or whether there's a translation layer already in `runtime/communication.py` (the `HcomAdapter`) that would need to be consulted too. Read `HcomAdapter` and any place that currently calls `record_run_session_link(...)` (the write side) to understand what values actually get written into `session_id`/`adapter_id`/`project_id` at session-creation time — that tells you the exact shape you need to query back with.
3. Whether, for an ACTIVE task with exactly one claiming worker (the only case `observe_silent_stops` considers — ambiguous multi-claim workers are already skipped upstream), the resulting `run_id` lookup is provably exact (at most one match) rather than "happens to usually be one match." If it's provably exact given the schema's uniqueness constraints, that's your non-heuristic binding. If it's not — e.g. if multiple runs could plausibly be ATTACHed to overlapping identity keys before this task, or if hcom session names don't cleanly map into the `run_session_links` identifier space at all — **do not paper over it with a "most recent" fallback**. Document exactly what you found and why an exact binding isn't currently possible, and stop there; that is a complete, legitimate task outcome.

## If an exact binding exists: implementation

- Add the narrowly-scoped reverse-lookup method (see above) if one doesn't already exist, matching the existing read-only query style in `run_lineage.py`.
- In `observe_silent_stops()`, resolve the `run_id` for each detected silent-stop event using that method, and pass it through to `self.store.schedule(..., run_id=resolved_run_id)`. If the lookup returns nothing for a specific incident (no exact match found for that one case, even though the mechanism generally works), pass `run_id=None` for that incident rather than failing the whole detection loop — this must stay purely additive; a missing `run_id` today already means "no advisory evidence," which is the existing safe behavior, not a regression.
- Do **not** change anything about what triggers, suppresses, or resumes an incident. This is required to remain **zero behavior change** to recovery decisions themselves (per the design note's Stage 2, Option A — already the only authorized option; Option B/gating is explicitly not authorized). The only observable difference should be that `tick()`'s returned action records may now carry non-null `environment_context` (via the already-existing, already-tested `_advisory_environment_evidence` path) when a real `run_id` was resolved.

## Tests required

- Extend the existing recovery test suite (`tests/test_helper_recovery_lineage.py` and/or wherever `observe_silent_stops`/`RecoverySupervisor` is currently tested — find the right file by grepping for `observe_silent_stops` in `tests/`) with a case that: creates a run manifest + session link with a known `run_id`, simulates a silent stop for that exact session, and asserts the resulting `RecoveryIncident`'s `run_id` matches. Also test the "no match found" path returns `run_id=None` without raising.
- If your investigation concludes no exact binding exists: instead of implementation, write up the finding (what you checked, why it's not exact) as a short addendum appended to `work/notes/2026-08-17-recovery-equivalence-authority-design.md` under a new `## Stage 1 investigation finding (later session)` heading, and stop. Do not implement a heuristic to force a result.

## Explicit non-goals

- No gating (Stage 3) — not authorized, not touched by this task regardless of outcome.
- No change to `_advisory_environment_evidence()` itself or to `tick()`'s existing logic beyond it now sometimes receiving a non-null `run_id` — that function is already correct and already tested.
- No change to how `observe_silent_stops` decides a stop is silent, or to the ambiguous-worker skip logic.

## Verification required before handoff

1. Full test suite passes (`python -m unittest discover -s tests -v`, run in background, ~7-11 minutes).
2. `python -m compileall -q runtime tests`.
3. The new test(s) described above are present and specifically exercise the run_id resolution (not just "suite is green").

## Delivery

Implement on a fresh branch off current `main` (clone fresh with `gh repo clone BigCatMellow/MAPS_Lean`; don't assume any existing local clone). Git identity: `git config user.email "201203536+BigCatMellow@users.noreply.github.com"`. Commit, push, `gh pr create` against `BigCatMellow/MAPS_Lean` main — **do not merge your own PR**, open it and stop. If your outcome is "no exact binding found, documented instead," open a PR with just that documentation addendum rather than no PR at all, so the finding is reviewable. Report back the PR URL and, specifically, whether you found an exact binding or concluded one doesn't currently exist and why.
