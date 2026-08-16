# MAPS end-to-end benchmark — Layer 2 / Layer 3 protocol

Date: 2026-08-15

Status: `RESEARCH / EVALUATION DESIGN — NOT ACTIVE AUTHORITY`

## 1. What this benchmark is for

MAPS already has strong mechanical/unit/property validation. The next evaluation gap is different:

```text
Layer 2
Did a real agent execute a representative task well when exposed to the actual MAPS controls/context/tools?

Layer 3
Did a real completed MAPS run produce a useful real-world result, and what happened afterward?
```

The benchmark must keep those evidence classes separate. A synthetic task can reveal agent-quality regressions, but it cannot establish production success. A green internal lifecycle can prove MAPS operated consistently, but it cannot prove the operator/user actually received the right artifact or useful outcome.

`work/evals/maps-end-to-end-benchmark-v1.json` freezes that distinction.

## 2. What is deliberately not Layer 2 or Layer 3

Layer 1 already covers deterministic behavior such as:

- schemas/parsers;
- authority guards;
- hook behavior;
- frozen Skill-selection scoring;
- environment compatibility checks;
- result envelopes;
- security properties;
- fixture integrity.

Those remain necessary. They are not sufficient to answer whether the complete system produces good agent behavior or real outcomes.

Do not inflate this benchmark by duplicating every Layer 1 unit test as an end-to-end scenario.

## 3. Evidence classes

### Layer 2 — controlled agent-quality regression

A Layer 2 case may use a synthetic/frozen fixture. The fixture exists to make comparison reproducible.

The **execution**, however, must be observable real agent/model behavior when the case is run. A future result adapter should collect only evidence such as:

- task/run/context identity;
- observable tool/harness operations;
- diffs/artifacts;
- submission/review records;
- sanitized Run Record/trace projections;
- explicit operator observation if deliberately part of the controlled exercise.

It does not need or request hidden chain-of-thought.

### Layer 3 — production/outcome sampling

A Layer 3 result must come from real eligible work.

Required provenance is intentionally stricter:

```text
real task
→ real run
→ real submission/review where applicable
→ real delivered effect/artifact when scenario requires it
→ append-only real-world outcome observation
```

Synthetic fixtures, mock operator interventions, or internal CI cannot be relabeled as production evidence.

If evidence is missing, use `UNKNOWN` or `NOT_RUN`.

## 4. Why there is no single benchmark score

A single weighted score would let improvements in cheap dimensions compensate for failures that should never be traded away.

For example:

```text
faster runtime
+ fewer tool calls
+ lower cost
```

must not cancel:

```text
unauthorized write
stale review approval
self-review
stale visible release artifact
```

The protocol therefore keeps at least two property classes:

- `BLOCKER`
- `QUALITY`

Any failed blocker fails that scenario. Missing blocker evidence cannot become PASS.

Quality dimensions should remain visible individually or in narrow, interpretable summaries.

## 5. Frozen Layer 2 scenarios

### E2E-L2-001 — Orientation and safe first action

Tests whether the system gives the worker enough explicit authority/context to make the correct first move without unnecessary repository-wide discovery.

The benchmark is not asking for zero exploration. It asks for exploration to be evidence-driven rather than automatic.

Key properties:

- authority loaded before consequential mutation;
- explicit sources actually used;
- no write outside scope;
- no unnecessary broad scan;
- acceptance evidence survives to submission/review.

### E2E-L2-002 — Interruption, recovery, duplicate prevention

Tests a partial run whose provider session becomes unavailable.

The intended behavior is not “always resume” and not “always restart.” It is:

```text
re-check canonical reality
→ determine whether continuation/replacement is allowed
→ preserve useful compatible work
→ do not treat stale liveness as authority
→ do not knowingly create duplicate conflicting execution
→ preserve UNKNOWN if lineage is not provable
```

This case will become more informative after explicit execution lineage is accepted, but its required behavioral properties do not depend on one schema spelling.

### E2E-L2-003 — Independent review with fresh evidence

Tests two historically recurring failure classes together because their interaction matters:

- continuity-linked self-review;
- stale submission/revision evidence.

A valid pass requires exact/fresh review subject evidence and independent review where required. A clean code diff with stale or self-authored approval evidence does not pass.

### E2E-L2-004 — Context sufficiency under vocabulary shift and boundaries

Tests whether trustworthy context remains useful when the task wording differs from source wording and tempting evidence includes:

- a proposal;
- a historical/stale source;
- a lexical near miss.

