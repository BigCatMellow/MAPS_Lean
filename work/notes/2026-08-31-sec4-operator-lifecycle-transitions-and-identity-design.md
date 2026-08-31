# SEC4 — operator-driven lifecycle transitions + operator-identity design

Date: 2026-08-31
Owner: `/root`
Status: design-only. No runtime behavior changed by this note.
Parents:
- `work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md` (storage/authority split)
- `work/notes/2026-08-31-sec4-half2-authority-wiring-design.md` ("Out of scope" names Half 3)

This note designs the **two remaining SEC4 lifecycle-authority items**, which
are coupled:

- **Item A — the `record_skill_lifecycle_transition()` production caller.** The
  storage method and the pure `runtime/skills/lifecycle.py::transition()` graph
  both exist; nothing in production calls them. Operator-driven transitions
  (`VALIDATED`/`QUARANTINED -> APPROVED -> ACTIVE`, `QUARANTINED -> RETIRED`,
  `ACTIVE -> SUPERSEDED`/`RETIRED`) have no entrypoint.
- **Item B — SEC4 Half 3, operator-identity.** `actor` / `decided_by` is only
  structurally checked (non-empty). No registry of authorized operators exists
  anywhere in `runtime/`.

They are coupled because A's entrypoint is the exact place B's check would be
consulted. This note specifies A fully and specifies B down to a smallest
first slice plus an explicit operator-decision callout for the trust-root
question.

---

## Re-verified facts at HEAD `98620e4` (rule 14)

- `runtime/state/skill_lifecycle_storage.py::record_skill_lifecycle_transition(
  catalog_key, to_state, *, decision_ref, decided_by=None, now=None) ->
  MutationResult` exists. It opens `BEGIN IMMEDIATE`, loads the subject row,
  replays decisions via `_compose_skill_state` -> pure
  `lifecycle.transition()`, calls `transition(current, to_state,
  actor=decided_by)` once more as the write-gate, then inserts one
  `skill_lifecycle_decisions` row. Result codes it can return:
  `INVALID_CATALOG_KEY`, `INVALID_TARGET_STATE`, `INVALID_DECISION_REF`,
  `SKILL_SUBJECT_NOT_FOUND`, `ILLEGAL_SKILL_TRANSITION`,
  `SKILL_DECISION_CONSTRAINT_VIOLATION`, and on success
  `SKILL_TRANSITION_RECORDED` with `{catalog_key, from_state, to_state}`.
- **Zero non-test callers.** `grep -rn "record_skill_lifecycle_transition"
  runtime/` returns only the definition and its own docstring mention in the
  module header. All other hits are in `tests/test_skill_lifecycle_storage.py`.
- `transition()` requires a non-empty `actor` **only** for
  `(VALIDATED, APPROVED)` and `(QUARANTINED, APPROVED)`
  (`_ACTOR_REQUIRED_TRANSITIONS`). `APPROVED -> ACTIVE`,
  `QUARANTINED -> RETIRED`, `ACTIVE -> SUPERSEDED`, `ACTIVE -> RETIRED` need no
  actor. `SUPERSEDED`/`RETIRED` are terminal (no outgoing edges).
- Schema (`runtime/state/schema.sql:795`): `skill_lifecycle_decisions` is
  append-only (no-update / no-delete triggers), `decision_ref TEXT NOT NULL
  CHECK (length(trim()) BETWEEN 1 AND 512)`, `decided_by TEXT` nullable with a
  1–128 length check when present, `CHECK (from_state <> to_state)`, a
  `CHECK (NOT (to_state='APPROVED' AND decided_by empty))` actor guard, and
  `trg_skill_lifecycle_decisions_no_post_terminal` refusing any decision once a
  `SUPERSEDED`/`RETIRED` row exists for that `catalog_key`.
- `catalog_key` is the subject PK, content-addressed
  `"<source_id>:<skill_id>@sha256:<content_sha256>"`. An edited Skill is a
  *new* subject starting at `VALIDATED`/`QUARANTINED`; it never inherits the
  prior revision's `APPROVED`/`ACTIVE`.
