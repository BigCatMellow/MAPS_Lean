# SEC4 / 6.10 Half 2 — authority wiring + first real refusal (design addendum)

Date: 2026-08-31
Owner: `/root`
Status: design-only. No runtime behavior changed by this note.
Parent: `work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md`
Predecessor PR: #171 (Half 1 — durable storage; store has zero non-test writers).

This note answers behavior questions 4–8 of the parent note so a bounded Half-2
implementation PR can proceed without guessing. It changes no code.

## Re-verified facts at HEAD `84cc3f7` (rule 14)

- `runtime/state/skill_lifecycle_storage.py` exists (Half 1). Its methods
  `record_skill_lifecycle_subject(entry, report)`,
  `record_skill_lifecycle_transition(...)`, `get_skill_lifecycle_state(...)`,
  `get_skill_lifecycle_subject(...)`, `list_skill_lifecycle_decisions(...)`,
  `list_skill_lifecycle_subjects(...)` have **zero non-test callers**
  (`grep -rn` across `runtime/` returns only `runtime/state/store.py` mixin
  registration). Confirmed.
- `runtime/skills/catalog.py::SkillTrustState` still has exactly one member,
  `UNASSESSED`. `SkillProvenance.trust_state` defaults to it and is never
  reassigned. `build_skill_catalog()` never sets it.
- **`build_skill_catalog()` has zero production callers.** Outside `tests/` the
  only references are the `runtime/skills/__init__.py` re-export.
- **`SkillCatalog.fingerprint` has zero readers anywhere.** `grep -rn` for
  `.fingerprint` on a `SkillCatalog` returns only `catalog.py` (the definition
  at `catalog.py:98,128`) and two assertions in `tests/test_skills_catalog.py`
  (`:92`, `:104`). No `runtime/` code reads it. `test_content_change_changes_
  catalog_fingerprint` passes because `descriptor.content_sha256` is hashed
  into the fingerprint independently of the trust field.
- The only production consumer of a `SkillCatalog` is
  `runtime/context_builder.py::_select_skills()`, reached from
  `build_context_plan(store, task_id, *, repo_root, skill_catalog=None)`.
  Both production callers of `build_context_plan` —
  `runtime/cli.py:373` and `runtime/flow_start.py:80` — pass **no**
  `skill_catalog`, so `_select_skills` receives `None` and returns `[]` in
  every production flow today. The Skills subsystem has no reachable
  production entrypoint at all.
- `_select_skills` reads `entry.provenance.trust_state` and calls
  `runtime/trust.py::skill_trust_class(...)` → `MemoryTrustClass`, then
  `admit_memory_evidence(...)`.
- `runtime/trust.py` holds THREE read-only correspondence mappings:
  `_SKILL_TRUST_STATE_TO_MEMORY_TRUST_CLASS` (1 entry, `UNASSESSED →
  OBSERVATION`), `_SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS` (all 7
  lifecycle states → `MemoryTrustClass`), and
  `_OPERATIONAL_LEARNING_STATUS_TO_MEMORY_TRUST_CLASS`.
- `load_catalog_skill(entry)` in `catalog.py` is the documented activation
  entrypoint. It has zero production callers (re-exported; mentioned only in a
  `context_builder.py` docstring). It calls `load_skill(entry.descriptor)`,
  which re-verifies the on-disk directory hash.
- No operator-identity / authorized-operator registry exists anywhere in
  `runtime/` (`grep` for `authorized operator`, `operator_identity`,
  `OperatorIdentity`, `operator_registry` → only the two SEC4 modules'
  own prose).
- Half-1 schema (`runtime/state/schema.sql:753`, `:795`) is sufficient for
  Half 2: `skill_lifecycle_subjects` (immutable, `initial_state IN
  ('VALIDATED','QUARANTINED')`), `skill_lifecycle_decisions` (append-only,
  actor `CHECK` on `-> APPROVED`, `no_post_terminal` trigger). No schema
  change is needed and this note proposes none.

---

## Q4 — Who calls `record_skill_lifecycle_subject()` in production, and when?

**Decision: catalog-build time, via a new dedicated function
`register_skill_catalog(catalog, store, *, now=None)` added to
`runtime/skills/catalog.py`.** Not first-activation, not an operator command.

Rationale:

- Subject creation is **gate-driven** by design (parent note): the row's
  starting state is derived by `initial_transition_from_gate_report(report)`
  from a real `SkillGateReport`, never caller-supplied. So the call site must
  be one that has run `assess_skill(descriptor)`. Nothing does today.
