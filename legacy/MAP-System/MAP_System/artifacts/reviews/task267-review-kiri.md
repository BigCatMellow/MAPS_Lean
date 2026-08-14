# Review: TASK-267 — Re-align MAP project vision, current state, and active execution lanes

## Verdict

CHANGES_REQUESTED

## Files Reviewed

- `MAP_System/tasks/TASK-267.json`
- `MAP_System/artifacts/planning/map-project-realignment-2026-07-22.md`
- `MAP_System/shared/project-brief.md`
- `MAP_System/shared/current-state.md`
- `MAP_System/shared/canonical-repo.md`
- `MAP_System/shared/agent-capability-matrix.md`
- `MAP_System/shared/hpom.md`
- `MAP_System/shared/decisions.md`
- live `map.db`, graph-runner output, task timelines, and hcom event `10496`

## Acceptance Criteria Check

| Criterion | Result | Evidence |
|---|---|---|
| Concise durable alignment memo states approved vision and non-goals | PASS | The memo and project brief align with DEC-008/DEC-028 and clearly reject infrastructure-for-its-own-sake. |
| Memo reconciles every active task, owner/lane, gate, and execution order | FAIL | All task IDs are present, but several database owners/claimants are omitted or conflated with model recommendations; see finding 2. |
| Refresh project brief/current state only where verified facts changed | FAIL | Project direction is supported, but TASK-186 was already unblocked by the recorded option-A decision and the shared-state count is stale; see finding 1. |
| Roles and authority boundaries explicit | PASS | Core, helper, Pi, local-model, and operator-attention boundaries agree with decisions and the helper guide. |
| Validators pass and every current-state fact is independently verifiable | FAIL | Claimed structural validators pass, but semantic cross-checks expose the TASK-186 and DEC-014 contradictions. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/shared/current-state.md` | The active-lane table says TASK-186 is “blocked on operator A/B/C state-authority choice.” The TASK-186 timeline records the operator selecting option A at `2026-07-22T14:31:38-04:00`, before TASK-267 submitted, and Gabi subsequently registered the recovered output paths. This makes the new high-confidence current-state snapshot false at publication time. The same file still says shared-state validation is “21/21 as of 2026-07-14,” while the claimed review run checks 22 files on 2026-07-22. | Refresh TASK-186 from its decision/task timeline and current runner immediately before resubmission. Update the shared-state validation count/date to the reproduced 22/22 result. Give the execution-lane snapshot an explicit as-of timestamp so rapid state changes are distinguishable from errors. |
| REQUIRED | `MAP_System/artifacts/planning/map-project-realignment-2026-07-22.md`; `MAP_System/shared/current-state.md` | Acceptance criterion 2 requires every active task’s current owner/lane. The memo and current-state table list work order and model fit but omit the authoritative database owner and current claimant for several lanes. Examples: TASK-236 owner `claude-lab-gome`; TASK-263 owner `codex-lab-kiri`; TASK-266 and TASK-268 owner `command-center`; TASK-186 still has database owner `claude-lab-mira` while claimant `claude-lab-gabi` is doing the work. Calling a recommended model tier or current worker the “accountable lane” does not reconcile these distinct fields. | Add explicit `owner` and `claimed_by/current worker` fields for every nonterminal task, using `map.db` at the stated snapshot time. Preserve the distinction between durable owner, live claimant, recommended support model, and decision authority. If an owner is intentionally stale, name that as a reconciliation gap instead of silently replacing it with the claimant. |
| REQUIRED | `MAP_System/shared/canonical-repo.md`; `MAP_System/shared/decisions.md` | The refreshed repository document calls `/home/home/Projects/MultiAgentProject` non-canonical, while active DEC-014 still literally declares that exact path canonical. The live `/home/mellow/Projects/MultiAgentProject` path is verified, and the intended Projects-over-Downloads rule is sensible, but an operational fact file cannot silently reinterpret an unsuperseded path decision while claiming the two agree. The decisions validator checks shape, not this semantic contradiction. | Record an authorized DEC-014 amendment/supersession that separates the logical “active Projects checkout” rule from host-specific resolved paths, then make both files agree; or stop labeling DEC-014’s still-active literal path non-canonical. Register any added decision output through the sanctioned task lifecycle. |
| RECOMMENDED | `MAP_System/shared/agent-capability-matrix.md` | “Observed Health” names only Lime and Gabi as active sessions. The paragraph correctly warns that names are ephemeral, but a high-confidence shared capability file becomes stale almost immediately when it embeds a partial roster. | Prefer a verified-at timestamp plus a pointer/command to `hcom list`, or omit individual live names from the canonical capability matrix. Keep volatile roster state in current-state/hcom surfaces. |

## Forbidden Changes Check

| Boundary | Result | Evidence |
|---|---|---|
| Do not invent architecture or authority | FAIL | No new runtime architecture is invented, but `canonical-repo.md` semantically replaces DEC-014's literal active path without a matching decision amendment. |
| Do not erase history | PASS | Old paths and the prior bootstrap baseline remain described; compacted history remains linked. |
| Do not widen Pi/helper authority | PASS | Pi and helpers remain explicitly barred from task/review/routing/release authority. |
| Do not mutate product/source behavior | PASS | TASK-267 changes planning/shared-state documentation only. |

## Verification

- `MAP_System/scripts/map-git rev-parse --show-toplevel` — PASS; current root is `/home/mellow/Projects/MultiAgentProject`.
- `MAP_System/.venv/bin/python MAP_System/graph/runner.py` — PASS; reproduced the current route/queue and policy gate.
- `python3 MAP_System/scripts/validate_shared_state.py` — PASS, 22 files checked; this exposes the stale 21/21 sentence.
- `python3 MAP_System/scripts/validate_task_mirrors.py` — PASS.
- `python3 MAP_System/scripts/validate_task_graph.py` — PASS.
- `python3 MAP_System/scripts/validate_decisions.py` — PASS structurally; it does not compare DEC-014 prose with `canonical-repo.md` semantics.
- `python3 MAP_System/scripts/validate_canonical_repo_paths.py` — PASS mechanically; it likewise does not resolve the active-decision contradiction.
- `python3 MAP_System/scripts/librarian.py validate` — 6 pre-existing broken-link findings in TASK-238/librarian artifacts, none in TASK-267 outputs.
- `MAP_System/graph/runner.py` imports and builds LangGraph `StateGraph`; the brief’s LangGraph routing claim is supported.
- DEC-008 supports Codex implementation-led / Claude review-and-planning-led roles; DEC-028 supports software delivery as the standing proving workflow.
- TASK-261’s recorded operator decision supports Pi’s exploratory-only posture and unchanged operational-authority ceiling.
- hcom event `10496` supports using task-appropriate model levels; the existing helper guide supports the Haiku/Sonnet/Opus distinctions and cross-core escalation boundary.

## Notes

The one-sentence vision is clear and consistent with DEC-028. The changes also
correctly separate model strength from authority, preserve the operator’s
attention boundary, and avoid granting Pi or helpers task/review/release
authority. No source or canonical file was edited by this review.
