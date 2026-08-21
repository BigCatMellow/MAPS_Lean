# Task: no-progress advisory projection

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: add a read-only advisory no-progress detector that reports when a
  live worker/session shows repeated equivalent activity without task,
  artifact, heartbeat, or explicit-wait progress across a caller-provided
  threshold.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `work/roadmaps/CAPABILITY_CHECKLIST.md` item 6.20,
  `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section 6.20,
  `work/roadmaps/prime-agent-capability-roadmap.md` §11.5-11.6,
  `runtime/incident_taxonomy.py`, and existing status/wait/helper tests.
- Authoritative sources: roadmap 6.20 governs advisory-only scope; Prime
  §11.5-11.6 governs false-positive protections.
- Evidence labels: `VERIFIED` for roadmap text and existing incident class
  `HELPER_NO_PROGRESS`; `UNKNOWN` for provider-specific liveness and actual
  session activity outside caller-supplied observations.
- Dependencies / preconditions: none beyond runtime module/test structure.

## Change boundary

- MAY CHANGE: a new `runtime/no_progress.py` projection module, targeted tests,
  this task file, and checklist 6.20 status/evidence text.
- MUST NOT CHANGE: task lifecycle state, recovery supervisor behavior,
  provider/session control, helper wrappers, routing decisions, database schema,
  and unrelated roadmap items.
- MAY CHANGE IF NECESSARY: exports only if tests need a stable public symbol.
- OPERATOR APPROVAL REQUIRED: auto-killing/reassigning/resuming workers,
  mutating tasks from no-progress signals, or provider-specific process calls.

## Decision authority

- Owner may decide: projection data shape, reason codes, default threshold
  validation, and tests.
- Owner must escalate: any remediation behavior, lifecycle mutation,
  provider-specific integration, or persisted incident labeling.

## Acceptance criteria

- [ ] Detector returns `NO_PROGRESS` only when the session is live, task is
  eligible, no explicit wait is active, repeated equivalent activity reaches
  threshold, and no progress signal changed within the observation window.
- [ ] Detector returns `CLEAR` with exact reasons for non-live sessions,
  ineligible tasks, explicit waits, threshold not reached, and progress changes.
- [ ] Projection is read-only/advisory and does not mutate task state or
  provider sessions.
- [ ] Checklist 6.20 moves to `IN PROGRESS` and states no remediation or
  provider integration exists yet.

## Verification and evidence

- Verification: `git diff --check`; targeted no-progress tests; relevant
  status/wait regression subset if needed.
- Evidence to preserve: task file, checklist row, test output, and independent
  review evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: local MAPS_Lean worktree only.
- Ordered procedure: implement pure projection; add false-positive tests;
  update checklist; verify.
- Failure branches: when evidence is missing/ambiguous, return `CLEAR` or
  `UNKNOWN` rather than `NO_PROGRESS`.
- Rollback / recovery: revert implementation commit.
- Security / privacy controls: do not store prompts/tool outputs; accept only
  caller-provided summary tokens/hashes.
- External side effects: GitHub PR publication only.
- Effort limit: advisory projection only; no supervisor wiring.
- Approved reference: roadmap 6.20 and Prime §11.5-11.6.

## Stop / escalate

Stop rather than guess if:

- provider liveness needs direct process/network inspection;
- no-progress would trigger automatic remediation;
- persisted incident labeling is needed; or
- task eligibility semantics require canonical state mutation.

Escalate to: operator for remediation authority; separate task for provider
integration or incident-corpus labeling.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`
