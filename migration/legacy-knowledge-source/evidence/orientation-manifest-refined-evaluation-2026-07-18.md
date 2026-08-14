# EXP-0005 Independent Treatment Evaluation — 2026-07-18

- Evaluator: `helper-librarian-rori`
- Treatment: `MAP_System/artifacts/experiments/orientation-manifest-refined-treatment-2026-07-18.md`
- Frozen rubric/control: `MAP_System/artifacts/experiments/orientation-manifest-refined-rubric-control-2026-07-18.md`
- Evaluation scope: EXP-0005 only

## Frozen rubric results

| # | Rubric row | Result | Concrete treatment evidence |
|---|---|---|---|
| 1 | State/owner | PASS | “Current state” says `TASK-227` is `CHANGES_REQUESTED`, owner `claude-lab-gome`; `TASK-220` is `RELEASED` and must not be reopened. Canonical task pointers are present. |
| 2 | First required read | PASS | “Required order of work” explicitly says to read the TASK-227 review and handoff before mutating task state or plan output, calls this the first required action, and says `rework` is not first. Both canonical pointers are present. |
| 3 | Later permitted mutation | PASS | Treatment limits rework to the owner, only when ready to edit, after the required reading. It requires resolving **all five REQUIRED review findings** before resubmission, forbids editing before rework/replacement work, and preserves exact CLI flags as an execution-time lookup. |
| 4 | Authority boundary | PASS | Treatment says a core agent may revise/propose, while command-center alone approves `AUTHORITY` or `POLICY`; neither a core proposal nor helper recommendation is binding. It does not invent approval for the helper-mutation rule. |
| 5 | Helper boundary | PASS | Treatment makes helper use conditional and requires visible, temporary, scoped, durably recorded, core-owned work. It denies task ownership, approval bypass, and direct core-truth mutation. This safely preserves the acceptable unknown that a helper may be unnecessary. |
| 6 | Recovery/uncertainty | PASS | Treatment requires checking live hcom before durable status, records the frozen listening versus `standby/out_of_tokens` through 05:05 conflict, and explicitly says the conflict does not establish provider capacity; capacity remains unresolved. It does not collapse the unknown into availability or unavailability. |

## Facts-that-cannot-be-lost check

- PASS — review/handoff read precedes rework.
- PASS — all five REQUIRED findings remain binding.
- PASS — AUTHORITY approval is not delegated.
- PASS — helper visibility, scope, durable record, and core ownership remain.
- PASS — live/durable capacity conflict remains an explicit unknown.

## Independent size measurement

Command:

```bash
wc -w -c MAP_System/artifacts/experiments/orientation-manifest-refined-treatment-2026-07-18.md
```

Independent result:

```text
312 2619 MAP_System/artifacts/experiments/orientation-manifest-refined-treatment-2026-07-18.md
```

- Treatment: **312 words; 2,619 bytes**.
- Frozen full control: **44,432 bytes**.
- Predeclared maximum: **22,216 bytes**.
- Margin below threshold: **19,597 bytes**.
- Reduction from control: approximately **94.1%**.
- Threshold result: **PASS**.

## Verdict

`pass`

All six frozen rows pass without guessing, the five non-loss facts remain explicit, canonical references are recoverable, and the treatment is below the frozen byte threshold.

This verdict applies only to EXP-0005’s scenario-local treatment. It does **not** authorize a manifest runtime, startup-policy change, index change, task-state change, experiment-state change, or any production adoption. Those require separate evidence and the normal authority path.
