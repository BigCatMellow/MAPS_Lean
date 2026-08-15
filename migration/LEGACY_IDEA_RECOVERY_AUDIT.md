# Legacy Idea Recovery Audit

Status: `AUDIT CHECKPOINT — NOT ACTIVE AUTHORITY`

Date: 2026-08-15

Purpose: record exactly what has and has not been screened while mining the legacy MAP System for useful mechanisms, abandoned work, unpromoted lessons, and ideas that should inform MAPS Lean. This file exists so a later session does not have to infer audit coverage from chat history.

This is an audit checkpoint, not a roadmap. Candidate implementation still belongs in `FUTURE_IDEAS_BACKLOG.md` and must be checked against current Lean behavior before promotion.

---

## Governing rule

Preserve useful invariants, evidence, experiments, and implementation lessons. Do not revive an old subsystem merely because it existed.

For each historical item ask:

1. What problem did it actually observe?
2. Was the evidence credible?
3. Was it implemented, abandoned, superseded, or only proposed?
4. Does Lean already solve the underlying problem?
5. If not, what is the smallest Lean-native behavior worth preserving?

---

# Coverage checkpoint

## Legacy Emergence corpus

The following collections under `legacy/MAP-System/MAP_System/emergence/` have now been inventoried:

| Collection | Coverage at this checkpoint | Notes |
|---|---|---|
| `ideas/` | Complete filename inventory; selected MAP-system records deep-read | Dedicated IDEA records through IDEA-0034 were screened; high-value and ambiguous chains were followed into tasks/experiments/current Lean. |
| `experiments/` | Complete inventory EXP-0001 through EXP-0010; major MAP experiments deep-read | Especially orientation/context, discovery, claim/evidence, self-review, submission authorship, and state-drift experiments. |
| `insights/` | Complete filename inventory through INS-0061; MAP-relevant records screened by title/status; high-value records deep-read | Project-specific lessons were not automatically promoted into MAPS candidates. |
| `synthesis/` | Complete inventory SYN-0001 through SYN-0005; major records deep-read | These often contain the most useful cross-system lesson rather than a concrete feature request. |
| `promotions/` | Complete inventory PROMO-0001 through PROMO-0018; relevant/ambiguous promotions deep-read | Used to distinguish genuinely adopted work from half-finished or internally inconsistent promotion records. |
| `candidates/` | Complete filename inventory; representative accepted/dismissed candidates deep-read | This is a temporary scanner queue, not durable idea authority. Accepted items should resolve into normal Insight/Idea records. |
| `coverage.json` | Read | Historical coverage itself was sparse, so absence of a review mark cannot be treated as rejection. |
| Emergence methods/index/docs | Inventoried; selectively read | Useful for understanding record semantics and promotion rules, not treated as feature candidates by default. |

## Legacy task corpus

Selected historical task chains have been deep-read where they explain whether an idea was implemented, retired, or left unfinished. Examples include review claiming, redaction, RnS terminal-session handling, submission authorship, shared-state validation, and process-adherence work.

This is **not yet a line-by-line audit of every legacy task or every project-specific artifact**. Later passes should prioritize records that are referenced by unresolved Insights/Ideas, marked RETIRED/PARKED/PROPOSED, or describe a MAP-system failure not represented in the Lean backlog.

## Other legacy material

The audit has also used referenced legacy artifacts, reviews, planning records, and research where a task/Idea/Insight pointed to them. It has **not** yet exhaustively read every file under all legacy artifact, notes, planning, research, archive, or project directories.

That distinction is intentional: this checkpoint means “the major Emergence idea-bearing collections have been inventoried and screened,” not “every byte of `legacy/` has been reviewed.”

---

# Recovered mechanisms and lessons

The following are either already in `FUTURE_IDEAS_BACKLOG.md` or should be considered during its next consolidation pass.

## 1. Telemetry/event secret-safety boundary

Legacy redaction work intentionally left at least one event-appender surface outside the first guard and parked a follow-up rather than rejecting it.

Lean translation: before adding richer replay/outcome/trace telemetry, enumerate durable write surfaces and define how sensitive material is handled without silently destroying audit evidence.

