# E5 — recovery-compatibility enforcement seam — design note

Date: 2026-09-09
Owner: `liro` (orchestration coordinator, session 40)
Status: planning evidence only — Stage 0, no code
Supersedes nothing; extends `work/notes/2026-08-17-recovery-equivalence-authority-design.md`

## Why this note exists

The 2026-08-17 recovery-equivalence-authority note staged this work as:

- Stage 1 — bind `RecoveryIncident` to `run_id` (**done**, PR #82/#94)
- Stage 2 — pure advisory environment-evidence surfacing, Option A (**done**,
  `_advisory_environment_evidence`, `evidence` key on every `tick()` action)
- Stage 3 — bounded gating of one already-authorized resume (**Option B —
  operator decided "not approved at this time", decision #1, 2026-08-17**)

E5's roadmap exit gate is *"incompatible replacement cannot silently resume"*
(`work/roadmaps/agent-harness-capabilities/03-environment-and-reproducibility.md`
line 630). That is Stage 3 / Option B by definition. `CAPABILITY_CHECKLIST.md`
line 49 correctly records E5 as **IN PROGRESS**: "evidence is surfaced but not
enforced."

Since 2026-08-17 the codebase grew two landed *enforcement* seams of exactly
the shape Stage 3 would need — the opt-in resume-validation gate (PR #199,
first production exposure PR #324) and the opt-in canonical-run denial parking
state (PR #195, `--enforce-canonical-run`). This note answers the specific
question the session-39 handoff flagged as the most-ready design task:
**"which `tick()` branch would enforce the compatibility evidence"** — so a
future implementation task does not re-derive it — **without** reopening the
operator decision that still blocks it.

## Ground truth: `tick()` structure as of `18b064c`

`runtime/recovery/supervisor.py::tick()` processes each due incident through a
fixed sequence of `continue`-terminated gates. In order:

| # | Line (approx) | Gate | Outcome if it fires |
|---|---|---|---|
| 1 | 444 | `session_name in terminal_sessions` | `suppress` |
| 2 | 460–483 | task missing / not ACTIVE / claim changed | `suppress` |
| 3 | 485 | `session_is_live(...)` | `resolve` |
| 4 | 506 | `now < due_at` (backoff) | skip (no action) |
| 5 | 510 | `attempt >= len(backoff_seconds)` | `fail` / `retry_budget_exhausted` |
| 6 | 533–545 | advisory `resume_validator.validate_for_run(...)` | **records only**, never continues |
| 7 | 556–588 | **opt-in** `_validation_blocks_resume and _quick_validation_failed(...)` | park `blocked_validation` (or `fail` at ceiling `_MAX_CONSECUTIVE_VALIDATION_BLOCKS`) — **before any resume call**, `attempt` untouched |
| 8 | 596–644 | `harness_service.resume(...)` if configured | may set `canonically_denied` |
| 9 | 646–701 | **opt-in** `canonically_denied` | park `denied` (or `fail` at ceiling `_MAX_CONSECUTIVE_CANONICAL_DENIALS`), `attempt` untouched |
| 10 | 703–711 | fallback direct `hcom.resume(...)` | `resume` / `resume_failed` |
| 11 | 712–738 | `attempt += 1`, state `probing`, backoff reschedule | the audit action |

The advisory environment evidence (`_advisory_environment_evidence`, line 433)
is read once at the top of the loop body and attached to **every** action dict
as `environment_evidence`. Its docstring: *"purely advisory context, never
consulted by any branch in `tick()`."*

## The E5 enforcement seam — where Stage 3 would sit

**A compat gate belongs at position 7.5 — immediately after the
resume-validation gate (gate 7), strictly before the harness/direct resume
(gates 8 and 10).** Rationale, mirroring the resume-validation gate's own
in-source rationale (lines 526–555):

1. Every non-resume outcome (suppress / resolve / fail / not-yet-due) has
   already `continue`d out above, so the incident is genuinely committed to a
   resume attempt — the only point at which "would this resume run in an
   incompatible environment" is a coherent question (Area 1, 2026-08-17 note).
2. It is still *before* the resume call, so an incompatible environment never
   triggers a canonical-guarded or direct resume attempt — satisfying the
   exit gate's word *"silently"*: the incident parks visibly instead.
3. It composes cleanly with gates 7 and 9 by using the **same pattern**:
   its own opt-in flag, its own distinct parked state, its own consecutive
   ceiling, `continue` before `attempt` is incremented.

### Concrete shape (for a future implementation task — NOT authorized here)

```
# gate 7.5 — opt-in recovery-compatibility gate
if self._compat_blocks_resume:
    state, reasons = _compat_state_from_evidence(evidence)   # evidence already read at line 433
    if state in {"INCOMPATIBLE", "UNKNOWN"}:                  # DRIFTED: see operator decision below
        blocks = int(incident.get("compat_blocks", 0)) + 1
        incident["compat_blocks"] = blocks
        if blocks >= _MAX_CONSECUTIVE_COMPAT_BLOCKS:
            incident["state"] = "failed";  action, reason = "fail", "compat_block_persistent"
        else:
            incident["state"] = "blocked_compat"
            incident["next_attempt_at"] = _time_z(now + timedelta(seconds=self.silent_stop_probe_delay_seconds))
            action, reason = "resume_blocked_compat", "environment_incompatible"
        actions.append({... "compat_state": state, "compat_reasons": reasons ...})
        continue
    if incident.get("compat_blocks"):
        incident["compat_blocks"] = 0
```

- New opt-in constructor kwarg `compat_blocks_resume: bool = False` (twin of
  `validation_blocks_resume`), surfaced as
  `maps recovery-tick --enforce-recovery-compat --repo-root PATH`.
- New reprocessable state `"blocked_compat"` added to `_REPROCESSABLE_STATES`
  (twin of `"blocked_validation"`).
- New `_MAX_CONSECUTIVE_COMPAT_BLOCKS` ceiling constant.
- Reads **only** the `evidence` already fetched at line 433 — no new I/O, no
  new reader dependency. `_compat_state_from_evidence` is a pure function over
  the `list_run_environment_evidence` payload shape.
- `--enforce-recovery-compat` does **not** require `--enforce-canonical-run`
  (the compat check sits before the harness path, like `--enforce-validation`
  — see 2026-09-09 handoff, "Conventions confirmed").
- Zero behaviour change when the flag is off: `evidence` stays attached to
  actions exactly as today, read by nothing.

### Drift-state precedence (settled by existing law, not a new call)

Per Area 3 of the 2026-08-17 note and `evaluate_environment_compatibility()`'s
own precedence:

- `INCOMPATIBLE` → always blocks. Not a policy call.
- `UNKNOWN` → always fails closed (blocks). Not a policy call (`AGENTS.md`
  rule 15 / roadmap 4.4).
- `COMPATIBLE` / `COMPATIBLE_WITH_WARNINGS` → never blocks; warnings surfaced
  verbatim on the action dict.
- `DRIFTED` → **operator decision #2, still deferred** (see below). A safe
  first implementation treats `DRIFTED` as *warn-and-resume* (attach
  `compat_state` to the `resume` action, do not park), matching the
  conservative reading that `DRIFTED` ≠ requirements-unmet.

## What is still BLOCKED_ON_OPERATOR_DECISION

This note changes nothing about the authority position. The 2026-08-17
operator record stands:

> **Decision #1: Option A only, for now.** Environment-compatibility evidence
> stays advisory, zero change to what authorizes recovery. Option B (bounded
> gating of an already-authorized action) is explicitly not approved at this
> time. Recovery actions have real consequences; advisory-only needs to
> accumulate real operational experience before any gating is reconsidered.

**The gating precondition the operator set — "accumulate real operational
experience" with the advisory evidence — is not yet met.** `tick()` has had
near-zero production invocation historically (`work/insights/2026-08-19-recovery
supervisortick-has-zero-production-invocation-anywh-INSIGHT-e0b448a6.md`), and
`_advisory_environment_evidence` only returns non-`None` when an incident's
bound `run_id` resolves to a run that has `run_environment_evidence` rows —
which requires the environment-evidence writers (E3) to have run for that run.
No production recovery tick has yet been observed surfacing a non-null
`environment_evidence` on a real incident.

### The single question for the operator (when they next triage E5)

> The E5 enforcement seam is now designed and is a clean structural twin of
> the landed resume-validation gate (#199/#324). It stays blocked on your
> 2026-08-17 decision #1. Two things would unblock a bounded Stage-3
> implementation task:
> (a) confirmation that enough advisory operational experience has accumulated
>     — which currently it has **not** (no production tick has surfaced real
>     `environment_evidence`); and
> (b) the deferred decision #2: does `DRIFTED` block like `INCOMPATIBLE`, or
>     warn-and-resume?
> Until (a), the most useful next step is not E5 enforcement — it is getting
> the advisory path exercised on a real recovery tick with a run that has E3
> environment evidence, so there is something to accumulate experience *from*.

## Recommendation

1. Land this note as the E5 enforcement-seam design record (Stage 0).
2. Do **not** open a Stage-3 implementation task — decision #1 blocks it and
   its own precondition is unmet.
3. The genuinely-ready bounded follow-up is an **advisory exercise**: drive
   one `maps recovery-tick` pass against a real stalled incident whose bound
   run carries E3 `run_environment_evidence`, and freeze the observed
   `environment_evidence` payload as the first data point toward decision #1's
   "operational experience" bar. This is the E5 analogue of the #320/#324
   first-exposure exercises and needs no new authority.

## Resume prompt

You are picking up E5 (recovery compatibility) planning for MAPS_Lean. Read
this note and `work/notes/2026-08-17-recovery-equivalence-authority-design.md`
in full. State: the enforcement seam is designed (gate 7.5 in `tick()`, twin
of the resume-validation gate); it stays BLOCKED_ON_OPERATOR_DECISION #1
(Option B not approved) and that decision's precondition ("accumulate real
operational experience" with advisory environment evidence) is unmet because
no production recovery tick has surfaced a non-null `environment_evidence`
yet. Do NOT open a Stage-3 implementation task. The ready bounded work is an
advisory exercise: one real `maps recovery-tick` pass over a stalled incident
whose bound run has E3 `run_environment_evidence`, freezing the observed
`environment_evidence` payload. If the operator is triaging E5, put the
single question in the "The single question for the operator" section to them
verbatim.
