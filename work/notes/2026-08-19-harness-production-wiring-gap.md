# Harness production-wiring gap — design note

Date: 2026-08-19
Owner: `agent/harness-production-wiring-gap-wave14`
Status: planning evidence + recommended direction (no code)

## Why this note exists

Several roadmap phases are marked `IN PROGRESS` in
`work/roadmaps/CAPABILITY_CHECKLIST.md`, each restating a variant of the same
blocker in its own words: "the mechanism exists, but nothing in production
calls it yet." Read individually, each looks like a separate small gap. Read
together, they are the same gap five times. This note documents that single
root cause once, lays out the concrete options for closing it, and — per
explicit operator direction relayed for this task — recommends one direction
rather than presenting an open menu. The structural template
(root-cause-by-direct-read, enumerated options, explicit reasoning) is still
`work/notes/2026-08-17-recovery-equivalence-authority-design.md`; the
difference from that note is deliberate: that note's operator had not yet
weighed in on its open questions, while this note's recommendation is made
under an explicit "reason through it and decide, don't defer" mandate for
this specific task.

This document is **descriptive and proposal-only**. It does not change any
`CAPABILITY_CHECKLIST.md` row status, and it does not touch any `runtime/`
or `tests/` file. Recommending a direction here is not the same as
implementing it: no code changes in this note, and the recommended
direction still requires its own scoped implementation task with its own
independent review before anything in `runtime/` moves.

## Root-cause finding, verified by direct read

```
$ grep -rln "ExecutionBinding(" runtime/ --include=*.py
$ grep -rln "HarnessService(" runtime/ --include=*.py
```

Both commands return **zero matches inside `runtime/`**. `ExecutionBinding`
and `HarnessService` are each constructed only inside `tests/`:

```
$ grep -rln "ExecutionBinding" --include=*.py .
tests/test_agentic_security_hook_context.py
tests/test_recovery_supervisor.py
tests/test_harness_types.py
tests/test_harness_service.py
tests/test_harness_adapter_contract.py
tests/test_harness_hcom_adapter.py
tests/test_agentic_security_baseline.py
tests/test_harness_canonical_guard.py
runtime/harness/types.py       <- defines the type
runtime/harness/__init__.py    <- re-exports it
runtime/harness/service.py     <- type-annotates parameters with it
runtime/harness/contract.py    <- type-annotates parameters with it
runtime/harness/protocol.py    <- type-annotates parameters with it
runtime/harness/adapters/hcom.py <- type-annotates parameters with it
```

Every non-test hit is `runtime/harness/*` itself defining or annotating the
type — never instantiating one for a real operation. `HarnessService(...)` is
identical: every construction is inside `tests/test_harness_*.py` or
`tests/test_agentic_security_*.py`, using a `DummyAdapter`, never a real
adapter driving real work.

**This is stronger than "adapters are still incomplete."** It means
`runtime/harness/service.py`'s `HarnessService` — and everything built to
sit downstream or alongside it (`runtime/harness/adapters/hcom.py`,
`runtime/harness/hooks.py`'s registered guards, `runtime/harness/config_ref.py`,
`runtime/environment/validation.py`'s Hook-callback factory) — currently has
**no real caller anywhere in this codebase**. The Harness layer (H1–H3 and
the foundational pieces of H4/H5/L6/SEC3) was built and is internally
correct and tested, but it has never been connected to how MAPS actually
executes work.

### The five blocked phases this explains

All five state, in their own words, exactly this same gap:

- **H4 — Immediate validation hooks** (`work/roadmaps/CAPABILITY_CHECKLIST.md`
  line 25): `runtime/environment/validation.py` "gives `EnvironmentSpec.validation`
  tiers a real executor and a Hook-callback factory; no production call site
  invokes it yet."
- **E4 — Validation tiers** (line 48): "same evidence as H4 ... this task adds
  the first executor + Hook wiring, but no real caller (`HarnessService` or an
  adapter) invokes it yet."
- **H5 — Remaining adapters + contract suite** (line 26): the contract suite
  half is done (`AdapterContractMixin` proves hcom satisfies the shared
  contract); the "remaining adapters" half is not — `runtime/helpers/ollama.py`
  /`aider.py` and `runtime/recovery/supervisor.py` "remain unwrapped,
  deliberately out of scope (their one-shot invocation shape doesn't naturally
  fit the session-lifecycle protocol)."
- **L6 — Harness configuration identity** (line 74): `runtime/harness/config_ref.py`
  and `ExecutionBinding.harness_config_hash` exist, "but no production call
  site actually sets/persists the hash onto a real run manifest yet."
- **L7 — Comparative harness evaluation** (line 75, `NOT STARTED`): "still
  depends on L6's hash actually being persisted on real runs (not yet
  wired)."
