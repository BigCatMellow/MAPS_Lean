# Development

> **Live status snapshot, not authority.** GitHub `main` and
> [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
> remain canonical. Open PRs and proposals do not change shipped behavior or the
> canonical capability scoreboard.

**Last refreshed:** 2026-09-09 14:14 ET  
**Canonical `main` before this status-source refresh:** `18b064c`  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

For the deeper working view, open the
[MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

MAPS_L is now primarily converting already-shipped mechanisms into real
production evidence while separately evaluating a new borrow-before-build
research/testing wave.

| State | Work | What remains | Source |
| --- | --- | --- | --- |
| **IN REVIEW** | 6.4 — destructive-action enforcement | PR #320 has now produced the first real `BEFORE_DESTRUCTIVE_ACTION` firing on the merged stop path. Review/reconcile the evidence and its authority caveat; row 6.4 remains canonically IN PROGRESS. | [PR #320](https://github.com/BigCatMellow/MAPS_Lean/pull/320) |
| **NEXT** | 6.22 — context-send / memory provenance | The production `HarnessService.send()` path is shipped, but a real `BEFORE_SEND` / memory-provenance exposure still has not been recorded. | [PR #310](https://github.com/BigCatMellow/MAPS_Lean/pull/310) |
| **IN REVIEW** | H4 — enforced validation | PR #324 has produced the first real enforced quick-tier validation failure that blocks resume before any resume call. H4 remains IN PROGRESS because normal/full tiers and per-spec enforcement remain deferred. | [PR #324](https://github.com/BigCatMellow/MAPS_Lean/pull/324) |
| **PROPOSED** | Emergence supersession authority | PR #319 proposes allowing Emergence to challenge/redesign/propose supersession of established mechanisms while leaving execution authority elsewhere. This is not current behavior. | [PR #319](https://github.com/BigCatMellow/MAPS_Lean/pull/319) |
| **IN REVIEW** | Borrow-before-build / roadmap evidence wave | PRs #322–#330 add reconciliation, research, tests, design audits, and one dependency-cycle runtime fix. None changes canonical capability status unless merged and later reconciled. | [Open PRs](https://github.com/BigCatMellow/MAPS_Lean/pulls) |

## Operator decisions / blockers

- **PR #319 — governance decision.** The proposed supersession authority is an
  explicit expansion of what Emergence may propose. It still requires operator
  disposition even if technical review is green.
- **E5 recovery compatibility remains evidence-gated.** PR #325 identifies the
  enforcement seam but explicitly recommends an advisory production exposure
  before revisiting the previously withheld enforcement decision.
- **Merge authority remains separate from CI readiness.** Open PRs may be green
  without being authorized to merge.

## Recently shipped

- **Development Wiki source/navigation — SHIPPED.** `docs/wiki/Development.md`
  and `[[Development]]` in `_Sidebar.md` are now canonical repository-owned Wiki
  sources, published by the existing Wiki sync workflow.
- **Roadmap trajectory check #26 — SHIPPED.** Canonical scoreboard remains
  **19 / 10 / 6**; 6.16 is DONE while 6.4 and 6.22 remain IN PROGRESS pending
  their own evidence. [PR #318](https://github.com/BigCatMellow/MAPS_Lean/pull/318)
- **Cross-root synthesis — SHIPPED.** Emergence can deliberately compare
  separate roots/arcs/domains without changing execution authority.
  [PR #315](https://github.com/BigCatMellow/MAPS_Lean/pull/315)
- **HCOM_DIR precedence — SHIPPED.** Explicit `--hcom-dir` wins over inherited
  `HCOM_DIR`, which wins over the `.hcom` default; real conflicts warn once.
  [PR #317](https://github.com/BigCatMellow/MAPS_Lean/pull/317)
- **6.4 and 6.22 production call sites — SHIPPED, capability rows still open.**
  The stop and context-send paths exist on `main`; row closure still depends on
  each row's own evidence bar. [PR #306](https://github.com/BigCatMellow/MAPS_Lean/pull/306) · [PR #310](https://github.com/BigCatMellow/MAPS_Lean/pull/310)

## Capability-area snapshot

| Area | Current read | Development direction |
| --- | --- | --- |
| **Harness Mechanics** | Advanced / active | 6.4 has open real exposure evidence in #320; H4 has open real validation-gate evidence in #324; 6.22 still needs its real send exposure. |
| **Procedural Knowledge & Skills** | Advanced | S1–S6 are DONE; competitor research may strengthen later work but does not alter current status. |
| **Environment & Reproducibility** | Mixed / active | 6.16 is DONE; H4 exposure advanced; E5 remains advisory/evidence-gated rather than implementation-ready. |
| **Agentic Security** | Advanced / active | Real resume and destructive-action guard evidence now exist; 6.22 remains the clearest unexercised hook path. |
| **Learning & Evaluation** | Active / review | Cross-root synthesis is shipped; supersession authority is proposed; borrow-before-build evidence is being routed through existing owners. |
| **Portable Deployment** | Mixed / active | Existing canonical-run/worktree infrastructure is strong; PR #322 proposes later external-pilot testing without changing current status. |

## Likely next sequence

1. Reconcile **PR #320** against row 6.4 without overclaiming closure.
2. Produce the first real **6.22** `BEFORE_SEND` / memory-provenance exposure.
3. Reconcile **PR #324** into H4 evidence while preserving its remaining gaps.
4. Review the #322–#330 research/test wave and promote only bounded findings
   supported by current MAPS_L owners and evidence.
5. Resolve **PR #319** as a separate governance decision.
6. Re-derive capability status from merged evidence before selecting the next
   broad roadmap increment.

## Development surfaces

- [Live Roadmap — Overview](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1154882262)
- [Live Roadmap — Development](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1160745974)
- [Live Roadmap — Active Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1476804517)
- [Live Roadmap — Capability Map](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=360062140)
- [Live Roadmap — Agent Action Pack](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=189197466)
- [Live Roadmap — Daily Log](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=374922834)
- [Canonical capability checklist](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
- [Agent-harness capability roadmaps](https://github.com/BigCatMellow/MAPS_Lean/tree/main/work/roadmaps/agent-harness-capabilities)
- [Open pull requests](https://github.com/BigCatMellow/MAPS_Lean/pulls)

## Status-reading rule

A useful distinction in current MAPS_L development is:

> **Production evidence can advance a capability without automatically closing it.**

The Development page therefore separates **SHIPPED/current behavior** from
**IN REVIEW/PROPOSED evidence and policy**, and never lets an open PR change the
canonical scoreboard.