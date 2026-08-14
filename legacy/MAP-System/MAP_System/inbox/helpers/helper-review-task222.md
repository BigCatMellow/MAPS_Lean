# Helper Assignment — TASK-222 Independent Review

- Owner: codex-lab-lilo
- Helper tag: helper-review-task222 (Claude attempt `maso`, stopped; Codex replacement `zulu`)
- Status: COMPLETE — Codex helper `zulu` approved TASK-222; review artifact recorded.
- Reason: TASK-222 is SUBMITTED; claude-lab-gome went idle without responding to the review request. A Claude helper (`maso`) also stopped without responding. The operator directed Codex helpers as the temporary fallback until Claude returns.
- Objective: Independently review `MAP_System/artifacts/research/SUMMARY-clearfront-delivery-systems-comparative-study-2026-07-17.md` against all TASK-222 acceptance criteria.
- Inputs: `MAP_System/tasks/TASK-222.json`, the research summary, directly cited local evidence, and cited primary-source links as needed.
- Required output: A review artifact under `MAP_System/artifacts/reviews/` with an APPROVED, CHANGES_REQUESTED, or BLOCKED verdict and concrete findings.
- Permissions: Read repository evidence and public cited sources; write only the review artifact and normal TASK-222 review state/events. Do not edit the research summary.
- Stopping condition: Stop after recording the independent verdict and reporting it to codex-lab-lilo through hcom.
- Conflict: The helper must claim review atomically and must not be the TASK-222 owner.

## Temporary routing rule

Until a Claude core session is confirmed responsive again, do not wait on or launch Claude for routine helper work. Launch a bounded Codex helper in a visible `wezterm-tab`, record its assignment durably, and report its result through hcom or an artifact. Re-evaluate this rule when Claude successfully responds to a direct readiness check.
