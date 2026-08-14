# TASK-320 Antigravity Command Center Retirement

- status: implementation_complete_pending_ruki_live_stub_approval
- operator_decision: remove Antigravity from the AI Command Center because its
  token limit is not useful for this workload
- owner: rotation-replacement-duma-bono
- independent_reviewer: Claude replacement identity pending rotation completion
- authority: RUKI through `map-authority`; Biggie's local `map.db` was not
  mutated

## Boundary

Retire Antigravity from active AI Command Center surfaces:

- fresh Command Center Lab startup tabs;
- Codex, Claude, Pi, and Librarian startup prompts;
- legacy Command Center CLI/shell/deck launch, status, log, and help paths;
- active MAP routing availability;
- current capability guidance; and
- assignments in the reviewed research-adoption program.

Preserve historical tasks, reviews, events, and archived evidence. Preserve
generic hcom/provider tooling outside the Command Center. TASK-320 does not
uninstall the Antigravity application or rewrite history.

## Before-state evidence

- The canonical WezTerm template already omitted the Antigravity startup tab,
  but Biggie's installed config still contained the tab, palette/tool labels,
  and extra tab shortcuts.
- Biggie's installed Codex/Claude/Pi/Librarian prompts still named
  `antigravity-lab` or described Antigravity as fixed-roster.
- No live Antigravity hcom identity, process, language-server process, or
  WezTerm pane was present when the task began.
- `test_command_center_lab_tab_titles` failed because installed behavior did
  not match the canonical template.
- RUKI's authoritative runner still listed `antigravity` as available.

## Changes

### Biggie live runtime

- Removed the Antigravity palette/tool mapping, startup tab, and obsolete tab
  shortcuts from `~/.config/wezterm/ai-command-center-lab.lua`.
- Removed Antigravity coordination/roster language from the four installed
  fixed-agent launch prompts.
- Did not restart or close the Command Center because there was no Antigravity
  pane/process and a restart would disrupt active operator work. WezTerm
  automatically reloads its configuration; the next fresh launch uses the
  reduced roster.

Backups:

- `~/.config/wezterm/ai-command-center-lab.lua.pre-antigravity-retirement-20260809`
- `~/.local/bin/ai-command-center-lab-codex.pre-antigravity-retirement-20260809`
- `~/.local/bin/ai-command-center-lab-claude.pre-antigravity-retirement-20260809`
- `~/.local/bin/ai-command-center-lab-pi.pre-antigravity-retirement-20260809`
- `~/.local/bin/ai-command-center-lab-librarian.pre-antigravity-retirement-20260809`
- `~/.local/bin/ai-command-center-lab-antigravity.pre-antigravity-retirement-20260809`

### Repository/runtime guidance

- Removed active Antigravity support from the legacy CLI, shell, and agent
  deck.
- Replaced the remaining Command Center UI fallback tooltip with a
  provider-neutral message in both template and Biggie live source.
- Converted `ai-command-center-antigravity` into an explicit retired stub so
  stale callers fail clearly instead of launching it.
- Kept `antigravity-wrapper` unchanged as generic provider tooling outside the
  Command Center.
- Removed Antigravity as an assignable capability and replaced research-plan
  UI duties with Codex implementation, Claude independent review, and operator
  visual/workflow acceptance.
- Added focused regression checks for the startup, legacy surfaces, plan,
  capability matrix, live config, and preserved provider boundary.

### Authority state and second host

Completed on RUKI:

- Changed the canonical `antigravity` agent record to `offline` with reason
  `operator_retired_unusable_token_limit` through the authority path.
- Regenerated `agents/status.json` and `shared/current-state.md`; both task and
  shared-state validators passed on RUKI.
- Verified `graph/runner.py` lists `antigravity` under unavailable agents and
  not under available agents.
- Verified `/home/home/.config/wezterm/ai-command-center-lab.lua` already has
  fixed startup tabs for Codex Lab, Claude Lab, Pi Lab, and Librarian only,
  with no Antigravity startup entry. Read-only SHA-256 verification:
  `17e9bf9aaa9732be786e2aa1dae02bc8d2c707d00140bfc2911b890fbf51a1b6`.

Open approval boundary:

- `/home/home/.local/bin/ai-command-center-lab-antigravity` is absent. RUKI's
  approval reviewer rejected installing the retired stub as a persistent live
  launcher change without explicit operator approval. The denial was preserved
  and was not retried or bypassed.
- RUKI requested an operator decision: approve the retired-stub install or
  explicitly accept the absent launcher as the retired state.
- Independent review remains pending until this deployment boundary is settled.

## Verification

Completed on Biggie:

```text
python3 -m unittest MAP_System.tests.test_command_center_lab_tab_titles -v
  PASS (2 tests; previously failed on live-template drift)

sh -n ~/.local/bin/ai-command-center-lab-{codex,claude,pi,librarian}
  PASS

rg -i antigravity <active Biggie startup/config/prompt paths>
  no matches

python3 MAP_System/tests/test_command_center_orchestrator_startup.py
  PASS (13 checks)

python3 -m unittest MAP_System.tests.test_antigravity_command_center_retirement -v
  PASS (6 tests)

python3 MAP_System/tests/test_command_center_deployment_parity.py
  PASS (7 checks)
```

Final task verification must also run:

```text
python3 MAP_System/tests/test_command_center_orchestrator_startup.py
python3 -m unittest MAP_System.tests.test_antigravity_command_center_retirement -v
python3 MAP_System/scripts/validate_task_mirrors.py
python3 MAP_System/scripts/validate_shared_state_tasks.py
MAP_System/.venv/bin/python MAP_System/graph/runner.py
```

The current runner result lists `antigravity` under unavailable agents and not
under available agents. `validate_shared_state_tasks.py` and `git diff --check`
pass. `validate_task_mirrors.py` is temporarily blocked by concurrent TASK-321
owner-mirror drift; TASK-321's owner was asked to synchronize its own mirrors.

## Rollback

Rollback requires an explicit new operator decision because the removal itself
is operator-directed. If ordered:

1. restore the six Biggie backup files listed above;
2. restore the reviewed source patch rather than copying historical scripts
   blindly;
3. restore RUKI live configuration from its recorded backup;
4. change agent availability through RUKI authority, never local mirror SQL;
5. rerun focused startup, prompt, task-mirror, shared-state, and runner checks.

No user data, task history, reviews, events, or generic provider tooling is
deleted by either the retirement or this rollback procedure.
