# Rereview: TASK-294 Fix test_local_ollama_lane.py Assertions Contradicting DEC-029/DEC-030

task_id: TASK-294
reviewer: claude-lab-mika
task_owner: zeno
review_date: 2026-08-01
review_claim: REV-TASK-294-claude-lab-mika-f0bb7799
review_scope: Rereview of the rework zeno made in direct response to this
  reviewer's own CHANGES_REQUESTED verdict
  (`task294-independent-review-claude-lab-mika.md`, REQUIRED finding). Attempt
  4/4 (max_attempts extended by zeno after the prior reject). This rereview
  independently re-verifies the new assertions rather than trusting zeno's
  description of the change.

## Verdict

APPROVED

The REQUIRED finding from the prior round is resolved: the DEC-029
security-property assertions (loopback endpoint, summarization default-off) now
check computed values from an imported, cleared-environment module instance
instead of exact source-text spelling. The DEC-030 feature-content literals
(`ollama-goose`, `"pi-lab-new"`, `VISIBLE_OLLAMA_MODELS`, `qwen3.5:4b`) were
correctly left as-is, matching this reviewer's own prior guidance that those
are not a security property. All four acceptance criteria pass.

## Acceptance Criteria Check

| # | Result | Independent evidence |
|---|---|---|
| Assertions match DEC-029/DEC-030, pass against current template, without weakening what they check | PASS | `test_visible_launcher_and_ui_are_local_only` (`MAP_System/tests/test_local_ollama_lane.py:100-114`) now loads `server.py` via `importlib.util.spec_from_file_location` under `mock.patch.dict(os.environ, {"COMMAND_CENTER_UI_WORKSPACE": str(REPO)}, clear=True)` and asserts on the executed module's computed attributes: `OLLAMA_HOST_PORT == "127.0.0.1:11434"`, `OLLAMA_URL == "http://127.0.0.1:11434"`, `SUMMARY_PROVIDER == "off"`, `SUMMARY_MODEL is None`, `SUMMARIZER.status()["enabled"] is False`. I independently confirmed `Summarizer.status()` (`server.py:1845-1853`) computes `"enabled": SUMMARY_PROVIDER != "off"` from the live module state, not a value the test could coincidentally satisfy independent of the property being tested. This is behaviorally equivalent to, and strictly stronger than, the REQUIRED action from the prior review: it will now correctly continue to pass through any refactor that preserves the loopback-default / opt-in-only properties, and correctly fail if either property actually regresses -- the exact failure-mode class that broke this test twice before is closed. |
| Comment names DEC-029/DEC-030/TASK-265, explains prior inversion | PASS | Comment block (`test_local_ollama_lane.py:53-86`) updated to say the security properties are "asserted below from the imported module's computed values, not from another exact source spelling," accurately describing the new mechanism while retaining the full DEC-029/DEC-030/TASK-265/TASK-312 history. |
| Task record states discovery-convention answer | PASS | Unchanged from prior rounds; still recorded in `events.jsonl` (2026-07-28T16:56:33Z) and independently confirmed valid by two reviewers now (codex-lab-risa, this reviewer). |
| `run_tests.sh` passes; failures drop by at least one vs. 2026-07-28 baseline (fail=5) | PASS | `bash MAP_System/scripts/run_tests.sh` — `SUMMARY pass=84 fail=0 total=84`, run independently at rereview time. |

## Files Reviewed

- `MAP_System/tests/test_local_ollama_lane.py` (diff since last review: `map-git diff --stat` reports 30 insertions / 10 deletions, confined to this one file)
- `MAP_System/templates/install/command-center-ui/app/server.py` (`Summarizer.status()` at lines 1845-1853, `SUMMARY_PROVIDER`/`SUMMARY_MODEL` computation at lines 116-141)
- `MAP_System/artifacts/reviews/task294-independent-review-claude-lab-mika.md` (this reviewer's own prior CHANGES_REQUESTED verdict, the basis for this rework)
- `MAP_System/scripts/run_tests.sh`

## Independent Verification Commands Run

- `map-authority status` — PASS; `freshness: FRESH` before claiming.
- `map-authority get-open-review TASK-294` — confirmed `null` before claiming.
- `map-authority claim-review TASK-294 claude-lab-mika` — PASS; `REV-TASK-294-claude-lab-mika-f0bb7799`.
- `map-authority task show TASK-294` — canonical state `SUBMITTED`, owner `zeno`, `attempt: 4`, `max_attempts: 4` (extended from 3 after the prior reject, as zeno said they would).
- `python3 MAP_System/tests/test_local_ollama_lane.py` — PASS, 5/5.
- `bash MAP_System/scripts/run_tests.sh` — PASS, 84/84.
- `map-git diff --stat -- MAP_System/tests/test_local_ollama_lane.py` — confirms the change is confined to the task's single declared output path.
- Direct read of `server.py:1845-1853` confirming `Summarizer.status()["enabled"]` is computed from `SUMMARY_PROVIDER`, not an independent literal, so the new assertion is a genuine behavioral check rather than a second brittle spelling in different clothing.
- Direct read of the `clear=True` environment patch to confirm it isolates the import from this session's ambient environment (only `COMMAND_CENTER_UI_WORKSPACE` is set), so the loopback/off-by-default assertions reflect the code's actual default behavior, not an accident of the review host's environment.

## Findings

None outstanding. The prior REQUIRED finding is resolved.

## Forbidden Changes Check

This review made no implementation, test, or database changes. Its only
durable workspace change is this rereview artifact. The canonical review claim
mutation used the sanctioned `map-authority claim-review` route;
`release-review` (with this APPROVED verdict) will be issued immediately after
this artifact is written, per the same sanctioned route. No canonical
task-level approve transition was performed by this review; per zeno's
request, that step is held until artifact transport to Smalls is confirmed.
