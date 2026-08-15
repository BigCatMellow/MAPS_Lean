# Active development handoff — 2026-08-15

Status: `WORKING NOTES — NOT ACTIVE AUTHORITY`

Purpose: preserve enough exact implementation state that a fresh agent can continue MAPS Lean development after a context reset without rediscovering the design, guessing about authority boundaries, or repeating already-completed work.

Canonical repository instructions, code, SQLite task/policy state, PR state, and independently reviewed/merged decisions remain authoritative. This file is coordination context only.

---

# START HERE

Repository:

`BigCatMellow/MAPS_Lean`

Merged `main` head when this handoff was refreshed:

`086e066f723d793273441dd52b500e62ac981deb`

The long implementation session has stopped deliberately after completing and validating **PR #34 — frozen regression case v1**.

Current newest implementation stack:

```text
main
  ↓
PR #33  portable Run Record v1
  ↓
PR #34  frozen regression case v1
```

PR #34:

- branch: `agent/frozen-regression-case-wave2`
- base: `agent/portable-run-record-wave2`
- implementation/CI head: `3baa0eabb42d6ab89e2d681fda1a297f994084ce`
- task-validation/documentation head after CI: `f803cd24e5acbd3630075b3f316535ba50540b0b`
- full Runtime stack CI: `31899393298` — **SUCCESS**
- task file: `work/tasks/frozen-regression-case-wave2.md`
- task state: `READY_FOR_REVIEW`
- PR remains **draft** and requires independent review before completion/merge.

**Do not self-approve, mark ready, or merge PR #34 or any upstream draft PR merely because CI is green.**

Recommended next implementation candidate:

> **Comparative evaluation/reporting v1 over frozen regression cases**, stacked on PR #34, with no automatic promotion or self-modification.

Before starting it, read:

1. `AGENTS.md`
2. this handoff
3. `work/tasks/frozen-regression-case-wave2.md`
4. `work/tasks/portable-run-record-wave2.md`
5. `work/roadmaps/agent-harness-capabilities/05-learning-and-evaluation.md`
6. `work/roadmaps/prime-agent-capability-roadmap.md`

---

# Operator direction that remains in force

- Continue implementation while upstream draft PRs await independent review **when the dependency is explicit and the next task does not require the review result**.
- Use stacked PRs for unmerged dependencies and make the base branch visible in the task file/PR body.
- Independent review is a completion/merge gate, not automatically an implementation-start gate.
- Do not self-approve, mark ready, or merge review-gated work.
- Preserve useful mechanisms/invariants; do not rebuild Prime or legacy MAPS complexity.
- Ordinary operational work: concise, simple, smallest sufficient action.
- Roadmaps/architecture plans: comprehensive and explicit.
- No material assumptions. Inspect evidence or stop/escalate rather than guess.
- Keep durable checkpoint/handoff notes during long sessions.

Core design rule:

> **Do not ask intelligence to solve what deterministic mechanisms, packaging, interface design, reproducibility, or evidence can solve more reliably.**

---

# Current development topology

## A. Harness / security stack

```text
main
→ PR #20  agent/harness-foundation-wave1
→ PR #21  agent/hcom-hooks-wave1
→ PR #22  agent/harness-service-wave1
→ PR #23  agent/harness-canonical-guard-wave1
→ PR #24  agent/agentic-security-baseline-wave1
```

All are draft/review-gated. Their implementation tranches are CI-green.

### PR #20 — typed provider-neutral Harness contracts

Implemented:

- `OperationResult`
- `ExecutionBinding`
- `SessionRef`
- `SessionStatus`
- explicit normalized session states
- retry-safety semantics
- `HarnessAdapter` protocol
- explicit `UNKNOWN` for unprovable provider state

Implementation commit: `5d408fc4c9fef165da3478e86bab3bd964470429`

CI: `31893719145` — success.

Invariant:

> Harness describes **how** an operation is performed. It does not decide **whether** the task is authorized.

### PR #21 — hcom normalization + deterministic Hooks

Implemented:

- normalized hcom `inspect`, `send`, `stop`;
- explicit no-match vs provider failure semantics;
- exact session/project binding;
- deterministic Hook registry;
- directives: `ALLOW`, `DENY`, `REQUIRE_APPROVAL`, `ANNOTATE`;
- fail-closed behavior for configured Hook failures.

Implementation commit: `cca097e69401bf7d79f753970c249c0ed86da3ec`

