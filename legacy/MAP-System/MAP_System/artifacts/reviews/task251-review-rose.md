# Review: TASK-251 Create a collaborative MAP improvement kickoff and execution roadmap

task_id: TASK-251
reviewer: claude-lab-rose
task_owner: codex-lab-kiri

## Verdict

APPROVED

A genuinely candid planning document, not a self-congratulatory status
report: its central conclusion is that MAP has more process evidence than
outcome evidence, and it structures an entire program around proving that
gap rather than adding more machinery. It explicitly disclaims authorizing
anything (§1) and defers every consequential choice to the operator (§12).
The one numeric claim I could cross-check against a live tool (change-request
rate) matched closely, which is a good proxy for the rest of the evidence
baseline's reliability.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| Plan integrates current runtime evidence and independent Codex/Claude perspectives into a candid state assessment. | PASS | §3 evidence baseline (task counts, review queue, graph validator, agent liveness) is specific and falsifiable, not vague. §13 describes Codex and Claude assessing independently before reconciling, then a Claude "contradiction pass" that produced two concrete corrections (no-MAP counterfactual; TASK-241–248 ownership repair before claiming green) — this is evidence of genuine friction, not rubber-stamped agreement. §3.2 names real strain (stale reviewer sessions, a policy-gate false positive, stale shared-file metadata) rather than only listing strengths. |
| Plan defines measurable goals, phased workstreams, dependencies, decision gates, risks, and explicit non-goals. | PASS | §5 (G1/G2/G3 with concrete success measures), §7 (5 phases with exit criteria, stop rules, and time-boxes), §10 (9 named risks with early-warning signals and countermeasures), §11 (9 explicit non-goals, including "do not widen Pi's authority" — consistent with the standing Pi pause I flagged in TASK-261). |
| Each workstream has a bounded accountable role, supporting roles, operator decision points, and durable outputs. | PASS | §8 role table has Accountable-for / Must-not-do columns per role (not just names). §9 work-package table has Owner / Reviewer / Durable output / Admission gate for all 6 packages. §12 lists 4 explicit operator decisions with issue/options/recommendation/needed structure. |
| Immediate cleanup, controlled practice experiments, and longer-term improvements are clearly separated so planning does not silently authorize implementation. | PASS | Phase 1 (stabilization, hard-capped at two sessions) is explicitly separated from Phase 2/3 (prove-it project) and from long-term architecture (§11 non-goals block permanent autonomous processes and new agent roles). §1: "This document is a proposed execution roadmap. It does not silently authorize new agents, new autonomous authority, deployment, policy changes, or a new database." §599 header: "status: PROPOSED — operator ratification required." |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Silently authorizing new agents, autonomous authority, deployment, policy changes, or a new database | NOT BROKEN — self-disclaimed in §1 and reinforced by §11's explicit non-goals list; every consequential decision is routed to §12 as an operator decision, not asserted as already-decided. |

## Files Reviewed

- `MAP_System/artifacts/planning/map-project-improvement-kickoff-2026-07-19.md` (full, 619 lines)
- Cross-checked referenced prior plans exist: `notes/system-improvement-kickoff.md`, `notes/system-improvement-implementation-plan.md`, `artifacts/reports/system-improvement-iteration-2026-07-18.md`, `notes/practice-scenario-runbook.md`, `artifacts/planning/map-practice-scenario-queue-2026-07-18.md`, `notes/map-system-deep-dive.md` — all present.

## Verification

- `MAP_System/scripts/map_metrics.py` (current, 2026-07-21) reports change-request rate 19.59% versus the report's "about 20%" claim from 2026-07-19 — close match on a ratio metric that's relatively insensitive to task-count growth, a reasonable proxy that the evidence baseline was gathered honestly rather than invented. (Raw counts like RELEASED 136 vs. reported 134, APPROVED 69 vs. reported 62 show plausible growth over the two days between report and this review, consistent rather than contradictory.)
- The TASK-241–248 output-path collision cited in §3.2/Phase 1 independently corroborates the same issue flagged in `task250-review-lure.md` (already-approved, cross-checked in the TASK-250 review above) — consistent fact reported across two independently-authored documents from the same period.
- No file references in §14 are broken.

## Notes

This is a planning artifact, not code — the review focus is honesty of the
assessment and absence of smuggled authority, both of which check out. One
observation worth carrying forward rather than blocking on: §11 explicitly
lists "widen Pi's authority" as a non-goal, and §8's role table says Pi
sessions get "none on critical path... Optional future requalification only
under a separately authorized, visible, no-write experiment" — this is the
same standing boundary TASK-261 (reviewed above) appears to have run past
without a durable authorization record. Worth the operator having both in
view together when resolving TASK-261.
