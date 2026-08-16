# Operational learning — guidance-only projection

Status: `IMPLEMENTED ON ISOLATED DRAFT BRANCH — NOT POLICY OR STARTUP AUTHORITY`

Branch: `agent/operational-learning-projection-wave3`

Base: merged `main@1652d515a5b991b1ed07c7f2e624fea95927ddfb`.

## Purpose

Preserve the useful part of the recovered operational-learning lifecycle without creating an unlimited memory system or a second policy plane.

The bounded problem is:

> If a reviewed/promoted lesson already exists, can MAPS decide whether it is currently applicable and safe to surface as guidance while preserving expiry, supersession, provenance, and uncertainty?

This tranche deliberately does **not** answer:

> Who may promote a lesson, where is the canonical lesson registry, or how should startup/context automatically inject it?

Those are later authority/integration decisions.

## Existing merged boundary

`runtime/state/outcomes.py` already provides append-only post-completion outcome observations with source/actor/run/task-revision evidence. Outcomes explicitly do not rewrite task lifecycle, ownership, policy, or review authority.

Operational learning preserves the same separation:

```text
observation / outcome
        ↓
lesson record
        ↓
external promotion decision, if any
        ↓
selective guidance projection
```

Never:

```text
observation
→ automatic instruction/policy change
```

## Lesson record

Version 1 supports:

```text
lesson_version
lesson_id
status: CANDIDATE | ACTIVE | RETIRED
claim
source_kind
source_refs[]
applicability
created_by
created_at
promotion?
superseded_by?
retirement?
```

Source kinds are descriptive provenance only:

```text
TASK_OUTCOME
INCIDENT
OPERATOR_OBSERVATION
NON_TASK_OBSERVATION
RESEARCH
```

A source class does not grant authority.

## Lifecycle rule

### CANDIDATE

- carries evidence/provenance;
- carries no promotion contract;
- never projects as active guidance.

### ACTIVE

Requires an externally supplied promotion contract:

```text
decision_ref
promoted_by
starts_at
review_at
expires_at?
```

There is intentionally no `promote()` function in this tranche.

The projector treats ACTIVE as a supplied fact that must already contain promotion evidence. It does not decide that promotion was authorized.

### RETIRED

Requires:

```text
decision_ref
retired_by
retired_at
```

A never-promoted candidate may also be retired, so RETIRED does not necessarily require an earlier promotion contract.

## Applicability

Applicability is explicit and deterministic:

```text
global
project_ids[]
task_types[]
risk_levels[]
path_prefixes[]
```

Rules:

- `global=true` cannot be combined with scoped matchers;
- `global=false` requires at least one explicit matcher;
- populated dimensions are ANDed;
- values within a dimension are alternatives;
- path prefixes are repository-relative POSIX paths;
- no semantic inference or free-text similarity matching occurs.

Example:

```text
project_id = PROJECT-A
AND risk = HIGH
AND path under runtime/state
```

only projects when every populated requirement is provably satisfied.

If required context is absent, projection returns `APPLICABILITY_UNKNOWN` and withholds the lesson rather than assuming broad applicability.

## Time and lifecycle withholding

An ACTIVE lesson is withheld when:

```text
NOT_STARTED
EXPIRED
REVIEW_DUE
SUPERSEDED
NOT_APPLICABLE
APPLICABILITY_UNKNOWN
```

Candidates and retired records are withheld as:

```text
CANDIDATE_NOT_PROMOTED
RETIRED
```

Review-due guidance is deliberately withheld. This avoids temporary guidance silently becoming permanent simply because nobody revisited it.

## Projection output

Only eligible ACTIVE lessons appear in `projected`.

Each projected item carries:

```text
lesson_id
claim
source_kind
source_refs
promotion_decision_ref
authority: GUIDANCE_ONLY
```

The overall projection explicitly states:

```text
can_grant_task_authority: false
can_grant_policy_authority: false
can_promote_candidates: false
```

This is a read model, not a control plane.

## Non-task observations

Recovered legacy evidence suggested useful observations may occur during explicitly non-task/operator-directed activity.

This tranche permits `NON_TASK_OBSERVATION` as provenance, but preserves the boundary:

```text
non-task observation
→ candidate evidence only
→ normal external promotion decision required
→ only then may ACTIVE guidance project
```

The observation itself does not import the originating activity into task governance and does not grant authority.

## Security/privacy

Lesson claims, source refs, decision refs, and actor identifiers are checked through the existing observability redaction boundary before projection.

The mechanism does not require:

- raw prompts;
- private chain-of-thought;
- provider transcripts;
- raw outcome notes;
- credentials.

## Tests

Focused tests cover:

- candidates never projecting;
- ACTIVE records requiring external promotion evidence;
- candidate promotion-smuggling rejection;
- project/path matching and mismatch;
- missing context preserving applicability UNKNOWN;
- explicit global matching;
- future start withholding;
- review-due withholding;
- expiry withholding;
- supersession withholding;
- retirement withholding;
- non-task observation projection only after external promotion;
- retired never-promoted candidate support;
- unsafe relative path rejection;
- duplicate lesson-ID rejection;
- deterministic ordering;
- promotion start cannot predate candidate creation.

## What remains deliberately unresolved

### Canonical storage

No lesson database/table/file registry is introduced here. Adding one would require an explicit decision about authority, mutation, append-only history, concurrency, and correction paths.

### Promotion/retirement mutation

No automatic or agent-owned promotion path exists. A later tranche should bind promotion/retirement to accepted review/operator decision mechanisms rather than inventing authority here.

### Production projection

This tranche does not automatically feed guidance into startup, Context Builder, routing, Skills, or policy. That integration should happen only after record authority/storage and conflict semantics are accepted.

### Conflicts

Operational guidance can never override current task/policy/operator authority. A later integration must fail safe when guidance conflicts with authoritative instructions rather than selecting a winner implicitly.

## Recommended next integration order

```text
this projection contract
→ independent review
→ define canonical lesson provenance/storage + mutation authority
→ bind promotion/retirement to accepted decision/review evidence
→ add applicability projection to Context Builder as guidance-only
→ evaluate usefulness/noise/expiry behavior
```

Do not skip directly from an observed failure to active startup instructions.
