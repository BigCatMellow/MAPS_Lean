# Design note: triage / continuous-improvement as a core Pilot standard

- Status: DESIGN NOTE ONLY — no implementation, no `AGENTS.md`/`playbook/`/`templates/` edits in this PR.
- Author: `af7f16` (dispatched design lane), 2026-09-03
- Source of truth: `work/coordination/FRICTION_LOG.md`, `playbook/REPAIR_AND_LEARNING.md`,
  `playbook/ROADMAP_TRAJECTORY_CHECK.md`, `playbook/EMERGENCE.md`, `AGENTS.md`,
  `playbook/INDEX.md`, `playbook/AGI_STANDARD.md`, `runtime/operational_learning.py`,
  `templates/{task,handoff,repair-record,agi-check}.md`, `tests/test_documentation_sprawl.py`.
- Operator's private rule 20 ("a repeat failure earns a durable *mechanical* countermeasure")
  is cited throughout as "rule 20"; it is not yet in `AGENTS.md`.
- Review: verification-only (design note; changes nothing executable).

---

## 1. Problem statement

Triage / continuous-improvement exists today as **four disconnected conventions**, none
of them mandatory or enforced:

| Piece | Where | Gap |
| --- | --- | --- |
| Capture surface | `work/coordination/FRICTION_LOG.md` | "every session appends its friction items before handoff" is stated in `REPAIR_AND_LEARNING.md` §"Operator-friction and request capture" and `templates/handoff.md` §"Before finalizing" — but nothing checks it happened. |
| Severity + regression freezing | `playbook/REPAIR_AND_LEARNING.md` | Owned and clear. Not wired to a mandatory trigger. |
| Consumption | `playbook/ROADMAP_TRAJECTORY_CHECK.md` §"Friction-log consumption" | A "standing duty" that a trajectory pass can (and does) discharge weakly — see below. |
| Recurrence → mechanical countermeasure | operator's private rule 20 + one paragraph in `REPAIR_AND_LEARNING.md` §"Learning loops" | The rule that most defines "self-improving" is **not in `AGENTS.md`** — it lives only in the operator's private CLAUDE.md. Agents working from the repo alone never see it. |

Concrete evidence that convention-only is not holding:

1. **Capture is skipped under pressure.** This session diagnosed a BLOCKING `hcom list`
   non-JSON defect and nearly folded it into a fix PR with **no `FRICTION_LOG` entry**
   until the operator asked for one. (`work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md`
   was not yet merged at design time; the near-miss is the point.) The capture rule is a
   request an agent mid-fix can forget.

2. **Recurrence escalation is ad hoc and was nearly missed three times.**
   `work/notes/2026-08-18-stalled-dispatched-worker-repair.md` (occurrence 1) added a
   *detection habit* to `work/coordination/README.md`. Its own Prevention section flagged
   "No mechanical timeout/heartbeat exists — the triage rule is a manual habit."
   `work/notes/2026-08-18-dispatched-worker-stall-recurrence.md` (occurrence 2, **same day**)
   records the identical pattern recurring **three times in a row on one task** *with an
   explicit prompt instruction in place* — proving a prompt instruction is not a
   countermeasure — and explicitly warns: "Filing a third repair note for a third
   recurrence … without a mechanical fix in place would itself be a process failure."
   The escalation to "mechanical safeguard now" depended entirely on an agent remembering
   rule 20 and choosing to apply it.

