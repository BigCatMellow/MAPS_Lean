# EXP-0004 Orientation Manifest: Control vs Treatment — 2026-07-18

## Fixed scenario

Claude owns `TASK-227`, now `CHANGES_REQUESTED`; `TASK-220` is released; the operator wants continued system improvement; helpers may assist only visibly and inside durable bounded scope. A resumed agent must recover task state/owner, first valid action, authority boundary, helper boundary, and interruption-safe recovery path.

Measurement timestamp: `2026-07-18T00:59:45-04:00`.

## Control packet

The control concatenates the complete required sources and point-in-time outputs, with no summarization:

1. `AGENTS.md`
2. `MAP_System/AGENTS.md`
3. `MAP_System/DECISION_AUTHORITY_SYSTEM.md`
4. `MAP_System/agents/README.md`
5. `MAP_System/tasks/TASK-220.json`
6. `MAP_System/tasks/TASK-227.json`
7. `MAP_System/artifacts/reviews/task227-review-lilo.md`
8. `MAP_System/handoffs/HANDOFF-20260718-system-improvement-kickoff-to-claude.md`
9. `MAP_System/agents/status.json`
10. `MAP_System/.venv/bin/python MAP_System/graph/runner.py` output
11. `hcom list claude-lab-gome --json --name rori` output

Measured with the sources/outputs concatenated into `wc -w -c`:

- Control words: **6,437**
- Control bytes: **51,378**

## Treatment manifest

The bytes/words reported for treatment cover only the text between the treatment markers, excluding this experiment’s analysis and verifier checklist.

<!-- treatment-start -->
```yaml
orientation_manifest: EXP-0004-treatment-v1
observed_at: "2026-07-18T00:59:45-04:00"
scenario: resume TASK-227 rework without reopening released TASK-220

facts:
  - id: task_227_state_owner
    fact: "TASK-227 is CHANGES_REQUESTED; owner is claude-lab-gome; sole output is MAP_System/notes/system-improvement-implementation-plan.md."
    authority_class: "task execution state and output ownership"
    currentness: "current file mirror at observed_at; runner loaded SQLite but does not expose CHANGES_REQUESTED tasks in its queue summary"
    canonical_ref: "MAP_System/tasks/TASK-227.json"

  - id: task_220_terminal
    fact: "TASK-220 is RELEASED; do not reopen or treat it as pending work."
    authority_class: "terminal task state"
    currentness: "current file mirror; runner includes TASK-220 among done_task_ids"
    canonical_ref: "MAP_System/tasks/TASK-220.json"

  - id: first_valid_task_action
    fact: "When the owner is able and ready to edit, run map_task.py rework for TASK-227 before changing the plan; then resolve the five REQUIRED review findings and resubmit through the normal task flow."
    authority_class: "state-machine transition plus binding review requirements"
    currentness: "review verdict and handoff review update are newer than the handoff's original READY snapshot"
    canonical_ref:
      - "MAP_System/artifacts/reviews/task227-review-lilo.md"
      - "MAP_System/handoffs/HANDOFF-20260718-system-improvement-kickoff-to-claude.md"

  - id: required_rework_scope
    fact: "Rework must add: status-source precedence/freshness and a mixed-state test; bounded index population/sample/owner; explicit AUTHORITY routing for helper mutation; evidence-intake iteration; and a lifecycle north star with measures."
    authority_class: "independent review findings; REQUIRED before approval"
    currentness: "current CHANGES_REQUESTED review"
    canonical_ref: "MAP_System/artifacts/reviews/task227-review-lilo.md"

  - id: authority_boundary
    fact: "The plan may propose architecture/ownership inside approved scope. A rule changing what helpers may mutate is AUTHORITY-class: only command-center may approve it; a core agent may propose it; a helper may only recommend it."
    authority_class: "MAP decision authority policy"
    currentness: "CURRENT, active DEC-018; last_verified 2026-07-03"
    canonical_ref:
      - "MAP_System/DECISION_AUTHORITY_SYSTEM.md"
      - "MAP_System/artifacts/reviews/task227-review-lilo.md"

  - id: helper_boundary
    fact: "Any helper must be visible, temporary, specifically scoped, recorded in MAP_System/inbox/helpers/, and owned by a core agent. It may not bypass task ownership, edit TASK-227's owned output without an explicit handoff/output-path update, or record a binding decision."
    authority_class: "agent operation, ownership, and helper safety rules"
    currentness: "current operating rules"
    canonical_ref:
      - "MAP_System/AGENTS.md"
      - "MAP_System/DECISION_AUTHORITY_SYSTEM.md"

  - id: operator_direction
    fact: "Continue system improvement as a bounded observe -> experiment -> evidence -> tune -> re-measure cycle; preserve visible human control and treat experimental findings as candidates, not automatic tasks or policy."
    authority_class: "operator direction preserved in durable handoff"
    currentness: "handoff review update is current for TASK-227 resume; task/review override its older READY line"
    canonical_ref: "MAP_System/handoffs/HANDOFF-20260718-system-improvement-kickoff-to-claude.md"

  - id: interruption_recovery
    fact: "On interruption, update durable availability, heartbeat or submit the claim, and write a HANDOFF or STATE_SNAPSHOT with status, changed files, remaining action, risks, and verification. On resume, use that packet only for orientation; task/SQLite state, decisions, and artifacts remain canonical."
    authority_class: "session continuity protocol"
    currentness: "current operating rules"
    canonical_ref: "MAP_System/AGENTS.md"

  - id: availability_conflict
    fact: "Durable status says claude-lab-gome is standby/out_of_tokens until 2026-07-18T05:05:00-04:00; runner therefore lists it unavailable. Live hcom shows a visible, process-bound claude-lab-gome session listening. Live presence does not prove provider capacity."
    authority_class: "point-in-time routing evidence; hcom is live-presence authority, status.json is durable availability"
    currentness: "conflicting observations at observed_at; unresolved"
    canonical_ref:
      - "MAP_System/agents/status.json"
      - "MAP_System/agents/README.md"
      - "runner output at observed_at"
      - "hcom list output at observed_at"

next:
  task_action: "owner runs map_task.py rework TASK-227 only after capacity/availability is confirmed, then edits only the registered plan output against the five findings"
  helper_action: "if useful, owner creates a durable bounded helper note and requests findings/draft support in a visible terminal; owner integrates or discards output"
  do_not:
    - "do not reopen TASK-220"
    - "do not let a helper modify binding policy or core truth"
    - "do not treat the stale READY line in the handoff as current task state"
    - "do not infer provider capacity from a listening hcom process"

unknowns:
  - "Whether claude-lab-gome can currently execute model work; hcom presence and durable out_of_tokens state disagree."
  - "Whether the operator has approved any specific helper-mutation authority change; no approval is present in the inspected sources."
  - "Whether a helper is needed for TASK-227 rework; no active helper note is named for it."
```
<!-- treatment-end -->