CI: `31894920245` — success.

Invariant:

> Hooks can narrow/block; they cannot manufacture task authority or operator approval.

### PR #22 — HarnessService

Implemented provider-neutral service over adapters + Hooks with exact binding/session correlation and conservative mutation reporting.

Implementation commit: `96c614846314ea604be95df9feed5c7e3b477b62`

CI: `31895128908` — success.

### PR #23 — canonical run/lease/session guard

Implemented read-only `CanonicalRunGuard` over canonical task/run evidence.

Implementation commit: `6c6eeeb050a3bc102250bafba9a849bab1e82b04`

CI: `31895412303` — success.

Continuation (`start/send/resume`) requires current task revision, ACTIVE task, correct claimant, live lease, and non-stale run/context. Stop is intentionally different: a stale known session may need cleanup, but historical identity verification does not revive authority.

### PR #24 — initial executable agentic security baseline

Current branch head at handoff refresh:

`923bc9bb5d5a422618cd1a2097708d45d7bb4536`

Current full Runtime stack CI:

`31898860232` — success.

Implemented adversarial properties include:

- prompt/tool text cannot fabricate operator approval;
- continuity-linked identities cannot become independent reviewers;
- stale session cannot resume after task revision change;
- provider liveness cannot override expired canonical lease;
- peer/message text cannot transfer canonical ownership;
- provider inspection cannot renew canonical heartbeat/lease;
- deterministic `BEFORE_RESUME` Hook closes the previous resume gap.

`work/security/AGENTIC_THREAT_MODEL.md` is descriptive/test-oriented, **not policy authority**.

Unresolved Harness boundary:

> durable late session attachment/replacement/helper lineage remains intentionally unresolved. Do not create a hidden mutable second session authority.

---

## B. Skills stack

```text
main
→ PR #25  Agent Skills format / progressive loading
→ PR #26  Skills catalog + provenance read model
→ PR #27  frozen Skill-selection evaluation corpus
→ PR #31  static Skill quality/security gate
```

### PR #25 — Skills format foundation

Implements standard-style Skill directories, minimal discovery metadata, progressive body loading, resource inventory, deterministic whole-directory hash, and drift detection.

No routing or execution authority.

### PR #26 — Skills catalog/provenance

Adds provenance-aware catalog/read model and explicit trust/source metadata without making catalog state task authority.

### PR #27 — frozen Skill-selection benchmark

Implementation commit:

`7175282c25584761f52059b36282c1f062d185c0`

Validation-record head:

`f6d6685b4396829cc71e67144a3ca0951f1d8b52`

CI:

`31897351677` — success.

Task:

`work/tasks/skills-selection-eval-wave2.md` → `READY_FOR_REVIEW`

Frozen corpus:

- five synthetic candidate Skills;
- 24 cases;
- categories: direct, paraphrase, vocabulary shift, near miss, hard negative, no-Skill, multi-Skill, ambiguity;
- prediction outcomes: `SELECT`, `ABSTAIN`, `AMBIGUOUS`;
- exact-case, precision/recall/F1, abstention, ambiguity, false-activation, missed-activation, and category metrics.

Critical boundary:

> The evaluator scores predictions produced elsewhere. It contains **no production Skill selector** and cannot activate a Skill.

### PR #31 — static Skill quality/security gate

Implementation commit:

`d3d186dbd0903eacd4dbe715335bf2560b1c74d3`

Validation-record head:

`e45d74a256d9f215fee49cff8abeb0ac3dfaaf38`

CI:

`31898263690` — success.

Task:

`work/tasks/skills-quality-gate-wave2.md` → `READY_FOR_REVIEW`

Static gate dispositions:

- `CLEAR`
- `REVIEW_REQUIRED`
- `QUARANTINE`

**None means approved or trusted.**

Static checks catch/flag executable resources, binary/non-UTF8/oversized resources, vague descriptions, persona-heavy instructions, privilege/destructive/environment/network behavior, secret literals, authority-override claims, sensitive key/credential resources, and remote-pipe-to-shell patterns.

Unresolved Skills boundaries:

- no production routing yet;
- no persistent Skill approval/trust/quarantine authority lifecycle yet;
- no auto-update/import trust;
- no automatic promotion from eval results.

---

## C. Environment / reproducibility stack

