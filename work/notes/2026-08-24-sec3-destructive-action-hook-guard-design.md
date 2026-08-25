# SEC3 destructive/external-action Hook guard design

Date: 2026-08-24
Owner: `/root`
Status: design complete; no runtime behavior changed

## Finding

Re-verified the session-6 finding with a fresh grep against
`origin/main@4431b3a`. Still true:

- `runtime/harness/hooks.py::HookEvent` declares `BEFORE_EXTERNAL_ACTION` and
  `BEFORE_DESTRUCTIVE_ACTION` as enum values, but `grep -rn
  "BEFORE_DESTRUCTIVE_ACTION\|BEFORE_EXTERNAL_ACTION"` across the repo turns up
  only the enum declaration itself and `tests/test_harness_hooks.py` (generic
  `HookRegistry` ordering/deny tests that use `BEFORE_EXTERNAL_ACTION` as an
  arbitrary event name, not a real guard). No production call site fires
  either event.
- `HookEnforcement` (`runtime/harness/hooks.py`) has exactly one member,
  `CANONICAL_RUN`. `HarnessService._require_canonical_enforcement()`
  (`runtime/harness/service.py`) is the only place that gates an operation on
  an enforcement being installed, and it only checks for `CANONICAL_RUN`.
- No action/tool declaration registry exists anywhere in `runtime/` (`grep
  -rln "ToolSpec\|ToolDeclaration\|action_type\|ActionType"` returns nothing).
  There is nowhere to hang a `destructive: bool` field on an existing "action"
  object, because no such object exists yet.
- The only existing notion of "destructive" in the codebase is
  `runtime/skills/gate.py::_DESTRUCTIVE_RE` (`rm -rf`, `DROP TABLE/DATABASE`
  regex), which is static text linting of Skill *content* for the SEC4
  supply-chain gate (S5), not a runtime classification of an *action about to
  execute*. It cannot be reused for SEC3: it operates on Skill source text,
  not on a live operation the harness is about to perform.
