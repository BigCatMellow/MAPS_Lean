# Biggie/Smalls Orchestration — Action Plan

- status: approved_direction_step1_in_progress (TASK-307 created 2026-07-29 for 1a; 1b intentionally not bundled into it)
- date: 2026-07-29
- decided_by: operator (direct chat, not hcom)
- drafted_by: claude-lab-nene
- references: `MAP_System/artifacts/planning/kudu-ruki-orchestration-plan-2026-07-28.md`
  (the underlying proposal; this file records the operator's decision on it
  plus the sequenced next steps — it does not replace the original doc)

## Naming convention

Going forward in conversation and in any new artifacts, use:

| Nickname | Machine | Identity | Role |
|---|---|---|---|
| **Biggie** | KUDU | `mellow@192.168.1.177` | Compute plane (GPU/Ollama, Codex implementation, read-only db mirror) |
| **Smalls** | RUKI | `home@192.168.1.153`, hostname `MediaCenter` | Control plane (writable `map.db`, task/review authority, coordination) |

This is a conversational/documentation convention only. **Not yet decided**:
whether to mechanically rename `KUDU`/`RUKI` references across existing
scripts, configs, and docs. Treat that as a separate, low-priority cleanup —
do not conflate it with the orchestration work below.

## Operator decision

Approved the overall direction of the 2026-07-28 orchestration proposal:
single writable database on Smalls, Biggie as compute/GPU plane, git as the
only source-of-truth sync mechanism, fail-closed sync (never auto-discard
local work), and the proposal's own non-goals list (no auto-booting the CCL,
no local-model review/approval authority, no dual writers).

**Not approved yet:** jumping straight to full execution of WP-2 through
WP-7. Two concrete blockers were identified in the same session this
decision was made, and must be resolved first — see steps 1–2 below.

## Action plan (sequenced)

Each step is unstarted as of this artifact's creation. Update this file's
`status` field and check items off as work proceeds in future sessions.

- [ ] **1. Fix two distinct gateway problems, previously conflated as one "bug."**
      All four incidents below shared the same opaque, empty-stderr
      `authority request failed (1)` symptom, which made them look like one
      bug. mebo's closer analysis (2026-07-29) separated the real causes —
      correcting an earlier version of this section that lumped them
      together:

      **1a. register-agent / rotation-transfer / rotation-restore fail
      because the code that implements them only exists on Biggie.**
      An earlier session (rotation-replacement-damo-nivo) wrote these
      operations into `MAP_System/db/claims.py`, `scripts/map_authority.py`,
      `scripts/context_rotation.py`, and `tests/test_context_rotation.py`
      to fix a real read-only-mirror-write bug, but the patch is
      uncommitted and was never reviewed or deployed to Smalls (RUKI). RUKI
      is the authority host these calls route to — it simply doesn't have
      this code. Evidence: claude-lab-nene's context-rotation
      `register-agent` call (this session, ~05:22Z; see
      `MAP_System/handoffs/STATE_SNAPSHOT-rotation-replacement-damo-nivo-20260729T045157Z.yaml`
      for the patch's own account of leaving it uncommitted pending
      security review).

      **1b. `task approve` fails because RUKI can't read a KUDU-only review
      file, not because of a code gap.** `validate_review.py` runs on RUKI
      and needs to read the `--review-record` path; review artifacts
      written on Biggie under `MAP_System/artifacts/reviews/` are never
      synced there. Evidence: claude-lab-nene's `task approve TASK-305`
      call (~14:33Z) and claude-lab-muza's `task approve TASK-306` call
      (tried twice, did not force a workaround) — both real, both this
      cause, per codex-lab-replacement-valo's original read-only-inspection
      diagnosis and mebo's confirmation.

      **Not actually a bug:** `task add-output-path` — nene's first attempt
      failed only because of missing `--path`/`--actor` flags; corrected
      syntax succeeded every time after (4/4). Removed from this count.

      **Net effect:** TASK-305 and TASK-306 both got durably recorded
      reviewer verdicts that couldn't land as canonical task status because
      of (1a)/(1b) — actively stalling two already-reviewed tasks, not a
      hypothetical future blocker. Escalated to bigboss 2026-07-29; decision
      (2026-07-29): prioritize 1a via a dedicated task (below), leave 1b
      (artifact transport) explicitly out of that task's scope — different
      problem, not to be bundled in. No manual TASK-305/306 transitions, no
      direct SQL, no deploy-before-review, for either sub-problem.

      Follow-up task for 1a: **TASK-307** (see its own record) — revalidate
      the damo-nivo patch, independent functional + explicit security
      review, checksum-staged deploy to Smalls, verify register-agent/
      rotation calls actually succeed after deployment.
      already built register-agent/rotation-transfer/rotation-restore gateway
      operations to fix a related read-only-mirror write bug, but left them
      **untracked and uncommitted** pending independent security review. Check
      whether this same failure is inside that uncommitted patch before
      re-implementing.