- First-activation is wrong: `_select_skills` never activates
  (`load_catalog_skill` is never called from the plan), and `load_catalog_skill`
  itself is unreached. Tying subject creation to activation would mean a Skill
  that is selected-as-metadata but never activated never gets a row, i.e. the
  store would be populated only by accident.
- An explicit operator command is wrong for *subject* creation: only the
  `-> APPROVED` edges require an operator (parent note "No auto-approval").
  Recording that a Skill exists and what its gate said is a mechanical
  consequence of building the catalog, not an operator decision.

Shape of `register_skill_catalog` (impl PR writes it; specified here so it is
not designed inside a broad PR):

```
def register_skill_catalog(catalog: SkillCatalog, store, *, now=None) -> list[MutationResult]:
    results = []
    for entry in catalog.entries:
        if store.get_skill_lifecycle_subject(entry.catalog_key) is not None:
            continue                      # idempotent; content-addressed key
        report = assess_skill(entry.descriptor)      # runtime.skills.gate_hardened.assess_skill
        results.append(store.record_skill_lifecycle_subject(entry, report, now=now))
    return results
```

Idempotent: `catalog_key` is content-addressed, and
`record_skill_lifecycle_subject` already returns `SKILL_SUBJECT_EXISTS` for a
re-insert; the pre-check just avoids re-running the gate.

**When it runs in production:** whichever composition root eventually
constructs the `SkillCatalog` passed to `build_context_plan(...,
skill_catalog=...)` calls `register_skill_catalog(catalog, store)` immediately
after `build_skill_catalog(...)` and before handing the catalog to the plan.
Because that composition root does not exist yet (see the scope boundary
below), Half 2 adds the function and its test but does **not** commit
`cli.py` / `flow_start.py` to building a catalog — that is a separate
context-budget (roadmap 6.11) decision.

**Single file/callsite for the impl PR:** `runtime/skills/catalog.py` — new
`register_skill_catalog()`; export it from `runtime/skills/__init__.py`.

---

## Q5 — Does the actor requirement gain a real check in Half 2? Which layer owns it?

**Decision: NO. The actor requirement stays structural (non-empty text) in
Half 2. The read side owns consulting persisted state; the write side keeps
only the structural check.**

- There is no operator-identity source in the repo to validate `decided_by`
  against. Introducing one (an operator registry, an auth path, a signed
  decision format) is unbounded and is exactly the kind of material scope
  boundary rule 9/10 says to stop at. It is not required for "the persisted
  state actually gates something".
- This matches the operational-learning precedent verbatim:
  `OperationalLessonStorageMixin.promote_operational_lesson()` requires
  `promoted_by` non-empty and a `decision_ref`, and verifies nothing further.
  Half 1's `record_skill_lifecycle_transition` already mirrors that.
- **The one place that owns authority enforcement in Half 2 is the read
  side** — `load_catalog_skill()` and catalog-build — which refuses to
  *act on* a Skill whose composed state is not activatable (Q7 refusal
  below). That is the "real authority wiring": the recorded state now
  changes what the system does, without adjudicating operator identity.

**Single file/callsite for the impl PR:** none for enforcement — an explicit
"structural only; real operator-identity check deferred" paragraph goes in the
`runtime/state/skill_lifecycle_storage.py` module docstring (already half
there) and in the `load_catalog_skill` docstring. A real operator-identity
check is a named future item (call it SEC4 Half 3), not Half 2.

---

## Q6 — What does `SkillTrustState` become? (rule 12: three enums for one fact)

**Decision: collapse. Delete `SkillTrustState` entirely. `SkillLifecycleState`
becomes the single system of record for "where is this Skill in its trust
lifecycle", and `MemoryTrustClass` is the only projection target.**

Concretely:

1. `runtime/skills/catalog.py`: delete the `SkillTrustState` enum. Change
   `SkillProvenance.trust_state: SkillTrustState = SkillTrustState.UNASSESSED`
   to `lifecycle_state: SkillLifecycleState | None = None`. `None` replaces
   `UNASSESSED` and means exactly what Half 1's `get_skill_lifecycle_state()`
   returning `None` means: "no subject row — discovered but not yet assessed".
2. `runtime/trust.py`: delete `_SKILL_TRUST_STATE_TO_MEMORY_TRUST_CLASS` and
   `skill_trust_class()`. Keep `skill_lifecycle_trust_class()` as the **sole**
   Skill→`MemoryTrustClass` projection. The `None` case is handled at the call
   site (`OBSERVATION`), not inside `trust.py`, so `trust.py` keeps taking a
   real enum member only.
