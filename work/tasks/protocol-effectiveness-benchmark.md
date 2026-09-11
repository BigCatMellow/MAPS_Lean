# Task: protocol effectiveness benchmark

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: benchmark-spec owner
- Risk: `MEDIUM`
- Goal: Establish an independently reviewable, protocol-neutral specification for comparing MAPS_L with matched controls without MAPS-favoring grading, treatment contamination, benchmark leakage, or post-result analyst discretion.
- Parent roadmap: `none — PR #341 is the bounded specification work`
- Related records: [`../evals/protocol-effectiveness-benchmark/README.md`](../evals/protocol-effectiveness-benchmark/README.md); [`../reviews/pr-341-review-evidence.md`](../reviews/pr-341-review-evidence.md); [`../reviews/pr-341-rereview-evidence-56c43aa.md`](../reviews/pr-341-rereview-evidence-56c43aa.md); [`../reviews/pr-341-rereview-evidence-dcc064b.md`](../reviews/pr-341-rereview-evidence-dcc064b.md); [`../reviews/pr-341-rereview-evidence-7ec7e1d.md`](../reviews/pr-341-rereview-evidence-7ec7e1d.md)
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: repository `AGENTS.md`; package owners; original review at `465d97300cf021840fb1fe0434656ff3772d1db4`; r2 at `56c43aa9c176a98b733c32cfb53b182b3c034b9f`; r3 at `dcc064bbc70648bded8f3e944d4f00c46b198fa5`; r4 at `7ec7e1d43e4252e3e6995cd83fc3ed6631a10e14`.
- Authoritative sources: `AGENTS.md` for repository rules; this task for bounded work; each package owner file for its concept; review records as immutable reviewer evidence.
- Evidence labels: review findings are VERIFIED as reviewer findings; G1–G10 correction completion is an OWNER CLAIM pending focused fresh independent verification; benchmark effectiveness remains UNKNOWN because nothing has run.
- Dependencies / preconditions: focused fresh independent re-review of G1–G10 plus the mechanical anchor check at the current corrected head before any corpus or holdout authoring.

## Change boundary

- MAY CHANGE: `work/evals/protocol-effectiveness-benchmark/**`; this task; PR #341 metadata; review/handoff evidence for this benchmark.
- MAY CHANGE FOR REQUIRED MECHANICAL SAFEGUARD: `scripts/check_protocol_effectiveness_benchmark_anchors.py`; the benchmark-specific step in `.github/workflows/review-evidence.yml`; append-only `work/coordination/FRICTION_LOG.md` entry required by AGENTS.md invariant 13.
- MUST NOT CHANGE: MAPS_L runtime/protocol behavior, existing frozen regression/end-to-end semantics, benchmark corpus/holdout contents, model/evaluator execution, spending, `main`.
- MAY CHANGE IF NECESSARY: documentation-only cross-links required to route this bounded work.
- HUMAN REAUTHORIZATION REQUIRED: benchmark/model/API spending; material scope expansion beyond specification/correction work; merge path remains governed by repository merge rules.

## Decision authority

- Inherited roadmap authority: user requested creation and correction of the benchmark information in MAPS_L.
- Owner may decide: bounded documentation corrections and the mechanical regression safeguard required to resolve independent review without changing runtime/protocol behavior.
- Resolve internally first: wording, ownership, experimental definitions, and regression pins.
- Human escalation only if: execution/spend or material objective change is required.

## Acceptance criteria

