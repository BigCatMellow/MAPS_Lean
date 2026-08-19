# Model Capability Routing

HPOM should route work to the **cheapest worker that is actually competent for
the task under the available context, tools, and verification**.

Model price or headline intelligence alone is not enough. A task can fail
because the worker cannot reliably follow the instruction shape, navigate the
repo, call the required tools, fit the necessary context, or verify the result.

## Separate model, harness, and runtime

Do not collapse these into one label:

```text
MODEL
Claude / GPT / Qwen / other

HARNESS OR AGENT
Codex / Claude Code / Aider / goose / Qwen-Agent / custom

RUNTIME OR PROVIDER
OpenAI / Anthropic / Ollama / vLLM / SGLang / local server / other
```

The same model may behave very differently under different harnesses, tool
parsers, context limits, or permission systems.

## Capability dimensions

Before routing consequential work, judge the worker on the capabilities that
matter for that task.

### 1. Reasoning and integration

Can the worker:

- understand a multi-step problem;
- compare alternatives;
- preserve constraints across several edits;
- integrate results from other workers;
- notice contradictions or missing dependencies?

### 2. Instruction following

Can it reliably respect:

- allowed output paths;
- non-goals;
- explicit stop conditions;
- required output structure;
- authority boundaries?

### 3. Repository navigation

Can the harness/model combination:

- search the repository;
- identify relevant files without loading everything;
- follow links to project instructions;
- distinguish context files from editable outputs?

### 4. Tool reliability

Can it reliably:

- choose the correct tool;
- produce valid tool arguments;
- interpret tool failures;
- avoid repeating side effects;
- respect read/write and destructive-action boundaries?

A model that reasons well but calls tools unreliably is not competent for an
autonomous mutation task.

### 5. Context capacity and context discipline

Record both:

- how much context is available; and
- how much relevant context the worker can use without performance degrading.

Large context capacity is not the same as good context use. Prefer the smallest
sufficient context package.

### 6. Structured-output reliability

Can the worker consistently produce required schemas, JSON, patches, command
arguments, checklists, or other machine-consumed output?

### 7. Verification ability

Can the worker run or inspect the proof required by the task?

Examples:

- tests;
- build output;
- screenshots;
- logs;
- benchmark results;
- database state;
- independent review evidence.

If the worker cannot observe the required proof, it should not independently
close the task.

### 8. Cost, speed, locality, and privacy

After competence is established, optimize for:

- monetary cost;
- latency;
- local hardware availability;
- privacy or data-locality requirements;
- provider limits;
- parallel capacity.

These are routing concerns, not authority.

## Suggested worker classes

These are operational classes, not permanent labels for a brand or model.
Promote or demote a specific worker based on observed performance.

### Core agent

Use for work requiring broad reasoning or integration.

Typical work:

- project planning;
- architecture;
- difficult debugging;
- multi-file implementation;
- integration of parallel results;
- consequential review;
- deciding how to shape uncertain work within operator-approved boundaries.

Instruction style:

```text
clear outcome
relevant context map
constraints and authority
verification target
room for implementation judgment
```

Do not micromanage steps that the worker can safely discover itself.

### Bounded implementer

Use for a clear task with known inputs and outputs.

Typical work:

- implementing an approved design;
- isolated refactor;
- adding tests;
- modifying a small set of known files;
- converting a reviewed plan into code.

Instruction style:

```text
explicit inputs
explicit output paths
specific acceptance criteria
verification command
clear non-goals
```

### Helper / investigator

Use for read-mostly or non-authoritative work.

Typical work:

- repository scan;
- source lookup;
- classification;
- comparison;
- checklist execution;
- alternate approach;
- independent reproduction;
- focused review.

Instruction style:

```text
specific question
bounded search area
required evidence
output format
stop condition
integration owner
```

Helpers report findings; they do not silently change project truth or take
ownership.

### Mechanical / local worker

Use for narrow work where correctness can be strongly constrained and checked.

Typical work:

- formatting;
- repetitive edits;
- data extraction;
- structured classification;
- applying a detailed edit plan;
- running deterministic checks;
- summarizing bounded evidence.

Instruction style should be more explicit:

```text
exact inputs
exact output format
few tools
small context
clear examples when useful
mechanical verification
no product or architecture decisions
```

A local model may qualify for a stronger class on tasks where it has been
proven reliable. "Local" does not automatically mean "weak."

