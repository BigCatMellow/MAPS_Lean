/* MAP Orchestrator — agent-tree + per-agent-thread view logic.
   Real data only: /api/presence, /api/chat, /api/attention, /api/chat/send.
   Tree groups are derived from each agent's real hcom `tag`, same approach
   as room.js. A per-agent "thread" is a client-side filter of the shared
   hcom feed (sender==agent or mentions include @agent) — there is no
   separate per-agent transcript endpoint, so this is the honest derivation. */

const ROOM_PALETTE = ["#5b9dff", "#a97bff", "#e0a23c", "#4bc4d6", "#3fb968", "#f0684b"];
const STATUS_DOT = { active: "#3fb968", listening: "#5b9dff", blocked: "#e0a23c", idle: "#5f6b7e", unknown: "#5f6b7e" };
const TONE = {
  request: { chipBg: "rgba(240,104,75,.14)", chipFg: "#f79e8a" },
  ack: { chipBg: "rgba(63,185,104,.14)", chipFg: "#6fd897" },
  inform: { chipBg: "rgba(91,157,255,.12)", chipFg: "#8bb8ff" },
  gray: { chipBg: "rgba(255,255,255,.07)", chipFg: "#b6c1d1" },
};

const state = {
  operator: null,
  agentsByName: new Map(),
  messages: [],
  messageIds: new Set(),
  lastMessageId: 0,
  attentionItems: [],
  gates: [],
  prompts: [],
  selected: null, // null = root/all, else an agent name
  pendingReply: null, // { id, sender } when Reply was opened from attention
  simplifier: { enabled: false, provider: "off", available: null },
};

const el = (id) => document.getElementById(id);
const tree = el("tree");
const threadScroll = el("thread-scroll");
const threadEmpty = el("thread-empty");
const composer = el("composer");
const input = el("input");
const sendBtn = el("send-btn");
const threadStatusMsg = el("thread-status-msg");

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function initials(name) {
  const parts = String(name).replace(/[^A-Za-z0-9]+/g, " ").trim().split(" ");
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return String(name).slice(0, 2).toUpperCase();
}
function colorFor(key) {
  let h = 0;
  for (const ch of String(key)) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return ROOM_PALETTE[h % ROOM_PALETTE.length];
}
function fmtTime(ts) { return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); }

const SUMMARY_LABEL_RE = /^(Need|Done|Next|Blocker|Review|Tests?|Refs?|Issue|Options?|Recommendation|Status|Warning|Files?)\s*:\s*(.*)$/i;

function appendReadableText(container, text) {
  const lines = String(text || "").replace(/\r\n/g, "\n").split("\n")
    .map((line) => line.trim()).filter(Boolean).slice(0, 8);
  let leadAdded = false;
  for (const line of lines) {
    const labeled = line.match(SUMMARY_LABEL_RE);
    if (labeled) {
      const row = document.createElement("div");
      row.className = "summary-row";
      const label = document.createElement("span");
      label.className = "summary-label";
      label.textContent = labeled[1];
      const value = document.createElement("span");
      value.textContent = labeled[2];
      row.append(label, value);
      container.append(row);
    } else if (/^[-*]\s+/.test(line)) {
      const bullet = document.createElement("div");
      bullet.className = "summary-bullet";
      bullet.textContent = line.replace(/^[-*]\s+/, "");
      container.append(bullet);
    } else {
      const detail = document.createElement("div");
      detail.className = leadAdded ? "summary-detail" : "summary-lead";
      detail.textContent = line;
      container.append(detail);
      leadAdded = true;
    }
  }
}

function needsReadableCard(msg) {
  if (msg.sender_kind !== "instance" || msg.sender === state.operator) return false;
  const text = String(msg.text || "");
  return Boolean(msg.summary) || text.length >= 180 || text.split("\n").length >= 4;
}

function attentionCountFor(agentName) {
  return state.attentionItems.filter((item) => item.sender === agentName).length
    + state.prompts.filter((prompt) => prompt.name === agentName).length;
}

/* ---------- tree ---------- */
function groupedTags() {
  const byTag = new Map();
  for (const agent of state.agentsByName.values()) {
    const tag = agent.tag || "__untagged__";
    if (!byTag.has(tag)) byTag.set(tag, []);
    byTag.get(tag).push(agent);
  }
  const tags = [...byTag.keys()].sort((a, b) => {
    if (a === "__untagged__") return 1;
    if (b === "__untagged__") return -1;
    return a.localeCompare(b);
  });
  return tags.map((tag) => ({
    tag,
    label: tag === "__untagged__" ? "UNTAGGED" : tag.toUpperCase(),
    color: colorFor(tag),
    members: byTag.get(tag).sort((a, b) => a.name.localeCompare(b.name)),
  }));
}

