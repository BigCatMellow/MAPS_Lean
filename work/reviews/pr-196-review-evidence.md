# PR #196 — resume-validation gate design note — independent design review evidence

reviewer: maps-lean-muzi
head_sha: 0237ad04eb8b6b43b45757d89838e767c68e5643
independent: true
summary: APPROVE. Docs-only design note (352-line note + 3 one-line "design note pending" checklist annotations, no status flip, no runtime/schema file). All 6 dispatch questions answered substantively. All load-bearing factual claims independently re-verified at origin/main d810509: (1) nothing consults `resume_validation` at HEAD — grep confirms only the producer in supervisor.py + vocab/docstrings in production.py; (2) a `make_validation_hook()` DENY at `BEFORE_RESUME` → `HarnessService._hook_block("resume")` → code `HOOK_DENIED` → `str(result.code) in _CANONICAL_DENIAL_CODES` (supervisor.py:24,447) → `action = "resume_denied"`, i.e. a broken environment would be mislabelled as a canonical-run denial — the note's Q2 rejection is correct; (3) the proposed `state = "blocked_validation"` / `_MAX_CONSECUTIVE_VALIDATION_BLOCKS` / `validation_block_persistent` are disjoint from PR #195's `state = "denied"` / `canonical_denial_persistent` — no collision, and both share the non-attempt-consuming + flat-reschedule pattern by design. Q3's operator-per-pass `--enforce-validation` first slice with the per-spec `EnvironmentSpec.validation.enforcement` field deferred is acceptable and correctly scoped. Diff in-bounds. No status token changed.

## Method

