reviewer: /root/pr162_reviewer
head_sha: 0a687e2fa429ecf90e9679d5b49e12c217847318
independent: true
rebase_note: Reviewed content was at ce2d5782 (design note, single-file, 241 insertions, fully fact-checked below). A subsequent `git merge origin/main` (bringing the branch current past #161) produced merge commit 0a687e2, which the checker's walk-back cannot skip past (merge commits stop the walk). `git diff ce2d578 0a687e2 --stat -- work/notes/2026-08-24-rns-production-trigger-loop-design.md work/reviews/pr-162-review-evidence.md` is empty -- the reviewed design note and this evidence file are byte-identical before and after the merge. head_sha rebound per the same procedure `work/reviews/pr-160-review-evidence.md` documents; the reviewed content is unchanged.
summary: APPROVED — the design note is factually accurate against current runtime/ code, respects §7.1/§7.9 non-goals (bounded one-shot CLI invocation, no daemon/cron/scheduler, no continuous discovery agent), is scoped design-only (single new file, no runtime/tests/roadmap changes, no DONE row claimed), and follows the PR154/PR160 pattern (finding, constraint, survey, single justified decision, call-site boundary, non-goals, open behavior questions, bounded follow-up scope).

# Review: PR #162 RnS production trigger loop design

- Reviewed file: `work/notes/2026-08-24-rns-production-trigger-loop-design.md`
- Pattern precedent: `work/notes/2026-08-21-rns-harness-validation-callsite-design.md` (shaped merged PR #160)
- Reviewer: `/root/pr162_reviewer`
- Verdict: `APPROVED`

## Scope check

- `PASS` — `git diff origin/main...origin/rns-trigger-loop-design --stat` shows exactly one file changed: `work/notes/2026-08-24-rns-production-trigger-loop-design.md` (241 insertions, 0 deletions). No runtime/, tests/, scripts/, or roadmap/checklist file touched.
- `PASS` — Note's own header states "no runtime behavior changed"; confirmed by the diff above.
- `PASS` — No roadmap/checklist row is marked `DONE`. The note's "Roadmap impact" section explicitly states it "does not close the insight file's finding" and defers implementation.

## Independent fact-checks against `origin/main` (commit `4431b3a`, post-#160)

- `PASS` — Zero production callers of `RecoverySupervisor(`/`.tick(`/`observe_silent_stops`. Ran `grep -rln 'RecoverySupervisor('`, `grep -rln '\.tick('`, and `grep -rn observe_silent_stops` against the full tree myself: matches are only in `tests/test_recovery_supervisor.py`, `tests/test_runtime_review_hardening.py` (also a test), and a comment in `runtime/recovery/store.py`. Matches the note's claim exactly.
- `PASS` — `tick()`'s required inputs. Read `runtime/recovery/supervisor.py:46-56` directly: `__init__(self, *, task_reader, hcom, recovery_store=None, backoff_seconds=..., silent_stop_probe_delay_seconds=..., environment_reader=None, harness_service=None)`. Matches the note's description (task_reader, hcom, recovery_store, environment_reader optional/advisory, harness_service optional) precisely, including that `environment_reader` and `harness_service` are both optional and advisory/fallback-safe.
- `PASS` — HookRegistry claim. Read `runtime/harness/hooks.py` (full `HookRegistry.run()`) and `runtime/harness/service.py:280-343`: `self.hooks.run(HookEvent.BEFORE_RESUME, ...)` is called only inside `HarnessService.resume()`, and `self.hooks.run(HookEvent.SESSION_STOPPING, ...)` only inside `HarnessService.stop()`. No other call site of `HookRegistry.run()` exists in `runtime/harness/service.py`. This confirms the note's load-bearing claim that hooks fire only as a side effect of an already-in-progress resume/stop attempt, not as an independent trigger — the circularity argument for rejecting the Hook-registry approach holds.
- `PASS` — `runtime/cli.py` subcommand list. `grep -n "sub.add_parser"` lists: init, create, shape, check, promote, show, trace, run-record, freeze-case, context, status, claim, heartbeat, submit, review-claim, review-record, outcome-record, outcomes, events, reviews, flow (with flow-start/flow-review-start subparsers) — matches the note's enumerated list exactly. No `recovery`/`rns`/`supervisor`-named subcommand exists (confirmed by the same grep — none present).
- `PASS` — `claim` calls `store.claim_task(...)`. `runtime/cli.py:297-298`: `if args.command == 'claim': return _emit(store.claim_task(args.task_id, args.worker_id, lease_seconds=args.lease_seconds))`. `store = TaskStore(args.db)` constructed at `runtime/cli.py:229`, top of `main()`, exactly as the note states.
- `PASS` — `build_status` is read-only. Read `runtime/status.py`: every operation inside `build_status` is a `SELECT` via `store._connect()`; the emitted status dict includes an explicit `"communication_hcom": False` field. No hcom call, no mutation. Justifies the note's rejection of attaching `tick()` there.
- `PASS` — `TaskStore` duck-types as `tick()`'s `task_reader` and is already exercised this way in tests. `tests/test_recovery_supervisor.py:383,423` and `:641,704` construct `self.task_store = TaskStore(self.root / "maps.db")` then `RecoverySupervisor(task_reader=self.task_store, ...)` — a real `TaskStore` instance, not a fake, used specifically (per the test file's own comments) to exercise the real schema-backed lineage lookups (`resolve_session_run`, `resolve_run_session`, `compute_task_revision`). This grounds the note's central "reuse the existing `store = TaskStore(args.db)` object directly" proposal in actual, already-passing test evidence rather than a hand-waved assumption.

## Non-goal / pattern-rigor check

- `PASS` — No daemon/cron/scheduler/always-on process proposed anywhere (§7.1). The proposed mechanism is exactly two one-shot, exit-on-completion call sites (a new `recovery-tick` subcommand, and a call appended to the existing `claim` branch) — no listener, no reschedule, no background thread.
- `PASS` — No continuous discovery/process-police agent proposed (§7.9). The note explicitly frames its choice as the "bounded audits and deterministic checks" alternative §7.9 prescribes, and cites `scripts/coordination_housekeeping.py` as existing precedent for this shape.
- `PASS` — Follows the PR154/PR160 pattern: has a single Finding section (grep-verified, not inferred), a Constraint section citing the exact roadmap non-goals, a Survey of alternatives considered and rejected with reasons, one concrete Decision with numbered justification, an explicit Call-site boundary (which object, which file, which existing construction point, exact optional-parameter handling), an explicit Non-goals-for-implementation list, and an explicit "Behavior questions the implementation task must answer" section in the same style as #160's design note — confirmed by side-by-side structural comparison with `work/notes/2026-08-21-rns-harness-validation-callsite-design.md`.
- `PASS` — No scope creep into already-tracked adjacent gaps. The note explicitly defers `harness_service` construction/wiring ("Do not build harness_service wiring as a side effect of this task; that is the separate, already-landed #160 gap") and explicitly excludes validation-tier execution as "separate, already-tracked H4/E4/6.5 fast-follow." It does not implement or specify internal changes to `tick()` itself.

## Findings

No blocking findings. No factual inaccuracies found against current `origin/main` code. No hand-waving detected in the central `claim`/`recovery-tick` proposal — every claim was independently verified against source, not merely restated from the note's prose.

## Reviewer limits

- Did not execute the design (there is no code to execute — design-only note, confirmed by scope check above).
- Did not evaluate the open "Behavior questions" section's answers, since the note correctly defers them to the implementation task rather than answering them itself; nothing to verify there beyond confirming the section exists and does not silently pre-decide them.
- Missing context/evidence: none.
- New requirements discovered: none.
