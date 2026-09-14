# Development

> **Live status snapshot, not authority.** GitHub `main` and
> [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
> remain canonical. Open PRs and proposals do not change shipped behavior or the canonical capability scoreboard.

**Last refreshed:** 2026-09-14 1:49 PM ET  
**Canonical main at reconciliation:** `08fd074` *(this Development-only refresh advances `main` without changing capability behavior)*  
**Capability/code basis:** `557abf6`  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

No implementation or capability-changing commit landed in the preceding 24 hours. Only **PR #341** remains open. The main development frontier therefore remains the same, and this page deliberately does not invent movement where none occurred.

1. **6.22 — memory-provenance enforcement:** #356 already proved a real non-vacuous referenced-only `WITHHOLD` provenance item through the production send path. #355 established that embedded-WITHHOLD and guard-level `DENY` are structurally unreachable through the current legitimate assembler because upstream assembly filters DENY items and emits WITHHOLD as `embedded=false`. The row remains **IN PROGRESS** pending a bounded exit-criterion/architecture disposition; repeating the same fixture would not add evidence.
2. **#341 — protocol-effectiveness benchmark:** design remains **APPROVED FOR CORPUS CONSTRUCTION**. Current head `e06e6b0` has successful Runtime and review-evidence checks, but GitHub reports `mergeable=false`. The substantive blocker remains genuinely independent corpus custody: a fresh chat under the same owner account is not eligible. No benchmark case selection or model/API execution has occurred.
3. **Issue #331 — tool friction:** still temporarily holds two verified friction records that need a safe terminal/local append into `work/coordination/FRICTION_LOG.md` before the issue can close.
4. **Reviewer execution lineage:** remains `BLOCKED_ON_TRUSTED_PRODUCER`; no independent producer currently proves the actual machine/process/provider execution behind a logical reviewer identity.

## Active / proposed work

| State | Work | Current verified read | Source |
| --- | --- | --- | --- |
| **DECISION NEEDED** | 6.22 residual closure | Real referenced-only WITHHOLD behavior is proven. Remaining stronger guard branches cannot arise through the current legitimate assembler without architecture change or an adversarial payload. Decide whether those branches are genuinely required by the row's exit criterion or whether upstream filtering is the intended enforcement boundary. | [Checklist](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md) · [#355](https://github.com/BigCatMellow/MAPS_Lean/pull/355) · [#356](https://github.com/BigCatMellow/MAPS_Lean/pull/356) |
| **BLOCKED** | #341 — benchmark corpus custody | Design approved; pre-authoring complete; current checks green. Private selection still requires a curator/custodian inaccessible to MAPS_L protocol modifiers; GitHub currently reports the PR non-mergeable. | [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341) |
| **NEXT** | Issue #331 — tool-friction capture | Temporary issue still holds code-search false-negative and unsafe-large-file-append records. | [#331](https://github.com/BigCatMellow/MAPS_Lean/issues/331) |
| **BLOCKED** | Trusted reviewer execution lineage | Merged #336/#337 found no trustworthy producer independently binding actual reviewer execution to reviewer principal. Preserve the blocker rather than substituting self-attested metadata. | [#337](https://github.com/BigCatMellow/MAPS_Lean/pull/337) |
| **IN PROGRESS / EVIDENCE-GATED** | E5 recovery compatibility | Stage-0 design is merged; enforcement remains withheld pending advisory production evidence. | [#325](https://github.com/BigCatMellow/MAPS_Lean/pull/325) |

## Operator decisions / blockers

- **6.22 needs a bounded disposition.** Do not fabricate an adversarial payload merely to produce a `DENY`. First determine whether its actual exit criterion requires an organically reachable stronger branch or whether the production assembler's earlier filtering is the intended boundary.
- **#341 independent custody may cross a real authority boundary.** New storage, accounts, credentials, provider access, or spending require explicit authority. Benchmark execution remains separately unauthorized.
- **Reviewer-execution lineage remains blocked** absent a trusted producer.
- **E5 enforcement remains intentionally withheld** pending real advisory evidence.
- **Issue #331 remains open** until its two captured records are safely appended to the canonical friction log.

## Meaningful recently shipped changes

- **6.22 non-vacuous provenance (#355/#356):** a real `WITHHOLD` provenance entry was re-derived in production and withheld content stayed out of the delivered message; the stronger residual branches were shown to be structurally unreachable through the current assembler.
- **Handoff reconciliation (#351/#354/#358):** repeated register/receipt drift now has a CI safeguard plus recurring reconciliation ownership.
- **Standing merge authorization (#352):** routine clean/reviewed/green merges can use the reviewed standing-authorization path while retaining hard safety gates and a live HOLD/STOP kill switch.
- **Coordination safeguards (#348/#350):** post-hoc direct-main alerting and isolated-worktree defaults are canonical.
- **Cross-project dependency visibility (#357):** THINK/PLAN/Prime are visible as dependencies without granting MAPS_L authority over them.

## Capability-area snapshot

| Area | Current read | Development direction |
| --- | --- | --- |
| **Harness Mechanics** | Advanced / active | Core contracts, recovery, stop/send paths, worktree enforcement and ambiguity safety are established; H4 residual tiers remain. |
| **Procedural Knowledge & Skills** | Advanced | S1–S6 remain DONE. Use measured benchmark evidence before expanding instruction machinery. |
| **Environment & Reproducibility** | Mixed / active | 6.16 is DONE; H4 quick-tier enforcement is proven; normal/full/per-spec gaps and E5 advisory evidence remain. |
| **Agentic Security** | Advanced / active | Real resume, destructive-action and send/provenance exposures exist. 6.22 now needs exit-criterion/architecture reconciliation, not another equivalent fixture. |
| **Learning & Evaluation** | Active / blocked | #341 design is approved; private corpus construction is blocked on independent custody. No benchmark execution has occurred. |
| **Portable Deployment / Continuity** | Mixed / active | Durable handoff lifecycle and receipt-drift safeguards are shipped; durable project memory/context compilation remain deferred. |

## Likely next sequence

1. Reconcile **6.22** against its exact exit criterion and the #355/#356 production evidence; record a bounded disposition before further testing or architecture work.
2. Preserve **#341**'s custody boundary; establish an eligible curator only if genuine separation is possible and separately authorize any external resources required.
3. Move **issue #331** into the canonical friction log and close the temporary issue.
4. Re-derive the next MAPS_L-owned capability priority from merged evidence; THINK/PLAN/Prime remain visibility-only dependencies.

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

> **No change is also a result.** If live `main`, canonical evidence, and the open queue have not materially moved, preserve the prior status rather than manufacturing a new milestone. Evidence can narrow a blocker without automatically closing a capability.
