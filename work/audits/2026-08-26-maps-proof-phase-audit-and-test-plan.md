# MAPS_Lean — Proof Phase Audit & External Test Plan

Status: `PROOF-PHASE INPUT — NON-AUTHORITATIVE UNTIL SHAPED INTO TASKS`

Primary question:

> **Does MAPS_Lean measurably improve real agent work enough to justify its control-plane complexity?**

## Connections

- [Audit index](README.md)
- [Deep Project Archaeology Audit](2026-08-26-deep-project-archaeology-audit.md)
- [Current reconciliation task](../tasks/reconcile-project-truth-20260826.md)
- [Current reconciliation / Proof Phase handoff](../handoffs/2026-08-26-project-reconciliation-and-proof-phase.md)
- [Roadmap index](../roadmaps/README.md)
- [Roadmap 06 — Portable Deployment](../roadmaps/agent-harness-capabilities/06-portable-deployment.md)
- [Capability checklist](../roadmaps/CAPABILITY_CHECKLIST.md)
- [Information lifecycle](../../playbook/INFORMATION_LIFECYCLE.md)
- [Roadmap trajectory check](../../playbook/ROADMAP_TRAJECTORY_CHECK.md)

**Current disposition:** preserve this as the external Proof Phase test
specification. The later archaeology audit supersedes any conflicting diagnosis
here about whether a particular old note/design remains unfinished. Always
reconcile against current `main`, current checklist evidence, merged PR history,
and live GitHub state before creating work.

---

## 1. Why the Proof Phase exists

MAPS_Lean has crossed several thresholds:

| Stage | Assessment |
|---|---|
| Interesting concept | Passed |
| Working prototype | Passed |
| Coherent internal architecture | Passed |
| Can coordinate real agents | Mostly passed |
| Dogfooded on its own development | Passed |
| Demonstrably improves unrelated real work | **Not proven** |
| Portable across unrelated repositories | **Not proven** |
| Worth its complexity compared with plain Claude/Codex | **Not proven** |
| General-purpose agent operating layer | Too early to claim |

The next question is no longer whether MAPS mechanisms can be built.

It is:

> **Which mechanisms deserve to survive?**

This document is therefore not a roadmap for feature expansion. It is a plan to
measure MAPS as it exists.

---

## 2. Core hypothesis to try to falsify

> **A small set of explicit mechanisms for authority, context trust, recovery,
> verification, and independent review can make long-running agent work more
> reliable without imposing excessive control-plane cost.**

The evaluator should attempt to falsify this hypothesis rather than confirm the
architecture narrative.

Do not reward MAPS merely for:

- passing its own tests;
- completing roadmap items;
- generating more evidence;
- producing more detailed records;
- creating more agent activity;
- or being internally coherent.

The project must prove that it helps real work.

---

## 3. Strong mechanisms worth preserving unless evidence disproves them

### 3.1 Canonical authority separation

MAPS distinguishes authority-bearing state from supporting information.

Authority-bearing examples:

- task truth;
- ownership;
- authorization;
- review state;
- acceptance;
- operator approvals.

Supporting/non-authoritative examples:

- messages;
- routing suggestions;
- context;
- helper output;
- recovery/session state;
- traces;
- memory/guidance.

Principle:

> **Information being available does not make it authoritative.**

### 3.2 Memory/context is not automatically truth

A retrievable memory, Skill, lesson, report, or old note must not silently become
current authority.

Principle:

> **Can retrieve != may rely on as current truth.**

### 3.3 Independent review

Authorship and continuity matter. A successor inheriting the original author's
context is not automatically an independent reviewer.

Keep the principle; measure the bookkeeping cost.

### 3.4 Recovery and resumption

MAPS addresses a real long-running-agent problem: distinguish current canonical
state, stale sessions, prior useful work, duplicate execution, and valid
continuation after interruption.

Keep and test. Do not extend recovery architecture merely to complete a shape.

### 3.5 Outcome/evaluation discipline

MAPS correctly distinguishes green CI/synthetic fixtures/activity from real
external outcome evidence. The immediate need is to run the evaluation, not add
more evaluation vocabulary.

