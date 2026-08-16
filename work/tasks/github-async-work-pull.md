# Task: GitHub-native asynchronous work pull

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `TOWER`
- Risk: `MEDIUM`
- Goal: define a minimal GitHub-native coordination protocol so explicitly role-bound ChatGPT browser sessions can pull eligible work asynchronously without requiring manual operator relay between agents, while SWITCHYARD persistently controls the entire live open-PR backlog.

## Inputs and source of truth

- Inputs: operator request; observed browser trial where a fresh unbound session self-selected SENTINEL; observed backlog-control need with many simultaneously open PRs; root `AGENTS.md`; `work/coordination/README.md`; current role split; live GitHub task/PR/branch/review/CI evidence.
- Authoritative sources: operator/policy authority, including browser-session role binding; canonical MAPS task state; live GitHub state. Coordination prose remains derived.
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

- Operator binds each browser session to exactly one existing MAPS role.
- TOWER decides product/work priority from derived planning evidence.
- SWITCHYARD owns persistent PR backlog control and integration safety, but not feature implementation or independent-review authority.
- Owner may decide: wording and rollout of the minimal browser/GitHub pull protocol.
- Owner must escalate: any design that creates duplicate task/PR truth, permits autonomous permanent role selection, weakens reviewer independence/integration gates, or requires new infrastructure/automation with consequential authority.

## Acceptance criteria

- [x] Shared protocol states the core model: `Operator binds roles; TOWER prioritizes; assigned agents pull; GitHub coordinates`.
- [x] Protocol explicitly forbids a fresh/unbound browser session from choosing its own permanent role based on workload or repository activity.
- [x] An unbound session is limited to safe orientation and must report `UNBOUND — role assignment required` before consequential work.
- [x] Protocol defines how each explicitly bound role discovers eligible work after the operator starts the browser session.
- [x] Protocol defines durable developer -> review -> integration handoffs through GitHub evidence rather than synchronous agent conversation.
- [x] Protocol defines SWITCHYARD as persistent controller of the **entire live open-PR backlog**, not merely the current integration candidate.
- [x] SWITCHYARD must ensure every open PR has a current derived disposition, next legitimate gate, and discoverable owner/blocker.
- [x] SWITCHYARD backlog dispositions include `INTEGRATE`, `REVIEW NEEDED`, `REPAIR NEEDED`, `BLOCKED`, `SUPERSEDED / CLOSE CANDIDATE`, and `PLANNING / COORDINATION`.
- [x] If one PR is waiting on another role, CI, dependency, or operator action, SWITCHYARD continues scanning/advancing other independent eligible PR-control work rather than idling.
- [x] Backlog control does not permit bypassing dependency, review, CI, ownership, exact-head, or merge-authority gates merely to reduce the PR count.
- [x] The PR queue remains a derived view of live GitHub and does not become a second mutable PR database.
- [x] Protocol preserves canonical task authority, role ownership, independent review, current-main synchronization, exact-head CI/review, and merge authority.
- [x] Protocol explicitly allows safe parallel work and identifies unsafe parallelism.
- [x] Protocol does not add a second task/PR database, daemon, mandatory inbox, automatic merge authority, dynamic role allocation, or speculative infrastructure.
- [x] Compact rollout roadmap includes both an unbound-role control test and a full-backlog SWITCHYARD trial.

## Verification and review

- Verify exact branch delta is documentation/planning only.
- Review required: `INDEPENDENT_REVIEW` because this is a shared multi-agent operating protocol.
- Reviewer should specifically test for hidden/duplicate authority, stale-state risk, ambiguous work claiming, autonomous role self-selection, role drift, reviewer-independence failure, unsafe parallelism, ownerless PR risk, and backlog-control behavior that could accidentally bypass integration gates.
- Any prior exact-head review is stale after changes to the protocol/roadmap/task files and must not be used as approval for the new head.

## Stop / escalation

Stop rather than guess if the protocol would require an agent to infer its browser-session role, task readiness, ownership, PR disposition, or close/merge authority from workload/coordination notes alone, or if GitHub routing/backlog state would become a competing source of truth.

## Completion / handoff

- Completed: protocol + explicit role-binding repair + SWITCHYARD full-PR-backlog control loop + rollout roadmap + task contract.
- Not completed: fresh independent review of the current head, integration, and empirical browser-session/backlog-control trial.
- Next action: fresh independent review; if clean, SWITCHYARD integrates. After acceptance, operator creates role-specific browser tabs by explicitly binding each one; SWITCHYARD is bound once as the standing PR-control tab and `continue` resumes the complete live backlog loop.