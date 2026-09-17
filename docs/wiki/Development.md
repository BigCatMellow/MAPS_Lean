# Development

> **Live status snapshot, not authority.** GitHub `main` and [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md) remain canonical. Open PRs, proposals, and merges into non-`main` benchmark branches do not change shipped behavior or the capability scoreboard.

**Last refreshed:** 2026-09-17 2:43 PM ET  
**Canonical main at reconciliation:** `0010397`  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

PR #368 is now **shipped on `main`**. It reconciled legacy handoff lifecycle receipts/register state and merged as `0010397`; the post-merge Runtime test and direct-push safeguard both passed.

The active queue is now #341, #367, #370, and #371. PR #367 remains a high-risk `AGENTS.md` / protocol-discoverability proposal and is not current contract behavior while open. PR #370 is documentation-only Wiki orientation awaiting genuine independent review. New PR #371 isolates a remaining protocol-effectiveness-benchmark problem: the public-beacon solution for selection unpredictability does not itself provide an independent competence/non-strawman judgment of Arm C's text.

PR #369 is no longer an open review item: it merged into `eval/protocol-effectiveness-benchmark-v0`, **not `main`**. Its public deterministic NIST-beacon selection method is therefore benchmark-branch state, not canonical MAPS_L behavior. Hidden case construction/material handling remain separate, and #371 addresses the still-open Arm C approval-independence question.

## Active / next

| State | Work | Verified read | Source |
| --- | --- | --- | --- |
| **SHIPPED** | #368 handoff reconciliation | Merged to `main` as `0010397`; Runtime test and direct-push safeguard passed. | [#368](https://github.com/BigCatMellow/MAPS_Lean/pull/368) |
| **IN REVIEW** | #371 Arm C solo-owner approval design | Design-only note distinguishes selection unpredictability from content-quality independence; proposes an inspectable self-critique fallback while explicitly admitting it is not true independence. | [#371](https://github.com/BigCatMellow/MAPS_Lean/pull/371) |
| **IN REVIEW** | #367 protocol discoverability / AGENTS contract | High-risk authority-surface proposal remains open; prior review state must be revalidated against current `main` after #368. | [#367](https://github.com/BigCatMellow/MAPS_Lean/pull/367) |
| **PROPOSED** | #370 Wiki methods/protocols orientation | Documentation-only orientation; author reports Runtime pass and review-evidence pending a genuine fresh independent review. | [#370](https://github.com/BigCatMellow/MAPS_Lean/pull/370) |
| **BLOCKED** | #341 protocol-effectiveness benchmark | Benchmark PR remains open. #369 changed its benchmark branch selection mechanism; #371 addresses a separate remaining Arm C approval gate. No benchmark execution has occurred. | [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341) |
| **NEXT** | Issue #331 friction capture | Two tool-friction records still need safe migration into the canonical friction log. | [#331](https://github.com/BigCatMellow/MAPS_Lean/issues/331) |

## Meaningful recently shipped changes

- **#368:** legacy handoff lifecycle reconciliation is now canonical on `main`.
- **#369:** public beacon-anchored deterministic selection is merged into the benchmark branch only. It removes the private selection secret for Gates 0–3 but does not solve hidden case construction or Arm C content-quality independence.
- The earlier 6.4 write-scope foundation (#361/#362/#365) remains shipped behind an unused production opt-in; it did not change the 19/10/6 score.

## Capability-area snapshot

| Area | Current read |
| --- | --- |
| Harness / security | Advanced and active. 6.4 write-scope foundation is shipped; residual production opt-in/exposure and exact checklist closure remain. |
| Skills / context | Advanced. #367 proposes discoverability/contract changes but is not canonical while open. |
| Environment / reproducibility | Mixed; H4 normal/full/per-spec and E5 evidence-gated residuals remain. |
| Learning / evaluation | Benchmark design is active. Gate 2 selection rewrite is benchmark-branch state; #371 exposes a distinct Arm C content-quality independence gate. No benchmark execution is authorized. |
| Portable deployment / continuity | Durable handoff lifecycle plus #368 legacy reconciliation are now canonical. |

## Operator decisions / blockers

- No new immediate operator decision is required by today's live state.
- **Benchmark execution:** model/evaluator/API execution and spending remain a separate later operator gate; nothing in #341/#369/#371 authorizes it.
- **#367:** any eventual merge must preserve the exact independent-review/CI/live-stop gates and use the repository's mandatory `scripts/opcmd_merge.py` route. Its open changes are not current authority.
- **#371:** an inspectable solo-owner self-critique must not be mislabeled as true independence; fresh independent review is the next gate.

## Likely next sequence

1. Fresh independently review #371's Arm C design and #370's Wiki orientation.
2. Revalidate #367's exact reviewed identity against current `main`; use only the mandatory OPCMD merge route if still authorized.
3. Recover #341's exact benchmark-branch state after #369 and the #371 review, then enumerate the remaining pre-corpus gates.
4. Safely migrate issue #331 into `work/coordination/FRICTION_LOG.md`.
5. Re-derive the next MAPS_L-owned capability priority from merged `main` rather than from stale handoffs.

## Development surfaces

- [Live Roadmap — Overview](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1154882262)
- [Live Roadmap — Development](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1160745974)
- [Live Roadmap — Active Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1476804517)
- [Live Roadmap — Capability Map](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=360062140)
- [Live Roadmap — Agent Action Pack](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=189197466)
- [Live Roadmap — Daily Log](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=374922834)
- [Canonical capability checklist](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
- [Agent-harness capability roadmaps](https://github.com/BigCatMellow/MAPS_Lean/tree/main/work/roadmaps/agent-harness-capabilities)
