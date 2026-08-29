# Task: Pilot information-routing housekeeping

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: orchestration operator
- Risk: `MEDIUM`
- Goal: Reduce MAPS_L/Pilot navigation token cost by making the active documentation graph route a fresh or returning agent to the smallest relevant authority/method/evidence set without broad directory search or duplicated prose.
- Parent roadmap: operator-authorized housekeeping assignment in current conversation
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: `AGENTS.md`, `docs/FIRST_RUN.md`, `README.md`, `playbook/INDEX.md`, `playbook/INFORMATION_LIFECYCLE.md`, `tools/digital_fungus.py`, `obsidian/README.md`, `work/roadmaps/README.md`, key templates, live open PRs #173/#174/#178 as non-authoritative evidence.
- Authoritative sources: current accepted `main` + this task + direct operator instruction; live GitHub wins for current PR/branch facts.
- Evidence labels: current files/SHAs and PR state are `VERIFIED`; route-cost improvements remain `ASSUMED` until mechanically checked.
- Dependencies / preconditions: avoid runtime/feature paths owned by other active agents.

## Change boundary

- MAY CHANGE: documentation/navigation files, templates, documentation regression tests, read-only documentation-analysis tooling, this task record, and a housekeeping PR.
- MUST NOT CHANGE: runtime behavior, task-state schema, orchestration implementation, provider adapters, feature roadmaps' substantive capability claims, or another agent's branch.
- MAY CHANGE IF NECESSARY: small path/index files whose only job is routing existing content.
- HUMAN REAUTHORIZATION REQUIRED: none for this bounded housekeeping pass.

## Decision authority

- Inherited roadmap authority: reorganize/link/compact active documentation for token-efficient routing without changing project behavior or authority.
- Owner may decide: exact routing hubs, link shape, compact wording, route-cost metrics, and relationship fields.
- Resolve internally first: whether to add a link/index versus consolidate; whether a relationship is navigationally useful or merely graph density.
- Human escalation only if: the change would alter runtime capability, approved project authority, or substantive roadmap intent.

## Acceptance criteria

- [ ] Common entry path stays small: `AGENTS.md + approved roadmap/task + one relevant method`, with explicit direct routes rather than directory search.
- [ ] The always-read operating contract is materially smaller without losing authority, autonomy, review, safety, or anti-sprawl semantics.
- [ ] `work/` has one compact routing index explaining where each durable record class lives and when to read it.
- [ ] High-cost roadmap surfaces tell agents what question they answer and where to go instead when they are not the right source.
- [ ] Forward-relevant durable records have an explicit link-over-duplication / no-island convention owned by `INFORMATION_LIFECYCLE.md` and reflected minimally in templates.
- [ ] Navigation tooling/tests measure or guard route quality/token proxy instead of link count alone.
- [ ] No broad automatic semantic linking, graph database, duplicate mutable index, or runtime authority change is introduced.
- [ ] Required CI and independent review pass before merge.

## Verification and evidence

- Verification: documentation-sprawl tests; focused link/route tests; Digital Fungus analysis; inspect size/route deltas; normal repository CI.
- Evidence to preserve: PR description + exact before/after byte/route metrics.
- Review required: `INDEPENDENT_REVIEW`

## Stop / escalate

Continue through the bounded housekeeping and verification pass. Do not merge or self-certify independent review. Stop if a proposed change begins altering runtime behavior or substantive capability/authority semantics.
