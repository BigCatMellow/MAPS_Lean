# Legacy recovery reconciliation map

Status: `PLANNING / RECONCILIATION — NOT ACTIVE AUTHORITY`

Last reconciled: `2026-08-15`

Purpose: connect the mechanisms and lessons recovered from legacy MAPS to the current MAPS Lean program so useful discoveries are neither lost nor blindly rebuilt.

This document is subordinate to `00-MASTER-MAPS-CAPABILITY-ROADMAP.md`. It owns only the **legacy-derived reconciliation view**: what is already merged, what is represented in current draft PRs, what should be next, what is evidence/usage-triggered, what remains historically unresolved, and what should not be revived.

Current behavior and authority remain defined by `AGENTS.md`, canonical task/policy/review state, merged code/tests, accepted task requirements, and explicit operator decisions.

---

# 1. Reconciliation rule

For every legacy mechanism or lesson, use the smallest honest classification:

```text
MERGED
= accepted behavior already exists on current main

IN OPEN PR
= current draft work implements or materially advances the recovered capability

NEXT
= recovered capability remains materially useful and prerequisites are now strong enough to plan the next tranche

TRIGGERED / LATER
= useful but should exist only after a measurable usage/risk/repetition trigger

DO NOT REVIVE
= legacy direction was invalidated, superseded, or conflicts with Lean architecture

AUDIT REMAINS
= historical evidence is incomplete enough that implementation disposition is still UNKNOWN
```

A candidate may be split across classifications. For example, `trace` can be `MERGED` at v1 while communication-complete lineage remains `NEXT`.

Never infer promotion from repeated citation. A legacy proposal, audit note, roadmap entry, or passing benchmark is not runtime authority.

---

# 2. Verified current baseline

At this reconciliation checkpoint:

- `main` is the merged PR #19 baseline (`086e066f723d793273441dd52b500e62ac981deb` when this task started);
- PRs #20-#35 are open draft implementation work;
- PR #36 is this planning reconciliation;
- PR #37 is the bounded parallel legacy-archaeology evidence report;
- review remediation found during the 2026-08-15 pass was fixed on the affected implementation branches and current-head Runtime CI passed at the recorded checkpoints;
- draft implementation PRs still require valid independent review before their behavior can be treated as accepted `main` authority.

Do not trust SHA/status lines in planning prose after time has passed; re-check GitHub before implementation or review.

---

# 3. Legacy-derived capabilities already merged

These should not be rebuilt as new systems. Future work should extend the accepted Lean mechanism only when a concrete gap exists.

| Recovered lesson/candidate | Current Lean result | Status | Follow-up boundary |
|---|---|---|---|
| Negative operating contract | root `AGENTS.md` prohibitions against overcomplexity, guessing, duplicate truth, silent scope growth, unnecessary permanent agents | `MERGED` | Preserve; do not grow into bureaucracy |
| Risk-specific review lenses | explicit functional/security/privacy/destructive/release/authority review framing | `MERGED` | Measure review quality before adding mandatory reviewer count |
| Telemetry/event secret-safety boundary | secret-safer event/diagnostic handling with explicit redaction markers | `MERGED` foundation | Re-audit each new durable telemetry surface |
| Outcome feedback | append-only SUCCESS/PARTIAL/FAILURE/UNKNOWN post-completion observations with provenance | `MERGED` foundation | Use for later incident/eval metrics; never rewrite historical task truth |
| Context Builder | explicit-first disposable context plan with exact file hashes and missing/outside boundaries | `MERGED` v1 | Exact evidence-card/retrieval refinement remains separate |
| Operator status surface | small read-only `status` view over canonical state | `MERGED` v1 | Wait/helper/lineage enrichments must remain derived |
| Task trace | secret-safer read-only trace over canonical task/review/policy/run/context/criterion/outcome evidence | `MERGED` v1 | External communication/helper/recovery correlation remains incomplete |
| PR Runtime CI | normal PR-triggered validation of runtime stack | `MERGED` | Green CI is evidence, not independent approval |
| Atomic review claiming / durable authorship / continuity-aware independence | current review lifecycle already mechanically protects these properties | `MERGED / SOLVED` | Preserve as regression invariant |
| RnS suppression of invalid/terminal recovery | current recovery already respects canonical task/claim reality | `MERGED / SOLVED` | Preserve as regression invariant |
| One-fact/one-authority rule | active operating/architecture invariant | `MERGED / SOLVED` | New subsystems must derive or reference rather than duplicate |
| Shaping-time contract correction | `update_contract()` allows transactional correction while shaping/blocked, then freezes active/reviewed work | `MERGED / SOLVED` | Preserve correction-path invariant; do not recreate legacy write-once path bureaucracy |

