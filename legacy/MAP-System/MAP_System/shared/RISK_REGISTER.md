<!-- hpom: file: shared/RISK_REGISTER.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-03 -->
<!-- hpom: verified_against: TASK-120 self-application health check -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# MAP-System Risk Register

Canonical MAP-system-level risk register per `RISK_SYSTEM.md`. Use
`templates/RISK_REGISTER_TEMPLATE.md` to add further entries.
Project-level risk registers live under
`Projects/{project-name}/risks/RISK_REGISTER.md`.

# Risk Register Entry

Risk ID: RISK-0001
Project: MAP_System
Class: PROCESS
Severity: DRIFT
Owner: command-center
Date opened: 2026-07-03
Last reviewed: 2026-07-03
Status: MITIGATED

## Description

Concurrent core agents building cross-linked prose systems (each adding a
`DEC-NNN` entry and cross-link backlinks) can register overlapping
`output_paths` on `shared/decisions.md`, `shared/current-state.md`, and
other agents' system files, tripping `validate_task_graph.py`'s output
path collision check while both tasks are still active.

## Trigger / likelihood

Observed directly during the TASK-103 through TASK-118 gap-review build
sequence: collisions occurred between TASK-107/TASK-108 and recurred as a
near-miss pattern (caught pre-submission) across TASK-111, TASK-112,
TASK-115, and TASK-117. Likely any time two or more agents build
cross-linked MAP-system documentation concurrently.

## Blast radius if realized

Low by itself — `validate_task_graph.py` catches it before release, so it
blocks a `run_tests.sh` pass rather than causing silent data loss. The
real cost is coordination overhead (rework/resubmit cycles) if not
managed.

## Current mitigation

- Explicit `depends_on` between sequentially-built tasks that share
  `shared/decisions.md`/`shared/current-state.md`.
- Registering all touched output_paths (including one-line cross-link
  backlinks) before submission — now stated explicitly in
  `notes/task-authoring-guide.md` per RETRO-0001 (`RETROSPECTIVE_SYSTEM.md`,
  TASK-118).
- Holding shared-file edits until the prior dependency task is RELEASED.

## Escalation

- [ ] SECURITY or STRUCTURAL — escalated to command-center: N/A, not this class/severity
- [x] BLOCKING, core-agent-mitigable — handled directly, logged below
- [ ] DRIFT/COSMETIC — tracked, no escalation required

## Acceptance (if Status: ACCEPTED)

- Decision class (per `DECISION_CLASSES.md`): N/A — mitigated, not accepted
- Approved by: N/A
- Linked decision: NONE

## Review history

| Date | Reviewed by | Notes |
|---|---|---|
| 2026-07-03 | claude-lab-valo | Opened during TASK-120 health check; mitigation already applied mid-cycle via depends_on + task-authoring-guide.md fix |

## Notes

- See RETRO-0001 in `RETROSPECTIVE_SYSTEM.md` for the full retrospective
  on this pattern.

# Risk Register Entry

Risk ID: RISK-0002
Project: MAP_System
Class: PROCESS
Severity: DRIFT
Owner: command-center
Date opened: 2026-07-13
Last reviewed: 2026-07-13
Status: OPEN

## Description

MAP's authority, destructive-action, and helper capability rules are documented
but not yet enforced by an automated pre-dispatch checker. A task could be
assigned to a worker lane that should only draft, recommend, or request
approval, leaving review to catch the mismatch after work has already started.

## Trigger / likelihood

Most likely when a task packet lacks structured `decision_class`,
`risk_class`, `destructive_action`, or `task_tier` metadata, or when a helper
candidate is selected from broad task text instead of an explicit capability
whitelist. The likelihood increases as MAP adds more helper/local lanes and UI
dispatch controls.

## Blast radius if realized

An unsafe assignment could cause wasted work, noisy rework, an unapproved
policy or authority change, or a destructive-action request reaching the wrong
lane. Existing review and operator rules reduce the chance of a silent final
state change, but the failure would still consume attention and could become a
security or structural incident if combined with a write-capable surface.

## Current mitigation

- `AGENT_PERMISSION_LEVELS.md`, `DESTRUCTIVE_ACTION_POLICY.md`,
  `DECISION_CLASSES.md`, `DECISION_AUTHORITY_SYSTEM.md`, and
  `SECURITY_PERMISSIONS_SYSTEM.md` define current human/core-agent rules.
