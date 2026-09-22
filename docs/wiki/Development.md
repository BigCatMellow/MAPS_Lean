# Development

> **Live status snapshot, not authority.** GitHub `main` and [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md) remain canonical. Open PRs, proposals, and merges into non-`main` benchmark branches do not change shipped behavior or the capability scoreboard.

**Last refreshed:** 2026-09-22 2:34 PM ET  
**Canonical main at reconciliation:** `f15c71c`  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

No commit landed on `main` in the preceding 24 hours. The latest canonical commit at reconciliation remained the 2026-09-21 Development status refresh (`f15c71c`), so capability status remains 19/10/6.

The active queue remains #341, #367, #370, and #371. The important live correction is #367: GitHub now reports it mergeable again at live head `3f3ec42`, but its PR body still names reviewed substantive head `0d53e88` and then-current head `d4df341`. Mergeability is not proof that the old high-risk review covers the live head; exact review binding/equivalence must be reconciled before any OPCMD merge.

PR #370 and benchmark-branch PR #371 still require genuine independent review. PR #341 remains open/non-mergeable and its body remains partly stale because it describes the older private-secret selection scheme superseded by #369 on the benchmark branch.

## Active / next

| State | Work | Verified live read | Next gate |
| --- | --- | --- | --- |
| **IN REVIEW** | [#367 protocol discoverability / AGENTS contract](https://github.com/BigCatMellow/MAPS_Lean/pull/367) | Live head `3f3ec42`; GitHub `mergeable=true`; PR-body reviewed/current identities are stale. | Recover exact commit/review equivalence and live checks; use OPCMD only if all gates validate. |
| **IN REVIEW** | [#370 Wiki methods/protocols orientation](https://github.com/BigCatMellow/MAPS_Lean/pull/370) | Head `85e85e1`; GitHub `mergeable=true`; PR itself records missing genuine independent review evidence. | Fresh independent documentation review; preserve non-authoritative orientation. |
| **IN REVIEW** | [#371 Arm C solo-owner approval design](https://github.com/BigCatMellow/MAPS_Lean/pull/371) | Benchmark head `e46fd8f`; GitHub `mergeable=true`; independent methodological review remains required. | Fresh independent methodological review; do not relabel inspectable self-critique as true independence. |
| **BLOCKED** | [#341 protocol-effectiveness benchmark](https://github.com/BigCatMellow/MAPS_Lean/pull/341) | Open/non-mergeable at `19d3d36`; branch contains #369's selection rewrite while PR body still describes the superseded private-secret selection scheme. | After #371 review, recover branch files and enumerate the actual remaining pre-corpus gates. |
| **NEXT** | [#331 friction capture](https://github.com/BigCatMellow/MAPS_Lean/issues/331) | Two temporary friction records remain to be migrated. | Safely append them to `work/coordination/FRICTION_LOG.md` from a terminal-capable lane and close with evidence. |

## Meaningful recently shipped changes

- **#368:** legacy handoff lifecycle reconciliation is canonical on `main` at `0010397`.
- **#369:** public beacon-anchored deterministic selection is merged into the benchmark branch only, not `main`.
- **#361/#362/#365:** 6.4 Git write-scope verification/opt-in/guard foundation remains shipped; the canonical scoreboard did not change.
- **Daily Development publication:** status-only refreshes after those changes do not alter capability state.

## Capability-area snapshot

| Area | Current read |
| --- | --- |
| Harness / security | Advanced. 6.4 write-scope foundation is shipped; exact remaining closure/exposure should be read from the canonical checklist before new work. |
| Skills / context | Advanced. #367 proposes repository-wide operating-contract/discoverability changes but is not canonical while open. |
| Environment / reproducibility | Mixed; H4 normal/full/per-spec and E5 evidence-gated residuals remain. |
| Learning / evaluation | Active. #369 changed benchmark-branch selection; #371 isolates Arm C content-quality independence. No benchmark execution is authorized. |
| Portable deployment / continuity | Durable handoff lifecycle and #368 legacy reconciliation are canonical. |

## Operator decisions / blockers

- No new immediate operator decision is required by today's live state.
- **Benchmark execution:** model/evaluator/API execution and spending remain a later operator gate; nothing in #341/#369/#371 authorizes execution.
- **#367:** standing authorization does not permit treating `mergeable=true` as review validity or using a bare GitHub/`gh pr merge`; recover exact live review binding and preserve review/CI/live-stop gates before OPCMD.
- **#370/#371:** genuine independent review remains a substantive blocker.

## Likely next sequence

1. Reconcile #367's live head `3f3ec42` against its existing high-risk review evidence; obtain refreshed independent review if equivalence cannot be proven.
2. Fresh independently review #370 and #371 at their exact live substantive heads.
3. Reconcile #341 from actual benchmark-branch files after the #371 disposition; do not trust stale PR-body prose as the gate list.
4. Safely migrate issue #331 into the canonical friction log.
5. Re-derive the next MAPS_L-owned capability priority from merged `main` and the canonical checklist.

## Development surfaces

- [Live Roadmap — Overview](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1154882262)
- [Live Roadmap — Development](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1160745974)
- [Live Roadmap — Active Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1476804517)
- [Live Roadmap — Capability Map](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=360062140)
- [Live Roadmap — Agent Action Pack](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=189197466)
- [Live Roadmap — Daily Log](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=374922834)
- [Canonical capability checklist](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
- [Agent-harness capability roadmaps](https://github.com/BigCatMellow/MAPS_Lean/tree/main/work/roadmaps/agent-harness-capabilities)
