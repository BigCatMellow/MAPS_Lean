# Independent review progress — 2026-08-15

## Purpose

This note records the independent-review lane's current technical findings and integration state so another agent can resume without reconstructing the full review session.

This reviewer has not implemented fixes on any reviewed implementation PR. Findings were recorded on GitHub and repaired work was re-reviewed on new exact heads. Because the connected GitHub identity is also the PR author, GitHub refuses formal `APPROVE` / `REQUEST_CHANGES` states on these PRs; clean/blocking conclusions are therefore stored as exact-head non-approval review comments. They are technical review evidence, not a substitute for any repository rule requiring a distinct GitHub reviewer identity.

## Current accepted main

Latest accepted `main` observed in this lane:

- `c9e52cfcea2afd6c1fab3956baedcf62117450af`
- latest merge: PR #23 — canonical run guard

Merged/accepted Wave 1 sequence so far:

- #20 harness foundation — merged
- #21 hcom normalization + Hook registry — merged
- #22 provider-neutral HarnessService — merged
- #23 canonical run guard — merged

PR #24 is technically cleared but remains open/draft at this checkpoint.

---

## Harness / security / lineage

### PR #24 — initial agentic security baseline

**Status: TECHNICALLY CLEARED / OPEN / DRAFT.**

Current exact head:

- base: `main@c9e52cfcea2afd6c1fab3956baedcf62117450af`
- head: `3be75c654051d27ad9beaf7d2620953f1e28d9ee`
- Runtime CI #236 / `31924470699`: PASS
- clean technical review ID: `4945310420`

Independent review originally found two material issues:

1. canonical run guarding was optional composition at the public `HarnessService` mutation boundary;
2. the first mandatory-enforcement implementation trusted a caller-controlled callback marker and was impersonable.

Final reviewed repair:

- public `start/send/resume/stop` fail closed when canonical enforcement is absent;
- enforcement membership is registry-owned rather than derived from callback attributes;
- ordinary ALLOW Hooks cannot satisfy canonical enforcement;
- fake callbacks carrying an apparent `CANONICAL_RUN` marker do not count;
- canonical composition requires exact `CanonicalRunGuard` type at the supported composition root;
- mandatory guard Specs remain `READ_ONLY` + `FAIL_CLOSED`;
- stale checkpoint/handoff files were removed from the PR delta;
- merged #23 adapter-qualified/bare-ID fail-closed behavior is preserved.

The remaining underscored registry composition helper was not treated as an attacker boundary: arbitrary code deliberately invoking private in-process Python internals would amount to arbitrary runtime-code execution, outside this tranche's public Hook-composition model.

Next action: integration/operator lane may merge #24 under repository rules. After merge, downstream branches must synchronize to the new main before final review.

### PR #48 — adapter-qualified run/session lineage A1

**Status: OPEN / BLOCKED.**

Current exact head:

- base: `agent/agentic-security-baseline-wave1@3be75c654051d27ad9beaf7d2620953f1e28d9ee`
- head: `13b3293781a43980066f642edb79cf7f4528d4aa`
- Runtime CI #248 / `31924691827`: PASS
- current blocking review ID: `4945315597`

Core append-only mechanics reviewed as sound:

- immutable `run_manifests` remain untouched;
- `run_session_links` are append-only;
- writer rechecks immutable run worker, ACTIVE claimant, live lease, and current task revision inside `BEGIN IMMEDIATE`;
- replacements name the exact current predecessor link ID;
- SQLite rejects branching, cross-run predecessors, UPDATE, and DELETE;
- resolver preserves `UNBOUND`, `ADAPTER_UNPROVEN`, `EXPLICIT`, and `INVALID` instead of guessing;
- Trace remains derived and explicitly incomplete for external coverage.

**HIGH blocker — provider identity is under-scoped.**

A1 currently freezes provider identity as global `(adapter_id, session_id)`:

- `run_session_links` has no project/provider-context identity;
- uniqueness is `UNIQUE(adapter_id, session_id)`;
- writer duplicate lookup uses only adapter + session;
- resolver current/history expose only adapter + session;
- canonical guard compares only those lineage fields after resolving the run.

Accepted `SessionRef` and `HcomHarnessAdapter` are project-scoped, and low-level hcom is scoped by configured `HCOM_DIR`. Two legitimate projects may therefore each have their own `hcom/S1`; current A1 falsely treats them as the same durable provider session and rejects the second binding.

This is not currently a cross-project mutation bypass because HarnessService/task/binding checks separately constrain project, but it is still a foundational identity-model blocker: the durable A1 schema encodes a false global uniqueness fact and cannot represent the provider-neutral identity it claims to make exact.

