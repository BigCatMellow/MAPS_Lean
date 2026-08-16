# Task: GitHub-native asynchronous work pull

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `TOWER`
- Risk: `MEDIUM`
- Goal: define a minimal GitHub-native coordination protocol so explicitly role-bound ChatGPT browser sessions can pull eligible work asynchronously without requiring manual operator relay between agents, while SWITCHYARD persistently controls the entire live open-PR backlog, independent review can scale across multiple explicitly bound SENTINEL browser continuities, and historical PRs cannot regress newer accepted main state.

## Inputs and source of truth

- Inputs: operator request; observed browser trial where a fresh unbound session self-selected SENTINEL; observed backlog-control need with many simultaneously open PRs; observed review bottleneck where multiple synchronized roots (#44, #48, #41 at the checkpoint) converge on independent integrated-head review; operator concern that processing PRs by recency could allow historical branches to overwrite newer accepted work; root `AGENTS.md`; `work/coordination/README.md`; current role split; live GitHub task/PR/branch/review/CI evidence.
- Authoritative sources: operator/policy authority, including browser-session role binding; canonical MAPS task state; accepted `main`; live GitHub state. Coordination prose and review claims remain derived.
- Constraint: browser sessions cannot wake/message one another directly; GitHub is the durable shared coordination surface.

## Change boundary

- MAY CHANGE:
  - `work/coordination/GITHUB_ASYNC_WORK_PULL.md`
  - `work/roadmaps/github-async-work-pull.md`
  - this task record
  - PR metadata/comments for this coordination change
- MUST NOT CHANGE:
  - runtime code, schemas, tests, feature branches, existing task lifecycle state, existing review dispositions, merge state, or another agent's owner-controlled coordination note
- OPERATOR APPROVAL REQUIRED: any new permanent authority, automatic merge behavior, external service/daemon, or material change to the role architecture.

## Decision authority

- Operator binds every browser session to exactly one existing MAPS role.
- Operator may explicitly bind multiple browser continuities to the same SENTINEL role when review demand justifies parallel capacity; unique labels such as `SENTINEL-A` / `SENTINEL-B` are coordination identity only, not new roles.
- TOWER decides product/work priority from derived planning evidence and should prioritize dependency roots when they gate downstream stacks.
- SENTINEL retains independent-review authority; parallel reviewer sessions do not weaken exact-head, independence, or no-self-review requirements.
- SWITCHYARD owns persistent PR backlog control and integration safety, including dependency-first ordering and protection of accepted `main`, but not feature implementation or independent-review authority.
- Accepted `main` is the baseline authority for integration state. Historical branch content has no authority to silently replace newer accepted behavior.
- Owner may decide: wording and rollout of the minimal browser/GitHub pull protocol, including advisory review-claim mechanics that prevent duplicate reviewer work without becoming canonical review state.
- Owner must escalate: any design that creates duplicate task/PR/review truth, permits autonomous permanent role selection, manufactures reviewer independence from a label, weakens reviewer independence/integration gates, allows old branch state to override accepted main without explicit current authority, or requires new infrastructure/automation with consequential authority.

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
- [x] Integration order is explicitly dependency-first / bottom-up; PR age, number, or creation time do not grant merge priority.
- [x] For stacked work, accepted prerequisites/root foundations must land before direct dependents are synchronized/reviewed for final integration.
- [x] Every historical integration candidate must be genuinely synchronized onto the latest accepted `main` before merge.
- [x] SWITCHYARD must compare exact `current main -> synchronized head` and verify only the intended task-authorized delta plus explicit reviewed conflict reconciliation remains.
- [x] Historical branch content may not silently delete, revert, replace, or reintroduce stale versions of newer accepted behavior outside explicit current task/operator authority.
- [x] When historical content overlaps newer accepted behavior, accepted `main` wins by default unless an explicitly authorized current task intentionally supersedes it and receives fresh exact-head review.
- [x] Any merge changing `main` makes remaining integration candidates potentially stale; ancestry, dependencies, exact delta, CI, and review freshness must be rechecked before subsequent merges.
- [x] SENTINEL integrated-head review includes anti-regression verification that synchronization preserved newer accepted behavior.
- [x] SENTINEL is defined as one review role that may have multiple explicitly operator-bound browser continuities; those continuities are not new permanent roles.
- [x] Each parallel SENTINEL continuity receives a unique operator-provided continuity label for GitHub coordination.
- [x] Reviewer eligibility remains continuity-specific: a SENTINEL continuity cannot review work it implemented, repaired, synchronized, or materially authored; a different label alone does not prove independence.
- [x] A lightweight `MAPS REVIEW CLAIM` records exact base/head, review layer, continuity label, and independence check before substantive review.
- [x] Review claims are explicitly advisory coordination evidence only: they do not make work ready, approve/reject it, change canonical task/review state, or grant merge authority.
- [x] Concurrent SENTINEL sessions preferentially claim different eligible exact heads; same-head claim races use GitHub ordering to avoid duplicate work unless multiple reviews are explicitly required.
- [x] Head/base movement or an exact-head disposition makes the corresponding claim irrelevant, and an abandoned claim cannot permanently deadlock review progress.
- [x] Parallel SENTINEL continuities may review different PRs concurrently without branch mutation or weakened review criteria.
- [x] Protocol preserves canonical task authority, role ownership, independent review, current-main synchronization, exact-head CI/review, and merge authority.
- [x] Protocol explicitly allows safe parallel work and identifies unsafe parallelism.
- [x] Protocol does not add a second task/PR/review database, daemon, mandatory inbox, automatic merge authority, dynamic role allocation, or speculative infrastructure.
- [x] Compact rollout roadmap includes an unbound-role control test, a parallel-SENTINEL review trial, dependency-first anti-regression integration proof, and a full-backlog SWITCHYARD trial.

## Verification and review

- Verify exact branch delta is documentation/planning only.
- Review required: `INDEPENDENT_REVIEW` because this is a shared multi-agent operating protocol.
- Reviewer should specifically test for hidden/duplicate authority, stale-state risk, ambiguous work claiming, autonomous role self-selection, role drift, manufactured reviewer independence, duplicate-review races, abandoned-claim deadlock, reviewer mutation of reviewed work, unsafe parallelism, ownerless PR risk, PR-age-based ordering, stale-branch regression of accepted main, and backlog-control behavior that could accidentally bypass integration gates.
- Any prior exact-head review is stale after changes to the protocol/roadmap/task files and must not be used as approval for the new head.
- The anti-regression update itself requires a fresh exact-head independent review; no earlier #73 disposition is reusable.

## Stop / escalation

Stop rather than guess if the protocol would require an agent to infer its browser-session role, reviewer continuity, reviewer independence, task readiness, ownership, dependency order, PR disposition, conflict resolution, or close/merge authority from workload/coordination notes alone, or if GitHub routing/backlog/review-claim state would become a competing source of truth.

Stop integration if a historical candidate cannot be reconciled with current accepted `main` without an authority decision about which behavior should survive. Do not resolve that ambiguity by favoring the old branch merely because it is older or was developed first.

## Completion / handoff

- Completed: protocol + explicit role-binding repair + parallel SENTINEL reviewer pool + lightweight exact-head review claims + SWITCHYARD full-PR-backlog control loop + dependency-first anti-regression integration rules + rollout roadmap + task contract.
- Not completed: fresh independent review of the current head, integration, and empirical browser-session/reviewer-pool/backlog-control/anti-regression trial.
- Next action: fresh independent review; if clean, SWITCHYARD integrates. After acceptance, operator creates role-specific browser tabs by explicitly binding each one; multiple SENTINEL tabs may be bound with unique continuity labels, while SWITCHYARD remains the standing PR-control tab and derives integration order from dependency structure rather than PR age.

Current exact #73 head after this anti-regression handoff refresh must be recovered live before review; any earlier head/review is stale.