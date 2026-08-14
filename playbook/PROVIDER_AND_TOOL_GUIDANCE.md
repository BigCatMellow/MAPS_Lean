# Provider and Tool Guidance

MAPS is provider-neutral, but providers and harnesses expose different strengths,
context behavior, planning modes, tool systems, and failure modes. Use their
native strengths without making MAPS depend on any one of them.

This document separates **model**, **agent/harness**, and **runtime** because they
are not the same thing.

- **Claude / Codex:** agent-capable coding systems backed by frontier models.
- **Aider / goose:** harnesses that organize models, files, tools, and workflows.
- **Ollama:** local model runtime and serving layer.
- **Qwen:** model family; Qwen-Agent is an agent framework around Qwen models.

Vendor behavior changes. Treat this as routing guidance, not an eternal product
specification.

## OpenAI Codex

### What OpenAI recommends

For larger changes:

1. Plan before implementation.
2. Scope work like a good GitHub issue: name the component, relevant paths,
   expected behavior, examples, and useful documentation.
3. Give Codex a configured development environment and reliable tests.
4. Keep persistent repository guidance in `AGENTS.md`, but do not turn it into
   a giant manual.
5. Keep durable plans and repository knowledge in versioned files so the agent
   can retrieve the right context as needed.
6. Give the agent feedback loops: tests, logs, metrics, screenshots, or other
   evidence it can inspect itself.

OpenAI's own agent-first engineering report describes a shift from one large
`AGENTS.md` to a short navigation map plus structured repository documentation.
The reason is simple: context is scarce, monolithic instructions become stale,
and agents need progressive disclosure.

### MAPS translation

Use Codex as a strong core worker for:

- codebase exploration and implementation planning;
- multi-file implementation;
- integration work;
- debugging where the agent can run the system and inspect evidence;
- bounded code review;
- long-running work when the repository contains durable state and tests.

Prefer:

```text
Task + relevant project context + named source paths + acceptance criteria +
verification commands
```

over copying large project histories into the prompt.

For substantial work, route:

```text
EXPLORE / ASK → PLAN → IMPLEMENT → VERIFY → REVIEW
```

Small obvious edits may skip formal planning.

### Sources

- https://openai.com/business/guides-and-resources/how-openai-uses-codex/
- https://openai.com/index/harness-engineering/
- https://openai.com/index/introducing-codex/
- https://openai.com/index/unrolling-the-codex-agent-loop/

## Anthropic Claude Code

### What Anthropic recommends

Anthropic's current best-practices guide emphasizes:

1. **Give Claude a way to verify its work.** Tests, screenshots, expected output,
   lint commands, or other feedback are described as especially high leverage.
2. **Explore first, then plan, then code** for complex work.
3. Be specific about the scenario, constraints, files, and testing preferences
   when those details matter.
4. Keep `CLAUDE.md` short and human-readable; use it for stable project
   conventions, commands, and workflow rules.
5. Manage context aggressively. Narrow investigations or move exploration into
   subagents when broad reading would pollute the main working context.
6. Use subagents for bounded investigation or parallel work rather than making
   one session absorb everything.
7. Use permission modes appropriate to the risk; bypass-style modes belong only
   in genuinely isolated environments.

Anthropic describes Claude's basic agent loop as gathering context, taking
an action, and verifying the result.

### MAPS translation

Claude is a strong core worker for:

- exploration and architecture understanding;
- planning and critique;
- implementation;
- review and failure analysis;
- UI work when screenshots or browser verification are available;
- independent investigation through subagents.

For complex work, prefer:

```text
EXPLORE → PLAN → IMPLEMENT → VERIFY → COMMIT / HANDOFF
```

The MAPS task should tell Claude what success means and expose a verification
mechanism whenever practical. Do not replace bounded delegation with detailed
micromanagement if Claude can safely discover implementation details itself.

### Sources

- https://code.claude.com/docs/en/best-practices
- https://code.claude.com/docs/en/how-claude-code-works
- https://code.claude.com/docs/en/common-workflows
- https://code.claude.com/docs/en/permissions

## Aider

### What Aider recommends

Aider's documentation repeatedly emphasizes selective context:

1. Add the files that actually need editing.
2. Do not flood the chat with irrelevant files; Aider's repo map supplies
   lightweight awareness of the rest of the repository.
3. Break large goals into bite-sized steps.
4. Use `/ask` to discuss a plan before complex changes, then switch to code.
5. Feed failing commands, tests, and error output back to the model.
6. Keep standing coding conventions in a small Markdown file loaded read-only.
7. Provide current documentation when library/API details may be newer than the
   model's training data.

Aider also supports architect/editor separation, where one model proposes the
solution and another applies edits. This can be useful when a smaller model is
adequate for mechanical file editing but not for high-level reasoning.

