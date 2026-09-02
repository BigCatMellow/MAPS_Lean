# PR #258 review evidence — `maps run bind-session` (lineage-bootstrap wiring)

reviewer: maps-lean-vame
head_sha: 20d716163c049b3c8d8f7b757e3f347f78a6f920
independent: true
summary: Independent review by maps-lean-vame (nava authored; vame independent of the impl) with vame's own 7-mutation set. Faithful thin-wrapper impl of #257's "impl slice" — diff is exactly the 2 MAY-touch files (runtime/cli.py +68, tests/test_cli_run.py +252 new), full MUST-NOT list holds (no runtime/harness or runtime/recovery change, no record_run_session_link param, no authority gate / --enforce flag on the verb, no checklist STATUS flip), all 5 acceptance criteria met with real end-to-end tests including the deadlock-demonstration pair, both #257 reviewer nits satisfied, 80 targeted tests (tests.test_cli_run + tests.test_run_session_lineage + tests.test_recovery_supervisor) + smoke green, 6/7 of vame's independent mutations killed (the one survivor hardcodes --created-by to its own default value — a near-equivalent, non-blocking, trivial optional test fix noted). VERDICT: APPROVE. Committed by maps-lean-luve (independent of both the impl and the review) to unblock the review-evidence CI check; content is vame's verbatim, posted via hcom #82244 and saved by vame at pr258_evidence.md.

---