- **SEC3 — Security hooks** (line 59): only `HookEnforcement.CANONICAL_RUN`
  has a registered guard; `HookEvent.BEFORE_EXTERNAL_ACTION` and
  `BEFORE_DESTRUCTIVE_ACTION` are declared enum values with zero registered
  guards, and — per this note's own finding — nothing invokes any
  `HarnessService` operation in production at all, so there is currently no
  live call site for those guards to even fire against.

Fixing "wire up a production call site for `HarnessService`" once would move
all five simultaneously, rather than each phase separately re-deriving the
same blocker.

## Historical intent: why was this built if nothing calls it?

`work/tasks/harness-foundation-wave1.md`, `harness-service-wave1.md`, and
`harness-canonical-guard-wave1.md` (the tasks that built H1–H3) each scope
themselves explicitly as foundation-only:

- `harness-foundation-wave1.md`, Notes/decisions: "This tranche deliberately
  does not implement hcom/helper adapters or Hooks yet."
- `harness-service-wave1.md`, Notes/decisions: "Durable run/session lineage
  is still separate future work; this tranche enforces explicit correlation
  at call time only."
- `harness-canonical-guard-wave1.md`, Notes/decisions: "Late session
  attachment and adapter-qualified durable lineage remain deferred rather
  than being smuggled into this guard."

None of the three original task docs commits to a specific plan for *which*
production code would eventually call `HarnessService`. The pattern across
all three is deliberate layer-by-layer construction (types → service →
guard → adapter → contract-suite → config-identity → validation-tiers) with
each wave explicitly deferring "wire this into a real caller" to later,
unspecified work. `harness-adapter-contract-suite-wave7.md` (H5's own task
doc) is the first to name the obstacle explicitly: the one-shot invocation
shape of helpers/recovery "doesn't naturally fit the session-lifecycle
protocol," which is presumably why no wave since has picked up "connect it"
as its own scoped task. This note is the first document that treats "connect
it" as the work item in its own right rather than an implicit follow-up.

## How MAPS actually executes work today, verified by direct read

There are exactly two execution paths in this repo, and neither goes through
`HarnessService`.

### 1. Bounded helpers — one-shot subprocess, no session lifecycle

`runtime/helpers/README.md` states the model precisely: a helper "accelerates
work inside an already-active task. [It does] not become the task owner,
reviewer, approver, or completion authority." Concretely, per
`runtime/helpers/ollama.py` (`OllamaHelper.run`) and
`runtime/helpers/aider.py` (`AiderHelper.run`):

- both validate the caller's task is `ACTIVE` and the target paths fit the
  task's declared `output_paths` (`validate_active_scope`);
- both invoke the underlying tool with a single blocking
  `subprocess.run(..., check=False)` call and a fixed timeout — `ollama run
  <model>` with the prompt on stdin, or `aider --message ... --no-auto-commits
  --no-dirty-commits --no-stream <targets>`;
  they return once the subprocess exits; there is no "session" object, no
  attach/resume/heartbeat, and no notion of an in-flight, addressable
  execution to reconnect to;
- both append one `HelperResult` record to `.maps/state/helper-runs.json`
  (`HelperRunStore`) and return it. That record is evidence of an
  invocation, explicitly **not** canonical lifecycle state.

There is no `SessionRef`, no `ExecutionBinding`, no adapter, and no Hook
anywhere in this path. The helper *is* the entire operation, start to finish,
inside one function call.

### 2. Recovery-and-supervision (RnS) — direct hcom session resume, bypassing the harness adapter that already exists for it

`runtime/recovery/supervisor.py`'s `RecoverySupervisor` is constructed with
`hcom: HcomAdapter` (from `runtime/communication/`) and calls
`self.hcom.list_sessions(...)` and `self.hcom.resume(session_name, headless=True,
go=True)` directly. It never imports or constructs anything from
`runtime.harness`.

