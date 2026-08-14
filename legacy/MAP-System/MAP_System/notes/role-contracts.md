# Stable role registry (TASK-280)

`workflow/role_registry.yaml` is the canonical registry for seven stable role
IDs: `shaper`, `scout`, `delivery-implementer`, `independent-reviewer`,
`state-steward`, `researcher`, and `escalation-analyst`. Each contract records
mission, ownership, permissions, obligations, prohibitions, required inputs and
outputs, escalation conditions, and its completion condition.

Task JSON keeps its original `role` string. `validate_task_schema.py` resolves a
stable ID directly or through the registry's explicit case-insensitive
compatibility aliases. An unknown value is rejected with a diagnostic; aliases
are read-time normalization and never rewrite historical task files. This lets
older free-form records load while requiring new work to use a registered ID
(or one of the deliberately enumerated legacy aliases during migration).

The runner adds routing-only `role_id` and `role_source` fields. It carries
`worker_id`, `provider`, `model_tier`, and `capability_requirements` as separate
fields; none is inferred from or substituted for another. A role expresses the
work contract, not an agent identity or model choice.

Role normalization does **not** enforce review independence. Independence is a
separate lifecycle invariant enforced by claims/review gates (the reviewer must
not be the delivery claimant/author). The `independent-reviewer` contract
describes that obligation and the tests assert that normalization alone cannot
turn an implementer into an independent reviewer.

Structural pre-dispatch approval for TASK-280 is evidenced by command-center
event `events.id=1717` (operator authorization for the remaining registered
roles-system roadmap). The implementation remains bounded to TASK-280's
registered output paths (see `MAP_System/tasks/TASK-280.json`), not to any
fixed count recorded here.
