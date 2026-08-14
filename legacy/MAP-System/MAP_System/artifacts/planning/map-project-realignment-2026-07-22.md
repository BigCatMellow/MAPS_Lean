# MAP Project Realignment - 2026-07-22

- task_id: TASK-267
- durable_owner: codex-lab-lime
- current_worker: codex-lab-kula
- directive: Get the project back on track and ensure agents share one project vision.
- evidence: DEC-008, DEC-014, DEC-028, live `map.db`, runner output, current handoff, task/review artifacts
- status: rework in progress after independent review

## One-Sentence Vision

MAP is an operator-directed system for shipping useful project work through
durable ownership, bounded authority, mechanical verification, independent
review, and reversible release - not a reason to keep building coordination
infrastructure indefinitely.

## Shared Operating Picture

1. The operator owns direction and high-authority decisions. The Command Center
   should ask for attention only when a decision, approval, blocker, conflict,
   or safety/scope risk genuinely needs it.
2. Codex and Claude are the two core agents. Each task has one accountable
   owner; substantive work gets independent review.
3. Pi, temporary helpers, and local/Ollama models are support capabilities with
   bounded scopes. Pi is exploratory-only and cannot write canonical state,
   own/review tasks, route work, or release changes.
4. SQLite coordinates live claims. Task files and the graph are synchronized
   mirrors. Shared state and decisions carry durable meaning. Hcom/UI messages
   communicate state but do not replace it.
5. DEC-028 makes software delivery the proving workflow. TASK-205 completed the
   first ProjectUpdater proving slice. Once the recovery queue is closed, the
   next priority should be another operator-valued software slice, not a new MAP
   subsystem by default.
6. Core ownership does not mean core-only execution. HPOM must select the right
   model level for bounded support: Haiku for explicit checks, Sonnet for
   cross-file reasoning, Opus for unusually hard security/architecture, and
   proven local models/Aider for narrow draft or edit support. Authority remains
   with the accountable core owner.

## What Drifted

| Drift | Evidence | Correction in TASK-267 |
|---|---|---|
| `shared/project-brief.md` still described the June bootstrap rather than the approved software-delivery direction. | DEC-028 and released TASK-205 post-date the brief. | Brief now states the current delivery vision, roles, completion condition, and non-goals. |
| `shared/current-state.md` was verified before the July 21-22 authority, security, recovery, and queue changes. | Latest state snapshot, runner, TASK-254/265/266 events. | Added a dated alignment baseline and exact active execution lanes. |
| Canonical repository path used a prior host username. | Live `map-git rev-parse --show-toplevel` returns `/home/mellow/Projects/MultiAgentProject`. | Refreshed the operational host path while preserving DEC-014's Projects-vs-Downloads decision. |
| Agents can still act from different capability eras, especially around Pi authority and review/claim state. | Pi Trial C, TASK-261, live TASK-266 review-claim false negative, 2026-07-22 broadcast. | Authority boundaries and state-source precedence are now explicit in the brief/current state. |
| Operational repair and research were competing in one flat ready queue. | Runner exposed TASK-236 and TASK-263 equally while TASK-186/254/265/266 remained unresolved. | Recovery order now puts attention-noise, state recovery, and CommandCenterUI truth before the production-neutral retrieval experiment. |
| HPOM existed, but agents still defaulted work to whichever regular core session was active. | Operator correction hcom #10496; runner proposed a generic helper without model-level execution mapping. | Added a task-by-task worker/model-fit plan and refreshed HPOM/capability guidance. |

## Root Pattern To Land

Claude's TASK-186 work confirmed that SYN-0001 has recurred across three live
failures: approval gates read fields the schema did not write; `claim_review()`
assumed agent registration that only `map_task.py` performed; and the exporter
removes terminal rows the watcher expects to read. These are one design defect:
two readers/writers with no declared authority contract.

This belongs above new framework feature work. After the current bounded fixes,
shape one task that names the authoritative writer, exported representation,
reader contract, and end-to-end reachability test for each recurrence. Unit
tests over synthetic downstream data are insufficient: TASK-186 has 32 green
watcher tests while the production exporter makes the tested feature mostly
unreachable.

## Active Task Snapshot

Snapshot time: `2026-07-22 22:42 EDT`. SQLite is authoritative for these
fields; model recommendations are support guidance, not ownership.

