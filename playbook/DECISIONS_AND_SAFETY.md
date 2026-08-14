# Decisions, Permissions, and Safety

Capability, assignment, ownership, authority, and approval are different.
An agent may be able to perform an action without being authorized to decide
that it should happen.

## Decision classes

Record a decision before acting when it changes product intent, scope,
architecture, security, external behavior, cost, data handling, or a standing
project rule. A decision record captures the options, rationale, owner, date,
consequences, and any superseded prior decision.

Escalate to the operator when a choice depends on user preference, priority,
irreversible external impact, broad scope, privacy, spending, publication, or
destructive action. A core owner may make bounded implementation choices that
do not cross those boundaries.

## Destructive actions

Before deleting, overwriting, resetting, force-pushing, bulk-changing data, or
performing an equivalently hard-to-reverse action:

1. identify the exact target and impact;
2. offer a safer reversible alternative when practical;
3. obtain explicit confirmation for the actual action; and
4. record the result and recovery path if material.

Never treat a broad request as permission for an irreversible action whose
targets have not been resolved.

## Security and external boundaries

- Keep credentials and secrets out of chat, logs, commits, screenshots, and
  agent prompts where possible.
- Treat network calls, external services, publication, permission changes, and
  data movement as explicit boundaries.
- Apply least privilege: agents/helpers receive only the access and scope they
  need.
- Security-sensitive output requires high-risk verification and independent
  review; uncertainty is an escalation signal, not a reason to guess.

