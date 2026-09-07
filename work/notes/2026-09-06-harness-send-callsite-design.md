# Design note — a production call site for `HarnessService.send()` (6.22)

**Status:** design only. No runtime code changed by this note. No
`CAPABILITY_CHECKLIST.md` edit. Not self-reviewed. Merge is on the 3-day
operator hold; `review-evidence` CI is expected red until a coordinator
dispatches an independent reviewer.

**Headline for @gigi (stop condition #2 fires):** unlike the sibling
`HarnessService.stop()` note (PR #305), there is **no bounded call site**
here. The orchestration layer sends *no message with content* through any
path today — the recovery supervisor only `.resume()`s (no payload), and
`maps flow start` deliberately stops before "send messages". Exercising
`MemoryProvenanceGuard` requires **building a real payload assembler + a
delivery call site** (context-plan → `send()` payload). That is
larger-than-a-bounded-follow-up. §2 scopes the minimal assembler; it is not
a one-liner in an existing branch.

**Source of truth**

- `work/roadmaps/CAPABILITY_CHECKLIST.md` row 6.22 ("Memory trust classes",
  IN PROGRESS) — read the full row.
- `runtime/policy/memory_provenance_guard.py` — `MemoryProvenanceGuard` on
  `HookEvent.BEFORE_SEND`; built + composed in
  `runtime/recovery/production.py::build_canonical_harness_service`
  (`production.py:420`).
- `runtime/harness/service.py::HarnessService.send()` (defn at L255-287) —
  fires `BEFORE_SEND`; zero production callers.
- `runtime/recovery/supervisor.py::RecoverySupervisor` — only production
  consumer of a `HarnessService`; calls `.resume()` only
  (`supervisor.py:538`).
- `runtime/flow_start.py::flow_start` + `runtime/context_builder.py::build_context_plan`.
- `runtime/policy/memory_trust_gate.py::admit_memory_evidence()`.
- Sibling precedent (mirror its structure):
  `work/notes/2026-09-06-harness-stop-callsite-design.md`, branch
  `design/6.4-harness-stop-callsite` (PR #305).
- Prior notes (read, not duplicated), each STOP-conditioned on exactly this
  work: `work/notes/2026-08-21-memory-trust-enforcement-design.md`,
  `work/notes/2026-08-25-memory-trust-enforcement-gate-design.md`,
  `work/notes/2026-08-31-memory-trust-tool-call-gate-design.md`.
- Local memory: `project_6_4_6_22_need_production_callsite.md`.

---

## 1. Fresh grep — zero production callers; what exists vs. not

All commands run in a fresh clone at `origin/main` =
`c958cf6ba099edf2363e0d66b40f10c2c1174425` (`#298`).

### 1a. Every `.send(` under `runtime/` (non-test)

```
$ /usr/bin/grep -rn "\.send(" runtime/ --include=*.py | grep -v test
runtime/harness/adapters/hcom.py:348:            self.backend.send(
runtime/harness/service.py:287:        return adapter.send(binding, payload)
runtime/harness/contract.py:51:            return self.adapter.send(self.binding, self.payload)
runtime/policy/memory_provenance_guard.py:13:`HarnessService.send(binding, session_ref, payload)` is the orchestrator
runtime/policy/memory_provenance_guard.py:18:`admit_memory_evidence()`, the `send()` is refused before `adapter.send()` is
runtime/policy/memory_provenance_guard.py:228:    one production caller. `HarnessService.send()` already fires
runtime/policy/memory_provenance_guard.py:230:    because `HarnessService.send()` has no production caller yet (design
```

- `service.py:287` — the *tail* of `HarnessService.send()` itself (delegates
  to `adapter.send()` after the `BEFORE_SEND` hook chain). Not a caller of
  `HarnessService.send`.
- `adapters/hcom.py:348` — `HcomHarnessAdapter.send()` calling its hcom
  *backend* (`self.backend.send(name, message, intent=…, thread=…,
  from_name=…)`); reached only *from* `HarnessService.send()` at L287. Not an
  independent caller.
- `contract.py:51` — `SendIntent.execute()` (a value-object convenience
  wrapper); grep for its constructor shows no production instantiation.
- The remaining hits are docstring prose in the guard module.

### 1b. Nothing under `runtime/recovery/` sends

```
$ /usr/bin/grep -rn "\.send(" runtime/recovery/ --include=*.py | grep -v test
(no matches)
```

### 1c. The one production `HarnessService` consumer routes resume only

```
$ /usr/bin/grep -n "harness_service\|\.resume(\|\.send(\|\.stop(" runtime/recovery/supervisor.py
99:        harness_service: Any | None = None,
117:        # instead of the direct self.hcom.resume(...) call. When unset, or
120:        self.harness_service = harness_service
532:            if self.harness_service is not None:
538:                        result = self.harness_service.resume(binding, session_ref)
629:                    self.hcom.resume(session_name, headless=True, go=True)
```

`supervisor.py:538` is the sole production invocation of any `HarnessService`
method, and it is `.resume(binding, session_ref)` — which takes **no
payload**. `supervisor.py:629` is the pre-existing direct-hcom fallback
`self.hcom.resume(...)` (also contentless).

### 1d. Context-plan consumers (the only memory-content producers)

```
$ /usr/bin/grep -rn "build_context_plan\|context_plan" runtime/ --include=*.py | grep -v test
runtime/cli.py:9:from runtime.context_builder import build_context_plan
runtime/cli.py:752:            plan = build_context_plan(store, args.task_id, repo_root=args.repo_root)
runtime/context_builder.py:602:def build_context_plan(
runtime/flow_start.py:7:from runtime.context_builder import build_context_plan
runtime/flow_start.py:131:        context_plan = build_context_plan(...)
runtime/flow_start.py:182:        "context_plan": context_plan,
runtime/skills/catalog.py:246: (docstring prose)
```

Both consumers **emit the plan as CLI output** (`maps context` at
`cli.py:752`; `maps flow start` returns it in the result dict at
`flow_start.py:182`). Neither delivers it into a session. `flow_start`'s own
result states the boundary explicitly:

```
$ /usr/bin/grep -n "send messages\|STOPPED_BEFORE" runtime/flow_start.py
185:            "state": "STOPPED_BEFORE_PROVIDER_SESSION",
188:            "flow start does not select workers, launch providers, attach "
188-189:            "sessions, or send messages"
```

### 1e. What already exists vs. not

| Piece | State | Location |
|---|---|---|
| `HookEvent.BEFORE_SEND` enum member | **exists** | `runtime/harness/hooks.py:20` |
| `HookEnforcement.MEMORY_PROVENANCE` enum member | **exists** | `runtime/harness/hooks.py:53` |
| `HarnessService.send(binding, session_ref, payload)` — validates binding↔session, resolves adapter, requires `CANONICAL_RUN` enforcement on `BEFORE_SEND`, fires `BEFORE_SEND`, then `adapter.send(binding, payload)` | **exists**, fully built | `runtime/harness/service.py:255-287` |
| `_require_canonical_enforcement()` gate on `BEFORE_SEND` (`send` returns `CANONICAL_GUARD_REQUIRED` if no `CANONICAL_RUN` guard registered for the event) | **exists** | `service.py:64-76`, called at `:269` |
| `MemoryProvenanceGuard` + `register_memory_provenance_guards` (subscribes to `BEFORE_SEND`, `READ_ONLY`, DENY-only) | **exists** | `runtime/policy/memory_provenance_guard.py` |
| Guard **composed into the one production `HarnessService`** | **exists** | `runtime/recovery/production.py:420` (`build_canonical_harness_service`) |
| `CanonicalRunGuard` also registered on `BEFORE_SEND` (so `_require_canonical_enforcement` is satisfied for `send`) | **exists** | `runtime/policy/harness_guard.py:243` (`RUN_STARTING, BEFORE_SEND, BEFORE_RESUME, SESSION_STOPPING`) |
| `HcomHarnessAdapter.send()` → hcom backend `send(name, message, intent, thread, from_name)`; requires `payload["message"]` non-empty | **exists** | `runtime/harness/adapters/hcom.py:323-366` |
| `admit_memory_evidence(trust_class, *, stale, unknown_admission)` → `MemoryAdmissionDecision` | **exists**, pure | `runtime/policy/memory_trust_gate.py` |
| `build_context_plan(...)` stamps every memory-like item (`guidance` / `withheld_guidance` / `skills`) with a string `trust_class` + `budget_class` (the trust gate's outputs) | **exists** | `runtime/context_builder.py` (`trust_class` at L260/L290/L541-560; `memory_trust_classification_present` coverage flag at L722) |
| `_resolve_harness_binding(incident, session_name)` → `(ExecutionBinding, SessionRef, reason)` | **exists**, used by the resume path | `runtime/recovery/supervisor.py:208-274` |
| A **production code path that calls `HarnessService.send()`** with any payload | **does NOT exist** | — (this note) |
| A **payload assembler** that turns a context plan (or any memory-derived text) into a `send()` payload carrying `payload["memory_provenance"]` | **does NOT exist** | — (this note) |
| Default-off CLI flag that would arm such a call | **does NOT exist** | — (this note) |

The `MemoryProvenanceGuard` callback has therefore **never executed in a real
pass**. `build_canonical_harness_service` was instantiated in a live enforced
pass twice (2026-09-03 resume-only; 2026-09-05 DEC-003 option B,
`CASE-378fb326…`), but both exercised only `HarnessService.resume()` →
`BEFORE_RESUME`. `BEFORE_SEND` has fired zero times outside unit tests.

**Conclusion:** `HarnessService.send()` has **zero production callers** on
current `origin/main`. Stop condition ("a caller already exists → STOP") does
not fire. Stop condition #2 (needs a real assembler subsystem, not a bounded
addition) **does** fire — see §2c.

---

## 2. The smallest legitimate production call site

### 2a. Candidates weighed

| Candidate | Carries memory-derived content? | Verdict |
|---|---|---|
| **Recovery supervisor resume/nudge** — add a `send()` "you were resumed because <deny reason>" nudge alongside the existing `.resume()` at `supervisor.py:538` | **No.** The nudge text is a recovery-status string (deny code, lease state) constructed at that code path. It touches no memory/lesson/Skill/guidance store. `memory_provenance` would be an empty list every time → the guard is inert (`GUARD_CODE_ALLOW_NO_MEMORY`). | **Rejected.** Wiring `send()` here would give the guard a firing site but never a non-trivial decision. Contrived; violates "do not invent a contrived caller". |
| **`maps run` / `maps flow` status message** — a "task claimed / run bound / lease renewed" notification to the bound session | **No.** Same shape as above: run-lifecycle status, not memory content. | **Rejected**, same reason. |
| **Context-plan delivery** — the assembler that turns `build_context_plan`'s output (its `guidance` / `withheld_guidance` / `skills` items, already `trust_class`-stamped by `admit_memory_evidence()`) into a `send()` payload injected into a freshly-bound session | **Yes — this is the one.** The context plan is *definitionally* the runtime's memory-derived content: reviewed guidance, candidate lessons, Skill bodies/descriptions, all carrying the exact `trust_class` values the guard re-derives. A payload embedding a `WITHHOLD`/`DENY`-classed item's text is precisely what `MemoryProvenanceGuard` exists to refuse. | **The correct target — but it does not exist and is not bounded.** See §2b/§2c. |

### 2b. Why the context-plan delivery is not a bounded addition

The `stop()` sibling (#305) had a bounded call site because a production
`HarnessService` consumer (`RecoverySupervisor`) already existed, already
resolved a binding every tick, and already had a terminal-state branch whose
*cause* legitimately meant "terminate". The `stop()` note added one call in an
existing branch reusing an existing `(binding, session_ref)` pair.

None of that holds for `send()`:

1. **No consumer sends anything.** `RecoverySupervisor` resumes; it never
   delivers context. `flow_start` explicitly "does not … send messages"
   (`flow_start.py:188`). `maps context` / `maps flow start` print the plan
   for a human or a dispatcher to act on. There is **no code that takes a
   context plan and puts it into a session** — that step is done by an agent
   operator today, outside the runtime.
2. **No assembler.** `build_context_plan` returns a structured dict
   (`authority` / `required` / `dependencies` / `guidance` /
   `withheld_guidance` / `skills` / `coverage` / …). Turning that into a
   single `payload["message"]` string (hcom `send` requires a non-empty
   `message`, `adapters/hcom.py:335`) plus the `payload["memory_provenance"]`
   annotation is a real rendering + provenance-extraction component that does
   not exist in any form.
3. **No delivery call site.** Even with an assembler, something has to call
   `HarnessService.send(binding, session_ref, payload)` — a new subcommand
   (`maps flow deliver-context` / `maps run send-context`) or a new opt-in
   branch of `flow_start` that runs *after* provider launch. `flow_start`
   today stops one step earlier by design; extending it past that boundary is
   itself a scope decision.

### 2c. Minimal assembler scope (stop condition #2: flag to @gigi)

If/when 6.22's exercise is authorised, the **minimal** assembler is:

```
render_context_send_payload(context_plan, *, from_name) -> Mapping[str, Any]
```

returning:

```python
{
    "message": <str>,              # deterministic text rendering of the plan's
                                   #   loadable buckets (authority + required +
                                   #   dependencies + LOAD-classed guidance +
                                   #   LOAD-classed Skill bodies). NEVER renders
                                   #   WITHHOLD/DENY item *text* into the body.
    "intent": "inform",
    "from_name": from_name,
    "memory_content": True,        # MEMORY_CONTENT_MARKER — set truthy so the
                                   #   fail-closed UNVERIFIED branch is reachable
                                   #   if the annotation is ever dropped.
    "memory_provenance": [         # PROVENANCE_KEY — one entry per plan item
                                   #   whose text OR identifier was copied in
        {
            "item_id": <str>,      # plan item's stable id / name
            "trust_class": <str>,  # verbatim from context_builder's stamp
            "admission": <str>,    # ADVISORY ONLY — guard re-derives, ignores this
            "embedded": <bool>,    # True if the item's *content text* is in
                                   #   `message`; False if only an id/name is.
            "stale": <bool>,       # from the plan item's stale_trust_metadata flag
        },
        ...
    ],
}
```

Contract (from the guard code, `memory_provenance_guard.py:34-54, 129-215`):

- The guard reads `context["details"]["payload"]` (set by `service.py:282`),
  takes `payload["memory_provenance"]`, and for each entry calls
  `admit_memory_evidence(entry["trust_class"], stale=entry.get("stale",
  False), unknown_admission=MemoryAdmission.DENY)` — it **re-derives** the
  admission and **does not trust** `entry["admission"]` (rule 12 / rule 14).
- `LOAD` → entry passes. `DENY` → payload denied. `WITHHOLD` → passes **only**
  if `entry["embedded"] is False` (an explicit bool); a missing / non-bool
  `embedded` fails closed as embedded. Missing annotation but
  `memory_content` truthy → `MEMORY_PROVENANCE_UNVERIFIED` deny. No annotation
  and no marker → `NO_MEMORY_CONTENT` allow (guard inert).
- The assembler **trusts its own `embedded` flag** — same residual as SEC3's
  caller-declared `destructive: bool` and as slice 1's stated residual. It
  must therefore be the single component that decides what text goes in
  `message`, so the flag is true by construction. The simplest safe rule: the
  renderer only ever embeds `LOAD`-classed item text; every `WITHHOLD`/`DENY`
  item contributes at most an id/name and is marked `embedded: False` (or is
  omitted entirely, in which case it needs no provenance entry). Under that
  rule the guard should *never* deny a correctly-assembled payload — the deny
  path exists to catch an assembler bug or a future looser renderer, which is
  exactly the point of a fail-closed guard.

This is a **bounded component once authorised** (one pure render function +
one delivery call site + one default-off flag), but it is **not** a
one-line addition to an existing branch. @gigi: treat as its own
implementation PR, not a rider on the #305 follow-up.

### 2d. `ExecutionBinding` / `SessionRef` construction

Reuse `RecoverySupervisor._resolve_harness_binding` (`supervisor.py:208-274`)
verbatim — it is already the one lineage-resolution path and already returns
the `(ExecutionBinding, SessionRef, reason)` triple `HarnessService.send()`
needs:

- `ExecutionBinding(task_id, run_id, worker_id, task_revision, project_id,
  session_id=adapter_session_id)` — built at `supervisor.py:255-262`.
- `SessionRef(session_id=adapter_session_id, worker_id, adapter="hcom",
  project_id, remote_ref=session_name)` — built at `supervisor.py:263-269`.
- `send()` calls `_validate_binding_session(binding, session_ref)` with
  `allow_unbound=False` (`service.py:261`), so `binding.session_id` **must**
  be present and equal to `session_ref.session_id`. `_resolve_harness_binding`
  only returns a non-`None` pair when lineage state is `EXPLICIT` and the
  adapter session id resolves (`supervisor.py:243-252`) — so the precondition
  is already met exactly where a resume is routable.

A context-plan delivery outside `RecoverySupervisor` (e.g. a `maps flow`
subcommand) would need the same lineage inputs (`run_id` → `resolve_run_session`
→ `EXPLICIT` current session). The note's recommendation is to **factor
`_resolve_harness_binding`'s body into a shared helper** (it currently lives on
the supervisor but references only `self.task_reader`) rather than duplicate
it — no new machinery, just a move (rule 12: no second lineage-resolution
truth).

### 2e. Default-off gating (mirror `--enforce-canonical-run` / #305's `--terminate-denied-sessions`)

A **new, separate** opt-in — not folded into `--enforce-canonical-run`,
because arming an outbound *content injection* into a live session is a
distinct authority grant from arming a resume-denial:

1. The delivery entrypoint (whether a `flow_start` option or a new subcommand)
   gains `deliver_context: bool = False` / `--deliver-context`
   (`action='store_true'`), documented "byte-identical when False".
2. It is only meaningful with a `HarnessService` in hand, which requires the
   `--harness-project-id` / `--repo-root` composition (`production.py`
   `build_canonical_harness_service`). Mirror the existing
   `harness_project_id requires validation_repo_root` guard: `parser.error(...)`
   (or `ValueError`) if `--deliver-context` is set without
   `--enforce-canonical-run` + `--harness-project-id`.
3. Every existing invocation stays byte-identical; the `send()` fires only
   under the full opt-in flag set.

### 2f. Fail-closed behaviour

"Fail-closed" here = **never inject content into a session that cannot be
canonically identified, and never let a send failure or a guard veto be
retried or silently swallowed into "delivered"**:

- `binding is None` / `session_ref is None` → do **not** call `.send()`, do
  **not** fall back to a direct `hcom send` (none is added by this note),
  record `context_delivery={"attempted": False, "reason": <binding_reason>}`,
  and treat the flow step as failed (the plan was not delivered).
- `HarnessService.send()` returns non-ok — including `CANONICAL_GUARD_REQUIRED`
  (no canonical guard registered), `HOOK_DENIED` from `MemoryProvenanceGuard`
  (`MEMORY_PROVENANCE_DENIED` / `_UNVERIFIED` / `_MALFORMED`), or
  `SESSION_MISMATCH` / `PROJECT_MISMATCH` / `WORKER_MISMATCH` → record the
  `OperationResult` verbatim, do **not** retry within the call, do **not**
  strip the offending item and re-send. A guard veto of the payload is a
  correct fail-closed outcome: the session simply does not receive that
  context, exactly as today (where it receives none via this path).
- `HarnessService.send()` raises → caught, recorded
  `{"attempted": True, "ok": False, "code": "HARNESS_CALL_ERROR", …}`.
- The assembler itself, on any rendering error, emits **no payload** rather
  than a partial one (a partial render could embed a `WITHHOLD` item without
  its provenance entry).

Audit-only: the outcome is recorded on a new `context_delivery` key (shape
mirrors `harness_resume`), read by nothing.

---

## 3. `memory_provenance` payload contract (consolidated)

Restating §2c precisely against the guard code so a reviewer can check it
without cross-referencing:

| Payload key | Type | Required | Guard behaviour |
|---|---|---|---|
| `message` | non-empty `str` | yes (hcom adapter) | not inspected by the guard (MUST-NOT 6: no text sniffing) |
| `memory_content` | truthy | recommended | if truthy and `memory_provenance` absent → **DENY** `MEMORY_PROVENANCE_UNVERIFIED` |
| `memory_provenance` | `list`/`tuple` of `Mapping` | yes when the message embeds any memory text | non-list → **DENY** `MEMORY_PROVENANCE_MALFORMED`; non-Mapping entry → **DENY** `MEMORY_PROVENANCE_MALFORMED` |
| `…[i].item_id` | `str` | recommended | used only for the evidence ref; blank → `#<index>` |
| `…[i].trust_class` | `str` (context_builder's stamp) | yes | fed to `admit_memory_evidence`; unresolved/blank/unknown → `DENY` (`unknown_admission=DENY`) |
| `…[i].stale` | `bool` | optional (default `False`) | non-`bool` → treated as stale (demotes `LOAD`→`WITHHOLD`) |
| `…[i].embedded` | `bool` | yes for `WITHHOLD` items | `WITHHOLD` + `embedded is True` → **DENY** `WITHHOLD_EMBEDDED`; `WITHHOLD` + `embedded is False` → pass; `WITHHOLD` + missing/non-bool → **DENY** `WITHHOLD_EMBEDDING_UNDECLARED` |
| `…[i].admission` | `str` | optional | **ignored** — guard re-derives from `trust_class` (rule 14) |

Guard outcomes: `NO_MEMORY_CONTENT` / `MEMORY_PROVENANCE_ADMITTED` → ALLOW;
everything else → DENY. `REQUIRE_APPROVAL` is never returned (MUST-NOT 5).

---

## 4. What a later 6.22 exercise would look like (analogous to PR #303 for 6.16)

**Not done here.** Sketch only:

1. **Impl PR** (§2c): `render_context_send_payload` + the delivery call site +
   `--deliver-context` opt-in + `_resolve_harness_binding` factored to a shared
   helper + unit coverage (`tests/test_flow_start.py` / a new
   `tests/test_context_delivery.py`): flag off = byte-identical output; flag on
   + fake `HarnessService` = exactly one `send(binding, session_ref, payload)`
   with a well-formed `memory_provenance` list; a plan containing a `WITHHOLD`
   lesson → that entry is `embedded: False` and the payload passes; a
   deliberately mis-assembled payload embedding a `DENY` Skill → `send()`
   returns `HOOK_DENIED` / `MEMORY_PROVENANCE_DENIED` and the flow step fails
   fail-closed.
2. **Real enforced pass**, extending the DEC-003 option B rig
   (`work/notes/2026-09-05-dec003-b-attempt2-real-run-results.md`): bind a live
   hcom session via `maps run bind-session`, then run `maps flow …
   --enforce-canonical-run --harness-project-id maps-lean --repo-root
   <checkout> --deliver-context` against a task whose context plan contains at
   least one `REVIEWED_GUIDANCE` (`LOAD`) item **and** one `CANDIDATE_LESSON` /
   `OBSERVATION` (`WITHHOLD`) item.
3. **Capture** as the #303-analogous evidence: the `send()` call's
   `OperationResult`, the `BEFORE_SEND` hook-chain evidence showing
   `MemoryProvenanceGuard` fired and returned `MEMORY_PROVENANCE_ADMITTED` for
   the correctly-assembled payload, plus a **second** deliberate run with a
   patched renderer that embeds the `WITHHOLD` item's text → `send()` denied,
   `guard_code="MEMORY_PROVENANCE_DENIED"`, `evidence_refs` naming the item,
   session receives nothing. Freeze both as regression cases per
   `playbook/REPAIR_AND_LEARNING.md`.
4. Only then does 6.22's stated "guard's `BEFORE_SEND` callback has never
   fired in a real pass" gap close. Update `CAPABILITY_CHECKLIST.md` row 6.22
   at that point — **not** before, and not in the impl PR unless the exercise
   is in the same PR.

Remaining 6.22 work after that (still open): `SkillTrustState` /
`SkillLifecycleState` / `operational_learning.py` remain unmigrated separate
systems of record; the assembler's `embedded: bool` residual (§2c) stays
trusted until a slice re-derives embed-vs-reference from the rendered text.

---

## 5. Explicitly OUT OF SCOPE

- **6.4's `HarnessService.stop()` caller** (`work/notes/2026-09-06-harness-stop-callsite-design.md`, PR #305). Separate gap; not touched.
- **Write / credential / filesystem-scope guards.** Not touched.
- **The capability-declaration manifest** (SEC4). Not touched.
- **Any schema change, migration, persisted provenance store, or provenance
  graph** — the annotation lives only on the in-flight payload (guard MUST-NOT 2).
- **A `BEFORE_TOOL` / `AFTER_TOOL` firing site or adapter tool-loop
  interception, or any new `HookEvent` member** (guard MUST-NOT 1).
- **Re-classifying embedded-vs-referenced inside the guard** — the `embedded:
  bool` residual stays trusted for now (guard slice-1 residual).
- **Loosening `HarnessService.send()`'s existing `CANONICAL_RUN` requirement**
  or adding a `_require_memory_provenance_enforcement()` fail-closed gate on
  `send()` itself (guard MUST-NOT 8).
- **Any actual runtime code change.** This note changes no file under
  `runtime/`, no test, no `work/roadmaps/CAPABILITY_CHECKLIST.md`, no other
  note, no PR wiring. `git status` after this note shows exactly one new
  untracked file.
- **Flipping 6.22 to DONE / editing the checklist row.** The row stays
  `IN PROGRESS` until §4's exercise runs. (A prior branch overclaimed the
  sibling 6.4/6.16 rows to DONE on resume-only evidence and was corrected
  2026-09-05; do not repeat that here.)

---

## Reproducing section 1's grep claims

```
$ git rev-parse origin/main
c958cf6ba099edf2363e0d66b40f10c2c1174425

$ /usr/bin/grep -rn "\.send(" runtime/ --include=*.py | grep -v test
runtime/harness/adapters/hcom.py:348:            self.backend.send(
runtime/harness/service.py:287:        return adapter.send(binding, payload)
runtime/harness/contract.py:51:            return self.adapter.send(self.binding, self.payload)
runtime/policy/memory_provenance_guard.py:13:`HarnessService.send(binding, session_ref, payload)` is the orchestrator
runtime/policy/memory_provenance_guard.py:18:`admit_memory_evidence()`, the `send()` is refused before `adapter.send()` is
runtime/policy/memory_provenance_guard.py:228:    one production caller. `HarnessService.send()` already fires
runtime/policy/memory_provenance_guard.py:230:    because `HarnessService.send()` has no production caller yet (design

$ /usr/bin/grep -rn "\.send(" runtime/recovery/ --include=*.py | grep -v test
(no matches)

$ /usr/bin/grep -n "harness_service\|\.resume(\|\.send(\|\.stop(" runtime/recovery/supervisor.py
99:        harness_service: Any | None = None,
117:        # instead of the direct self.hcom.resume(...) call. When unset, or
120:        self.harness_service = harness_service
532:            if self.harness_service is not None:
538:                        result = self.harness_service.resume(binding, session_ref)
629:                    self.hcom.resume(session_name, headless=True, go=True)

$ /usr/bin/grep -rn "BEFORE_SEND\|MEMORY_PROVENANCE" runtime/harness/hooks.py
20:    BEFORE_SEND = "before_send"
53:    MEMORY_PROVENANCE = "MEMORY_PROVENANCE"

$ /usr/bin/grep -n "register_memory_provenance_guards\|MemoryProvenanceGuard()" runtime/recovery/production.py
131:from runtime.policy.memory_provenance_guard import (
132:    MemoryProvenanceGuard,
133:    register_memory_provenance_guards,
420:    register_memory_provenance_guards(registry, MemoryProvenanceGuard())
```

---

## Resume prompt

You are picking up after the 6.22 "harness-send call site" design note
(`work/notes/2026-09-06-harness-send-callsite-design.md`, branch
`design/6.22-harness-send-callsite`). The note is design-only and awaits an
independent review under the 3-day operator merge hold. Do **not** merge it
and do **not** edit `CAPABILITY_CHECKLIST.md`. Key finding: unlike the sibling
`stop()` note (#305), there is **no bounded call site** — `HarnessService.send()`
has zero production callers and nothing in the orchestration layer sends
memory-derived content today. Exercising `MemoryProvenanceGuard` requires
building a real payload assembler (`render_context_send_payload`: context plan →
`send()` payload with a `memory_provenance` annotation per §2c/§3), a delivery
call site (a new `maps flow deliver-context` subcommand or a post-launch
`flow_start` branch), and a default-off `--deliver-context` opt-in threaded like
`--enforce-canonical-run`. Reuse `_resolve_harness_binding` (factor it to a
shared helper). Next action once this note is reviewed + merged **and** the
operator authorises the work: dispatch that implementation PR, then the §4
real enforced-pass exercise (bind a live hcom session, deliver a plan
containing both a `LOAD` and a `WITHHOLD` item, capture the `BEFORE_SEND`
hook-chain evidence for both the admitted payload and a deliberately
mis-assembled denied one, freeze as regression cases). Only after that exercise
does 6.22's "guard callback never fired in a real pass" gap close.
