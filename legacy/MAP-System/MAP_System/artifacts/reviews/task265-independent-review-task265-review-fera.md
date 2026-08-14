# Review: TASK-265 (CommandCenterUI server.py reconciliation)

## Verdict

APPROVED

## Reviewer

task265-review-fera (fresh, visible Sonnet helper spawned specifically for
this review per `MAP_System/inbox/helpers/helper-review-task-265.md`).
Owner: `lili-replacement-nisa`. Not `lili-replacement-nisa` or
`claude-lab-lili` (rotation lineage), not `task288-review-valo`
(self-disqualified — diffed both files, took the DEC-033 decision live with
the operator, added the live output path while preparing the handoff), not
`pi-lab-mule` (Pi is exploratory-only, DEC-008, not a review authority).
Claimed cleanly via `claim_review("TASK-265", "task265-review-fera",
db_path="MAP_System/map.db")` — `True` on first call.

## Files Reviewed

- `/home/mellow/Projects/CommandCenterUI/app/server.py` (live, external —
  the only file with a real code change)
- `MAP_System/templates/install/command-center-ui/app/server.py` (template)
- `MAP_System/tests/test_command_center_ollama_allowlist.py` (new, 6 tests)
- `MAP_System/artifacts/tests/task265-commandcenterui-reconciliation-delivery-note.md`
- `MAP_System/tasks/TASK-265.json`
- `MAP_System/shared/decisions.md` (DEC-029, DEC-030, DEC-033)
- `MAP_System/handoffs/HANDOFF-TASK-265-task288-review-valo-to-nisa.md`

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Decision record states whether CommandCenterUI may reach a remote `OLLAMA_HOST`, and by what opt-in mechanism | PASS (carried over, confirmed settled) | DEC-029 (2026-07-23): permitted in principle, only via explicit UI-visible config, not ambient env inheritance; implementation deferred. Verified live `server.py` still hardcodes `OLLAMA_HOST_PORT = "127.0.0.1:11434"` (line 116) at every call site (lines 459, 882) — no remote support was added by this submission, consistent with "not yet authorized." Not re-litigated, only confirmed unchanged. |
| 2 | One copy of `server.py` declared authoritative, sync direction written down | PASS (carried over, confirmed settled) | DEC-030 (2026-07-23): live authoritative for features, template for install, merge direction live→template. Delivery note followed this direction (wholesale-copied live → template) and the operator independently restated the same substance to `task288-review-valo` before this submission (per the handoff note). Genuinely settled, not re-derived here. |
| 3 | Live feature work from the 2026-07-21 edit folded in or explicitly rejected with reasons | PASS | Template now byte-identical to the fixed live copy (verified myself, see below): terminal-prompt feature set, chat intent validation, `OLLAMA_HOST_PORT` consolidation, and the `ollama-goose`/`pi-lab-new` launcher entries are all present. Nothing was silently dropped. |
| 4 | Mechanical drift check exists | PASS | `test_command_center_ollama_allowlist.py`'s `TemplateLiveGateParityTests` (2 tests) does exact substring matching of the `VISIBLE_OLLAMA_MODELS` definition and the `local_agent_defs()` gate against **both** files independently, failing loudly if either drifts. Ran it myself — passes today. |

## Reproduce, don't trust

- `MAP_System/.venv/bin/python3 -m unittest MAP_System.tests.test_command_center_ollama_allowlist -v` — 6/6 PASS, reproduced myself.
- Re-ran all 9 `test_command_center_*` suites present in the tree (the delivery note names 5; I found 4 more and ran those too, since the note's list is not itself authoritative for "no regression"): `test_command_center_agent_identity`, `test_command_center_attention_history`, `test_command_center_attention_popup`, `test_command_center_composer_alignment`, `test_command_center_lab_tab_titles`, `test_command_center_message_intent_copy`, `test_command_center_popup_formatting` — all PASS. `test_command_center_intake` and `test_command_center_orchestrator_startup` ran 0 tests (environment-gated, unrelated to `server.py`'s Ollama-gating logic — not a TASK-265 regression).
- `diff` on the two `server.py` files myself: exit 0, **byte-identical**, confirming the delivery note's claim.
- App-running check: `ps aux | grep server.py` — no matching process, confirming the delivery note's "not currently running" claim and its consequent restart-plan (no restart needed now, next launch picks up the fix).

## Gate logic read directly (not trusted from the test's pass/fail)

Read `local_agent_defs()` and `VISIBLE_OLLAMA_MODELS` in the live file
myself (`app/server.py:201-224`, `907-930`):

- `VISIBLE_OLLAMA_MODELS = {"qwen3.5:4b": ...}` — single entry, as DEC-033
  requires.
- `local_agent_defs()` iterates `ollama_models()` (the actual installed set
  from `ollama list`) and does `description = VISIBLE_OLLAMA_MODELS.get(model_name); if description is None: continue` — an explicit allowlist gate, fail-closed by construction: a model not in the dict is skipped, not defaulted to visible.
