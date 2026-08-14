# Current State

- Current goal: complete the MAPS Lean migration while leaving deletion of
  top-level `legacy/` as the final separate operator-approved action.
- Replacement runtime status: **MERGED TO `main`** by PR #16, squash commit
  `78791fca0d5cd0def5bae2c5b2eb9addcbf0770e`.
- Former stacked PRs #9–#15 are closed as superseded by PR #16 and remain only
  as detailed implementation/review history.
- Review truth: `work/reviews/RUNTIME_INTEGRATION_REVIEW.md` records a fresh
  adversarial integration review. It was performed by the same assistant
  continuity that participated in implementation, so it is not represented as
  an independent model/human review. Independent verification is mechanical and
  GitHub-hosted: compile, Ruff, Bandit, dependency checks, regression tests,
  LangGraph/SQLite smoke, installer checks, and the active legacy-dependency gate.
- Active runtime now contains:
  1. canonical SQLite task truth + structural AGI `READY` gate + atomic claims,
     leases, submission/review state, and scoped output reservations;
  2. explicit policy/worker profiles + operator approval/halt gates;
  3. read-first LangGraph routing with checkpoint state separate from task truth;
  4. project-isolated hcom transport with no task authority;
  5. deterministic RnS recovery for known current ACTIVE claims only;
  6. bounded Ollama/Aider helper lanes;
  7. preview-first fresh-clone installer and disposable smoke;
  8. immutable run/context binding, staleness proof, writable/forbidden Git
     scope proof, run-budget checks, continuity-aware review, and optional
     criterion-level evidence.
- Integration hardening fixed transactional policy shaping, parent/child output
  conflicts, repo path escape, rename-aware scope proof, dirty-worktree Aider
  attribution, typed capability booleans, scoped-halt targets, routing
  head-of-line blocking, ambiguous RnS binding, criterion-record immutability,
  writable/forbidden overlap, run-budget enforcement, and artifact filename
  containment.
- Verification on merged `main`: Actions run `31850974870` passed the full
  runtime workflow after PR #16 merged.
- Final dependency/reference sweep: **PASS**. Actions run `31851301307` scanned
  50 active executable/config files, found no active legacy/migration execution
  dependency, then passed compile/Ruff/Bandit/pip checks, **93/93 unit tests**,
  disposable SQLite/LangGraph smoke, and installer syntax/preview. See
  `migration/FINAL_LEGACY_DEPENDENCY_SWEEP.md`.
- Preservation privacy/secret sweep: **PASS — current preservation set**. See
  `migration/PRESERVATION_PRIVACY_SWEEP.md`; this is a current-tree/snapshot
  audit, not a forensic scan of all historical Git objects.
- Release decision remains: Lean does **not** restore a universal
  `APPROVED → RELEASED` state machine. Real deploy/destructive/external actions
  are explicit policy-gated tasks/actions.
- Historical Markdown/task/report files may still mention `legacy/`; they are
  provenance/safety records and are not execution dependencies.
- The curated preservation snapshots remain under `migration/` and are evidence,
  not runtime dependencies.

## Remaining migration action

**Only one migration action remains:** explicit operator-approved deletion of
 top-level `legacy/`.

Do not infer deletion authority from this status file. The deletion must be a
separate explicit operator instruction/change.
