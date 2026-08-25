# RnS validation-tier hook-in design

Date: 2026-08-25
Owner: `/root`
Status: design complete; no runtime code changed by this note

Continues `work/notes/2026-08-21-rns-harness-validation-callsite-design.md`
("Validation-tier fast-follow" section). That note is the starting point; this
note resolves the placement it left open, now that the base call site (PR #160)
and the production trigger loop (PR #165) both exist.

## 1. Finding

### 1.1 The exit-gate language, quoted exactly

`work/roadmaps/CAPABILITY_CHECKLIST.md` line 25, row `H4 — Immediate validation
hooks` (`IN PROGRESS`):

> `runtime/environment/validation.py` + `tests/test_environment_validation.py`;
> merged via PR #106. Gives `EnvironmentSpec.validation` tiers a real executor
> and a Hook-callback factory; no production call site invokes it yet, so the
> exit gate ("representative failures caught immediately after mutation") is
> only partly met. The prerequisite base call site now exists
> (`work/tasks/rns-harness-resume-callsite.md`,
> `runtime/recovery/supervisor.py::RecoverySupervisor.tick()` routes resume
> through `HarnessService.resume()`), but that call site does not run validation
> tiers and nothing yet triggers `tick()` in production — validation-tier
> hook-in remains the still-unstarted fast-follow.

Line 48, row `E4 — Validation tiers` (`IN PROGRESS`):

> Same evidence as H4 (`runtime/environment/validation.py`); merged via PR #106.
> `ValidationTiers` (quick/normal/full) previously existed as pure declared data
> with zero callers; this task adds the first executor + Hook wiring, but no real
> caller (`HarnessService` or an adapter) invokes it yet.
> `work/notes/2026-08-21-rns-harness-validation-callsite-design.md` defined the
> prerequisite RnS harness call-site boundary; that call site is now built
> (`work/tasks/rns-harness-resume-callsite.md`), but it deliberately runs no
> validation tiers -- actual validation execution remains a separate fast-follow
> task.

Line 114, row `6.5 | Immediate deterministic validation` (`IN PROGRESS`):

> = H4/E4. `work/notes/2026-08-21-rns-harness-validation-callsite-design.md`
> identified RnS harness resume wiring as the prerequisite production call site;
> that call site now exists (`work/tasks/rns-harness-resume-callsite.md`), but
> validation-tier command execution itself remains unimplemented -- this task
> does not complete 6.5.

The operative phrase is **"representative failures caught immediately after
mutation"**. Note what it does *not* say: it does not require that a caught
failure block anything.

### 1.2 Current state, verified by grep at `8923adb` (origin/main, post-#165)

- `grep -rn "run_validation_tier\|make_validation_hook" --include=*.py .` →
  hits in `runtime/environment/validation.py` (the definitions),
  `runtime/environment/__init__.py` (re-exports), and `tests/` only. **Zero
  production callers.** No validation tier executes anywhere on the resume path,
  or anywhere else.
- `grep -rn "HarnessService(\|HcomHarnessAdapter(" --include=*.py .` → `tests/`
  only. **There is still no production `HarnessService` construction.**
  `runtime/recovery/production.py` (new in #165) documents this deliberately:
  "`harness_service` and `environment_reader` are intentionally left `None`",
  so in production `tick()` takes its unchanged direct-`hcom.resume()` fallback
  and `RecoverySupervisor.harness_service` is never non-`None`.
- `grep -rn "EnvironmentSpec" runtime/recovery/` → zero hits. Additionally
  `tests/test_recovery_supervisor.py::test_no_validation_tier_commands_or_task_mutation_in_source`
  (line 901) asserts the literals `environmentspec` and `make_validation_hook`
  do **not** appear in `runtime/recovery/supervisor.py`. That guard is a
  deliberate scope boundary from #160 and this design keeps it passing
  unchanged (see §2.4).
- `grep -rn "record_run_environment_evidence" --include=*.py .` →
  `runtime/state/environment.py` (the definition) and
  `tests/test_run_environment_evidence.py` only. **The `run_environment_evidence`
  table has zero production writers**, so it is empty in every real deployment
  today. This is load-bearing for §3.

So: post-#165 the harness invokes `tick()` in production (via the `claim` CLI
branch and the `recovery-tick` subcommand), and `tick()` attempts real resumes,
but no validation tier runs on that path. That is exactly the remaining piece of
6.5/H4/E4 identified in `work/notes/2026-08-24-roadmap-trajectory-check-7.md`
§5a item 2.

## 2. Proposed call site

### 2.1 Option A — register `make_validation_hook()` at `HookEvent.BEFORE_RESUME`

This is the obvious reading of the fast-follow section ("register the validation
hook at a resume-adjacent harness event"), and it must be **rejected as the
default placement**. Three concrete, code-grounded reasons:

1. **It would be a mandatory gate, which is a hard non-goal.**
   `make_validation_hook()` returns `HookOutcome(HookDirective.DENY, ...)` on any
   failing command (`runtime/environment/validation.py:196`).
   `HarnessService.resume()` runs `BEFORE_RESUME` hooks and returns
   `self._hook_block("resume", before)` when `not before.permitted`
   (`runtime/harness/service.py:309-310`). There is no non-blocking registration
   mode. Registering the factory's output as-is makes a failed quick tier
   *prevent the resume*, by construction.
2. **It would mislabel validation failure as a canonical-run mismatch.**
   `_hook_block` sets `code = "HOOK_DENIED"` (`service.py:121`), and
   `runtime/recovery/supervisor.py:24` has
   `_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}`. A DENY from
   *any* `BEFORE_RESUME` hook therefore lands in `tick()`'s
   `action = "resume_denied"; resolved = True` branch (`supervisor.py:394-405`)
   — the one branch that deliberately does **not** fall back to direct resume.
   A validation failure would be recorded as, and behave identically to, a
   canonical-run denial. That destroys the attribution #160 was explicitly
   designed to preserve.
3. **It is blocked on wiring that does not exist.** It requires a production
   `HarnessService` (none, §1.2) *and* an installed `CANONICAL_RUN` enforcement
   hook, because `resume()` calls `_require_canonical_enforcement(...)` before
   running hooks at all (`service.py:294-298`); without it the call returns
   `CANONICAL_GUARD_REQUIRED` and `tick()` falls back to direct resume, never
   reaching the validation hook. Option A therefore cannot run a single
   validation command in production until two other unbuilt pieces land.

Option A stays the right shape for a *later, explicit policy task* that decides
validation should gate resumes. It is not the shape of this one.

### 2.2 Option B — recommended: advisory pre-resume validation, composed outside `supervisor.py`

Attach validation at the point in `tick()` where an incident has been determined
to actually attempt a resume, as a read-only observation that is recorded and
never consulted by a decision branch — structurally identical to the existing
`environment_reader` slot.

Concretely:

- **New optional constructor input** on `RecoverySupervisor.__init__`, alongside
  `environment_reader` and `harness_service` (`supervisor.py:46-76`):
  a duck-typed `resume_validator` exposing a single method, e.g.
  `validate_for_run(run_id: str) -> dict[str, Any] | None`. Default `None`
  (behavior byte-identical to today). It takes the *incident's already-bound
  `run_id`* — the same value `_advisory_environment_evidence` already receives
  (`supervisor.py:285`) — and nothing else.
- **Invocation point:** inside `tick()`'s per-incident loop, **after** the
  retry-budget check at `supervisor.py:352-366` and **before** the harness/direct
  resume attempt at `supervisor.py:368`. That placement matters:
  - every earlier branch (`suppress`, `resolve`, `fail`, and the `now < due_at`
    skip) `continue`s out, so no validation command runs for an incident that is
    not about to be resumed;
  - it is the last point before the mutation-adjacent action, which is what
    "immediately after mutation" is reaching for on a resume path — the resume is
    the mutation, and validating the environment the session is about to be
    resumed into is the resume-path analogue;
  - it is genuinely *pre*-resume, so the result is not confounded by whatever the
    resumed session then does.
- **Surfacing:** a new key on the per-incident action dict, `"resume_validation"`,
  mirroring the existing `"harness_resume"` shape (`supervisor.py:290`,
  `380-389`, `414`): `None` when no validator is configured;
  `{"attempted": False, "reason": "<reason>"}` when a validator is configured but
  no spec could be sourced; `{"attempted": True, "passed": bool, "tier": "quick",
  "environment_spec_hash": ..., "result": <ValidationTierResult.to_dict()>}`
  when a tier actually ran. `ValidationTierResult.to_dict()` already produces
  exactly this payload (`validation.py:94-101`), including per-command outcomes
  that have been secret-redacted by `_redact_outcome` (`validation.py:71-83`).
  Emit it on the same action dicts the resume outcome is emitted on, and leave it
  `None` on the suppress/resolve/fail dicts, matching how `harness_resume` is
  already handled.
- **No decision branch reads it.** The resume proceeds exactly as it does today
  regardless of the validation outcome (see §5 Q1 — this is the recommendation,
  and it is the implementation task's job to state and test it, not to infer it).

### 2.3 Why Option B and not "wrap it in production.py after the tick"

`run_recovery_tick` (`production.py:80-97`) only sees the aggregate action list
*after* `tick()` returns. By then every resume has already happened, so a
post-hoc wrapper cannot produce a pre-resume observation, cannot bind a result to
the specific incident's run before its resume, and would have to re-derive the
run lineage `tick()` already has in hand. Rejected.

### 2.4 Composition root: `production.py`, not `supervisor.py`

The `resume_validator` object is **constructed in
`runtime/recovery/production.py`**, the module #165 established as the single
production construction site for `RecoverySupervisor`. Only that module imports
`parse_environment_spec` / `run_validation_tier`.

This is not cosmetic. It means `runtime/recovery/supervisor.py` never imports
`EnvironmentSpec` or `make_validation_hook`, so
`tests/test_recovery_supervisor.py::test_no_validation_tier_commands_or_task_mutation_in_source`
keeps passing **unmodified** — the #160 boundary guard survives intact and does
not have to be weakened to land this. The implementation task must verify that
test still passes as written rather than editing it.

It also means the validation path works on **both** the harness-routed resume and
the current direct `hcom.resume()` fallback, so — unlike Option A — it does not
depend on the still-nonexistent production `HarnessService`/`CANONICAL_RUN` guard
wiring. That is the decisive argument.

### 2.5 Tier

`quick` only, per the fast-follow recommendation. `normal`/`full` are review-time
tiers and have no business inside a bounded recovery pass; nothing in this design
makes them reachable from RnS.

## 3. What "EnvironmentSpec sourced from explicit task/run evidence" means here

Grounded in what actually exists — there is exactly one persisted-EnvironmentSpec
location in this codebase, and one file-based loader.

### 3.1 The one legitimate source: `run_environment_evidence.spec_snapshot`

`runtime/state/environment.py::EnvironmentEvidenceMixin` persists, per run:

- `record_run_environment_evidence(run_id, *, spec, fingerprint, spec_ref,
  recorded_by, reference=None)` writes `spec_snapshot` =
  `self._canonical_json(spec.to_dict())` into the `run_environment_evidence` table
  (lines 89, 119-142), bound to an existing `run_manifests.run_id` (lines 107-117).
- `list_run_environment_evidence(run_id)` (line 172) returns those rows
  `ORDER BY id`, with `spec_snapshot` already `json.loads`-decoded by
  `_decode_environment_row` (lines 33-42).

That reader is **already what RnS holds**: `RecoverySupervisor.environment_reader`
is documented as "must expose `list_run_environment_evidence(run_id) -> list[dict]`"
(`supervisor.py:62-65`). So the evidence path requires no new storage location, no
new schema, and no new reader interface — the run-bound spec is reachable from the
`run_id` already carried on the incident.

Reconstitution: `EnvironmentSpec` has **no `from_dict`**; it has `to_dict`
(`spec.py:168`) and a module-level `parse_environment_spec(data)` (`spec.py:195`)
whose `_reject_unknown` allow-set is exactly the key set `to_dict()` emits. The
round-trip therefore already works with no new API, and the implementation must
use `parse_environment_spec(row["spec_snapshot"])` rather than adding a
`from_dict`. It should also assert the parsed `spec.sha256` equals the row's
stored `environment_spec_hash` column and treat a mismatch as "no usable spec",
not as a validation failure.

### 3.2 The rejected source: `load_environment_spec(path)`

`runtime/environment/spec.py:317` loads a spec from a file path. Sourcing the spec
that way — from a conventional path, the repo root, or a config default — is
precisely the "universal default" the fast-follow section forbids: it is ambient,
not bound to the run being resumed, and would silently validate against a spec the
run never declared. **Not to be used by this call site.**

### 3.3 The consequence that must be stated loudly

Per §1.2, `record_run_environment_evidence` has **zero production writers**. The
`run_environment_evidence` table is empty in every real deployment today.
Therefore, on the day this design is implemented, the honest production behavior
is: **every incident reports `{"attempted": False, "reason": "no_spec_bound"}` and
no validation command runs anywhere.**

This is the correct outcome, not a defect, and the implementation task must not
"fix" it by inventing a fallback:

- it satisfies "if no spec is bound, validation must be skipped or reported as
  missing, not guessed";
- it makes the hook-in inert-but-wired, so the moment a production writer of
  environment evidence exists (the 6.24-adjacent work), validation begins running
  with no further RnS change;
- it means the implementation's own tests must supply run-bound evidence
  explicitly to exercise the positive path.

It also means this implementation, on its own, does **not** let anyone mark
6.5/H4/E4 `DONE` — see §7.

### 3.4 `repo_root` is part of the evidence problem, not a detail

`run_validation_tier(spec, tier, *, repo_root, ...)` requires a real directory and
raises `ValidationTierError` if it is not one (`validation.py:144-146`). RnS has no
repo root today: `production.py` takes `hcom_dir`, `hcom_executable`,
`hcom_timeout_seconds`, `recovery_state_path` — no repo root — and the
`recovery-tick` subcommand (`runtime/cli.py:155-177`) exposes none, though other
subcommands do (`context --repo-root`, `runtime/cli.py:145`; `flow start
--repo-root`, `runtime/cli.py:239` — both `default='.'`).

`EnvironmentSpec` does not carry a repo root either; the persisted evidence binds a
spec to a run, not to a checkout. Recommendation: an explicit caller-supplied
`repo_root` on `run_recovery_tick` plus a `--repo-root` flag on `recovery-tick`,
with **no implicit cwd default**; when it is absent, validation is skipped and
reported (`{"attempted": False, "reason": "no_repo_root"}`) on the same footing as
a missing spec. Whether the `claim`-piggyback path supplies one at all is an open
question (§5 Q2).

## 4. Non-goals for the implementation

Mirrors the fast-follow list, refined against what §2/§3 uncovered. The
implementation task must not:

1. **Add a report cache** of any kind — no memoized `ValidationTierResult`, no
   per-tick dedup store persisted anywhere, no reuse of a prior run's result.
2. **Introduce a default `EnvironmentSpec`** — no `load_environment_spec` from a
   conventional path, no bundled spec, no "the last spec we saw", no synthesizing
   a spec from a fingerprint. Only `run_environment_evidence` rows bound to the
   incident's own `run_id` (§3.1).
3. **Infer a `repo_root`** from cwd, `git rev-parse`, or the recovery-state path
   (§3.4).
4. **Pilot against an external project** — this is in-repo RnS wiring only.
5. **Add any always-on validation daemon, scheduler, thread, timer, cron entry, or
   background worker** (master roadmap §7.1 "Large persistent `mapd` supervisor
   daemon", §7.9 "Continuous discovery/process-police agents"). The only new
   process is the validation command's own bounded `subprocess.run`, inside a pass
   that is still triggered only by an already-occurring external event.
6. **Make validation a gate.** A failed or missing validation must not deny the
   resume, must not mark the incident `suppressed`/`failed`, must not consume the
   retry budget differently, and must not by itself imply environment
   incompatibility. No `compatibility_state` is derived from it.
7. **Register the validation hook as a `HookEnforcement`**, add a new
   `HookEnforcement` member, or change `_CANONICAL_DENIAL_CODES` /
   `HarnessService._hook_block` semantics (§2.1).
8. **Build production `HarnessService`/`HcomHarnessAdapter` wiring** — still a
   separate gap; this design deliberately does not depend on it (§2.4).
9. **Mutate task truth** — the existing RnS contract is unchanged: no
   `claim_task`/`submit_task`/`record_review`/`promote_ready`/`update_contract`,
   no writes to the task DB.
10. **Write new rows to `run_environment_evidence` or any run record** as part of
    the tick (see §5 Q7 — persistence is an open question, and the default answer
    is "action list only").
11. **Weaken `tests/test_recovery_supervisor.py::test_no_validation_tier_commands_or_task_mutation_in_source`**
    (§2.4).
12. **Mark 6.5, H4, or E4 `DONE`**, or edit any roadmap/checklist status field.

## 5. Open behavior questions the implementation must answer, not guess

Each has a recommendation; each must be decided explicitly in the task and covered
by a test.

**Q1 — On validation failure, does the resume proceed, get blocked, or get
flagged?**
Recommendation: **proceed, and flag**. The resume attempt happens exactly as
today; `resume_validation.passed = false` is recorded on the action dict. This is
forced by non-goal 6, and the H4 exit gate asks that failures be *caught*, not that
they block. The task must state this and test that a failing quick tier does not
change `action`, `attempt`, `state`, `last_error`, or `next_attempt_at`.

**Q2 — What is the runtime/timeout budget, and does validation run on the
`claim`-piggyback path at all?**
This is the largest cost question. `_default_executor` uses `timeout=600`
*per command* (`validation.py:59`), and a quick tier may declare several commands.
Meanwhile #165 deliberately bounded the `claim` path at
`CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS = 3.0` precisely so a previously pure-local
`claim` cannot stall (`production.py:44-51`), and its review recorded the ~6s
worst case as the tradeoff it accepted with eyes open. Running arbitrary
operator-declared shell commands inside that same pass could add minutes.
Recommendation: **validation off by default on the `claim`-piggyback path**
(no validator constructed there), **available on the explicitly-invoked
`recovery-tick` subcommand**, with an explicit total wall-clock budget for the
whole tier (not just per command) and a documented worst-case addition. The task
must pick and justify concrete numbers.

**Q3 — Per-incident or per-tick execution?**
With no cache permitted (non-goal 1), N due incidents sharing one run/spec would
run the quick tier N times. Recommendation: accept it, but bound it — validation
only runs for incidents that actually reach a resume attempt (§2.2 placement),
and the task should set an explicit per-tick cap on validation executions,
skipping with a recorded reason past the cap rather than running unbounded work.
"Reuse the result within a single tick" is a cache and is out of scope unless the
task argues it is not.

**Q4 — What exactly does "reported as missing" look like?**
Recommendation: the `{"attempted": False, "reason": ...}` shape from §2.2, with a
closed vocabulary of reasons (`no_run_id_bound`, `no_spec_bound`,
`spec_ambiguous`, `spec_unparseable`, `spec_hash_mismatch`, `no_repo_root`,
`no_validator_configured`, `validation_error`, `budget_exceeded`). It must be
impossible for a consumer to confuse "missing" with "passed" — in particular
`passed` must be absent, not `false`, when nothing ran.

**Q5 — Which row, when a run has several environment-evidence rows?**
`list_run_environment_evidence` returns all rows `ORDER BY id`. Recommendation:
if every row agrees on `environment_spec_hash`, use the last; if they disagree,
report `spec_ambiguous` and run nothing. Do not silently pick "latest" across
disagreeing specs.

**Q6 — Which failures are containable, and how?**
`run_validation_tier` can raise `ValidationTierError` (unknown tier, `repo_root`
not a directory), and an executor can raise. `tick()` must never break because of
validation. Recommendation: the same containment style already used for
`_advisory_environment_evidence` and `_resolve_harness_binding` — catch broadly,
record `{"attempted": False, "reason": "validation_error", ...}`, continue.
The task must decide whether the caught exception type/message is recorded, given
that raw text is only secret-redacted inside `_redact_outcome`, which does not
cover exception strings.

**Q7 — Where does the result persist?**
The tick's action list is **discarded** on the `claim` path (#165's review, F2:
only `.maps/state/recovery.json` is written). So an action-list-only result is
invisible for `claim`-triggered passes. Options: action list only (default);
additionally onto the incident record in `.maps/state/recovery.json`; or as new
run-record/environment evidence (which non-goal 10 currently forbids).
Recommendation: **action list only** for this task, which is coherent with Q2's
"not on the `claim` path". If the task chooses to persist onto the incident
record, it must justify the added recovery-state growth.

**Q8 — Does validation ever run for non-resume outcomes?**
Recommendation: **no** — suppress/resolve/fail/not-yet-due incidents run nothing
and carry `resume_validation: None`. Stated so it is tested, not assumed.

**Q9 — Does a validation result influence the environment-compatibility story?**
Recommendation: **no**, per the fast-follow's "missing validation evidence should
not imply environment incompatibility". No `EnvironmentCompatibilityReport` is
computed, altered, or persisted from a tier result. Whether validation ever
becomes mandatory is a **later, explicit policy decision that this design does not
make**.

## 6. Bounded follow-up implementation

Recommended next task: `RnS resume-path validation-tier hook-in`.

Allowed scope:

- `runtime/recovery/supervisor.py`: one new optional `resume_validator`
  constructor input; one call at the §2.2 point; one new `"resume_validation"`
  key on the action dicts. No `EnvironmentSpec`/validation imports.
- `runtime/recovery/production.py`: construct the validator (reading
  `run_environment_evidence` via the existing reader interface, parsing with
  `parse_environment_spec`, executing with `run_validation_tier(..., tier="quick")`),
  wire the explicit `repo_root` and budget inputs, and keep it unconstructed on
  whichever path Q2 decides.
- `runtime/cli.py`: at most the flags Q2/§3.4 require on `recovery-tick`.
- Tests covering: the no-validator default is byte-identical to today; missing
  spec reports missing and runs nothing; a run-bound spec runs the quick tier and
  records a redacted result; a *failing* quick tier does not alter the resume
  outcome or incident bookkeeping (Q1); suppressed/resolved/failed/not-due
  incidents run nothing (Q8); an exploding validator cannot break a tick (Q6);
  ambiguous evidence reports `spec_ambiguous` (Q5); the budget cap is enforced
  (Q2/Q3); and the existing #160 source-guard test still passes unmodified.

Must not do: anything in §4.

## 7. Roadmap impact

This note is design only and completes nothing. Even its implementation does not
by itself close 6.5/H4/E4: per §3.3 the validation path will be inert in
production until something writes run-bound environment evidence, so
"representative failures caught immediately after mutation" will be *wired* but
not yet *demonstrated*. The checklist rows should be updated only when a real run
carries bound environment evidence and a tier result is observed on a resume —
which is a distinct, later piece of evidence, not this task's acceptance
criterion.