## Effort-level routing

Worker class (which model/harness) and reasoning effort (`low | medium | high
| xhigh | max`, where the harness exposes such a dial) are two different
routing decisions. Do not conflate them: a Core agent can be run at low
effort for a trivial sub-step, and a Bounded implementer can be run at high
effort for a fiddly pattern-match. Choose each axis per task.

### Low / medium effort

Use for mechanical or narrow work with a clear, checkable answer:

- formatting;
- running a fixed command;
- filling a template with facts already supplied;
- simple bounded implementation that follows an established pattern.

### High effort

Use for work that requires integrating multiple sources, catching subtle
inconsistencies, or where a wrong answer is expensive to discover later:

- implementing a novel feature;
- most independent review work.

### xhigh / max

Use for:

- architecture or authority-boundary decisions;
- independent review of something that already had a review pass and needs a
  second, more skeptical look;
- any review whose whole purpose is catching what a first pass at the same
  effort level would also miss.

### Reviewer effort must not be lower than implementer effort

An independent reviewer should generally run at **equal or higher** effort
than the implementer it is reviewing, never lower. Reviewing at the same or
lower effort as the implementation risks reproducing the exact blind spot the
review exists to catch.

## Roadmap and checklist construction and maintenance

Building or updating a *status* claim in a roadmap/checklist document (for
example, marking a phase `DONE`) is Core-agent-class work at **high effort
minimum**, not Helper/investigator or Mechanical/local-worker class. Getting
a status claim right requires synthesizing across code, tests, and PR
history — the same integration demand as consequential review. A false
`DONE` claim is worse than an honest `NOT STARTED`, because future sessions
will trust the doc and skip work that still needs doing.

```text
Every status claim carries a one-line evidence citation
(PR number, file path, or test name)
that a reader could independently check.
Never write an unsupported status.
```

A checklist a session writes about its own completed work is a
self-certification risk — structurally identical to the code-review
self-certification problem this repo already solves with independent
SENTINEL-style review. Therefore: any new or updated roadmap/checklist status
document requires the same independent-review-before-merge treatment as
code. A fresh reviewer spot-checks a sample of the status claims against
real evidence; checking that the file is well-formatted is not sufficient.

Status drift prevention: any PR that changes what a checklist item's status
should be (starts or finishes a phase) must update that phase's status line
in the checklist file in the **same** PR, not a separate follow-up. A status
document that lags the merged state it describes is worse than no status
document.

Keep one canonical status-checklist file per program. Do not let
per-sub-roadmap or per-session duplicate status trackers accumulate — the
sub-roadmap files stay as design-detail references, while a single
consolidated file (for example,
[`work/roadmaps/CAPABILITY_CHECKLIST.md`](../work/roadmaps/CAPABILITY_CHECKLIST.md))
owns the live status view.

## Increase instruction detail as capability decreases

The task stays the same; the execution contract changes.

Example for a capable core worker:

```text
Goal: Fix expired-card checkout failures.
Relevant area: src/payments/.
Preserve existing payment-provider behavior.
Reproduce the reported failure, fix the root cause, add regression coverage,
and run the relevant tests.
Escalate if the fix requires changing checkout product behavior.
```

The same task for a narrower worker may need:

```text
Input files: <named files>
Allowed outputs: <named files>
Failure reproduction: <command>
Expected failing condition: <observable result>
Implementation boundary: <specific component>
Do not change: <paths / behavior>
Required tests: <commands>
Required output: patch + command results
Stop if: reproduction differs, another file must change, or API behavior is
unclear.
```

Do not compensate for a worker that is fundamentally incapable of the task by
writing an infinitely long prompt. Route upward instead.

## Context package by worker class

### Core agent

May receive:

- task;
- project brief / current roadmap section;
- relevant architecture or decisions;
- source-path map;
- tests and verification guidance;
- selected prior evidence.

### Bounded implementer

Prefer:

- task;
- exact relevant source files or paths;
- one or two examples/patterns;
- required tests;
- necessary local conventions.

### Helper / mechanical worker

Prefer:

- one bounded question;
- small input set;
- explicit output schema;
- minimal tools;
- no unrelated project history.

## Tool gating

Do not grant a worker a mutating tool merely because it supports tool calling.

For each worker/tool combination, verify:

```text
Can it choose the tool correctly?
Can it produce valid arguments?
Can it recognize a failed call?
Can it avoid duplicate side effects?
Can it obey authority and confirmation boundaries?
```

