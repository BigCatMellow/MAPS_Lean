# Task: tag-prefix vs bare-instance-name mismatch strands `run_id: null` for tagged hcom agents recovered via option C

- Status: `IN_REVIEW` (impl PR open on branch `impl/dec003-bug2-name-mismatch`,
  stacked on `investigate/dec003-bug2-name-mismatch` / #309; awaiting independent
  reviewer + 3-day operator merge hold)
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: unassigned
- Risk: `LOW` (localized fix in `HcomAdapter._stopped_records_from_events` +
  its dedup, and/or one lookup in `RecoverySupervisor`; no authority, no
  destructive path, no harness lifecycle change; silent-stop *detection* is
  unaffected either way — only lineage binding is)
- Goal: a tagged hcom agent (`hcom … --tag <label>`) that stops and is
  reconstructed through the option-C `hcom events` fallback must resolve to
  the same `run_id` an untagged agent would — i.e. the synthesized stopped
  record must (a) be recognised as a duplicate of a still-listed alive entry
  for the same agent, and (b) be found by the recovery binding's
  `session_name` so `RecoverySupervisor._resolve_run_id` binds the
  silent-stop incident to its run instead of recording `run_id: null`.
- Parent: DEC-003 known-bugs follow-up
  (`work/notes/2026-09-05-dec003-known-bugs-followup.md`, "Bug 2"). This task
  is the "picked up" shaped contract that note asked for. Option C itself
  landed in PR #276 (`9a884c2`); its own "blast radius" section missed this
  tag case.
- Related records:
  - `work/notes/2026-09-06-dec003-bug2-name-mismatch-repro.md` — **live repro
    evidence, this investigation** (`vuro`, 2026-09-06). Read first.
  - `work/notes/2026-09-05-dec003-known-bugs-followup.md` — "Bug 2", the
    original unconfirmed claim.
  - `work/notes/2026-09-03-item5-optionC-impl.md` — option-C design + the
    synthetic-record shape table.
  - `work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md` — Part A/B
    split; the `session_id -> run_id` reverse-lookup contract.
- Autonomous continuation: `YES`

## Inputs and source of truth

- `runtime/communication/hcom_adapter.py` — authoritative for the synthesized
  record shape:
  - `_stopped_records_from_events` sets `name = str(event.get("instance") …)`.
    On current hcom `0.7.25` the `instance` field is **always the bare
    `base_name`** (`leta`), never the tag-prefixed display name
    (`maps-lean-leta`). Synthesized records carry **no `base_name` key**.
  - `list_sessions(include_stopped=True)`, `except json.JSONDecodeError`
    branch: `alive_names = {item.get("name") …}` is built from the alive
    `hcom list --json`, whose `name` **is** tag-prefixed for tagged agents.
    The dedup `record["name"] not in alive_names` therefore never fires for a
    tagged agent.
- `runtime/recovery/supervisor.py` — authoritative for the lookup:
  - `observe_silent_stops` / `tick` build `sessions = {item.get("name"): item}`
    then look up `sessions.get(session_name, {})` where `session_name` comes
    from the `worker_id -> session_name` recovery binding.
  - `_resolve_run_id(task, session)` reads `session.get("session_id")` and
    calls `resolve_session_run(project_id, "hcom", session_id)`. An empty
    `session` dict ⇒ empty `session_id` ⇒ returns `None`.
- Evidence labels:
  - VERIFIED (live, this investigation): alive `list --json` `name` is
    prefixed; events `instance` is bare; `list --stopped` text is bare +
    `tag:` parenthetical; the dedup miss; the `_resolve_run_id` → `None`
    outcome when the binding name is prefixed. Reproduced against
    `origin/main` @ `c958cf6` with no runtime changes.
  - VERIFIED: `hcom list --json` alive records also expose `base_name` and
    `tag` as separate keys.
  - ASSUMED: that recovery bindings for tagged agents hold the **prefixed**
    name. Strongly implied (live tagged agents currently resolve, which
    requires the binding key to match the prefixed alive `name`), but the
    binding-creation path was not traced end to end in this investigation —
    the implementer must confirm which form `run_session_links` /
    `--binding` / the dispatch flow records for a tagged agent before
    choosing between the two fixes below.
  - ASSUMED until greped: how many real recovery bindings today are for
    tagged agents (blast radius sizing only; does not change the fix).
