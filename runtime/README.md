# MAPS Lean Runtime

This directory is the active provider-neutral MAPS runtime merged to `main` by
PR #16.

Implemented components:

- `runtime/state/` — SQLite task truth, structural AGI `READY` gate, claims,
  leases, submission evidence, review, policy, continuity, immutable run
  manifests, and optional criterion-level evidence.
- `runtime/policy/` — explicit task policy metadata, operator approvals, worker
  capability envelopes, and durable dispatch halt state.
- `runtime/routing/` — deterministic route selection wrapped by LangGraph with
  a separate SQLite checkpoint database.
- `runtime/communication/` — project-isolated hcom messaging/session adapter;
  transport state never grants MAPS authority.
- `runtime/recovery/` — deterministic RnS recovery for known already-active
  sessions with bounded retry/backoff and no WezTerm requirement.
- `runtime/helpers/` — bounded Ollama/Aider helper lanes that inherit parent
  task scope but never parent ownership/review authority.
- `runtime/integrity/` — immutable execution-time contract/context binding,
  staleness checks, writable/forbidden Git scope proof, run-budget checks,
  continuity-aware review support, and optional criterion evidence.

Active runtime does not import executable code from `legacy/` or `migration/`.
The final removal-readiness gate additionally scans active runtime/tests/scripts/
workflow/config surfaces for old execution dependencies.

## Responsibility boundaries

```text
SQLite      task truth / authority / evidence
LangGraph   route recommendation / checkpoint memory
hcom        communication / session process control
RnS         recovery of explicitly known active sessions
helpers     bounded delegated work
integrity   frozen run contract + proof; no new authority
Markdown    durable human-readable record
WezTerm     optional presentation
```

A route, message, active session, recovery attempt, helper result, or run
manifest does not itself change task authority.

## Mutable local state

```text
.maps/state/maps.db                    canonical MAPS task truth
.maps/state/langgraph-checkpoints.db   LangGraph routing/checkpoint memory
.maps/state/halt.json                  dispatch halt state
.maps/state/recovery.json              RnS incident/retry state
.maps/state/helper-runs.json           helper invocation evidence
.maps/state/escalations/               budget/escalation evidence
.hcom/                                 hcom message/session/process state
```

The task DB and LangGraph checkpoint DB remain separate.

## Lifecycle

```text
NEEDS_SHAPING
    │ AGI gate
    ▼
READY
    │ guarded claim
    ▼
ACTIVE
    │ optional run manifest for high-risk/resumable work
    │ implementation + evidence
    ▼
READY_FOR_REVIEW
    │ required review
    ├─ APPROVED ─────────► DONE
    ├─ CHANGES_REQUESTED ► CHANGES_REQUESTED ─► ACTIVE
    └─ BLOCKED ──────────► BLOCKED
```

There is no universal second `RELEASED` state in Lean. High-risk
`OPERATOR_VISIBLE_RELEASE_CHECK` work uses the final approved review/completion
summary as its durable operator-visible release summary. Actual destructive or
external actions still require explicit policy approval.

## AGI and run integrity

AGI asks whether the task is sufficiently specified.

For high-risk, resumable, or drift-sensitive execution, a run manifest freezes
what a specific worker actually received:

- stable task-definition hash;
- worker/session identity;
- readable/writable/forbidden scope;
- context-file hashes;
- runtime limits;
- optional Git base revision.

Run manifests/context refs are SQLite-immutable. Staleness, Git-scope, and budget
checks report or persist evidence; they do not auto-reset, restore, clean, widen
authority, or silently re-dispatch work.

See `runtime/integrity/README.md`.

## Review independence

Submission authorship is durable. Continuity links additionally record when a
replacement identity inherited the author's in-flight context/obligations.

When independent review is required, the author **and the whole connected
continuity lineage** are ineligible. This is enforced by route selection and
canonical review transitions, including a final re-check at approval time.

## Criterion evidence

Ordinary tasks retain the simple submission-evidence + review-summary path.

If a current submission records criterion claims, it opts into criterion mode:

```text
implementer claim: complete / partial / blocked + evidence refs
reviewer verdict: confirmed / rejected
```

Overall `APPROVED` then requires every current acceptance criterion to be
complete + confirmed. Claims/verdicts are SQLite-immutable audit records and
reviewer verdicts never rewrite implementer claims.

## Routing and policy

Routes:

```text
review
wait_for_agent
propose_helper
claim_or_assign
policy_gate
wait_or_reconcile
```

Worker profiles describe actual capability/availability/cost. Provider names do
not grant capability or authority. Blocked low-ID work does not prevent the
router from considering later independent routable work.

Explicit policy flags:

```text
requires_operator_approval
destructive_action
external_side_effect
security_sensitive
broad_architecture
paid_execution
```

Reshaping and policy changes are one transaction and invalidate prior operator
approval atomically.

## Communication, recovery, and helpers

hcom is live transport/session control only. RnS may recover a session only when
an existing `ACTIVE` task, current claimant, and explicit worker/session binding
still agree; ambiguous one-worker/multiple-task bindings are not guessed.
Helpers require an `ACTIVE` parent task and stay inside its output scope. Bounded
Aider additionally requires a clean worktree so its changes are attributable.

None of those mechanisms can mark work `DONE`, approve review, or widen task
authority.

## Setup

Preview first:

```bash
bash scripts/install_maps.sh
```

Apply and smoke:

```bash
bash scripts/install_maps.sh --apply --run-smoke
```

See `docs/FRESH_INSTALL.md` and `docs/CONTROL_PLANE_SETUP.md`.

## Verification

```bash
python scripts/check_legacy_removal_readiness.py
python -m unittest discover -s tests -v
python -m runtime.smoke --with-langgraph
```

Removal-readiness Actions run `31851301307` passed the legacy dependency gate,
compile/Ruff/Bandit/pip checks, **93/93 unit tests**, disposable SQLite/LangGraph
smoke, and installer syntax/preview.
