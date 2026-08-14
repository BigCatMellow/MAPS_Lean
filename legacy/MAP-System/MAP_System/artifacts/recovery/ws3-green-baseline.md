# WS-3 Reproducible Green MAP Baseline

- task_id: TASK-312
- owner: zeno (operator-authorized takeover from rotation-replacement-mimi-koda)
- verified_at: 2026-08-01
- environment: Biggie/KUDU, read-only mirrored production `map.db`, repository virtual environment
- result: PASS — 84 checks passed, 0 failed

## Canonical command

From the repository `Source/` directory:

```bash
bash MAP_System/scripts/run_tests.sh
```

Final summary:

```text
SUMMARY pass=84 fail=0 total=84
```

The suite includes the mirror/task/schema/shared-state validators, event and
Layer-1 checks, focused authority/Command Center checks, lifecycle/security
regressions, the isolated integration flow, and the local Ollama lane check.
Documented `SKIP` results for mechanisms that do not exist are explicit test
outcomes, not failures or hidden exceptions.

## Recovery of the seven failing checks

The approved recovery kickoff recorded 76 passing and 7 failing checks. Each
failing check is now accounted for:

1. **Active output collisions / task-graph validation** — TASK-311 resolved the
   collision set through sanctioned ownership/retirement sequencing and was
   independently approved. `validate_task_graph` now passes.
2. **Invalid Herdr research-summary contract** —
   `artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md` now has the
   required research-summary envelope and validates.
3. **New event warnings** — the one historical noncanonical
   `TASK_SUBMITTED` event was independently investigated as immediately
   self-corrected by the following canonical `SUBMISSION`; TASK-312 extended
   `events/warning_baseline.json` only through that reviewed line. No later
   warning was folded into the baseline. The event warning check passes.
4. **TASK-294 exact-code assertion** — the local Ollama lane test now asserts
   stable security behavior for DEC-029/DEC-030/TASK-265 and the current
   explicit summary-provider gate. Its five focused checks pass; TASK-294 is
   separately submitted for independent review.
5. **Layer-1 derived failure** — this was downstream of the event warning and
   passes once the reviewed warning baseline is applied.
6. **Liveness-reaper read-only fixture** — its isolated copy explicitly changes
   mode to `0644` after copying production's intentionally read-only database;
   the test passes without changing `MAP_System/map.db`.
7. **Chaos-resilience read-only fixture** — the same isolated-fixture repair is
   applied and the test passes without creating a second production writer.

## Transient current-state limitation resolved

The takeover handoff recorded one later remaining failure: a Biggie-local
`shared/current-state.md` regeneration was overwritten by Smalls' canonical
mirror export. No Biggie-side writer or exclusion was added. After the
canonical lifecycle transitions were exported by Smalls and the mirror was
refreshed, `validate_shared_state_tasks.py` reports that the active-lane table
matches `map.db`; the complete suite reproduces green. This preserves Smalls as
the sole lifecycle authority rather than working around it.

## Scope and rollback

- No unrelated user change was overwritten.
- Production `MAP_System/map.db` remains mode `0444` on Biggie.
- The fixture edits affect only temporary copied databases.
- TASK-315's checksummed pre-convergence archives and Git bundles preserve both
  hosts' pre-publication working trees.