---

## 4. Main concerns to test

### 4.1 Architecture completing architecture

Observed risk pattern:

```text
design capability
→ implement primitive
→ test primitive
→ design integration
→ implement integration
→ discover no production caller
→ design caller
→ implement caller
→ discover another boundary
```

A cleanly designed component can still be unnecessary.

### 4.2 Roadmap self-demand

MAPS can become very good at asking:

> Are we implementing MAPS correctly?

while failing to ask:

> Was implementing this part worth doing?

Roadmap membership is not proof of value.

### 4.3 Production wiring vs. primitives

Look for mechanisms that are implemented/tested but not exercised by real work.
Classify them separately from both “not implemented” and “proven.”

Useful maturity distinctions:

```text
DECLARED
IMPLEMENTED
TESTED
PRODUCTION_REACHABLE
PRODUCTION_COMPOSED
EVIDENCE_FED
EXTERNALLY_PROVEN
```

### 4.4 Human-readable integrity

Machine-readable authority can be correct while PR title/body/branch/task/files
and roadmap references disagree. A real example occurred on PR #172.

Test whether lightweight consistency checks catch repeated real failures before
building anything larger.

### 4.5 Review-evidence bookkeeping cost

Exact review binding is valuable, but repeated evidence commits/rebinds/main-sync
can create a self-invalidating proof loop.

Measure:

- rebinding/sync operations;
- time/tool/token cost;
- actual defects caught because exact binding existed;
- whether a smaller immutable-artifact mechanism could preserve the invariant.

Do not weaken the invariant merely because it is inconvenient.

### 4.6 Legacy/cognitive surface

Measure whether preserved legacy/historical material causes:

- irrelevant reads;
- orientation delay;
- incorrect assumptions;
- implementation against dead architecture.

Do not delete legacy during the initial test.

### 4.7 Over-governance of trivial work

Target proportionality:

```text
LOW
work → basic validation → done

MEDIUM
bounded task → execution → evidence → review

HIGH
frozen context → constrained authority → evidence
→ independent review → operator gate → external action
```

If every task pays high-risk ceremony, MAPS is not Lean enough.

### 4.8 Workflow governance vs. execution governance

Determine precisely what MAPS actually controls.

- Workflow governance: canonical records, authorization, review, acceptance.
- Execution governance: an unavoidable policy choke point between agent and
  real tool/action.

Do not describe MAPS as a security sandbox unless the actual invocation path is
enforced.

---

## 5. First-class metric: control-plane tax

> **Control-plane tax = resources MAPS consumes to govern, coordinate, verify,
> record, route, recover, or review work rather than directly perform the
> requested work.**

Measure at least:

- extra tool/model calls;
- tokens if available;
- wall-clock time;
- coordination messages;
- state writes / claims / leases;
- context-building operations;
- evidence generation;
- review operations;
- rebinding/synchronization work;
- recovery operations;
- operator interventions;
- MAPS-only artifacts.

Then ask:

> **What did we buy with that tax?**

The same overhead can be justified for a consequential migration and absurd for
a trivial cosmetic edit.

---

## 6. Proof Phase freeze rule

During evaluation:

> **Do not add a new major capability category unless a real test exposes a
> concrete failure that existing MAPS mechanisms cannot handle.**

Decision sequence:

```text
observed failure
→ can existing MAPS solve it?
    yes → do not build
    no  → identify smallest missing mechanism
        → bounded experiment
        → measurable improvement?
            yes → keep
            no  → revert/remove
```

---

## 7. Areas to keep, freeze, or defer

| Area | Direction |
|---|---|
| Canonical state / authority | KEEP |
| Independent review principle | KEEP; measure cost |
| Recovery/resumption | KEEP; integrate/test, do not extend by default |
| Outcome/evaluation | PRIORITIZE |
| Explicit-first context | KEEP |
| Portable external pilot | PRIORITIZE |
| Third-party Skill support | Finish already-bounded work, then freeze |
| More Skill lifecycle sophistication | FREEZE pending evidence |
| New memory mechanisms | DEFER |
| Semantic/vector memory production use | DEFER / evidence-gated |
| Autonomous learning/promotion | DEFER |
| More agent/persona architecture | STOP |
| New capability families | FREEZE |
| Unified mission object | DEFER unless tests demand it |
| VM/container sandbox architecture | DEFER unless execution governance requires it |
| More review bookkeeping | STOP adding; measure/simplify |
| Roadmap expansion | PAUSE |

