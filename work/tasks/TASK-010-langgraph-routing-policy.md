# Task: Promote LangGraph routing and policy gates

- Status: `READY`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `implementation-agent`
- Risk: `HIGH`
- Goal: Add a read-first LangGraph routing layer that consumes canonical SQLite task state and explicit worker capability profiles, applies deterministic policy/halt gates, recommends a route, and never mutates task truth.

## Inputs and source of truth

- Inputs: `runtime/state/**`, `playbook/HPOM_ROUTING.md`, `playbook/MODEL_CAPABILITY_ROUTING.md`, `playbook/DECISIONS_AND_SAFETY.md`, `migration/legacy-runtime-source/graph/**`, `migration/legacy-runtime-source/scripts/pre_dispatch_policy.py`, `migration/legacy-runtime-source/scripts/halt_state.py`, relevant preserved tests.
- Authoritative sources: active Lean playbooks and active SQLite task state. Legacy migration source is behavioral evidence only.
- Evidence labels: active Lean rules = VERIFIED current policy; migration source = VERIFIED historical behavior.
- Dependencies / preconditions: TASK-009 branch provides the active SQLite task store.

## Change boundary

- MAY CHANGE: `runtime/routing/**`, `runtime/policy/**`, `runtime/requirements.txt`, `runtime/cli.py`, targeted `runtime/state/**` fields/read APIs needed for routing, `tests/**`, setup/runtime docs, migration checklists, this task record and current state.
- MUST NOT CHANGE: hcom/RnS/local-helper implementations, legacy source, migration snapshots, operator intent, unrelated playbooks.
- MAY CHANGE IF NECESSARY: task schema only for explicit policy metadata/approval records required to avoid text-based authority inference.
- OPERATOR APPROVAL REQUIRED: destructive actions, external side effects, architecture/product/security decisions remain operator-owned; this task may encode gates but not approve them.

## Decision authority

- Owner may decide: internal routing data structures, deterministic policy representation, route-result schema, tests, checkpoint adapter shape.
- Owner must escalate: changing operator authority, weakening AGI/independent-review gates, making LangGraph a writer of canonical task state, or broadening scope into hcom/RnS/helpers.

## Acceptance criteria

- [ ] Router reads canonical task snapshots and returns one typed recommendation without mutating task state.
- [ ] Policy evaluation uses explicit task metadata and worker profiles rather than provider/name-based capability inference.
- [ ] Operator-required/destructive/external/security-sensitive work routes to `policy_gate` until explicit approval exists.
- [ ] Durable halt state can block appropriate dispatch lanes without deleting/changing task truth.
- [ ] `READY_FOR_REVIEW` work routes to an eligible independent reviewer when available.
- [ ] Ready work routes to the cheapest competent available execution envelope based on explicit profile rank/capability fields.
- [ ] LangGraph checkpoint state uses `.maps/state/langgraph-checkpoints.db`, separate from `.maps/state/maps.db`.
- [ ] Routing/checkpoint tests pass; state-layer tests from TASK-009 remain green.

## Verification and evidence

- Verification: unit tests for pure routing/policy/halt behavior; optional LangGraph integration test when dependency is installed; static/syntax checks in development.
- Evidence to preserve: test output and PR diff.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Python 3.10+; LangGraph SQLite saver for lightweight local synchronous routing.
- Ordered procedure: preserve legacy invariant → implement explicit Lean policy/profile model → test pure evaluator → add thin LangGraph/checkpoint adapter → update docs/checklists.
- Failure branches: IF LangGraph dependency is unavailable locally THEN verify pure routing logic and keep the integration test dependency-gated; do not fake successful checkpoint execution.
- Rollback / recovery: remove `runtime/routing/` and `runtime/policy/` slice; SQLite TASK-009 state remains independent.
- Security / privacy controls: checkpoint DB is local runtime state and must not grant authority.
- External side effects: none beyond repository changes.
- Effort limit: keep this a routing/policy slice; defer transport/recovery/helpers.
- Approved reference: active Lean playbooks plus preserved legacy routing behavior.

## Stop / escalate

Stop rather than guess if:

- routing requires mutating task truth directly from LangGraph;
- a capability/authority decision cannot be represented explicitly;
- implementation would require hcom/RnS/helper changes.

Escalate to: operator for authority/architecture changes.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This is stacked on TASK-009 while its independent review is deferred by operator instruction.
- LangGraph is routing/checkpoint memory, never canonical task authority.

## Completion / handoff

- Completed: task shaped.
- Not completed: implementation and verification.
- Current blocker: none.
- Next action if not DONE: create stacked branch and implement policy/routing tests first.