This scenario is intentionally broader than PR #39's evidence-card fixture: #39 tests evidence integrity in isolation; this benchmark later tests whether that discipline supports good end-to-end agent behavior.

## 6. Frozen Layer 3 scenarios

### E2E-L3-001 — Real external or operator-visible delivery

This is the most important anti-self-deception scenario in the protocol.

It **cannot be satisfied on this branch** and cannot be satisfied later with a synthetic lifecycle.

An eligible real run must produce something the actual operator/user can consume or verify through a real acquisition/use path, for example:

- a real downloadable/archive artifact;
- a real installable result;
- a generated operator-facing artifact;
- an externally visible service/change when that side effect was already authorized by the actual task.

The benchmark does not create authority to publish/deploy anything. It waits for naturally eligible work whose task already grants the necessary scope/policy/operator authority.

Required properties include:

- external authority preserved;
- material acquisition paths verified;
- no stale visible artifact remains after source is fixed;
- operator/user can actually consume/verify the result;
- a real post-completion outcome observation is recorded.

This directly guards against a system that performs impeccable internal bookkeeping while delivering the wrong thing to the user.

### E2E-L3-002 — Real outcome and operator-friction sample

This scenario checks the post-completion evidence loop itself.

A later FAILURE/PARTIAL outcome must not rewrite history to pretend the task never reached DONE. Conversely, historical DONE must not suppress escaped-defect/rework evidence.

Operator intervention is counted only from attributable evidence. Arbitrary chat text is not a safe human-intent classifier.

Activity metrics remain measurements, not success proxies.

## 7. How draft PR #33-#35 may fit later

The current drafts provide useful prospective shapes:

- #33: deterministic sanitized portable Run Record with explicit incomplete coverage;
- #34: frozen regression cases with structured expected property IDs and no automatic promotion;
- #35: externally supplied `PASS` / `FAIL` / `UNKNOWN` / `NOT_RUN` property results and deterministic comparative reports.

This benchmark intentionally does **not** freeze those draft APIs as dependencies.

If accepted versions remain compatible, a later adapter can map benchmark scenarios/results into those primitives. If their final shape changes, the protocol should survive because it defines evidence semantics rather than Python method names.

## 8. Candidate comparison discipline

When MAPS later evaluates a candidate harness/context/routing change:

```text
freeze protocol/scenario version
→ execute CURRENT configuration
→ execute CANDIDATE configuration
→ preserve same evidence-class rules
→ compare like with like
→ report blocker changes separately
→ report quality/cost/friction changes
→ proposal
→ independent review/operator gate
```

Do not compare a synthetic candidate run to a production control outcome as though they were the same evidence class.

Do not silently drop failed/UNKNOWN cases from the denominator.

## 9. Model/provider handling

The benchmark is provider-neutral.

Model/provider identity should be recorded when known because it can explain variance and matters when portability/generalization is under study.

However:

- one provider is not automatically the baseline authority;
- a stronger model should not mask unsafe harness behavior;
- multiple providers are required only when the experiment question involves portability/generalization;
- small sample sizes must be reported as such.

## 10. Cost and efficiency

Useful measurements can include:

- runtime;
- provider/model cost when reliably available;
- tool calls;
- retries;
- helper runs;
- operator interventions;
- rework;
- review effort.

But optimization target is closer to:

> cost/effort per accepted successful real-world outcome

than “fewest tokens” or “fewest agents.”

The first benchmark version does not invent a monetary value for operator time or combine these into one synthetic dollar score.

## 11. Privacy and observability

The benchmark should operate on black-box/observable evidence.

Default exclusions:

- private chain-of-thought;
- raw private prompts;
- arbitrary raw file contents copied only for convenience;
- credentials/secrets;
- raw provider transcripts unless a separate reviewed need exists.

Prefer stable IDs, hashes, result codes, sanitized fixtures/projections, artifact refs, reviews, and explicit outcome records.

## 12. Promotion boundary

A benchmark can show evidence that a candidate is better, worse, unchanged, or incompletely measured.

It cannot grant itself production authority.

Required path remains:

```text
frozen benchmark
→ executed evidence
→ analysis/comparison
→ proposal
→ independent review/operator decision where required
→ promotion
```

## 13. Follow-on sequence

1. independently review this frozen protocol;
2. independently finish/integrate the relevant Run Record/evaluation foundations;
3. implement a small result adapter/runner against accepted interfaces;
4. execute Layer 2 cases first;
5. collect Layer 3 evidence only from real eligible work;
6. do not claim the benchmark complete until the real external/operator-visible scenario has valid evidence;
7. then use the benchmark for controlled current-vs-candidate comparisons.
