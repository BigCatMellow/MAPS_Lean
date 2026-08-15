# Roadmap 05 — Learning & Evaluation

Status: `PLANNING ONLY — NOT ACTIVE AUTHORITY`

Purpose: give MAPS a disciplined evidence loop for learning from real runs, evaluating Skills/interfaces/environments/harness changes, preserving failures as regression cases, and proposing improvements without self-authorizing them.

Source research themes:

- SWE-agent trajectories and reproducible experiment records
- three-layer evaluation discipline recovered from legacy MAPS
- append-only real-world outcomes
- frozen incident regression cases
- ACI/Skill/environment experiments
- operational-learning promotion lifecycle
- controlled harness refinement
- time-travel/fork debugging concepts from durable workflow systems

---

# 1. Why this roadmap exists

A system can pass its internal process and still fail in the real world.

Examples:

- tests passed but user later reports regression;
- Skill makes agents faster but increases escaped defects;
- new routing policy reduces cost but increases operator intervention;
- environment snapshot improves setup speed but creates stale dependency failures;
- hook catches syntax errors but causes excessive false blocking;
- semantic context retrieval improves recall on matched wording but fails hard negatives.

MAPS needs a way to answer:

> Did this mechanism actually improve outcomes, and can we prove it on stable evidence before promoting it?

The target is **measured, reviewable improvement**, not autonomous prompt tweaking.

---

# 2. Non-negotiable learning rules

## 2.1 Outcome is separate from completion

`DONE` means the required MAPS implementation/review process completed.

Outcome observations answer what happened later in the real world.

Neither rewrites the other.

## 2.2 Historical evidence is append-only

Do not edit old failures into successes.

Corrections/supersession append new observations and preserve lineage.

## 2.3 Evaluation sets are frozen before comparison

Do not modify the test set while examining a candidate because it makes the candidate look better.

## 2.4 Candidate changes are proposal-only

MAPS may recommend:

- routing changes;
- instruction changes;
- Skill revisions;
- hook thresholds;
- environment defaults;
- helper policy;
- recovery parameters.

It may not promote them without the normal review/decision path.

## 2.5 Optimize outcomes, not activity

Never treat these as success metrics by themselves:

- more agents;
- more messages;
- more tool calls;
- more Skills;
- longer traces;
- more automation.

---

# 3. Target evidence architecture

```text
TASK / RUN
   │
   ├── canonical task revision
   ├── run manifest
   ├── environment fingerprint
   ├── Skill/capability versions
   ├── Harness config ID
   ├── operation/session trajectory
   ├── submission/review
   └── outcome observations
           │
           ▼
      Portable Run Record
           │
           ├────► Incident classification
           │             │
           │             ▼
           │      Frozen regression case
           │
           └────► Aggregate metrics
                         │
                         ▼
                Candidate improvement
                         │
                  frozen evaluation
                         │
                current vs candidate
                         │
                         ▼
                  review / approval
```

---

# 4. Portable Run Record

## 4.1 Purpose

Create a reproducible, sanitized export/projection of a run sufficient for diagnosis/evaluation.

It is derived from canonical and supporting evidence; it is not a new task authority database.

## 4.2 Candidate contents

```text
record_version
record_id

task:
  task_id
  project_id
  stable task revision
  task type/risk

run:
  run_id
  worker_id
  provider/adapter identity
  session IDs
  parent/child/helper lineage
  base revision

context:
  context refs/hashes
  selected Skills + hashes
  authority/instruction refs

environment:
  EnvironmentSpec hash
  fingerprint summary

harness:
  Harness config/version ID
  hook set/version IDs
  routing/config identifiers

trajectory:
  operation IDs
  action/result codes
  timings
  mutation markers
  evidence refs

completion:
  submission metadata
  review metadata
  artifact/revision refs

outcomes:
  append-only outcome observations

metrics:
  runtime
  model/provider usage if available
  cost if available
  retries
  operator interventions
  rework
```

Sensitive raw prompts, file contents, credentials, and private user data are omitted/redacted by default.

---

# 5. Trajectory semantics

A trajectory is more than logs.

It should reconstruct:

