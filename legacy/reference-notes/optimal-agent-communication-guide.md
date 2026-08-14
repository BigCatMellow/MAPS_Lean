# MAP Agent DSL and Communication Guide

## Operating assumption

Raw agent communication is machine-facing. A human is not expected to read it
unless they request an explanation. Agents should generate a plain-English view
on demand.

Human readability is therefore optional, but correct model comprehension is
not. MAP should use a small domain-specific language (DSL) for commands, state,
roles, routing, and stable references. Controlled English should carry novel
reasoning, uncertainty, exceptions, aesthetic judgment, and nuanced intent.

The objective is to reduce total coordination tokens while preserving correct
interpretation, ownership, state, evidence, constraints, and next actions.

## Central design principle

Shorthand is a pointer, not a summary. Its complete meaning must exist in an
authoritative, versioned registry and should be decoded by software rather than
remembered or guessed by an AI.

```text
agent emits DSL
→ deterministic parser
→ schema and version validation
→ routing and selective retrieval
→ minimal canonical instruction
→ receiving agent
→ structured result validation
```

This prevents semantic drift. `P17@v2` always resolves to the registered version
2 definition of P17; no agent may decide that it “probably means” something
else.

## Recommended architecture

### Layer 1: typed MAP DSL

The DSL carries repeated, categorical, stable, and mechanically verifiable
information:

```text
@MAP/1
FROM=critic
TO=builder
TASK=revise
TARGET=game_rules@12
APPLY=[P03@2,P07@1]
PRESERVE=[animation@4]
RETURN=[artifact,change_log]
```

Software parses and validates these fields before the receiving model acts.

### Layer 2: controlled-English payload

Natural language carries meaning that is new, nuanced, uncertain, or difficult
to represent without loss:

```text
DETAIL="The new mechanic creates more decisions, but it may require players to
remember too many exceptions. Preserve simplicity without eliminating meaningful
strategic choices."
```

Do not replace this tension with a vague code such as `SIMPLE+DEPTH` unless the
exact principle is registered and versioned.

### Layer 3: deterministic expansion and selective context

The orchestrator expands stable references and retrieves only what the current
task requires:

```text
Revise game_rules@12.

Requirements:
- P03@2: Strategic depth must arise from interactions among simple mechanics.
- P07@1: Avoid exceptions that do not produce meaningful decisions.

Preserve animation@4. Return the revised artifact and a change log.
```

Routing, permissions, target selection, and output requirements should remain
outside the prose prompt whenever the agent framework can enforce them directly.

### Layer 4: human explanation on demand

When a human requests context, render the DSL, resolved definitions, and natural
language payload into ordinary English. The explanation is a temporary view;
the validated DSL record and durable artifacts remain canonical.

## Why not another natural language?

Chinese or another natural language does not guarantee fewer model tokens.
Project IDs, code, paths, tools, and documentation are predominantly English.
Translation can add ambiguity and work.

The DSL plus controlled-English design offers a better tradeoff: formal control
where meanings are stable, and full expressive capacity where meaning is new.

## MAP/1 readable DSL schema

Every message begins with `@MAP/1`. An incompatible revision must use a new
version such as `@MAP/2`; agents and parsers must reject unknown versions rather
than guess their meaning.

### Standard fields

| Field | Meaning |
| --- | --- |
| `type` | `task`, `decision`, `blocker`, `ack`, `handoff`, or `info` |
| `id` | Stable task, decision, message, incident, or workstream ID |
| `state` | Current state |
| `owner` | Accountable agent |
| `done` | Newly completed work |
| `next` | Next action and target |
| `need` | Information, approval, or choice required |
| `blocker` | Active blocker; use `none` when useful to state explicitly |
| `risk` | Material risk or immutable constraint |
| `refs` | Durable evidence or context |
| `verify` | Checks performed and results |
| `priority` | Scheduling priority when needed |
| `detail` | Concise controlled English for information that does not fit safely elsewhere |

### State values

Use full state names:

`ready`, `active`, `blocked`, `submitted`, `approved`, `released`, `standby`,
`complete`

Full names prevent ambiguity such as whether `SUB` means “submitted” or
“subtask.”

### Agent targets

Use exact hcom groups in raw messages:

| Agent group | Target |
| --- | --- |
| Claude lab | `@claude-lab-` |
| Codex lab | `@codex-lab-` |
| Pi lab | `@pi-lab-` |
| Operator | `@bigboss` or configured operator identity |

Do not rely on an alias such as `@claude` unless transport software expands and
verifies it.

## Communication rules

