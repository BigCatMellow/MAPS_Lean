# H06 — Policy, least privilege, and trustworthy boundaries

- **Record:** candidate success-condition branch, not a new task or authority source
- **Parent:** [Full MAPS_L goal map](../README.md) · **Dependencies:** [cross-branch graph](../DEPENDENCIES.md)
- **Coverage:** [45 checklist rows + 35 master capability areas](../COVERAGE.md)
- **Children stored separately:** [H06.3 — consequential actions](H06.3-consequential-actions.md)
- **Evidence checkpoint:** 2026-10-20, main `69879cd0375f687c1df753fb5a4b83dda76b562e`; current runtime and task evidence supersedes status prose

## Required outcome
Workers, helpers, imported instructions, tools, recovery, memory and automation can **never obtain or transfer authority by assertion**. Consequential side effects use explicit, inspectable, enforced permission boundaries.

## Recursive conditions
- **H06.1 — Stable trust taxonomy and threat model.** Untrusted content, observation, proposal, reviewed procedure, active guidance and canonical policy stay distinct. **Proof:** prompt injection and memory-poisoning cases remain contained.
- **H06.2 — Capability ∩ task policy ∩ operator consent.** Tool availability is not permission. **Proof:** unauthorized external/destructive action is blocked despite a technically available tool or persuasive agent text.
- **H06.3 — Guard actual consequential call sites.** [Open H06.3](H06.3-consequential-actions.md): before write, before external/destructive action, credentials, Skill/tool activation, guidance promotion and recovery. No code-only or prose-only guard proof.
- **H06.4 — Supply-chain lifecycle.** Provenance, inspection, capability declaration, quarantine, review and hash pinning of executable Skills/MCP/tools; no silent refresh. **Proof:** malicious changed Skill cannot activate without accepted trust decision.
- **H06.5 — Memory and operational learning cannot self-promote.** Candidate lesson remains non-authoritative until review; expiry/supersession and provenance survive retention.
- **H06.6 — Secrets/credential broker only when triggered.** Prefer ambient narrow permission controls until a real remote or cross-provider secret-handling case shows need; never capture secret values in specs or evidence.
- **H06.7 — Independence, privacy and failure containment.** Helpers may not approve themselves or another identity's claims by assertion; sensitive logs redacted; failures do not cascade through delegated agents.
- **H06.8 — Adversarial regression cases.** Every repeated safety escape earns an enforced, testable countermeasure; measure false-positive blocking as well as unsafe allowance.

## Evidence and unknowns
**SEC1/SEC2/SEC5/SEC7 DONE** in checklist; **SEC3/SEC4 IN PROGRESS**, **SEC6 NOT STARTED (triggered)**. The guard/hook primitives exist, but `BEFORE_EXTERNAL_ACTION` is not established as firing in every actual external path. [Security roadmap](../../agent-harness-capabilities/04-agentic-security.md) owns technical threat/controls, not this branch.

## First verification gate
Choose the real operations the approved workflow exercises; enumerate enforcement call sites and execute failure/denial tests. Do not mark the entire security roadmap blocked for unrelated hypothetical APIs, but do not call an actually exposed consequential path safe on the strength of class definitions alone.