Required direction: scope durable provider identity mechanically to the canonical provider/project context without creating a second mutable project authority; scope uniqueness accordingly; preserve the context in resolution; verify it against `SessionRef` / current run context; add two-project same-session-ID and project-mismatch adversarial tests.

The move from blocked head `2541bae...` to current `13b329...` changed only the task document, so the runtime blocker remains exact-current.

---

## Portable Run Record / evaluation stack

### PR #33 — portable Run Record v1

**Status: SUBSTANTIVELY CLEAN REPAIR / INTEGRATION FRESHNESS OPEN.**

Current exact head: `8ce0cf03998ed22b926612a171ee8cbe8554a6b3`

- Runtime CI #223 / `31924139475`: PASS
- clean remediation review ID: `4945303783`

Prior blockers are fixed:

- criterion claims are filtered to the selected run and verdicts only follow selected-run claims;
- unrelated-run review subjects no longer upgrade selected-run review-subject coverage to `VERIFIED`.

Run-level vs task-level uncertainty remains explicit; replay stays `complete:false`; raw/private free text remains omitted.

Remaining gate: branch is still based on older `main@1652d515...`. Synchronize to then-current accepted main, rerun CI, and exact-head review before merge.

### PR #34 — frozen regression case v1

**Status: SUBSTANTIVELY CLEAN DOWNSTREAM LAYER / UPSTREAM INTEGRATION OPEN.**

Current exact head: `4532ccffd00122e4236e91ca3cb2f52aac8127b8`

- based on current #33 head
- Runtime CI #226 / `31924211899`: PASS
- clean downstream review ID: `4945304143`

Earlier type-confusion concern is fixed:

- requires `record_kind == MAPS_PORTABLE_RUN_RECORD`;
- validates required v1 shape;
- validates self ID/hash;
- preserves partial replay semantics;
- adversarial tests reject wrong artifact kind and incomplete shape.

### PR #35 — comparative frozen regression evaluator

**Status: SUBSTANTIVELY CLEAN DOWNSTREAM LAYER / UPSTREAM INTEGRATION OPEN.**

Current exact head: `350fdbab03dcc84dcba6dba7f3fbd42844cda0d1`

- based on current #34 head
- Runtime CI #230 / `31924356114`: PASS
- clean downstream review ID: `4945304511`

Earlier baseline/candidate provenance concern is fixed:

- evaluator now requires immutable configuration refs (`sha256:` / `git:`);
- free-form `candidate-latest` style identity is rejected;
- reports preserve exact configuration refs and report IDs/hashes;
- same frozen corpus is used for baseline/candidate;
- UNKNOWN / NOT_RUN remain distinct;
- promotion remains explicitly non-automatic.

---

## Skills stack

### PR #25 — Agent Skills format foundation

**Status: SUBSTANTIVELY CLEAN REPAIR / INTEGRATION FRESHNESS OPEN.**

Current exact head: `378b66dda487bfe956499a0167dc46cfd2b4cb5d`

- Runtime CI #243 / `31924603714`: PASS
- clean remediation review ID: `4945313697`

Prior activation TOCTOU is fixed:

- `load_skill()` builds one byte snapshot;
- hashes those exact bytes;
- validates them against discovered `content_sha256`;
- parses the body from the same verified `SKILL.md` bytes;
- adversarial test changes `SKILL.md` after the read and proves activation uses the verified snapshot while the next activation rejects drift.

Still needs synchronization to then-current main before final merge review.

### PR #26 — Skills catalog provenance read model

**Status: BLOCKED — DESTRUCTIVE ANCESTRY / INTEGRATION DEFECT.**

Current exact head: `25c169d89cb1295eed05c9ea88201a62d69b67a3`
Current base: #25 head `378b66dda487bfe956499a0167dc46cfd2b4cb5d`

- Runtime CI #247 is green but misleading for integration safety.
- blocking review ID: `4945314672`

Exact current base→head compare shows #26 is not a catalog-only child of repaired #25. It removes accepted upstream harness files and tests:

- `runtime/harness/__init__.py`
- `runtime/harness/protocol.py`
- `runtime/harness/types.py`
- `tests/test_harness_types.py`
- `work/tasks/harness-foundation-wave1.md`

while adding catalog files.

This is ancestry/synchronization damage, not a catalog-logic defect. The catalog layer itself was substantively clean.

Required correction: rebuild/synchronize #26 from the exact current #25 head while preserving all upstream files; exact #25→#26 delta must contain only intended catalog/provenance changes. Fresh CI + exact review required afterward.

### PR #27 — frozen Skill selection evaluation corpus