3. **"Verified live" is aspirational; entries do not close.**
   `FRICTION_LOG.md` "2026-08-31 — orchestrator tool-use burned ~30-40k context" carries
   **eight** consecutive "no recurrence — Nth consecutive arc" follow-up lines
   (trajectory checks #14–#19) and is still open. Either it should have a real close
   condition ("N clean arcs → closed") or it is pure ceremony. Separately,
   `FRICTION_LOG.md` "2026-09-02 — agent edited the shared coordinator checkout" has a
   proposed rule-20 countermeasure that has sat **unadopted for the whole #253 operator
   batch window** ("#253 item 2 still unanswered" at check #19) — the consumption duty
   surfaced it but had no lever to force a disposition.

4. **The consumption half has no staleness bound.** `ROADMAP_TRAJECTORY_CHECK.md` says
   "skim … close, verify, or escalate each one" but sets no limit on how many passes an
   entry may stay `UNVERIFIED`, so "escalate" never actually fires — an entry can be
   "noted again" indefinitely.

**Net:** the loop's parts are individually sound; what is missing is (a) a *mandatory*
capture trigger, (b) the recurrence→mechanical-countermeasure rule as a **repo-visible
invariant**, (c) a precise **close** definition with a **staleness bound** so entries
terminate, and (d) enforcement wiring that makes all three unavoidable rather than
remembered.

---

## 2. Scope of the standard

### Mandatory capture — a `FRICTION_LOG` entry is REQUIRED when any of these occurs

- a **run or command failed** in a way that cost rework or blocked progress (not an
  expected non-zero exit that the workflow handles);
- a **dispatched worker stalled** or had to be re-dispatched / re-prompted;
- a **wrong assumption was discovered** — recorded state, a doc claim, or a plan step
  turned out not to match reality and work had to change;
- a **tool or environment gap** — a capability the work needed was missing, broken, or
  behaved differently than documented;
- an **operator expressed friction** — a request, complaint, or "this is clunky", even if
  small;
- a **review caught a class of defect** (not a single typo) — the reviewer identifies a
  pattern the process should have prevented.

### Explicitly NOT in scope (do not create entries for)

- one-off typos, formatting slips, and cosmetic fixes with no rework cost;
- expected negative results (a test that is supposed to fail failing; a probe that
  correctly returns "not found");
- normal design iteration inside a task (revising your own draft);
- routine merge-conflict resolution with no lost work;
- anything already captured — append a follow-up to the existing entry instead.

Rule of thumb: **if it cost rework, surprised someone, or the operator mentioned it, it
is in scope.** If in doubt, a one-line entry is cheap; a missed recurrence is not.

---

## 3. The triage procedure (the core loop)

```
capture → classify severity → recurrence check → 1st: fix + record
                                               → Nth: mechanical safeguard + why prior fix failed
                                               → verify the countermeasure live → close
```

1. **Capture.** Append one `FRICTION_LOG.md` entry in the existing format the moment a
   §2 trigger fires — before the fix PR opens, not after. Concrete `signal`; `countermeasure:
   none yet` is a valid initial value.

2. **Classify severity.** Reuse `REPAIR_AND_LEARNING.md`'s table verbatim —
   Cosmetic / Drift / Blocking / Structural. Drift-or-worse also gets a repair record
   (`templates/repair-record.md`); Structural routes to a decision path. No new severity
   vocabulary.

3. **Recurrence check.** Is this the **1st** occurrence of this *pattern*, or the **Nth**?
   "Same pattern" = same failure mode / same root cause class, not necessarily the same
   file or symptom (the dispatched-worker stalls recurred across different tasks and
   different agents — still the same pattern). Search `FRICTION_LOG.md` + `work/notes/`
   repair records before deciding.

4a. **1st occurrence → fix + record.** Apply the mechanical repair if authorized; propose/
    escalate if structural. Record the fix in the entry's `countermeasure` field. A prompt
    instruction, a doc line, or a convention **is an acceptable 1st-occurrence fix.**

4b. **Nth occurrence → the prior fix was insufficient.** Per rule 20, a second
    instruction is not allowed. Add an **enforced safeguard**: a test, a template field, a
    hook, a CI check, a script the trajectory pass runs, a schema constraint — something
    that fails or blocks mechanically when the pattern recurs. In the entry, **state
    explicitly why the previous fix did not hold** (e.g. "prompt instruction present on
    attempts 2 and 3, ignored under load"). If no mechanical safeguard is feasible,
    that is an **operator escalation**, not a third instruction.

5. **Verify the countermeasure live.** The `verified:` field moves off `UNVERIFIED` only
   when the countermeasure has been **observed working against real system state** — the
   test exists and is red on the failure / green on the fix; the template line is in the
   committed template; the script flags a real overdue entry; the hook actually blocked a
   real write. "Written down and merged" is **not** verified. A countermeasure that
   inherently needs a future event to observe (e.g. "next rotation delivers the handoff")
   stays `UNVERIFIED` with a named observation condition and is checked at the next
   trajectory pass.

6. **Close.** An entry is **CLOSED** when **all** of:
   - `countermeasure` names a concrete durable mechanism (or the entry is a pure
     operator-preference record with no fix needed, marked as such);
   - `verified:` records how + when it was confirmed live (not `UNVERIFIED`);
   - `follow-up` is `none` OR every follow-up item has its own dated disposition;
   - for a behavioral / "watch if it recurs" entry: **N consecutive clean trajectory
     arcs** have passed with no recurrence (recommend **N = 3**; see §7). After N, the
     entry is CLOSED with a "no recurrence in N arcs" line and stops consuming pass
     attention. A later recurrence opens a **new** entry that links back.
   A trajectory pass appends `**CLOSED — <how>**` as the final follow-up line. Closed
   entries are never deleted (append-only file).

---

## 4. Where it lives — recommendation: **fold into `REPAIR_AND_LEARNING.md`**, do not add a playbook

### Anti-sprawl test (`AGENTS.md` §"Documentation sprawl invariant" + `INDEX.md` §"Adding or changing a method")

> "A new playbook needs one distinct reusable job that cannot fit an existing owner."

- `playbook/` is at **24/24** files (`PLAYBOOK_SURFACE_BUDGET` in
  `tests/test_documentation_sprawl.py`). A new `TRIAGE_STANDARD.md` forces a deliberate
  budget raise to 25 — allowed, but only for a genuinely distinct job.
- The candidate jobs are: **mandatory-capture rule**, **recurrence-escalation ladder**,
  **live-verification close definition**, **enforcement wiring**.
- `REPAIR_AND_LEARNING.md` **already owns**: severity triage, repair records, "if a
  failure repeats add a durable countermeasure" (rule 20 in prose form), regression-case
  freezing, **and** the `FRICTION_LOG` capture pointer (§"Operator-friction and request
  capture"). The four candidate jobs are all *tightenings of that same concept* —
  "prevent the next occurrence, not only this one" is literally its opening line. They do
  not form a distinct reusable job; they are the missing teeth on the job it already has.
- `FRICTION_LOG.md` stays the **capture surface** (unchanged). `ROADMAP_TRAJECTORY_CHECK.md`
  stays the **consumption venue** (tightened, §5). Splitting a third doc between them
  would violate "one concept, one owner" and lengthen the reading route.

### Recommendation

**Expand `playbook/REPAIR_AND_LEARNING.md`** into the named standard. Concretely:

- Retitle its framing so it is explicitly "the triage / continuous-improvement standard"
  (one line near the top), so `AGENTS.md` and templates can point to a *named core
  standard* the way they point to `AGI_STANDARD.md`.
- Add a `## Triage procedure (mandatory)` section = §2 scope + §3 loop + §3.6 close
  definition.
- Keep severity table, repair-record requirement, regression freezing, and the
  `FRICTION_LOG` pointer where they are — they become steps *inside* the procedure rather
  than loose subsections.
- Net growth ~40–60 lines in one already-owned file; **zero** playbook-budget change,
  **zero** new index entry beyond editing the existing `REPAIR_AND_LEARNING.md` row in
  `INDEX.md` to say "…the mandatory triage loop: capture → severity → recurrence →
  mechanical countermeasure → live-verified close."

### The distinct job the standard owns (inside `REPAIR_AND_LEARNING.md`)

The **mandatory-capture rule + the recurrence-escalation ladder + the live-verification
close + the enforcement wiring** — i.e. turning an existing advisory loop into an enforced
one. That is an amendment to an existing owner, not a new owner.

### Rejected alternative

A standalone `playbook/TRIAGE_STANDARD.md` modeled on `AGI_STANDARD.md`. Rejected because
`AGI_STANDARD.md` earned its own file by being a genuinely separate concept (task-readiness
vs. operating authority); triage is not separate from repair-and-learning, it *is*
repair-and-learning with enforcement. Choosing this would need `PLAYBOOK_SURFACE_BUDGET`
24 → 25 and a non-overlap statement that would be strained. **(Operator decision §7.3.)**

---

## 5. Enforcement wiring — what makes it "core"

### 5.1 `AGENTS.md` — promote rule 20 into a hard invariant + one pointer

`AGENTS.md` is at **10289 / 10400 bytes** (`AGENTS_BYTE_BUDGET`). The additions below are
~430 bytes over budget, so this needs a deliberate budget raise (precedent: the test's own
comment records a 10000 → 10400 raise for the merge-authority rule). **Recommend
`AGENTS_BYTE_BUDGET` → 10800.** (Operator decision §7.2.)

**Add invariant 13** (the sprawl invariant itself says "new global rules belong here"; the
merge-authority rule set the precedent):

```markdown
13. **A repeat failure earns an enforced countermeasure.** First occurrence: fix
    and record it. Second occurrence of the same pattern: the fix was
    insufficient — add a mechanical safeguard (test, template field, hook, or
    check), not another instruction, and record why the first fix did not hold.
```

**Amend the "Work records and changes" section** — add one sentence after the task-record
paragraph:

```markdown
Every session captures its friction signals — failed runs, worker stalls, wrong
assumptions found, tool/environment gaps, operator-expressed friction, a
review-caught defect class — to
[`work/coordination/FRICTION_LOG.md`](work/coordination/FRICTION_LOG.md) before
handoff. The mandatory triage loop that classifies, escalates, and closes them is
[Repair and Learning](playbook/REPAIR_AND_LEARNING.md).
```

That is the whole `AGENTS.md` footprint: one invariant + one sentence + a budget-comment
update in the test. Everything else lives in the owned playbook. (Exact wording is
§7.1 for the operator.)

### 5.2 `templates/task.md` + `templates/handoff.md`

- **`handoff.md`** already has §"Before finalizing / self-clearing" pointing at
  `FRICTION_LOG.md`. Tighten it to name the §2 triggers explicitly and add: "If any
  captured signal is the **Nth** occurrence of a known pattern, the entry MUST name a
  mechanical safeguard or an operator escalation — not a second instruction."
- **`task.md`** — add one line to the "Completion / handoff" block:
  ```markdown
  - Triage capture: <FRICTION_LOG entries appended this task (ids/dates), or `none — no §2 trigger fired`>
  ```
  This makes "did you capture?" a visible, reviewable field rather than a hope.
  `tests/test_documentation_sprawl.py::test_repeatable_work_requires_operational_independence`
  already asserts specific `task.md` lines by substring — a new line is additive and does
  not break it, but a matching assertion should be **added** so the field cannot silently
  vanish (that assertion *is* a slice-2 mechanical backstop, see §5.5).

### 5.3 Dispatch-brief boilerplate

Every impl/review dispatch already must be AGI-ready (rule 19 / `AGI_STANDARD.md`). Add one
standing clause to the dispatch shape (in `HELPERS_AND_COMMUNICATION.md` or the
`AGI_STANDARD.md` §8 practical pattern, wherever dispatch boilerplate is owned — **not** a
new file):

> **Triage capture:** if anything fails, stalls, surprises you, or the environment is
> missing something you need, append a `FRICTION_LOG.md` entry before you report back.
> Run test suites as a blocking foreground call — never background-and-wait on your own
> tests.

The second sentence is itself a triage countermeasure: this session had to hand-add "don't
background-wait on tests" to every brief, which is exactly the dispatched-worker-stall
pattern from the 2026-08-18 records recurring at the dispatch layer. Templating it is the
mechanical fix rule 20 demands. (Operator decision §7.5 — which doc owns dispatch
boilerplate.)

### 5.4 `playbook/ROADMAP_TRAJECTORY_CHECK.md` — tighten "consume" into "close-or-escalate"

Replace the current soft "do one of: close / verify / escalate" with a hard requirement:

> Every `verified: UNVERIFIED` or `countermeasure: none yet` entry MUST reach a
> disposition **this pass**: CLOSED (per the close definition), or an explicit escalation
> recorded as an operator-decision item or in-scope trajectory work. An entry that has
> been `UNVERIFIED` across **N = 3** consecutive trajectory passes without a disposition
> is **automatically an operator-escalation item** — the pass names it in its operator
> section and does not record a clean result until it is listed. A behavioral
> "watch-if-it-recurs" entry with 3 clean arcs is CLOSED, not carried a 4th time.

This gives "escalate" a real trigger and stops both failure modes from §1 (entries that
never close; countermeasures that sit unadopted with no forcing function).

### 5.5 Mechanical backstop — **recommend a slice-2 advisory script, reject CI-blocking (for now)**

Proposed: `tools/triage_status.py` (or extend an existing digest script) that scans
`FRICTION_LOG.md` and reports:
- entries `verified: UNVERIFIED` older than N trajectory passes (needs a machine-readable
  pass-count or date anchor per entry — a small format addition);
- repair records under `work/notes/` with severity Drift+ and no linked `countermeasure`
  / regression case;
- the count of open vs. closed entries.

The trajectory pass **runs it** and must address what it prints. Plus the
`test_documentation_sprawl.py` assertion on the `task.md` "Triage capture" line (§5.2) —
that one is cheap and belongs in slice 1.

**Recommendation:**
- **Adopt the `task.md`-line assertion now** (slice 1) — trivial, high value, no downside.
- **Adopt the advisory script as slice 2** — it makes the §5.4 staleness bound mechanical
  instead of a remembered instruction (which §1 evidence shows is not enough).
- **Reject a CI check that fails the build on a stale `FRICTION_LOG` entry** — it would
  block unrelated PRs on an unrelated stale friction item, creating pressure to close
  entries prematurely or delete them, which is the opposite of the goal. "Detect →
  report, stay read-only unless repair is explicitly in contract" is exactly the pattern
  `REPAIR_AND_LEARNING.md` §"Diagnostics do not grant repair authority" already
  prescribes. Apply rule 20 *to the backstop itself*: if the advisory script proves
  insufficient (entries still rot with the script in place), *then* escalate it to
  blocking. (Operator decision §7.4.)

---

## 6. Relationship to operational lessons (`runtime/operational_learning.py`)

`operational_learning.py` validates **promoted, operator-gated, applicability-scoped
guidance lessons** (`CANDIDATE → ACTIVE → RETIRED`, every ACTIVE lesson needs a
`promotion.decision_ref`, projection is `GUIDANCE_ONLY` and "can_grant_policy_authority:
false"). It is a heavyweight, deliberately gated channel with near-zero writers today
(noted in `FRICTION_LOG.md` "2026-08-31 — triage loop was procedure-only").

**Boundary:**

| | Triage / `FRICTION_LOG` | Operational lesson |
| --- | --- | --- |
| Purpose | fix *this* recurring failure with a mechanism | encode *reusable guidance* for future unrelated tasks |
| Trigger | a §2 friction signal | a triaged item whose *insight* generalizes beyond its own fix |
| Authority to create | any agent, immediately | operator promotion + `decision_ref` |
| Output | test / hook / template line / closed entry | a validated `ACTIVE` lesson record with applicability scope |

A triaged **recurrence is a candidate operational lesson only when its lesson generalizes**
— e.g. "dispatched workers do not reliably self-resume after background tasks" is a
pattern likely to recur in *any* future dispatch-and-wait automation
(`2026-08-18-stalled-dispatched-worker-repair.md` §Prevention item 2 says exactly this),
so it is worth an `INCIDENT`-sourced candidate lesson. A triaged item whose fix is
entirely local (a specific test for a specific parser bug) is **not** a lesson — it closes
in `FRICTION_LOG` and stops there.

So: the triage loop is the **feeder**; `EMERGENCE.md` (`observe → … → promote`) is the
**promotion path**; `operational_learning.py` is the **registry** for the few that clear
promotion. The standard should say this in one sentence and not duplicate the promotion
mechanics. No change to `operational_learning.py`.

---

## 7. Operator decisions (recorded 2026-09-03)

### 7.1 — Exact `AGENTS.md` invariant wording

Proposed invariant 13:
> **A repeat failure earns an enforced countermeasure.** First occurrence: fix and record
> it. Second occurrence of the same pattern: the fix was insufficient — add a mechanical
> safeguard (test, template field, hook, or check), not another instruction, and record
> why the first fix did not hold.

Plus the one-sentence capture rule in "Work records and changes" (§5.1).
**Recommended: adopt as written.** It is rule 20 compressed to invariant register and
matches the existing numbered style. Alternative: shorten to a single sentence without the
"record why" clause to save ~90 bytes — not recommended, the "why the first fix failed"
step is the part that was skipped in the 2026-08-18 recurrence.

### 7.2 — Raise `AGENTS_BYTE_BUDGET` 10400 → 10800?

**Recommended: yes.** The additions are a genuine new global rule (the sprawl invariant
says those belong in `AGENTS.md`) plus a pointer; precedent is the merge-authority raise
recorded in the test comment. 10800 leaves ~80 bytes headroom after the change — tight;
**11000** if the operator wants room for the next rule without another raise. Reject =
the rule 20 invariant cannot land in `AGENTS.md` and stays convention-only, which defeats
the point of this note.

### 7.3 — New `playbook/TRIAGE_STANDARD.md`, or fold into `REPAIR_AND_LEARNING.md`?

**Recommended: fold into `REPAIR_AND_LEARNING.md`** (§4). It already owns severity +
regression freezing + the `FRICTION_LOG` capture pointer + rule-20-in-prose; the standard
is the enforcement teeth on that same concept, not a distinct job. Keeps `playbook/` at
24/24. New file only if the operator wants triage to have `AGI_STANDARD.md`-level visual
prominence as its own named doc — at the cost of a budget raise and a strained non-overlap
statement.

### 7.4 — Mechanical staleness backstop: advisory script, CI-blocking, or none?

**Recommended: advisory `tools/triage_status.py` as slice 2, plus the `task.md`-line
`test_documentation_sprawl` assertion in slice 1. Reject CI-blocking now.** (§5.5.)
Escalate the script to blocking only if entries still rot with it in place (rule 20
applied to the backstop).

### 7.5 — Staleness bound N (consecutive trajectory passes before auto-escalation; also the "clean arcs before a behavioral entry closes")

**Recommended: N = 3.** Rationale: trajectory checks currently run roughly every arc
(checks #13–#19 span ~3 days), so 3 passes ≈ up to ~1 week — long enough for a
countermeasure that needs a real event to be observed, short enough that the
"orchestrator tool-use" entry (8 passes open) would have closed at pass 3. Operator may
prefer N = 2 (tighter) or N = 4 (more slack). One number, used in both §3.6 and §5.4.

### 7.6 — Which doc owns the dispatch-brief triage clause (§5.3)?

`playbook/HELPERS_AND_COMMUNICATION.md` vs. `playbook/AGI_STANDARD.md` §8. **Recommended:
`HELPERS_AND_COMMUNICATION.md`** — it owns delegation mechanics; `AGI_STANDARD.md` is
about instruction *quality* generally, not a checklist of standing clauses. Either way, no
new file.

### 7.7 — Does promoting rule 20 to `AGENTS.md` change the operator's private CLAUDE.md?

Out of repo scope, but flagged: once invariant 13 is in `AGENTS.md`, the operator may want
to trim rule 20 in their private CLAUDE.md to a pointer to avoid duplicate truth
(invariant 6). **Recommended: operator's call; not part of any repo PR.**

---

## 8. Smallest first slice

**Slice 1 (makes it real — one PR):**
1. `AGENTS.md`: invariant 13 + the capture sentence in "Work records and changes"
   (§5.1); bump `AGENTS_BYTE_BUDGET` + comment in `tests/test_documentation_sprawl.py`.
2. `playbook/REPAIR_AND_LEARNING.md`: retitle framing + add `## Triage procedure
   (mandatory)` = §2 + §3 + close definition (§3.6), with N from §7.5.
3. `playbook/INDEX.md`: update the `REPAIR_AND_LEARNING.md` row text.
4. `templates/task.md`: add the "Triage capture:" completion line; add the matching
   `test_documentation_sprawl` assertion.
5. `templates/handoff.md`: tighten §"Before finalizing" with the §2 triggers + the
   Nth-occurrence clause.
6. `playbook/ROADMAP_TRAJECTORY_CHECK.md`: replace soft "consume" with the
   close-or-escalate + N-pass staleness rule (§5.4).
7. `playbook/HELPERS_AND_COMMUNICATION.md`: the standing dispatch triage clause (§5.3).

Verification for slice 1: `python3 -m unittest tests.test_documentation_sprawl` green;
one real friction signal run end-to-end through capture → classify → (1st-occurrence) fix
→ close, recorded in the PR.

**Slice 2 (mechanical staleness backstop):**
- `tools/triage_status.py` + a machine-readable date/pass anchor per `FRICTION_LOG` entry
  (small format addition);
- wire it into the trajectory-check procedure as a step that must be run and addressed.

**Slice 3 (only if needed):** escalate the advisory script to a CI check — *only* on
evidence that slice 2 is insufficient.

**Proportionality check (invariant 7):** slice 1 adds one invariant, ~50 playbook lines
in an owned file, 3 template lines, and 1 test assertion. It removes ceremony (entries
that never close; repeated instruction-only "fixes") and adds one enforced field. Net
effect is a *faster* not-repeating-mistakes loop, not new process. If slice 1 turns out
to add friction without catching anything over ~5 arcs, that is itself a §2 signal and the
standard should be trimmed.

---

## Resume prompt

You are picking up the "triage as a core Pilot standard" design. The design note is
merged at `work/notes/2026-09-03-triage-core-standard-design.md`. Next action: wait for
the operator to answer §7 (seven decisions; recommendations are in the note). Once
answered, implement **Slice 1** from §8 as a single PR — verification-only review is not
enough here since it edits `AGENTS.md` and `playbook/`, so it needs independent review.
Do NOT start slice 2 until slice 1 has run one real friction signal end-to-end. Do not
touch `~/Projects/MAPS_Lean` or `.maps/`.
