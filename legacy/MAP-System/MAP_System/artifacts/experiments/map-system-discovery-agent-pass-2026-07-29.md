# Discovery Agent Pass: MAP System (self-scope)

Run: 2026-07-29, claude-lab-muza, visible wezterm-tab session.
Method: `MAP_System/notes/discovery-agent-guide.md` (seven-pass, non-forcing).
Target: MAP System itself — no single completed phase, general orientation
scope (root AGENTS.md, docs/project-map.md, emergence/INDEX.md full registry,
recent shared/decisions.md entries through DEC-035, MAP_System/CHANGE_CONTROL_SYSTEM.md
release gate, and one live incident from this same session).
Trigger: operator asked "isn't there a thing for E/I to try and come up with
new ideas?" after watching the deterministic sentinel run (which only detects
mechanical event-log signals, not genuine new ideas) — the Discovery Agent
role from IDEA-0013/INS-0028 is exactly that missing piece.

Known findings checked before writing (to dedupe against): INS-0013
(emergence capture skipped for a whole project), INS-0032 (promoted rules
need mechanical surfacing), IDEA-0011/IDEA-0013 (parked/reopened idea-scouting
role history), EXP-0003 (prior Discovery Agent pilot, adopted "for bounded
visible phase-boundary use, not a continuous loop"), TASK-293/REPAIR-0010/
REPAIR-0012 (sanctioned `extend-attempts` verb for raw-SQL-blocked attempt
budget repairs).

---

## Finding 1

```yaml
title: Sanctioned CLI calls that cross to the remote authority host are not exempt from classifier blocking, and TASK-293's fix does not cover them
classification: risk_or_contradiction
trigger:
  - This session's own context-rotation ack: `context_rotation.py ack` (a fully sanctioned, audited verb, not raw SQL) failed once with an opaque remote error (`map-authority register-agent failed: authority request failed (1)`, empty stderr), then on a bare retry of the identical command was blocked outright by the auto-mode permission classifier.
  - DEC-035's own footnote: "Auto mode is not blanket approval: the classifier still blocks unmediated mutations of canonical state, as it did to a raw-SQL max_attempts update on 2026-07-28 (REPAIR-0012), which is what prompted building the sanctioned verb in TASK-293 instead."
problem: TASK-293 assumed the fix for classifier-blocked mutations was "build a sanctioned CLI verb instead of raw SQL" — and that fix is correct for the case it targeted (in-process SQLite writes). But `context_rotation.py ack` / `map_authority.py register-agent` is already a sanctioned, mirror-synced, audited verb, and it still got blocked — because the block trigger here isn't "raw SQL vs. CLI verb," it's "a command that mutates state on a remote host over SSH." The classifier's threshold conflates two different risk shapes under one policy.
user_impact: A rotation handoff (a routine, safety-motivated two-phase protocol) stalled mid-flight with no clean retry path, and the deciding agent had to hand-write an hcom explanation instead of the protocol completing mechanically. Any other sanctioned verb that happens to call out to the remote authority (register-agent, rotation-transfer, rotation-restore, claim-review against RUKI) is exposed to the same failure mode.
proposed_response: Do not weaken the classifier. Instead give `context_rotation.py ack` (and siblings that hit `map_authority.py`'s remote_request path) a documented, bounded retry/backoff behavior distinct from a bare shell re-invocation, and record in AGENTS.md / MAP_System/AGENTS.md that "sanctioned verb" and "classifier-approved" are not the same guarantee when the verb crosses a network boundary — so an agent hitting this doesn't burn a cycle assuming the TASK-293 pattern already covers it.
minimal_version: A one-paragraph addition to MAP_System/AGENTS.md's authority/rotation section stating explicitly that remote-authority calls (anything hitting `map_authority.py`'s ssh path) can be classifier-blocked independent of sanctioning, and the correct response is to report the specific stderr/exit code rather than retry blindly.
alternatives:
  - Wrap `_run_authority_operation` calls in a small number of automatic retries with jitter before surfacing failure (treats it as transient-only, which may be wrong if the block is a policy denial rather than a network blip — the evidence from this session shows both occurred back to back).
  - Escalate to the operator to have the classifier itself special-case already-sanctioned MAP CLI verbs (out of scope for an agent to decide; a classifier-policy change, not a MAP doc change).
evidence:
  - This session's hcom thread with claude-lab-nene (context-rotation ack failure, 2026-07-29)
  - MAP_System/shared/decisions.md DEC-035, closing paragraph
  - MAP_System/tasks/TASK-293.json description (scope explicitly SQLite-only)
confidence: 4
scores: {user_value: 3, goal_alignment: 4, necessity: 2, novelty: 4, leverage: 3, confidence: 4, reversibility: 5, complexity: 1, maintenance_burden: 1, scope_risk: 1}
recommendation: add_to_backlog
reasoning_summary: Low cost, low risk, directly evidenced by a real incident in this session; doesn't require touching the classifier itself, just naming the gap so the next agent who hits it doesn't assume TASK-293 already solved it.
```

## Finding 2

```yaml
title: The mandatory "Emergence capture considered" release checkbox never invokes the actual Discovery Agent method it's supposed to gate
classification: emergent_opportunity
trigger:
  - MAP_System/CHANGE_CONTROL_SYSTEM.md line 65/124: every release requires a literal `- [x] Emergence capture considered` line.
  - EXP-0003 (2026-07-17): the Discovery Agent seven-pass method was piloted, scored (2 new findings, 0 scope drift), and adopted with the explicit verdict "adopt with refinement for bounded visible phase-boundary use" — i.e., at phase/release boundaries, which is exactly where the checklist line fires.
  - IDEA-0013's reopening note (2026-07-17): operator said E/I "never seems to be taken advantage of."
problem: The one mechanical gate that fires at every single task release is satisfied by a checkbox, not by running the method the checkbox is presumably there to prompt. Nothing connects "Emergence capture considered" to actually invoking the seven-pass Discovery Agent guide; an agent can tick the box after a five-second glance and pass the gate. This is consistent with, and gives a concrete mechanism for, INS-0032's general claim that promoted rules go unused without mechanical surfacing — but it's worth naming the specific missing link rather than leaving it as a general pattern, because it's the exact gap the operator surfaced today by asking this question at all.
user_impact: The operator has to remember to ask "isn't there a thing for this?" per-session instead of the system routing new ideas to them; the more expensive, higher-signal discovery method (adopted, evidenced, not experimental) sits unused while a free-text checkbox does its job on paper.
proposed_response: Do not make Discovery Agent runs automatic/continuous (already rejected by EXP-0003's own notes and IDEA-0011/IDEA-0013's history — see rejected_idea below). Instead, change the checklist item's wording (or add an adjacent line) to require naming which of the two E/I mechanisms was used — the deterministic sentinel (already wired, runs continuously) or a Discovery Agent pass (bounded, phase-boundary, must be requested) — so "considered" stops meaning "typed one checkbox character."
minimal_version: Edit the checklist template line in MAP_System/CHANGE_CONTROL_SYSTEM.md to `- [x] Emergence capture considered (sentinel scan / Discovery Agent pass / neither — reason)`, no automation required.
alternatives:
  - Wire an automatic Discovery Agent trigger into the release script itself (rejected: EXP-0003 explicitly warns against turning this into a continuous model loop, and it costs a real model-backed pass per release).
  - Leave as-is and rely on operators asking (status quo — is the thing generating this finding).
evidence:
  - MAP_System/CHANGE_CONTROL_SYSTEM.md:65, :124
  - MAP_System/emergence/experiments/EXP-0003-*.md Decision/Notes sections
  - MAP_System/emergence/ideas/IDEA-0013-*.md "Reopened" section, operator quote
confidence: 4
scores: {user_value: 4, goal_alignment: 5, necessity: 2, novelty: 3, leverage: 4, confidence: 4, reversibility: 5, complexity: 1, maintenance_burden: 1, scope_risk: 1}
recommendation: add_to_backlog
reasoning_summary: Cheap, reversible, directly closes the gap the operator just asked about, and reuses machinery (Discovery Agent guide) that's already built, tested, and adopted rather than proposing anything new.
```

## Finding 3

```yaml
title: Operator-directed work explicitly scoped outside MAP task governance has zero insight-capture mechanism, not even a skipped checkbox
classification: essential_omission
trigger:
  - nene's active session (2026-07-29) is mid-way through porting a UI redesign into CommandCenterUI, a sibling project directory. The handoff snapshot records this as deliberately outside MAP: "This UI work lives entirely under /home/mellow/Projects/CommandCenterUI... not an hcom/MAP task — do not invent a MAP task_id for it or expect map.db claims to cover it."
  - Real design decisions are already being made in that work (three operator AskUserQuestion scoping choices: tag-derived rooms vs. fictional projects, alongside rollout vs. replacing chat.html, vanilla JS vs. shipping a React runtime) that are exactly the shape of thing MAP would normally capture as an insight if it happened inside a governed task.
problem: This is not INS-0013's failure mode (capture accidentally skipped inside a real MAP project). It's structurally different and arguably worse: MAP's only capture trigger (CHANGE_CONTROL_SYSTEM's checklist) fires on *task release*, so work explicitly and correctly kept outside MAP task governance has no capture trigger at all — not a skipped step, an absent one. The three scoping decisions above are the kind of thing a future agent doing similar mockup-to-real-data porting work would want to find, and right now they only exist in one session's snapshot file and hcom transcript, not in any durable emergence record.
user_impact: Real, reusable porting lessons (e.g., "derive UI groupings from an existing live field like hcom tags instead of inventing new taxonomy," "check what the backend actually serves before assuming a mockup's data model") will be lost the moment this session/handoff chain ends, and rediscovered from scratch next time someone ports a design comp.
proposed_response: Emergence capture should not require a MAP task_id. `map_emergence.py insight` already takes free-form `--related-task`; confirm/document that "NONE" or a non-MAP identifier (e.g. "CommandCenterUI (non-MAP)") is an accepted value, and note in AGENTS.md's routing table that operator-directed work outside any project's MAP governance can and should still get lightweight insight capture, scoped to whichever agent is doing the work rather than gated by task release.
minimal_version: One insight record, right now, capturing the three scoping decisions from this UI-port session as a reusable pattern for future mockup-to-real-backend porting work — filed with `--related-task NONE`, which the CLI already supports.
alternatives:
  - Leave it: accept that non-MAP-governed work is out of scope for E/I entirely (this is the implicit status quo, and is the thing this finding argues against).
  - Retroactively invent a MAP task for CommandCenterUI (rejected: the operator explicitly chose to keep this outside MAP governance; forcing a task_id onto it would relitigate that scoping decision without new evidence).
evidence:
  - MAP_System/handoffs/STATE_SNAPSHOT-claude-lab-nene-20260729T052244Z.yaml, active_constraints[1] and forward_tasks[0]
  - MAP_System/emergence/insights/INS-0013-*.md (the nearest existing but distinct pattern)
confidence: 3
scores: {user_value: 3, goal_alignment: 3, necessity: 2, novelty: 4, leverage: 2, confidence: 3, reversibility: 5, complexity: 1, maintenance_burden: 1, scope_risk: 1}
recommendation: ask_user
reasoning_summary: The proposed_response is cheap and reversible, but whether the operator actually wants insight capture applied to work they deliberately kept outside MAP governance is a scope call for them, not a default an agent should just apply.
```

## Rejected (checked, not re-proposed)

```yaml
title: Make the Discovery Agent a continuous/standing background role
classification: rejected_idea
reasoning_summary: Already tried in concept and explicitly rejected twice — IDEA-0011 parked (2026-07-04, overlaps with a standing-role pattern AGENTS.md's Pushback Standard cautions against) and EXP-0003's own adoption note ("Do not turn this into a continuous model loop," 2026-07-17). No new evidence in this pass changes that calculus; Finding 2 above proposes a lighter-weight mechanical trigger instead of a standing role.
```

## Adjudication note

3 findings offered, all `add_to_backlog` / `ask_user` — none rise to `implement` on their own evidence; none are novel-for-novelty's-sake (each ties to a concrete artifact or a live incident from this session); 1 known pattern explicitly checked and not re-proposed. Scope stayed inside MAP orientation docs plus one cross-referenced live incident; no implementation edits made, no task/policy/decision state changed, no emergence records promoted.
