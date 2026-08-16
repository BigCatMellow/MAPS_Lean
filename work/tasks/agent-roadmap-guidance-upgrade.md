# Task: Agent roadmap guidance upgrade

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: ATLAS / roadmap-guidance documentation lane
- Risk: `MEDIUM`
- Goal: active coordination agents contain durable, role-specific guidance for participating in MAPS roadmap creation, evidence-testing, execution, review, and integration, and ATLAS is established as the operator-facing request-shaping / roadmap-orchestration lane without taking over another agent's current work.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `playbook/INDEX.md`, `playbook/AGI_STANDARD.md`, `playbook/AGENT_GRADE_INSTRUCTIONS.md`, `playbook/ROADMAP_AND_PROJECTUPDATER.md`, `templates/roadmap.md`, `templates/task.md`, `work/coordination/README.md`, the current coordination-agent files, and live GitHub ownership/PR state.
- Authoritative sources: live GitHub state for repository/PR/branch status; operator statements for intent, priority, scope, and consequential approvals; `AGENTS.md` for repository operating rules; `playbook/AGI_STANDARD.md` / `playbook/AGENT_GRADE_INSTRUCTIONS.md` for execution-instruction quality; `playbook/ROADMAP_AND_PROJECTUPDATER.md` and `templates/roadmap.md` for roadmap method and structure.
- Evidence labels: repository files and live GitHub reads are `VERIFIED` at the inspected refs; coordination snapshots remain evidence only and may become stale; operator-requested role intent is `VERIFIED` from the current request.
- Dependencies / preconditions: preserve active lane ownership and avoid rewriting volatile PR/head/status blocks; do not take over FOUNDRY's current planning/control-surface work or PR #71; keep the change documentation-only.

## Change boundary

- MAY CHANGE: `work/tasks/agent-roadmap-guidance-upgrade.md`, `work/coordination/agents/ANVIL.md`, `work/coordination/agents/FOUNDRY.md`, `work/coordination/agents/SENTINEL.md`, `work/coordination/agents/SWITCHYARD.md`, `work/coordination/agents/ATLAS.md`, and PR #70 description/title metadata.
- MUST NOT CHANGE: runtime code, tests, schemas, canonical project roadmaps, policies, unrelated tasks, active feature branches, current PR ownership, review dispositions, merge state, or another agent's live technical-planning outputs.
- MAY CHANGE IF NECESSARY: none; new repository paths require task amendment first.
- OPERATOR APPROVAL REQUIRED: any change that alters agent authority, lane ownership, merge authority, review independence, project scope, or the canonical MAPS methods themselves.

## Decision authority

- Owner may decide: wording, organization, agent name, and role-specific emphasis needed to faithfully apply the canonical instruction/roadmap methods inside the operator-requested role while preserving existing lane boundaries.
- Owner must escalate: any conflict requiring changed operator intent, changed lane authority, takeover of another agent's branch/artifact, merge action, or modification of the canonical MAPS methods.

## Acceptance criteria

- [x] ANVIL and FOUNDRY guidance explains how their lanes evidence-test feasibility, execute only shaped first-wave tasks, surface unknowns, and trigger re-planning without silently expanding scope.
- [x] SENTINEL guidance explicitly defines independent roadmap evidence-testing as looking for source evidence that could show claims or assumptions are wrong, incomplete, or unsupported; it also covers exact-evidence checks, defect routing, and reviewer independence.
- [x] SWITCHYARD guidance explains dependency/integration sequencing, evidence-testing of parallelism and ordering assumptions, exact-head proof, checkpoint/re-plan triggers, and why roadmap state never substitutes for merge authority.
- [x] `work/coordination/agents/ATLAS.md` establishes a distinct operator-intake / roadmap-orchestration role with no feature, review, or merge authority by implication.
- [x] ATLAS defines a request-intake flow that preserves operator intent, inspects authoritative evidence first, labels uncertainty, resolves inspectable ambiguity before asking, and escalates only material decisions rather than guessing.
- [x] ATLAS defines an AGI-ready prompt construction protocol covering outcome, owner, sources/inputs, evidence status, dependencies, outputs/boundaries, decision authority, ordered procedure when needed, acceptance criteria, verification, review, failure branches, stop/escalate, and handoff state.
- [x] ATLAS defines a MAPS roadmap protocol covering current reality, observable DONE/final proof, boundaries/effort limit, backward conditions, research for unknown links, forward phases/dependencies/parallel work, mission-meeting evidence-testing, first-wave task records, checkpoints, and evidence-driven re-planning.
- [x] ATLAS explicitly preserves FOUNDRY's current planning/control-surface ownership (including PR #71), ANVIL implementation, SENTINEL independent review, and SWITCHYARD integration/merge control.
- [x] Existing active-lane/status content is otherwise preserved and the branch delta remains documentation-only.

