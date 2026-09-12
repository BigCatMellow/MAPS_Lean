# Development

> **Live status snapshot, not authority.** GitHub `main` and
> [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
> remain canonical. Open PRs and proposals do not change shipped behavior or the canonical capability scoreboard.

**Last refreshed:** 2026-09-12 13:53 ET  
**Canonical main at reconciliation:** `5e2f7d7` *(this Development-only refresh advances `main` without changing capability behavior)*  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

The integration queue largely cleared. Only **#341** and **#344** remain open.

1. **6.22 — memory-provenance enforcement:** the first real production `BEFORE_SEND` exposure is now recorded on `main` by #346. A live `send-context --deliver-context` actually delivered a payload through `HarnessService.send()`. The remaining gap is narrower but material: the fixture had `memory_provenance=[]`, so the guard's non-trivial `WITHHOLD`/`DENY` re-derivation paths remain unexercised. The row stays **IN PROGRESS**.
2. **#344 — 6.22 exercise evidence:** the exercise note and independent review are still in the open PR even though #346 already records their result in the canonical checklist. Preserve/land that evidence through the normal merge-authority path; do not rerun the same empty-provenance exercise.
3. **#341 — protocol-effectiveness benchmark:** the design gate is now **APPROVED FOR CORPUS CONSTRUCTION** and the owner-safe pre-authoring package is complete. The true blocker is independent custody: a curator/custodian whose private selection data and transcript are inaccessible to MAPS_L protocol modifiers. No benchmark cases or model/API runs have been executed.
4. **Reviewer execution provenance:** #336/#337 are merged. Their durable result remains `BLOCKED_ON_TRUSTED_PRODUCER`; current MAPS evidence cannot independently bind actual machine/process execution to the logical reviewer identity.

## Active / proposed work

| State | Work | Current verified read | Source |
| --- | --- | --- | --- |
| **NEXT** | 6.22 — non-vacuous memory-provenance exposure | First real `BEFORE_SEND` exposure is shipped, but the payload had an empty provenance list. Exercise real memory-like evidence so `MemoryProvenanceGuard` actually re-derives a `WITHHOLD` or `DENY` decision; do not pre-flip status. | [Checklist](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md) · [#346](https://github.com/BigCatMellow/MAPS_Lean/pull/346) |
| **IN REVIEW** | #344 — 6.22 exercise evidence | Research-only PR containing the exact exercise note and review. Runtime and review-evidence are green. Its result is already summarized on `main` by #346, so the priority is durable evidence reconciliation, not a duplicate exposure. | [#344](https://github.com/BigCatMellow/MAPS_Lean/pull/344) |
| **BLOCKED** | #341 — protocol-effectiveness benchmark corpus | Design is approved and the owner-safe pre-authoring package is complete. Construction is blocked on a genuinely independent curator/custodian. A normal fresh chat under the same owner account is explicitly ineligible. | [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341) |
| **BLOCKED** | Trusted reviewer execution lineage | #336/#337 are merged, but no trustworthy producer currently proves actual reviewer execution → logical reviewer principal independently of reviewer-supplied evidence. | [#337](https://github.com/BigCatMellow/MAPS_Lean/pull/337) |
| **IN PROGRESS / EVIDENCE-GATED** | E5 recovery compatibility | Stage-0 design is merged; enforcement remains withheld pending advisory production evidence. | [#325](https://github.com/BigCatMellow/MAPS_Lean/pull/325) |

## Operator decisions / blockers

- **Merge authority remains separate from CI/readiness.** Any desired merge still goes through mandatory `scripts/opcmd_merge.py` with operator-authored authorization.
- **#341 independent custody may cross a real authority boundary.** If the required curator/custodian channel needs new storage, accounts, credentials, provider access, or spending, obtain explicit operator authority before creating it.
- **Benchmark execution remains unauthorized.** Design approval and future corpus approval do not authorize scored model/API/evaluator execution or spending.
- **Reviewer-execution lineage remains blocked** unless a trusted execution producer is actually demonstrated; do not substitute reviewer-entered provider/model/session fields.
- **E5 enforcement remains intentionally withheld** pending real advisory evidence.
- **Issue #331 remains open.** Its tool-friction records still need a safe append into `work/coordination/FRICTION_LOG.md` from a terminal-capable workflow. [#331](https://github.com/BigCatMellow/MAPS_Lean/issues/331)

## Meaningful recently shipped changes

- **Recovery ambiguity safety (#335):** after a returned failed harness resume with `RetryDisposition.UNKNOWN`, recovery no longer immediately attempts a second direct resume in the same tick; the next tick re-observes real session state.
- **Reviewer-provenance research (#336/#337):** the design and producer audit are now canonical; the honest result is a trusted-producer blocker rather than self-attested execution metadata.
- **Canonical history retention (#338/#342):** normal hard-delete of canonical tasks and mutation/deletion of committed task events are mechanically rejected while ordinary append-only lifecycle operation remains intact.
- **Durable handoff lifecycle (#340):** durable handoffs now track acknowledgment/continuation/closure without becoming a second store of volatile GitHub state.
- **Trajectory check #28 (#343):** re-derived **19 / 10 / 6**, action **CONTINUE**, and escalated the then-unexercised 6.22 send seam; #344/#346 subsequently produced and recorded the first real exposure.
- **Rebase-safe review revalidation (#345):** pure rebases can use diff equivalence rather than literal ancestry when determining the zero-diff review tier.
- **6.22 first exposure status update (#346):** canonical checklist now records that `BEFORE_SEND` fired for real while preserving the remaining non-vacuous provenance gap and keeping 6.22 IN PROGRESS.

## Capability-area snapshot

| Area | Current read | Development direction |
| --- | --- | --- |
| **Harness Mechanics** | Advanced / active | Core contracts, lineage and recovery paths are established; #335 ambiguity safety is shipped. H4 residual tiers remain. |
| **Procedural Knowledge & Skills** | Advanced | S1–S6 remain DONE; later semantic/retrieval expansion stays evidence-gated. |
| **Environment & Reproducibility** | Mixed / active | 6.16 is DONE; H4 has real quick-tier enforcement evidence but normal/full/per-spec gaps remain; E5 is advisory/evidence-gated. |
| **Agentic Security** | Advanced / active | Real resume, destructive-action and `BEFORE_SEND` exposures exist. 6.22 remains IN PROGRESS because meaningful memory-provenance `WITHHOLD`/`DENY` behavior has not yet been exercised. |
| **Learning & Evaluation** | Active / maturing | #341's benchmark design is approved. Progress is now blocked on independent custody before private corpus construction; nothing has been executed. |
| **Portable Deployment** | Mixed / active | Durable handoff lifecycle is shipped; worktree/canonical-run infrastructure is substantial. Durable project memory/context compilation remain deferred. |

## Likely next sequence

1. Reconcile **#344** so the detailed 6.22 exercise evidence cited by canonical `main` is itself durable on `main`; do not repeat the empty-provenance exposure.
2. Design/run the smallest **non-vacuous 6.22 provenance exercise** with real recorded memory-like evidence, then independently review what the guard actually does before any status change.
3. For **#341**, establish an eligible independent curator/custodian only if the required custody can genuinely be kept outside MAPS_L protocol-modifier access; stop for operator authority if new external resources are required.
4. Move **issue #331** friction records into the canonical friction log and close the temporary issue.
5. Re-derive capability status from merged evidence before selecting another broad capability arc.

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

> **Shipped evidence can narrow a blocker without closing the capability.** A real hook firing is not the same as exercising every meaningful guard branch, and an approved benchmark design is not the same as an executed benchmark.

Open work never changes the canonical scoreboard by itself.
