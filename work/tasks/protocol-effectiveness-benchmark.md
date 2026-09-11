# Task: protocol effectiveness benchmark

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: benchmark-spec owner
- Risk: `MEDIUM`
- Goal: Establish an independently reviewable, protocol-neutral specification for comparing MAPS_L with matched controls without MAPS-favoring grading, treatment contamination, benchmark leakage, or post-result analyst discretion.
- Parent roadmap: `none — PR #341 is the bounded specification work`
- Related records: [`../evals/protocol-effectiveness-benchmark/README.md`](../evals/protocol-effectiveness-benchmark/README.md); all PR #341 review records through [`../reviews/pr-341-rereview-evidence-5f1ef8e.md`](../reviews/pr-341-rereview-evidence-5f1ef8e.md)
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: repository `AGENTS.md`; package owners; independent review generations r1–r7, with r7 bound to `5f1ef8e090b62c8393113ddb211399646d381c84`.
- Authoritative sources: `AGENTS.md` for repository rules; this task for bounded work; each package owner file for its concept; immutable review records for reviewer findings.
- Evidence labels: r7 findings are VERIFIED reviewer findings; I2–I4 and B/M/N/F/G/H owner-document status are independently verified at r7; J1 correction completion is an OWNER CLAIM pending focused fresh independent verification; J2 is optional/NIT; benchmark effectiveness remains UNKNOWN because nothing has run.
- Dependencies / preconditions: fresh review of J1/v4 safeguard, r7 mutation probes, 512-state S4 enumeration, and bounded B/M/N/F/G/H regression check before any corpus or holdout authoring.

## Change boundary

- MAY CHANGE: `work/evals/protocol-effectiveness-benchmark/**`; this task; PR #341 metadata; review/handoff evidence for this benchmark.
- MAY CHANGE FOR REQUIRED MECHANICAL SAFEGUARD: `scripts/check_protocol_effectiveness_benchmark_anchors.py`; benchmark-specific CI integration; append-only friction capture when tooling permits.
- MUST NOT CHANGE: MAPS_L runtime/protocol behavior, existing frozen regression/end-to-end semantics, benchmark corpus/holdout contents, model/evaluator execution, spending, `main`.
- HUMAN REAUTHORIZATION REQUIRED: benchmark/model/API spending; material scope expansion beyond specification/correction work; merge remains governed by repository rules.

## Decision authority

- Owner may make bounded documentation/safeguard corrections required by independent review without changing runtime/protocol behavior.
- Resolve internally first: wording, ownership, experimental definitions, report vocabulary, and regression machinery.
- Human escalation only if execution/spend or material objective change is required.

## Acceptance criteria

- [x] Independent review evidence r1–r6 preserved separately.
- [x] r7 review at `5f1ef8e090b62c8393113ddb211399646d381c84` preserved separately: `MINOR CORRECTIONS REQUIRED`.
- [x] r7 independently verified I2–I4 resolved and no B/M/N/F/G/H owner-document regression.
- [x] r7 identified J1 as the only gate-holding residual; J2 is optional/NIT and intentionally left unchanged.
- [x] J1 v4 safeguard hard-codes all 49 finding IDs and exact owner paths independently of the manifest.
- [x] J1 rejects duplicate/trivial anchors and applies minimum unique-anchor counts to historically vulnerable findings.
- [x] J1 structurally pins 13 independently accepted rule sections across SCORING, CASE, SPEC, and REPORT so additive semantic exceptions cannot pass merely by retaining old sentences.
- [x] J1 restores the exact comparator no-shield protection and directly checks report five-verdict vocabulary / forbidden added labels / `BLOCKED_WRONG_CLASS`.
- [x] r7 safeguard-gap occurrence captured in `work/coordination/FRICTION-PR341-REVIEW-REGRESSION.md` with v4 countermeasure.
- [x] Status remains not executed; no corpus or holdout authored.
- [ ] Fresh independent reviewer at the exact current head returns `APPROVED FOR CORPUS CONSTRUCTION`, confirms the v4 checker/mutation probes and 512-state S4 enumeration, and finds no B/M/N/F/G/H regression.

## Verification and evidence

- Run `python scripts/check_protocol_effectiveness_benchmark_anchors.py`.
- Repeat r7 probes 1–9, especially 2b and 8a–8c, plus additive semantic-exception variants against structurally pinned sections.
- Repeat the 512-state S4 branch/enumeration check against accepted semantics.
- Confirm I2–I4 remain resolved without owner-document edits in the J1 pass.
- Perform bounded regression check over B1–B3, M1–M12, N1–N10, F1–F9, G1–G10, H1–H5.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: GitHub documentation branch for PR #341.
- Ordered procedure: preserve r7 → apply J1 only → upgrade invariant-13 safeguard/friction record → update task/PR → fresh independent J1 re-review.
- Failure branch: correct only any independently found gate-holding residual before corpus work; repeated semantic-regression classes extend structural machinery rather than prose reminders.
- Rollback / recovery: branch/commit history.
- Security / privacy: no actual case secrets/holdout contents introduced.
- External side effects: GitHub branch/PR metadata and CI safeguard only.
- Effort limit: specification safeguard correction only; no benchmark execution/corpus construction.
- Approved reference: r7 review at `5f1ef8e...` for J1 scope.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Primary inference remains outcome-based and protocol-neutral.
- Comparator S4s cannot rescue a tested-arm loss; tested-arm S4 restrictions remain conservative.
- Seeded MAPS-favored stress cannot escape the STRESS ceiling through efficiency/burden-only counterweight paths.
- Arm C remains the independently authored/approved generic structured comparator for MAPS-specific B−C claims.
- The v4 invariant-13 safeguard combines human-reviewable anchors with checker-owned owner mapping, structural section hashes, and direct report-vocabulary validation.
- J2 was not changed because it is optional and not needed to open the corpus gate.
- Experiment P remains separate from MAPS runtime/E2E process grading.

## Completion / handoff

- Completed: r7 evidence preserved; J1 targeted safeguard correction; friction carrier updated; v4 structural backstop installed.
- Not completed: fresh independent verification at current head; corpus construction; canonical `FRICTION_LOG.md` append.
- Canonical friction-log append is administrative housekeeping; the temporary carrier does not claim to replace the append-only log.
- Current blocker: fresh focused independent J1 re-review.
- Next eligible roadmap task: bounded corpus construction only after `APPROVED FOR CORPUS CONSTRUCTION`.
- Human action required: none unless execution/spending is later requested.
