# PR #287 review evidence

reviewer: pr287-reviewer-sana (independent reviewer, session maps-lean-sana / session-26 coordinator rotated out; did NOT author PR #287 — kema implemented it, miso authored the design note and dispatched this review)
head_sha: 8626111f260da8c6b2ca7610e804bc71d93c3f8e
independent: true
summary: APPROVE (1 optional non-blocking observation) — mechanical pre-merge operator-authorization gate, ships DORMANT. Scope = exactly the 4 declared files (scripts/opcmd_merge.py, tests/test_opcmd_merge.py, work/notes/2026-09-04-merge-auth-mechanical-backstop-design.md, .gitignore ledger line), +1027/-0. No AGENTS.md / templates/ / playbook/ / CI / other-script touch (MUST-NOT list honoured). Tests fully mock the hcom/gh subprocess runner (FakeRunner monkeypatches opcmd_merge.run_command) — no network. 18/18 unit tests pass locally; CI `test` PASS at this head.

Full review history — three blocking findings raised and resolved:

- **F1 (blocking, FIXED + verified):** `check_scope`/`_names_pr` only checked that `#<N>` was PRESENT in the authz text, and step 4 (`check_no_hold`) only scans messages with `id > authz_id` — so an authz message that itself says "don't merge #N" (alone, or mixed with "merge #M") passed the gate for `#N`. Verified against the real code at Phase 1 (CASE A "merge #40 now. do not merge #42…" → GATE PASSED for #42; CASE B "do not merge #42 yet" → GATE PASSED). Fixed via `check_authz_not_prohibiting(msg, pr)` as step 3b (between scope and HOLD-scan): a PR-specific `do\w*\s*n[o']?t\s+merge\s+#?\s*<pr>` match, or a standalone HOLD/STOP/abort token, voids the authz message; a PR-specific prohibition of `#N` does not void a sibling `#M` authorized in the same message. Re-verified against the fixed head: CASE A → REFUSED, CASE B → REFUSED, sibling-authorization preserved. `test_authz_pure_prohibition_refused` / `test_authz_mixed_authorize_and_prohibit_refused` pin both. Design note gains §3.1 §3b.
- **O1 (non-blocking, done):** step 4 was fail-open if `hcom events --sql "id > N"` returned rc=0 with empty output for a reason other than "genuinely no later messages". `_assert_hcom_live(authz_id)` added — `hcom events --type message --all --last 1`; rc≠0 → EnvError, no message events → EnvError, newest id < authz_id → EnvError ("querying the wrong store"). `test_liveness_check_stale_stream_refused` covers it.
- **O2/O3/O4 (non-blocking, done):** `_names_pr` low-PR-number comment; design note §4/§5 reworded (ledger is `.gitignore`d local-only, the durable cross-clone audit trail is the pasted stdout JSON block); `test_naive_timestamp_stale_batch_designation_refused` exercises the real naive-ts path.
- **O6 (raised Phase 2, resolved in-PR):** soft natural-language deferrals ("#42 stays for later") are not caught — an unbounded NLP problem; the documented incident (post-authz HOLD) and the realistic threat (explicit "don't merge #N") are both covered. miso directed an in-PR doc fix: design note §3.1 gains a "Boundary" paragraph (the gate confirms an authorization exists and is not retracted, it does not infer intent from prose).
- **F2 (blocking, FIXED):** the original `DormancyTest` walked every prose `.md` and flagged any file mentioning `scripts/opcmd_merge.py` near "python"/"subprocess" — so this PR's own review-evidence file tripped it (surfaced by my first evidence commit failing CI). First narrowing scoped the walk to executable files + excluded `work/` and `.md`.
- **F3 (blocking, FIXED):** the F2 narrowing used `"work" in path.parts` on the ABSOLUTE path — the GitHub Actions checkout lives under `/home/runner/work/`, so `"work"` matched a runner path segment and `_is_executable_repo_file` returned False for every file, making the dormancy check inert in CI (`test_real_invocation_would_trip_the_walk` failed). Verified the mechanism (`('/','home','runner','work','MAPS_Lean','MAPS_Lean','scripts',…)`).
- **F3 fix (this head, reviewed):** dormancy check rewritten. `line_invokes_script(line)` is a pure filesystem-free regex matcher (`_INVOKE_RE`, verbose/case-insensitive): `import`/`from opcmd_merge`; a `subprocess`/`Popen`/`check_call`/`check_output`/`os.system`/`run(` call whose args name `opcmd_merge.py`; `opcmd_merge.py || …`; a shell-command-position `[python] …opcmd_merge.py` after `^`/`;`/`&`/`|`/`sh -c`. Traced against the 10 positive + 8 negative string cases (all correct) plus 4 adversarial lines of my own (`subprocess.run([…, os.path.join("scripts","opcmd_merge.py")])` caught; prose "see scripts/opcmd_merge.py:143 for the gate() flow" and "RUN scripts/opcmd_merge.py in CI" correctly not caught). `find_invocations(root)` enumerates candidates via `git ls-files -- *.py *.yml *.yaml *.sh` — always repo-relative, so the F3 absolute-path bug cannot recur — skips the script + its own test + first-segment `work`/`.git`, and applies the matcher line by line. `DormancyTest.test_script_is_dormant_in_the_repo` asserts `find_invocations(_ROOT) == []` against the real repo. The fixture-writing tests that wrote into the live checkout (O7) are removed; the string-matcher unit tests replace their coverage.

Verified SOLID against real `hcom events` output (Phase 1): message-event shape matches the tests' `_msg_event` exactly (`data.from` = sender, top-level `id`/`ts`/`type`); `hcom events --sql "id=N"` and `--sql "id > N"` (+ `--all`) both work, rc=0, correct ranges. Gate control flow: `--dry-run` returns before ledger write and before merge; steps 1-4 (+3b) raise `GateError` → exit 2 → no merge; `EnvError` → exit 3 → no merge; ledger append precedes `gh pr merge`; batch-designation 12h staleness bound enforced with a fail-closed unparseable-ts branch; `OPERATOR_IDENTITIES = {"bigboss"}` (fail-closed default; §6 flags the allowlist as an operator decision); coordinator/agent seats are structurally excluded (`test_coordinator_sender_refused`).

NON-BLOCKING OBSERVATION (O8, optional): `find_invocations` globs `.py`/`.yml`/`.yaml`/`.sh` — covers the realistic activation surfaces (a Python import, a `subprocess` call, a CI workflow, a shell script). A future activation via a root `Makefile`, `pyproject.toml [project.scripts]`, a git hook, or `package.json` would not be caught. This repo wires every tool as `python scripts/X.py` so the practical surface is covered; a one-line comment noting the glob's scope would suffice if wanted. Not blocking.

## Method

- Fresh clones across the review rounds: `/tmp/rev287` (14b8711, Phase 1),
  `/tmp/rev287b` (cde1364, Phase 2), `/tmp/rev287c` (8405fc1, O6), `/tmp/rev287d`
  (22af50c, F2 narrowing — CI failed → F3), `/tmp/rev287e` (this head,
  `8626111f260da8c6b2ca7610e804bc71d93c3f8e` == branch tip
  `feat/opcmd-merge-authz-gate`). Coordinator checkout never touched.
- F1: read `scripts/opcmd_merge.py` in full; traced steps 1→6 + 3b for
  fail-closed behaviour; built and ran the CASE A/B/C exploit as a standalone
  harness against the pre- and post-fix heads.
- hcom shape: ran `hcom events --last 3 --type message`, `--sql "id=<id>"`,
  `--sql "id > <id>" --all` against the live channel.
- F3 fix: read `_INVOKE_RE` + `line_invokes_script` + `find_invocations`; ran the
  18-test module (`python3 -m unittest tests.test_opcmd_merge` → OK); ran the
  matcher against the test's 18 cases + 4 adversarial lines; confirmed
  `git ls-files` works in a fresh clone and returns repo-relative paths.
- CI `test` observed: FAIL at d3c43b2 (F2), FAIL at 22af50c (F3), PASS at
  8626111 (this head).
- Phase 1 / Phase 2 / F2 / F3 findings + this verdict all posted to `@miso` /
  `@kema` on hcom before this evidence commit.

## Disposition

**APPROVE.** F1/F2/F3 all fixed and (F1) regression-tested; O1-O4 folded in; O6
resolved in-PR; O8 optional. No open blocking findings. Evidence bound to code
head `8626111f260da8c6b2ca7610e804bc71d93c3f8e`.
