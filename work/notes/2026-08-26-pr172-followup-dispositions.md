# PR #172 non-blocking finding dispositions

Source: [PR #172](https://github.com/BigCatMellow/MAPS_Lean/pull/172) and its
accepted independent review evidence.

Purpose: preserve the accepted F3-F8 findings outside merged-PR prose **without
turning every review comment into an active task**. This note grants no task or
implementation authority.

| Finding | Disposition | Why preserved | Revisit trigger |
| --- | --- | --- | --- |
| F3 — make the stored spec-hash check unconditional | `TEST / DEFERRED` | Real robustness question, but current production runs have no run-bound environment-evidence writer, so the path is not yet evidence-fed. | Before/when the first production writer of run-bound environment evidence lands, or when the Proof Phase exercises the real evidence-fed path. |
| F4 — narrow the documented validator return type to `dict` | `DEFERRED` | Contract/doc precision; not a demonstrated correctness failure. | Touch the validator interface for another justified change, or observe misuse caused by the broader wording. |
| F5 — end-to-end CLI test with `--repo-root` plus run-bound evidence | `TEST` | Directly tests the currently unproven boundary between production invocation and real evidence input. | Fold into the external Proof Phase / first real evidence-fed recovery exercise. |
| F6 — rename a test whose name overstates its fixture | `DEFERRED` | Naming debt only; changing it now would create maintenance churn without outcome value. | Rename when that test/file is next changed for substantive reasons. |
| F7 — mechanically enforce the `runtime.state` before `runtime.environment` import-order constraint | `WATCH` | The current comment documents a real import/cycle sensitivity, but another guard is not justified without recurrence. | Promote only if the ordering is accidentally broken/reintroduced or a second caller makes the boundary fragile. |
| F8 — promote `_default_executor` to a public export | `DEFERRED` | Premature API expansion while there is only one justified production composition. | Revisit when a second legitimate caller needs the executor or private import friction becomes real. |

## Relationship to current work

- [Recovery/validation implementation design](2026-08-25-rns-validation-tier-hookin-design.md)
- [Current handoff](../handoffs/2026-08-26-project-reconciliation-and-proof-phase.md)
- [Roadmap trajectory check](../../playbook/ROADMAP_TRAJECTORY_CHECK.md)

These findings are intentionally **not** new roadmap rows. If a revisit trigger
fires and the issue changes outcomes, shape the smallest bounded task then.
