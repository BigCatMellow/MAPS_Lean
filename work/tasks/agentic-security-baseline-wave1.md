# Task: agentic security baseline

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: freeze the first MAPS-specific agentic attack cases as behavioral regressions and close the discovered stale-session resume gap without adding new security bureaucracy or authority state.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PRs #20–#23, `work/roadmaps/agent-harness-capabilities/04-agentic-security.md`, current task/review/outcome/recovery tests.
- Authoritative sources: current runtime behavior and canonical task/policy state win; the security roadmap defines planning intent.
- Dependencies / preconditions: verified canonical-run-guard implementation from PR #23; existing review continuity and task lease semantics.

## Change boundary

- MAY CHANGE: `runtime/harness/hooks.py`, `runtime/harness/service.py`, `runtime/policy/harness_guard.py`, `tests/test_agentic_security_baseline.py`, `work/security/AGENTIC_THREAT_MODEL.md`, this task file.
- MUST NOT CHANGE: SQLite schema, task/review/policy authority semantics, hcom/helper/RnS behavior, Skill/memory/environment systems not yet implemented, external systems.
- MAY CHANGE IF NECESSARY: none without re-shaping.
- OPERATOR APPROVAL REQUIRED: new persistent authority/security state or consequential external behavior.

## Decision authority

- Owner may decide: representative adversarial fixtures, test IDs, threat-model wording, and the narrow pre-resume Hook needed to enforce the already-approved stale-session invariant.
- Owner must escalate: new policy rules, credential architecture, Skill trust implementation, or a security fix requiring durable lineage/schema changes.

## Acceptance criteria

- [ ] `resume` has an explicit pre-resume Hook interception point.
- [ ] canonical run guard treats `resume` as continuation: current revision, active claimant, live lease, non-stale run, exact durable session binding.
- [ ] stale reshaped sessions and expired-lease sessions cannot reach adapter `resume`.
- [ ] text claiming operator approval cannot satisfy a `REQUIRE_APPROVAL` Hook.
- [ ] continuity-linked helper/replacement identity cannot claim independent review.
- [ ] peer/message text cannot mutate canonical task ownership.
- [ ] provider session inspection cannot renew task lease/heartbeat.
- [ ] threat-model/corpus note preserves remaining planned attacks without claiming unimplemented protection.
- [ ] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: `tests.test_agentic_security_baseline` plus existing harness tests and full PR-triggered Runtime stack CI.
- Evidence to preserve: stacked PR diff, CI run, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing MAPS Lean Python runtime.
- Ordered procedure: freeze threat cases → add narrow `BEFORE_RESUME` guard → tests → stacked PR → CI → review.
- Failure branches: IF an attack needs an unimplemented subsystem (Skills, credential broker, learning registry) THEN preserve it as planned rather than inventing placeholder machinery.
- Rollback / recovery: revert isolated stacked commit/PR; no data migration.
- Security / privacy controls: tests use fakes/local temporary SQLite; no credentials/provider calls; raw malicious text is fixture data only.
- External side effects: Git branch/PR publication only.
- Effort limit: initial cross-system adversarial baseline, not all 20 future cases.
- Approved reference: Agentic Security roadmap SEC1/SEC2/SEC3.

## Stop / escalate

Stop rather than guess if a security property requires new policy semantics or durable session/approval representation not already present.

Escalate to: operator / roadmap re-shaping as appropriate.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task is stacked on PR #23; upstream review changes must be propagated before merge.
- The corpus intentionally distinguishes executable protections from attacks that remain planned for Skills/tools/memory/environment phases.
- The stale-session resume gap is fixed mechanically with a new pre-resume Hook; no prompt-only warning is added.

## Completion / handoff

- Completed: implementation prepared on `agent/agentic-security-baseline-wave1`.
- Not completed: commit/PR/CI/review.
- Current blocker: none.
- Next action if not DONE: commit, open stacked draft PR against `agent/harness-canonical-guard-wave1`, and run CI.