3. `runtime/context_builder.py::_select_skills`: replace
   `skill_trust_class(entry.provenance.trust_state)` with
   `skill_lifecycle_trust_class(entry.provenance.lifecycle_state)` guarded by
   `lifecycle_state is None -> MemoryTrustClass.OBSERVATION` (identical
   admission outcome to today's `UNASSESSED -> OBSERVATION`, so #148's
   class/action behavior is unchanged: an unassessed Skill is still
   `ON_DEMAND` metadata with a `withheld_reason`). The emitted item's
   `"trust_state"` field becomes `"lifecycle_state"` with value
   `lifecycle_state.value` or `None`.

**One-directional derivation chain (the rule-12 resolution):**

```
store: replay decisions -> SkillLifecycleState        (canonical, one place: lifecycle.py graph)
   |                                                   (read: get_skill_lifecycle_state)
   v
SkillProvenance.lifecycle_state : SkillLifecycleState | None   (a cached read, never authored here)
   |                                                   (skill_lifecycle_trust_class, the one mapping)
   v
MemoryTrustClass                                        (admission input only)
```

No enum defines its own members independently after this. `SkillTrustState`
ceases to exist; there is no second vocabulary to drift.

**Single file/callsite for the impl PR:** `runtime/skills/catalog.py`
(`SkillProvenance` field + enum deletion) is the anchor; `runtime/trust.py`
and `runtime/context_builder.py:359` follow mechanically. Test updates:
`tests/test_trust.py`, `tests/test_context_builder.py`,
`tests/test_skills_catalog.py`, `tests/test_skills_selection_evaluation.py`
(any that name `trust_state` / `SkillTrustState` / `skill_trust_class`).

How `lifecycle_state` gets populated: `build_skill_catalog()` gains an
optional `store=None` parameter; when supplied, each `SkillProvenance` is
built with `lifecycle_state=store.get_skill_lifecycle_state(catalog_key)`.
With `store=None` (all callers today) every entry is `lifecycle_state=None`,
byte-identical in behavior to the current `UNASSESSED` default.

---

## Q7 — Does populating `SkillProvenance.lifecycle_state` change `SkillCatalog.fingerprint`?

**Consumer check first (before wiring): `SkillCatalog.fingerprint` has ZERO
readers — in `runtime/`, in `cli/`, anywhere. Only two test assertions touch
it.** Nothing downstream depends on it.

**Decision: keep lifecycle/approval state OUT of the fingerprint. Change the
`catalog.py` digest to stop hashing the trust field.** The fingerprint stays a
pure function of (provenance identity + `content_sha256`), matching its
documented intent — "changed content yields a different `catalog_key`" —
and re-approving a Skill does not churn it.

- Today the digest folds `entry.provenance.trust_state.value` (line ~118).
  Replace that tuple element: drop it, or if a fixed field count is wanted,
  substitute a constant `""`. Either way the fingerprint no longer varies
  with lifecycle state.
- **Consequence, stated:** the catalog fingerprint remains
  content-and-provenance-derived and stable across approval decisions. A
  caller that ever wants an "approval-aware" identity composes
  `(catalog.fingerprint, tuple(sorted lifecycle states)))` itself — no such
  caller exists, so this is not built now (rule 8, smallest change).
