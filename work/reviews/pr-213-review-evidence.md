# PR #213 review evidence — Follow-up to #210: close 3 non-blocking stale-caller-checker items

reviewer: maps-lean-nava
head_sha: acbb15a7699a823c2846e684b4c703c8f36f945e
independent: true
summary: APPROVE — same-module blind spot closed by a pure-AST caller pass (fail-then-pass proven), M1 multi-backtick attribution locked in both directions, M5 dead regex removed with no coverage gap; 18/18 checker tests green, whole-repo scan exit 0, runtime.smoke exit 0, diff is scripts/ + tests/ only, 8 mutations on the new logic all killed. head_sha rebound by coordinator after a clean single-commit rebase onto main (015dcc6 → acbb15a); no code content change from the reviewed 0a6e85e tree.

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Same-module stale claim with a real non-test caller is NOW caught (fail-then-pass) | PASS. `_callers` replaced grep + defining-file exclusion with an `ast.Call` walk over every non-test `runtime/**/*.py`; same module no longer excluded. `test_same_module_caller_is_caught` asserts 1 failure naming `store.py:6`; passed silently on origin/main's checker. `test_sibling_method_call_in_same_class_is_a_caller` covers the intra-class variant. |
| 2 | Cross-file behavior unchanged, all prior tests green | PASS. All 7 origin/main tests retained verbatim and green. 7 → 18 tests. |
| 3 | `python3 scripts/check_stale_no_caller_docstrings.py` exit 0 on current tree | PASS. `check_stale_no_caller_docstrings: OK`, exit=0. |
| 4 | No new false positives (dormant-enum / prose / test-only / bare-mention) | PASS. `test_repo_checkout_is_clean` scans the real repo → `[]`. `test_bare_mention_is_not_a_caller`, `test_string_literal_named_like_a_call_is_not_a_caller`, `test_only_test_caller_passes` green. `STALE_PHRASES` stays curated with no "no firing site / no call site" phrasing. Non-blocking: no dedicated dormant-enum fixture (none on main either). |
| 5 | M5 (dead call-shape regex) removal leaves no gap | PASS. An `ast.Call` node with matching callee name is call-shaped by construction. `x = symbol` → `Assign`/`Name`, `'symbol()'` → `Constant` — neither is `ast.Call`. Two tests prove no regression. Rationale comment added above `_callers`. |
| 6 | AST approach doesn't regress on syntactically-odd files | PASS. `_runtime_sources` wraps `ast.parse` in `except (SyntaxError, UnicodeDecodeError): continue`. Verified ad hoc with a broken `runtime/broken.py`: as bystander the real stale claim elsewhere still caught; bearing a stale claim itself it is silently skipped, no crash. Conservative false-negative on an unparseable file, which fails py_compile/CI elsewhere. |
| 7 | Diff = scripts/ + tests/ only, ZERO runtime/ or roadmap change | PASS. Files = exactly `scripts/check_stale_no_caller_docstrings.py`, `tests/test_check_stale_no_caller_docstrings.py`. |
| 8 | Min-5 mutation on new AST caller-detection logic, all killed | PASS. 8 distinct mutations, all KILLED. |
| 9 | unittest foreground green + runtime.smoke exit 0 | PASS. `Ran 18 tests OK` (blocking foreground, 0.7s). `runtime.smoke` → `"ok": true`, exit=0. |

## Mutation log (`scripts/check_stale_no_caller_docstrings.py`, new logic)

| # | Mutation | Result |
|---|----------|--------|
| M1 | `_symbol_for`: `before[-1]` → `before[0]` (farthest backtick) | KILLED — failures=2 |
| M2 | `_symbol_for`: drop the `m.start() < cut` filter | KILLED — failures=1 (`test_backtick_after_phrase_is_ignored`) |
| M3 | `_callers`: neutralize the recursion skip | KILLED — failures=1 (`test_recursive_self_call_is_not_a_caller`) |
| M4 | `_runtime_sources`: stop excluding `tests/` dirs | KILLED — failures=1 (`test_only_test_caller_passes`) |
| M5 | `_callee_name`: drop the `ast.Attribute` branch | KILLED — failures=8 |
| M6 | `_callee_name`: drop the `ast.Name` branch | KILLED — failures=1 (`test_bare_function_call_is_a_caller`) |
| M7 | `_symbol_for`: keep the full dotted symbol | KILLED — failures=1 (`test_dotted_backtick_symbol_resolves_to_final_attr`) |
| M8 | `_phrase_line_starts`: find only the first phrase occurrence | KILLED — failures=1 (`test_two_stale_claims_same_phrase_one_file_both_reported`) |

Worktree restored after each mutation and at end (`git status --porcelain` clean).

## Notes / non-blocking

- Recursion exclusion is line-range based; two unrelated same-named functions → calls in either body skipped. Acceptable conservatism for a false-positive-averse checker.
- Unparseable `runtime/` file bearing a stale claim is silently not caller-checked (documented `# pragma: no cover`); breaks other CI gates first.
- PR body "dormant-enum cases retained" = curated phrase list + `test_repo_checkout_is_clean`, not a dedicated fixture.

## Verdict

APPROVE.
