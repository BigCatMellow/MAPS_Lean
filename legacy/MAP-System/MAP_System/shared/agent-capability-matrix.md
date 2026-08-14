<!-- hpom: file: shared/agent-capability-matrix.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-08-10 -->
<!-- hpom: verified_against: TASK-267 model-fit directive, TASK-320 Antigravity retirement, and hcom roster lookup rule -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Agent Capability Matrix

Status: working HPOM routing reference
Owner: command-center
Related: `shared/hpom.md`, `notes/local-model-helper-guide.md`

## Rule

Assign work by fit, not by availability.

If a worker cannot produce a reliable output for the task shape, do not use it
just to keep it busy.

## Core Agents

| Worker | Best At | Good Outputs | Avoid | Default Authority |
|---|---|---|---|---|
| Codex | Code edits, scripts, validators, SQLite, CLI tools, tests, precise file changes | implementation, test artifact, bug fix, task shaping with concrete files | approving its own implementation, vague product decisions, broad unsupervised refactors | owns implementation |
| Claude | Review, architecture critique, synthesis, task shaping, prose-heavy documentation, risk analysis | review findings, architecture note, acceptance criteria, operator summary | approving its own deliverable, hidden implementation without task ownership | owns review/planning |

## Standby / Manual Agents

| Worker | Best At | Use When | Avoid | Current Status |
|---|---|---|---|---|
| Gemini | alternate brainstorming, broad summaries, second-pass ideation when manually prompted | operator explicitly activates it for bounded support | relying on passive hcom awareness or final authority | standby/manual |

Antigravity was retired from active Command Center routing by operator decision
in TASK-320 because its token limit is not useful for this workload. Historical
records remain evidence, but new plans and task assignments must not depend on
it.

## Local Models

| Worker | Best At | Good Outputs | Avoid | Authority |
|---|---|---|---|---|
| `qwen3.5:4b` | one visible, bounded JSON advisory packet | advisory recommendation/draft with core review | task ownership, file writes, coordination, approval, release, authority | draft-only; narrow drill only |
| `qwen2.5-coder:1.5b` | installed only | none until a bounded drill passes | any task assignment or reliability claim | not assignable |
| `llama3.2:1b` | disposable rough hint | none; direct-use output was not accepted | structured output or final work | not assignable |
| Pi / current visible local model | bounded probes, drafts, and experiments only | exploratory observation with a durable run record | MAP operational work, task/review/handoff/release/routing, capacity decisions, or durable canonical mutation | exploratory-only; no operational authority |

## Helper Model Tiers

| Tier | Best Fit | Escalation Rule |
|---|---|---|
| Haiku | explicit criteria, named-file scan, summary, fixture/checklist pass | default visible helper tier |
| Sonnet | non-obvious debugging, cross-file reasoning, careful review or plan | different core agent approves the bounded higher-tier request |
| Opus | unusually hard architecture or subtle security/safety tradeoffs | different core agent approves and the note explains why Sonnet is insufficient |

The core agent is the accountable owner/integrator, not necessarily the worker
for every subproblem. Apply this table before defaulting work to the currently
open Codex or Claude session.

## Tools

| Tool | Best At | Preconditions | Avoid |
|---|---|---|---|
| Aider | narrow supervised edits using local coding model | Git baseline understood, explicit task id, explicit output paths, helper note path | broad cleanup, unclear scope, final authority |
| hcom | visible agent orchestration and messaging | use `--terminal wezterm-tab` for spawned agents/helpers unless explicitly told otherwise | treating messages as durable memory without file records |
| LangGraph runner | next-route recommendation and approval interrupts | task graph valid, file/SQLite state synced | canonical memory or autonomous helper spawning |

## Assignment Checklist

Use a local assistant when all are true:

- the task can be reduced to summary, classification, checklist, draft, or
  diff suggestion;
- the output can be reviewed by Codex or Claude before changing MAP state;
- input paths are bounded;
- no human intent, approval, or architecture decision is required.

Use a temporary hcom helper when all are true:

- the scope is bounded;
- parallelism saves real time;
- a core owner will integrate or reject the result;
- a durable helper note exists;
- the session is visible or command-center-reachable.

Use a core agent directly when:

- implementation changes MAP behavior;
- the task changes task state, claims, approval gates, or helper policy;
- the work requires judgment about system design;
- the result will be treated as final after independent review.

Ask command-center when:

- the task intent cannot be made pass/fail;
- HPOM/MAP boundaries are changing;
- helper use would require hidden or expensive subscription work;
- a preference tradeoff matters more than a technical check.

## Observed Health

- Live session names are intentionally omitted because the roster changes
  faster than this canonical capability reference. Run `hcom list` immediately
  before assigning or messaging a live worker.
- Durable `agents/status.json` still contains historical agent ids; use live
  `hcom list` before assigning real-time work.
- Local inventory was checked 2026-07-18. `qwen3.5:4b` is the sole narrowly
  drilled advisory lane; installed is not equivalent to assignable.
- Pi's operator posture changed on 2026-07-21 from paused to exploratory-only;
  its failed no-write drill still forbids operational authority and canonical
  file mutation.
