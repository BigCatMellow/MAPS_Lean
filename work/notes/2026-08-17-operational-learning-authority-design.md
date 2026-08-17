# Operational learning authority — design note

Date: 2026-08-17
Owner: `agent/operational-learning-authority-wave4`
Status: planning evidence only

## Why this lane exists

PR #43 (`runtime/operational_learning.py`) and PR #60
(`runtime/outcome_lesson_candidate.py`) are merged and accepted. Both are
narrow by design:

- `validate_lesson_record()` validates the **shape** of an externally supplied
  lesson dict. It never reads from or writes to any store.
- `project_applicable_lessons()` filters a **given list** of lesson records
  against a **given** context. It never discovers lessons on its own.
- `build_outcome_lesson_candidate()` builds one `CANDIDATE` lesson dict from a
  canonical outcome plus caller-supplied claim/applicability. It never
  persists, promotes, or injects anything.

None of the three functions has ever put a lesson in front of a worker's
actual context, and there is deliberately no `promote()`, no SQLite table, and
no store. The 2026-08-16 reconciliation checkpoint (§9) names the exact next
gap:

> Before operational-learning promotion/persistence: resolve canonical storage
> ownership, promotion/retirement authority, expiry/supersession,
> applicability conflict, precedence, and safe context injection.

This note answers those five questions with staged, smallest-safe-next-step
proposals — the same shape PR #51 used for communication correlation: name the
exact evidence/interface that has to exist first, and stop there. It does not
implement anything. Where the honest answer is "this is a human policy call,"
it says so and does not pick an answer for expedience, per `AGENTS.md` §3
("do not make material assumptions... ask the owner/operator rather than
guessing").

## Ground truth restated

```text
observation / outcome
   → CANDIDATE lesson dict         (#60 builds this; caller supplies claim/applicability)
   → [validate_lesson_record]      (#43; shape only, no authority)
   → ??? persistence ???           <- does not exist
   → ??? promotion to ACTIVE ???   <- does not exist; schema for it exists (promotion sub-dict)
   → [project_applicable_lessons]  (#43; filters a GIVEN list, does not discover one)
   → ??? reaches a worker's context ???  <- does not exist
   → ??? expiry/supersession enforcement ??? <- schema fields exist, no enforcement
   → ??? retirement ???            <- schema for it exists (retirement sub-dict), no mutation path
```

Everything below the first two rows is currently `UNKNOWN` / not built. That is
the correct state today — #43/#60 were both explicitly scoped to exclude it
(see their task docs' "Non-features" / "MUST NOT CHANGE" sections: "no
database/store, mutation API, promotion API, or production injection path").

---

## 1. Canonical storage

### Question

Where do lesson records live once they exist beyond "a dict returned by a
function"?

### Reasoning

Roadmap law 4.1 ("one fact, one authority") and §7.2 ("second task/session
authority database" — rejected by default) both push toward the same answer:
lesson records are a new *kind* of durable object, not a new *authority*.
`TaskStore`'s existing SQLite database is already the single canonical store
for run manifests, outcomes, review evidence, and cross-source relationship
tables (`run_helper_links`, `run_recovery_links`, `run_environment_evidence`).
A second SQLite file, or an in-process registry, or a JSON file on disk would
each create a second mutable truth for something (lesson lifecycle state) that
is exactly the kind of fact `TaskStore` already exists to hold under "one
fact, one authority."

The existing house style for this kind of record (see `run_helper_links`,
`run_recovery_links` in `runtime/state/schema.sql`) is: **append-only rows**,
`INTEGER PRIMARY KEY AUTOINCREMENT` or a validated text ID, `created_by` +
`created_at` on every row, `CHECK` constraints doing the same shape validation
`validate_lesson_record()` already does in Python, and explicit
`BEFORE UPDATE` / `BEFORE DELETE` triggers that `RAISE(ABORT, ...)` — so the
row can never be silently mutated in place. Lifecycle transitions (candidate →
active → retired, or superseded-by) are modeled as **new rows referencing the
old row**, not as `UPDATE` statements on the original row. That mirrors how
`run_recovery_links` models "this run replaced that run" as a new linking row
rather than mutating `run_manifests`.

### Illustrative schema sketch (design prose only — not an authorized schema edit)

```sql
-- Canonical lesson snapshots. Each row is one immutable validated lesson
-- record as accepted by runtime.operational_learning.validate_lesson_record().
-- A lifecycle change (promotion, retirement, supersession) is recorded as a
-- NEW row, never as an UPDATE to an existing row. lesson_id is the stable
-- semantic identity (see outcome_lesson_candidate._candidate_id); lesson_row_id
-- is the append-only storage key.
CREATE TABLE IF NOT EXISTS operational_lessons (
    lesson_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id TEXT NOT NULL CHECK (length(trim(lesson_id)) BETWEEN 1 AND 128),
    lesson_version INTEGER NOT NULL CHECK (lesson_version = 1),
    status TEXT NOT NULL CHECK (status IN ('CANDIDATE','ACTIVE','RETIRED')),
    claim TEXT NOT NULL,
    source_kind TEXT NOT NULL CHECK (source_kind IN (
        'TASK_OUTCOME','INCIDENT','OPERATOR_OBSERVATION','NON_TASK_OBSERVATION','RESEARCH'
    )),
    source_refs_json TEXT NOT NULL,        -- validated list, stored as JSON text
    applicability_json TEXT NOT NULL,      -- validated applicability dict, JSON text
    created_by TEXT NOT NULL CHECK (length(trim(created_by)) BETWEEN 1 AND 128),
    created_at TEXT NOT NULL,
    promotion_json TEXT,                   -- NULL unless this row already carries promotion evidence
    retirement_json TEXT,                  -- NULL unless this row is a RETIRED snapshot
    superseded_by TEXT,                    -- lesson_id of the superseding lesson, or NULL
    supersedes_row_id INTEGER REFERENCES operational_lessons(lesson_row_id),
    evidence_ref TEXT NOT NULL CHECK (length(trim(evidence_ref)) BETWEEN 1 AND 256)
);
CREATE INDEX IF NOT EXISTS idx_operational_lessons_lesson_id
    ON operational_lessons(lesson_id, created_at);

CREATE TRIGGER IF NOT EXISTS trg_operational_lessons_no_update
BEFORE UPDATE ON operational_lessons
BEGIN
    SELECT RAISE(ABORT, 'operational lesson snapshots are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_operational_lessons_no_delete
BEFORE DELETE ON operational_lessons
BEGIN
    SELECT RAISE(ABORT, 'operational lesson snapshots are immutable');
END;
```

Every insert should be validated in Python through the existing
`validate_lesson_record()` before the row is written — the table's `CHECK`
constraints are a second, cheaper backstop, not a replacement for that
validation, matching how `run_helper_links`/`run_recovery_links` pair SQLite
`CHECK`s with Python-level construction functions.

Deliberately **not** in this sketch: no `UPDATE ... SET status = 'ACTIVE'`
path. Promotion, retirement, and supersession are each a new
`validate_lesson_record()`-approved row with a later `created_at`, linked back
via `lesson_id` (same semantic lesson) and `supersedes_row_id` /
`superseded_by` (explicit lineage). This is consistent with #43's own
`validate_lesson_record()`, which already treats a lesson record as a
timestamped snapshot with `promotion`/`retirement` sub-schemas rather than a
row with mutable columns.

### Staged smallest-safe-next-step

1. **Storage-0**: land only the table + triggers above (or a corrected variant
   after review) inside `runtime/state/schema.sql`, with an `insert-only`
   Python helper that calls `validate_lesson_record()` first and then inserts
   exactly one row. No promotion/retirement mutation logic yet — this step
   only proves CANDIDATE rows can be durably recorded and read back.
2. **Storage-1** (after Promotion authority, below, is decided): a second
   insert path that writes an ACTIVE or RETIRED snapshot row, gated by
   whatever authority mechanism the operator selects.

This is an owner-decidable design area — no operator policy call is required
to choose "existing `TaskStore` SQLite, append-only rows" over "a new store,"
because that is dictated by the existing "one fact, one authority" law, not a
new tradeoff.

---

## 2. Promotion / retirement authority

### Question

Who or what is allowed to move a lesson `CANDIDATE → ACTIVE`, or
`ACTIVE → RETIRED`?

### Why this repo's existing role model does not resolve it

TOWER (dispatch/checkpointing), ANVIL (implementation), FOUNDRY
(planning/dev-ownership), SENTINEL (independent review), and SWITCHYARD
(integration order/merge authority) are all roles that exist to move **code**
through a lifecycle (task → PR → reviewed → merged). None of them is defined
as owning **policy** promotion — the decision that a piece of guidance is now
trusted enough to shape how future agents work. SWITCHYARD's merge authority
is the closest analog structurally (gatekeeper before something becomes
"real"), but merging code and promoting operational guidance are different
kinds of authority: a bad merge is caught by tests/review/rollback; bad
promoted guidance can quietly bias many future agents' behavior before anyone
notices, which is exactly the harm Wave 6's non-goal is warning about:

> MAPS never says: "I changed my own policy because my internal metric
> improved." The output is a proposal with evidence, not self-authorization.

Assigning promotion authority to an existing code-lifecycle role by default
would be exactly the kind of "do not make material assumptions... about
authority" violation `AGENTS.md` warns against. This task does not do that.

### Real options (not resolved here — operator decision required)

**Option A — Operator-only approval, every time.**
Every `CANDIDATE → ACTIVE` and every `ACTIVE → RETIRED` transition requires an
explicit human operator action (e.g., an operator-authored `decision_ref`,
exactly as `_promotion`/`_retirement` already require `promoted_by` /
`retired_by` / `decision_ref`). No automatic path exists at all.

- Tradeoffs: maximally safe, matches Wave 6's non-goal literally, and needs no
  new evidence-gate design. Cost: does not scale — if operational-learning
  volume grows, this becomes a bottleneck, and "operator-only" can decay into
  "operator rubber-stamps whatever an agent hands them," which is not actually
  safer than a well-designed gate.

**Option B — Bounded automatic promotion under strict evidence gates.**
A lesson may be mechanically promoted only if it clears a pre-defined,
narrow, high-bar evidence gate (e.g., N independent outcome-linked
observations, from N distinct tasks/runs, with no counter-examples, reviewed
by a frozen-eval-style check rather than a live metric) — analogous to how
§6.31 (Controlled harness refinement) requires "frozen comparison" plus
"safety/correctness/cost/outcome evaluation" before even a *proposal* is
made.

- Tradeoffs: scales; keeps humans out of the loop for well-evidenced,
  low-risk lessons. Cost: is exactly the shape of self-authorizing refinement
  Wave 6's non-goal forbids if the evidence gate is ever internally
  self-referential (e.g., "my own metric improved" is itself the gate). Any
  Option B design would need the gate's evidence to be external/outcome-based,
  not a self-reported confidence score, and would still need an operator to
  approve the *gate design itself* even if not every individual promotion.
  This is a genuine "how much autonomy" tradeoff, not a detail.

**Option C — Hybrid: automatic promotion to a lower-trust "REVIEW_PENDING"
tier, human required only for reaching full `ACTIVE`.**
A candidate meeting Option B's evidence bar could auto-advance to a
non-projecting intermediate state that is visible to the operator as a
queued, evidence-backed proposal, but `project_applicable_lessons()` (or its
future successor) still withholds anything short of operator-confirmed
`ACTIVE`.

- Tradeoffs: reduces operator toil to "review queue triage" instead of
  "originate every promotion," while keeping the actual authority boundary at
  the human. Cost: adds a state (and its own lifecycle/queue-staleness
  questions) that must itself follow roadmap law 4.6 ("durable state needs
  lifecycle").

Retirement is the lower-risk mirror of the same question (moving something
*out* of guidance is safer by default than moving something *in*), but the
same three shapes apply: operator-only, automatic-on-expiry (see §3 below,
which is somewhat different — expiry is closer to Option B's mechanical case
because *not renewing* is a safe default, whereas early/for-cause retirement
of an otherwise-valid ACTIVE lesson is closer to Option A).

### Staged smallest-safe-next-step

1. **Authority-0** (no operator decision needed): implement Storage-0 above
   (append-only CANDIDATE rows) with **no** promotion path at all. This is
   pure landing of already-accepted CANDIDATE-building behavior into durable
   storage.
2. **Authority-1** (operator decision required before starting): once the
   operator picks A, B, or C, shape a narrowly bounded task for exactly that
   mechanism — do not build all three "just in case."

### Operator decision required

Which of A/B/C (or a variant) governs promotion, and separately, whether
retirement uses the same or a different mechanism. This task explicitly does
not pick one.

---

## 3. Expiry / supersession

### Question

What happens mechanically when `expires_at` passes with no renewal, and how
does a new lesson supersede an old one (`superseded_by` already exists as a
field in `_LESSON_KEYS`)?

### Reasoning

`project_applicable_lessons()` already treats `EXPIRED` and `SUPERSEDED` as
withholding reasons computed **at projection time** from the `expires_at`
timestamp and the `superseded_by` field — it does not need a background job to
know a lesson is expired; it recomputes that on every call using `at`.
This means the *projection* side of expiry is already mechanical and requires
no new authority: `now >= expires_at` is a pure fact, not a policy judgment,
exactly like `run_recovery_links`'s `trg_run_recovery_chronological` trigger
enforces a pure temporal fact via SQLite rather than requiring human
adjudication.

What is **not** mechanical, and does require the same authority as promotion
(§2), is *renewal* — deciding a still-useful lesson should get a new
`review_at`/`expires_at` window. Renewal is functionally a re-promotion: it
extends the period during which guidance is trusted, so it should carry the
same `decision_ref`/`promoted_by` evidence a fresh promotion would, recorded
as a new row (per §1) rather than an `UPDATE` to the expiring row.

Supersession splits the same way:

- **Detecting** that lesson B's `source_refs`/`applicability` claim to replace
  lesson A (via `superseded_by`) is a pure fact once someone has asserted it —
  SQLite can enforce referential integrity (the target `lesson_id` must exist,
  cannot supersede itself, per the existing `validate_lesson_record()` check).
- **Deciding** that B *should* supersede A is a promotion-shaped judgment
  (does B's evidence actually improve on A's?), so asserting `superseded_by`
  on an ACTIVE lesson should require the same authority as promoting B in the
  first place — otherwise supersession becomes a backdoor around whatever
  promotion gate is chosen in §2.

### Staged smallest-safe-next-step

1. **Lifecycle-0** (mechanical, owner-decidable, no new authority): keep
   expiry/supersession/review-due as **projection-time computed facts**,
   exactly as #43 already does. No scheduled job, no cron, no daemon — this
   matches roadmap law 4.9 ("deterministic chores should not become agents")
   and §7.1 (reject a persistent supervisor daemon by default). A lapsed
   lesson simply stops projecting the next time `project_applicable_lessons()`
   runs; nothing needs to "notice" it expired.
2. **Lifecycle-1** (requires §2's authority decision): renewal and
   assert-supersession both go through whatever promotion mechanism is chosen,
   written as a new append-only row referencing the prior `lesson_id`.

### Operator decision required

None *specific* to this section beyond what §2 already requires — expiry
detection itself needs no new operator decision; renewal/supersession inherit
§2's decision.

---

## 4. Applicability conflict / precedence

### Question

If two `ACTIVE` lessons both match the same context (`global`/`project_ids`/
`task_types`/`risk_levels`/`path_prefixes`) and give conflicting guidance,
what resolves it?

### Reasoning

`_match_applicability()` already returns `MATCH` / `NO_MATCH` / `UNKNOWN`, and
`project_applicable_lessons()` already withholds `UNKNOWN` matches rather than
guessing. That is the load-bearing precedent: this codebase's answer to "we
are not sure" is **withhold and surface**, not "pick one and move on." The
same discipline should apply to *conflict*, which is a harder case than
`UNKNOWN` because both lessons individually pass validation and match — the
system would have to invent a preference between two equally well-formed,
independently promoted claims.

Two silent-precedence rules an implementation might be tempted to reach for,
and why they are unsafe as an automatic default:

- **"Most specific applicability wins"** (e.g., a `path_prefixes`-scoped
  lesson beats a `global` one). This is a defensible *default* in many rule
  systems, but it is a genuine policy choice about what "more applicable"
  means, and MAPS has no existing precedent that specificity implies
  correctness — a broad lesson could be the newer, better-evidenced one.
  Silently applying this is exactly the kind of inference `AGENTS.md`/roadmap
  law 4.4 ("do not infer... from probably") warns against, because
  specificity is a proxy, not a proof of which claim is actually right.
- **"Most recent promotion wins"** (`starts_at` or `promotion_at`
  tie-break). Recency is *evidence* worth surfacing, but treating it as an
  automatic winner assumes newer is always better, which is not something
  #43's schema asserts anywhere — it is silent on recency-as-correctness.

Because both of these are plausible-sounding heuristics rather than proven
facts, and this codebase's own applicability matcher already chose
"withhold + surface" over "infer a match," the same posture should extend to
conflicting matches:

### Staged smallest-safe-next-step

1. **Conflict-0** (owner-decidable, no operator policy call): extend
   projection (as a **new, additively-versioned** projection field, not a
   change to #43's existing contract) to **detect** and **surface** — not
   resolve — the case where two or more currently-`MATCH`ing `ACTIVE` lessons
   are returned for the same context. This is pure evidence surfacing: report
   `{"lesson_ids": [...], "reason": "MULTIPLE_MATCHES"}` (or similar) alongside
   the existing `projected`/`withheld` lists, and let whatever consumes the
   projection (a human reviewer, or eventually a bounded UI) see that more
   than one lesson applies. This does not require deciding precedence — it
   only requires being honest that more than one exists.
2. **Conflict-1** (operator decision required): whether/how MAPS is ever
   allowed to auto-resolve a genuine **semantic** conflict (two lessons that
   actively disagree, not just two that both apply) versus always surfacing
   both for a human to reconcile. Note this is a strictly harder problem than
   "both match" — detecting that two claims *semantically contradict* likely
   requires either explicit authoring discipline (lessons declare what they
   supersede/conflict with at creation time) or a human judgment call; MAPS
   should not attempt automatic natural-language conflict detection between
   claims, since that is exactly the kind of "probably" inference the
   negative operating contract prohibits.

### Operator decision required

Whether multiple simultaneously-applicable ACTIVE lessons are (a) always
surfaced together with no precedence at all (safest, but pushes
reconciliation work onto whoever consumes guidance), (b) resolved by an
explicit precedence rule the operator picks and authors (e.g., specificity or
recency, adopted as policy rather than inferred), or (c) prevented at
promotion time by requiring new lessons to explicitly declare
`superseded_by`/non-overlap with existing ACTIVE lessons before they can be
promoted at all. This task does not choose among (a)/(b)/(c).

---

## 5. Safe context injection

### Question

How would an `ACTIVE` lesson actually reach a worker's context without
becoming unreviewed policy the agent just obeys?

### Reasoning

This is the most safety-sensitive of the five, and the existing code already
encodes the right posture: `project_applicable_lessons()` labels every
projected item `"authority": "GUIDANCE_ONLY"` and returns a top-level
`authority` block asserting `can_grant_task_authority: False`,
`can_grant_policy_authority: False`, `can_promote_candidates: False`. That is
the correct shape — the question is only how that already-labeled guidance
physically reaches a worker's context without the label being lost along the
way.

Roadmap law 4.2 ("capability is not authority") is exactly on point: being
*able* to surface a lesson's claim text into a prompt does not make it
authorized to act like an instruction. And law 4.7 ("derived views stay
derived") already establishes the pattern this should follow: Context Builder
surfaces evidence (outcomes, task state, prior review notes) as *cited,
attributed source material* the agent reads and reasons about — it does not
splice raw text into the system prompt as if it were an instruction from the
operator. An ACTIVE lesson claim should be surfaced the same way: as one more
attributed evidence item in whatever Context Builder already does for other
evidence classes, carrying its `lesson_id`, `source_kind`, `source_refs`, and
`promotion_decision_ref` (all already present in the projection) so a worker
or reviewer can trace *why* this text is here and that it is "GUIDANCE_ONLY,"
not a directive.

This also ties directly to the Wave 6 non-goal: if a lesson claim were ever
injected as unattributed instruction text, "the model behaved differently
because a promoted lesson said so" would functionally become the model
self-modifying its own effective policy the moment enough lessons accumulate
— exactly what Wave 6 forbids, even though no single step looks like
"self-authorization." The boundary has to be enforced at the injection point,
not just at promotion.

### Concrete design constraints for a future injection mechanism

- The injected representation must preserve the `GUIDANCE_ONLY` /
  `can_grant_*: False` labels through to wherever the worker actually reads
  it — not just at the projection function's return value.
- It must be visibly attributed (lesson ID + decision ref), the same way
  Context Builder's other evidence is attributed, so a human or downstream
  reviewer can trace and challenge it.
- It must never be the sole/authoritative source for anything that requires
  actual task/policy/review authority (matches existing `authority` block
  already asserting this in code — the design must not weaken that).
- It should be excludable/filterable the same way other Context Builder
  sources are (budget-constrained context, per roadmap §6.11 "context
  budgets"), not force-included as if mandatory.

### Staged smallest-safe-next-step

1. **Injection-0** (owner-decidable design, no runtime change yet): specify
   the exact shape a lesson-guidance evidence item would take *inside* an
   existing Context Builder evidence class, reusing the projection's existing
   fields (`lesson_id`, `claim`, `source_kind`, `source_refs`,
   `promotion_decision_ref`, `authority: "GUIDANCE_ONLY"`), without writing
   the integration code. This is scoping the interface, not building it.
2. **Injection-1** (operator decision required): whether *any* automatic
   inclusion in a worker's context is authorized at all, versus lessons
   remaining something a human/operator manually cites when relevant. Even a
   read-only, clearly-labeled evidence item is a step up in reach compared to
   today (where #43's projection output currently reaches nothing), so the
   decision to wire it into live Context Builder output — even in
   advisory form — is exactly the kind of "production Context
   Builder/startup integration" #43's own task doc named as something that
   must escalate, not something this design resolves.

### Operator decision required

Whether/when ACTIVE lesson guidance is allowed to appear in a worker's actual
context at all (versus staying a query-only projection a human consults), and
if so, whether "another attributed Context Builder evidence source" is a
strong enough boundary or whether an even stronger boundary (e.g., requiring
a human to manually attach it per-task rather than any automatic surfacing) is
required. This task does not choose.

---

## Summary table

| Area | Mechanical / owner-decidable now | Requires operator decision |
|---|---|---|
| 1. Canonical storage | Yes — reuse `TaskStore` SQLite, append-only rows + immutability triggers, house-style schema sketch above | No (dictated by existing "one fact, one authority" law) |
| 2. Promotion/retirement authority | No | **Yes** — Option A (operator-only) vs B (bounded automatic evidence gate) vs C (hybrid queue) |
| 3. Expiry/supersession | Expiry detection: yes, projection-time computed fact, no new authority | Renewal and asserting supersession inherit §2's answer |
| 4. Applicability conflict/precedence | Detecting + surfacing multiple matches: yes | **Yes** — whether/how to ever auto-resolve a genuine conflict, or require non-overlap at promotion time |
| 5. Safe context injection | Interface shape (attributed, `GUIDANCE_ONLY`-labeled evidence item): yes, design only | **Yes** — whether any automatic worker-context inclusion is authorized at all, and how strong the boundary must be |

## Explicit non-goals of this note

- No SQLite migration is applied; the schema sketch in §1 is illustrative
  prose only.
- No promotion/retirement mechanism is chosen or implemented.
- No Context Builder integration code is written.
- No claim is made that any existing role (TOWER/ANVIL/FOUNDRY/SENTINEL/
  SWITCHYARD) already owns promotion authority; this note explicitly declines
  to assign it.

## Recommended continuation

```text
operator decisions on #2 (promotion authority) and #5 (injection boundary)
        ↓
re-check this design against then-current main head
        ↓
Storage-0: append-only CANDIDATE row landing in schema.sql (no promotion path)
        ↓
Authority-1: implement exactly the chosen promotion/retirement mechanism
        ↓
Lifecycle-1: renewal/supersession using that same mechanism
        ↓
Conflict-0: multi-match detection/surfacing in projection output
        ↓
Injection-0 → Injection-1: attributed GUIDANCE_ONLY evidence item, only if
    operator authorizes any automatic worker-context inclusion
```

Until those two operator decisions land, operational-learning persistence and
promotion correctly remain `BLOCKED_ON_OPERATOR_DECISION`, not an invitation
to infer a default.

## Operator decisions (recorded 2026-08-17)

The operator reviewed the three flagged questions and decided:

1. **Promotion/retirement authority: Option A — operator-only, every promotion and every retirement.** Rationale: matches Wave 6's own stated "review/operator promotion gate" requirement and its explicit non-goal ("MAPS never says: I changed my own policy because my internal metric improved"). Revisable later once there is real operational history to justify a bounded automatic path, but that is not this decision.
2. **Applicability conflict/precedence: surface conflicts as evidence, do not auto-resolve.** No specificity/recency heuristic is authorized. A conflict between two ACTIVE lessons matching the same context remains visible, unresolved evidence rather than a silently-picked winner.
3. **Safe context injection: authorized, bounded to operator-promoted ACTIVE lessons only, as an attributed `GUIDANCE_ONLY` Context Builder evidence item — never spliced into instructions.** Because promotion now requires an explicit human decision (per #1 above), this is a safe next surface: a worker sees labeled, sourced guidance the same way it sees any other evidence, never something it is structurally obligated to obey.

## Unblocked next step

With #1-#3 decided, `Storage-0` (append-only `CANDIDATE` row landing in schema, no promotion path) is now authorized as a bounded implementation task. `Authority-1` (implementing the chosen operator-only promotion mechanism) and `Injection-0/1` (the attributed `GUIDANCE_ONLY` evidence surface) are also authorized in scope, but as separate bounded tasks from `Storage-0` — do not combine them into one unreviewed implementation.
