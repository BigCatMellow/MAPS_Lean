# Task: GitHub-native asynchronous work pull

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `TOWER`
- Risk: `MEDIUM`
- Goal: define a minimal GitHub-native coordination protocol so separate ChatGPT browser sessions can pull eligible work asynchronously without requiring manual operator relay between agents.

## Inputs and source of truth

- Inputs: operator request; root `AGENTS.md`; `work/coordination/README.md`; current role split; live GitHub task/PR/branch/review/CI evidence.
- Authoritative sources: operator/policy authority, canonical MAPS task state, live GitHub state. Coordination prose remains derived.
- Constraint: browser sessions cannot wake/message one another directly; GitHub is the durable shared coordination surface.

## Change boundary

- MAY CHANGE:
  - `work/coordination/GITHUB_ASYNC_WORK_PULL.md`
  - `work/roadmaps/github-async-work-pull.md`
  - this task record
  - PR metadata/comments for this coordination change
- MUST NOT CHANGE:
  - runtime code, schemas, tests, feature branches, existing task lifecycle state, review dispositions, merge state, or another agent's owner-controlled coordination note
- OPERATOR APPROVAL REQUIRED: any new permanent authority, automatic merge behavior, external service/daemon, or material change to the role architecture.

## Decision authority

- Owner may decide: wording and rollout of the minimal browser/GitHub pull protocol.
- Owner must escalate: any design that creates duplicate task truth, weakens reviewer independence/integration gates, or requires new infrastructure/automation with consequential authority.

## Acceptance criteria

- [x] Shared protocol states the core model: `TOWER prioritizes; agents pull; GitHub coordinates`.
- [x] Protocol defines how each role discovers eligible work after the operator starts the browser session.
- [x] Protocol defines durable developer -> review -> integration handoffs through GitHub evidence rather than synchronous agent conversation.
- [x] Protocol preserves canonical task authority, role ownership, independent review, current-main synchronization, exact-head CI/review, and merge authority.
- [x] Protocol explicitly allows safe parallel work and identifies unsafe parallelism.
- [x] Protocol does not add a second task database, daemon, mandatory inbox, automatic merge authority, or speculative infrastructure.
- [x] Compact rollout roadmap exists.

## Verification and review

- Verify exact branch delta is documentation/planning only.
- Review required: `INDEPENDENT_REVIEW` because this is a shared multi-agent operating protocol.
- Reviewer should specifically test for hidden/duplicate authority, stale-state risk, ambiguous work claiming, reviewer-independence failure, and unsafe parallelism.

## Stop / escalation

Stop rather than guess if the protocol would require an agent to infer task readiness/ownership from a coordination note alone or if GitHub routing state would become a competing source of truth.

## Completion / handoff

- Completed: protocol + rollout roadmap + task contract.
- Not completed: independent review, integration, and empirical browser-session trial.
- Next action: independent review; if clean, SWITCHYARD integrates. After acceptance, role-specific browser agents may be instructed to follow the protocol and TOWER observes whether discovery friction remains high enough to justify labels/generated views.
