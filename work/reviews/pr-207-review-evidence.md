reviewer: maps-lean-rev-tutu
head_sha: 21a27d77df518aa0c51b509582633b5f0cb6e9fd
independent: true
summary: Independent design/security-argument review of PR #207 (env-evidence-writer authority re-decision after PR #204). pogo's conclusion "posture did NOT regress, no runtime change required" is CONFIRMED against code at PR head. Verdict APPROVE. Only non-blocking nit: a few stale line-number references in the note.

# PR #207 — Independent Review Evidence

**Reviewer:** maps-lean-rev-tutu (independent; did not author — pogo authored)
**Coordinator:** niko
**Type:** design-only note + 1-line CAPABILITY_CHECKLIST annotation. No mutation testing (docs-only per `reference_committee_review`).
**Reviewed commit:** `21a27d77df518aa0c51b509582633b5f0cb6e9fd`
**Verdict:** **APPROVE**

## Scope / in-bounds check

Diff = `work/notes/2026-08-31-env-evidence-writer-authority-redecision-design.md` (new, +404) + `work/roadmaps/CAPABILITY_CHECKLIST.md` (+1/-1). Verified:
- No runtime code touched.
- CAPABILITY_CHECKLIST E4 row: annotation appended only, status stays `IN PROGRESS` — **no status flip**. Annotation text is accurate.
- In bounds as dispatched.

## Independent re-verification at PR head (rule 14)

Every load-bearing claim re-checked with `/usr/bin/grep` + direct read of the file at `21a27d7`.

### Q1 — is `recorded_by="maps-flow-start"` provenance, not authority?

**CONFIRMED.** `/usr/bin/grep -rn recorded_by runtime/` — complete hit list:
- `runtime/flow_start.py:55` — the write (`recorded_by="maps-flow-start"`).
- `runtime/state/environment.py:51,56,65,69,126,139,148` — arg validation (non-empty required), column insert, and the `RUN_ENVIRONMENT_RECORDED` event actor stamp.
- `runtime/state/schema.sql:495` — `recorded_by TEXT NOT NULL` column.
- `runtime/recovery/production.py:71` — docstring prose only.

**No consumer reads or branches on `recorded_by`:**
- `RunBoundValidator.validate_for_run` (`runtime/recovery/production.py:266-336`) reads `list_run_environment_evidence(run_id)` and works off `environment_spec_hash`, `spec_snapshot`, re-parsed `spec.sha256`. `recorded_by` is never referenced.
- `runtime/routing/environment_reports.py::select_recorded_environment_reports` — pure freshness filter; docstring + code confirm it "never converts stale/malformed/missing evidence into an incompatibility" and does not consult `recorded_by`.
- `runtime/recovery/supervisor.py::_advisory_environment_evidence` — explicitly advisory, "never consulted by any branch in tick()".

Row *content* authority is the operator: `flow_start._record_environment_evidence` (`runtime/flow_start.py:43-56`) does `spec = load_environment_spec(root / contract["spec_ref"])` — loads the checked-in, operator-authored spec file verbatim and hash-pins it; synthesizes nothing. `spec_ref` is set only through `runtime/state/environment_contract.py::update_contract` (review-gated task state). Step 4 is unreachable unless `task_record.get("environment") is not None` (`runtime/flow_start.py:159-163`) — the `environment` contract *is* the per-task opt-in.

No operator-identity registry needed: an environment observation carries no operator *assertion* to authenticate (contrast SEC4 Half 3). Agreed.

### Q2 — can `recovery-tick --repo-root` run quick-tier against a flow-start row, and does the `validation_repo_root` gate still suffice?

**CONFIRMED — yes it can, and the gate is unchanged and sufficient.**
- `runtime/cli.py:183-193` — `recovery-tick --repo-root default=None`, with the explicit comment that it is *deliberately unlike* `context`/`flow start` `--repo-root` (which default to `.`); absent it "no validator is constructed and no command runs."
- `runtime/cli.py:566-568` — the `maps claim` piggyback calls `run_recovery_tick_isolated(store, hcom_timeout_seconds=CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS)` with **no** `validation_repo_root`.
- `runtime/recovery/production.py:510-521` — `RunBoundValidator` is constructed **iff** `validation_repo_root is not None`.
- **No path reaches quick-tier without an explicit operator `--repo-root`.** Confirmed.

Executed commands = operator-authored spec, hash-verified twice: write-time `ENVIRONMENT_SPEC_FINGERPRINT_MISMATCH` (`runtime/state/environment.py:77-82`), read-time `spec_hash_mismatch` before `run_validation_tier` (`runtime/recovery/production.py:307-312`). Tier hard-wired `VALIDATION_TIER = "quick"` (`production.py:148`). Advisory unless `--enforce-validation` *also* passed (`cli.py:592-598`, `production.py:481-486,532`).

