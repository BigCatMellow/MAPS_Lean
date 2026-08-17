# Outcome-derived lesson candidates

Date: 2026-08-15/16  
Owner: `agent/outcome-lesson-candidate-wave3`  
Status: implementation evidence, pending review

## Purpose

This tranche closes one safe gap in the operational-learning chain:

```text
canonical post-completion outcome
        ↓
non-authoritative lesson candidate
        ↓
external promotion decision
        ↓
#43 guidance-only projection
```

It deliberately stops at `CANDIDATE`.

## Why not generate the lesson from outcome notes?

`task_outcomes.source` and `task_outcomes.notes` are evidence/diagnostic text. They can contain incomplete analysis, arbitrary prose, or even text that looks like instructions.

Converting that prose directly into durable guidance would create a prompt/memory authority path.

The builder therefore accepts the lesson `claim` and `applicability` only as explicit caller inputs. It uses the outcome solely to establish source provenance.

The tests include hostile-looking outcome notes and prove they never appear in the lesson record.

## Canonical checks

For outcome `O`, the builder requires:

1. `get_outcome(O)` returns a canonical outcome;
2. the owning task exists and is `DONE`;
3. the outcome carries a valid task-revision SHA-256;
4. if `run_id` is present, that run exists and belongs to the same task;
5. no later canonical outcome explicitly supersedes `O`.

If any check fails, candidate creation fails closed.

## Exact source refs

A run-bound candidate receives refs conceptually like:

```text
outcome:17
run:RUN-...
task-revision-sha256:<hash>
task:TASK-...
```

These refs identify source evidence. They do not copy outcome status, notes, failure class, or metrics into the lesson claim.

## Superseded outcomes

Outcome observations are append-only and may explicitly supersede an earlier observation.

Learning from a known-superseded observation would be a stale-evidence failure. The builder checks the task's canonical outcome history and rejects an outcome if a later row names it in `supersedes_outcome_id`.

This does not choose the "best" outcome semantically. It only prevents using evidence the canonical source already marks obsolete.

## Candidate identity

Candidate ID is deterministic over semantic lesson content:

- normalized explicit claim;
- normalized explicit applicability;
- exact source refs;
- `source_kind=TASK_OUTCOME`.

It intentionally excludes `created_at` and `created_by` from the semantic ID.

Thus two agents/times proposing the same lesson from the same evidence/scope converge on the same candidate identity while retaining their own provenance metadata in the record.

Material changes to claim, applicability, or source evidence create a different candidate ID.

## Reuse of #43 validation

The builder does not create a second lesson schema. It constructs a provisional `CANDIDATE`, runs it through `validate_lesson_record()`, computes the semantic ID from normalized values, then validates the final record again.

That means #43 continues to own:

- sensitive-text rejection;
- applicability normalization/safety;
- source-ref normalization;
- timestamp validation;
- `CANDIDATE` promotion-smuggling prohibition.

## Authority boundary

Returned records always have:

```text
status = CANDIDATE
promotion = null
retirement = null
superseded_by = null
```

There is no:

- lesson store;
- `promote()` function;
- automatic applicability inference;
- startup injection;
- Context Builder injection;
- policy/task authority;
- automatic self-modification.

The integration test passes the candidate into #43's projection and proves it is withheld as:

```text
CANDIDATE_NOT_PROMOTED
```

## What remains unresolved

The repository still intentionally has no rule here for:

- who may promote a lesson;
- what review/operator evidence is required for promotion;
- where canonical promoted lessons would be stored;
- conflict resolution against authoritative instructions.

Those are authority decisions, not gaps this builder should guess across.

## Tests

Focused tests cover:

- exact source refs;
- no promotion fields;
- hostile outcome prose ignored;
- deterministic semantic ID across creator/time changes;
- claim/scope/source changes alter ID;
- missing outcome/task/run;
- non-DONE task;
- run/task mismatch;
- invalid task revision;
- superseded outcome rejection;
- sensitive claim and invalid applicability rejection through #43;
- #43 projection withholding the result as an unpromoted candidate.

## Continuation

After review/integration, the next operational-learning step should remain an explicit authority decision rather than another implementation guess:

```text
candidate
→ reviewed promotion-decision contract
→ optional canonical storage
→ #43 ACTIVE projection
```

Until that decision exists, candidate generation may advance evidence organization without activating guidance.
