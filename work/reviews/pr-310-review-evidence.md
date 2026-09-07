# PR #310 review evidence — row 6.22 impl: production call site for HarnessService.send()

reviewer: ledo (independent reviewer, no prior involvement with row 6.22 or the harness-send work; not leta/buna/kava/zeno/nima/lulu/zura)
head_sha: be1d2c1a690fd8d43c9da5f89596d778fc0a5367
independent: true
summary: CHANGES-REQUESTED. Assembler, verbatim binding-resolution factor, all four fail-closed paths, default-off byte-identity, and the §5 output boundary all verified clean and CI test job green (1306 tests). One substantive finding blocks approval — item 7: PR knowingly ships the first production caller of HarnessService.send() while leaving register_memory_provenance_guards' docstring asserting send() "has no production caller yet", and the rule-20 CI safeguard scripts/check_stale_no_caller_docstrings.py cannot catch it because a blanket `# noqa: stale-caller-check` permanently suppresses that symbol (the checker resolves `HarnessService.send` to the bare name `send`, which also matches adapter/backend `.send`). This is the third first-caller PR to leave a stale "no production caller" docstring and the first to defeat the safeguard built for exactly this. Fix belongs in this PR (correct the one docstring sentence — doc-only, does not alter guard logic/contract) or the guard needs strengthening to resolve dotted Class.method against the callee receiver. Routed to @zamu for a third-agent fix; not fixed here. DO NOT MERGE (3-day operator hold).

## Verification performed (fresh clone /tmp/rev310-238920, PR head be1d2c1)

### 1. §5 OUT OF SCOPE — ALL CONFIRMED UNTOUCHED
`git diff --name-only origin/main...pr310` = exactly 5 files: runtime/cli.py, runtime/context_delivery.py (new), runtime/harness/binding_resolution.py (new), runtime/recovery/supervisor.py, tests/test_context_delivery.py.
- runtime/harness/service.py — empty diff. send()'s CANONICAL_RUN requirement not loosened; no _require_memory_provenance_enforcement gate added.
- runtime/policy/memory_provenance_guard.py — empty diff (but see finding 7 re its now-stale docstring).
- runtime/policy/harness_guard.py / CanonicalRunGuard / harness lifecycle — empty diff.
- runtime/recovery/production.py — empty diff.
- work/roadmaps/CAPABILITY_CHECKLIST.md — empty diff (no row 6.22 edit).
- runtime/harness/hooks.py — empty diff (no new HookEvent member).
- No schema / migration / persisted-provenance store; annotation lives only on the in-flight payload.
- No BEFORE_TOOL / AFTER_TOOL site. verify_git_run() payloads untouched.

### 2. Factoring (§2d) — VERBATIM MOVE CONFIRMED
runtime/harness/binding_resolution.py::resolve_harness_binding is _resolve_harness_binding's body moved with the single substitution self.task_reader -> task_reader (first positional arg). Line-by-line diff of the logic: identical — same run_id/task/project_id/task_revision/resolve_run_session lineage checks, same EXPLICIT + adapter_id=="hcom" gate, same ExecutionBinding/SessionRef construction, same reason strings, same bare-except -> "binding_lookup_error". supervisor.py::_resolve_harness_binding is now a one-line delegator. No lineage-resolution semantics changed (rule 12: one truth). tests/test_recovery_supervisor.py — 70 tests, OK (371s; slow backoff tests, not a hang).

### 3. Assembler (§2c) vs guard contract (memory_provenance_guard.py) — CONSISTENT
render_context_send_payload:
- Never embeds WITHHOLD/DENY item text. guidance-bucket items embed `claim` with embedded=True; withheld_guidance items emit only a `[lesson_id] withheld (reason)` reference line with embedded=False (claim text is not even present on withheld items); skills embed `body` only when it is a non-empty str (LOAD skills carry a hash-verified body), else a reference line with embedded=False.
- One memory_provenance entry per guidance / withheld_guidance / skills item, each with item_id / trust_class (verbatim `str(item.get("trust_class") or "")`) / admission (advisory, via _advisory_admission) / embedded (always an explicit bool — never missing/non-bool, so WITHHOLD_EMBEDDING_UNDECLARED is unreachable from a correct render) / stale (from stale_trust_metadata).
- memory_content marker set truthy only when the plan carried >=1 memory-like item; memory_provenance list always present.
- Cross-check vs guard: guard re-derives admission via admit_memory_evidence(trust_class, stale=, unknown_admission=DENY) and ignores entry["admission"]; blank/unknown trust_class -> DENY (fail-closed); WITHHOLD passes only when embedded is exactly False. Assembler relies on context_builder's bucketing/body-attachment discipline for the "only LOAD embedded" rule, with the guard as the fail-closed backstop — matches design intent ("deny path catches an assembler bug or a looser renderer"). test_payload_with_withheld_item_passes_guard -> MEMORY_PROVENANCE_ADMITTED; test_mis_assembled_payload_embedding_denied_skill_is_denied (QUARANTINED skill, embedded=True, advisory admission lie "LOAD") -> MEMORY_PROVENANCE_DENIED. Both pass.

