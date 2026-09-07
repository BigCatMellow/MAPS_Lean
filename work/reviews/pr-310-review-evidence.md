# PR #310 review evidence — row 6.22 impl: production call site for HarnessService.send()

reviewer: nuvi (independent focused re-reviewer; no prior involvement with row 6.22 / harness-send work; not leta/polo/ledo/buna/kava/zeno/nima/lulu/zura/tara)
head_sha: 0849be4db7dc73565e8784fee0c801cfcb0acbfe
independent: true
summary: APPROVE. Focused re-review of the single blocking finding from ledo's prior independent review (stale "no production caller" docstring in runtime/policy/memory_provenance_guard.py::register_memory_provenance_guards, plus the blanket `# noqa: stale-caller-check` that defeated the rule-20 safeguard). polo's fix commit 0849be4 is docstring-only (6 ins / 7 del, single file), noqa removed, zero logic/contract/other-file change. New wording is accurate: runtime/cli.py::_dispatch_send_context (cli.py:741) really calls `service.send(binding, session_ref, payload)` and is the sole production caller of HarnessService.send() (all other `.send(` hits in runtime/ are adapter/backend methods or docstring/comment text). scripts/check_stale_no_caller_docstrings.py exits 0 with the noqa gone: the corrected docstring contains none of STALE_PHRASES, so the checker scans the block, matches nothing, and moves on — a genuine pass, not a silent miss (the noqa escape-hatch path is only consulted when a phrase is matched). All prior-APPROVE items still hold at 0849be4: §5 output boundary intact (name-only vs origin/main = the 5 in-scope files + memory_provenance_guard.py docstring + this evidence file, nothing else), factor move / assembler / default-off / fail-closed unchanged. CI `test` job PASS on the new head (run 34090202545). Full `unittest discover -s tests` run locally at 0849be4. Merge remains under the 3-day operator hold — DO NOT MERGE.

## Delta verified (fresh clone, PR head 0849be4)

### 1. git diff be1d2c1a..0849be4 — docstring block ONLY
Commits in range: `983f475` (ledo's CHANGES-REQUESTED evidence file) + `0849be4` (the fix). `git show 0849be4 --stat` = `runtime/policy/memory_provenance_guard.py | 13 +++++-------` (6 ins, 7 del) — nothing else. Diff hunk is the docstring at ~L225-234: "composing this guard changes no live behavior because `HarnessService.send()` has no production caller yet" replaced with "as of PR #310 that send path has its first production caller: the `maps run send-context --deliver-context` CLI verb (`runtime/cli.py::_dispatch_send_context`)". The trailing `# noqa: stale-caller-check` on the docstring closing line is removed. Guard body below the docstring (`if type(guard) is not MemoryProvenanceGuard: raise TypeError`, `registry._register_enforcement(...)`) untouched. No contract/signature/other-file change.

### 2. New wording is accurate
- `grep -n "\.send(" runtime/cli.py` → `runtime/cli.py:741  result = service.send(binding, session_ref, payload)`, lexically inside `_dispatch_send_context` (def at cli.py:659). Real syntactic production call.
- `grep -rn "\.send(" runtime/` → other hits are `adapter.send` / `self.adapter.send` / `backend.send` (unrelated adapter/backend methods) and docstring/comment prose (context_delivery.py, cli.py:193, memory_provenance_guard.py). `_dispatch_send_context` is the first and only production caller of `HarnessService.send()`.

### 3. check_stale_no_caller_docstrings.py — exit 0, and it SEES the docstring
`python3 scripts/check_stale_no_caller_docstrings.py` → `check_stale_no_caller_docstrings: OK`, exit 0. Manual scan of runtime/policy/memory_provenance_guard.py against every STALE_PHRASES entry ("no production caller[s]", "zero production caller[s]", "no production writer", "no runtime caller", "no non-test caller", "not called in production", "no real production caller") → zero matches. Checker flow: scan file text for a STALE_PHRASE; only if one is found does it resolve a symbol and consult the `# noqa` escape hatch. Phrase gone ⇒ checker inspects the block, matches nothing, proceeds. True pass, not a skipped symbol.

### 4. Full test suite
`python3 -m unittest discover -s tests -v` run at 0849be4 — see §6.

### 5. Prior APPROVE spot-check at 0849be4
- `git diff --name-only origin/main...0849be4` = runtime/cli.py, runtime/context_delivery.py, runtime/harness/binding_resolution.py, runtime/policy/memory_provenance_guard.py, runtime/recovery/supervisor.py, tests/test_context_delivery.py, work/reviews/pr-310-review-evidence.md. Exactly the 5 in-scope files + the docstring-only guard edit + this evidence file. §5 boundary intact: service.py, harness_guard.py, production.py, CAPABILITY_CHECKLIST.md, hooks.py all empty-diff.
- ledo's §2c/§2d/§2e/§2f findings (assembler correctness, verbatim binding-resolution factor move, default-off byte-identity, four fail-closed paths tested, stacking on #307 acknowledged) are unaffected by a docstring-only change and stand as reviewed.

### 6. CI on new head
`gh pr checks 310`: `test` → **pass** (1m33s, run 34090202545). `review-evidence` → fail (expected: committed evidence pointed at be1d2c1 until this commit rebinds it).

## Verdict
APPROVE (independent, focused re-review). The single blocking finding is resolved cleanly, docstring-only, safeguard now honest. All other prior-review items hold. Merge stays under the 3-day operator hold.
