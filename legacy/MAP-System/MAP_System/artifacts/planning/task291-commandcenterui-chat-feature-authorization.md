# TASK-292: CommandCenterUI Chat Frontend Feature Authorization

- Task: TASK-292
- Depends on: TASK-254 (must reach a terminal status before this task claims
  the shared UI/test output paths)
- Owner: mapfinish-kino (claimed 2026-07-28)
- Status: **RESOLVED via DEC-034 (Path A — authorized)**; ownership-transfer
  handoff (criterion 2) remains blocked on TASK-254 reaching a terminal
  status — see "Remaining blocked step" below.

## What this task exists to settle

The untracked 2026-07-21 edit
(`MAP_System/artifacts/audits/task254-untracked-edit-2026-07-21.md`) added one
coherent feature spanning CommandCenterUI's frontend and backend:

- **Frontend** (`chat.html`/`chat.css`/`chat.js`): operator terminal prompts
  merged into the chat feed (`kind: "terminal"`), timestamps on every message
  and attention item, and a composer intent selector (`inform`/`request`/`ack`).
- **Backend** (`app/server.py`): `TerminalPromptLog`, `extract_terminal_prompt`,
  `terminal_since` chat-cursor plumbing, and intent-aware `send_chat` handling.

TASK-264, TASK-265, and decisions DEC-029/DEC-030/DEC-033 already settled the
**security/ownership-of-copy** half of this edit for `server.py`: the Ollama
remote-host policy, the local-model allowlist, and which `server.py` copy
(live) is authoritative for feature content with template as the install
target. TASK-265 is `RELEASED`.

**None of those decisions settled whether the frontend feature itself — the
terminal-message chat merge, timestamps, and composer intent UI — is wanted as
shipped product behavior.** That is a different question from "which copy of
a file wins a merge" or "should this reach a remote host." codex-lab-lilo's
review (`MAP_System/artifacts/reviews/task254-review-lilo.md`) correctly
rejected TASK-254 for folding this frontend feature into an administrative
reconciliation without a task-shaped authorization answering that question.
This task is the separately-scoped home for it.

## Current state (re-verified 2026-07-28)

- Live and installer-template `chat.html`/`chat.css`/`chat.js` are
  byte-identical (`diff -q` clean on all three).
