# SEC4 Half 3 — slice 2 scoping (after the authorized-operator registry)

**STATUS: DESIGN ONLY. No runtime code, no schema, no checklist status change.**
Scopes the smallest next SEC4 Half 3 increment after slice 1
(`authorized_operators` registry, PR #245, luve APPROVE — merge pending).

Parent: `work/notes/2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md`
(Item B / Q B1–B5). All code re-verified against `origin/main` `070dc65` plus
`origin/worktree-sec4-half3` (the #245 branch) (rule 14).

---

## 1. What slice 1 actually delivered (and what it is *not*)

Delivered on `origin/worktree-sec4-half3`:

- `authorized_operators` + `authorized_operator_revocations` tables, each with
  no-update / no-delete triggers (house pattern). "Authorized as of now" is
  composed (`is_authorized_operator`), never a mutable column.
- `AuthorizedOperatorStorageMixin` on `TaskStore`:
  `record_authorized_operator`, `revoke_authorized_operator`,
  `is_authorized_operator`, `list_authorized_operators`,
  `has_authorized_operator_registry`.
- Genesis row via `maps init --operator <id> --operator-decision-ref R`
  (`added_by` = the reserved `"GENESIS"` sentinel; first row only). Later rows
  require an already-authorized `--by` (`GENESIS_ALREADY_SEEDED` /
  `UNAUTHORIZED_AUTHORIZER` otherwise).
- `maps operator add|revoke|list`.
- **One** enforced call site: `maps skill approve` consults the registry
  **only when it is non-empty** (`has_authorized_operator_registry()`), CLI-side
  per Q B3, returning `UNAUTHORIZED_ACTOR` for an unrecognised `--actor`. Empty
  registry ⇒ byte-identical to pre-registry behavior.
- Beyond Q B5: `CANNOT_REVOKE_LAST_OPERATOR` guard (prevents a non-empty
  registry with nobody authorized — which would brick every `maps skill
  approve`). A revoked `operator_id` cannot be re-authorized in this slice
  (`operator_id` is the PK; rotation is Q B5 out-of-scope).

**Framing correction.** Slice 1's check is not a "stub". A seeded registry
genuinely blocks `maps skill approve` for a non-authorized actor. It is
deliberately *narrow* (one verb) and *fail-open when unseeded* — the latter is
the operator-chosen semantic (session-17 batch: "no rows → fail-open
(disabled)"), not a placeholder. Slice 2 is about **widening a working gate**,
not replacing a fake one.

---

## 2. Deferred surface — status of each candidate

### 2a. Widen the gate to the other Skill lifecycle verbs — READY, no blocker

`_dispatch_skill` maps four verbs to `record_skill_lifecycle_transition`:
`approve` (→ APPROVED), `activate` (→ ACTIVE), `retire` (→ RETIRED),
`supersede` (→ SUPERSEDED). Only the `approve` branch consults the registry.

- The pure `runtime/skills/lifecycle.py::transition()` graph requires a
  non-empty `actor` **only** for `(VALIDATED→APPROVED)` / `(QUARANTINED→
  APPROVED)` — which is why slice 1 picked `approve`.
- But the registry check is an **independent CLI-layer authority gate**, not a
  restatement of the graph's `actor`-required rule. `activate` (APPROVED→
  ACTIVE) is the transition that makes a Skill *loadable* into a real
  `maps flow start` context plan (`build_project_skill_catalog` → `LOAD`); an
  operator activating a Skill is an authority action whether or not the graph
  demands an `actor` string. Same argument, lower stakes, for `retire` /
  `supersede` (removing a Skill from service).
- Cost: move the `has_authorized_operator_registry()` guard so it covers all
  four transition verbs (or the `resolved`-is-a-key branch wholesale), keep the
  identical `UNAUTHORIZED_ACTOR` shape, make `--actor` required for all four
  when the registry is seeded. ~15–20 LOC + tests. **No schema, no new store
  primitive, no operator decision** — it only tightens a path that is already
  opt-in-by-data and already default-off.

**This is the recommended slice 2.** It is the "one consistent way" Q B4 asked
for, applied across the verb family instead of one verb.

### 2b. `maps promote` / `promote_operational_lesson(promoted_by=…)` — DEFER

Q B4's named shared consumer. Still has **zero production callers**
(`/usr/bin/grep -rn promote_operational_lesson runtime/` → definition +
`maps promote` dispatch only; the mixin method itself is unreached). Wiring the
registry check into `maps promote` is coherent but (i) it is a different
authority domain (operational-lesson promotion, not Skill trust), and (ii) it
would be gating a verb whose underlying primitive nothing production-exercises.
Fold it in *when operational-lesson promotion gets a real entrypoint*, reusing
whatever 2a produces. Not slice 2.

### 2c. Empty-registry "block everything" cutover — OPERATOR DECISION

Q B2's third undecided sub-item. Slice 1 shipped the operator-chosen fail-open
("no rows ⇒ checks disabled"). Flipping the default so an empty registry blocks
every gated verb (safer, but a hard cutover that breaks every existing
`maps skill`/CI invocation until a genesis row exists) is an **operator-only**
call. Name it; do not implement it. A middle option worth offering the operator:
a fleet-level `--enforce-operator-identity` flag (default off) that turns
fail-open into fail-closed without changing the empty-registry default —
mirrors `maps recovery-tick --enforce-canonical-run`.

### 2d. Re-authorization / rotation after revoke — DESIGN + LIKELY OPERATOR

`revoke_authorized_operator`'s docstring records that a revoked `operator_id`
cannot be re-authorized in slice 1 (PK collision). A real rotation story needs a
schema decision (revocation supersession row, or a re-authorization table) and
probably an operator nod on "may a previously-revoked operator return, and on
whose authority". Its own design note later. Not slice 2.

### 2e. `authorized_operators` ↔ `outcomes.py::actor_class=OPERATOR` mapping — DEFER

Q B1 alternative-considered. Additive, no operator decision, but nothing
currently consumes an `actor_class=OPERATOR` derivation, so zero value now.
Revisit if/when outcome-actor adjudication gets a consumer.

---

## 3. The slice (Phase 2 — do not implement until this note lands + a
coordinator confirms)

Increment **2a — widen the authorized-operator gate to every `maps skill`
lifecycle-transition verb.**

### MAY touch
- `runtime/cli.py` — `_dispatch_skill` (move/extend the
  `has_authorized_operator_registry()` guard to cover `approve` / `activate` /
  `retire` / `supersede`); the `skill` subparser if `--actor` needs to become
  required for the newly-gated verbs when seeded (prefer keeping it optional at
  the argparse layer and enforcing in the dispatch, so the empty-registry path
  and its error text are unchanged).
- `tests/test_cli_skill.py` — extend `OperatorRegistryCliTests`.
- `work/roadmaps/CAPABILITY_CHECKLIST.md` — 6.10 row evidence text only
  (s/"`approve`-only"/"all `maps skill` lifecycle verbs"/), **no STATUS change**.

### MUST NOT
- Add any column, table, trigger, or index.
- Add a new store method or a parameter to `record_skill_lifecycle_transition`
  (the check stays CLI-side — Q B3, and slice 1's precedent).
- Change the empty-registry semantics (still fail-open / inert).
- Touch `record_authorized_operator` / `revoke_authorized_operator` /
  genesis / `maps operator`.
- Wire `maps promote`, `maps context`, `maps flow start`, or
  `promote_operational_lesson`.
- Introduce re-authorization, rotation, expiry, `--enforce` flags, or
  `actor_class` mapping.
- Flip 6.10 (or any) checklist STATUS.

### Acceptance criteria
- With a seeded registry, `maps skill activate|retire|supersede` with an
  unauthorized `--actor` returns `ok:false`, `error_code:"UNAUTHORIZED_ACTOR"`,
  and records **no** `skill_lifecycle_decisions` row.
- With a seeded registry and an authorized `--actor`, all four verbs behave
  exactly as today.
- With an **empty** registry, all four verbs are byte-identical to pre-#245
  behavior (existing `seeded-registry-does-not-gate-activate` test flips to
  cover the seeded case; an empty-registry no-gate test is added/kept).
- `maps flow start` and every existing non-skill test unchanged.

### Verification
`python3 -m unittest -q tests.test_cli_skill tests.test_authorized_operator_storage
tests.test_skill_lifecycle_storage` as a blocking foreground run, plus
`python3 -m runtime.smoke`. Full `tests/` tree → the PR's CI
(`runtime-stack-tests`), per the session-17 test-contention protocol.

### Stop conditions
- If widening the gate turns out to require `--actor` to become an argparse
  `required=True` (changing the empty-registry error surface) → STOP, that is a
  behavior change to the unseeded path; re-scope.
- If any existing test asserts an *un*authorized actor can `activate`/`retire`/
  `supersede` against a **seeded** registry → that is the old narrow contract;
  update it (this slice deliberately changes it) and note the change in the PR.
- If a reviewer wants the gate at the store layer after all → that is a Q B3
  reversal, needs its own note, not this slice.

---

## 4. Recommendation

Do **2a only**. It is the whole of the "consistent authority gate across the
verb family" idea, costs no schema and no operator decision, and leaves 2b–2e
each with a clean, individually-scoped reason for deferral. 2c (the fail-closed
cutover) is the one item that should be surfaced to the operator as a written
question when someone next assembles a decision batch — it is the only part of
Half 3 that is genuinely blocked on an authority call rather than on
sequencing.

---

## Resume prompt

You are picking up SEC4 Half 3 slice 2. This note is `work/notes/2026-09-01-sec4-half3-slice2-scoping.md`.
Slice 1 (`authorized_operators` registry, PR #245) is merged. Implement
**increment 2a only**: widen the `has_authorized_operator_registry()` gate in
`runtime/cli.py::_dispatch_skill` so `maps skill activate|retire|supersede`
consult the registry the same way `approve` already does (identical
`UNAUTHORIZED_ACTOR` shape, still inert while the registry is empty). Stay
CLI-side — no new store method, no schema. Extend `OperatorRegistryCliTests` in
`tests/test_cli_skill.py`. Update only the 6.10 evidence text in
`work/roadmaps/CAPABILITY_CHECKLIST.md` (s/`approve`-only/all lifecycle verbs/),
**no STATUS flip**. Obey the MUST NOT / Stop-conditions lists in §3. Verify with
the §3 command as a blocking foreground run + `python3 -m runtime.smoke`; full
suite goes to CI. New worktree off `origin/main`. PR into `main`; author does
not spawn the reviewer — ping the coordinator when the PR is open.
