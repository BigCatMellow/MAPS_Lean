# Memory trust — first tool-call enforcement seam (roadmap 6.22)

Date: 2026-08-31
Status: design-only. No runtime code change, no schema change, no checklist
status flip. Design review only.

Selects the FIRST bounded seam at which an *action* (not just the Context
Builder plan) is denied because it is informed by an untrusted
`MemoryTrustClass` item. Continues:

- `work/notes/2026-08-21-memory-trust-enforcement-design.md` (PR #148 — first
  seam = Context Builder evidence annotation; its class/action table already
  names "tool calls" as something `UNTRUSTED_INPUT` / `QUARANTINED` must not
  influence);
- `work/notes/2026-08-25-memory-trust-enforcement-gate-design.md` (PR — the
  `admit_memory_evidence()` LOAD/WITHHOLD/DENY gate over that seam), §5:
  "no *action/tool-call* gate consults the class" is the named remaining gap.

All callsite claims re-verified at `origin/main` `d810509` (rule 14).

---

## Q1 — What is a "tool call" here, and where could a guard intercept it?

### 1a. MAPS_Lean does not intercept the driven agent's own tool calls

MAPS_Lean is an orchestration runtime. The worker is an LLM session driven
through `runtime/harness/adapters/hcom.py`. The runtime **drives** sessions
(`start` / `send` / `resume` / `stop` on `HarnessService`); it does not sit
inside the session's own tool-execution loop. `HookEvent.BEFORE_TOOL` /
`AFTER_TOOL` exist in `runtime/harness/hooks.py:14-15` **as vocabulary with
zero firing sites** — `grep -rn "BEFORE_TOOL\|before_tool" runtime/` returns
only the enum definition. Firing them would require an interception point in
the adapter's execution path that does not exist and is not in scope for
6.22. **Proposing/firing `BEFORE_TOOL` is therefore a MUST-NOT for the first
slice** (dispatch Q1).

### 1b. The orchestrator-side analog that IS already a fired seam: `BEFORE_SEND`

The runtime's own "tool call carrying memory-derived content" is
`HarnessService.send(binding, session_ref, payload)`
(`runtime/harness/service.py:255-287`): the orchestrator injecting a
follow-up message/instruction into a running session. If that `payload`
embeds remembered guidance or Skill-instruction text (from the Context
Builder plan, or assembled elsewhere), then a `send()` whose payload body
contains a `WITHHOLD`/`DENY`-classed memory item **is** "a tool call informed
by an untrusted memory/lesson/Skill".

`send()` already:

- fires `HookEvent.BEFORE_SEND` (`service.py:276`) with
  `details={"payload": dict(payload)}` in the hook context — the payload is
  already visible to a guard;
- fail-closes via `_require_canonical_enforcement(BEFORE_SEND, "send")`
  (`service.py:270`) — the "consequential operation requires a guard"
  pattern is already established for this event;
- is already a `CanonicalRunGuard` subscription point
  (`runtime/policy/harness_guard.py:243`).

