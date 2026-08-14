# Independent Review: TASK-286 (Minimal, Orchestrator-Driven CCL Startup)

**Reviewer:** helper-review-task-286-gina  
**Date:** 2026-07-27  
**Task Submitted By:** claude-lab-venu

---

## Verdict

**APPROVED**

TASK-286 meets all acceptance criteria and exhibits honest, careful design around the authority boundary it explicitly documents. The implementation reduces CCL default startup from six auto-opened tabs to three (Shell, Codex Lab, Monitor), moves lane-opening decisions to the Codex orchestrator (which decides based on live SQLite/runner state, not terminal presence), and clearly disclaims any new authority or capability the orchestrator gains from this role.

The changes are well-scoped, thoroughly tested (12/12 tests pass), and pose no regression risk to existing operations or continuity safeguards.

---

## Acceptance Criteria Check

### ✓ Criterion 1: Default topology opens only Shell, Codex, Monitor
**PASS** — Verified in lua file (lines 120-129):
- `gui-startup` spawns exactly three tabs: Shell, Codex Lab, Monitor
- Claude/Pi/Librarian are not referenced in the gui-startup handler
- Tests `test_default_topology_starts_shell_codex_monitor_only` and `test_default_topology_does_not_auto_open_claude_pi_librarian` both pass

### ✓ Criterion 2: Orchestrator routes from SQLite/runner, uses visible workers, records progress durably
**PASS** — Verified in orchestrator prompt (ai-command-center-lab-codex):
- Explicitly mentions `runner route and live SQLite claims are the only authority for whether a lane needs to open`
- Instructs: `hcom N <tool> --tag <lane> --terminal wezterm-tab only when the runner route or an actual READY/SUBMITTED task genuinely needs`
- References `MAP_System/scripts/operational_lessons.py` and `graph/runner.py` for routing context
- Uses hcom for durable progress communication
- Tests `test_orchestrator_prompt_routes_from_runner_and_sqlite_state` passes

### ✓ Criterion 3: Finished workers placed in standby/terminal; no unsolicited replacement rotation
**PASS** — Verified in orchestrator prompt:
- Instructs: `mark it standby via python3 MAP_System/scripts/declare_standby.py <name> rather than leaving it ambiguously idle`
- Explicitly prohibits: `do not launch a replacement or rotation for it unless it is verified-live with an actual claim or continuation obligation still open`
- Lifecycle note confirms orchestrator startup is read-only (context_rotation.py validate/advise) and does not launch replacements
- Tests `test_orchestrator_prompt_avoids_unsolicited_replacement_rotation` and `test_orchestrator_prompt_marks_finished_lanes_standby` both pass

### ✓ Criterion 4: Focused tests prove topology, launchers, provider binding, no headless, no regression
**PASS** — All 12 tests pass:
- `test_default_topology_*`: Confirm Shell/Codex/Monitor startup, no Claude/Pi/Librarian
- `test_on_demand_launchers_still_exist_and_are_unchanged_scripts`: Confirms Claude/Pi/Librarian launchers remain available
- `test_no_fixed_provider_to_role_binding_in_orchestrator_prompt`: Verifies prompt explicitly disclaims permanent provider bindings
- `test_no_headless_launch_path_anywhere_in_ccl_scripts`: Confirms no headless launch introduced; prompt states "never --headless"
- `test_shell_and_monitor_launchers_unaffected`: Confirms operator surfaces preserved
- `test_lua_config_is_syntactically_valid` and `test_codex_launcher_shell_syntax_is_valid`: Structural validation

Test file's docstring honestly discloses limitation: "These are static content checks against the wezterm config and launcher scripts -- there is no way to actually drive a GUI wezterm session inside a test. That is a real limitation (see the delivery note's residual risk), not something this suite claims to close."

### ✓ Criterion 5: Delivery evidence documents migration, rollback, boundaries, routing vs. authority
**PASS** — Verified in command-center-orchestrator-lifecycle.md:
- **Migration** section (line 90): Documents exact changes to lua and codex prompt files
- **Rollback** section (line 106): Clear, reversible steps (revert gui-startup to spawn all six tabs, revert codex prompt paragraph)
- **Residual risk** section (line 114): Honestly lists three residual risks:
  1. Does not affect already-running sessions (only fresh startup)
  2. Orchestrator lane-opening is prompt-guidance only, not deterministic (could be hardened in future task)
  3. Privacy/approval boundaries unchanged (orchestrator still subject to same safeguards)
- **Orchestrator routing vs. autonomous authority** section (line 71): **Explicitly disclaims** any new authority:
  - "Acting as the default orchestrator grants no capability beyond what any core agent already has"
  - "does NOT: bypass approval gates, launch headless, spawn helpers without proper notes, bind providers permanently"
  - "Routing is a decision about when to start already-sanctioned, already-visible workers, not a new authority layer"

Test `test_lifecycle_note_documents_migration_rollback_and_residual_risk` passes.

