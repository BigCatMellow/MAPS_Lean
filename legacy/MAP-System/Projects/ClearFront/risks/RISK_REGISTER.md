<!-- hpom: file: risks/RISK_REGISTER.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: independent process audit, clearfront-independent-delivery-audit-2026-07-17.md -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Risk Register — ClearFront

Template: `MAP_System/templates/RISK_REGISTER_TEMPLATE.md`

# Risk Register Entry

Entries below follow the template's field set; both are closed as
MITIGATED as of 2026-07-17 (phase-end review following the independent
delivery audit).

## RISK-CF-0001

Risk ID: RISK-CF-0001
Project: ClearFront
Class: PROCESS
Severity: BLOCKING
Owner: claude-lab-gome
Date opened: 2026-07-16
Last reviewed: 2026-07-17
Status: MITIGATED

### Description

A mechanical split of the currently monolithic embedded script could
change order-dependent behavior (global/IIFE-scoped state, event wiring
order, DOMContentLoaded timing) even when each extracted piece looks
correct in isolation.

### Trigger / likelihood

Likely if decomposition tasks move code between files without a parity
check against the extracted baseline. Moderate likelihood given the
single-file prototype almost certainly relies on script execution order.

### Blast radius if realized

Silent gameplay bugs (wrong turn order, combat miscalculation, state
desync) that are hard to notice without active playtesting, undermining
the "readable rules" design principle itself.

### Current mitigation

Baseline extraction is tracked as its own task with a required smoke
test before any decomposition begins (TASK-207). Decomposition tasks
will require a parity check per `shared/requirements.md`.

### Escalation

- [ ] SECURITY or STRUCTURAL — escalated to command-center: N/A
- [x] BLOCKING, core-agent-mitigable — handled directly, logged above
- [ ] DRIFT/COSMETIC — tracked, no escalation required

### Review history

| Date | Reviewed by | Notes |
|---|---|---|
| 2026-07-16 | claude-lab-gome | Opened during bootstrap, from Lilo's intake risk notes |
| 2026-07-17 | claude-lab-gome | MITIGATED: the parity gate (byte-identical screenshot + deterministic seeded CDP replay + undo regression) was applied and passed on every decomposition slice (TASK-207/208/212/214/215/216/217), including two rounds that caught and disclosed real order-dependent defects before release (TASK-214's missed `renderCombatReport` forwarding, TASK-215's four live-only bugs). The independent process audit (`artifacts/reviews/clearfront-independent-delivery-audit-2026-07-17.md`) confirms this evidence is credible for behavior-preserving refactor but correctly notes it is a smoke-test oracle, not full rule-engine coverage — that gap is tracked as a distinct follow-up (rule/effect test matrix), not this risk, which was specifically about order-dependent extraction defects. |

---

## RISK-CF-0002

Risk ID: RISK-CF-0002
Project: ClearFront
Class: DATA
Severity: DRIFT
Owner: claude-lab-gome
Date opened: 2026-07-16
Last reviewed: 2026-07-17
Status: MITIGATED

### Description

The generated bundle may embed third-party or binary resources (fonts,
libraries) whose provenance/license is not obvious from the bundle
alone. Reproducible extraction could silently drop or mis-attribute
these if not enumerated carefully.

### Trigger / likelihood

Occurs during bundle extraction (TASK-207) if the manifest is not fully
enumerated and cross-checked against the rendered output.

### Blast radius if realized

Missing assets in the extracted baseline, or an untracked third-party
dependency shipped without attribution.

### Current mitigation

Extraction script will enumerate every manifest entry and every
`__bundler/ext_resources` entry and report counts; smoke test compares
rendered output to the original bundle.

### Escalation

- [ ] SECURITY or STRUCTURAL — escalated to command-center: N/A
- [ ] BLOCKING, core-agent-mitigable — handled directly, logged below
- [x] DRIFT/COSMETIC — tracked, no escalation required

### Review history

| Date | Reviewed by | Notes |
|---|---|---|
| 2026-07-16 | claude-lab-gome | Opened during bootstrap |
| 2026-07-17 | claude-lab-gome | MITIGATED: TASK-207's extractor enumerated all 6 manifest entries and 6 `ext_resources` against the real bundle with zero silent drops (independently reproduced by reviewer); no third-party/font/library resources were present in this bundle to begin with (manifest was 100% first-party PNG portraits). Closing as mitigated rather than "no longer applicable" since the extractor's enumeration behavior is the durable mitigation if a future bundle re-extraction ever does include such resources. |

---

## Acceptance (if Status: ACCEPTED)

Not applicable — no risk in this register is in ACCEPTED status. Both
entries are MITIGATED (see per-entry review history); this section
exists per the template's required structure.

## Notes

- Register format aligned to `RISK_REGISTER_TEMPLATE.md`'s required
  fragments on 2026-07-18 after `validate_risk_registers.py` (newer than
  this register's bootstrap) flagged the original layout. Content
  unchanged; structure only.
