# Development

> **Live status snapshot, not authority.** GitHub `main` and
> [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
> remain canonical. Open PRs and proposals do not change shipped behavior or the canonical capability scoreboard.

**Last refreshed:** 2026-09-10 14:12 ET  
**Canonical code/status basis:** `7dfcbd0` *(latest `main` before this snapshot-only Wiki-source commit; this page refresh itself advances `main` without changing capability behavior)*  
**Capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Deeper working view: [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).

## Current focus

The project has moved from the September 9 exposure/review backlog into an operator-approved reviewed-gap sequence, while one older roadmap proof remains conspicuously unfinished:

1. land the bounded recovery-safety fix in **PR #335** after review/merge authority;
2. keep reviewer-execution lineage honest: **#336/#337** conclude that implementation is blocked until MAPS has a trusted execution-observation producer;
3. land the task-history retention contract/guards in dependency order **#338 → #339** if review remains green;
4. repair the red handoff-lifecycle branch **#340**;
5. independently re-review the corrected protocol-effectiveness benchmark **#341** before any corpus construction;
6. do not lose the roadmap's **6.22 `BEFORE_SEND` / memory-provenance first-exposure** watch while the reliability/evaluation queue grows.

## Active / proposed work

| State | Work | Current verified read | Source |
| --- | --- | --- | --- |
| **IN REVIEW** | Recovery ambiguity safety | #335 suppresses same-tick direct fallback after a failed bound harness resume with `RetryDisposition.UNKNOWN`, preserves ambiguity metadata, and re-observes session truth on the next tick. Runtime and review-evidence are green. | [#335](https://github.com/BigCatMellow/MAPS_Lean/pull/335) |
| **BLOCKED** | Trusted reviewer execution lineage | #336 designs the missing reviewer-execution provenance relation. #337 finds no trustworthy current producer that independently proves actual machine/process review execution → logical reviewer principal. Do not replace the missing proof with reviewer-supplied provider/model/session labels. | [#336](https://github.com/BigCatMellow/MAPS_Lean/pull/336) · [#337](https://github.com/BigCatMellow/MAPS_Lean/pull/337) |
| **IN REVIEW** | Canonical task/history retention | #338 defines the smallest retention contract; stacked #339 adds DB guards rejecting task-event update/delete and canonical task hard-delete. Both current heads are runtime/review green; #338 must integrate before or with #339. | [#338](https://github.com/BigCatMellow/MAPS_Lean/pull/338) · [#339](https://github.com/BigCatMellow/MAPS_Lean/pull/339) |
| **BLOCKED** | Durable handoff acknowledgment | #340 proposes a durable handoff lifecycle/register without mirroring live GitHub status. Its current head fails both Runtime stack tests and review-evidence, so it is not merge-ready. | [#340](https://github.com/BigCatMellow/MAPS_Lean/pull/340) |
| **IN REVIEW** | Protocol-effectiveness benchmark | #341 asks whether MAPS_L improves objectively correct autonomous completion enough to justify its overhead. The first validity review required major corrections; the corrected head is runtime-green but still review-evidence-red. No corpus, model scoring, API spend, or effectiveness claim is authorized. | [#341](https://github.com/BigCatMellow/MAPS_Lean/pull/341) |
| **NEXT / WATCH** | 6.22 — real `BEFORE_SEND` / memory-provenance exposure | The production `maps run send-context --deliver-context` path is shipped, but trajectory check #27 still found no real first-exposure evidence. It becomes a named finding if another trajectory arc passes without the exercise. | [#310](https://github.com/BigCatMellow/MAPS_Lean/pull/310) · [#332](https://github.com/BigCatMellow/MAPS_Lean/pull/332) |
| **IN PROGRESS / EVIDENCE-GATED** | E5 recovery compatibility | Stage-0 design is merged (#325), but enforcement remains blocked on the earlier operator decision. The legitimate next step is advisory operational evidence, not Stage-3 implementation. | [#325](https://github.com/BigCatMellow/MAPS_Lean/pull/325) |

## Operator decisions / blockers

- **Merge authority remains separate from CI readiness.** Every merge to `main` still requires the repository's mandatory `scripts/opcmd_merge.py` path and operator-authored authorization.
- **Reviewer-execution lineage is blocked on evidence, not schema design.** If the next trusted-producer path requires a new account/App, provider access, credentials, or spending, that branch needs explicit operator authority; until then, #337's `BLOCKED_ON_TRUSTED_PRODUCER` is the honest state.
- **E5 enforcement remains intentionally withheld.** The next useful evidence is advisory production exposure; do not turn #325's design note into implementation authority.
- **Protocol benchmark execution is not authorized.** #341 needs a fresh independent verdict of `APPROVED FOR CORPUS CONSTRUCTION` before corpus work, and later model/API execution or spending requires its own authority.
- **Issue #331 remains open.** Its two tool-friction records still need a safe terminal/local append into `work/coordination/FRICTION_LOG.md`; do not reconstruct the large canonical log from truncated connector output. [#331](https://github.com/BigCatMellow/MAPS_Lean/issues/331)

Resolved since the prior snapshot:

- **Emergence supersession authority — RESOLVED/SHIPPED.** #319 is merged. Emergence may challenge/redesign/propose replacement of established mechanisms, while implementation/merge authority remains separate.
- **Recurring trajectory insights — RESOLVED as KEEP.** #333 records operator KEEP dispositions for `INSIGHT-45727354` and `INSIGHT-68a53a28`; they remain live observations without automatic task promotion.
- **Stalled-worker repair record — CLOSED.** #334 adds a real regression/countermeasure pointer after operator confirmation. The broader `triage_status.py` substring-scan weakness remains a separate known issue.

## Meaningful recently shipped changes

- **6.4 destructive-action first exposure — SHIPPED, row still IN PROGRESS.** #320 proved real `BEFORE_DESTRUCTIVE_ACTION` DENY/ALLOW behavior; other 6.4 controls remain open.
- **H4 enforced-validation first exposure — SHIPPED, row still IN PROGRESS.** #324 proved real quick-tier enforcement can block resume without consuming attempt budget; normal/full tiers and per-spec enforcement remain open.
- **Emergence may challenge established mechanisms — SHIPPED.** #319 expanded proposal space without granting self-authorization.
- **Roadmap reconciliation / borrow-before-build evidence — SHIPPED.** #322/#323 route external evidence into existing MAPS owners without changing capability status.
- **Reliability hardening — SHIPPED.** #326 added stale-owner/symlink regressions; #328 now rejects reachable dependency cycles as malformed shaping state; #330 proves task state and semantic event rollback together in one SQLite transaction.
- **Recovery ambiguity characterized — SHIPPED as evidence.** #327 froze the same-tick UNKNOWN-fallback seam that #335 now addresses.
- **Cost/resource admission gap documented — SHIPPED as research.** #329 distinguishes current retrospective run budgets from a future atomic pre-launch reservation invariant; no monetary-budget mechanism was silently claimed.
- **Trajectory check #27 — SHIPPED.** #332 re-derived **19 / 10 / 6**, action **CONTINUE**, and placed 6.22 on explicit watch.
- **Operator insight dispositions and stalled-worker closure — SHIPPED.** #333/#334 remove recurring false/undisposed status noise without capability flips.

## Capability-area snapshot

| Area | Current read | Development direction |
| --- | --- | --- |
| **Harness Mechanics** | Advanced / active | Core resume/stop/send machinery exists. #335 tightens ambiguous-resume safety. H4 remains IN PROGRESS; 6.22 still needs a real send exposure. |
| **Procedural Knowledge & Skills** | Advanced | S1–S6 remain DONE; semantic/retrieval expansion stays evidence-gated. |
| **Environment & Reproducibility** | Mixed / active | 6.16 is DONE; H4 has first-exposure evidence but residual tiers remain; E5 is advisory/evidence-gated. |
| **Agentic Security** | Advanced / active | Real resume and destructive-action evidence exist; 6.4 remains open for other stated controls and 6.22 lacks real send/provenance exposure. |
| **Learning & Evaluation** | Active / maturing | Emergence/cross-root synthesis operate; #341 is building a falsifiable protocol-effectiveness test but is not yet approved for corpus construction. |
| **Portable Deployment** | Mixed / active | Canonical-run/worktree infrastructure is strong; external pilot and durable project-memory work remain incomplete/deferred. #340 addresses handoff continuity but is currently CI-red. |

## Likely next sequence

1. Integrate **#335** if the current reviewed head remains valid and operator-authorized.
2. Treat **#337** as a real stop condition: either identify/authorize a trusted reviewer-execution producer or keep lineage implementation blocked; do not add self-attested fields.
3. Integrate **#338 → #339** in order if their reviews remain valid.
4. Repair **#340**'s actual test/review failures before reconsidering its handoff-lifecycle change.
5. Obtain a fresh independent experimental-validity review for **#341**; do not construct the corpus until it earns `APPROVED FOR CORPUS CONSTRUCTION`.
6. Run the still-missing **6.22** real `BEFORE_SEND` / memory-provenance exposure before it becomes recurring roadmap debt.
7. Re-derive capability status from merged evidence before starting another broad capability arc.

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

> **Evidence can narrow a capability gap without closing the whole capability, and green CI can coexist with a substantive BLOCKED state.**

This page separates **SHIPPED/current behavior** from **IN REVIEW/PROPOSED/BLOCKED work**. Open work never changes the canonical scoreboard by itself.