- **No CLI surface for Skill lifecycle.** `runtime/cli.py` has no `skill`
  subcommand. `maps flow start` (`runtime/flow_start.py:84`) calls
  `build_project_skill_catalog(repo_root, store)` which calls
  `register_skill_catalog()` -> `record_skill_lifecycle_subject()`; that is the
  only production write to either Skill table. `maps context` (`cli.py`) is
  deliberately **not** wired (write-on-read hazard).
- **No operator-identity / authorized-operator source anywhere in `runtime/`.**
  `grep -rn "authorized|operator_registry|OperatorIdentity|operator_identity"
  runtime/` -> only prose in the two SEC4 modules and this design lineage.
  - The closest existing concept is `runtime/state/outcomes.py`'s
    `VALID_ACTOR_CLASSES = {OPERATOR, CORE_AGENT, HELPER, SYSTEM, UNKNOWN}`
    with `actor_id` required when the class is not `UNKNOWN`. This is
    **descriptive tagging** — nothing verifies that an `actor_id` names a real
    principal, and there is no list of which ids are `OPERATOR`.
  - `maps promote --actor <str>` (`cli.py:97,355`) and
    `OperationalLessonStorageMixin.promote_operational_lesson(promoted_by=...)`
    (`operational_learning_storage.py:210`) both take an **unverified free
    string**. `promote_operational_lesson` itself also has zero production
    callers — the identical "recorded but unadjudicated actor" residual.
  - The MAPS CLI trusts its invoking process entirely: no login, no session
    auth, no principal. Whatever runs `python -m runtime.cli` is the operator.
- SEC3 (`work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`)
  and the memory-trust notes carry the parallel "a `bool` / free field
  encodes a trust assumption nothing checks" residual (`destructive: bool`,
  `embedded: bool`). The resolution pattern there is the same one this note
  applies: keep the structural field, add an **opt-in** real check at exactly
  one call site, default off = byte-identical behavior.

---

## Item A — the operator-driven transition entrypoint

### Q A1 — What is the entrypoint?

**Decision: a new `maps skill` CLI subcommand group in `runtime/cli.py`, thin
over the existing storage methods.** Not a new service, not a flow, not a
library-only function.

Rationale:

- Operator-driven transitions are, by definition, an operator typing a
  command. The MAPS operator surface is `runtime/cli.py`; every other
  operator action (`create`, `promote`, `outcome-record`, `review-record`)
  lives there as a thin `_emit(store.<method>(...))` wrapper. A Skill
  approval is the same shape.
- The composition (`replay -> transition() -> insert`) already lives *inside*
  `record_skill_lifecycle_transition()` in one `BEGIN IMMEDIATE`
  transaction. The CLI must **not** re-implement or pre-compose any of it —
  it parses args, resolves a `catalog_key`, calls the one method, and
  `_emit`s the `MutationResult`. (rule 12 — the graph and the compose step
  stay in exactly one place.)
- `maps flow start` is the wrong home: it is an automated context-plan build,
  not an operator decision point, and it already correctly only *records
  subjects* (gate-driven, no actor). Adding approval there would be
  auto-approval, an explicit non-goal.

### Q A2 — What subcommands / verbs?

**Decision: one verb per legal operator transition, not a generic
`transition <from> <to>`.** A generic verb invites illegal-edge typos and
makes the actor requirement invisible.

| Command | Edge(s) | Actor | Notes |
|---|---|---|---|
| `maps skill approve <key> --decision-ref R --actor A` | `VALIDATED -> APPROVED`, `QUARANTINED -> APPROVED` | **required** | The only actor-bearing edge. Current composed state decides which edge. |
| `maps skill activate <key> --decision-ref R` | `APPROVED -> ACTIVE` | none | Deployment fact, not a second decision. |
| `maps skill retire <key> --decision-ref R` | `QUARANTINED -> RETIRED`, `ACTIVE -> RETIRED` | none | Operator rejects / withdraws. |
| `maps skill supersede <key> --decision-ref R` | `ACTIVE -> SUPERSEDED` | none | `--decision-ref` SHOULD name the successor `catalog_key` (convention, not enforced — Q A5). |