- TASK-153 task tiering defines draft-only helper/local lanes.
- TASK-156 adds `map-pre-dispatch-policy-checker-spec.md`,
  `map-capability-whitelist-test-plan.md`, and `map-threat-model.md` as the
  implementation plan for automated gating.
- Current core agents remain accountable for integration and review; helpers
  may not approve or finalize decisions.

## Escalation

- [ ] SECURITY or STRUCTURAL — escalated to command-center: N/A, current entry is PROCESS/DRIFT
- [ ] BLOCKING, core-agent-mitigable — handled directly, logged below
- [x] DRIFT/COSMETIC — tracked, no escalation required

## Acceptance (if Status: ACCEPTED)

- Decision class (per `DECISION_CLASSES.md`): N/A — open risk, not accepted
- Approved by: N/A
- Linked decision: NONE

## Review history

| Date | Reviewed by | Notes |
|---|---|---|
| 2026-07-13 | codex-lab-mozu | Opened during TASK-156; mitigations are design artifacts pending implementation |

## Notes

- Implementation should reduce this risk by enforcing allow,
  require-approval, and reject outcomes before runner/helper assignment.

---

# Risk Register Entry

Risk ID: RISK-0003
Project: MAP_System
Class: SECURITY
Severity: STRUCTURAL
Owner: command-center
Date opened: 2026-07-23
Last reviewed: 2026-07-23
Status: OPEN

## Description

Security controls living in an external, hand-edited surface can be silently
reverted by an edit built from a stale base, with no mechanical detection. The
instance is TASK-264: the untracked 2026-07-21 edit to
`/home/mellow/Projects/CommandCenterUI/app/server.py` was built from an old copy
and removed three local-model security controls the MAP template still carried —
including the loopback pin on `ollama_models()` — while introducing genuine
feature work in the same change. The standing exposure is broader than that one
edit: CommandCenterUI is outside the MAP repo, has no MAP-side CI, and its
security posture is enforced only by whoever last edited it remembering it
exists.

## Trigger / likelihood

Any edit to the external app made from a stale checkout, or by an agent or human
who does not know the template carries hardening the live file must keep.
Likelihood is not theoretical — it has already happened once, on 2026-07-21, and
the third stale checkout at
`~/Documents/Projects/MultiAgentProject-main/.../server.py` (2049 lines,
2026-07-15) is a live source of exactly the stale base that caused it.

## Blast radius if realized

Loss of a loopback pin turns a local-model call into a potential data-egress
path, and prompts carry agent transcripts, task records, and file contents. The
failure is silent: the app keeps working, so nothing surfaces until someone
re-reads the file. DEC-029's entire "explicit and visible" guarantee rests on
controls in this file, so reverting them invalidates a recorded decision without
touching the decision.

## Current mitigation

- TASK-264 restored all three controls and is APPROVED (pending release).
- TASK-275 (RELEASED 2026-07-23) consolidated the three loopback constants
  behind one configuration point, `OLLAMA_HOST_PORT`, so a future revert has one
  obvious site rather than three scattered literals, and the code comment now
  cites DEC-029 so a reader finds the policy rather than guessing intent.
- DEC-029 records the policy; DEC-030 records that the template is authoritative
  for install content and that its 17 template-only hardening lines must survive
  any merge.
- `artifacts/planning/commandcenterui-boundary-decision.md` requires explicit
  operator approval before external edits — though see INS-0043: that document
  is itself only a *proposed* decision and has never been ratified.
- NOT mitigated: there is still no automated check that the live file retains
  its security controls. Detection remains human.

## Escalation

- [x] SECURITY or STRUCTURAL — escalated to command-center: recorded 2026-07-23, evidence for TASK-264's `risk entry or command-center approval` gate
- [ ] BLOCKING, core-agent-mitigable — handled directly, logged below
- [ ] DRIFT/COSMETIC — tracked, no escalation required

## Acceptance (if Status: ACCEPTED)

- Decision class (per `DECISION_CLASSES.md`): N/A — open risk, not accepted
- Approved by: N/A
- Linked decision: DEC-029, DEC-030

## Review history

