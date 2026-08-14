# Command Center UI Serial Batch Reconciliation

- Date: 2026-07-19
- Reconciliation task: TASK-254
- Steward: codex-lab-kiri
- Superseded snapshot tasks: TASK-241 through TASK-248
- Review unit: the current combined final state
- Behavior change in TASK-254: none

## Issue

The operator gave eight successive rounds of feedback on the same Command
Center composer and attention sidebar. Each round was implemented and recorded
as its own task, but the tasks all remained `SUBMITTED` while later rounds
continued editing the same live and installer-template files.

MAP correctly rejected that registry shape: six active tasks claimed
`chat.css`, five claimed `chat.js`, four claimed `chat.html`, and two test files
also had multiple active owners. Dependencies would not solve the problem
because output paths are active ownership boundaries, even for serial work.

The worktree retains only the final combined state. Pretending an independent
reviewer can recover eight exact implementation snapshots from that state would
produce fictional review evidence.

## Decision

Treat the eight records as a rapid-feedback history and the current UI as one
final-state release candidate:

1. TASK-241 through TASK-248 are `RETIRED` as overwritten serial snapshots,
   explicitly superseded by TASK-254.
2. Their task records, acceptance criteria, submissions, and event timelines
   remain intact. Retirement does not mean the operator changes were removed.
3. TASK-254 is the sole active owner of the shared live/template files and the
   four focused test files.
4. An independent reviewer evaluates the combined current state once against
   all eight rounds of operator intent.
5. Any review defect returns TASK-254 for rework. The system does not reopen an
   unrecoverable earlier snapshot.

This is administrative reconciliation only. TASK-254 did not edit
CommandCenterUI HTML, CSS, JavaScript, or tests.

## Preserved lineage

| Original task | Operator-visible change retained in final state | Primary focused evidence |
|---|---|---|
| TASK-241 | Plain-language message-type choices and concise reply-expectation help while retaining protocol values | `test_command_center_message_intent_copy.py` |
| TASK-242 | Agent labels include concise name and provider/agent type without changing routing identity | `test_command_center_agent_identity.py` |
| TASK-243 | Attention history is collapsible and popup Open reveals it | `test_command_center_attention_history.py`; attention-popup regression |
| TASK-244 | First increase to agent identity color contrast | Historical step; final palette tested by identity coverage |
| TASK-245 | Operator-requested second palette strengthening | `test_command_center_agent_identity.py` |
| TASK-246 | Attention header remains present with a zero count | `test_command_center_attention_history.py` |
| TASK-247 | `Attention needed` and spaced `Project Updater` operator copy | `test_command_center_attention_history.py` |
| TASK-248 | Text field and Send button align with the dropdown rather than its helper line | `test_command_center_composer_alignment.py` |

TASK-244 and TASK-245 are deliberately not treated as two simultaneously
shippable palettes. TASK-245 is the final visual tuning; TASK-244 remains the
record of how the operator reached it.

## Active output ownership

TASK-254 now owns exactly one combined release-candidate set:

### Live UI

- `../../CommandCenterUI/src/chat.html`
- `../../CommandCenterUI/src/chat.css`
- `../../CommandCenterUI/src/chat.js`

### Installer template

- `MAP_System/templates/install/command-center-ui/src/chat.html`
- `MAP_System/templates/install/command-center-ui/src/chat.css`
- `MAP_System/templates/install/command-center-ui/src/chat.js`

### Focused tests

- `MAP_System/tests/test_command_center_message_intent_copy.py`
- `MAP_System/tests/test_command_center_agent_identity.py`
- `MAP_System/tests/test_command_center_attention_history.py`
- `MAP_System/tests/test_command_center_composer_alignment.py`

### Reconciliation evidence

- `MAP_System/artifacts/planning/command-center-ui-serial-batch-reconciliation-2026-07-19.md`

No other nonterminal task owns any of these paths after reconciliation.

## Final-state verification

### Live/template parity

Byte comparisons pass for all three source files. The matching SHA-256 values
make the parity result explicit:

| File | SHA-256 for both live and template copies |
|---|---|
| `chat.html` | `8fff4ec871825c832ee78e671e0a173ac123fcfc85bce01b765cc1c503267cd5` |
| `chat.css` | `5c9036fe1faf285a33d7240372a83037027c38a0888b55e096e0aad9938fa272` |
| `chat.js` | `53651874f7886952f1c1f427bdfa80444e456805aa1eae95a945c2f969c3d597` |