### MAPS translation

Use Aider when the task is already shaped and the relevant edit surface is
known.

Good fit:

- one or a few files;
- bounded code changes;
- applying an already-reviewed plan;
- test/fix loops;
- local pair-programming;
- strong-model architect + cheaper editor workflows.

Give Aider less, better context rather than the entire project brain.

### Sources

- https://aider.chat/docs/usage/tips.html
- https://aider.chat/docs/usage/modes.html
- https://aider.chat/docs/usage/conventions.html
- https://aider.chat/docs/usage.html

## goose

### What goose recommends or enables

Goose is a general agent harness. Its current documentation emphasizes:

- durable context over one-shot prompting;
- tools and data through MCP extensions;
- reusable workflows through Recipes;
- independent subagents for parallel work;
- provider neutrality across hosted and local models.

The goose context-engineering guidance recommends making the finish line,
non-negotiables, and persistent context explicit, then storing important
context somewhere that survives the chat session.

### MAPS translation

Goose is a natural execution host for MAPS methods because it is already built
around provider-neutral models, MCP tools, recipes, and subagents.

Potential mapping:

```text
MAPS playbook method → goose Recipe
MAPS bounded helper → goose subagent
MAPS tool adapter → MCP extension
MAPS durable context → project files / hints / memory
```

Do not make goose's recipe format the source of truth. Keep the provider-neutral
method in MAPS Markdown; recipes are executable adapters.

### Sources

- https://block.github.io/goose/
- https://goose-docs.ai/blog/2026/02/07/context-engineering/

## Ollama

Ollama is a runtime, not an agent architecture. Agent quality depends both on
which model is served and how the harness uses it.

### What Ollama documents

- Context length is configurable and consumes more memory as it grows.
- Ollama recommends at least 64K context for large-context workloads such as
  agents and coding tools.
- `Modelfile` supports persistent `SYSTEM` instructions, prompt templates, and
  runtime parameters such as `num_ctx`.
- Model runtime configuration should be checked rather than assumed.

### MAPS translation

For a local worker, record at least:

```text
model name / tag
available context
actual context configured
GPU/CPU offload state when performance matters
tool-calling support
harness used
structured-output reliability
known task strengths / weaknesses
```

A large context window is capacity, not permission to fill it. Continue to use
progressive disclosure and selective context.

### Sources

- https://docs.ollama.com/context-length
- https://docs.ollama.com/modelfile

## Qwen and Qwen-Agent

### What Qwen documents

Qwen-Agent is explicitly built around Qwen's instruction following, tool use,
planning, memory, MCP, and code-interpreter capabilities.

Tool configuration matters. Qwen's current quickstart distinguishes between
model-server-native tool parsing and Qwen-Agent's built-in parsing. For
Qwen3-Coder, the documentation recommends the model server's native tool-call
parser when deployed through compatible servers. Other Qwen variants may use
Qwen-Agent's built-in parser instead.

Qwen examples also warn that tool-call arguments may not always be valid JSON;
robust harnesses must validate and handle failures.

### MAPS translation

Do not treat "Qwen supports tools" as enough information. A local profile must
state the exact model and serving path.

Example:

```text
Model: Qwen3-Coder-<size>
Runtime: Ollama / vLLM / SGLang / other
Harness: goose / Aider / Qwen-Agent / custom
Tool parser: <configured method>
Context: <actual configured tokens>
Tools verified: YES / NO
Structured output verified: YES / NO
```

Route consequential tool use only after the specific model+harness+parser
combination has been tested.

### Sources

- https://github.com/QwenLM/Qwen-Agent
- https://github.com/QwenLM/Qwen-Agent/blob/main/qwen-agent-docs/website/content/en/guide/get_started/quickstart.md
- https://github.com/QwenLM/Qwen3/blob/main/docs/source/framework/function_call.md

## Shared guidance across the tools

Despite different products, the recurring advice is similar:

```text
1. Define the result clearly.
2. Inspect before changing complex systems.
3. Plan difficult work before implementation.
4. Give relevant context, not maximum context.
5. Keep persistent project knowledge outside transient chat.
6. Use focused tools with clear operational boundaries.
7. Break large work into bounded pieces.
8. Give the agent an objective way to verify itself.
9. Use parallel agents for independent work, not uncontrolled duplication.
10. Correct the environment or workflow when failures repeat; do not only
    rewrite the prompt and hope.
```

MAPS should preserve those principles while keeping vendor-specific commands,
file names, and UI details behind adapters or provider notes.

## Maintenance rule

This page was checked against vendor documentation on **2026-08-14**.
Re-verify vendor-specific claims before building long-lived automation around a
particular command, permission mode, parser flag, context default, or product
feature.
