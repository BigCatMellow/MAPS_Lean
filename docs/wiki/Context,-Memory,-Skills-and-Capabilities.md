# Context, Memory, Skills and Capabilities

MAPS_L treats context selection, memory trust, Skill loading, and actual
delivery as separate decisions. That separation prevents a useful-looking
record from becoming authority merely because it was retrieved or remembered.

Back to [[Home]].

## Context plans

`maps context TASK --repo-root PATH` builds a disposable, read-only plan. It
uses explicit task relationships, root authority, dependency state, and exact
file hashes. It does not copy file contents, scan the repository, or run
semantic search.

The plan distinguishes:

- authority;
- required task inputs;
- dependency state;
- guidance and withheld guidance;
- matched Skills;
- unresolved or out-of-repository references; and
- task boundaries and verification requirements.

It also reports that semantic retrieval, repository scanning, and file-content
inclusion were not used. This is deliberate: explicit-first assembly is the
current production design.

## Memory trust and admission

Memory-like evidence is classified into trust classes and passed through one
fixed admission table:

| Admission | Meaning |
| --- | --- |
| `LOAD` | eligible to enter the default context/action payload |
| `WITHHOLD` | keep out of the default load; a reference may remain so it can be pursued deliberately |
| `DENY` | exclude; unresolved Skill trust and quarantined/untrusted input fail closed |

Examples of current behavior:

- canonical policy, approved Skills, and reviewed guidance may load;
- claims, observations, candidate lessons, superseded material, and retired
  material are withheld;
- quarantined and untrusted input are denied;
- stale metadata can demote a loadable item to WITHHOLD; and
- missing or malformed trust metadata never means trusted.

The canonical task context—authority, required inputs, dependencies, and
boundaries—is outside this optional-memory gate, so one malformed memory item
does not suppress the whole plan.

## Assembly is not delivery

`maps run send-context RUN_ID` renders the run's current context plan into a
deterministic payload. By default it is a dry run: it prints the payload,
constructs no `HarnessService`, and sends nothing.

Actual delivery requires all of:

```text
--deliver-context
--enforce-canonical-run
--harness-project-id PROJECT
```

The armed path resolves the run/session binding and makes exactly one
`HarnessService.send()` call. It has no direct hcom fallback and no automatic
retry. An unresolved binding, Hook denial, non-OK adapter result, or exception
reports failure rather than claiming delivery.

## Outbound memory provenance

The renderer attaches a `memory_provenance` entry for every guidance or Skill
item whose text or identifier enters the payload. Only LOAD-class guidance and
hash-verified LOAD-class Skill bodies are embedded. WITHHOLD/DENY items can at
most appear as non-content references.

Before hcom receives the message, the `BEFORE_SEND` memory-provenance guard:

- re-derives admission from each trust class instead of trusting the payload's
  stated admission;
- allows LOAD;
- allows WITHHOLD only when referenced rather than embedded;
- denies embedded WITHHOLD or any DENY item;
- denies a memory-bearing payload with missing or malformed provenance; and
- remains inert for a payload that contains no memory-derived content.

The guard currently trusts the renderer's boolean claim about whether content
was embedded; it does not independently parse the message body to prove that
claim.

**Capability 6.22 remains IN PROGRESS.** The production caller and fail-closed
path are merged, but the checklist still requires the first real
`BEFORE_SEND`/memory-provenance exposure. Implementation alone did not close the
row.

## Skill discovery and progressive loading

`maps flow start` builds the project Skill catalog. Startup discovery reads
metadata and identity rather than loading every procedure body:

1. discover Skill name/id, description, content hash, and resource metadata;
2. assess/catalog provenance and lifecycle state;
3. select using explicit task signals and the current match-strength gate;
4. apply trust and task-capability gates;
5. load the hash-verified `SKILL.md` body only for a selected LOAD-class Skill;
6. attach an execution-resource **manifest**—path, kind, size, no content; and
7. load one declared resource on demand through `load_skill_resource`, with a
   whole-directory hash check.

WITHHOLD, ON_DEMAND, and DENY Skills receive neither a body nor a resource
manifest. A body or manifest loading error fails closed for that Skill without
destroying the rest of the context plan.

## Current Skill selection quality

The selector uses token match strength, inverse document frequency, routing
stopwords, an anchor requirement, and strength/coverage thresholds. A frozen
25-case evaluation recorded zero false activations after hard-negative tuning.

This is **not semantic routing**. The accepted explicit-first selector remains
weak on synonym-level vocabulary shifts and fine ambiguity. Those cases are
deferred to capability 6.33. The semantic retrieval candidate is evaluation
only and is not used in production context construction.

## Skill trust lifecycle and operators

Skill revisions are content-addressed; changing the bytes creates a new catalog
subject. The append-only lifecycle supports:

```text
VALIDATED / QUARANTINED -> APPROVED -> ACTIVE -> SUPERSEDED
QUARANTINED / ACTIVE -> RETIRED
```

`maps skill list|show|approve|activate|retire|supersede` expose the lifecycle.
Illegal transitions are rejected by the canonical store. A Skill recorded as
quarantined, retired, or superseded cannot be loaded as active procedure text.

Once the authorized-operator registry is seeded, every lifecycle-transition
verb requires an authorized `--actor`. With an empty registry, this identity
gate is currently disabled; see [[Review, Authority and Merge Safety]].

Capability 6.10 remains **IN PROGRESS** because the wider supply-chain control
model is not complete, including third-party manifest/countersign behavior and
some activation/enforcement gaps.

## Capability sidecars and task-policy intersection

A Skill may declare capabilities in a `capabilities` sidecar. Static detectors
compare observed risky content with those declarations. A detected capability
that was not declared produces `UNDECLARED_CAPABILITY` and quarantine.

Selected Skills are also intersected with the task's existing policy envelope.
An out-of-envelope declaration is denied from the plan with
`SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE`.

Current distinctions include:

- `network-read` is narrower than `network-general`; because the static script
  detector cannot reliably distinguish read from write, a generic detected
  network operation requires `network-general`;
- `filesystem-write:<relative-path>` is valid only for a relative path with no
  `..`; and
- `process-stop`, general network/GitHub/database writes, external deployment,
  and secret use map to the task policy flags that must authorize them.

Limits that should not be overstated:

- path-scoped `filesystem-write:<path>` is parsed as a narrowing but is not yet
  enforced against the task's exact writable paths;
- `paid_execution` and `broad_architecture` have no corresponding Skill token;
- per-host network scoping and a separate MCP/tool-server manifest are not
  implemented; and
- the capability check currently occurs at context-plan assembly rather than as
  a universal tool-call sandbox.

Capability 6.24 therefore remains **IN PROGRESS**.

Sources: current
[`runtime/context_builder.py`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/runtime/context_builder.py),
[`runtime/context_delivery.py`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/runtime/context_delivery.py),
[`runtime/skills/`](https://github.com/BigCatMellow/MAPS_Lean/tree/main/runtime/skills),
and the
[`capability checklist`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md).