## Verification and evidence

- Verification: re-fetch every changed file from the branch; compare branch against its base; inspect ATLAS and the four role contracts for canonical links, role boundaries, roadmap checkpoints, AGI task gating, explicit non-authority language, and unambiguous evidence-testing instructions; re-check live PR #68/#71/#70 state before final handoff.
- Evidence to preserve: branch compare, resulting exact head SHA, PR #70 metadata, and direct source reads used to establish the role boundary.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: GitHub Markdown documentation.
- Ordered procedure: inspect live rules/ownership -> amend the existing documentation task -> add ATLAS identity -> verify exact delta -> update PR #70 -> hand exact head to independent review.
- Failure branches: IF an agent file or `main` moves before a write THEN re-fetch that path/state and do not overwrite unseen changes; IF FOUNDRY or another agent claims operator-intake/roadmap ownership in live state THEN stop and reconcile the role boundary; IF a concurrent coordination PR touches the same existing file THEN keep this change non-destructive and leave integration ordering to SWITCHYARD.
- Rollback / recovery: close/revert the documentation PR or remove/revise the ATLAS coordination file; no runtime state is affected.
- Security / privacy controls: N/A.
- External side effects: GitHub branch/commits and draft PR metadata only.
- Effort limit: no redesign of the coordination system or MAPS instruction/roadmap standards; stop once the five agent roles and ATLAS intake/prompt/roadmap contract are documented and verified.
- Approved reference: `AGENTS.md`, `playbook/AGI_STANDARD.md`, `playbook/AGENT_GRADE_INSTRUCTIONS.md`, `playbook/ROADMAP_AND_PROJECTUPDATER.md`, `templates/task.md`, and `templates/roadmap.md`.

## Stop / escalate

Stop rather than guess if:

- canonical MAPS instruction/roadmap methods conflict materially with `AGENTS.md`;
- live ownership changes in a way that makes ATLAS duplicate or override another planning authority;
- completing the change would require taking over or modifying another agent's active feature/planning branch;
- a new role responsibility would imply implementation, independent-review, merge, external-action, or operator authority not explicitly granted.

Escalate to: operator for authority/scope changes; current lane owner for ownership conflicts; SWITCHYARD for later integration ordering only.

## AGI readiness

Before setting `Status: READY`, validate against [the AGI standard](../../playbook/AGI_STANDARD.md).
Use [the AGI check template](../../templates/agi-check.md) when a durable check is useful.

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

A consequential task MUST NOT be marked `READY` unless every applicable mandatory AGI requirement passes.

## Notes / decisions

- The operator explicitly requested a persistent roadmap-agent identity that takes operator requests, converts them into MAPS-compliant prompts, and builds roadmaps using MAP protocols.
- The role name selected is **ATLAS**, reflecting the roadmap/navigation function while remaining distinct from existing coordination identities.
- Live state showed PR #68 transitioning FOUNDRY to a Planning / Control-Surface lane and PR #71 as FOUNDRY-owned capability-roadmap reconciliation. ATLAS therefore owns the operator-facing intake/prompt/project-roadmap interface and explicitly does not take over #71 or incumbent technical planning.
- Durable roadmap guidance remains separate from volatile PR/head/status facts where practical.
- Evidence-testing wording is explicit throughout the added guidance: agents actively look for source evidence that could show a claim, assumption, dependency, proof, safety statement, or readiness statement is wrong, incomplete, or unsupported. They must not alter, invent, suppress, or manufacture contrary evidence, and a supported claim remains supported when the evidence withstands the check.

## Completion / handoff

- Completed: role-specific roadmap guidance for ANVIL, FOUNDRY, SENTINEL, and SWITCHYARD; ATLAS operator-intake / AGI-prompt / roadmap-orchestration identity and protocols added.
- Not completed: required independent review and integration to `main`.
- Current blocker: none known; exact-head verification and independent review are the next gates.
- Next action if not DONE: verify the exact branch delta and PR #70 head, then hand that exact head to an independent reviewer/SWITCHYARD without self-approving or merging.
