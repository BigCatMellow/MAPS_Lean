# DEC-003 option B — real-stall exercise — attempt 2 (real run) — SUCCESS

**Correction (2026-09-05, post-review by `bona`):** the SUCCESS claim below
about the `resume_denied` capture itself stands. But the capture only
exercises `HarnessService.resume()` on a lease-expiry path — it does not
close 6.4 (no `.stop()` call, so `BEFORE_DESTRUCTIVE_ACTION` never fired),
6.16 (no `--require-canonical-run` worktree-bound run, so
`RUN_WORKTREE_MISMATCH` was not exercised), or 6.22 (no `.send()` call, so
`MemoryProvenanceGuard`'s `BEFORE_SEND` callback never fired). Those 3 rows
were walked back from DONE to IN PROGRESS in `CAPABILITY_CHECKLIST.md`; only
6.5/H5/E4/L6 are genuinely closed by this evidence. See those rows for the
corrected gap language.

**Status: SUCCESS.** A real, routable `resume_denied` was captured from
`recovery-tick --enforce-canonical-run` against a genuinely-live hcom session
that stalled unattended past its lease, closing DEC-003's strong-evidence path
for the 7-row harness-enforcement cluster (6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 /
L6). Frozen as regression case
`CASE-378fb326d2aceaa0cd3ceeb5ce314f8dba541a234a7331d86e6d31f24663e5c9`
(`work/regression-cases/`).

Executed 2026-09-05 by `dec003-oauth-hila`, dispatched by coordinator `mizo`.
This is the exercise's first counted attempt (the 2026-09-04
`dec003-exercise-luvo` run was an environment/OAuth precondition failure, not
a stall-detection attempt — see
`work/notes/2026-09-04-dec003-b-real-stall-exercise-results.md`). Task doc:
`work/tasks/dec003-b-real-stall-exercise.md`.

## Environment precondition (resolved)

`~/.claude/.credentials.json` is global to `$HOME`, not per-directory —
confirmed by spawning real hcom sessions in three different fresh `/tmp`
scratch directories (none under `~/Projects/MAPS_Lean` or
`.claude/worktrees/`) and all three authenticated immediately, no OAuth
browser flow needed. The prior attempt's blocker was specific to that
session's host state at the time, not a structural precondition of this
exercise.

One mechanical wrinkle: a fresh, never-trusted directory shows Claude Code's
one-time "Quick safety check" trust prompt, defaulted to **"No, exit"**. A
blind `hcom term inject <name> --enter` accepts that default and kills the
launch (hit this twice — see attempts below). The reliable sequence is
`printf -v esc '\x1b[B'; hcom term inject <name> "$esc" --enter` (down-arrow
then enter) to select "Yes, I trust this folder" before Enter.

## Corrected procedure, as actually run

The 2026-09-04 note's 3-tick correction was confirmed: `observe_silent_stops`
opens an incident only on an observed live→not-live transition, so tick 1 is
always a baseline, tick 2 is the transition tick (opens the incident,
`resume_after = now + 900s`), and a third tick after that delay is required to
attempt the resume.

### Two additional, previously-undocumented mechanical bugs found and worked around

