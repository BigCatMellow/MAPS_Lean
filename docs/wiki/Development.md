# Development

> **Live status snapshot, not authority.** GitHub `main` and [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md) remain canonical. Open PRs and proposals do not change shipped behavior or the capability scoreboard.

**Last refreshed:** 2026-09-16 1:54 PM ET  
**Canonical main at reconciliation:** `cac29bf`  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

No implementation or capability-changing commit landed on `main` after the September 15 Development refresh. The important movement is in the open queue, which expanded from one PR to five: #341, #367, #368, #369, and #370.

PR #367 is a high-risk operating-contract/discoverability change touching `AGENTS.md` and routing surfaces. Its exact substantive head has independent approval, Runtime and review-evidence pass, and GitHub reports it mergeable. It is still proposed behavior until merged.

PR #368 reconciles legacy handoff lifecycle receipts. Its exact substantive correction has passed fresh independent review and current checks are green, but the PR explicitly requires operator merge authority. Any merge must use `scripts/opcmd_merge.py`.

PR #369 is stacked on the protocol-effectiveness benchmark branch, not `main`. It replaces the private-secret Gate 2 selection method with a public NIST-beacon-anchored deterministic selection method. The owner recomputed the package hash, but the mechanism change explicitly awaits fresh independent review before `PRE-AUTHORING PACKAGE ACCEPTED` can be claimed. No case selection, corpus construction, model/API run, or spending is authorized.

PR #370 proposes a new non-authoritative Wiki orientation page for MAPS methods and protocols. It does not change current authority, runtime behavior, or capability status while open.

## Active / next

| State | Work | Verified read | Source |
| --- | --- | --- | --- |
| **IN REVIEW** | #367 protocol discoverability / AGENTS contract | High-risk authority-surface changes independently approved; Runtime and review-evidence pass; mergeable. | [#367](https://github.com/BigCatMellow/MAPS_Lean/pull/367) |
| **DECISION NEEDED** | #368 handoff reconciliation | Reviewed correction is green and mergeable; explicit operator merge authority remains the gate. | [#368](https://github.com/BigCatMellow/MAPS_Lean/pull/368) |
| **IN REVIEW** | #369 benchmark Gate 2 rewrite | Public beacon-anchored selection is proposed on the benchmark branch; fresh independent review is still required. | [#369](https://github.com/BigCatMellow/MAPS_Lean/pull/369) |
| **PROPOSED** | #370 Wiki methods/protocols orientation | Documentation-only orientation; non-authoritative by design and not current Wiki behavior until merged/synced. | [#370](https://github.com/BigCatMellow/MAPS_Lean/pull/370) |
| **BLOCKED** | #341 protocol-effectiveness benchmark | Benchmark remains open; its pre-authoring selection/custody mechanism is being revised by stacked #369. No benchmark execution has occurred. | [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341) |
| **NEXT** | Issue #331 friction capture | Two tool-friction records still need safe migration into the canonical friction log. | [#331](https://github.com/BigCatMellow/MAPS_Lean/issues/331) |

## Meaningful recently shipped changes

- **No new implementation/capability change in the last 24 hours.** `cac29bf` is the September 15 Development-source refresh.
- The prior shipped 6.4 write-scope foundation remains current: #361 Git-scope verification, #362 explicit opt-in, and #365 `CanonicalRunGuard` wiring. No production caller currently opts in, so that foundation did not itself change the 19/10/6 score.
- #364's merge-path audit remains a durable warning: repository policy requires `scripts/opcmd_merge.py`; open #367/#368 explicitly preserve that boundary.

## Capability-area snapshot

| Area | Current read |
| --- | --- |
| Harness / security | Advanced and active. Existing 6.4 write-scope foundation is shipped; residual production exposure/status work remains governed by the exact checklist exit criteria. |
| Skills / context | Advanced. #367 proposes discoverability/contract changes but is not canonical while open. |
| Environment / reproducibility | Mixed; existing H4/E5 residuals remain. |
| Learning / evaluation | Benchmark design work is active, but #369 changes the pre-authoring selection mechanism and requires fresh independent review before corpus work. |
| Portable deployment / continuity | Durable handoff mechanisms are shipped; #368 proposes legacy receipt corrections but is not canonical until merged. |

## Operator decisions / blockers

- **#368:** explicit operator merge authority is required for the exact reviewed PR identity. If granted, the merge must use `scripts/opcmd_merge.py`; a bare GitHub/`gh pr merge` is not the repository-authorized route.
- **#369/#341:** fresh independent review must accept the revised pre-authoring package before selection/corpus work proceeds. Benchmark model/evaluator/API execution and spending remain separate later gates.
- **#367:** reports standing merge authorization active, but the mandatory merge helper and all review/CI/live-stop gates still apply.

## Likely next sequence

1. Preserve #367's reviewed identity and process it only through the required merge route if its authorization remains valid.
2. Decide #368's explicit merge authority; if granted, merge only through `scripts/opcmd_merge.py`.
3. Perform a fresh independent review of #369 before any benchmark selection or corpus work.
4. Review #370 as orientation-only documentation, ensuring it routes to canonical owners rather than becoming a second contract.
5. Safely migrate issue #331 into `work/coordination/FRICTION_LOG.md`, then re-derive the next MAPS_L-owned capability priority from merged `main`.

## Development surfaces

- [Live Roadmap — Overview](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1154882262)
- [Live Roadmap — Development](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1160745974)
- [Live Roadmap — Active Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1476804517)
- [Live Roadmap — Capability Map](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=360062140)
- [Live Roadmap — Agent Action Pack](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=189197466)
- [Live Roadmap — Daily Log](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=374922834)
- [Canonical capability checklist](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
- [Agent-harness capability roadmaps](https://github.com/BigCatMellow/MAPS_Lean/tree/main/work/roadmaps/agent-harness-capabilities)
