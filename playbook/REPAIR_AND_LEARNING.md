# Repair and Learning

Fix what is mechanical. Propose what is structural. Prevent the next
occurrence, not only this one.

This is the **triage / continuous-improvement core standard**: the mandatory loop
that captures every friction signal, classifies it, escalates a recurrence to an
*enforced* countermeasure (not another instruction), and closes it only when the
countermeasure is verified live. `AGENTS.md` invariant 13 and the friction-capture
sentence in "Work records and changes" point here.
[`work/coordination/FRICTION_LOG.md`](../work/coordination/FRICTION_LOG.md) is the
capture surface; [`ROADMAP_TRAJECTORY_CHECK.md`](ROADMAP_TRAJECTORY_CHECK.md) is
the consumption venue.

## Triage procedure (mandatory)

### Mandatory capture — a `FRICTION_LOG` entry is REQUIRED when any of these occurs

- a **run or command failed** in a way that cost rework or blocked progress (not
  an expected non-zero exit that the workflow handles);
- a **dispatched worker stalled** or had to be re-dispatched / re-prompted;
- a **wrong assumption was discovered** — recorded state, a doc claim, or a plan
  step turned out not to match reality and work had to change;
- a **tool or environment gap** — a capability the work needed was missing,
  broken, or behaved differently than documented;
- an **operator expressed friction** — a request, complaint, or "this is clunky",
  even if small;
- a **review caught a class of defect** (not a single typo) — the reviewer
  identifies a pattern the process should have prevented.

The entry is appended **before the fix PR opens, not after**.

### Explicitly NOT in scope (do not create entries for)

- one-off typos, formatting slips, and cosmetic fixes with no rework cost;
- expected negative results (a test that is supposed to fail failing; a probe
  that correctly returns "not found");
- normal design iteration inside a task (revising your own draft);
- routine merge-conflict resolution with no lost work;
- anything already captured — append a follow-up to the existing entry instead.

Rule of thumb: **if it cost rework, surprised someone, or the operator mentioned
it, it is in scope.** If in doubt, a one-line entry is cheap; a missed recurrence
is not.

### The loop

```text
capture → classify severity → recurrence check → 1st: fix + record
                                              → Nth: mechanical safeguard + why prior fix failed
                                              → verify the countermeasure live → close
```

1. **Capture.** Append one `FRICTION_LOG.md` entry in the existing format the
   moment a trigger fires. Concrete `signal`; `countermeasure: none yet` is a
   valid initial value.
