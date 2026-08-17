# Recovery-equivalence authority — design note

Date: 2026-08-17
Owner: `agent/recovery-equivalence-authority-wave4`
Status: planning evidence only

## Why this lane exists

E1/E2/E3 (EnvironmentSpec, EnvironmentFingerprint/compatibility, run-environment
evidence — PR #28/#29/#30) are accepted. The reconciliation doc's dependency
map puts a deliberate gate after them:

```text
ENVIRONMENT E1/E2/E3 ACCEPTED
        ↓
recovery/setup equivalence only after explicit authority design
```

and its bounded next planning question:

> For recovery-equivalence work: use accepted environment evidence without
> turning COMPATIBLE into permission; current task/run/policy/ownership
> authority still controls recovery.

This note answers that question without resolving genuine policy calls
silently, matching how the parallel operational-learning-promotion-authority
task is expected to flag its own policy questions rather than assume answers.

## Ground truth: what RnS currently does (verified by direct read)

`runtime/recovery/supervisor.py`:

- `observe_silent_stops()` opens an incident only when a worker's single
  unambiguous `ACTIVE` task's bound session transitions from live to not-live.
  Ambiguous workers (multiple `ACTIVE` claims) are recorded and skipped, not
  guessed.
- `tick()` processes due incidents and, in order, checks: terminal-session
  membership, task existence, `task.status == "ACTIVE"`, `task.claimed_by ==
  worker_id`, then `session_is_live()`, then backoff timing and attempt
  budget, before calling `hcom.resume(...)`.

`runtime/recovery/store.py`:

- `RecoveryIncident` fields: `incident_id, task_id, worker_id, session_name,
  reason, resume_after, state, attempt, next_attempt_at, last_attempt_at,
  last_error, created_at, updated_at`. No `run_id`, no fingerprint reference,
  no compatibility field.

Neither file imports `runtime.environment`, reads `run_environment_evidence`,
or references `EnvironmentFingerprint`/`CompatibilityState` anywhere.

**Conclusion**: current recovery authority is already entirely task/claim/
session-liveness based. Environment compatibility plays no role today, by
omission, not by an explicit "ignore environment" rule. This matters for area
4 below — the smallest safe next step is additive surfacing, not removal of
an existing environment check (there is none to remove).

## Area 1 — What would "equivalence" even mean for recovery

Two different questions get conflated if we're not careful:

```text
Q_env:      does this observed environment look like the one a prior run
            declared/observed? (EnvironmentSpec + EnvironmentFingerprint +
            evaluate_environment_compatibility() — mechanical, evidence-only)

Q_recover:  is resuming/replacing THIS run/task authorized right now?
            (task status, claim/lease, policy, ownership, review state —
            RnS's actual current gates)
```

`Q_env` is answered entirely by `runtime/environment/fingerprint.py`. It is a
necessary-but-not-sufficient signal for `Q_recover` **at best** — an
environment that is `COMPATIBLE` says nothing about whether the task is still
`ACTIVE`, still claimed by the same worker, still in policy, or whether an
operator has revoked the work. Conversely, an environment that is `DRIFTED`
does not by itself revoke a lease that current RnS checks independently.

For compatibility evidence to become *relevant* to a recovery decision at
all, all of the following must independently already hold, using only
existing mechanisms:

1. the task still exists and is `ACTIVE` (existing RnS check, unchanged);
2. the claim/worker binding is still valid (existing RnS check, unchanged);
3. the session is genuinely not live, i.e. recovery is actually being
   considered (existing RnS check, unchanged);
4. there is an exact, non-heuristic binding from the recovery incident to the
   specific run whose environment evidence would apply. **This does not exist
   today** — `RecoveryIncident` has no `run_id`. Without it, "look up this
   incident's environment evidence" has no well-defined target, and guessing
   the most-recent run for a task would be exactly the kind of heuristic
   `AGENTS.md` and roadmap `4.4` prohibit.

Only once (1)–(4) hold is there a coherent question to even ask compatibility
evidence. At that point compatibility evidence answers a strictly narrower
question than "may recovery proceed" — it can only ever answer "does the
environment this recovery would run in match what was declared," which is
necessary context, not sufficient permission.

**Staged next step**: do not attempt to answer `Q_env` inside recovery until
(4) is resolved by a separate, explicitly scoped schema/runtime task. This
design does not add `run_id` to `RecoveryIncident` — that is out of this
task's change boundary (see task file) and is flagged as an operator decision
below.

## Area 2 — Where the authority boundary sits

Roadmap law `4.2`, "Capability is not authority," and `AGENTS.md` rule 5,
"Do not confuse capability with permission," both apply directly: a
mechanically `COMPATIBLE` result is a capability-shaped fact (the environment
*can* support the declared runtime/tool/network/service requirements). It is
not, and must never silently become, an assignment/ownership/policy-approval
fact.

Two structurally different designs are possible:

**Option A — evidence stays purely advisory.** Recovery authority remains
100% with existing task/policy/ownership/lease mechanisms exactly as
implemented in `runtime/recovery/supervisor.py` today. Environment
compatibility, if surfaced at all, is additional read-only context attached
to an already-independently-authorized recovery action (e.g., in the audit
action list `tick()` already returns) — never a gating input to whether that
action happens. This changes zero behavior of `tick()`/`observe_silent_stops()`.

**Option B — mechanical equivalence gates one narrow, already-bounded,
reversible action.** For example: an incident that RnS has *already*
independently decided to `resume` (task ACTIVE, claim valid, session dead,
within backoff budget) could additionally require `COMPATIBLE` or
`COMPATIBLE_WITH_WARNINGS` before the resume attempt fires, with anything
else (`DRIFTED`/`INCOMPATIBLE`/`UNKNOWN`) causing the incident to suppress
with an explicit reason instead of attempting resume. This does not *expand*
authority — it only ever *narrows* an action RnS already independently
decided to take. It never lets environment evidence authorize something RnS
wouldn't otherwise have done.

Option A is unambiguously safe under `4.2` and requires no new judgment call.
Option B is narrower than "compatibility grants recovery permission" but it
is still a policy choice: it changes RnS's *success rate/behavior* (some
resumes that would happen today would instead suppress), and "should
environment mismatch be allowed to block an otherwise-authorized resume" is
exactly the kind of consequential, external-behavior-changing decision
`AGENTS.md` reserves for the operator, not the task owner.

