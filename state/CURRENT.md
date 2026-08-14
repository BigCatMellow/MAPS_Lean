# Current State

- Current goal: Promote the retained MAPS control plane into a small active,
  provider-neutral runtime without restoring legacy cockpit complexity.
- Review status: operator explicitly deferred independent review. PRs #9–#14
  remain open/draft in a stacked chain; TASK-015 is `READY_FOR_REVIEW` on the
  execution-integrity branch. Nothing in this stack has been merged to `main`.
- Stacked implementation now contains:
  1. SQLite task truth + structural AGI `READY` gate + claims/review (`PR #9`);
  2. explicit policy/worker profiles + read-first LangGraph routing (`PR #10`);
  3. project-isolated hcom transport/session adapter (`PR #11`);
  4. deterministic RnS recovery without WezTerm (`PR #12`);
  5. bounded Ollama/Aider helper lanes (`PR #13`);
  6. preview-first fresh-clone installer and disposable smoke (`PR #14`);
  7. immutable run manifests, context/task staleness proof, Git run-scope proof,
     continuity-aware review, and optional criterion-level evidence (`TASK-015`).
- Verification: GitHub Actions run `31847038026` passed **79/79 tests** on
  Python 3.12 with ResourceWarnings treated as errors. The disposable smoke
  passed `NEEDS_SHAPING → READY → ACTIVE → READY_FOR_REVIEW → DONE`, verified
  `foreign_keys=1`, WAL, 5000 ms busy timeout, and created a separate LangGraph
  checkpoint DB with route `wait_or_reconcile`. Installer syntax/preview passed.
- Execution-integrity proof now includes SQLite-immutable run manifests/context
  hashes, stable task revision checks, report-only Git scope verification,
  transitive continuity lineage at routing/claim/final review, and optional
  criterion claims whose reviewer verdicts remain separate.
- Release decision: Lean does **not** restore a universal `APPROVED → RELEASED`
  state machine. For `OPERATOR_VISIBLE_RELEASE_CHECK`, the approved high-risk
  review/completion summary is the operator-visible release summary. A real
  deploy/destructive/external action remains its own policy-gated task/action.
- Decisions that matter now: SQLite is canonical task truth; LangGraph only
  recommends; hcom is transport; RnS only recovers known active bindings;
  helpers stay bounded; run-integrity records constrain/prove execution but add
  no authority; WezTerm is optional presentation.
- Legacy status: useful implementation/knowledge is preserved outside
  `legacy/`. Execution-integrity follow-ups are now deliberately implemented or
  rejected. Remaining deletion blockers are deferred review/merge, final
  reference/privacy sweep, and explicit operator removal approval.
- Next action: keep review deferred as requested; open the TASK-015 draft PR,
  then perform the preserved-source privacy/secret sweep. Final active-reference
  cleanup is best done after the reviewed stack reaches `main`.