---

## 8. External test design

Use at least:

- **2–3 unrelated repositories**;
- **10–20 genuine tasks total**;
- different structures/stacks where practical.

Do not use MAPS_Lean itself as the primary benchmark. Dogfooding is useful but
familiarity with the architecture biases the test.

### Matched comparison

**Condition A — plain agent**

```text
Claude or Codex
+ repository
+ normal task instructions
```

**Condition B — MAPS**

```text
same model/provider class where practical
+ same repository
+ same task
+ MAPS_Lean process
```

Perfect laboratory matching is not required; document meaningful differences.

---

## 9. Required task classes

1. **Simple bounded change** — measure low-risk overhead.
2. **Multi-file feature** — test scoping/context/evidence/review.
3. **Ambiguous bug** — test investigation and premature conclusions.
4. **Interrupted task** — intentionally lose/stop a session after partial work.
5. **Stale-context task** — change relevant repo state between stages.
6. **Independent-review task** — measure defect yield and review cost.
7. **Research-heavy task** — test provenance/context selection.
8. **Safe external/destructive simulation** — determine advisory vs. enforced
   policy without touching real production systems.

Where useful, fold existing research experiments into the pilot rather than
creating separate work:

- EXP-B: deterministic hook value;
- EXP-C: structured tool/ACI output ergonomics;
- EXP-D: EnvironmentSpec reproducibility;
- EXP-E: malicious/ambiguous Skill red-team after a baseline exists.

---

## 10. Per-task measurements

### Outcome quality

- correct result?
- acceptance criteria met?
- regressions/defects introduced?
- reviewer-found defects?
- operator-visible quality?

### Execution reliability

- wrong/stale assumptions?
- unauthorized writes?
- scope violations?
- duplicate work?
- failed resumption?
- false “done” claims?

### Efficiency

- tool/model calls;
- tokens;
- wall time;
- files inspected/modified;
- repeated investigation;
- retries.

### Human burden

- interventions;
- clarifications;
- approvals;
- corrections;
- manual cleanup;
- attention required.

### MAPS-specific burden

- claims/leases;
- state mutations;
- context plans;
- evidence/review artifacts;
- trace/rebind operations;
- recovery/helper coordination;
- process-only artifacts.

Suggested comparison table:

| Metric | Plain | MAPS | Difference |
|---|---:|---:|---:|
| Correct outcome | | | |
| Serious defects | | | |
| Rework | | | |
| Human interventions | | | |
| Tool calls | | | |
| Tokens | | | |
| Time | | | |
| Duplicate work | | | |
| Wrong/stale assumptions | | | |
| Review defects caught | | | |
| Recovery success | | | |
| MAPS-only operations | 0 | | |
| Control-plane tax | baseline | | |

---

## 11. Review effectiveness must be measured separately

Recent MAPS reviews are demonstrably not pure rubber stamps, but “a finding” can
range from a blocking conceptual defect to a harmless nit.

Measure:

- review finding rate;
- blocking-finding rate;
- action rate — finding caused code/design change;
- material defect-prevention rate;
- non-blocking/nit rate;
- review time/tokens/tool calls;
- post-merge escaped defects.

A useful mechanism earns its place when the defects prevented justify the
review tax.

---

## 12. Specific stress tests

### Canonical state / authority

Attempt stale continuation, conflicting ownership, false completion, and
unauthorized transitions.

### Context Builder

Test whether explicit-first context prevents repository scanning without hiding
necessary evidence, and whether guidance remains non-authoritative.

### Recovery

Force session loss, stale provider session, partial completed work, and
replacement worker. Measure duplicated/lost work and operator burden.

### Independent review

Measure real defects caught, false positives, review latency, continuity rules,
and evidence bookkeeping.

### Evidence binding

