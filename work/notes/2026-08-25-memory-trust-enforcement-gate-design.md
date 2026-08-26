# Memory trust enforcement gate design (roadmap 6.22)

Date: 2026-08-25
Owner: `/root`
Status: design complete; no runtime code changed

Scope: this note designs the *gate* that consumes the `MemoryTrustClass`
vocabulary (PR #127) and the Context Builder annotations (PR #149) on the
enforcement seam already selected by PR #148. It does not re-open the seam
choice, does not define new vocabulary, and changes no runtime behavior.

## 1. Finding

Verified against `origin/main@8923adb`, and re-confirmed unchanged at the
rebase base `65e140b` (the only intervening commit on `main` is docs-only).

### 1a. The vocabulary exists and is inert by its own admission

`runtime/trust.py` defines the full 11-member enum in roadmap order:

```python
class MemoryTrustClass(str, Enum):
    """The roadmap's 11 candidate memory trust classes, in roadmap order."""
    UNTRUSTED_INPUT = "UNTRUSTED_INPUT"
    OBSERVATION = "OBSERVATION"
    CLAIM = "CLAIM"
    CANDIDATE_LESSON = "CANDIDATE_LESSON"
    REVIEWED_GUIDANCE = "REVIEWED_GUIDANCE"
    APPROVED_SKILL = "APPROVED_SKILL"
    ACTIVE_INSTRUCTION = "ACTIVE_INSTRUCTION"
    CANONICAL_POLICY = "CANONICAL_POLICY"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"
    QUARANTINED = "QUARANTINED"
```

plus three read-only correspondence mappings (`skill_trust_class`,
`skill_lifecycle_trust_class`, `operational_learning_trust_class`) and a
`TrustClassError`. The module docstring states its own limit verbatim:

> "it is NOT wired into any decision-gating code path. Actually gating real
> behavior (e.g. 'only ACTIVE_INSTRUCTION or CANONICAL_POLICY content may
> influence a tool call') on `MemoryTrustClass` is deliberately out of scope
> and left for a future task"

That future task is this one.

### 1b. PR #148's selected seam, exactly

PR #148 ("Design memory trust enforcement seam", merged 2026-08-21, branch
`rns-harness-callsite-task`) landed
`work/notes/2026-08-21-memory-trust-enforcement-design.md`, whose
"Decision: first seam is Context Builder evidence annotation and validation"
section reads:

> "The first implementation should wire `MemoryTrustClass` into
> `runtime/context_builder.py` as metadata on memory-like evidence that
> Context Builder already emits: operational-learning `guidance` /
> `withheld_guidance`; Skill selection metadata under `skills`."

So the seam is **`runtime/context_builder.py::build_context_plan()`'s
memory-like evidence buckets** — `guidance`, `withheld_guidance`, `skills` —
and specifically the two producers `_lesson_guidance()` and
`_select_skills()`. This is a prior decision; this note builds on it.

Note the seam is deliberately *not* Hook-based. Unlike SEC3
(`work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`, whose
`DestructiveExternalActionGuard` now lives in
`runtime/policy/destructive_action_guard.py` behind
`HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION`), Context Builder sits on no
Hook path: `grep -n "hook" runtime/context_builder.py` returns nothing, and
its only production callers are `runtime/cli.py:333` and
`runtime/flow_start.py:80` — both direct function calls. A
`HookEnforcement`-style gate is therefore *not* the natural mechanism here;
imposing one would mean routing Context Builder through `HarnessService`
purely to host a guard, which is new infrastructure for a one-off need. The
SEC3 note's *shape* (fail-closed, caller/context-supplied classification, a
deterministic pure decision function, no policy DSL) is what carries over —
not its Hook plumbing.

### 1c. PR #149 annotated; nothing yet decides

`runtime/context_builder.py` now stamps `trust_class` onto memory-like
evidence:

- `_lesson_guidance()` line 155 stamps every projected lesson
  `operational_learning_trust_class("ACTIVE").value` (i.e.
  `REVIEWED_GUIDANCE`);
- `_withheld_lesson_with_trust_class()` maps the withholding *reason*
  (`CANDIDATE_NOT_PROMOTED`/`RETIRED`/`SUPERSEDED`) to a class and sets
  `stale_trust_metadata: True` for `EXPIRED`/`REVIEW_DUE`;
- `_select_skills()` line 252 stamps `skill_trust_class(entry.provenance.
  trust_state).value` (always `OBSERVATION` today, since `SkillTrustState`
  has only `UNASSESSED`).

