# PR #187 review evidence

reviewer: independent-reviewer-a42e2056
head_sha: 65bc4f893bc11765c4f5cfdce63a986ecb876e74
independent: true
summary: APPROVE — scope clean (6 files, no runtime/ or AGENTS.md), context_rotation.py constant-only change with correct math, boundary test genuinely updated to new constants (25/25 pass), pre-existing test_startup_context_rotation.py ValueError confirmed identical on clean origin/main, doc-sprawl green; only non-blocking nits. (head_sha re-bound to merge commit 65bc4f8 after update-branch; `git diff 0e3b963 65bc4f8 -- . ':!work/reviews/'` is only already-merged PR #174 Spiderweb-audit content — none of #187's own files changed.)

## Checks performed

- `git diff origin/main...0e3b963 --stat`: exactly the 6 expected files. No `runtime/` code, no `AGENTS.md` authority content, no extra files.
- `context_rotation.py`: only `DEFAULT_THRESHOLD_TOKENS` (150k->185k), `SOFT_FRACTION` (0.60->0.78), `HARD_FRACTION` (0.75->0.90) changed + comment block. Flat `soft_at = int(threshold * 0.80)` unchanged. argparse `--threshold-tokens` still `default=DEFAULT_THRESHOLD_TOKENS`.
  - flat default: soft `int(185000*0.80)`=148000, rotate 185000 — matches comment.
  - 200k window: rotate `min(185000, 180000)`=180000; soft `min(148000, 156000)`=148000 — matches PR body.
- `test_context_rotation.py`: assertions updated to 147999/148000/185000 and proportional soft_at=78000 rotate_at=90000 (input bumped 75000->95000 to stay rotation_due under new 90000 cap). Still tests real boundary behavior. 25/25 pass (ran test functions directly; file is bare `test_` funcs, not unittest/pytest-discoverable in this tree). On origin/main the old-constant version also passes 25/25 — not rubber-stamped.
- Pre-existing failure (#4): `python3 tests/test_startup_context_rotation.py` fails with `ValueError: substring not found` in `prompt_text()` (codex launcher parser) on branch head AND identically on clean origin/main (7aeefa8). Pre-existing, unrelated. NOT blocking.
- `python3 -m unittest tests.test_documentation_sprawl`: 22/22 OK. FRICTION_LOG lives in already-routed `work/coordination/`, no PLAYBOOK_SURFACE_BUDGET bump needed. `test_work_index_routes_every_top_level_record_directory` passes.
- FRICTION_LOG: 5 entries, consistent format. Entry 1 correctly describes the 3-layer countermeasure (SessionStart hook `maps-handoff-context` + `claude-selfclear` verify-and-retry + >2h stale warning) and honestly marks itself UNVERIFIED end-to-end. Entries 3 and 4 correctly UNVERIFIED. Entries 2 and 5 verified/n-a appropriately.
- Playbook edits: `REPAIR_AND_LEARNING.md` capture section + `ROADMAP_TRAJECTORY_CHECK.md` consumption duty form a coherent capture->consumption loop, no contradiction with surrounding text. TENTH_SEAT cross-ref points to `playbook/TENTH_SEAT_REVIEW.md`, accurately describes "Trigger 2" (trajectory-check pass finding nothing after passes that found something) and its section 7 "signs this has gone wrong" duty.
- `templates/handoff.md`: one checklist line, correct relative link to FRICTION_LOG.

## Non-blocking nits

- FRICTION_LOG.md is not listed in `work/coordination/README.md` read-order; discoverable only via playbook cross-refs. Consider adding a line.
- `SOFT_FRACTION` constant now 0.78 but the flat (no-window) branch still hardcodes `0.80`; the constant only binds in the known-window branch. Comment documents this correctly, but the constant name reads as if it governs both.
- Legacy `tests/test_context_rotation.py` is not exercised by any CI workflow (runtime-stack-tests only covers repo-root `tests/`); pre-existing gap, not introduced here.