```text
what state the system believed
what operation was requested
what the harness/tool returned
what mutated
what validation followed
what the agent did next
what review/outcome occurred
```

Each step should preserve stable IDs and result codes.

Avoid requiring replay of hidden model reasoning. We need observable actions/evidence, not private chain-of-thought.

---

# 6. Incident taxonomy

Start with the recovered MAPS taxonomy and extend only when real cases demand it.

Initial categories:

```text
TOOL_FAILURE
CONTEXT_OMISSION
CONTEXT_POISONING
RUNAWAY_LOOP
ROUTING_ERROR
SKILL_ROUTING_ERROR
SKILL_PROCEDURE_ERROR
HELPER_FAILURE
HELPER_NO_PROGRESS
RECOVERY_FAILURE
DUPLICATE_EXECUTION
ENVIRONMENT_DRIFT
REVIEW_MISS
STALE_REVIEW_EVIDENCE
VALIDATOR_FALSE_POSITIVE
VALIDATOR_FALSE_NEGATIVE
AUTHORITY_VIOLATION_ATTEMPT
SECURITY_BOUNDARY_FAILURE
OPERATOR_FRICTION_INTERVENTION
ACI_AMBIGUITY
SUPPLY_CHAIN_DEFECT
UNKNOWN
```

Do not force every incident into a precise category if evidence supports only `UNKNOWN`.

---

# 7. Frozen regression cases

## 7.1 Promotion rule

A real incident should become a frozen case when:

- it materially affected outcome/safety/rework/operator effort; and
- it can be represented reproducibly enough to test the relevant mechanism.

## 7.2 Case contents

```text
case_id
source run/outcome/incident
problem statement
frozen task/context/environment fixture or safe surrogate
expected behavioral properties
known failure classification
relevant harness/Skill config
privacy/sanitization notes
created_at
```

## 7.3 Expected behavior

Prefer behavior properties:

> write outside scope must be denied

rather than brittle implementation text:

> source file must contain exact string X.

---

# 8. Three-layer evaluation model

## Layer 1 — Mechanical/unit/property evaluation

Fast, deterministic checks:

- schema/parsers;
- authority guards;
- hook behavior;
- Skill routing fixtures;
- environment compatibility;
- tool result envelopes;
- security properties.

## Layer 2 — Agent/model qualitative regression

Run representative tasks through real agent behavior and score:

- correctness;
- instruction following;
- context selection;
- tool use;
- rework;
- unnecessary actions;
- reviewability.

Use multiple models/providers only when comparing portability/generalization matters.

## Layer 3 — Production/outcome sampling

Measure real completed runs:

- escaped defects;
- real-world FAILURE/PARTIAL outcomes;
- operator intervention;
- recovery incidents;
- cost/yield;
- time-to-useful-completion;
- security incidents.

No single layer is sufficient.

---

# 9. Evaluation corpus structure

Candidate organization:

```text
evals/
  mechanical/
  tasks/
  context/
  skills/
  aci/
  environment/
  security/
  recovery/
  historical-incidents/
```

Each eval declares:

```text
purpose
fixture/source
frozen inputs
scoring method
expected properties
known limitations
version
```

Avoid giant generic benchmark scores that do not map to MAPS failure modes.

---

# 10. Core experiment program

The research scan proposed five experiments. They become explicit roadmap milestones.

## EXP-A — Skill selection reliability

### Question

Can agents/context routing reliably select the right Skill and abstain when none applies?

### Corpus

- positive cases;
- paraphrases;
- vocabulary shifts;
- near misses;
- hard negatives;
- multi-skill cases;
- no-skill cases.

### Metrics

- precision;
- recall;
- false activation;
- missed activation;
- top-k ranking;
- context overhead.

### Promotion gate

Do not rely on fuzzy autonomous Skill selection until performance meets an explicit threshold and failure modes are understood.

---

## EXP-B — Hooks/interceptors impact

### Question

Do deterministic hooks improve reliability enough to justify added complexity/friction?

### Control

Normal agent/harness behavior.

### Treatment

Representative hook set:

```text
before_write scope guard
after_write compile/lint
secret-safe telemetry
before_external/destructive policy check
```