- Preconditions / dependencies: none. Independent of any open PR.

## The two candidate fixes

**Fix A — normalize the synthesized record UP to the prefixed convention**
(in `_stopped_records_from_events`):
- Build an `instance -> tag` map from `batch_launched` `life` events in the
  same lookback window (`data.tag`, `data.instances`), then emit
  `name = "<tag>-<instance>"` to match the alive `list --json` `name`.
- **Caveat (VERIFIED):** `batch_launched.data.tag` is set to the *tool name*
  (`claude`/`codex`/`gemini`) when the agent had no explicit `--tag`, and hcom
  does **not** prefix those in `list --json`. A correct Fix A must replicate
  hcom's rule (`tag` present AND `tag != tool`), not just concatenate.
- **Gap (VERIFIED):** when the `batch_launched` event is older than
  `_STOPPED_EVENTS_LOOKBACK` (2000) but the stop event is inside it (e.g.
  long-lived agents like `romi`), the tag is unknown and the record falls
  back to bare — still mismatched. Fix A does not fully close the bug.

**Fix B — normalize the match DOWN to `base_name` at the dedup + lookup keys**
(recommended):
- `_stopped_records_from_events`: also set `base_name` on each synthesized
  record (trivially, it is the `instance` string already in hand).
- `list_sessions` dedup: compare on `base_name` as well as `name` (drop a
  synthesized record whose `base_name` matches any alive record's `base_name`
  or `name`).
- `RecoverySupervisor`: when `sessions.get(session_name)` misses, fall back to
  a record whose `base_name == session_name` **or** whose `name` ends with
  `"-" + session_name` — exact `name` match still wins first.
- **Edge case to design for:** two agents with the same `base_name` under
  different tags (`housekeep-zale`, `review-zale`). The binding is prefixed,
  so exact-match-first handles the common case; the `base_name` fallback must
  only apply when exactly one candidate matches, else leave it unresolved
  (same failure mode as today, no regression).
- Robust regardless of the events window; uses fields hcom already provides.

Owner picks A or B (or A-for-dedup + B-for-lookup). Recommendation: **B**,
because A has a verified correctness gap and a fragile tag-vs-tool rule.

## Change boundary

- MAY CHANGE:
  - `runtime/communication/hcom_adapter.py` — `_stopped_records_from_events`
    (record shape / name normalization) and the dedup in the
    `list_sessions(include_stopped=True)` `JSONDecodeError` branch only.
  - `runtime/recovery/supervisor.py` — only the `session_name -> record`
    lookup (the `sessions` index construction and/or the `sessions.get(...)`
    call sites in `observe_silent_stops` / `tick` / `_resolve_run_id`
    caller). No change to detection semantics, incident scheduling, backoff,
    resume, or `_resolve_run_id`'s reverse-lookup contract itself.
  - `tests/test_hcom_adapter.py`, `tests/test_recovery_supervisor.py` (and
    `tests/test_harness_hcom_adapter.py` only if a shared fixture shifts).
  - this task file (status / completion notes).
