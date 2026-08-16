# Integration Progress Checkpoint — 2026-08-15

**Status:** NON-AUTHORITATIVE CHECKPOINT / HANDOFF EVIDENCE

This note records the verified integration state late on 2026-08-15 ET. It is not task, policy, review, roadmap, or merge authority. Re-check live `main`, PR base/head SHAs, CI, and review evidence before acting on it.

## Current accepted `main`

At this checkpoint:

- `main`: `c9e52cfcea2afd6c1fab3956baedcf62117450af`
- that commit is the merge of PR #23, `Add canonical run guard for harness operations`

The Wave 1 harness/security stack has progressed substantially:

| PR | Capability | Integration state |
|---|---|---|
| #20 | typed provider-neutral harness foundation | MERGED |
| #21 | hcom normalization + deterministic Hooks | MERGED |
| #22 | provider-neutral `HarnessService` | MERGED |
| #23 | canonical run guard | MERGED |
| #24 | agentic-security baseline / mandatory guard composition | OPEN — FINAL WAVE 1 GATE |

Important merge commits already reached on `main` during this sequence:

- after #20: `1652d515a5b991b1ed07c7f2e624fea95927ddfb`
- after #21: `6a086d018e430591070935cfe83f9ededfcb5cb7`
- after #22: `0a03d70e6812a789f921d95b27196282cc195f31`
- after #23: `c9e52cfcea2afd6c1fab3956baedcf62117450af`

## Active gate — PR #24

Current verified PR #24 state:

- PR: #24 `Add initial agentic security adversarial baseline`
- base: `main@c9e52cfcea2afd6c1fab3956baedcf62117450af`
- head: `4ec42de3398258ebde0e0645516caef953a6a0ed`
- state: OPEN
- draft: YES
- mergeable: YES
- changed files: 8
- Runtime CI: run `31921940428` / #219 — SUCCESS on the exact head above

The final bounded #24 delta is:

- `runtime/harness/hooks.py`
- `runtime/harness/service.py`
- `runtime/policy/harness_guard.py`
- `tests/test_agentic_security_baseline.py`
- `tests/test_agentic_security_hook_context.py`
- `tests/test_harness_service.py`
- `work/security/AGENTIC_THREAT_MODEL.md`
- `work/tasks/agentic-security-baseline-wave1.md`

### Review history and resolved findings

Earlier independent review found important problems in the pre-integration stack. The current #24 head addresses the relevant findings rather than merely rebasing them away.

Resolved/represented on the current head:

1. **Canonical security guarding is no longer optional at the public consequential service boundary.**
   - `start`, `send`, `resume`, and `stop` require matching canonical-run enforcement.
   - absence of the mandatory guard fails closed with `CANONICAL_GUARD_REQUIRED` before adapter mutation.
   - ordinary `ALLOW` Hooks cannot impersonate mandatory canonical enforcement.

2. **Resume is covered mechanically.**
   - `BEFORE_RESUME` exists.
   - `HarnessService.resume()` runs the Hook before adapter mutation.
   - `CanonicalRunGuard` treats resume as a continuing, session-bound operation.

3. **Adapter-qualified session identity remains fail-closed.**
   - bare provider-local `session_id` is not treated as sufficient provider-neutral identity.
   - if canonical evidence cannot prove the session adapter, the guard returns `SESSION_ADAPTER_UNPROVEN` rather than guessing.

4. **Inherited Hook-context mutation defenses remain present.**
   - the hardened recursive Hook-value boundary from accepted #21 is preserved.
   - adversarial security coverage exercises earlier-Hook mutation attempts before canonical guarding.

5. **Stale operational note spillover was removed.**
   - the final #24 branch was rebuilt to contain only the bounded runtime/security/test/task surface listed above.

### Current review state

A fresh exact-head independent-review packet has been posted for:

- base `c9e52cfcea2afd6c1fab3956baedcf62117450af`
- head `4ec42de3398258ebde0e0645516caef953a6a0ed`
- Runtime CI #219 / `31921940428`

At this checkpoint, #24 must **not** be treated as accepted merely because older review blockers were fixed and CI is green. It still needs a clean independent substantive disposition bound to this exact final base/head.

## Important #21 review lesson retained