---

# 4. Legacy-derived work represented by current open PRs

These are **implementation evidence in progress**, not accepted authority until independently reviewed/merged.

## 4.1 Harness, lifecycle and authority enforcement — PRs #20-#24

Recovered legacy/Prime problems addressed:

- provider-specific lifecycle behavior;
- ambiguous worker/session terminology;
- session liveness being mistaken for task truth;
- authority checks depending on agent memory;
- stale recovery/session continuation;
- adversarial authority/identity manipulation.

Current draft sequence:

```text
#20 provider-neutral harness types/protocol
  ↓
#21 hcom normalization + deterministic Hook registry
  ↓
#22 HarnessService execution surface
  ↓
#23 canonical run/task guard before consequential harness operations
  ↓
#24 executable agentic-security/adversarial baseline
```

Reconciliation status: `IN OPEN PR`.

Still not solved by this stack:

- complete durable task → run → provider session → helper → recovery/replacement lineage;
- communication-complete replay/trace;
- explainable waits;
- broad ACI normalization for every tool surface;
- general immediate post-mutation validation coverage.

Those belong in later focused tranches, not scope creep into #20-#24.

## 4.2 Procedural knowledge / Skills — PRs #25-#27 and #31

Recovered problems addressed:

- reusable expertise being encoded as persona-heavy permanent agents;
- procedural content lacking provenance;
- unsafe imported instructions/scripts;
- lexical/vocabulary-sensitive routing claims being accepted without frozen evaluation.

Current draft sequence:

```text
#25 Agent Skills format/discovery foundation
  ↓
#26 provenance-aware derived Skill catalog
  ↓
#27 frozen Skill selection evaluation corpus
  ↓
#31 static Skill quality/security gate
```

Reconciliation status: `IN OPEN PR`.

Still not solved:

- reviewed Skill trust/promotion/retirement lifecycle;
- persistent quarantine workflow if it proves necessary;
- Context Builder integration;
- production Skill selection/routing;
- behavioral sandbox/evaluation of executable Skill resources;
- capability intersection when a Skill requests tools/network/credentials.

No `CLEAR` static scan may become automatic trust or production activation.

## 4.3 Environment and reproducibility — PRs #28-#30

Recovered problems addressed:

- model/agent failure being confused with environment drift;
- recovery occurring without explicit environment compatibility evidence;
- reproducibility relying on implied host assumptions.

Current draft sequence:

```text
#28 EnvironmentSpec v1
  ↓
#29 local EnvironmentFingerprint + compatibility
  ↓
#30 append-only environment evidence bound to runs
```

Reconciliation status: `IN OPEN PR`.

Still not solved:

- recovery decisions that consume compatibility evidence safely;
- environment-declared validation execution;
- worktree/container/remote environment implementation;
- snapshots/rehydration;
- credential brokering.

Environment compatibility remains evidence, not task authority.

## 4.4 Review-time evidence freshness — PR #32

Recovered problem addressed:

- submission-time evidence becoming stale before consequential review;
- reviewers approving a different revision/evidence set than the one claimed.

Current draft:

- immutable review subjects;
- exact task/submission/revision binding;
- immutable artifact/evidence refs;
- revision-bound or re-derived freshness modes.

Reconciliation status: `IN OPEN PR`.

Still not solved:

- user-visible release/acquisition-path verification;
- broader artifact registry (not automatically desirable).

The parallel archaeology pass confirmed the first item is a real historical failure mode (`INS-0005 → IDEA-0005 → PROMO-0005 → TASK-078`): source could be fixed while a stale user-visible ZIP remained the actual acquisition path. Preserve this as a narrow risk-triggered review capability, not as a reason to build a general artifact registry.

## 4.5 Run Records, incident freezing and comparative evaluation — PRs #33-#35

Recovered problems addressed:

- no portable black-box-style execution evidence;
- incidents remaining anecdotes rather than regression cases;
- candidate harness changes being judged without a frozen baseline;
- evaluation success being able to drift toward implicit promotion authority.

Current draft sequence:

```text
#33 portable Run Record v1
  ↓
#34 frozen regression case v1 + recovered incident taxonomy
  ↓
#35 deterministic baseline-vs-candidate comparative evaluator
```

