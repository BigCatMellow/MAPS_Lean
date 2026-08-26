# MAPS Lean Runtime

This directory is the active provider-neutral MAPS runtime merged to `main` by
PR #16.

Implemented components:

- `runtime/state/` — SQLite task truth, structural AGI `READY` gate, claims,
  leases, submission evidence, review, policy, continuity, immutable run
  manifests, optional criterion-level evidence, append-only post-completion
  outcomes, secret-safer task events, and a read-only canonical task trace.
- `runtime/context_builder.py` — disposable explicit context plan from task
  relationships, root authority, exact file hashes, and dependency state; no
  repository scan or semantic retrieval. Its `authority`/`required`/`guidance`
  fields correspond to the authority/task-context/fact-knowledge classes in
  `playbook/INFORMATION_CLASSES.md`.
- `runtime/status.py` — compact read-only operator projection of canonical task
  counts, active claims, attention items, recent events, and outcome failures.
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
- `runtime/environment/` — EnvironmentSpec/EnvironmentFingerprint declaration
  and compatibility evaluation; advisory only, never task authority.
  `validation.py` executes a spec's declared quick/normal/full validation-tier
  commands and exposes a Hook-callback factory. PR #172 also made the RnS
  resume path able to invoke an advisory run-bound quick-tier observation from
  the explicitly-invoked `maps recovery-tick --repo-root <path>` production
  composition. That path normally reports `no_spec_bound` and executes no
  validation command because `run_environment_evidence` still has no production
  writer; validation does not gate resume.
- `runtime/operational_learning.py` — lesson record validation and
  guidance-only projection; `runtime/outcome_lesson_candidate.py` builds
  CANDIDATE snapshots from task outcomes. Promotion/retirement is
  operator-only (`runtime/state/operational_learning_storage.py`).
- `runtime/context_retrieval_eval.py` — frozen Stage 2 retrieval evaluator;
  `context_retrieval_semantic.py` is one evaluation-only candidate
  (fastembed-based), not a production path.
- `runtime/wait_projection.py` — read-only explainable-wait projection over
  task/review/dependency state.
- `runtime/skills/` — skill discovery (`discover_skills`: id/name/content-hash
  only), full loading (`load_skill`/`load_catalog_skill`, returns procedure
  body), a content-safety gate (`gate.py`), and a selection-evaluation harness.
- `runtime/benchmark_results.py`, `runtime/acquisition_evidence.py`,
  `runtime/evaluation/` — evidence-binding and benchmark-protocol support.

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
outcomes    append-only later evidence; no task authority
context     disposable explicit read plan; no task authority
status      disposable operator read model; no task authority
trace       disposable read model over canonical task DB records
Markdown    durable human-readable record
WezTerm     optional presentation
```

A route, message, active session, recovery attempt, helper result, run manifest,
outcome observation, context plan, status view, or trace projection does not
itself change task authority.

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

## Task trace and event safety

`python -m runtime.cli trace TASK-0042` produces a read-only projection from the
canonical task database. It includes current task state, policy, event timeline,
review metadata, run manifests/context hashes, criterion evidence, and recorded
post-completion outcomes.

Trace v1 intentionally omits raw submission evidence and explicitly reports
coverage gaps. It does **not** yet correlate hcom, recovery JSON, helper-run
evidence, or escalation artifacts into the timeline; the output says so rather
than presenting a partial history as complete replay.

Durable `task_events.summary` writes pass through a best-effort secret redaction
boundary for common bearer tokens, API/access credentials, passwords, known
token formats, and private-key blocks. Redaction leaves an explicit
`[REDACTED:...]` marker. Canonical evidence in its owning tables is not silently
rewritten; diagnostic trace output is redacted again on read so older event or
review text is safer to inspect.

This is a safety boundary, not a claim that arbitrary secrets can always be
recognized. Do not intentionally place secrets in task/review text.

## Outcome feedback

A task becoming `DONE` records that MAPS's required implementation/review process
completed. It does not prove the real-world result remained successful later.
Outcome observations preserve that later knowledge separately:

```bash
python -m runtime.cli outcome-record TASK-0042 FAILURE \
  --source "operator regression report" \
  --actor-class OPERATOR --actor-id operator-1 \
  --failure-class regression --escaped-defect --rework-count 1

python -m runtime.cli outcomes TASK-0042
```

Outcome records are SQLite append-only. They include explicit actor provenance
(or `UNKNOWN`), source, task revision, optional run binding, failure class,
escaped-defect/rework/operator-intervention metrics, and optional notes. A later
observation may explicitly supersede an earlier outcome ID; the older record is
never deleted or rewritten.

Outcome recording requires the task to already be `DONE` and does not reopen the
task, change review, change ownership, change policy, or grant routing authority.
Source/notes are best-effort redacted at write because they are diagnostic
metadata, not a place to store secrets or full evidence artifacts.

## Context Builder v1

`python -m runtime.cli context TASK-0042 --repo-root .` creates a disposable
read-only context plan. It does **not** copy file contents or create another
knowledge store.

The plan contains:

- root `AGENTS.md` as active repository authority when present;
- explicit task `inputs` and `sources`;
- exact repo-relative path, SHA-256, and byte size for referenced files;
- descriptive/external references without pretending they are files;
- explicit missing, outside-repo, or directory-not-expanded references;
- dependency task status;
- decision/output/non-goal/acceptance/verification/review/escalation boundaries;
- the stable task revision used to build the plan.

v1 explicitly reports:

```text
semantic_retrieval_used: false
repository_scan_used: false
file_contents_included: false
```

This is intentional. The legacy lexical claim-card retriever did not validate.
Semantic supplementation, query expansion, or other retrieval should be added
only after a frozen evaluation demonstrates benefit on paraphrase/vocabulary-
shift queries and hard negatives. Current v1 answers the narrower question:
**what exact context has the task already told us is authoritative or required?**

## Status surface v1

`python -m runtime.cli status` gives the operator a compact read-only view of the
canonical task database. It is a read model, not a Command Center authority.

It reports:

- counts for every task lifecycle status;
- active claimant, lease, heartbeat, and attempt information;
- attention items for `READY_FOR_REVIEW`, `BLOCKED`, expired/missing ACTIVE
  leases, and the latest post-completion `FAILURE` outcome for a task;
- recent event IDs/types/actors/timestamps without copying free-text summaries;
- explicit coverage gaps for hcom, recovery, and helper-run state.

A later successful outcome removes an older post-completion failure from the
current attention view because status uses the latest outcome observation while
preserving the older append-only record in history.

v1 deliberately does not poll, retry, kill, reassign, approve, recover, or infer
state from communication. Those actions remain with their existing guarded
runtime mechanisms.

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

The runtime stack workflow verifies the legacy dependency gate, compile/Ruff/
Bandit/pip checks, the current full unit-test suite, disposable SQLite/LangGraph
smoke, and installer syntax/preview. Pull requests run this workflow automatically.
