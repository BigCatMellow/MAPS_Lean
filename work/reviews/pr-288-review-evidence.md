# PR #288 review evidence

reviewer: pr288-reviewer-sana (independent reviewer, session maps-lean-sana / session-26 coordinator rotated out; did NOT author PR #288 — lohe implemented it, miso dispatched this review)
head_sha: c05adc32ad4ba3dbc0c5c7a80243c49b54bc2274
independent: true
summary: APPROVE — sharded self-bounding local test runner (dispatched-worker full-suite-stall mechanical safeguard, rule 20). Scope = exactly the 5 declared files (scripts/run_tests_sharded.py, tests/test_run_tests_sharded.py, scripts/hooks/block-monitor-on-tests.example.json, work/notes/2026-09-04-monitor-stall-mechanical-safeguard-design.md, work/coordination/FRICTION_LOG.md), +649/-0, stdlib only. MUST-NOT list honoured — no runtime/ / .github/ / playbook/ / templates/ / AGENTS.md touch. Runner's own suite 10/10 green; CI `test` PASS at this head. All six of the review-brief focus areas verified empirically (no pipe-to-tail in any check).

- **(a) WARMUP_IMPORTS ImportError swallow — reviewed + tightened.** Phase 1: the swallow does not cause under-reporting (the shard still runs `unittest.main` on the real module; its exit code is honest, so a broken `runtime.state` surfaces via the test modules that import it — it cannot turn a real failure into a PASS), but `except ImportError` also swallowed a *present-but-broken* warmup module, which would then read as "the known circular import". lohe narrowed it to `except ModuleNotFoundError` at this head. Verified: a warmup target that `raise`s during import now propagates and fails the shard loudly ("reached past warmup" is not printed); a genuinely-absent module (`no_such_pkg_xyz`, `test_missing_warmup_import_is_swallowed`) is still tolerated. Comment updated to match.
- **(b) Exit code — trustworthy.** Verified directly: all-pass → rc 0; a module with a failing test → rc 1; per-module timeout → rc 1; no `-k` match → rc 2; run from the wrong cwd → rc 2 ("tests dir not found"). `bad = [r for r in results if r.status != PASS]; if bad: return 1`; a killed/OOM'd shard returns a negative code → `!= 0` → FAIL. No path from a failed / errored / timed-out module to rc 0. Addresses `feedback_pipe_to_tail_masks_exit_code` (the runner emits per-module status directly, no need to pipe for readability).
- **(c) Streaming — verified.** Ran a 4-second fixture module with `--heartbeat 1`: `running 1s / 2s / 3s / 4s` heartbeat lines appeared live at 1-second intervals while the shard was still running, then the `PASS … (4.1s)` line. `_emit` does `write()` + `flush()` per line (now under `threading.Lock` — N1). Per-module verbose output is captured and only dumped at the end for FAILING modules — intended.
- **(d) Circular-import claim + the 4 `test_environment_*` modules — accurate.** `python3 -m unittest tests.test_environment_spec` in isolation → `FAILED (errors=1)` (circular import). All four `test_environment_*` modules through the runner (`WARMUP_IMPORTS = ("runtime.state",)`) → PASS, shard rc 0. The warmup genuinely resolves the cycle — it is not masking (the shard's `unittest.main` exit code is honest; failing tests would be reported FAIL). The FRICTION_LOG entry's import chain (`runtime/environment/__init__.py` → `.fingerprint` → `.spec` → `runtime.state.observability` → `runtime/state/__init__.py` → `.store` → `.environment` → back) and its "only the full 96-module alphabetical run masks it" claim match what I reproduced. The entry's follow-up correctly frames the warmup as a workaround and defers the real cycle-break to a separate PR (this PR's MUST-NOT list forbids touching existing source).
- **(e) `block-monitor-on-tests.example.json` — valid + correct.** Valid JSON, `hooks.PreToolUse`, matcher `Monitor|Bash`. Ran the embedded python one-liner against 5 payloads: Monitor-on-`unittest` → deny; Bash + `run_in_background` + `pytest` → deny; Bash foreground `run_tests_sharded` → allow (`{}`); Monitor on `watch kubectl` → allow; Bash background `sleep 100` → allow. Correct `PreToolUse` decision shape (`hookSpecificOutput.permissionDecision: "deny"` + reason).
- **(f) Hook dormancy — confirmed.** `scripts/hooks/*.json` is not a path Claude Code auto-loads; the file is `.example.json` with a `_comment` telling the reader to paste the `hooks` block into their own git-ignored `.claude/settings.local.json`. Only referenced from the design note (§3.2 / §5). Nothing activates it.

## Method

- Fresh clones: `/tmp/rev288` / `/tmp/rev288b` (Phase 1, old head 4e07acd then the
  rebase head ceb912f) and `/tmp/rev288c` (this head
  `c05adc32ad4ba3dbc0c5c7a80243c49b54bc2274` == branch tip
  `feat/sharded-test-runner`). `#288` was rebased onto merged `#287` by the
  coordinator between Phase 1 and now (`git diff ceb912f c05adc3` = exactly the
  three Phase-1 fixes). Coordinator checkout never touched.
- Read `scripts/run_tests_sharded.py` in full; traced `_run_one` → `run` → `main`
  status/exit-code flow.
- Ran: the runner's own suite (`python3 -m unittest tests.test_run_tests_sharded`
  → 10 OK); the runner against a real failing fixture module (→ rc 1); a 4s slow
  fixture with `--heartbeat 1` (streaming); `tests.test_environment_*` bare
  (ERROR) vs through the runner (PASS); the hook one-liner against 5 tool
  payloads; a `raise`-on-import warmup target (propagates under
  ModuleNotFoundError narrowing).
- `git diff origin/main --name-only` → 5 files, no MUST-NOT path.
- CI `test` observed PASS at ceb912f and c05adc3.
- Phase 1 findings + this verdict posted to `@miso` / `@lohe` on hcom before this
  evidence commit.

## Disposition

**APPROVE.** No blocking findings. Phase-1 item (a) tightened + N1/N2 applied at
this head; the circular-import workaround is documented as a tracked follow-up
(a separate PR breaks the cycle). Evidence bound to code head
`c05adc32ad4ba3dbc0c5c7a80243c49b54bc2274`.