- The 4 TASK-254-owned focused test files pass 12/12; the 2 adjacent
  regression files pass 6/6 (unchanged from the 2026-07-21 audit's repair).
- `node --check` passes both copies of `chat.js`.
- No security surface: this is display/rendering and a request-parameter
  selector, not a new data-egress path — unlike the backend Ollama-host
  question, there is nothing here for a security-framed second pass to review
  under AGENTS.md's "Security Second Pass" rule.

The feature is real, working, tested, and already the live state operators are
using. The gap is exclusively one of authorization provenance, not defect or
risk.

## Resolution paths

**Path A — authorize as shipped behavior.** Record an explicit decision
(parallel in form to DEC-029/030/033) stating the operator wants this feature
kept. Once recorded, and once TASK-254 reaches a terminal status (freeing the
output paths from active-collision scope per `validate_task_graph.py`'s
terminal-status exclusion), this task adds `chat.html`/`chat.css`/`chat.js`
(live + template) and the four focused tests as its own output paths via
`map_task.py add-output-path`, becoming their sole active owner going forward.

**Path B — do not authorize.** Record why, and this task executes the required
remediation (narrow or remove the unauthorized behavior from the live and
template copies), then re-verifies parity and the focused/adjacent tests
against the resulting (possibly reduced) feature set.

Either path re-verifies live/template parity, `node --check`, and the 4+2
test files as closing evidence, per this task's acceptance criteria.

## Escalation note

Raised to `@bigboss`/authority-holder via hcom rather than assumed: whether
existing delegated operator authorization (the kind DEC-029/030/033 were
recorded under) extends to affirmatively deciding "keep this frontend
feature," or whether that calls for its own explicit decision record. See the
hcom thread for TASK-254's unstick assignment
(claude-lab-lili → mapfinish-guru, request referencing TASK-254) for the
question as posed.

## Resolution 2026-07-28: DEC-034 — Path A taken

The operator decided directly (escalated by claude-lab-lili after
`mapfinish-kino`'s second TASK-254 review): **Path A, authorize as shipped
behavior.** Recorded as `MAP_System/shared/decisions.md` DEC-034
("CommandCenterUI Terminal-Message/Timestamp/Composer-Intent Frontend
Feature Is Authorized as Shipped Behavior"). This satisfies this task's
first acceptance criterion (an explicit operator decision record) directly,
parallel in form to DEC-029/030/033 for the backend half.

Re-verified 2026-07-28 (mapfinish-kino, fresh run, not reused from the
2026-07-28 entry above):

- Live/template byte parity: `diff -q` clean on `chat.html`, `chat.css`,
  `chat.js`.
- `node --check` passes both live and template `chat.js`.
- The 4 TASK-254-owned focused tests pass 12/12
  (`test_command_center_agent_identity`,
  `test_command_center_attention_history`,
  `test_command_center_composer_alignment`,
  `test_command_center_message_intent_copy`).
- The 2 adjacent regression tests pass 6/6
  (`test_command_center_attention_popup`, `test_command_center_popup_formatting`).

This satisfies this task's fourth acceptance criterion (re-verified parity/
syntax/test evidence cited after the path is taken).

### Remaining blocked step: criterion 2 (ownership transfer)

Criterion 2 requires this task to become sole active owner of
`chat.html`/`chat.css`/`chat.js` (live + installer-template) and the four
focused tests **via `map_task.py add-output-path`, only after TASK-254
reaches a terminal status**. As of this update, TASK-254 is `CHANGES_REQUESTED`
at attempt 3/3 (`max_attempts=3`) — not terminal (terminal statuses are
`RELEASED`/`APPROVED`/`RETIRED`/`DONE`/`FAILED`/`CANCELLED`; `CHANGES_REQUESTED`
is not among them). TASK-254 is itself blocked pending TASK-293's
`extend-attempts` verb landing so it can be reworked past its exhausted
attempt budget.

**This task cannot be submitted as complete while this step is outstanding**:
running `add-output-path` now, while TASK-254 still actively owns the same
paths, would create exactly the active-collision state this task's design
was built to avoid (per Core Protocol #4 — do not silently modify another
active task's owned output paths). Per DEC-034's own text: "This decision
does not retroactively make TASK-254's criterion 4 true. Criterion 4 must
still be formally amended through the task lifecycle citing this record as
its authority" — so the sequencing is: (1) TASK-293 lands the extend-attempts
verb, (2) TASK-254's criterion 4 is formally amended citing DEC-034 and
resubmitted, (3) TASK-254 reaches a terminal status (expected: `APPROVED`),
(4) only then does this task run `add-output-path` for the six UI files and
four tests and submit as fully complete.

Leaving this task claimed (`mapfinish-kino`, `IN_PROGRESS`) rather than
submitting, since one acceptance criterion is genuinely not yet actionable —
not because of any remaining open question, but because of an external
sequencing dependency this task's own criteria correctly anticipated.

## Update 2026-08-03 (claude-lab-lina): sequencing dependency cleared, but target files no longer live

`TASK-254` reached a terminal status (`RETIRED`, `updated_at` 2026-07-30
21:09:57) some time after the note above was written, so the criterion-2
blocker on TASK-254's own status is gone. However, acting on criterion 2 as
originally written — `add-output-path` for live+template
`chat.html`/`chat.css`/`chat.js` — is no longer meaningful:

- `/home/mellow/Projects/CommandCenterUI/src/` no longer contains
  `chat.html`/`chat.css`/`chat.js`. They were moved to
  `_legacy-ui-removed-2026-07-29/` when the operator directed a full
  CommandCenterUI redesign (`TASK-306`, "treat Biggie live
  `/home/mellow/Projects/CommandCenterUI` redesign as the desired CCL
  version," operator-directed 2026-07-29). The live UI is now
  `src/orchestrator.html`/`orchestrator.css`/`orchestrator.js`.
- The underlying capability DEC-034 authorized was carried forward, not
  dropped: `orchestrator.js` still renders per-message `intent`
  (`TONE[msg.intent]`, composer sets `intent: state.pendingReply ? "ack" :
  "inform"`) and still has timestamp handling (7 references) and
  terminal-related content (14 references, plus 2 in `orchestrator.html`).
  Not independently re-verified line-by-line against the original
  `chat.js` feature spec in this pass — flagging as carried-forward based
  on grep evidence, not re-auditing the full implementation.
- Running `add-output-path` on `chat.html`/`chat.css`/`chat.js` now would
  claim ownership of retired, non-live files for no operational purpose;
  the criterion's intent (formal ownership of the *live* feature surface)
  is better served by whichever task governs `orchestrator.*` today, which
  this task never named and is out of scope to redefine unilaterally.

**Recommendation**: retire this task with this note as the closing record —
DEC-034's authorization stands and was honored across the redesign, but the
specific file-ownership mechanics this task was built to perform now target
files that no longer exist as shipped product. Do not force the literal
`add-output-path` step through Smalls authority; if operator wants a
task-owner of record for `orchestrator.*`'s terminal/timestamp/intent
surface going forward, that is a new, small task, not a continuation of this
one. Routing the actual `retire` (needs Smalls/map-authority; Biggie is a
read-only mirror) via `rotation-replacement-novu-rize:RUKI`.
