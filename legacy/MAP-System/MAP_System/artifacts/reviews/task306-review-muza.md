# Review: TASK-306 — Version and align Biggie canonical Command Center Lab with Smalls

Reviewer: claude-lab-muza (independent — not task owner; claimed via `map-authority claim-review` at 2026-07-29T15:26:14Z, confirmed no prior open claim via `get-open-review`)

## Verdict

CHANGES_REQUESTED (self-corrected after mebo's catch — see Self-Correction section; the intermediate APPROVED verdict below was wrong and never reached the canonical record because the gateway `approve` call itself failed)

## Reviewed Files

- `MAP_System/artifacts/operations/command-center-cross-pc-alignment-2026-07-29.md`
- `MAP_System/notes/command-center-cross-pc-sync.md`
- `MAP_System/scripts/command_center_version.py`
- `MAP_System/templates/install/command-center-ui/README.md`
- `MAP_System/templates/install/command-center-ui/app/server.py`
- `MAP_System/templates/install/command-center-ui/src/bcmagent.svg`
- `MAP_System/templates/install/command-center-ui/src/orchestrator.{css,html,js}`
- `MAP_System/templates/install/command-center-ui/version.json`
- `MAP_System/tests/test_command_center_agent_identity.py`
- `MAP_System/tests/test_command_center_attention_history.py`
- `MAP_System/tests/test_command_center_composer_alignment.py`
- `MAP_System/tests/test_command_center_deployment_parity.py`
- `MAP_System/tests/test_command_center_message_intent_copy.py`

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/templates/install/command-center-ui/version.json` | Acceptance criterion 1 ("repo template source matches [Biggie live] byte-for-byte") is currently **false, reproduced independently**. Live `src/orchestrator.js` and `src/orchestrator.css` were edited at 2026-07-29T15:28:54Z / 15:29:09Z (an unrelated, operator-directed recap-card feature) — after TASK-306 was SUBMITTED (15:25:07Z) and after this review was claimed (15:26:14Z). Rerunning `command_center_version.py verify --bundle-root /home/mellow/Projects/CommandCenterUI` right now returns `PARITY FAILED (2 issues)` with concrete changed hashes on both files. The submitted evidence document's "clean, zero issues, both directions" claim was true at generation time (15:16:38Z) but is stale at review time. | Regenerate `version.json` against Biggie's current live state (`command_center_version.py generate`), re-import the two changed files into the template, rerun `verify` in both directions until clean, and rerun `test_command_center_deployment_parity.py`'s live-vs-template test before resubmitting. Owner (nene) has already acknowledged this independently and stopped further live edits pending this verdict. |
| REQUIRED | `MAP_System/tests/test_command_center_deployment_parity.py` | This new test is the sole mechanical check enforcing the exact invariant TASK-306 exists to establish (live/template checksum parity), but it is not registered in `MAP_System/scripts/run_tests.sh` (confirmed: only `test_command_center_intake.py` appears among all `test_command_center_*` files in the full `run_check` list). It only runs when someone remembers to invoke it by hand, so the drift this task is meant to prevent can recur silently — exactly as just happened live during this review — without the standard test-suite gate ever catching it. | Add a `run_check` line for `test_command_center_deployment_parity.py` in `run_tests.sh` so parity checking is durable, not manual-only. (Note, non-blocking for this task: the other 8 pre-existing `test_command_center_*.py` files are similarly unregistered — pre-existing debt, not introduced by TASK-306, flagged for awareness only.) |
| OPTIONAL | `MAP_System/scripts/command_center_version.py`, `version.json` | `--source-host` defaults to a literal `"Biggie (KUDU, mellow@192.168.1.177)"`, embedding the operator's local username and LAN IP into a tracked/generated file. Consistent with existing practice already committed elsewhere in this repo (e.g. `map_authority.py`'s own examples, install scripts); not a new issue and not required to fix here. | None required. Noted for awareness only. |

## Verification

- `MAP_System/.venv/bin/python -m py_compile MAP_System/scripts/command_center_version.py MAP_System/tests/test_command_center_deployment_parity.py` — PASS.
- `command_center_version.py verify` (template, default bundle-root) — OK, 11/11 managed files, at first check.
- `command_center_version.py verify --bundle-root /home/mellow/Projects/CommandCenterUI` — **OK on first check, PARITY FAILED on independent recheck** after live edits landed mid-review (see Finding 1). Exact failure: `changed: src/orchestrator.css (expected sha256 6df55da2b3d5…, got 77a28792d86e…)`, `changed: src/orchestrator.js (expected sha256 e1ce29c01e23…, got 8a63cd0b0b66…)`. Corroborated against `stat` mtimes on the live files (2026-07-29 15:28:54Z / 15:29:09Z), matching the edit window mebo and nene both independently reported.
- `MAP_System/tests/test_command_center_deployment_parity.py` — 7/7 PASS at time of run (includes the live-vs-template test, which passed *before* the live edit landed; would now fail on rerun given the confirmed drift above — not rerun a second time to avoid redundant churn once the fix path is clear).
- `test_command_center_agent_identity.py`, `test_command_center_composer_alignment.py`, `test_command_center_message_intent_copy.py`, `test_command_center_attention_history.py` — each OK with exactly 1 skip, independently rerun. Inspected `test_command_center_agent_identity.py` directly: the `@unittest.skip` applies only to the retired `test_live_files_match_installer_template` method with an accurate, specific reason; the file's other two assertions are untouched and still exercise real behavior.
- `grep -n "^run_check" MAP_System/scripts/run_tests.sh` — confirmed only `command_center_intake_test` among all Command-Center-named checks; no line for `test_command_center_deployment_parity.py` or any of the four incidentally-touched files.
- Read `MAP_System/notes/command-center-cross-pc-sync.md` in full: direction lock (Biggie always source), explicit non-goal ("never writes to map.db, never calls map_authority.py's task/claim/review verbs, never changes which host is the MAP authority"), and all four required preconditions (destination identity, clean-or-preserved destination state, pre-write backup, dry-run review) plus staged/atomic activation and a verified rollback path are specified before any Smalls-side write is permitted. No step of this protocol has been executed — confirmed by inspecting `MAP_System/artifacts/operations/`: only pre-existing 2026-07-28 cross-PC docs and today's Biggie-side-only evidence file exist; nothing dated as a Smalls deployment.
- Read `MAP_System/scripts/command_center_version.py` in full: `generate()` refuses to run while any unaccounted-for file exists under the bundle root (hard stop, not silent pass); the three exclusion classes (runtime/host-local, host-rendered, pre-existing legacy) are each named and justified in-code; nothing in the excluded sets overlaps `MANAGED_FILES`.
- Targeted security read of `app/server.py`'s network-facing additions relevant to today's UI work (`/api/term`, `/api/term/inject`): default bind is `127.0.0.1` (matches `CommandCenterUI/AGENTS.md`'s localhost-only rule); POST endpoints gated by `same_origin_request()`; `term_inject` validates the target name against a real hcom instance via `known_instance()` (regex + DB row check), caps injected text at 500 chars, uses argv-list `subprocess.run` (no `shell=True`), and writes a durable audit line per injection. This is pre-existing live behavior being imported unchanged (proven identical by the manifest at generation time), not new logic introduced by TASK-306 itself — a full from-scratch audit of `server.py` is out of this task's scope.

## Notes

This is a genuine timing/process gap, not owner error: nothing in the current protocol pins or freezes the live source directory during the window between submission and review sign-off, and the operator legitimately kept directing new work (the recap-card feature) against that same live path while review was in flight. Owner (nene) independently reproduced the same failure and stopped further live edits pending this verdict — appropriate response, no further action needed from them beyond the fix below.

Recommend the resubmission treat "re-verify parity" as the literal last step immediately before resubmitting (not just at whatever earlier point `generate` was run), and that any future cross-machine version-pinning task consider whether a short, explicit "frozen for review" convention is worth adding — out of scope to require here, offered as a forward note only.

The engineering itself (`command_center_version.py`'s exclusion design, the cross-PC protocol's precondition/backup/staged-activation/rollback sequencing, direction lock, and MAP-authority isolation) is sound and needs no redesign — this verdict is about re-syncing to current live state and closing the durability gap on the parity test's own registration, not about the approach.

## Rereview (2026-07-29, attempt 2, claude-lab-muza)

Owner reworked and resubmitted (`CHANGES_REQUESTED` → `READY` → `SUBMITTED`, attempt 2/3). Reclaimed via `map-authority claim-review` (no prior open claim) and independently reran every check rather than trusting the resubmission narrative:

- `command_center_version.py verify` (template, default root) — **OK, 11/11 managed files.**
- `command_center_version.py verify --bundle-root /home/mellow/Projects/CommandCenterUI` — **OK, 11/11 managed files**, checked at rereview time, not reused from the prior stale result.
- `version.json` version id — `2026-07-29-orchestrator-v2-recap`, confirming the manifest was actually regenerated, not just re-verified against the old one.
- `test_command_center_deployment_parity.py` — 7/7 PASS, rerun fresh.
- `grep -n "command_center_deployment_parity_test\|command_center_intake_test" MAP_System/scripts/run_tests.sh` — confirms the new `run_check` line is present at line 100, immediately after `command_center_intake_test` at line 99, exactly as claimed.
- `bash -n MAP_System/scripts/run_tests.sh` — syntax OK.
- `py_compile` on `command_center_version.py` and `test_command_center_deployment_parity.py` — OK.
- All four previously-touched Command-Center test modules (`agent_identity`, `composer_alignment`, `message_intent_copy`, `attention_history`) — each still OK with exactly 1 skip, unchanged from the original review.
- `map-git diff --check` — clean exit.
- `MAP_System/artifacts/operations/` directory listing — still no Smalls-deployment-dated artifact; only the updated Biggie-side evidence file (now with a documented "Rework" section explaining the drift, root cause, and both fixes) and the pre-existing 2026-07-28 docs. No Smalls/RUKI write occurred, as required.
- Read the new "Rework" section in `command-center-cross-pc-alignment-2026-07-29.md`: accurately describes the drift's root cause (no mechanism pins live source during a review window; this session's own concurrent recap-card work is what surfaced it), both fixes, and the correct `map-authority task rework` → reclaim transition sequence.

Both REQUIRED findings from the first pass are resolved and independently confirmed, not merely re-asserted. No new issues found. The OPTIONAL note (hardcoded `mellow@192.168.1.177` in `command_center_version.py`'s default) remains unchanged and still does not block approval, consistent with existing codebase practice.

**Verdict at this point: APPROVED.** (Superseded below — see Self-Correction. This verdict never reached the canonical record: the `map-authority task approve` call itself failed with the same empty-stderr `authority request failed (1)` signature as the register-agent bug documented in `INS-0054`, tried twice, not force-retried. Traced to `MAP_System/artifacts/planning/biggie-smalls-orchestration-action-plan-2026-07-29.md` Step 1 — a known, already-tracked production gateway bug, independent of TASK-306 itself.)

## Self-Correction (2026-07-29, prompted by codex-lab-mebo)

mebo caught a real gap in this review's own methodology, on both passes: I verified the two specific REQUIRED findings carried over from pass 1 (parity, test registration) but never re-checked the submission against TASK-306's **full, literal acceptance-criteria list** either time. Doing that now:

| # | Acceptance criterion (verbatim, abbreviated) | Met? |
|---|---|---|
| 1 | Biggie live/template byte-for-byte parity, exclusions explicit | Yes — reverified clean both directions on rereview. |
| 2 | Deterministic `version.json`/checksum manifest, fails on drift | Yes — `generate`/`verify` behavior independently exercised (7/7 tests, including deliberate tamper/delete/extra-file negative cases). |
| 3 | Cross-PC protocol: direction lock, destination identity, backup, dry-run, staged verification, atomic activation, never touches MAP authority topology | Yes, **as a written document only** — `command-center-cross-pc-sync.md` specifies all of this correctly, but a written protocol satisfies "the protocol locks direction / requires X / never changes Y" only as a design artifact, not as proven operational behavior. |
| 4 | Smalls not modified until identity/dry-run confirmed; remote writes preserve rollback evidence | **Not applicable / not attempted** — no Smalls-side write of any kind has happened, by the task's own evidence note. Correct as a safety property (nothing was done recklessly), but this criterion describes a proof obligation about an actual remote write, which does not exist yet to evaluate. |
| 5 | Focused tests pass; Biggie live/template parity proven; **Smalls installed parity and communication proven after deployment**; independent review before approval | Tests/parity: yes. **Smalls installed parity and communication: not done, not attempted, explicitly deferred** in the evidence note's own "What TASK-306's acceptance criteria still require (deferred, not done)" section. Independent review: this review itself. |

Criterion 5's Smalls-parity clause (and, by extension, the practical substance of criterion 4) is **not met** by this submission, and was never going to be met by design — nene's evidence note is explicit that this pass only implements "the local versioned-source half," per an earlier informal scoping instruction from mebo. That instruction narrowed *what work happened in this pass*, but nothing narrowed the task's own recorded `acceptance_criteria` in `map.db` to match — the canonical record still literally requires Smalls-side proof. A reviewer (me) informally treating the deferred items as out-of-scope because a prior chat message said so is exactly the kind of undocumented, unrecorded scope narrowing this system's own process exists to prevent: the task record is the source of truth, not a remembered instruction in an hcom thread.

Per mebo's three options (retain APPROVED anyway / reject now and rescope later / obtain an operator-approved rescope first, then rereview that exact scope) — **mebo's recommendation (reject now) is correct and is what this review adopts.** The engineering delivered so far (parity tool, protocol document, template import, test registration) is real, sound, and independently verified — but it satisfies a subset of TASK-306's literal acceptance criteria, not all of them, and approval requires all of them or an explicit, canonical rescope of the task record itself (not a reviewer's informal judgment call).

**Corrected verdict: CHANGES_REQUESTED.** Required action: either (a) a canonically-recorded rescope of TASK-306's acceptance criteria to explicitly split off the Smalls-deployment half into its own follow-up task (matching what the evidence note already describes as deferred), then resubmit against the narrowed criteria for a fresh, correctly-scoped review; or (b) complete the Smalls-side criteria under this same task before resubmitting. Given the operator-approved `biggie-smalls-orchestration-action-plan-2026-07-29.md` blocks WP-2 (source convergence) until its own Steps 1–3 (gateway repair, password rotation, WP-1 architecture decision) are done, option (a) is almost certainly the realistic path — but that rescope decision belongs to the operator/orchestrator (nene), not to this review.
