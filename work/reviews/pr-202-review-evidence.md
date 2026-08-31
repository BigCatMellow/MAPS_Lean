# PR #202 — SEC/6.22 slice 1: `MemoryProvenanceGuard` on `BEFORE_SEND` — independent review evidence

reviewer: maps-lean-rev-muso
head_sha: d08269e8feaa0412bfd9e47f71eee2e7b595d1c4
independent: true
summary: APPROVE. Exact structural mirror of the SEC3 `DestructiveExternalActionGuard` composition — one callable guard + `register_memory_provenance_guards` + `HookEnforcement.MEMORY_PROVENANCE` enum member + one registration line in `build_canonical_harness_service`, on the already-fired `HookEvent.BEFORE_SEND`. Decision is a pure projection of `admit_memory_evidence()`'s `MemoryAdmission` onto `HookDirective` (LOAD→ALLOW, embedded-WITHHOLD/DENY→DENY, referenced-only-WITHHOLD→ALLOW, memory-bearing-but-unannotated→DENY `MEMORY_PROVENANCE_UNVERIFIED`); the annotation's stated `admission` is re-derived, never trusted. DENY-only, never `REQUIRE_APPROVAL`. All 11 design-note MUST-NOTs verified respected by `/usr/bin/grep` at HEAD. 7/7 mutations against the verdict logic killed by existing tests. No schema/migration/store, no `BEFORE_TOOL` firing, no new `HookEvent`, no `_require_memory_provenance_enforcement()` in `send()`, no status flip. `embedded: bool` slice-1 trust residual stated in both the guard module docstring and the 6.22 checklist evidence text. Diff in-bounds. `python3 -m unittest tests.test_memory_provenance_guard tests.test_recovery_composition_root` → OK (41); `python3 -m runtime.smoke` → exit 0.

## Method

