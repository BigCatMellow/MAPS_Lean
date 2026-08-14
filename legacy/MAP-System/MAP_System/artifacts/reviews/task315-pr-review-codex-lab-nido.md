# TASK-315 PR-level independent review - codex-lab-nido

- reviewer: codex-lab-nido
- requested_by: zeno
- reviewed_pr: https://github.com/BigCatMellow/MultiAgentProject/pull/1
- reviewed_commit: 2e45f14fd4eb2e7e2d013ed52f1aa0ca92e16eb4
- review_type: PR-level independent review; TASK-315 was still `IN_PROGRESS` locally and had no open review claim at review time.
- verdict: CHANGES_REQUESTED for merge

## Findings

1. BLOCKING: `events/events.jsonl` is rewritten instead of appended.

   The PR changes `Source/MAP_System/events/events.jsonl` with 155 deleted JSONL event records and 4,845 added records. The first hunk changes an existing event type from `REVIEW_RECORD_CORRECTED` to `PROGRESS`; the next hunk replaces a 157-line historical block with a 4,847-line block whose prior `limit_watcher` event timestamps differ. This violates the repository rule that progress uses "append-only event records in `events/events.jsonl`" (`docs/agent-quickstart.md:38`) and the MAP rule to use `events/events.jsonl` for "short append-only activity records" (`MAP_System/AGENTS.md:47`). Historical event corrections should be new correction/progress events, not edits or deletions of old records.

   Evidence: PR diff hunk for `Source/MAP_System/events/events.jsonl` begins at `@@ -4498,7 +4498,7 @@` and `@@ -4709,157 +4709,4847 @@`; local diff inspection counted 155 deleted event records.

2. BLOCKING: Command Center can run model-backed summarization in a hidden background path.

   The PR-head Command Center server allows `SUMMARY_PROVIDER` from environment or `runtime/ui-settings.json` and documents Antigravity as "non-interactive" print mode (`Source/MAP_System/templates/install/command-center-ui/app/server.py:118-121`). When enabled, the background summarizer sends agent message content into `agy --effort low --sandbox --print` via `subprocess.run` (`server.py:1904-1910`), and the fallback path can call Ollama directly. Current MAP helper-routing policy says every LLM agent and model-backed helper must remain visible, launched with `--terminal wezterm-tab`, and "If a deterministic watcher invokes a model for judgment, that model invocation is agent work and must move to a visible terminal/session" (`MAP_System/AGENTS.md:150-160`). This PR would ship an operator-configurable hidden model worker over hcom message content, without a visible terminal, helper note, or stop/approval surface matching that policy.

   Required fix: remove/disable background model summarization, or route it through an explicitly visible, bounded helper/session with durable ownership and stop controls, or obtain and record an explicit operator policy exception before merging.

## Checks Performed

- Resolved PR #1 from commit `2e45f14` with `gh pr list`.
- Read PR metadata and changed file list via GitHub CLI.
- Pulled PR patch to `/tmp/pr1.diff` for read-only inspection.
- Read PR-head versions of `map_authority.py`, `graph/runner.py`, `render_active_state.py`, Command Center `server.py`, `orchestrator.js`, and attention tests through GitHub raw content.
- Ran `operational_lessons.py orientation --scope helper-routing --pretty`; active lesson confirms visible model-backed helpers and no headless/hidden model workers.
- Did not run the PR test suite locally because the target commit is not present in this checkout and the working tree is heavily dirty; GitHub reports no status checks on the PR.

## Non-blocking Notes

- The PR-head authority/freshness work appears to address the prior direct-runner gap: direct runner output now calls `summarize_with_authority()` and gate/interruption paths use `output_with_authority()`.
- SQLite runtime sidecar removal (`map.db-shm`, `map.db-wal`) is directionally correct, but merge should wait until the event-log rewrite and hidden model-worker issue are resolved.
