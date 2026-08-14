# MAP Delivery Note — TASK-279 Generated Active State

- task: `TASK-279`
- implementer: `codex-lab-meba`
- source chain: TASK-276 drift evidence → TASK-277 approved P0 roadmap slice
- risk: PROCESS / DRIFT
- registered outputs: exactly the five paths owned by TASK-279

## Delivered Behavior

- `scripts/render_active_state.py` opens `map.db` read-only and generates the
  designated active-lane lifecycle columns: task ID, status, durable owner, and
  current claimant.
- `shared/active-lane-annotations.json` is the separate human-authored source
  for lane selection, order, rationale, and gate text. Regeneration never
  modifies this file.
- `shared/current-state.md` contains one marker-bounded generated block.
  Surrounding prose and unrelated tables are preserved byte-for-byte by the
  renderer and are never parsed as lifecycle truth.
- An annotation whose task is absent from SQLite is reported as `ORPHAN`.
  An annotation whose canonical task is `DONE`, `RELEASED`, or `RETIRED` is
  reported as `STALE` and omitted from the active rows. Diagnostics appear in
  both command output and the generated Markdown block.
- `--check` performs a non-writing idempotence/drift check. It exits `1` when
  the generated block differs from canonical SQLite plus the annotation source.

## Acceptance Evidence

1. **Canonical lifecycle projection.** The first live render corrected
   TASK-268 from the former hand-maintained `READY` claim to SQLite's current
   `APPROVED` status. `validate_shared_state_tasks.py` then reported that every
   generated numbered row matched `map.db`.
2. **Separate annotations.** Tests hash the annotation bytes before and after
   two renders. The bytes remain identical, and rationale/gate text remains in
   the generated table.
3. **No prose parsing; explicit stale/orphan reporting.** A fixture includes
   TASK IDs and status words in prose and a second table; both remain unchanged
   and create no lifecycle rows or diagnostics. Separate fixtures prove
   `ORPHAN` and `STALE` diagnostics.
4. **Transitions, ordering, and no-op behavior.** Focused tests mutate the
   canonical row through `READY` (claimable), `IN_PROGRESS` (claimed),
   `SUBMITTED`, `APPROVED`, and `RELEASED`, regenerating after each transition.
   The displayed state follows SQLite without an annotation or prose edit.
   Tests also prove annotation-order determinism and a byte-identical repeated
   no-op render.
5. **Migration validators.** The TASK-276 table validator remains active as an
   independent projection consistency test. Shared-state, task-mirror, task
   graph, and task-schema validators are run before submission.

## Migration

The migration seeded the seven prior hand-maintained lanes into
`active-lane-annotations.json`, preserving their human purpose and gate text
while removing lifecycle claims from that source. The old table and its stale
maintenance narrative were replaced by the marker-bounded generated block.

Regenerate:

```bash
MAP_System/.venv/bin/python MAP_System/scripts/render_active_state.py
```

Verify without writing:

```bash
MAP_System/.venv/bin/python MAP_System/scripts/render_active_state.py --check
MAP_System/.venv/bin/python MAP_System/scripts/validate_shared_state_tasks.py
```

## Rollback

Rollback is file-local and does not mutate SQLite:

1. Restore the pre-migration active-lane section in `shared/current-state.md`
   from version control or the task diff.
2. Stop invoking `render_active_state.py`.
3. Retain `validate_shared_state_tasks.py`; it will resume detecting drift in
   the restored numbered table.
4. The renderer and annotation JSON can remain unused or be removed in the
   same rollback change. No database schema or data rollback is required.

## Focused Test Evidence

Commands and expected successful results:

```text
python MAP_System/tests/test_render_active_state.py
  6 tests, OK

python MAP_System/scripts/render_active_state.py --check
  current-state.md: unchanged

python MAP_System/scripts/validate_shared_state_tasks.py
  active-lane table matches map.db

python MAP_System/scripts/validate_shared_state.py
  23 files checked; 0 failures; 0 warnings

python MAP_System/scripts/validate_task_mirrors.py
  passed

python MAP_System/scripts/validate_task_graph.py
  passed
```

Repository-wide suite:

```text
bash MAP_System/scripts/run_tests.sh
  SUMMARY pass=74 fail=3 total=77
```

The three failures are unrelated pre-existing repository findings:

- `validate_research_artifacts`: the HERDR summary lacks the required research
  template fragments.
- `validate_events_no_new_warnings`: legacy `TASK_SUBMITTED` at event line 2145.
- `validate_layer1_test`: cascades from the same event-validator failure.

The suite's TASK-276 live projection check and all 14 TASK-276 isolated tests
passed. TASK-279's six focused tests also passed separately.