function renderRoot() {
  el("root-node").classList.toggle("active", state.selected === null);
  const total = currentPopupQueue().length;
  const badge = el("root-badge");
  if (total > 0) { badge.hidden = false; badge.textContent = String(total); }
  else badge.hidden = true;
  const attentionBtn = el("attention-btn");
  el("attention-btn-count").textContent = String(total);
  attentionBtn.classList.toggle("clear", total === 0);
}

function renderTree() {
  const groups = groupedTags();
  el("agent-total").textContent = `${state.agentsByName.size} agent${state.agentsByName.size === 1 ? "" : "s"}`;
  tree.replaceChildren(
    ...groups.flatMap((group) => {
      const header = document.createElement("div");
      header.className = "tree-header";
      header.innerHTML = `<span class="label" style="color:${group.color}">${escapeHtml(group.label)}</span><span class="line"></span>`;

      const rows = group.members.map((agent) => {
        const item = document.createElement("div");
        item.className = "tree-item";
        const dot = STATUS_DOT[agent.status] || STATUS_DOT.unknown;
        const color = colorFor(agent.name);
        const need = attentionCountFor(agent.name);
        item.innerHTML = `
          <span class="stub"></span>
          <button type="button" class="node${state.selected === agent.name ? " active" : ""}">
            <span class="avatar" style="background:${color}22;color:${color}">${escapeHtml(initials(agent.name))}</span>
            <span class="col">
              <span class="name-row"><span class="name">${escapeHtml(agent.name)}</span></span>
              <span class="status mono" style="color:${dot}">${escapeHtml(agent.status)}</span>
            </span>
            ${need > 0 ? `<span class="need" title="${escapeHtml(agent.name)} needs a reply — click to show it">!</span>` : ""}
            <span class="dot" style="background:${dot}"></span>
          </button>
          <button type="button" class="term-btn" title="Open ${escapeHtml(agent.name)}'s terminal">▸</button>`;
        item.querySelector(".node").addEventListener("click", () => {
          state.pendingReply = null;
          state.selected = agent.name;
          input.placeholder = "Message this thread — Enter to send";
          renderAll();
        });
        const needBadge = item.querySelector(".need");
        if (needBadge) {
          needBadge.addEventListener("click", (e) => {
            e.stopPropagation();
            reopenAttentionFor(agent.name);
          });
        }
        item.querySelector(".term-btn").addEventListener("click", (e) => {
          e.stopPropagation();
          openScreen(agent.name);
        });
        return item;
      });
      return [header, ...rows];
    }),
  );
}

el("root-node").addEventListener("click", () => {
  state.pendingReply = null;
  state.selected = null;
  input.placeholder = "Message this thread — Enter to send";
  renderAll();
});
el("root-badge").addEventListener("click", (event) => {
  event.stopPropagation();
  openAttentionPanel();
});

/* ---------- thread ---------- */
function messageInThread(msg) {
  if (state.selected === null) return true;
  if (msg.sender === state.selected) return true;
  const mentions = (msg.mentions || []).map((m) => String(m).replace(/^@/, ""));
  return mentions.includes(state.selected);
}

function renderThreadHeader() {
  if (state.selected === null) {
    el("thread-avatar").textContent = "CC";
    el("thread-avatar").style.background = "rgba(91,157,255,.18)";
    el("thread-avatar").style.color = "#8bb8ff";
    el("thread-name").textContent = "All agents";
    el("thread-status").textContent = "orchestrator feed";
    return;
  }
  const agent = state.agentsByName.get(state.selected);
  const color = colorFor(state.selected);
  const avatarEl = el("thread-avatar");
  avatarEl.textContent = initials(state.selected);
  avatarEl.style.background = color + "22";
  avatarEl.style.color = color;
  el("thread-name").textContent = state.selected;
  el("thread-status").textContent = agent ? agent.status : "not currently present";
  el("thread-status").style.color = STATUS_DOT[agent?.status] || STATUS_DOT.unknown;
}

