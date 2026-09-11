# Task: protocol effectiveness benchmark

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: benchmark-spec owner
- Risk: `MEDIUM`
- Goal: Establish an independently reviewable, protocol-neutral specification for comparing MAPS_L with matched controls without MAPS-favoring grading, treatment contamination, benchmark leakage, or post-result analyst discretion.
- Parent roadmap: `none — PR #341 is the bounded specification work`
- Related records: [`../evals/protocol-effectiveness-benchmark/README.md`](../evals/protocol-effectiveness-benchmark/README.md); all PR #341 review records through [`../reviews/pr-341-rereview-evidence-fd2408f.md`](../reviews/pr-341-rereview-evidence-fd2408f.md)
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: repository `AGENTS.md`; package owners; independent review generations r1–r8, with r8 bound to `fd2408fda31d574554bf345cde6319fe8313bd90`.
- Authoritative sources: `AGENTS.md` for repository rules; this task for bounded work; each package owner file for its concept; immutable review records for reviewer findings.
- Evidence labels: r8 findings are VERIFIED reviewer findings; I2–I4 and all B/M/N/F/G/H owner-document findings remain independently resolved; J3 safeguard completion is an OWNER CLAIM pending focused fresh verification; J2/J4 are optional; benchmark effectiveness remains UNKNOWN because nothing has run.
- Dependencies / preconditions: fresh review of J3/v5 safeguard and bounded confirmation that accepted owner blobs remain unchanged before any corpus or holdout authoring.

## Change boundary

- MAY CHANGE: `work/evals/protocol-effectiveness-benchmark/**`; this task; PR #341 metadata; review/handoff evidence for this benchmark.
- MAY CHANGE FOR REQUIRED MECHANICAL SAFEGUARD: `scripts/check_protocol_effectiveness_benchmark_anchors.py`; benchmark-specific CI integration; append-only friction capture when tooling permits.
- MUST NOT CHANGE: MAPS_L runtime/protocol behavior, accepted normative owner semantics, benchmark corpus/holdout contents, model/evaluator execution, spending, `main`.
- HUMAN REAUTHORIZATION REQUIRED: benchmark/model/API spending; material scope expansion beyond specification/correction work; merge remains governed by repository rules.

## Decision authority

- Owner may make the bounded J3 safeguard correction required by independent review without changing normative benchmark-owner documents.
- J2/J4 remain optional and are not part of the gate.
- Human escalation only if execution/spend or material objective change is required.

## Acceptance criteria

- [x] Independent review evidence r1–r7 preserved separately.
- [x] r8 review at `fd2408fda31d574554bf345cde6319fe8313bd90` preserved separately: `MINOR CORRECTIONS REQUIRED`.
- [x] r8 independently verified I2–I4 and all B/M/N/F/G/H owner findings still resolved.
- [x] r8 independently verified the 512-state S4 enumeration: 0 ambiguous, 0 unhandled, 0 semantic mismatches.
- [x] J3 v5 safeguard pins normalized whole-document hashes for SPEC, CASE, RUN, SCORING, and REPORT using independently reviewed r7/r8 owner blobs.
- [x] J3 retains 13 localized structural pins and requires every pinned heading to occur exactly once.
- [x] J3 preserves the 49-ID/owner map, semantic-anchor checks, and direct report-vocabulary invariants.
- [x] r8 safeguard-gap recurrence captured in `work/coordination/FRICTION-PR341-REVIEW-REGRESSION.md` with v5 countermeasure.
- [x] No normative benchmark-owner file was edited in the J3 pass; no corpus/holdout authored.
- [ ] Fresh independent reviewer at the exact current head returns `APPROVED FOR CORPUS CONSTRUCTION`, confirms the v5 checker rejects r8 probe 9b plus out-of-span/duplicate-heading variants, and confirms the accepted owner blobs are unchanged.

## Verification and evidence

- Run `python scripts/check_protocol_effectiveness_benchmark_anchors.py`.
- Independently recompute the five normalized whole-owner hashes from the accepted `5f1ef8e`/`fd2408f` blobs.
- Repeat r8 probe 9b plus representative out-of-span, sibling-section, duplicate-heading, CASE §5, RUN, and generic-anchor substitutions; all normative-owner semantic mutations must fail.
- Confirm whitespace/CRLF-only normalization still remains green.
- Confirm I2–I4 and B/M/N/F/G/H carry forward only because the five owner blobs are unchanged.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: GitHub documentation branch for PR #341.
- Ordered procedure: preserve r8 → apply J3 only → upgrade invariant-13 safeguard/friction record → update task/PR → fresh independent J3 re-review.
- Failure branch: correct only an independently found gate-holding residual; do not reopen optional J2/J4.
- Rollback / recovery: branch/commit history.
- Security / privacy: no actual case secrets/holdout contents introduced.
- External side effects: GitHub branch/PR metadata and CI safeguard only.
- Effort limit: safeguard correction only; no benchmark execution/corpus construction.
- Approved reference: r8 review at `fd2408f...` for J3 scope.

## Notes / decisions

- Primary inference remains outcome-based and protocol-neutral.
- Accepted owner semantics are frozen by the v5 safeguard for this gate; deliberate future owner changes require checker update plus fresh review.
- Comparator S4s cannot rescue a tested-arm loss; stress/counterweight, leakage, Arm C, exposure, and verdict protections remain independently verified.
- J2/J4 were not changed because they are optional and not needed to open the corpus gate.

## Completion / handoff

- Completed: r8 evidence preserved; J3 whole-owner safeguard correction; friction carrier updated; v5 backstop installed.
- Not completed: fresh independent verification at current head; corpus construction; canonical `FRICTION_LOG.md` append.
- Current blocker: fresh focused independent J3 re-review.
- Next eligible roadmap task: bounded corpus construction only after `APPROVED FOR CORPUS CONSTRUCTION`.
- Human action required: none unless execution/spending is later requested.
