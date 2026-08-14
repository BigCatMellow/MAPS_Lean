# Review: TASK-231 Helper-Note Activity Metadata

```text
task_id: TASK-231
reviewer: helper-librarian-rori
review_date: 2026-07-18
task_owner: codex-lab-lilo
```

## Verdict

APPROVED

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | `AGENTS.md` provides a copyable manual helper-note metadata block with status, owner, scope, and creation fields, and names the active values recognized by the runner. | PASS | The new contract includes `status`, `owner`, `provider`, `created_at`, and `scope`, and names `active`, `running`, and `in_progress`. Independent inspection of `read_helper_note_metadata` and `scan_helper_notes` confirms plain bullet parsing and the same three active values. `complete`, `stopped`, and `superseded` are accurately presented as non-active final examples. |
| 2 | Graph documentation identifies helper-note metadata as the source of helper-capacity accounting and points to the canonical contract. | PASS | `graph/README.md` says `scan_helper_notes` counts durable note metadata, not terminal visibility or prose headings, and points to the `MAP_System/AGENTS.md` helper-note metadata contract. |
| 3 | A focused regression test proves a manually authored active helper note is counted while a non-active note is not. | PASS | `test_runner_helper_notes.py` creates `active` and `complete` notes, calls the existing `scan_helper_notes`, and asserts only `helper-active` appears in `active_helper_notes`; it also verifies both parsed statuses. |
| 4 | The focused regression test is registered in `run_tests.sh` and passes with the existing runner. | PASS | `run_tests.sh` registers `runner_helper_notes_test` with the project virtual-environment Python. Independent focused execution passed, and `bash -n` confirmed valid shell syntax. No runner code changed. |

## Files Reviewed

- `MAP_System/AGENTS.md`
- `MAP_System/graph/README.md`
- `MAP_System/tests/test_runner_helper_notes.py`
- `MAP_System/scripts/run_tests.sh`
- Read-only implementation reference: `MAP_System/graph/runner.py` metadata parsing and capacity classification

## Forbidden Changes Check

- PASS: no changes to `MAP_System/graph/runner.py`; runner behavior is unchanged.
- PASS: documentation makes durable metadata explicit without expanding helper ownership, approval, release, routing, or policy authority.
- PASS: the test exercises existing behavior and does not mutate durable project state.
- PASS: reviewer `helper-librarian-rori` is independent of task owner `codex-lab-lilo`.
- PASS: pre-existing shared-file edits are not attributed to TASK-231. In particular, the visible-terminal policy edit in `MAP_System/AGENTS.md` and the `local_ollama_lane_test` registration in `run_tests.sh` are outside this task's additions. The separately reported HPOM research-artifact validation failure is also unrelated and was not attributed to TASK-231.

## Commands Run

```bash
MAP_System/.venv/bin/python MAP_System/tests/test_runner_helper_notes.py
bash -n MAP_System/scripts/run_tests.sh
MAP_System/scripts/map-git diff -- MAP_System/AGENTS.md MAP_System/graph/README.md MAP_System/tests/test_runner_helper_notes.py MAP_System/scripts/run_tests.sh
```

Focused result: `PASS manual active helper note counts; terminal note does not`.

## Risk

Low. The change documents and tests existing runner behavior rather than changing it. The focused test covers the requested active/non-active distinction; it does not exhaustively parameterize every documented active and final example, but direct source inspection confirms the documented active set and all other status strings remain non-active.
