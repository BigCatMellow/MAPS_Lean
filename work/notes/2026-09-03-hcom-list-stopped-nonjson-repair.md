# Repair Record: hcom 0.7.25 `list --stopped` ignores `--json`, blocking `maps recovery-tick`

- Severity: `BLOCKING`
- Owner: coordinator (rafa)
- Trigger and evidence: enforced canonical-run pass (operator decision batch item 5), run 2026-09-03 by rafa:
  ```
  python3 -m runtime.cli --db .maps/state/maps.db recovery-tick --enforce-canonical-run \
    --harness-project-id maps-lean --repo-root ~/Projects/MAPS_Lean \
    --binding nava-worker-1=hcom-sess-nava-lbw-1
  ```
  Result: `{"ok": false, "error": "HcomProtocolError: hcom list --json returned invalid JSON", "actions": [], "opened_incidents": []}` (exit 2). Nothing written -- the pass aborts before `RecoveryStore.save`.
  Reproduced 2026-09-03 in a fresh clone against the installed `hcom 0.7.25` (`/home/home/.local/bin/hcom`):
  - `hcom list --json --stopped --all` -> human text, exit 0. Empty: `No recently stopped agents (last 60m)`. Non-empty: `Stopped agents (all, showing N):\n\n  <name> (<tool>) <age> ago  [<reason> by:<who>]  <dir>`.
  - `hcom list --json` (alive-only) -> valid JSON `[]`, exit 0.
  - `hcom list --help` documents `--json` only for the alive-only and single-agent forms; the `hcom list --stopped [name] --all` form has **no** `--json`. So this is hcom's intended surface, not a transient hcom bug that a patch release will fix.

## Finding

`HcomAdapter.list_sessions(include_stopped=True)` (`runtime/communication/hcom_adapter.py`) assumed `--json` is honored when `--stopped --all` is added. hcom 0.7.25 ignores `--json` for `--stopped` and always emits human-formatted text, so `json.loads()` raises `JSONDecodeError` -> `HcomProtocolError`.

`RecoverySupervisor.observe_silent_stops` (~line 298) and `RecoverySupervisor.tick` (~line 356) both call `self.hcom.list_sessions(include_stopped=True)` unconditionally at the top. `HcomSessionAdapter._session_records` (`runtime/harness/adapters/hcom.py:104`) does the same. Therefore **all** of `maps recovery-tick` -- not only the `--enforce-canonical-run` variant -- is dead against hcom 0.7.25: the supervisor is never reached and nothing is persisted.

Expected: `list_sessions(include_stopped=True)` returns a list of session records (alive + recently stopped), each dict carrying at least `name`, `status`, and hcom's `session_id`. The stopped records feed two things beyond liveness detection:
- `RecoverySupervisor._resolve_run_id(task, session)` reads `session.get("session_id")` and does the schema-enforced reverse lookup `resolve_session_run(project_id, "hcom", session_id) -> run_id` (`runtime/state/run_lineage.py:234`) to bind the incident to its run.
- `HcomSessionAdapter._find_by_session_id` matches on `session_id` for `resume_session_run`.

`session_is_live({})` is already `False`, so a session that is merely *absent* from the list reads as not-live -- liveness detection does not need the stopped record. Only the `session_id -> run_id` lineage does.

## Change or proposal

Two-part, split by blast radius:

### Part A -- folded into this PR: tolerate non-JSON `--stopped` output (option D)

`HcomAdapter.list_sessions`: if `include_stopped=True` and stdout does not parse as JSON, fall back to the contractual alive-only `hcom list --json` instead of raising. Alive-only parsing is unchanged and still fails closed. Effect: `recovery-tick` reaches the supervisor again; silent-stop **detection** is fully preserved (absent == not-live). Known, documented degradation: a stopped session's `session_id` is unavailable, so `_resolve_run_id` and the harness `session_id` lookup return "not found" and the incident's `run_id` is left unresolved (advisory-evidence and canonical-lineage binding degrade, they do not misbehave). This is strictly better than the current total abort and is a no-op on any hcom build that does honor `--json` for `--stopped`.