- [ ] **2. Rotate the Smalls (RUKI) account password.**
      Flagged in the original plan (section 9, last bullet) as previously
      exposed in setup transcript history. Outstanding security debt,
      independent of the rest of this plan. Do this regardless of sequencing
      below.

- [ ] **3. Promote WP-1 (architecture decision) as a real MAP task.**
      Deliver exactly what the original plan's WP-1 specifies: an approved
      MAP decision naming Biggie/Smalls roles, machine-readable host-role
      config, authority/failover boundaries, and an explicit statement that
      Git source authority and SQLite state authority are different things.
      Route for independent review per this repo's no-self-review rule
      before treating it as decided.

- [ ] **4. WP-2 — Git-based source convergence.** Only after WP-1 is
      approved. Desired-revision manifest, clean-tree-safe fetch/check/
      activate tool, rollback without deleting local work. No live-tree
      `rsync` as the normal path.

- [ ] **5. WP-3 — Cross-host health supervisor.** After WP-2. Deterministic
      health schema (host/role/ssh/hcom/map_authority/source_revision/
      services/gpu/ollama/last_success/active_incident), incident dedup,
      boot-safe systemd units on both machines.

- [ ] **6. WP-4 — Capability-aware router.** After WP-3. Routing rules by
      task tier/authority/compute need/health; architecture and authority
      work must never route to a local model; GPU work prefers Biggie;
      database lifecycle operations always execute on Smalls.

- [ ] **7. WP-5 — Biggie bounded-job lane: OPEN QUESTION, not committed.**
      The original plan's own review checklist (section 14.3) already asks
      whether this is necessary versus just using task branches plus visible
      agents. Revisit that question explicitly before building it — this is
      the highest-risk item (new network-facing, write-adjacent surface) and
      should not be assumed as a deliverable just because it's numbered.

- [ ] **8. WP-6 — Unified CCL cross-host surface.** After WP-4 (and WP-5 if
      built). Operator-visible host role, connectivity, revision, services,
      GPU/Ollama, incidents, job status; retry/cancel/inspect controls.

- [ ] **9. WP-7 — Failover and recovery runbook.** After WP-2, WP-3, and
      (if built) WP-5. Outage procedures for both machines, database
      restoration, deliberate authority-transfer procedure preserving the
      one-writer invariant, source rollback/divergence reconciliation.
      Prove via tabletop and live drills.

## Orchestrator role

Operator asked this session (claude-lab-nene) to act as orchestrator for
this sequence. In practice that means: drive step 3 onward through MAP's
normal task-creation/routing/review process and coordinate with whichever
agents are live on Smalls via hcom — not hand-editing SSH/systemd/authority
config directly from a chat session. Steps 1–2 are plain bug-fix/security
hygiene work and can be picked up directly without a new task record.

## Resume note

Nothing below step 0 has been started. A future session picking this up
should: read this file, check whether steps 1–2 are already done (`git log`
on `MAP_System/scripts/map_authority.py` /
`MAP_System/scripts/context_rotation.py`, and ask the operator whether the
Smalls password rotation happened), then continue from the first unchecked
step.
