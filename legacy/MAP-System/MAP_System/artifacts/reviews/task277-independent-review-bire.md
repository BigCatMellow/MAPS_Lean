# Review: TASK-277

- task_id: TASK-277
- reviewer: helper-review-task277-bire
- task_owner: codex-lab-kazu
- review_date: 2026-07-26
- review_claim: `claim_review("TASK-277", "helper-review-task277-bire")` returned `True`

## Verdict

CHANGES_REQUESTED

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | The report traces the source from persona prompts through functional seats, the superhero analogy, global/project separation, contract templates, capability routing, run manifests, structured submission/review, and compact memory. Its executive finding and progression table identify the late-stage role/capability/run/evidence chain as the strongest design. This matches the source's progression into the constitution, role, skill, task, routing, manifest, submission, review, fingerprint, and digest templates. |
| 2 | FAIL | Most proposal classifications are supported, including exactly 40 distinct live `tasks.role` values, no task-revision column, keyword-based helper-fit routing, the EXP-0005 94.11% bounded result, TASK-256's 100% task recall@6 with weaker source recall, and TASK-276's five observed active-table drifts. However, the “Fresh independent review” row calls the current mechanism a “Strong identity gate.” Primary code and current task evidence show that it is not: `claim_review()` compares the reviewer only with `tasks.owner`; the actual approve/reject verb has no database-backed author comparison; `validate_review.py` trusts reviewer-authored `task_owner` text; and sanctioned submission currently destroys `claimed_by` without a durable submitter event. `TASK-274` and `INS-0039` record this live gap. |
| 3 | FAIL | The two P0 recommendations are behavior-oriented, and generated active state is correctly tied to a measured failure. But role normalization is placed first while the report understates the exercised, load-bearing review-separation failure as merely an inability to prove fresh sessions. Current evidence shows a more immediate failure mode: an actual submission author can pass both no-self-review checks whenever durable owner and author differ. The roadmap must classify and prioritize that behavior accurately before treating role normalization as the first integrity prerequisite. |
| 4 | PASS | P0/P1/P2 sections separate immediate normalization/projection work, bounded manifest and submission work, later scope enforcement, retrieval experiments, and digest pilots. Every deliverable has verification; the implementation-sequence table supplies risk and prerequisite fields, with additional inline dependencies for structured submissions and scope enforcement. |
| 5 | PASS | “Do Not Adopt As Written” explicitly rejects the parallel `.map` authority tree, a duplicate constitution, permanent model-to-role binding, full-team deployment, full read/transcript logging, unenforced containment claims, automatic local-model promotion, unqualified generated memory, and profession/technique proliferation, with reasons. |

## Files Reviewed

- `/home/mellow/Projects/MultiAgentProject/roles_in_MAP_system.md`
- `MAP_System/tasks/TASK-277.json`
- `MAP_System/artifacts/planning/roles-system-map-improvement-review.md`
- `AGENTS.md`
- `MAP_System/AGENTS.md`
- `MAP_System/notes/review-guide.md`
- `MAP_System/shared/project-brief.md`
- `MAP_System/shared/requirements.md`
- `MAP_System/shared/decisions.md`
- `MAP_System/shared/current-state.md`
- `MAP_System/shared/hpom.md`
- `MAP_System/shared/agent-capability-matrix.md`
- `MAP_System/db/claims.py`
- `MAP_System/scripts/map_task.py`
- `MAP_System/scripts/validate_review.py`
- `MAP_System/graph/runner.py`
- `MAP_System/tasks/TASK-274.json`
- `MAP_System/emergence/insights/INS-0039-both-no-self-review-guards-key-on-tasks-owner-so-owner-claimant-.md`
- `MAP_System/artifacts/tests/task-shared-state-table-validator-delivery-note.md`
- `MAP_System/artifacts/experiments/task-fingerprint-index-pilot-2026-07-19.md`
- `MAP_System/artifacts/reports/system-improvement-iteration-2026-07-18.md`

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/artifacts/planning/roles-system-map-improvement-review.md:69` | The report describes MAP's current no-self-review/claim/artifact combination as a “Strong identity gate,” then frames the missing piece as proof of fresh-session independence. That classification is materially inaccurate. `MAP_System/db/claims.py:451-462` compares the reviewer with `tasks.owner`, not the submission author. `MAP_System/scripts/map_task.py:269-295` permits the terminal review transition without a database-backed author comparison and allows review without an atomic claim. `MAP_System/scripts/validate_review.py:63-72` compares two fields supplied inside the review artifact itself. `TASK-274` confirms that sanctioned submission clears `claimed_by` and emits no durable authorship record. This means the actual author can self-review after ordinary owner/author drift; the gap is exercised and load-bearing, not just a session-freshness limitation. | Reclassify current independent review to disclose the owner-versus-submitter guard gap explicitly. Distinguish three separate concerns: atomic duplicate-review claiming, submission-author no-self-review enforcement, and fresh run/session independence. Update the roadmap priority/dependency logic so durable submission authorship and the follow-on author-keyed guard are treated according to their observed integrity impact; do not imply role normalization fixes review independence by itself. |

## Forbidden Changes Check

- PASS: Only this review artifact was written.
- PASS: The submitted report, task record, workflow graph, shared state, decisions, runtime, and implementation files were not edited.
- PASS: All runtime and SQLite verification was read-only except the required atomic review claim.

## Verification

- `claim_review("TASK-277", "helper-review-task277-bire")` - PASS; returned `True` before substantive review and created the open review record for this identity.
- Read-only SQLite role query - PASS; found exactly 40 distinct `tasks.role` values, including provider/model labels and sentence-like roles.
- Read-only `PRAGMA table_info(tasks)` - PASS; no task revision or run identity columns exist.
- Direct inspection of `MAP_System/graph/runner.py:418-433` - PASS; helper-fit routing uses task type, role, and description/title keywords.
- `python3 MAP_System/scripts/validate_shared_state_tasks.py` - PASS; 7 active-lane rows match live `map.db`.
- `python3 MAP_System/scripts/validate_task_mirrors.py` - PASS; canonical SQLite task state matches file and graph mirrors.
- EXP-0005 primary artifacts - PASS; the retained control was 44,432 bytes, the treatment 2,619 bytes, all six rubric rows passed, and the result explicitly did not authorize production adoption.
- TASK-256 primary artifact and independent review - PASS; task recall@6 was 1.0 while primary-source recall was 68.75%, supporting “promising, not production-ready.”
- TASK-276 delivery evidence and current-state - PASS; they record the fifth same-day drift and explain that ordinary listed-task transitions drift the hand-maintained table until edited.
- Direct inspection of `claims.py`, `map_task.py`, `validate_review.py`, `TASK-274`, and `INS-0039` - FAIL for the report's “Strong identity gate” classification, for the reasons in the REQUIRED finding.

## Risks Identified

- Approving the report as written would preserve a misleading architecture baseline: a later implementer could prioritize role vocabulary while believing review authorship is already mechanically protected.
- The required correction must not naively compare against `claimed_by`, because sanctioned submission clears it. The durable submission-author record described by `TASK-274` is a prerequisite to an author-keyed enforcement change.

## Notes

- The report is otherwise strong, concise, and grounded. The required change is narrow but material because acceptance criteria 2 and 3 explicitly require accurate current-state mapping and failure-impact prioritization.
- No new implementation requirement is introduced here; the authorship gap and sequencing already exist in current primary MAP evidence.
