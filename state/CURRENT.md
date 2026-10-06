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
4. **PR #341 — protocol-effectiveness benchmark.** Owner-safe design/pre-authoring
   work is complete; execution is blocked on genuinely independent corpus
   custody. PR #371 is a design child of this benchmark arc.

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
  `migration/` audit/ledger when they already answer the question; read a
  specific legacy source when the active question requires it.
- Historical wording does not become current authority merely because it is
  preserved.

## True external blocker

The benchmark in PR #341 requires an independent curator/custodian whose hidden
working state is inaccessible to MAPS_L protocol modifiers. That remains a real
external dependency rather than ordinary unfinished repository work.