2. **Classify severity.** Reuse the [Repair triage](#repair-triage) table
   verbatim — Cosmetic / Drift / Blocking / Structural. Drift-or-worse also gets
   a repair record ([`templates/repair-record.md`](../templates/repair-record.md));
   Structural routes to a decision path. No new severity vocabulary.
3. **Recurrence check.** Is this the **1st** occurrence of this *pattern*, or the
   **Nth**? "Same pattern" = same failure mode / same root-cause class, not
   necessarily the same file or symptom. Search `FRICTION_LOG.md` + `work/notes/`
   repair records before deciding.
4a. **1st occurrence → fix + record.** Apply the mechanical repair if authorized;
    propose/escalate if structural. Record the fix in the entry's `countermeasure`
    field. A prompt instruction, a doc line, or a convention **is an acceptable
    1st-occurrence fix.**
4b. **Nth occurrence → the prior fix was insufficient.** Per invariant 13, a
    second instruction is not allowed. Add an **enforced safeguard**: a test, a
    template field, a hook, a CI check, a script the trajectory pass runs, a
    schema constraint — something that fails or blocks mechanically when the
    pattern recurs. In the entry, **state explicitly why the previous fix did not
    hold**. If no mechanical safeguard is feasible, that is an **operator
    escalation**, not a third instruction.
5. **Verify the countermeasure live.** `verified:` moves off `UNVERIFIED` only
   when the countermeasure has been **observed working against real system
   state** — the test exists and is red on the failure / green on the fix; the
   template line is in the committed template; the script flags a real overdue
   entry; the hook actually blocked a real write. "Written down and merged" is
   **not** verified. A countermeasure that inherently needs a future event to
   observe stays `UNVERIFIED` with a named observation condition and is checked at
   the next trajectory pass.
6. **Close.** An entry is **CLOSED** when **all** of:
   - `countermeasure` names a concrete durable mechanism (or the entry is a pure
     operator-preference record with no fix needed, marked as such);
   - `verified:` records how + when it was confirmed live (not `UNVERIFIED`);
   - `follow-up` is `none` OR every follow-up item has its own dated disposition;
   - for a behavioral / "watch if it recurs" entry: **N = 3** consecutive clean
     trajectory arcs have passed with no recurrence. After 3, the entry is CLOSED
     with a "no recurrence in 3 arcs" line and stops consuming pass attention. A
     later recurrence opens a **new** entry that links back.
   A trajectory pass appends `**CLOSED — <how>**` as the final follow-up line.
   Closed entries are never deleted (append-only file).

### Relationship to operational lessons

A triaged recurrence is a candidate operational lesson
(`runtime/operational_learning.py`) **only when its lesson generalizes** beyond
its own fix; the promotion path is [`EMERGENCE.md`](EMERGENCE.md). A triaged item
whose fix is entirely local closes in `FRICTION_LOG` and stops there. No
duplication of the promotion mechanics here.

## Repair triage

| Severity | Meaning | Action |
| --- | --- | --- |
| Cosmetic | Formatting or harmless stale detail | Correct and verify normally. |
| Drift | Recorded state differs from verified reality | Repair mechanically; record the cause and verification. |
| Blocking | Drift stops valid work | Repair directly only if mechanical; otherwise propose and escalate. |
| Structural | Repair changes authority, ownership, decisions, data shape, or approved behavior | Do not silently apply; use a decision/change path. |

For drift or worse, write a repair note with: trigger/evidence, severity,
change made or proposed, verification, rollback, and prevention follow-up.
Use [the repair-record template](../templates/repair-record.md) to capture that
evidence before applying a drift/blocking repair or proposing a structural one.

## Diagnostics do not grant repair authority

A validator, health check, replay index, monitor, or audit may detect a problem.
Detection does not authorize it to rewrite intent, policy, ownership, scope,
architecture, or other structural state.

Use:

```text
detect
→ classify
→ repair mechanically when already authorized
  OR propose/escalate
→ verify
```

A diagnostic surface should report drift clearly and remain read-only unless a
separate, bounded repair action is explicitly part of its contract.

## Learning loops

- **In-line repair:** one incident, repaired and verified.
- **Emergence:** a reusable insight or idea surfaced by the incident.
- **Retrospective:** at a project phase or multi-task cycle, examine patterns:
  what happened, why, what worked, what did not, and which change to make.

If a failure repeats, do not merely create another repair note. Add a durable
countermeasure: validator, template field, test, default, checklist, or
decision. Test the countermeasure against the failure that motivated it.

When a recurring lesson becomes startup/task guidance, keep it scoped and point
back to the evidence that justified it. Do not load the full incident archive
into every future agent session.

## Operator-friction and request capture

Friction signals that are **not drift** — operator requests, recurring stalls,
tool-gaps, clunky workflows — do not fit the repair-note severity table above.
Capture them instead in
[`work/coordination/FRICTION_LOG.md`](../work/coordination/FRICTION_LOG.md):

- one append-only entry each, with a concrete `signal`, the durable
  `countermeasure` (or `none yet`), and a `verified:` field recording whether
  the countermeasure is confirmed live in the system or still `UNVERIFIED`;
- every session appends its friction/request items to that log before
  self-clearing or handing off (also part of the handoff checklist);
- [`ROADMAP_TRAJECTORY_CHECK.md`](ROADMAP_TRAJECTORY_CHECK.md) consumes the log
  every pass — it skims for `UNVERIFIED` / `none yet` entries and closes,
  verifies, or escalates each one.

This is the capture half of the continuous-improvement ("triage") loop; the
trajectory check is the consumption half. A signal severe enough for a
permanent test still becomes a frozen regression case as above.

## Freezing a real incident as a regression case

When a real incident is severe enough, or has already repeated, to warrant a
permanent test (the "add a durable countermeasure" step above) rather than
only a repair note, convert it into a `MAPS_FROZEN_REGRESSION_CASE`
(`runtime/evaluation/regression_case.py`) instead of describing it in prose:

1. Produce or locate the exact portable Run Record for the task/run that
   exhibited the failure: `python -m runtime.cli run-record <task_id> <run_id>`.
2. Classify the incident into one `IncidentCategory`
   (`runtime/evaluation/regression_case.py`) -- e.g. `TOOL_FAILURE`,
   `CONTEXT_POISONING`, `AUTHORITY_VIOLATION_ATTEMPT`. `UNKNOWN` is accepted
   but should be revisited once the real cause is understood.
3. Write a sanitized fixture: the minimal reproducible input/state that
   exhibits the failure, with any secret-shaped text redacted -- `freeze-case`
   rejects a fixture that still contains text `redact_sensitive_text` would
   flag.
4. Name the specific expected properties the case should assert as short
   lowercase machine IDs (e.g. `no-secret-leak`, `hook-blocks-write`) -- these
   become the pass/fail contract future evaluation runs check against.
5. Freeze it: `python -m runtime.cli freeze-case <task_id> <run_id> --category
   <CATEGORY> --fixture-file <path|-> --expect <property-id> [--expect ...]
   --tag <tag> [--tag ...] --frozen-by <actor>`.
6. Store the emitted JSON at `work/regression-cases/<case_id>.json` (create
   the directory the first time it is used) and commit it alongside the
   repair note -- this is the durable countermeasure artifact the note should
   reference, not a description of one.
7. A frozen case's `promotion.automatic` is always `false`: it is evaluation
   evidence only and never self-authorizes a harness/policy/routing change on
   its own. A case passing or failing informs a human repair/change decision;
   it does not make one.

This adds the mechanical step; it does not change repair-note severity
triage above, and it does not itself decide when a countermeasure is
warranted -- that judgment still follows the triage table.