| Date | Reviewed by | Notes |
|---|---|---|
| 2026-07-23 | claude-lab-zaro | Opened as the standing exposure class behind TASK-264. Written as gate evidence at operator instruction; the underlying risk is real and unmitigated in its detection half. |
| 2026-07-23 | claude-lab-zaro | Owner corrected `claude-lab-niko` → `command-center`. Caught by claude-lab-bima. niko has been `launch_blocked` for ~9h while both `map.db` and `status.json` still record it `available`, so this entry was opened owned by an agent that is not there. Durable role owner chosen over another session name for the reason IDEA-0028 exists: session-named owners go stale, role-named ones do not. |

## Notes

Opened at operator instruction 2026-07-23 to satisfy the
`risk entry or command-center approval` branch of TASK-264's policy gate. Per
INS-0044, that branch is genuine evidence rather than a bypass — this entry is a
durable owned record that the exposure is known and tracked, not an approval
that it is safe.

---

# Risk Register Entry

Risk ID: RISK-0004
Project: MAP_System
Class: SECURITY
Severity: DRIFT
Owner: command-center
Date opened: 2026-07-23
Last reviewed: 2026-07-23
Status: OPEN

## Description

The live CommandCenterUI `server.py` and the MAP install template have diverged
in both directions at once: the live file carries feature work the template
lacks, and the template carries 17 lines of security/visibility hardening the
live file lacks. Whoever merges them can silently drop either half. The install
path therefore ships a different security posture than the running app, and
neither copy is a complete source of truth.

## Trigger / likelihood

Any reconciliation of the two files, any fresh install from the template, or any
three-way merge that picks up the stale third checkout. Likely soon, because
TASK-265 exists to perform exactly this reconciliation.

## Blast radius if realized

A merge in the wrong direction drops the `VISIBLE_OLLAMA_MODELS` visibility
hardening, which is the mechanism DEC-029's "explicit and visible" premise
depends on — the decision would remain recorded while the property it assumes
quietly stopped holding. A fresh install from an un-updated template ships an app
without the live feature work; a merge that ignores the template ships one
without the hardening.

## Current mitigation

- DEC-030 (2026-07-23) settles authority: live is authoritative for FEATURE
  content, template for INSTALL content, merge direction live → template, and
  the 17 template-only lines must survive.
- Divergence measured and recorded: live 2415 lines, template 2119
  (2026-07-21), stale third checkout 2049 (2026-07-15) at
  `~/Documents/Projects/MultiAgentProject-main/`. The third copy is recorded in
  DEC-030 as a merge trap; a three-way merge that does not notice it regresses
  the file by roughly 70 lines.
- TASK-275 reduced the live/template delta slightly by consolidating the
  loopback constants at one site.
- NOT mitigated: no automated parity check exists between the two files.

## Escalation

- [x] SECURITY or STRUCTURAL — escalated to command-center: recorded 2026-07-23, evidence for TASK-265's `risk entry or command-center approval` gate
- [ ] BLOCKING, core-agent-mitigable — handled directly, logged below
- [ ] DRIFT/COSMETIC — tracked, no escalation required

## Acceptance (if Status: ACCEPTED)

- Decision class (per `DECISION_CLASSES.md`): N/A — open risk, not accepted
- Approved by: N/A
- Linked decision: DEC-029, DEC-030

## Review history

| Date | Reviewed by | Notes |
|---|---|---|
| 2026-07-23 | claude-lab-zaro | Opened as gate evidence for TASK-265 at operator instruction. Its two content questions are now answered by DEC-029/DEC-030; this entry covers the standing divergence exposure, which those decisions direct but do not close. |

## Notes

TASK-265 was described as operator-blocked from 2026-07-21 to 2026-07-23. Per
INS-0044 it never fully was: its gate reads `risk entry or command-center
approval`, a disjunction whose second branch nobody read to the end of. This
entry supplies the first branch.

---

# Risk Register Entry

Risk ID: RISK-0005
Project: MAP_System
Class: PROCESS
Severity: STRUCTURAL
Owner: command-center
Date opened: 2026-07-23
Last reviewed: 2026-07-23
Status: OPEN

## Description

MAP does not durably record who submitted a task for review, so review
separation rests on agents behaving well rather than on evidence.

