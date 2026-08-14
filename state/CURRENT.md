# Current State

- Current goal: Promote the retained MAPS control plane into a small active,
  provider-neutral runtime without restoring legacy cockpit complexity.
- Review status: operator explicitly deferred independent review. PRs #9–#13
  remain open/draft in a stacked chain; TASK-014 is `READY_FOR_REVIEW` on the
  final installer/smoke branch. Nothing in this stack has been merged to `main`.
- Stacked implementation now contains:
  1. SQLite task truth + structural AGI `READY` gate + claims/review (`PR #9`);
  2. explicit policy/worker profiles + read-first LangGraph routing (`PR #10`);
  3. project-isolated hcom transport/session adapter (`PR #11`);
  4. deterministic RnS recovery without WezTerm (`PR #12`);
  5. bounded Ollama/Aider helper lanes (`PR #13`);
  6. preview-first fresh-clone installer and disposable smoke verification (`TASK-014`).
- Verification: GitHub Actions run `31845946112` installed the active runtime
  dependencies and passed **64/64 tests** with ResourceWarnings treated as
  errors. The separate disposable smoke also passed SQLite lifecycle
  `NEEDS_SHAPING → READY → ACTIVE → READY_FOR_REVIEW → DONE`, verified
  `foreign_keys=1`, WAL, 5000 ms busy timeout, and created a separate LangGraph
  checkpoint DB with route `wait_or_reconcile`. Installer syntax and preview
  execution also passed.
- Failure found and fixed during verification: the first full-stack CI run
  exposed new tests/smoke code using nonexistent `MutationResult.data`; the
  correct payload is `.task`. The fix was propagated down the stacked branches
  before the final green run.
- Decisions that matter now: SQLite is the only canonical mutable task state;
  LangGraph recommends routes but does not mutate task truth; hcom remains
  transport/session state; RnS may recover only already-active explicitly bound
  sessions and may not invent/claim/reassign work; local helpers remain bounded;
  WezTerm remains optional presentation.
- Legacy status: useful implementation/knowledge is preserved outside
  `legacy/`; the new stack can install/smoke without executing legacy or
  migration source. `legacy/` is still retained until deferred reviews/merges,
  final reference/privacy sweep, and explicit operator removal approval.
- Next action: keep review deferred as requested. Continue closing the few
  remaining execution-integrity ports (run-manifest/continuity/run-scope where
  warranted) or, when the operator is ready, review the stack from PR #9 upward
  before merging and deleting legacy.
