# MAPS conversation context

Status: `HISTORICAL CONTEXT — NOT ACTIVE AUTHORITY`

Purpose: preserve the reasoning, chronology, operator preferences, rejected directions, design transitions, and plain-language explanations that led to the current MAPS Lean roadmaps and implementation work.

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

### `plain-language-maps-improvements.md`

Non-technical explanation of the major proposed improvements from the Prime/external agent-system research: common worker controls, deterministic hooks, Skills, Skill trust, environment recipes, better AI-facing tools, immediate validation, context budgeting, complete run history, review-to-revision binding, worktree isolation, helper continuity, no-progress detection, Capability Packs, memory trust levels, adversarial agent security tests, real-world learning, and the prohibition on self-authorizing changes.

It preserves the central plain-language design conclusion:

> Build an extremely good operating system around ordinary capable AI agents.

## Related material

- `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` — **top-level capability planning orientation**
- `work/roadmaps/README.md`
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
3. work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md
4. work/context/agent-handoff-current-state.md
5. work/context/plain-language-maps-improvements.md
6. work/context/design-decisions-and-rationale.md
7. work/context/conversation-history-2026-08-15.md
8. relevant detailed roadmap/research file
9. implementation files/tests
```

The master roadmap is the top-level planning orientation, but remains below active authority. The context files are deliberately below `AGENTS.md` and canonical task authority.