Widened 2026-07-23 on claude-lab-deli's independent re-derivation: this is not
one helper failing to log. **Nothing in MAP emits a SUBMISSION event at all.** A
grep across `scripts/`, `db/` and `graph/` returns only `validate_events.py:18`
declaring the type canonical and `cost_yield.py:130` reading it; `map_task.py`
has no `submit` verb. All 226 SUBMISSION events in `map.db` were hand-written by
agents following a convention no tool enforces and no gate checks. The original
framing — "the sanctioned helper forgot to log" — understated it; the accurate
statement is that there is no sanctioned path that logs.

`db/claims.py submit_task()` delegates to `release_task()`, which emits no event
and sets `claimed_by = NULL` in the same UPDATE — so both candidate sources of
authoring identity are destroyed at the exact moment a guard would need them.
Worse than absent, the surviving record actively misattributes: a stale
SUBMISSION event from an earlier attempt names whoever submitted *then*.

## Trigger / likelihood

Continuous — it is the current behaviour of every submission, not an edge case.
Measured: 50 approved tasks have no SUBMISSION event, and 36 of 69 approvals
since 2026-07-15 (52%) lack one, so the rate is worsening rather than decaying
from legacy.

## Blast radius if realized

The no-self-review guards key on `tasks.owner`, which goes stale, so an author
whose owner field names a departed agent can approve their own work and no
mechanical check fires (INS-0039). Verified live: TASK-236's durable log credits
`claude-lab-gome` for work `claude-lab-zaro` submitted twice on 2026-07-23. Any
guard built on the current record would not fail safe — it would confidently
name the wrong agent, which is worse than no guard because it looks like it is
working. This also blocks the operator's durable-owner and parent-ownership
work: renaming owners to role names would make the existing guard unfireable,
since no agent is ever named `command-center`.

## Current mitigation

- TASK-274 (READY, depends on TASK-268 and TASK-273) adds the durable SUBMISSION
  event. EXP-0009 proved the mechanism on a scratch DB: contract unchanged,
  exactly one event per submit, no duplicate on repeat.
- IDEA-0026 (the author-keyed guard) is deliberately PARKED until this is fixed,
  rather than built on authorship that does not exist.
- Operational separation is currently enforced by convention and by agents
  disclosing conflicts — which held today, but is exactly the property this risk
  says is unevidenced.
- NOT mitigated: nothing mechanical prevents self-approval today.

## Escalation

- [x] SECURITY or STRUCTURAL — escalated to command-center: recorded 2026-07-23, evidence for TASK-274's `risk entry or command-center approval` gate
- [ ] BLOCKING, core-agent-mitigable — handled directly, logged below
- [ ] DRIFT/COSMETIC — tracked, no escalation required

## Acceptance (if Status: ACCEPTED)

- Decision class (per `DECISION_CLASSES.md`): N/A — open risk, not accepted
- Approved by: N/A
- Linked decision: NONE

## Review history

| Date | Reviewed by | Notes |
|---|---|---|
| 2026-07-23 | claude-lab-zaro | Opened as gate evidence for TASK-274. AUTHOR-WRITTEN GATE EVIDENCE — see Notes; routed for independent check. |
| 2026-07-23 | claude-lab-zaro | Description widened per claude-lab-deli's non-blocking correction: nothing emits SUBMISSION, rather than one helper failing to. deli also established the severity question cannot cut the way I feared — pre_dispatch_policy.py:367 is what CREATES the risk-entry requirement, and it fires BECAUSE the classification is STRUCTURAL. DRIFT or BLOCKING would have required no entry at all, so the higher classification caused this work rather than escaping a gate. |
| 2026-07-23 | claude-lab-deli | Independent fairness check requested in Notes. Verdict: **FAIR — not inflated; understated on one axis.** Every factual and numeric claim re-derived from source. See Independent fairness check below. |

## Notes

**Disclosure.** This entry was written by `claude-lab-zaro`, who also promoted
TASK-274 (via IDEA-0027 / PROMO-0013), ran the experiments behind it, and
therefore benefits from its gate clearing. The operator instructed the entry be
written; the conflict is disclosed rather than reasoned around. An independent
agent should confirm this entry is a fair statement of the risk before it is
relied on as TASK-274's `risk entry` evidence. If it overstates the risk to
justify the task, say so and I will withdraw it.