function renderTerminalBtn() {
  const btn = el("open-terminal-btn");
  btn.disabled = state.selected === null;
  btn.textContent = state.selected === null ? "▸ Terminal" : `▸ ${state.selected}'s terminal`;
}
el("open-terminal-btn").addEventListener("click", () => {
  if (state.selected !== null) openScreen(state.selected);
});

function isThreadAtBottom() {
  return threadScroll.scrollHeight - threadScroll.scrollTop - threadScroll.clientHeight < 80;
}

/* ---------- recap cards ----------
   Proposal from claude-lab-muza: agents post a normal hcom inform prefixed
   "RECAP:" at natural checkpoints (turn/task completion, handoff, blocker)
   with the same substantive recap they'd give the operator directly,
   instead of only terse status lines. This is purely a rendering
   convention on the client: no new hcom intent, no backend change, no
   server-side summarization. A message not prefixed this way renders as a
   normal chat row exactly as before. */
const RECAP_PREFIX_RE = /^\s*RECAP:\s*/i;

function recapTextOf(msg) {
  const match = RECAP_PREFIX_RE.exec(msg.text || "");
  return match ? msg.text.slice(match[0].length).replace(/^\s+/, "") : null;
}

function renderPlainMessage(msg) {
  const tone = TONE[msg.intent] || TONE.gray;
  const isYou = state.operator && msg.sender === state.operator;
  const color = isYou ? "#5b9dff" : colorFor(msg.sender);
  const row = document.createElement("div");
  row.className = "msg";
  row.innerHTML = `
    <span class="avatar" style="background:${color}22;color:${color}">${escapeHtml(initials(msg.sender))}</span>
    <div class="col">
      <div class="head"><span class="name">${escapeHtml(msg.sender)}</span><span class="time mono">${fmtTime(msg.ts)}</span></div>
      <div class="text"><span class="chip mono" style="background:${tone.chipBg};color:${tone.chipFg}">${escapeHtml(msg.intent || "inform")}</span></div>
    </div>`;
  const body = row.querySelector(".text");
  if (!needsReadableCard(msg)) {
    body.append(" " + String(msg.text || ""));
    return row;
  }
  const readable = document.createElement("div");
  readable.className = "readable-message";
  if (msg.summary) {
    const kicker = document.createElement("div");
    kicker.className = "summary-kicker";
    kicker.textContent = "Plain-language view";
    readable.append(kicker);
    appendReadableText(readable, msg.summary);
  } else {
    const pending = document.createElement("div");
    pending.className = "summary-pending";
    pending.textContent = state.simplifier.enabled
      ? "Preparing a plain-language version…"
      : "Long message — open the original below.";
    const preview = document.createElement("div");
    preview.className = "summary-preview";
    const compact = String(msg.text || "").replace(/\s+/g, " ").trim();
    preview.textContent = compact.slice(0, 260) + (compact.length > 260 ? "…" : "");
    readable.append(pending, preview);
  }
  const original = document.createElement("details");
  original.className = "message-original";
  const toggle = document.createElement("summary");
  toggle.textContent = "Show original message";
  const raw = document.createElement("pre");
  raw.textContent = msg.text || "";
  original.append(toggle, raw);
  body.append(readable, original);
  return row;
}

function renderRecapCard(msg) {
  const color = colorFor(msg.sender);
  const card = document.createElement("div");
  card.className = "recap-card";
  card.innerHTML = `
    <div class="recap-head">
      <span class="avatar" style="background:${color}22;color:${color}">${escapeHtml(initials(msg.sender))}</span>
      <span class="recap-badge">RECAP</span>
      <span class="name">${escapeHtml(msg.sender)}</span>
      <span class="time mono">${fmtTime(msg.ts)}</span>
    </div>
    <div class="recap-text">${escapeHtml(recapTextOf(msg))}</div>`;
  return card;
}

function renderThread() {
  const msgs = state.messages.filter(messageInThread);
  const atBottom = isThreadAtBottom();
  threadScroll.replaceChildren();
  if (!msgs.length) {
    threadEmpty.hidden = false;
    threadScroll.append(threadEmpty);
    return;
  }
  threadEmpty.hidden = true;
  for (const msg of msgs) {
    threadScroll.append(recapTextOf(msg) !== null ? renderRecapCard(msg) : renderPlainMessage(msg));
  }
  if (atBottom) threadScroll.scrollTop = threadScroll.scrollHeight;
}

function renderAll() {
  renderRoot();
  renderTree();
  renderThreadHeader();
  renderThread();
  renderTerminalBtn();
}