So `BEFORE_SEND` is an **existing, fired hook event with an existing
guard-composition pattern** — not a new seam. It is the exact structural
analog of how SEC3's `DestructiveExternalActionGuard` sits on
`BEFORE_DESTRUCTIVE_ACTION` / `HarnessService.stop()` (PR #194, `d810509`).

### 1c. Caller-maturity caveat (does not change the seam choice)

`HarnessService.send()` has **no production caller today** — `grep -rn
"\.send(" runtime/` shows only `AdapterContractMixin` (test contract) and the
adapter's own internal `backend.send`. This is the **same maturity level** as
the two shipped guards: `HarnessService.stop()` (SEC3's firing site) has no
production caller either (checklist H5/SEC3: "a real production caller of
`stop()`" is still listed as missing), and `load_catalog_skill()` (SEC4's
"first real refusal") has no production caller (checklist SEC4: "the refusal
is real, tested code with no production caller yet"). MAPS_Lean's established
pattern is **guard-ahead-of-caller, composed default-off, first production
exposure gates the status flip**. This note follows that precedent; §7
states the caller gap explicitly and it is flagged to `miga`.

---

## Q2 — Which `MemoryTrustClass` values block vs warn vs allow, and does it
reuse `admit_memory_evidence()`?

**It reuses `admit_memory_evidence()`'s decision — it does not define a new
table.** The tool-call gate is a *projection of `MemoryAdmission` onto
`HookDirective`*, applied to the provenance of the `send()` payload:

| Contributing item's `MemoryAdmission` (from `admit_memory_evidence()`) | `send()` guard directive |
|---|---|
| `LOAD` | `ALLOW` |
| `WITHHOLD` | `ALLOW` **iff** the item appears in the payload only as a *reference* (id/name), `DENY` if its content/body text is embedded in the payload |
| `DENY` | `DENY` |
| provenance annotation absent on a payload that carries memory-derived content | `DENY` (`MEMORY_PROVENANCE_UNVERIFIED`) |

- **No new vocabulary, no new semantics.** The gate calls the existing
  `admit_memory_evidence(trust_class, stale=..., unknown_admission=...)` and
  branches on its `MemoryAdmissionDecision.admission`.
- **DENY-only, no `REQUIRE_APPROVAL`.** Consistent with `CanonicalRunGuard`
  and `DestructiveExternalActionGuard` (both DENY-only; no approval bridge).
  There is no "warn" tier in the first slice — `HookDirective.ANNOTATE`
  could host one later, but the minimal seam is allow/deny, matching SEC3.
- The `WITHHOLD`-embedded-vs-referenced distinction is the same one §2e of
  the gate note already draws for lessons (reference: `{lesson_id, reason}`)
  vs Skills (content: `name`/`description` inline).

---

## Q3 — Smallest first seam (rule 8)

**One guard, one fired event, one enforcement point.**

### `runtime/policy/` — a new `MemoryProvenanceGuard` (name must not appear in
any other `runtime/` source — same test convention as
`DestructiveExternalActionGuard`, `tests/test_destructive_external_action_guard.py:316`)

- Callable guard, `__call__(context) -> HookOutcome`, mirroring
  `DestructiveExternalActionGuard`'s shape: a `HookDirective` + a stable
  `guard_code` annotation, no free-form policy payload.
- Reads `context.details["payload"]`. Looks for a **provenance annotation**
  the payload assembler is required to attach (Q4):
  `payload["memory_provenance"]` — a list of
  `{"item_id": str, "trust_class": str, "admission": str, "embedded": bool}`.
- Decision:
  - no `memory_provenance` key **and** `payload` has no memory-derived
    content marker → `ALLOW` (`NO_MEMORY_CONTENT`); the guard is inert for
    payloads that never touch memory.
  - `memory_provenance` present → for each entry, re-run
    `admit_memory_evidence()` on its `trust_class`/`stale` (do **not** trust
    the assembler's stated `admission` — re-derive it, fail-closed) and apply
    the Q2 projection. Any `DENY` → `HookDirective.DENY`,
    `guard_code = "MEMORY_PROVENANCE_DENIED"`, `evidence_refs` listing the
    offending `item_id`(s) and class(es) **without** the untrusted text.
  - payload carries a memory-content marker but **no** `memory_provenance`
    → `DENY` (`MEMORY_PROVENANCE_UNVERIFIED`). Fail-closed: unannotated
    memory content cannot be proven clean.
- Never returns `ALLOW` for a `DENY`-classed item; never returns
  `REQUIRE_APPROVAL`.

### `runtime/policy/` — `register_memory_provenance_guards(registry, guard)`

Exact mirror of `register_destructive_external_action_guards`
(`destructive_action_guard.py:209`): `type(guard) is not
MemoryProvenanceGuard` → `TypeError`; registers one `HookSpec` on
`HookEvent.BEFORE_SEND` under a new `HookEnforcement.MEMORY_PROVENANCE` enum
member, `side_effect=HookSideEffect.READ_ONLY`.

`HookEnforcement.MEMORY_PROVENANCE` is a new **enum member**, not a schema
change — identical in kind to SEC3 adding
`HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION`.

### `runtime/recovery/production.py::build_canonical_harness_service`

One added line, next to the existing
`register_destructive_external_action_guards(...)` call:
`register_memory_provenance_guards(registry, MemoryProvenanceGuard())`. The
guard needs **no store** — it reads only the payload annotation and the pure
`admit_memory_evidence()` function. Default-off in the sense that matters:
nothing calls `HarnessService.send()` in production yet, so composing it
changes no live behavior (§7).

### The one real enforcement point

A `send()` payload assembled from a Context Builder plan whose contributing
item was `WITHHOLD`/`DENY` (e.g. an `OBSERVATION` Skill's `description`
text, or a `QUARANTINED` lesson) — embedded rather than referenced, or
carrying no provenance — is refused with `HOOK_DENIED` /
`MEMORY_PROVENANCE_DENIED` before `adapter.send()` is reached.

### Deferred (explicitly not in the first slice)

- Firing `BEFORE_TOOL` / `AFTER_TOOL` or any adapter-loop interception.
- A `BEFORE_SEND` `_require_memory_provenance_enforcement()` fail-closed
  gate (the SEC3 `_require_destructive_enforcement` analog) — that would make
  *every* `send()` fail without the guard; defer until there is a production
  `send()` caller to reason about.
- Extending the seam to `load_catalog_skill()` (Q3 alt below).
- Any per-project config, severity matrix, or `ANNOTATE`/warn tier.
- Carrying `memory_provenance` through `resume()` / `start()` payloads.

### Q3 alternative considered — `load_catalog_skill()` — deferred to SEC4

`runtime/skills/catalog.py::load_catalog_skill(entry, store)` already refuses
activation when the composed `SkillLifecycleState` is `QUARANTINED` /
`RETIRED` / `SUPERSEDED` (`catalog.py:254-288`, SEC4 "first real refusal").
`runtime/trust.py::skill_lifecycle_trust_class()` already maps those states
into `MemoryTrustClass`. Re-expressing that refusal as "consult
`skill_lifecycle_trust_class()` → `admit_memory_evidence()`" would be a
*second* valid tool-call seam and a small one. It is **deferred** because:
(a) it is Skill-activation-specific, not the general "tool call" the roadmap
gap names; (b) it is SEC4/6.10 territory (that lane owns the lifecycle
store and the refusal); (c) the dispatch asks to mirror SEC3's hook/guard
composition, which `load_catalog_skill` is not. Recommend SEC4 pick it up as
a follow-up once this seam lands.

---

## Q4 — Provenance flow: how does the guard know a payload traces to a
trust-classified plan item?

The Context Builder plan already stamps `trust_class` (and, after the gate
PR, an admission outcome + `budget_class`) on every memory-like item in
`guidance` / `withheld_guidance` / `skills`, each with a stable identifier
(`lesson_id`, or `skill_id` / `catalog_key`).

The **payload assembler** — whatever future component turns a plan into a
`send()` payload — is required to attach `payload["memory_provenance"]`: for
every plan item whose text it copies into the payload body, one entry
`{"item_id", "trust_class", "admission", "embedded": True}`; for every item
it names by reference only, `"embedded": False`.

- This is a **contract on the assembler**, enforced by the guard's
  fail-closed `MEMORY_PROVENANCE_UNVERIFIED` branch: an assembler that
  embeds memory text without annotating it gets its `send()` denied.
- The guard **re-derives** the admission from `trust_class` via
  `admit_memory_evidence()` rather than trusting the assembler's stated
  `admission` — the annotation is an identifier + class claim, and the
  authoritative decision stays in the one pure function (rule 12: no second
  derivation of the admission).
- No provenance *graph*, no lineage store, no persistence — the annotation
  lives only on the in-flight payload, exactly as
  `DestructiveExternalActionGuard` reads a caller-supplied action
  classification off `context` rather than from a store.

For the first slice, since no production assembler exists yet, the contract
is specified and tested against a synthetic payload; the real assembler
adopts it when it is built (that is a separate task — likely part of
"`maps flow` session-launch" / 6.21).

---

## Q5 — Interaction with the plan-level gate: downstream, defense-in-depth

The `send()` guard is **strictly downstream** of `admit_memory_evidence()`
at the Context Builder seam. It does **not** subsume the plan gate:

- The plan gate shapes the *default load set* and `coverage`, and runs even
  when no `send()` ever happens (`maps flow start` builds a plan and stops;
  `maps context-plan` just prints one).
- The `send()` guard catches what the plan gate cannot: (a) a plan consumer
  that ignores `budget_class` / `withheld_guidance` and embeds a WITHHOLD
  item into an injected prompt anyway; (b) a payload assembled from a source
  other than the Context Builder plan; (c) a future regression in the
  assembler.
- Both consult the **same** `admit_memory_evidence()` function and the same
  `MemoryTrustClass` mappings — one decision procedure, two enforcement
  points. No divergent policy.

This is the standard two-layer shape: the plan gate is "what may be
*offered*", the send guard is "what may actually *cross into an action*".

---

## Q6 — STOP conditions / MUST-NOTs for the eventual impl

**MUST NOT:**

1. Fire `HookEvent.BEFORE_TOOL` / `AFTER_TOOL`, add an adapter
   tool-execution interception point, or add any new `HookEvent` member.
   The seam is the already-fired `BEFORE_SEND`.
2. Add a schema change, a migration, a new persisted store, or a provenance/
   lineage graph. The annotation lives on the in-flight payload only.
3. Migrate or re-home `SkillTrustState`, `SkillLifecycleState`, or
   `operational_learning.py` status strings — they stay the systems of
   record, read only through the existing `runtime/trust.py` mappings.
4. Define a second admission table. The guard calls the existing
   `admit_memory_evidence()` and projects its `MemoryAdmission` onto a
   `HookDirective` (Q2). No new vocabulary, no `class >= threshold` over
   enum order.
5. Return `HookDirective.REQUIRE_APPROVAL` or add an approval bridge —
   DENY-only, matching `CanonicalRunGuard` / `DestructiveExternalActionGuard`.
6. Inspect or regex-sniff the payload *text* for "untrusted-looking"
   content. The decision comes only from the `memory_provenance` annotation
   + `trust_class` mapping — same reasoning the gate note gives for
   rejecting inferred classification.
7. Let a missing/malformed `memory_provenance` annotation on a
   memory-bearing payload mean "trusted" — it must `DENY`
   (`MEMORY_PROVENANCE_UNVERIFIED`).
8. Add `_require_memory_provenance_enforcement()` to `send()` in the first
   slice (would break every `send()` without the guard; no production
   `send()` caller exists to reason about yet).
9. Route `runtime/context_builder.py`, `runtime/flow_start.py`, or
   `runtime/cli.py` through `HarnessService` purely to host the guard —
   the guard composes in the existing `build_canonical_harness_service`
   only.
10. Flip 6.22 (or S6 / SEC3 / SEC4) status. The checklist's "no action/
    tool-call gate consults `MemoryTrustClass`" clause is *narrowed* (a
    guard now exists on `BEFORE_SEND`, default-off, no production exposure),
    not deleted. First production exposure — a real `send()` caller that
    assembles a payload from a plan and is denied on a WITHHOLD item — is
    still required before any status moves.
11. Weaken `tests/test_destructive_external_action_guard.py`'s
    "guard-name-appears-in-no-other-source" style test when adding the
    analogous one for `MemoryProvenanceGuard`.

**STOP and escalate to `miga` if:**

- wiring the guard forces a production `HarnessService.send()` caller or a
  payload assembler to be built as part of this slice (it must not — the
  guard ships against a synthetic-payload test, ahead of the caller, like
  SEC3);
- the `memory_provenance` payload contract cannot be expressed without a
  schema change or a new persisted structure;
- `BEFORE_SEND` turns out to be unreachable for a memory-bearing payload in
  every realistic assembler design (then the note becomes "why `BEFORE_TOOL`
  must be given a firing site" — a new-architecture task).

---

## Roadmap impact

Does not complete 6.22. Selects and specifies the first *action-level* seam:
`MemoryProvenanceGuard` on the already-fired `HookEvent.BEFORE_SEND`,
composed in `build_canonical_harness_service` (SEC3 mirror), consuming the
existing `admit_memory_evidence()` decision via a payload provenance
annotation. After the follow-up impl, the checklist's "no action/tool-call
gate consults `MemoryTrustClass`" clause narrows to "a `BEFORE_SEND` guard
exists but has had no first production exposure" — the same wording shape as
SEC3/H5. The `SkillTrustState`/`SkillLifecycleState`/`operational_learning.py`
non-migration clause is untouched. An optional one-line "tool-call gate
design pending" annotation on 6.22's evidence text is within the output
boundary.

---

## Resume prompt

You are implementing the **first slice** of the memory-trust tool-call gate
for MAPS_Lean (roadmap 6.22). Work in your own git worktree off
`origin/main`; `cd ~/Projects/MAPS_Lean` and `git fetch origin main` first.
Re-verify every callsite at your HEAD (rule 14).

Source of truth: this note
(`work/notes/2026-08-31-memory-trust-tool-call-gate-design.md`), its parents
`work/notes/2026-08-21-memory-trust-enforcement-design.md` and
`work/notes/2026-08-25-memory-trust-enforcement-gate-design.md`, and SEC3's
composition (`runtime/policy/destructive_action_guard.py` +
`register_destructive_external_action_guards` +
`runtime/recovery/production.py::build_canonical_harness_service`, PR #194).

Implement exactly the **Q3 "Smallest first seam"** list:

1. `runtime/policy/memory_provenance_guard.py` (new): a `MemoryProvenanceGuard`
   callable + `register_memory_provenance_guards(registry, guard)`, exact
   structural mirror of `destructive_action_guard.py`. Guard reads
   `context.details["payload"]["memory_provenance"]`, re-runs
   `admit_memory_evidence()` per entry, applies the Q2 projection, returns
   `HookDirective.DENY` / `MEMORY_PROVENANCE_DENIED` on any DENY (or
   embedded-WITHHOLD), `MEMORY_PROVENANCE_UNVERIFIED` on a memory-bearing
   payload with no annotation, `ALLOW` / `NO_MEMORY_CONTENT` otherwise.
   DENY-only, never `REQUIRE_APPROVAL`, never `ALLOW` for a DENY class.
2. `runtime/harness/hooks.py`: add `HookEnforcement.MEMORY_PROVENANCE` enum
   member (member only — no other change).
3. `runtime/recovery/production.py::build_canonical_harness_service`: one
   line registering the guard on the existing `registry`, next to the
   destructive-guard registration. No store argument.

MUST NOT: fire `BEFORE_TOOL`/`AFTER_TOOL` or add any `HookEvent`; add a
schema change / migration / persisted store / provenance graph; define a
second admission table (call `admit_memory_evidence()`); return
`REQUIRE_APPROVAL`; sniff payload text; let a missing annotation mean
trusted; add `_require_memory_provenance_enforcement()` to `send()`; route
context_builder/flow_start/cli through `HarnessService`; flip
6.22/S6/SEC3/SEC4 status; weaken the guard-name-isolation test.

Tests (one blocking foreground `python3 -m unittest
tests.test_memory_provenance_guard tests.test_recovery_composition_root`,
no Monitor, no background): synthetic payload with a DENY-classed embedded
item + guard composed → `HOOK_DENIED` / `MEMORY_PROVENANCE_DENIED`, decision
re-derived not trusted from the annotation; embedded WITHHOLD item → DENY;
referenced-only WITHHOLD item → ALLOW; LOAD item → ALLOW; memory-bearing
payload with no `memory_provenance` → `MEMORY_PROVENANCE_UNVERIFIED`;
non-memory payload → ALLOW / `NO_MEMORY_CONTENT`; guard name appears in no
other `runtime/` source. `python3 -m runtime.smoke` exits 0. Push before any
full-suite run; rely on CI.

Update the 6.22 evidence text in `work/roadmaps/CAPABILITY_CHECKLIST.md` in
the same PR — narrow the "no action/tool-call gate" clause, **no status
flip**.

Then: PR into `main` (never push to main). Request independent review with
mutation testing (min 5) per `reference_committee_review`; add a bound
`work/reviews/pr-<N>-review-evidence.md` (the reviewer's, not yours — see
`feedback_implementer_cannot_commit_review_evidence`). Do NOT self-merge.
Report the PR number to `miga`.

Stop conditions: if wiring the guard forces a production
`HarnessService.send()` caller or a payload assembler to be built now, or
the `memory_provenance` contract needs a schema change, STOP and flag `miga`.
