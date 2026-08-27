# Design: a production composition root for the Hook/Harness enforcement layer

**Status: DESIGN ONLY.** This note changes no runtime code. It proposes the
minimum composition code that would make the already-built, already-tested Hook
enforcement layer reachable in production, and settles the one safety question
that decides whether that composition can be default-on.

Serves roadmap trajectory pass #8 §5a item 1
(`work/notes/2026-08-26-roadmap-trajectory-check-8.md`). Affected checklist
rows: **6.4/SEC3**, **6.5/H4/E4**, **6.16/E6**, **H5**.

---

## 1. The finding, re-derived

Pass #8 §3a and PR #175's design note both assert this. Neither was trusted; the
grep below was re-run at this branch's head (`origin/main` `722beab`, PR #176
merged) and the result is reproduced verbatim:

```
$ grep -rn "HarnessService(\|HookRegistry(\|register_canonical_run_guards(" --include=*.py . \
    | grep -v '/tests/'
runtime/harness/service.py:27:        self.hooks = hooks or HookRegistry()
runtime/policy/harness_guard.py:194:def register_canonical_run_guards(registry: HookRegistry, guard: CanonicalRunGuard, *, priority: int = 10) -> None:
```

Two hits, 61 total. The first is `HarnessService`'s own internal fallback
default — it constructs an *empty* registry for itself, which is the opposite of
composition. The second is the definition of the registration helper. **Every
one of the other 59 hits is under `tests/`.**

The same re-derivation for the second guard:

```
$ grep -rn "DestructiveExternalActionGuard\|register_destructive_external_action_guards" \
    --include=*.py runtime/
runtime/policy/destructive_action_guard.py   (definition + helper)
runtime/policy/__init__.py                   (re-export)
```

So: **nothing in this repository composes a `HookRegistry`, registers a guard on
one, or constructs a `HarnessService`, outside `tests/`.** The enforcement layer
that 6.4/SEC3, 6.5/H4/E4, 6.16/E6 and H5 all route through has no production
composition root at all.

### 1a. Is `runtime/` intended to be library-only?

Pass #8's own honesty check (§7) flags this as the question that would
invalidate the whole item: if `runtime/` is meant to be a library that an
external caller composes, then §1 describes the designed state, not a gap.

**Settled: no.** `runtime/cli.py` is a production entrypoint that already
composes concrete objects and performs consequential mutations —
`TaskStore(args.db)` at line 290, and `run_recovery_tick_isolated(store, ...)`
at lines 376 and 387, which via `runtime/recovery/production.py:382-392`
constructs a `RecoverySupervisor`, an `HcomAdapter`, a `RecoveryStore` and
(conditionally) a `RunBoundValidator`, then calls `observe_silent_stops()` and
`tick()`. `runtime/recovery/production.py`'s own module docstring calls itself
"the single production construction site for `RecoverySupervisor`". Three other
`main()`-bearing modules exist (`runtime/smoke.py`, `runtime/routing/cli.py`,
`runtime/integrity/cli.py`). A library-only runtime would have none of this.
The Hook layer is the outlier, not the rule.

### 1b. Why this is one gap and not four