## Treatment measurement

- Treatment words: **629**
- Treatment bytes: **5,653**

## Explicit gaps and non-inferences

- The manifest does not resolve the live/durable availability conflict. Per `agents/README.md`, hcom is live authority, but a listening process does not prove the provider limit has cleared.
- The runner’s `wait_or_reconcile` route omits `CHANGES_REQUESTED` from actionable queues; the task record and review still establish the required rework transition.
- The handoff originally says TASK-227 was READY, but its appended review update and current task record supersede that line. The handoff is orientation, not task-state authority.
- No inspected source grants a helper permission to edit the plan or make policy binding. A separate scoped handoff/output-path change or owner integration would be required.
- Exact `map_task.py rework` CLI arguments are intentionally not invented in the manifest; the canonical command help should be consulted at execution time.

## Verifier checklist

- [ ] **Task state/owner:** Answer says `TASK-227 = CHANGES_REQUESTED`, owner `claude-lab-gome`, and does not reopen released TASK-220.
- [ ] **First valid action:** Answer identifies rework transition before editing, then the five REQUIRED findings and resubmission.
- [ ] **Authority boundary:** Answer preserves command-center approval for AUTHORITY-class helper-mutation policy and distinguishes proposal from approval.
- [ ] **Helper boundary:** Answer requires visible, temporary, bounded, durably recorded helper work under a core owner, with no ownership/policy bypass.
- [ ] **Interruption recovery:** Answer names availability + claim state + HANDOFF/STATE_SNAPSHOT, and treats the packet as orientation beneath canonical task/decision/artifact state.
- [ ] **Uncertainty safety:** Answer does not collapse the hcom/status availability conflict or stale READY handoff line into a false current fact.

## Experiment interpretation

The treatment is successful only if an independent verifier answers all five fixed questions correctly and preserves the availability uncertainty. A smaller byte count alone is insufficient. The control remains available unchanged, so the experiment is reversible: discard this projection and retrieve the named canonical sources whenever a fact is disputed.
