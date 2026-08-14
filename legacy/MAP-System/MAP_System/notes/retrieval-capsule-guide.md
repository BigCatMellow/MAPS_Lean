# Retrieval Capsule Guide

## Retrieval capsule

- Purpose: Defines the small, retrieval-oriented metadata block used near the top of important durable Markdown so an index can identify the document without loading or rewriting its full prose.
- Proves: The required fields, controlled evidence types, validation rules, authoring boundaries, and evaluation discipline for retrieval capsules.
- Applies to: Selected governing, procedural, decision, test, research, current-state, release, and measured-outcome documents whose meaning is otherwise difficult to infer from title and headings.
- Does not provide: Canonical authority, task ownership, approval, release status, permission to keyword-stuff documents, or permission to add capsules across the repository without measured need.
- Evidence type: procedure
- Status: current

## Purpose

A retrieval capsule is a 60–120-word human-readable description placed near
the top of selected durable Markdown. It helps a lexical or hybrid index answer
four questions cheaply:

1. What is this document for?
2. What can it actually prove?
3. Where does it apply?
4. What must not be inferred from it?

The capsule is descriptive metadata. It never overrides the document body,
SQLite task state, decisions, review records, release gates, or operator
authority.

## Required shape

Use this exact heading and field order:

```md
## Retrieval capsule

- Purpose: <plain-English purpose>
- Proves: <specific facts or behavior this document can support>
- Applies to: <project, subsystem, lifecycle, or time boundary>
- Does not provide: <explicit non-goals and authority boundary>
- Evidence type: <controlled value>
- Status: <controlled value>
```

Required evidence types are:

- `governing_rule`
- `procedure`
- `decision`
- `implementation`
- `test_evidence`
- `measured_outcome`
- `research`
- `current_state`
- `release_record`
- `task_scope`

Required status values are `current`, `historical`, `draft`, and `superseded`.

## Authoring rules

- Keep the six field values together between 60 and 120 words.
- State concrete nouns, mechanisms, and boundaries in ordinary language.
- Use vocabulary a person asking about the capability would naturally use,
  but do not add a keyword or synonym list.
- Describe only facts supported by the document body.
- Name the proof role precisely. A test is not an implementation; a task
  record is not measured outcome evidence; a current file is not automatically
  evidence of its historical state.
- Make `Does not provide` meaningful. It should prevent a plausible bad
  inference, especially around authority, scope, temporal attribution, or
  negative capability claims.
- Add capsules only where measured retrieval value justifies their maintenance
  cost. Documents without a capsule remain valid and use normal index fallback.
- When the body changes materially, update or remove its capsule in the same
  task. A stale capsule is worse than no capsule.

## Placement

Place the capsule after the title and any machine-owned preamble that must stay
first, but before the main body. Existing metadata bullets may remain before or
after the capsule when another validator requires their location. The capsule
must begin within the first 40 lines so validators and bounded readers can find
it without scanning the full file.

## Validation and use

`MAP_System/scripts/task_memory_capsule_pilot.py` parses and validates the
format. Missing capsules are valid fallbacks. Present capsules fail validation
when fields are missing, duplicated, unknown, empty, out of order, too long,
too short, or use uncontrolled evidence/status values.

An index should store capsule fields separately from document bodies. Purpose,
proof, and applicability are positive retrieval signals. `Does not provide` is
a boundary signal and must not be treated as evidence that the excluded
capability exists. Evidence type and status are soft ranking signals, never
authority or a substitute for opening the selected source.

## Evaluation rule

Capsules may be tuned on labeled development data, but the parser, scoring,
field vocabulary, and candidate files must then be frozen before a fresh
holdout. A useful result improves exact or acceptable-source visibility without
increasing task context materially, hiding unresolved paths, or creating false
historical attribution.
