# Review: TASK-255 Map conversation notes into existing E/I and triage architecture

task_id: TASK-255
reviewer: claude-lab-rose
task_owner: codex-lab-kiri

## Verdict

APPROVED

A disciplined intake that resists the two easiest failure modes for this
kind of task: treating an operator's design conversation as either
authorization to build a new parallel system, or as unverified external
claims to accept at face value. It maps every proposal against MAP's actual
current mechanisms (§3), names real gaps precisely (§4), and its Experiment
1 (§13) is — verifiably, in hindsight — exactly what became the TASK-256
retrieval-experiment chain I reviewed and approved earlier in this pass, run
faithfully to the success thresholds this document set.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| Maps each major proposal to an existing MAP mechanism, a genuine gap, or a deferred idea without creating a duplicate source of truth. | PASS | §3's table maps 11 proposal ideas to specific existing MAP substrate (`map.db`, `shared/current-state.md`, `emergence/`, `operational-lessons.json`, RnS/limit watcher, `event_trace.py`, etc.) with a one-line assessment each. §4 names 5 specific gaps (no task fingerprint, no workstream digest, no retrieval token contract, waits not uniformly explainable, incidents don't consistently feed E/I) rather than a vague "needs more memory." §5 explicitly argues against merging navigation and retrieval into one index — an anti-duplication design call. |
| Separates adopt-now principles, extensions to existing systems, bounded experiments, and deferred or rejected architecture. | PASS | §12's table has exactly these categories as rows: "Adopt as a design principle now" / "Extend existing systems" / "Experiment before adoption" / "Defer" / "Separate operator decision later" (GitHub). Each row lists specific items, not generalities. |
| Defines measurable experiments for task fingerprints, workstream digests, E/I recall, and explainable waits/incidents while preserving proposal-only authority. | PASS | §13 Experiments 1–4 map 1:1 to these four areas, each with corpus size, frozen truth-set requirement, and numeric success thresholds (e.g. Experiment 1: "recall@6 at least 80%... zero critical known-evidence misses... fresh reviewer judges at least 70% of shown candidates useful"). §17/status line and §15 repeatedly state "no implementation authority" / architecture intake only. |
| GitHub and external references are treated as optional unverified inputs and no external write or integration is authorized. | PASS | §2: "It does **not** independently validate the external references, quotations, or product claims... not treated here as verified evidence or as authorization to adopt an external tool. No GitHub repository, issue, project, webhook, or external service was changed." §12's dedicated "Separate operator decision later" row defers all GitHub mirroring/webhooks explicitly to a future operator decision. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Creating a new agent, helper, background process, database table, policy, or task-state authority | NOT BROKEN — §2 explicit disclaimer; this is a single planning artifact with no code/schema changes. |
| Treating external/GitHub references as verified or authorizing external writes | NOT BROKEN — see AC4 above. |

## Files Reviewed

- `MAP_System/artifacts/planning/conversation-notes-ei-triage-intake-2026-07-19.md` (full, 492 lines)
- Verified existence of the operator source (`/home/mellow/Projects/MultiAgentProject/conversation_notes.md`) and all 14 files cited in §16 "Sources inspected."

## Verification

- All 14 cited source files plus the operator's `conversation_notes.md` exist at their referenced paths — no fabricated or broken citations.
- Retrospective cross-check: this document's §13 "Experiment 1 — frozen task-fingerprint retrieval" specifies a frozen truth set, ≤6 candidates, ≤1,200-token discovery ceiling, recall@6 ≥80%, zero critical misses, and a fresh reviewer judging candidate usefulness — this is, point for point, the design that TASK-256 (reviewed earlier in this session, `task256-review-rose.md`) actually implemented and measured (TASK-256 achieved 100% recall@6, 0 critical misses, all sources resolvable, packets under the token ceiling, and used a fresh helper for the usefulness judgment). This is strong evidence the document's proposals were substantive and actually followed through on, not planning theater.
- §15's ownership boundaries (TASK-227 owns navigation reconciliation, TASK-236 owns advisory-monitor rework) are consistent with references to those same open items in TASK-251's kickoff plan (reviewed earlier in this session), which independently corroborates their status as real, still-open work rather than an invented dependency.

## Notes

No findings. This is the traceable origin document for the TASK-256→262
retrieval-experiment chain reviewed earlier in this session — worth noting
for anyone reading the chain later that its lineage back to an explicit,
bounded, operator-sourced planning intake is intact and verifiable.
