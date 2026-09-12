# Development

> **Live status snapshot, not authority.** GitHub `main` and
> [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
> remain canonical. Open PRs and proposals do not change shipped behavior or the canonical capability scoreboard.

**Last refreshed:** 2026-09-11 14:22 ET  
**Canonical main at reconciliation:** `344b4ae` *(this Development-only refresh advances `main` without changing capability behavior)*  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

No implementation merged to `main` in the last 24 hours. Work advanced inside the seven open PRs rather than changing canonical capability status.

1. **#340 — durable handoff lifecycle:** corrections, integration onto current `main`, exact-head validation, and fresh independent integrated-head review are complete. It is now at **final merge disposition**, not a repair gate.
2. **#341 — protocol-effectiveness benchmark:** the owner has corrected the remaining J1 safeguard issue after seven review passes. A fresh independent J1 re-review is still required before `APPROVED FOR CORPUS CONSTRUCTION` can be claimed.
3. **#335 — recovery ambiguity safety:** reviewed and green; keep the change narrow and merge only through the required authority path.
4. **#338 → #339 — canonical task/history retention:** reviewed/green design and stacked enforcement; preserve dependency order.
5. **#336/#337 — reviewer execution provenance:** technically reviewed but substantively `BLOCKED_ON_TRUSTED_PRODUCER`; do not replace trusted provenance with reviewer self-description.
6. **6.22 — `BEFORE_SEND` / memory-provenance first exposure:** still an explicit old roadmap watch and should not disappear behind newer reliability/evaluation work.

## Active / proposed work

| State | Work | Current verified read | Source |
| --- | --- | --- | --- |
| **IN REVIEW** | Recovery ambiguity safety | #335 suppresses same-tick direct fallback after a failed bound harness resume with `RetryDisposition.UNKNOWN`; Runtime and review-evidence are green. | [#335](https://github.com/BigCatMellow/MAPS_Lean/pull/335) |
| **BLOCKED** | Trusted reviewer execution lineage | #336 defines the missing execution-provenance relation. #337 finds no current trusted producer that independently proves actual machine/process reviewer execution → logical reviewer principal. Green CI does not remove this substantive blocker. | [#336](https://github.com/BigCatMellow/MAPS_Lean/pull/336) · [#337](https://github.com/BigCatMellow/MAPS_Lean/pull/337) |
| **IN REVIEW** | Canonical task/history retention | #338 defines the narrow retention contract; stacked #339 adds DB guards rejecting task-event update/delete and canonical task hard-delete. Both current heads are runtime/review green; #338 must integrate before or with #339. | [#338](https://github.com/BigCatMellow/MAPS_Lean/pull/338) · [#339](https://github.com/BigCatMellow/MAPS_Lean/pull/339) |
| **IN REVIEW — FINAL MERGE DISPOSITION** | Durable handoff lifecycle | #340 now has corrected thread-only lifecycle semantics, root `AGENTS.md` below its enforced size budget, integration onto accepted `main`, exact-head validation, fresh independent integrated-head **APPROVE**, and green Runtime/review-evidence. No implementation defect remains; merge is a separate authority action. | [#340](https://github.com/BigCatMellow/MAPS_Lean/pull/340) |
| **IN REVIEW** | Protocol-effectiveness benchmark | #341 has progressed through one major and six minor-correction reviews. At current head, J1 is owner-corrected but still awaits focused independent verification. Runtime is green; review-evidence remains red. Nothing has been executed. | [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341) |
| **NEXT / WATCH** | 6.22 — real `BEFORE_SEND` / memory-provenance exposure | The production `maps run send-context --deliver-context` path is shipped, but trajectory #27 still found no real first-exposure evidence. | [#310](https://github.com/BigCatMellow/MAPS_Lean/pull/310) · [#332](https://github.com/BigCatMellow/MAPS_Lean/pull/332) |
| **IN PROGRESS / EVIDENCE-GATED** | E5 recovery compatibility | Stage-0 design is merged (#325), but enforcement remains withheld. Advisory operational evidence is the legitimate next step if reprioritized. | [#325](https://github.com/BigCatMellow/MAPS_Lean/pull/325) |

## Operator decisions / blockers

- **Merge authority remains separate from CI/readiness.** Every merge to `main` still requires the repository's mandatory `scripts/opcmd_merge.py` path and operator-authored authorization. This now applies to #340 as a ready-to-dispose merge as well as the other green PRs.
- **Reviewer-execution lineage remains blocked on trusted evidence.** If a credible producer requires a new account/App, provider access, credentials, or spending, that bounded branch needs explicit operator authority. Until then, #337's `BLOCKED_ON_TRUSTED_PRODUCER` is the honest state.
- **Protocol benchmark corpus/model execution is not authorized.** #341 first needs a fresh independent `APPROVED FOR CORPUS CONSTRUCTION` verdict. That would authorize bounded corpus construction/review only, not scored model/API runs or spending.
- **E5 enforcement remains intentionally withheld** pending real advisory production evidence.
- **Issue #331 remains open.** Its two tool-friction records still need a safe terminal/local append into `work/coordination/FRICTION_LOG.md`; do not reconstruct the large log from truncated connector output. [#331](https://github.com/BigCatMellow/MAPS_Lean/issues/331)

## Meaningful recently shipped changes

No code or capability-changing commit landed in the last 24 hours. The most meaningful current shipped basis remains:

- **6.4 destructive-action first exposure:** #320 proved real `BEFORE_DESTRUCTIVE_ACTION` DENY/ALLOW behavior; the broader row remains IN PROGRESS for residual controls.
- **H4 enforced-validation first exposure:** #324 proved real quick-tier enforcement can block resume without consuming attempt budget; normal/full tiers and per-spec enforcement remain open.
- **Reliability/evidence wave:** #322–#334 landed roadmap reconciliation, borrow-before-build evidence, regression hardening, dependency-cycle rejection, recovery-ambiguity characterization, cost/resource analysis, transaction rollback proof, operator insight dispositions, and stalled-worker repair closure.
- **Trajectory check #27:** #332 re-derived **19 / 10 / 6**, action **CONTINUE**, and placed 6.22 on explicit watch.

## Capability-area snapshot

| Area | Current read | Development direction |
| --- | --- | --- |
| **Harness Mechanics** | Advanced / active | Core resume/stop/send machinery exists. #335 tightens ambiguous-resume safety. H4 residual tiers remain; 6.22 still needs a real send exposure. |
| **Procedural Knowledge & Skills** | Advanced | S1–S6 remain DONE; later semantic/retrieval expansion stays evidence-gated. |
| **Environment & Reproducibility** | Mixed / active | 6.16 is DONE; H4 has first-exposure evidence but residual tiers remain; E5 is advisory/evidence-gated. |
| **Agentic Security** | Advanced / active | Real resume and destructive-action evidence exist; 6.4 remains open for residual controls and 6.22 lacks real send/provenance exposure. |
| **Learning & Evaluation** | Active / maturing | Emergence/trajectory machinery operates; #341 is building a falsifiable effectiveness benchmark but is not approved for corpus construction. |
| **Portable Deployment** | Mixed / active | Worktree/canonical-run infrastructure is substantial; #340 handoff lifecycle is now review-valid and awaiting merge disposition. Durable project memory/context compilation remain deferred. |

## Likely next sequence

1. Resolve **#340** through the final merge-authority gate; do not redo its corrected implementation/review.
2. Obtain the focused fresh independent J1 review for **#341**. Do not construct the corpus until it earns `APPROVED FOR CORPUS CONSTRUCTION`.
3. Integrate **#335** and **#338 → #339** only after current-head/dependency checks and operator merge authorization.
4. Treat **#337** as a legitimate stop condition unless a trusted producer is actually identified; do not add self-attested provenance fields.
5. Run the overdue **6.22** real `BEFORE_SEND` / memory-provenance exposure before another roadmap arc makes it recurring debt.
6. Re-derive capability status from merged evidence before opening another broad capability arc.

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

> **Open work can become technically/review ready without becoming shipped, and green CI can coexist with a substantive BLOCKED state.**

This page separates **SHIPPED/current behavior** from **IN REVIEW/PROPOSED/BLOCKED work**. Open work never changes the canonical scoreboard by itself.
