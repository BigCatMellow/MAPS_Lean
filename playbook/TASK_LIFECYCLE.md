# Task Lifecycle: Shape, Own, Verify, Continue

Every consequential task should be executable by a future agent without the
original chat. Every approved roadmap should be executable without routine
human nudges between its child tasks.

This is the task lifecycle method under [`AGENTS.md`](../AGENTS.md); it does not
create a separate authority model.

## Shape before claiming

Shape work when intent, output paths, criteria, dependencies, authority, or
proof are materially unclear. Use
[Operator Request Compilation](REQUEST_COMPILATION.md) for concise live requests.

A task record states:

- observable outcome;
- one accountable owner and risk tier;
- authoritative inputs/evidence;
- dependencies/preconditions;
- allowed outputs and non-goals;
- inherited roadmap permission envelope;
- bounded decision authority and true human reauthorization boundary;
- pass/fail acceptance criteria;
- verification/evidence;
- required review; and
- failure/recovery/escalation conditions.

If information is missing, resolve it through evidence, research, helpers, or
orchestration judgment when inside approved authority. Human escalation is for
permission-envelope crossings, not ordinary shaping.

## AGI gate

A consequential task may enter `READY` only when `AGI READY` under
[AGI_STANDARD.md](AGI_STANDARD.md).

`READY` means a suitable fresh worker can execute without consequential guessing
and can prove success. Missing information may route to shaping/research/internal
authority resolution; it does not automatically route to the human.

Worker suitability is a separate question. After AGI passes, use the single
[model capability routing](MODEL_CAPABILITY_ROUTING.md) method to choose the
cheapest worker proven competent for the whole execution envelope.

## Ownership rules

Output paths are prospective write boundaries. Register them before editing.
Inside an approved roadmap, if a new in-scope file/path becomes necessary, the
orchestration operator may amend the task, re-check readiness, and continue
without human approval.

Only one active owner edits a given output path. Parallel helpers may research,
review, or prepare non-overlapping work; name one integration owner.

## State model

```text
NEEDS_SHAPING --AGI PASS--> READY --> ACTIVE --> READY_FOR_REVIEW --> DONE
                                      |                    |
                                      v                    |
                                   BLOCKED                 |
                                      ^                    |
                                      |                    v
                                CHANGES_REQUESTED <--------
```

`DONE` means acceptance criteria, required verification, proportional review,
and any triggered operational-independence requirement (`OIG-DONE`) are complete.

## Operational independence gate

A repeatable result should not depend on the original AI/session remembering how
it was produced.

This gate is **REQUIRED** when the work creates or discovers a process that a
person may reasonably need to run, rebuild, refresh, migrate, troubleshoot, or
repeat later. Typical triggers include spreadsheet/sheet generation,
transformations/imports, reports, recurring administration, data cleanup,
deployments/setup, generated configurations, and software/program workflows.

Do the real project first when discovery is necessary. Once the successful path
is known, look back at the work and convert that path into the smallest durable
reproduction package. Do not prematurely automate an unknown process if doing so
would slow or distort solving the actual problem.

Before parent success, a triggered reproduction package MUST contain:

1. **First-time-user instructions.** Assume the reader has never seen the project.
   State purpose, prerequisites/access, inputs, exact ordered steps, expected
   outputs, verification, routine operation, common failure/recovery, and how to
   make the most likely future changes. Use concrete names/locations; do not rely
   on unexplained chat history.
2. **Reproducible implementation.** Preserve the code/script/formulas/query/config/
   template that can recreate or rerun the process when technically feasible.
   For example, a Google Sheets workflow should normally leave Apps Script,
   formulas, queries, or equivalent automation rather than only a finished sheet.
3. **Portable configuration.** Separate credentials/secrets and volatile IDs from
   logic. Use documented placeholders/configuration and never embed secrets merely
   to make reproduction easier.
4. **Provenance.** State which source inputs and assumptions the automation uses,
   and which output it is expected to recreate. The goal is enough traceability to
   rebuild without reconstructing the original conversation.
5. **Reproduction proof.** When safe and feasible, run the automation against a
   clean/disposable/sample target and verify the produced result, not only the
   already-finished artifact. Prefer rerunnable/idempotent behavior where practical.

The instructions may live in the target project's normal README/instructions
surface; the automation belongs with the project/source it operates. Do not
create a second documentation system just for this gate.

### Gate rules