### Metrics

- escaped defects;
- corrections before submission;
- model/tool calls;
- false blocks;
- operator interventions;
- runtime/context overhead.

### Promotion gate

Keep hooks whose measured prevention value exceeds their false-positive/friction cost.

---

## EXP-C — ACI/tool interface quality

### Question

Do bounded structured operation results reduce agent confusion?

### Control

Raw shell/file/text-heavy interfaces.

### Treatment

Structured bounded results with stable codes, pagination, explicit mutation/completeness.

### Metrics

- repeated tool calls;
- false assumptions;
- context tokens;
- time to correct action;
- task outcome;
- error-recovery quality.

### Promotion gate

Standardize result shapes only where evidence shows better reliability/usability or where safety semantics require it.

---

## EXP-D — EnvironmentSpec reproducibility

### Question

Does explicit environment specification reduce irreproducibility and recovery failures?

### Control

Ad-hoc current machine state.

### Treatment

EnvironmentSpec + fingerprint + compatibility checks.

### Metrics

- setup failure;
- inconsistent test results;
- environment-related incident rate;
- recovery success;
- setup cost/time.

### Promotion gate

Expand EnvironmentSpec scope/snapshotting only if measurable reproducibility gains justify it.

---

## EXP-E — Imported Skill red team

### Question

Can MAPS reliably constrain malicious/low-quality Skills before community/imported capability expansion?

### Cases

- root filesystem request;
- hidden script execution;
- policy override claim;
- misleading routing metadata;
- poisoned reference;
- credential request;
- network exfiltration;
- capability expansion after update.

### Metrics

- detection/block rate;
- false-positive quarantine;
- policy enforcement;
- analyst/reviewer effort.

### Promotion gate

Third-party executable Skills remain quarantined until this suite is credible.

---

# 11. Context Builder evaluation

The legacy experience makes this mandatory.

Corpus must include:

- exact wording;
- paraphrases;
- vocabulary shifts;
- hard negatives;
- temporal/version questions;
- source drift;
- explicit missing evidence;
- authority-status distinctions.

Metrics:

- task/source recall;
- exact-source accuracy;
- anchored evidence accuracy;
- abstention on negatives;
- temporal/version correctness;
- authority-label preservation;
- context cost.

Do not promote semantic/vector retrieval merely because it retrieves more text.

---

# 12. Skill evaluation

Evaluate both selection and procedure quality.

## Selection

Did the right Skill activate?

## Procedure

When active, did it improve:

- correctness;
- completion;
- safety;
- time;
- rework;
- context consumption;
- operator effort?

A Skill with perfect routing but harmful procedure should fail.

---

# 13. Security evaluation

Integrate the Agentic Security adversarial corpus.

Track:

- blocked unauthorized actions;
- escaped boundary violations;
- false-positive blocks;
- secret exposures;
- stale recovery attempts;
- poisoned-memory/Skill cases;
- supply-chain cases.

Security evaluation is not a separate optional score; certain property failures are release blockers.

---

# 14. Review quality evaluation

Potential metrics:

- escaped defect after APPROVED review;
- stale evidence approval;
- criterion verification misses;
- security/authority review miss;
- review turnaround;
- unnecessary review blockers;
- reviewer independence failures blocked.

Goal is not more reviews; it is better detection per review effort.

---

# 15. Operator friction metrics

Operational usability matters.

Capture when known:

```text
operator had to restate task
operator corrected scope
operator manually reconciled session
operator repeated approval context
operator fixed environment
operator bypassed/disabled noisy guard
operator intervened in runaway/no-progress run
```

These observations can be outcome/incident evidence.

Do not infer intervention from arbitrary chat. Preserve explicit provenance.

---

# 16. Cost/yield metrics

Useful cost is not just token spend.

Candidate measures:

```text
provider/model cost
runtime duration
tool calls
retries
helper runs
operator time/interventions
review effort
rework count
escaped defects
successful outcome
```

Useful derived concept:

> cost per accepted successful outcome

rather than cheapest run in isolation.

---

# 17. Operational learning lifecycle

## 17.1 Observation

Something happened in a run/outcome/incident.

