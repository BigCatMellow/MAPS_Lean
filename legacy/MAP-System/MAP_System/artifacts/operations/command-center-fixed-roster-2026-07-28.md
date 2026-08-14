# TASK-302 Fixed Command Center Lab Roster

- status: verified_and_installed_both_pcs
- operator_direction: The Lab must open with its specific agents and
  instructions.
- supersedes_runtime_topology: TASK-286 minimal orchestrator-driven startup

## Required fresh-launch tabs

- Shell
- Codex Lab
- Claude Lab
- Pi Lab
- Librarian
- New Agent
- Monitor

## Implementation

- The WezTerm `gui-startup` callback invokes each agent's existing
  instruction-bearing launcher.
- Task-scoped extra agents remain available through New Agent and `hcom`.
- The Codex launcher must not claim that the other fixed agents should be
  withheld at startup.

## Root causes found

1. TASK-286 intentionally reduced the fixed roster to a sole Codex
   orchestrator plus operator tabs, contrary to the current operator direction.
2. The WezTerm startup callback called `set_title` through an unsupported
   `gui_window()` path on the installed WezTerm build. The exception aborted
   the callback before any agent tabs were created.
3. Current `hcom` defaults launches to preview-only. Fixed launchers without
   `--go` displayed a preview and exited instead of starting their agent.

## Verification

- `python3 MAP_System/tests/test_command_center_orchestrator_startup.py`:
  12 focused checks passed.
- `python3 -m unittest MAP_System.tests.test_command_center_lab_tab_titles -v`:
  2 checks passed.
- All four fixed agent launchers and installed copies pass `sh -n`.
- The live WezTerm config parses with the installed
  `wezterm 20240203-110809-5046fc22`.
- A fresh Lab launched on dedicated socket `gui-sock-86072` with seven panes:
  Shell, Codex, Claude, Pi, Librarian, New Agent, and Monitor.
- The corresponding live identities were:
  - `codex-lab-rosa`
  - `claude-lab-damo`
  - `pi-lab-lila`
  - `helper-librarian-boho`
- Every agent was visible in a WezTerm tab and registered through `hcom`.
- The eight TASK-302 source files were copied to RUKI's canonical project
  tree.
- Only the five rendered runtime files were installed on RUKI; the broader
  installer was not applied because its dry run also proposed replacing the
  unrelated CommandCenterUI bundle.
- RUKI passed the same 12 focused tests, all four installed launchers passed
  `sh -n`, and its live WezTerm configuration parsed successfully.
- RUKI's five installed runtime checksums match the staged `/home/home`
  render exactly.
