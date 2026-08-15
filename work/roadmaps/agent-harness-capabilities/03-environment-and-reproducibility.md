# Roadmap 03 — Environment & Reproducibility

Status: `PLANNING ONLY — NOT ACTIVE AUTHORITY`

Purpose: make MAPS executions reproducible, diagnosable, and safely recoverable across machines, worktrees, containers, remote sandboxes, and restarted sessions by explicitly binding runs to the environment assumptions that matter.

Source research themes:

- Devin environment blueprints / known-good setup
- OpenHands sandboxes
- OpenAI Agents SDK harness/compute separation, workspace manifests, snapshot/rehydration concepts
- Prime-style runtime environment binding
- worktree isolation
- recovery compatibility

---

# 1. Why this roadmap exists

Two runs can receive the same task and context yet behave differently because their execution environments differ:

- package versions;
- runtime versions;
- missing tools;
- stale dependencies;
- environment variables;
- network availability;
- repository base revision;
- generated files;
- local services;
- dirty worktree state.

If MAPS does not capture these differences, it can misdiagnose environment drift as model failure, reproduce bugs inconsistently, or recover work into an incompatible environment.

The target is **declarative reproducibility first**, not universal containerization.

---

# 2. Current MAPS baseline

Already available:

- immutable run manifests;
- task revision binding;
- context-file hashes;
- readable/writable/forbidden scopes;
- runtime limits;
- optional Git base revision;
- bounded helper/recovery state;
- installer/smoke validation;
- current worktree cleanliness checks in selected helper paths.

Missing as a first-class concept:

> What environment assumptions must hold for this run to be considered equivalent/recoverable?

---

# 3. Target architecture

```text
Task / Run Manifest
       │
       ├── task revision
       ├── context hashes
       ├── base revision
       └── environment_spec_hash
                    │
                    ▼
            EnvironmentSpec
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
   local host    worktree      sandbox/container
      │             │             │
      └─────────────┼─────────────┘
                    ▼
          EnvironmentFingerprint
                    │
                    ▼
          compatible / drifted / unknown
```

EnvironmentSpec describes requirements. EnvironmentFingerprint records observed execution facts.

---

# 4. EnvironmentSpec v1

## 4.1 Goal

Describe the minimum environment contract needed to set up, validate, execute, and recover a task.

## 4.2 Candidate fields

```yaml
environment_id: maps-python-runtime
version: 1

repository:
  base_revision: optional
  require_clean_worktree: true|false

runtimes:
  python: ">=3.12,<3.13"
  node: optional

required_tools:
  - git
  - python

setup:
  commands:
    - python -m pip install -r runtime/requirements.txt

maintenance:
  commands: []

validation:
  quick:
    - python -m compileall -q runtime tests
  normal:
    - python -m unittest discover -s tests -v
  full:
    - python -m runtime.smoke --with-langgraph

network:
  required: false
  allowed_domains: []

services:
  - optional structured service requirements

secrets:
  required_names: []

artifacts:
  dependency_locks:
    - runtime/requirements.txt
```

The exact syntax may be JSON/YAML/TOML. Semantics matter more than format.

## 4.3 Do not include secret values

Spec may name required secret capabilities/identifiers, never values.

---

# 5. Environment fingerprint

A fingerprint is observed evidence from a concrete execution environment.

Candidate content:

```text
environment_spec_hash
host/sandbox type
runtime versions
required tool versions
repo revision
worktree identity
worktree dirty state
lockfile/dependency hashes
selected environment variables by name/presence only
network mode
service availability summary
created_at
```

Do not dump the whole environment (`env`) into durable logs.

The fingerprint should be intentionally minimal and security-aware.

---

# 6. Compatibility semantics

Recovery and comparison need explicit rules.

Candidate states:

```text
COMPATIBLE
COMPATIBLE_WITH_WARNINGS
DRIFTED
INCOMPATIBLE
UNKNOWN
```

Examples:

- exact same spec/hash/runtime versions → COMPATIBLE;
- patch-level runtime drift allowed by spec → COMPATIBLE_WITH_WARNINGS;
- wrong major runtime → INCOMPATIBLE;
- lockfile changed from run binding → DRIFTED;
- tool version cannot be inspected → UNKNOWN.

Do not collapse unknown into compatible.

---

# 7. Setup lifecycle

Proposed stages:

```text
resolve EnvironmentSpec
        ↓
inspect current environment
        ↓
compare requirements
        ↓
setup if authorized/needed
        ↓
validate environment
        ↓
create fingerprint
        ↓
bind fingerprint/spec hash to run evidence
```

Setup operations that mutate the host/environment must themselves pass Harness hooks/authority rules.

---

# 8. Harness / compute separation

## 8.1 Principle

MAPS state and authority should survive loss/replacement of the execution environment.

Harness side owns/references:

