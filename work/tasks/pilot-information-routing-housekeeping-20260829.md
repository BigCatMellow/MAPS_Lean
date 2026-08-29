# Task: Pilot system housekeeping

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: orchestration operator
- Risk: `MEDIUM`
- Goal: Keep Pilot/MAPS_L cheap to navigate and independently operable: minimize documentation retrieval cost, preserve a repeatable routing-maintenance procedure, and prevent repeatable project outcomes from depending on the original AI/session for future operation or reconstruction.
- Parent roadmap: operator-authorized housekeeping assignment in current conversation
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: `AGENTS.md`, `docs/FIRST_RUN.md`, `README.md`, `playbook/INDEX.md`, `playbook/INFORMATION_LIFECYCLE.md`, `playbook/TASK_LIFECYCLE.md`, `tools/digital_fungus.py`, `obsidian/README.md`, `work/roadmaps/README.md`, key templates, and live GitHub state.
- Authoritative sources: current accepted `main` + this task + direct operator instruction; live GitHub wins for current PR/branch facts.
- Evidence labels: current files/SHAs, route-cost checks, completion-rule tests, and implementation CI are `VERIFIED`.
- Dependencies / preconditions: avoid runtime/feature paths owned by other active agents.

## Change boundary

- MAY CHANGE: documentation/navigation files, task/completion procedures, templates, documentation regression tests, read-only documentation-analysis tooling, this task record, and the housekeeping PR.
- MUST NOT CHANGE: runtime behavior, task-state schema, orchestration implementation, provider adapters, feature roadmaps' substantive capability claims, or another agent's branch.
- MAY CHANGE IF NECESSARY: small path/index files whose only job is routing existing content.
- HUMAN REAUTHORIZATION REQUIRED: none for this bounded housekeeping pass.

## Decision authority

- Inherited roadmap authority: reorganize/link/compact active documentation and improve completion hygiene without changing project behavior or authority.
- Owner may decide: routing hubs, compact wording, route-cost metrics, relationship fields, maintenance triggers, and the exact reproducibility/first-time-user completion checks for repeatable work.
- Resolve internally first: add/link/consolidate/retire decisions; whether a process is genuinely repeatable; whether automation is technically feasible/proportionate; whether maintenance produces measurable benefit before retaining churn.
- Human escalation only if: the change would alter runtime capability, approved project authority, substantive roadmap intent, or require a human-only product preference.

## Acceptance criteria

- [x] Common entry path stays small: `AGENTS.md + approved roadmap/task + one relevant method`, with explicit direct routes rather than directory search.
- [x] The always-read operating contract is materially smaller without losing authority, autonomy, review, safety, or anti-sprawl semantics.
- [x] `work/` has one compact routing index explaining where each durable record class lives and when to read it.
- [x] High-cost roadmap surfaces tell agents what question they answer and where to go instead when they are not the right source.
- [x] Forward-relevant durable records have an explicit link-over-duplication / no-island convention owned by `INFORMATION_LIFECYCLE.md` and reflected minimally in templates.
- [x] Navigation tooling/tests measure and guard route quality/token proxy instead of link count alone.
- [x] `INFORMATION_LIFECYCLE.md` owns a repeatable, trigger-based information-routing maintenance pass with baseline, consolidation/link/retirement, remeasurement, and stop criteria.
- [x] `AGENTS.md` points documentation-cost degradation to that procedure without duplicating it.
- [x] The maintenance procedure is discoverable from `playbook/INDEX.md` and does not preserve links to retired duplicate docs.
- [x] Repeatable operational work cannot reach parent success while the triggered Operational independence gate is unresolved.
- [x] `TASK_LIFECYCLE.md` requires solve/discover first when useful, then first-time-user instructions, reproducible code/script/formulas/query/config/template, portable configuration, provenance, and reproduction proof.
- [x] The reproducibility rule explicitly covers spreadsheet/Google Sheets-style workflows and avoids embedding secrets.
- [x] A justified `N/A` exists for genuinely one-off/creative work or technically unavailable/disproportionate automation; best-available manual reproduction remains required when useful.
- [x] `templates/task.md` records `Operational independence: REQUIRED | N/A — reason` and the reproduction-package path/proof.
- [x] Regression tests guard the global completion rule, procedure, and task-template fields.
- [x] No broad automatic semantic linking, graph database, duplicate mutable index, or runtime authority change is introduced.
- [x] Exact-head implementation CI passes.
- [ ] Independent review passes before merge.

## Verification and evidence

- `AGENTS.md`: original 13,554 bytes; compacted surface remains under its 10,000-byte guard after adding the completion-gate route.
- Root `README.md`: 7,151 → 3,511 bytes (~51% smaller).
- `docs/FIRST_RUN.md`: 2,267 bytes with direct routes to all five stable navigation hubs.
- `playbook/INDEX.md`: 8,516 → 6,759 bytes (~21% smaller) after the maintenance pass caught the hub approaching its route-cost budget.
- Route guards verify all five common hubs are exactly one hop from `FIRST_RUN` and stay below a 2,200-token planning proxy.
- `work/README.md` routes every top-level durable record class without requiring directory search.
- Large roadmap/checklist surfaces (~58 KB / ~36 KB) are behind a question router rather than normal orientation.
- Redundant `docs/WORKFLOW.md` and `docs/CONTEXT.md` were retired; the stale playbook-index reference was repaired.
- Digital Fungus distinguishes note edges, valid directory destinations, real broken links, and least-read-cost routes.
- Operational independence owner: `playbook/TASK_LIFECYCLE.md#operational-independence-gate`; global route: `AGENTS.md`; task capture: `templates/task.md`.
- Runtime stack run `33250738694` / run 986 passed on implementation head `4d449325246721718a22dc2f0d6b32dfd9cb54c7`, including full active tests, LangGraph smoke, lint, security analysis, dependency consistency, and installer preview.
- Final head changes only this task record to `READY_FOR_REVIEW`; normal CI reruns on it.
- Independent `review-evidence` remains intentionally pending/failing until a separate reviewer supplies evidence.

## Stop / escalate

Implementation housekeeping is complete and ready for independent review. No further change churn unless CI or independent review identifies a concrete defect. Do not merge or self-certify independent review.
