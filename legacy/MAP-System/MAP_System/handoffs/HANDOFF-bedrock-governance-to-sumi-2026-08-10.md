# Bedrock Governance Packet for Sumi

Project working name: `MAP Bedrock`

Purpose: take ownership of the Bedrock operating structure so the MAP system runs with stable responsibility, durable logging, and clear triage even when agent names rotate.

Scope to own:

- Define a role-based responsibility charter that is not tied to session names.
- Define live role bindings plus the rotation-transfer rule.
- Create a canonical program ledger mapping `phase -> gate -> task -> role -> status -> blocker -> next`.
- Define the concise status protocol.
- Define task/event/E-I/triage logging and routing rules.
- Define checkpoint cadence and who is accountable at each checkpoint.
- Reconcile current Phase 0 gaps against the plan.
- Correct plan naming/status references to `MAP Bedrock` where appropriate.

Non-negotiable constraints:

- `Smalls` is sole write authority.
- No direct `Biggie` DB writes.
- Independent review required.
- No self-approval.
- Preserve evidence and durable records.
- Keep answers short.
- Stable structure first, people/session names only as temporary bindings.

Required operating structure:

- `Operator`: authorizes direction, releases, and escalations.
- `Program Coordinator`: owns cross-phase flow, checkpoint enforcement, routing, and drift control.
- `Phase Owner`: owns one phase gate and completion evidence.
- `Task Owner`: owns one task delivery.
- `Independent Reviewer`: verifies task without self-approval.
- `Security Reviewer`: handles security-sensitive review where needed.
- `Verifier`: reruns exact evidence path and confirms claims.
- `E/I Curator`: routes emergence/insight items into durable records.
- `Librarian`: keeps artifacts, handoffs, and references findable/current.

Rules for role binding:

- Roles are stable.
- Names are replaceable bindings.
- Every active role needs an explicit current binding or explicit vacancy.
- Every rotation must transfer open obligations, blockers, and evidence.
- No task should depend on one specific name staying active.

Required logging and triage behavior:

- Material work must land in durable MAP records, not only chat.
- Each checkpoint should capture: current gate, blocker, owner, evidence, next action.
- E/I items must be logged and either promoted, linked, or dispositioned.
- Triage must classify findings into: task, blocker, review item, decision, E/I, or deferred note.
- Unowned work and stale claims must be surfaced explicitly.

Current status to reconcile:

- `MAP Bedrock` is still effectively in `Phase 0`, not through the full gate.
- `TASK-321` released, but the broader Phase 0 exit evidence still needs reconciliation against the program plan.
- Prior discussion identified need for stable responsibility structure, concise answers, logging, E/I routing, and triage discipline.
- Plan text and live status may still need naming/status cleanup so the project is described consistently as `MAP Bedrock`.

Expected first action:

1. ACK ownership.
2. Claim or route the proper MAP task before edits.
3. Produce the governance structure in durable form.
4. Tie it back to the existing Bedrock plan and current Phase 0 reality.

Definition of done for this governance packet:

- Stable role model exists.
- Current live bindings/vacancies are explicit.
- Ledger format is defined.
- Logging/triage/checkpoint rules are defined.
- Phase 0 governance gaps are identified with owners and next actions.
- Bedrock can be run without relying on fixed agent names.
