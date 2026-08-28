# Model Capability Routing

Use this method to choose the **cheapest available worker proven competent for
the whole execution envelope**. It owns worker capability/cost routing only.

Repository-wide authority comes from [`AGENTS.md`](../AGENTS.md). Task readiness
comes from [AGI_STANDARD.md](AGI_STANDARD.md). Provider-specific behavior belongs
in [PROVIDER_AND_TOOL_GUIDANCE.md](PROVIDER_AND_TOOL_GUIDANCE.md).

## Separate the layers

Do not collapse these into one label:

```text
MODEL      Claude / GPT / Qwen / other
HARNESS    Codex / Claude Code / Aider / goose / Qwen-Agent / custom
RUNTIME    OpenAI / Anthropic / Ollama / vLLM / SGLang / other
```

Competence is a property of the actual combination plus its tools/context, not a
brand name.

## Capability dimensions

Before routing consequential work, evaluate only dimensions the task needs:

1. **Reasoning/integration** — can it preserve constraints, compare alternatives,
   integrate results, and notice contradictions?
2. **Instruction following** — can it respect output boundaries, non-goals,
   stop conditions, schemas, and authority boundaries?
3. **Repository navigation** — can it find the right sources without loading the
   whole repository or confusing context with writable output?
4. **Tool reliability** — can it choose tools, form valid arguments, recognize
   failures, and avoid duplicate side effects?
5. **Context discipline** — can it use the necessary context without drowning in
   irrelevant material?
6. **Structured output** — can it reliably emit required patches/schemas/JSON or
   other machine-consumed forms?
7. **Verification ability** — can it observe/run the proof the task requires?
8. **Cost/speed/locality/privacy** — optimize these only after competence is
   established.

If the worker cannot observe required proof, it must not independently close the
task.

## Worker classes

Classes are task-relative, not permanent model rankings.

### Core

Use for architecture, difficult debugging, broad integration, project planning,
consequential review, or uncertain work requiring wide judgment inside approved
scope.

Give: outcome, relevant context map, constraints/authority, verification target,
and room for safe implementation judgment.

### Bounded implementer

Use for clear work with known inputs/outputs: approved implementation, isolated
refactor, tests, or a small known edit surface.

Give: exact inputs/output paths, acceptance criteria, verification, and non-goals.

### Helper / investigator

Use for focused research, scans, comparison, reproduction, alternate approach,
or review.

Give: one question, bounded search area, required evidence/output, stop condition,
and integration owner. Helpers report; they do not own the parent scope.

### Mechanical / local worker

Use for strongly constrained formatting, repetitive edits, extraction,
classification, deterministic checks, or applying a detailed plan.

Give: exact inputs/output, small context/tool set, examples when useful, and
mechanical verification. Do not assign unresolved product/architecture decisions.

A local model may qualify for stronger work when actual evidence supports it.

## Effort level is a separate axis

Worker class and reasoning effort are different routing choices.

- **Low/medium:** mechanical or narrow, clear, cheaply verifiable work.
- **High:** integration, novel implementation, subtle debugging, most independent
  review.
- **xhigh/max when available:** architecture, difficult authority-boundary
  analysis, or deliberately skeptical second review.

Independent review should generally use equal or greater reasoning effort than
the implementation it reviews.

## Routing rule

```text
1. What capability does this task require?
2. What authority does the task already permit this worker to exercise?
3. What context must the worker understand?
4. What tools and verification must it reliably use?
5. Which available workers have demonstrated competence for that envelope?
6. Among those, which minimizes compute + coordination + retry cost?
```

"Cheapest competent" means cheapest **after competence is established for the
whole envelope**, not the cheapest model that can emit plausible text.

## Context by worker class

Prefer progressive disclosure:

- **Core:** task + relevant roadmap/architecture/decisions + source map + proof.
- **Bounded implementer:** task + exact source paths/examples + required tests.
- **Helper/mechanical:** one bounded question/input set + explicit output schema.

Do not compensate for an unsuitable worker by making the prompt infinitely long.
Route upward.

## Tool gating

Tool capability does not create permission. First inherit the task/roadmap
authority from `AGENTS.md`; then decide whether this worker can safely exercise
it.

For a mutating tool, ask:

```text
Can the worker choose it correctly?
Can it produce valid arguments?
Can it detect a failed call?
Can it avoid duplicate side effects?
Can it remain inside the inherited permission envelope?
```

If not, use a read-only interface, deterministic wrapper, narrower task,
stronger worker, or no tool. Human reauthorization applies only when the proposed
action itself crosses the approved envelope—not because the worker is weak.

## Worker profile

Record observed deployment facts when routing depends on them:

```text
Worker: <id>
Model: <exact model/tag>
Harness: <agent/editor>
Runtime: <provider/server>
Context configured: <tokens>
Tool path/parser: <method>
Structured output tested: YES/NO
File mutation tested: YES/NO
Verification available: <tests/commands>
Proven strengths: <task types>
Known failures: <observed issues>
Maximum safe task class: <bounded description>
Last validated: <date>
```

Profiles are evidence, not marketing claims and not permission grants.

## Fallback and recovery

Route upward/reassign when the worker repeatedly violates boundaries, cannot use
required tools/context, misunderstands acceptance criteria, cannot diagnose
verification failures, or costs more in retries than a stronger worker.

When a run fails, diagnose the layer before changing the prompt:

```text
task shape | context | instruction | model capability | harness | tool/parser |
environment | verification
```

Fix the layer that failed.

## Evidence loop

```text
ASSIGN → OBSERVE → VERIFY → RECORD → UPDATE WORKER PROFILE
```

Worker profiles should evolve from real runs. A routing recommendation never
changes task authority or parent ownership.
