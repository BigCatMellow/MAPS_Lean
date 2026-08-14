# Audit: TASK-254 untracked live edit, 2026-07-21

task_id: TASK-254
auditor: audit-untracked-bozo
trigger: claude-lab-rose's TASK-254 review found live CommandCenterUI chat.*
files diverged from the template after submission, with no active task owning
the change (`MAP_System/artifacts/reviews/task254-review-rose.md`).
status: Part 1 (investigation) complete; attribution not established beyond
what is ruled out below. Part 2 (repair) complete for the files TASK-254 owns.

## What changed

Four live files under `/home/mellow/Projects/CommandCenterUI/` were rewritten
in one short session on 2026-07-21, all with inode Birth == Modify time (atomic
replace, not in-place edit):

| File | mtime (local -0400) |
|---|---|
| `src/chat.html` | 12:50:58 |
| `src/chat.js` | 12:51:14 |
| `src/chat.css` | 12:51:35 |
| `app/server.py` | 12:59:30 |
| `README.md` | 13:00:26 |

No other file under CommandCenterUI changed in that window (checked via
`find -newermt`). The order (UI files, then backend, then docs) and the ~10
minute span are consistent with one deliberate editing session, not a
corruption or partial write.

## What the change actually is

Diffing live against the pre-edit template (both the git-tracked baseline and
its own already-uncommitted TASK-254 work) shows a single coherent, working
feature, not noise or a partial edit:

- **Frontend** (`chat.html`/`chat.css`/`chat.js`): operator prompts typed
  directly into an agent's terminal are read from each tool's own transcript
  (Claude/Codex/Pi formats) and merged into the chat feed (`kind: "terminal"`,
  `via-terminal` styling); every message and attention item gained a
  human-readable timestamp (`fmtStamp`/`fmtFullStamp`/`stampElement`); the
  composer gained explicit intent selection (`inform`/`request`/`ack`) wired
  to a new backend parameter.
- **Backend** (`app/server.py`): a matching `TerminalPromptLog` class,
  `extract_terminal_prompt()` per-tool parser, `read_chat(..., terminal_since)`
  plumbing, and `send_chat()` intent validation — a real, working
  implementation, not a stub. `node --check` and `python -m py_compile` both
  pass on the live copies; nothing here is syntactically broken.