---

## Authority Question (Deep Scrutiny)

**Question:** Does the orchestrator prompt actually grant the Codex lab session any new capability it didn't already have (bypass gates, spawn headless, self-approve, bind fixed provider)?

**Answer: NO. The authority boundary is sound.**

**Evidence:**

1. **No bypass of approval gates**: The prompt explicitly instructs "use hcom send --intent request only for operator decisions, approvals, blockers, conflicts, privacy/scope risks, or questions" — unchanged from prior Codex lab responsibilities. No new self-approval.

2. **No headless spawning**: Prompt states "Every model-backed agent/helper must remain visible; always use --terminal wezterm-tab and never --headless" — this is an *additional* constraint, not a permission. Tests confirm this guard phrase is present.

3. **No permanent provider binding**: Prompt explicitly disclaims: "it must never bind a specific provider permanently to an organizational role (worker choice stays a per-task routing decision, not a fixed identity)." This is read directly from the prompt and is consistent with the lifecycle note.

4. **Routing ≠ Authority**: The key paragraph (present in prompt, lines 8-9 in the ai-command-center-lab-codex file):
   > "Routing is not authority: this Codex session gets no capability beyond a normal core agent from acting as orchestrator -- it must still honor every existing approval gate, privacy boundary, no-headless rule, and review-separation rule, and it must never bind a specific provider permanently to an organizational role (worker choice stays a per-task routing decision, not a fixed identity)."
   
   This is not merely aspirational. It is a clear statement of constraint, not capability.

5. **No self-approval**: The prompt instructs that the Codex orchestrator "must not approve \[its\] own substantive deliverables" — this is Core Protocol rule 9, unchanged.

**Critique of the claim "routing is not authority"**: The claim holds. Routing decisions (when to spawn Claude, Pi, Librarian lanes) are decisions about *which already-authorized workers to invoke*, made by consulting SQLite and the runner route. The Codex orchestrator remains one core agent among peers, gaining only the responsibility to read task state and decide whether other lanes should be opened. This is advisory decision-making, not new capability.

---

## Files Reviewed

1. **MAP_System/tasks/TASK-286.json** — Task definition, acceptance criteria, output_paths
2. **MAP_System/notes/command-center-orchestrator-lifecycle.md** — Design, migration, rollback, residual risk, authority boundaries
3. **MAP_System/templates/install/bin/ai-command-center-lab-codex** — Orchestrator prompt (full text review)
4. **MAP_System/templates/install/wezterm/ai-command-center-lab.lua** — GUI startup function (lines 120-129) and keybindings (lines 209-214)
5. **MAP_System/tests/test_command_center_orchestrator_startup.py** — Test suite (12 tests, all passing)
6. **MAP_System/inbox/helpers/helper-review-task-286.md** — Review assignment and scope

---

## Forbidden Changes Check

**Method:** Verified using output_paths list and file modification times (as instructed in review assignment, avoiding raw git diff).

**Registered output_paths for TASK-286:**
- MAP_System/notes/command-center-orchestrator-lifecycle.md
- MAP_System/templates/install/bin/ai-command-center-lab-codex
- MAP_System/templates/install/wezterm/ai-command-center-lab.lua
- MAP_System/tests/test_command_center_orchestrator_startup.py

**Verification:**
- All four output_paths show recent mtimes (2026-07-27 13:49–13:51)
- No other MAP_System files show modifications from the same time window that would suggest out-of-scope changes
- Keybindings in lua file (Ctrl+4, Ctrl+5, Ctrl+6) are unchanged and still reference tabs 3, 4, 5; these remain safe as they simply activate additional tabs if opened manually, not auto-created by startup
- Spot-checked for references to tab index assumptions in other Python/shell scripts: none found
- On-demand launcher scripts (claude, pi, librarian, shell, monitor) all remain unchanged and runnable

**Result: No forbidden changes detected. Scope is clean.**

---

## Regression Risk Assessment

**Reducing tabs from 6 to 3 at startup:** LOW RISK

- All on-demand launchers (claude, pi, librarian) remain fully available and directly runnable
- Tests confirm keybindings are unaffected (Ctrl+1..6 still exist; they just activate fewer pre-opened tabs)
- No code in MAP_System assumes all six tabs are always open by default
- Operators can manually open additional lanes at any time using standard elastic-helper invocation
- This change only affects the *default* startup; it does not affect already-running sessions

**Test suite limitation honestly disclosed:** The test suite uses static content checks only (no actual GUI wezterm drive). The test docstring explicitly states this limitation and refers readers to the lifecycle note's residual-risk section.

---

## Summary

TASK-286 is a carefully scoped, well-tested lifecycle correction that moves CCL lane-opening from "open everything by default" to "open based on what work actually exists." The orchestrator role is purely advisory/routing, not a new authority layer. Authority boundaries are preserved and clearly documented. No regression risk identified.

Approved for merge.