"No new privilege in kind" argument holds: post-#204, "a party who can insert rows" = "a party who can run `maps flow start` on a contracted task in a checkout whose `spec_ref` file they control" — and unattended execution still additionally requires an operator running `recovery-tick --repo-root` against that run. The evidence row adds no reach an attacker with checkout control + operator pass didn't already have.

The one real operational shift the note itself flags (an operator running `recovery-tick --repo-root` "without realizing rows now exist" now actually executes quick-tier where it was previously a no-op) is correctly characterized as operator-awareness, addressed by #206 doc correction + the checklist annotation — not a posture regression, because the operator still passes the flag whose help text fully describes the behavior.

### Q3 — safe by construction? "posture did not regress"?

**CONFIRMED.** Spot-checked 8 of the 9 clause-table rows against code — all `unchanged`:
| Clause | Verified at |
|---|---|
| `--repo-root` no cwd default, never on claim piggyback | `cli.py:183`, `cli.py:566`, `production.py:519` |
| commands = operator spec verbatim | `flow_start.py:43-47` |
| hash-verified at write | `environment.py:77` |
| hash-verified at read, fail-close | `production.py:307-312` |
| `quick` tier only | `production.py:148` |
| bounded budget | `production.py:152-160,272-281` |
| advisory unless `--enforce-validation` | `cli.py:592`, `production.py:532` |
| rows insert-only / immutable | `schema.sql:501-511` (`trg_run_environment_evidence_no_update` / `_no_delete`, `RAISE(ABORT, 'run environment evidence is immutable')`) |
| sensitive-text fail-close | `environment.py:71-76,92-102` |

The honest summary — "only clause (a)'s *frequency* (a row existing) changed; that is the intended activation of a capability `RunBoundValidator` was built inert to accommodate" — is accurate. flow_start step 4 is fail-**closed** (`flow_start.py:167-168`: `if not evidence.ok: return _failed(...)`), so a contracted task with a malformed/sensitive spec cannot complete `flow start` — no fail-open path.

### Q4 — deferral of the `recorded_by` allowlist

**Appropriate.** `recorded_by` is already `NOT NULL` on every row (`schema.sql:495`) and stamped at write — an allowlist check at the `RunBoundValidator` read site genuinely needs no schema change. No downstream consumes `recorded_by` today, so there is no current distinction that a deferral leaves broken. Documented-not-built, default-off, strictly additive: correct call. The MUST-NOT list and STOP conditions for that eventual slice are sound (esp. "STOP if the allowlist needs `recorded_by` *authenticated* rather than string-matched — that is SEC4-Half-3 bleeding in").

### "OPERATOR DECISION REQUIRED" callout

Correctly scoped as **ratification, not a blocker**. The technical "no regression" claim stands entirely on code (Q3). The callout asks the operator to record acceptance of a *threat-model framing* — "a task's `environment` contract is sufficient operator authority for that task's runs to become quick-tier-executable under an explicit `--repo-root`." That is a genuine operator acceptance (same authority class as `spec_ref` / `max_age_seconds` / `required_for_routing`), not a hidden unmade code decision. The stated fallback if the operator declines (build the Q4 slice, default `--trusted-evidence-recorder` to exclude `maps-flow-start`) is correct and is *not* a flow-start runtime change.

## Finding: pogo's "no regression" conclusion is NOT wrong

The dispatch's BLOCK condition — "quick-tier can now run against attacker-influenceable evidence without an operator gate" — **does not fire**. The operator `--repo-root` gate is intact, the executed commands are the operator's own checked-in hash-pinned spec, and an attacker who could influence the spec file already has checkout control. No escalation, no urgent flag.

## Non-blocking nits (for a follow-up doc correction, not this PR)

1. Stale line references in the note's "Re-verified facts" section:
   - "step 4 ... (lines ~150-166)" → actually `runtime/flow_start.py:155-168`.
   - `recorded_by="maps-flow-start"` implied ~line 44 → actually `flow_start.py:55`.
   - production.py docstring trigger "lines ~78-85" / "~78-85" → the re-decision sentence is at `production.py:82-85`.
   The *substance* at each cited location is described accurately; only the numbers drift.
2. Q1 point 2 cites `runtime/state/environment_contract.py` `store.update_contract` — verified it exists (`environment_contract.py:101`) and gates `spec_ref`; fine, just noting it was checked.

## Verification run

`python3 scripts/check_review_evidence.py 207` — run from the review worktree after this file is committed as an evidence-only commit; `head_sha` above is the note commit `21a27d7`, which the checker reaches by walking past the trailing evidence-only commit.

## Verdict

**APPROVE.** Independent re-verification confirms pogo's conclusion on all four questions and the two callouts. No runtime change required; posture did not regress. Recommend the operator record the Q-ratification acceptance (recommended answer: yes) at merge.
