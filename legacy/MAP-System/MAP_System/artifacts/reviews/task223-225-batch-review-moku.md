# Review: TASK-223, TASK-224, and TASK-225

## Reviewer

- Reviewer: helper-review-steward-moku
- Date: 2026-07-17
- Scope: Independent review of operational learning, the E/I sentinel pilot,
  and the visible MAP Steward.

## Verdicts

- TASK-223: CHANGES_REQUESTED
- TASK-224: CHANGES_REQUESTED
- TASK-225: CHANGES_REQUESTED

## Reviewed Files

- `MAP_System/tasks/TASK-223.json`
- `MAP_System/tasks/TASK-224.json`
- `MAP_System/tasks/TASK-225.json`
- All output paths listed in those three task records.
- Live `GET /api/map/steward` and deterministic `refresh` control response.

## TASK-223 Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/tests/test_operational_lessons.py` | The acceptance criteria require deterministic coverage of stale/conflict validation and retirement behavior. Tests cover missing provenance, duplicate-title conflict, and `superseded`, but never exercise an overdue `review_after` lesson or a `retired` lesson. The named fallback test only proves that a pre-authored guidance string is selected for `review-routing`; it does not separately prove the stale and retirement requirements. | Add deterministic tests showing an overdue lesson is surfaced as review-due/stale and a retired lesson is excluded. Keep or strengthen the explicit Claude-unavailable-to-visible-Codex guidance assertion so the fallback scenario remains unambiguous. |

## TASK-224 Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/templates/install/command-center-ui/` | The task requires sentinel status, last run, outputs, errors, and stop control to be visible in Command Center. No sentinel-specific UI or control endpoint exists; the steward API carries nested sentinel state, but `chat.js` does not render it and exposes no sentinel scan/stop control. | Add a visible sentinel status/control surface that renders the required state and provides explicit deterministic scan/stop controls, with integration coverage. |
| REQUIRED | `MAP_System/scripts/emergence_sentinel.py` and install templates | The task requires the scanner to be runnable on a low-frequency local schedule. No timer/service/launcher schedule for the sentinel is present in the submitted outputs or installation templates. | Add and document a bounded low-frequency local schedule with visible state and stop control; do not introduce a hidden model worker. |
| REQUIRED | `MAP_System/emergence/candidates/README.md` | The documented curation example omits the CLI-required `--actor`, so the provided usage command fails argument parsing. | Update the example to include `--actor` and add a CLI-level test or smoke check for the documented curation path. |

## TASK-225 Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/templates/install/command-center-ui/src/chat.js` | The API returns a detailed `inputs` object, but `renderSteward()` displays only status/mode, last run/model or error, and recommendations. The acceptance criterion explicitly requires the Command Center to visibly show inputs. | Render the bounded input summary, including sentinel state/counts, in the steward card and cover it with UI/integration verification. |
| REQUIRED | `MAP_System/templates/install/command-center-ui/app/server.py` and `MAP_System/scripts/map_steward.py` | `stop` writes `stop_requested=true`, but the next `refresh` unconditionally runs the steward and `run()` rewrites `stop_requested=false`. The documented claim that Stop controls future runs is therefore false. | Make Stop an effective gate for future deterministic/model runs until an explicit resume/start action, or redefine and label the control honestly with matching acceptance-compliant behavior; add a stop-then-refresh test. |

## Verification

- `python3 -m unittest MAP_System.tests.test_operational_lessons MAP_System.tests.test_emergence_sentinel MAP_System.tests.test_map_steward -v` — 10/10 passed.
- `python3 MAP_System/scripts/map_emergence.py validate` — passed, 63 artifacts checked.
- `python3 MAP_System/scripts/validate_task_graph.py` — passed.
- `python3 MAP_System/scripts/validate_task_mirrors.py` — passed before verdict transitions.
- `python3 -m py_compile ...` for the three scripts and Command Center server — passed.
- `node --check MAP_System/templates/install/command-center-ui/src/chat.js` — passed.
- Live `GET http://127.0.0.1:8765/api/map/steward` — returned the steward state and bounded input data.
- Live deterministic `POST /api/map/steward/control` with `refresh` — returned a fresh packet; no model was invoked.

## Notes

- No implementation files were edited during review.
- The deterministic sentinel is correctly non-promoting and its existing scan is idempotent for exact deduplication keys.
- The steward's local-model failure path falls back deterministically in unit tests, and the submitted model prompt is bounded to the collected packet.