/* ---------- composer ---------- */
async function send() {
  let text = input.value.trim();
  if (!text) return;
  if (state.selected !== null && !text.includes(`@${state.selected}`)) {
    text = `@${state.selected} ${text}`;
  }
  sendBtn.disabled = true;
  threadStatusMsg.textContent = "";
  try {
    const res = await fetch("/api/chat/send", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        intent: state.pendingReply ? "ack" : "inform",
        reply_to: state.pendingReply?.id,
      }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.stderr || data.error || "send failed");
    input.value = "";
    state.pendingReply = null;
    input.placeholder = "Message this thread — Enter to send";
    await poll();
    await pollAttention();
  } catch (err) {
    threadStatusMsg.textContent = `send failed: ${err.message}`;
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}
composer.addEventListener("submit", (e) => { e.preventDefault(); send(); });
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
});

/* ---------- polling ---------- */
async function poll() {
  try {
    const res = await fetch(`/api/chat?since=${state.lastMessageId}&limit=200`);
    const data = await res.json();
    if (!data.ok) return;
    if (data.operator) {
      state.operator = data.operator;
      el("operator-name").textContent = data.operator;
    }
    for (const msg of data.messages) {
      if (state.messageIds.has(msg.id)) continue;
      state.messageIds.add(msg.id);
      state.messages.push(msg);
      state.lastMessageId = Math.max(state.lastMessageId, msg.id);
    }
    state.messages.sort((a, b) => a.id - b.id);
    renderAll();
  } catch { /* transient */ }
}

async function pollPresence() {
  try {
    const res = await fetch("/api/presence");
    const data = await res.json();
    if (!data.ok) return;
    state.agentsByName = new Map((data.agents || []).map((a) => [a.name, a]));
    el("top-meta").textContent = `${state.agentsByName.size} present`;
    renderAll();
  } catch { /* transient */ }
}

const AUTHORITY_STATUS_CLASS = {
  AUTHORITATIVE: "ok",
  FRESH: "ok",
  STALE: "warn",
  UNAVAILABLE: "error",
  INVALID: "error",
};

async function pollAuthority() {
  const el_ = el("authority-status");
  try {
    const res = await fetch("/api/map/authority");
    const data = await res.json();
    const freshness = data.freshness || "UNAVAILABLE";
    const cls = AUTHORITY_STATUS_CLASS[freshness] || "error";
    const host = data.authority_host || (data.mode === "authority" ? "self" : "unknown");
    el_.textContent = `authority: ${data.freshness_label || freshness.toLowerCase()}`;
    el_.className = `authority-status mono ${cls}`;
    const revision = data.authority_revision ? ` · revision ${data.authority_revision.slice(0, 15)}…` : "";
    const synced = data.last_successful_sync_at ? ` · synced ${data.last_successful_sync_at}` : "";
    const err = data.last_error || data.error ? ` · ${data.last_error || data.error}` : "";
    el_.title = `MAP authority: ${freshness} · mode ${data.mode || "unknown"} · host ${host}${revision}${synced}${err}`;
  } catch {
    el_.textContent = "authority: unavailable";
    el_.className = "authority-status mono error";
    el_.title = "MAP authority status request failed";
  }
}

async function pollSummaries() {
  const ids = state.messages.map((msg) => msg.id).filter(Number.isFinite);
  const since = ids.length ? Math.max(0, Math.min(...ids) - 1) : 0;
  try {
    const res = await fetch(`/api/summaries?since=${since}`);
    const data = await res.json();
    if (!data.ok) return;
    state.simplifier = data;
    const status = el("simplifier-status");
    if (!data.enabled) {
      status.textContent = "originals";
      status.className = "simplifier-status mono";
      status.title = "Plain-language message simplifier is off";
    } else if (data.available === false) {
      status.textContent = `${data.provider} unavailable`;
      status.className = "simplifier-status mono error";
      status.title = data.last_error || "Message simplifier unavailable";
    } else {
      const fallback = data.effective_provider === "ollama-fallback";
      status.textContent = fallback ? "local fallback · plain language" : `${data.provider} · plain language`;
      status.className = `simplifier-status mono active${fallback ? " fallback" : ""}`;
      status.title = fallback
        ? `Primary simplifier unavailable; using local ${data.fallback_model}. Originals remain available.`
        : "Agent messages are simplified; originals remain available";
    }
    let changed = false;
    for (const [id, summary] of Object.entries(data.summaries || {})) {
      const msg = state.messages.find((item) => item.id === Number(id));
      if (msg && msg.summary !== summary) {
        msg.summary = summary;
        changed = true;
      }
    }
    if (changed) renderAll();
  } catch { /* best-effort presentation enhancement */ }
}

