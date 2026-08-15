# MAPS conversation context

Status: `HISTORICAL CONTEXT — NOT ACTIVE AUTHORITY`

Purpose: preserve the reasoning, chronology, operator preferences, rejected directions, and design transitions that led to the current MAPS Lean roadmaps and implementation work.

These files exist so a future agent can understand **why the repository looks the way it does**, not merely what the current files contain.

## Authority warning

These notes are retrospective conversation-derived context.

They may explain:

- why a mechanism was chosen;
- why another mechanism was rejected;
- what uncertainty existed at the time;
- what the operator emphasized;
- how research changed the roadmap;
- what remains intentionally deferred.

They do **not** override:

- `AGENTS.md`;
- canonical SQLite task/policy/review state;
- active runtime code;
- accepted task requirements;
- merged implementation;
- current repository instructions.

If these notes disagree with current authoritative state, the current authoritative state wins.

## Files

### `conversation-history-2026-08-15.md`

Chronological narrative of the MAPS/Prime-agent discussion and implementation evolution: legacy archaeology, Lean simplification, Prime capability recovery, external research, roadmap expansion, and the transition from “more agents” toward better harness mechanics.

### `design-decisions-and-rationale.md`

Decision ledger explaining major design choices, alternatives rejected, promotion triggers, and the reasoning behind important invariants.

### `agent-handoff-current-state.md`

Compact onboarding/handoff for a new agent entering the project now. It points to the canonical files, describes the current draft PR state, summarizes what is already implemented, and lists the next planning/implementation fronts.

## Related material

- `work/roadmaps/prime-agent-capability-roadmap.md`
- `work/research/agent-harness-patterns-scan-2026-08.md`
- `work/roadmaps/agent-harness-capabilities/README.md`
- `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`
- `migration/FUTURE_IDEAS_BACKLOG.md`
- `work/review_queue/`

## Reading order for a new agent

```text
1. AGENTS.md
2. current task / canonical task state
3. work/context/agent-handoff-current-state.md
4. work/context/design-decisions-and-rationale.md
5. work/context/conversation-history-2026-08-15.md
6. relevant roadmap/research file
7. implementation files/tests
```

The context files are deliberately below `AGENTS.md` and task authority in that order.