Reconciliation status: `IN OPEN PR`.

Preserved promotion path:

```text
frozen cases
→ candidate results
→ comparative report
→ proposal
→ independent review/operator gate where required
→ promotion
```

Never:

```text
better score → automatic production change
```

Still not solved:

- complete operation/session/helper/recovery trajectories;
- production incident sampling/triage into cases;
- Layer 2 qualitative agent-quality evaluation;
- Layer 3 real-world outcome comparison;
- proposal/promotion lifecycle;
- operational lesson lifecycle.

Integration note: #33 already accepts optional environment evidence and immutable review-subject trace enrichments while preserving missing communication/session/helper/recovery coverage as `MISSING`/`UNKNOWN`. Those later enrichments do not require turning Run Record into a new authority store.

## 4.6 Parallel archaeology reconciliation — PR #37

The bounded independent archaeology report on PR #37 found **one new Lean-native candidate** and otherwise sharpened existing candidates.

New candidate:

- risk-triggered **user-visible acquisition-path verification** for tasks that actually publish/package/install/expose something to an operator or user.

Folded into existing work:

- `INS-0034`: reviewer drops, duplicate work and unexplained waits strengthen NEXT A/B lineage/communication priority;
- `INS-0037`: process liveness must be distinguished from provider/API readiness;
- `INS-0032`: promoted lessons need selective applicability projection, not inert prose;
- `INS-0056`: observations from explicitly non-task/operator-directed work may enter learning as non-authoritative candidates without importing that work into task authority;
- `INS-0061`: evidence references must resolve to the exact subject/event they claim;
- `INS-0023`: end-to-end evaluation needs at least one real external/operator-visible workflow, not only internal synthetic lifecycle exercises;
- `INS-0051` / `IDEA-0030`: helper `NO_PROGRESS` should remain progress-sensitive and advisory, not fixed-timeout/auto-kill machinery.

Historical negative evidence reinforced:

- `EXP-0006` remains `REVISE`, not validation of the lexical retriever;
- permanent supervisor/blackboard identity, process watchers, old sentinel heuristics, remote-authority/classifier coupling and legacy agents-table ownership machinery should not be restored wholesale.

Explicit unresolved records:

- `SYN-0004` remains `UNKNOWN`: its body still lacks enough linked IDs/evidence to establish what fix was approved/lost/recovered;
- `EXP-0007` remains `UNKNOWN`: status `PROPOSED`, result pending; it is not validation of a startup idea-scouting cadence.

The checked-in aggregate legacy task graph did not expose current `RETIRED`, `ABANDONED`, `BLOCKED`, or `READY` task states during the bounded pass. Do not invent abandoned-task cases merely to satisfy an archaeology checklist.

This report is enough to **pause broad active archaeology**. Future archaeology should be targeted only when a concrete unresolved claim such as `SYN-0004` materially affects a decision. `UNKNOWN` is an acceptable final evidence state when the archive does not support a stronger conclusion.

---

# 5. What should come next

The next work should close evidence/lineage gaps **before** adding broader autonomy or self-refinement.

## NEXT A — Explicit execution lineage and communication coverage

Priority: `NEXT / P1` after relevant harness branches are accepted or their final interfaces are known.

Problem:

Current evidence can identify task/run facts, but full reconstruction still cannot reliably answer which provider session/helper/recovery replacement produced each action without gaps. Legacy evidence also shows reviewer/request drops and “process alive but provider blocked” states create coordination failures that liveness alone cannot explain.

Smallest target:

```text
task
→ immutable run
→ worker
→ provider session binding
→ helper/child invocation
→ recovery/replacement link
→ request/thread/addressee correlation where authoritative
→ operation/evidence refs
→ submission
```

Requirements:

- reuse canonical run/task/session/helper sources; no second authority database;
- explicit stable identifiers rather than timestamp/name inference;
- late attachment/replacement needs explicit reconciliation semantics;
- distinguish provider/API readiness from mere process/session existence;
- Run Record/trace must state `MISSING`/`UNKNOWN` coverage honestly;
- communication coverage must say which source was queried and whether attribution is complete;
- request/reviewer/thread lineage should be reconstructable where the source system provides authoritative metadata.

Unlocks:

- trustworthy explainable waits;
- stronger replay/Run Records;
- safe recovery compatibility;
- helper NO_PROGRESS evidence;
- better Layer 3 evaluation.

## NEXT B — Explainable waits as a derived projection

Priority: `NEXT/P2` once authoritative request/addressee/thread/session correlation exists.

