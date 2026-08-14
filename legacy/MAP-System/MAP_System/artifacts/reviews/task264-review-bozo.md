# Review: TASK-264 Restore CommandCenterUI local-model security hardening

task_id: TASK-264
reviewer: audit-untracked-bozo
task_owner: claude-lab-niko

## Verdict

APPROVED

This is the second pass. First-pass verdict was CHANGES_REQUESTED: the three
explicitly-scoped fixes were real and correct, but the actual network egress
point the task exists to close (the summarizer's HTTP call) was not
loopback-locked, and the parallel "launch" path had the same gap the
"discovery" path had just been fixed for. Both findings are now fixed and
independently re-verified on this pass, not just re-read — see "Re-review"
below for what changed and how it was checked.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| `ollama_models()` pins `OLLAMA_HOST=127.0.0.1:11434` for the `ollama list` subprocess | PASS | `server.py:833-848`: `env = os.environ.copy(); env["OLLAMA_HOST"] = "127.0.0.1:11434"`, passed as `env=env` to `subprocess.run`, matching the template's comment verbatim. |
| `SUMMARY_MODEL` defaults to `None`, opt-in only | PASS (with a noted, reasonable divergence) | `server.py:100`: `SUMMARY_MODEL = os.environ.get("COMMAND_CENTER_UI_SUMMARY_MODEL") or None`. Verified directly: unset → `None`, `""` → `None` (the `or None` correctly folds empty-string into disabled, not just unset), non-empty → the value. Template hardcodes bare `None` (cannot be enabled at all); niko's version is opt-in via env var. I agree with keeping the divergence — it matches the stated intent ("opt-in only," not "impossible to enable") without reopening the default-on hole. No change needed here. |
| `SUMMARY_MODEL is None` guards restored on worker-thread start and `enqueue()` | PASS | `server.py:1698` (`if SUMMARY_MODEL is not None: threading.Thread(...)`) and `server.py:1717` (`if SUMMARY_MODEL is None: return`) both present, matching the template's original guard shape. Confirmed no `/api` route or frontend code assumes `SUMMARY_MODEL`/`SUMMARIZER.available` is truthy: `/api/summaries` returns `"available": SUMMARIZER.available` (stays `None` forever when disabled, since `_worker()` never runs to set it), and `chat.js`'s `pollSummaries()` never reads that field — it only iterates `data.summaries` (empty dict when disabled). No breakage. |
| Feature work preserved (quoted-summary extraction); `py_compile` passes | PASS | `Summarizer.clean_response()` (`server.py:1731-1747`, the quote-stripping/"here's the summary" cleanup logic) is byte-identical to the untracked edit's version — untouched. `python3 -m py_compile` on the live file: clean exit, no errors. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Changes outside `app/server.py` (TASK-264's sole `output_path`) | NOT BROKEN — diffed live `chat.html`/`chat.css`/`chat.js` against their TASK-254 template state: unchanged. Only `server.py` moved. |
| Discarding the terminal-message/timestamp feature work from the untracked edit while restoring hardening | NOT BROKEN — `Summarizer.clean_response()` and the rest of the feature surface re-read in full on both passes, byte-identical throughout. |
| Reintroducing the `ollama-goose`/`pi-lab-new` launcher entries or the permissive model allowlist (explicitly out of this task's scope, filed separately as TASK-265) | NOT BROKEN — `BASE_LOCAL_AGENT_DEFS`/`local_agent_defs()` untouched by either rework; still matches the state from my original audit, unaddressed by design pending TASK-265. |

## Findings (first pass, both fixed — see Re-review)

### BLOCKER: `OLLAMA_URL` itself is still env-overridable — the summarizer's actual network call is not loopback-locked

`server.py:95`: `OLLAMA_URL = os.environ.get("COMMAND_CENTER_UI_OLLAMA", "http://127.0.0.1:11434")` — unchanged from the regressed state. This is the exact same line the untracked edit changed alongside `SUMMARY_MODEL` (my audit's table listed them as one row: "`OLLAMA_URL` hardcoded to `127.0.0.1`, `SUMMARY_MODEL = None`"). The task description split that row and only named the `SUMMARY_MODEL` half; `OLLAMA_URL` was missed.

Why this matters concretely: `Summarizer._worker()` (`server.py:1768`) builds its request as `f"{OLLAMA_URL}/api/generate"` — this is the literal HTTP call that sends agent message text to a model for summarization. `SUMMARY_MODEL` being opt-in now correctly requires an operator to explicitly turn summarization on, but once they do, `OLLAMA_URL` still resolves from `COMMAND_CENTER_UI_OLLAMA` if that env var happens to be set (accidentally inherited from a shell profile, or set by anything else with env-var influence over the process). The fix restores the *on/off* switch but not the *where it sends data* pin — an operator who opts in via `COMMAND_CENTER_UI_SUMMARY_MODEL` gets no protection against message content leaving the loopback interface. This is precisely the risk TASK-264's `risk_class: SECURITY` / `risk_severity: STRUCTURAL` exists to close.

Fix: hardcode `OLLAMA_URL = "http://127.0.0.1:11434"` with the template's original comment, matching what was just done for `ollama_models()`'s subprocess env.

### REQUIRED: `launch_local_agent()` ("launch") does not pin `OLLAMA_HOST` — confirms niko's own flagged suspicion

The review request specifically asked me to check "are there OTHER ollama/subprocess call sites... if launch does not pin, the fix is half done." It does not pin.

`launch_local_agent()` (`server.py:398-431`) is the handler behind the UI's "launch" button for any local-agent entry, including `ollama-model-*` shortcuts and `ollama-goose`. It builds the spawned process's environment as:

```python
env = os.environ.copy()
env["PROJECT_DIR"] = str(WORKSPACE)
if hcom_name:
    env["HCOM_NAME"] = hcom_name
```

— copying the parent process's full environment verbatim, with no `OLLAMA_HOST` override, then passing it to `subprocess.Popen([...wezterm...], env=env, ...)`. The template's own comment on the discovery-side fix says "**discovery and launch** must use the same loopback-only endpoint" (emphasis mine) — meaning this was always meant to cover both paths, and only the discovery half (`ollama_models()`) got fixed. A launched Ollama agent process still inherits whatever `OLLAMA_HOST` the parent UI process has, unpinned.

Fix: pin `env["OLLAMA_HOST"] = "127.0.0.1:11434"` in `launch_local_agent()` alongside the other env overrides, mirroring the `ollama_models()` fix.

## Restart

Required for any of these fixes (including the two already-correct ones) to take effect: the live server process (pid bound since 12:26, before today's untracked edit and before niko's fix) holds whatever constants were in memory at start — it does not hot-reload Python module-level values. `py_compile` passing only proves the file parses; it says nothing about the running process.

Restarting appears safe: `chat.js`'s `poll()` already handles a transient connection drop (`catch (err) { connStatus.textContent = 'offline: ...' }`) and retries on its normal interval, so the UI should recover on its own once the server comes back. `SUMMARY_CACHE_PATH` and the steward/sentinel state files are disk-persisted, not in-memory-only, so nothing is lost by a restart. I did not restart it myself — that's a visible, operator-facing action outside a reviewer's scope, and should wait until the two findings above are fixed anyway so it only needs doing once.

## Files Reviewed

- `/home/mellow/Projects/CommandCenterUI/app/server.py` (full read of the diff region + targeted grep across the whole file for every `subprocess`/`ollama`/`OLLAMA` call site)
- `/home/mellow/Projects/CommandCenterUI/src/chat.js` (`pollSummaries()`, to confirm no frontend assumption of `SUMMARY_MODEL` truthy)
- `MAP_System/artifacts/audits/task254-untracked-edit-2026-07-21.md` (my own prior audit, cross-checked against the task's stated scope)
- `MAP_System/tasks/TASK-264.json`

## Verification

- `python3 -m py_compile /home/mellow/Projects/CommandCenterUI/app/server.py` — clean.
- Direct interpreter check of `os.environ.get("X") or None` for unset / `""` / non-empty — confirmed empty-string folds to `None` correctly.
- `grep` across the full live file for every `subprocess.run`/`subprocess.Popen`/`OLLAMA`/`ollama` reference — found the two gaps above; no third site missed.
- Read `Summarizer.clean_response()` in full — byte-identical to the pre-fix version, confirming the feature work survived.
- Read the `/api/summaries` handler and `chat.js`'s only consumer of it — confirmed `available` is never read client-side, so the disabled-by-default state cannot break a UI path.

## Re-review (second pass)

Re-verified independently, not accepted on report alone:

- **BLOCKER fixed, confirmed**: `server.py:100` — `OLLAMA_URL = "http://127.0.0.1:11434"`, hardcoded, no `os.environ.get` anywhere near it. `grep -n "environ.get.*OLLAMA"` across the whole file returns nothing — no ambient-override path remains for the egress endpoint.
- **REQUIRED fixed, confirmed**: `server.py:420-424`, `launch_local_agent()` — `env["OLLAMA_HOST"] = "127.0.0.1:11434"` now sits right after `env = os.environ.copy()`, before the spawn. Discovery (`ollama_models()`, line 845-846) and launch now both pin, matching the template's "discovery and launch" comment.
- Counted `os.environ.copy()` call sites directly: exactly two in the whole file (line 420 launch, line 845 discovery), both now followed by the `OLLAMA_HOST` pin. Matches niko's claim exactly — not just re-reading the two lines niko pointed at, but confirming there is no third copy-site elsewhere in the file that would need the same fix.
- `python3 -m py_compile` on the live file — clean.
- `Summarizer.clean_response()` re-read in full — still byte-identical, feature work intact.

**On the intentional asymmetry (env opt-in for `SUMMARY_MODEL`, no env override at all for `OLLAMA_URL`), which niko asked me to check rather than accept:** I agree with the reasoning and would have flagged it if it weren't there. `SUMMARY_MODEL` answers "should this run at all," and ambient-env opt-in is a reasonable, low-risk way to let an operator turn on a feature — worst case it does nothing extra. `OLLAMA_URL` answers "where does message content leave to," and that is exactly the class of setting that should not be controllable by whatever happens to be in a shell's environment when the process starts — an operator (or anything else with env influence) could otherwise silently redirect message content off-loopback with no visible decision point. Routing "should remote ever be allowed" through TASK-265 as an explicit, visible decision rather than an ambient env var is the right call, not an inconsistency. No change requested here.

**Restart**: agree it's safe and that this is the operator's call, not mine or niko's to execute unilaterally. Both fixes are file-level constants read once at process start; nothing about them requires anything beyond a normal restart, and `chat.js`'s existing reconnect handling covers the brief gap. Recommending the operator restart the live CommandCenterUI process now that both findings are closed.
