# PR #210 review evidence — rule-20 safeguard: stale "no production caller" docstring CI check

reviewer: maps-lean-luve
head_sha: ce5e4e17c2b0f95cbb50b3e74be4fd32fea29b40
independent: true
summary: Independent review by maps-lean-luve (did not author). All 9 acceptance criteria PASS. Checker catches cross-file stale "no production caller" claims (verified by planting the reverted stale wording), is conservative against dormant-enum / prose / test-only false positives, split-across-lines and noqa handling verified, the skill_lifecycle_storage.py:12 fix is correct (production caller runtime.cli._dispatch_skill since #205), and the two new # noqa suppressions are each individually justified. No runtime logic change (docstring/comment/CI-yaml/new-script/tests only). Mutation testing: 8 mutations applied, 6 killed (min-5 met); 2 non-blocking survivors (M1 multi-backtick heuristic untested, M5 redundant inner call regex). VERDICT: APPROVE. Three non-blocking follow-ups noted, none gate merge.

## Verification commands

```
python3 -m unittest tests.test_check_stale_no_caller_docstrings   -> OK, 7 tests
python3 scripts/check_stale_no_caller_docstrings.py; echo exit=$?  -> "check_stale_no_caller_docstrings: OK", exit=0
python3 -m runtime.smoke; echo exit=$?                             -> {"ok": true}, exit=0
```

Worktree: `.claude/worktrees/rev-210` off `origin/worktree-rule20-stale-caller`. `git status` after checkout: clean (no staged-revert hazard).

## Acceptance criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Checker catches a planted stale claim (real non-test caller) | PASS |
| 2 | No false-positive on dormant-enum notes / prose / test-only / bare mention | PASS |
| 3 | Split-across-lines phrase handling (test + manual) | PASS |
| 4 | noqa escape hatch suppresses | PASS |
| 5 | skill_lifecycle_storage.py:12 fix correct — caller exists at HEAD | PASS |
| 6 | The two `# noqa` additions justified | PASS |
| 7 | No runtime logic change | PASS |
| 8 | Min-5 mutation on core logic | PASS (6/8 killed; 2 non-blocking survivors) |
| 9 | unittest green + smoke exit 0 | PASS |

### C1 — planted stale claim caught
Reverted the PR's own fix hunk in `skill_lifecycle_storage.py:12` back to the stale wording. Checker reported the correct symbol (`record_skill_lifecycle_transition`), the correct caller (`runtime/cli.py:469`), non-zero exit. Reverted plant; tree clean. Confirmed the PR's fixed wording produces a clean exit.

Known limitation (non-blocking): the defining-file exclusion keys on the file containing the *phrase*, not the file *defining the symbol*. A stale claim in a method's docstring with a new caller in the same module is not detected. Both historical cases (#204/#206, #205) and the recurring pattern (state/*.py store methods called from cli.py / recovery/) are cross-file, so the safeguard covers the real failure mode.

### C2 — no false positives
Realistic dormant-enum phrasings not in the curated list ("has no firing site yet", "is never emitted in production", "is dormant scaffolding, no writer wired", "no caller is wired yet", "reserved; nothing dispatches it today") all produce clean scans even with a real call present. Existing runtime/ dormant notes (`destructive_action_guard.py:220`, `production.py:387`) stay clean. Test-only caller: clean. Bare mention / string literal without `(`: clean. Whole-repo scan at HEAD: exit 0.

### C3 — split-across-lines
`test_claim_split_across_lines_is_caught` asserts it. Manual `scan()` on a 2-line-wrapped phrase + real caller → 1 failure reported. Mutation M7 (collapse the 2-line window to 1) is killed.

### C4 — noqa
`test_noqa_escape_hatch_suppresses` asserts it. Manual: phrase + real caller + `# noqa: stale-caller-check` on the closing `"""` → clean. Mutation M6 (disable the noqa branch) is killed.

### C5 — skill_lifecycle_storage.py:12 fix
`record_skill_lifecycle_transition` production caller confirmed at HEAD: `runtime/cli.py:469` inside `_dispatch_skill`, dispatching `maps skill approve|activate|retire|supersede`. Not a test path. Docstring wording now accurate.

### C6 — the two `# noqa` additions
- `runtime/policy/memory_provenance_guard.py:230` — claim: `HarnessService.send()` has no production caller yet. Verified: the only `.send(` hits in runtime are `adapter.send` / `backend.send` — none call `HarnessService.send` itself. Bare-name grep for `send(` would match all adapter methods, so the noqa is necessary and the underlying claim is genuinely still accurate. Justified.
- `runtime/recovery/production.py:57` — claim: `run_validation_tier` had zero production callers *before this module*; explicitly historical. Only live-looking grep hit is a dormant same-module builder (`validation.py:184` inside `make_validation_hook`, itself uncalled). Historical framing + dormant-only real hit → noqa justified. Not a hidden stale claim.

### C7 — no runtime logic change
`git diff 7459333..HEAD`: 6 files. `.github/workflows/review-evidence.yml` (+CI step), `scripts/check_stale_no_caller_docstrings.py` (new), `tests/test_check_stale_no_caller_docstrings.py` (new). The three runtime files are docstring / comment / `# noqa` only — zero executable lines changed. Confirmed line-by-line.

### C8 — mutation testing (checker core: symbol resolution + caller detection)

| # | Mutation | Outcome |
|---|----------|---------|
| M1 | `_symbol_for`: pick first backticked symbol on line instead of last | SURVIVED |
| M2 | `_symbol_for`: disable the enclosing-`def` fallback | KILLED |
| M3 | `_callers`: drop the defining-file self-exclusion | KILLED |
| M4 | `_callers`: drop the `tests/` path exclusion | KILLED |
| M5 | `_callers`: replace call regex `symbol\s*\(` with bare `symbol in text` | SURVIVED |
| M6 | `scan`: disable the `# noqa` escape hatch | KILLED |
| M7 | `scan`: collapse the split-across-lines 2-line window to 1 line | KILLED |
| M8 | `scan`: always skip via the prev-window dedup guard | KILLED |

6/8 killed — min-5 satisfied. Survivors non-blocking: M1 (no test has two backticked symbols on the phrase line; worst case is wrong-symbol output but still a non-zero exit forcing a human look), M5 (inner call-shape regex is effectively dead code — the upstream `/usr/bin/grep "symbol("` already excludes bare mentions).

## Verdict: APPROVE

All 9 criteria pass. No runtime behavior change. Non-blocking follow-ups for a later pass (do not gate this merge):
1. Same-module caller blind spot (defining-file exclusion keys on phrase file, not symbol-def file).
2. M1 — add a test with two backticked symbols on the phrase line.
3. M5 — either test the inner call regex directly or drop it as dead code.