source of truth: work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md (#257) "The impl slice" + §2

## Diff scope — CLEAN
`git diff --stat origin/main` = exactly **2 files, +320**:
- `runtime/cli.py` (+68: `run` subparser + `bind-session` subcommand + `_dispatch_run` + one `main()` dispatch line)
- `tests/test_cli_run.py` (+252, new)
No other file. CAPABILITY_CHECKLIST.md **not** touched (correct — #257 MAY-touch permits it "only if the impl PR also runs a pass"; this PR doesn't).

## MUST-NOT walk — ALL HOLD
| MUST-NOT | Result |
|---|---|
| Touch `runtime/harness/` or `runtime/recovery/` | HOLD — absent from the diff (the new test *imports* from them; that's test code, not a runtime change) |
| Add a param to `record_run_session_link` / change its guard logic | HOLD — `runtime/state/run_lineage.py` absent from the diff |
| Fold session recording into `maps flow start` as primary | HOLD — standalone `run bind-session` verb; `flow_start` untouched, no `--session-id` added there |
| Any authority gate / `--enforce-*` flag / operator check on the verb | HOLD — `_dispatch_run` is a bare passthrough; no `is_authorized_operator`, no enforce flag; the code comment states "the CLI adds no authority check of its own" (the store self-gates via RUN_NOT_OWNED / LEASE_EXPIRED) |
| Run any `--enforce-canonical-run` pass | HOLD — code PR only, no pass |
| Flip any checklist STATUS | HOLD — CAPABILITY_CHECKLIST.md not in the diff |

## `_dispatch_run` shape
Mirrors `_dispatch_operator` / `_dispatch_skill` exactly: thin `if args.run_command == 'bind-session': return _emit(store.record_run_session_link(...))`, `raise AssertionError(args.run_command)` fallthrough, no `HarnessService` import. Wired in `main()`: `if args.command == 'run': return _dispatch_run(store, args)`. Kwarg mapping verified: `args.run_id`→positional, `args.worker_id`→positional, `--adapter`→`adapter_id`, `--session-id`→`session_id`, `--evidence-ref`→`evidence_ref`, `--created-by`→`created_by`. Defaults per spec (`--adapter hcom`, `--created-by maps-run-bind-session`; `--worker-id` / `--session-id` / `--evidence-ref` required).

## Acceptance 1–5
1. **`resolve_run_session` → EXPLICIT after `flow start` + `bind-session`** — MET. `test_bind_session_makes_lineage_explicit` seeds a real active run (create → contract → promote → claim → `create_run_manifest`), asserts state != EXPLICIT, binds via the CLI (`main([...])`), asserts exit 0 + `code == 'SESSION_ATTACHED'` + `resolve_run_session(run_id)['state'] == 'EXPLICIT'` + current session_id/adapter_id. End-to-end through the real `TaskStore`.
2. **Every failure code surfaced, non-zero exit + store message** — MET for the CLI-reachable set: `RUN_NOT_FOUND`, `RUN_WORKER_MISMATCH`, `RUN_NOT_OWNED` (task forced out of ACTIVE), `LEASE_EXPIRED` (lease UPDATE'd to the past), `SESSION_ALREADY_BOUND` (double-bind), `MANIFEST_SESSION_CONFLICT` (manifest seeded with a different legacy session_id), `INVALID_SESSION_LINK` (empty `--evidence-ref`). Each asserts `code == 2` + the store `code`; `test_run_not_found` also asserts `payload['message']`. NOT covered: `RUN_STALE`, `SESSION_LINEAGE_INVALID`, `TASK_NOT_FOUND`, `PROJECT_CONTEXT_UNAVAILABLE`, `UNEXPECTED_REPLACEMENT_LINK` — see non-blocking note 2.
3. **Foreground test modules + smoke** — MET. `python3 -m unittest tests.test_cli_run tests.test_run_session_lineage tests.test_recovery_supervisor` → **Ran 80 tests, OK** (170s). `python3 -m runtime.smoke` → **exit 0**. (nava's reported 12+14+54; the 80 total matches.)
4. **≥5 mutations** — MET, my own set below (6/7 killed).
5. **Diff = only MAY-touch** — MET (see Diff scope).

## The two #257 nits
(a) **Integration test seeds an expired lease explicitly + asserts denial CLASS not a pinned code** — SATISFIED. `RunBindSessionUnblocksSupervisorRoutingTests` has a *pair*: `test_without_bind_session_the_harness_path_cannot_be_built` (proves the #255 deadlock: `harness_resume == {"attempted": False, "reason": "session_not_durably_bound"}`) and `test_bind_session_then_guard_denies_on_expired_lease` (binds, then `self.expire_lease(task_id)` = explicit UPDATE to a past timestamp, then asserts `harness_resume["code"] == "HOOK_DENIED"` + `actions[0]["action"] == "resume_denied"` — with the comment "Denial CLASS, not the specific LEASE_EXPIRED string"). This directly demonstrates the deadlock + its resolution end-to-end through a real `HarnessService` + `CanonicalRunGuard`.
(b) **`--help` distinguishes `session_id` (hcom id) from the `recovery-tick --binding` display name** — SATISFIED. Both the `--session-id` arg help ("provider session_id -- the adapter identifier (hcom `session_id`), NOT the display name used by `maps recovery-tick --binding`") and the subparser `description=` spell it out.

## My mutation set (target: `_dispatch_run` wiring + subparser args + dispatch guards; oracle: `tests.test_cli_run`, 12 tests; ≤1 mut/run, `git checkout` + clean-tree check after each)

| # | Mutation | Result |
|---|----------|--------|
| M1 | `session_id=args.session_id` → `session_id=args.worker_id` | **KILLED** (FAILED 1 — `test_bind_session_makes_lineage_explicit`) |
| M2 | first positional `args.run_id` → `args.session_id` | **KILLED** (FAILED 9) |
| M3 | `created_by=args.created_by` → `created_by='maps-run-bind-session'` (its own default) | **SURVIVED** — see non-blocking note 1 |
| M4 | dispatch guard `args.run_command == 'bind-session'` → `!= 'bind-session'` | **KILLED** (FAILED 11) |
| M5 | `--adapter` default `'hcom'` → `'grpc'` | **KILLED** (FAILED 3) |
| M6 | `main()` `args.command == 'run'` → `'run-XXX'` | **KILLED** (FAILED 11) |
| M7 | `evidence_ref=args.evidence_ref` → `'hcom:attach:x'` (constant) | **KILLED** (FAILED 1 — `test_invalid_session_link_on_empty_evidence_ref`) |

**6 / 7 killed.** Working tree confirmed clean (`git status --porcelain` = 0) after the set.

## Non-blocking notes (do NOT block merge)
1. **M3 survivor** — no test passes a non-default `--created-by`, so hardcoding it to its own default value is undetected. Near-equivalent (the constant equals the default), low severity. Recommend a one-line test: `self.bind(run_id, created_by='alice')` then assert `resolve_run_session(run_id)['history'][0]['created_by'] == 'alice'`. Same shape as `test_created_by_defaults_to_verb_name`.
2. **Acceptance-2 coverage** — `RUN_STALE` and `SESSION_LINEAGE_INVALID` (both in #257 §2's table) aren't exercised. They need a contrived deeper store state (revision drift / a pre-existing INVALID chain) and the CLI handles them identically to every other code (uniform `_emit` passthrough — proven by the 7 covered codes). Optional to add.
3. **#257 note typo (not this PR)** — the merged #257 acceptance-3 names `tests.test_run_lineage`; the real module is `tests.test_run_session_lineage` (soda's dispatch had it right). Worth a one-line fix to the #257 note if anyone touches it; does not affect this impl.

## Verdict
**APPROVE.** The impl is a faithful thin wrapper matching #257's spec line-for-line, the full MUST-NOT list holds, the diff is exactly the two MAY-touch files, all five acceptance criteria are met with real end-to-end tests (including the deadlock-demonstration pair), both reviewer nits are satisfied, 80 targeted tests + smoke are green, and 6/7 of my independent mutations are killed (the survivor is a near-equivalent with a trivial optional test fix).