**Confirmed: no allow/deny/withhold decision reads any of it.** Evidence:

- `grep -rn "trust_class" runtime/ --include=*.py` outside
  `context_builder.py` returns only the three *producer* function
  definitions in `runtime/trust.py`. No consumer exists anywhere else in
  `runtime/`.
- Inside `context_builder.py` the only *read* of a stamped `trust_class` is
  `build_context_plan()` lines 399-403:

  ```python
  memory_like = [*guidance, *withheld_guidance, *skills]
  memory_trust_classification_present = all(
      isinstance(item.get("trust_class"), str) and bool(item["trust_class"].strip())
      for item in memory_like
  )
  ```

  That is a presence/coverage boolean surfaced under `coverage`. It checks
  that a label exists; it never inspects *which* label, and no branch
  anywhere changes what is emitted based on its value. It is observability,
  not a gate — precisely the gap
  `work/notes/2026-08-24-roadmap-trajectory-check-7.md` §5b item 2 names:
  "Still no gate consults `MemoryTrustClass` for a real decision."

### 1d. The concrete defect this leaves open

Because classification and routing are computed in parallel from the same
upstream status rather than one deriving from the other, the label currently
*asserts* trust instead of *checking* it:

- `_select_skills()` emits every matched Skill with
  `"budget_class": "SHOULD_LOAD"` while stamping it `OBSERVATION` — a class
  the #148 class/action table says "must not influence ... loaded
  instructions". Nothing enforces that; the SHOULD_LOAD tag is assigned
  before and independently of the class. **This is the concrete, presently
  reachable gap.**
- `_lesson_guidance()` stamps `REVIEWED_GUIDANCE` on **every** item in
  `projection["projected"]`, unconditionally — a constant, not a check.
  Scope limit, stated plainly: `project_applicable_lessons()`
  (`runtime/operational_learning.py:381-386`) already routes `RETIRED`,
  `CANDIDATE`, and superseded lessons into `withheld` *before*
  `_lesson_guidance()` ever sees them, and the projected item it emits
  (`runtime/operational_learning.py:413-422`) carries only `lesson_id`,
  `claim`, `source_kind`, `source_refs`, `promotion_decision_ref`, and
  `authority` — **no `status` and no `reason` field**. So a gate placed at
  `_lesson_guidance()` has nothing to re-derive a class *from*, and the
  residual threat (a projection bug that lets a retired lesson through) is
  exactly the case such a gate cannot detect with today's data shape. The
  unconditional stamp is therefore an honesty defect in the label, not a
  currently exploitable laundering path, and closing it properly requires an
  upstream change to what `project_applicable_lessons()` carries — see
  §2b's scope statement and open question 4h. This note does not assume that
  change.

This is also a duplicate-truth violation (global rule 12): two mutable
derivations of the same fact, with nothing making the second answerable to
the first.

## 2. Proposed gate: `admit_memory_evidence()` — one pure admission decision

Add one module-private choke point in `runtime/context_builder.py` (or a
small `runtime/trust_gate.py` if the implementation prefers to keep it
testable in isolation — see open question 4f) through which **every**
memory-like item must pass before it can enter a plan bucket. Nothing else
in the plan changes.

### 2a. The decision it makes

`admit_memory_evidence(trust_class, *, stale) -> MemoryAdmission`, a pure
deterministic function of the item's `MemoryTrustClass` (plus its
`stale_trust_metadata` flag), returning one of three outcomes:

| Outcome | Meaning | Effect on the plan |
|---|---|---|
| `LOAD` | admissible to the default load set | item keeps `budget_class: SHOULD_LOAD` and stays in `guidance` / `skills` |
| `WITHHOLD` | may be *named* but never default-loaded | item moves to `withheld_guidance` (or the skills equivalent) with `budget_class: ON_DEMAND` and an added `withheld_reason` |
| `DENY` | must not appear in the plan at all | item is dropped entirely and counted in a `denied` tally under `coverage` |

The admission table, derived directly from #148's class/action table (no new
vocabulary, no new semantics):

| `MemoryTrustClass` | Admission |
|---|---|
| `CANONICAL_POLICY` | `LOAD` |
| `ACTIVE_INSTRUCTION` | `LOAD` (see caveat below) |
| `APPROVED_SKILL` | `LOAD` |
| `REVIEWED_GUIDANCE` | `LOAD` |
| `CANDIDATE_LESSON` | `WITHHOLD` |
| `CLAIM` | `WITHHOLD` |
| `OBSERVATION` | `WITHHOLD` |
| `SUPERSEDED` | `WITHHOLD` |
| `RETIRED` | `WITHHOLD` |
| `UNTRUSTED_INPUT` | `DENY` |
| `QUARANTINED` | `DENY` |
| *missing / unparseable / mapping error* | `WITHHOLD` if the withheld form carries no content, else `DENY` (see 2e) |

