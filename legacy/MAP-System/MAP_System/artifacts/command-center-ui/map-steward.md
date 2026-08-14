# Visible Local MAP Steward — TASK-225

- Owner: codex-lab-lilo
- Date: 2026-07-17
- Status: IMPLEMENTED, PENDING INDEPENDENT REVIEW
- Local model: `qwen3.5:4b` through Ollama

## Operator surface

Command Center's MAP sidebar now includes a MAP Steward card showing:

- idle/working/stopped state and deterministic/model/fallback mode;
- last run and local model name;
- bounded recommendations with source references;
- explicit Refresh, Ask visibly, Stop, and Resume controls;
- a bounded input summary covering actionable tasks, unavailable agents,
  active lessons, E/I candidates, and sentinel state/counts.

`Ask visibly` opens `map_steward.py --model --pretty` in a WezTerm terminal.
There is no headless model call. Refresh performs deterministic aggregation
only. Stop persists and blocks future deterministic/model runs until explicit
Resume; it does not kill or hide an agent session.

## Inputs

The steward reads only approved durable MAP sources:

- task graph actionable statuses;
- durable agent availability/RnS fields;
- promoted operational lessons;
- E/I sentinel state and non-promoted candidate queue.

It does not read raw hcom/model transcripts, source code, secrets, browser
history, or arbitrary home-directory files.

## Authority boundary

The steward writes only `agents/map-steward-state.json`. It cannot claim or
edit tasks, approve/release work, promote E/I records, modify policy, message
the operator, or spawn specialist agents. The Command Center server may open
the steward itself in a visible terminal after the operator clicks Ask visibly;
the steward cannot launch anything.

## Model behavior

The first CLI-based `qwen3.5:4b` structured-output attempts were malformed, and
the deterministic fallback worked as designed. Switching to Ollama's local
`/api/generate` endpoint with `think=false` and `format=json` produced valid
structured recommendations in about 9 seconds. The model saw only the bounded
attention packet and returned five advisory items; no actions were executed.

## Verification

- `python3 -m unittest MAP_System.tests.test_map_steward -v`: includes
  stop-then-refresh/resume and visible-input assertions.
- Combined operational-lessons, sentinel, and steward tests cover overdue and
  retired lessons, sentinel CLI/stop/schedule/UI, model fallback, and steward
  stop persistence.
- `python3 -m py_compile` passes for the steward and Command Center server.
- `node --check` passes for `chat.js`.
- Deterministic live packet correctly identified TASK-220 rework, submitted
  review queue, and seven pending E/I candidates.
- Real local-model run completed with `mode=model`, `last_error=null`.

## Known limits

- The stop flag controls future steward runs; model runs are intentionally
  short-lived rather than a persistent hidden process.
- The E/I sentinel's current recall is narrow (1/4 recent known insights), so
  steward candidate summaries must not be mistaken for comprehensive learning.
- The install template was deployed to `~/Projects/CommandCenterUI`, the
  visible application was launched, `GET /api/map/steward` returned the real
  model-backed state, and `POST /api/map/steward/control` with `refresh`
  returned a fresh deterministic packet. The live card is therefore available.
