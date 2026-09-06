# PR #307 — independent review evidence

reviewer: maps-lean-rev3-kava (BigCatMellow, no prior involvement in PR #307 or the 6.4 chain — not buna/zeno/nima/lulu/zura)
head_sha: f1feeded01c00c2c79b34261dbfe78d56c754e1a
independent: true
summary: APPROVE. Design-only note (one new file, work/notes/2026-09-06-harness-send-callsite-design.md, +479). Central finding independently verified: HarnessService.send() has zero production callers on origin/main (c958cf6) and nothing in the orchestration layer delivers memory-derived content today, so — unlike the sibling stop() note (#305) — there is NO bounded call site, and 6.22's exercise needs a real payload assembler + delivery call site + default-off opt-in as its own impl PR. The note honestly scopes that work rather than shrinking it. Boundary clean, test CI green.

## Verdict

**APPROVE.** A design note that honestly says "no bounded call site, needs an assembler PR" is approvable when that finding is correct (per the dispatch: the note's job is to scope, not to shrink the work). It is correct.

## Verification performed (fresh clone, branch design/6.22-harness-send-callsite @ f1feede; origin/main = c958cf6)

### 1. Boundary — clean
- `git diff --name-status origin/main` → exactly one file: `A work/notes/2026-09-06-harness-send-callsite-design.md` (+479, 0 deletions).
- No `runtime/` change, no test, no `work/roadmaps/CAPABILITY_CHECKLIST.md` edit, no PR wiring. `git status --porcelain` on a fresh checkout: clean.
- §5 out-of-scope list ("Any actual runtime code change … git status after this note shows exactly one new untracked file") is accurate.

### 2. Core claim — zero production callers of `HarnessService.send()` — REPRODUCED
- `/usr/bin/grep -rn "\.send(" runtime/ --include=*.py | grep -v test` → reproduces §1a byte-for-byte. Every hit is either the tail of `HarnessService.send()` itself (`service.py:287 return adapter.send(binding, payload)`), the hcom adapter calling its own backend (`adapters/hcom.py:348`), a test-support mixin (`contract.py:51`), or docstring prose in the guard module. None is an independent caller of `HarnessService.send()`.
- Whole-repo (not just `runtime/`) grep for `.send(` non-test: same four categories, no additional caller. `cli.py` / `flow_start.py` do not call it.
- `/usr/bin/grep -rn "\.send(" runtime/recovery/ --include=*.py | grep -v test` → no matches (§1b reproduced).
- `runtime/recovery/supervisor.py`: the sole production `HarnessService` consumer invokes `.resume(binding, session_ref)` at `:538` (no payload) and the pre-existing direct `self.hcom.resume(...)` fallback at `:629`. No `.send(` / `.stop(` anywhere in the file. (§1c reproduced.)
- What already exists is accurately catalogued: `HookEvent.BEFORE_SEND` (`hooks.py:20`), `HookEnforcement.MEMORY_PROVENANCE` (`hooks.py:53`), `HarnessService.send()` fully built with `_require_canonical_enforcement(BEFORE_SEND)` gate (`service.py:265-287`, gate at `:64-76`), `MemoryProvenanceGuard` + `register_memory_provenance_guards` composed into the one production `HarnessService` at `runtime/recovery/production.py:420` (`build_canonical_harness_service`), `CanonicalRunGuard` registered on `BEFORE_SEND` (`harness_guard.py:243`). The guard's `BEFORE_SEND` callback has therefore never executed outside unit tests — corroborated independently by the current `CAPABILITY_CHECKLIST.md` row 6.22 text, which states the identical blocker ("`HarnessService.send()` has no production caller and no real payload assembler emits `memory_provenance` yet").

### 3. Central finding — no bounded call site; needs a real assembler as its own impl PR — CORRECT
- `RecoverySupervisor` resumes only; it never delivers context. Verified: no `.send(` in `runtime/recovery/`.
- `flow_start` explicitly does not send: `runtime/flow_start.py` returns `context_plan` in its result dict (`:182`) and stamps `next_step.state = "STOPPED_BEFORE_PROVIDER_SESSION"` with reason `"flow start does not select workers, launch providers, attach sessions, or send messages"` (`:185-188`). Reproduced.
- `build_context_plan` consumers are CLI-output-only: `cli.py:752` (`maps context`) and `flow_start.py` (returned in the dict). Neither injects the plan into a session. Reproduced via `/usr/bin/grep -rn "build_context_plan\|context_plan" runtime/ --include=*.py | grep -v test`.
- Conclusion: there is no production code path that turns a context plan into a `send()` payload; that step is performed by an agent operator outside the runtime today. The note's "no bounded call site, stop condition #2 fires" is accurate. Stop condition #2 for THIS review ("a real bounded site exists → CHANGES-REQUESTED naming it") does not fire — no such site exists.

### 4. §2c minimal-assembler scope — genuinely minimal, correctly shaped
- Proposed impl surface: one pure `render_context_send_payload(context_plan, *, from_name)` function + one delivery call site + one default-off `--deliver-context` flag + factoring `_resolve_harness_binding` (currently `supervisor.py:208-274`) to a shared helper (a move, not new machinery — rule 12). This is a bounded impl PR, not a subsystem.
- No provenance store / schema / migration / graph is proposed; §5 explicitly excludes all of them, consistent with guard MUST-NOT 2.
- The `memory_provenance` payload shape in §2c/§3 was cross-checked line-by-line against `runtime/policy/memory_provenance_guard.py`:
  - `MEMORY_CONTENT_MARKER = "memory_content"` (`:91`), `PROVENANCE_KEY = "memory_provenance"` (`:94`) — match.
  - Guard reads `context["details"]["payload"]` (set by `service.py` `details={"payload": dict(payload)}`) — match.
  - Per entry: `admit_memory_evidence(entry.get("trust_class"), stale=entry.get("stale", False), unknown_admission=MemoryAdmission.DENY)`; stated `admission` field ignored / re-derived (`:174-179`) — matches §2c and `admit_memory_evidence`'s real signature `(trust_class, *, stale, unknown_admission)` at `memory_trust_gate.py:101`.
  - `LOAD`→pass; `DENY`→`MEMORY_PROVENANCE_DENIED`; `WITHHOLD` + `embedded is True`→`WITHHOLD_EMBEDDED` deny; `WITHHOLD` + `embedded` explicit `False`→pass; `WITHHOLD` + missing/non-bool `embedded`→`WITHHOLD_EMBEDDING_UNDECLARED` deny; provenance absent + `memory_content` truthy→`MEMORY_PROVENANCE_UNVERIFIED` deny; non-list provenance→`MEMORY_PROVENANCE_MALFORMED`; no annotation + no marker→`NO_MEMORY_CONTENT` allow (guard inert). Every branch in §3's table matches the guard code (`:130-215`).
  - Slice-1 residual (guard trusts the assembler's `embedded: bool`) is stated in both the guard module docstring and §2c/§5 — consistent.

### 5. §3 gating, §4 exercise sketch, §5 out-of-scope — honest and complete
- §2e gating mirrors the existing `harness_project_id requires validation_repo_root` pattern in `production.py` and proposes a *separate* opt-in (not folded into `--enforce-canonical-run`) because arming outbound content injection is a distinct authority grant — reasonable and conservative.
- §4 is explicitly "Not done here. Sketch only." and defers the `CAPABILITY_CHECKLIST.md` row 6.22 flip to after the real enforced pass — consistent with the row's current IN PROGRESS state and its own note that a prior branch commit overclaimed this row to DONE and was corrected 2026-09-05.
- §5 out-of-scope list (6.4 stop() caller, write/credential guards, capability manifest, schema/migration/store/graph, BEFORE_TOOL firing site / new HookEvent, re-classifying embedded-vs-referenced in the guard, loosening send()'s CANONICAL_RUN requirement, any runtime change, checklist flip) is complete and matches the guard's stated MUST-NOTs.

### 6. Overclaim check
- No place found where the note asserts more than the code supports. The note repeatedly under-claims (flags the work as larger-than-bounded, defers the checklist flip, names the prior overclaim as a thing not to repeat).
- One minor descriptive inaccuracy, non-blocking, does not affect any finding: §1a describes `runtime/harness/contract.py:51` as "`SendIntent.execute()` (a value-object convenience wrapper)" and says a grep for its constructor shows no production instantiation. That line is actually `AdapterContractMixin._call()`, a `unittest` contract-test support mixin; there is no `SendIntent` class anywhere in the repo. The bullet's conclusion — that `contract.py:51` is not an independent caller of `HarnessService.send()` — is nonetheless correct (it calls `adapter.send`, and it is test-support code). Recommend the author correct the label in a follow-up touch if the note is otherwise edited; not worth a CHANGES-REQUESTED on its own.

### CI
- `test` (Runtime stack tests): **pass** (1m25s, run 34016797602).
- `review-evidence`: fail before this commit (no evidence file); this commit provides the file bound to head_sha f1feede.

## Independent-verification statement

I have no prior involvement in PR #307 or the 6.4/stop() design chain. All greps re-run in a fresh clone against the branch tip; every §1 reproduction command matched; the guard payload contract was cross-checked against `memory_provenance_guard.py` directly rather than from the note's narrative. The central "no bounded call site" finding is correct.