- task/run identity;
- policy/authority;
- context hashes;
- environment requirements;
- session lineage;
- recovery evidence.

Compute side receives only what it needs to execute.

## 8.2 Benefits

- sandbox crashes do not destroy task truth;
- sessions can be rehydrated into a compatible environment;
- secrets can remain brokered outside model-controlled storage;
- multiple execution providers can satisfy the same EnvironmentSpec;
- runtime differences become explicit evidence.

---

# 9. Workspace model

MAPS should support multiple implementations behind one environment contract.

## 9.1 Local workspace

Good for low-risk/simple work.

Requirements:

- explicit repo root;
- dirty-state inspection;
- scope enforcement;
- environment fingerprint.

## 9.2 Git worktree

Good for concurrent writable coding runs.

One run → one attributable worktree when this track is active.

Bind:

```text
run_id
worktree path/id
base revision
branch/ref if used
created_at
cleanup state
```

## 9.3 Container/sandbox

Useful when isolation/reproducibility/security justify it.

EnvironmentSpec remains portable across implementations.

## 9.4 Remote execution

Must preserve stable run/session/environment IDs and avoid making remote provider state canonical task truth.

---

# 10. Worktree isolation roadmap

This is conditional but important.

## Trigger

Promote when:

- multiple writable agents commonly operate concurrently; or
- a collision/dirty-worktree incident occurs; or
- helpers and primary agents routinely need parallel code changes.

## Lifecycle

```text
run prepared
   ↓
create worktree from bound base revision
   ↓
bind worktree to run
   ↓
execute within scoped paths
   ↓
submission/review
   ↓
integration decision
   ↓
explicit cleanup
```

## Safety rules

- never reuse a dirty worktree for another run without explicit reconciliation;
- never `reset --hard` another run's work automatically;
- cleanup after integration/rejection is explicit;
- worktree deletion requires proof that needed evidence/work has been collected;
- base revision must be visible in review evidence.

---

# 11. Snapshot / rehydration track

Do not build snapshot infrastructure immediately.

First prove EnvironmentSpec/fingerprint value.

Later candidate:

```text
known-good workspace
   ↓
snapshot identifier
   ↓
run starts from snapshot
   ↓
crash/loss
   ↓
rehydrate same/compatible snapshot
   ↓
restore explicit run/session context
```

Snapshot identity must not become task authority.

Useful only if setup cost, remote execution, or recovery complexity makes it worthwhile.

---

# 12. Dependency integrity

Environment reproducibility requires tracking dependency inputs.

Possible evidence:

- lockfile/content hashes;
- requirements files;
- package-manager lock versions;
- system tool versions;
- image digest if containerized;
- setup script hash.

Do not attempt to hash entire machines.

Track only factors material to execution.

---

# 13. Network model

EnvironmentSpec should state whether network is:

```text
NOT_REQUIRED
REQUIRED_RESTRICTED
REQUIRED_GENERAL
UNKNOWN
```

Where restricted, declare expected domains/services when practical.

This supports both reproducibility and security.

A task requiring external network access still needs task/policy authority where consequential.

---

# 14. Secret capability model

EnvironmentSpec can declare:

```text
requires credential capability: github-read
requires credential capability: staging-db-read
```

Not:

```text
GITHUB_TOKEN=...
```

Future credential broker can satisfy these capabilities with scoped/time-limited material.

The environment fingerprint records only that the capability was available, not the secret value.

---

# 15. Recovery integration

Before RnS resumes/replaces a run, check:

1. canonical task still ACTIVE/current;
2. run binding still valid;
3. context hashes compatible;
4. EnvironmentSpec still current;
5. observed replacement environment compatible;
6. worktree/repo state attributable;
7. session ambiguity resolved.

If environment compatibility is unknown and material, recovery should stop/escalate rather than guess.

---

# 16. Validation tiers

EnvironmentSpec should support named validation tiers.

## Quick

Cheap sanity checks run frequently:

- compiler/parser;
- dependency presence;
- basic tool availability.

## Normal

Task-development validation:

- relevant unit tests;
- lint/security checks.

## Full

Review/release validation:

- full suite;
- smoke/integration/install tests;
- artifact validation.

Skills/tasks may reference tiers rather than duplicating commands.

---

# 17. Failure modes

## 17.1 Setup command partially succeeds

Required:

- capture structured failure;
- do not claim environment READY;
- do not continue merely because some dependencies installed;
- safe retry semantics depend on command declarations.

## 17.2 Runtime version outside spec

Return INCOMPATIBLE or warning per declared range; do not silently continue for consequential work.

## 17.3 Dirty worktree discovered

Do not clean automatically.

Identify whether dirt belongs to current run, prior work, or unknown origin.

## 17.4 Lockfile changed mid-run

Mark environment/context drift. Require revalidation/rebinding before consequential continuation.

## 17.5 Snapshot unavailable during recovery

