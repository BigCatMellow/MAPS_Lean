# Review: TASK-240 CommandCenterUI attention-popup formatting

- task_id: TASK-240
- reviewer: codex-lab-lilo
- task_owner: codex-lab-kiri
- risk_tier: medium

## Verdict

CHANGES_REQUESTED

## Files Reviewed

- `MAP_System/tasks/TASK-240.json`
- `/home/mellow/Projects/CommandCenterUI/src/chat.js`
- `/home/mellow/Projects/CommandCenterUI/src/chat.css`
- `MAP_System/templates/install/command-center-ui/src/chat.js`
- `MAP_System/templates/install/command-center-ui/src/chat.css`
- `MAP_System/tests/test_command_center_popup_formatting.py`

## Forbidden Changes Check

PASS — the formatter changes only display text in the attention popup. It does
not change message routing, reply targets, request intent, or approval logic.

## Acceptance Criteria Check

| Criterion | Result | Evidence |
|---|---|---|
| Preserve newlines and wrap long popup text | PASS | Both CSS copies use `white-space: pre-wrap`, `overflow-wrap: anywhere`, bounded width, and vertical overflow. |
| Render structured request fields on separate lines | PASS | Both JS copies use `formatPopupText()` to normalize line endings and insert a newline before `Issue`, `Options`, `Recommendation`, and `Needed` labels before rendering. |
| Live and installer code stay equivalent and focused checks pass | PARTIAL | Byte-for-byte parity presently passes for both `chat.js` and `chat.css`; the focused test passes. However, the task record does not declare the actual live files, so MAP cannot truthfully track ownership of the live half of this change. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/tasks/TASK-240.json` | The registered live output paths are `../CommandCenterUI/src/chat.{js,css}`, but those paths do not exist from this repository. The edited live files are `/home/mellow/Projects/CommandCenterUI/src/chat.{js,css}` (equivalent relative path from `Source` is `../../CommandCenterUI/...`). As submitted, the task record only tracks the installer copies, leaving the operator-facing source outside declared ownership and future parity review. | Correct the task metadata through a sanctioned lifecycle path (or supersede/replace the task record if correction is not supported) so it explicitly records the actual live `CommandCenterUI` files alongside the installer copies. Do not release while the nonexistent paths are the only registered live outputs. |

## Verification

- `cmp -s /home/mellow/Projects/CommandCenterUI/src/chat.js MAP_System/templates/install/command-center-ui/src/chat.js` — PASS.
- `cmp -s /home/mellow/Projects/CommandCenterUI/src/chat.css MAP_System/templates/install/command-center-ui/src/chat.css` — PASS.
- `python3 MAP_System/tests/test_command_center_popup_formatting.py` — PASS (2 tests).
- Inspected `formatPopupText()` in both JS copies and popup CSS in both CSS copies.
- Confirmed `../CommandCenterUI/src/chat.js` is absent while `/home/mellow/Projects/CommandCenterUI/src/chat.js` exists.

## Notes

The implementation is narrow and the current source pairs are aligned. The
focused test is source-contract based rather than a DOM behavior test; a small
fixture exercising representative one-line request text would be a useful
follow-up, but it is not required for this correction.
