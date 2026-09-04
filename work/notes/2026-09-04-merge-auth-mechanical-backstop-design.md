# Design note: mechanical pre-merge operator-authorization gate

- Status: DESIGN NOTE ONLY — no `AGENTS.md` / `templates/` edits, no behavior change,
  in the PR that carries this note. Implementation is a separate PR and ships the
  script **dormant / opt-in** (pattern of `tools/triage_status.py`, #281).
- Author: `miso` (coordinator, session 29), 2026-09-04.
- Source of truth: `work/coordination/FRICTION_LOG.md` entry
  **"2026-09-03 — coordinator merge marks treated as merge authorization (recurrence)"**;
  `AGENTS.md` §"Merge authority (operator-adopted 2026-09-02)" (added by #266);
  memories `feedback_opcmd_hold_lost_to_retry_race`, `feedback_no_direct_main_push`;
  session handoffs 24 / 25 / 26 §3.
- Rule references: operator rule 13 (no machinery until repeated evidence), rule 20
  (a repeat failure earns a *mechanical* countermeasure, not another instruction),
  invariant 13 (actor-side gate tension — addressed in §5).
- Review: verification-only for this note; the impl PR gets a real independent review.

---

## 1. Problem

`gh pr merge` into `main` is authority-gated by **prose only**:

- #266 added `AGENTS.md` §"Merge authority": "`gh pr merge` is operator-only, or an
  explicitly designated coordinator seat."
- That is an *instruction*. It has now failed to stop a merge **twice**:
  - **Occurrence 1** (session 24, #270): the OPCMD merge retry loop merged #270 one
    turn *before* an operator HOLD landed — the retry raced an authority-ambiguous
    merge.
  - **Occurrence 2** (session 25): the #266 rule was already in place; a
    coordinator-mark-only merge was still queued because nothing mechanically checks
    that a *specific* operator authorization exists for the *specific* PR before the
    merge runs. The retry loop and the coordinator seat each read the prose as
    "already satisfied by my role" and proceeded.

The FRICTION_LOG entry is on the N=3 ladder: **UNVERIFIED, pass 1 of ≤3** (traj #21).
Passes #22 and #23 close it or it **auto-escalates to an operator escalation at #24**.
A working mechanical gate discharges it early and permanently.

Today `gule` (the merge-runner seat under "Mode A") runs a bare `gh pr merge` with the
operator approving in `gule`'s terminal window. There is no wrapper, no ledger, no
programmatic check that the approval maps to a real operator instruction naming the PR.

## 2. Goal / non-goals

**Goal:** a merge-runner cannot execute `gh pr merge <N>` unless it can point to a
concrete, external, operator-authored authorization that names PR `<N>` (or designates
the runner as merge seat for the batch). "External" = an hcom message id from an
operator-authority sender — not the runner's own reasoning, not a coordinator mark.

**Non-goals:**
- Not a branch-protection / server-side change (that is `main`'s STRICT setting; this
  gate is about *who may invoke the merge*, not *what may land*).
- Not a replacement for review-evidence (`check_review_evidence.py`) or CI gates —
  it is an *additional* pre-condition, checked last, just before `gh pr merge`.
- Not automation of the merge decision — the operator still authorizes; the gate only
  refuses to proceed without a quotable authorization.

## 3. Design

### 3.1 A wrapper the runner MUST call instead of bare `gh pr merge`

`scripts/opcmd_merge.py` (name TBD — `opcmd` matches the seat). Signature:

```
python scripts/opcmd_merge.py --pr <N> --authz <hcom_message_id> [--dry-run] [--merge-arg ...]
```

Steps, in order, each a hard stop on failure:

1. **Resolve the authz message.** `hcom events --sql "id=<id>" --type message` (or the
   equivalent read API). Fail if not found.
2. **Sender check.** The message `from` must be an operator-authority identity. The
   allowlist is a small config constant (`OPERATOR_IDENTITIES = {"bigboss", ...}`),
   seeded from the same source `hcom`'s own "Authority: Prioritize @bigboss" uses.
   Fail if `from` is any agent seat (coordinator marks are structurally excluded —
   a coordinator is never in the allowlist).
3. **Scope check.** The message text must either (a) contain the token `#<N>` or a
   bare `<N>` in a merge-intent context, or (b) explicitly designate the caller as
   merge seat for a batch (`"merge the queue"`, `"you are the merge seat"`) AND be
   dated within the current session window (staleness bound, e.g. 12h). Fail closed
   on ambiguity.
   - **3b. Authz-message negation check** (added after PR #287 review finding F1).
     Presence of `#<N>` is not the same as *authorization* of `<N>`. The authz
     message itself is scanned for `"don't merge #<N>"` (PR-specific) and for
     standalone HOLD/STOP/abort tokens; either voids the message as an
     authorization. A PR-specific prohibition of `#<N>` does **not** void the
     message for a *different* PR it authorizes in the same breath
     (`"merge #40 now, do not merge #42"` still authorizes `#40`).
4. **Freshness / HOLD check.** Re-scan messages *after* the authz message for a HOLD /
   STOP / "don't merge #<N>" from any operator-authority identity. If found, refuse.
   (This directly closes Occurrence 1 — the retry-races-a-HOLD case.)
5. **Ledger append.** Append `{ts, pr, authz_id, authz_from, authz_excerpt, caller,
   head_sha}` to an append-only `work/coordination/merge-ledger.jsonl` (or emit to
   stdout for the runner to post in-channel — see §4). This is the "quote the operator
   authorization in-channel" step, made mechanical.
6. **Merge.** Only now: `gh pr merge <N> --squash` (pass-through of `--merge-arg`).
   On `--dry-run`, stop before this step and print what would run.

### 3.2 What "designated coordinator seat" becomes

#266's "or an explicitly designated coordinator seat" clause is the softest part of the
prose — it is what both failures leaned on. Under this gate the *only* way a non-operator
merge is legitimate is step 3(b): an operator message that explicitly designates the
seat, logged in the ledger. The seat's own claim to be "the designated coordinator" is
never sufficient. Recommend the impl PR also proposes tightening the `AGENTS.md` clause
to point at the gate — **but that wording is an operator decision** (see §6), so the
impl PR ships the script and leaves `AGENTS.md` for a follow-up operator-adopted change.

## 4. Delivery of the authz quote

Two options; recommend **A**:

- **A (ledger file).** Script appends to `work/coordination/merge-ledger.jsonl`. This file
  is **`.gitignore`d** — it is a local runtime log, never committed. It gives the runner's
  own machine a machine-readable local history; it is **not** the cross-clone audit trail.
- **B (in-channel only).** Script prints the quote block; runner pastes it into hcom
  before reporting the merge.

The impl ships **both halves of A**: it writes the local ledger *and* prints the same
JSON line (with `authz_id` + excerpt) to stdout for the runner to paste into hcom. Because
the ledger is `.gitignore`d, **the durable audit trail a trajectory pass reads from a fresh
clone is the hcom transcript** (the pasted stdout block), not a committed file — the exact
observation condition the FRICTION_LOG entry names. A future CI-side `merge-authz.yml`
(§5) would be the committed-artifact audit if one is ever wanted.

## 5. Invariant-13 tension (actor-side gate)

The gate lives in the runner's own pre-merge step — the actor polices its own authority,
which invariant 13 flags as weaker than an independent gate. Why this is acceptable here:

- The **authorization source is external** to the runner (an operator-authored hcom
  message the runner cannot forge — `hcom` message provenance is host-written).
- The check is **mechanical and fail-closed**: no judgment call the runner can rationalize
  past, unlike the prose rule.
- A truly independent gate would be server-side branch protection keyed to an operator
  identity — not available on this repo's GitHub plan for the "who invoked" question.
- The stdout authz block the runner pastes into hcom (§4) makes every merge
  **retroactively auditable** by an independent party (the trajectory pass) from the
  transcript alone, which restores most of the independence invariant 13 wants. (The
  `.gitignore`d local ledger is a convenience copy, not the audit trail.)

This is the same shape as `check_review_evidence.py` (an actor-side check that CI then
re-runs independently via `review-evidence.yml`). Follow-up worth considering if the gate
itself is ever bypassed: a `merge-authz.yml` CI-side post-merge audit that fails the next
build if the last merge has no ledger entry.

## 6. Operator decisions required before the gate becomes mandatory

1. **Approve the wrapper as the required merge path** for the `gule` / OPCMD seat
   (script ships dormant regardless; this makes calling it mandatory).
2. **Confirm the operator-identity allowlist** (§3.1 step 2) — who counts.
3. **`AGENTS.md` §"Merge authority" rewording** to point at the gate and drop / tighten
   the "designated coordinator seat" clause (§3.2). Operator owns this wording.
4. Ledger vs in-channel-only (§4) — recommend ledger.

The impl PR does **not** need these answered — it ships `scripts/opcmd_merge.py` +
tests, dormant. Making it mandatory + the `AGENTS.md` change is a follow-up.

## 7. Implementation scope (for the impl dispatch)

- **MAY touch:** `scripts/opcmd_merge.py` (new), `tests/test_opcmd_merge.py` (new),
  `.gitignore` (add `work/coordination/merge-ledger.jsonl` if option A).
- **MUST NOT touch:** `AGENTS.md`, `templates/`, `playbook/`, any existing script,
  `check_review_evidence.py`, CI workflows.
- **Acceptance:** `--dry-run` with a valid authz message prints the merge command and
  the authz quote and exits 0; with a coordinator-seat `from`, exits non-zero and does
  not print a merge command; with a post-authz HOLD message present, exits non-zero;
  with `#<N>` absent from the authz text and no batch designation, exits non-zero.
  Unit tests cover all four. No network in tests (mock the hcom read).
- **Verify:** `python -m unittest discover -s tests` green as a blocking foreground run
  (CI `test` is the authoritative gate; do NOT background-and-wait, no `Monitor` on it).

## 8. Resume prompt

You are implementing the mechanical pre-merge operator-authorization gate from
`work/notes/2026-09-04-merge-auth-mechanical-backstop-design.md`. Read that note in
full (esp. §3, §7). Fresh-clone `BigCatMellow/MAPS_Lean` to a unique `/tmp/<tag>-$$/`
path — never touch `~/Projects/MAPS_Lean` or `.claude/worktrees/`. Branch off current
`origin/main`. Add `scripts/opcmd_merge.py` + `tests/test_opcmd_merge.py` implementing
§3.1 steps 1–6 with the §7 acceptance behavior; ship it dormant (nothing calls it yet).
Do NOT edit `AGENTS.md`, `templates/`, `playbook/`, CI, or any existing file except
`.gitignore` (option A ledger path). Run `python -m unittest discover -s tests` as a
blocking foreground call — do NOT background it, do NOT put a `Monitor` on it. Open a
PR, post the head SHA + CI status to hcom, request independent review (two-phase:
findings to hcom first, no evidence push; fix; reviewer rebinds evidence at final head).
Stop and report if the hcom read API shape is unclear — do not guess it.