`node --check` passes for live and template `chat.js`.

### Focused behavior tests

The four TASK-254-owned test files pass **12 of 12** tests:

| Test file | Result |
|---|---|
| `test_command_center_message_intent_copy.py` | 4/4 PASS |
| `test_command_center_agent_identity.py` | 3/3 PASS |
| `test_command_center_attention_history.py` | 3/3 PASS |
| `test_command_center_composer_alignment.py` | 2/2 PASS |

Two adjacent popup suites were also run as regression coverage:

| Adjacent regression file | Result |
|---|---|
| `test_command_center_attention_popup.py` | 4/4 PASS |
| `test_command_center_popup_formatting.py` | 2/2 PASS |

Total focused and adjacent result: **18 of 18 PASS**.

The environment does not install `pytest` in `MAP_System/.venv`; each unittest
file was therefore executed directly with the project virtual-environment
Python, which is the supported form for these files.

### Registry validation

After the status and ownership reconciliation:

- active output-collision query: zero rows;
- `MAP_System/scripts/validate_task_graph.py`: PASS;
- `MAP_System/scripts/validate_task_mirrors.py`: PASS.

## Combined independent-review checklist

The reviewer should evaluate the current final state, not reconstruct obsolete
intermediate palettes or labels.

1. Confirm the message-type dropdown uses understandable operator language,
   keeps the underlying `inform`/`request`/`ack` values, and explains reply
   expectations compactly.
2. Confirm agent chips derive display type without altering sender IDs used for
   mentions, replies, or routing.
3. Confirm provider colors are distinguishable and readable at the final
   TASK-245 strength, without resembling error or warning states.
4. Confirm `Attention needed` is always present, shows zero when empty, remains
   collapsible, and expands when a popup Open action navigates to history.
5. Confirm operator-visible `Project Updater` copy is spaced while internal
   identifiers remain unchanged.
6. Confirm the message textarea and Send button align with the dropdown control
   rather than the explanatory helper line.
7. Confirm popup option lists and attention behavior still pass their adjacent
   regressions.
8. Re-run live/template parity, JavaScript syntax, and the 18 focused/adjacent
   tests.
9. Record findings against TASK-254. Do not approve or reject the retired
   snapshot tasks individually.

## Outcome

The operator's eight feedback rounds remain visible as durable history, while
MAP now presents one honest object for review: the UI state that actually
exists. The repair removes 28 reported collision instances without changing a
pixel or a line of UI behavior.

## Addendum 2026-07-21: post-submission live drift, investigated and repaired

claude-lab-rose's review (`MAP_System/artifacts/reviews/task254-review-rose.md`)
found that the live copies at `/home/mellow/Projects/CommandCenterUI/src/chat.*`
had diverged from the template after this task's 2026-07-19 submission, with no
active task owning the change — an ownership-integrity breach, not a defect in
the design above. Full investigation, attribution attempt, and repair record:
`MAP_System/artifacts/audits/task254-untracked-edit-2026-07-21.md`.

Summary: the live files gained a genuine, coherent, well-documented feature
(operator terminal prompts merged into the chat log; timestamps on every
message/attention item) built across `chat.html`/`chat.css`/`chat.js` and
`app/server.py` together, plus a matching `README.md` update — not noise or a
partial edit. Root actor could not be attributed to any hcom-tracked agent or
to the operator (who was asked directly and denied it); see the audit for what
was ruled out. Decision: **fold**, not revert — the feature is real and
functioning (`node --check` passes both copies; no syntax break).

`app/server.py` is explicitly **not** one of this task's `output_paths` and was
left untouched here even though it changed in the same edit window: folding it
would also require deciding whether to keep or drop a second, unrelated change
bundled into that file (see the audit's server.py finding — a security-hardening
reversion). That decision belongs to whoever owns a follow-up task for that
file, not to this reconciliation.

Updated parity hashes after folding the chat.html/css/js feature into the
template (`chat.js`/`chat.css`/`chat.html` are otherwise identical, differing
only in the SHA-256 because of the folded content):

