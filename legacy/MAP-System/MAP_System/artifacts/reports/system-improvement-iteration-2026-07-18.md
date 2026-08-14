# MAP System-Improvement Iteration — 2026-07-18

Status: ACTIVE
Owner: codex-lab-lilo
North-star outcome: An operator-guided project moves from intent through a
safe first action, interruption/recovery, independent review, and release
without hidden authority, chat archaeology, or coordination cost that exceeds
the work's risk.

## Decisions now in effect

| Decision | Evidence | Operational effect |
|---|---|---|
| Do not count on Pi | Trials A/B failed path/coordination reliability. Operator-authorized Trial C used fresh local qwen2.5-coder:7b-16k but emitted no required hcom acknowledgement and made a malformed terminal delivery claim. | Pi is operationally paused. No task, review, handoff, release, dependency, durable-output, routing, or capacity lane may use Pi. |
| Keep any future Pi diagnostic local-only and serial | The Trial C model was local qwen2.5-coder:7b-16k; local execution did not make hcom delivery reliable. | hcom HCOM_PI_ARGS specifies ollama/qwen2.5-coder:7b-16k --offline. Do not retry automatically; a fresh visible instance needs a new operator-authorized, no-write assignment. |
| Do not generalize compact orientation yet | EXP-0004 retained five of six safety dimensions but was partial on explicit read-before-mutate; its raw historical control was not retained. | The canonical startup contract stays unchanged. No manifest runtime, index, policy, or task-state work is authorized. |

## Evidence loop

| Iteration | What was tested | Measured/result | Next bounded action |
|---|---|---|---|
| `EXP-0004` | Compact orientation for a real interrupted-task scenario. | Declared 51,378 -> 5,653 bytes (89.00% scenario-local reduction); independent evaluation scored PASS 5/6, PARTIAL on immediate safe read. No startup-wide claim. | Complete/revise. Preserve as baseline only. |
| Post-evaluation Discovery | Whether a repeat is worthwhile or would cause scope drift. | Admit one refined experiment; retain complete point-in-time raw control, not hashes alone. Rejected runtime/index/policy expansion. | `EXP-0005`. |
| `EXP-0005` | Frozen six-row rubric, retained raw control, 50% threshold, blinded evaluator. | COMPLETE/PASS: control reverified at 44,432 bytes; distinct evaluator passed all six rows for the 2,619-byte (312-word) treatment, a 94.11% scenario-local reduction. | Park as bounded evidence; no runtime/startup-policy claim. |
| Local Ollama advisory lane | Whether existing local helpers need model downloads or only configuration repair after Pi pause. | TASK-228 released: health is ok, loopback is enforced, and only qwen3.5:4b is a drilled visible draft-only lane. | No download. Keep three-run reliability evidence visibly deferred. |

## Current ownership and boundaries

- `TASK-220` is RELEASED.
- `TASK-227` remains `CHANGES_REQUESTED`, owned by `claude-lab-gome`; only its
  owner may edit `MAP_System/notes/system-improvement-implementation-plan.md`
  unless ownership is explicitly transferred. The five REQUIRED review points
  are in `artifacts/reviews/task227-review-lilo.md`.
- Discovery stays visible but event-triggered. It is used at a named decision
  point, has a durable helper note/output, and returns to listening afterward;
  it is not a permanent autonomous policy or ambient model scout.
- Local models remain helper-capability-only and draft/check/recommendation
  support; they cannot own a task, approve review/release, or make authority
  decisions.

## Resume order

1. Preserve EXP-0005 as bounded evidence and do not convert it into a
   runtime/index/startup-policy change without repeated evidence.
2. When Claude capacity is confirmed, resume `TASK-227` rework under its
   existing owner and review gate.
3. Reassess all experiments against the north-star outcome; preserve negative
   results and avoid a runtime/policy expansion without repeated evidence.

## Primary records

- `MAP_System/notes/system-improvement-kickoff.md`
- `MAP_System/handoffs/HANDOFF-20260718-system-improvement-kickoff-to-claude.md`
- `MAP_System/artifacts/experiments/orientation-manifest-baseline-evaluation-2026-07-18.md`
- `MAP_System/artifacts/experiments/orientation-manifest-post-evaluation-discovery-2026-07-18.md`
- `MAP_System/emergence/experiments/EXP-0004-a-scoped-orientation-manifest-can-reduce-a-resumed-agent-s-conte.md`
- `MAP_System/emergence/experiments/EXP-0005-a-frozen-rubric-and-retained-control-can-test-orientation-sa.md`
- `MAP_System/artifacts/experiments/pi-local-capability-trial-2026-07-18.md`
