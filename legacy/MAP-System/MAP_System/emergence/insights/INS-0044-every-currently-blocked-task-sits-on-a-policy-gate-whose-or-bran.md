# Insight Record

Insight ID: INS-0044
Project: MAP
Related task: TASK-265
Detected by: claude-lab-zaro
Date: 2026-07-23
Status: RAW

## Short description


- obs: Every currently blocked task sits on a policy gate whose 'or' branch nobody read to the end of

## Trigger


- src: TASK-265 sat blocked from 2026-07-21 to 2026-07-23 while everyone, bima included, described it as waiting on command-center approval. Its policy result actually reads required_evidence: ['risk entry or command-center approval'] — a disjunction. A risk entry satisfies the same gate and an agent can write one.

## The synthesis


- synth: The gate was never a single requirement; it was a choice, and the second option went unread for two days. This is a different shape from [[SYN-0005]]: nothing is missing from the system, the escape hatch exists and is documented in [[RISK_SYSTEM]]. What failed is reading. 'Blocked' became social fact faster than anyone re-read the condition, and each agent that repeated it — including the ones who wrote the status summaries — made the next re-read less likely. A stated blocker propagates as a conclusion rather than as a claim with an expiry.

## Why it might matter


- why: It is not one task. Measured across every nonterminal task by running pre_dispatch_policy.py: exactly 3 sit in require_approval — TASK-264, TASK-265, TASK-274 — and ALL 3 are blocked solely on 'risk entry or command-center approval'. Every currently blocked task in the project can be unblocked by an action an agent is permitted to take. TASK-265 lost two days to it; the others are losing time now. The gate design is fine — it deliberately offers a self-serve path so work is not hostage to an approver's availability — and the entire benefit of that design was going unused.

## Evidence


- ev: 1) pre_dispatch_policy.py line 369: risk_class == 'SECURITY' or risk_severity == 'STRUCTURAL' appends 'risk entry or command-center approval'. 2) Live run for TASK-265: decision require_approval, single reason REQUIRE_SECURITY_STRUCTURAL_APPROVAL, required_evidence ['risk entry or command-center approval']. 3) Swept all nonterminal tasks: 3 in require_approval, 3 disjunctive, 0 blocked on a non-disjunctive gate. 4) Three of the six evidence strings the checker can emit are disjunctions — 'operator instruction or approving decision', 'command-center approval or DEC record', 'risk entry or command-center approval'. So half the gate vocabulary offers an alternative, and 'command-center approval or DEC record' means a written DEC record also clears a gate people wait on. 5) [[RISK_SYSTEM]] documents the register format and requires exactly one owner per entry, so the self-serve path is fully specified — it was available the whole time.

## Risk


- risk: The wrong lesson is 'agents should self-serve past approval gates'. The or-branches are not loopholes: a risk entry is a durable, owned, reviewable record that someone accepted a named risk, which is why the checker treats it as equivalent evidence. Writing a thin risk entry to clear a gate would be gaming it and would be worse than waiting. The right lesson is narrower: read the whole condition before reporting something blocked, and state gates as the disjunctions they are. A second, cheap mitigation: whatever surfaces blocked tasks should render the full required_evidence string rather than a summarised 'awaiting approval', because the summarisation is where the 'or' was lost.

## Scope


- scope: Observation only. No gate bypassed, no risk entry written, no task unblocked by this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:

## Follow-up: the branch is real but unwired (claude-lab-zaro, 2026-07-23)

At operator instruction I wrote the evidence for all three blocked tasks —
RISK-0003 (TASK-264), RISK-0004 (TASK-265), RISK-0005 (TASK-274) — and re-ran
the checker. **The output did not change.** All three still report
`require_approval` with `required_evidence: ["risk entry or command-center
approval"]`.

Verified cause: `pre_dispatch_policy.py` contains **zero** references to the
risk register, and a repo-wide search shows nothing consumes `required_evidence`
at all except the checker that emits it and that checker's own test. The gate
*declares* what evidence is required; it never *reads* whether the evidence
exists. Satisfying it is a human judgement, not a state transition.

This sharpens the original insight rather than contradicting it. The or-branch
is genuine policy — RISK_SYSTEM.md fully specifies the register, and the gate
names a risk entry as equivalent evidence. But taking the self-serve branch
produces **no visible change anywhere**: the tool says `require_approval` before
and after, so an agent who does the right thing gets no confirmation that it
worked, and the next reader of the gate sees exactly what the previous one saw.

That is a better explanation of two days of paralysis than inattention. Nobody
read to the end of the condition partly because the system gives no signal that
reading to the end of it would accomplish anything. A disjunction whose second
branch is unobservable will be treated as a single requirement, and correctly
so, until something reflects that the branch was taken.

Cheap fix, not proposed as a task here: have the checker look for an open risk
register entry naming the task, and report `evidence_present` alongside
`required_evidence`. Then the branch becomes observable and the failure mode
disappears on its own.
