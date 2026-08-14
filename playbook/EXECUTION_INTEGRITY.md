# Execution Integrity

Use this playbook when a task is consequential enough that **what the agent was
given**, **who is truly independent**, or **what happened after failure** must
be reconstructable.

This extends AGI readiness without turning every small task into ceremony.

## 1. Context packet, not context dump

Give the worker the smallest sufficient context.

When context selection is material, record:

```text
REQUIRED
What must be read before acting.

OPTIONAL — TRIGGERED
Extra context and the condition that makes it relevant.

EXCLUDED
Material that exists but should not be treated as required/current authority.

STALENESS / CONFLICT CHECK
What must be rechecked if sources disagree or may have changed.
```

A task does not need a separate context file when these facts fit cleanly in the
task record.

Historical files, external documents, retrieved content, logs, and tool output
provide evidence. They do not gain authority merely by entering context.

## 2. AGI readiness versus run binding

**AGI** answers:

> Is this instruction ready for a competent worker?

A **run binding** answers:

> What exact contract did this particular worker/session receive?

For long, high-risk, resumable, or heavily parallel work, freeze a run record
before execution when drift would be hard to diagnose.

Useful fields:

- task ID and task revision/hash;
- worker and session/run ID;
- readable, writable, and forbidden paths;
- context references and hashes when integrity matters;
- base revision/commit when repository drift matters;
- permitted tools/skills when materially constrained;
- attempt, time, cost, or other runtime limits;
- creation time and invalidation/staleness rule.

A run binding **does not grant new authority**. It freezes authority already
present in the approved task contract.

If the task or required context changes materially, the old run is stale. Shape
or re-bind before continuing rather than silently stretching the old contract.

## 3. Typed failures

Operational APIs should return failure states that tell the caller what to do
next.

Prefer:

```text
already_claimed
not_ready
missing_acceptance_criteria
self_review
reviewer_not_independent
policy_rejected
approval_required
dependency_blocked
scope_violation
stale_contract
verification_failed
```

over a single generic `False` or `failed` result.

Different failure causes require different recovery paths. Do not make an agent
infer them from side effects or error prose when the system already knows the
reason.

## 4. Conflict freeze

When authoritative current sources materially disagree about:

- scope;
- ownership;
- task/lifecycle state;
- an approved decision;
- or a load-bearing fact;

stop only the affected work and record the contradiction.

The record should state:

- conflicting claims/sources;
- affected task/scope;
- what is safe to continue, if anything;
- who can resolve it or what evidence is required;
- resolution and resulting source of truth.

Do not silently choose whichever source appears more plausible.

A conflict record reports a problem; it does not itself grant authority to
resolve the conflict.

## 5. Independent review means independent context

Reviewer independence is not satisfied only because two sessions have different
names.

A reviewer is not independent when it is effectively a continuation of the
submission author—for example, a replacement session that inherited the same
in-flight claims and frozen handoff through context rotation.

When independent review is required, exclude:

- the submission author;
- a direct continuation/rotation successor of the author for that work;
- any worker that materially authored the reviewed output through a helper or
  shared editing path.

Use a fresh reviewer context where practical: task contract, outputs,
acceptance criteria, evidence, and necessary references—not the author's full
reasoning transcript.

## 6. Claim versus verification

For higher-risk work, distinguish what the implementer claims from what an
independent reviewer verifies.

Example:

```text
Criterion: invalid credentials do not create a session

Implementer claim: COMPLETE
Evidence: integration test X, log Y

Reviewer verdict: CONFIRMED
Reviewer evidence: independently reran test X
```

Do not rewrite the implementer's original claim when review disagrees. Record a
separate `REJECTED` or `CHANGES_REQUESTED` verdict and the evidence.

This distinction is optional for low-risk work where one review verdict over the
whole task is sufficient.

## 7. Diagnostics are not repairs

A validator, health check, monitor, or replay view may detect drift. Detection
does not give it permission to alter intent, authority, ownership, policy, or
architecture.

Use:

```text
detect
→ classify
→ repair mechanically if already authorized
  OR propose/escalate
→ verify
```

Structural repair follows the normal decision/change path.

## 8. Security is a separate review question

Functional correctness does not prove security correctness.

When work creates or changes a network-facing or write-capable surface, crosses
repo/machine/network trust boundaries, changes permissions, handles secrets, or
moves sensitive data, include a security-focused verification/review pass
appropriate to the risk.

That pass should inspect the actual boundary—authentication/authorization,
request method and origin/CSRF exposure, command/data injection, secret
handling, permissions, or equivalent concerns—not merely rerun functional
tests under a different label.

## 9. Session continuity

For consequential session replacement:

```text
checkpoint
→ verify the checkpoint
→ start/resume replacement
→ replacement acknowledges exact state
→ transfer explicit obligations/claims
→ supersede old session
```

Never destroy the only recoverable context first and reconstruct later.

Continuity transfer carries only the recorded obligations and authority already
held. A new provider, model, session ID, terminal, or process does not create
new governance authority.

## 10. Derived views remain derived

Replay indexes, dashboards, generated current-state sections, metrics, and
search indexes should be disposable and rebuildable from canonical sources.

A derived view may warn about disagreement. It must not become the hidden writer
that silently repairs the canonical source.

## Minimal rule

Use these protections where failure would otherwise create consequential
ambiguity. For a small, low-risk, session-local task, AGI + ordinary owner
verification may be enough.
