# Task: Agent Skills catalog and provenance read model

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: stack a deterministic multi-source Skill catalog/provenance read model on the verified format layer without inventing Skill approval, trust authority, routing, or persistence.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PR #25 / `agent/skills-format-wave2`, `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md` S3.
- Authoritative sources: Skill files/hashes and active repository instructions win; source metadata supplied to the catalog is descriptive provenance, not authority.
- Dependencies / preconditions: verified Skills-format implementation commit `0de3ac7535ba84b51a4b3d2a498473d4a0b8e384`; validation-record head `f2985f3dd510ee1679f19df45120afc316c15b6d`.

## Change boundary

- MAY CHANGE: `runtime/skills/catalog.py`, `runtime/skills/__init__.py`, focused catalog tests, this task file.
- MUST NOT CHANGE: Skill parser semantics unless a demonstrated catalog defect requires re-shaping, task/policy/review state, routing, Context Builder, Skill execution, durable approval/trust state, external systems.
- MAY CHANGE IF NECESSARY: none without re-shaping.
- OPERATOR APPROVAL REQUIRED: durable trust/approval storage, executable third-party behavior, autonomous routing/activation, or material scope expansion.

## Decision authority

- Owner may decide: immutable source/provenance types, deterministic catalog ordering/fingerprint, ambiguity representation, and exact lookup behavior.
- Owner must escalate: any design in which catalog discovery itself can mark a Skill approved/trusted, resolve ambiguous same-name Skills by guessing, or persist a second authority store.

## Acceptance criteria

- [x] multiple explicitly declared Skill roots can be combined into one deterministic read-only catalog.
- [x] each entry preserves source ID, source kind, source reference, optional declared revision, Skill directory ID/name, and exact content hash.
- [x] source metadata is clearly descriptive; the only v1 catalog trust state is `UNASSESSED`.
- [x] catalog construction does not load Skill procedure bodies.
- [x] catalog fingerprint is deterministic and independent of input-source order.
- [x] Skill content/provenance changes affect the catalog fingerprint.
- [x] duplicate source IDs are rejected.
- [x] same Skill name across different sources is retained as an explicit ambiguity/conflict rather than silently shadowed or merged.
- [x] unique lookup raises explicit NOT FOUND / AMBIGUOUS errors instead of guessing.
- [x] catalog activation uses the existing full-directory hash drift check.
- [x] no routing, trust promotion, approval, script execution, capability grant, or persistent database is added.
- [x] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: PR-triggered full Runtime stack CI run `31896101565` passed on implementation commit `cc30de70c170b2abaa61354ae775d8c9da2ec74d`.
- Evidence to preserve: GitHub Actions run `31896101565`, PR #26 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing MAPS Lean Python runtime.
- Ordered procedure: catalog/provenance read model → focused tests → stacked PR against PR #25 branch → CI → independent review.
- Failure branches: IF source trust needs to influence activation THEN stop; implement a reviewed trust/approval lifecycle first rather than treating catalog metadata as authority.
- Rollback / recovery: revert isolated stacked commit/PR; no schema/data migration.
- Security / privacy controls: no procedure body during catalog discovery, no execution, trust defaults to `UNASSESSED`, ambiguity is surfaced rather than auto-resolved.
- External side effects: Git branch/PR publication only.
- Effort limit: S3 derived catalog/provenance foundation only; no durable trust registry.
- Approved reference: Procedural Knowledge & Skills roadmap S3.

## Stop / escalate

Stop rather than guess if:

- the catalog would need to choose between ambiguous Skills automatically;
- a trust label would be interpreted as operator/task authorization;
- provenance requires unverifiable claims to be presented as verified facts.

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

- This task is stacked on PR #25; it may continue before review because the dependency is explicit and the implementation commit passed full Runtime stack CI.
- `declared_revision` is named deliberately: the catalog records what the configured source says, but does not independently prove a remote VCS revision.
- `SkillTrustState` contains only `UNASSESSED` in this tranche. Approval/trust lifecycle is separate future work.
- Same-name Skills across sources remain visible and ambiguous. The catalog never uses source ordering as hidden precedence.

## Completion / handoff

- Completed: multi-source Skills catalog/provenance read model, focused tests, draft PR #26, and full Runtime stack CI.
- Not completed: independent review / merge.
- Current blocker: independent review required for completion; next Skills work should remain evaluation-first rather than adding automatic routing.
- Next action if not DONE: independent review of PR #26; if continuing implementation, build the frozen Skill-selection evaluation corpus before any autonomous Skill routing.