Target:

```text
what is waiting
who/what it is waiting on
source request/thread/message ID
request time
known resume condition
provider/API readiness state when known
UNKNOWN where not derivable
```

A live process/session does not prove provider/API readiness, ownership, authority, or progress. Do not create a new wait authority plane or infer human intent from arbitrary message prose.

## NEXT C — Context Builder v2 evidence integrity

Priority: `NEXT/P2`, evaluation-first.

Preserve from legacy:

- exact Markdown section/code-symbol anchors;
- source hashes/watermarks;
- temporal/historical attribution;
- proof role;
- positive evidence and negative boundaries separately;
- source-drift reporting against frozen hashes;
- frozen holdouts;
- paraphrase/vocabulary-shift cases;
- abstention/no-answer quality;
- evidence references that mechanically resolve to the exact claimed event/anchor;
- acceptable-substitute credit only when that substitute was actually retrieved/proven, never because it would have been acceptable in theory.

Start with evidence-card **integrity**, not another retrieval algorithm.

The legacy lexical claim-card retriever is explicitly not the solution; see `DO NOT REVIVE` below.

## NEXT D — Complete the three-layer evaluation discipline

Priority: `NEXT/P2` after #33-#35 foundation is accepted.

Layer 1 is becoming strong through tests/frozen mechanical cases.

Still needed:

```text
Layer 2 — agent-quality regression
- implementation quality
- review quality
- context sufficiency
- Skill procedure quality
- recovery decision quality

Layer 3 — production/outcome sampling
- escaped defects
- rework
- operator-friction interventions
- recovery success
- duplicate work
- environment drift failures
- cost/runtime only when measured reliably
```

A major future benchmark should exercise an end-to-end MAPS scenario:

```text
orientation
→ safe first action
→ execution/delegation
→ interruption/recovery
→ independent review
→ completion/release
→ post-completion outcome
```

At least one Layer 3/end-to-end case must represent a **real external or operator-visible workflow**, not only an internal synthetic MAPS lifecycle round trip. This preserves the legacy lesson that inward infrastructure can look healthy while failing to demonstrate useful external work.

No single metric/layer proves the system improved.

## NEXT E — Controlled operational-learning lifecycle

Priority: `NEXT AFTER EVALUATION FOUNDATION`, not before.

Recovered target:

```text
operational observation/outcome
→ candidate lesson
→ evidence/provenance
→ independent review/promotion
→ scoped active guidance
→ selective projection when applicable
→ expiry/review-at
→ supersession/retirement
```

Required fields should include provenance, applicability/trigger, promotion authority, start, expiry/review date, supersession, and status.

Hard boundaries:

- observation is not policy;
- candidate lesson is not active guidance;
- promoted guidance must surface only where its applicability trigger matches rather than becoming permanent prompt clutter;
- observations may come from explicitly non-task/operator-directed work, but enter only as non-authoritative candidate evidence and do not import that work into task governance;
- temporary workarounds must expire;
- superseded guidance must stop projecting into startup/context;
- do not create a second policy database in disguise.

---

# 6. Triggered / later work

These capabilities remain useful options, but building them now would violate Lean's evidence/repetition/usage rules.

| Candidate | Trigger before implementation | Initial boundary |
|---|---|---|
| User-visible acquisition-path verification | task actually publishes/packages/installs/exposes an operator/user acquisition path, or repeated release-path failures justify a reusable review check | enumerate real reachable acquisition paths and verify them against intended immutable content/revision; derived review evidence only, no general artifact authority store |
| Git worktree isolation | concurrent writable agents become common or collisions are observed | one writable run → one attributable worktree; explicit integration/cleanup |
| Helper continuity | repeated same-task specialist reuse saves meaningful setup/context | task-scoped, TTL-bound, invalidated by incompatible revision/context |
| Helper `NO_PROGRESS` | real alive-but-stuck cases recur enough to measure | progress-sensitive advisory signal based on lack of meaningful advancement; measure false positives; no naive fixed timeout, auto-kill or auto-escalation |
| Deterministic `maps flow` | a lifecycle sequence is repeated, stable and well understood | fixed guarded sequence, not another workflow engine |
| Capability Packs | repeated Skill+tools+hooks+environment combinations become stable | packaging only; does not grant authority |
| Credential broker | remote/external execution needs secrets often enough for ad-hoc injection to become material risk | short-lived capability grants after canonical policy/scope checks |
| Sandboxes/containers/remote compute | reproducibility/isolation/resource-control need exceeds complexity cost | satisfy EnvironmentSpec; compute remains disposable |
| Snapshots/rehydration | environment startup/recovery cost justifies durable reconstruction | task truth remains outside snapshot |
| Time-travel/fork debugging | Run Records/transition semantics become complete enough to replay honestly | partial replay must remain explicitly partial |
| Semantic retrieval/query expansion | frozen paraphrase/hard-negative/no-answer eval beats explicit-first Context Builder materially | never promote because embeddings are fashionable |
| Thin Mission object | project/task dependencies demonstrably fail to represent multi-task intent | grouping/intent only; tasks remain execution authority |
| Scoped temporary halt delegation | concrete safety case requires bounded non-operator halt authority | disabled by default; explicit scope/grantor/expiry/reason |