**Bug 1 — `recovery-tick --hcom-dir` is not the shell's `HCOM_DIR`.**
`export HCOM_DIR="$PWD/.hcom"` (as directed by the lineage-bootstrap
precedent, appropriate there because that exercise used a *synthetic* session
that never needed real hcom lookups) has **no effect** on `recovery-tick`:
`HcomAdapter.environment()` (`runtime/communication/hcom_adapter.py:88-91`)
builds its subprocess env from `os.environ.copy()` and then unconditionally
overwrites `HCOM_DIR` with `Path(args.hcom_dir).resolve()`, and
`--hcom-dir` defaults to the literal string `.hcom`
(`runtime/recovery/production.py:139`, `DEFAULT_HCOM_DIR`) resolved against
the **process cwd** (this task's own clone), not the real global hcom
transport where an actually-spawned real session lives (`~/.hcom`
/ `/home/home/.hcom` on this host). Two ticks were run against an empty,
disconnected `.hcom` before this was caught — both spuriously showed
`last_live: false` for a session that was, at that moment, genuinely alive.
**Fix: pass `--hcom-dir /home/home/.hcom` explicitly** (or whatever the
correct global path is) on every `recovery-tick` invocation that must observe
a real session.

**Bug 2 — `--binding W=<name>` must be hcom's tag-prefixed `name` field, not
the session UUID, and Option C's stopped-session reconstruction uses a
*different, untagged* name than the alive listing — a real name-identity bug.**
`RecoverySupervisor.observe_silent_stops` builds its session lookup table keyed
by `item.get("name")` from `HcomAdapter.list_sessions()`
(`runtime/recovery/supervisor.py:295-297`), and `--binding` values are
`worker_id=session_name` pairs looked up directly in that table
(`supervisor.py:320,325`) — the session UUID is a different field
(`session.get("session_id")`, used only inside `_resolve_run_id` for the
`run_session_links` reverse lookup). Passing the UUID as the binding name (a
plausible reading of the task doc, and how `bind-session --session-id` is
used) makes every lookup miss silently (`sessions.get(session_name, {})` = `{}`,
`session_is_live({})` = `False`) — this was caught first, with the corrected
binding = `worker_id=<hcom name>`.

A second, deeper instance of the same class of bug then appeared: for a
`--tag`'d agent, `hcom list --json`'s alive-session `name` field is
tag-prefixed (e.g. `dec003-stall-nate`), but `HcomAdapter._stopped_records_from_events()`
— the option-C fallback synthesizing stopped-session records from the `hcom
events` stream (`hcom_adapter.py:218-`) — builds its record's `name` from the
event's bare `instance` field (e.g. `nate`, no tag prefix; confirmed directly:
`{"data":{"action":"stopped","by":"pty","reason":"closed"},...,"instance":"nate",...,"type":"life"}`).
**These two `name` values never match for any tagged agent.** The first
throwaway session (`dec003-stall-nate`, tagged `dec003-stall` per the task
doc's own suggestion) hit this: tick 1 correctly saw `last_live: true`
(alive-list path, tag-prefixed name matches the `--binding`), but after the
process was killed, tick 2's `sessions.get("dec003-stall-nate", {})` returned
`{}` (option-C's reconstructed record is keyed `"nate"`, never
`"dec003-stall-nate"`) — the incident still opened (empty dict → not-live,
correctly detected as a transition), but `_resolve_run_id` got `session={}`
too, so `run_id` was permanently `null` on that incident
(`RNS-616777848625`, task `DEC003B-A2-2`, still visible in the transcript
below, left `state: probing` / `no_run_id_bound` at tick 3 — this incident was
never going to reach a routable denial and was abandoned in place, not part
of the counted result).

**Workaround used (no runtime change): launch the throwaway session with no
`--tag` at all.** An untagged session's `name` field equals its bare instance
name in both the alive listing and the events-derived reconstruction (verified
directly for the working session, `zora`: `name == base_name == "zora" ==` the
events `instance` field), so the two paths agree and `run_id` resolves
correctly across the live→dead transition. This is within the task's
explicit "owner may decide ... task-id/worker-id naming" latitude and required
no `runtime/` change — the coordinator was told which untagged names to
exclude from babysitting instead of relying on a tag prefix.

Both of these are real, reproducible production bugs in
`runtime/communication/hcom_adapter.py` / `runtime/recovery/supervisor.py`
(not something this exercise is authorized to fix — change boundary is
`work/notes/`, `work/regression-cases/`, `work/decisions/DEC-003-*.md`
Result section, and the 7 named `CAPABILITY_CHECKLIST.md` rows only). Flagging
both for a follow-up task:
- the hcom-dir env-vs-flag precedent-note guidance is stale/misleading for a
  *real* (non-synthetic) session and should be corrected in the precedent note
  or the CLI help text;
- the tag-prefix / bare-instance-name mismatch between `hcom list --json`'s
  alive records and `HcomAdapter._stopped_records_from_events()`'s
  events-derived records is a latent bug that will silently strand
  `run_id: null` on any silent-stop incident for a **tagged** hcom agent,
  which is the common case in this coordinator's fleet (nearly every agent in
  `hcom list -v` carries a tag). This should be fixed in
  `_stopped_records_from_events` (recover/propagate the tag prefix onto the
  synthesized record's `name`) rather than worked around by convention in
  every future exercise.

## The successful run (task `DEC003B-A2-3`, run `RUN-7249d47f13e646f2aabc04f3e7e12bee`, session `zora`)

Fresh clone: `/tmp/dec003-b-a2-12209/`. `export HCOM_DIR="$PWD/.hcom"` was set
per the precedent note for the `maps` control-plane commands (`init`,
`create`, `shape`, `promote`, `flow start`, `run bind-session`) — this is
unrelated to `recovery-tick`'s separate `--hcom-dir` flag (Bug 1 above); those
control-plane commands never call the hcom adapter.

### Throwaway session

`hcom-claude-visible --dir /tmp/dec003-stall-<pid>-notag2 --hcom-prompt "..."`
with `HCOM_TAG=""` explicitly overridden (the coordinator's own shell exports
`HCOM_TAG=dec003-oauth`, which is otherwise inherited even with no `--tag`
flag — confirmed: a first no-`--tag` attempt still produced
`name: dec003-oauth-dura`). Result: `zora`, `session_id
67a76380-959e-4c5a-975b-fdf7801eceb7`, PID 14470, `name == base_name == "zora"`
in both `hcom list --json` and the events stream's `instance` field.

### Control-plane sequence (verbatim, condensed to codes)

```
$ python3 -m runtime.cli --db .maps/state/maps.db create --task-id DEC003B-A2-3 \
    --project-id maps-lean --title "DEC-003 option B real-stall exercise attempt 2 (untagged session)"
{"code": "CREATED", "ok": true, ...}

$ python3 -m runtime.cli --db .maps/state/maps.db shape DEC003B-A2-3 --contract-json contract.json
{"code": "UPDATED", "ok": true, ...}
# contract.json: goal/sources/inputs/output_paths(work/scratch-dec003b-a2-3)/
# outcome/owner(hila)/decision_authority/verification/evidence_expected/
# escalation/task_type(RESEARCH)/risk(MEDIUM)/review_required(INDEPENDENT_REVIEW)/
# acceptance_criteria/stop_conditions — output_paths deliberately NOT
# "work/notes" (that scope was still reserved by an earlier, abandoned
# task attempt DEC003B-A2-1/2 in the same DB; overlapping output scope is
# rejected by `promote`).

$ python3 -m runtime.cli --db .maps/state/maps.db promote DEC003B-A2-3 --actor hila
{"code": "READY", "message": "DEC003B-A2-3 is READY", "ok": true, ...}

$ python3 -m runtime.cli --db .maps/state/maps.db flow start DEC003B-A2-3 \
    --worker-id hila-worker-3 --repo-root "$PWD" --lease-seconds 90
{"code": "FLOW_STARTED", "ok": true,
 "run_manifest": {"run_id": "RUN-7249d47f13e646f2aabc04f3e7e12bee",
                   "worker_id": "hila-worker-3", "session_id": null,
                   "writable_scope": ["work/scratch-dec003b-a2-3"]},
 "claim": {"task": {"lease_expires_at": "2026-09-05T02:56:29Z"}}}

$ python3 -m runtime.cli --db .maps/state/maps.db run bind-session \
    RUN-7249d47f13e646f2aabc04f3e7e12bee --worker-id hila-worker-3 \
    --session-id 67a76380-959e-4c5a-975b-fdf7801eceb7 --adapter hcom \
    --evidence-ref hcom:attach:67a76380-959e-4c5a-975b-fdf7801eceb7
{"code": "SESSION_ATTACHED", "ok": true,
 "task": {"state": "EXPLICIT", "chain_complete": true, ...}}
```

Lease: 90 seconds, expiring `2026-09-05T02:56:29Z`.

### Tick 1 — baseline, `zora` genuinely alive (`2026-09-05T02:55:11Z`)

```
$ python3 -m runtime.cli --db .maps/state/maps.db recovery-tick \
    --enforce-canonical-run --harness-project-id maps-lean --repo-root "$PWD" \
    --hcom-dir /home/home/.hcom --binding "hila-worker-3=zora"
{"actions": [], "error": "", "ok": true, "opened_incidents": []}
```

`.maps/state/recovery.json` after: `"last_live": {..., "zora": true}` — the
first correctly-observed real "alive" reading of this whole exercise (both
prior attempts, with the hcom-dir and binding-name bugs still present, showed
`false` for a genuinely-alive session).

`zora`'s process (PID 14470) then killed: `kill -9 14470`; confirmed gone
(`ps -p 14470` → no such process) and confirmed absent from
`hcom list --json` at `/home/home/.hcom` immediately after.

### Tick 2 — transition, `zora` process killed (`2026-09-05T02:55:27Z`)

```
$ python3 -m runtime.cli --db .maps/state/maps.db recovery-tick \
    --enforce-canonical-run --harness-project-id maps-lean --repo-root "$PWD" \
    --hcom-dir /home/home/.hcom --binding "hila-worker-3=zora"
{"actions": [], "error": "", "ok": true, "opened_incidents": ["RNS-c6df6df85686"]}
```

`.maps/state/recovery.json` after:

```json
"RNS-c6df6df85686": {
  "created_at": "2026-09-05T02:55:27Z", "incident_id": "RNS-c6df6df85686",
  "reason": "silent_stop", "resume_after": "2026-09-05T03:10:27Z",
  "run_id": "RUN-7249d47f13e646f2aabc04f3e7e12bee",
  "session_name": "zora", "state": "scheduled",
  "task_id": "DEC003B-A2-3", "worker_id": "hila-worker-3"
}
```

`run_id` resolved correctly (contrast with the abandoned `dec003-stall-nate`
incident, `run_id: null`, above) — confirms Bug 2's workaround closed the
lineage-resolution gap. `resume_after` = +900s exactly, matching the
undocumented, non-CLI-configurable `silent_stop_probe_delay_seconds` default
traced in the 2026-09-04 note.

### Wait: ~960 seconds (past `resume_after`), then

### Tick 3 — resume attempt (`2026-09-05T03:11:53Z`)

```
$ python3 -m runtime.cli --db .maps/state/maps.db recovery-tick \
    --enforce-canonical-run --harness-project-id maps-lean --repo-root "$PWD" \
    --hcom-dir /home/home/.hcom --binding "hila-worker-3=zora"
{
  "actions": [
    {
      "action": "resume_failed", "attempt": 1,
      "error": "hcom command failed (2): hcom r --go dec003-stall-nate --headless: ",
      "harness_resume": {"attempted": false, "reason": "no_run_id_bound"},
      "incident_id": "RNS-616777848625",
      "resume_validation": {"attempted": false, "reason": "no_run_id_bound"}
    },
    {
      "action": "resume_denied", "attempt": 0,
      "error": "Deterministic Hook denied the operation.",
      "harness_resume": {"attempted": true, "code": "HOOK_DENIED", "ok": false,
                          "summary": "Deterministic Hook denied the operation."},
      "incident_id": "RNS-c6df6df85686",
      "resume_validation": {"attempted": false, "reason": "no_spec_bound"}
    }
  ],
  "error": "", "ok": true, "opened_incidents": []
}
```

**`RNS-c6df6df85686` (the `zora` incident): `action: "resume_denied"`,
`harness_resume: {attempted: true, code: "HOOK_DENIED", ok: false}`.** This is
the routable, harness-attempted denial DEC-003 pictured — not a no-op, not an
absent result. `.maps/state/recovery.json` after: `canonical_denials: 1`,
`state: "denied"`.

(The other action, `RNS-616777848625` / `dec003-stall-nate`, is the abandoned
Bug-2-affected incident — `harness_resume.reason: no_run_id_bound`, not
routable, and its own fallback direct-hcom-resume attempt
`hcom r --go dec003-stall-nate --headless` is a side effect of `tick()`'s
non-harness resume path, not something this exercise requested; it later
succeeded on its own retry and revived `dec003-stall-nate` — this was noticed
and the revived session was killed via `hcom kill dec003-stall-nate`
immediately after. It does not affect the `zora` result and is not part of
the counted evidence.)

### Denial code confirmed

`runtime/recovery/production.py:392-397`'s own docstring for
`build_canonical_harness_service` states exactly this shape: *"`CanonicalRunGuard`
... denies on absent evidence ... its first production exposure converts
currently-working resumes into `resume_denied` (the guard veto carries
`guard_code="LEASE_EXPIRED"` as an annotation; the resulting
`OperationResult.code` is `HOOK_DENIED`"*. `DEC003B-A2-3`'s task lease
(`lease_expires_at: 2026-09-05T02:56:29Z`) had been expired for over 15
minutes by the time of tick 3 (`2026-09-05T03:11:53Z`) — this is precisely the
`LEASE_EXPIRED` case the design predicted, confirmed by source, not guessed.

## Frozen regression case

```
$ python3 -m runtime.cli --db .maps/state/maps.db run-record DEC003B-A2-3 \
    RUN-7249d47f13e646f2aabc04f3e7e12bee
{"record_id": "RR-c2a1c255df41c79f332d94689ee9d5acca413cf2cbdf8090de41db523ba9ac30", ...}

$ python3 -m runtime.cli --db .maps/state/maps.db freeze-case DEC003B-A2-3 \
    RUN-7249d47f13e646f2aabc04f3e7e12bee --category RECOVERY_FAILURE \
    --fixture-file fixture.json \
    --expect canonical-run-guard-denies-expired-lease-resume \
    --expect silent-stop-incident-opens-on-live-to-dead-transition \
    --tag dec-003 --tag option-b --tag real-stall-exercise --frozen-by hila
{"case_id": "CASE-378fb326d2aceaa0cd3ceeb5ce314f8dba541a234a7331d86e6d31f24663e5c9",
 "case_kind": "MAPS_FROZEN_REGRESSION_CASE", ...,
 "promotion": {"automatic": false, "reason": "frozen cases are evaluation evidence only; passing a case cannot self-authorize a harness/policy/routing change"}}
```

Stored at
`work/regression-cases/CASE-378fb326d2aceaa0cd3ceeb5ce314f8dba541a234a7331d86e6d31f24663e5c9.json`.
Per `playbook/REPAIR_AND_LEARNING.md`, `promotion.automatic: false` — this
case is evaluation evidence for a future human repair/change decision, it does
not self-authorize one.

## Cleanup

`zora`'s process was already dead (killed for the exercise); confirmed via
`hcom list --stopped zora` (stopped, not resumable-and-forgotten) and
`hcom list -v zora` (not found — fully gone). The revived `dec003-stall-nate`
(see above) was killed via `hcom kill dec003-stall-nate`. No other throwaway
session remains.

## Boundaries honoured

No `runtime/` change (two real bugs found and documented above, neither
fixed — flagged for a follow-up task per the change boundary's explicit "if
you find yourself needing a runtime code change ... STOP and escalate," which
this is not: the exercise succeeded via a naming workaround, not a code
change). No test file touched. `work/decisions/DEC-003-*.md`'s existing
authorization text is unmodified — only a new "Result" section appended
separately. Only the 7 named `CAPABILITY_CHECKLIST.md` rows are flipped, and
only because this is a genuine routable-denial SUCCESS.

## Resume prompt

DEC-003 option B's real-stall exercise is now DONE (SUCCESS) — do not
re-run it. If you are picking this up: the frozen case is
`work/regression-cases/CASE-378fb326d2aceaa0cd3ceeb5ce314f8dba541a234a7331d86e6d31f24663e5c9.json`,
the Result section is in `work/decisions/DEC-003-harness-enforcement-cluster-exit-criterion.md`,
and the 7 rows (6.4/6.5/6.16/6.22/H5/E4/L6) are flipped in
`work/roadmaps/CAPABILITY_CHECKLIST.md` citing this note + the case id. This
PR needs INDEPENDENT_REVIEW (the owner, `hila`, is not eligible to review it)
before merge — check whether that review has happened before treating the PR
as final. Two real runtime bugs were found and documented but NOT fixed here
(scope boundary): (1) `recovery-tick --hcom-dir` defaulting/overwriting env
`HCOM_DIR`, stale precedent-note guidance; (2) tag-prefix vs bare-instance-name
mismatch between `hcom list --json` and `HcomAdapter._stopped_records_from_events()`,
which strands `run_id: null` on any silent-stop incident for a tagged hcom
agent. Both should become their own follow-up task(s) — read this note's
"Two additional, previously-undocumented mechanical bugs" section in full
before scoping that work.