**Status: OWN EVALUATOR LAYER CLEAN / BLOCKED BY #26 INTEGRATION.**

Current exact head: `bf42e87b5b27d27cffada5f136e8df688aeef8a6`

- Runtime CI #249 / `31924714404`: PASS
- clean remediation review ID: `4945314111`

Prior precision defect is fixed: false Skill selections on expected-ABSTAIN cases now enter the false-positive denominator and directly lower selection precision/F1, while `false_activation_cases` remains a separate safety metric.

Final review cannot proceed until corrected #26 ancestry propagates.

### PR #31 — static Skill quality/security gate

**Status: BLOCKED; DOWNSTREAM STACK ALSO STALE.**

Current head observed: `ace6131845c729937dee1c6fcfedc8914c4024cb`

Independent blocker remains: report `content_sha256` is not mechanically bound to all bytes actually scanned. Gate code independently rereads frontmatter/resources after upstream verification; report can therefore name one Skill identity while scanning later bytes.

Required direction: assess one stable snapshot (or prove exact post-scan revalidation over all scanned bytes), with adversarial mutation-between-verification-and-scan tests.

It also remains based on an older #27 head and must propagate corrected #25→#27 ancestry before final review.

---

## Environment / reproducibility

### PR #28 — EnvironmentSpec v1

**Status: BLOCKED.**

Head: `6128ef94334b1868677430d65724628d19bb8b70`

Independent blocker: no-credential-value enforcement applies to `secrets.required_names` but not persistent setup/maintenance/validation command strings. Credential literals can become normalized spec/hash material.

Required direction: reject likely credential material in persistent free-form command strings using bounded sensitive-text detection or an equivalently narrow mechanical rule; reject rather than redact hashed contract bytes.

### PR #29 — environment fingerprint / compatibility

**Status: BLOCKED; DOWNSTREAM OF #28.**

Head: `93e63fb49fb5bbcebb3002ff17cada6fc02fdbc3`

The earlier static symlink escape was improved, but a check/use race remains: containment is validated and then the dependency file is later reopened normally. Replacement with an external symlink between validation and read can escape.

Required direction: containment-safe open/hash semantics bound to the verified object, with an adversarial replacement race test.

### PR #30 — append-only environment evidence

**Status: NO OWN SUBSTANTIVE BLOCKER; BLOCKED BY #28/#29.**

Head: `b7599bc71e7e0f55118ad4708a2a21ac0c6ae1b0`

Environment compatibility remains append-only derived evidence, not task/recovery authority. Final review waits for repaired upstream ancestry.

---

## Review freshness

### PR #32 — immutable review subjects

**Status: BLOCKED.**

Head: `489a2524b513d6d9ab5eb186874cbc04e6e4ba4a`

Independent blocker: consequential `REVISION_BOUND` review may be satisfied by `run_id` alone, without immutable output/artifact references. Run identity proves execution contract, not the exact final reviewed bytes.

Required direction: consequential review subjects must bind immutable reviewed output/evidence identity (run ID may remain extra provenance); automatic criterion-derived consequential subjects must meet the same requirement or remain unable to approve.

---

## Legacy / planning / research

### PR #36 — legacy-recovery reconciliation

**Status: PLANNING TRUTH STALE / CHANGES REQUIRED.**

Current-state sections still describe an older repository baseline. Refresh only live integration/review status against accepted main/current PRs; preserve the architecture/classification unless facts actually change.

### PR #37 — bounded legacy archaeology

**Status: SUBSTANTIVELY CLEAN RESEARCH EVIDENCE / NEEDS SYNC.**

Load-bearing archaeology claims were independently spot-checked and supported. This is a dated research snapshot, not a live current-state map.

### PR #38 — execution-lineage design

**Status: DESIGN BLOCKER.**

The design correctly recognizes project/provider-qualified session identity but older replacement-chain design used bare predecessor session IDs. Exact lineage must use full provider-scoped identity or a stable internal link identity.

PR #48's stable predecessor link IDs improve the chain-predecessor half, but #48 still has the separate project/provider-context identity blocker described above.

---

## Wave 3 evaluation / communication / learning

### PR #39 — Context Builder evidence-integrity corpus

**Status: BLOCKED.**

`CBI-010` permits a baseline document about implementation state as an acceptable substitute for an authorization-status query. Implementation state does not prove authorization state.

### PR #40 — Layer 2 / Layer 3 benchmark protocol

**Status: SUBSTANTIVELY CLEAN / NEEDS SYNC.**

Layer separation, external-authority requirements, non-tradeable blockers, uncertainty, and no-auto-promotion semantics were coherent.

### PR #41 — Stage 1 Context Builder evidence projector/scorer