- `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md` §7.2
  ("Destructive/external policy guard") already states the intended shape at
  the roadmap level ("inspect task policy; require operator approval if
  configured; deny if caller lacks task authority") but was never implemented.

Confirmed: SEC3's missing piece is exactly what the checklist says — a second
`HookEnforcement` type, plus a classification a guard can gate on. Neither
exists. This note designs both without touching runtime code.

## Decision: context-supplied classification, gated the same way CANONICAL_RUN is gated

Do not build an action/tool registry to hang a `destructive`/`external` flag
on. There is no existing registry to extend, and building one now would be
new infrastructure for a classification need that a two-field context
contract already satisfies (rule: smallest change that satisfies the
requirement).

Proposed mechanism:

1. **Classification is caller-declared, not inferred.** The code about to
   perform a consequential operation already knows what it is about to do
   (call a shell tool, hit a network endpoint, delete a file, resume a
   session). It states that fact explicitly in the Hook context, the same way
   `CanonicalRunGuard._extract_binding()` already reads an explicit
   `context["binding"]` mapping rather than inferring identity from
   surrounding state. Concretely, add two required boolean keys read by the
   guard:
   - `context["destructive"]` — `True` if the operation is irreversible or
     removes/overwrites state outside of normal task-scoped edits (delete,
     force-push, DB drop, kill session, etc).
   - `context["external"]` — `True` if the operation crosses the process/host
     boundary (network call, subprocess exec, sending a message/notification
     to a third party, spending money).
   These are independent booleans, not a single enum — an action can be both,
   either, or neither (e.g. `rm -rf` locally is destructive but not external;
   an HTTP GET is external but not destructive).
2. **No new taxonomy, no severity levels, no policy language.** This is
   intentionally just two flags on the existing frozen Hook context mapping
   (`_freeze_hook_value` already accepts booleans). It reuses
   `HookOutcome`'s existing `ALLOW/DENY/REQUIRE_APPROVAL/ANNOTATE` vocabulary
   for the guard's response — no new outcome type.
3. **A new `HookEnforcement` member: `DESTRUCTIVE_EXTERNAL_ACTION`.** Add it
   next to `CANONICAL_RUN` in `runtime/harness/hooks.py`. A guard registers
   for `BEFORE_DESTRUCTIVE_ACTION` and/or `BEFORE_EXTERNAL_ACTION` via the
   existing `HookRegistry._register_enforcement()` path (already generic over
   `HookEnforcement`; no registry code changes needed beyond adding the enum
   member).
4. **A concrete guard, same shape as `CanonicalRunGuard`.** A new
   `DestructiveExternalActionGuard` (or similarly named class) in
   `runtime/policy/`, read-only, `FAIL_CLOSED`, mirroring
   `CanonicalRunGuard`'s style: reads `context["destructive"]` /
   `context["external"]`, and where either is `True`, applies the §7.2
   roadmap policy — deny if the caller's task/binding does not carry explicit
   authority for that action class, `REQUIRE_APPROVAL` if task policy says an
   operator must confirm, else `ALLOW`. Where the source of "task policy"
   comes from is an open question below, not decided here.

## The second enforcement type: how the registry gates on it

Mirror the existing `CANONICAL_RUN` gate pattern in
`runtime/harness/service.py` exactly:

- `HarnessService` (or whatever future call site performs a
  destructive/external operation) must call `self.hooks.has_enforcement(
  HookEvent.BEFORE_DESTRUCTIVE_ACTION, HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION)`
  (and the `BEFORE_EXTERNAL_ACTION` equivalent) before proceeding, the same
  way `_require_canonical_enforcement()` is checked before start/send/resume/
  stop.
- If no guard with that enforcement role is installed, the operation must be
  refused with a result analogous to today's `CANONICAL_GUARD_REQUIRED`
  failure (e.g. `DESTRUCTIVE_GUARD_REQUIRED`) — fail closed by construction,
  not fail open. This preserves the existing security invariant: an
  enforcement-gated operation path is unusable until a real guard is
  registered and passes, exactly like `CANONICAL_RUN` today.
- If a guard is installed, `self.hooks.run(event, context)` runs as usual and
  its `HookRunResult.denied` / `.requires_approval` short-circuits the
  operation via the existing `_hook_block()` helper — no new blocking
  mechanism needed.

This is the "second enforcement type" the checklist calls for: it reuses
every existing registry/service mechanic (`_register_enforcement`,
`has_enforcement`, `run`, `_hook_block`) with zero changes to `HookRegistry`
itself beyond adding the enum member.

## Non-goals

- No action/tool declaration registry. No manifest of "every action MAPS can
  take" with a destructive/external bit baked in. Classification stays
  caller-declared context, not a queryable catalog (roadmap §7.2/§7.6/§7.7:
  no giant knowledge graph, no semantic classification).
- No policy engine, no rules DSL, no per-project configurable severity
  matrix. The guard is a fixed deterministic function of two booleans plus
  existing task/binding authority state — not a second authority database
  (roadmap §7.2 "second task/session authority database" — rejected).
- No automatic/inferred classification (static analysis of shell strings,
  regex sniffing of arguments, LLM judgment of "is this destructive"). That
  reintroduces exactly the "model remembered a sentence" failure mode 6.4
  exists to eliminate, and it is unverifiable/gameable. If a real call site
  cannot honestly self-declare `destructive`/`external`, that is a defect at
  the call site, not something this guard should paper over with inference.
- No wiring of this guard into a real production call site in this task.
  Exactly like the RnS harness note (`2026-08-21-...`) separated "build the
  guard" from "wire the first caller," this note only designs the
  classification contract and the enforcement gate. The first real call site
  (e.g. `runtime/recovery/supervisor.py` stop/kill paths, or a future
  external-network action) is a separate, bounded follow-up task.
- No new `HookOutcome` variants, no new `HookDirective` values, no changes to
  `HookRegistry.run()`/`register()` internals.
- No daemon, no background scanning of pending actions, no always-on process.

## Behavior questions the implementation task must answer

Do not guess these inside a broad implementation:

- What is the exact source of "task policy" the guard consults to decide
  ALLOW vs DENY vs REQUIRE_APPROVAL for a destructive/external action? Is it
  a field on the existing task record, something new on `ExecutionBinding`,
  or absent for now (i.e. deny-by-default until a real policy field exists)?
  This note deliberately does not invent a new field name or storage
  location for that authority.
- Which concrete production operations get their first
  `context["destructive"]` / `context["external"]` classification, and who
  sets it — the adapter, the service caller, or a thin wrapper at the
  operation boundary? (Mirrors the RnS note's "which exact existing lookup
  constructs the binding" question.)
- Should `destructive` and `external` share one guard/enforcement type (as
  proposed above) or be split into two separate `HookEnforcement` members
  gating `BEFORE_DESTRUCTIVE_ACTION` and `BEFORE_EXTERNAL_ACTION`
  independently? This note picked one combined guard for minimalism, but the
  implementation task should confirm that a single guard doesn't force an
  awkward policy conflation once a real policy source exists.
- What happens when neither `destructive` nor `external` is present in the
  context at all (caller forgot to declare)? Fail closed (treat missing key
  as an implicit DENY/guard-required failure) is the safer default consistent
  with `CanonicalRunGuard`'s existing `BINDING_REQUIRED` pattern, but the
  implementation task must decide and test it explicitly rather than let a
  missing key silently mean "not destructive."
- Where does the guard's decision get recorded as evidence (recovery action
  evidence, Run Record, both, or a new evidence stream), consistent with how
  `HookOutcome.evidence_refs` is already used elsewhere?
- Does `REQUIRE_APPROVAL` on a destructive/external action have an existing
  operator-approval mechanism to attach to today, or does that approval path
  itself need to be built first? If it doesn't exist yet, the first call site
  may need to start as DENY-only (no approval escape hatch) until that
  mechanism exists — this note does not assume one exists.

## Roadmap impact

This design does not complete 6.4 or SEC3. It specifies the missing
classification contract and the second `HookEnforcement` gate so a bounded
follow-up can implement `DestructiveExternalActionGuard` plus its enum member
without inventing a new taxonomy, and a second follow-up can wire a first real
call site through it — the same two-step split used for the RnS harness
resume work (design note vs. call-site PR #160).