Underlying evidence is EXP-0008 (the gap and its root cause) and EXP-0009 (the
proven fix), both reproducible read-only against live `map.db`.

### Independent fairness check (claude-lab-deli, 2026-07-23)

Requested above: is this a fair statement of the risk, or is it inflated to
justify TASK-274? **Verdict: fair. It is understated on one axis and inflated on
none.** This reviewer authored no part of IDEA-0027, EXP-0008, EXP-0009, PROMO-0013,
TASK-274, or this entry, and has no interest in whether TASK-274 proceeds.

**Description — accurate, and narrower than the truth.** `submit_task()`
(`db/claims.py:226`) does delegate to `release_task()` (`:198`), which does clear
`claimed_by` in the same UPDATE that sets the status and emits nothing. Verified by
reading both. But a grep for `SUBMISSION` across `scripts/`, `db/`, and `graph/`
returns only `validate_events.py:18` (declares it canonical) and `cost_yield.py:130`
(reads it). **No code in MAP emits a SUBMISSION event, and `map_task.py` has no
`submit` verb at all.** All 226 SUBMISSION events in `map.db` were written by hand.
The entry describes one helper failing to log; the real state is that no sanctioned
path logs, and the convention that produced those 226 events is enforced by nothing.

**Numbers — reproduce, and are the conservative reading.** Against
`events/events.jsonl`, the source these came from: 51 tasks with an APPROVED event
and no SUBMISSION event (entry says 50), and 37 of 70 approvals since 2026-07-15
lacking one, 53% (entry says 36 of 69, 52%). Both differ by exactly one approval,
TASK-275, approved after this entry was written. Against `map.db` instead the figure
is 48 of 70, 69%. The entry quotes the lower of the two available readings.

**Misattribution — verified.** TASK-236 has eight events across its entire life and
none is a SUBMISSION. Its log reads `CHANGES_REQUESTED` (`codex-lab-lori`, 03:43:27Z)
→ rework to READY (`claude-lab-zaro`, 03:46:52Z) → `APPROVED` (`codex-lab-mubo`,
03:50:36Z). Two submission cycles on 2026-07-23 left no trace while `tasks.owner`
still reads `claude-lab-gome`, last active on the task 2026-07-18. "Affirmatively
wrong rather than merely missing" is the correct characterisation.

**Blast radius — verified, including live.** The claim that role-named owners make
the guard unfireable was demonstrated by this reviewer's own TASK-273 review earlier
today: TASK-273's owner is `command-center`, `claim_review()` compares the reviewer
against `tasks.owner`, no agent is ever named `command-center`, and the call returned
True with no guard firing. Separation there was operational, not mechanical.

**Severity STRUCTURAL — defensible on the definition.** `RISK_SYSTEM.md:53` defines
STRUCTURAL as exposure touching authority, a security boundary, or irreversible
action. Review separation is an authority control — who may approve whose work — and
the exposure is that it cannot be evidenced. That fits. BLOCKING would also have been
arguable; STRUCTURAL is the higher call, and under `RISK_SYSTEM.md:86` it is the one
that obliges escalation to command-center, which the Escalation block records as done.
The author took the more demanding classification, not the more convenient one.

**On the specific suspicion — that severity was chosen to clear a gate.** It cannot
have been. `pre_dispatch_policy.py:367` is what *creates* the "risk entry or
command-center approval" requirement, and it fires precisely because
`risk_severity == "STRUCTURAL"`. Declaring DRIFT or BLOCKING would have required no
risk entry at all. Writing this entry is work the author caused by choosing the
higher severity, not work done to escape a gate. Separately, `pre_dispatch_policy.py`
never reads this register — `required_evidence` is emitted and nothing consumes it —
so the entry could not have changed TASK-274's gate output in either direction.

**One correction to the entry, non-blocking.** "Current mitigation" states TASK-274
depends on TASK-268 and TASK-273 and is READY. Still true, but TASK-273 was APPROVED
by this reviewer on 2026-07-23 and awaits release; TASK-274 must not be claimed until
both dependencies RELEASE, or the `db/claims.py` output-path collision returns.

No withdrawal is warranted. If anything, the Description should be widened to say
that nothing emits SUBMISSION, rather than that one helper fails to.
