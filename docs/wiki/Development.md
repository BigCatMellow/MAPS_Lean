# Development

> **Live status snapshot, not authority.** GitHub `main` and [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md) remain canonical. Open PRs and proposals do not change shipped behavior or the capability scoreboard.

**Last refreshed:** 2026-09-15 2:13 PM ET  
**Canonical main at reconciliation:** `9968262`  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

The last 24 hours materially advanced **6.4 write-scope enforcement** without changing its canonical status. PR #361 verified run write scope against real Git changes; #362 added an explicit `require_write_scope_binding` opt-in; #365 wired that opt-in into `CanonicalRunGuard`. The guard can now return `RUN_WRITE_SCOPE_VIOLATION` or `RUN_WRITE_SCOPE_UNAVAILABLE`, but no production caller currently enables the opt-in, so existing live behavior remains unchanged.

A separate governance finding is now critical: PR #364 found that `scripts/opcmd_merge.py` contains the required review-evidence gates but has never completed a real repository merge; recent merges including #359–#362 used another merge path. This is a mechanism-versus-convention gap, not a capability-score change.

PR #341 remains the only open PR. Its protocol-effectiveness design is approved for corpus construction but remains blocked on genuinely independent custody of hidden corpus material.

## Active / next

| State | Work | Verified read | Source |
| --- | --- | --- | --- |
| **NEXT** | 6.4 production write-scope exposure | Verification, opt-in and guard wiring are merged; no legitimate production caller requests write-scope enforcement yet. | [#361](https://github.com/BigCatMellow/MAPS_Lean/pull/361) · [#362](https://github.com/BigCatMellow/MAPS_Lean/pull/362) · [#365](https://github.com/BigCatMellow/MAPS_Lean/pull/365) |
| **DECISION NEEDED** | Merge-process integrity | Required helper gates exist, but #364 found no real merges recorded through the helper. A bounded mechanical safeguard is needed rather than relying only on convention. | [#364](https://github.com/BigCatMellow/MAPS_Lean/pull/364) |
| **BLOCKED** | #341 benchmark custody | Design approved; owner-safe pre-authoring complete; same-owner context is not eligible to hold hidden case identities/secrets. | [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341) |
| **NEXT** | Issue #331 friction capture | Temporary issue still needs its records safely moved into the canonical friction log. | [#331](https://github.com/BigCatMellow/MAPS_Lean/issues/331) |

## Meaningful recently shipped changes

- **#359:** pre-dispatch roadmap-row freshness check to catch already-merged/already-scoped work before dispatch.
- **#361/#362/#365:** real Git write-scope verification, explicit enforcement opt-in, and CanonicalRunGuard wiring for 6.4.
- **#363:** trajectory check #31 independently re-derived the canonical scoreboard as **19/10/6 unchanged**.
- **#364:** merge-path audit exposed that the required merge-evidence helper is not actually being used for real merges.

## Capability-area snapshot

| Area | Current read |
| --- | --- |
| Harness / security | Advanced and active. 6.4 write-scope enforcement is implemented behind an unused opt-in; real production exposure remains. |
| Skills / context | Advanced; no scoreboard change today. |
| Environment / reproducibility | Mixed; existing H4/E5 residuals remain. |
| Learning / evaluation | #341 design approved, blocked on independent corpus custody. |
| Portable deployment | Planning-only roadmap remains non-authoritative for implementation. |

## Likely next sequence

1. Identify the smallest legitimate production flow that should opt into 6.4 write-scope enforcement; correct the stale CLI help noted by #365 review; then obtain real production ALLOW/DENY evidence before any status change.
2. Resolve #364 with the smallest reviewed mechanical safeguard that makes incorrect merge-path use visible or enforceable without weakening existing gates.
3. Preserve #341's custody boundary; do not select cases or run benchmark models from the owner context.
4. Safely migrate issue #331 into the canonical friction log.

## Development surfaces

- [Live Roadmap — Overview](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1154882262)
- [Live Roadmap — Development](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1160745974)
- [Live Roadmap — Active Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=1476804517)
- [Live Roadmap — Capability Map](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=360062140)
- [Live Roadmap — Agent Action Pack](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=189197466)
- [Live Roadmap — Daily Log](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit#gid=374922834)
- [Canonical capability checklist](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
- [Agent-harness capability roadmaps](https://github.com/BigCatMellow/MAPS_Lean/tree/main/work/roadmaps/agent-harness-capabilities)