1. Send changes, not complete history.
2. Use stable IDs instead of repeating descriptions.
3. Put the result and current state first.
4. Include an owner for actionable work.
5. Express the next action as `action@exact-target`.
6. Reference durable files and records instead of quoting them.
7. Omit optional fields when their absence cannot be misunderstood.
8. Broadcast only when every recipient needs the update.
9. Avoid acknowledgements with no new state unless delivery confirmation was
   requested.
10. Preserve approvals, destructive-action boundaries, privacy concerns, and
    safety constraints in explicit language.
11. Reject or clarify malformed and contradictory messages before acting.
12. Durable current state overrides stale messages.

## What to compress

DSL fields work best for information that is repeated, categorical, precisely
defined, stable, and easy to validate:

```text
DEPTH=3
FORMAT=markdown
SOURCE_POLICY=primary_only
ROLE=critic
STATE=blocked
```

Keep natural language for creative reasoning, early ideas, uncertain evidence,
exceptions, aesthetic judgment, unresolved interpretations, changing project
requirements, and descriptions of human intent.

Stable principles may use versioned pointers:

```text
APPLY=[P17@2]
```

The registry—not agent memory—must define `P17@2`. Definitions are immutable
within a version. Changing a meaning requires a new version.

## Formal facts and relationships

Logical propositions are useful for facts, relationships, status, and decisions:

```text
requires(project_7,rule_12)
violates(output_3,rule_12)
confidence(violates(output_3,rule_12),0.91)
```

These propositions should use registered predicates and validated argument
types. They complement rather than replace natural language; they are poorly
suited to novel interpretations or nuanced goals.

## Readable coordination examples

### Routine task update

```text
@MAP/1|type=task|id=TASK-205|state=submitted|owner=codex-lab-nivo
done=full-fidelity JSON export/import,tests
next=independent-review@claude-lab-
blocker=none
refs=TASK-205,src/app.js
```

### Decision request

```text
@MAP/1|type=decision|id=DEC-028|owner=claude-lab-gune
need=choose A/B/C@bigboss
recommend=A
detail=A exercises implementation,review,release,recovery
refs=artifacts/planning/working-backwards-proving-workflow-2026-07-15.md
```

### Blocker

```text
@MAP/1|type=blocker|id=TASK-204|state=blocked|owner=helper-soho
blocker=decision owner missing
next=record owner or reassign@claude-lab-gune
refs=PROMO-0009
```

### Useful acknowledgement

```text
@MAP/1|type=ack|id=hcom#394|owner=pi-lab-puma
done=route received
next=inspect schema edge cases
refs=TASK-205
```

### Narrow agent routing

```text
@pi-lab- @MAP/1|type=task|id=TASK-205|next=inspect schema edge cases|detail=findings only
@claude-lab- @MAP/1|type=task|id=TASK-204|next=review decision rationale|refs=DEC-028
@codex-lab- @MAP/1|type=task|id=TASK-204|next=implement approved change
```

## Durable handoff format

A handoff records current truth rather than replaying the conversation:

```text
@MAP/1|type=handoff|id=<workstream>|state=<state>|owner=<lead>
done=<current results>
next=<open actions and owners>
blocker=<active blockers>
risk=<constraints>
verify=<checks and results>
refs=<artifacts>
```

For long reference lists, use local aliases:

```text
refs=R1,R2,R3
R1=artifacts/reports/report.md
R2=artifacts/reviews/task-review.md
R3=artifacts/releases/task-release-checklist.md
```

## Transforming the example handoff

Source reviewed:

`/home/mellow/Documents/Projects/MultiAgentProject-main/Source/MAP_System/handoffs/ei-wave-external-benchmark-2026-07-15.md`

The source repeats chronology and retains two stale claims:

- It calls `TASK-205` in flight after recording its release.
- It says to promote `IDEA-0019` after released `TASK-204` completed that work.

Retain only the latest verified state, open work, constraints, verification, and
references.

### Improved readable MAP/1 version

