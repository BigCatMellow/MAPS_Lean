# Development

> **Live status snapshot, not authority.** GitHub `main` and [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md) remain canonical. Open PRs, proposals, and merges into non-`main` benchmark branches do not change shipped behavior or the capability scoreboard.

**Last refreshed:** 2026-09-19 2:47 PM ET  
**Canonical main at reconciliation:** `30772be`  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

No commit landed on `main` in the preceding 24 hours. The latest canonical commit at reconciliation remained the 2026-09-18 Development snapshot (`30772be`), so capability status remains 19/10/6.

The active queue remains #341, #367, #370, and #371. The important live-state correction is #367: its head is still `c520155` and both Runtime and review-evidence checks pass, but GitHub now reports the PR non-mergeable. Its PR-body identity text also names older heads. Do not force or bypass this state; diagnose the exact mergeability/review-binding condition before any OPCMD merge.

PR #370 and benchmark-branch PR #371 still have green Runtime tests but failing review-evidence checks because genuine independent review is missing. PR #341 remains open and non-mergeable; its body remains partly stale because it describes the older private-secret selection scheme superseded by #369 on the benchmark branch.

## Active / next

| State | Work | Verified live read | Next gate |
| --- | --- | --- | --- |
| **BLOCKED** | [#367 protocol discoverability / AGENTS contract](https://github.com/BigCatMellow/MAPS_Lean/pull/367) | Head `c520155`; Runtime + review-evidence green; GitHub `mergeable=false`; PR-body head text is stale. | Diagnose mergeability and exact reviewed equivalence; use OPCMD only if all live gates validate. |
| **IN REVIEW** | [#370 Wiki methods/protocols orientation](https://github.com/BigCatMellow/MAPS_Lean/pull/370) | Head `85e85e1`; Runtime green; review-evidence failed; GitHub `mergeable=false`. | Fresh independent documentation review; preserve non-authoritative orientation. |
| **IN REVIEW** | [#371 Arm C solo-owner approval design](https://github.com/BigCatMellow/MAPS_Lean/pull/371) | Benchmark head `e46fd8f`; Runtime green; review-evidence failed; GitHub `mergeable=true`. | Fresh independent methodological review; do not relabel inspectable self-critique as true independence. |
| **BLOCKED** | [#341 protocol-effectiveness benchmark](https://github.com/BigCatMellow/MAPS_Lean/pull/341) | Open; `mergeable=false`; branch contains #369's selection rewrite while PR body still describes the superseded private-secret selection scheme. | After #371 review, recover branch files and enumerate the actual remaining pre-corpus gates. |
| **NEXT** | [#331 friction capture](https://github.com/BigCatMellow/MAPS_Lean/issues/331) | Still open; two tool-friction records remain temporary. | Safely append them to `work/coordination/FRICTION_LOG.md` from a terminal-capable lane and close with evidence. |

## Meaningful recently shipped changes

- **#368:** legacy handoff lifecycle reconciliation is canonical on `main` at `0010397`.
- **#369:** public beacon-anchored deterministic selection is merged into the benchmark branch only, not `main`.
- **#361/#362/#365:** 6.4 Git write-scope verification/opt-in/guard foundation remains shipped; the canonical scoreboard did not change.

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
- **#367:** standing authorization does not permit conflict-forcing or a bare GitHub/`gh pr merge`; diagnose the live non-mergeable state and preserve exact review/CI/live-stop gates before OPCMD.
- **#370/#371:** review-evidence failures remain substantive process blockers until genuine independent review exists.

## Likely next sequence

1. Fresh independently review #370 and #371 at their exact live heads.
2. Diagnose #367's live non-mergeable state and recover exact review binding without widening scope; use OPCMD only if merge-valid.
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