async function pollAttention() {
  try {
    const [attnRes, apprRes] = await Promise.all([fetch("/api/attention"), fetch("/api/approvals")]);
    const attn = await attnRes.json();
    const appr = await apprRes.json();
    if (attn.ok) state.attentionItems = attn.items || [];
    if (appr.ok) { state.gates = appr.gates || []; state.prompts = appr.prompts || []; }
    renderAll();
    renderAttentionPopup();
    if (!attentionPanel.hidden) renderAttentionPanel();
  } catch { /* transient */ }
}

/* ---------- agent terminal (live PTY screen) ----------
   Ported from the old chat.js screen panel: /api/term polls the agent's
   real terminal via `hcom term <name> --json`, /api/term/inject sends
   keystrokes via `hcom term inject <name> [text] [--enter]`. Both are
   already name-allowlisted server-side (known_instance check). */

const screenPanel = el("screen-panel");
const screenTitle = el("screen-title");
const screenStatus = el("screen-status");
const screenBody = el("screen-body");
const screenForm = el("screen-form");
const screenInput = el("screen-input");
const screenEnterBtn = el("screen-enter");
const screenCloseBtn = el("screen-close");

let screenAgent = null;
let screenTimer = null;

async function refreshScreen() {
  if (!screenAgent) return;
  try {
    const res = await fetch(`/api/term?name=${encodeURIComponent(screenAgent)}`);
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "screen read failed");
    const nearBottom = screenBody.scrollHeight - screenBody.scrollTop - screenBody.clientHeight < 40;
    screenBody.textContent = (data.screen.lines || []).join("\n");
    if (nearBottom) screenBody.scrollTop = screenBody.scrollHeight;
    const agent = state.agentsByName.get(screenAgent);
    screenStatus.textContent = agent ? agent.status : "not currently present";
  } catch (err) {
    screenBody.textContent = `— ${err.message} —`;
  }
}

function openScreen(name) {
  screenAgent = name;
  screenTitle.textContent = `${name} — terminal`;
  screenStatus.textContent = "";
  screenBody.textContent = "loading…";
  screenPanel.hidden = false;
  refreshScreen();
  clearInterval(screenTimer);
  screenTimer = setInterval(refreshScreen, 2000);
  screenInput.focus();
}
function closeScreen() {
  screenAgent = null;
  screenPanel.hidden = true;
  clearInterval(screenTimer);
}

async function inject(text, enter) {
  if (!screenAgent) return;
  try {
    const res = await fetch("/api/term/inject", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: screenAgent, text, enter }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "inject failed");
    screenInput.value = "";
    await refreshScreen();
  } catch (err) {
    screenBody.textContent += `\n— inject failed: ${err.message} —`;
  }
}

screenForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = screenInput.value;
  if (!text && !confirm(`Send a bare Enter to ${screenAgent}?`)) return;
  inject(text, true);
});
screenEnterBtn.addEventListener("click", () => inject("", true));
document.querySelectorAll(".quick-keys button").forEach((btn) => {
  btn.addEventListener("click", () => inject(btn.dataset.key, false));
});
screenCloseBtn.addEventListener("click", closeScreen);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !screenPanel.hidden) closeScreen();
});

/* ---------- operator attention popup ----------
   Ported from the old chat.js: a bottom-right alert that surfaces the single
   most urgent open item (an unanswered request, a MAP approval gate, or an
   agent blocked waiting in its own terminal) so it can't be missed even if
   you're not looking at the tree. Dismiss/snooze state persists locally,
   same as before. */

const ATTENTION_POPUP_SNOOZE_MS = 5 * 60 * 1000;
const popupDismissed = new Set(JSON.parse(localStorage.getItem("orch-popup-dismissed") || "[]"));
let popupSnoozed = loadPopupSnoozes();
let pinnedPopupKey = null; // set when the operator clicks a tree row's "!" badge

