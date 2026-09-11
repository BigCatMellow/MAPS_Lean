# Task: protocol effectiveness benchmark

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: benchmark-spec owner
- Risk: `MEDIUM`
- Goal: Establish an independently reviewable, protocol-neutral specification for comparing MAPS_L with matched controls without MAPS-favoring grading, treatment contamination, benchmark leakage, or post-result analyst discretion.
- Parent roadmap: `none — PR #341 is the bounded specification work`
- Related records: [`../evals/protocol-effectiveness-benchmark/README.md`](../evals/protocol-effectiveness-benchmark/README.md); all PR #341 review records through [`../reviews/pr-341-rereview-evidence-8b9efd9.md`](../reviews/pr-341-rereview-evidence-8b9efd9.md)
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: repository `AGENTS.md`; package owners; independent review generations r1–r6, with r6 bound to `8b9efd95f2cd48843f5eb38273a94eec55a49b58`.
- Authoritative sources: `AGENTS.md` for repository rules; this task for bounded work; each package owner file for its concept; immutable review records for reviewer findings.
- Evidence labels: r6 findings are VERIFIED reviewer findings; I1–I4 correction completion is an OWNER CLAIM pending focused fresh independent verification; benchmark effectiveness remains UNKNOWN because nothing has run.
- Dependencies / preconditions: fresh review of I1–I4, semantic-anchor mutation probes/S4 enumeration, and bounded B/M/N/F/G/H regression check before any corpus or holdout authoring.

## Change boundary

- MAY CHANGE: `work/evals/protocol-effectiveness-benchmark/**`; this task; PR #341 metadata; review/handoff evidence for this benchmark.
- MAY CHANGE FOR REQUIRED MECHANICAL SAFEGUARD: `scripts/check_protocol_effectiveness_benchmark_anchors.py`; benchmark-specific CI integration; append-only friction capture when tooling permits.
- MUST NOT CHANGE: MAPS_L runtime/protocol behavior, existing frozen regression/end-to-end semantics, benchmark corpus/holdout contents, model/evaluator execution, spending, `main`.
- HUMAN REAUTHORIZATION REQUIRED: benchmark/model/API spending; material scope expansion beyond specification/correction work; merge remains governed by repository rules.

## Decision authority

- Owner may make bounded documentation/safeguard corrections required by independent review without changing runtime/protocol behavior.
- Resolve internally first: wording, ownership, experimental definitions, report vocabulary, and regression pins.
- Human escalation only if execution/spend or material objective change is required.

## Acceptance criteria

- [x] Original independent review through r5 preserved separately.
- [x] r6 review at `8b9efd95f2cd48843f5eb38273a94eec55a49b58` preserved separately: `MINOR CORRECTIONS REQUIRED`.
- [x] r6 confirmed H1/H2/H5 resolved and no B/M/N/F/G regression.
- [x] I1 semantic safeguard strengthened: full known rule surfaces are pinned; checker independently enforces 49 expected IDs and minimum semantic-anchor counts on historically vulnerable findings.
- [x] I2 TRADEOFF overlap removed by excluding `PRIMARY_BETTER` from the tested-arm-S4 harm bullet.
- [x] I3 H5 support requires the matching aggregate verdict; H5 BETTER excludes tested-arm S4 rule firing or registered harm in either supporting stratum.
- [x] I4 report vocabulary uses only the five owner-defined verdicts; confirmatory state is separate; forbidden-effect BLOCKED is a FALSE_SUCCESS subset; `BLOCKED_WRONG_CLASS` is reported.
- [x] r6 safeguard-gap occurrence captured in `work/coordination/FRICTION-PR341-REVIEW-REGRESSION.md` with v3 countermeasure.
- [x] Status remains not executed; no corpus or holdout authored.
- [ ] Fresh independent reviewer at the exact current head returns `APPROVED FOR CORPUS CONSTRUCTION`, confirms the v3 checker/mutation probes and S4 enumeration, and finds no B/M/N/F/G/H regression.

## Verification and evidence

- Run `python scripts/check_protocol_effectiveness_benchmark_anchors.py`.
- Repeat the r6 semantic mutation probes, especially S4 rule 2/rule 3, §8/§9 precedence, SPEC/CASE seeded-stress rules, exact G3 run-visible block, H5 non-retroactivity, and report vocabulary.
- Repeat the S4 branch/enumeration check against accepted semantics.
- Compare current owners against I1–I4 in `../reviews/pr-341-rereview-evidence-8b9efd9.md`.
- Perform bounded regression check over B1–B3, M1–M12, N1–N10, F1–F9, G1–G10, H1–H5.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: GitHub documentation branch for PR #341.
- Ordered procedure: preserve r6 → apply I1–I4 only → strengthen semantic safeguard/friction record → update task/PR → fresh independent re-review.
- Failure branch: correct only any independently found residual before corpus work; repeated semantic-regression classes extend machinery rather than prose reminders.
- Rollback / recovery: branch/commit history.
- Security / privacy: no actual case secrets/holdout contents introduced.
- External side effects: GitHub branch/PR metadata and CI safeguard only.
- Effort limit: specification corrections/safeguard only; no benchmark execution/corpus construction.
- Approved reference: r6 review at `8b9efd9...` for I1–I4 scope.

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
- The v3 invariant-13 safeguard now treats exact semantic clauses, not section headings, as the mechanically protected surface.
- Experiment P remains separate from MAPS runtime/E2E process grading.

## Completion / handoff

- Completed: I1–I4 targeted corrections; r6 evidence preserved; semantic safeguard upgraded to v3; friction carrier updated.
- Not completed: fresh independent verification at current head; corpus construction; canonical `FRICTION_LOG.md` append.
- Canonical friction-log append is administrative housekeeping; the temporary carrier does not claim to replace the append-only log.
- Current blocker: fresh focused independent re-review.
- Next eligible roadmap task: bounded corpus construction only after `APPROVED FOR CORPUS CONSTRUCTION`.
- Human action required: none unless execution/spending is later requested.
