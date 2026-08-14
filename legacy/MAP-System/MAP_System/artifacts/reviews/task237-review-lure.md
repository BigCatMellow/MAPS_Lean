# Review: TASK-237 Add operator reply popup queue to CommandCenterUI

task_id: TASK-237
reviewer: claude-lab-lure
task_owner: codex-lab-kiri

## Verdict

APPROVED

The operator-only attention popup queue meets all three acceptance criteria, keeps
an explicit action boundary (no automatic send or approval), preserves reply-to
context, and is at byte-for-byte parity between the live copy and the install
template. One out-of-scope parity observation is recorded under Risks / Follow-up
(the pre-existing "Send as" message-intent feature is live-only); it does not
block this task's popup deliverable.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| AC1 — New unanswered request messages, approval gates, and terminal prompts are queued into one operator-visible popup at a time, without duplicating a popup for an item already seen. | PASS | `pollAttention` builds `popupQueue` from `/api/attention` items (kind `request`), `/api/approvals` gates (kind `gate`), and prompts (kind `prompt`), keyed `${kind}:${id}` (`chat.js:1535-1539`, `popupItem` 1399-1401). `renderAttentionPopup` shows only `visible[0]` — one at a time (1423-1444). Seen items do not recur: dismissed keys persist in `popupDismissed` (`attn-popup-dismissed` localStorage) and are filtered out (1426, `dismissPopupItem` 1407-1411). |
| AC2 — Popup actions explicitly route to reply or open paths, persist snooze/dismissal locally, retain the existing inbox, and keep approval decisions explicit. | PASS | Reply → `jumpToAttentionMessage(item, true)` → `startReply` opens the existing composer (85-91); Open → scroll/`openScreen`/inbox scroll (1453-1460); Snooze → local 5-min (`ATTENTION_POPUP_SNOOZE_MS`) persisted in `attn-popup-snoozed` (1462-1469); Dismiss → local persist (1471-1476). The existing needs-attention inbox list is unchanged (`attentionList.replaceChildren`, 1543+). Gate approval stays explicit: the popup's Open for a gate only scrolls to the inbox; approval is a separate `Approve/Reject` click that POSTs `{gate_id, approve}` (`gateItem` ~1487-1498). Reply button is hidden for non-request kinds (`attentionPopupReply.hidden = item.kind !== "request"`, 1441). |
| AC3 — Focused UI checks verify popup markup, queue behavior, action wiring, and no automatic approval or send behavior. | PASS | `test_command_center_attention_popup` — 4 tests PASS. `node --check` passes on both the template and live `chat.js`. Independent scan of popup handlers (`chat.js:1399-1477`) confirms no `fetch`/POST/`/api` call on any popup action path — reply only opens the composer. |

## Files Reviewed

- `MAP_System/templates/install/command-center-ui/src/chat.js` (+ `.html`, `.css`)
- `/home/mellow/Projects/CommandCenterUI/src/chat.js` (+ `.html`, `.css`) — live copy
- `MAP_System/artifacts/tests/task237-attention-popup.md` (author evidence)
- `MAP_System/tests/test_command_center_attention_popup.py`

## Forbidden Changes Check

PASS — No auto-send and no auto-approve. Every popup action is a distinct
operator click; the only network writes in the touched code are the pre-existing
explicit `Approve/Reject` gate POST and the pre-existing composer send. No
policy, authority, shared-state, installer, or TASK-227 change is present in the
reviewed diff.

## Live / Template Parity

- Attention-popup feature (HTML, CSS, JS): **identical** in live and template
  (`diff` shows zero `attention`/`popup`/`snooze` differences). The task's
  deliverable is at parity.
- The **only** live↔template divergence across all three files is the entire
  **"Send as" message-intent feature**: the `#message-intent` select
  (`chat.html`), its styling (`chat.css`), and the intent logic + guards
  (`messageIntent`, `{ text, intent }` body, request-needs-@agent and
  ack-needs-reply-target guards in `chat.js`). This exists in the **live** copy
  and is **absent from the install template**.

## Risks / Follow-up

- REQUIRED-decision (parity, out of TASK-237 popup scope): The install template
  lacks the live "Send as" message-intent feature entirely. Because the template
  is the fresh-install source, an install from it would ship without
  message-intent — an install-copy drift, not merely the contrast correction the
  evidence describes. Recommend kiri/operator choose: (a) port the full Send-as
  feature (select + styling + intent guards) into the template to restore
  parity, or (b) record the intentional live-ahead divergence as a provenance
  note. This drift is a concrete input to TASK-235's deployment-source manifest.
- Minor (non-blocking): `popupDismissed` grows unbounded in localStorage (keys
  are never pruned). Harmless at current scale; worth a cap/TTL if the attention
  volume grows.

## Parity Follow-up — RESOLVED 2026-07-18 (operator: port it)

Per operator instruction ("Port it"), the live-only "Send as" message-intent
feature was ported into the install template by syncing the three template files
from the live copy (`cp` live → template for `chat.js`/`chat.html`/`chat.css`).
The full `diff -u` had confirmed the Send-as blocks were the *only* divergence,
so the sync introduces exactly the intended feature (select + styling + intent
logic + request-needs-@agent and ack-needs-reply-target guards) with no other
change. Post-sync: all three files are byte-identical live↔template; template
`chat.js` passes `node --check`; the 4 focused popup tests still PASS. Template
and live are now at full parity; the install-copy drift is closed.

## Verification

- `node --check` template `chat.js` — OK; live `chat.js` — OK.
- `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_command_center_attention_popup` — 4 tests PASS.
- `diff` live vs template `chat.js`/`chat.html`/`chat.css` — divergence isolated to the Send-as feature; popup code identical.
- Manual read of popup handlers (`chat.js:1399-1477`) — no `fetch`/POST/`/api` on any popup action path.