### 4. Default-off byte-identity (§2e) — CONFIRMED
`maps run send-context <run_id>` without --deliver-context: builds plan, renders payload, prints CONTEXT_PAYLOAD_ASSEMBLED / delivered=false. No HarnessService constructed, no send(). test_default_off_assembles_no_send_no_service patches build_canonical_harness_service to raise and asserts builder.assert_not_called(). --deliver-context is parser.error-gated on --enforce-canonical-run AND a truthy --harness-project-id (SystemExit code 2; test_deliver_context_requires_enforcement_flags). Subcommand is net-new; no existing invocation changes.

### 5. Fail-closed (§2f) — ALL FOUR PATHS HAVE REAL TESTS
- binding/session_ref None -> no send(), no direct-hcom fallback, context_delivery={"attempted": false, "reason": <binding_reason>}, exit 2. test_fail_closed_binding_unresolved asserts fake.send_calls == [] and reason "session_not_durably_bound".
- send() returns non-ok -> OperationResult recorded verbatim (code HOOK_DENIED), exit 2, exactly one send() call (no retry). test_fail_closed_send_denied_no_retry asserts len(fake.send_calls) == 1.
- send() raises -> caught, context_delivery.code = "HARNESS_CALL_ERROR", exit 2. test_fail_closed_send_raising_is_caught.
- --deliver-context without enforcement flags -> parser.error -> SystemExit(2).
Nothing swallowed into "delivered": CONTEXT_DELIVERED only when result.ok; _emit returns 2 on ok=False.
Happy path: test_deliver_context_happy_path_exactly_one_send — exactly one send(binding, session_ref, payload), payload["memory_provenance"] is a list, intent "inform".

### 6. Full suite — GREEN
tests/test_context_delivery.py: 16 tests, OK (run per-class; the _RunCliMixin classes are git-backed and slow, ~123s, not hung).
CI `test` job: PASS (1m27s, run 34083146308) — corroborates leta's 1306-tests-OK claim.
CI `review-evidence` job: FAIL (expected — no evidence file existed until this commit).

### 7. Stale-docstring finding (item 7) — THE BLOCKING FINDING
memory_provenance_guard.py register_memory_provenance_guards docstring still reads: "composing this guard changes no live behavior because `HarnessService.send()` has no production caller yet". After this PR, runtime/cli.py::_dispatch_send_context calls `service.send(binding, session_ref, payload)` — a real production caller. The sentence is now false.
The rule-20 CI safeguard scripts/check_stale_no_caller_docstrings.py does NOT catch it: a `# noqa: stale-caller-check` on the docstring's closing line permanently suppresses the check for this symbol. The suppression is structurally necessary for that checker as written — it resolves `` `HarnessService.send()` `` to the bare final attribute `send`, and `_callers("send", ...)` already matches unrelated `adapter.send` / `backend.send` / `SendIntent.execute`'s `self.adapter.send` calls (hcom.py:348, service.py:287, contract.py:51), so without the noqa the check fails spuriously regardless of whether a real HarnessService.send caller exists. Net effect: the one mechanical safeguard built for stale "no production caller" docstrings (after PR #204/#206 and #205) is blind to exactly this class of change for this symbol.
Assessment: real gap, CHANGES-REQUESTED-worthy per the review dispatch and rule 20. Recommended fix (coordinator to route to a third agent):
  (a) minimal: this PR corrects the one stale sentence in the guard docstring — a doc-only change that does not touch the guard's logic or contract, so it is compatible with §5's intent even though §5 lists the file; leaving a knowingly-false statement is worse than the boundary nit; OR
  (b) durable: strengthen check_stale_no_caller_docstrings.py to resolve a dotted `` `Class.method` `` against the call's receiver (e.g. only count `x.send(...)` where `x` is a HarnessService, or the enclosing class name matches), removing the need for a blanket noqa and letting the guard catch the next real first-caller. (b) is the rule-20 answer; (a) unblocks this PR.

### 8. Stacking — CONFIRMED
PR body: "Stacks on unmerged design note #307 (branch off main; #307 lands first when the hold lifts)". "Flips no checklist row and runs no exercise (both are separate later PRs per design note §4)." Branch impl/6.22-context-send-payload is off origin/main c958cf6; design note lives on pr307 only. No CAPABILITY_CHECKLIST.md edit (confirmed item 1).

## Verdict
CHANGES-REQUESTED to @zamu. Single blocking finding: item 7 (stale guard docstring + defeated rule-20 safeguard). All other checks pass. Fix routed to a third agent; not applied by this reviewer. Merge remains under the 3-day operator hold regardless.
