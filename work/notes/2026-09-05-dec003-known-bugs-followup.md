# DEC-003 exercise — two known bugs, not fixed (out of scope for #298)

Source: found during PR #298's DEC-003 option B "real resume_denied" exercise
(coordinator mizo, session 32). Neither blocked #298; both are cataloged here
for a future pick-up. This is a bug note, not a task contract or a fix attempt.

## Bug 1 — `recovery-tick --hcom-dir` silently overrides `HCOM_DIR` env var

Location: `runtime/communication/hcom_adapter.py:88-91`
(`HcomAdapter.environment()`):

```python
def environment(self) -> dict[str, str]:
    env = os.environ.copy()
    env["HCOM_DIR"] = str(self.hcom_dir)
    return env
```

`self.hcom_dir` is set from the adapter's `hcom_dir=` constructor argument
(default `".hcom"`), which callers wire from `--hcom-dir`. Because
`environment()` unconditionally overwrites the copied `HCOM_DIR` key, a shell
that has already exported `HCOM_DIR` to point at a specific session's hcom
directory gets silently redirected to whatever `--hcom-dir` resolved to (or
the `.hcom` default) for every subprocess call this adapter makes — no
warning, no error.

Cost observed: during the DEC-003 exercise this cost two wasted
`recovery-tick` attempts before the mismatch was noticed (the tick was
reading/writing the wrong hcom directory).

Repro:
1. `export HCOM_DIR=/path/to/session-A/.hcom`
2. Run a command that constructs `HcomAdapter()` with a different or default
   `hcom_dir` (e.g. `maps recovery-tick` without `--hcom-dir` matching
   session A, or with an explicit `--hcom-dir` pointing elsewhere).
3. Observe the subprocess's effective `HCOM_DIR` is the adapter's resolved
   `hcom_dir`, not the shell's exported value — confirm via the tick acting on
   the wrong session's events/messages.

Not fixed: precedence between the shell's `HCOM_DIR` and an explicit
`--hcom-dir`/`hcom_dir=` argument was not decided during #298; that's a
product-behavior call (which should win, and whether to warn on conflict),
not a mechanical fix.

## Bug 2 — tag-prefix vs bare-instance-name mismatch strands `run_id: null`

Location: `runtime/communication/hcom_adapter.py`, the option-C
stopped-session reconstruction path (`HcomAdapter._stopped_records_from_events`,
~line 218-280, dedup/merge at ~line 210-215) — see
`work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md` and
`work/notes/2026-09-03-item5-optionC-impl.md` for the original option-C design.

`_stopped_records_from_events` derives each record's `name` from the `hcom
events` stream's `instance` field (line ~263:
`name = str(event.get("instance") or "").strip()`). For a tagged agent
(spawned with `--tag <label>`), the alive path's `hcom list --json` reports
the tag-prefixed name (e.g. `housekeep-zale`), but observed `events` records
for the same agent carry the bare CVCV instance name alone (e.g. `zale`) in
at least some cases. The dedup at line 210
(`alive_names = {str(item.get("name") or "") for item in alive}`) and the
downstream `session_id -> run_id` reverse lookup
(`RecoverySupervisor._resolve_run_id`) both key on this `name` string, so a
tag-prefix/bare-name mismatch means:
- a stopped tagged agent's synthesized record isn't recognized as a duplicate
  of its (already-gone) alive entry, and/or
- the reverse lookup never matches the record to a `run_id`, leaving
  `run_id: null` for any tagged hcom agent reconstructed via option C after
  it stops.

Not confirmed: which side (events vs `list --json`) is bare vs prefixed in
which agent-spawn configurations, and whether this reproduces for every tag
or only specific spawn paths. Needs a live repro capturing both `hcom list
--json` and raw `hcom events` output for the same tagged agent across a
stop transition before a fix is scoped.

Repro sketch (not yet executed to full confirmation):
1. Spawn a tagged hcom agent: `hcom 1 claude --tag sometag`.
2. Capture `hcom list --json` while it's alive — note the `name` field.
3. Stop the agent; capture `hcom events --last 200` and find its `status`/`life`
   stop event — note the `instance` field.
4. Compare the two name strings; if they differ, trigger the option-C fallback
   (`hcom list --stopped` non-JSON case) and confirm the resulting synthesized
   record's `run_id` comes back `null` due to the mismatch.

## Disposition

Both are candidates for `work/ideas/` (E/I capture) or a shaped `work/tasks/`
contract once someone picks this up; neither is fixed here. No runtime code
touched by this note.