Disposition: `P1 candidate / audit first`.

## 2. Three-layer evaluation discipline

Preserve separate evaluation layers:

1. deterministic/mechanical control regression;
2. qualitative agent/review/context quality regression;
3. sampled real production traces and outcomes.

Use recurring production incidents to create frozen regression cases. Maintain a small incident taxonomy rather than relying on anecdotes.

Disposition: fold into Outcome Feedback / Eval Corpus and Controlled Harness Evaluation.

## 3. Operational-learning promotion with expiry/supersession

Historical records identified a real gap: useful operational notes could be durable yet never be presented to a future applicable agent.

The old operational-learning idea reached a promotion record, but that promotion record is internally inconsistent: it is labeled approved while its approval block and target fields remain incomplete. Treat it as unfinished historical work, not as a completed adoption.

Lean already preserves the principle in `REPAIR_AND_LEARNING.md`; the still-interesting future mechanism is selective promotion into startup/task context with provenance, applicability, expiry, and supersession.

Disposition: `P1 preserved candidate`; do not create an unlimited memory subsystem.

## 4. Context packets can be dramatically smaller, but proof must be frozen and end-to-end

EXP-0004 first showed a compact orientation packet could retain most required facts but missed the immediate read-before-mutate boundary, so the result was REVISE.

EXP-0005 corrected the method with a frozen rubric/control and blinded evaluation. In that one scenario the compact treatment passed all six rubric rows and measured 2,619 bytes versus a retained 44,432-byte control (94.11% smaller). The experiment was still parked because one scenario does not justify changing production startup behavior.

Preserved lesson:

- context reduction can be large;
- authority/safety facts may not be sacrificed for compression;
- freeze evaluation criteria and the control before treatment;
- measure end-to-end behavior, not byte reduction alone.

Disposition: strengthens the P1 Context Builder and evaluation plan.

## 5. Exact evidence anchors are promising as evidence discipline, not validated as the old retrieval algorithm

Important correction to avoid future historical overclaim:

EXP-0006 did **not** validate the legacy claim-card retriever. Its scored treatment reported:

- task recall: 12/23;
- exact-source accuracy: 17/41;
- anchored-evidence accuracy: 7/41;
- negative abstention: 2/5 correct, with 3 false positives;
- historical-version correctness: 2/3;
- decision: `REVISE`.

What remains worth preserving:

- exact section/code-symbol anchors;
- source hashes and explicit source-drift reporting;
- temporal/historical attribution;
- proof role;
- positive evidence separated from negative boundaries;
- frozen holdouts and independent/blinded evaluation.

Do **not** cite the legacy lexical claim-card implementation as proven better than the capsule baseline.

Disposition: fold only these evidence-quality properties into the Context Builder.

## 6. Retrieval evaluation must include vocabulary/paraphrase shift

INS-0035 found that holding corpus and expected truth fixed while rephrasing questions in non-corpus vocabulary dropped task recall from 9/9 to 3/9 and source visibility from 81% to 31%.

Preserved lesson: lexical success on vocabulary-matched test questions does not prove retrieval is solved. Context/retrieval evals should include paraphrases, hard negatives, abstention quality, source rank, and drifted vocabulary.

Disposition: add to Context Builder / eval proof requirements.

## 7. Bounded phase-boundary discovery is useful; continuous discovery agents are not justified

EXP-0003 tested a visible, proposal-only, non-forcing Discovery Agent method on a completed phase. It produced two genuinely new useful findings, one useful rejection, zero scope drift, and zero implementation edits. The experiment recommended adoption with refinement for bounded phase-boundary use and explicitly rejected turning it into a continuous model loop.

Preserve the positive mechanism:

- bounded phase/project-boundary discovery pass;
- proposal-only;
- evidence linked;
- distinguish fact / inference / proposal;
- check existing records before claiming novelty;
- name the decision owner;
- no idea quota and no forced implementation.

Disposition: preserve as a bounded retrospective/discovery method, not a standing agent role.

## 8. Periodic system-adherence audit without a permanent watcher role

