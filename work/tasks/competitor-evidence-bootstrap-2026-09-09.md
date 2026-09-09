# Task: Competitor evidence bootstrap into MAPS_L research

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `RESEARCH`
- Owner: ChatGPT
- Risk: `LOW`
- Goal: integrate the highest-value competitor-system evidence already collected in Pilot into MAPS_L's existing research topic owners without changing runtime behavior, capability status, current implementation plans, or authority.
- Parent roadmap: `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` — research supports the existing six capability roadmaps; it does not replace them.
- Related records: `work/research/README.md`, PR #322 roadmap reconciliation, Pilot_Projects PR #5 borrow-before-build corpus.
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs:
  - current MAPS_L `main` and `AGENTS.md`;
  - current open PR surface (#319, #320, #321, #322);
  - current `work/research/` router and topic records;
  - Pilot_Projects PR #5 at `f6d584465e15b0fcf3cd09fea9e056bc23852e94`;
  - exact upstream source/test/fix-history anchors preserved in that Pilot corpus.
- Authoritative sources: MAPS_L `AGENTS.md`, approved roadmap/task authority, current code/tests/GitHub, and existing MAPS_L roadmap owners. External systems and Pilot research are evidence only.
- Evidence labels: upstream implementation/test/fix evidence = `VERIFIED` where pinned in Pilot source index/fix history; MAPS_L implications = `INTERPRETATION / CANDIDATE` until reviewed/adopted.
- Dependencies / preconditions: none; this tranche is intentionally non-overlapping with current runtime/wiki/Emergence/reconciliation implementation PRs.

## Change boundary

- MAY CHANGE:
  - `work/research/README.md`;
  - new dated research records under the four existing `work/research/` topic folders;
  - this task record.
- MUST NOT CHANGE:
  - runtime, schemas, capability checklist/status, roadmap implementation status;
  - `AGENTS.md`, `playbook/EMERGENCE.md`, PR #319 files;
  - PR #320 6.4 exercise evidence/status files;
  - `docs/wiki/` / PR #321 files;
  - `playbook/PROGRAM_STEERING.md` / PR #322 files;
  - merge authority, provider choices, SQLite/LangGraph architecture.
- MAY CHANGE IF NECESSARY: direct research routing links needed to make this tranche discoverable.
- HUMAN REAUTHORIZATION REQUIRED: dependency adoption, runtime implementation, capability-status change, authority expansion, paid-resource behavior, or modification of another active agent's PR surface.

## Decision authority

- Inherited roadmap authority: research and roadmap evidence can be gathered and routed without promoting it into implementation.
- Owner may decide: evidence organization, deduplication, exact source links, candidate regression-test mapping, and which existing MAPS_L topic owns each finding.
- Resolve internally first: whether a finding is genuinely new versus already represented by existing MAPS_L design.
- Human escalation only if: research implies a material roadmap/objective/authority change rather than merely stronger evidence or tests.

## Acceptance criteria

- [x] Current open PRs checked; no changed-file overlap with the research-only tranche.
- [x] Competitor findings routed into the existing four MAPS_L research topics rather than a new taxonomy.
- [x] Each note distinguishes upstream evidence from MAPS_L interpretation and explicitly forbids automatic adoption.
- [x] Exact immutable Pilot evidence snapshot is linked so future agents can drill into source/test/fix history without chat.
- [x] Portable failure/regression cases are called out where they strengthen existing MAPS_L mechanisms.
- [x] No runtime, status, wiki, Emergence, or active implementation files are modified.

## Verification and evidence

- Verification: compare branch against `main`; inspect changed-file set; verify links and topic routing; independent review required before merge.
- Evidence to preserve: PR diff, immutable Pilot snapshot link, changed-file list, CI/review status.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: GitHub repository records only.
- Ordered procedure: recover live PR collision surface → route each finding to one existing research topic → preserve exact evidence links → compare diff → independent review.
- Failure branches: if an active PR begins touching one of these research files, stop/rebase that file rather than create competing edits.
- Rollback / recovery: branch/PR can be closed without changing runtime or canonical status.
- Security / privacy controls: no secrets or private user data; source links point to repositories already available to the project owner.
- External side effects: GitHub branch/PR only; no runtime/provider action.
- Effort limit: bounded evidence integration; no new system survey.
- Approved reference: Pilot_Projects PR #5 at pinned head.
- Operational independence: `N/A — one-time research integration tranche`
- Reproduction package: exact source links and routing notes in the four research records.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- The purpose is to make competitor lessons available to MAPS_L now without forcing any implementation to wait on or depend on this research.
- Evidence that merely reinforces an existing MAPS_L mechanism is recorded as a strengthening input, not as a replacement proposal.

## Completion / handoff

- Completed: research tranche prepared on a separate branch; no active PR collision by path at task start.
- Not completed: independent review / merge.
- Triage capture: `none — no §2 trigger fired`
- Reproduction package: four dated research notes + immutable Pilot source snapshot.
- Current blocker: independent review only.
- Next eligible roadmap task: unchanged; current live MAPS_L sequencing remains owned by roadmap/current GitHub state.
- Human action required: none for research merge; any later dependency/runtime adoption remains a separate decision.