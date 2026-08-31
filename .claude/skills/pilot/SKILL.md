---
name: pilot
description: Use MAPS_L to take an approved project or substantial task from current reality to verified completion. Use when the user explicitly invokes Pilot/MAPS_L for multi-step or multi-agent project work. Preserve target-project authority, choose the smallest useful MAPS_L operating depth, delegate bounded work, resolve in-scope uncertainty internally, reconcile results, and continue automatically until the parent outcome is complete or a true authority boundary is reached.
metadata:
  author: BigCatMellow
  version: "0.1.0"
---

# Pilot a project with MAPS_L

`pilot` is a **thin invocation adapter** for MAPS_L. It does not define a second
MAPS_L operating contract and must not become one.

When current repository/web access is available, use the live MAPS_L sources:

- `https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md`
- `https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/FIRST_RUN.md`
- `https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INDEX.md`
- `https://github.com/BigCatMellow/MAPS_Lean/wiki`

Read only what the work needs. `AGENTS.md` governs work **inside MAPS_Lean**;
when piloting another project, that project's own instructions and approved scope
govern its authority. MAPS_L supplies the operating method, not permission to
ignore the target project's rules.

## Invocation

Treat the request supplied with the skill as the target project/task and desired
parent outcome.

Claude Code direct examples:

```text
/pilot the Pokemon project
/pilot BigCatMellow/Dismissal- and make the mobile workflow first-time-user safe
/pilot this migration through completion
```

When Claude Code expands skill arguments, the invocation request is:

```text
$ARGUMENTS
```

If a compatible client does not expand `$ARGUMENTS`, use the current user request
that invoked/selected the skill instead. Do not ask the user to repeat information
already available in the conversation, repository, project state, or connected
tools.

## 1. Establish target, reality, and authority

Before broad planning:

1. Identify the actual target project/repository/system and parent objective.
2. Inspect current authoritative evidence and live state.
3. Read the target project's local agent instructions, approved roadmap/scope,
   active task, and continuation state when they exist.
4. Separate important `VERIFIED`, `REPORTED`, `ASSUMED`, and `UNKNOWN` facts.
5. Determine the current permission envelope and what would genuinely leave it.

If the user invocation already gives a sufficiently bounded objective, do not
manufacture an extra approval ceremony. Shape the work inside that objective and
continue. If consequential execution would require a materially broader outcome,
excluded side effect, destructive action, new spending/credential authority, or
an irreducibly human preference, isolate that boundary and escalate it precisely.

When the target is MAPS_Lean itself, follow the live `docs/FIRST_RUN.md` route and
its `AGENTS.md` contract rather than this skill's summary.

## 2. Define the parent DONE condition

Translate the request into an observable parent result. For durable or
consequential work, establish enough of the following to remove material
ambiguity:

```text
parent outcome
source of truth
scope / exclusions
permission envelope
acceptance criteria
verification / evidence
review requirement
failure / recovery path
```

Use the current MAPS_L playbook index to select the **one most relevant method**.
Follow another method only when a distinct concern actually requires it.

## 3. Choose the smallest useful operating depth

Use the least machinery that reliably solves the problem:

- **Method-only:** one capable agent can safely own the work.
- **Orchestrated:** multiple bounded workers, parallel investigation, independent
  review, or multi-task continuity materially helps.
- **Runtime-backed:** concurrent/resumable execution actually needs durable MAPS_L
  task state, routing, communication, recovery, or integrity machinery.

Do **not** install, enable, or recreate the MAPS_L control plane merely because it
exists. Verify a runtime capability is current and actually wired before relying
on it.

## 4. Operate the parent scope

The active agent is the orchestration operator for the authorized parent scope.
It retains accountability after delegation.

Use available helper/subagent mechanisms when they add bounded value. Give each
worker a narrow question/output, relevant context, evidence target, stop
condition, and non-overlapping write boundary where applicable.

The operating loop is:

```text
inspect parent state
→ choose highest-value eligible action
→ act directly or dispatch bounded worker(s)
→ observe returned evidence/results
→ reconcile into parent state
→ verify what is now true
→ select the next authorized action
→ repeat
```

A completed child task, commit, review, checkpoint, or status report is **not** a
request for permission to continue. Advance automatically while authorized
parent work remains.

## 5. Resolve questions internally first

For a material in-scope uncertainty:

```text
authoritative evidence
→ safe inspection
→ focused research/helper
→ independent challenger/tenth-seat pass when consequential
→ orchestration operator decides inside authority
→ human only for a true boundary crossing
```

If native helpers are unavailable, perform a clearly separated challenger pass
that attacks the weakest assumption and strongest plausible alternative before
escalating ordinary uncertainty to the user.

Do not use a helper's confidence as evidence. Reconcile its result against the
source of truth.

## 6. Verify and review

Use proof proportional to risk. Prefer direct evidence: tests, reproduction,
logs, screenshots, database state, benchmarks, live behavior, or other observable
criteria appropriate to the target.

Independent review is a quality gate when required; it does not transfer parent
ownership and is not a routine human permission gate. Route findings back into
correction/reverification.

Do not declare the parent complete while actionable work, active workers,
unreconciled results, recoverable blockers, unmet acceptance criteria, or
required verification/review remain.

## 7. Finish correctly

Stop in exactly these normal cases:

- **COMPLETE:** parent acceptance criteria and required proof/review pass.
- **BLOCKED:** a specific unresolved dependency/safety condition prevents useful
  in-scope progress.
- **REAUTHORIZATION REQUIRED:** the next necessary action would materially leave
  the authorized envelope or requires human-only authority/preference.
- **ACTIVE WAIT:** a named active dependency is expected to return, with a known
  next action or timeout/recovery path.

Do not invent follow-on work after genuine completion.

## Reporting

Keep operator-facing reports terse. Lead with result, blocker, or required
boundary decision. Do not narrate routine tool use or repeatedly ask whether to
continue.

Typical completion:

```text
DONE
Changed: <material outputs>
Verified: <proof>
```

Typical true boundary:

```text
REAUTHORIZATION REQUIRED
Boundary: <exact action outside current authority>
Why needed: <material reason>
In-scope work remaining: <none or what can still continue>
```

## Portability

This directory is the skill package.

- **Claude Code, this repository:** `.claude/skills/pilot/SKILL.md` exposes
  `/pilot` while working in MAPS_Lean.
- **Claude Code, all local projects:** copy the `pilot/` directory to
  `~/.claude/skills/pilot/`.
- **Other Agent-Skills-compatible clients / hosted skill APIs:** install or upload
  the same `pilot/` directory according to that client's skill mechanism. The
  frontmatter intentionally stays within the portable Agent Skills fields.

Client installation changes *where the adapter is available*; it does not change
MAPS_L authority or copy MAPS_L's canonical rules into the skill.

## Final self-check

Before stopping, confirm:

- target authority was preserved;
- parent DONE is explicit;
- MAPS_L depth was proportional;
- delegation did not transfer parent ownership;
- returned work was reconciled;
- material uncertainty was challenged rather than pushed reflexively to the user;
- acceptance criteria and required proof/review pass; and
- no authorized actionable work remains.

If these are true, stop. If not, continue the operating loop or name the exact
blocker/boundary.
