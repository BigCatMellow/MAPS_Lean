# Task: Pilot information-routing housekeeping

- Status: `READY_FOR_REVIEW`
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
- Evidence labels: current files/SHAs, route-cost checks, and CI results are `VERIFIED`.
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

- [x] Common entry path stays small: `AGENTS.md + approved roadmap/task + one relevant method`, with explicit direct routes rather than directory search.
- [x] The always-read operating contract is materially smaller without losing authority, autonomy, review, safety, or anti-sprawl semantics.
- [x] `work/` has one compact routing index explaining where each durable record class lives and when to read it.
- [x] High-cost roadmap surfaces tell agents what question they answer and where to go instead when they are not the right source.
- [x] Forward-relevant durable records have an explicit link-over-duplication / no-island convention owned by `INFORMATION_LIFECYCLE.md` and reflected minimally in templates.
- [x] Navigation tooling/tests measure and guard route quality/token proxy instead of link count alone.
- [x] No broad automatic semantic linking, graph database, duplicate mutable index, or runtime authority change is introduced.
- [x] Required implementation CI passes.
- [ ] Independent review passes before merge.

## Verification and evidence

- `AGENTS.md`: 13,554 → 9,410 bytes (~31% smaller).
- Root `README.md`: 7,151 → 3,511 bytes (~51% smaller).
- `docs/FIRST_RUN.md`: 2,267 bytes with direct routes to all five stable navigation hubs.
- Route guards verify all five common hubs are exactly one hop from `FIRST_RUN` and stay below a 2,200-token planning proxy.
- `work/README.md` routes every top-level durable record class without requiring directory search.
- Large roadmap/checklist surfaces (~58 KB / ~36 KB) are now behind a question router rather than normal orientation.
- Redundant `docs/WORKFLOW.md` and `docs/CONTEXT.md` were retired instead of preserving duplicate islands.
- Digital Fungus now distinguishes note edges, valid directory destinations, real broken links, and least-read-cost routes.
- Runtime stack tests run `33246742451` / run 968 passed on implementation head `0bfefc37604069e0c566cdf77245e19235663a17`, including full active tests, LangGraph smoke, lint, security, dependency consistency, and installer preview.
- Independent `review-evidence` remains intentionally pending/failing until a separate reviewer supplies evidence.

## Stop / escalate

Implementation housekeeping is complete. No further change churn unless CI or independent review identifies a concrete defect. Do not merge or self-certify independent review.