- [x] Original independent review evidence preserved: `MAJOR CORRECTIONS REQUIRED`.
- [x] B1–B3 and M1–M12 correction pass preserved without removing the reviewer-designated architecture.
- [x] Fresh re-review at `56c43aa...` preserved separately: `MINOR CORRECTIONS REQUIRED`.
- [x] N1–N10 second correction pass preserved.
- [x] Focused r3 re-review at `dcc064b...` preserved separately: `MINOR CORRECTIONS REQUIRED`.
- [x] F1–F9 third correction pass preserved.
- [x] Focused r4 re-review at `7ec7e1d...` preserved separately: `MINOR CORRECTIONS REQUIRED`; G1–G4 MATERIAL, G5–G10 MINOR; M2/N5/N7 regressions identified.
- [x] G1 Arm C independence/competence/context-cost disclosure restored and routed into the pre-corpus gate.
- [x] G2 independent overlay review now covers every NONE/STRESS/COUNTERWEIGHT label; seeded stress cannot hide as NONE.
- [x] G3 every model-reachable retrieval route, run-visible metadata boundary, process environment, and runner metadata are inside the leakage firewall.
- [x] G4 common task-facing COMPLETE/BLOCKED/INCOMPLETE definitions prevent treatment vocabulary from deciding terminal success.
- [x] G5 task-facing instruction precedence restored in the common bootstrap/fixture.
- [x] G6 S4 comparator-side clause, S3 crossing basis, and all-fields-execution-critical rule remove residual verdict discretion.
- [x] G7 Smoke evidence exposed to editors before Standard lock must be arm-masked; unmasked run-level material counts as per-arm exposure.
- [x] G8 operator-authored sampling requests must predate the benchmark package's first commit or come from a non-stakeholder.
- [x] G9 env/shell/global-VCS/runner state is inventoried and all non-chain caches reset.
- [x] G10 external cases record resolution date versus strongest documented model training cutoff; pre/within-cutoff and UNKNOWN cases are sensitivity strata.
- [x] Repeated fix-pass regression has a mechanical safeguard: `RESOLVED-FINDING-ANCHORS.json` + `scripts/check_protocol_effectiveness_benchmark_anchors.py` + CI step.
- [x] Status remains not executed; no corpus or holdout authored.
- [ ] Focused fresh independent reviewer at the current head returns `APPROVED FOR CORPUS CONSTRUCTION` and confirms the anchor check passes.

## Verification and evidence

- Verification: compare current owners against G1–G10 in `../reviews/pr-341-rereview-evidence-7ec7e1d.md`; run `python scripts/check_protocol_effectiveness_benchmark_anchors.py`; bounded regression check that B/M/N/F findings remain intact.
- Evidence to preserve: PR/head/diff; all review generations; anchor-manifest/check output; future approval evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: GitHub documentation branch for PR #341.
- Ordered procedure: preserve r4 review → apply targeted G1–G10 owner corrections → install mechanical anchor backstop and friction record → update PR/task status → focused independent re-review.
- Failure branches: if focused re-review finds a remaining validity defect, correct only that defect and repeat review before corpus work. Any future repeat regression extends the mechanical anchor set rather than relying on another prose reminder.
- Rollback / recovery: branch/commit history.
- Security / privacy controls: no actual case secrets/holdout contents introduced; future storage/isolation rules only.
- External side effects: GitHub branch/PR metadata and CI safeguard only.
- Effort limit: specification corrections/safeguard only; no benchmark execution/corpus construction.
- Approved reference: r4 review at `7ec7e1d...` for G1–G10 scope and invariant-13 safeguard requirement.
- Operational independence: `N/A — one-off specification correction; future benchmark execution will have its own reproducible package`.
- Reproduction package: package owners + immutable PR/review history + anchor manifest/check.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Primary inference uses only unexposed Standard + sealed holdout evidence for the protocol version under test.
- Treatment bundle is frozen before case authoring; run snapshots are history-free/sanitized and full execution environments undergo canary/resolution checks.
- Network/retrieval is deny-all by default across sandbox and provider-hosted routes; enabled tools are individually tested against answer leakage.
- The agent-visible case surface is explicit and excludes benchmark labels/provenance/answer-bearing metadata.
- Standard cases retire from later confirmatory inference after exposure to protocol modifiers.
- Smoke material available to benchmark editors is arm-masked; treatment-identifiable run-level Smoke material creates exposure.
- Human-response content has a mandatory neutral default; responder implementation may not turn check-ins into stalls.
- S4/tradeoff/verdict/H5 decisions are deterministic from frozen inputs/crossing bases.
- Every overlay class is independently reviewed; COUNTERWEIGHT prevalence requires audited named harm paths.
- Arm C is independently authored/approved, competent, frozen, and disclosed for instruction/context cost.
- Experiment P remains outcome-scored; MAPS runtime/E2E criteria remain outside its primary scorer.

## Completion / handoff

- Completed: G1–G10 targeted owner corrections prepared; r4 review preserved; mechanical regression safeguard installed.
- Not completed: focused fresh independent verification at current head; corpus construction.
- Triage capture: repeated fix-pass regression recorded in `work/coordination/FRICTION_LOG.md`; anchor safeguard is the countermeasure.
- Reproduction package: package owner files + PR/review history + `RESOLVED-FINDING-ANCHORS.json` + anchor-check script/CI step.
- Current blocker: focused fresh independent re-review.
- Next eligible roadmap task: corpus construction only after `APPROVED FOR CORPUS CONSTRUCTION`.
- Human action required: none unless execution/spending is later requested.