## 17.2 Candidate lesson

A bounded proposed generalization is written with provenance.

Example:

> Candidate: For project X, generated files should be traced to their generator before direct edits.

## 17.3 Review

Check:

- does evidence support generalization?
- is scope narrow enough?
- does active policy already cover it?
- is it a one-off rather than recurring pattern?
- should solution be a hook/Skill/flow instead of prose guidance?

## 17.4 Promotion

Possible destinations:

```text
Skill revision
hook/invariant
EnvironmentSpec update
Context Builder rule
review checklist
scoped guidance
flow
no action
```

Do not default every lesson to prompt text.

## 17.5 Expiry/supersession

Every promoted temporary/scoped lesson should be reviewable and removable.

---

# 18. Harness configuration identity

Evaluation requires knowing what configuration produced a run.

Define a `HarnessConfigRef` or equivalent derived identity for consequential settings such as:

```text
routing configuration
hook set/versions
context-builder version/config
Skill selection logic
recovery parameters
helper policy
environment behavior
instruction-set revision
```

Prefer content hashes/versioned config references over copying configs into every Run Record.

---

# 19. Controlled harness refinement

## 19.1 Candidate generation

Candidates may come from:

- recurring incident analysis;
- operator proposal;
- research;
- agent-generated suggestion;
- Skill eval failures;
- cost/yield analysis.

Source does not grant authority.

## 19.2 Evaluation

Compare:

```text
CURRENT configuration
vs
CANDIDATE configuration
```

on the same frozen corpus.

## 19.3 Required dimensions

At minimum:

- correctness;
- safety/security blockers;
- escaped defects;
- operator intervention;
- rework;
- runtime/cost;
- context consumption;
- failure distribution.

## 19.4 Promotion

Candidate becomes proposal with evidence.

Normal independent review/operator decision applies when consequential.

## 19.5 Rollback

Configuration promotion must be versioned so regression can revert to known prior configuration without rewriting history.

---

# 20. Time-travel / fork debugging track

Durable workflow systems show value in replaying/forking from historical checkpoints.

MAPS should not attempt deterministic replay of arbitrary LLM thought.

Useful narrower form:

```text
historical Run Record
   ↓
select observable checkpoint
   ↓
reuse frozen task/context/environment fixture
   ↓
change one harness variable
   ↓
run new branch
   ↓
compare outcomes/trajectory
```

This is experimental fork-debugging, not mutation of the original run.

Useful for:

- routing changes;
- Skill revisions;
- hook behavior;
- context composition;
- recovery parameter changes.

---

# 21. Statistical caution

MAPS may initially have small sample sizes.

Rules:

- report counts and uncertainty, not fake precision;
- distinguish controlled eval results from production observations;
- avoid claiming causality from a handful of runs;
- preserve model/provider/task mix;
- compare like with like where possible;
- major harness changes need stronger evidence than one anecdote.

A small but severe security incident may justify action even without statistical frequency; risk severity matters.

---

# 22. Data retention/privacy

Evaluation data can contain sensitive information.

Default Run Record should avoid raw:

- prompts;
- private file contents;
- secrets;
- user data;
- unredacted logs.

Use references/hashes/structured outcomes where possible.

Historical regression fixtures should be sanitized or synthetic when raw evidence is sensitive.

Retention policy may differ for:

```text
canonical task evidence
portable Run Records
raw diagnostic artifacts
eval fixtures
aggregate metrics
```

---

# 23. Dashboards/read models

A future evaluation/status view may show:

```text
outcome success/partial/failure rates
escaped defect rate
operator interventions
recovery incidents
Skill routing failures
security blocks/failures
cost per successful outcome
regression-suite status
candidate harness experiments
```

Read-only. No dashboard button should silently promote a harness configuration without normal approval semantics.

---

# 24. Metrics hierarchy

## Primary outcome metrics

- real SUCCESS/PARTIAL/FAILURE;
- escaped defects;
- accepted task completion;
- operator intervention/rework.

## Reliability metrics

- recovery success;
- duplicate execution;
- tool failure;
- environment drift;
- stale evidence/session incidents.

## Efficiency metrics

