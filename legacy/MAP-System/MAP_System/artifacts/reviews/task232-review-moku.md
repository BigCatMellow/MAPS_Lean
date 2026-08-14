# Review: TASK-232 Normalize the HPOM Comparative Research Artifact

task_id: TASK-232  
reviewer: helper-review-steward-moku  
task_owner: codex-lab-lilo

## Verdict

APPROVED

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| Comparative findings and source links are preserved in a validator-recognized SUMMARY artifact with required headings. | PASS | The former `hpom-operating-models-comparative-2026-07-18.md` path is absent and `SUMMARY-HPOM-OPERATING-MODELS-2026-07-18.md` exists. Its filename starts with `SUMMARY`; it contains every validator-required summary heading (`Question`, `Answer`, `Confidence`, `Confidence decays after`, `Open questions`, and `Downstream effect`) and no placeholder match. `validate_research_artifacts.py` passes. |
| Comparative sources, model comparison, problem-to-practice table, candidate experiments, conclusions, and restraint boundaries remain available. | PASS | The normalized summary retains six linked authoritative/primary sources; four-model comparison with fit limits; five-row problem-to-practice comparison; five explicitly non-decision candidate experiments with measures/stop rules; and source fact/MAP inference/proposal-boundary conclusions. It explicitly rejects wholesale framework import, permanent helper bureaucracy, automatic promotion, and authority expansion. |
| Current synthesis navigation points to the normalized artifact; historical evidence is not rewritten. | PASS | `SYN-0002` now names `artifacts/research/SUMMARY-HPOM-OPERATING-MODELS-2026-07-18.md`. Historical references to the former path remain in `artifacts/tests/local-ollama-advisory-lane-test-2026-07-18.md` and `artifacts/reviews/task228-review-rori.md`, where they accurately record the former validation failure. |
| Research and emergence validators pass after normalization, without policy/task/decision introduction. | PASS | `MAP_System/.venv/bin/python MAP_System/scripts/validate_research_artifacts.py` returned `PASS research validation`; `MAP_System/.venv/bin/python MAP_System/scripts/map_emergence.py validate` returned `OK emergence artifacts valid (68 checked)`. The summary's downstream effect is explicitly informational only; SYN-0002 remains `CLARIFIED`, and no task, decision, policy, or promotion output is registered. |

## Files Reviewed

- `MAP_System/tasks/TASK-232.json`
- `MAP_System/artifacts/research/SUMMARY-HPOM-OPERATING-MODELS-2026-07-18.md`
- `MAP_System/emergence/synthesis/SYN-0002-a-goal-first-evidence-budgeted-practice-loop-makes-map-coordinat.md`
- `MAP_System/scripts/validate_research_artifacts.py`

## Forbidden Changes Check

PASS — The registered former source path is absent as the intended relocation;
the normalized SUMMARY and current synthesis link are present. The two
historical review/test records that retain the old path are outside TASK-232's
registered outputs and were not rewritten.

## Verification

- `MAP_System/.venv/bin/python MAP_System/scripts/validate_research_artifacts.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/map_emergence.py validate` — PASS (`68` artifacts checked).
- Checked the normalized SUMMARY filename/required fragments against
  `MAP_System/scripts/validate_research_artifacts.py` — PASS.
- Checked current and historical old/new path references with `rg` — PASS.

## Risks

The research remains advisory. Its model comparisons and candidate experiments
are useful evidence for a future owner-reviewed proposal, not evidence that an
operating model, helper lane, policy, decision, or task promotion has been
adopted. The normalized filename fixes validator recognition without changing
that boundary.

This review does not approve/release TASK-232 or alter research, synthesis,
policy, task, or shared state.
