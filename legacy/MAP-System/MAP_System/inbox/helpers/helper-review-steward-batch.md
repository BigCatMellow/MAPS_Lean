# Helper Assignment — TASK-223/224/225 Independent Batch Review

- Owner: codex-lab-lilo
- Helper tag: helper-review-steward
- Status: COMPLETE — TASK-223/224/225 APPROVED; final review at `MAP_System/artifacts/reviews/task223-225-batch-final-review-moku.md`.
- Routing: Claude is not confirmed responsive; operator directed visible Codex helpers until it returns.
- Objective: Independently review the operational-learning, E/I sentinel, and visible MAP Steward batch against each task's acceptance criteria and safety boundaries.
- Inputs: TASK-223, TASK-224, TASK-225 records and listed outputs; live `GET /api/map/steward`; focused test commands in the artifacts.
- Required output: One batch review artifact under `MAP_System/artifacts/reviews/` with separate verdicts for all three tasks, followed by normal review-gate actions.
- Permissions: Read repository and live localhost UI endpoints; write only the review artifact and normal review state/events. Do not edit implementation files.
- Focus: no hidden/headless model work, no unintended mutation/authority, privacy/source bounds, startup retrieval, sentinel non-promotion/deduplication, model fallback, and live UI controls.
- Stopping condition: Stop after recording durable verdicts and reporting the artifact path through hcom.