IDEA-0012/PROMO-0007 became TASK-129, a bounded audit that checked whether major MAP subsystems were:

- complete against their own intended behavior;
- cross-linked coherently;
- actually used in practice rather than merely documented.

Findings were routed into normal repair/tasks rather than silently fixed by the auditor.

Preserved lesson: periodically testing “built vs actually used” is useful, but this does not require a permanent process-policing agent.

Disposition: candidate reusable audit/cadence, especially after large batches of MAPS infrastructure changes.

## 9. One fact, multiple readers: require declared authority, atomic mutation, or reconciliation

SYN-0001 connected failures across tasks, agents, repositories, events, mirrors, and generated files. The common shape was one logical fact with multiple readers/copies and no declared winner.

The successful fixes fell into three patterns:

1. declare one source authoritative;
2. make competing mutation atomic;
3. mechanically reconcile/cross-check derived views.

Useful review question:

> Who else reads this state, and which copy wins?

Disposition: preserve as a design/review invariant; do not create a new subsystem merely for it.

## 10. End-to-end practice benchmark

SYN-0002 argues MAPS changes should ultimately be judged by an end-to-end scenario, not isolated subsystem metrics.

A useful benchmark shape is:

- correct orientation;
- safe first action;
- interruption and recovery;
- independent review;
- completion/release;
- context and coordination cost.

Disposition: fold into historical eval corpus and major Context Builder validation.

## 11. Explainable waits can be derived from structured communication metadata

INS-0036 found that most of a wait record can be derived from hcom metadata: requester, addressee, request body, message ID, timestamp, and thread. Agents need only specify exceptional `resumes_when`, timeout behavior, or impact when defaults are insufficient.

Possible Lean value:

- surface stranded review/request waits in `maps status` or replay;
- derive rather than ask agents to retype known communication facts;
- keep the wait record a read/projection aid rather than task-state authority.

Disposition: candidate refinement to replay/status/communication observability, not a new authority plane.

## 12. Helper/dispatch no-progress advisory

A nominally live helper can be stuck without producing progress. This differs from a stopped session handled by RnS.

Preserve only the bounded advisory experiment: no progress event/output change for a measured interval -> advisory signal. Avoid naive fixed timeouts, auto-kill, and permanent watcher roles.

Disposition: `P2 experiment candidate`.

## 13. Review evidence must still be true at review time

INS-0058 documented submission-time parity/checksum/metric evidence becoming stale before independent review. Reviewers who reran live/current checks caught real failures.

Preserved rule:

- bind evidence to an immutable revision where possible;
- otherwise rederive material evidence at review time;
- a submission snapshot must not be silently treated as a current fact.

Disposition: fold into review/evidence integrity.

## 14. Security/authority tests should assert behavior, not source spelling

INS-0060 documented repeated rework caused by tests matching exact source strings rather than the security property itself.

Preserved rule: when safely exercisable, test computed/executed security and authority behavior in an isolated environment. Source-text checks are acceptable only when the text itself is the property.

Disposition: fold into risk-specific review lenses and mechanical eval discipline.

## 15. Risk-specific/adversarial review framing

Legacy security reviews repeatedly found defects only when the reviewer explicitly asked “what can an attacker, hostile input, or bad timing window do here?” rather than only “does this satisfy the spec?”

Preserve risk lenses without requiring two reviewers for every task. Additional independent reviewers should be proportional to actual risk.

Disposition: `P2 review-quality refinement`.

## 16. Authority provenance: citation does not ratify a proposal

INS-0043 found an artifact explicitly labeled `proposed decision` gradually became a de facto binding gate because later authoritative records cited it as though it were approved.

Lean already requires consequential decisions to be recorded before acting, but preserve this explicit invariant:

> Referencing a proposal does not promote it to authority. Any artifact used as a gate must have traceable decision/approval provenance.

Disposition: design/review invariant; add mechanical checking only if this failure recurs in Lean.

## 17. Promotion/precondition ordering

INS-0046 found tasks being created before the promotion records that were supposed to authorize them had actually completed approval.

Preserved lesson: where one artifact/action is a true precondition for another, stable deterministic flows or guard checks should make the ordering visible. Do not create ceremony where the current Lean workflow has already removed the dependency.

