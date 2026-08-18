# Task: Document the MAPS information classes (S1)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: `agent/information-classification-doc-wave9`
- Risk: `LOW`
- Goal: give the 7 MAPS information classes (authority/invariant, task
  context, fact/knowledge, Skill/procedure, flow, tool/capability,
  example/demonstration) a durable, applied home outside roadmap prose,
  closing the gap `work/roadmaps/CAPABILITY_CHECKLIST.md` flagged for
  `agent-harness-capabilities/02-procedural-knowledge-and-skills.md` phase
  **S1**: the classes were defined only in that roadmap file's section 2, not
  in any active, non-roadmap doc that current guidance can point to.

## Inputs and source of truth

- `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md`
  lines 43-100 ("2. Information classes", unmodified) -- the exact
  definitions/examples carried over verbatim into the new doc; this task does
  not invent new classes, rename them, or reinterpret them.
- `runtime/context_builder.py::build_context_plan` (unmodified) -- read to
  confirm its existing `authority`/`required`/`guidance` return fields are a
  real, already-built instance of the authority/task-context/fact-knowledge
  split, not something this task needs to build.
- `runtime/skills/format.py`, `runtime/skills/catalog.py` (unmodified) --
  read to confirm Skills are already treated as loaded procedure with
  provenance/trust metadata, distinct from authority, before describing that
  in the new doc.
- `playbook/INFORMATION_LIFECYCLE.md` (unmodified) -- a different axis
  (temporal state: active/retired/archived); the new doc explicitly
  distinguishes itself from this one rather than merging into it.
- `playbook/INDEX.md`, `runtime/README.md` -- existing structure/conventions
  the new doc and its index row/pointer follow.

## Change boundary

MAY CHANGE / ADD:
- `playbook/INFORMATION_CLASSES.md` (new doc)
- `playbook/INDEX.md` (additive: one new table row)
- `runtime/README.md` (additive: one line appended to the existing
  `context_builder.py` bullet)
- `work/roadmaps/CAPABILITY_CHECKLIST.md` (S1 row status update, same PR per
  that file's own "How to keep this current" convention)
- this task doc

MUST NOT CHANGE:
- `runtime/context_builder.py`, `runtime/skills/*`, or any other code/test
  file -- S1 is naming/documenting an existing distinction the runtime
  already makes, not building new mechanism.
- `playbook/INFORMATION_LIFECYCLE.md` -- referenced, not merged into or
  restructured.
- `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md`
  -- source of truth for the 7 classes, read-only for this task.

## Required semantics

1. All 7 classes are named and defined exactly as the roadmap source states
   them (authority/invariant, task context, fact/knowledge, Skill/procedure,
   flow, tool/capability, example/demonstration), each with the roadmap's own
   example reused rather than a new invented example.
2. The new doc explicitly distinguishes itself from
   `playbook/INFORMATION_LIFECYCLE.md`'s temporal-state axis, so the two are
   never conflated by a future reader.
3. The "how these interact" section is grounded in what
   `runtime/context_builder.py` and `runtime/skills/` already do today (e.g.
   Context Builder's `authority`/`required`/`guidance` fields, Skills as
   loaded procedure distinct from authority) -- no new mechanism is described
   as if it already exists.
4. `runtime/README.md`'s pointer stays to one added line on the existing
   `context_builder.py` bullet; the bullet is not otherwise restructured.

## Acceptance criteria

- [x] `playbook/INFORMATION_CLASSES.md` defines all 7 classes with the
      roadmap's own examples and an interaction section grounded in existing
      `runtime/context_builder.py`/`runtime/skills/` behavior.
- [x] `playbook/INDEX.md` has a new row pointing to the doc, distinguishing
      it from `INFORMATION_LIFECYCLE.md`.
- [x] `runtime/README.md`'s `context_builder.py` bullet has exactly one new
      line referencing the doc.
- [x] `work/roadmaps/CAPABILITY_CHECKLIST.md`'s S1 row reflects the new doc.
- [x] No runtime/test files changed.

## Verification

```text
git diff --stat origin/main
```

(Confirms the diff touches only `playbook/`, `runtime/README.md`, and
`work/` docs -- no `.py` files. Full test suite not required for a docs-only
change per this repo's convention -- CI's own `test` job covers it.)

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## Stop / escalate

Stop rather than guess if:
- documenting the interaction section would require describing Skill
  loading, routing, or Context Builder behavior that does not actually exist
  yet in `runtime/` -- S1 documents what is real today, not the S6/S7
  roadmap's future state.
- a reviewer finds the roadmap's own section 2 wording ambiguous enough that
  faithfully carrying it over produces a materially different definition
  than intended -- resolve against the roadmap text, not by inventing a
  reinterpretation.