```text
main
→ PR #28  EnvironmentSpec v1
→ PR #29  EnvironmentFingerprint + compatibility v1
→ PR #30  append-only run environment evidence
```

### PR #28 — EnvironmentSpec v1

Implementation commit:

`21622438602bc22a70c3dc735c1d918a45463171`

Validation-record head:

`6128ef94334b1868677430d65724628d19bb8b70`

CI:

`31897492718` — success.

Task:

`work/tasks/environment-spec-wave2.md` → `READY_FOR_REVIEW`

Implements strict JSON environment requirements, semantic hash, runtime/tool/setup/maintenance/validation/network/service/credential-capability/dependency-input description.

Unknown fields fail closed. Commands are data only and are not executed by this layer. Secret values are not stored.

### PR #29 — EnvironmentFingerprint / compatibility v1

Implementation commit:

`6d639380fe3683745611dc0092edb0ec9b30414a`

Validation-record head:

`620834a0db9cce7e2de3d4750c98f1c49687ccdd`

CI:

`31897745175` — success.

Task:

`work/tasks/environment-fingerprint-wave2.md` → `READY_FOR_REVIEW`

Compatibility states:

- `COMPATIBLE`
- `COMPATIBLE_WITH_WARNINGS`
- `DRIFTED`
- `INCOMPATIBLE`
- `UNKNOWN`

Unknown material evidence stays unknown. Fingerprint does not dump arbitrary environment variables or secret values; credential requirements are caller-supplied capability availability only.

### PR #30 — append-only run environment evidence

Implementation commit:

`cf47e82f58586091becc5d298f27833ae97f0aac`

Validation-record head:

`862e8bebe852ed6cea4ad0fd69c8bcc4c4251955`

CI:

`31898071184` — success.

Task:

`work/tasks/environment-run-evidence-wave2.md` → `READY_FOR_REVIEW`

Adds append-only `run_environment_evidence` beside immutable `run_manifests`; **does not modify run contracts or task authority**. Trace can project this evidence under the exact run.

Important persistence rule:

If normalized environment evidence contains text recognized as sensitive, recording fails rather than silently redacting the hashed EnvironmentSpec snapshot.

Unresolved Environment boundaries:

- compatibility is evidence, not execution/recovery authority;
- no automatic environment-driven resume/recovery;
- no setup/validation command runner outside Harness/Hook authority;
- no container/sandbox platform imposed by default.

---

## D. Review/evidence correctness

### PR #32 — immutable consequential review subject binding

Branch:

`agent/review-subject-binding-wave2`

Independent from `main`.

Initial implementation commit:

`1bf786995336a088e465028932720664dac699f7`

Corrected implementation commit:

`fde24736323cdd196309fb753422e053399e9171`

Validation-record head:

`489a2524b513d6d9ab5eb186874cbc04e6e4ba4a`

Initial CI:

`31898581152` — failed because the new subject check changed established criterion-verification error precedence.

Corrected CI:

`31898786757` — success.

Task:

`work/tasks/review-subject-binding-wave2.md` → `READY_FOR_REVIEW`

Implemented:

- immutable one-to-one `review_subjects`;
- task/submission/revision/run/artifact identity binding;
- v1 immutable artifact refs only: `sha256:<64 hex>` or `git:<40/64 hex>`;
- freshness modes: `REVISION_BOUND`, `REDERIVED_AT_REVIEW`, `NON_CONSEQUENTIAL`;
- consequential approval requires exact freshness evidence;
- ordinary low-risk/unflagged reviews retain the existing simple path;
- approval validation occurs inside the existing review transaction;
- stale submission/task revision/run/criterion mismatch blocks approval;
- trace exposes exact review subject.

Important CI-driven correction:

Existing criterion completeness checks keep their established precedence. When all current criterion claims are complete/confirmed and identify one exact current run/revision, MAPS derives the overall `REVISION_BOUND` review subject atomically instead of forcing redundant manual binding.

Invariant:

> A review subject identifies what was reviewed. It does not grant reviewer/operator/task authority.

---

## E. Learning / evaluation stack — newest work

```text
main
→ PR #33  portable Run Record v1
→ PR #34  frozen regression case v1
```

### PR #33 — portable Run Record v1

Branch:

`agent/portable-run-record-wave2`

Implementation commit:

`f2eb44a1cf180a2e58de85904eafb891df75bf7c`

Validation-record/current stacked base head:

`3d618a4d74d8be4ba42e119cc5d659e204ccd9d5`