Regression test: `tests/test_hcom_adapter.py::HcomAdapterTests::test_list_sessions_include_stopped_survives_nonjson_stopped_output` -- feeds the adapter hcom's actual `--stopped` text (both the empty and the non-empty real formats) and asserts (a) no exception, (b) the alive-only payload is returned, (c) the fallback `list --json` call was actually issued.

### Part B -- design-only, follow-up impl + review: restore stopped-session lineage without `--stopped --json`

Recommended: **option C -- derive stopped-session records from `hcom events --json`.** `hcom list --stopped` is itself documented as "from events"; `HcomAdapter.read_events` already parses `hcom events` JSON-lines and is contractual. A small helper would fold life/stop events into synthetic session records (`name`, `session_id`, `status="inactive"`, stop reason/age) and merge them under the alive list, restoring the `session_id -> run_id` reverse lookup that Part A drops.

- Rejected **(A)** "alive-only, absent == not-live, drop stopped records entirely": simplest, but permanently loses `session_id` for every silent-stop incident -> `run_id` never resolves -> a canonical-enforcement lineage regression for exactly the incidents recovery exists to handle. Acceptable only as the Part A degraded fallback, not as the target state. (Open sub-question if A were ever chosen: `--binding` supplies `worker_id -> session_name`, not `session_id`; `session_id` would have to come from a `run_session_links` forward lookup by name or from the incident record -- neither exists today.)
- Rejected **(B)** parse the human `--stopped` text: format is not contractual (`hcom list --help` shows no stability guarantee); fragile across hcom releases.
- Rejected as primary **(D)**: it is Part A (the guard), not a lineage fix.
- **(E)** hcom version floor: there is **no** hcom version that honors `--json` for `--stopped` -- the `--help` output shows it is deliberately absent from that subcommand. So a "floor" cannot fix this; what is warranted is a documented note that the adapter must never depend on `--stopped --json` (added below under Prevention). Upstream changelog could not be fetched from this environment (hcom ships as a compiled binary; `raw.githubusercontent.com/aannoo/hcom/main/CHANGELOG.md` 404s); if hcom later adds `--json` to `--stopped`, Part B can be simplified but Part A stays as defense-in-depth.

Because Part B changes which hcom command recovery relies on and restores lineage semantics that Part A degrades, it is **not** folded into this PR -- it needs its own impl PR + independent review.

## Verification and rollback

- Verification (Part A):
  - `python3 -m pytest tests/test_hcom_adapter.py -q` -- new frozen regression test passes.
  - `python3 -m pytest tests/test_recovery_supervisor.py tests/test_harness_hcom_adapter.py tests/test_recovery_production_trigger.py -q` -- unchanged.
  - Full suite (see PR body).
  - Manual (NOT run here -- stop condition forbids `--enforce-*` / `recovery-tick`): against hcom 0.7.25, `HcomAdapter(...).list_sessions(include_stopped=True)` returns the alive list instead of raising.
- Rollback: revert the `list_sessions` change in `runtime/communication/hcom_adapter.py` and the test additions in `tests/test_hcom_adapter.py`. No state, schema, or config touched.

## Prevention

- Frozen regression test added in this PR (see Part A). A `MAPS_FROZEN_REGRESSION_CASE` (`runtime/evaluation/regression_case.py`) was considered per `playbook/REPAIR_AND_LEARNING.md` but is not applicable: that flow requires a portable Run Record (`run-record <task_id> <run_id>`), and this defect aborts before any run/incident state is written, so no Run Record exists. The unit-level frozen regression test is the durable countermeasure artifact instead; this note is its reference.
- Documented constraint: **`HcomAdapter` must never depend on `hcom list --stopped` honoring `--json`** -- it does not, by hcom's design. Any future stopped-session need goes through `hcom events --json` (Part B) or the alive-only + absent-is-not-live pattern.
- Friction log entry: `work/coordination/FRICTION_LOG.md` 2026-09-03 (class `tool-gap`).
- Follow-up: Part B impl PR (option C) — **LANDED** on branch
  `impl/item5-optionC-events-stopped-records` (`HcomAdapter._stopped_records_from_events`,
  merged under the alive list in the non-JSON `--stopped` fallback). Impl + Step-0
  findings: `work/notes/2026-09-03-item5-optionC-impl.md`. Independent review pending
  (two-phase). Tracked from the friction entry.