This matters more than a simple "not migrated yet" gap: `runtime/harness/
adapters/hcom.py`'s `HcomHarnessAdapter.resume()` — the harness-layer adapter
that already exists and specifically wraps `HcomAdapter` for exactly this
kind of operation — is implemented as an explicit `_unsupported()` stub
today: `"hcom resume mode is not normalized yet; no headless/terminal
behavior is guessed."` So even if RnS were changed to call through
`HarnessService.resume()` today, the call would immediately fail — the
adapter method deliberately refuses to guess RnS's `headless=True, go=True`
semantics rather than inventing a mapping no one has confirmed is correct.
(`HcomHarnessAdapter.start()`, `.heartbeat()`, and `.collect()` are
similarly `_unsupported()` today, for the same reason: normalizing them
without a confirmed real caller would mean guessing behavior, which
`AGENTS.md` and this repo's own conventions treat as worse than leaving
them unimplemented.)

### 3. `runtime/cli.py` — pure task-state CRUD, no execution loop at all

`runtime/cli.py`'s subcommands are exhaustively: `init`, `create`, `shape`,
`check`, `promote`, `show`, `trace`, `run-record`, `freeze-case`, `context`,
`status`, `claim`, `heartbeat`, `submit`, `review-claim`, `review-record`,
`outcome-record`, `outcomes`, `events`, `reviews`. Every one of these reads
or mutates task/run/review state in `.maps/state/*`. None of them starts,
attaches to, sends to, or stops an agent session. The actual "worker" in
this system is an external process — an agent (such as a Claude Code
session, including the one that wrote this note) that calls this CLI to
claim/heartbeat/submit work, while doing its actual work (editing files,
running tools, talking to hcom) entirely outside anything this repo's code
drives or observes as a session.

**This is the direct answer to "why doesn't anything call `HarnessService`":**
nothing in MAPS today has a session-lifecycle-shaped hole to fill. Helpers
are one-shot and stateless-between-calls. RnS treats hcom sessions as an
external fact to poll and nudge, not something it opens/attaches/manages
through a typed contract. The CLI has no execution loop; the "loop" is a
human-or-agent process outside the repo, driving the CLI by hand (or by
being one). `HarnessService` was built to be the provider-neutral surface
*for* a session-lifecycle-shaped caller — and no such caller currently
exists in this codebase.

## Options for a first real production call site

These are independent, not mutually exclusive stages of one plan — each
would need its own scoped implementation task and its own independent
review regardless of which is chosen. All four were evaluated below;
**Option B is the recommended direction** (see "Recommendation" after the
option list for the reasoning).

### Option A — Migrate `runtime/helpers/ollama.py`/`aider.py` to be `HarnessAdapter` implementations, routed through `HarnessService`

**What would change:** `OllamaHelper`/`AiderHelper` would need to implement
the `HarnessAdapter` protocol (`start`/`attach`/`inspect`/`send`/`heartbeat`/
`resume`/`stop`/`collect` per `runtime/harness/protocol.py`), and their
current single `.run(...)` call would need to be decomposed into that
lifecycle shape, or `.run(...)` would need to internally call
`HarnessService.start()` then synchronously poll/collect and call
`HarnessService.stop()`/`collect()` before returning.

