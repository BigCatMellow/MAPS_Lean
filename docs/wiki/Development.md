# Development

> **Live status snapshot, not authority.** GitHub `main` and
> [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
> remain canonical. Open PRs and proposals do not change shipped behavior or the canonical capability scoreboard.

**Last refreshed:** 2026-09-09 15:12 ET  
**Reconciled against `main`:** `378468c` *(includes #319/#320/#324/#325 and the merge-train wiki-status commits)*  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

Close evidence gaps before starting another broad capability arc:

1. reconcile the real **6.4** destructive-action exposure in PR #320;
2. run the still-missing real **6.22** `BEFORE_SEND` / memory-provenance exposure;
3. reconcile the real **H4** enforced-validation exposure in PR #324;
4. review the larger borrow-before-build/test wave without letting open research redefine canonical status.

| State | Work | Current verified read | Source |
| --- | --- | --- | --- |
| **MERGED — row still IN PROGRESS** | 6.4 — destructive-action enforcement | PR #320 (merged) produced the first real `BEFORE_DESTRUCTIVE_ACTION` DENY/ALLOW/control evidence. Row 6.4 remains canonically IN PROGRESS because other stated controls remain open. | [#320](https://github.com/BigCatMellow/MAPS_Lean/pull/320) |
| **NEXT** | 6.22 — send / memory provenance | The production `send-context` / `HarnessService.send()` path is shipped, but no real `BEFORE_SEND` / `MemoryProvenanceGuard` exposure is recorded yet. | [#310](https://github.com/BigCatMellow/MAPS_Lean/pull/310) |
| **MERGED — row still IN PROGRESS** | H4 — immediate validation | PR #324 (merged) proved a real failing quick-tier validation can park recovery before resume while preserving attempt budget. H4 remains IN PROGRESS for normal/full tiers and per-spec enforcement. | [#324](https://github.com/BigCatMellow/MAPS_Lean/pull/324) |
| **MERGED — current behavior** | Emergence supersession authority | PR #319 is merged (commit `69d6497`, 2026-09-09). Emergence may now explicitly challenge/redesign/propose replacement of established mechanisms; proposal authority stays distinct from execution/merge authority. | [#319](https://github.com/BigCatMellow/MAPS_Lean/pull/319) |
| **IN REVIEW** | Borrow-before-build / reliability wave | PRs #322–#330 add reconciliation, research, regressions, design audits and bounded runtime hardening. All checked heads are runtime-green; #322/#323/#326/#327/#328/#329/#330 still fail the repository review-evidence gate. None changes the canonical capability score while open. | [Open PRs](https://github.com/BigCatMellow/MAPS_Lean/pulls) |
| **BLOCKED** | Full Wiki reconciliation | PR #321 is runtime-green but review-evidence-red and currently non-mergeable against newer canonical Wiki source. It must preserve this Development snapshot when reconciled. | [#321](https://github.com/BigCatMellow/MAPS_Lean/pull/321) |
| **MERGED — design-only** | E5 recovery compatibility | PR #325 (merged) is a Stage-0 design note. It identifies the enforcement seam but keeps enforcement withheld; the next evidence step is an advisory production exposure, not Stage-3 implementation. | [#325](https://github.com/BigCatMellow/MAPS_Lean/pull/325) |

## Operator decisions / blockers

- **PR #319 — RESOLVED.** The operator governance decision landed: PR #319 is merged (`69d6497`). Emergence-proposed supersession of established mechanisms is now permitted, with proposal authority still distinct from execution/merge authority.
- **Merge authority remains separate from CI readiness.** Every merge to `main` still requires the repository's mandatory `scripts/opcmd_merge.py` path and operator-authored authorization.
- **E5 enforcement remains intentionally withheld.** PR #325 does not authorize implementation; advisory operational evidence is still missing.
- **Issue #331 remains open.** Two tool-friction records need a safe terminal/local append into `work/coordination/FRICTION_LOG.md`; do not reconstruct the large canonical log from truncated connector output. [#331](https://github.com/BigCatMellow/MAPS_Lean/issues/331)

## Recently shipped

- **Emergence mechanism-supersession authority — SHIPPED.** [PR #319](https://github.com/BigCatMellow/MAPS_Lean/pull/319) lets Emergence challenge/redesign/propose replacement of established mechanisms; execution/merge authority is unchanged.
- **6.4 destructive-action first-exposure exercise — SHIPPED.** [PR #320](https://github.com/BigCatMellow/MAPS_Lean/pull/320) exercised the recovery `stop()` call site for the first real `BEFORE_DESTRUCTIVE_ACTION` firing. Row 6.4 stays IN PROGRESS.
- **H4 enforced-validation-gate first-exposure exercise — SHIPPED.** [PR #324](https://github.com/BigCatMellow/MAPS_Lean/pull/324) gave the enforced resume-validation gate its first real production exposure. Row H4 stays IN PROGRESS.
- **E5 recovery-compat enforcement-seam design note — SHIPPED.** [PR #325](https://github.com/BigCatMellow/MAPS_Lean/pull/325) is a Stage-0 design note; enforcement remains withheld.
- **Development Wiki source/navigation — SHIPPED.** `docs/wiki/Development.md` and `[[Development]]` in `_Sidebar.md` are repository-owned Wiki sources.
- **Trajectory check #26 — SHIPPED.** Canonical scoreboard is **19 / 10 / 6**; trajectory remains **CONTINUE**. [#318](https://github.com/BigCatMellow/MAPS_Lean/pull/318)
- **Cross-root synthesis — SHIPPED.** Emergence can compare separate roots/arcs/domains without changing execution authority. [#315](https://github.com/BigCatMellow/MAPS_Lean/pull/315)
- **HCOM_DIR precedence — SHIPPED.** Explicit `--hcom-dir` wins over inherited `HCOM_DIR`, which wins over `.hcom`; genuine conflicts warn. [#317](https://github.com/BigCatMellow/MAPS_Lean/pull/317)
- **6.4 and 6.22 production call sites — SHIPPED, capability rows still open.** The stop and context-send paths exist on `main`; row closure still depends on each row's own exit criteria. [#306](https://github.com/BigCatMellow/MAPS_Lean/pull/306) · [#310](https://github.com/BigCatMellow/MAPS_Lean/pull/310)

## Capability-area snapshot

| Area | Current read | Development direction |
| --- | --- | --- |
| **Harness Mechanics** | Advanced / active | 6.4 has real open exposure evidence; H4 has real open validation evidence; 6.22 still needs its real send exposure. |
| **Procedural Knowledge & Skills** | Advanced | S1–S6 are DONE; external research may strengthen later work but does not change current status. |
| **Environment & Reproducibility** | Mixed / active | 6.16 is DONE; H4 exposure advanced; E5 remains advisory/evidence-gated. |
| **Agentic Security** | Advanced / active | Real resume and destructive-action guard evidence exist; 6.22 remains the clearest unexercised hook path. |
| **Learning & Evaluation** | Active / review | Cross-root synthesis is shipped; supersession authority is proposed; competitor evidence is being routed through existing owners. |
| **Portable Deployment** | Mixed / active | Canonical-run/worktree infrastructure is strong; later external-pilot work remains proposed/evidence-gated. |

## Likely next sequence

1. Fold merged **#320** / **#324** evidence into the 6.4 / H4 rows without overclaiming closure; both stay IN PROGRESS.
2. Produce the first real **6.22** `BEFORE_SEND` / memory-provenance exposure.
3. Reconcile **#321** (this Wiki pass) and complete independent review for the red review-evidence branches in #322–#330.
4. Review borrowed findings against existing MAPS owners; prefer discriminating tests and bounded fixes over architecture-by-analogy.
5. Re-derive capability status from merged evidence before selecting the next broad roadmap increment.

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

> **Production evidence can advance a capability without automatically closing it.**

This page separates **SHIPPED/current behavior** from **IN REVIEW/PROPOSED evidence and policy**. Open work never changes the canonical scoreboard by itself.
