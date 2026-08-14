# Helper Agent Guide

Temporary helper agents are useful for bounded parallel work. They should not
become unmanaged background workers.

## When To Use A Helper

Use a helper for:

- independent review;
- focused research;
- repetitive inspection across many files;
- implementation support with clear ownership;
- summarizing a large but bounded context set.

Do not use a helper just to keep agents busy.

Local Ollama models and Aider may be used as helper capabilities for low-risk
support work. See `local-model-helper-guide.md`.

Use local assistants to reduce paid-model load, not to replace core-agent
ownership. Expected outputs are summaries, classifications, checklist results,
drafts, recommendations, or diff suggestions.

### Review-Conflict Default

When a submitted task needs review and the obvious live reviewer has a
no-self-review conflict, the owning agent should route to a visible helper
without asking the operator, provided the review is routine and bounded.

Default sequence:

1. Record the conflict in `events/events.jsonl` or the task timeline.
2. Create `inbox/helpers/helper-review-task-NNN.md` with owner, scope, input
   paths, conflict reason, expected review artifact, and stop condition.
3. Spawn a visible helper:

   ```bash
   hcom 1 claude --tag helper-review-task-NNN --terminal wezterm-tab --model haiku
   ```

4. Send the helper a bounded review packet.
5. Validate the helper's review artifact before release.
6. Stop or retire the helper after its findings are integrated.

Ask the operator only when helper spawning is unavailable, the task requires a
human decision, or the review crosses privacy, destructive-action, security, or
scope boundaries.

## Broadcast Ownership (Core Agents, Not Helpers)

This guide is about spawning and running helpers. A related but separate
problem is two *core* agents (Claude, Codex, or their lab sessions) both
responding to the same operator broadcast — that is not a helper-routing
question and is covered in `AGENTS.md` under "Broadcast Coordinator
Convention": the first agent to act announces its claimed scope over hcom
before starting, instead of both agents independently duplicating the same
audit or fix.

## Required Setup

Every helper needs:

- a stable tag, such as `helper-review-task-048`;
- a specific scope;
- an owning core agent;
- command-center-managed terminal mode;
- a durable note in `inbox/helpers/`.

Visible terminal tabs are the default. Headless `hcom` is allowed only when the
AI Command Center remains the operator interface for inspecting screen state,
sending input, approving prompts, and stopping the helper.

Do not run assistants or helper agents in an unreachable background mode.

Example:

```bash
hcom 1 claude --tag helper-review-task-048 --terminal wezterm-tab
```

## Claude Helper Model And Permission Defaults

Claude helpers default to:

- visible terminal: `--terminal wezterm-tab`;
- permission mode: auto mode, currently persisted in hcom config as
  `--permission-mode auto`;
- model tier: Sonnet, currently persisted in hcom config as `--model sonnet`
  (DEC-035, 2026-07-28; see `shared/decisions.md`).

Haiku is still available and still the right choice for narrowly-scoped,
low-friction work — spawn it explicitly with `--model haiku` when the rubric
below says so. It is a deliberate per-spawn override now, not the default,
and choosing it needs no escalation (only going *above* the default to Opus
does — see "Requesting A Higher Claude Tier" below).

Use the explicit spawn shape in examples anyway. Explicit flags make helper
notes and transcripts readable even if local hcom config changes later.

### Why The Default Changed (DEC-035)

TASK-194 originally set the default to Haiku as a resource-management
measure. In practice it cost operator attention instead: every spawned agent
blocked on manual permission prompts, and those prompts fell to the operator,
because **`--permission-mode auto` had never actually been passed at spawn
time** — every agent, Sonnet included, defaulted to manual approval. An
earlier working note concluded "Haiku sessions cannot be set to auto mode";
nothing in `claude --help` supports a model-tier restriction on
`--permission-mode auto`, so that conclusion most likely came from the
missing flag, not a real Haiku-specific limitation.

This is not yet fully closed: the missing flag is the more likely
explanation, but it has not been positively ruled out. **What would prove a
real Haiku-specific restriction exists:** a Haiku spawn that still blocks on
approval prompts *after* `--permission-mode auto` is correctly passed at
spawn time. If that is ever observed, this note and DEC-035 should be
corrected — do not silently re-inherit "Haiku can't use auto mode" as fact
without that evidence, and do not silently drop the possibility either.

Allowed cases:

