# Operator asks — MAPS_Lean session 13 (`niko`), 2026-08-31

---

## SESSION 17 (`luve`), 2026-09-01 — OPERATOR ANSWERED

The operator was given the trajectory-check-#16 §3b decision batch (Ask #1, the
`flow release-check` batch, SEC4 B1 trust-root, Ask #2, Ask #3) with a
recommended answer per item and instructed: **"Go ahead and do all those
things."** The recommended answers are therefore **accepted**. Recorded here as
the canonical answer; the coordinator dispatches the now-unblocked impl work.

### Ask #1 — first enforced `--enforce-canonical-run` pass — **AUTHORIZED**

One enforced pass is authorized. **Target/timing still to be pinned with the
operator by the coordinator** — the obvious candidate is the MAPS_Lean checkout
itself (`--repo-root ~/Projects/MAPS_Lean`), which is where the control plane
already runs. Expect `LEASE_EXPIRED` denials on first run; remediate per
`docs/CONTROL_PLANE_SETUP.md` §5 (claim-recovery under the manifest's original
worker id). The coordinator runs the operator workflow — no impl/review agent
runs `maps recovery-tick --enforce-canonical-run` autonomously. Unblocks
**6.4 / 6.5 / 6.16 / 6.22 + H5 / E4 / L6** (verify each hard before any status
flip).

### `flow release-check` batch (#234 §6) — **RECOMMENDED ANSWERS ACCEPTED**

1. **Summary sink** → a new append-only `release_checks` table keyed by
   `(task_id, review_id)` (acquisition report ref + smoke report ref +
   composite state + optional operator-ack ref). This is a **`schema.sql`
   change** — the impl slice carries it.
2. **Evaluator report persistence** → persist the `report_ref` of
   `evaluate_acquisition_evidence` / `evaluate_benchmark_results` plus the input
   evidence refs in the `release_checks` row.
3. **`composite == BLOCKED`** → **advisory** to start (the reviewer sees
   `BLOCKED` and chooses the verdict). The approval-blocking variant (3b) is a
   later hardening slice with its own callout — not this one.
4. **Who may run `flow release-check`** → any of the releasing party / reviewer
   / operator (it records no verdict; low-authority while advisory-only).

### SEC4 B1 — `authorized_operators` trust root — **RECOMMENDED ANSWERS ACCEPTED**

- Keep the structural `--actor` / `decided_by` field; add an **opt-in** real
  identity check at exactly one site, **default off**.
- A repo with **no `authorized_operators` rows** → identity checks are
  effectively disabled (fail-open on absence, so the default-off path needs no
  bootstrap to function).
- Bootstrap (genesis operator) → a `maps init`-time step (Q B2) — the first
  `authorized_operators` row is written at init when the check is opted in;
  scope a separate opt-in `maps operator add` for later rows.
- Unblocks **SEC4 Half 3**.

### Ask #2 — env-evidence-writer authority ratification — **YES**

Accepted: *"a task's `environment` contract is sufficient operator authority for
that task's runs to become quick-tier-executable under an explicit
`--repo-root`"* — same authority class as `spec_ref` / `max_age_seconds` /
`required_for_routing`. No runtime change; the Q4 `--trusted-evidence-recorder`
fallback slice is **not** needed.

### Ask #3 / Infra #1 — kill zombie pid 3874 — **DONE**

Operator ran `kill 3874` (session 17). Confirmed dead (`ps -p 3874` → gone).
It was a session-8 `claude` orphan, ~1d 17h CPU, PPID 3868, running a stale
session-8 orchestration prompt (referenced long-merged PRs #173/#174/#178/#179).
Its 4 worktree locks (`agent-a633de15fc2a5afd0` / `agent-ab5f53cc65eae08e5` /
`agent-abbdc8e8498cbe3a8` / `agent-ace9b0d006a4789c9`) are now safe to release
as part of Infra #2.

### Infra #2 / #3 — worktree + stale-branch cleanup — still pending the operator

Not in the answered batch. Infra #2 (44 classifier-blocked `git worktree remove`
/ `git branch -D`) and Infra #3 (5 stale remote branches) remain: either add a
Bash permission rule, or the operator runs the audited `remove.sh` /
`gh api -X DELETE` set.

---

## SESSION 16 (`rozo`), 2026-09-01 — still-open + infra asks

- **Ask #1** (first `--enforce-canonical-run` pass) — STILL OPEN. 3rd session
  flagged. 6.4/6.5/6.16/6.22/H5/E4 parked until answered. Roadmap moving on
  independent work (SEC4 manifest, 6.21, 6.9/S6 dispatched this session).
- **Ask #2** (env-evidence-writer authority ratification) — STILL OPEN, not a
  blocker. Recommended answer: yes.
- **Infra #1 — kill zombie pid 3874.** Verified alive, elapsed 1d 00:32h,
  session-8 detached orphan, invisible to hcom, holds 4 merged-worktree locks.
  Safe to `kill 3874`. Coordinator will not kill unilaterally.