**Concretely, what the awkwardness looks like:** a helper subprocess call is
already complete by the time `subprocess.run()` returns — there is no
"session" to `attach()` to later, no `heartbeat()` to send mid-run (the
process either is or isn't still executing, observable only by
`subprocess.run`'s own blocking return), and no `resume()` semantics at all
(a helper invocation that times out or fails is retried as a brand-new
invocation, not resumed). Most of the eight `HarnessAdapter` methods would
be forced into the same shape as `HcomHarnessAdapter`'s current stubs —
`_unsupported()` — because the underlying reality genuinely has no
concept of those operations. `start()` would likely have to *be* the whole
synchronous subprocess run (violating the "start returns promptly, session
becomes addressable" shape the protocol otherwise implies for hcom), and
`collect()` would have nothing asynchronous to collect. This is the same
"doesn't naturally fit the session-lifecycle protocol" observation
`work/tasks/harness-adapter-contract-suite-wave7.md` already made when H5
deliberately scoped helpers out.

**Risk/blast radius:** touches `runtime/helpers/ollama.py`,
`runtime/helpers/aider.py`, both helpers' test suites, and
`runtime/harness/adapters/` (new adapter modules). Helper safety properties
(scope validation, clean-worktree requirement, no-auto-revert) would need to
be preserved exactly through the adapter wrapper — a regression here
directly risks the guarantees `runtime/helpers/README.md` documents as load
bearing. Moderate-to-high risk for a fit that is, by the protocol's own
shape, forced rather than natural.

**What it would unblock:** H5 ("remaining adapters") directly. Indirectly
gives H4/E4 a call site (validation tiers could run as part of `start()`),
SEC3 a call site (`BEFORE_EXTERNAL_ACTION`/`BEFORE_DESTRUCTIVE_ACTION` guards
could fire around subprocess invocation), and L6 a call site (config hash
could be set on the binding before `start()`). Does not by itself unblock
L7 (L7 needs the hash actually persisted onto a run manifest, a separate
step from having *a* call site).

### Option B — Migrate `runtime/recovery/supervisor.py`'s hcom resume calls to go through `HcomHarnessAdapter`/`HarnessService` instead of `HcomAdapter` directly

**What would change:** `RecoverySupervisor` would construct/receive a
`HarnessService` wrapping a `HcomHarnessAdapter` instead of a raw
`HcomAdapter`, and `tick()`'s `self.hcom.resume(session_name, headless=True,
go=True)` call would become
`harness_service.resume(binding, session_ref)`. This is blocked
immediately on a prerequisite this option must also do:
**`HcomHarnessAdapter.resume()` is currently `_unsupported()`** and would
need to be implemented for real (deciding what `headless=True, go=True`
means as normalized harness semantics) before RnS could call it. The same
applies to `list_sessions`/`session_is_live` style polling, which currently
happens via `self.hcom.list_sessions(...)` directly and has no
`HarnessService`-level equivalent today (`inspect()` exists but is
per-session, not a listing operation).

Additionally, `HcomHarnessAdapter.attach()` requires a `lineage_writer`
already wired to durable `run_session_links` (per commit history, this now
has a real writer per PR #100) and requires `binding.run_id` to resolve via
`resolve_run_session`. RnS's existing `_resolve_run_id` already does a
comparable lookup for advisory environment evidence (per
`work/notes/2026-08-17-recovery-equivalence-authority-design.md` Stage 1),
so the run-binding infrastructure partially already exists on the RnS side,
but nothing currently connects it to `ExecutionBinding` construction.

**Risk/blast radius:** touches `runtime/recovery/supervisor.py` (a module
whose current behavior is deliberately conservative — "resume known-live
sessions for already-active work; never mutate task truth," per its own
docstring) and `runtime/harness/adapters/hcom.py`'s currently-stubbed
`resume()`/possibly `heartbeat()`. This is a live-production-behavior-changing
module in the retry/backoff/recovery path — a subtle bug here has direct
operational consequences (missed or duplicate resumes). Also directly
touches SEC3-relevant territory: RnS resuming a session is exactly the kind
of "resume" operation `HookEvent.BEFORE_RESUME` + `HookEnforcement.CANONICAL_RUN`
already gate in `HarnessService.resume()` — routing RnS through the harness
would, for the first time, subject RnS's resume action to the canonical-run
guard, which is a behavior change (today RnS's resume is gated only by its
own task/claim/session-liveness checks, not by any Hook).

**What it would unblock:** H5 ("remaining adapters," recovery-supervisor
half). Immediately gives SEC3 a real, already-consequential call site for
`BEFORE_RESUME`/`CANONICAL_RUN` enforcement (this event/enforcement pair
already exists and is tested — RnS would be its first live-traffic user, not
BEFORE_EXTERNAL_ACTION/BEFORE_DESTRUCTIVE_ACTION which still have zero
guards regardless). Gives H4/E4 a call site if validation tiers are wired
into the resume path. Gives L6 a call site if the config hash is set on the
binding RnS constructs. Same L7 caveat as Option A — a call site alone
doesn't persist the hash onto a run manifest.

### Option C — A genuinely new worker-loop entrypoint that treats an interactive agent session as what `HarnessService.start()`/`attach()` models

**What this would mean:** a new piece of code in this repo that itself opens
("starts") an agent session (e.g., spawns or attaches to a Claude Code / hcom
session) as the executor of a claimed task, using `HarnessService` as the
lifecycle surface for that session, rather than the current model where an
external agent session calls `runtime/cli.py` from outside the repo.

**Is this coherent given the repo's actual current usage pattern?** Not
without a genuine architecture change, and this note does not treat it as
free to pursue. Every other execution path in this codebase (helpers, RnS,
the CLI itself) is built on the premise that MAPS is *called by* an external
agent process, never that MAPS *drives* one. `runtime/cli.py`'s existence as
a pure CRUD surface — with claim/heartbeat/submit as its full worker-facing
API — is itself evidence of this premise; nothing about it hints at MAPS
ever holding the driver's seat. Building Option C would mean MAPS
transitioning from "task-state authority that agents check in with" to
"orchestrator that spawns and manages agent sessions," which is a materially
larger architectural shift than "wire an existing type into an existing
caller" (Options A/B). It is the option most likely to require its own
separate authority/scope design (in the same vein as the
recovery-equivalence note's staged approach), not a wiring task.

**Risk/blast radius:** largest by far — new code, new failure modes (a
session MAPS itself started can now fail in ways the current
externally-driven model never has to reason about), and a scope change that
arguably belongs at the roadmap-phase level, not inside a "wire up the
harness" task.

**What it would unblock:** in principle, all five (it would be a genuinely
natural `HarnessService` caller, unlike A/B which are forced fits). In
practice, this is very unlikely to be the *first* call site given its size,
and this note takes no position on whether it should be pursued at all.

### Option D — a smaller variant worth naming: a purely observational Hook/validation call site, decoupled from any adapter migration

One thing distinct from A/B/C surfaced while reading `runtime/environment/
validation.py`: H4/E4's exit gate is about validation tiers running and
catching failures, not specifically about `HarnessService` being the caller.
It is possible in principle to invoke the validation-tier executor and
Hook-callback factory from some other call site (e.g., directly inside RnS
or a helper, without going through `HarnessService.start()`/adapters at
all) purely to get H4/E4's exit gate met, decoupled from the harder
adapter-fit question in A/B. This note flags it as a *possible* narrower
path but does not evaluate it in depth — it still requires picking a real
call site and integrating it into a live code path, so it carries the same
"who decides where" question as A/B, just with a smaller footprint. It would
not, by itself, address H5, L6/L7, or SEC3.

## Recommendation: Option B (migrate RnS's hcom resume path through `HcomHarnessAdapter`/`HarnessService`)

Weighing the four options against fit, risk, and how many of the five
blocked phases each actually moves:

- **Option A (migrate helpers)** is rejected as the first move. Helpers are
  structurally a poor fit for the `HarnessAdapter` protocol — a one-shot
  blocking subprocess call has no natural `attach`/`heartbeat`/`resume`
  semantics, so most of the eight protocol methods would become forced
  `_unsupported()` stubs with no real behavior behind them. Forcing that fit
  just to satisfy H5's letter risks producing an adapter that exists on
  paper but adds no real capability — the same "don't guess a shape nobody
  confirmed" concern `work/tasks/harness-adapter-contract-suite-wave7.md`
  already raised when it deliberately scoped helpers out.
- **Option C (new worker-loop entrypoint)** is rejected for now. It is a
  materially larger architectural shift — MAPS moving from "called by an
  external agent" to "driving agent sessions itself" — than a wiring task
  should attempt to smuggle in. It is out of proportion to the problem this
  note is scoped to (closing five specific IN-PROGRESS gaps), and it would
  make more sense as its own future roadmap-level proposal if MAPS's
  execution model is ever deliberately revisited.
- **Option D (narrow validation-only call site)** is a reasonable
  complement, not a substitute: it could close H4/E4 in isolation with the
  smallest footprint, but by itself it does not touch H5, L6/L7, or SEC3,
  so it does not resolve the shared root cause — only one of its five
  symptoms.
- **Option B (migrate RnS)** is the best fit of the four. Unlike helpers,
  RnS already treats hcom sessions as long-lived, resumable, pollable
  entities — that is exactly the session-lifecycle shape `HarnessService`
  models. RnS already does a comparable run-binding lookup for advisory
  environment evidence (`_resolve_run_id`, per the 2026-08-17
  recovery-equivalence note's Stage 1), so the surrounding infrastructure
  for constructing a real `ExecutionBinding` partially already exists. It
  gives SEC3 its first genuinely live call site for the
  `CANONICAL_RUN`/`BEFORE_RESUME` guard pair that H1–H3 already built and
  tested but has never run against real traffic. It gives H4/E4 and L6
  natural places to hook in (validation tiers before a resume attempt;
  config hash set on the binding RnS constructs) as fast-follow work once
  the base wiring lands. It's the option where the harness's session model
  and the target code's actual behavior already resemble each other, rather
  than one where the model has to be bent to fit.

**Recommended path:** treat Option B as the first production call site,
staged as its own implementation task (not this note). That task's minimum
scope: (1) implement `HcomHarnessAdapter.resume()` for real — deciding what
RnS's current `headless=True, go=True` call means as normalized harness
semantics, since the adapter currently refuses to guess this; (2) construct
a real `ExecutionBinding` inside `RecoverySupervisor.tick()` using the
run-binding lookup that already exists; (3) route the resume call through
`HarnessService.resume()` instead of `HcomAdapter.resume()` directly,
accepting that this activates `CANONICAL_RUN`/`BEFORE_RESUME` gating on RnS
resume attempts for the first time — a real behavior change that the
implementation task must call out explicitly and verify does not silently
suppress recoveries that should succeed. Option D (validation-tier wiring)
is a reasonable fast-follow once B's plumbing exists, since by then a real
call site already exists to attach it to. Options A and C are not
recommended at this time; this note does not treat that as permanent —
either could be revisited later if the tradeoffs above no longer hold (e.g.
if MAPS's execution model changes in a way that makes C coherent).

This is a recommendation, not an implementation. Landing it requires its
own scoped task with its own change boundary and its own independent
review — this note authorizes none of that work by itself.

## What is safe to build right now, independent of this recommendation

Nothing in `runtime/` or `tests/` changes as part of this note. The
concrete next step this note points to (implementing
`HcomHarnessAdapter.resume()` and routing `RecoverySupervisor.tick()`
through `HarnessService`) is itself the first real code change, and per the
scope given for this task it is explicitly **not** performed here — it is
left for a dedicated follow-up implementation task so that the code change
gets its own change boundary and its own independent review, separate from
this research note.

## Decision authority

### Owner (this note) may decide

- That all five phases (H4/E4, H5, L6/L7, SEC3) share one root cause,
  verified by direct grep evidence above.
- That helpers and RnS are the only two production execution paths that
  exist today, and that neither currently constructs an `ExecutionBinding`
  or calls `HarnessService`.
- That `HcomHarnessAdapter.resume()`/`start()`/`heartbeat()`/`collect()`
  being `_unsupported()` today is a real prerequisite blocker for Option B,
  not a detail to gloss over.
- That Option B is the recommended first production call site, for the
  reasons stated above (this recommendation was made under explicit
  direction for this task to decide rather than defer; see note header).
- That no runtime/test file or `CAPABILITY_CHECKLIST.md` row is touched by
  this note.

### Left to the follow-up implementation task

1. **Exact normalized semantics for `HcomHarnessAdapter.resume()`/
   `heartbeat()`** — what RnS's current `headless=True, go=True` call and
   liveness polling should mean as harness-contract operations. Not
   guessed here; the adapter's existing `_unsupported()` stance is
   deliberate until this is worked out concretely.
2. **Whether `CANONICAL_RUN`/`BEFORE_RESUME` gating activating on RnS's
   resume path changes observed recovery success rates**, and what to do
   if it does — this must be verified empirically once real wiring exists,
   not assumed safe in advance.
3. **Sequencing of the H4/E4 (validation-tier) and L6 (config-hash)
   fast-follow work** relative to the base Option B wiring — this note
   recommends they follow once B's call site exists, but does not schedule
   them.

## Continuation

```text
this note (descriptive research + recommended direction, no code,
no checklist change)
        ↓
follow-up implementation task: Option B base wiring
  (own change boundary, own independent review)
        ↓
fast-follow: H4/E4 validation-tier hook-in, L6 config-hash persistence
  (own change boundary(ies), own independent review(s))
        ↓
H4/E4/H5(recovery half)/L6/L7/SEC3 checklist rows updated as each lands
  (not by this note)
```