`stale=True` (today's `stale_trust_metadata`, set for `EXPIRED` /
`REVIEW_DUE`) demotes `LOAD` to `WITHHOLD`; it never promotes.

Two caveats on the table, both deliberate:

- **This is an explicit table, not a comparison against enum declaration
  order.** `SUPERSEDED`, `RETIRED`, and `QUARANTINED` are declared *after*
  `CANONICAL_POLICY` in `MemoryTrustClass` but do not load. Implement it as
  a literal dict keyed by class; do not implement it as `class >= threshold`
  over `Enum` ordering, which would admit all three.
- **`ACTIVE_INSTRUCTION`'s `LOAD` is unconditional here, where #148's table
  conditions it** ("only if a separate Skill loader task proves the source
  active"). No current producer can emit `ACTIVE_INSTRUCTION` at this seam —
  it is reachable only through `skill_lifecycle_trust_class()`, which
  Context Builder does not call, since `_select_skills()` reads
  `entry.provenance.trust_state` (always `UNASSESSED`) and no durable Skill
  lifecycle state exists yet (see the SEC4/6.10 persistence design note).
  The row is therefore unreachable today; the implementation must either
  keep it unreachable or carry #148's condition forward verbatim rather than
  silently widening it. Same for `CANONICAL_POLICY`, which no memory-like
  producer emits at all.

Beyond those, no configuration surface, no per-project override, no severity
matrix.

### 2b. What "a real decision" looks like concretely

Three behaviors change, all observable in the emitted plan and all
mechanically testable:

1. **`OBSERVATION` Skills stop being SHOULD_LOAD.** Every matched Skill
   today carries `trust_class: OBSERVATION` *and* `budget_class:
   SHOULD_LOAD`. Under the gate, `OBSERVATION` → `WITHHOLD`, so matched but
   unassessed Skills appear as `ON_DEMAND` metadata with a withheld reason
   and are no longer part of the default load set. This is a real,
   currently-visible behavior change (`tests/test_context_builder.py:202`
   asserts the current SHOULD_LOAD tag and would need updating — see open
   question 4c), and it is exactly the invariant the #148 table asserts and
   nothing enforces. **This is the load-bearing behavior change of this
   design**; the other two are structural.
2. **Budget class is assigned *by* the class, not alongside it.** Today the
   `SHOULD_LOAD` / `ON_DEMAND` tag is a literal written at
   `context_builder.py:269` and lines 394-397, computed in parallel with the
   trust class from the same upstream status. After the gate, membership in
   `guidance` / `withheld_guidance` / `skills` and the budget class are
   *outputs of* `admit_memory_evidence()` and of nothing else. That removes
   the duplicate-truth violation (global rule 12): there is one derivation,
   and any future producer that emits a low class cannot also hand itself a
   SHOULD_LOAD tag. The `stale_trust_metadata` flag set at
   `context_builder.py:177` likewise stops being decorative and becomes a
   gate input that demotes.
3. **A quarantined or untrusted item cannot appear at all.** `QUARANTINED` /
   `UNTRUSTED_INPUT` are dropped rather than withheld, because for any item
   whose withheld form carries its own content (Skill `name` /
   `description`) being "named in the plan" is itself the poisoning
   surface. The count surfaces under `coverage` so the drop is auditable
   rather than silent. Unreachable at this seam today (no producer emits
   either class); it is the standing rule for when one does.

Honest scope statement: on the **guidance** path specifically, this design
changes no output for any input `project_applicable_lessons()` can produce
today, because that function already routes retired/candidate/superseded
lessons to `withheld` upstream (§1d) and hands `_lesson_guidance()` no
`status` to re-check. The guidance path gets structural correctness (item 2)
and readiness for open question 4h; the **skills** path gets the actual
allow/withhold behavior change (item 1). The note claims nothing stronger.

### 2c. Where exactly it plugs in

Three call sites, all inside the seam #148 selected:

- `_lesson_guidance()` (`runtime/context_builder.py:125-165`) — keep the
  `operational_learning_trust_class("ACTIVE")` derivation for
  `projection["projected"]` (there is no per-item status to re-derive from;
  §1d), but stop letting the caller assign the bucket and budget class
  independently: pass the derived class through `admit_memory_evidence()`
  and route by its outcome. `_withheld_lesson_with_trust_class()` (lines
  168-178) keeps its existing reason→class mapping and its
  `stale_trust_metadata` flag, and feeds the same gate — a withheld item can
  be further demoted, never promoted to `LOAD`. If open question 4h is
  answered "yes", the same call site gains the real per-item status check;
  the gate's signature does not change either way.
- `_select_skills()` (`runtime/context_builder.py:216-272`) — the
  `trust_class` it already computes at line 252 becomes the input to
  `admit_memory_evidence()`, and the hardcoded `"budget_class":
  "SHOULD_LOAD"` at line 269 becomes the gate's output. The existing
  `except TrustClassError: continue` becomes an explicit `DENY` with a
  counted reason rather than a silent skip.
- `build_context_plan()` (`runtime/context_builder.py:393-403`) — the
  `memory_trust_classification_present` coverage boolean stays, and gains
  companion fields recording that the gate ran and what it decided
  (admitted / withheld / denied counts, plus reasons). Coverage remains
  reporting; the gate itself lives at the two producers.

### 2d. Fail-closed posture

Consistent with `CanonicalRunGuard`'s `BINDING_REQUIRED` and
`DestructiveExternalActionGuard`'s deny-on-missing-key pattern: absent,
malformed, or unmappable trust metadata **never yields `LOAD`**. It yields
`WITHHOLD` or `DENY` per §2e. Fail-closed here means "this optional memory
item does not enter the load set", **not** "the plan fails" — as #148
already established for this seam. `authority`, `required`, `boundaries`,
`dependencies`, and `unresolved` are canonical task context, entirely
outside this gate; a poisoned or malformed lesson store must never suppress
them.

### 2e. `WITHHOLD` vs `DENY` for the unknown case: decided by what the bucket carries

`WITHHOLD` is only safe when the withheld representation is a *reference*
rather than a copy of the content. That is answerable from code today, and
the answer differs by producer:

- **Lessons: reference only.** `project_applicable_lessons()` appends
  `{"lesson_id": ..., "reason": ...}` and nothing else
  (`runtime/operational_learning.py:410`). The lesson `claim` text appears
  only on *projected* items (lines 413-422), never on withheld ones. So a
  withheld lesson carries no attack surface, and the unknown/malformed case
  on this path should be `WITHHOLD` — which also keeps this note aligned
  with #148's stated fail-closed rule ("mark item withheld, or omit it if no
  safe withheld bucket exists") rather than departing from it.
- **Skills: carries content.** `_select_skills()` emits `name` and
  `description` text inline (`context_builder.py:258-259`). A withheld Skill
  entry in that shape *is* instruction-bearing text in the plan. So on the
  skills path the unknown/malformed case should be `DENY`, unless the
  implementation strips the entry to `skill_id` + `catalog_key` + reason —
  in which case `WITHHOLD` becomes safe there too, which is the preferable
  outcome (auditable, and consistent across producers).

This supersedes an earlier draft of this note that applied a blanket `DENY`
to the unknown case on the stated premise that withheld buckets carry text.
For lessons that premise is false, and the rule is corrected accordingly.

## 3. Non-goals for the implementation follow-up

Per roadmap §7 and #148's own bounds:

- **No policy engine, DSL, or configurable threshold.** The admission table
  in §2a is a fixed dict literal. No per-project config, no operator-tunable
  severity, no rule expressions.
- **No second authority database.** `SkillTrustState`,
  `SkillLifecycleState`, and `operational_learning.py`'s status strings
  remain the systems of record. The gate reads their existing values through
  the existing read-only mappings in `runtime/trust.py`. No new store, no
  migration, no persisted trust records, no lineage/provenance graph.
- **No knowledge graph, no semantic classification, no inference.** Trust
  class comes only from the existing subsystem status mappings. No LLM
  judgment, no regex sniffing of lesson text, no content analysis — the same
  reasoning the SEC3 note gives for rejecting inferred classification.
- **No daemon, no background scanning, no always-on process.**
- **No new `HookEvent`, `HookEnforcement`, `HookOutcome`, or guard class,
  and no routing of Context Builder through `HarnessService`.** The seam is
  a direct function call (§1b); do not add Hook plumbing to host this.
- **No Skill body loading.** `load_skill()` / `load_catalog_skill()` stay
  uncalled from Context Builder. `APPROVED_SKILL` → `LOAD` here means "the
  descriptor metadata may be in the default load set", nothing more.
- **No promotion of guidance to authority.** `REVIEWED_GUIDANCE` items keep
  the `GUIDANCE_ONLY` label and are still never merged into instructions or
  boundaries.
- **No changes to `runtime/trust.py`'s enum or mappings**, no new enum
  members, no re-mapping of existing subsystem statuses.
- **Do not flip 6.22 to `DONE`.** This gate covers the Context Builder seam
  only. Action/tool-call-level enforcement remains outstanding, and the
  checklist row's "Still missing" clause must be narrowed, not deleted.

## 4. Open behavior questions the implementation must answer, not guess

- **4a. Whether to strip Skill entries so the unknown case can be uniformly
  `WITHHOLD`.** §2e settles the *principle* (the outcome follows from
  whether the withheld form carries content) and settles the lessons path
  (`WITHHOLD`, matching #148). What remains open is the skills path: strip a
  withheld Skill entry to `skill_id` + `catalog_key` + reason and use
  `WITHHOLD` uniformly, or leave the entry shape alone and use `DENY` there.
  The implementation must pick one and test it explicitly; what it must
  never do is let missing or malformed trust metadata mean "trusted".
- **4b. Audit trail for `DENY`.** Dropping an item entirely makes the plan
  quieter but loses the trail; #148's table says "omitted or withheld with
  reason". §2a picks drop-with-counted-reason under `coverage`. The
  implementation must confirm a count is sufficient audit, or add a separate
  `denied_memory` list carrying identifiers **without** the untrusted text.
- **4c. What happens to the existing Skill-selection tests and the S6 exit
  gate.** Demoting `OBSERVATION` Skills from `SHOULD_LOAD` to `ON_DEMAND`
  changes assertions in `tests/test_context_builder.py`. The implementation
  must confirm this does not regress the S6 exit gate ("unrelated Skills
  demonstrably stay out of context") — it should strengthen it — and must
  not weaken the gate to keep old assertions green.
- **4d. RESOLVED — do not re-open.** "Do withheld guidance items carry
  lesson text?" No: `runtime/operational_learning.py:410` emits
  `{"lesson_id", "reason"}` only. Recorded here rather than deleted because
  an earlier draft of this note assumed the opposite and drew the wrong
  default from it; §2e carries the corrected rule.
- **4e. Where the gate's decisions get recorded as evidence.** Under
  `coverage` only (as §2c proposes), or also into the Run Record / plan
  evidence stream, consistent with how `HookOutcome.evidence_refs` is used
  elsewhere. Do not invent a new evidence stream.
- **4f. Module placement.** Keeping `admit_memory_evidence()` private to
  `runtime/context_builder.py` is the smallest change; putting it in a small
  `runtime/trust_gate.py` (or next to the enum in `runtime/trust.py`) makes
  it independently unit-testable and reusable by the eventual action-level
  gate. The implementation should pick one and justify it against rule 8
  (smallest change) versus the known second consumer.
- **4g. Whether the admission table belongs beside the enum.** If it lands
  in `runtime/trust.py`, that module's docstring — which currently states it
  is "NOT wired into any decision-gating code path" — becomes false and must
  be corrected in the same change.
- **4h. Should `project_applicable_lessons()` carry per-item `status` onto
  projected items, so the guidance path can gate on a re-derived class?**
  Today it does not (§1d), which is why the guidance path gets no behavior
  change from this design. Adding it would make §1d's residual
  projection-bug threat detectable and would let `_lesson_guidance()` check
  rather than assert. It is also an upstream shape change to a stable
  projection contract with its own tests, i.e. real scope. The
  implementation must decide it deliberately — either do it as a named,
  separately-reviewed step, or record that the guidance path stays
  structural-only for now. It must **not** be smuggled in as an incidental
  edit, and this note does not assume it.

## 5. Roadmap impact

This does not complete 6.22. It converts the Context Builder seam from
annotation to enforcement: after the follow-up, a real allow/withhold/deny
decision is made from `MemoryTrustClass` — concretely on the skills path,
where `OBSERVATION` stops being default-loadable, and structurally on the
guidance path, where bucket and budget class stop being computed in parallel
with the class (§2b). The checklist's "no gate consults `MemoryTrustClass`"
gap closes for that seam. The row stays
`IN PROGRESS` because the checklist's other two outstanding clauses remain
true — no *action/tool-call* gate consults the class, and
`SkillTrustState`/`SkillLifecycleState`/`operational_learning.py` remain
separate, unmigrated systems of record. Those are later, separately bounded
tasks.
