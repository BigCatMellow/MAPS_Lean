# Task: Agent Skills format foundation

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: implement the first independent Wave 2 Agent Skills format layer: safe directory discovery, minimum standard frontmatter metadata, stable whole-Skill content identity, resource inventory, and explicit progressive activation without routing, execution, or new authority.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md`, merged `main` baseline.
- Authoritative sources: active repository instructions and current code win; the roadmap provides planning intent only.
- Dependencies / preconditions: none from the draft Harness stack; this branch starts from merged `main` commit `086e066f723d793273441dd52b500e62ac981deb`.

## Change boundary

- MAY CHANGE: new `runtime/skills/**`, focused Skills-format tests, this task file.
- MUST NOT CHANGE: `AGENTS.md` authority, task/policy/review state, Harness behavior, Context Builder routing, provider/tool execution, third-party approval/quarantine state, external systems.
- MAY CHANGE IF NECESSARY: none without re-shaping.
- OPERATOR APPROVAL REQUIRED: executable third-party Skill behavior, network/tool activation, new durable trust/approval state, or material scope expansion.

## Decision authority

- Owner may decide: narrow parser behavior for required discovery metadata, directory hash representation, resource inventory representation, fail-closed change detection, and focused test design consistent with the roadmap.
- Owner must escalate: any need to execute scripts, treat Skill metadata as policy, autonomously route/activate Skills, add a persistent trust database, or pull in a broad dependency merely for speculative metadata fields.

## Acceptance criteria

- [ ] immediate child directories containing `SKILL.md` can be discovered deterministically.
- [ ] `SKILL.md` requires frontmatter with non-empty `name` and `description`.
- [ ] common scalar quoting and block-scalar descriptions are supported without introducing a new YAML dependency solely for v1 discovery.
- [ ] unrelated/nested custom metadata is tolerated but not interpreted as authority or executable state.
- [ ] discovery returns compact descriptors without loading the procedure body through the activation path.
- [ ] every descriptor contains a deterministic SHA-256 identity over all regular files in the Skill directory.
- [ ] scripts/references/assets/examples and other resources are inventoried but never executed by this layer.
- [ ] symlinked Skill roots/resources are rejected in v1 to prevent path/provenance ambiguity.
- [ ] duplicate Skill names are rejected within one catalog root.
- [ ] `load_skill()` rechecks the complete content hash and refuses activation after drift until rediscovery.
- [ ] no routing, Skill approval, trust promotion, capability grant, or task authority is added.
- [ ] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: `python -m unittest tests.test_skills_format -v` plus full PR-triggered Runtime stack CI.
- Evidence to preserve: PR diff, GitHub Actions run, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing MAPS Lean Python runtime and standard library.
- Ordered procedure: format/discovery implementation → focused tests → draft PR against `main` → full CI → independent review.
- Failure branches: IF general YAML semantics become necessary for real compatible Skills THEN evaluate a maintained parser dependency as a separate evidence-backed change; do not silently grow a homegrown YAML implementation.
- Rollback / recovery: revert isolated commit/PR; no schema/data migration.
- Security / privacy controls: no execution during discovery; symlinks rejected; hashes cover complete regular-file contents; metadata beyond required discovery fields is descriptive only.
- External side effects: Git branch/PR publication only.
- Effort limit: S2 format support foundation only; no S3 durable provenance/trust registry or S4 routing evaluation.
- Approved reference: Procedural Knowledge & Skills roadmap S2.

## Stop / escalate

Stop rather than guess if:

- compatibility requires YAML features substantially beyond required discovery metadata;
- imported Skill content needs executable trust decisions;
- a requested feature would make Skill metadata override canonical task/policy authority.

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

- This first Skills tranche is intentionally independent of PRs #20–#24 and targets `main`.
- No new YAML dependency is introduced merely to extract `name` and `description`; v1 supports the common scalar/block forms needed for discovery and ignores unneeded nested metadata.
- If broader Agent Skills compatibility later proves that a real YAML parser is necessary, that should replace/extend this narrow parser deliberately rather than accreting ad hoc YAML semantics.
- Whole-directory hashing includes `SKILL.md` and every regular resource file, so executable/reference/resource changes invalidate prior discovery identity.
- Progressive disclosure is represented by separate descriptor discovery and explicit `load_skill()` activation; discovery objects contain no procedure body.

## Completion / handoff

- Completed: implementation and focused tests prepared for commit on `agent/skills-format-wave2`.
- Not completed: commit/PR/CI/review.
- Current blocker: none.
- Next action if not DONE: commit the tranche, open a draft PR against `main`, and run full Runtime stack CI.