- `OLLAMA_MODEL_USES` (lines 201-207, 5-entry dict) is grep-confirmed to
  have **no other reference in the file** beyond its own definition and the
  comment block directly above `VISIBLE_OLLAMA_MODELS` that explicitly
  labels it inert and points at DEC-033. `local_agent_defs()` never reads
  it. Confirmed this is genuinely true of the code, not just asserted by
  the test.
- Since the two files are byte-identical, this all holds for the template
  copy too — verified directly rather than inferring from the diff result
  alone (read the template file's same line ranges).

## Item 6: is leaving `OLLAMA_MODEL_USES` in, unused, the right call?

Yes, with a mitigation already in place that makes this stronger than a
bare "DEC-033 permits it" argument. The latent risk named in the review
packet is real in the abstract — dead-but-plausible config inviting a
future "helpful" rewiring — but two things blunt it here:

1. The comment directly above `VISIBLE_OLLAMA_MODELS` (`app/server.py:208-221`) doesn't just describe the field, it explicitly says `OLLAMA_MODEL_USES` "does not gate anything," names `VISIBLE_OLLAMA_MODELS` as "the actual security gate," and cites DEC-033 by ID with a one-line reason ("Do not widen this... that was explicitly rejected"). That's stronger than typical inert-config hygiene — it pre-empts the exact misunderstanding the risk describes, in the same file a future editor would be reading.
2. `test_ollama_model_uses_is_not_used_as_a_gate` doesn't just check the current dict contents — it imports and executes the **real** `local_agent_defs()`, feeds it all 5 `OLLAMA_MODEL_USES` model names as "installed," and asserts only the allowlist∩installed set is exposed. I traced this myself: if a future edit changed `local_agent_defs()` to read `OLLAMA_MODEL_USES` instead of (or in addition to) `VISIBLE_OLLAMA_MODELS`, this test would fail immediately, because the 5 `OLLAMA_MODEL_USES` names don't overlap with `qwen3.5:4b`. This is a real regression guard against the specific failure mode named in the review packet, not just documentation.

Net: removing `OLLAMA_MODEL_USES` entirely would be marginally safer in
isolation, but DEC-033 already made this call deliberately and the
in-code comment + test together substantively cover the residual risk. Not
a finding.

## Item 7: was folding `OLLAMA_MODEL_USES` into the template via wholesale copy correct?

Yes. DEC-033 says the 5-model dict "can stay as inert description text
only if convenient" — i.e., permitted to remain, not required to be
stripped. The wholesale-copy approach (verified byte-identical) carries it
into the template as exactly that: inert text, not a gate, matching what
DEC-033 authorized. That 2 of the 5 (`llama3.2:3b`, `llama3.2:1b`) aren't
installed doesn't change this — the dict was never claimed to reflect
current installation state, only to be non-gating description text, which
it is in both copies. This is not a case of the wholesale copy accidentally
promoting something DEC-033 rejected; the thing DEC-033 rejected was using
it *as an allowlist*, which the code does not do.

## Forbidden Changes Check

`git status --porcelain` on TASK-265's in-repo output paths, run from the
repo root, shows exactly:

```
 M Source/MAP_System/templates/install/command-center-ui/app/server.py
?? Source/MAP_System/artifacts/tests/task265-commandcenterui-reconciliation-delivery-note.md
?? Source/MAP_System/tasks/TASK-265.json
?? Source/MAP_System/tests/test_command_center_ollama_allowlist.py
```

All four match the registered `output_paths` (the live external file isn't
git-tracked at all — confirmed `~/Projects/CommandCenterUI` has no `.git`,
consistent with it being outside MAP's normal writable scope per
`commandcenterui-boundary-decision.md`). `TASK-265.json` itself and
`workflow/task_graph.json` (also modified) are the standard claim/submit
mirror-export side effects, not scope creep. No file outside the registered
output paths was touched. The wider uncommitted diff visible in overall
`git status` (many unrelated `M` files across the tree) predates this
submission and belongs to concurrent work, not TASK-265 — checked by
content, not by count.

## Findings

None.

## Notes

This is a real fix to a real, unnoticed-for-a-week security gap (every
installed Ollama model, 11 as of today, was launchable through the UI
instead of just the reviewed one), and the submission holds up under
independent reproduction on every axis the review packet asked for: the
gate is genuinely fail-closed code (not just a passing test), the two
copies are genuinely byte-identical, nothing outside scope was touched, and
the two carried-over policy questions (remote-Ollama, authoritative-copy)
were correctly treated as already-settled rather than re-opened. The new
test suite is unusually well-aimed — it exercises the live module's actual
functions under monkeypatched installed-model lists rather than re-asserting
static text, which is exactly what makes the `OLLAMA_MODEL_USES` mitigation
in item 6 credible rather than aspirational.
