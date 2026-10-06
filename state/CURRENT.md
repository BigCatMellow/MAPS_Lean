# Current State

**Last reconciled: 2026-10-06.** This is a compact cross-session orientation
snapshot, not a live status board. Before acting on PR/CI/review/ownership state,
recover live GitHub state through
[`work/coordination/README.md`](../work/coordination/README.md).

## Parent objective

MAPS_L is a provider-neutral operating system around capable AI workers. It owns
task truth, bounded authority, orchestration, reusable methods, verification,
recovery, durable evidence, and controlled learning; workers supply reasoning,
judgment, exploration, coding, and synthesis.

## Current baseline

- `main`: `08cd0e81576779c5b06371c58fcbfe3b22352c05` (2026-09-23 status refresh).
- The replacement-runtime migration is complete and active runtime code is
  independent of top-level `legacy/`.
- **Operator decision 2026-10-06:** retain `legacy/` as an intentional reference
  corpus. Deletion is no longer a pending migration action.
- A separate safety fork exists at
  `BigCatMellow-Archive/MAPSL_Backup`; it does not become an authority source.

## Active development arcs

These are dated orientation facts; verify them live before acting.

1. **PR #372 — DecisionBroker / Jev evaluation seam.** Latest substantive
   development lane. Runtime-stack CI passed at its recorded head; the PR is
   still draft because independent review evidence has not been satisfied.
2. **PR #367 — protocol discoverability.** Intended to reduce operating-method
   retrieval cost. It previously reached independent approval, but should be
   reconciled against current `main` and later work before merge.
3. **PR #370 — Wiki methods/protocol orientation.** Documentation-only
   orientation work; fresh independent review remains the recorded gate.
4. **PR #341 — protocol-effectiveness benchmark.** PR #369 has already merged
   the public beacon-anchored selection rewrite into the #341 branch, retiring
   independent custody for **selection**. The current pre-authoring package
   manifest is owner-recomputed and awaits fresh independent review. Gate 1's
   exact Arm C competence/non-strawman approval remains unresolved; PR #371 is
   the open design child addressing that issue. Separate Gate 4/5 case-
   construction/hidden-material custody remains an unresolved later phase.

## Restart order

1. Finish independent review/correction for PR #372.
2. Reconcile the discoverability work in PR #367.
3. Reconcile PR #370 after the canonical method structure is settled.
4. Run a fresh roadmap/capability trajectory pass against merged code/tests/CI.
5. Select a small next set of parent outcomes rather than advancing every
   unfinished roadmap row mechanically.

## Retrieval boundaries

Normal work should still need:

```text
AGENTS.md + approved roadmap/task + one relevant playbook method
```

- `work/tasks/`, `work/reviews/`, and `work/notes/` are retained evidence
  collections, not orientation surfaces. Reach a record from its current
  task/roadmap/PR/handoff or a focused retrieval question; do not directory-scan
  them as startup context.
- `legacy/` is intentionally retained for historical implementations, negative
  lessons, experiments, methods, and source recovery. Prefer the curated
  `migration/` router when it already answers the question. Under
  `AGENTS.md`, read a specific legacy source only when an active higher-level
  source links that specific source for a specific reason.
- Historical wording does not become current authority merely because it is
  preserved.

## Benchmark gates still unresolved

For PR #341, the immediate package-level gate is fresh independent review of the
selection-mechanism revision, with Gate 1 Arm C competence/non-strawman approval
still unresolved. Gate 4/5 case-construction custody is a distinct later
boundary and may still require an eligible external custodian or another
approved design resolution. Benchmark execution remains unauthorized.