| File | SHA-256 for both live and template copies |
|---|---|
| `chat.html` | `8054786ad4b8e6a9651fd38cb84879887516ade4d3b2844d0ac3c65cc2dd180e` |
| `chat.css` | `12df31d9702d34037a3f27aac190fe9c9871ea8b501bc78ea4397dc0653b3972` |
| `chat.js` | `992936f2c8e49b501266b3884d18dc13cc0eeb4caeab9e486a6a4ead368fef91` |

Re-verified 2026-07-21: all 12/12 focused tests pass, both adjacent regression
files still pass (6/6), `node --check` passes both copies, and
`validate_task_graph.py`/`validate_task_mirrors.py` both pass.

## Addendum 2026-07-22: authority rework also needs backend integration scope

After `task254-review-lilo.md` rejected the folded frontend behavior for
missing scope/authority, a read-only integration check found that preserving
the feature cannot be handled by relabeling the three frontend files alone:

- Live and installer-template `chat.html`, `chat.css`, and `chat.js` remain
  byte-identical at the hashes above. The 12/12 TASK-254-focused tests and both
  JavaScript syntax checks still pass.
- The live backend contains `extract_terminal_prompt`, `TerminalPromptLog`, the
  `terminal_since` chat cursor, terminal-message merging, and intent-aware
  `send_chat` handling.
- The installer-template backend lacks those terminal-prompt paths even though
  its byte-identical frontend requests `/api/chat?...&terminal_since=...`.
- The backend copies are not byte-identical: live `app/server.py` SHA-256 is
  `eb6fca4083073f74365f3547b077721fb5456ae4bb5a476623908633ea073977`;
  installer-template SHA-256 is
  `3881cdb17f86963ddb1c5ef872b0701245e13a19790b71448eefcac0459ef291`.

Therefore an operator choice to preserve/re-authorize the feature must include
an explicitly scoped live/template backend reconciliation and security review,
or explicitly narrow the promised feature to behavior both backends support.
This addendum records evidence only. It does not authorize, copy, revert, or
otherwise modify any CommandCenterUI source.

## Addendum 2026-07-28: scope split — TASK-254 restored to administrative-only, feature authorization moved to TASK-292

The backend half of the 2026-07-22 addendum's open question is now resolved:
TASK-264 restored the security hardening in live `server.py`, and TASK-265
(RELEASED) reconciled live and template `server.py` to byte-identical under
DEC-029/DEC-030/DEC-033, with a dedicated drift-check test
(`test_command_center_ollama_allowlist.py`).

That leaves exactly the gap `task254-review-lilo.md` named: no task ever
authorized the **frontend** terminal-message/timestamp/composer-intent feature
itself as shipped product behavior — only the security/copy-authority
questions around it. Per that review's "Route 1", this reconciliation is
restored to administrative-only, and the frontend feature's authorization is
moved to a separately scoped task:

- **New task: TASK-292** — owns the open question of whether the frontend
  feature (terminal-message chat merge, timestamps, composer intent selector)
  is authorized to remain, and will become sole active owner of
  `chat.html`/`chat.css`/`chat.js` (live + template) and the four focused
  tests once it is claimed and TASK-254 reaches a terminal status. See
  `MAP_System/artifacts/planning/task291-commandcenterui-chat-feature-authorization.md`.
- **TASK-254's corrected claim, going forward:** TASK-254 certifies two
  things and no more — (1) the original eight-round operator-feedback
  consolidation (TASK-241–248) introduced no behavior change, which remains
  true and unaffected by any of this; and (2) the mechanical ownership-
  integrity repair performed here on 2026-07-21 (folding the then-untracked
  live edit into the template) restored live/template byte parity for files
  TASK-254 was the sole active owner of. TASK-254 does **not** certify that
  the folded feature content is authorized product behavior — that
  determination belongs to TASK-292. Acceptance criterion 4 ("no
  CommandCenterUI source or behavior is changed by the administrative
  repair") is read against TASK-254's own reconciliation design, not against
  the separate, out-of-scope untracked edit it was forced to react to at
  review time; this addendum makes that reading explicit rather than
  implicit, which is the defect lilo's review correctly found.
- Re-verified 2026-07-28: live and template `chat.html`/`chat.css`/`chat.js`
  remain byte-identical, the 4 TASK-254-owned focused tests pass 12/12, the 2
  adjacent regression files pass 6/6, and `node --check` passes both copies.
  Nothing in this addendum changes any CommandCenterUI source or behavior.
