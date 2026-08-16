# Multi-agent coordination

This directory is a lightweight coordination surface for concurrent MAPS_Lean agents.

It is **not canonical task, review, policy, or repository state**. Live GitHub state and accepted MAPS state remain authoritative. These notes exist only to prevent accidental overlap.

## Protocol

Each active agent should maintain its own file under `work/coordination/agents/` using a stable human-readable name, for example:

```text
work/coordination/agents/SWITCHYARD.md
work/coordination/agents/<OTHER-AGENT>.md
```

Before taking or modifying a lane, read the other current agent notes and then re-check live GitHub state.

Each agent note should state, briefly:

- agent name and role;
- branches / PRs actively owned;
- branches / PRs being reviewed or observed only;
- files or stacks that other agents should not modify;
- current blocker / next action;
- timestamp or base/head snapshot where useful.

## Low-contention rule

Agents should normally edit **only their own status file**. Do not rewrite another agent's note. If another lane needs attention, use that agent's PR/issue thread or add the fact to your own note.

A note never transfers branch ownership or grants permission to modify another lane. Unexpected branch movement still means stop writing and re-check ownership.

## Current named lanes

- **SWITCHYARD** — integration / PR-control lane; exact-head synchronization, CI/review gating, safe merges, and independent review support when eligible.

Other active agents should add their own named file rather than sharing SWITCHYARD's file.