CI:

`31899074481` — success.

Task:

`work/tasks/portable-run-record-wave2.md` → `READY_FOR_REVIEW`

Implemented:

- `build_run_record(source, task_id, run_id)` over existing sanitized `trace_task()`;
- exact run selection;
- deterministic record ID/content SHA;
- structural task/policy/run/context/submission/review/criterion/outcome/event evidence;
- free-text task/review/event/outcome prose omitted by default and replaced by bounded presence/length metadata;
- context contents omitted; path/hash refs retained;
- outcomes split into exact run-bound vs task-unbound;
- task-level review/timeline joins labeled `UNKNOWN` unless exact structured evidence resolves them;
- explicit coverage states: `VERIFIED`, `SOURCE_LOCAL`, `MISSING`, `UNKNOWN`;
- replay explicitly `complete: false`;
- read-only CLI: `python -m runtime.cli run-record TASK_ID RUN_ID`.

Critical boundary:

> Portable does not mean complete replay. Missing provider/session/helper/recovery/operation trajectory sources stay visibly missing/unknown.

### PR #34 — frozen regression case v1 — LAST COMPLETED WORK

Branch:

`agent/frozen-regression-case-wave2`

Base:

`agent/portable-run-record-wave2`

Implementation/CI head:

`3baa0eabb42d6ab89e2d681fda1a297f994084ce`

Task-validation/documentation head:

`f803cd24e5acbd3630075b3f316535ba50540b0b`

CI:

`31899393298` — success.

Task:

`work/tasks/frozen-regression-case-wave2.md` → `READY_FOR_REVIEW`

Implemented:

- explicit incident taxonomy including tool/context/routing/helper/recovery/environment/review/validator/authority/ACI/supply-chain/operator-friction/unknown categories;
- `freeze_regression_case()` requires:
  - validated Run Record v1;
  - explicit incident category;
  - explicitly sanitized bounded fixture;
  - structured expected-property IDs;
  - freezer identity;
  - optional structured tags;
- revalidates Run Record content hash before freezing;
- rejects sensitive fixtures using existing MAPS sensitive-text detector;
- deterministic case ID/content SHA with no clock timestamp;
- embeds the already-sanitized Run Record so the case is portable/self-contained;
- preserves `replay.complete: false`;
- explicitly records `promotion.automatic = false`;
- CLI `freeze-case` reads fixture from file/stdin to avoid putting incident text in shell history;
- CLI emits JSON and does not mutate canonical task state.

Not implemented:

- no incident classifier;
- no replay engine;
- no comparative evaluator yet;
- no persistent corpus authority/database;
- no automatic harness/policy/routing change;
- no self-promotion.

---

# Major invariants that must survive context loss

1. **One authority per fact.** Do not create duplicate mutable task/run/session/review truth.
2. **Capability is not authority.** Tool availability, Skill capability, provider session, or successful Hook does not grant task permission.
3. **Session liveness is not task truth.** Live provider state cannot revive ownership/lease/revision.
4. **Hooks can block/narrow, never create missing authority.**
5. **Citation is not ratification.** Repetition/retrieval does not promote memory/guidance into policy.
6. **Persistent memory needs trust/lifecycle states.** Do not build one undifferentiated memory bucket.
7. **Review must bind fresh/exact evidence for consequential actions.**
8. **Partial replay must never claim complete replay.**
9. **Environment compatibility is evidence, not recovery authority.**
10. **`CLEAR` Skill scan is not Skill approval.**
11. **Frozen case/eval success cannot self-authorize harness/policy/routing changes.**
12. **Real failures should become frozen regression evidence before harness changes are promoted.**
13. **Better interfaces often matter as much as smarter models.** Prefer deterministic ACI/result semantics over more prompting where possible.
14. **No permanent agents/daemons/watchers without demonstrated need.**
15. **Do not import community Skills/tools blindly.** Treat them as supply-chain artifacts with provenance/review/eval.

Mechanism hierarchy:

| Problem | Preferred mechanism |
|---|---|
| Something must always happen | Hook / invariant |
| Reusable procedure | Skill |
| Perform concrete operation | Tool/script |
| Repetitive stable orchestration | Flow |
| Need facts | Context/source |
| Need judgment/exploration | Agent/helper |
| High-impact permission | Policy/operator |
| Improve future behavior | Outcome → frozen evidence → eval → reviewed promotion |