- **Docs** (`README.md`): the "What It Shows" section was updated to describe
  exactly this capability ("Operator prompts typed directly into an agent's
  wezterm window, merged into the same chat log... read from each tool's own
  transcript").

This reads as real, deliberate engineering work someone wanted live, built and
verified in one sitting, not an accident.

### A second, unrelated change bundled into the same server.py edit

`app/server.py`'s live copy also reverts a security-hardening change that was
already pending (uncommitted) in the template as part of TASK-254's own prior
work:

| Hardening (template, in progress before this edit) | Live (2026-07-21 edit) |
|---|---|
| `OLLAMA_URL` hardcoded to `127.0.0.1`, `SUMMARY_MODEL = None` (background summarization off) | Both overridable via env vars, `SUMMARY_MODEL` defaults to `"gemma3:4b"` |
| `ollama_models()` pins `OLLAMA_HOST=127.0.0.1:11434` for discovery/launch | Pin removed — would inherit an operator's remote `OLLAMA_HOST` |
| `VISIBLE_OLLAMA_MODELS` allowlist (`qwen3.5:4b` only) gates which local models become launchable | Allowlist gate removed — any discovered Ollama model becomes launchable; `ollama-goose` and `pi-lab-new` launcher entries added |

`CommandCenterUI/AGENTS.md` states explicitly: "Keep the backend bound to
`127.0.0.1` unless the operator explicitly scopes a network-exposed mode."
The live edit conflicts with that rule. The most likely explanation is that
whoever built the terminal-prompt feature was working from an **older base
copy** of `server.py` that predated the hardening, not that they deliberately
reverted it — but the practical effect is the same: a real, already-decided
safety property silently disappeared from the live app. This is a second,
independent instance of the exact failure pattern niko named today in
SYN-0001/the TASK-254 discussion ("one piece of state, two readers, no
declared authority") — one edit session, working outside task tracking,
collided with concurrent hardening it never saw.

## Attribution: ruled out, not established

**hcom-tracked agents (rose, niko, soba, lilo, kiri, lulu, fume, hana, memo):**
the full hcom event stream (`hcom events --last 2000`) has **zero events of
any kind** — from any instance — between 16:48 and 17:20 UTC
(12:48–13:00 -0400), which is exactly the edit window. Every other 10-30
minute stretch that day has continuous tool-call status events from whichever
agent was active. Individually:
- `codex-lab-lulu`, `helper-librarian-fume`: transcripts show one prompt each,
  no response — effectively inert the whole day.
- `codex-lab-hana`: transcript shows it stuck in an RnS-limit-watcher
  self-check loop the whole session, never touching CommandCenterUI.
- `pi-lab-memo`: transcript shows it failed to even parse its startup
  instructions ("unknown command error"); its last hcom status is
  "listening" from 16:35:53 onward with no further activity of any kind.
  This is far below the capability the terminal-prompt feature required, so
  Pi's known hcom-reporting unreliability (2026-07-18 Trial C) is not a
  plausible explanation here — memo simply did not do substantive work.
- `claude-lab-niko`, `claude-lab-rose`, `review-coverage-soba`: continuously
  active on other named work (coverage ledger, TASK-254 review, gate-input
  tests) with no gap that fits this edit, and no CommandCenterUI references in
  their event streams.

**Operator (bigboss):** asked directly by niko in hcom
(event id 9408, 17:54:51); denied it per this task's brief.

**Filesystem/process evidence:** no `.git` repository anywhere under
`/home/mellow/Projects/CommandCenterUI` (confirmed via `find` and `git -C`),
so there is no commit trail for the live app at all. No editor swap/backup
files (`*.sw?`, `*~`, `*.orig`) exist anywhere under the project. No
`aider`/`opencode`/`goose`/`vim`/`nvim`/`code` process is currently running.
Only one desktop login session was active all day (`tty7`, since 08:24,
uninterrupted) — the machine was not shared or remotely accessed in the
relevant window. `~/.bash_history` shows `aider`, `opencode` (via `ollama
launch`), and `goose` were all installed on this machine at some point, which
would let someone edit files directly without leaving any hcom trace, but
history has no timestamps and no entry visibly matches the edit; this is a
plausible channel, not confirmed use. The `ai tell` wrapper
(`MAP_System/templates/install/bin/ai`) was also checked and ruled out — it
only relays hcom messages to the labs, it cannot write files itself.

**Conclusion:** unattributable to a specific person or process with the
evidence available. What can be said with confidence: it was not any of the
nine hcom-tracked agents active that day (activity/capability evidence above),
and it was not routed through any MAP-visible tool. The edit is too coherent
and well-documented to read as corruption, and the bundled security-hardening
reversion is best explained as a stale base copy colliding with concurrent
work, not malice.

## Repair (Part 2)

**Decision: fold, not revert**, for the files TASK-254 owns
(`chat.html`/`chat.css`/`chat.js`, live and template). The feature is real,
functioning, matches the app's own README description of intended behavior,
and the live/template diff for these three files is a clean superset with no
regressions — every "template only" line in the diff is just the older,
simpler counterpart of the same live feature (e.g. `fmtTime` → `fmtStamp`/
`fmtFullStamp`), not distinct functionality the live edit dropped.

Actions taken:
1. Copied the live `chat.html`/`chat.css`/`chat.js` over the template copies
   (byte-identical now; template previously lacked only the terminal-message
   and timestamp feature, nothing else).
2. Re-ran the four TASK-254-owned focused test files: **12/12 pass**
   (was 8/12 failing per rose's review).
3. Re-ran the two adjacent regression files: **6/6 pass**, unchanged.
4. `node --check` passes both copies of `chat.js`.
5. `validate_task_graph.py` and `validate_task_mirrors.py` both pass.
6. Updated the reconciliation record
   (`MAP_System/artifacts/planning/command-center-ui-serial-batch-reconciliation-2026-07-19.md`)
   with an addendum: new parity SHA-256 hashes, and a pointer to this audit.

**`app/server.py` was explicitly left alone**, in both the live and template
copies. It is not one of TASK-254's `output_paths` — folding it would mean
this task silently deciding whether to keep the `ollama-goose`/`pi-lab-new`
launcher additions and the permissive-model change, which is a separate,
unrelated decision this task has no mandate to make. (I did try folding
server.py first, including a selective merge that kept the terminal-prompt
backend but restored the security hardening — it worked and compiled clean —
but reverted it once I confirmed server.py isn't in TASK-254's declared
output paths. The merge recipe is preserved here in case a follow-up task
wants it: keep `TERMINAL_PROMPT_*` constants, `plain_prompt_text`,
`extract_terminal_prompt`, `TerminalPromptLog`, the `read_chat`/`send_chat`
signature changes, and the `prompts` endpoint's `ts` field; drop
`LOCAL_GOOSE_LAUNCHER`/`LAB_PI_LAUNCHER`/the `ollama-goose` and `pi-lab-new`
`BASE_LOCAL_AGENT_DEFS` entries, and restore `OLLAMA_URL`/`SUMMARY_MODEL`
hardcoding, the `OLLAMA_HOST` loopback pin in `ollama_models()`, and the
`VISIBLE_OLLAMA_MODELS` allowlist gate in `local_agent_defs()`.)

**Follow-up needed, not done here:** the live `app/server.py` at
`/home/mellow/Projects/CommandCenterUI/app/server.py` still has the
security-hardening reversion described above, right now, on the actually
running app (server process pid started 12:26, before this edit — it has the
old hardened constants in memory, but the file on disk does not, so a future
restart would pick up the regression). This needs its own task and owner
decision on the ollama-goose/pi-lab-new scope question; flagging to
@bigboss/@niko rather than fixing unilaterally under TASK-254.
