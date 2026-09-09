# Development

> **Live status snapshot, not authority.** GitHub `main` and
> [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
> remain canonical. Open PRs and proposals do not change shipped behavior or the
> canonical capability scoreboard.

**Last refreshed:** 2026-09-09 14:42 ET  
**Reconciled against `main`:** `60c0dbf` *(this source-only refresh may advance the tip)*  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

For the deeper working view, open the
[MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

MAPS_L is primarily converting already-shipped mechanisms into real production
evidence while separately reviewing a growing borrow-before-build research/test
wave. The two must stay distinct: evidence/research can sharpen work without
changing canonical capability status until merged and reconciled.

| State | Work | What remains | Source |
| --- | --- | --- | --- |
| **IN REVIEW** | 6.4 — destructive-action enforcement | PR #320 has produced the first real `BEFORE_DESTRUCTIVE_ACTION` firing on the merged stop path. Review/reconcile the evidence and the recovery-authority caveat; row 6.4 remains canonically IN PROGRESS because other stated controls remain open. | [PR #320](https://github.com/BigCatMellow/MAPS_Lean/pull/320) |
| **NEXT** | 6.22 — context-send / memory provenance | The production `HarnessService.send()` path is shipped, but a real `BEFORE_SEND` / memory-provenance exposure still has not been recorded. | [PR #310](https://github.com/BigCatMellow/MAPS_Lean/pull/310) |
| **IN REVIEW** | H4 — enforced validation | PR #324 has produced the first real enforced quick-tier validation failure that blocks resume before any resume call. H4 remains IN PROGRESS because normal/full tiers and per-spec enforcement remain deferred. | [PR #324](https://github.com/BigCatMellow/MAPS_Lean/pull/324) |
| **PROPOSED** | Emergence supersession authority | PR #319 proposes allowing Emergence to challenge/redesign/propose supersession of established mechanisms while leaving execution authority elsewhere. This is not current behavior. Runtime and review-evidence checks are green, but the governance substance still requires operator disposition. | [PR #319](https://github.com/BigCatMellow/MAPS_Lean/pull/319) |
| **IN REVIEW** | Borrow-before-build / roadmap evidence wave | PRs #322–#330 add reconciliation, research, regressions, design audits, and one dependency-cycle runtime fix. They do not change canonical capability status while open. Review state is mixed; notably #327 is currently failing and several others still lack valid review evidence. | [Open PRs](https://github.com/BigCatMellow/MAPS_Lean/pulls) |
| **BLOCKED** | Full Wiki reconciliation | PR #321 is runtime-green but review-evidence-red and currently non-mergeable against newer canonical Wiki source. It must be reconciled without overwriting this Development snapshot. | [PR #321](https://github.com/BigCatMellow/MAPS_Lean/pull/321) |

## Operator decisions / blockers

- **PR #319 — governance decision.** The proposed supersession authority is an
  explicit expansion of what Emergence may propose. It still requires operator
  disposition even with green technical/review checks.
- **E5 recovery compatibility remains evidence-gated.** PR #325 identifies the
  enforcement seam but explicitly recommends an advisory production exposure
  before revisiting the previously withheld enforcement decision.
- **Merge authority remains separate from CI readiness.** Open PRs may be green
  without being authorized to merge; repository policy requires the mechanical
  merge-authority path.
- **Issue #331 is temporary friction capture.** Its two tool-gap entries still
  need a terminal-safe append into `work/coordination/FRICTION_LOG.md`; do not
  reconstruct the large canonical file from truncated connector output.

## Recently shipped

- **Development Wiki source/navigation — SHIPPED.** `docs/wiki/Development.md`
  and `[[Development]]` in `_Sidebar.md` are canonical repository-owned Wiki
  sources, published through the existing Wiki sync workflow.
- **Roadmap trajectory check #26 — SHIPPED.** Canonical scoreboard is
  **19 / 10 / 6**; 6.16 is DONE while 6.4 and 6.22 remain IN PROGRESS pending
  their own row-specific evidence. [PR #318](https://github.com/BigCatMellow/MAPS_Lean/pull/318)
- **Cross-root synthesis — SHIPPED.** Emergence can deliberately compare
  separate roots/arcs/domains without changing execution authority.
  [PR #315](https://github.com/BigCatMellow/MAPS_Lean/pull/315)
- **HCOM_DIR precedence — SHIPPED.** Explicit `--hcom-dir` wins over inherited
  `HCOM_DIR`, which wins over the `.hcom` default; real conflicts warn once.
  [PR #317](https://github.com/BigCatMellow/MAPS_Lean/pull/317)
- **6.4 and 6.22 production call sites — SHIPPED, capability rows still open.**
  The stop and context-send paths exist on `main`; row closure still depends on
  each row's own exit criteria. [PR #306](https://github.com/BigCatMellow/MAPS_Lean/pull/306) · [PR #310](https://github.com/BigCatMellow/MAPS_Lean/pull/310)

## Capability-area snapshot

| Area | Current read | Development direction |
| --- | --- | --- |
| **Harness Mechanics** | Advanced / active | 6.4 has real exposure evidence in #320; H4 has real validation-gate evidence in #324; 6.22 still needs its real send exposure. |
| **Procedural Knowledge & Skills** | Advanced | S1–S6 are DONE; competitor research may strengthen later work but does not alter current status. |
| **Environment & Reproducibility** | Mixed / active | 6.16 is DONE; H4 exposure advanced; E5 remains advisory/evidence-gated rather than implementation-ready. |
| **Agentic Security** | Advanced / active | Real resume and destructive-action guard evidence exist; 6.22 remains the clearest unexercised hook path. |
| **Learning & Evaluation** | Active / review | Cross-root synthesis is shipped; supersession authority is proposed; borrow-before-build evidence is being routed through existing owners. |
| **Portable Deployment** | Mixed / active | Canonical-run/worktree infrastructure is strong; PR #322 proposes later external-pilot testing without changing current status. |

## Likely next sequence

1. Reconcile **PR #320** against row 6.4 without overclaiming closure.
2. Produce the first real **6.22** `BEFORE_SEND` / memory-provenance exposure.
3. Reconcile **PR #324** into H4 evidence while preserving its remaining gaps.
4. Repair **PR #321** and **PR #327** before treating either as integration-ready.
5. Review the #322–#330 research/test wave and promote only bounded findings
   supported by current MAPS_L owners and evidence.
6. Resolve **PR #319** as a separate governance decision.
7. Re-derive capability status from merged evidence before selecting the next
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
