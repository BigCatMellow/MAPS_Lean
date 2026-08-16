# Task: Agent roadmap guidance upgrade

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: roadmap-guidance documentation lane
- Risk: `MEDIUM`
- Goal: each active coordination agent file contains durable, role-specific guidance for participating in MAPS roadmap creation, challenge, execution, review, and integration without changing the agent's current lane ownership or volatile status.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `playbook/INDEX.md`, `playbook/ROADMAP_AND_PROJECTUPDATER.md`, `templates/roadmap.md`, `templates/task.md`, `work/coordination/README.md`, and the four current files under `work/coordination/agents/`.
- Authoritative sources: live GitHub state for repository/PR/branch status; `AGENTS.md` for repository operating rules; `playbook/ROADMAP_AND_PROJECTUPDATER.md` and `templates/roadmap.md` for roadmap method and structure.
- Evidence labels: repository files and live GitHub reads are VERIFIED at the inspected refs; coordination snapshots remain evidence only and may become stale.
- Dependencies / preconditions: preserve active lane ownership and avoid rewriting volatile PR/head/status blocks; append durable guidance so concurrent coordination-refresh PRs can continue independently.

## Change boundary

- MAY CHANGE: `work/tasks/agent-roadmap-guidance-upgrade.md`, `work/coordination/agents/ANVIL.md`, `work/coordination/agents/FOUNDRY.md`, `work/coordination/agents/SENTINEL.md`, `work/coordination/agents/SWITCHYARD.md`.
- MUST NOT CHANGE: runtime code, tests, schemas, roadmaps, policies, other tasks, active feature branches, PR ownership, merge state, or current volatile coordination facts except as necessary to preserve the fetched file while appending guidance.
- MAY CHANGE IF NECESSARY: none; new paths require task amendment first.
- OPERATOR APPROVAL REQUIRED: any change that alters agent authority, lane ownership, merge authority, review independence, or project scope beyond the requested roadmap guidance.

## Decision authority

- Owner may decide: wording, organization, and role-specific emphasis needed to faithfully apply the canonical roadmap method inside each existing agent role.
- Owner must escalate: any conflict that would require changing lane authority, modifying another agent's active branch, merging coordination PRs, or changing the canonical roadmap method itself.

## Acceptance criteria

- [x] All four active agent files point to the canonical roadmap playbook/template and summarize the roadmap lifecycle sufficiently to operate without inventing missing authority.
- [x] ANVIL and FOUNDRY guidance explains how implementation lanes challenge feasibility, execute only shaped first-wave tasks, surface unknowns, and trigger re-planning without silently expanding scope.
- [x] SENTINEL guidance explains independent roadmap challenge/review, exact-evidence checks, defect routing, and preservation of reviewer independence.
- [x] SWITCHYARD guidance explains dependency/integration sequencing, exact-head proof, checkpoint/re-plan triggers, and why roadmap state never substitutes for merge authority.
- [x] Existing active-lane/status content is otherwise preserved and the branch delta is documentation-only.

## Verification and evidence

- Verification: re-fetch every changed file from the branch; compare branch against its base and confirm only the declared Markdown paths changed; inspect the rendered guidance for canonical links, role boundaries, roadmap checkpoints, task-record gating, and explicit non-authority language.
- Evidence to preserve: branch compare, resulting commit/head SHA, and draft PR if connector support permits.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: GitHub Markdown documentation.
- Ordered procedure: inspect live rules and files -> create isolated branch/task -> append durable role guidance -> verify exact delta -> open draft PR for independent review.
- Failure branches: IF an agent file or `main` moves before a write THEN re-fetch that path/state and do not overwrite unseen changes; IF a concurrent coordination PR touches the same file THEN keep this change append-only and leave integration ordering to SWITCHYARD.
- Rollback / recovery: close the documentation PR or revert its documentation commits; no runtime state is affected.
- Security / privacy controls: N/A.
- External side effects: GitHub branch/commits and draft PR only.
- Effort limit: no redesign of the coordination system or roadmap standard; stop after all four files are upgraded and verified.
- Approved reference: `playbook/ROADMAP_AND_PROJECTUPDATER.md` and `templates/roadmap.md`.

## Stop / escalate

Stop rather than guess if:

- the canonical roadmap files conflict materially with `AGENTS.md`;
- an agent's live ownership changes in a way that makes the proposed guidance alter authority rather than explain it;
- completing the change would require taking over or modifying another agent's active feature branch.

Escalate to: operator for authority/scope changes; SWITCHYARD for later integration ordering only.

## AGI readiness

Before setting `Status: READY`, validate against
[the AGI standard](../../playbook/AGI_STANDARD.md).
Use [the AGI check template](../../templates/agi-check.md) when a durable check is useful.

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

A consequential task MUST NOT be marked `READY` unless every applicable
mandatory AGI requirement passes.

## Notes / decisions

- The operator explicitly requested upgrading all agent files. This permits the documentation-only cross-file change despite the coordination README's normal rule that each lane edits only its own note.
- Durable roadmap guidance was appended rather than mixed into volatile PR/head/status sections, minimizing contention with active coordination-refresh PRs.
- Pre-review compare against base `146f092a63af63b0fd750445e584a39e82ea1442` showed exactly the four agent notes plus this task record, with zero deletions and no runtime/test/schema/roadmap changes.
- SENTINEL wording uses "actively look for evidence that could disprove" rather than "falsify" so the instruction cannot be mistaken for altering or manufacturing false information.

## Completion / handoff

- Completed: canonical roadmap guidance appended to ANVIL, FOUNDRY, SENTINEL, and SWITCHYARD; documentation-only delta verified against the task base.
- Not completed: required independent review and integration to `main`.
- Current blocker: none; review is the next gate.
- Next action if not DONE: hand the exact branch head to an independent reviewer/SWITCHYARD without self-approving or merging.
