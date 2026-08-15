# Next-agent continuation prompt — 2026-08-15

Use the following prompt to resume MAPS Lean development after a context reset.

---

You are continuing active development of `BigCatMellow/MAPS_Lean`.

Do **not** start by redesigning the system or asking me to restate prior work. Recover the repository state first.

## First actions

1. Read root `AGENTS.md` and obey it.
2. Read `work/notes/2026-08-15-active-development-handoff.md` from branch `agent/agentic-security-baseline-wave1`.
3. Inspect current `main` and current PR states before trusting old branch/head numbers. At the handoff moment, `main` was `086e066f723d793273441dd52b500e62ac981deb`.
4. Inspect PR #34, branch `agent/frozen-regression-case-wave2`, plus:
   - `work/tasks/frozen-regression-case-wave2.md`
   - `work/tasks/portable-run-record-wave2.md`
   - `work/roadmaps/agent-harness-capabilities/05-learning-and-evaluation.md`
   - `work/roadmaps/prime-agent-capability-roadmap.md`
5. Verify whether any upstream independent review changed the contracts before stacking more work.

## Exact stopping point

The previous agent finished **PR #34 — frozen regression case v1**.

At handoff:

- PR #34 was open and draft;
- base: `agent/portable-run-record-wave2` / PR #33;
- implementation head: `3baa0eabb42d6ab89e2d681fda1a297f994084ce`;
- task-validation head: `f803cd24e5acbd3630075b3f316535ba50540b0b`;
- implementation CI `31899393298` passed;
- current-head CI `31899450620` also passed;
- task state is `READY_FOR_REVIEW`;
- independent review/merge remains outstanding.

Do **not** self-approve, mark ready, or merge it merely because CI passed.

## Next recommended implementation

If PR #34 remains contract-compatible and no upstream review requires rework, create a stacked branch:

`agent/regression-evaluator-wave2`

from:

`agent/frozen-regression-case-wave2`

Then shape a new task record before coding.

Build **comparative evaluation/reporting v1 over frozen regression cases**.

Preferred v1 behavior:

- validate frozen case IDs/content hashes before use;
- accept candidate identity/version/config hash as descriptive evidence;
- accept externally produced expected-property results only; do not execute models/providers/tasks in the evaluator;
- property result states should be explicit, e.g. `PASS`, `FAIL`, `UNKNOWN`, `NOT_RUN`;
- missing required property results must be reported as incomplete, never treated as pass;
- aggregate per-case and corpus-level pass/fail/unknown/incomplete metrics;
- support baseline-vs-candidate comparison only when both result sets reference the exact same frozen case IDs;
- mechanically identify `improved`, `regressed`, `unchanged`, and `incomplete` from supplied results;
- preserve incident category/tags for slicing;
- include cost/latency only when explicitly measured and supplied; never guess;
- deterministic report identity/hash;
- read-only / no canonical MAPS writes;
- no automatic routing/harness/policy changes;
- no automatic promotion/self-modification.

Required promotion shape remains:

`frozen cases → candidate results → comparative report → proposal → independent review/operator gate where required → promotion`

Never:

`better score → automatic production change`

## Invariants you must preserve

- one authority per fact;
- capability is not authority;
- provider/session liveness is not task truth;
- Hooks may deny/narrow, never grant missing authority;
- review must bind exact/fresh evidence for consequential actions;
- environment compatibility is evidence, not recovery authority;
- `CLEAR` Skill scan is not Skill approval;
- Run Record/frozen case remain explicitly partial where source coverage is incomplete;
- frozen/eval success cannot self-authorize promotion;
- do not create a second task/session/review authority store;
- do not add permanent agents/daemons/watchers without demonstrated need;
- do not revive legacy lexical retrieval or persona-heavy agent bureaucracy.

## Working style

Continue implementation while upstream drafts await review when dependencies are explicit and review results are not required for the next step. Use stacked draft PRs. Run focused tests plus full Runtime stack CI. Record durable task/checkpoint notes as context grows. If a consequential unknown remains, inspect evidence or stop/escalate rather than guess.

---
