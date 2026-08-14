# WS-3 Finding: `liveness_reaper_test` / `chaos_resilience_test` Readonly-Fixture Failure

- found_by: claude-lab-mimi
- date: 2026-07-30
- status: documented, not fixed — TASK-312 (WS-3) is dependency-gated on
  TASK-311 and was not claimable at the time this was found; no file was
  edited to respect that gate and the one-owner-per-output-path rule this
  session already enforced on TASK-295's review.

## Root cause (confirmed, not guessed)

`MAP_System/map.db` on Biggie is mode `444` (read-only for everyone,
confirmed via `stat -c %a`) — the deliberate, correct enforcement of "Biggie
never writes canonical state."

Both `MAP_System/tests/test_liveness_reaper.py::_make_fixture_db` and
`MAP_System/tests/test_chaos_resilience.py::_make_fixture_db` do:

```python
fixture_db = Path(tmp) / "fixture-map.db"
shutil.copy(REPO / "MAP_System" / "map.db", fixture_db)
```

`shutil.copy` (unlike `shutil.copyfile`) preserves the source file's
permission bits. The intent, per the docstring, was always an "isolated,
writable copy" — that held before `map.db` became `444`; the fixture
inherited the read-only bit once it did, and every fixture write since then
(`_insert_fixture_task`'s raw `sqlite3.connect(...).execute("INSERT ...")`)
fails with `sqlite3.OperationalError: attempt to write a readonly database`.

Live evidence, this session, 2026-07-30:

```text
$ stat -c "%a %U:%G" MAP_System/map.db
444 mellow:mellow

RUN liveness_reaper_test
...
sqlite3.OperationalError: attempt to write a readonly database
FAIL liveness_reaper_test

RUN chaos_resilience_test
...
sqlite3.OperationalError: attempt to write a readonly database
FAIL chaos_resilience_test
```

## Fix (small, mechanical, not yet applied)

Add one line after each `shutil.copy` call in both `_make_fixture_db`
helpers:

```python
fixture_db.chmod(0o644)
```

This does **not** touch `map.db`'s own permissions (still `444`, still
correct) — it only makes the disposable temp-directory copy writable again,
restoring the helper's original stated intent. No other change should be
needed; both tests already assert correct behavior once the fixture is
writable, they just never get to run their assertions today.

## Scope note for whoever claims TASK-312

- Only these two files need the one-line fix:
  `MAP_System/tests/test_liveness_reaper.py`,
  `MAP_System/tests/test_chaos_resilience.py`.
- No collision at time of writing: the only other task referencing either
  file (`TASK-161`) is `RELEASED` (terminal).
- This directly addresses part of TASK-312's "seven captured failures"
  acceptance criterion — confirm against the current live failure list at
  claim time, since two days passed between the kickoff plan's original
  count and this finding (same evidence-can-go-stale pattern as INS-0058) —
  do not assume this note's failure list is still exhaustive without
  re-running the suite.
