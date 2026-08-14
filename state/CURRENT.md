# Current State

- Current goal: Promote the retained MAPS control plane into a small active,
  provider-neutral runtime without restoring legacy cockpit complexity.
- Review status: operator explicitly deferred independent review. PRs #9–#14
  remain open/draft in a stacked chain; TASK-015 / PR #15 is
  `READY_FOR_REVIEW`. Nothing in this stack has been merged to `main`.
- Stacked implementation now contains:
  1. SQLite task truth + structural AGI `READY` gate + claims/review (`PR #9`);
  2. explicit policy/worker profiles + read-first LangGraph routing (`PR #10`);
  3. project-isolated hcom transport/session adapter (`PR #11`);
  4. deterministic RnS recovery without WezTerm (`PR #12`);
  5. bounded Ollama/Aider helper lanes (`PR #13`);
  6. preview-first fresh-clone installer and disposable smoke (`PR #14`);
  7. immutable run manifests, context/task staleness proof, Git run-scope proof,
     continuity-aware review, and optional criterion-level evidence (`PR #15`).
- Verification: GitHub Actions run `31847038026` passed **79/79 tests** on
  Python 3.12 with ResourceWarnings treated as errors. The disposable smoke
  passed `NEEDS_SHAPING → READY → ACTIVE → READY_FOR_REVIEW → DONE`, verified
  `foreign_keys=1`, WAL, 5000 ms busy timeout, and created a separate LangGraph
  checkpoint DB with route `wait_or_reconcile`. Installer syntax/preview passed.
- Execution-integrity proof includes SQLite-immutable run manifests/context
  hashes, stable task revision checks, report-only Git scope verification,
  transitive continuity lineage at routing/claim/final review, and optional
  criterion claims whose reviewer verdicts remain separate.
- Release decision: Lean does **not** restore a universal `APPROVED → RELEASED`
  state machine. For `OPERATOR_VISIBLE_RELEASE_CHECK`, the approved high-risk
  review/completion summary is the operator-visible release summary. A real
  deploy/destructive/external action remains its own policy-gated task/action.
- Privacy/secret sweep: `migration/PRESERVATION_PRIVACY_SWEEP.md` records a
  PASS for the current preservation set. No checked credential/private-key
  patterns or copied live DB/sidecar, transcript/inbox/message store, log/JSONL,
  settings/status/state snapshot, screenshot/image, or machine-private home path
  was identified in the two curated migration snapshots/current indexed tree.
  This is explicitly a current-tree audit, not a forensic scan of all historical
  Git objects.
- Decisions that matter now: SQLite is canonical task truth; LangGraph only
  recommends; hcom is transport; RnS only recovers known active bindings;
  helpers stay bounded; run-integrity records constrain/prove execution but add
  no authority; WezTerm is optional presentation.
- Legacy status: useful implementation/knowledge is preserved outside
  `legacy/`. Execution-integrity follow-ups are implemented or deliberately
  rejected and the current preservation privacy gate is closed.
- Remaining legacy-deletion blockers:
  1. deferred independent review of PRs #9–#15;
  2. merge the reviewed stack to `main`;
  3. run the final active reference/dependency sweep against the merged tree;
  4. explicit operator approval for the legacy-removal change.
- Next action: keep review deferred as requested. No further architecture is
  required before review; the next productive phase is review/fix/merge when
  the operator chooses to begin it.