---

# Explicitly deferred / unresolved

Do **not** casually solve these by adding machinery:

- durable late session attachment/replacement/helper lineage;
- persistent Skill approval/trust/quarantine lifecycle;
- production Skill routing;
- environment-driven automatic continuation/recovery;
- EnvironmentSpec command execution outside Hooks/Harness;
- generic artifact registry/acquisition path;
- complete provider/session/helper/recovery operation trajectory;
- autonomous incident classification;
- autonomous self-modification/promotion.

Also continue to avoid by default:

- large `mapd` daemon;
- giant knowledge graph/Library revival;
- fixed agent roster/persona bureaucracy;
- WezTerm-dependent orchestration;
- provider-specific permanent identities;
- continuous discovery/process watcher agents;
- Temporal/Cedar/A2A/Firecracker rewrites without demonstrated need;
- legacy lexical retriever;
- blindly loaded MCP/tool universe;
- universal planner/editor split.

---

# Recommended next task

## Comparative evaluation/reporting v1 over frozen cases

Create a new stacked branch from:

`agent/frozen-regression-case-wave2`

Suggested branch:

`agent/regression-evaluator-wave2`

Goal:

Build a **model/provider-agnostic evaluator/reporting layer** that consumes frozen case artifacts plus externally produced candidate results and compares expected-property outcomes without executing tasks or promoting changes.

Suggested v1 boundary:

- validate frozen case identity/hash before evaluation;
- accept candidate identity/version/config hash as descriptive evidence;
- accept externally supplied property results such as `PASS`, `FAIL`, `UNKNOWN`, `NOT_RUN`;
- require results for expected properties or report explicit incompleteness;
- aggregate per-case and corpus-level pass/fail/unknown/regression metrics;
- optionally compare baseline vs candidate when both result sets refer to the exact same frozen case IDs;
- classify `improved`, `regressed`, `unchanged`, `incomplete` mechanically from supplied property results;
- preserve case/category/tags for slicing;
- report cost/latency only if supplied as explicit measured data; never guess;
- deterministic report identity/hash;
- no model/provider calls in evaluator;
- no task execution;
- no automatic promotion;
- no writing canonical MAPS state;
- no “winner becomes production” behavior.

Promotion must remain:

```text
frozen cases
→ candidate results
→ comparative report
→ proposal
→ independent review / operator gate where required
→ promotion
```

Not:

```text
better score → automatic self-modification
```

Before implementing, create a new `work/tasks/...md` with exact change boundary and stop conditions.

---

# Exact continuation checklist

A fresh agent should:

1. Read `AGENTS.md`.
2. Read this handoff.
3. Inspect PR #34 and verify it is still open/draft and its dependency/base has not materially changed.
4. Inspect current `main`; if it advanced, do not assume this handoff overrides it.
5. Inspect `work/tasks/frozen-regression-case-wave2.md` and PR #34 CI/review state.
6. If PR #34 remains CI-green and no upstream review changed its contract, create `agent/regression-evaluator-wave2` from `agent/frozen-regression-case-wave2`.
7. Shape the comparative-evaluator task before coding.
8. Keep evaluator pure/read-only and provider/model agnostic.
9. Use frozen case IDs/hashes as the evaluation join key; never fuzzy-match cases.
10. Run focused tests and full Runtime stack CI.
11. Keep the PR draft and require independent review.
12. Add/update a durable checkpoint before context grows large.

If review feedback arrives on any upstream PR, address that feedback first when it materially affects a downstream contract; then rebase/reshape dependent branches as needed.

---

# Quick PR index

- #19 — merged foundation / preservation work now represented in `main`
- #20 — typed Harness contracts
- #21 — hcom normalization + Hooks
- #22 — HarnessService
- #23 — canonical run/lease/session guard
- #24 — agentic security adversarial baseline
- #25 — Agent Skills format foundation
- #26 — Skills catalog/provenance
- #27 — frozen Skill-selection evaluation
- #28 — EnvironmentSpec v1
- #29 — EnvironmentFingerprint/compatibility
- #30 — append-only run environment evidence
- #31 — static Skill quality/security gate
- #32 — immutable consequential review subject binding
- #33 — portable Run Record v1
- #34 — frozen regression case v1 **(last completed tranche)**

All #20–#34 are review-gated draft work unless GitHub state has changed after this handoff; verify current PR state before acting.