- MUST NOT CHANGE:
  - any `runtime/` file other than the two named above.
  - `runtime/state/run_lineage.py` / `resolve_session_run` / the
    `run_session_links` schema.
  - `HcomSessionAdapter._find_by_session_id` (keys on `session_id`, already
    correct — do not touch).
  - `runtime/recovery/production.py`, `CanonicalRunGuard`, harness lifecycle.
  - `work/notes/2026-09-05-dec003-known-bugs-followup.md` (the bug note).
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` (at most a one-line "landed"
    pointer if a maintainer asks; not required by this task).
  - `_STOPPED_EVENTS_LOOKBACK`, the warn-once flag, the JSONDecodeError
    narrowing, `_parse_session_list`'s fail-closed behavior.
- MAY CHANGE IF NECESSARY: adjacent tests asserting the old bare-only
  synthesized `name` or the old dedup behavior — update them to the new
  behavior and say so in the PR body.
- OPERATOR APPROVAL REQUIRED: none anticipated. Escalate (to coordinator) only
  if the binding-form investigation shows bindings actually hold the **bare**
  name — that would mean the alive-side live lookup is the broken half and the
  fix shape changes.

## Decision authority

- Owner may decide: Fix A vs B vs hybrid; the exact fallback-match predicate;
  whether to add `base_name` to the synthetic record unconditionally; test
  fixture shape; the new field's placement in the record-shape docstring.
- Owner must escalate: any change touching `_resolve_run_id`'s resolver call,
  the `run_session_links` lookup, or detection (`session_is_live`) semantics;
  any evidence that bindings hold the bare name.
- Resolve internally first: which name form the dispatch/binding path records
  for a tagged agent (read `runtime/state/run_lineage.py`, the `--binding`
  CLI wiring, and how `observe_silent_stops`' `bindings` arg is populated);
  hcom's exact prefix rule (read the repro note — `tag != tool`).

## Acceptance criteria

- [ ] For a **tagged** agent present in both the alive `list --json` (prefixed
      `name`) and the option-C event stream (bare `instance`), the
      `list_sessions(include_stopped=True)` result contains **one** record for
      that agent, not two.
- [ ] Given a recovery binding whose `session_name` is the prefixed alive
      `name` of a now-stopped tagged agent, and an option-C synthesized record
      carrying that agent's `session_id`, `RecoverySupervisor._resolve_run_id`
      returns the bound `run_id` (not `None`). Covered by a regression test
      with a fake hcom adapter + a stub `resolve_session_run`.
- [ ] Untagged-agent behavior is byte-for-byte unchanged (regression test:
      untagged stop → same record, same resolution as today).
- [ ] Silent-stop **detection** is unchanged for both tagged and untagged
      agents (a stopped agent still reads as not-live; `session_is_live`
      logic untouched).
- [ ] The `base_name`-collision-across-tags case (if Fix B) resolves to the
      exact match when one exists and does **not** mis-bind when two bare
      matches exist (leaves `run_id` unresolved, as today).
- [ ] No change to `resolve_session_run`, `run_session_links`,
      `HcomSessionAdapter`, `production.py`, or any guard.
- [ ] Record-shape docstring in `_stopped_records_from_events` updated to
      list any new key.

## Verification and evidence

- `python3 -m py_compile runtime/communication/hcom_adapter.py runtime/recovery/supervisor.py`
- Targeted, as a blocking foreground call with output redirected (never piped
  to `tail`):
  `python3 -m unittest tests.test_hcom_adapter tests.test_recovery_supervisor tests.test_harness_hcom_adapter -v > /tmp/bug2-suite.log 2>&1; echo $?`
- Full suite, same redirect pattern:
  `python3 -m unittest discover -s tests > /tmp/bug2-full.log 2>&1; echo $?`
- Manual (optional, needs a live hcom + populated `HCOM_DIR`): the command
  block in `work/notes/2026-09-06-dec003-bug2-name-mismatch-repro.md` step 4,
  re-run post-fix, showing the tagged synthesized record now deduped and the
  simulated `_resolve_run_id` returning a run_id.
- `recovery-tick` / `--enforce-*` NOT run (same stop condition as PR #269 /
  #276).
- Evidence to preserve: both suite logs, the pre/post manual transcript, and
  `work/reviews/pr-<N>-review-evidence.md`.
- Review required: `INDEPENDENT_REVIEW` — self-authored implementation; the
  implementer is not eligible to review. Reviewer must be independent of the
  implementer and of this task's author (`vuro`).

## Conditional execution rules

- Environment / target: fresh `git clone` to a UNIQUE `/tmp/<tag>-$$/` path.
  Never the coordinator checkout (`~/Projects/MAPS_Lean`) or
  `.claude/worktrees/`. `git config user.name "BigCatMellow"` / matching
  noreply email.
- Ordered procedure: (1) read the repro note + the three option-C notes +
  the actual code; (2) trace which name form a tagged-agent recovery binding
  records — escalate if it is the bare form; (3) pick Fix A / B / hybrid;
  (4) implement in `hcom_adapter.py` (+ `supervisor.py` lookup if Fix B);
  (5) update the record-shape docstring; (6) tests — tagged dedup, tagged
  resolution, untagged-unchanged, collision; (7) run targeted then full suite
  as blocking foreground calls with redirects.
- Failure branches: if bindings hold the bare name → STOP, hand back to the
  coordinator (the broken half is then the alive-side lookup, not option C).
  If the fix appears to need a `run_session_links` / `resolve_session_run`
  change → STOP, that is out of boundary.
- Rollback: revert the branch; no persistent state, no schema, no destructive
  Git op.
- Security / privacy: hcom session ids and local paths stay local runtime
  evidence only; do not put them in the PR body beyond what the repro note
  already contains.
- External side effects: GitHub PR publication only. **Do not merge** — the
  operator merge-hold window is in force; open the PR and let it queue.
- Effort limit: the two named functions + their dedup/lookup + tests. Do not
  expand into option-D, the `--hcom-dir`/`HCOM_DIR` precedence bug (that is
  "Bug 1" of the same note, separate), or any hcom-version work.

## Stop / escalate

Stop rather than guess if:
- recovery bindings for tagged agents turn out to hold the bare `base_name`;
- the fix appears to require a `run_session_links` schema or
  `resolve_session_run` signature change;
- hcom's prefixing rule cannot be pinned down from the repro note + a live
  `hcom list --json` (do not reverse-engineer the hcom binary).

Escalate to: the coordinator (not the operator) for retry-vs-reshape. Operator
only if a behavior change would break an existing passing dispatch flow.

## AGI readiness

- Fresh-Agent Test: `PASS` — bug, root cause (two name conventions across
  hcom surfaces), the two files, the two candidate fixes with tradeoffs, and
  the live repro are all named.
- No-Guess Test: `PASS` — one ASSUMED item (binding name form) is called out
  with an explicit "confirm before choosing / escalate if bare" instruction;
  line numbers deferred to a direct read.
- Scope Test: `PASS` — MAY / MUST NOT lists are concrete and file-scoped.
- Authority Test: `PASS` — escalation trigger (bare-form bindings) named.
- Completion Test: `PASS` — acceptance criteria are checkable; verification
  commands are copy-pasteable with the redirect pattern spelled out.
- Failure Test: `PASS` — failure branches and stop conditions listed.
- Continuation Test: `PASS` — autonomous continuation YES; hand-back target is
  the coordinator.

## Completion / handoff

- Created 2026-09-06 by `vuro` from a live repro of DEC-003 known-bug 2. The
  bug is **confirmed reproduced** on `main` @ `c958cf6` with current hcom
  `0.7.25`; see `work/notes/2026-09-06-dec003-bug2-name-mismatch-repro.md`.
- Implemented 2026-09-07 by `vamu` (independent of `vuro`). **Fix B chosen.**
  Binding-form trace result: `observe_silent_stops`' `bindings` arg is
  populated *only* from `maps recovery-tick --binding WORKER_ID=SESSION_NAME`
  (runtime/cli.py `_parse_bindings` → runtime/recovery/production.py
  `run_recovery_pass(bindings=...)`; no automatic/derived source exists). That
  CLI takes the operator-visible display name, which is the tag-prefixed
  `name` for a tagged agent — so bindings hold the **prefixed** form, NOT the
  bare `base_name`. Escalation trigger not hit; Fix B proceeds.
  Changes:
  - `hcom_adapter.py::_stopped_records_from_events` — synthetic records now
    carry `base_name` (= the bare `instance` string); docstring updated.
  - `hcom_adapter.py::list_sessions` JSONDecodeError dedup — compares on
    `name` AND `base_name` against alive records' `name`/`base_name`.
  - `supervisor.py` — new module helper `_resolve_session_record(records,
    session_name)`: exact `name` match first, else single-candidate
    `base_name` fallback (`session_name == base_name` or
    `session_name.endswith("-" + base_name)`); two matches → `{}` (unresolved,
    no mis-bind). Both `observe_silent_stops` and `tick` build a
    `session_records` list and route the `session_name → record` lookup
    through it. No change to `_resolve_run_id`'s resolver call,
    `run_session_links`, `HcomSessionAdapter`, `production.py`, or any guard.
  - Tests: `test_hcom_adapter.py` (tagged dedup, base_name present),
    `test_recovery_supervisor.py` (tagged run_id binds, base_name collision
    stays unresolved, untagged unchanged).
- Next action: coordinator `lira` dispatches an independent reviewer
  (independent of `vamu` and of `vuro`).