**Flagged as requiring an explicit operator decision**: whether Option B is
ever legitimate, and if so, exactly which bounded RnS action (if any) it may
gate. This design does not assume an answer. Absent an explicit operator
decision, Option A is the only version of this design a task owner may
implement.

## Area 3 — Drift handling

| Compatibility state | Recovery-context meaning | Proposed treatment |
|---|---|---|
| `COMPATIBLE` | Everything the spec required was observed and matched | Neutral positive signal; still not permission (Option A) or, only if Option B is operator-approved, satisfies the gate |
| `COMPATIBLE_WITH_WARNINGS` | Requirements held; some non-blocking difference (e.g. tool version drift, broader network) | Same as `COMPATIBLE` for gating purposes, but the warning reasons should always be surfaced verbatim, never summarized away |
| `DRIFTED` | Something the reference/spec pinned (repo revision, worktree cleanliness, dependency hash, spec hash) changed | Distinct from `INCOMPATIBLE`: requirements aren't necessarily unmet, but the *known* prior state no longer matches. Whether this should block a bounded recovery action or merely warn is a genuine policy call — flagged below, not resolved here |
| `INCOMPATIBLE` | A hard requirement (missing runtime/tool, missing secret/service capability, network mode mismatch, unmet version constraint) is unmet | Must never be treated as satisfying any recovery gate, under any option. This is not a policy call — it directly mirrors `evaluate_environment_compatibility()`'s own precedence (incompatible dominates) and roadmap `4.2` |
| `UNKNOWN` | Evidence is missing/unreadable for at least one required fact | Must fail closed for recovery purposes always. Treating `UNKNOWN` as "assume compatible" would directly violate `AGENTS.md` rule 9 ("do not hide uncertainty") and roadmap `4.4` ("Unknown remains unknown"). This is settled by existing law, not a new call this task makes |