Plus two **read** commands so an operator can find a `catalog_key` and see
state (no writes):

| Command | Wraps |
|---|---|
| `maps skill list [--state STATE]` | `store.list_skill_lifecycle_subjects(state)` |
| `maps skill show <key>` | `store.get_skill_lifecycle_subject(key)` + `list_skill_lifecycle_decisions(key)` |

Each write command maps its verb to the concrete `to_state` and calls
`store.record_skill_lifecycle_transition(key, to_state,
decision_ref=args.decision_ref, decided_by=args.actor)`. The store's own
replay determines the `from_state` and rejects an illegal edge with
`ILLEGAL_SKILL_TRANSITION` — the CLI does not pre-check.

### Q A3 — How does the operator supply the `catalog_key`?

`catalog_key` is a long content-addressed string an operator will not type by
hand. **Decision: accept either the full `catalog_key` OR a
`--source-id/--skill-id/--sha` triple, and also accept an unambiguous prefix
of the `content_sha256`.** Resolution logic (in the CLI, read-only):

1. If the positional arg contains `@sha256:` treat it as a full `catalog_key`,
   pass through unchanged.
2. Otherwise treat it as `<source_id>:<skill_id>` and look up
   `list_skill_lifecycle_subjects()` for rows matching that `source_id` +
   `skill_id`; if exactly one, use its `catalog_key`; if several (multiple
   recorded revisions), refuse with a `MULTIPLE_REVISIONS` error listing the
   `content_sha256` prefixes so the operator can disambiguate with
   `<source_id>:<skill_id>@<sha-prefix>`.
3. `@<sha-prefix>` (< 64 chars) → substring match on `content_sha256`; exactly
   one or refuse `AMBIGUOUS_SHA_PREFIX`.

This resolver is pure read; it never writes and never composes lifecycle
state. Keep it in a small helper (`_resolve_skill_catalog_key(store, arg)`)
that returns `str | MutationResult`.

### Q A4 — `decision_ref` semantics

