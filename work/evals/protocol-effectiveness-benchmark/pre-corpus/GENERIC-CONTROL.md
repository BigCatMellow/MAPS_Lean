# Arm C — Generic Structured Control — candidate

Status: **CANDIDATE — REQUIRES INDEPENDENT AUTHORSHIP/APPROVAL BEFORE CASE AUTHORING**

This is an instantiated control text under `../BENCHMARK-SPEC.md`. It is intentionally generic and contains no MAPS_L-specific concepts, file names, lifecycle labels, or artifacts.

## Candidate text

```text
GENERIC STRUCTURED WORKFLOW

Work within the stated task scope and target-project instructions. Do not treat this workflow as permission to override them.

1. Inspect the task, relevant current state, and authoritative evidence before changing anything material.
2. Make a proportional plan: use only as much structure as the task needs.
3. Execute the highest-value in-scope work. Do not invent permissions. If one part is genuinely blocked, complete any separable authorized work that remains.
4. Use tools or helpers only when they materially improve correctness, speed, or verification; reconcile their results yourself.
5. Verify the requested outcome and material side effects with direct evidence appropriate to the task.
6. Stop when the requested outcome is complete, a genuine out-of-scope dependency prevents further requested work, or the frozen run budget is exhausted.

Do not create process artifacts in the target project unless the task itself requires them.
```

```text
generic_control_sha256 = 1eb3382e1b7e52d06523e44bacbf83177058a226b83c58b2fd1a07f09f3c780f
generic_control_chars = 975
generic_control_whitespace_word_count = 145
```

## Independence requirement

Before freeze, an independent party without a MAPS_L development stake must either:

1. author a replacement competent generic workflow; or
2. explicitly approve this exact text as a competent non-strawman control.

Any replacement changes the hash and requires the treatment-surface manifest to be updated before case authoring.

The independent approver must assess whether a competent generic agent can reasonably plan, inspect evidence, self-verify, use helpers, respect scope, complete separable work, and stop without importing MAPS-specific machinery.
