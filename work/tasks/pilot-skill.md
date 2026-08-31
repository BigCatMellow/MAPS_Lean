# Task: Pilot skill

- Status: `READY_FOR_REVIEW`
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

- MAY CHANGE: `.claude/skills/pilot/**`, directly related wiki/README onboarding references, documentation regression tests, this task record, PR description.
- MUST NOT CHANGE: runtime behavior, MAPS_L global authority rules, unrelated playbooks.
- MAY CHANGE IF NECESSARY: small install/discovery guidance required to make the skill portable.
- HUMAN REAUTHORIZATION REQUIRED: none for this bounded skill/onboarding addition.

## Decision authority

- Inherited roadmap authority: create a reusable MAPS_L skill with a natural command-style name.
- Owner may decide: final skill wording, trigger description, portability layout, focused regression guards, and related onboarding links.
- Resolve internally first: naming/trigger ambiguity, client-specific invocation differences, how much workflow belongs in the skill versus canonical MAPS_L sources.
- Human escalation only if: implementation would require redefining MAPS_L behavior rather than invoking it.

## Acceptance criteria

- [x] Skill uses the Agent Skills `SKILL.md` format with directory/name `pilot`.
- [x] `/pilot <project/task>` is a natural direct invocation in Claude Code; other compatible clients can install/use the same skill package.
- [x] Skill identifies the target project and preserves target-project authority before applying MAPS_L.
- [x] Skill retrieves/uses current canonical MAPS_L sources instead of embedding a second operating contract.
- [x] Skill chooses method-only, orchestrated, or runtime-backed depth proportionally.
- [x] Skill retains parent ownership after delegation, resolves in-scope questions internally first, reconciles returned work, and advances automatically until parent completion or a true boundary.
- [x] Skill does not install/enable the full control plane by default.
- [x] Regression tests guard the skill's thin-adapter role, discoverable Claude Code location, and command identity.
- [ ] Required CI/review gates pass before merge.

## Verification and evidence

- Verification: skill frontmatter uses only portable Agent Skills fields; project package is at Claude Code's documented `.claude/skills/pilot/SKILL.md` discovery path; documentation regression tests cover command identity, thin-adapter behavior, canonical-source routing, continuation, and absence of the old undiscoverable duplicate.
- Evidence to preserve: PR #178 diff; Runtime CI on final head; required independent review evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Stop / escalate

Implementation is complete. Continue through CI/review reconciliation; stop only at the repository's independent-review gate or a true authority boundary.

## Notes / decisions

- Command name: `pilot`. `/roadmap` was rejected as too planning-specific; `/map` is too collision-prone with literal maps/data structures.
- Canonical package location is `.claude/skills/pilot/`, not a second copy under `skills/`. Claude Code derives `/pilot` from the directory name; other clients can install/upload the same directory according to their skill mechanism.
- The wiki links to the skill but remains orientation; the skill links back to canonical MAPS_L sources and remains an invocation adapter.

## Completion / handoff

- Completed: skill package, direct `/pilot` interface, argument handling/fallback, portability guidance, wiki discovery link, anti-sprawl regression guards.
- Not completed: final CI result and required independent review/merge.
- Current blocker: repository independent-review gate after CI.
- Next eligible roadmap task: reconcile CI; then independent review.
- Human action required: none unless no independent reviewer is available through the repository process.
