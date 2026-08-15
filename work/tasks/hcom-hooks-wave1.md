# Task: hcom normalization and Hook registry

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: extend the Wave 1 harness foundation with honest hcom operation normalization and a deterministic in-process Hook registry without creating new authority, lineage, helper-session, or provider behavior.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PR #20 / `agent/harness-foundation-wave1`, `runtime/communication/hcom_adapter.py`, `runtime/helpers/**`, `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`, and `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md`.
- Authoritative sources: active repository instructions and current runtime behavior win; roadmap files provide planning intent; PR #20 provides the typed harness contract this stacked task depends on.
- Evidence labels: PR #20 head `ecfc27269e096db5d83bfa376878c33089a4e106` is VERIFIED as the dependency baseline and has successful Runtime stack CI.
- Dependencies / preconditions: PR #20 contract exists; this task is intentionally stacked on it and must be rebased/reshaped if #20 changes materially in review.

## Change boundary

- MAY CHANGE: `runtime/harness/**`, new focused harness tests, and this task file.
- MUST NOT CHANGE: canonical task-state schema/authority, hcom's existing low-level behavior, RnS behavior, helper execution behavior, routing behavior, review semantics, deployment/external systems.
- MAY CHANGE IF NECESSARY: none without re-shaping.
- OPERATOR APPROVAL REQUIRED: destructive/external behavior or material expansion beyond adapter normalization and Hook mechanics.

## Decision authority

- Owner may decide: normalized hcom status mappings, bounded hcom result semantics, Hook event/result/failure-policy types, deterministic ordering, and focused test design consistent with the roadmaps.
- Owner must escalate: any design that would infer task authority from session liveness, create a second lineage/task store, force run-to-completion helpers into a false live-session abstraction, or guess unsupported hcom lifecycle semantics.

## Acceptance criteria

- [ ] hcom `inspect`, `send`, and `stop` use `OperationResult` with explicit project/session checks and bounded output.
- [ ] Unknown provider status remains `UNKNOWN`; session-not-found is distinct from transport failure.
- [ ] Unsupported hcom lifecycle operations return structured `UNSUPPORTED` instead of guessed behavior.
- [ ] Hook registry provides deterministic ordering and `ALLOW`, `DENY`, `REQUIRE_APPROVAL`, and `ANNOTATE` outcomes.
- [ ] Hook failures fail closed by default; optional non-blocking/raise policies are explicit.
- [ ] Hook execution does not grant task authority, approval, ownership, scope, or completion.
- [ ] Existing helper subsystem remains unchanged; this task records that helper runs are evidence, not live sessions, and defers helper lineage normalization until the lineage design exists.
- [ ] Focused tests and full Runtime stack CI pass.
- [ ] Changes receive independent review before completion.

## Verification and evidence

- Verification: focused unittest modules for hcom harness normalization and Hook mechanics, plus PR-triggered full Runtime stack CI.
- Evidence to preserve: stacked PR diff, GitHub Actions run, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing MAPS Lean Python runtime.
- Ordered procedure: hcom normalization + Hook registry → focused tests → stacked PR → CI → independent review.
- Failure branches: IF a hcom operation cannot be represented without guessing identity/lineage/runtime mode THEN return `UNSUPPORTED`; IF helper adaptation would falsely imply live-session semantics THEN defer it.
- Rollback / recovery: revert the isolated stacked commit/PR; no schema/data migration is introduced.
- Security / privacy controls: provider exceptions are normalized without raw error text in agent-facing summaries; project isolation remains explicit; hooks default fail-closed.
- External side effects: Git branch/PR publication only; tests use fakes and do not control real sessions.
- Effort limit: one stacked Wave 1 tranche; no concrete scope/policy guard Hook yet.
- Approved reference: master roadmap + Harness Mechanics roadmap.

## Stop / escalate

Stop rather than guess if:

- hcom cannot prove the session identity required by an operation;
- a new durable join/lineage store appears necessary;
- provider-specific resume/start behavior requires an unapproved default;
- review of PR #20 materially changes the contract underneath this branch.

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

- This is a stacked task based on PR #20 rather than a blocker on PR #20 review.
- hcom `start` is deferred until spawn can return or reconcile a structured session identity.
- hcom `attach` is deferred until durable run/session lineage can represent the attachment honestly.
- hcom `heartbeat` is not mapped to MAPS task-claim heartbeat; session liveness stays separate.
- hcom `resume` is deferred rather than guessing headless/terminal behavior.
- helper runs remain bounded run-to-completion evidence; do not force them into `SessionRef` semantics.

## Completion / handoff

- Completed: implementation in progress on `agent/hcom-hooks-wave1`.
- Not completed: tests/CI/review.
- Current blocker: none.
- Next action if not DONE: commit implementation and open stacked draft PR against `agent/harness-foundation-wave1`.
