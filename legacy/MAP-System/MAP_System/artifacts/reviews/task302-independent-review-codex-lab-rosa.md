# TASK-302 Independent Review

task_id: TASK-302
reviewer: codex-lab-rosa
task_owner: codex-live
review_date: 2026-07-28

## Verdict

APPROVED.

The fixed AI Command Center Lab roster is restored through the existing
instruction-bearing launchers. The installed KUDU runtime matches the rendered
templates, the focused tests pass, and the live workspace exposes Codex,
Claude, Pi, Librarian, Shell, and New Agent as expected. The delivery evidence
records the fresh-launch Monitor pane and equivalent RUKI verification.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | `ai-command-center-lab.lua` starts Codex, Claude, Pi, and Librarian through their dedicated launchers. `hcom list -v --json` and `wezterm cli list --format json` independently showed live `codex-lab-rosa`, `claude-lab-damo`, `pi-lab-lila`, and `helper-librarian-boho` identities in visible WezTerm panes. |
| 2 | PASS | The startup callback retains Shell and starts New Agent and Monitor. The delivery artifact records a fresh dedicated-socket launch with all seven required panes. The installed Monitor launcher is an unchanged persistent five-second loop. |
| 3 | PASS | The Codex launcher identifies Codex as one fixed-roster member and contains no sole-orchestrator or withhold-the-roster instruction. It also preserves task ownership, independent-review, approval, and startup-rotation boundaries. |
| 4 | PASS | The 12 focused startup tests and two tab-title tests pass. All four source and installed fixed-agent launchers pass `sh -n`; the installed WezTerm configuration parses; rendered source templates exactly match the five KUDU runtime files. The delivery artifact records the live fresh-launch inspection and equivalent RUKI checks. |

## Files Reviewed

- `MAP_System/tasks/TASK-302.json` through `map-authority task show TASK-302`
- `MAP_System/artifacts/operations/command-center-fixed-roster-2026-07-28.md`
- `MAP_System/notes/command-center-orchestrator-lifecycle.md`
- `MAP_System/templates/install/wezterm/ai-command-center-lab.lua`
- `MAP_System/templates/install/bin/ai-command-center-lab-codex`
- `MAP_System/templates/install/bin/ai-command-center-lab-claude`
- `MAP_System/templates/install/bin/ai-command-center-lab-pi`
- `MAP_System/templates/install/bin/ai-command-center-lab-librarian`
- `MAP_System/tests/test_command_center_orchestrator_startup.py`
- `/home/mellow/.config/wezterm/ai-command-center-lab.lua`
- `/home/mellow/.local/bin/ai-command-center-lab-codex`
- `/home/mellow/.local/bin/ai-command-center-lab-claude`
- `/home/mellow/.local/bin/ai-command-center-lab-pi`
- `/home/mellow/.local/bin/ai-command-center-lab-librarian`

## Forbidden Changes Check

PASS. This review did not modify implementation, launcher, configuration,
database, task, event, or installed runtime files. The only reviewer-authored
file is this review artifact. Canonical task state was read and claimed through
`map-authority`; the read-only KUDU `map.db` mirror was not mutated.

## Verification

- `python3 MAP_System/tests/test_command_center_orchestrator_startup.py` — PASS, 12/12.
- `python3 -m unittest MAP_System.tests.test_command_center_lab_tab_titles -v` — PASS, 2/2.
- `sh -n` over the four source and four installed fixed-agent launchers — PASS.
- `wezterm --config-file /home/mellow/.config/wezterm/ai-command-center-lab.lua show-keys` — PASS.
- Rendered-template diffs for the four fixed launchers and WezTerm configuration — no differences.
- `hcom list -v --json --name rosa` — all four fixed model-backed identities live and non-headless.
- `wezterm cli list --format json` — visible fixed-agent, Shell, and New Agent panes observed.
- `map-authority status` — KUDU confirmed as a read-only mirror.

## Risks And Notes

- The current later pane listing did not include Monitor, although the
  fresh-launch evidence records it and its persistent launcher is unchanged.
  A tab can be closed after startup; this later observation does not contradict
  the recorded fresh-launch acceptance check.
- KUDU's local SQLite mirror had not yet synchronized TASK-302 during review.
  Canonical task reads and the atomic review claim succeeded against RUKI
  through `map-authority`, so no local lifecycle state was used as authority.
- The historical TASK-286 design remains in the lifecycle note but is clearly
  labeled historical and superseded. The current operator direction is stated
  first.