Own worktree at PR #196 head `a0a868376f16b971690218e49b3f7084e9baca02`
(branch `sec-65-resume-val-gate`). `git fetch origin` first; main is at
`d810509` (#194), one commit ahead of the note's stated verification base
`fbe88bc`. #194 touches only the SEC3/6.4 area (destructive-action guard) —
no overlap with the RnS resume path — so every callsite claim re-verified at
`d810509` still holds. Source of truth: the note itself, its parent
`work/notes/2026-08-25-rns-validation-tier-hookin-design.md`, PR #195's design
`work/notes/2026-08-31-canonical-enforcement-first-exposure-design.md`,
`work/notes/2026-08-31-roadmap-trajectory-check-10.md` §5a.4, and the real
`runtime/recovery/supervisor.py` / `runtime/harness/service.py` /
`runtime/environment/validation.py` code.

## 1. Six dispatch questions — all answered substantively

- **Q1 (producer/consumer of `resume_validation`)** — answered. Producer:
  `RecoverySupervisor.tick()` when `self.resume_validator is not None`, one
  `validate_for_run()` call per still-eligible incident before the resume
  attempt, dict stored on the action under `resume_validation`. Only concrete
  validator `RunBoundValidator`, built only when `--repo-root` is passed.
  Consumer: nothing. **Verified** (§2.1).
- **Q2 (enforcement point)** — answered. In `tick()`, immediately after the
  `validate_for_run` call, before the `harness_service` resume block; new
  `_blocked()` predicate = `attempted is True and passed is False`; enforced by
  `RecoverySupervisor` via a `validation_blocks_resume` kwarg, NOT a hook.
  The "why not `make_validation_hook()` at `BEFORE_RESUME`" rejection is
  substantive and **verified** (§2.2).
- **Q3 (who decides block vs warn)** — answered with an options table (per-tier
  default / `task_policy` flag / per-spec field / operator opt-in) and a
  two-level recommendation. Judgment in §3.
- **Q4 (interaction with `--enforce-canonical-run`)** — answered. Independent,
  not a slice of it; the `tick()` placement needs no `HarnessService` and no
  `CANONICAL_RUN` hook; the two compose (validation gate first, then canonical
  guard on the harness path); shared design pattern, no shared code.
- **Q5 (smallest slice)** — answered. Concrete file-by-file list: one kwarg +
  one check + one re-processable-state addition in supervisor.py; optional
  `validation_blocks: int` field in store.py (only if the ceiling is in v1);
  a `--enforce-validation` flag in production.py + cli.py requiring
  `--repo-root`. Explicit deferred list. Test list is a single blocking
  foreground `unittest` run.
- **Q6 (STOP / MUST-NOT for impl)** — answered. 10 numbered MUST-NOTs
  (hook registration, `task_policy` read, `EnvironmentSpec` import/name in
  supervisor.py, `{"attempted": False}` blocking, default-behaviour change,
  retry-budget consumption, `claim` piggyback, schema/`POLICY_FLAGS` change,
  status flip, weakening the #160 source guard) + 3 STOP-and-escalate triggers.

## 2. Load-bearing factual claims — independently verified

### 2.1 "Nothing consults `resume_validation` at HEAD" — CONFIRMED

`grep -rn resume_validation runtime/` at `d810509`:

- `runtime/recovery/supervisor.py` — the producer only: assignment at ~L409 /
  ~L416, and passthrough into the action dict at L331/356/372/395/500. No
  branch reads `resume_validation` to change control flow.
- `runtime/recovery/production.py` — L158 comment defining the closed
  `reason` vocabulary, L431 docstring on the `claim`-piggyback path. No read.

No other `runtime/` hit. `run_recovery_tick` returns `actions` verbatim;
`runtime/cli.py` serialises them as JSON. The trajectory note's
"consulted by nothing" claim holds exactly.

### 2.2 Q2 mislabelling claim — CONFIRMED

- `runtime/environment/validation.py::make_validation_hook` returns
  `HookOutcome(HookDirective.DENY, …)` on a failed tier (L196–197).
- `runtime/harness/service.py`: `BEFORE_RESUME` hook evaluation at L317–332;
  a denied outcome → `self._hook_block("resume", before)` (L332);
  `_hook_block` sets `code = "HOOK_DENIED" if result.denied else
  "APPROVAL_REQUIRED"` (L137).
- `runtime/recovery/supervisor.py`: `_CANONICAL_DENIAL_CODES =
  {"HOOK_DENIED", "APPROVAL_REQUIRED"}` (L24); in `tick()` the harness-resume
  result is classified `elif str(result.code) in _CANONICAL_DENIAL_CODES:` →
  `action = "resume_denied"`, `resolved = True` (L447–457), with the inline
  comment asserting this is "a concrete canonical-run mismatch".

So registering the validation hook at `BEFORE_RESUME` would route a failed
`quick` tier into the `resume_denied` branch, destroying the canonical-vs-
environment attribution PR #160/#195 preserve. The note's rejection of
Option A is factually correct, and the alternative (`tick()` placement
reading a dict `tick()` already computes) genuinely sidesteps it.

### 2.3 Disjointness from PR #195's `denied` state — CONFIRMED, no collision

PR #195 design (`…canonical-enforcement-first-exposure-design.md` §2b / Q4):

- new state: `incident["state"] = "denied"` (L110);
- persistent ceiling → `state = "failed"`,
  `last_error = "canonical_denial_persistent"` (L117–118, L307–308);
- does not consume the transient `attempt`; reschedules on a flat interval;
  own consecutive-denial ceiling (N≈3).

PR #196 proposes: `state = "blocked_validation"`,
`_MAX_CONSECUTIVE_VALIDATION_BLOCKS` → `failed` /
`validation_block_persistent`, own `validation_blocks` counter field, same
non-attempt-consuming + flat-reschedule semantics.

State names (`denied` vs `blocked_validation`), terminal `last_error` codes
(`canonical_denial_persistent` vs `validation_block_persistent`), counter
fields (`canonical_denials` vs `validation_blocks`), and action labels
(`resume_denied` vs `resume_blocked_validation`) are all distinct. The note's
composition claim — with both flags on, `due → validation gate → harness
resume → canonical guard` — is coherent: the validation gate `continue`s
before the harness call is ever made, so the canonical branch is only
reached for incidents the validation gate let through. No shared code, no
shared state, no name collision. Neither state name currently exists in
`supervisor.py` at HEAD (both are net-new), so there is nothing for #196 to
clash with even before #195 lands.

Note: #195 has not merged yet, so #196's parity claims are against a design,
not shipped code. Acceptable for a design note; the impl PR must re-verify
against whatever #195 actually ships (the note's Resume prompt already says
so). Not a blocker.

### 2.4 Re-processable state set — CONFIRMED

`supervisor.py` L219 and L302 both gate on `item.get("state") in
{"scheduled", "probing"}`. The note's "add `blocked_validation` to that set"
is the correct and minimal change for a re-processable parked state.

## 3. Q3 deferral judgment — ACCEPTABLE

Deferring the per-spec `EnvironmentSpec.validation.enforcement` policy field
to a separate authorised task, and shipping the first slice with an operator
per-pass `maps recovery-tick --enforce-validation` flag, is the right call:

- **Exact parallel to `--enforce-canonical-run`.** That enablement model
  already shipped (PR #180, `build_canonical_harness_service`) as a
  default-off operator opt-in at an explicitly-invoked pass, with the
  finer-grained policy model deferred. Using the same shape here is
  consistent, not novel risk.
- **The authority argument holds.** The operator who runs
  `maps recovery-tick --repo-root` has already chosen to run validation at
  all; `--enforce-validation` is the same operator, same pass, choosing that
  a hard failure blocks rather than annotates. "May a broken environment
  block a resume" is a run/environment property — the note correctly rejects
  routing it through `task_policy` (RnS never reads task policy for a
  recovery decision; and it would force a `POLICY_FLAGS` schema entry).
- **Deferring avoids a schema change in the first slice** (rule 8 / rule 10).
  The per-spec field is a `parse_environment_spec` change with its own
  tamper-evidence and default-semantics questions; bundling it here would
  expand scope past "make one tier gate one path".
- **The deferral is bounded, not open-ended.** Q6 STOP-condition 2 and the
  §Q3 "Later (separate authorised task)" paragraph name the exact follow-up
  and its layering (flag off ⇒ always advisory; flag on ⇒ per-spec,
  defaulting to blocking). The policy-model question is documented, not lost.

The question does **not** need resolving now: the first slice is coherent and
safe without it, and forcing the spec-schema decision into this PR would
violate the smallest-change rule the note itself invokes.

## 4. Diff in-bounds — CONFIRMED

`git diff origin/main...HEAD --stat`:

```
 work/notes/2026-08-31-resume-validation-gate-design.md | 352 +++++++++++++++
 work/roadmaps/CAPABILITY_CHECKLIST.md                  |   6 +-
 2 files changed, 355 insertions(+), 3 deletions(-)
```

- The note: new file, 352 lines, design-only.
- `CAPABILITY_CHECKLIST.md`: exactly 3 rows touched — H4, E4, 6.5. Each gets
  ONE appended sentence pointing at the note ("Design note pending: …").
  Status tokens unchanged: H4 `IN PROGRESS`, E4 `IN PROGRESS`, 6.5
  `IN PROGRESS` before and after. 6.16 / H5 untouched.
- No `runtime/`, no `schema.sql`, no `tests/`, no other file. Matches the
  dispatch's expected diff exactly.

## 5. Rebase / mergeability note (for author or coordinator, not a review blocker)

PR #196 is **BEHIND** `origin/main` by one commit (`d810509`, #194) and
`gh pr view` reports `mergeable: CONFLICTING`. Both #194 and #196 edit
`work/roadmaps/CAPABILITY_CHECKLIST.md` on disjoint rows (#194: SEC3 / 6.4;
#196: H4 / E4 / 6.5), so the conflict is textual/adjacent, not semantic — a
trivial rebase. Author or coordinator should rebase onto current `main`
before merge. If the rebase moves the note commit, re-point `head_sha` in
this file (and re-run `scripts/check_review_evidence.py 196`) — the current
`head_sha` binds the pre-rebase note commit `a0a868376f16b971690218e49b3f7084e9baca02`.

## Verdict

**APPROVE.** All 6 questions answered substantively; all load-bearing factual
claims independently verified against `origin/main` `d810509`; the two parked
states are disjoint (no collision); Q3's deferral is acceptable and bounded;
diff is in-bounds with no status flip. No MUST-NOT for the eventual impl is
violated by the note itself.
