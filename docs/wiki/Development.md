# Development

> **Live status snapshot, not authority.** GitHub `main` and
> [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
> remain canonical. Open PRs and proposals do not change shipped behavior or the canonical capability scoreboard.

**Last refreshed:** 2026-09-13 2:06 PM ET  
**Canonical main at reconciliation:** `557abf6` *(this Development-only refresh advances `main` without changing capability behavior)*  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

Only **PR #341** remains open. The main development frontier has shifted from call-site reachability to honest closure of remaining evidence/architecture gaps.

1. **6.22 — memory-provenance enforcement:** #356 produced the first real non-vacuous `MemoryProvenanceGuard` pass. A real promoted operational lesson became `WITHHOLD` because its review date was past, appeared as a real provenance entry, took the referenced-only (`embedded=false`) branch, and its claim text was excluded from the delivered message. The result remained `ALLOW`. #355 independently established that embedded-WITHHOLD and guard-level `DENY` are structurally unreachable through the current production assembler, so another ordinary fixture cannot exercise them. Row 6.22 correctly remains **IN PROGRESS** pending an explicit decision about the residual architecture/exit criterion.
2. **#341 — protocol-effectiveness benchmark:** design remains **APPROVED FOR CORPUS CONSTRUCTION** and checks are green, but the PR is currently non-mergeable and corpus construction is still blocked on genuinely independent custody. No benchmark case selection or model/API execution has occurred.
3. **Durable handoff discipline:** #351 triaged 62 legacy handoffs; #354 fixed a newly missed receipt; #358 converted the repeated receipt/register drift into a CI safeguard plus trajectory-check reconciliation ownership.
4. **Cross-project visibility:** #357 adds THINK/PLAN/Prime dependency visibility to the checklist only. It grants no MAPS_L authority over those projects and does not change the 19/10/6 scoreboard.

## Active / proposed work

| State | Work | Current verified read | Source |
| --- | --- | --- | --- |
| **DECISION NEEDED** | 6.22 residual closure | Real referenced-only WITHHOLD behavior is now proven. The real assembler filters DENY-classed items before send and emits WITHHOLD items only as `embedded=false`, making the remaining DENY/embedded-WITHHOLD guard branches structurally unreachable without an adversarial payload or architecture change. Decide whether 6.22's exit criterion requires such a path or whether the current fail-closed composition/evidence is sufficient after reconciliation. | [Checklist](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md) · [#355](https://github.com/BigCatMellow/MAPS_Lean/pull/355) · [#356](https://github.com/BigCatMellow/MAPS_Lean/pull/356) |
| **BLOCKED** | #341 — protocol-effectiveness benchmark corpus | Design is approved and both checks are green. Private corpus selection still requires an independent curator/custodian inaccessible to MAPS_L protocol modifiers; GitHub currently also reports the PR non-mergeable. | [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341) |
| **NEXT** | Issue #331 — tool-friction capture | Temporary issue still holds two friction records: code-search false negatives and lack of safe large-file append. | [#331](https://github.com/BigCatMellow/MAPS_Lean/issues/331) |
| **BLOCKED** | Trusted reviewer execution lineage | Merged #336/#337 found no trustworthy producer independently binding actual reviewer execution to reviewer principal. Preserve `BLOCKED_ON_TRUSTED_PRODUCER`; do not replace proof with self-attested fields. | [#337](https://github.com/BigCatMellow/MAPS_Lean/pull/337) |
| **IN PROGRESS / EVIDENCE-GATED** | E5 recovery compatibility | Stage-0 design is merged; enforcement remains withheld pending advisory production evidence. | [#325](https://github.com/BigCatMellow/MAPS_Lean/pull/325) |

## Operator decisions / blockers

- **Routine merge authorization changed:** #352 added a reviewed standing-authorization path to `scripts/opcmd_merge.py`. Clean merge state, independent review evidence, green CI, and live HOLD/STOP remain mechanical gates; routine merges no longer require a fresh operator message for every PR when the standing record applies.
- **6.22 residual semantics need a bounded disposition.** Do not fabricate an adversarial payload merely to make `DENY` reachable. First decide whether the row requires an organically reachable DENY/embedded-WITHHOLD production path or whether the production assembler's earlier filtering is itself the intended enforcement boundary.
- **#341 independent custody may cross a real authority boundary.** New storage, accounts, credentials, provider access, or spending require explicit authority. Benchmark execution remains separately unauthorized.
- **Reviewer-execution lineage remains blocked** absent a trusted producer.
- **E5 enforcement remains intentionally withheld** pending real advisory evidence.
- **Issue #331 remains open** until its two captured records are safely appended to the canonical friction log.

## Meaningful recently shipped changes

- **6.22 non-vacuous provenance (#355/#356):** a real `WITHHOLD` provenance entry was re-derived in production; referenced-only content stayed out of the delivered message. The design audit also established which stronger branches are structurally unreachable through the current assembler.
- **Handoff reconciliation (#351/#354/#358):** legacy handoffs were triaged, a new missing receipt was repaired, and repeated register/receipt drift now has a CI check plus a recurring reconciliation owner.
- **Standing merge authorization (#352):** routine clean/reviewed/green merges can use a standing authorization record while retaining hard safety gates and a live HOLD/STOP kill switch.
- **Isolated-worktree default (#350):** existing practice is now named in root `AGENTS.md` without exceeding the enforced instruction-size budget.
- **Direct-to-main alert (#348/#349):** repeat admin-bypass direct pushes now trigger a post-hoc CI alert; trajectory #30 kept the scoreboard at 19/10/6 and action `CONTINUE`.
- **Cross-project dependency visibility (#357):** THINK/PLAN/Prime are visible from the checklist without changing their own authorization gates or MAPS_L authority.

## Capability-area snapshot

| Area | Current read | Development direction |
| --- | --- | --- |
| **Harness Mechanics** | Advanced / active | Core contracts, recovery, stop/send paths, worktree enforcement and ambiguity safety are established; H4 residual tiers remain. |
| **Procedural Knowledge & Skills** | Advanced | S1–S6 remain DONE. Use measured benchmark evidence before expanding instruction machinery. |
| **Environment & Reproducibility** | Mixed / active | 6.16 is DONE; H4 quick-tier enforcement is proven; normal/full/per-spec gaps and E5 advisory evidence remain. |
| **Agentic Security** | Advanced / active | Real resume, destructive-action and send/provenance exposures exist. 6.22 now has real non-vacuous referenced-only WITHHOLD evidence; residual DENY/embedded branches are structurally unreachable through the current assembler. |
| **Learning & Evaluation** | Active / blocked | #341 design is approved; private corpus construction is blocked on independent custody. No benchmark execution has occurred. |
| **Portable Deployment / Continuity** | Mixed / active | Durable handoff lifecycle, legacy reconciliation and receipt-drift safeguards are shipped; durable project memory/context compilation remain deferred. |

## Likely next sequence

1. Reconcile **6.22** against the new #355/#356 evidence and make a bounded decision on the structurally unreachable residual branches before opening another fixture.
2. Preserve **#341**'s custody boundary; establish an eligible curator only if genuine separation is possible and separately authorize any external resources required.
3. Move **issue #331** into the canonical friction log and close the temporary issue.
4. Re-derive the next broad capability priority from merged evidence; treat THINK/PLAN/Prime rows as visibility-only dependencies, not MAPS_L dispatch authority.

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

> **Evidence can narrow a blocker without automatically closing a capability.** A branch that cannot occur through the real production assembler should trigger an exit-criterion/architecture decision, not a synthetic test solely to manufacture coverage.

Open work never changes the canonical scoreboard by itself.