---

# 7. Bounded audits, not permanent agents

Two recovered legacy mechanisms are worth keeping as **procedures**, not standing autonomous roles.

## 7.1 Phase-boundary discovery

Use after major phases/releases when useful:

- proposal-only;
- evidence-linked;
- distinguish fact/inference/proposal;
- check existing records before claiming novelty;
- no idea quota;
- no automatic implementation.

`EXP-0007` does **not** validate a fixed startup cadence; its result is pending. Do not cite it as evidence for a 14-day or other mandatory schedule.

## 7.2 System-adherence audit

Use periodically after substantial infrastructure changes to ask:

```text
Was it built as intended?
Is it cross-linked coherently?
Is production work actually using it?
Is a documented mechanism silently bypassed?
```

Findings enter normal task/review channels. The auditor does not silently repair or become process authority.

The parallel legacy-archaeology pass is itself an example of a bounded procedure, not a proposal for a permanent archaeology/discovery worker.

---

# 8. Design/review invariants recovered from legacy

These do not need a dedicated subsystem unless repeated failure proves one necessary.

## 8.1 Authority provenance

Citation does not ratify a proposal. Anything used as a consequential gate needs explicit decision/approval provenance.

## 8.2 Source-of-truth reconciliation

When one fact has multiple readers/copies, require one of:

1. one declared authority;
2. atomic mutation;
3. mechanical reconciliation/cross-check of derived views.

Review question:

> Who else reads this state, and which copy wins?

## 8.3 Durable state reachability

For every new durable state/field, define:

```text
how entered
how exited
how corrected
what happens after interruption/owner loss/session loss
how superseded/retired
```

## 8.4 Security/authority tests should assert behavior

Prefer executed/computed behavioral properties in isolation. Do not rely on source-string spelling unless the text itself is the property.

Privileged/cross-host lifecycle mutation deserves a security-framed review that separately considers trust binding and concurrency/atomicity; legacy `INS-0059` records real review catches in both areas.

## 8.5 Review policy changes require measurement

Do not weaken or strengthen independent review because of hypothetical validators or intuition. Use review-catch rate, escaped defects, rework, intervention, and validator-quality evidence.

## 8.6 Precondition ordering should become deterministic only when real

If a repeated process genuinely requires A before B, make the ordering mechanically visible. Do not add ceremony for dependencies Lean has already eliminated.

## 8.7 Evidence attribution is part of correctness

A correct aggregate count is not enough when its evidence references point to the wrong event/subject. Consequential evidence should be testable for both value **and attribution**.

---

# 9. Do not revive

These directions are explicitly excluded absent new evidence strong enough to reopen architecture review.

## 9.1 Legacy lexical claim-card retriever

Legacy `EXP-0006` ended `REVISE` and did not validate the old lexical retrieval implementation. Preserve exact anchors, hashes, drift reporting, temporal attribution, explicit negatives, frozen holdouts and blind scoring—not the retriever.

The bounded archaeology pass reconfirmed the poor treatment results: `17/41` exact-source accuracy, `7/41` anchored-evidence accuracy, and `2/5` negative abstention, plus later source-drift and substitute-credit corrections. Do not turn these failed metrics into retrospective validation.

## 9.2 Permanent discovery/process-police agents

Bounded discovery/adherence audits were useful. Continuous watcher roles are not justified.

## 9.3 Second task/session/review/policy authority store

Rejected. New mechanisms must reference/derive from existing canonical facts or explicitly reconcile them.

## 9.4 Large persistent `mapd`/Prime supervisor

Rejected by default. Provider-neutral harness mechanisms live below canonical task/policy authority.

## 9.5 Fixed permanent personality roster

