# Review: TASK-272

task_id: TASK-272
reviewer: claude-lab-gabi
task_owner: codex-lab-veto
review_date: 2026-07-22

## Verdict

APPROVED

Add-context-continuity-checks-to-startup is correct, internally consistent
across all five outputs, and test-enforced. The four acceptance criteria are
met, the referenced scripts and subcommands all exist and run, the released
TASK-271 rotation protocol is unchanged, and the specific focus areas veto
flagged (exact current hcom identity, validate-before-advise-before-routing
ordering, single bigboss message content, advisory/read-only startup boundary)
each hold.

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Both launcher prompts require startup to run `context_rotation.py validate` and `advise` for the exact current hcom identity before routing. | PASS | Both `ai-command-center-lab-claude` and `-codex` prompts contain the `validate` command, `advise --agent <your-exact-current-hcom-identity>`, and "exact current hcom identity". `test_startup_context_rotation.py` asserts all three and asserts `prompt.index(validate) < prompt.index(advise) < prompt.index(route)`. Mutation-checked: removing `validate`, weakening `advise`, or reordering `validate` after the route each makes the test fail. |
| 2 | The one bigboss message includes continuity validation state and the checkpoint/rotation recommendation alongside the resume plan or priorities request. | PASS | Prompts require "exactly one hcom message" containing "continuity validity", "checkpoint/rotation recommendation", "resume plan", and "request priorities in that same message". All four strings are asserted by the test. The startup notes and AGENTS.md state the same. |
| 3 | Startup docs and AGENTS.md state the same ordering and safe behavior: startup checks advise/validate only, never supersede or clear automatically. | PASS | AGENTS.md "Verified Context Rotation" and `command-center-lab-restart-startup.md` both state the checks are advisory and read-only and that startup must never clear history, prepare/finalize a rotation, supersede a session, or use `advise --notify`. Test asserts "advisory and read-only" and "never use advise --notify". |
| 4 | Focused tests cover both launchers and fail if either omits validate, advise, continuity ledger, or plan-reporting language. | PASS | `test_startup_context_rotation.py` covers both launchers; mutation testing confirms it is not vacuous. |

## Focused checks requested by owner

- **Exact current hcom identity.** Present in both launchers, the startup notes,
  and AGENTS.md. `advise` takes `--agent` and the prompt binds it to the current
  identity rather than a static name. Verified `context_rotation.py advise
  --agent claude-lab-gabi` runs and returns structured checkpoint/rotation state.
- **validate → advise → routing ordering.** Enforced by an explicit index
  assertion in the test, not merely by co-presence. Independently mutation-tested
  by moving `validate` after the route command; the test fails as required.
- **One bigboss message content.** The prompt composes continuity validity,
  checkpoint/rotation recommendation, status, and resume-plan-or-priorities into
  a single message. No second startup message path is introduced.
- **Advisory/read-only startup boundary.** All three prose surfaces forbid
  `advise --notify`, automatic history clearing, prepare/finalize, supersede, and
  replacement launch at startup. `--notify` is a real `advise` flag, so the
  prohibition is meaningful rather than decorative.

## Forbidden Changes Check

| Boundary | Status |
|---|---|
| Do not change the verified TASK-271 rotation protocol. | NOT BROKEN. `test_context_rotation.py` passes 15/15, including snapshot-tamper and pre-ACK canonical-drift detection and the proportional-guard boundaries. |
| Startup must remain advisory; no automatic supersede/clear. | NOT BROKEN; explicitly stated in all three surfaces and asserted in the test. |
| Do not duplicate or clobber existing AGENTS.md sections. | NOT BROKEN. TASK-272 shares AGENTS.md with the already-approved TASK-269 (helper model tier) edit; each of Retrieval capsule, Helper-note metadata contract, Verified Context Rotation, and File Ownership appears exactly once. The new section is additive and does not overwrite the TASK-269 content. |

## Files Reviewed

- `MAP_System/AGENTS.md`
- `MAP_System/notes/command-center-lab-restart-startup.md`
- `MAP_System/templates/install/bin/ai-command-center-lab-claude`
- `MAP_System/templates/install/bin/ai-command-center-lab-codex`
- `MAP_System/tests/test_startup_context_rotation.py`
- Cross-referenced: `scripts/context_rotation.py`, `scripts/operational_lessons.py`

## Verification

- `context_rotation.py validate` — runs; currently reports `ok:false` with
  `claude-lab-gabi:canonical_task_drift`. This is the REVIEWER's own stale
  prepared rotation (I prepared a rotation, then continued working and released
  tasks, so the frozen snapshot legitimately no longer matches canonical state).
  It is NOT a TASK-272 defect; it is the validator correctly detecting drift,
  which is evidence the startup check does something real. Reviewer will abandon
  the stale prepared attempt separately.
- `context_rotation.py advise --agent claude-lab-gabi` — runs; returns
  `state: rotation_due` at 300436 tokens with the 120k/150k thresholds.
- `context_rotation.py` and `operational_lessons.py` both expose every
  subcommand the prompts invoke (`validate`, `advise`, `orientation`), and
  `advise` exposes both `--agent` and `--notify`.
- `test_startup_context_rotation.py` — 2/2 pass; mutation-tested non-vacuous.
- `test_context_rotation.py` — 15/15 pass; released protocol intact.
- `sh -n` on both launchers — syntax OK.

## Notes

- Non-blocking robustness observation, not a required change: the test's
  `prompt_text` parser locates the prompt by the literal delimiter `'\n\nexec `.
  Both launchers currently match, but a future edit that alters the line between
  the closing quote and `exec` would make the parser raise `ValueError` rather
  than assert a contract gap. Fine as-is; worth knowing if the launcher shape
  changes.
- The prompts also add `operational_lessons.py orientation` and (in the notes)
  an emergence-coverage step. These are beyond the four acceptance criteria but
  consistent with startup orientation, reference real subcommands, and do not
  violate the advisory/read-only boundary. Not a finding.