Own detached worktree at PR #202 head `d0200acb34a576455269a6d3e509eea3b8fae7a4`
(branch `sec-6.22-memory-provenance-guard`). `git fetch origin main` first.
`git merge-base --is-ancestor origin/main d0200ac` → true: the PR head sits
directly on the current `origin/main` tip (`98620e4`), **no rebase needed**.
Every callsite/existence claim re-verified at HEAD with `/usr/bin/grep` (rule 14
— the shell `grep` wrapper strips leading `./`). Source of truth:
`work/notes/2026-08-31-memory-trust-tool-call-gate-design.md` (Q2 projection
table, Q3 "smallest first seam", Q6 MUST-NOT list + STOP conditions); SEC3
precedent `runtime/policy/destructive_action_guard.py` +
`register_destructive_external_action_guards` +
`runtime/recovery/production.py::build_canonical_harness_service` (PR #194);
`admit_memory_evidence()` in `runtime/policy/memory_trust_gate.py`.

## 1. Slice matches design note Q3 — CONFIRMED

| Q3 "smallest first seam" item | Impl | Verdict |
|---|---|---|
| `runtime/policy/memory_provenance_guard.py` (new): `MemoryProvenanceGuard` callable, `__call__(context) -> HookOutcome`, mirroring `DestructiveExternalActionGuard` shape (directive + stable `guard_code` annotation, no free-form policy payload) | present, 245 lines; `_deny()` helper returns `HookOutcome(DENY, reason, evidence_refs=…, annotations={"guard_code": …})` exactly like SEC3's `_deny` | ✓ |
| Reads `context["details"]["payload"]`; looks for `payload["memory_provenance"]` list of `{item_id, trust_class, admission, embedded}` | `_payload()` walks `context["details"]["payload"]`, typed-guarded to `Mapping`; `PROVENANCE_KEY = "memory_provenance"` | ✓ |
| No `memory_provenance` key **and** no memory-content marker → ALLOW `NO_MEMORY_CONTENT` (inert) | `provenance is None and not has_marker` → ALLOW `NO_MEMORY_CONTENT` | ✓ |
| `memory_provenance` present → per entry, re-run `admit_memory_evidence()` on `trust_class`/`stale`, do **not** trust stated `admission`, apply Q2 projection; any DENY → `HookDirective.DENY` `MEMORY_PROVENANCE_DENIED`, `evidence_refs` listing offending `item_id`/class **without** the untrusted text | `admit_memory_evidence(entry.get("trust_class"), stale=entry.get("stale", False), unknown_admission=MemoryAdmission.DENY)` — `admission` field is read into `_entry()` fixtures but never consulted by the guard; `evidence_refs=tuple(f"memory_item:{ref}" …)`, `ref` is `item_id` or `#<index>` + `decision.code`, no payload text | ✓ |
| memory-content marker but **no** `memory_provenance` → DENY `MEMORY_PROVENANCE_UNVERIFIED` (fail-closed) | `provenance is None and has_marker` → `_deny(GUARD_CODE_UNVERIFIED, …)` | ✓ |
| Never ALLOW for a DENY-classed item; never `REQUIRE_APPROVAL` | DENY branch always appends to `denied`; `HookDirective.REQUIRE_APPROVAL` appears nowhere in the module body; `test_never_returns_require_approval` sweeps the class×embedded matrix | ✓ |
| `register_memory_provenance_guards(registry, guard)` — exact mirror of `register_destructive_external_action_guards`: `type(guard) is not MemoryProvenanceGuard` → `TypeError`; one `HookSpec` on `BEFORE_SEND` under `HookEnforcement.MEMORY_PROVENANCE`, `side_effect=READ_ONLY` | line-for-line mirror; `priority=10` (same as SEC3) | ✓ |
| `HookEnforcement.MEMORY_PROVENANCE` new **enum member** (member only) | `runtime/harness/hooks.py` diff = one line added to `HookEnforcement`; no `HookEvent` change | ✓ |
| `build_canonical_harness_service`: one added line next to `register_destructive_external_action_guards(...)`, **no store arg** | `register_memory_provenance_guards(registry, MemoryProvenanceGuard())` + a 4-line explanatory comment; `MemoryProvenanceGuard()` takes no constructor args | ✓ |

Also added (not literally in the Q3 list, but the exact SEC3 mirror does the
same and it is benign): `runtime/policy/__init__.py` re-exports
`MemoryProvenanceGuard` / `register_memory_provenance_guards` and adds them to
`__all__`. In-bounds.

## 2. MUST-NOT list (design Q6) — all 11 CONFIRMED respected

| # | MUST NOT | Check at HEAD | Verdict |
|---|---|---|---|
| 1 | Fire `BEFORE_TOOL`/`AFTER_TOOL`, add adapter tool-loop interception, or any new `HookEvent` member | `/usr/bin/grep -rn "BEFORE_TOOL\|AFTER_TOOL\|before_tool\|after_tool" runtime/` → only the two enum definitions in `hooks.py:14-15` + a docstring mention in the guard. `git diff` on `hooks.py` = one `HookEnforcement` member, `HookEvent` untouched. | ✓ |
| 2 | Schema change / migration / new persisted store / provenance graph | `git diff --stat` touches no `*.sql`, no `migrat*`, no store module; `production.py` registration passes no store; guard has no `__init__` state | ✓ |
| 3 | Migrate/re-home `SkillTrustState` / `SkillLifecycleState` / `operational_learning.py` | none of those symbols appear in the diff; guard imports only `MemoryAdmission`, `admit_memory_evidence` from `.memory_trust_gate` | ✓ |
| 4 | Define a second admission table | guard has no dict literal mapping classes → outcomes; it calls `admit_memory_evidence()` and branches on `decision.admission` (`is LOAD` / `is DENY` / else WITHHOLD). No `class >= threshold` over enum order. | ✓ |
| 5 | Return `REQUIRE_APPROVAL` / add approval bridge | `REQUIRE_APPROVAL` absent from module body; `test_never_returns_require_approval` | ✓ |
| 6 | Inspect/regex-sniff the payload text | guard reads only `payload.get(PROVENANCE_KEY)` and `bool(payload.get(MEMORY_CONTENT_MARKER))` (a boolean key, not text); no `re`, no substring scan of any body field | ✓ |
| 7 | Missing/malformed annotation on a memory-bearing payload = "trusted" | no annotation + marker → DENY `UNVERIFIED`; non-list `memory_provenance` → DENY `MALFORMED`; non-Mapping entry → DENY `MALFORMED`; missing/non-`True` `embedded` on a WITHHOLD entry → deny (`WITHHOLD_EMBEDDING_UNDECLARED`) | ✓ |
| 8 | Add `_require_memory_provenance_enforcement()` to `send()` | `/usr/bin/grep -n "memory_provenance\|_require_memory" runtime/harness/service.py` → nothing; `send()` unchanged | ✓ |
| 9 | Route `context_builder` / `flow_start` / `cli` through `HarnessService` to host the guard | diff touches none of those files; guard composes only in `build_canonical_harness_service` | ✓ |
| 10 | Flip 6.22 / S6 / SEC3 / SEC4 status | `CAPABILITY_CHECKLIST.md` diff = the 6.22 row only, still `IN PROGRESS`; the "no action/tool-call gate" clause is **narrowed** ("clause **narrows**… a `BEFORE_SEND` guard now exists… no first production exposure"), not deleted; "Still no status flip: `HarnessService.send()` has **no production caller**" stated. SEC3/SEC4/S6 rows untouched. | ✓ |
| 11 | Weaken the SEC3 guard-name-isolation test | `tests/test_destructive_external_action_guard.py` not in the diff. The new `GuardNameIsolationTest` mirrors it and is arguably stronger (two tests: name-confinement + `MEMORY_PROVENANCE` enforcement-member-confinement). | ✓ |

`/usr/bin/grep -rln "MemoryProvenanceGuard\|register_memory_provenance_guards" runtime/`
→ `memory_provenance_guard.py`, `policy/__init__.py`, `recovery/production.py`
only (+ pyc). `/usr/bin/grep -rln "MEMORY_PROVENANCE" runtime/` → `hooks.py`,
`memory_provenance_guard.py` only (+ pyc). Both isolation tests pass.

## 3. `embedded: bool` slice-1 trust residual — CONFIRMED stated in both places

- Guard module docstring, "Residual trusted in slice 1" section: "Slice 1
  TRUSTS the assembler's `embedded: bool` flag on each provenance entry. The
  guard re-derives the admission verdict via `admit_memory_evidence()`, but it
  does **not** itself re-classify whether a given item's content is embedded in
  the payload body vs merely referenced by id/name… This is the exact same kind
  of residual as SEC3's caller-declared `destructive: bool` flag."
- `CAPABILITY_CHECKLIST.md` 6.22 row: "Slice-1 residual, stated explicitly: the
  guard **trusts the assembler's `embedded: bool` flag** per provenance entry —
  it re-derives the admission verdict but does not itself re-classify
  embedded-vs-referenced, the same kind of residual as SEC3's caller-declared
  `destructive: bool`."
- `tests/test_memory_provenance_guard.py` module docstring restates it as "a
  documented contract, not closed."

## 4. Mutation testing — 7 mutations against the verdict logic, 7/7 killed

Each mutation applied to `runtime/policy/memory_provenance_guard.py` in the
worktree, `python3 -m unittest tests.test_memory_provenance_guard` (+ the
composition test for M1) run, then reverted.

| # | Mutation | Effect | Killed by | Result |
|---|---|---|---|---|
| M1 | DENY branch: drop `denied.append(...)` + `continue` (DENY-classed items pass) | a `DENY`/`QUARANTINED`/`UNTRUSTED_INPUT` item no longer blocks the send | `test_deny_class_item_denies_even_when_only_referenced`, `test_decision_is_re_derived_not_trusted_from_the_annotation`, `ComposedServiceSendTest.test_synthetic_deny_classed_embedded_item_blocks_the_send`, `test_recovery_composition_root` (4 failures) | KILLED |
| M2 | LOAD branch: `continue` → `pass` (LOAD item falls through to the WITHHOLD embedded check) | a clean `REVIEWED_GUIDANCE`/`LOAD` item gets denied `WITHHOLD_EMBEDDED` | `test_load_class_item_allows`, `ComposedServiceSendTest.test_clean_payload_reaches_the_adapter` | KILLED |
| M3 | embedded-WITHHOLD: `denied.append(f"{item_ref}:WITHHOLD_EMBEDDED")` → `continue` | an `OBSERVATION`/`CANDIDATE_LESSON` item whose text is embedded in the payload passes | `test_embedded_withhold_item_denies`, `test_stale_demotes_load_to_withhold_then_embedded_denies` | KILLED |
| M4 | re-derivation fail-closed default: `unknown_admission=MemoryAdmission.DENY` → `WITHHOLD` | an unresolvable/blank/unknown `trust_class` referenced-only would ALLOW instead of DENY | `test_unknown_trust_class_denies_fail_closed` | KILLED |
| M5 | UNVERIFIED branch: `if has_marker:` → `if not has_marker:` (marker logic inverted) | memory-bearing unannotated payload ALLOWs; inert non-memory payload DENYs | `test_memory_bearing_payload_with_no_annotation_is_unverified`, `test_non_memory_payload_allows_inert` | KILLED |
| M6 | missing-`embedded` on WITHHOLD: drop the `WITHHOLD_EMBEDDING_UNDECLARED` append | a WITHHOLD entry that omits the `embedded` flag passes (fail-open) | `test_missing_embedded_flag_on_withhold_denies_fail_closed` | KILLED |
| M7 | embedded test: `if embedded is not True:` → `if embedded is True:` (referenced/embedded sense flipped) | embedded WITHHOLD passes, referenced-only WITHHOLD denies | `test_embedded_withhold_item_denies`, `test_referenced_only_withhold_item_allows`, `test_stale_demotes_load_to_withhold_then_embedded_denies` (3 failures) | KILLED |

Covered by these: the DENY branch, the LOAD→ALLOW branch, the WITHHOLD
embedded/referenced split, the `admit_memory_evidence()` re-derivation
(fail-closed default), and the embedded-WITHHOLD path. The
`admit_memory_evidence()` "do not trust the annotation" property is directly
asserted by `test_decision_is_re_derived_not_trusted_from_the_annotation`
(entry claims `admission="LOAD"` on a `QUARANTINED` item → still DENY) and by
`test_stale_demotes_load_to_withhold_then_embedded_denies`.

### Non-killing mutation (benign redundancy, not a coverage gap)

M8: invert the container-type guard `if not isinstance(provenance, (list, tuple)):`
so a bare string `memory_provenance` is not rejected up front. Tests still pass
— `test_malformed_provenance_container_denies` (`"memory_provenance": "OBSERVATION"`)
survives because the per-entry loop then iterates the string's characters, each
fails the `isinstance(entry, Mapping)` check, and the guard returns the same
`MEMORY_PROVENANCE_MALFORMED` code. Two independent fail-closed paths converge
on the same verdict; the assertion is on `guard_code`, which is identical. Not a
defect — defence-in-depth. Worth a one-line test asserting the container-level
path specifically if a future refactor removes the per-entry check, but not
blocking.

## 5. Composition & behavior — CONFIRMED

- `runtime/harness/service.py::send()` fires `HookEvent.BEFORE_SEND` with
  `details={"payload": dict(payload)}` and `_require_canonical_enforcement(BEFORE_SEND, "send")`
  already in place (verified at HEAD, `service.py:269-284`). The guard reads
  exactly that context shape.
- `send()` has no production caller (`/usr/bin/grep -rn "\.send(" runtime/` →
  only `AdapterContractMixin` test contract + the adapter's internal
  `backend.send`), matching the guard-ahead-of-caller precedent the design note
  cites for SEC3 `stop()` and SEC4 `load_catalog_skill()`. Composing the guard
  changes no live behavior. First production exposure still gates the status
  flip — correctly not done here.
- `ComposedServiceSendTest`: a real `HarnessService([_RecordingAdapter()],
  hooks=registry)` with the guard composed + a permissive canonical-run shim →
  a `QUARANTINED` embedded item yields `result.code == "HOOK_DENIED"`,
  `"lesson-9"` in `blocking_reasons`, `adapter.sends == []`; a clean
  `REVIEWED_GUIDANCE` payload reaches the adapter. End-to-end path exercised.
- `test_recovery_composition_root.py::test_registers_memory_provenance_enforcement_on_before_send`:
  `build_canonical_harness_service(...)` → `service.hooks.has_enforcement(BEFORE_SEND, MEMORY_PROVENANCE)` true.
- `python3 -m unittest tests.test_memory_provenance_guard tests.test_recovery_composition_root` → **OK (41)**.
- `python3 -m runtime.smoke` → **exit 0**.

## 6. Observations (non-blocking, no change required)

1. **Marker-gated UNVERIFIED (design-sanctioned residual).** An assembler that
   embeds memory-derived text but sets *neither* `MEMORY_CONTENT_MARKER` *nor*
   `memory_provenance` passes as `NO_MEMORY_CONTENT`. The `UNVERIFIED`
   fail-closed branch only fires when the marker is present. This is exactly
   design note Q3/Q4 ("no memory-content marker → ALLOW … the contract is
   enforced by the guard's fail-closed `MEMORY_PROVENANCE_UNVERIFIED` branch:
   an assembler that embeds memory text without annotating it gets its `send()`
   denied" — i.e. *when it declares the marker*). The residual is inherent to a
   contract-on-the-assembler design with no payload-text inspection (MUST-NOT
   6) and no production assembler yet to reason about. Acceptable for slice 1;
   the real assembler task (6.21 / `maps flow` session-launch) owns closing it.
2. **`decision.code` in `evidence_refs`.** The DENY evidence ref is
   `memory_item:<item_id>:<decision.code>` (e.g. `TRUST_CLASS_DENIED`,
   `TRUST_CLASS_UNRESOLVED`). No untrusted payload text leaks — `item_id` is the
   assembler-supplied stable identifier and `decision.code` is a fixed
   machine string. Consistent with MUST-NOT 6.
3. **M8 above** — optional container-level malformed test.

## Verdict

**APPROVE.** The slice is the minimal seam the design note specifies, an exact
SEC3 composition mirror, fail-closed on every unknown, DENY-only, with the
`embedded: bool` residual disclosed in code + checklist + tests. All MUST-NOTs
hold at HEAD. Mutation coverage of the verdict logic is complete (7/7). No
schema change, no status flip, diff in-bounds. `check_review_evidence.py 202`
green from inside the worktree.
