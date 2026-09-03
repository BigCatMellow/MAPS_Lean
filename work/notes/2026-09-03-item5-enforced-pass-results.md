# Item 5 — first `--enforce-canonical-run` pass: results

**Status: DONE (run executed 2026-09-03, coordinator sana, session 26).** This
note records the first production `recovery-tick --enforce-canonical-run` pass
against the live `~/Projects/MAPS_Lean/.maps/`. It is the results counterpart to
the pre-run analysis in `work/notes/2026-09-02-ask1-control-plane-runbook.md`
(read that first — §3 traces exactly what the pass does, §8 explains why it
produces 0 denials, §6 is the 7-row table this note advances).

The pass followed **runbook §8 OPTION A**: run the documented 0-denial pass now
for the instantiation evidence; the real `resume_denied` outcome #243 pictured
stays gated on the lineage-bootstrap wiring (OPTION B), already scoped in
`work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md`.

## The pass

```bash
cd ~/Projects/MAPS_Lean
env -i HOME=$HOME PATH=$PATH HCOM_DIR="$PWD/.hcom" \
  python3 -m runtime.cli --db .maps/state/maps.db recovery-tick \
    --enforce-canonical-run --harness-project-id maps-lean --repo-root "$PWD" \
    --binding nava-worker-1=hcom-sess-nava-lbw-1
```

`--binding nava-worker-1=hcom-sess-nava-lbw-1` names the synthetic worker/session
that PR #261's lineage-bootstrap exercise (`maps run bind-session`) set up as
task `LBW-EXERCISE-1` — the one run in the live `.maps/` that carries an
`EXPLICIT` `run_session_links` ATTACH row.

### stdout (exit 0)

```
hcom `list --stopped` returned non-JSON output; reconstructing stopped-session
records from the `hcom events` stream (option C) and merging them under the
alive-only list. [...option C warn, expected...]
{"actions": [], "error": "", "ok": true, "opened_incidents": []}
```

The option-C warn (PR #276, `HcomAdapter._stopped_records_from_events()`) firing
here is the **first exercise of option C on the production enforced path** — the
`hcom list --stopped` non-JSON fallback ran, reconstructed stopped-session
records from the `hcom events` stream, merged them under the alive-only list, and
did not crash.

### `.maps/state/recovery.json` after (the only mutable artifact written)

```json
{"ambiguous_workers": {}, "incidents": {},
 "last_live": {"hcom-sess-nava-lbw-1": false},
 "terminal_sessions": {}}
```

`last_live["hcom-sess-nava-lbw-1"] = false` is the pass's one recorded
observation: the `--binding` session was evaluated for liveness via option C and
found not live. `incidents: {}` — nothing opened.

## Task truth unchanged (before == after, byte-identical via `maps ... status`)

```
LBW-EXERCISE-1  status=ACTIVE  claimed_by=nava-worker-1
lease_expires_at=2026-09-02T15:36:48Z (EXPIRED)  attempt=1/3  owner=maps-lean-nava
attention: STALE_LEASE (unchanged)
```

`CanonicalRunGuard` is `HookSideEffect.READ_ONLY` and no resume was attempted, so
no task row, lease, attempt counter, or `task_revision` moved. Matches runbook §5
("Task truth (`maps.db` `tasks` + children): nothing").

## Lineage resolvability (confirmed, read-only)

```
run_session_links row 1: RUN-6d536476052a4633af0d5679af0eb22d  ATTACH
  project_id=maps-lean  adapter_id=hcom  session_id=hcom-sess-nava-lbw-1
  evidence_ref=hcom:attach:hcom-sess-nava-lbw-1  created_by=maps-run-bind-session
=> resolve_session_run('maps-lean','hcom','hcom-sess-nava-lbw-1')
   -> RUN-6d536476052a4633af0d5679af0eb22d
```

`_resolve_run_id` **would** succeed if an incident opened — option C (#276) plus
the #261 link work together resolve the `session_id -> run_id` lineage. The
supervisor's `state == "EXPLICIT"` pre-check is satisfiable for this run.

## Why 0 incidents / 0 denials (runbook §8, OPTION A)

`observe_silent_stops` opens an incident only on an **observed live -> stopped
transition**. `nava-worker-1` / `hcom-sess-nava-lbw-1` was never a real live hcom
session — `LBW-EXERCISE-1` was created by a synthetic `maps run bind-session`
(#261). Neither `$PWD/.hcom` nor `~/.hcom` holds any event for it. The first
observation of `last_live = false` is a **baseline, not a transition**, so no
incident opens; a second tick also opens nothing (still no transition). With no
incident, `tick()` has nothing reprocessable, `_resolve_harness_binding` is never
called, `CanonicalRunGuard.__call__` never runs — 0 actions, 0 routable
bindings, 0 denials. This is runbook §8 OPTION A exactly.

## What the pass DID achieve (first production exposure, narrower than #243 pictured)

- **`build_canonical_harness_service` composition instantiated in a real enforced
  pass for the first time** — `HcomHarnessAdapter` -> `HookRegistry()` ->
  `register_canonical_run_guards(registry, CanonicalRunGuard(...))` ->
  `register_destructive_external_action_guards` ->
  `register_memory_provenance_guards` -> `HarnessService`. `HarnessService(...)`
  and `HookRegistry()` were exercised by a production enforced pass, not just a
  test.
- **Option C (#276) exercised on the production path for the first time** — the
  non-JSON `hcom list --stopped` fallback warn fired, the `hcom events`
  reconstruction ran, no crash.
- The `--binding` was resolved and `hcom-sess-nava-lbw-1` liveness evaluated via
  option C (= not live), recorded in `recovery.json` `last_live`.
- **0 opened incidents, 0 actions, 0 routable bindings, 0 denials.**
- Task truth untouched (`CanonicalRunGuard` is READ_ONLY; no resume attempted).

## Remediation: N/A

No incident parked `denied`, so runbook §4 (`maps claim --worker-id
nava-worker-1` + re-tick) has nothing to act on. A re-tick reproduces the
0-incident baseline. Reset if wanted: `rm .maps/state/recovery.json` (undo
incident state, keep DB) or `rm -rf .maps/` (full reset; all gitignored).

## A real `resume_denied` still needs runbook §8 OPTION B

The outcome #243 pictured — a currently-working resume converted to
`resume_denied` (most likely `LEASE_EXPIRED`) — is **not reachable from
`recovery-tick` against the current code**: no production path writes the
`EXPLICIT` `run_session_links` row for a **genuinely live, then stalled**
session, and the supervisor pre-checks that lineage before it would let the
adapter bootstrap it. Reaching it needs either:

- the lineage-bootstrap wiring already scoped in
  `work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md` — a production path
  that records a `run_session_links` row for a genuinely live, then stalled,
  session; or
- an engineered live -> stopped bound hcom session.

Neither is in Ask #1's scope; both are follow-ups.

## Checklist rows advanced (evidence prose only — NO status flip)

Per runbook §6 and the #263 gate discipline (#18), this pass advances the
**evidence text** of 7 rows from "composition default-off, never exposed" to
"composition instantiated in a real enforced pass on 2026-09-03; 0 incidents / 0
routable / 0 denials". **No row's STATUS column changes** — H5 / E4 / L6 / 6.4 /
6.5 / 6.16 / 6.22 all stay exactly as they were (`IN PROGRESS` / `NOT STARTED`).
None reaches `DONE` from the pass alone (runbook §6 "Summary for the gate step").
