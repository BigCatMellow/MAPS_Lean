# Re-review: TASK-290 (Orchestrator auto-spawns an independent reviewer for unclaimed SUBMITTED tasks)

```
task_id:     TASK-290
reviewer:    task288-review-valo
task_owner:  lili-replacement-nisa
```

## Verdict

APPROVED

## Prior review

`MAP_System/artifacts/reviews/task290-independent-review-task288-review-valo.md`
(CHANGES_REQUESTED) — one REQUIRED finding: neither
`command-center-orchestrator-lifecycle.md` nor the `ai-command-center-lab-codex`
`PROMPT` named `scripts/review_routing.py`; both described the author/lineage
disqualification check via raw primitives and single-hop prose reasoning,
risking a future hand-reimplementation that regresses the tested
multi-hop/history-inclusive logic.

## Fix verified

- `MAP_System/notes/command-center-orchestrator-lifecycle.md` (lines
  84-102): now explicitly says to "use `MAP_System/scripts/review_routing.py`
  (TASK-290) rather than hand-deriving author/lineage disqualification from
  the underlying primitives directly," gives the exact CLI invocation and
  the in-process `eligible_reviewer()` call, and adds a sentence naming the
  precise failure mode my finding described: "A hand-rolled single-hop
  version of this check ... would regress silently on a multi-hop rotation
  chain — do not re-derive it inline." This is not a superficial name-drop;
  it addresses the substance of the finding.
- `ai-command-center-lab-codex`'s `PROMPT`: the `next_route=review` clause
  now reads "run `MAP_System/scripts/review_routing.py <task_id>
  --live-agent <name>` for each live core agent (or call `eligible_reviewer`
  directly) ... this is the tested multi-hop-correct check, do not
  hand-derive it inline from the raw primitives." Read the actual string
  (not just grep count) to confirm the wording, not just the presence of
  the module name.
- `bash -n MAP_System/templates/install/bin/ai-command-center-lab-codex` —
  syntax OK, reproduced myself. Worth checking again specifically because
  nisa was editing the same apostrophe-fragile single-quoted string a
  second time (it broke once already during this task, per the original
  helper note).
- Reran both test suites myself: `test_review_routing.py` 7/7 PASS,
  `test_release_gate.py` 9/9 PASS (16/16 total) — unchanged from before,
  consistent with this being a text-only fix with no code touched.

## Acceptance Criteria Check

All 6 remain PASS, per the original review; AC3 (author/lineage exclusion)
is now PASS without qualification — the doc/prompt gap that was the sole
blocker is closed.

## Files Reviewed

- `MAP_System/notes/command-center-orchestrator-lifecycle.md` (diff: `review_routing.py` reference)
- `MAP_System/templates/install/bin/ai-command-center-lab-codex` (diff: `PROMPT` clause)
- `MAP_System/scripts/review_routing.py`, `MAP_System/tests/test_review_routing.py` (re-ran, unchanged)
- `MAP_System/tests/test_release_gate.py` (re-ran, unchanged, confirms no regression on the unrelated TASK-288 gate)

## Forbidden Changes Check

Fix is confined to the two doc/prompt files named above, both within
TASK-290's registered `output_paths`. No code files changed (confirmed:
`review_routing.py`/`test_review_routing.py` test output is identical to
the prior pass, same 7 tests, no additions). No scope violation found.

## Notes

Second REQUIRED finding in a row (after TASK-288) that got fixed with a
real, substantive correction rather than a minimal check-the-box edit —
the new doc text explicitly warns against the exact regression path my
finding described. Approving.