- Alternative considered and rejected: letting the fingerprint absorb
  `lifecycle_state`. It has a superficial appeal ("approval is part of the
  catalog's identity") but with zero consumers it buys nothing, and it would
  make the fingerprint non-reproducible from a filesystem checkout alone
  (you'd need the store), which breaks the one property the fingerprint is
  for.

**Single file/callsite for the impl PR:** `runtime/skills/catalog.py`
`SkillCatalog.__post_init__` digest loop; update
`tests/test_skills_catalog.py:92,104` (the round-trip-equality test still
holds; the content-change test still holds via `content_sha256`).

---

## Q8 — Should `SUPERSEDED` record which revision superseded it?

**Decision: NO. No successor pointer, no `superseded_by` column, no FK.** This
confirms the choice Half 1 already made and documented (the
`skill_lifecycle_storage.py` docstring, answer 8: "SUPERSEDED records no
successor pointer... named in the decision's free-text `decision_ref`").

- A FK'd `superseded_by` forces the successor subject to be registered before
  the supersession decision can be written — an ordering constraint with no
  benefit today.
- A cross-Skill link is the first edge of a knowledge graph, an explicit
  roadmap non-goal (§7.6) and a parent-note non-goal.
- If a successor ever needs to be discoverable, its `catalog_key` goes in the
  `decision_ref` free text of the `ACTIVE -> SUPERSEDED` decision row. No
  schema change, no new column, no query surface.

**Single file/callsite for the impl PR:** none — no change. The impl PR's
`register_skill_catalog` / transition tests should include one
`ACTIVE -> SUPERSEDED` case whose `decision_ref` names the successor
`catalog_key` as a string, to pin the convention.

---

## Half 2 impl — scope boundary

### In scope

| Change | File | Notes |
|---|---|---|
| `register_skill_catalog(catalog, store, *, now=None)` | `runtime/skills/catalog.py` (+ `__init__.py` export) | Q4. Gate + record subjects, idempotent. |
| `build_skill_catalog(..., store=None)` populates `lifecycle_state` | `runtime/skills/catalog.py` | Q6. One-directional read from `store.get_skill_lifecycle_state`. |
| Delete `SkillTrustState`; `SkillProvenance.trust_state` → `lifecycle_state: SkillLifecycleState \| None` | `runtime/skills/catalog.py` | Q6. |
| Delete `_SKILL_TRUST_STATE_TO_MEMORY_TRUST_CLASS`, `skill_trust_class()` | `runtime/trust.py` | Q6. Keep `skill_lifecycle_trust_class` as sole projection. |
| `_select_skills`: use `skill_lifecycle_trust_class` + `None → OBSERVATION` guard; rename emitted field to `lifecycle_state` | `runtime/context_builder.py` | Q6. Admission outcomes unchanged for the unassessed case. |
| Stop hashing the trust field into `SkillCatalog.fingerprint` | `runtime/skills/catalog.py` | Q7. |
| First real refusal: `load_catalog_skill(entry, store)` raises `SkillCatalogError` when composed state ∈ {`QUARANTINED`, `RETIRED`, `SUPERSEDED`} | `runtime/skills/catalog.py` (+ `__init__.py` if signature exported) | Q5. `store=None` keeps today's unconditional behavior. |
| Tests for all the above | `tests/test_skills_catalog.py`, `tests/test_trust.py`, `tests/test_context_builder.py`, `tests/test_skills_selection_evaluation.py`, new coverage for `register_skill_catalog` + refusal | Round-trip through a real temp-file `TaskStore`. |
| `CAPABILITY_CHECKLIST.md` 6.10 / SEC4 row: evidence text only, no status flip (stays IN PROGRESS — capability-declaration manifest half still NOT STARTED) | `work/roadmaps/CAPABILITY_CHECKLIST.md` | Per that file's line ~149 same-PR rule. |

### Out of scope

- **Real operator-identity check** for `decided_by` (Q5). No operator
  registry / auth path. Named future item: SEC4 Half 3.
- **Capability-declaration manifest for third-party Skills/tools** — SEC4's
  other component, stays `NOT STARTED`, untouched. Finishing Half 2 still
  leaves SEC4 partially complete.
- **Committing `cli.py` / `flow_start.py` to build a `SkillCatalog`** and
  deciding the catalog composition root — that is roadmap 6.11 (context
  budgets) territory. Half 2 wires the *seams* (`build_skill_catalog`,
  `load_catalog_skill`, `register_skill_catalog` all accept a store) but does
  not force a production catalog into existence. Consequence, stated plainly:
  the "first real refusal" is real, callable and tested code, but like the
  rest of the Skills subsystem it has no production caller yet. Making the
  subsystem reachable from a runtime entrypoint is its own roadmap item.
- **`superseded_by` column / any schema change** (Q8 = no). Half 1's schema
  is sufficient.
- **Any change to `runtime/skills/lifecycle.py`** — its transition graph,
  actor rules and public functions stay untouched; the 184-line
  `tests/test_skill_lifecycle.py` contract must keep passing unmodified.
- **Persisting `DISCOVERED`** — resolved in Half 1 (absence of a row).

---

## Rule-12 hazard: resolved

Before: `SkillTrustState` (catalog), `SkillLifecycleState` (lifecycle),
`_SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS` + `_SKILL_TRUST_STATE_TO_MEMORY_
TRUST_CLASS` (trust) — four definitions, three of them independently editable,
all describing one fact ("how trusted is this Skill").

After: `SkillLifecycleState` is the single authored vocabulary. Its value for a
given Skill is composed once, in the store, from the pure `lifecycle.py` graph.
`SkillProvenance.lifecycle_state` is a cached read of that. `MemoryTrustClass`
is reached only through the one surviving `skill_lifecycle_trust_class`
mapping. Derivation is strictly one-directional
(store → provenance → trust class); nothing writes back up the chain.

## Roadmap impact

Does not complete SEC4 or 6.10. Specifies the Half-2 authority wiring and the
first refusal precisely enough for a bounded PR. SEC4's
capability-declaration-manifest half stays out. `work/roadmaps/CAPABILITY_
CHECKLIST.md` is unchanged by this note (the impl PR touches the 6.10/SEC4
evidence text, not the status label).

---

## Resume prompt

You are implementing SEC4 / 6.10 Half 2 for MAPS_Lean. Work in your own git
worktree off `origin/main`; `cd ~/Projects/MAPS_Lean` first and
`git fetch origin main`.

Source of truth: `work/notes/2026-08-31-sec4-half2-authority-wiring-design.md`
(this note) and its parent `work/notes/2026-08-25-sec4-skill-lifecycle-
persistence-design.md`. Re-verify every callsite/grep claim at your own HEAD
(rule 14) before relying on it.

Goal: wire the Half-1 store (`runtime/state/skill_lifecycle_storage.py`) into
real behavior and land the first real refusal. Implement exactly the "In
scope" table in this note's "Half 2 impl — scope boundary" section:

1. `register_skill_catalog(catalog, store, *, now=None)` in
   `runtime/skills/catalog.py`, exported from `runtime/skills/__init__.py`.
   Gate each entry with `assess_skill`, skip entries that already have a
   subject row, call `store.record_skill_lifecycle_subject(entry, report)`.
2. Add `store=None` to `build_skill_catalog`; when supplied, build each
   `SkillProvenance` with
   `lifecycle_state=store.get_skill_lifecycle_state(catalog_key)`.
3. Delete `SkillTrustState`. Change `SkillProvenance.trust_state` to
   `lifecycle_state: SkillLifecycleState | None = None`.
4. In `runtime/trust.py` delete `_SKILL_TRUST_STATE_TO_MEMORY_TRUST_CLASS`
   and `skill_trust_class()`; keep `skill_lifecycle_trust_class()`.
5. In `runtime/context_builder.py::_select_skills`, project via
   `skill_lifecycle_trust_class` with `lifecycle_state is None ->
   MemoryTrustClass.OBSERVATION`; rename the emitted `trust_state` field to
   `lifecycle_state`. Admission outcomes for the unassessed case must not
   change.
6. In `SkillCatalog.__post_init__`, stop folding the trust field into the
   fingerprint digest.
7. `load_catalog_skill(entry, store=None)`: when `store` is given, raise
   `SkillCatalogError` if `store.get_skill_lifecycle_state(entry.catalog_key)`
   is in {`QUARANTINED`, `RETIRED`, `SUPERSEDED`}. `store=None` keeps the
   current unconditional behavior.

MUST NOT touch: `runtime/skills/lifecycle.py`, `runtime/state/schema.sql`,
`runtime/state/skill_lifecycle_storage.py` (beyond docstring), the
`tests/test_skill_lifecycle.py` contract file. No operator-identity registry.
No capability-declaration manifest. No new schema column. Do not make
`cli.py` / `flow_start.py` build a catalog.

Tests: round-trip a subject + decision chain through a real temp-file
`TaskStore`; assert `register_skill_catalog` is idempotent; assert the refusal
fires for `QUARANTINED`/`RETIRED`/`SUPERSEDED` and not for
`VALIDATED`/`APPROVED`/`ACTIVE`; assert an unassessed Skill's admission
outcome in `_select_skills` is unchanged from `main`; include one
`ACTIVE -> SUPERSEDED` transition whose `decision_ref` names the successor
`catalog_key`. Update `tests/test_trust.py`,
`tests/test_context_builder.py`, `tests/test_skills_catalog.py`,
`tests/test_skills_selection_evaluation.py` for the enum/field rename.

Verification: one blocking foreground
`python3 -m unittest tests.test_skills_catalog tests.test_trust
tests.test_context_builder tests.test_skill_lifecycle
tests.test_skill_lifecycle_storage tests.test_skills_selection_evaluation`
— no `Monitor`, no background. Push before any full-suite run; rely on CI.
`python3 -m runtime.smoke` must exit 0.

Also update the 6.10 / SEC4 evidence text in
`work/roadmaps/CAPABILITY_CHECKLIST.md` in the same PR (no status flip —
stays IN PROGRESS; the capability-declaration-manifest half is still NOT
STARTED).

Then: PR into `main` (never push to main). Request independent review per
`reference_committee_review` and add a bound
`work/reviews/pr-<N>-review-evidence.md`. Do NOT self-merge. Report the PR
number to `gobi` via hcom when open and green.

Stop conditions: if wiring `lifecycle_state` into `_select_skills` or the
fingerprint change turns out to depend on a downstream consumer you cannot
find in the repo, write `UNKNOWN` and flag `gobi` rather than guess. If the
PR starts growing an operator-identity registry or a catalog composition
root in `cli.py`/`flow_start.py`, STOP — that is out of scope.