`decision_ref` is **required and non-empty on every edge** (already enforced
by the store + schema). It is a free-text pointer to the durable record of
the operator's decision — a git commit SHA, a PR/issue URL, a
`work/decisions/*.md` path, or an ADR id. The note does **not** add a format
`CHECK` or a resolver: the operational-learning precedent
(`promote_operational_lesson`'s `decision_ref`) is likewise free text, and a
format regex is scope creep with no consumer. The CLI `--decision-ref` help
string states the intent ("commit / PR / decision-doc reference for this
approval"). It is the audit trail; keeping it mandatory and uniform is the
whole mechanism.

### Q A5 — Idempotency & re-runs

**`record_skill_lifecycle_transition()` is not idempotent and must not be
made so.** It is append-only by design. Consequences, stated:

- Re-running `maps skill approve <key>` after the Skill is already `APPROVED`
  returns `ILLEGAL_SKILL_TRANSITION` (`APPROVED` has no `-> APPROVED` edge).
  That is the correct, safe outcome — a no-op error, nothing written.
- Re-running after a terminal state returns `ILLEGAL_SKILL_TRANSITION` (from
  the pure graph) or `SKILL_DECISION_CONSTRAINT_VIOLATION` (from the
  `no_post_terminal` trigger, if it somehow got past Python). Either way:
  refused, nothing written.
- Two operators racing the same transition: the `BEGIN IMMEDIATE` + in-txn
  replay means the second commit sees the first's decision row and its
  `transition()` call fails. Exactly one row lands. No new work needed — this
  is already how the store behaves; the CLI just surfaces the result.
- The CLI therefore needs **no** `--force`, no `--if-state`, no confirm
  prompt for writes. The store is the guard.

### Q A6 — Failure modes the CLI must surface (not swallow)

| Store result code | Operator-facing meaning | CLI action |
|---|---|---|
| `SKILL_SUBJECT_NOT_FOUND` | No recorded subject for this key — `maps flow start` has not run in this repo yet, or the Skill was edited (new `catalog_key`). | `_emit` the result; exit non-zero. Do **not** auto-run a catalog build. |
| `ILLEGAL_SKILL_TRANSITION` | Wrong current state for this verb (already approved, terminal, etc.). | `_emit`; exit non-zero. |
| `INVALID_DECISION_REF` | `--decision-ref` missing/blank. | argparse `required=True` catches most; store is the backstop. |
| `transition ... requires a non-empty actor` (inside `ILLEGAL_SKILL_TRANSITION`) | `maps skill approve` run without `--actor`. | Make `--actor` `required=True` on the `approve` subparser specifically. |
| `MULTIPLE_REVISIONS` / `AMBIGUOUS_SHA_PREFIX` (new, CLI-level) | Key resolver could not pick one subject. | `_emit` a `MutationResult(False, ...)` listing candidates; exit non-zero. |

### Q A7 — Does A wire anything into an automated path?

**No.** A adds only operator-typed commands + read commands. It does not
touch `flow_start.py`, `context_builder.py`, or `build_project_skill_catalog`.
The refusal that already gates automated behavior (`load_catalog_skill` /
`_select_skills` dropping a `QUARANTINED` Skill) keeps working unchanged and
now has an operator way to *move* a Skill out of `QUARANTINED` (approve) or
confirm it (`retire`).

### Q A8 — Where does the code go?

- `runtime/cli.py`: the `skill` subparser group + arg wiring + the
  `_resolve_skill_catalog_key` helper + `_emit` dispatch. ~5 subcommands.
- No change to `runtime/state/skill_lifecycle_storage.py`,
  `runtime/skills/lifecycle.py`, or `runtime/state/schema.sql`.
- Tests: `tests/test_cli.py` (or a new `tests/test_cli_skill.py`) —
  round-trip each verb against a real temp-file `TaskStore` seeded via
  `record_skill_lifecycle_subject`; assert `approve` without `--actor` fails;
  assert the key resolver's ambiguity errors; assert an illegal edge exits
  non-zero and writes nothing; assert `list`/`show` are read-only.

---

## Item B — operator-identity (SEC4 Half 3)

### The trust-root question is operator-only — flagged

There is **no existing authoritative identity system** to reuse (facts
section). Deciding the trust root — *how operator identity is established at
all* in a CLI that currently trusts its caller, and *who authorizes the first
operator* — is a threat-model decision, not something derivable from the
repo. **This note does not pick it.** It is surfaced to the coordinator as an
explicit operator decision (see "Operator decision required" below). The
design below is valid for the most likely answer (a local append-only
registry in the existing store) and flags where a different answer changes
things.

### Q B1 — Where does the operator-identity source live?

**Recommended (pending the operator decision): a new append-only
`authorized_operators` table in the existing `TaskStore` SQLite file**, same
"immutable rows + append-only status changes" shape as
`operational_lessons` / `skill_lifecycle_*`. Not a config file, not a new DB,
not an external IdP.

```
CREATE TABLE authorized_operators (
    operator_id   TEXT PRIMARY KEY CHECK (length(trim(operator_id)) BETWEEN 1 AND 128),
    display_name  TEXT,
    added_by      TEXT NOT NULL,          -- operator_id of the authorizer, or the genesis sentinel
    decision_ref  TEXT NOT NULL CHECK (length(trim(decision_ref)) BETWEEN 1 AND 512),
    added_at      TEXT NOT NULL,
    created_at    TEXT NOT NULL
);
CREATE TABLE authorized_operator_revocations (
    revocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operator_id   TEXT NOT NULL REFERENCES authorized_operators(operator_id),
    revoked_by    TEXT NOT NULL,
    decision_ref  TEXT NOT NULL,
    revoked_at    TEXT NOT NULL,
    created_at    TEXT NOT NULL
);
-- no-update / no-delete triggers on both, per the house pattern
```

An operator is "authorized as of now" iff it has an `authorized_operators`
row and no `authorized_operator_revocations` row. Composed, never a mutable
`active` column (rule 12 / no-mutable-state house rule).

Alternatives considered:

- **Config file (`.maps/operators.txt` / settings key).** Rejected as the
  primary store: it is a second mutable source of truth outside the canonical
  DB (rule 12), it has no audit trail (who added whom, when, why), and it is
  editable by anyone with repo write — exactly the property an authority
  registry must not have. It *may* be the **bootstrap input** (B2).
- **Reuse `actor_class=OPERATOR` from `outcomes.py`.** That vocabulary stays
  useful for *tagging* an outcome's actor, but it is not a registry and
  extending it into one would overload a descriptive enum with an authority
  role. Keep them separate; a future note could map "is `operator_id` X in
  `authorized_operators`" → "may be tagged `actor_class=OPERATOR`".
- **External IdP / OS user / signed decisions.** Out of scope — unbounded,
  and there is no process-identity story in MAPS to build on.

### Q B2 — Who authorizes an operator? (bootstrap)

This is the operator-only part. The design supports it as: the **genesis
row** is written at `maps init` (or a dedicated `maps operator add`
first-run) from an explicit input the operator must pass — `--operator
<id>` plus `--decision-ref` — with `added_by` set to a reserved sentinel
(`"GENESIS"`). After that, only an already-authorized operator may add or
revoke another (`maps operator add <id> --by <self-id> --decision-ref R`
where `<self-id>` must resolve in `authorized_operators`).

The note does **not** decide:

- whether genesis is `maps init`-time or a separate opt-in step;
- whether the genesis input comes from a CLI arg, an env var, or a
  checked-in config value;
- whether a repo with no `authorized_operators` rows means "identity checks
  disabled" (recommended, = today's behavior) or "all approvals blocked"
  (safer but a hard cutover).

These are the "Operator decision required" items.

### Q B3 — How does the transition entrypoint (A) consult it?

**Opt-in, single call site, default off.** `record_skill_lifecycle_transition`
gains one keyword: `require_authorized_actor: bool = False` (or the check
lives in the CLI layer — see below). When true, before the
`transition()` write-gate, it calls
`store.is_authorized_operator(decided_by)` and returns
`MutationResult(False, "UNAUTHORIZED_ACTOR", ...)` if not.

- `False` (every caller today, and `maps flow start`) → byte-identical to
  current behavior.
- The `maps skill approve` CLI command passes `True` (or applies the check
  itself and only calls the store on success).

**Open sub-decision (low stakes, implementer may pick): does the check belong
in the store method or the CLI?** The half-2 note put read-side enforcement
in `load_catalog_skill`; by that precedent the *authority* check could sit in
the CLI (`maps skill approve` resolves `--actor` against
`is_authorized_operator` before calling the store) and keep the store method a
pure structural recorder. Recommended: **CLI-side**, so the store stays a
faithful recorder of claimed facts (matches its own docstring) and there is no
new store parameter to thread. The store keeps only the existing non-empty
`CHECK`.

### Q B4 — Cross-references (same residual pattern)

- `promote_operational_lesson(promoted_by=...)` — identical unverified-actor
  residual, also zero production callers. Whatever `is_authorized_operator`
  shape lands here should be reused there when operational-lesson promotion
  gets its own entrypoint. Note it as a shared future consumer; do **not**
  wire it in this slice.
- SEC3 `destructive: bool` / #198 `embedded: bool` — same "structural field
  encodes an unchecked trust assumption" shape; the resolution pattern
  (keep field, opt-in real check at one site, default off) is deliberately
  mirrored here so the codebase has one consistent way to retire these.

### Q B5 — Smallest first slice for B

1. `authorized_operators` + `authorized_operator_revocations` tables +
   immutability triggers in `schema.sql`.
2. `AuthorizedOperatorStorageMixin` (`runtime/state/authorized_operator_storage.py`):
   `record_authorized_operator(...)`, `revoke_authorized_operator(...)`,
   `is_authorized_operator(operator_id) -> bool` (composed),
   `list_authorized_operators()`. Registered on `TaskStore` like the other
   mixins.
3. `maps operator add|revoke|list` CLI commands (genesis rule per the
   operator decision).
4. `maps skill approve` resolves `--actor` against `is_authorized_operator`
   **when at least one operator row exists**; empty registry = check skipped
   (= today). This makes the check opt-in-by-data, no flag.
5. Tests: registry round-trip; genesis vs. authorized-adds-authorized;
   revocation; `maps skill approve` blocked for an unknown actor once the
   registry is non-empty; `maps skill approve` unchanged when the registry is
   empty; `maps flow start` and every existing test byte-identical.

Explicitly **not** in slice 1: signing decisions, external identity, mapping
to `actor_class`, wiring `promote_operational_lesson`, any per-Skill or
per-source operator scoping, expiry/rotation.

---

## MUST-NOT list for the eventual impl PR(s)

- MUST NOT re-implement or pre-compose lifecycle state in the CLI — call
  `record_skill_lifecycle_transition()` and let its in-txn replay decide the
  `from_state` (rule 12).
- MUST NOT touch `runtime/skills/lifecycle.py` (transition graph, actor
  rules, public functions) — the 184-line `tests/test_skill_lifecycle.py`
  contract stays green unmodified.
- MUST NOT change `record_skill_lifecycle_subject()` or the subject/decision
  schema for Item A. Item B adds *new* tables only; it does not alter
  `skill_lifecycle_decisions`.
- MUST NOT add a mutable `active`/`state` column anywhere — compose from
  append-only rows (house rule).
- MUST NOT make any existing caller's behavior change: `maps flow start`,
  `build_project_skill_catalog`, `_select_skills`, `load_catalog_skill(store)`
  outputs must be byte-identical. The identity check is opt-in (by flag or by
  registry-non-empty), never on by default in the same PR that introduces it.
- MUST NOT build an operator-identity registry from a config file as the
  canonical store, an external IdP, OS-user detection, or signed decision
  payloads.
- MUST NOT add login / session-auth / credential machinery of any kind — the
  registry answers "is this id currently an authorized operator", nothing
  more.
- MUST NOT make the identity check implicit or default-on in the PR that
  introduces it — it is opt-in (by flag or by registry-non-empty), inert
  until deliberately enabled.
- MUST NOT retroactively validate `decided_by` / `promoted_by` / `actor`
  strings on rows that already exist — the registry gates *new* decisions
  only; historical rows stay as recorded facts.
- MUST NOT auto-approve, auto-activate, or auto-retire on any evidence, gate
  result, age, or source kind.
- MUST NOT wire `maps context` (`cli.py`) to build a catalog (write-on-read).
- MUST NOT add a `superseded_by` FK/column (Q8 of the parent note stands).
- MUST NOT expand Item A into the capability-declaration manifest (SEC4's
  other half, still `NOT STARTED`).

## Smallest-first-slice summary

- **Slice A1:** `maps skill list` + `maps skill show` (read-only) +
  `_resolve_skill_catalog_key`. Zero write risk; gives operators visibility
  immediately. Ships alone.
- **Slice A2:** `maps skill approve|activate|retire|supersede`, each a thin
  `_emit(store.record_skill_lifecycle_transition(...))`. `--actor` still an
  unverified string (structural, matches `promote_operational_lesson`).
- **Slice B1:** the `authorized_operators` registry + `maps operator`
  commands + opt-in check in `maps skill approve` (Q B5). Requires the
  operator decision (below) first.

A2 depends on A1's resolver. B1 depends on A2 existing. A1 + A2 can land in
one PR; B1 is a separate PR after the operator decision.

## STOP conditions for the impl PR

- If Item A's CLI starts needing to compose or cache lifecycle state itself
  (rather than delegating every write to the one store method), STOP — the
  design is being violated; the store owns composition.
- If the `catalog_key` resolver grows beyond the three cases in Q A3 (e.g.
  fuzzy name matching, cross-source dedupe), STOP and flag — that is a
  catalog-query feature, not this task.
- If Item B cannot proceed because the trust-root / bootstrap decision
  (Q B2) has not been made, STOP — build Slice A1 + A2 and flag the
  coordinator for the operator decision.
- If Item B's registry starts acquiring roles beyond "is this id an
  authorized operator right now" (scoping, expiry, delegation, signing),
  STOP — that is beyond the smallest slice.
- If wiring the opt-in check turns out to require changing a default or an
  existing test's expected output, STOP — the check must be inert until
  explicitly enabled.
- If the genesis bootstrap (Q B2) cannot be expressed without a schema
  migration whose shape you are not comfortable pre-deciding, STOP and flag
  the coordinator — do not invent the migration.

## Operator decision required (surface, do not guess)

1. **Trust root:** how is operator identity established in a CLI that today
   trusts its caller? (local registry seeded at init — recommended — vs.
   something else)
2. **Genesis:** who/what writes the first `authorized_operators` row, and via
   what input (CLI arg / env / checked-in config)?
3. **Empty-registry semantics:** does "no authorized operators recorded" mean
   *checks disabled* (recommended, = today's behavior, opt-in-by-data) or
   *all approvals blocked* (hard cutover)?
4. **Should operator-identity be its own note** entirely separate from Item A,
   or is co-designing them here (as done) acceptable?

## Roadmap impact

Does not complete SEC4 or 6.10. Specifies the operator-transition entrypoint
(Item A) precisely enough for a bounded 2-slice PR, and the operator-identity
registry (Item B / Half 3) down to a smallest slice gated on one operator
decision. SEC4's capability-declaration-manifest half stays `NOT STARTED` and
untouched. `work/roadmaps/CAPABILITY_CHECKLIST.md` gets at most a one-line
"design-pending" annotation on the SEC4 row — no status flip.

---

## Resume prompt

You are implementing SEC4 operator-driven lifecycle transitions for
MAPS_Lean. Work in your own git worktree off `origin/main`;
`cd ~/Projects/MAPS_Lean` first and `git fetch origin main`. Re-verify every
callsite/grep claim in this note at your own HEAD (rule 14) before relying on
it.

Source of truth: this note
(`work/notes/2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md`)
and its parents
(`work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md`,
`work/notes/2026-08-31-sec4-half2-authority-wiring-design.md`).

Do **Slice A1 + A2 only** unless the coordinator says the operator decision
(this note's "Operator decision required") is made:

1. `maps skill list [--state STATE]` and `maps skill show <key>` in
   `runtime/cli.py`, thin over `store.list_skill_lifecycle_subjects` /
   `get_skill_lifecycle_subject` + `list_skill_lifecycle_decisions`.
   Read-only.
2. `_resolve_skill_catalog_key(store, arg)` helper — the three cases in Q A3,
   returns `str | MutationResult`.
3. `maps skill approve|activate|retire|supersede <key> --decision-ref R`
   (`approve` also `--actor A`, `required=True`). Each maps its verb to the
   `to_state` and calls
   `store.record_skill_lifecycle_transition(key, to_state,
   decision_ref=args.decision_ref, decided_by=getattr(args,'actor',None))`,
   then `_emit`s the result. No pre-check of the edge — the store's replay
   decides.

MUST NOT: touch `runtime/skills/lifecycle.py`,
`runtime/state/skill_lifecycle_storage.py`,
`runtime/state/schema.sql`, `tests/test_skill_lifecycle.py`. No catalog
build in `maps context`. No auto-approval. No identity registry in this PR
(that is Slice B1, gated on the operator decision).

Tests: `tests/test_cli.py` or new `tests/test_cli_skill.py` — round-trip each
verb against a real temp-file `TaskStore` seeded via
`record_skill_lifecycle_subject`; `approve` without `--actor` exits non-zero;
resolver ambiguity errors; illegal edge exits non-zero and writes nothing;
`list`/`show` never write.

Verification: one blocking foreground
`python3 -m unittest tests.test_cli tests.test_cli_skill
tests.test_skill_lifecycle_storage tests.test_skill_lifecycle` — no
`Monitor`, no background. Push before any full-suite run; rely on CI.
`python3 -m runtime.smoke` must exit 0.

Optionally annotate the `work/roadmaps/CAPABILITY_CHECKLIST.md` SEC4 row
"operator-transition CLI landed; identity registry (Half 3) design-pending" —
no status flip.

PR into `main` (never push to main). Independent review per
`reference_committee_review` (with mutation testing, min 5, for this code
PR). Reviewer commits `work/reviews/pr-<N>-review-evidence.md`. Do not
self-merge. Report the PR number to `niko` via hcom.

Stop conditions: as listed in "STOP conditions for the impl PR" above.
