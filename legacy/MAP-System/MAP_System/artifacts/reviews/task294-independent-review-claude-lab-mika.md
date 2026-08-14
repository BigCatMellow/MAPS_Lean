# Review: TASK-294 Fix test_local_ollama_lane.py Assertions Contradicting DEC-029/DEC-030

task_id: TASK-294
reviewer: claude-lab-mika
task_owner: zeno
review_date: 2026-08-01
review_claim: REV-TASK-294-claude-lab-mika-c590f434
review_scope: Fresh Biggie-local review requested by zeno (task315-task294-review
  #9322). This is the third review round (attempt 3/3): codex-lab-risa's
  2026-07-29 review (`task294-independent-review-risa.md`) returned
  CHANGES_REQUESTED with a REQUIRED finding to rebase the SUMMARY_MODEL/
  SUMMARY_PROVIDER assertions on stable security behavior rather than one exact
  assignment/guard spelling; the task was then reworked again after TASK-312
  found it stale a second time. This review independently re-checks from
  current canonical state whether that REQUIRED finding was actually resolved,
  not just re-patched to match the newest code shape.

## Verdict

CHANGES_REQUESTED

The four acceptance criteria pass mechanically today (all tests green, full
suite 84/84), but acceptance criterion 1's "without weakening what it checks"
condition is not met: the fix re-aligned the same brittle exact-source-text
assertion style codex-lab-risa's prior REQUIRED finding explicitly asked to be
replaced, rather than rebasing onto behavior. This recreates the identical
brittleness class two review rounds have now hit against server.py's evolving
SUMMARY_PROVIDER/OLLAMA_HOST_PORT internals, and it currently provides no
behavioral (import-and-execute) coverage that summarization actually defaults
to off.

## Acceptance Criteria Check

| # | Result | Independent evidence |
|---|---|---|
| Assertions match DEC-029/DEC-030, pass against current template, without weakening what they check | PARTIAL / FAIL on "without weakening" | Currently passes (`python3 MAP_System/tests/test_local_ollama_lane.py` — 5/5). However `test_visible_launcher_and_ui_are_local_only` still checks `OLLAMA_HOST_PORT`, `OLLAMA_URL`, and all four `SUMMARY_PROVIDER`-related lines via exact `... in server_text` literal-string matches (`MAP_System/tests/test_local_ollama_lane.py:99-104`), the same assertion style codex-lab-risa's 2026-07-29 review (`task294-independent-review-risa.md`, REQUIRED finding) said to replace with a test of "stable security behavior (loopback endpoint; summarization disabled by default; no silent ambient endpoint inheritance) rather than one exact assignment/guard spelling." The literals were updated to match the current `SUMMARY_PROVIDER` shape (confirmed present verbatim in `MAP_System/templates/install/command-center-ui/app/server.py:127-141`), not rebased onto behavior. `test_ui_discovery_forces_loopback_despite_ambient_host` (same file, pre-existing, untouched by TASK-294) does correctly behavior-test the ambient-`OLLAMA_HOST`-non-inheritance property by importing the module and mocking `subprocess.run` — proving a behavioral approach is feasible in this file — but no equivalent behavioral test exists for "summarization defaults off absent explicit opt-in," which is asserted only via the brittle literals above. |
| Comment names DEC-029/DEC-030/TASK-265, explains prior inversion | PASS | `test_local_ollama_lane.py:53-86` names all three records and explains the OLLAMA-endpoint consolidation, the DEC-030 launcher merge, and the TASK-312 `SUMMARY_PROVIDER` follow-up drift, each with dated rationale. |
| Task record states discovery-convention answer for non-`test_command_center_*`-prefixed CommandCenterUI tests | PASS | Recorded in `MAP_System/events/events.jsonl` (2026-07-28T16:56:33Z, mapfinish-kino, task_id TASK-294): `run_tests.sh` registers every test file explicitly by name rather than a `test_command_center_*` glob, so it already catches this file; the actual gap was `task265-review-fera` manually re-running a hand-picked subset instead of the authoritative script. codex-lab-risa's prior review independently confirmed this same answer as PASS; unchanged since, still valid. |
| `run_tests.sh` passes for this check; total failures drop by at least one vs. the 2026-07-28 baseline (fail=5) | PASS | `bash MAP_System/scripts/run_tests.sh` — `SUMMARY pass=84 fail=0 total=84`, run independently at review time. `local_ollama_lane_test` is in the passing set. |

## Files Reviewed

- `MAP_System/tests/test_local_ollama_lane.py`
- `MAP_System/templates/install/command-center-ui/app/server.py`
- `MAP_System/shared/decisions.md` (DEC-029, DEC-030)
- `MAP_System/tasks/TASK-294.json`
- `MAP_System/events/events.jsonl` (TASK-294 event history, all rounds)
- `MAP_System/artifacts/reviews/task294-independent-review-risa.md` (prior review; read for the REQUIRED finding text, not relied on to inherit its evidence)
- `MAP_System/scripts/run_tests.sh`

## Independent Verification Commands Run

- `map-authority status` — PASS; `freshness: FRESH` before claiming.
- `map-authority get-open-review TASK-294` — confirmed `null` before claiming.
- `map-authority claim-review TASK-294 claude-lab-mika` — PASS; `REV-TASK-294-claude-lab-mika-c590f434`.
- `map-authority task show TASK-294` — canonical state `SUBMITTED`, owner `zeno`, `attempt: 3`, `max_attempts: 3` (this is the final permitted attempt at current limits; a further rework would need `extend-attempts`, a decision for the task owner/operator, not this review).
- `python3 MAP_System/tests/test_local_ollama_lane.py` — PASS, 5/5.
- `bash MAP_System/scripts/run_tests.sh` — PASS, 84/84.
- Direct read of `server.py:110-141` confirming the exact `SUMMARY_PROVIDER`/`OLLAMA_HOST_PORT`/`OLLAMA_URL` source lines the test asserts against verbatim.
- Direct read of `test_ui_discovery_forces_loopback_despite_ambient_host` confirming a behavioral test pattern (importlib module load + `subprocess.run` mock + assertion on computed values) already exists and works in this same file, establishing that a behavioral rewrite of the flagged assertions is achievable, not blocked by the file's structure.

## Finding

- severity: REQUIRED
- file: `MAP_System/tests/test_local_ollama_lane.py`
- finding: `test_visible_launcher_and_ui_are_local_only` still asserts `OLLAMA_HOST_PORT`,
  `OLLAMA_URL`, and the `SUMMARY_PROVIDER` gate via exact `... in server_text`
  source-literal matches. This is the same brittleness class codex-lab-risa's
  2026-07-29 review required be removed — it was addressed by re-matching the
  literals to the current code shape, not by testing behavior. It will break
  again on the next cosmetically-different-but-behaviorally-identical refactor
  of `server.py` (e.g., renaming `SUMMARY_PROVIDER`, restructuring the
  conditional), reproducing the exact failure mode (TASK-294 attempts 1 and 2)
  a third time.
- required_action: Replace the literal-string assertions for the DEC-029
  security property with a behavioral test, following the pattern already
  proven in the same file by `test_ui_discovery_forces_loopback_despite_ambient_host`:
  load `server.py` via `importlib.util.spec_from_file_location` with a clean
  environment (no `COMMAND_CENTER_UI_SUMMARY_PROVIDER`/`COMMAND_CENTER_UI_SUMMARY_MODEL`
  set, no `runtime/ui-settings.json`), execute the module, and assert
  `module.SUMMARY_PROVIDER == "off"` and `module.SUMMARY_MODEL is None` by
  computed value, not by source spelling. The `OLLAMA_HOST_PORT`/`OLLAMA_URL`
  loopback assertions can similarly assert `module.OLLAMA_HOST_PORT ==
  "127.0.0.1:11434"` post-import. The DEC-030 feature-content checks
  (`ollama-goose`, `"pi-lab-new"`, `VISIBLE_OLLAMA_MODELS` presence) are not a
  security property and are reasonable to leave as literal/structural checks —
  only the DEC-029 security-behavior assertions need to move.

## Forbidden Changes Check

This review made no implementation, test, or database changes. Its only
durable workspace change is this review artifact. The canonical review claim
mutation used the sanctioned `map-authority claim-review` route;
`release-review` (with this CHANGES_REQUESTED verdict) will be issued
immediately after this artifact is written, per the same sanctioned route. No
canonical task-level reject/rework transition was performed by this review;
per zeno's request, that step (and confirming artifact transport to Smalls)
is left to the task's accountable coordinator.