**Flagged as requiring an explicit operator decision**: whether `DRIFTED`
should be treated identically to `INCOMPATIBLE` (hard-block any bounded
recovery gate) or as a lesser caution that still allows a bounded action with
a recorded warning. Both readings are defensible from the fingerprint code
alone (`DRIFTED` and `INCOMPATIBLE` are already distinct states with distinct
precedence in `evaluate_environment_compatibility()`), so this task does not
pick one.

## Area 4 — Relationship to existing RnS behavior

Confirmed by direct read (see "Ground truth" above): current RnS makes every
continuation/resumption decision without consulting environment evidence at
all — not because it was deliberately excluded, but because environment
evidence didn't exist yet when RnS was built and no integration has been
attempted since E3 landed.

Given that, and given Area 1's finding that there is no `run_id` binding on
`RecoveryIncident` to even locate the relevant evidence, the smallest safe
next step is:

**Stage 0 (this task): design only, no code.**

**Stage 1 (future implementation task, requires its own review): bind
incidents to runs.** Add whatever minimal, append-only reference lets a
`RecoveryIncident` (or the audit action `tick()` emits) resolve to the
specific `run_id` it concerns, without touching task/claim/lease semantics.
This is a prerequisite, not the recovery-authority change itself.

**Stage 2 (future implementation task, requires its own review, and only
after Stage 1 lands): pure evidence surfacing (Option A).** When `tick()`
processes an incident that already independently qualifies for `resume`
under its current checks, look up the run's most recent
`run_environment_evidence` (via `list_run_environment_evidence` /
`get_run_environment_evidence`, which already exist and are read-only) and
attach the compatibility state and reasons to the returned action record as
additional context — e.g. `{"incident_id": ..., "action": "resume",
"environment_context": {"state": "DRIFTED", "reasons": [...]}}`. This changes
**zero** behavior of what triggers, suppresses, or resumes an incident. It is
purely additive observability, consistent with roadmap `4.7` ("Derived views
stay derived") and the existing `EnvironmentEvidenceMixin` docstring's own
boundary.

**Stage 3 (only if the Area 2 operator decision approves Option B): bounded
gating.** Only after an explicit operator decision authorizes it, and only
for the specific narrow action they approve, would `tick()` additionally
consult the surfaced compatibility state to decide whether to *suppress
instead of attempt* a resume it had already independently qualified. This
stage is not authorized by this task and is not assumed to happen.

This task performs none of Stages 1–3. It documents them as the smallest
safe staged path so a future implementation task doesn't have to
re-derive the ground truth above.

## Area 5 — Snapshot/rehydration relevance

`work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` `6.17 Sandboxes /
snapshots / rehydration` is listed `TRIGGERED` — not yet justified, not
built. Its own prerequisites list EnvironmentFingerprint as an input to it,
not the other way around. This design does not assume snapshots/rehydration
exist, does not reference them as a mechanism, and scopes entirely to what
`runtime/recovery/` actually does today: resuming a known hcom session for
an already-claimed, already-`ACTIVE` task. If snapshot/rehydration is
eventually triggered separately, it would need its own authority design; this
note does not pre-decide how (or whether) recovery-equivalence work should
extend to it.

**Flagged as requiring an explicit operator decision**: whether
recovery-equivalence work should ever be expected to extend toward
snapshot/rehydration continuation once 6.17 is separately triggered, or
whether it should remain permanently scoped to RnS session-resume only. Not
answered here; out of scope by roadmap status alone (`TRIGGERED` ≠ built).

## Decision authority

### Owner (this task) may decide

- That `Q_env` (environment equivalence) and `Q_recover` (recovery authority)
  are distinct facts and must not be merged into one signal.
- That `UNKNOWN` fails closed for recovery purposes always — this follows
  directly from existing `AGENTS.md`/roadmap law, not a new policy choice.
- That `INCOMPATIBLE` can never satisfy any recovery gate under any option —
  same reasoning.
- That the smallest safe next step is Stage 2 (pure evidence surfacing,
  Option A), and that it cannot be implemented before Stage 1 (run binding)
  exists.
- That this design does not assume snapshot/rehydration capability.
- That no runtime/schema file is touched by this task.

### Requires an explicit operator decision (not resolved by this task)

1. **Option A vs. Option B (Area 2)** — may mechanical environment
   equivalence ever gate *any* bounded recovery action (narrowing an
   already-authorized resume), or must it remain purely advisory forever?
2. **`DRIFTED` treatment (Area 3)** — if Option B is ever approved, does
   `DRIFTED` hard-block like `INCOMPATIBLE`, or count as a lesser warning
   that still permits the bounded action?
3. **`RecoveryIncident`-to-run binding (Area 1 / Area 4 Stage 1)** — should
   `RecoveryIncident` gain a `run_id` (or equivalent) at all, and if so, what
   schema/migration/authority process governs that change? This is a
   prerequisite for Stage 2 even under the safest option.
4. **Who may act on surfaced advisory evidence (Area 4 Stage 2)** — is
   surfaced `environment_context` intended for a human operator reviewing
   incidents only, or could a future automated policy layer read it? This
   note assumes human-visible-only unless told otherwise; that assumption
   itself should be confirmed, not silently carried forward.
5. **Snapshot/rehydration extension (Area 5)** — should recovery-equivalence
   work ever be expected to extend toward 6.17 once it is separately
   triggered, or stay scoped to RnS session-resume permanently?

None of these five are resolved in this note. They are the concrete output
this design task was asked to produce.

## Continuation

```text
this design (Stage 0)
        ↓
operator decisions 1-5 above
        ↓
IF run-id-binding approved:
    Stage 1 — bind RecoveryIncident to run_id (separate implementation task,
    independent review)
        ↓
    Stage 2 — pure evidence surfacing, Option A (separate implementation
    task, independent review)
        ↓
    IF Option B explicitly approved AND DRIFTED policy decided:
        Stage 3 — bounded gating of one already-authorized action
                  (separate implementation task, independent review)
ELSE:
    recovery-equivalence work stops at Stage 0; environment evidence remains
    unconsulted by RnS, exactly as it is today
```

Until operator decisions 1-5 land, recovery-equivalence work is correctly
**BLOCKED_ON_OPERATOR_DECISION**, not an invitation to pick a default.

## Operator decisions (recorded 2026-08-17)

The operator reviewed the five flagged questions and decided:

1. **Option A only, for now: environment-compatibility evidence stays advisory, zero change to what currently authorizes recovery.** Option B (bounded gating of an already-authorized action) is explicitly not approved at this time. Recovery actions have real consequences; advisory-only needs to accumulate real operational experience before any gating is reconsidered.
2. **Deferred.** Since no gating is authorized (per #1), whether `DRIFTED` should hard-block like `INCOMPATIBLE` does not need an answer yet.
3. **Approved: bind `RecoveryIncident` to `run_id`.** This is the concrete prerequisite Stage 1 needs regardless of the bigger authority questions, and is low-risk (additive field, append-only).
4. **Human operators only, for now.** No automated policy layer may consume surfaced environment evidence to make recovery decisions.
5. **Out of scope.** This work stays scoped to RnS session-resume; it does not extend toward snapshot/rehydration (roadmap 6.17, still `TRIGGERED`).

## Unblocked next step

With #1 and #3 decided, **Stage 1** (bind `RecoveryIncident` to `run_id`) and **Stage 2, Option A only** (pure read-only environment-evidence surfacing in `tick()`'s output, zero behavior change) are now authorized as bounded implementation tasks, each requiring independent review per the continuation plan above. Stage 3 (any gating) remains **BLOCKED_ON_OPERATOR_DECISION** and is not authorized by this record.