Disposition: fold into deterministic `maps flow` procedures only when a repeated Lean procedure demonstrates this risk.

## 18. State reachability and correction paths

SYN-0005 and related insights observed state fields/statuses accumulating faster than sanctioned verbs to set, clear, or repair them, leaving live work stranded until a recovery command was retrofitted.

Preserved design question for any new durable field/state:

- how is it entered?
- how is it exited?
- how is an incorrect value corrected?
- what happens after interruption or owner/session loss?

Disposition: regression/design invariant. Lean's smaller state model already reduces this risk; do not recreate old lifecycle complexity to solve it.

## 19. Independent review should be changed only from measured evidence

INS-0021 measured a 23.1% pre-release changes-requested rate (36/156 submissions) in the old system while the semantic validator assumed by an earlier simulation did not exist. Its conclusion was to avoid weakening review based on a hypothetical validator.

Lean already uses proportional risk-tiered review rather than universal ceremony. Preserve the measurement principle: use review-catch, escaped-defect, rework, and validator-quality data before materially weakening or strengthening review requirements.

Disposition: fold into Outcome Feedback / metrics / harness evaluation.

---

# Historical items checked and found already solved or improved in Lean

Do not revive these merely because they appear in legacy records.

- **Atomic review claiming:** Lean mechanically claims reviews.
- **Durable submission authorship / no-self-review integrity:** Lean keys review independence to durable submission authorship and continuity lineage rather than stale owner strings.
- **Terminal/superseded-session suppression:** Lean RnS suppresses terminal sessions and stops recovery when task/claim reality changed.
- **Complex policy OR-branch evidence issue:** the historical bug depended on an evidence gate that emitted alternatives without consuming the evidence. Lean's current policy evaluator uses a simpler explicit approval state and actually checks it.

These remain useful regression history, not future-feature requests.

---

# Candidate queue interpretation

`emergence/candidates/` is a deterministic scanner queue. Candidate JSON files are signals for human/core-agent curation, not Insights, Ideas, policy, or task authority.

The records sampled in this audit support that intended lifecycle:

- genuinely reusable findings were accepted and linked to durable Insights;
- routine rework/noise was dismissed;
- at least one historical scanner had incorrect evidence pointers, demonstrating why scanner output must remain independently verifiable.

Future recovery passes should therefore prioritize unresolved durable Insights/Ideas/Syntheses and follow accepted candidates to their resolution reference rather than treating every `CAND-*` file as an idea to preserve.

---

# Remaining audit work

This checkpoint deliberately does **not** claim full-line coverage of all legacy material.

Highest-value remaining work:

1. deep-read MAP-relevant Insights that remain `RAW`, `OPEN`, `CANDIDATE`, `PARKED`, or otherwise unresolved and compare each against current Lean;
2. inspect ambiguous/unfinished promotion chains and confirm whether their downstream task actually shipped;
3. inspect `RETIRED`/abandoned MAP-system tasks for supersession versus genuinely lost functionality;
4. follow important legacy research/planning/artifact references when they support an unresolved MAP-system claim;
5. periodically reconcile this audit with `FUTURE_IDEAS_BACKLOG.md` so a useful recovered lesson does not exist only in the audit checkpoint.

Avoid exhaustive project-specific archaeology unless it yields a reusable MAPS mechanism or exposes a control-plane failure.

---

# Resume point for a future session

If this audit is interrupted, resume with:

> Continue the MAPS Lean legacy idea-recovery audit from `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`. Focus on unresolved MAP-system Insights/Syntheses/promotions and RETIRED/abandoned task chains. For each item, compare the underlying problem against current Lean before adding anything to `migration/FUTURE_IDEAS_BACKLOG.md`. Do not revive project-specific or old-system complexity without evidence.

The most important rule is to distinguish four outcomes:

```text
RECOVER AS CANDIDATE
FOLD INTO EXISTING CANDIDATE
ALREADY SOLVED IN LEAN
HISTORICAL / DO NOT REVIVE
```

That classification is the durable output of the archaeology.