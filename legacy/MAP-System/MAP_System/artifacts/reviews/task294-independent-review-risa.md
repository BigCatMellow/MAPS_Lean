# TASK-294 Independent Review

- task_id: TASK-294
- reviewer: codex-lab-risa
- task_owner: command-center
- review_date: 2026-07-29
- verdict: CHANGES_REQUESTED

## Summary

The four originally inverted expectations were corrected in the intended
direction, and the added explanation accurately anchors the launcher and
loopback expectations to DEC-029, DEC-030, and TASK-265. The submitted test
does not, however, pass against the current installer template, so the first
acceptance criterion is not met.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| Assertions match DEC-029/DEC-030 and pass against the current template without weakening the test | FAIL | `test_visible_launcher_and_ui_are_local_only()` fails at the exact-string `SUMMARY_MODEL` assertion. The current template now derives `SUMMARY_PROVIDER` and `SUMMARY_MODEL` from explicit environment or operator-owned settings and gates the worker on `SUMMARY_PROVIDER != "off"`; it no longer contains either `SUMMARY_MODEL = os.environ.get(...) or None` or `if SUMMARY_MODEL is not None:`. |
| Comment names DEC-029/DEC-030/TASK-265 and explains the prior inversion | PASS | The comment names all three records and explains the OLLAMA endpoint and launcher-entry changes. |
| Discovery convention or explanation is recorded | PASS | The comment identifies the filename-prefix miss, and the submission event explains that `run_tests.sh` explicitly registers the file; the authoritative suite, rather than a hand-picked `test_command_center_*` subset, is the discovery mechanism. |
| Authoritative check passes and failure count drops by one | FAIL | The focused file fails before a full-suite pass can be established. A full `run_tests.sh` rerun would not change this deterministic failure. |

## Required Finding

- severity: REQUIRED
- file: `MAP_System/tests/test_local_ollama_lane.py`
- finding: The fix still tests an implementation-shaped, single-line
  `SUMMARY_MODEL` assignment and guard. The current
  `MAP_System/templates/install/command-center-ui/app/server.py` no longer has
  that shape, so the task recreated the same brittleness class it was meant to
  remove and fails its own current-template criterion.
- required_action: Rebase the assertion on the stable security behavior
  (loopback endpoint; summarization disabled by default; no silent ambient
  endpoint inheritance) rather than one exact assignment/guard spelling.
  Coordinate with TASK-306's owner because that task currently owns the
  template provider changes; do not make TASK-294 silently approve or overwrite
  TASK-306 behavior. Re-run this focused file and the authoritative suite after
  the provider surface is stable.

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_local_ollama_lane.py`:
  FAIL at line 93 after two preceding tests pass.
- Read DEC-029 and DEC-030 in `MAP_System/shared/decisions.md`.
- Read released TASK-265 and its independent review evidence.
- Inspected the current template's endpoint, allowlist, launcher definitions,
  summary-provider defaults, and worker gate.
- Confirmed through `map-authority get-open-review TASK-294` that this review
  is claimed by `codex-lab-risa`.

## Scope And Independence

The reviewer is neither the task owner nor the submitter and changed no
implementation file. The only file created by this review is this artifact.
The current template change belongs to TASK-306 and was treated as concurrent
owned work, not edited or approved here.