Rejected as system architecture. Select workers/capabilities for tasks; procedures belong in Skills.

## 9.6 Giant knowledge graph/library by default

Rejected without a narrow measured retrieval/evidence problem.

## 9.7 Universal container/microVM per worker

Rejected until a threat/reproducibility requirement justifies the cost.

## 9.8 Automatic self-refinement/promotion

Rejected absolutely for policy/authority/safety/routing/persistent guidance changes.

```text
measurement → proposal
not
measurement → authority
```

## 9.9 Legacy supervisor/blackboard/swarm identity

Preserve durable state, explicit gates and handoff evidence; do not recreate an all-encompassing supervisor/blackboard subsystem identity around mechanisms Lean already separates cleanly.

## 9.10 Legacy sentinel/watcher heuristics and remote-authority coupling

Do not revive:

- old emergence-sentinel aggregate heuristics that confused mechanism-emitted events with task-level blockers/rework;
- remote authority-host/classifier coupling;
- agents-table ownership/FK machinery that current Lean does not need;
- release-time “emergence considered” checkbox as discovery machinery.

Preserve only their failure lessons: typed actor/subject attribution, safety denial is not a transient network error, validate mutation inputs, and ceremony is not evidence.

---

# 10. Historical audit status after the bounded parallel pass

The legacy audit never claimed every legacy file/task was deep-read. The follow-up PR #37 specifically covered the unresolved/system-relevant Insights/Syntheses/experiments and direct task/promotion chains called out by the audit.

Current residual `AUDIT REMAINS` is narrow:

1. `SYN-0004` — incomplete/TBD chain; exact approved/lost/recovered mechanism remains unsupported by the inspected evidence.
2. `EXP-0007` — proposed startup discovery cadence with `result: pending`; not validated evidence.
3. Any future legacy claim discovered while implementing a current capability that materially conflicts with the current invariant/candidate map.

Broad archaeology should now stop. Re-open targeted archaeology only when one of those unknowns would materially change architecture, authority, safety, or implementation priority.

Future results still resolve to one of:

```text
RECOVER AS CANDIDATE
FOLD INTO EXISTING CANDIDATE
ALREADY SOLVED IN LEAN
HISTORICAL / DO NOT REVIVE
UNKNOWN / AUDIT REMAINS
```

Unknown historical items do not block already-evidenced work unless they reveal a material conflicting invariant.

---

# 11. Recommended implementation order from here

Assuming current open PR interfaces survive independent review materially intact:

```text
A. review/merge or explicitly reshape current #20-#35 stacks
        ↓
B. explicit run/session/helper/recovery + communication lineage
        ↓
C. derived explainable waits / fuller trace + Run Record coverage
        ↓
D. Context Builder v2 evidence-integrity experiment
        ↓
E. complete Layer 2 + Layer 3 evaluation and end-to-end benchmark
        ↓
F. controlled operational-learning lifecycle
        ↓
G. candidate harness improvements only through frozen comparison + review
```

The user-visible acquisition-path check is a **risk-triggered side track**, not a prerequisite for lineage/evaluation. Triggered scaling tracks (worktrees, persistent helpers, snapshots, credentials, capability packs, deterministic flows) likewise branch off only when their own activation evidence exists.

This ordering deliberately puts **truth/evidence before autonomy**.

---

# 12. Definition of legacy-recovery completion

The bounded recovery program is now complete enough to pause broad active archaeology when judged against its intended scope:

- [x] major idea-bearing legacy collections have a durable reconciliation path through the original audit plus the targeted parallel pass;
- [x] unresolved MAP-relevant chains are classified or explicitly `UNKNOWN` with a reason (`SYN-0004`, `EXP-0007`);
- [x] every surviving candidate found by the bounded pass is represented here or folded into an existing master/detailed candidate;
- [x] already-solved behavior is marked so later agents do not rebuild it;
- [x] rejected/failed historical directions are named so they are not accidentally resurrected;
- [x] remaining implementation work has evidence/usage/repetition triggers and prerequisite order;
- [x] deletion/preservation of the top-level legacy tree remains a separate explicit operator decision and is not implied by roadmap completion.

This is **not** a claim that every historical file was semantically read line by line. It means additional broad archaeology has diminishing value relative to the now-classified implementation program. Targeted retrieval remains appropriate when a concrete future decision depends on unresolved historical evidence.

PR #37 should remain preserved as research/planning evidence. Its findings do not become runtime authority merely because they were reconciled here.
