# Memory trust enforcement gate design (roadmap 6.22)

Date: 2026-08-25
Owner: `/root`
Status: design complete; no runtime code changed

Scope: this note designs the *gate* that consumes the `MemoryTrustClass`
vocabulary (PR #127) and the Context Builder annotations (PR #149) on the
enforcement seam already selected by PR #148. It does not re-open the seam
choice, does not define new vocabulary, and changes no runtime behavior.

## 1. Finding (verified against `origin/main@8923adb`)

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

- `_lesson_guidance()` stamps `REVIEWED_GUIDANCE` on **every** item in
  `projection["projected"]`, unconditionally — the item's own `status` field
  is never consulted at stamp time. If a `RETIRED`, `SUPERSEDED`, or
  `CANDIDATE` lesson ever reaches the projected bucket (a projection bug, a
  hand-edited or poisoned lesson store, a future change to
  `project_applicable_lessons()`), Context Builder will label it
  `REVIEWED_GUIDANCE` and emit it as `SHOULD_LOAD` default-load guidance. The
  trust class would actively *launder* the poisoned item.
- `_select_skills()` emits every matched Skill with
  `"budget_class": "SHOULD_LOAD"` while stamping it `OBSERVATION` — a class
  the #148 class/action table says "must not influence ... loaded
  instructions". Nothing enforces that; the SHOULD_LOAD tag is assigned
  before and independently of the class.

This is also a duplicate-truth violation (global rule 12): two mutable
derivations of the same fact, with nothing making the second answerable to
the first.

## 2. Proposed gate: `admit_memory_evidence()` — one pure admission decision

Add one module-private choke point in `runtime/context_builder.py` (or a
small `runtime/trust_gate.py` if the implementation prefers to keep it
testable in isolation — see open question 5f) through which **every**
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
| `ACTIVE_INSTRUCTION` | `LOAD` |
| `APPROVED_SKILL` | `LOAD` |
| `REVIEWED_GUIDANCE` | `LOAD` |
| `CANDIDATE_LESSON` | `WITHHOLD` |
| `CLAIM` | `WITHHOLD` |
| `OBSERVATION` | `WITHHOLD` |
| `SUPERSEDED` | `WITHHOLD` |
| `RETIRED` | `WITHHOLD` |
| `UNTRUSTED_INPUT` | `DENY` |
| `QUARANTINED` | `DENY` |
| *missing / unparseable / mapping error* | `DENY` |

`stale=True` (today's `stale_trust_metadata`, set for `EXPIRED` /
`REVIEW_DUE`) demotes `LOAD` to `WITHHOLD`; it never promotes.

The threshold is a single ordering over the enum — the four classes at or
above `REVIEWED_GUIDANCE` load, the two explicitly-adverse classes are
denied, everything else is withheld. That is the whole rule. No
configuration surface, no per-project override, no severity matrix.

### 2b. What "a real decision" looks like concretely

Three behaviors change, all observable in the emitted plan and all
mechanically testable:

1. **Class-vs-status disagreement is caught, not laundered.** The gate
   re-derives the class from the item's *own* status/reason field via the
   existing `operational_learning_trust_class()` mapping rather than
   accepting the unconditional `"ACTIVE"` stamp at line 155. A projected
   lesson whose own status says `RETIRED` maps to `RETIRED` → `WITHHOLD`,
   so it leaves `guidance` and lands in `withheld_guidance` instead of
   being emitted as loadable `REVIEWED_GUIDANCE`. Today the same input is
   emitted as loadable guidance. That is the allow/deny difference.
2. **`OBSERVATION` Skills stop being SHOULD_LOAD.** Every matched Skill
   today carries `trust_class: OBSERVATION` *and* `budget_class:
   SHOULD_LOAD`. Under the gate, `OBSERVATION` → `WITHHOLD`, so matched but
   unassessed Skills appear as `ON_DEMAND` metadata with a withheld reason
   and are no longer part of the default load set. This is a real,
   currently-visible behavior change (existing Skill-selection tests will
   need updating — see open question 5c), and it is exactly the invariant
   the #148 table asserts and nothing enforces.
3. **A quarantined or untrusted item cannot appear at all.** `QUARANTINED` /
   `UNTRUSTED_INPUT` are dropped rather than withheld, because "named in
   the plan with its text attached" is itself the poisoning surface for
   those two classes. The count surfaces under `coverage` so the drop is
   auditable rather than silent.

The gate's outcome is the *only* thing that assigns membership in
`guidance` / `withheld_guidance` / `skills` and the `SHOULD_LOAD` vs
`ON_DEMAND` budget class for memory-like items. Routing derives from the
class; the class no longer merely narrates a routing decision made
elsewhere.

### 2c. Where exactly it plugs in

Three call sites, all inside the seam #148 selected:

- `_lesson_guidance()` (`runtime/context_builder.py:125-165`) — replace the
  unconditional `trust_class=operational_learning_trust_class("ACTIVE")`
  stamp on `projection["projected"]` with: derive the class from the item's
  own status, call `admit_memory_evidence()`, and route by its outcome.
  `_withheld_lesson_with_trust_class()` (lines 168-178) keeps its existing
  reason→class mapping and feeds the same gate (a withheld item can be
  further demoted to `DENY`, never promoted to `LOAD`).
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
malformed, or unmappable trust metadata is `DENY`, never `LOAD`. But — as
#148 already established for this seam — fail-closed means "this optional
memory item does not enter the load set", **not** "the plan fails".
`authority`, `required`, `boundaries`, `dependencies`, and `unresolved` are
canonical task context and are entirely outside this gate; a poisoned or
malformed lesson store must never suppress them.

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

- **4a. Default when no trust class can be determined at all.** §2a proposes
  `DENY` (fail closed), consistent with `CanonicalRunGuard`'s
  `BINDING_REQUIRED` and `DestructiveExternalActionGuard`'s deny-on-missing.
  But #148's fail-closed rules say "mark item withheld, or omit it if no
  safe withheld bucket exists" — i.e. `WITHHOLD`, one step weaker. The
  implementation must pick one, state why, and test it explicitly rather
  than let a missing key silently mean "trusted". The tie-break question is
  whether a withheld-but-named unknown item is itself a poisoning surface;
  if the withheld bucket carries the lesson *text*, it is, and `DENY` wins.
- **4b. `DENY` vs `WITHHOLD` for `UNTRUSTED_INPUT` / `QUARANTINED`.**
  Dropping an item entirely makes the plan quieter but loses the audit
  trail; #148's table says "omitted or withheld with reason". §2a picks
  drop-with-counted-reason. The implementation must confirm the count under
  `coverage` is sufficient audit, or switch to a separate `denied_memory`
  list that carries identifiers **without** carrying the untrusted text.
- **4c. What happens to the existing Skill-selection tests and the S6 exit
  gate.** Demoting `OBSERVATION` Skills from `SHOULD_LOAD` to `ON_DEMAND`
  changes assertions in `tests/test_context_builder.py`. The implementation
  must confirm this does not regress the S6 exit gate ("unrelated Skills
  demonstrably stay out of context") — it should strengthen it — and must
  not weaken the gate to keep old assertions green.
- **4d. Whether `withheld_guidance` items carry lesson text today.** The
  `WITHHOLD` outcome is only safe if the withheld bucket is a *reference*,
  not a full copy of the content. The implementation must read what
  `project_applicable_lessons()`'s withheld items actually contain and, if
  they carry text, decide whether `WITHHOLD` must strip it for the lower
  classes.
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

## 5. Roadmap impact

This does not complete 6.22. It converts the Context Builder seam from
annotation to enforcement: after the follow-up, a real allow/withhold/deny
decision is made from `MemoryTrustClass`, and the checklist's "no gate
consults `MemoryTrustClass`" gap closes for that seam. The row stays
`IN PROGRESS` because the checklist's other two outstanding clauses remain
true — no *action/tool-call* gate consults the class, and
`SkillTrustState`/`SkillLifecycleState`/`operational_learning.py` remain
separate, unmigrated systems of record. Those are later, separately bounded
tasks.
