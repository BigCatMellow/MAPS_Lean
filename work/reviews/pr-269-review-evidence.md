reviewer: independent-review-agent a5c75a7b (PR #269, two-phase)
head_sha: fb51c3add861b5ee241d8366c41b9cad7950ebd3
independent: true
summary: APPROVE. Record + option-D guard for the hcom 0.7.25 `list --stopped` ignores-`--json` defect that aborts all of `maps recovery-tick`. Diff scope is exactly the 4 declared files (b52acd1) plus one nit-fix commit (2f46281) touching only runtime/communication/hcom_adapter.py + its test; no runtime/recovery or runtime/harness change. The guard degrades the stopped path to the contractual alive-only `hcom list --json` when stdout is non-JSON, preserving silent-stop *detection* (session_is_live({}) is already False for an absent session). Regression test feeds hcom's real `--stopped` text (empty + non-empty) and locks no-exception + fallback-issued. CRUX: option D unblocks the total HcomProtocolError abort so recovery-tick reaches the supervisor again, but it does NOT deliver item 5's goal (a routable LEASE_EXPIRED `resume_denied` on LBW-EXERCISE-1) -- the stopped session's session_id is dropped, so RecoverySupervisor._resolve_run_id returns None, the incident opens with an unresolved run_id, _resolve_harness_binding returns "no_run_id_bound", and the harness canonical-denial path is skipped entirely (falls back to plain direct hcom resume, which cannot emit a canonical denial). Item 5 genuinely needs the option-C follow-up (rebuild stopped records from `hcom events --json`) first. The PR, repair record, and FRICTION_LOG all state this accurately. All 3 Phase-1 nits were addressed in 2f46281 and re-verified here. Full suite green; PR `test` check green.

## Diff scope

`git diff 828d5e7..2f46281 --name-status`:
- M `runtime/communication/hcom_adapter.py`
- M `tests/test_hcom_adapter.py`
- M `work/coordination/FRICTION_LOG.md` (append-only -- new dated entry after the last existing entry, no past entry rewritten)
- A `work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md`

`git diff b52acd1..2f46281 --name-only` (the nit-fix commit): only `runtime/communication/hcom_adapter.py` + `tests/test_hcom_adapter.py`. No `runtime/recovery/`, `runtime/harness/`, schema, config, or `.maps/` change anywhere in the PR.

## Defect (reproduced live)

hcom 0.7.25 is installed at `/home/home/.local/bin/hcom`. Confirmed 2026-09-03:
- `hcom list --json --stopped --all` -> `No recently stopped agents (last 60m)` (human text, exit 0)
- `hcom list --json` -> `[]` (valid JSON, exit 0)
`json.loads` on the human text raises `JSONDecodeError` -> `HcomProtocolError`. `RecoverySupervisor.observe_silent_stops` (supervisor.py:297), `tick` (supervisor.py:355), and `HcomSessionAdapter._session_records` (harness/adapters/hcom.py:104) all call `list_sessions(include_stopped=True)` unconditionally, so the pre-patch adapter kills the entire `maps recovery-tick` command against installed hcom, not just `--enforce-canonical-run`. `hcom list --help` shows `--json` is deliberately absent from the `--stopped` subcommand, so no hcom version fixes this upstream.

Ran the patched adapter (head 2f46281) against the real installed hcom: `list_sessions(include_stopped=True)` -> `[]` (survives, no raise); `list_sessions(include_stopped=False)` -> `[]`. Patch confirmed effective against the live defect.

## Findings

### CRUX (not a defect in the PR -- disclosed, and the crux of whether item 5 is unblocked)

Option D alone does NOT unblock item 5's goal (a real, routable `LEASE_EXPIRED` `resume_denied` on `LBW-EXERCISE-1`). Traced:

- `supervisor.py` `tick()` (~L533): the canonical `resume_denied` outcome flows only through `_resolve_harness_binding(incident, session_name)` returning a non-None binding.
- `_resolve_harness_binding` (supervisor.py:216) returns `(None, None, "no_run_id_bound")` when `incident.get("run_id")` is falsy.
- `incident["run_id"]` is populated only by `observe_silent_stops` -> `_resolve_run_id(task, sessions.get(session_name, {}))` (supervisor.py:337) at incident-open time.
- `_resolve_run_id` (supervisor.py:162) needs `session["session_id"]` from the stopped-session record; on `{}` (absent session, which is exactly what option D produces) it returns `None`.
- `--binding` supplies `worker_id -> session_name`, not `session_id`, and no `run_session_links` forward-lookup-by-name exists -- so run_id cannot be recovered another way.

Net: option D unblocks the abort (recovery-tick runs, silent-stop detection preserved), but a stopped-session incident opens with an unresolved run_id -> harness canonical-denial path skipped -> falls back to plain direct hcom resume -> no canonical denial emitted. Item 5 needs option C (or equivalent lineage restoration) first. The PR body, `work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md` (Part A "KNOWN LIMITATION" / Part B, and its explicit rejection of option A as a target state for this exact reason), and the FRICTION_LOG entry all state this correctly. No misrepresentation.

(Side note, orthogonal: `_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}` at supervisor.py:24; `production.py:394` says production exposure converts working resumes to `resume_denied` "most likely via LEASE_EXPIRED". Whether `LEASE_EXPIRED` actually lands in `_CANONICAL_DENIAL_CODES` at production wiring time is for the option-C impl PR to confirm -- out of scope here.)

### Nit 1 -- RESOLVED in 2f46281

Degradation is now logged: module logger `runtime.communication.hcom_adapter` (`_LOGGER = logging.getLogger(__name__)`), one `logging.warning` on the non-JSON `--stopped` fallback, gated by `self._warned_stopped_nonjson` (initialised `False` in `__init__`, set `True` after the first warning) so it fires once per adapter instance. The message names the unresolved-run_id consequence and points at the repair note. On the correct path (inside `except json.JSONDecodeError` in the `include_stopped` branch). Verified once-per-instance by `test_list_sessions_include_stopped_nonjson_fallback_logs_once` (two degraded passes, asserts `len(ctx.records) == 1`).

### Nit 2 -- RESOLVED in 2f46281

The catch is narrowed to `except json.JSONDecodeError` around a bare `json.loads(result.stdout or "[]")`. A structurally valid JSON payload that fails `_parse_session_list`'s type check (e.g. a hypothetically `--json`-honoring hcom emitting `[1, 2, 3]` on the stopped path) is no longer masked: `json.loads` succeeds, no fallback is taken, and `_parse_session_list(result.stdout)` raises `HcomProtocolError("hcom list --json did not return a JSON array of objects")`. Verified directly: monkeypatched `_run` to return `'[1, 2, 3]'` on the stopped path -> `HcomProtocolError` raised, only one `_run` call issued (no fallback). The narrowing is structurally sound because the only statement in the `try` is `json.loads`.

### Nit 3 -- RESOLVED in 2f46281

`test_list_sessions_alive_only_still_fails_closed_on_bad_json`: with `HCOM_FAKE_BAD_LIST=1` (fake hcom prints `not json` for `list --json`), asserts BOTH `list_sessions()` and `list_sessions(include_stopped=True)` raise `HcomProtocolError` -- locking that the alive-only path and the broken-fallback path both fail closed. Genuine lock (proven by mutation Mc below). The `if not include_stopped: raise` line from b52acd1 is gone; the new structure ends with an unconditional `return self._parse_session_list(result.stdout)`, and this test is what guards it.

## Regression / lock tests -- genuine, not tautological

- `test_list_sessions_include_stopped_survives_nonjson_stopped_output`: feeds hcom's actual text (both `"No recently stopped agents (last 60m)"` and `"Stopped agents (all, showing 2):\n..."`), asserts no exception, returned names == alive-only payload, and the two most-recent calls are `["list","--json","--stopped","--all"]` then `["list","--json"]` (fallback actually issued).
- `test_list_sessions_include_stopped_nonjson_fallback_logs_once`: locks once-per-instance warning.
- `test_list_sessions_alive_only_still_fails_closed_on_bad_json`: locks fail-closed on both paths.

## Mutation testing (guard, head 2f46281, run against `tests.test_hcom_adapter`)

| # | mutation | caught? |
|---|---|---|
| Ma | drop the `if not self._warned_stopped_nonjson` once-gate (always warn) | caught (logs_once fails) |
| Mb | don't set `self._warned_stopped_nonjson = True` | caught (logs_once fails) |
| Mc | alive-only bad JSON returns `[]` instead of raising | caught (fails_closed fails) |
| Md | broaden stopped catch `json.JSONDecodeError` -> `Exception` | not caught -- **behaviourally inert** (the only statement in the `try` is `json.loads`, which raises nothing but `JSONDecodeError` for a `str`; wrong-typed arrays are still checked outside the `try`). Not a real escape. |

Phase-1 mutation set (M2-M6 on b52acd1: fallback returns None / inverted guard / wrong fallback command / no fallback / parse-success also raises) all remained caught after the refactor.

## Verification

- `python3 -m unittest tests.test_hcom_adapter tests.test_recovery_supervisor tests.test_harness_hcom_adapter` -> Ran 89 tests, OK (matches impl's report).
- `gh pr checks 269 -R BigCatMellow/MAPS_Lean` -> `test` = pass (1m24s, authoritative). `review-evidence` = fail (expected -- this file did not exist yet; re-runs green after this commit).
- hcom 0.7.25 present -> original defect reproduced, patched adapter survives it (see "Defect (reproduced live)" above).
- Fresh scratchpad clone, on branch `fix/hcom-stopped-json-defect`, `git status --porcelain` clean throughout -- no dirty state, no foreign staged files, no cross-agent contamination observed in this clone.

## Repair record + FRICTION_LOG

- `work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md` conforms to `templates/repair-record.md` (all required sections present, plus justified extras). Severity `BLOCKING` justified: all of `maps recovery-tick` is dead against installed hcom. Prevention section names the frozen regression test and the option-C follow-up, and explains why a `MAPS_FROZEN_REGRESSION_CASE` Run Record is not applicable (abort precedes any run/incident state).
- FRICTION_LOG entry matches the documented format (class `tool-gap` [valid enum] / signal / countermeasure / verified / follow-up). Append-only confirmed (`git diff 828d5e7..2f46281 -- work/coordination/FRICTION_LOG.md` shows only additions).

## Option-C deferral

Correct call. Option C changes which hcom command recovery depends on and restores lineage semantics option D degrades -- larger blast radius, warrants its own impl PR + independent review. Folding it here would over-scope a record + minimal guard.

## Disposition

APPROVE. Head `fb51c3a`, single-parent chain `2f46281 -> b52acd1 -> 828d5e7`. Minimal correct guard, honestly scoped, well-tested, degradation now logged. All 3 Phase-1 nits resolved and re-verified at this head. No blocking findings.

Operator note: the crux stands -- merging this does NOT by itself enable item 5's routable `LEASE_EXPIRED` denial on `LBW-EXERCISE-1`; the option-C follow-up (stopped-record reconstruction from `hcom events --json`) is a prerequisite for that. This PR's value is unblocking the total `recovery-tick` abort and recording the defect.

Do NOT merge -- coordinator merge-prep.