- **Infra #2 — worktree cleanup Bash permission.** 44 safe `git worktree remove`
  + `git branch -D` pending; autoMode-classifier-blocked. Need a permission rule
  or operator runs the audited remove.sh (session-15 scratchpad).
- **Infra #3 — 5 stale remote branches** on origin (audit rows 24/33/39/47/48) —
  separate `gh api -X DELETE` go/no-go.

---


Two decisions are genuinely operator-only. Nothing is enabled/changed until you
answer. Both are low-urgency — the roadmap keeps moving without them, but they
are the next real unblock.

---

## RE-SURFACED — session 15 (`mono`), 2026-09-01, after trajectory check #12 (PR #214)

**Ask #1 is now the single highest-leverage item on the board, flagged by TWO
consecutive trajectory checks (#11 and #12).** Sharper framing:

> **6.4, 6.5, 6.16, 6.22 — and H5, E4 — are code-complete for their next
> milestone and blocked only on one decision.** Every guard is merged and
> composed into `build_canonical_harness_service`. None needs more design or
> code (#211 was the last piece — the SEC3 readiness-layer reauth rule). They
> need one operator action: authorize (or decline) a single
> `maps recovery-tick --enforce-canonical-run --repo-root <checkout>` pass
> against one named project, once. Expected first-run effect: some currently-
> working resumes become `resume_denied` (most likely `LEASE_EXPIRED`),
> remediated per `docs/CONTROL_PLANE_SETUP.md` §5. Until this happens, 4–6
> roadmap rows cannot advance regardless of any other work.

Trajectory check #12 REPRIORITIZED away from this cluster: sessions are now
dispatched on SEC4 capability-declaration manifest, 6.21 review lifecycle ops,
and L6 harness-config-hash persistence — all independent of both asks. So the
roadmap keeps moving, but 6.4/6.5/6.16/6.22 are parked until you answer #1.

**Answer options for #1:** (a) "go — run it against <project>, <when>"; (b) "not
yet, keep building the default-off surface" (note: per check #12 there is no
more surface to build for these 4 rows — this option = park them indefinitely);
(c) "decline enforced exposure entirely" (would trigger a CUT SCOPE pass).

Full analysis: `work/notes/2026-09-01-roadmap-trajectory-check-12.md` §5.

## 1. First enforced `--enforce-canonical-run` / `--enforce-validation` pass on a real project

**This is the single biggest lever right now.** Four checklist rows (6.4, 6.5,
6.16, H5) plus E4 close only on first real production exposure of an *enforced*
pass. Three guards are composed default-off in `build_canonical_harness_service`
today with no/partial production callers:
- canonical-run guard (#180 / #185)
- destructive-action guard (#194)
- memory-provenance guard (#202, this session)

`docs/CONTROL_PLANE_SETUP.md` §5 has the operator workflow. Expect
`LEASE_EXPIRED` denials on first run; remediate with claim-recovery under the
manifest's original worker id.

**What I need:** your go-ahead to run one enforced pass against a real project
(which one; when), OR a "not yet, keep building the default-off surface".
I will not enable this autonomously.

**Trajectory check #11 (PR #209) escalation:** 6.4, 6.5, 6.16, 6.22 are now ALL
single-threaded through this one decision — their enforcement code is merged and
composed into the same `build_canonical_harness_service` root, all default-off,
none exposed. If this decision stays open, trajectory check #12 will treat "4
roadmap items blocked on 1 ungiven decision" as a REPRIORITIZE trigger.

## 2. Ratify the env-evidence-writer authority framing (#207, merged)

#204 made `maps flow start` a production writer of `run_environment_evidence`
for environment-contracted tasks. Independent review (pogo authored, tutu
confirmed against code) concluded **posture did not regress** — the
`recovery-tick --repo-root` operator gate is intact, executed commands are the
operator's own checked-in hash-pinned spec, an attacker who could influence the
spec already has checkout control. Full argument:
`work/notes/2026-08-31-env-evidence-writer-authority-redecision-design.md`.

The note leaves one thing for you to record acceptance of (ratification, not a
blocker): **"a task's `environment` contract is sufficient operator authority
for that task's runs to become quick-tier-executable under an explicit
`--repo-root`."** Same authority class as `spec_ref` / `max_age_seconds` /
`required_for_routing`. Recommended answer: **yes**. If you decline, the
fallback is to build the Q4 slice (opt-in `--trusted-evidence-recorder`
allowlist defaulting to exclude `maps-flow-start`) — no flow-start runtime
change either way.

---

## Session 13 status (context, not an ask)

6 PRs merged: #202 (6.22 MemoryProvenanceGuard slice 1), #203 (SEC4
operator-transitions + Half 3 design), #204 (6.24 env-report production
source/cache slice 1), #205 (SEC4/6.10 `maps skill` CLI — first real
`record_skill_lifecycle_transition` caller), #206 (6.24 test-hardening), #207
(authority re-decision). Trajectory check #11 dispatched. Next queued: SEC4 B1
(operator-identity registry — blocked on an OPERATOR DECISION callout in the
#203 note), #194 residual.
