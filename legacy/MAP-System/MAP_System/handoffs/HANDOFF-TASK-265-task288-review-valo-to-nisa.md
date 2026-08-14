# Handoff: TASK-265 (CommandCenterUI server.py reconciliation)

- task ID: TASK-265
- sender: task288-review-valo (helper)
- intended recipient: lili-replacement-nisa (or any live core agent — this needs core-agent tier, see below)
- status: READY, unclaimed, blocked for a helper specifically (see below); not blocked for a core agent

## Why this landed with me and why I'm handing it off

The operator asked me directly (in chat, not hcom) about TASK-265's two
open questions. Both turned out to already be answered:

- **Remote OLLAMA_HOST timing**: operator restated "soon I will be using
  another machine... for now, that needs to be on hold" — this is DEC-029
  (2026-07-23) verbatim in substance. Nothing new to decide; DEC-029 stands.
- **Which `server.py` copy is authoritative**: operator said "whichever is
  most recent with the updated guidelines" — this is DEC-030 (2026-07-23):
  live is authoritative for features, template for install, merge direction
  is live → template, template's hardening lines must survive the merge.
  Nothing new to decide; DEC-030 stands.

While preparing to act on the operator's "go ahead," I found a **third,
previously-unaddressed gap**: live `server.py`'s `local_agent_defs()` has
no allowlist at all right now — every installed Ollama model (11, per
`ollama list` today) is launchable through the UI, not just a reviewed
set. This was already flagged once, on 2026-07-21, in
`artifacts/audits/task254-untracked-edit-2026-07-21.md`'s "Follow-up
needed, not done here" section — and never picked up. TASK-264 restored
the other three hardening items that same edit reverted, but explicitly
did not touch this one.

I took this back to the operator live. They chose: **keep the allowlist
to `qwen3.5:4b` only**, not the live copy's unused 5-model
`OLLAMA_MODEL_USES` table (3 of those 5 aren't even installed). Recorded as
**DEC-033** in `shared/decisions.md` — read it for full reasoning.

Then I tried to actually claim TASK-265 myself and `pre_dispatch_policy.py`
rejected it: `REJECT_HELPER_BROAD_ARCHITECTURE`. This is a structural
role boundary (helpers don't execute architecture-tier work), not a
missing-approval gate — the operator's go-ahead doesn't waive it, and
given this whole session has been about strengthening exactly these
guardrails, I didn't try to route around it. Hence this handoff instead of
a diff.

## What's already decided (do not re-litigate)

- DEC-029: remote `OLLAMA_HOST` policy — permitted in principle later,
  loopback stays default now, no implementation yet.
- DEC-030: live is authoritative for features; template for install; merge
  direction live → template; template's hardening lines must survive.
- DEC-033 (new): local-model allowlist is `qwen3.5:4b` only. Do not adopt
  `OLLAMA_MODEL_USES`'s broader list as the new allowlist.

## What's mechanically new since DEC-029/030 were recorded

I added `/home/mellow/Projects/CommandCenterUI/app/server.py` to TASK-265's
`output_paths` (via `map_task.py add-output-path`, actor
`task288-review-valo`) so the live file is now a declared, in-scope output
— satisfying `commandcenterui-boundary-decision.md`'s "output paths for the
exact external files to edit" requirement. The template copy
(`MAP_System/templates/install/command-center-ui/app/server.py`) was
already in scope.

## The merge recipe already exists — use it, don't re-derive it

`artifacts/audits/task254-untracked-edit-2026-07-21.md`'s "Repair (Part 2)"
section already worked out and verified a selective merge (built once,
confirmed it compiles clean, then reverted only because `server.py` wasn't
in TASK-254's scope at the time — it is now, via TASK-265):

**Keep from live** (real feature work, no regression):
`TERMINAL_PROMPT_*` constants, `plain_prompt_text`,
`extract_terminal_prompt`, `TerminalPromptLog`, the `read_chat`/`send_chat`
signature changes (intent validation, `terminal_since`), the `ollama-goose`/
`pi-lab-new` launcher entries and their `LOCAL_GOOSE_LAUNCHER`/
`LAB_PI_LAUNCHER` constants, the `prompts` endpoint's `ts` field, and the
already-consolidated `OLLAMA_HOST_PORT` single-configuration-point pattern
(this part is DEC-029's near-term action and is **already done** in the
live file — verified today, all three call sites reference the one
constant).

**Restore/keep from template, not live** (per DEC-033): the
`VISIBLE_OLLAMA_MODELS = {"qwen3.5:4b": ...}` allowlist and its gating
`if description is None: continue` skip in `local_agent_defs()` — both in
the template (unaffected) and, per DEC-033, added into the **live** file
too, since live currently has no gate at all. Do not adopt `live`'s
`OLLAMA_MODEL_USES` dict as a replacement allowlist; it can stay as inert
description text only if convenient, but must not itself gate which
models are exposed.

## Remaining TASK-265 acceptance criteria after the merge

- A **mechanical drift check** (AC4) — I did not find one already built;
  this still needs writing (e.g. a script that diffs the two `server.py`
  copies against a recorded allow-list of "known template-only hardening
  lines" and fails loudly on anything unexpected, so the next divergence
  is caught by a check rather than another manual audit).
- Restart plan for the live app once `server.py` changes (per
  `commandcenterui-boundary-decision.md`'s required-approval checklist) —
  not yet defined here; needs stating in whatever review record closes
  this out.
- Independent review before APPROVED (I'm disqualified — see below).

## Review note

I should not be the independent reviewer for this task's eventual
submission: I've now done enough hands-on investigation (diffing both
files, deciding scope questions with the operator, adding an output path)
that I'm not independent of it, separate from the helper-execution
boundary above.

## Known limitations

- I have not touched either `server.py` file. No merge has been performed.
- The exact restart/verification plan for the live app is not defined —
  whoever executes this should check whether the app is currently running
  and what a safe reload/restart looks like before editing the live file.
- `ollama list` output (11 installed models) was captured 2026-07-28 for
  DEC-033's context; it will drift over time and is not itself a source of
  truth for the allowlist decision (the allowlist is `qwen3.5:4b` only,
  regardless of what else is installed).