If not, use one of:

- read-only tool access;
- a deterministic wrapper;
- human/core-agent approval before execution;
- a stronger worker;
- no tool access.

## Local-model profile

For a local worker, record the actual deployment rather than only the model
family:

```markdown
# Worker profile: <name>

- Model: <exact model and size/tag>
- Harness: <goose | Aider | Qwen-Agent | custom | other>
- Runtime: <Ollama | vLLM | SGLang | other>
- Context configured: <tokens>
- Tool-calling path: <native parser / harness parser / none>
- Structured output tested: `YES | NO`
- File editing tested: `YES | NO`
- Shell/tool use tested: `YES | NO`
- Verification available: <tests / commands / none>
- Proven strengths: <task types>
- Known failure modes: <observed issues>
- Maximum authority: <read-only / bounded edits / other>
- Last validated: <date>
```

This profile should be based on actual runs, not marketing claims.

## Qwen-specific deployment note

Qwen tool behavior depends on the model and serving path. Qwen's current
documentation distinguishes native model-server tool parsers from Qwen-Agent's
built-in parser, and specifically recommends a native parser for Qwen3-Coder
under compatible vLLM/SGLang deployments.

Therefore:

```text
Qwen model name alone != verified tool worker
```

Record and test the exact `model + runtime + harness + parser` combination.

## Ollama-specific deployment note

Ollama currently recommends at least 64K context for agent/coding workloads,
but larger context uses more memory. Configure context deliberately and verify
the actual runtime state.

Do not solve context problems only by increasing `num_ctx`. First remove
irrelevant context and use progressive disclosure.

## Aider-specific routing note

Aider is strongest when the edit surface is already bounded. Its own guidance
recommends adding only relevant files, planning complex changes first, and
breaking work into bite-sized steps.

A useful pattern is:

```text
strong architect/core agent → reviewed change plan → Aider/editor worker → tests
```

when a cheaper/local editor can reliably apply the plan.

## goose-specific routing note

Goose can host different providers and spawn subagents, so the goose session is
not itself a capability class. Route based on the model, tools, recipe, and
permissions configured for that session.

## HPOM routing rule

Use this order:

```text
1. What capability does the task require?
2. What authority may the worker hold?
3. What context must the worker understand?
4. What tools and verification must it reliably use?
5. Which available workers have proven competence for that envelope?
6. Among those workers, which has the lowest coordination + compute cost?
```

"Cheapest competent worker" means cheapest after competence is proven for the
**whole execution envelope**, not cheapest model that can generate plausible
text.

## Fallback and escalation

Route upward when:

- the worker repeatedly violates boundaries;
- tool arguments are unreliable;
- required context cannot fit or cannot be navigated effectively;
- the worker cannot understand the acceptance criteria;
- verification repeatedly fails for reasons the worker cannot diagnose;
- integration crosses several domains;
- a consequential decision appears;
- repeated retries cost more than using a stronger worker.

Do not keep retrying an unsuitable model just because it is cheaper per token.

## Evaluation loop

Worker profiles should evolve from evidence:

```text
ASSIGN → OBSERVE → VERIFY → RECORD FAILURE/SUCCESS → UPDATE ROUTING PROFILE
```

When a run fails, diagnose the layer:

- bad task shape;
- missing context;
- bad instruction;
- model capability;
- harness limitation;
- tool/parser failure;
- environment failure;
- verification gap.

Fix the layer that actually failed.

## Sources

Checked 2026-08-14:

- OpenAI Codex guidance:
  - https://openai.com/business/guides-and-resources/how-openai-uses-codex/
  - https://openai.com/index/harness-engineering/
- Anthropic Claude Code:
  - https://code.claude.com/docs/en/best-practices
  - https://code.claude.com/docs/en/how-claude-code-works
- Aider:
  - https://aider.chat/docs/usage/tips.html
  - https://aider.chat/docs/usage/modes.html
- goose:
  - https://block.github.io/goose/
  - https://goose-docs.ai/blog/2026/02/07/context-engineering/
- Ollama:
  - https://docs.ollama.com/context-length
  - https://docs.ollama.com/modelfile
- Qwen:
  - https://github.com/QwenLM/Qwen-Agent
  - https://github.com/QwenLM/Qwen-Agent/blob/main/qwen-agent-docs/website/content/en/guide/get_started/quickstart.md