function loadPopupSnoozes() {
  try {
    const value = JSON.parse(localStorage.getItem("orch-popup-snoozed") || "{}");
    if (!value || typeof value !== "object" || Array.isArray(value)) return {};
    return Object.fromEntries(Object.entries(value).filter(([, until]) => Number.isFinite(until) && until > Date.now()));
  } catch { return {}; }
}
function savePopupState() {
  localStorage.setItem("orch-popup-dismissed", JSON.stringify([...popupDismissed]));
  localStorage.setItem("orch-popup-snoozed", JSON.stringify(popupSnoozed));
}
function popupItem(kind, id, sender, text, ts) {
  return { key: `${kind}:${id}`, kind, id, sender, text, ts };
}
function fmtFullStamp(ts) {
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString([], { weekday: "short", year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "2-digit", second: "2-digit" });
}

const attentionPopup = el("attention-popup");
const popupKind = el("attention-popup-kind");
const popupPosition = el("attention-popup-position");
const popupTitle = el("attention-popup-title");
const popupFrom = el("attention-popup-from");
const popupWhen = el("attention-popup-when");
const popupText = el("attention-popup-text");
const popupActions = el("attention-popup-actions");

function currentPopupQueue() {
  return [
    ...state.attentionItems.map((item) => popupItem("request", item.id, item.sender, item.summary || item.text, item.ts)),
    ...state.gates.map((gate) => popupItem("gate", gate.gate_id, "MAP gate", gate.name + (gate.after_task ? ` (after ${gate.after_task})` : ""), gate.created_at)),
    ...state.prompts.map((prompt) => popupItem("prompt", prompt.name, prompt.name, prompt.context || "needs a response", prompt.ts)),
  ];
}

function dismissPopupItem(item) {
  popupDismissed.add(item.key);
  savePopupState();
  attentionPopup.hidden = true;
  if (pinnedPopupKey === item.key) pinnedPopupKey = null;
}

/* Re-surface a specific agent's popup even if it was already dismissed or
   snoozed — triggered by clicking the "!" badge on its tree row, since
   that's otherwise the only clue something needs attention. */
function reopenAttentionFor(agentName) {
  const match = currentPopupQueue().find((it) =>
    (it.kind === "request" && it.sender === agentName)
    || (it.kind === "prompt" && it.id === agentName));
  if (!match) return;
  popupDismissed.delete(match.key);
  delete popupSnoozed[match.key];
  savePopupState();
  pinnedPopupKey = match.key;
  renderAttentionPopup();
}

function beginAttentionReply(item) {
  state.pendingReply = { id: item.id, sender: item.sender };
  state.selected = item.sender;
  input.placeholder = `Reply to ${item.sender}'s request — Enter to send`;
  renderAll();
  closeAttentionPanel();
  input.focus();
}

function renderAttentionPopup() {
  const now = Date.now();
  popupSnoozed = Object.fromEntries(Object.entries(popupSnoozed).filter(([, until]) => until > now));
  const queue = currentPopupQueue();
  const visible = queue.filter((item) => !popupDismissed.has(item.key) && !(popupSnoozed[item.key] > now));
  const item = (pinnedPopupKey && visible.find((v) => v.key === pinnedPopupKey)) || visible[0];
  attentionPopup.hidden = !item;
  if (!item) return;

  const labels = {
    request: { kind: "Reply needed", title: "An agent needs your reply" },
    gate: { kind: "Approval needed", title: "A MAP gate needs your decision" },
    prompt: { kind: "Terminal reply needed", title: "An agent is waiting in its terminal" },
  };
  const label = labels[item.kind];
  popupKind.textContent = label.kind;
  popupPosition.textContent = visible.length > 1 ? `1 of ${visible.length}` : "";
  popupTitle.textContent = label.title;
  popupFrom.textContent = item.sender;
  popupWhen.textContent = fmtTime(item.ts);
  popupWhen.title = fmtFullStamp(item.ts);
  popupWhen.hidden = !item.ts;
  popupText.textContent = String(item.text || "").slice(0, 360);
  attentionPopup.dataset.key = item.key;

  const buttons = [];
  if (item.kind === "request") {
    buttons.push({ label: "Reply", primary: true, dismissOnAction: true, action: () => {
      beginAttentionReply(item);
    } });
  } else if (item.kind === "gate") {
    buttons.push({ label: "Approve", primary: true, dismissOnAction: true, action: () => decideGatePopup(item.id, true) });
    buttons.push({ label: "Deny", deny: true, dismissOnAction: true, action: () => decideGatePopup(item.id, false) });
  } else if (item.kind === "prompt") {
    buttons.push({ label: "Open terminal", primary: true, dismissOnAction: true, action: () => openScreen(item.id) });
  }
  buttons.push({ label: "Snooze 5m", action: () => {
    popupSnoozed[item.key] = Date.now() + ATTENTION_POPUP_SNOOZE_MS;
    savePopupState();
    renderAttentionPopup();
    setTimeout(pollAttention, ATTENTION_POPUP_SNOOZE_MS);
  } });
  buttons.push({ label: "Dismiss", action: () => { dismissPopupItem(item); renderAttentionPopup(); } });

  popupActions.replaceChildren(
    ...buttons.map((b) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = b.label;
      if (b.primary) btn.className = "primary";
      if (b.deny) btn.className = "deny";
      btn.addEventListener("click", () => {
        b.action();
        if (b.dismissOnAction) dismissPopupItem(item);
      });
      return btn;
    }),
  );
}

