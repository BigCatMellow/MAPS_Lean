# Roadmap: <project>

- State: `DRAFT | APPROVED_FOR_AUTONOMOUS_EXECUTION | WORKING | DONE`
- Authorization revision/date: <revision/date or `not yet approved`>
- Default autonomous execution: `YES`

## Current reality

- Checked facts: <what was directly inspected or verified>
- Evidence/source paths: <files, systems, data, screenshots, links, or other proof>
- Important assumptions: <what is still assumed rather than verified>

## Definition of DONE

- Finished result: <observable end state>
- Final proof: <specific test, review, release, or evidence proving completion>
- Who can perform/inspect final proof: <agent, reviewer, human operator, or named role>

## Execution permission envelope

Approval of this roadmap authorizes the orchestration operator to execute it
end-to-end without routine human approval between tasks or checkpoints.

- Authorized objective: <what the approved work is trying to accomplish>
- In-scope decisions/actions: <implementation, task shaping, tests, helpers, routine commits/PRs, etc.>
- In scope: <items>
- Explicitly excluded: <items/actions that remain outside authority>
- Preauthorized external/destructive/irreversible actions: <exact bounded targets/classes, limits, recovery/verification, or `none`>
- Human reauthorization triggers: <material scope/objective expansion, non-preauthorized irreversible action, spending/credentials/publication/etc.>
- Human checkpoints: <named checkpoints requiring human approval, or `none`>
- Effort limit: <when cost/time/attempts require reconsideration>
- Highest-risk unknown: <unknown to research or prototype early>

A normal checkpoint, review, task completion, commit, or status report is **not**
a human approval gate unless listed above as a `HUMAN CHECKPOINT`.

## Backward plan

Work from DONE toward the present before filling execution phases. Record
unknown links as unknowns; do not invent missing facts.

1. Immediately before DONE: <required condition>
2. Before that: <required condition>
3. Before that: <required condition>
4. Current state: <where the project is now>

## Mission meeting

- Required: `YES | NO`
- Questions to settle: <missing steps, assumptions, risks, dependencies, scope, parallel work, verification>
- Assumptions accepted/rejected: <results>
- Questions resolved internally: <question → evidence/helper/challenge → decision>
- Human decisions required before roadmap approval: <none or true permission-envelope decisions>
- Roadmap changes: <what changed and why>
- First wave selected: <task IDs or task group>

## First wave

Only detail work ready to start now. Each consequential task gets its own task
record with owner, inputs, inherited roadmap authority, allowed outputs,
dependencies, pass/fail criteria, verification, review, and escalation boundary.

- [ ] `<TASK-ID>` — <concrete result> — Owner: <agent/person>
- [ ] `<TASK-ID>` — <concrete result> — Owner: <agent/person>

## Phase 0 — Foundation
- [ ] <resolve important unknown or dependency>

## Phase 1 — Delivery
- [ ] <major outcome or usable slice>
  - [ ] <concrete leaf step when known>

## Phase 2 — Integration and final proof
- [ ] <integrate completed work>
- [ ] <review or acceptance test>
- [ ] <perform final proof of DONE>

## Autonomous continuation

After roadmap approval:

1. select the next eligible roadmap item;
2. shape/check it to `AGI READY`;
3. dispatch/execute with bounded helpers as useful;
4. reconcile and review the result;
5. mark the task complete when proven;
6. immediately continue with the next eligible item.

Do not stop merely to ask whether to continue. Stop for the human only when a
listed reauthorization trigger is actually reached and cannot be avoided by an
in-scope alternative.

## Checkpoints

Checkpoint after a major phase/usable result, failed key assumption, realized
risk, effort-limit trigger, or before a consequential hard-to-reverse change.

The orchestration operator records one decision:
`CONTINUE | CHANGE | CUT SCOPE | RESEARCH | STOP | HUMAN REAUTHORIZATION`.

`HUMAN REAUTHORIZATION` is valid only when the permission envelope would be
crossed. All other checkpoint decisions are made by the orchestration operator
using evidence and helper/challenger input as needed.

- Checkpoint: <when or after what result>
- Type: `INTERNAL | HUMAN CHECKPOINT`
- Evidence reviewed: <facts/results informing the decision>
- Decision: <one option above>
- Reason: <why>
- Next action: <what happens now>
- Re-plan if: <future evidence, failed assumption, risk, or effort threshold>
