# TASK-305 integration delivery note

- Task: TASK-305
- Owner: codex-lab-replacement-valo
- Scope: INS-0054 through INS-0057
- Status: implementation evidence; independent review still required

## Adopted choices

| Insight | Implementation choice | Evidence |
|---|---|---|
| INS-0054 | Document sanctioned remote-authority calls as still subject to classifier policy and version compatibility. Require exact failure evidence and prohibit blind retry, alternate transport, classifier bypass, or local mirror mutation. | `MAP_System/AGENTS.md` |
| INS-0055 | Replace the generated checklist's generic checkbox with structured mechanism plus evidence/reason. Accept `sentinel scan`, `Discovery Agent pass`, or `neither`; reject incomplete structured evidence; retain the historical exact-checkbox form. No model is invoked automatically. | `MAP_System/templates/release-checklist.md`, `MAP_System/scripts/release_task.py`, `MAP_System/tests/test_release_gate.py`, `MAP_System/CHANGE_CONTROL_SYSTEM.md` |
| INS-0056 | Document opt-in `Related task: NONE` capture for reusable lessons from intentionally non-MAP work, with an explicit no-task/no-claim/no-authority/no-governance boundary. | `MAP_System/emergence/README.md` |
| INS-0057 | Extend design-port task authoring to verify the live data contract, prefer existing backend fields, and choose rollout and runtime integration deliberately, while allowing recorded operator-approved exceptions. | `MAP_System/notes/task-authoring-guide.md` |

## Incidental promoted-work completion

The `task-authoring-guide.md` edit also completes the previously omitted
second half of PROMO-0012 / IDEA-0024 / INS-0031: the visual-fidelity rule had
been added to `review-guide.md` on 2026-07-19, but PROMO-0012 inaccurately
claimed it had also been added to `task-authoring-guide.md`. TASK-305 adds that
already-approved guidance while touching the same section for INS-0057 and
corrects PROMO-0012's completion history. The additional output path was
registered through RUKI before PROMO-0012 was edited.

## Rejected choices

- No classifier exemption, workaround, alternate mutation channel, or
  automatic retry was added.
- No automatic Discovery Agent/model invocation was added to the release path.
- Capturing a non-MAP lesson does not import the underlying work into MAP.
- The design-port defaults do not ban runtime migrations or direct cutovers
  explicitly approved by the operator.

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_release_gate.py`: PASS,
  12 focused release-gate tests, including named SECURITY and policy-tier
  branch coverage.
- `MAP_System/.venv/bin/python MAP_System/scripts/map_emergence.py validate`:
  PASS, 124 artifacts checked.
- `MAP_System/.venv/bin/python -m py_compile
  MAP_System/scripts/release_task.py MAP_System/tests/test_release_gate.py`:
  PASS.
- `MAP_System/scripts/map-git diff --check -- <TASK-305 paths>`: PASS.
- Independent task review: required after submission and intentionally not
  performed by the owner.
