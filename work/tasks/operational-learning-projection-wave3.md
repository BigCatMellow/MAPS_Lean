# Task: Operational learning projection Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `operational-learning-projection-wave3`
- Risk: `MEDIUM`
- Goal: validate externally supplied operational-lesson records and selectively project already-promoted, currently applicable guidance without creating lesson authority, policy authority, or a second durable state store.

## Inputs and source of truth

- Inputs:
  - root `AGENTS.md`
  - merged append-only outcome evidence in `runtime/state/outcomes.py`
  - `migration/FUTURE_IDEAS_BACKLOG.md`
  - `work/roadmaps/legacy-recovery-reconciliation.md` NEXT E
  - `work/roadmaps/agent-harness-capabilities/05-learning-and-evaluation.md`
- Authoritative sources: merged task/policy/review/outcome mechanisms remain authoritative for their facts. Operational lesson records are externally supplied guidance evidence only.
- Evidence labels: candidate observation != promoted guidance != policy/authority.
- Dependencies / preconditions: none beyond merged outcome/provenance foundation; this tranche deliberately does not depend on draft evaluation or harness PRs.

## Change boundary

- MAY CHANGE:
  - `runtime/operational_learning.py`
  - `tests/test_operational_learning.py`
  - this task file
  - `work/notes/2026-08-15-operational-learning-projection.md`
- MUST NOT CHANGE:
  - SQLite schema/task/outcome/policy/review state
  - Context Builder production behavior
  - task/startup instructions
  - existing PR #20-#42 branches
  - automatic promotion or self-modifying policy
  - a durable lesson registry/store
- MAY CHANGE IF NECESSARY: record/projection validation rules only through explicit task amendment.
- OPERATOR APPROVAL REQUIRED: any mechanism that promotes a lesson, persists active guidance, mutates policy/instructions, or automatically injects guidance into production execution.

## Decision authority

- Owner may decide: bounded immutable record contract, applicability matching semantics, expiry/review/supersession withholding, deterministic projection shape, focused tests.
- Owner must escalate: durable storage, promotion authority, policy semantics, automatic activation, conflict resolution between authoritative instructions and lessons, or production Context Builder/startup integration.

## Acceptance criteria

- [x] `CANDIDATE` lessons never project as active guidance.
- [x] `ACTIVE` lessons require an externally supplied promotion decision reference, promoter, start time, and review time.
- [x] `RETIRED` lessons never project; retirement carries explicit decision/actor/time evidence.
- [x] Applicability can be global or explicitly scoped by project/task type/risk/path, but not both.
- [x] Missing applicability inputs preserve `UNKNOWN` and withhold guidance rather than broadening applicability.
- [x] Not-started, expired, review-due, superseded, retired, candidate, non-applicable, and unknown-applicability lessons are withheld with explicit reasons.
- [x] Non-task observations may project only after arriving as an externally promoted ACTIVE lesson; their source class does not grant authority.
- [x] Projected records are explicitly `GUIDANCE_ONLY` and cannot grant task/policy authority or promote candidates.
- [x] Promotion cannot begin before lesson creation; retirement cannot predate creation/promotion.
- [x] Unsafe repository path matchers fail closed.
- [x] Duplicate lesson IDs fail closed and output ordering is deterministic.
- [x] No database/store, mutation API, promotion API, or production injection path is added.

## Verification and evidence

- Verification:
  - `python -m unittest tests.test_operational_learning -v`
  - full PR Runtime stack CI
- Evidence to preserve: exact head, changed-file list, focused/full CI result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: repository Python runtime.
- Ordered procedure: validate externally supplied lesson snapshot → evaluate lifecycle time gates → evaluate explicit applicability → emit guidance-only projection or withholding reason.
- Failure branches: malformed records fail closed; missing applicability context becomes `APPLICABILITY_UNKNOWN`; review due/expiry/supersession withholds.
- Rollback / recovery: revert isolated PR; no durable data migration exists.
- Security / privacy controls: claims/source refs/decision refs are checked through the existing observability redaction boundary; no raw private prompts or hidden model reasoning are required.
- External side effects: none.
- Effort limit: record validation/projection only; no registry/promotion/startup integration.
- Approved reference: merged outcome evidence boundary + planning roadmap NEXT E.

## Stop / escalate

Stop rather than guess if:

- lesson persistence or mutation becomes necessary;
- a candidate must be promoted;
- guidance conflicts with current authoritative task/policy/operator instructions;
- automatic startup/Context Builder injection is requested;
- applicability needs semantic inference rather than explicit fields.

Escalate to: operator / separately shaped authority or integration task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- There is deliberately no `promote()` function. ACTIVE status is accepted only as an externally decided input carrying promotion evidence.
- Guidance projection is derived/read-only. It is not a second policy database in disguise.
- Review-due guidance is withheld rather than silently remaining active forever.
- This tranche does not decide where reviewed lesson records should eventually live.

## Completion / handoff

- Completed: pure validation/projection implementation and lifecycle/applicability adversarial tests.
- Not completed: durable lesson registry, promotion/retirement mutation flow, production Context Builder/startup integration, independent review.
- Current blocker: none for this bounded tranche.
- Next action if not DONE: open isolated draft PR against current main and run full Runtime CI.
