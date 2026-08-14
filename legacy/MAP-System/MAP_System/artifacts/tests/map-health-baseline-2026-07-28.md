# MAP System Health Baseline — 2026-07-28

- author: lili-replacement-nisa
- assigned by: claude-lab-lili (via hcom, request #20671)
- scope: investigation and reporting only — no fixes applied, no task state changed
- status: honest snapshot at time of writing; several tasks were genuinely in flight during this audit (see "In-flight context" below)

## Headline

- **Full registered suite (`run_tests.sh`): 74 pass / 5 fail / 79 total.**
- Of the 5 failures: **1 is a genuine, unrelated-to-drift regression** (see
  Finding 1, below — a real conflict between a released task and a
  pre-existing test), **2 are transient in-flight drift** (expected, not
  defects), **1 is a genuinely new (post-baseline) event-log warning** that
  turns out to be historical and self-corrected, and **1 (`validate_layer1_test`)
  fails only because it depends on the same event-log warning**.
- `map_emergence.py validate`: 1 pre-existing malformed record
  (`INS-0047`), matches the assignment's own framing of known noise.
- `context_rotation.py validate`: **2 genuine issues** — two `prepared`
  (never acknowledged or abandoned) rotation attempts with real
  canonical-task/output-path drift (`codex-lab-kazu`, `task278-levi`).
- Everything else checked (`validate_task_mirrors`, `validate_task_graph`,
  `validate_task_schema`, `validate_shared_state.py`, `validate_decisions`,
  `map_emergence.py stale` — findings-only, not failures) is clean.

## Finding 1 (most important): a released task's approved change breaks a pre-existing test that nobody ran during its review

`test_local_ollama_lane.py::test_visible_launcher_and_ui_are_local_only`
asserts, against the in-repo template `server.py`:

```python
assert "ollama-goose" not in server_text
assert '"pi-lab-new"' not in server_text
assert 'OLLAMA_URL = "http://127.0.0.1:11434"' in server_text
assert "SUMMARY_MODEL = None" in server_text
```

This directly contradicts **DEC-029** (2026-07-23, consolidates
`OLLAMA_URL`/`SUMMARY_MODEL` into a single `OLLAMA_HOST_PORT`-derived,
opt-in form) and **DEC-030** (2026-07-23, live is authoritative for
features — including the `ollama-goose`/`pi-lab-new` launchers — merge
direction is live→template). **TASK-265** (released today, 2026-07-28,
independently reviewed and APPROVED by a freshly-spawned reviewer) folded
live into the template per DEC-030, which is exactly what made this
pre-existing test start failing — it encodes assumptions from before
DEC-029/030 existed and nobody updated it when those decisions were made,
five days before TASK-265 executed them.

This is not a defect in TASK-265's logic — DEC-029/030/033 are real,
command-center-recorded decisions, and TASK-265's own new test suite
(`test_command_center_ollama_allowlist.py`) correctly proves the security
gate this task restored is fail-closed. The gap is procedural: TASK-265's
independent reviewer (`task265-review-fera`) re-ran "all 9
`test_command_center_*` suites" — `test_local_ollama_lane.py` doesn't
match that naming prefix despite testing the exact same file, so it fell
outside the search. This is exactly the class of gap this session's
`emergence/insights/INS-0053` is about (prose/naming conventions letting
a real check get silently skipped) — recommend a follow-up task to either
rename this test into the `test_command_center_*` family or update
`run_tests.sh`'s CommandCenterUI-related grouping so a reviewer's file
search actually catches every relevant test, plus updating this specific
test's assertions to match DEC-029/030/033. Not fixed here — investigation
only, per assignment.

## Finding 2: two stale `prepared` context-rotation attempts with real drift

`context_rotation.py validate` returns `ok: false` (exit 1). Of ~29
recorded rotation entries, all but two show empty `issues` (the
`path_drift`/`task_drift` booleans alone are not failures — they're
expected on old finalized/history entries where files have since moved).
Two are real:

- `codex-lab-kazu`: `["canonical_task_drift", "touched_path_drift"]`,
  phase `prepared` (never acknowledged or abandoned)
- `task278-levi`: `["canonical_task_drift", "touched_path_drift"]`, phase
  `prepared` (never acknowledged or abandoned)

Both are stale prepared rotations sitting in limbo — not actively harmful
(a `prepared`-but-never-`ack`'d rotation can't be finalized, so no
duplicate-live-agent risk), but they're real validator failures that
should eventually be resolved via `context_rotation.py abandon` by
whoever owns those identities, not silently left failing `validate`
indefinitely. Not fixed here — investigation only.

## Finding 3: `validate_shared_state_tasks` — 2 drifted rows (transient, expected)

```
DRIFT current-state.md:60: TASK-263: claims SUBMITTED, map.db has CHANGES_REQUESTED
DRIFT current-state.md:62: TASK-289: claims SUBMITTED, map.db has APPROVED
```

Both match the assignment's own framing: TASK-263 and TASK-289 were both
under active review when the swarm's other agents were mid-flight during
this audit. Live DB check at report time: TASK-263 is `CHANGES_REQUESTED`
(claimed_by: none — rework needed, per `mapfinish-kino`'s review),
TASK-289 is `APPROVED` (per `mapfinish2-zemi`'s review, not yet released).
`current-state.md`'s generated snapshot simply hadn't been re-rendered
since those transitions landed. **Not a genuine regression** — this is
exactly the kind of momentary active-lane drift the assignment said to
expect and not flag as a defect.

## Finding 4: `validate_events_no_new_warnings` — 1 new warning, but historical and self-corrected

```
WARN-NEW line 2145: non-canonical event type TASK_SUBMITTED
SUMMARY errors=0 legacy_warnings=33 new_warnings=1 baseline_line_count=680
```

Checked `events/warning_baseline.json` directly (baseline_line_count=680,
recorded 2026-07-04) rather than assuming — this genuinely is past the
baseline cutoff, so the mechanical check is correct to flag it as new,
not baseline noise. But reading the actual event: it's from
**2026-07-19** (`codex-lab-kiri`, TASK-257), and the very next line in the
log (2146) is a canonical `SUBMISSION` event whose own summary reads
*"supersedes the immediately preceding noncanonical TASK_SUBMITTED
event-type label without altering its result or evidence"* — i.e.,
`codex-lab-kiri` caught and self-corrected this in the same session it
happened, nine days ago. This is real signal that the accepted-warning
baseline was never updated to absorb this specific historical line — an
oversight, not an active or ongoing defect. Recommend adding this one
line to `warning_baseline.json`'s accepted set in a future task (not
done here). `validate_layer1_test` fails only because it depends on
`validate_events` passing clean, so it inherits this same root cause —
not a second, independent problem.

## Finding 5 (informational, not a validator failure): `claude-lab-lili` status changed mid-audit

At the time this session's context-rotation ack/finalize ran (earlier
today), `claude-lab-lili` was correctly recorded `status=inactive`
(session_superseded) in `map.db`. At the time of this audit, it shows
`status=available`. I flagged the provenance concern about this identity
issuing a new assignment while superseded directly to `claude-lab-lili`
and `bigboss` over hcom before starting this work (separate from this
report). Recording it here too since it's a real state change worth
someone confirming was intentional.

## In-flight context at time of audit (expected, not defects)

- `TASK-254`: SUBMITTED, owner `codex-lab-kiri`, no live claim
- `TASK-263`: CHANGES_REQUESTED (was SUBMITTED during part of this audit)
- `TASK-289`: APPROVED (was SUBMITTED during part of this audit)
- `TASK-291`: IN_PROGRESS, claimed by `mapfinish-rafa`
- `TASK-293`: IN_PROGRESS, claimed by `mapfinish2-zemi`
- `TASK-292`: READY, unclaimed (new since this session's earlier snapshot)

## Task-state summary (map.db, at report time)

| Status | Count |
|---|---|
| RELEASED | 208 |
| APPROVED | 30 |
| DONE | 25 |
| RETIRED | 15 |
| IN_PROGRESS | 2 |
| CHANGES_REQUESTED | 1 |
| READY | 1 |
| SUBMITTED | 1 |

`graph/runner.py`: `next_route=review` (TASK-254 needs an independent
reviewer), `halt_state=clear`, `policy_gated_tasks=[]`,
`blocked_tasks=["TASK-292"]`.

## Full check results

### `run_tests.sh` (74 pass / 5 fail / 79 total)

Failing checks, by name: `validate_research_artifacts`,
`validate_shared_state_tasks` (Finding 3), `validate_events_no_new_warnings`
(Finding 4), `validate_layer1_test` (downstream of Finding 4),
`local_ollama_lane_test` (Finding 1).

`validate_research_artifacts` failure (not otherwise analyzed above,
listed for completeness): `artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md`
is missing 8 required fragments (`# Research Summary`, `Summary ID:`,
`## Question`, `## Answer`, `## Confidence`, `## Confidence decays after`,
`## Open questions`, `## Downstream effect`). Not investigated further
against a baseline (no accepted-warning mechanism exists for this
validator the way it does for `validate_events`) — reporting as a plain
genuine failure; whether it is pre-existing or new was not determined in
this pass.

### Standalone validator invocations (as explicitly requested)

- `validate_task_mirrors.py` — PASS (also in suite)
- `validate_task_graph.py` — PASS (also in suite)
- `validate_task_schema.py` — PASS (also in suite)
- `validate_shared_state.py` — PASS, 23 files checked, 0 failures, 0 warnings
- `validate_shared_state_tasks.py` — FAIL, 2 drifted rows (Finding 3)
- `validate_decisions.py` — PASS, 32 decisions checked, 0 failures
- `validate_events.py` — FAIL, 1 new warning beyond the 680-line baseline (Finding 4)
- `map_emergence.py validate` — FAIL, `INS-0047` missing/invalid required
  fields (matches assignment's framing of known pre-existing noise; not
  independently re-verified against a formal baseline since none exists
  for this validator)
- `map_emergence.py stale` — 12 findings, all "RELEASED/APPROVED but
  artifact remains RAW/CANDIDATE" — informational backlog, not failures
  (the command has no pass/fail exit distinct from reporting)
- `context_rotation.py validate` — FAIL, exit 1, 2 genuine issues
  (Finding 2)