Measure whether exact binding prevents actual errors and how much maintenance it
causes. Watch specifically for self-invalidating proof cycles.

### Skills

Test progressive Skill body activation and trust/gating only after the existing
bounded foundation. Do not build Capability Packs first.

### Memory / operational learning

Look for bad lessons, stale lessons, self-reinforcing assumptions, and guidance
accidentally acquiring authority. Do not expand autonomous promotion.

### External/destructive action policy

Use safe simulations and multiple paths — direct worker, helper, resumed run,
alternate route. A bypass is a real finding.

### Spiderweb / continuity

Once [Spiderweb Audit](../../playbook/SPIDERWEB_AUDIT.md) is accepted, use it as
an advisory continuity test. It must not auto-promote, auto-link, or create
work merely because graph structure is thin.

### Tenth Seat

Use [Tenth-Seat review](../../playbook/TENTH_SEAT_REVIEW.md) only when its
pre-registered rare trigger fires. Measure whether it finds a material weakness
ordinary review missed.

---

## 13. What counts as a MAPS win

Not “more thorough.” A mechanism earns its place when it observably:

- prevents a serious mistake;
- catches stale work;
- prevents duplicate execution;
- improves recovery/resumption;
- reduces repeated investigation;
- catches a meaningful defect in independent review;
- prevents an unauthorized action;
- reduces human supervision;
- preserves trustworthy context;
- or materially improves final outcome.

The gain must be compared with cost.

---

## 14. Evidence to freeze, simplify, or remove a mechanism

Consider subtraction when a mechanism:

- is rarely/never exercised;
- produces the same outcomes as the lighter baseline;
- carries substantial control-plane tax;
- primarily exists to maintain other MAPS machinery;
- produces records nobody uses;
- duplicates another mechanism;
- catches only hypothetical problems;
- creates more operator work than failures it prevents;
- or has value only while MAPS develops itself.

Do not remove mechanisms mid-initial test. Record evidence first.

---

## 15. Reporting discipline

Every conclusion must be labeled as one of:

- **OBSERVED** — directly demonstrated;
- **SUPPORTED INFERENCE** — strongly indicated by evidence;
- **HYPOTHESIS** — plausible but untested.

Test status must use:

- `PASS`
- `FAIL`
- `UNKNOWN`
- `NOT RUN`

Missing evidence never becomes PASS.

Do not infer:

- authority from session activity;
- correctness from green CI;
- usefulness from agent activity;
- provenance from similarity;
- production readiness from unit tests.

---

## 16. Required final Proof Phase report

The evaluating agent must produce:

### A. Executive assessment

Answer:

> **Does MAPS_Lean currently justify its complexity?**

Choose: `YES | PARTIALLY | NOT YET | NO`.

### B. Mechanisms that earned their place

For each: mechanism, observed failure prevented, evidence, cost, recommendation.

### C. Mechanisms with uncertain value

State the intended failure, whether it occurred, cost, and next test.

### D. Mechanisms to freeze/simplify/remove

Require evidence; “feels complicated” is insufficient.

### E. Missing mechanisms revealed by real failures

Only include observed gaps. For each: failure, why existing MAPS failed,
smallest plausible mechanism, proof test.

### F. Control-plane tax

Summarize calls/time/tokens/operator burden/artifacts and answer:

> **Where is MAPS worth paying for?**

### G. Proportional-governance result

Identify task classes where MAPS helps, is neutral, or is excessive.

### H. Recommended project direction

Choose among continue, simplify, narrow, focus on high-risk workflows, collect
more evidence, or redesign.

### I. Mandatory subtraction list

List what should remain, freeze, simplify, archive, or be removed.

A Proof Phase that only proposes additions is incomplete.

---

## 17. Decision standard

Every MAPS mechanism should eventually answer:

1. What observable failure does this solve?
2. Does that failure actually occur?
3. What is the smallest mechanism that solves it?
4. Can we measure whether it worked?
5. What does it cost?
6. What can be deleted or avoided because it exists?

The next major milestone is not another completed roadmap section.

It is evidence that MAPS has found:

> **the smallest set of mechanisms that reliably makes agent work better.**
