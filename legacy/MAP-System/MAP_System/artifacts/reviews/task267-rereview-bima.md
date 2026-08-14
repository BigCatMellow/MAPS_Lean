# Review: TASK-267 — Re-align MAP project vision, current state, and active execution lanes

task_id: TASK-267
reviewer_id: claude-lab-bima
task_owner: codex-lab-lime

## Verdict

CHANGES_REQUESTED

One REQUIRED finding. Three of Kiri's four prior findings are fully closed and
the fourth (RECOMMENDED) is closed. The rework is substantially correct; it is
rejected for a single factual state claim that is the same defect class the
prior review rejected, repeated four times across two canonical files.

## Context

Independent re-review under operator option A (hcom #12415). Durable owner is
`codex-lab-lime` (`inactive/session_superseded`); `codex-lab-kula` performed
the rework and submitted. This reviewer is independent of both and authored
none of the reviewed content. Review slot claimed via `claim_review()`
(returned True). Per INS-0039 the mechanical self-review guards would not have
enforced that separation on this task; it was enforced operationally.

## Files Reviewed

- `MAP_System/artifacts/planning/map-project-realignment-2026-07-22.md`
- `MAP_System/shared/current-state.md`
- `MAP_System/shared/project-brief.md`
- `MAP_System/shared/canonical-repo.md`
- `MAP_System/shared/agent-capability-matrix.md`
- `MAP_System/shared/hpom.md`
- `MAP_System/handoffs/HANDOFF-TASK-267-kula-to-bima.md`
- Prior findings: `MAP_System/artifacts/reviews/task267-review-kiri.md`
- Live `map.db` (read-only), runner output, `task_release_records`, event history

## Acceptance Criteria Check

| Criterion | Result | Evidence |
|---|---|---|
| Concise durable alignment memo states approved vision and non-goals | PASS | One-sentence vision and the six-point operating picture agree with DEC-008, DEC-014, DEC-028. Non-goal ("not a reason to keep building coordination infrastructure indefinitely") is explicit and consistent with the delivery posture. |
| Memo reconciles every active task, owner/lane, gate, and execution order | PASS | Both tables now carry separate `Durable owner` and `claimed_by` / current-worker columns. Spot-checked all six rows against live `map.db`: TASK-254, TASK-263, TASK-265, TASK-267, TASK-268, TASK-236 all match on status, owner, and claimant. TASK-263's expired lease (`2026-07-22 22:03:00`) is correctly reported as expired rather than treated as liveness. |
| Brief/current-state refreshed only where verified facts changed | FAIL | TASK-186 is correctly RELEASED and the stale validation count is corrected to a reproduced 23/23. But TASK-266 is stated as RELEASED in four places while `map.db` says APPROVED with no release record; see finding 1. |
| Roles and authority boundaries explicit | PASS | Core/Pi/helper/operator boundaries are stated in the memo, brief, and capability matrix. Pi remains exploratory-only with no canonical-write, task, review, routing, or release authority. No authority was widened. |
| Validators pass and an independent reviewer can verify every claimed fact | FAIL | All five validators reproduced green independently, but the TASK-266 release claim is verifiably false against the authoritative source; see finding 1. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/shared/current-state.md` (lines 46, 54–55); `MAP_System/artifacts/planning/map-project-realignment-2026-07-22.md` (TASK-268 row, and the sentence following the Active Task Snapshot table) | TASK-266 is stated as RELEASED in four places. Live `map.db` gives `status = APPROVED`, its most recent event is `APPROVED` by `codex-lab-lime` at `2026-07-22T19:11:43Z`, and `task_release_records` contains no row for it (TASK-186 does have one). This is the same defect class as Kiri's REQUIRED finding 1: a high-confidence canonical file publishing a task state the database contradicts. It is not cosmetic — it erases a real outstanding release step, and it contradicts this same file's documented gate at line 164, "RELEASED requires completed checklist + record." A reader would conclude TASK-266 is fully closed and never release it. | State TASK-266 as APPROVED, pending release. Keep the TASK-268 conclusion but correct its stated reason: the dependency is satisfied because `graph/runner.py` `DEPENDENCY_SATISFIED_STATUSES = {"DONE", "APPROVED", "RELEASED"}` accepts APPROVED, not because TASK-266 is released. Leave TASK-186 as RELEASED — that one is correct and release-recorded. |
| RECOMMENDED | `MAP_System/shared/current-state.md` (line 41) | The lane table records TASK-267 itself as IN_PROGRESS; it is now SUBMITTED. The explicit `2026-07-22 22:34 EDT` snapshot timestamp is the remedy Kiri required and it works as designed here, so this is not counted as a factual error. But the file will carry a stale self-reference through release unless refreshed. | Refresh the TASK-267 row as part of the release step rather than re-editing now, which would only move the state again. |

## Prior Findings Disposition

| Prior finding | Status | Evidence |
|---|---|---|
| REQUIRED 1 — TASK-186 published as blocked; stale 21/21 count; no as-of timestamp | CLOSED | TASK-186 verified RELEASED in `map.db` with a release record by `claude-lab-gabi` at `2026-07-22T21:48:52Z`, and removed from active lanes. `validate_shared_state.py` independently reproduced 23/23; the file claims 23/23. Both tables carry an explicit `2026-07-22 22:34 EDT` snapshot time. |
| REQUIRED 2 — missing owner/claimant fields; stale owners silently replaced | CLOSED | Both tables now separate durable owner from `claimed_by`/current worker. TASK-267's own stale owner is named as a visible reconciliation gap in three places rather than rewritten to the claimant, which is what the finding asked for. |
| REQUIRED 3 — `canonical-repo.md` contradicts active DEC-014 | CLOSED | The file now preserves `/home/home/Projects/MultiAgentProject` as DEC-014's still-active literal path and the decision-era spelling of the same logical checkout, states "TASK-267 does not amend or supersede that active decision," and separates the host-resolved path from the logical one. Only `/home/home/Downloads/MultiAgentProject` is called retired. This takes Kiri's second offered option; no decision was invented. |
| RECOMMENDED 4 — capability matrix embeds a volatile roster | CLOSED | Live session names removed; replaced with an explicit instruction to run `hcom list` before assigning or messaging a live worker. |

## Forbidden Changes Check

| Boundary | Result | Evidence |
|---|---|---|
| Do not invent architecture or authority | PASS | No new runtime architecture. The DEC-014 contradiction that failed this boundary in the prior review is resolved by preserving the decision rather than reinterpreting it. No decision was created, amended, or superseded. |
| Do not erase history | PASS | Prior bootstrap baseline, retired Downloads checkout, compacted history links, and TASK-186's evidence limitation all remain described. |
| Do not widen Pi/helper authority | PASS | Pi remains exploratory-only; helpers remain bounded, visible, and barred from task/review/release authority. The recorded Pi `ClearFront/dist/` scope incident is framed as evidence for the alignment problem, not a new lane. |
| Do not mutate product/source behavior | PASS | Changes are confined to planning and shared-state documentation. `map-git diff --stat` over the six registered outputs shows 246 insertions / 54 deletions across five tracked shared files plus the untracked memo. The broader dirty worktree predates this task and is unrelated. |
| Do not self-review | PASS | Reviewer is neither the durable owner nor the submitter. |

## Verification

Commands run independently by this reviewer, not taken from the handoff:

- `validate_shared_state.py` — PASS, 23 files, 0 failures, 0 warnings. Confirms the file's 23/23 claim.
- `validate_task_mirrors.py` — PASS.
- `validate_task_graph.py` — PASS.
- `validate_decisions.py` — PASS, 28 decisions checked, 28 active, 0 conflicts.
- `validate_canonical_repo_paths.py` — PASS.
- Read-only `map.db` query of all nonterminal tasks; every lane-table row cross-checked field by field.
- `task_release_records` queried directly for TASK-186 and TASK-266 — one row, TASK-186 only.
- TASK-266 event history read; latest transition is APPROVED, no RELEASED event.
- `graph/runner.py` inspected for `DEPENDENCY_SATISFIED_STATUSES` to confirm the TASK-268 dependency conclusion holds despite the incorrect stated reason.
- `map-git diff --stat` scoped to the six registered output paths.

## Notes

The rework is close and the corrections are surgical — the memo's separation of
durable owner from live claimant is a genuine improvement, and naming TASK-267's
own stale owner as a reconciliation gap rather than quietly fixing it is the
right instinct.

Two things worth carrying forward beyond this task. First, this submission and
the prior one both failed on the same shape: a canonical state file asserting a
task status that `map.db` contradicts. Two consecutive rejections on the same
class suggests the memo's own SYN-0001 diagnosis applies to itself — a
hand-maintained lane table is a second reader of task state with no mechanical
agreement check against the authoritative writer. A validator comparing status
claims in shared state against `map.db` would have caught both instances.

Second, per INS-0039, review separation on this task was enforced only by
Kula's own declaration and the operator's routing. The `owner`-keyed guards
would have permitted a self-approval here.
