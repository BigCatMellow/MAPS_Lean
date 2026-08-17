# Task: recovery-equivalence authority design Wave 4

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `agent/recovery-equivalence-authority-wave4`
- Risk: `MEDIUM`
- Goal: Design what, if anything, would legitimately let environment-compatibility evidence (E2/E3, PR #28/#29/#30) participate in a recovery/continuation decision (RnS, `runtime/recovery/`) without letting a mechanical `COMPATIBLE` result become permission by itself.

## Inputs and source of truth

- Root `AGENTS.md`, especially negative-operating-contract rules 3 ("do not make material assumptions") and 9 ("do not hide uncertainty").
- `runtime/environment/fingerprint.py` (accepted, PR #29) — `CompatibilityState` = `COMPATIBLE | COMPATIBLE_WITH_WARNINGS | DRIFTED | INCOMPATIBLE | UNKNOWN`; `evaluate_environment_compatibility()` derives state from spec/fingerprint/reference facts only.
- `runtime/environment/spec.py` (EnvironmentSpec v1, PR #28) and `runtime/environment/safety.py`.
- `runtime/state/environment.py` (accepted, PR #30) — `EnvironmentEvidenceMixin` docstring: "Environment evidence describes where/how a run was observed. It does not grant task ownership, renew a lease, approve policy, or authorize recovery."
- `runtime/recovery/store.py` and `runtime/recovery/supervisor.py` — current RnS mechanism (verified by direct read, see Verified findings).
- `work/tasks/environment-run-evidence-wave2.md`, `work/tasks/environment-fingerprint-wave2.md` — original task framing; the latter's Notes section states "Reference comparison is evidence for equivalence/recovery decisions, not permission to resume a task."
- `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` — `4.2 Capability is not authority`, `4.3 Session liveness is not task truth`, `4.4 Unknown remains unknown`, `6.6 Explicit run/session/helper/recovery lineage`, `6.14 EnvironmentFingerprint and compatibility`, `6.17 Sandboxes / snapshots / rehydration` (`TRIGGERED`), Scenario C ("Interrupted worker").
- `work/roadmaps/current-capability-reconciliation-2026-08-16.md` — dependency map: "`ENVIRONMENT E1/E2/E3 ACCEPTED` → `recovery/setup equivalence only after explicit authority design`"; bounded next planning question: "For recovery-equivalence work: use accepted environment evidence without turning COMPATIBLE into permission; current task/run/policy/ownership authority still controls recovery."
- `work/tasks/communication-task-run-join-wave3.md` / `work/notes/2026-08-15-communication-task-run-join-design.md` (merged #51) as the structural model for this task.

Authoritative evidence ordering: current merged `main` code (`runtime/recovery/*.py`, `runtime/environment/*.py`, `runtime/state/environment.py`) wins over roadmap prose; roadmap prose describes target end-state, not built behavior; this task's own notes below are proposals, not authority.

## Verified findings (direct code read, not assumed)

1. **`runtime/recovery/supervisor.py` never references environment/compatibility evidence.** `RecoverySupervisor.tick()` and `observe_silent_stops()` gate every decision on: `terminal_sessions` membership, `task.status == "ACTIVE"`, `task.claimed_by == worker_id`, `session_is_live()` (process/status heuristic), and a fixed attempt/backoff budget. There is no import of `runtime.environment`, no read of `run_environment_evidence`, and no `EnvironmentFingerprint`/`CompatibilityState` reference anywhere in `runtime/recovery/`.
2. **`RecoveryIncident` (in `runtime/recovery/store.py`) carries no `run_id` field** — only `task_id`, `worker_id`, `session_name`. There is currently no schema path linking a recovery incident to the specific run whose `run_environment_evidence` rows would need to be consulted. Wiring compatibility evidence into a recovery decision would first require deciding how (or whether) to bind an incident to a run — that is itself a scoping/authority question, not a mechanical lookup.
3. **`runtime/state/environment.py`'s own docstring already states the boundary this task is designing around**: environment evidence "does not grant task ownership, renew a lease, approve policy, or authorize recovery." This task does not need to invent that rule; it needs to design what (if anything) sits on top of it.
4. **The master roadmap's target end-state (6.14, Scenario C) explicitly wants recovery to eventually consult environment compatibility** ("Recovery can answer whether a session can safely continue instead of blindly resuming on a different machine state"; "Recovery checks task revision, context hashes, policy and environment compatibility"). That end-state is not built today — current RnS resumes/suppresses based purely on task/claim/session-liveness facts, independent of environment.
5. **Snapshots/rehydration (6.17) is listed `TRIGGERED`** (not yet justified/built), with EnvironmentFingerprint as one of its prerequisites, not the reverse. This design does not assume snapshot/rehydration exists.

## Change boundary

MAY CHANGE:

- `work/tasks/recovery-equivalence-authority-design-wave4.md` (this file)
- `work/notes/2026-08-17-recovery-equivalence-authority-design.md`

MUST NOT CHANGE:

- `runtime/environment/*.py`
- `runtime/state/environment.py`
- `runtime/recovery/*.py`
- `runtime/state/schema.sql`
- any other runtime file
- any other agent's branch, including the concurrent operational-learning-promotion-authority design branch (no file overlap; not referenced further in this task)
- any existing task/note file

No runtime implementation is authorized by this task.

## Decision authority

Owner may decide (design-only, within this task):

- the vocabulary/taxonomy distinguishing "environment equivalence" from "recovery authority";
- that `UNKNOWN` compatibility must fail closed for recovery purposes (this is not a new policy call — it follows directly from `AGENTS.md` rule 9 and roadmap `4.4`, both already-accepted law);
- that this design does not assume snapshots/rehydration exist;
- that the smallest safe next step is evidence-only surfacing with zero behavior change to what currently authorizes recovery;
- that wiring a `run_id` onto `RecoveryIncident` (a schema/runtime change) is out of this task's boundary and belongs to a future implementation task, not this design.

Owner must not decide (flagged below as requiring an explicit operator decision):

- whether mechanical `COMPATIBLE` may ever gate *any* bounded recovery action, even a narrow one;
- whether `DRIFTED` should be treated the same as `INCOMPATIBLE` for recovery purposes, or as a lesser caution;
- whether/how `RecoveryIncident` should be extended to bind to a run for future evidence consumption;
- who/what is authorized to act on surfaced advisory environment evidence (human operator only vs. a future policy layer);
- whether recovery-equivalence work should ever extend toward snapshot/rehydration continuation, or stay permanently scoped to RnS session-resume only.

## Acceptance criteria

- [x] `runtime/recovery/supervisor.py` and `runtime/recovery/store.py` are read in full and their actual decision inputs are stated as verified findings, not assumed.
- [x] `runtime/state/environment.py`'s explicit non-authority statement is quoted and treated as binding.
- [x] Master roadmap `4.2`/`4.4`/`6.14`/`6.17` and the reconciliation doc's exact gap language are located and cited.
- [x] "Equivalence" (environment-compatibility) and "authority" (task/run/policy/ownership) are kept as distinct facts throughout, per roadmap `4.1`/`4.2`.
- [x] `UNKNOWN` is specified to fail closed for recovery purposes, consistent with `AGENTS.md` rule 9 and roadmap `4.4`.
- [x] A staged, smallest-safe-next-step proposal is given for each of the five design areas in the originating brief, not a finished implementation.
- [x] Every genuine policy question is listed under "Decision authority → Owner must not decide" and in this task's escalation list, not resolved silently.
- [x] Snapshot/rehydration is explicitly marked out of scope (6.17 is `TRIGGERED`, not built).
- [x] No runtime file is modified; only the two design files exist on this branch.

## Verification and evidence

- Verification: direct reads of `runtime/recovery/supervisor.py`, `runtime/recovery/store.py`, `runtime/environment/fingerprint.py`, `runtime/environment/spec.py`, `runtime/environment/safety.py`, `runtime/state/environment.py`, and the named roadmap/task files on this branch's checkout of `main` at clone time.
- Evidence to preserve: the verified-findings section above (line-level behavior of `tick()`/`observe_silent_stops()`; absence of any environment import in `runtime/recovery/`; absence of `run_id` on `RecoveryIncident`).
- Review required: `INDEPENDENT_REVIEW` before this design becomes implementation authority (matching the #51 model).

## Conditional execution rules

- Environment / target: design-only, local MAPS Lean workspace clone; N/A for runtime execution.
- Ordered procedure: read root law → read accepted environment foundation (E1/E2/E3) → read current RnS implementation → read roadmap target state and reconciliation gap → produce staged proposal per area → split decision authority → escalate genuine policy questions.
- Failure branches: IF a proposed integration would require inferring recovery permission from `COMPATIBLE` alone THEN reject that branch and mark it operator-decision-required; IF `RecoveryIncident` cannot be bound to a run without a schema change THEN treat that binding as a separate future implementation task, not something this design performs.
- Rollback / recovery: N/A — no runtime/schema mutation occurs.
- Security / privacy controls: N/A — no secret values, no environment mutation.
- External side effects: none. No push/PR is performed by this task; branch state is left local per the originating instruction.
- Effort limit: two files, matching the #51 model's scope.
- Approved reference: `work/tasks/communication-task-run-join-wave3.md` / `work/notes/2026-08-15-communication-task-run-join-design.md` (#51) as structural model.

## Stop / escalate

Stop rather than guess if:

- a proposed integration would let mechanical `COMPATIBLE` become recovery permission by itself (this happened nowhere in this design; flagged instead as an operator decision in area 2);
- `UNKNOWN` compatibility would need to be treated as "assume compatible" for any bounded action (rejected outright; `UNKNOWN` fails closed per existing law, not a new call this task makes);
- the design would need to assume snapshot/rehydration capability exists (rejected; 6.17 is `TRIGGERED`, not built, and is out of scope);
- implementation would require editing `runtime/recovery/*.py`, `runtime/environment/*.py`, or `runtime/state/environment.py` (out of this task's change boundary; deferred to a future implementation task after operator decisions land).

Escalate to: operator, for the five questions listed under "Owner must not decide" above and restated in the design note's Decision authority section.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- See `work/notes/2026-08-17-recovery-equivalence-authority-design.md` for the full five-area analysis, staged proposals, and drift-handling table.
- This task deliberately does not touch `runtime/recovery/store.py`'s `RecoveryIncident` shape even though the analysis identifies that a `run_id` field would be a prerequisite for any future evidence-surfacing step. Adding that field is schema/runtime work requiring its own task and review, not something a design-only task performs implicitly.

## Completion / handoff

- Completed: five-area design analysis, staged smallest-safe-next-step proposals, explicit decision-authority split, all flagged operator questions enumerated.
- Not completed: independent review; any runtime implementation (not authorized by this task); the schema question of whether/how to bind `RecoveryIncident` to a run.
- Current blocker: operator decisions listed in "Decision authority → Owner must not decide" must land before any implementation task can be shaped.
- Next action if not DONE: independent review of this design; if approved, shape a follow-on `IMPLEMENTATION` task scoped to exactly the operator-approved subset (most likely: evidence-only surfacing, zero new authority, per area 4 below) — and only after the `RecoveryIncident`-to-run binding question is separately resolved.