- read-only review;
- bounded file inspection;
- local syntax or validator commands already inside the task scope;
- draft-only findings that the core owner will integrate.

Do not use an auto-approval mode for work that crosses a human approval,
privacy/scope, security, destructive-action, external-service, broad Git, or
publication boundary. In those cases the helper should remain interruptible and
the owning core agent should escalate through the normal operator request
format.

Record the chosen permission mode, verification method, and stop condition in
the helper note when the setting materially affects whether the helper can
finish without waiting on the operator.

### Claude Model Tier Rubric

The default is Sonnet with auto permission mode (DEC-035), chosen to remove
permission-prompt babysitting for the operator without giving up bounded,
cheap helper work — that work should still deliberately choose Haiku via
`--model haiku`. The default is not a hard cap in either direction.

| Tier | Use when | Avoid when |
|---|---|---|
| Haiku | The helper is summarizing, checking explicit criteria, scanning named files, drafting a review packet, classifying records, or running a simple bounded inspection. | The task needs deep cross-file reasoning, ambiguous design judgment, or high-risk correctness. |
| Sonnet | The helper must reason across several files, debug a non-obvious failure, review complex implementation behavior, compare competing designs, or produce a careful plan where missing a nuance would waste core-agent time. | The work is simple extraction, mechanical formatting, or a tiny checklist Haiku can handle. |
| Opus | The helper request involves unusually hard architecture, subtle safety/security tradeoffs, high ambiguity, or a prior Sonnet/Haiku attempt produced inadequate reasoning with evidence. | The request is only "use the best model" without concrete difficulty or risk evidence. |

Reviewers should approve higher tiers generously when the request explains the
complexity and the expected bounded use. Resource management means matching
model strength to the work, not always choosing the lowest or highest tier.

### Requesting A Higher Claude Tier

A Claude helper may use Opus only after a written escalation request is
reviewed by a different core agent. Record the request in the helper note,
task event, or hcom thread before spawning the Opus helper. This process is
unchanged by DEC-035 — it moved only the default (Haiku → Sonnet), not this
escalation gate, which still governs going above the default. Choosing Haiku,
below the default, needs no escalation — spawn it directly per the rubric
above.

Required request format:

```text
Issue: helper scope and why Sonnet is likely insufficient.
Options: Sonnet default, Haiku, Opus, or no helper.
Recommendation: requested tier and bounded duration/scope.
Needed: approval from a non-requesting core agent.
```

The reviewer decides the tier using the rubric above. They may approve the
requested tier, choose a higher tier if the reasoning shows the work needs it,
choose a lower tier if the work is clearly bounded enough, or reject helper use
when the task should stay with a core agent or operator.

The approved helper note must include:

- requested model tier and approved model tier;
- approving core agent;
- reasoning summary;
- scope and stop condition;
- whether any lower-tier attempt was made or intentionally skipped.

The approved tier goes in the `model:` field of the helper-note metadata
contract in `AGENTS.md` ("Helper-note metadata contract"). Put it there, not
only in prose: the graph reads that contract, and reports any active helper note
with no `model` line as `helpers_missing_model_tier`. The remaining items above
belong in the note body.

This requirement predates the field. Until TASK-269 the contract had no place to
record a tier, so 76 of 82 helper notes carried none and the rubric could not be
audited — a rule with nowhere to write its answer is not enforceable.

## Helper Note

Create or update:

```text
inbox/helpers/helper-review-task-048.md
```

Include:

- helper tag;
- tool or provider;
- owner;
- task or question;
- input paths;
- findings;
- current status;
- stop condition.

## Stop Conditions

Stop or retire a helper when:

- its assigned work is complete;
- its findings have been integrated or rejected;
- it is stale;
- another helper duplicates the same scope;
- it is waiting indefinitely on unavailable context.

## Accountability

The owning core agent remains responsible for final integration, review routing,
and cleanup. Helpers do not approve final deliverables.

Local assistants do not claim completion, approve reviews, or make final
architecture decisions.

## Communication

Helpers should report findings to their owning core agent by default.

Direct helper-to-core communication is allowed for bounded questions. For
example, a Claude-owned helper may ask Codex a narrow implementation question
directly, but it must record the exchange and summarize it back to Claude.

Route communication through the owning core agent when the request changes task
scope, ownership, priority, implementation responsibility, or approval state.

See `communication-guide.md` for the full routing rules.