async function decideGatePopup(gateId, approve) {
  try {
    const res = await fetch("/api/gate/decide", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gate_id: gateId, approve }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "gate decision failed");
  } catch { /* surfaced on next poll via the gate remaining/disappearing */ }
  await pollAttention();
}

/* ---------- persistent attention inbox ----------
   Unlike the alert popup, this panel intentionally ignores local dismiss and
   snooze state. Those controls only quiet alerts; every still-live source item
   remains reviewable here until it is answered or resolved at the source. */

const attentionPanel = el("attention-panel");
const attentionBackdrop = el("attention-backdrop");
const attentionList = el("attention-list");
const attentionEmpty = el("attention-empty");

function openAttentionPanel() {
  renderAttentionPanel();
  attentionPanel.hidden = false;
  attentionBackdrop.hidden = false;
}
function closeAttentionPanel() {
  attentionPanel.hidden = true;
  attentionBackdrop.hidden = true;
}
function attentionCardButton(label, className, action) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  if (className) button.className = className;
  button.addEventListener("click", action);
  return button;
}
function renderAttentionPanel() {
  const queue = currentPopupQueue();
  el("attention-panel-summary").textContent = queue.length === 1
    ? "1 item needs your attention"
    : `${queue.length} items need your attention`;
  attentionEmpty.hidden = queue.length > 0;
  attentionList.hidden = queue.length === 0;
  attentionList.replaceChildren(...queue.map((item) => {
    const card = document.createElement("article");
    card.className = `attention-card ${item.kind}`;
    const labels = { request: "Reply", gate: "Approval", prompt: "Terminal" };
    card.innerHTML = `
      <div class="topline">
        <span class="kind">${labels[item.kind]}</span>
        <span class="from">${escapeHtml(item.sender)}</span>
        ${item.ts ? `<time title="${escapeHtml(fmtFullStamp(item.ts))}">${escapeHtml(fmtTime(item.ts))}</time>` : ""}
      </div>
      <p class="body">${escapeHtml(item.text || "")}</p>
      <div class="actions"></div>`;
    const actions = card.querySelector(".actions");
    if (item.kind === "request") {
      actions.append(attentionCardButton("Reply", "primary", () => {
        beginAttentionReply(item);
      }));
      actions.append(attentionCardButton("Show in feed", "", () => {
        state.pendingReply = null;
        state.selected = item.sender;
        input.placeholder = "Message this thread — Enter to send";
        renderAll();
        closeAttentionPanel();
      }));
    } else if (item.kind === "gate") {
      actions.append(attentionCardButton("Approve", "primary", () => decideGatePopup(item.id, true)));
      actions.append(attentionCardButton("Deny", "deny", () => decideGatePopup(item.id, false)));
    } else {
      actions.append(attentionCardButton("Open terminal", "primary", () => {
        closeAttentionPanel();
        openScreen(item.id);
      }));
    }
    return card;
  }));
}

el("attention-btn").addEventListener("click", openAttentionPanel);
el("attention-panel-close").addEventListener("click", closeAttentionPanel);
attentionBackdrop.addEventListener("click", closeAttentionPanel);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !attentionPanel.hidden) closeAttentionPanel();
});

(async function init() {
  await pollPresence();
  await poll();
  await pollAttention();
  await pollSummaries();
  await pollAuthority();
  setInterval(poll, 2000);
  setInterval(pollPresence, 8000);
  setInterval(pollAttention, 8000);
  setInterval(pollSummaries, 2500);
  setInterval(pollAuthority, 15000);
})();