Fallback only if a newly constructed environment proves compatible. Otherwise explicit blocker.

## 17.6 Remote provider claims environment success but local evidence unavailable

Represent provider assertion separately from verified fingerprint.

## 17.7 Network unexpectedly required

Do not widen network permissions automatically. Surface mismatch between spec and actual execution need.

---

# 18. Security requirements

- EnvironmentSpec contains no secret values;
- setup scripts are versioned/provenanced;
- network permissions explicit;
- containers/sandboxes do not imply trust;
- worktree path cannot widen task write scope;
- environment setup does not grant external/destructive authority;
- remote execution identity verified before attachment;
- third-party images/snapshots require provenance/trust policy;
- fingerprint output avoids sensitive environment dumps.

---

# 19. Testing strategy

## 19.1 Spec parsing/validation

- valid/invalid versions;
- missing tools;
- incompatible runtime;
- malformed commands;
- secret-value detection where feasible.

## 19.2 Fingerprint tests

- stable hashes for same environment inputs;
- meaningful drift detection;
- no secret values captured.

## 19.3 Compatibility tests

- allowed patch drift;
- incompatible major version;
- changed lockfile;
- unknown tool version;
- missing network/service.

## 19.4 Worktree tests

- two concurrent worktrees isolated;
- dirty-state handling;
- explicit cleanup;
- no cross-run reset/delete;
- base-revision evidence preserved.

## 19.5 Recovery tests

- same environment resumes;
- compatible replacement succeeds;
- incompatible environment blocks;
- task/context revision drift blocks.

## 19.6 Reproducibility experiment

Run same fixed tasks under:

```text
ad-hoc environment
vs
EnvironmentSpec-governed environment
```

Measure setup failures, test disagreements, recovery success, and reproducibility.

---

# 20. Metrics

Useful:

- environment-related failure rate;
- reproducibility success rate;
- recovery success on compatible replacement;
- setup time;
- setup retry rate;
- test disagreement attributable to environment drift;
- dirty-worktree collision incidents;
- percentage of runs with known environment compatibility;
- snapshot benefit if later introduced.

Avoid:

- number of containers;
- number of EnvironmentSpecs;
- environment complexity as a proxy for quality.

---

# 21. Implementation phases

## E1 — EnvironmentSpec schema

Define minimum portable spec + parser + hash.

Exit gate: one existing MAPS runtime workflow can be described accurately without container assumptions.

## E2 — Fingerprint + compatibility

Inspect runtime/tool/repo/dependency facts and compare to spec.

Exit gate: tests distinguish compatible/drifted/incompatible/unknown environments.

## E3 — Run binding

Add environment spec/fingerprint references to run evidence without making them task authority.

Exit gate: trace can show what environment a run actually used.

## E4 — Validation tiers

Integrate quick/normal/full commands with Harness hooks.

Exit gate: immediate and review-time validation can reference one environment definition.

## E5 — Recovery compatibility

Require environment compatibility for selected recovery paths.

Exit gate: incompatible replacement cannot silently resume.

## E6 — Worktree isolation

Conditional trigger as described above.

Exit gate: concurrent writable runs do not share mutable worktree state.

## E7 — Snapshot/rehydration experiment

Only if setup/recovery cost warrants it.

Exit gate: measured improvement over reconstruction from spec.

---

# 22. Concrete task backlog

1. Define EnvironmentSpec v1 schema.
2. Implement parser/validator/hash.
3. Describe current MAPS runtime as first spec.
4. Implement environment fingerprint collector.
5. Add secret-safe fingerprint policy.
6. Implement compatibility evaluator.
7. Add runtime/tool/dependency drift tests.
8. Bind spec hash to run evidence.
9. Surface environment in trace/status.
10. Define validation tiers.
11. Integrate validation tiers with post-write/review hooks.
12. Add network requirement classification.
13. Add credential-capability declarations by name only.
14. Integrate recovery compatibility checks.
15. Run reproducibility experiment.
16. Define worktree binding model.
17. Implement isolated writable worktree pilot when trigger met.
18. Add worktree cleanup/integration evidence.
19. Evaluate snapshot/rehydration need after real data.
20. Prototype snapshot provider only if justified.

---

# 23. Definition of done

Environment & Reproducibility v1 is done when:

- important runs declare a portable EnvironmentSpec;
- MAPS can observe a minimal secret-safe environment fingerprint;
- compatibility/drift/unknown are explicit;
- run evidence shows which environment requirements/facts applied;
- validation commands are declared once and reusable by hooks/review;
- recovery can reject materially incompatible environments;
- local/worktree/sandbox implementations can satisfy the same conceptual spec;
- concurrent worktree isolation is available when evidence justifies it;
- secret values and machine-wide environment dumps are not persisted;
- universal containerization or snapshot infrastructure has not been added without evidence.
