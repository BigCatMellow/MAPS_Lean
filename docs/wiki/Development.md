# Development

> **Live status snapshot, not authority.** GitHub `main` and
> [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
> remain canonical. Open PRs and proposals do not change shipped behavior or the
> canonical capability scoreboard.

**Last refreshed:** 2026-09-09 ET  
**Canonical `main`:** `25c7729`  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

For the deeper working view, open the
[MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

MAPS_L is currently closing evidence gaps rather than adding replacement
implementations for capabilities that already have production call sites.

| State | Work | What remains | Source |
| --- | --- | --- | --- |
| **NEXT** | 6.4 — destructive-action enforcement | Exercise the merged default-off `HarnessService.stop()` production path and capture the first real `BEFORE_DESTRUCTIVE_ACTION` evidence before considering the capability row complete. | [PR #306](https://github.com/BigCatMellow/MAPS_Lean/pull/306) |
| **NEXT** | 6.22 — context-send / memory provenance | Exercise a real bound `maps run send-context --deliver-context` path and capture `BEFORE_SEND` + memory-provenance guard evidence before considering the capability row complete. | [PR #310](https://github.com/BigCatMellow/MAPS_Lean/pull/310) |
| **PROPOSED** | Emergence supersession authority | PR #319 proposes allowing Emergence to challenge/redesign/supersede established MAPS_L mechanisms while keeping execution authority elsewhere. This is **not current behavior** until reviewed, authorized, and merged. | [PR #319](https://github.com/BigCatMellow/MAPS_Lean/pull/319) |
| **DECISION NEEDED** | Trajectory follow-ups | Operator disposition remains useful for recurring insight/idea items surfaced by trajectory check #26, including the diff-equivalence review-revalidation idea. | [PR #318](https://github.com/BigCatMellow/MAPS_Lean/pull/318) |

## Recently shipped

- **Roadmap trajectory check #26 — SHIPPED.** Re-derived the canonical
  scoreboard as **19 / 10 / 6**, confirmed row 6.16 (Git worktree isolation) as
  DONE, and kept 6.4/6.22 IN PROGRESS because their first real hook exposures
  remain unproven. [PR #318](https://github.com/BigCatMellow/MAPS_Lean/pull/318)
- **Cross-root synthesis — SHIPPED.** Emergence can deliberately compare
  separate roots/arcs/domains for meaningful transfer, contradiction,
  composition, dependencies, or alternative frames. This did **not** expand
  Capture/Promote authority. [PR #315](https://github.com/BigCatMellow/MAPS_Lean/pull/315)
- **HCOM_DIR precedence — SHIPPED.** Explicit `--hcom-dir` now wins over an
  inherited shell `HCOM_DIR`, which wins over the `.hcom` default; real
  conflicts warn once. [PR #317](https://github.com/BigCatMellow/MAPS_Lean/pull/317)
- **Worktree-bound canonical enforcement — SHIPPED.** Real worktree mismatch
  and unavailable paths were exercised and row 6.16 is canonically DONE.
  [PR #304](https://github.com/BigCatMellow/MAPS_Lean/pull/304)
- **Production context-send path — SHIPPED, capability still incomplete.**
  `maps run send-context` provides a guarded default-off `HarnessService.send()`
  production route. The call site is shipped; row 6.22 still needs first real
  exposure evidence. [PR #310](https://github.com/BigCatMellow/MAPS_Lean/pull/310)
- **Production stop path — SHIPPED, capability still incomplete.** A bounded
  default-off `HarnessService.stop()` caller exists for persistent canonical
  denial. Row 6.4 still needs first real hook exposure evidence.
  [PR #306](https://github.com/BigCatMellow/MAPS_Lean/pull/306)

## Capability-area snapshot

| Area | Current read | Development direction |
| --- | --- | --- |
| **Harness Mechanics** | Advanced / active | Prove remaining real enforcement exposures rather than add duplicate call sites. |
| **Procedural Knowledge & Skills** | Advanced | S1–S6 are DONE; later semantic retrieval/routing work remains separate from the completed explicit-first routing slice. |
| **Environment & Reproducibility** | Mixed / in progress | Worktree-bound execution is materially stronger and row 6.16 is DONE; broader environment/deployment automation remains incomplete. |
| **Agentic Security** | Advanced / active | Canonical resume denial and worktree guards have real evidence; 6.4 and 6.22 remain row-specific evidence gaps. |
| **Learning & Evaluation** | Active | Trajectory, triage, regression freezing, emergence, and cross-root synthesis are operating; governance expansion in #319 is still proposed. |
| **Portable Deployment** | Mixed / active | Significant canonical-run/worktree infrastructure exists, but broader portable deployment and durable project-memory work remain incomplete/deferred. |

## Likely next sequence

1. Produce the first real **6.4** destructive-action hook exposure.
2. Produce the first real **6.22** send/memory-provenance hook exposure.
3. Reconcile the exact capability rows from observed evidence; do not infer DONE
   from implementation count.
4. Review/disposition **PR #319** as a governance proposal, keeping proposal
   authority separate from execution authority.
5. Select the next capability cluster from merged evidence rather than from an
   old planned sequence.

## Development surfaces

- [Live Roadmap — Overview](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit)
- [Canonical capability checklist](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
- [Agent-harness capability roadmaps](https://github.com/BigCatMellow/MAPS_Lean/tree/main/work/roadmaps/agent-harness-capabilities)
- [Open pull requests](https://github.com/BigCatMellow/MAPS_Lean/pulls)

## Status-reading rule

A useful distinction in current MAPS_L development is:

> **Production code may exist while the capability remains IN PROGRESS.**

Several roadmap rows require observed production evidence before they can be
called DONE. The Development page therefore distinguishes implementation from
closure and **SHIPPED** behavior from **PROPOSED** behavior.
