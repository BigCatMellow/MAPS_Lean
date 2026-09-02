reviewer: maps-lean-nava
head_sha: 5fd39ee012b50a52741aab6f97a5321561b00c15
independent: true
summary: APPROVE — the operator-answer record faithfully captures the session-17 §3b batch (release-check batch, SEC4 B1, Ask #2, Ask #3 all verbatim against the relay); one factual inaccuracy in the Ask #1 section ("control plane already runs" in a checkout with no `.maps/` — verified) was flagged and corrected in-branch; the rebased tip 5fd39ee is 1 file / +76, clean vs current origin/main, smoke exit 0.

# PR #243 review evidence — operator answered the trajectory-#16 §3b batch

Verification-only review of a docs-only PR (`work/notes/OPERATOR_ASK_2026-08-31-session13.md`, +76). Two review rounds folded in; this evidence is bound to the final rebased tip.

## Round 1 — faithfulness of the recorded answers vs the session-17 relay

| Item | Recorded in doc | Matches relay? |
|---|---|---|
| **`flow release-check` batch (#234 §6)** | new append-only `release_checks` table keyed `(task_id, review_id)` (acq ref + smoke ref + composite + optional operator-ack); persist evaluator `report_ref`s + input evidence refs; `composite == BLOCKED` **advisory** (approval-blocking = later 3b slice); any of releasing party / reviewer / operator may run | **Yes — verbatim.** |
| **SEC4 B1 `authorized_operators`** | keep structural `--actor`/`decided_by`; opt-in real identity check at one site, default off; no rows -> fail-open (disabled); genesis row at `maps init` when opted in + separate `maps operator add` for later rows | **Yes — verbatim.** |
| **Ask #2 — env-evidence-writer ratification** | YES; a task's `environment` contract is sufficient operator authority for quick-tier execution under explicit `--repo-root`; no runtime change; Q4 fallback not needed | **Yes.** |
| **Ask #3 — kill pid 3874** | commit history: "AUTHORIZED; operator to run" -> updated to **DONE** ("Operator ran `kill 3874`, confirmed dead; 4 worktree locks now safe to release as part of Infra #2") | **Yes.** |
| **Infra #2 / #3 (worktree + stale-branch cleanup)** | "still pending the operator — Not in the answered batch" | **Yes — correctly held out.** |

## Round 1 finding (REQUEST_CHANGES) — Ask #1 section factual inaccuracy — CORRECTED

Original doc: *"the obvious candidate is the MAPS_Lean checkout itself ... which is where the control plane already runs. Expect `LEASE_EXPIRED` denials on first run ..."*

Verified: `ls ~/Projects/MAPS_Lean/.maps/` -> "No such file or directory" — no `.maps/` directory at all, so no control-plane DB; the control plane does **not** "already run" here. The session-17 relay itself flagged this precondition (*"`.maps/state/maps.db` does NOT exist in this dev checkout — the live control-plane DB path + `--harness-project-id` need to be established before the pass can run"*); the committed doc had dropped it and asserted the opposite. Material because this doc drives Ask #1 target-pinning.

## Round 2 (delta, commit `12b9d7a` -> rebased `5fd39ee`) — fix verified

The Ask #1 clause now reads: *"The obvious candidate is the MAPS_Lean checkout (`--repo-root ~/Projects/MAPS_Lean`) — but `.maps/` does not yet exist in this dev checkout, so there is no control-plane DB here today. Establishing the control-plane DB path and registering the `--harness-project-id` (per `docs/CONTROL_PLANE_SETUP.md`) is part of the coordinator's target-pinning step, before any enforced pass. Only once a control plane with real run manifests exists does the `LEASE_EXPIRED`-on-first-run -> remediate-per-§5 ... narrative apply."* — corrects the false assertion, restores the relay's precondition, correctly scopes the `LEASE_EXPIRED` narrative, and retains AUTHORIZED + the 7-row unblock list + "verify each hard before any status flip". No other change. Delta is that one section only.

## Final state

- Rebased tip `5fd39ee012b50a52741aab6f97a5321561b00c15`: `git diff origin/main..HEAD --stat` = 1 file, `work/notes/OPERATOR_ASK_2026-08-31-session13.md` (+76). Clean.
- `python3 -m runtime.smoke` -> `"ok": true`, exit 0.
- No runtime / test / checklist change. `docs/CONTROL_PLANE_SETUP.md` exists (the §5 reference is valid).

## Verdict

APPROVE.