**Status: BLOCKED on current owner-hardening head `c997821c4a5f3d11c2bc7f8a98dd7a33750c3feb`.**

Current CODE_SYMBOL resolver still accepts `Owner.symbol` from independent substring matches (`class Owner` somewhere + `def symbol` somewhere) rather than structural ownership. Requires exact structural/AST resolution and adversarial wrong-owner/prefix tests. #39 remains an upstream blocker.

### PR #42 — benchmark result validation

**Status: BLOCKED on current owner-hardening head `beeef987e25509136ff3de5b79263c984cc501da`.**

Two blockers remain:

1. report binds only protocol version, not exact frozen protocol identity/content;
2. exact validated property/provenance evidence refs are discarded from output, so materially different evidence packages can collapse to indistinguishable reports.

The scorer does not itself need to become canonical-source authority; adapter-supplied VERIFIED provenance is an intentional boundary.

### PR #43 — operational-learning projection

**Status: RUNTIME/SEMANTICS CLEAN; SMALL TASK-SCOPE CORRECTION REQUIRED.**

Head: `aeecf1b5775db1d5ac2484819620f476752f3654`
Runtime CI #202 passed.
Review ID: `4945318769`.

Guidance remains externally promoted input, selectively projected, lifecycle-withheld, `GUIDANCE_ONLY`, and non-authoritative.

Only current finding: task MAY CHANGE list names four paths but PR also adds useful `tests/test_operational_learning_schema.py`. Amend the explicit task/PR boundary to include that file; preserve the test. Then sync/current-main review.

### PR #44 — full-fidelity hcom lineage read

**Status: BLOCKED.**

Capability can say `SUPPORTED` without proving local event-ID uniqueness. Upstream hcom uses one local SQLite event-ID namespace, so validation must reject duplicate bare local event IDs in the bounded sample.

### PR #45 — exact hcom message relationships

**Status: BLOCKED; DOWNSTREAM OF #44.**

Bare local event-ID relationship keying is consistent with upstream hcom. Blocker is evidence consistency: optional values such as `reply_to_local`, `intent`, and `thread` can create exact relationships even when corresponding `field_presence` says the field was not observed.

Required direction: only field-presence-proven optional values may create relationship evidence; contradictions fail closed.

---

## Handoff/status PRs

### PR #46 — Wave 3 progress handoff

**Status: CHANGES REQUIRED.**

Handoff overstates #44/#45 as complete and omits active #39/#41/#42 independent blockers. Update status before using as navigation truth.

### PR #47 — integration progress checkpoint

**Status: NEEDS STATUS REFRESH.**

It was blocked because it described #24 mandatory canonical enforcement as fully resolved while an impersonation path still existed. That underlying #24 defect has now actually been repaired and independently cleared on `3be75c...`, but #47 still needs exact head/CI/review chronology refreshed rather than leaving the older checkpoint wording as current truth.

---

## Highest-leverage continuation queue

1. Integration/operator lane: merge technically cleared **#24** under repository rules.
2. Repair **#48** provider/project-scoped durable session identity; after #24 merges, synchronize #48 to accepted main, rerun CI, exact review.
3. Synchronize technically clean **#33** to then-current main; then propagate/re-review **#34 → #35**.
4. Synchronize technically clean **#25** to then-current main.
5. Fix **#26** destructive ancestry so exact #25→#26 delta is catalog-only; propagate clean #27 repair; then repair/review **#31**.
6. Repair **#28 → #29**, then re-check clean downstream **#30**.
7. Repair **#32**; coordinate its state-layer overlap with #30 through real synchronization whichever lands second.
8. Repair **#39 → #41**.
9. Repair **#44 → #45**.
10. Repair **#42** evidence/protocol binding; #40 remains the cleaner protocol root.
11. Refresh **#36/#38/#46/#47** planning/handoff truth after implementation heads settle.
12. Preserve **#37** as dated research evidence and #43 as a clean runtime concept pending scope amendment/current-main sync.

## Reviewer continuation rules

For every re-review:

- re-resolve live `main`, PR base/base SHA, head/head SHA, draft/mergeability, exact diff, and exact CI;
- never carry an old approval/blocker forward solely from branch names or green CI;
- stacked review does not survive a material base/diff change automatically;
- explicit `UNKNOWN` is valid evidence state and must not be guessed away;
- capability/evidence never becomes permission or task authority by itself;
- do not accept duplicate authority stores or prompt/prose-only security enforcement;
- consequential fixes require behavioral/adversarial tests, not source-string assertions alone;
- if this reviewer implements a fix on a PR, this reviewer loses independence for that changed work.