PR #21 required multiple independent passes before it became clean. The useful lesson is mechanical, not procedural theater:

- shallow immutability is insufficient for security-sensitive structured evidence;
- Python annotations are not runtime security boundaries;
- every externally reachable registration/composition boundary must enforce the same validation assumptions as the constructor/type itself;
- normalized provider adapters must contain low-level exceptions rather than leak them past the declared result contract.

Concrete #21 repairs that are now in accepted ancestry include:

- recursive detached Hook context values with unsupported mutable leaves rejected/fail-closed;
- recursive immutable Hook annotations;
- runtime validation of Hook events/directives/side-effect/failure-policy values;
- `HookRegistry.register()` requiring a real validated `HookSpec`, closing the duck-typed fail-open bypass;
- hcom `stop()` normalizing low-level `ValueError` into bounded `OperationResult` failure.

Do not regress these properties while synchronizing later branches.

## Next integration sequence after #24

Assuming the current #24 interface survives its fresh independent review:

1. receive clean independent disposition on exact #24 base/head;
2. mark #24 ready only after the exact review/CI gate is satisfied;
3. merge #24 with an expected-head guard;
4. re-read live `main` immediately after merge;
5. move to the evaluation/run-record critical path:
   - #33 portable Run Record v1
   - #34 frozen regression case v1
   - #35 comparative frozen regression evaluator v1
6. for each PR in that stack:
   - synchronize it to the newly accepted upstream state with real Git ancestry/integration;
   - do not merely retarget the PR base when the branch needs upstream fixes;
   - rerun full Runtime CI on the resulting exact head;
   - independently review that exact base/head;
   - merge only the independently reviewed exact head;
7. only then use those accepted interfaces as foundations for later lineage/evaluation work.

Current observed heads in the #33 → #35 draft stack at this checkpoint are:

- #33: `0b0f73ffdab67c48f61324b5b2d9c402dbe3f256`
- #34: `d895d3352e3ec35b0649702373ea115a6ca3d1e8`
- #35: `966654b385657654a72c5118112d8d5a7b42f2d3`

These are draft heads, not accepted authority. Re-check them before integration.

## Newer Wave 3 work exists, but do not leapfrog the accepted foundation

Additional draft work now exists in roughly PRs #38–#45, including:

- execution-lineage design;
- Context Builder v2 evidence-integrity corpus/scoring;
- Layer 2/Layer 3 end-to-end benchmark protocol/result validation;
- operational-learning guidance projection;
- full-fidelity hcom lineage reads;
- exact provider-local message relationship projection.

This work may be useful, but it was developed while foundational interfaces were still moving. Treat it as prospective/draft evidence until its dependencies are reconciled against accepted `main`.

In particular:

- do not freeze execution-lineage runtime work against pre-#24 harness/security interfaces;
- do not assume draft Run Record/evaluator APIs until #33–#35 are accepted;
- do not derive explainable waits until structured lineage/communication coverage is trustworthy;
- do not turn operational-learning observations into policy or self-authorizing guidance;
- do not convert provider communication evidence into task/run authority without an accepted exact join.

## Core invariants to preserve during continued integration

- one authority per fact;
- capability is not authority;
- provider/session/process liveness is not task truth;
- Hooks may block/narrow/require existing approval/annotate, but may not grant missing authority;
- explicit `UNKNOWN` / `MISSING` is preferable to inferred certainty;
- derived views remain derived;
- security boundaries require mechanical validation, not prose conventions;
- review evidence is valid only for the exact reviewed base/head;
- continuity-linked implementers do not self-satisfy independent review;
- better evaluation scores never automatically promote runtime/policy/harness changes;
- no second task/session/review/policy authority store;
- do not manufacture fake merges or hide missing integration by changing only a PR base.

## Immediate handoff

The next integration agent should begin by re-checking:

1. live `main` SHA;
2. PR #24 exact base/head/state;
3. Runtime CI for the exact #24 head;
4. all independent review submissions/comments added after this checkpoint.

If #24 has a clean independent disposition on the exact unchanged head, merge it and proceed to #33. If #24 has new findings or either base/head moved, resolve that exact state first and obtain fresh CI/re-review as necessary.

Do not restart broad legacy archaeology by default. Do not begin a new competing roadmap. Continue truth/evidence integration before adding autonomy.