- **H5 / 6.5.** `runtime/recovery/production.py:391` passes
  `harness_service` omitted (the call-site comment reads
  "environment_reader/harness_service deliberately omitted -- see module
  docstring"; the docstring's stated reason is that "no production
  `HarnessService` / `HcomHarnessAdapter` construction exists anywhere outside
  tests"). `runtime/recovery/supervisor.py:422` gates the whole PR #160 routing
  block on `if self.harness_service is not None:`. So the harness-routed resume
  path is dead code in production, and `_resolve_harness_binding` is never
  called.
- **6.16/E6.** PR #175 designs the worktree-binding enforcement seam *as a
  change inside `CanonicalRunGuard._require_current_run()`*. Implementing it
  produces a stricter guard that is still never composed.
- **6.4/SEC3.** `DestructiveExternalActionGuard` is unwired, and there is no
  registry to wire it onto.
- **E4.** PR #106's `make_validation_hook` factory has no production
  `HookRegistry` to attach to.

The docstring reasoning in `production.py` is worth reading carefully, because
this design must engage it rather than reverse it: it does **not** say harness
routing is undesirable. It says the wiring did not exist and building it was out
of that PR's scope. That is a scope statement, not a policy objection, and it is
the exact statement this note proposes to retire.

---

## 2. The safety question, answered first

This is the load-bearing part of the note, so it comes before the proposal.

**Question:** when `CanonicalRunGuard` sees no policy signal, does it ALLOW,
DENY, or REQUIRE_APPROVAL?

**Answer, read directly from `runtime/policy/harness_guard.py`: it DENIES, and
it never returns ALLOW at all.**

`CanonicalRunGuard.__call__` (lines 158-191) has exactly two kinds of exit:
- every failure path returns `self._deny(...)`, i.e.
  `HookOutcome(HookDirective.DENY, ...)`;
- the single success path (line 186) returns
  `HookOutcome(HookDirective.ANNOTATE, ..., guard_code="CANONICAL_RUN_VERIFIED")`.

`HookDirective.ALLOW` is never constructed anywhere in that file.
`HookDirective.REQUIRE_APPROVAL` is never constructed there either. The guard is
**fail-closed by construction**: absent evidence is a denial, and the best
available outcome is a permitted annotation. There are 28 `_deny(...)` call sites
carrying **23 distinct deny codes**, including `BINDING_REQUIRED`,
`BINDING_INCOMPLETE`, `TASK_NOT_FOUND`, `RUN_NOT_FOUND`, `RUN_TASK_MISMATCH`,
`RUN_WORKER_MISMATCH`, `RUN_REVISION_MISMATCH`, `TASK_REVISION_STALE`,
`TASK_NOT_ACTIVE`, `NOT_CLAIM_OWNER`, `LEASE_EXPIRED`, `RUN_STALE`,
`UNSUPPORTED_OPERATION`, and **nine** `SESSION_*` lineage denials.

### 2a. What this means, stated precisely

The guard is **safe-by-default in the authority sense and unsafe-by-default in
the availability sense**, and conflating those two is exactly the hand-wave this
section exists to avoid.

- *Authority*: it can only narrow. It grants nothing, mutates nothing, performs
  no I/O beyond reads through `CanonicalRunSource`, and is registered
  `READ_ONLY` + `FAIL_CLOSED` (enforced by
  `HookRegistry._register_enforcement`, which raises otherwise). There is no
  privilege-escalation risk in composing it. **On this axis, no gate is needed.**
- *Availability*: composing it will **deny resumes that succeed today**, and
  will do so on the most likely path, not an edge case. That is the risk.

### 2b. The concrete first-exposure behavior change on the RnS path

`_resolve_harness_binding` (`supervisor.py:148-211`) already pre-filters, and
that pre-filter subsumes *some* of the guard's checks: it requires the task to
exist, `project_id` and `compute_task_revision()` to resolve, and the run/session
lineage to be `EXPLICIT` with `adapter_id == "hcom"`. Incidents failing those
return `(None, None, reason)` and fall back to the direct resume — unchanged.

But the pre-filter deliberately does **not** check what
`CanonicalRunGuard._require_live_claim` and `_require_current_run` check:

| Guard check | Deny code | Pre-filtered by `_resolve_harness_binding`? |
|---|---|---|
| `task.status == "ACTIVE"` | `TASK_NOT_ACTIVE` | **No** |
| `task.claimed_by == worker_id` | `NOT_CLAIM_OWNER` | **No** |
| `lease_expires_at > now` | `LEASE_EXPIRED` | **No** |
| `check_run_stale(run_id)` false | `RUN_STALE` | **No** |
| `manifest.task_revision == binding revision` | `RUN_REVISION_MISMATCH` | **No** |
| `compute_task_revision() == binding revision` | `TASK_REVISION_STALE` | *Tautological here — see below* |

One row in that table needs a caveat rather than a checkmark.
`TASK_REVISION_STALE` cannot actually fire on this path: `_resolve_harness_binding`
builds `binding.task_revision` *from* `self.task_reader.compute_task_revision(task_id)`
(`supervisor.py:172-176`), and the guard's `require_current_revision` check calls
the same method on the same source and compares the two
(`harness_guard.py:73-76`). It is a comparison of a value against itself. The
denial that actually catches task-definition drift on this path is
`RUN_REVISION_MISMATCH` (`harness_guard.py:71-72`), which compares the *immutable
run manifest's* recorded revision against the freshly-computed one — and that is
genuinely unfiltered and genuinely reachable. Listing `TASK_REVISION_STALE` as a
live first-exposure risk would overstate the case; `RUN_REVISION_MISMATCH` is the
real one and was missing from an earlier draft of this table.

These are precisely the conditions most likely to be violated for a recovery
incident. RnS exists to resume a session that *stopped silently* — and a session
that stopped silently is a strong candidate for a task whose lease has since
expired. `LEASE_EXPIRED` is not a hypothetical first-exposure denial; on the RnS
path it is close to the expected case.

Trace the consequence through `tick()`:

1. Guard returns `DENY` → `HookRunResult.denied` is True → `permitted` False.
2. `HarnessService.resume` (`service.py:309`) returns `_hook_block("resume", before)`
   → `OperationResult.failure("HOOK_DENIED", ...)`.
3. `supervisor.py:24` defines `_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}`;
   line 447 matches, sets `action = "resume_denied"`, `resolved = True`.
4. **No fallback.** The direct `hcom.resume()` is skipped by design (the block's
   own comment: "This is the one outcome allowed to change behavior versus the
   pre-existing direct-resume call").
5. `attempt += 1`, backoff applied, incident stays `probing`.
6. On a later pass, once `attempt >= len(self.backoff_seconds)` (line 384), the
   incident becomes `state = "failed"`, `last_error = "retry_budget_exhausted"`.

So the realistic first-exposure outcome is not "one denial gets logged". It is
**incidents that RnS resumes today instead burning their retry budget and
terminating as `failed`**. That change is contained — it touches only the
`RecoveryStore` JSON file, never task truth, and `harness_resume` records the
denial code and summary on the action dict for every affected incident — but it
is a real availability regression from the operator's point of view, and it is
arguably *the correct behavior* (resuming a run whose claim lease has expired is
what canonical enforcement is meant to prevent). Both facts are true at once.

### 2c. Verdict on the gate

**A feature gate is required for first production exposure — not because the
guard is unsafe, but because it is strict.** Default-on would silently convert a
common, currently-working recovery outcome into a terminal one. Default-off with
an explicit opt-in makes the first exposure a deliberate, observable, operator-
chosen act, which matches how `--repo-root` was introduced for the validation
tier in PR #172 and how `--binding` was introduced in PR #165.

**An observe-only / dry-run mode is not available without runtime changes, and
this is a real constraint rather than a preference.** The obvious idea —
register the guard as an ordinary (non-enforcement) hook so it annotates without
blocking — does not work: `HarnessService.resume` calls
`_require_canonical_enforcement` (line 294) *before* `self.hooks.run(...)`
(line 300), so with no `CANONICAL_RUN` enforcement installed the guard is never
invoked at all and the service returns `CANONICAL_GUARD_REQUIRED`. (That code is
deliberately **not** in `_CANONICAL_DENIAL_CODES`, so it falls through to the
direct resume — which is exactly why composing a `HarnessService` with an *empty*
registry would be a pure no-op.) A genuine shadow mode would require changing
`tick()`'s decision logic or the service's ordering, both of which are non-goals
(§4). The gate is therefore an on/off opt-in, and §5 records shadow mode as an
open question for a later slice rather than smuggling it in here.

---

## 3. Proposal: the minimum viable composition root

### 3a. Location

**`runtime/recovery/production.py`**, as a new module-level helper alongside the
existing `RunBoundValidator` composition — not a new module, not
`runtime/cli.py`, not a new package.

Rationale, in the project's own terms (master roadmap §7.1/§7.9; smallest change
that satisfies the requirement):

- `production.py` already declares itself the production composition site for
  this flow, and already composes a second optional collaborator
  (`RunBoundValidator`) under exactly the same explicit-opt-in shape. Adding a
  third follows an established local pattern rather than inventing one.
- There is exactly **one** production consumer of a `HarnessService` today: the
  `harness_service=` parameter at `production.py:382-392`. `maps flow start` is
  explicitly "claim, plan context, and bind a run manifest **without provider
  launch**" (`cli.py:249`), so it never reaches `HarnessService.start()`. A
  neutral `runtime/harness/composition.py` would be infrastructure for a single
  caller.
- `runtime/cli.py` is the right place for the *flags*, not the *construction*.
  It stays a thin argument-parsing layer, consistent with how it treats
  `--repo-root` today.

If and when a second consumer appears (a real `flow launch`, or SEC3's first
call site), the helper moves to a neutral home in that PR. That is a cheap move
and is not worth pre-paying for.

### 3b. Shape

```
def build_canonical_harness_service(
    task_reader, *, project_id: str, repo_root: str | Path
) -> HarnessService: ...
```

Constructs, in order:
1. `HcomHarnessAdapter(HcomAdapter(...), project_id=project_id, lineage_writer=task_reader)`
   — mirroring `tests/test_recovery_supervisor.py:765-769`, which is the only
   existing correct composition of these objects and should be followed rather
   than re-derived.
2. `HookRegistry()`.
3. `register_canonical_run_guards(registry, CanonicalRunGuard(task_reader, repo_root=repo_root))`.
4. `HarnessService([adapter], hooks=registry)`.

`task_reader` is the caller's existing `TaskStore`. It already satisfies the
`CanonicalRunSource` protocol by duck typing — verified member by member:
`get_task` (`runtime/state/base.py:249`), `get_run_manifest`
(`runtime/state/integrity.py:378`), `compute_task_revision`
(`integrity.py:108`), `check_run_stale` (`integrity.py:402`),
`resolve_run_session` (`runtime/state/run_lineage.py:227`). **No second store is
opened and no new persistence appears** — which is what keeps this inside master
roadmap §7's "no second authority database" non-goal.

`run_recovery_tick` / `run_recovery_tick_isolated` gain one optional keyword
(name to be settled at implementation; `harness_project_id` reads best), default
`None`, threaded through to `RecoverySupervisor(harness_service=...)`. When
`None` — every caller that does not deliberately opt in, including the
`claim`-piggyback path — nothing is constructed and behavior is byte-identical
to today. This mirrors `validation_repo_root` exactly.

### 3c. CLI surface

One new flag on `recovery-tick` only:

```
maps recovery-tick --enforce-canonical-run --harness-project-id PROJ --repo-root PATH
```

- **Never on the `claim` piggyback.** `cli.py:376` passes no opt-in flags today
  and must not start. The piggyback is best-effort and latency-sensitive; giving
  it enforcement authority over resumes it did not ask for repeats exactly the
  mistake PR #165's own comments were written to avoid.
- **`--repo-root` is required when enforcement is on, and must not be defaulted.**
  `CanonicalRunGuard.__init__` takes `repo_root` and resolves it, and
  `_require_current_run` passes it to `check_run_stale`. `recovery-tick`'s
  existing `--repo-root` deliberately has no default (`cli.py:178-191`).
  Reusing that same value is correct — it is the same checkout — but the two
  opt-ins must stay **separate flags**: `--repo-root` alone must keep meaning
  only "advisory validation", or PR #172's opt-in silently acquires enforcement
  power it was never reviewed for. Missing `--repo-root` with
  `--enforce-canonical-run` should be a loud argument error, never an inferred
  cwd.
- **`--harness-project-id` is required and is not inferred.** This is a genuine
  structural constraint, not boilerplate: `HcomHarnessAdapter` is bound to a
  **single** `project_id` (`adapters/hcom.py:53-60`), and `HarnessService` keys
  adapters by `adapter_id` (`"hcom"`), so **at most one hcom adapter can be
  registered per service**. A `tick()` pass, by contrast, can span incidents from
  several projects. Deriving the project from the first incident would be a
  guess, and this project does not guess bindings (`cli.py:55-68`).

  The multi-project consequence is **not** benign, and getting this backwards
  understates the blast radius, so it is spelled out. An incident from a
  different project does eventually produce `PROJECT_MISMATCH` from
  `HcomHarnessAdapter._project_error` (`adapters/hcom.py:93-100`), and that code
  is **not** in `_CANONICAL_DENIAL_CODES`, so `tick()` would fall through to the
  pre-existing direct resume (`supervisor.py:459-465` comment). But it only ever
  gets that far if it first survives the guard:

  - `HarnessService.resume` runs `_require_canonical_enforcement` at
    `service.py:294` and `self.hooks.run(BEFORE_RESUME, ...)` at `service.py:300`
    — both **before** `adapter.resume(binding)` at `service.py:311`.
  - The adapter's project check is reached only inside `_binding_session`
    (`adapters/hcom.py:294-299`), i.e. after the guard has already returned.
  - Neither earlier project comparison rejects an out-of-project incident:
    `HarnessService._validate_binding_session` compares `binding.project_id`
    against `session_ref.project_id`, and `CanonicalRunGuard._base_evidence`
    compares the task's `project_id` against the binding's. In
    `_resolve_harness_binding` all three are read from the *same* `task`
    record (`supervisor.py:170-171, 199-207`), so all three are equal by
    construction and none of them can fire.

  So an out-of-project incident is **fully subject to canonical denial** and
  reaches the benign `PROJECT_MISMATCH` fallback only if it passes every guard
  check first. Enforcement is not scoped to `--harness-project-id`; only the
  eventual adapter call is. This makes the §2c gate conclusion stronger, not
  weaker, and it is the single most important thing for the implementer not to
  assume away.

### 3d. Which guards are registered

**`CanonicalRunGuard` only. `DestructiveExternalActionGuard` is deliberately
left out of this slice**, and the reason is mechanical, not cautious:

`HarnessService` fires exactly five events — `RUN_STARTING`, `RUN_STARTED`,
`BEFORE_SEND`, `BEFORE_RESUME`, `SESSION_STOPPING` (`service.py:181, 197, 253,
300, 333` — the only five `hooks.run(...)` call sites in `runtime/`).
`register_destructive_external_action_guards` registers on
`BEFORE_DESTRUCTIVE_ACTION` and `BEFORE_EXTERNAL_ACTION`
(`destructive_action_guard.py:129`). **Nothing in `runtime/` fires either event
through a registry** — the only five `hooks.run(...)` call sites in `runtime/`
are the `HarnessService` ones listed above, and neither destructive event is
among them. (Two tests do fire them directly against a bare registry —
`tests/test_harness_hooks.py:68` and
`tests/test_destructive_external_action_guard.py:132` — which is how the guard
is proven; an earlier draft of this note wrongly said "no code anywhere, tests
included". The load-bearing half is the production half, and it holds.)

So registering it here would be a guaranteed no-op — and a harmful one, because
`HookRegistry.has_enforcement(…, DESTRUCTIVE_EXTERNAL_ACTION)` would start
returning True, which is a truthful-looking signal that no operation actually
consults. Composing the registry does **not** oblige wiring every guard into it.
SEC3's first call site remains its own follow-up, exactly as PR #164's design
states, and it needs an *emitter* of those events, not a registration.

---

## 4. Non-goals

Explicit, and each is a boundary the implementation PR must be checkable against:

1. **No new guard types.** `CanonicalRunGuard` and
   `DestructiveExternalActionGuard` are used exactly as they are. No subclass,
   no wrapper, no variant.
2. **No daemon, scheduler, cron entry, thread, or long-lived process.** Master
   roadmap §7.1/§7.9. The composed objects live for one bounded CLI pass and are
   discarded, following PR #165's precedent.
3. **No change to `tick()`'s internal decision logic.** The `harness_service is
   not None` branch, `_resolve_harness_binding`, `_CANONICAL_DENIAL_CODES`, the
   fallback rules, and the retry/backoff arithmetic are all untouched. This
   design supplies a non-`None` argument to a parameter that already exists; it
   does not alter what the supervisor does with it.
4. **No change to `HookRegistry` / `HookEnforcement` / `HookSpec` /
   `HarnessService` internals.** No new enforcement role, no new event, no
   change to `_register_enforcement`'s validation or to `run()`'s failure
   handling.
5. **No second authority database and no new persistence.** The existing
   `TaskStore` is reused as `CanonicalRunSource`; no store is opened, no table
   added, no state file written beyond the `RecoveryStore` writes `tick()`
   already performs.
6. **No policy engine, rules DSL, or config file.** Guard selection is literal
   construction code.
7. **No change to `maps claim`.** Its piggybacked pass stays enforcement-free.
8. **No roadmap row flipped to DONE.** This note is a design; the rows close
   when the implementation and its first real production exposure land.

---

## 5. Open behavior questions for the implementation follow-up

Recorded as genuinely open, not as rhetorical questions with an implied answer.

1. **Scope: minimum viable composition root vs. full guard rollout.**
   §3d recommends `CanonicalRunGuard` only, on the mechanical grounds that
   `DestructiveExternalActionGuard`'s two events are fired by nothing in
   `runtime/` (two tests fire them directly; no production path does). Should
   the implementation PR nonetheless register it to "establish the pattern"?
   *Recommendation: no* — a `has_enforcement` that reports True for a role
   nothing consults is worse than an honest gap. But this is a judgment about
   how much scaffolding is healthy, and the implementer should confirm the
   grep result still holds at their head before relying on it.

2. **Should the opt-in be per-flag or per-mode?** §3c proposes
   `--enforce-canonical-run` + `--harness-project-id` + required `--repo-root`.
   An alternative is a single `--harness-project-id` whose presence implies
   enforcement (fewer flags, but couples two decisions). *Leaning:* keep them
   separate, so "compose a harness service" and "let it deny" stay independently
   reviewable — but this is genuinely a taste call.

3. **Is a shadow/observe mode worth a follow-up slice?** §2c establishes it is
   impossible today without changing `tick()` or the service's
   enforcement-before-run ordering, both non-goals here. An operator who wants
   to know "which incidents *would* be denied" currently has to run an enforced
   pass, which really denies and really consumes retry budget. Is a
   `harness_resume`-only dry run worth a later, separately-reviewed change to
   `tick()`? *Not answered here.*

4. **Retry-budget interaction.** §2b shows repeated canonical denials drive an
   incident to `failed` / `retry_budget_exhausted`. Is that the intended
   terminal state for "this run is no longer canonically resumable", or should a
   canonical denial be distinguished from a transient failure (e.g. not consume
   an attempt)? Changing that is a `tick()` decision-logic change and therefore
   out of scope here — but the first operator to run an enforced pass will hit
   it, so it should be decided before enforcement is recommended for routine use.

5. **Should `LEASE_EXPIRED` specifically be reconsidered?** Denying resume for an
   expired lease is defensible and probably correct, but it is also the single
   most likely denial on the recovery path (§2b), which means it dominates the
   first-exposure experience. Is the right operator workflow "renew the lease,
   then re-run the pass"? That workflow is not currently documented anywhere,
   and if it is the answer, it belongs in the implementation PR.

6. **Does 6.16/E6's worktree-binding seam (PR #175) land before or after this?**
   Pass #8 §5a ranks it second and notes it should land "after or with" this
   item. Landing it first produces a stricter `CanonicalRunGuard` that still
   never runs; landing it after means the first enforced production pass uses
   the pre-#175 staleness definition. Sequencing is an ordering call for whoever
   dispatches both.

7. **`--harness-project-id` for a genuinely multi-project deployment.** §3c
   accepts that out-of-project incidents fall through to direct resume. If
   multi-project ticks become normal, the honest fix is per-project passes, not
   multiple adapters (the service keys by `adapter_id`, so it cannot hold two
   hcom adapters). Worth confirming that single-project-per-pass is acceptable
   before building on it.

---

## 6. Checklist impact

Deliberately recorded, because trajectory pass #8 §2 identified three
consecutive PRs (#165, #171, #172) shipping code with no
`work/roadmaps/CAPABILITY_CHECKLIST.md` edit, and named that skipped step as the
common cause of six falsified rows.

**Checked; no edit warranted by this note.** This is a design-only note that
changes no runtime behavior, so it does not falsify any evidence text. The four
affected rows were corrected by PR #176 one commit ago and were re-read at this
head: **H5** already states that `run_recovery_tick` "deliberately passes
`harness_service=None`" and that "`HarnessService(...)` has zero non-test callers
anywhere in the repo"; **E4** already records that "no `HookRegistry` in
production carries a validation callback"; **6.16** already carries the
composition-layer finding. **6.5** does not state it in its own text, but it is
written as "= H4/E4" and inherits it by reference, so it is not falsified
either. Those descriptions remain exactly accurate. The rows
become editable when the *implementation* lands — and per pass #8's process
finding, that edit belongs in the implementation PR itself, not a fast-follow.

---

## Resume prompt

Implement the Hook/Harness production composition root designed in
`work/notes/2026-08-26-hook-enforcement-composition-root-design.md`. Add
`build_canonical_harness_service(task_reader, *, project_id, repo_root)` to
`runtime/recovery/production.py` (construct `HcomHarnessAdapter` →
`HookRegistry()` → `register_canonical_run_guards(registry,
CanonicalRunGuard(task_reader, repo_root=repo_root))` → `HarnessService([adapter],
hooks=registry)`; reuse the caller's existing `TaskStore` as the
`CanonicalRunSource`, open no second store). Thread one optional keyword through
`run_recovery_tick` / `run_recovery_tick_isolated` to
`RecoverySupervisor(harness_service=...)`, defaulting `None` so every non-opted-in
caller — including the `maps claim` piggyback, which must never opt in — stays
byte-identical to today. Add `--enforce-canonical-run` and
`--harness-project-id` to `maps recovery-tick` only, requiring the existing
`--repo-root` when enforcement is on (loud argument error if absent; never infer
cwd) while leaving `--repo-root` alone still meaning advisory validation only.
Register **`CanonicalRunGuard` only** — `DestructiveExternalActionGuard`'s two
events (`BEFORE_DESTRUCTIVE_ACTION`, `BEFORE_EXTERNAL_ACTION`) are fired by
nothing in `runtime/`, so registering it would make `has_enforcement` report a
role nothing consults; re-run that grep to confirm before relying on it. Note
also that enforcement is **not** scoped to `--harness-project-id`: the guard runs
at `service.py:300`, before the adapter's `PROJECT_MISMATCH` check is ever
reached, so out-of-project incidents are fully subject to denial (§3c).
Enforcement
**must default off**: `CanonicalRunGuard` never returns `ALLOW` and denies on
absent evidence, so its first production exposure will convert currently-working
resumes into `resume_denied` (most likely via `LEASE_EXPIRED`) and, on repeat,
into `failed`/`retry_budget_exhausted` — see §2b. Respect §4's non-goals: no new
guard types, no daemon, no change to `tick()`'s decision logic, no change to
`HookRegistry`/`HookEnforcement` internals, no second store. **Edit
`work/roadmaps/CAPABILITY_CHECKLIST.md`'s H5, E4, 6.5 and 6.16 rows in the
implementation PR itself** — pass #8 §2 found three consecutive PRs skipping that
step, and those rows currently assert zero non-test `HarnessService` callers,
which the implementation falsifies. Settle §5 questions 4 and 5 (retry-budget
interaction and the expired-lease operator workflow) before recommending
enforcement for routine use. Get an independent reviewer; do not self-certify.