```text
@MAP/1|type=handoff|id=ei-benchmark-2026-07-15|state=complete|owner=claude-lab-gune
done=external benchmark,emergence records,DEC-028,TASK-204,TASK-205
next=consider promotion of IDEA-0018;consider pilot of IDEA-0020
blocker=none
risk=no commit or push without operator authorization
verify=emergence validation passed;TASK-204 review passed;TASK-205 review passed
refs=R1,R2,R3,R4,R5,R6,R7

record=INS-0022|state=complete|detail=MAP differentiator is durable state plus mechanical gates
record=INS-0023|state=complete|detail=proving-workflow gap resolved by DEC-028
record=IDEA-0018|state=ready|detail=three-layer evaluation plus incident taxonomy
record=IDEA-0019|state=released|refs=TASK-204|detail=optional debate pre-escalation
record=IDEA-0020|state=ready|detail=per-agent ownership metrics
record=DEC-028|state=active|detail=standing proving workflow is software delivery
record=TASK-204|state=released|verify=independent review passed
record=TASK-205|state=released|verify=round-trip,malformed-input,8 lossy fields

R1=artifacts/reports/ei-external-benchmark-2026-07-15.md
R2=notes/agent-incident-taxonomy.md
R3=artifacts/planning/working-backwards-proving-workflow-2026-07-15.md
R4=artifacts/reviews/task204-review-toku.md
R5=artifacts/releases/task-204-release-checklist.md
R6=artifacts/reviews/task205-review-zera.md
R7=artifacts/releases/task-205-release-checklist.md
```

### Explanation rendered only if requested

> The E/I benchmark wave is complete. It produced the benchmark, emergence
> records, DEC-028, and released TASK-204 and TASK-205. IDEA-0018 and IDEA-0020
> remain candidates for future work. Validation and both reviews passed. No push
> was performed.

## Conversion process

1. Extract every stable task, decision, idea, insight, message, and artifact ID.
2. Determine the newest verified state for each ID.
3. Remove chronology unless ordering changes current meaning.
4. Keep one current record per ID.
5. Map results to `done`, open work to `next`, blockers to `blocker`, boundaries
   to `risk`, evidence to `refs`, and checks to `verify`.
6. Delete superseded next steps and contradictory status labels.
7. Use full field and state names.
8. Validate syntax, required fields, exact recipients, states, and references.
9. Generate plain English only when a human requests it.

## Token accounting: transport is not context

Compression can reduce different costs, and they must not be confused:

| Design | Reliability | Model-context savings |
| --- | ---: | ---: |
| Model interprets shorthand directly | lower | high |
| Software expands shorthand into full prose inside the prompt | high | low |
| Software uses DSL fields as native controls and loads minimal context | high | high |

If software expands a short code into a long instruction and inserts all of it
into the receiving model's prompt, it has compressed storage and transmission,
not inference context.

Actual model-token savings occur when the orchestrator uses DSL fields outside
the prompt to perform routing, permission checks, artifact selection, output
validation, and selective retrieval. Only irreducible task content should enter
the reasoning context.

Prompt caching may reduce price or latency, but cached instructions still
consume context-window capacity on many systems. Treat caching as an optimization,
not as free information.

A useful accounting model is:

```text
net benefit = tokens avoided
            - retrieval cost
            - expansion cost
            - correction cost
            - rework caused by misunderstanding
```

## Required safeguards

- A canonical MAP/1 schema and typed definition registry.
- A validator for required fields, states, targets, and references.
- Rejection or explicit migration of unknown protocol versions.
- Exact recipient verification.
- Immutable or explicitly versioned shared definitions such as `P17@2`.
- Deterministic expansion rather than model inference of abbreviations.
- A controlled-English `detail` field for meaning that cannot be compressed safely.
- A plain-English renderer for operator requests and audits.
- Tests for malformed records, missing fields, stale updates, contradictions,
  unknown states, and broken references.
- Measurement of model tokens, interpretation accuracy, task success, and
  rework—not character count alone.

## Reliability and expected savings

Readable MAP/1 should be almost as easy for an unfamiliar agent to understand as
ordinary prose while still reducing communication tokens substantially.

Planning estimates:

- Against repetitive prose handoffs: roughly 55–75% fewer tokens.
- Against concise structured English: roughly 15–35% fewer tokens.
- Across routine system communication: roughly 25–45% fewer tokens when DSL
  fields prevent irrelevant coordination material from entering model context.

These are estimates. A pilot should measure actual tokenizer counts and
miscommunication or rework rates.

## Recommended adoption

1. Create a small typed MAP/1 schema for routing, state, ownership, standard
   operations, source policy, output format, and stable references.
2. Implement parsing, validation, a versioned definition registry, selective
   retrieval, and a plain-English renderer.
3. Pilot readable MAP/1 for routine hcom updates. Require agents to summarize a
   sample of received messages to verify interpretation.
4. Measure transport tokens and receiving-model context tokens separately.
5. Compare interpretation accuracy, latency, task success, and rework against
   concise natural language.
6. Expand to handoffs and abbreviated transport only after validation and
   accuracy are consistently reliable.

Use abbreviated DSL only after a parser, validator, registry, and readable
expansion layer exist. Keep novel reasoning in controlled English. Maximum
compression is not the objective; the optimum is the smallest validated context
that lets agents act correctly without guessing.