| Task | State | Durable owner | `claimed_by` / current worker | Dependency, gate, or reconciliation note |
|---|---|---|---|---|
| TASK-254 | CHANGES_REQUESTED | `codex-lab-kiri` | none | Reconcile the CommandCenterUI final-state scope and authority findings before re-review. |
| TASK-263 | IN_PROGRESS | `codex-lab-kiri` | `codex-lab-kiri` recorded | The recorded lease expired at `2026-07-22 22:03:00`; treat live execution as unverified until heartbeat or sanctioned recovery. Keep its frozen/blinded experiment ordering. |
| TASK-265 | READY | `command-center` | none | Policy-gated on command-center security/structural approval plus the remote-Ollama and authoritative-copy decisions. |
| TASK-267 | IN_PROGRESS | `codex-lab-lime` | `codex-lab-kula` | Lime is durably `inactive/session_superseded`; Kula resumed the finalized handoff. The stale durable owner is a visible reconciliation gap, not silently rewritten as the claimant. |
| TASK-268 | READY | `command-center` | none | Its recorded TASK-266 dependency is satisfied because the runner accepts APPROVED dependencies. TASK-266 is APPROVED and pending release. This is now a claimable implementation lane, subject to normal output-path checks. |
| TASK-236 | READY | `claude-lab-gome` | none | Deliberately parked by cross-agent agreement until TASK-267 releases; runner helper eligibility does not override that agreement. |

TASK-186 is RELEASED. TASK-266 is APPROVED and pending release; neither appears
in the active-lane table. Separately, the runner treats `DONE`, `APPROVED`, and
`RELEASED` dependencies as satisfied, so TASK-268 is not dependency-blocked.
TASK-186's operator choice was option A; its release preserves the explicitly
documented limitation that no post-restart live terminal-attribution transition
was manufactured.

## Recovery Sequence

### Now

- `codex-lab-kula`: resolve TASK-267's required review findings, refresh the
  timestamped SQLite snapshot immediately before submission, and route a new
  independent review.
- Keep TASK-236 parked until TASK-267 releases.
- Reconcile TASK-263's expired recorded lease through its existing owner or the
  sanctioned recovery path; do not infer liveness from `claimed_by` alone.

### Next

- TASK-268 now durably owns the follow-on lifecycle seam: add a synchronized
  submit verb and fix `claim_review()` so an unregistered-reviewer foreign-key
  failure cannot collapse into "already claimed." Its TASK-266 dependency is
  satisfied; verify output-path availability before claim.
- Resolve TASK-254's scope/authority findings before calling the rapid UI batch
  a clean baseline.
- Satisfy TASK-265's security/structural gate by obtaining the still-missing
  operator decisions on remote Ollama and the authoritative `server.py`, then
  combine template-to-live and add drift detection.

### Then

- Rework TASK-236's malformed-claim logic and missing isolated tests. Keep it
  proposal-only; it observes and suggests but never claims, edits, approves, or
  promotes.
- Apply the worker/model-fit table in `shared/current-state.md`: Sonnet for
  TASK-236's non-obvious logic, Opus for TASK-265's bounded security second
  pass, and separate freeze/evaluator helpers for TASK-263. Higher tiers require
  the documented cross-core approval; they do not gain core authority.
- Continue TASK-263 only after its expired-lease state is reconciled and with
  its frozen-question/treatment/evaluator ordering intact. It is experiment
  evidence, not production retrieval authority.
- Ask the operator to select the next real software-delivery slice if no
  already-approved product task is ready.

## Coordination Incident During Alignment

The Pi session began creating `Projects/ClearFront/dist/` after misreading the
broadcast as unrelated ClearFront implementation work. Codex sent an immediate
scope-stop request. Pi stopped before creating a file; the empty, untracked
directory remains and is not treated as project output. This reinforces the
existing exploratory-only/no-write boundary and is evidence for the alignment
problem, not a new task lane.

## Verification Checklist

- [x] Active task states and claims read from `map.db`.
- [x] Runner route and policy-gated task list reproduced.
- [x] DEC-008, DEC-014, and DEC-028 reconciled into the working vision.
- [x] HPOM and capability guidance refreshed to require model-level fit rather
  than default core-only execution.
- [x] TASK-236, TASK-254, TASK-263, TASK-265, and TASK-266 task/review evidence inspected.
- [x] Canonical Git root verified with the repository wrapper.
- [x] Shared-state, task-mirror, and graph validators pass after edits.
- [ ] Independent reviewer verifies facts and no new authority was invented.
