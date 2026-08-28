# Task: Pilot skill

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: orchestration operator
- Risk: `MEDIUM`
- Goal: Provide a thin, portable Agent Skills entrypoint named `pilot` that lets a capable agent apply MAPS_L to a target project through verified parent-scope completion without copying MAPS_L's operating contract into the skill.
- Parent roadmap: user-authorized MAPS_L onboarding/usability work in this conversation
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: current `AGENTS.md`, `docs/FIRST_RUN.md`, `playbook/INDEX.md`, audited wiki source, Agent Skills open format, current Claude Code skill invocation behavior.
- Authoritative sources: target-project instructions/approved scope for target authority; current MAPS_L repository sources for MAPS_L method; the skill is an invocation adapter only.
- Dependencies / preconditions: none.

## Change boundary

- MAY CHANGE: `skills/pilot/**`, directly related wiki/README onboarding references, documentation regression tests, this task record, PR description.
- MUST NOT CHANGE: runtime behavior, MAPS_L global authority rules, unrelated playbooks.
- MAY CHANGE IF NECESSARY: small install/discovery guidance required to make the skill portable.
- HUMAN REAUTHORIZATION REQUIRED: none for this bounded skill/onboarding addition.

## Decision authority

- Inherited roadmap authority: create a reusable MAPS_L skill with a natural command-style name.
- Owner may decide: final skill wording, trigger description, portability layout, focused regression guards, and related onboarding links.
- Resolve internally first: naming/trigger ambiguity, client-specific invocation differences, how much workflow belongs in the skill versus canonical MAPS_L sources.
- Human escalation only if: implementation would require redefining MAPS_L behavior rather than invoking it.

## Acceptance criteria

- [ ] Skill uses the Agent Skills `SKILL.md` format with directory/name `pilot`.
- [ ] `/pilot <project/task>` is a natural direct invocation in Claude Code; other compatible clients can discover/use the same skill package.
- [ ] Skill identifies the target project and preserves target-project authority before applying MAPS_L.
- [ ] Skill retrieves/uses current canonical MAPS_L sources instead of embedding a second operating contract.
- [ ] Skill chooses method-only, orchestrated, or runtime-backed depth proportionally.
- [ ] Skill retains parent ownership after delegation, resolves in-scope questions internally first, reconciles returned work, and advances automatically until parent completion or a true boundary.
- [ ] Skill does not install/enable the full control plane by default.
- [ ] Regression tests guard the skill's thin-adapter role and command identity.
- [ ] Required CI/review gates pass before merge.

## Verification and evidence

- Verification: inspect skill against current Agent Skills format; run documentation/runtime CI; fresh-agent/read-through test; independent review through existing PR gate.
- Review required: `INDEPENDENT_REVIEW`.

## Stop / escalate

Continue autonomously through implementation/test/reconciliation. Stop only for a true authority boundary or the repository's independent-review merge gate.