Stable rule IDs; regression protection keys on these, not on surrounding prose.

- `OIG-DONE` — When triggered, this gate is part of `DONE` and of parent
  success. Acceptance/verification/review completing does not close the task
  while the triggered gate is unresolved.
- `OIG-NA-WHOLE` — A whole-gate `N/A — <reason>` is reserved for work that is
  genuinely non-repeatable or inherently one-off/creative: there is no process a
  person could reasonably need to rerun, rebuild, refresh, or troubleshoot.
  Automation being infeasible or disproportionate is **not** a valid whole-gate
  `N/A` reason for otherwise-repeatable work.
- `OIG-NA-AUTO` — For repeatable work where building the automation (item 2) is
  technically infeasible or disproportionate to its value, keep the gate
  `REQUIRED` and mark only that component `N/A — <reason>`. The reproduction
  package MUST still carry the best available manual reproduction instructions
  (item 1), the source inputs/materials and provenance (items 3–4), and
  proportional verification (item 5). `N/A` never licenses leaving nothing
  behind or an AI-/session-only dependency.

Record the reason for any `N/A` in the task record.

## Autonomous roadmap continuation

`DONE` is a child-task terminal state, not a default pause for the human.

After a task becomes `DONE`, the orchestration operator MUST:

1. reconcile its result into parent state;
2. identify newly unblocked/eligible roadmap work;
3. select the next useful item;
4. shape/check it to `AGI READY`;
5. dispatch/execute it; and
6. continue until the parent roadmap is genuinely complete or a true authority
   boundary blocks further progress.

Do not ask `continue?`, `approve next task?`, or equivalent when the next task is
already inside an approved roadmap.

A normal status report, review verdict, checkpoint, commit, or PR is visibility,
not a permission gate.

## High-risk release visibility

`OPERATOR_VISIBLE_RELEASE_CHECK` adds visibility, not routine human approval.
The completion summary states what became true, reproduced verification,
residual risk, exact artifact/revision, and any genuinely non-preauthorized
boundary action still pending.

If a destructive/external/security-sensitive action was explicitly
preauthorized in the approved permission envelope, required review/checks may
complete and execution may continue without asking again. If it was not
preauthorized, obtain human reauthorization before that action.

## Conflicts and questions

When authoritative sources materially disagree:

1. stop only affected work;
2. record the conflicting claims/sources;
3. inspect evidence/research;
4. use a focused helper and, when consequential, an independent challenger;
5. let the orchestration operator resolve the conflict when resolution remains
   inside approved authority; or
6. escalate to the human only when resolution would require changing that
   authority/objective or a human-only preference.

Do not silently choose a convenient source. Do not freeze unrelated work when it
can safely proceed.

## Review independence and evidence

When independent review is required, the reviewer must be meaningfully
independent of the implementer. Review routes one of:

- `APPROVED` → orchestration operator reconciles and continues;
- `CHANGES_REQUESTED` → orchestration operator routes corrections;
- `BLOCKED` → orchestration operator resolves evidence/dependency or escalates a
  true boundary blocker.

Review is not a routine human approval step.

Functional, security, privacy, destructive/data-loss, release-path, and
authority review lenses are applied only when triggered by the task.

## When the contract changes during execution

If execution discovers a material new requirement, output path, dependency,
authority question, safety issue, or failed assumption:

1. stop the affected branch before crossing its current boundary;
2. label the new fact `VERIFIED`, `REPORTED`, `ASSUMED`, or `UNKNOWN`;
3. determine whether the change fits the parent roadmap permission envelope;
4. if **inside**, amend/re-shape the task, run helper/research/challenge as useful,
   re-run AGI, and continue;
5. if **outside**, record the exact boundary crossing and seek human
   reauthorization; and
6. continue independent authorized work when safe.

Do not preserve `READY` by silently widening a task. Do not require human
approval merely to amend a child task inside already approved scope.

## Execution integrity

Use [EXECUTION_INTEGRITY.md](EXECUTION_INTEGRITY.md) when drift, recovery,
reviewer independence, or exact run binding matters. Run binding freezes the
current contract; it does not revoke inherited roadmap authority or create a
human gate.

## Special acceptance checks

- Repeatable operational work: complete the Operational independence gate above.
- Visual work: freeze reference, render real target viewport, compare evidence.
- Design port: inspect live data/API fields before inventing new ones.
- User-acquired release: test acquisition/install/launch path, not only dev entry.
