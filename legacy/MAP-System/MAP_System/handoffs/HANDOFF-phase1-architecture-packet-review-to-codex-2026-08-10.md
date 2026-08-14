# Phase 1 Architecture Decision Packet — Review Request to Codex

From: claude-lab-sumi (Program Coordinator, MAP Bedrock, per DEC-042)
To: Codex (any live core Codex identity — see `hcom list`)
Date: 2026-08-10

Purpose: independent review of the P1.1 architecture decision packet,
per `map-2-research-adoption-implementation-program-2026-08-09.md`
§8's own routing ("Recommended owner: Claude architecture lead.
Reviewer: Codex.").

Document to review:
`MAP_System/artifacts/planning/phase1-architecture-decision-packet-2026-08-10.md`

What it decides: the ten P1.1 points (authority seam, projection
contract, event model, identity/version semantics, operator-approval
object semantics, compatibility/rollback, per-project namespace) plus
the exit-gate's required threat-model coverage (spoofing, stale
version, duplicate retries, post-commit response loss, partial
projection, cross-host replay, malformed request, approval
substitution).

## What to check

- Does each of the ten decisions actually follow from the current
  system (`map_authority.py`'s `ALLOWED_TASK_VERBS`, `MIRROR_FILES`,
  the live `map.db` schema — `tasks`, `events`, `approval_gates` have
  no version/idempotency/dedup columns today), or does it assume
  something not actually true?
- §6 (authenticated server context supplies actor identity) is flagged
  as the packet's own highest-priority open gap — actor identity today
  is a client-supplied `--actor` string, not server-authenticated.
  Confirm this reading is accurate and that the proposed fix direction
  (defer the actual fix to the Phase 2 command layer, but name the gap
  now) is the right sequencing, not premature deferral of something
  that should block Phase 1 itself.
- Threat-model coverage: is any of the eight required categories
  covered by hand-waving rather than a real mechanism?
- P1.2 (schema/command contract — your own owned deliverable next)
  needs a stable target from this packet. Flag anything in the ten
  decisions that would make P1.2 harder or ambiguous to design against.
- Independence: this packet was authored by claude-lab-sumi (program
  coordinator + architecture lead per this task's own recommended
  routing) — per DEC-039/DEC-042's "does not own every implementation
  or approve own deliverables" rule, this review must come from you,
  not be rubber-stamped back.

## How to respond

Write an independent review record (durable, e.g.
`MAP_System/artifacts/reviews/phase1-architecture-packet-review-<your-name>.md`)
with a clear verdict: approve as-is, approve with named changes, or
reject with reasons. Report back to claude-lab-sumi via hcom or by
editing this handoff's own status line below once done.

Once approved, the next step is D1: operator approval tied to this
packet's exact sha256 hash (computed once the packet is finalized,
including any changes from this review).

## Status

- [ ] Codex review complete (fill in reviewer name + verdict here)
