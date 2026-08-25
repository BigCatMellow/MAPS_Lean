# SEC4 / 6.10 Skill lifecycle persistence design

Date: 2026-08-25
Owner: `/root`
Status: design complete; no runtime behavior changed

## Finding

Re-verified against a fresh read of `origin/main@8923adb` (not from the
trajectory note's summary). All of the following is current fact:

- `runtime/skills/lifecycle.py` is 161 lines and contains exactly four
  things: the `SkillLifecycleState` enum (7 members), `SkillLifecycleError`,
  two module-level frozen tables (`_ACTOR_REQUIRED_TRANSITIONS`,
  `_ALLOWED_TRANSITIONS`), and two pure functions — `transition(current,
  target, *, actor=None) -> SkillLifecycleState` and
  `initial_transition_from_gate_report(report) -> SkillLifecycleState`.
  It imports only `enum` and `.gate`. There is no `sqlite3`, no `Path`, no
  file I/O, no store handle, no class holding state.
- So "unpersisted" is not "in-memory store with no flush." It is stricter:
  **`transition()` is a pure validator that returns its own `target`
  argument.** It never records what happened. The caller holds the current
  state, and nothing outside the caller's local variable knows it. There is
  no storage backend at all, and no transition history object either — both
  halves are missing.
- **No production code calls `transition()` or
  `initial_transition_from_gate_report()`.** `grep -rn "skills.lifecycle\|
  SkillLifecycleState\|initial_transition_from_gate_report"` across the repo
  returns: the module itself; `runtime/skills/__init__.py` (which does
  re-export both the enum and `initial_transition_from_gate_report`, so the
  public surface exists); `tests/test_skill_lifecycle.py` and
  `tests/test_trust.py`; and `runtime/trust.py`, which imports the enum for
  `_SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS` /
  `skill_lifecycle_trust_class()` — a second pure mapping that is itself
  also unwired. So the enum has one non-test consumer, and it is another
  storage-free primitive; the *functions* have none.
- `tests/test_skill_lifecycle.py` (184 lines) pins the contract that any
  persistence layer must not break: all 8 legal edges succeed; every one of
  the 41 remaining (source, target) pairs raises; `DISCOVERED` cannot reach
  `APPROVED` or `ACTIVE`; both `*->APPROVED` edges reject `None`/`""`/`"   "`
  actors; `APPROVED->ACTIVE` and `QUARANTINED->RETIRED` need no actor;
  `SUPERSEDED`/`RETIRED` have zero outgoing edges; non-enum arguments raise.
  Three further tests drive `initial_transition_from_gate_report` off real
  `assess_skill()` output (CLEAR and REVIEW_REQUIRED -> `VALIDATED`,
  QUARANTINE -> `QUARANTINED`).
- `runtime/skills/catalog.py::SkillTrustState` still has exactly one member,
  `UNASSESSED`, with the comment "A future reviewed trust lifecycle may add
  states." `SkillProvenance.trust_state` defaults to it and is never
  reassigned anywhere. `SkillCatalog.fingerprint` hashes `trust_state.value`
  into the catalog fingerprint, so today the fingerprint is
  trust-state-invariant purely because the value is constant.
- `SkillCatalogEntry.catalog_key` already produces the exact stable identity
  a persisted row needs: `f"{source_id}:{skill_id}@sha256:{content_sha256}"`.
  This is a content-addressed key — a Skill edit changes `content_sha256` and
  therefore produces a *different* `catalog_key`, which is precisely the
  roadmap's "a Skill update creates a new hash/version requiring
  re-evaluation / no silent auto-update of active procedures"
  (`work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md`
  §7).
- `runtime/state/schema.sql` (734 lines, 30+ tables) has **no** Skill table
  of any kind. `grep -in "skill" runtime/state/schema.sql` returns nothing.
  There is no existing place a Skill's lifecycle state could live.

Confirmed: SEC4's gap is exactly what
`work/roadmaps/CAPABILITY_CHECKLIST.md` line 60 says — "a pure, unpersisted
primitive with no durable storage of a Skill's current state and no real
operator-authority wiring." (Verified that wording verbatim; line 119's 6.10
row uses the shorter "unpersisted — no durable lifecycle state or real
authority wiring yet.") This note designs both halves without touching
runtime code.

## Decision: mirror `operational_lesson_decisions` — append-only decisions plus a composed effective state

Do not add a mutable `lifecycle_state` column that gets `UPDATE`d on each
transition. This codebase already solved the identical problem — a validated
state machine (`CANDIDATE -> ACTIVE -> RETIRED`) whose transitions require an
explicit actor and must survive restarts — in
`runtime/state/operational_learning_storage.py` +
`runtime/state/schema.sql` lines 640-734. Reuse that exact pattern rather
than inventing a second one.

The pattern, as it exists today for lessons:

1. An immutable base row (`operational_lessons`), locked by
   `CHECK (status = 'CANDIDATE')` plus `BEFORE UPDATE`/`BEFORE DELETE`
   triggers that `RAISE(ABORT, ...)`.
2. An append-only decision table (`operational_lesson_decisions`) — one row
   per operator decision, each carrying `decision_kind`, a JSON
   `decision_payload`, a non-empty `decided_by`, and `decided_at`. Also
   update/delete-trigger-locked.
3. Effective status is **derived** by `_compose(base_row, decisions)`, never
   stored. `get_operational_lesson()` composes and then re-validates the
   composed record through the pure validator as defense in depth.
4. Illegal sequences are refused twice: in Python (`ALREADY_PROMOTED`,
   `LESSON_RETIRED`) and again by SQLite triggers
   (`trg_operational_lesson_decisions_no_repromote`,
   `..._no_reretire`).

Applied to Skills, concretely:

**Storage location.** `runtime/state/schema.sql`, inside the existing
`TaskStore` SQLite database. This is *not* a second authority database
(roadmap §7.2): it is the same single canonical store that already holds
`operational_lessons`, which is likewise not task/session state. No new file,
no new DB handle, no new process. Access is through a new mixin,
`SkillLifecycleStorageMixin` in `runtime/state/skill_lifecycle_storage.py`,
added to the `TaskStore` mixin list in `runtime/state/store.py` exactly like
`OperationalLessonStorageMixin` is.

**Two tables.**

- `skill_lifecycle_subjects` — the immutable identity row. Keyed by
  `catalog_key TEXT PRIMARY KEY`, storing only the already-derived
  provenance/identity fields (`source_id`, `source_kind`, `source_ref`,
  `declared_revision`, `skill_id`, `skill_name`, `content_sha256`,
  `first_seen_at`) plus the initial gate verdict that produced the row's
  starting state (`initial_state` restricted by
  `CHECK (initial_state IN ('VALIDATED','QUARANTINED'))`, `gate_disposition`,
  and `gate_report` as a `json_valid` snapshot of
  `SkillGateReport.to_dict()`). Locked immutable by `BEFORE UPDATE`/
  `BEFORE DELETE` triggers.

  Note what is *absent*: no `SKILL.md` body, no resource contents, no
  procedure text. Only references and hashes — required by roadmap
  §6.3 ("Prefer manifests/indexes derived from filesystem + small approval
  metadata rather than copying entire Skill content into SQLite... store
  references/hashes, not duplicate Skill bodies"). `gate_report` is the one
  JSON blob, and it is a findings/verdict summary, not Skill content.

- `skill_lifecycle_decisions` — append-only, one row per transition after
  the initial gate verdict. `decision_id INTEGER PRIMARY KEY AUTOINCREMENT`,
  `catalog_key TEXT NOT NULL REFERENCES skill_lifecycle_subjects(catalog_key)`,
  `from_state`/`to_state` both `CHECK (... IN (<the 7 states>))`,
  `decision_ref TEXT` (the operator decision this implements),
  `decided_by TEXT` (nullable exactly where the pure module says no actor is
  required), `decided_at`, `created_at`. Update/delete-trigger-locked.

  A schema-level `CHECK` enforces the actor requirement the pure module
  already enforces, as defense in depth: `CHECK (NOT (to_state = 'APPROVED'
  AND (decided_by IS NULL OR length(trim(decided_by)) = 0)))`.

**Effective state is composed, never stored.** A `_compose()` equivalent
reads the subject's `initial_state`, then replays decisions in
`decision_id` order through the *existing pure* `transition()` from
`runtime/skills/lifecycle.py` — reusing the validator rather than
reimplementing the graph in SQL or in the mixin. If a replay ever raises
`SkillLifecycleError`, the read fails loudly rather than returning a state
the graph forbids. This is the direct analogue of
`get_operational_lesson()` re-running `validate_lesson_record()` on the
composed record.

**The write path calls the pure validator before inserting.** `record_skill_
lifecycle_transition(catalog_key, to_state, *, decided_by=None,
decision_ref, now=None) -> MutationResult` computes current effective state
by replay, calls `transition(current, to_state, actor=decided_by)`, and only
inserts if that returns without raising. `SkillLifecycleError` maps to a
`MutationResult(False, "ILLEGAL_SKILL_TRANSITION", str(exc))` — same
false/code/message shape every other mixin already returns. **No transition
logic is duplicated into the storage layer** (rule 12, no duplicate truth):
the graph lives in exactly one place and the storage layer is a caller of it.

**Subject creation is gate-driven, not free-form.** `record_skill_lifecycle_
subject(entry: SkillCatalogEntry, report: SkillGateReport)` derives
`initial_state` by calling the existing
`initial_transition_from_gate_report(report)` — it does not accept a
caller-supplied starting state, so `DISCOVERED -> APPROVED` cannot be
smuggled in by inserting a subject that starts at `APPROVED`. This preserves
the module's central invariant (nothing reaches `APPROVED` except through an
explicit actor-bearing decision row) across the persistence boundary.

## What "durable storage + real authority wiring" means as an implementation boundary

The checklist phrase names two separable halves. They should be two PRs, the
same way `#154 -> #160` and the operational-learning storage/authority tasks
were split (`work/tasks/operational-learning-authority-design-wave4.md`
exists precisely because storage and authority were separated there).

**Half 1 — durable storage. In scope:**

- The two tables + triggers in `runtime/state/schema.sql`.
- `runtime/state/skill_lifecycle_storage.py` with the mixin: record subject,
  record transition, get effective state, list decisions, list subjects in a
  given effective state.
- Registering the mixin on `TaskStore` in `runtime/state/store.py`.
- Tests: round-trip a subject + decision chain through a real temp-file
  `TaskStore`; assert the composed state after each write; assert every
  illegal edge is refused at the Python layer *and* separately that the
  actor `CHECK` and the immutability triggers fire on direct SQL; assert a
  content edit produces a distinct `catalog_key` and therefore a distinct
  subject at `VALIDATED`/`QUARANTINED`, never inheriting the old
  `catalog_key`'s `APPROVED`/`ACTIVE`.

**Half 1 explicitly does NOT include:** verifying that `decided_by` names a
real, authorized operator. Storage records the claimed actor as a fact; it
does not adjudicate it. This matches
`OperationalLessonStorageMixin.promote_operational_lesson()`, which requires
`promoted_by` to be non-empty and requires a `decision_ref`, and verifies
nothing further.

**Half 2 — real authority wiring. In scope:**

- Deciding and implementing who may supply `decided_by` for the two
  `-> APPROVED` edges, how that identity is established, and how the approval
  event is audited beyond the decision row itself.
- Wiring `SkillCatalog`/`SkillTrustState` to the persisted state so that
  loading a Skill consults it: `SkillTrustState` gains members beyond
  `UNASSESSED`, or `SkillProvenance.trust_state` is populated from the store
  at catalog-build time. This is the "real authority wiring" that makes the
  persisted state actually *gate* something rather than merely be recorded.
- A first real refusal: `load_catalog_skill()` (or its caller) declining to
  activate a Skill whose composed state is `QUARANTINED`/`RETIRED`.

**Not part of either half:** SEC4's other stated component, the
"capability-declaration manifest for third-party Skills/tools," remains
`NOT STARTED` and untouched. Finishing both halves above still leaves SEC4
partially complete.

## Non-goals

- **No second authority database** (roadmap §7.2). Both tables go into the
  existing `TaskStore` schema. No separate skills DB file, no JSON/YAML
  sidecar registry on disk, no parallel store class with its own connection
  logic.
- **No mutable state column.** No `UPDATE skills SET state = ?`. The
  append-only-decisions + composed-view pattern is the whole point; a
  mutable column would make the transition history unrecoverable and would
  let a bad write land a Skill in `APPROVED` with no decision row behind it.
- **No Skill content in SQLite** (roadmap §6.3). References and hashes only.
  The `SKILL.md` body stays on the filesystem and keeps being verified by
  `load_skill()`'s existing hash check at activation time.
- **No reconciliation daemon, no background sync, no catalog-watcher**
  (roadmap §7.1/§7.9). Persistence is plain synchronous read/write on the
  existing store, called from the code path that already discovers/assesses
  Skills. Nothing polls for content drift; drift is detected structurally,
  because changed content yields a different `catalog_key` that simply has
  no `APPROVED` decision behind it.
- **No knowledge graph / no cross-Skill relationship modeling**
  (roadmap §7.6). `SUPERSEDED` is a state, and if a successor pointer is
  wanted it is at most one nullable `superseded_by` reference on a decision
  payload — not a graph, not a dependency index, not a queryable ontology.
- **No change to the pure module's transition graph, actor rules, or public
  functions.** `runtime/skills/lifecycle.py` should ideally be untouched by
  Half 1; the storage layer is a *caller*. If it must change, the 184-line
  existing test file is the contract that must keep passing unmodified.
- **No auto-approval.** Nothing derives `APPROVED` from evidence, gate
  cleanliness, source kind, or elapsed time. Every `-> APPROVED` row carries
  an explicit human-supplied `decided_by` and `decision_ref`, matching the
  operational-learning "operator decision recorded 2026-08-17, Option A"
  precedent (no automatic/evidence-gated path).
- **No CLI/UI surface in Half 1.** Whether operators drive this through a
  `skills` CLI subcommand is a separate question; Half 1 ships the store API
  and its tests only.

## Behavior questions the implementation task must answer

Do not guess these inside a broad implementation:

1. **Is `catalog_key` the primary key, or `(source_id, skill_id)` with
   `content_sha256` as an attribute?** This note proposes `catalog_key`
   (content-addressed, so an edited Skill is a new subject that must be
   re-approved). The cost is that approving a Skill approves exactly one
   revision and every edit needs re-approval — which is the roadmap's stated
   intent, but the implementation must confirm that is tolerable in practice
   for `BUNDLED` Skills that change with every repo commit, or decide that
   `BUNDLED` gets a different rule.
2. **What is the durable answer for a Skill that vanishes from disk?** Its
   subject row still exists with an `ACTIVE` composed state. Does the store
   need a `RETIRED` decision written by someone, does a read-time existence
   check downgrade it, or is a stale row harmless because activation
   re-verifies the hash anyway? Do not silently delete rows — the tables are
   trigger-locked immutable by design.
3. **Where does `DISCOVERED` live?** The proposed subject row starts at
   `VALIDATED`/`QUARANTINED` because a subject is only created once a gate
   report exists, so `DISCOVERED` is never a persisted state. That is a real
   semantic choice: it means "discovered but not yet assessed" is represented
   by the *absence* of a row. The implementation must either accept that
   (and say so in the module docstring) or persist `DISCOVERED` subjects and
   accept rows with no gate report.
4. **Who calls `record_skill_lifecycle_subject()` in production, and when?**
   Catalog build time, first activation attempt, or an explicit operator
   command? This is the analogue of the SEC3 note's "which exact call site
   constructs the binding" question and it is not answered here.
5. **Does the actor requirement gain a real check in Half 2, or stay
   structural?** Today `transition()` only requires non-empty text. If Half 2
   introduces a genuine operator-identity source, does the storage layer
   validate against it, or does the gate at the *read* side (catalog/load)
   do it? Two different places could plausibly own this; pick one.
6. **What does `SkillTrustState` become?** Adding members mirroring
   `SkillLifecycleState` risks two vocabularies for one fact (rule 12) —
   and there is already a third, `runtime/trust.py`'s
   `_SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS`, which maps all seven
   lifecycle states onto `MemoryTrustClass`. The alternatives are: collapse
   `SkillTrustState` into `SkillLifecycleState`; keep `SkillTrustState` as a
   coarse projection derived from the lifecycle state; or drop it in favour
   of the existing `runtime/trust.py` mapping. Decide explicitly and make
   the derivation one-directional; do not let three enums grow
   independently.
7. **Does populating `SkillProvenance.trust_state` from the store change
   `SkillCatalog.fingerprint`?** It currently hashes `trust_state.value`,
   which is constant today. Once it varies, the catalog fingerprint becomes
   sensitive to approval decisions — which may be correct (approval is part
   of the catalog's identity) or may break something that assumes the
   fingerprint depends only on filesystem content. Check before wiring.
8. **Should `SUPERSEDED` record which revision superseded it?** If yes, the
   pointer belongs in the decision payload as a `catalog_key` reference, and
   the implementation must decide whether a `FOREIGN KEY` to
   `skill_lifecycle_subjects` is required (which would force the successor to
   be registered first). This note deliberately does not commit to a
   supersession link.

## Roadmap impact

This design does not complete SEC4 or 6.10. It specifies the storage shape
and the storage/authority split so a bounded Half-1 PR can add two tables
plus one mixin — reusing the `operational_lessons` /
`operational_lesson_decisions` pattern verbatim rather than inventing a
storage mechanism — and a Half-2 PR can wire `SkillCatalog`/`SkillTrustState`
to it and make the first real refusal. SEC4's capability-declaration-manifest
half stays out of scope for both. `work/roadmaps/CAPABILITY_CHECKLIST.md` is
unchanged by this note.