- cost per successful outcome;
- runtime;
- tool/model calls;
- context consumption.

## Safety metrics

- unauthorized actions blocked/escaped;
- secret exposures;
- supply-chain defects;
- security false positives.

## Learning metrics

- incidents converted to regression cases;
- candidate lessons promoted/rejected/expired;
- harness changes with comparative evidence;
- regressions caught before promotion.

---

# 25. Implementation phases

## L1 — Run Record v1

Define portable redacted record assembled from current task/run/trace/outcome evidence.

Exit gate: representative run can be exported/reviewed without copying canonical authority.

## L2 — Incident taxonomy + case format

Implement explicit incident classification and frozen-case specification.

Exit gate: one real/historical incident represented as reproducible regression case.

## L3 — Three-layer eval harness

Create mechanical + agent/task + production/outcome evaluation structure.

Exit gate: one candidate mechanism can be tested across at least layers 1 and 2; production layer remains observational until data accumulates.

## L4 — Research experiments A–E

Run the five pre-architecture experiments.

Exit gate: roadmap decisions updated based on measured findings rather than assumptions.

## L5 — Operational-learning lifecycle

Implement candidate lesson → review → scoped promotion → expiry/supersession.

Exit gate: lessons cannot become active guidance without provenance/review.

## L6 — Harness configuration identity

Version/hash consequential harness configurations.

Exit gate: each evaluated run can identify which configuration produced it.

## L7 — Comparative harness evaluation

Current vs candidate on frozen corpus.

Exit gate: evidence report includes correctness/safety/cost/operator-friction deltas.

## L8 — Proposal-only refinement workflow

Candidate can be proposed and reviewed, not self-promoted.

Exit gate: promotion requires explicit authorized review/decision and is reversible/versioned.

## L9 — Fork/time-travel experiment

Only after Run Records/environment fixtures are mature.

Exit gate: one historical case can be re-run from a selected observable checkpoint under a changed harness variable.

---

# 26. Concrete task backlog

1. Define Run Record v1 schema.
2. Build redacted Run Record exporter from canonical/derived evidence.
3. Define HarnessConfigRef/version identity.
4. Add Skill/environment/hook version refs to Run Record where available.
5. Define incident taxonomy record.
6. Define frozen regression-case format.
7. Convert one legacy/real incident into first case.
8. Create eval directory/manifest conventions.
9. Implement mechanical property-eval runner.
10. Implement representative task/agent eval runner.
11. Define production outcome aggregation read model.
12. Build EXP-A Skill-routing corpus.
13. Run EXP-B hook control/treatment comparison.
14. Run EXP-C ACI comparison.
15. Run EXP-D EnvironmentSpec reproducibility comparison.
16. Run EXP-E malicious Skill red-team suite.
17. Add Context Builder paraphrase/hard-negative eval.
18. Add security regression corpus integration.
19. Add review-quality/escaped-defect metrics.
20. Add explicit operator-friction observation fields/workflow where justified.
21. Define candidate operational lesson record.
22. Implement lesson review/promotion/expiry lifecycle.
23. Add harness-config comparison report.
24. Define promotion thresholds by risk/mechanism class.
25. Implement proposal-only harness change workflow.
26. Add versioned rollback reference.
27. Prototype fork debugging on one frozen case.
28. Add read-only evaluation summary to future status/operator surface.

---

# 27. Definition of done

Learning & Evaluation v1 is done when:

- representative runs can produce a portable, secret-safer Run Record;
- real failures can become frozen regression cases with provenance;
- MAPS has mechanical, agent/task, and production/outcome evaluation layers;
- Skill, ACI, EnvironmentSpec, Context Builder, security, and hook changes can be tested on explicit corpora;
- harness configuration identity makes comparisons reproducible;
- operational lessons require review and have scope/expiry/supersession;
- candidate harness changes are compared against the current harness on frozen evidence;
- safety/correctness/operator-friction/cost dimensions are evaluated together;
- MAPS cannot self-authorize a persistent configuration/policy/guidance change;
- promoted changes remain versioned and reversible;
- the system optimizes for useful successful outcomes rather than agent activity.
