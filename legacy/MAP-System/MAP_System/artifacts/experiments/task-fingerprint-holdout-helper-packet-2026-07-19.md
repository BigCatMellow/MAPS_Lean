# TASK-257 Combined Holdout Packets

Audit copy only. The evaluator receives one query file at a time.

# TASK-257 Holdout Packet — H1

Generated retrieval projection; not authority.
Use only this packet. Do not search or open named sources.

- corpus searched: 45 deterministic uncurated fingerprints
- truth set: withheld
- discovery ceiling: 1200 estimated tokens
- watermark: 2026-07-19T14:05:00-04:00

## Query

How can I rebuild a disposable local view of task and event history, query it by task, agent, or trace, and avoid treating the view as healthy when its canonical sources drift?

## Candidates

### 1. TASK-170 — Propagate trace IDs through MAP lifecycle events

- scope: MAP / map-runtime / APPROVED
- task score: 35
- summary: APPROVED: Propagate trace IDs through MAP lifecycle events.
- match: title=trace; concepts=trace; result=trace; changed_paths=event,local,trace; goal=event,trace,view
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_event_trace.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/scripts/event_trace.py` — implementation; can prove implementation behavior and executable mechanism

### 2. TASK-174 — Build librarian agent + real Library-layer viability measurement

- scope: MAP / map-runtime / APPROVED
- task score: 25
- summary: APPROVED: Build librarian agent + real Library-layer viability measurement.
- match: title=agent; concepts=agent; result=agent; changed_paths=agent; goal=agent
- source warning: none
- ranked evidence choices:
  - `MAP_System/AGENT_PERMISSION_LEVELS.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence
  - `MAP_System/tests/test_librarian.py` — test; can prove executed checks, regression behavior, parity, or validation evidence

### 3. TASK-189 — Outcome feedback: event type + validator blind-spot metric

- scope: MAP / map-runtime / RELEASED
- task score: 22
- summary: RELEASED: Outcome feedback: event type + validator blind-spot metric.
- match: title=event; concepts=event; result=event; goal=event
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_outcome_feedback.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/tests/test_liveness_reaper.py` — test; can prove executed checks, regression behavior, parity, or validation evidence

### 4. TASK-181 — Use local librarian to compact emergence records

- scope: MAP / command-center-ui / RELEASED
- task score: 20
- summary: RELEASED: Use local librarian to compact emergence records.
- match: title=local; result=local; changed_paths=local; goal=agent,local
- source warning: registered output gap
- ranked evidence choices:
  - `MAP_System/tests/test_local_runner.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/emergence/ideas/IDEA-0009-rns-should-ignore-superseded-and-disposable-sessions.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

### 5. TASK-190 — Cost/yield rollup: per-task cost x outcome view

- scope: MAP / map-runtime / RELEASED
- task score: 20
- summary: RELEASED: Cost/yield rollup: per-task cost x outcome view.
- match: title=view; concepts=view; result=view
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_cost_yield.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/artifacts/reports/cost-yield-rollup-2026-07-14.md` — outcome; can prove measured result, cost/yield, later use, or operational effect

### 6. TASK-172 — Design MAP session replay read model

- scope: MAP / command-center-ui / APPROVED
- task score: 8
- summary: APPROVED: Design MAP session replay read model.
- match: goal=canonical,event,local,sources
- source warning: none
- ranked evidence choices:
  - `MAP_System/artifacts/designs/session-replay-read-model-design.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence
  - `MAP_System/tasks/TASK-172.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs

## Required response

Return: `query ID | selected TASK IDs | up to two selected source paths |
confidence high/medium/low | concise rationale or no strong match`.
Also state ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1083

---

# TASK-257 Holdout Packet — H2

Generated retrieval projection; not authority.
Use only this packet. Do not search or open named sources.

- corpus searched: 45 deterministic uncurated fingerprints
- truth set: withheld
- discovery ceiling: 1200 estimated tokens
- watermark: 2026-07-19T14:05:00-04:00

## Query

Related-files entries in nested documents were being skipped when they used a repository-root prefix or a sibling filename. Where was path resolution corrected?

## Candidates

### 1. TASK-179 — Fix librarian.py wikilink path resolution (repo-root-relative and own-dir-relative)

- scope: MAP / emergence-and-learning / APPROVED
- task score: 56
- summary: APPROVED: Fix librarian.py wikilink path resolution (repo-root-relative and own-dir-relative).
- match: title=path,resolution,root; concepts=root; result=path,resolution,root; goal=prefix,related,resolution,root,were
- source warning: none
- ranked evidence choices:
  - `MAP_System/artifacts/tests/map-613-simulation-testdrive-probes.md` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/artifacts/tests/map-validator-halt-probe.md` — test; can prove executed checks, regression behavior, parity, or validation evidence

### 2. TASK-184 — Make command-center intake the default visible broad-directive path

- scope: MAP / command-center-ui / RELEASED
- task score: 22
- summary: RELEASED: Make command-center intake the default visible broad-directive path.
- match: title=path; concepts=path; result=path; goal=path
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_command_center_intake.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/AGENTS.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

### 3. TASK-204 — Optional debate pre-escalation step for conflict-freeze / decision-authority path

- scope: MAP / map-runtime / RELEASED
- task score: 15
- summary: RELEASED: Optional debate pre-escalation step for conflict-freeze / decision-authority path.
- match: title=path; result=path; goal=path
- source warning: none
- ranked evidence choices:
  - `MAP_System/DECISION_AUTHORITY_SYSTEM.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence
  - `MAP_System/notes/review-guide.md` — guide; can prove documented procedure, protocol, or operating convention

### 4. TASK-181 — Use local librarian to compact emergence records

- scope: MAP / command-center-ui / RELEASED
- task score: 5
- summary: RELEASED: Use local librarian to compact emergence records.
- match: changed_paths=path; goal=files
- source warning: registered output gap
- ranked evidence choices:
  - `MAP_System/emergence/ideas/IDEA-0005-add-a-release-path-smoke-checklist-for-user-facing-packages.md` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/emergence/insights/INS-0005-release-reviews-must-inspect-every-user-visible-acquisition-path.md` — review; can prove independent findings, verdict, and acceptance assessment

### 5. TASK-176 — Prune stale RnS incidents for absent sessions

- scope: MAP / agent-liveness-and-helpers / APPROVED
- task score: 4
- summary: APPROVED: Prune stale RnS incidents for absent sessions.
- match: goal=entries,path
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_limit_watcher.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/scripts/limit_watcher.py` — implementation; can prove implementation behavior and executable mechanism

### 6. TASK-192 — Close taxonomy-audit regression tests #4-#6

- scope: MAP / map-runtime / RELEASED
- task score: 4
- summary: RELEASED: Close taxonomy-audit regression tests #4-#6.
- match: goal=files,skipped
- source warning: none
- ranked evidence choices:
  - `MAP_System/artifacts/tests/taxonomy-tests-4-6-report.md` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/tests/test_multi_project_isolation.py` — test; can prove executed checks, regression behavior, parity, or validation evidence

## Required response

Return: `query ID | selected TASK IDs | up to two selected source paths |
confidence high/medium/low | concise rationale or no strong match`.
Also state ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1114

---

# TASK-257 Holdout Packet — H3

Generated retrieval projection; not authority.
Use only this packet. Do not search or open named sources.

- corpus searched: 45 deterministic uncurated fingerprints
- truth set: withheld
- discovery ceiling: 1200 estimated tokens
- watermark: 2026-07-19T14:05:00-04:00

## Query

How do we keep API keys, URL passwords, credential assignments, and suspicious high-entropy tokens out of durable capture records without rejecting the capture itself?

## Candidates

### 1. TASK-191 — Redaction guard for capture pipelines

- scope: MAP / emergence-and-learning / RELEASED
- task score: 28
- summary: RELEASED: Redaction guard for capture pipelines.
- match: title=capture; concepts=capture; result=capture; goal=credential,entropy,high,url
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_redaction.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/artifacts/audits/map-threat-model.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

### 2. TASK-180 — Compact and wikilink emergence records

- scope: MAP / emergence-and-learning / RELEASED
- task score: 24
- summary: RELEASED: Compact and wikilink emergence records.
- match: title=records; concepts=records; result=records; goal=records,without
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_map_emergence_stale.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/tests/test_map_emergence.py` — test; can prove executed checks, regression behavior, parity, or validation evidence

### 3. TASK-183 — Deterministic compact active emergence records

- scope: MAP / command-center-ui / RELEASED
- task score: 24
- summary: RELEASED: Deterministic compact active emergence records.
- match: title=records; concepts=records; result=records; goal=records,without
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_map_emergence.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/artifacts/reviews/task181-review-mira.md` — review; can prove independent findings, verdict, and acceptance assessment

### 4. TASK-202 — Operator-identity + message-intent conventions in durable state

- scope: MAP / command-center-ui / RELEASED
- task score: 22
- summary: RELEASED: Operator-identity + message-intent conventions in durable state.
- match: title=durable; concepts=durable; result=durable; goal=durable
- source warning: none
- ranked evidence choices:
  - `MAP_System/artifacts/audits/map-real-parameter-calibration-results-2026-07-14.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence
  - `MAP_System/notes/communication-architecture.md` — guide; can prove documented procedure, protocol, or operating convention

### 5. TASK-181 — Use local librarian to compact emergence records

- scope: MAP / command-center-ui / RELEASED
- task score: 15
- summary: RELEASED: Use local librarian to compact emergence records.
- match: title=records; result=records; goal=records
- source warning: registered output gap
- ranked evidence choices:
  - `MAP_System/emergence/insights/INS-0007-emergence-records-need-lifecycle-closeout-not-just-capture.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence
  - `MAP_System/emergence/insights/INS-0013-emergence-insight-capture-was-skipped-entirely-for-an-entire-pro.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

### 6. TASK-198 — Fix RnS failed-nudge consumption and live-state reconciliation

- scope: MAP / agent-liveness-and-helpers / RETIRED
- task score: 6
- summary: RETIRED: Fix RnS failed-nudge consumption and live-state reconciliation.
- match: goal=durable,out,tokens
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_limit_watcher.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/agents/status.json` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

## Required response

Return: `query ID | selected TASK IDs | up to two selected source paths |
confidence high/medium/low | concise rationale or no strong match`.
Also state ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1107

---

# TASK-257 Holdout Packet — H4

Generated retrieval projection; not authority.
Use only this packet. Do not search or open named sources.

- corpus searched: 45 deterministic uncurated fingerprints
- truth set: withheld
- discovery ceiling: 1200 estimated tokens
- watermark: 2026-07-19T14:05:00-04:00

## Query

Two reviewers can race to review the same submitted task. What prevents duplicate ownership while also blocking the task owner from reviewing their own work?

## Candidates

### 1. TASK-199 — Atomic review claiming (claim_review in db/claims.py)

- scope: MAP / map-runtime / RELEASED
- task score: 31
- summary: RELEASED: Atomic review claiming (claim_review in db/claims.py).
- match: title=review; concepts=review; result=review; changed_paths=review; goal=owner,review,reviewers,same
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_review_claims.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/tasks/TASK-199.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs

### 2. TASK-179 — Fix librarian.py wikilink path resolution (repo-root-relative and own-dir-relative)

- scope: MAP / emergence-and-learning / APPROVED
- task score: 15
- summary: APPROVED: Fix librarian.py wikilink path resolution (repo-root-relative and own-dir-relative).
- match: title=own; result=own; goal=own
- source warning: none
- ranked evidence choices:
  - `MAP_System/tasks/TASK-179.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs
  - `MAP_System/artifacts/tests/map-613-simulation-testdrive-probes.md` — test; can prove executed checks, regression behavior, parity, or validation evidence

### 3. TASK-183 — Deterministic compact active emergence records

- scope: MAP / command-center-ui / RELEASED
- task score: 8
- summary: RELEASED: Deterministic compact active emergence records.
- match: changed_paths=review,two; goal=review
- source warning: none
- ranked evidence choices:
  - `MAP_System/artifacts/reviews/task181-review-mira.md` — review; can prove independent findings, verdict, and acceptance assessment
  - `MAP_System/tasks/TASK-183.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs

### 4. TASK-181 — Use local librarian to compact emergence records

- scope: MAP / command-center-ui / RELEASED
- task score: 5
- summary: RELEASED: Use local librarian to compact emergence records.
- match: changed_paths=review; goal=review
- source warning: registered output gap
- ranked evidence choices:
  - `MAP_System/emergence/insights/INS-0015-a-routine-no-self-review-reviewer-conflict-should-trigger-the-ex.md` — review; can prove independent findings, verdict, and acceptance assessment
  - `MAP_System/emergence/ideas/IDEA-0004-require-a-second-security-focused-review-pass-for-any-task-that-.md` — review; can prove independent findings, verdict, and acceptance assessment

### 5. TASK-162 — MAP 6.13: Implement protocol/semantic validator L1 wiring and halt-store integration

- scope: MAP / map-runtime / APPROVED
- task score: 4
- summary: APPROVED: MAP 6.13: Implement protocol/semantic validator L1 wiring and halt-store integration.
- match: goal=blocking,review
- source warning: none
- ranked evidence choices:
  - `MAP_System/tasks/TASK-162.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs
  - `MAP_System/tests/test_validate_layer1.py` — test; can prove executed checks, regression behavior, parity, or validation evidence

### 6. TASK-197 — Decision-conflict detection pass for validate_decisions.py

- scope: MAP / map-runtime / RELEASED
- task score: 4
- summary: RELEASED: Decision-conflict detection pass for validate_decisions.py.
- match: goal=review,same
- source warning: none
- ranked evidence choices:
  - `MAP_System/tasks/TASK-197.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs
  - `MAP_System/artifacts/tests/task197-decision-conflict-run.md` — test; can prove executed checks, regression behavior, parity, or validation evidence

## Required response

Return: `query ID | selected TASK IDs | up to two selected source paths |
confidence high/medium/low | concise rationale or no strong match`.
Also state ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1106

---

# TASK-257 Holdout Packet — H5

Generated retrieval projection; not authority.
Use only this packet. Do not search or open named sources.

- corpus searched: 45 deterministic uncurated fingerprints
- truth set: withheld
- discovery ceiling: 1200 estimated tokens
- watermark: 2026-07-19T14:05:00-04:00

## Query

Can deterministic validators ever set a real halt instead of merely reporting telemetry, and how is that authority kept disabled by default, time-bounded, scope-limited, and operator-clearable?

## Candidates

### 1. TASK-201 — Bounded halt-authority window mechanism

- scope: MAP / map-runtime / RELEASED
- task score: 86
- summary: RELEASED: Bounded halt-authority window mechanism.
- match: title=authority,bounded,halt; concepts=authority,bounded,halt; result=authority,bounded,halt; changed_paths=authority,halt; goal=authority,bounded,clearable,default,disabled,halt,operator,set,telemetry,validators
- source warning: none
- ranked evidence choices:
  - `MAP_System/notes/halt-authority-window-runbook.md` — guide; can prove documented procedure, protocol, or operating convention
  - `MAP_System/tests/test_halt_authority_window.py` — test; can prove executed checks, regression behavior, parity, or validation evidence

### 2. TASK-183 — Deterministic compact active emergence records

- scope: MAP / command-center-ui / RELEASED
- task score: 33
- summary: RELEASED: Deterministic compact active emergence records.
- match: title=deterministic; concepts=deterministic; result=deterministic; changed_paths=deterministic,instead,operator; goal=deterministic,scope
- source warning: none
- ranked evidence choices:
  - `MAP_System/emergence/insights/INS-0009-e-i-should-proactively-scout-operator-workflow-friction-instead-.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence
  - `MAP_System/tasks/TASK-183.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs

### 3. TASK-202 — Operator-identity + message-intent conventions in durable state

- scope: MAP / command-center-ui / RELEASED
- task score: 30
- summary: RELEASED: Operator-identity + message-intent conventions in durable state.
- match: title=operator; concepts=operator; result=operator; changed_paths=operator,real; goal=operator,real
- source warning: none
- ranked evidence choices:
  - `MAP_System/notes/communication-architecture.md` — guide; can prove documented procedure, protocol, or operating convention
  - `MAP_System/tasks/TASK-202.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs

### 4. TASK-204 — Optional debate pre-escalation step for conflict-freeze / decision-authority path

- scope: MAP / map-runtime / RELEASED
- task score: 27
- summary: RELEASED: Optional debate pre-escalation step for conflict-freeze / decision-authority path.
- match: title=authority; concepts=authority; result=authority; changed_paths=authority; goal=authority,operator
- source warning: none
- ranked evidence choices:
  - `MAP_System/notes/review-guide.md` — guide; can prove documented procedure, protocol, or operating convention
  - `MAP_System/tasks/TASK-204.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs

### 5. TASK-184 — Make command-center intake the default visible broad-directive path

- scope: MAP / command-center-ui / RELEASED
- task score: 26
- summary: RELEASED: Make command-center intake the default visible broad-directive path.
- match: title=default; concepts=default; result=default; goal=default,operator,scope
- source warning: none
- ranked evidence choices:
  - `MAP_System/tasks/TASK-184.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs
  - `MAP_System/tests/test_command_center_intake.py` — test; can prove executed checks, regression behavior, parity, or validation evidence

### 6. TASK-188 — Real-parameter calibration + first robustness grading

- scope: MAP / map-runtime / RELEASED
- task score: 25
- summary: RELEASED: Real-parameter calibration + first robustness grading.
- match: title=real; concepts=real; result=real; changed_paths=real; goal=real
- source warning: none
- ranked evidence choices:
  - `MAP_System/tasks/TASK-188.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs
  - `MAP_System/artifacts/audits/map-real-parameter-calibration-results-2026-07-14.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

## Required response

Return: `query ID | selected TASK IDs | up to two selected source paths |
confidence high/medium/low | concise rationale or no strong match`.
Also state ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1196

---

# TASK-257 Holdout Packet — H6

Generated retrieval projection; not authority.
Use only this packet. Do not search or open named sources.

- corpus searched: 45 deterministic uncurated fingerprints
- truth set: withheld
- discovery ceiling: 1200 estimated tokens
- watermark: 2026-07-19T14:05:00-04:00

## Query

How can a ProjectUpdater user export and restore every stored project field, keep the older status snapshot intact, reject malformed input safely, and require confirmation before overwriting current data?

## Candidates

### 1. TASK-205 — ProjectUpdater full JSON backup export + import (complete IDEA-0015 data-loss mitigation)

- scope: ProjectUpdater / map-runtime / RELEASED
- task score: 77
- summary: RELEASED: ProjectUpdater full JSON backup export + import (complete IDEA-0015 data-loss mitigation).
- match: title=data,export,projectupdater; concepts=data,export,projectupdater; result=data,export,projectupdater; changed_paths=projectupdater; project=projectupdater; goal=data,export,keep,restore,snapshot,status
- source warning: none
- ranked evidence choices:
  - `MAP_System/tasks/TASK-205.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs
  - `Projects/ProjectUpdater/artifacts/task-projectupdater-backup-verification.md` — test; can prove executed checks, regression behavior, parity, or validation evidence

### 2. TASK-168 — Mission-control write-control design (spec only, no implementation)

- scope: MAP / map-runtime / APPROVED
- task score: 8
- summary: APPROVED: Mission-control write-control design (spec only, no implementation).
- match: goal=confirmation,every,reject,safely
- source warning: none
- ranked evidence choices:
  - `MAP_System/tasks/TASK-168.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs
  - `MAP_System/artifacts/planning/mission-control-write-control-spec.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

### 3. TASK-193 — First brain compaction: archive TASK-147-192 era narrative

- scope: MAP / map-runtime / RELEASED
- task score: 7
- summary: RELEASED: First brain compaction: archive TASK-147-192 era narrative.
- match: changed_paths=current; goal=current,keep
- source warning: none
- ranked evidence choices:
  - `MAP_System/shared/current-state.md` — current_state; can prove current project/system posture at its verification watermark
  - `MAP_System/tasks/TASK-193.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs

### 4. TASK-181 — Use local librarian to compact emergence records

- scope: MAP / command-center-ui / RELEASED
- task score: 6
- summary: RELEASED: Use local librarian to compact emergence records.
- match: changed_paths=require,user
- source warning: registered output gap
- ranked evidence choices:
  - `MAP_System/emergence/insights/INS-0005-release-reviews-must-inspect-every-user-visible-acquisition-path.md` — review; can prove independent findings, verdict, and acceptance assessment
  - `MAP_System/emergence/ideas/IDEA-0015-add-an-export-import-json-button-to-projectupdater-to-mitigate-i.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

### 5. TASK-188 — Real-parameter calibration + first robustness grading

- scope: MAP / map-runtime / RELEASED
- task score: 6
- summary: RELEASED: Real-parameter calibration + first robustness grading.
- match: goal=current,data,every
- source warning: none
- ranked evidence choices:
  - `MAP_System/tasks/TASK-188.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs
  - `MAP_System/artifacts/audits/map-real-parameter-calibration-results-2026-07-14.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

### 6. TASK-192 — Close taxonomy-audit regression tests #4-#6

- scope: MAP / map-runtime / RELEASED
- task score: 5
- summary: RELEASED: Close taxonomy-audit regression tests #4-#6.
- match: changed_paths=project; goal=project
- source warning: none
- ranked evidence choices:
  - `MAP_System/tasks/TASK-192.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs
  - `MAP_System/tests/test_multi_project_isolation.py` — test; can prove executed checks, regression behavior, parity, or validation evidence

## Required response

Return: `query ID | selected TASK IDs | up to two selected source paths |
confidence high/medium/low | concise rationale or no strong match`.
Also state ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1156

---

# TASK-257 Holdout Packet — H7

Generated retrieval projection; not authority.
Use only this packet. Do not search or open named sources.

- corpus searched: 45 deterministic uncurated fingerprints
- truth set: withheld
- discovery ceiling: 1200 estimated tokens
- watermark: 2026-07-19T14:05:00-04:00

## Query

Where can I compare per-task effort proxies with delivery outcomes and see productive versus discarded work without inventing token costs or dollar amounts?

## Candidates

### 1. TASK-190 — Cost/yield rollup: per-task cost x outcome view

- scope: MAP / map-runtime / RELEASED
- task score: 28
- summary: RELEASED: Cost/yield rollup: per-task cost x outcome view.
- match: title=per; concepts=per; result=per; goal=dollar,per,productive,proxies
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_cost_yield.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/artifacts/reports/cost-yield-rollup-2026-07-14.md` — outcome; can prove measured result, cost/yield, later use, or operational effect

### 2. TASK-162 — MAP 6.13: Implement protocol/semantic validator L1 wiring and halt-store integration

- scope: MAP / map-runtime / APPROVED
- task score: 4
- summary: APPROVED: MAP 6.13: Implement protocol/semantic validator L1 wiring and halt-store integration.
- match: goal=per,token
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_validate_layer1.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/tests/test_validate_protocol.py` — guide; can prove documented procedure, protocol, or operating convention

### 3. TASK-180 — Compact and wikilink emergence records

- scope: MAP / emergence-and-learning / RELEASED
- task score: 4
- summary: RELEASED: Compact and wikilink emergence records.
- match: goal=token,without
- source warning: none
- ranked evidence choices:
  - `MAP_System/emergence/templates/PROMOTION_RECORD_TEMPLATE.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence
  - `MAP_System/emergence/templates/SYNTHESIS_NOTE_TEMPLATE.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

### 4. TASK-193 — First brain compaction: archive TASK-147-192 era narrative

- scope: MAP / map-runtime / RELEASED
- task score: 4
- summary: RELEASED: First brain compaction: archive TASK-147-192 era narrative.
- match: goal=outcomes,per
- source warning: none
- ranked evidence choices:
  - `MAP_System/archive/compactions/compaction-2026-07-14-tasks-147-192.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence
  - `MAP_System/shared/improvement-backlog.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

### 5. TASK-203 — CommandCenterUI outcome + cost/yield rows in MAP runtime card

- scope: MAP / command-center-ui / RELEASED
- task score: 4
- summary: RELEASED: CommandCenterUI outcome + cost/yield rows in MAP runtime card.
- match: goal=outcomes,per
- source warning: registered output gap
- ranked evidence choices:
  - `MAP_System/artifacts/reports/task203-map-health-card.png` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence
  - `MAP_System/artifacts/reports/task-203-ui-metrics-cards-evidence.md` — outcome; can prove measured result, cost/yield, later use, or operational effect

### 6. TASK-161 — MAP 6.13: Implement resilience controls and chaos probes

- scope: MAP / map-runtime / APPROVED
- task score: 2
- summary: APPROVED: MAP 6.13: Implement resilience controls and chaos probes.
- match: goal=inventing
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_resilience_controls.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/tests/test_durable_execution.py` — test; can prove executed checks, regression behavior, parity, or validation evidence

## Required response

Return: `query ID | selected TASK IDs | up to two selected source paths |
confidence high/medium/low | concise rationale or no strong match`.
Also state ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1061

---

# TASK-257 Holdout Packet — H8

Generated retrieval projection; not authority.
Use only this packet. Do not search or open named sources.

- corpus searched: 45 deterministic uncurated fingerprints
- truth set: withheld
- discovery ceiling: 1200 estimated tokens
- watermark: 2026-07-19T14:05:00-04:00

## Query

A scheduled recovery nudge may fail because the target session is already live, or it may hang during resume. Which completed fixes cover those two distinct failure modes?

## Candidates

### 1. TASK-187 — Make RnS active-session resume aware

- scope: MAP / agent-liveness-and-helpers / RELEASED
- task score: 54
- summary: RELEASED: Make RnS active-session resume aware.
- match: title=resume,session; concepts=resume,session; result=resume,session; goal=already,because,failure,nudge,resume,scheduled,session
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_limit_watcher.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/notes/limit-exhaustion-protocol.md` — guide; can prove documented procedure, protocol, or operating convention

### 2. TASK-198 — Fix RnS failed-nudge consumption and live-state reconciliation

- scope: MAP / agent-liveness-and-helpers / RETIRED
- task score: 48
- summary: RETIRED: Fix RnS failed-nudge consumption and live-state reconciliation.
- match: title=live,nudge; concepts=live,nudge; result=live,nudge; goal=already,live,resume,scheduled
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_limit_watcher.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/agents/status.json` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence

### 3. TASK-172 — Design MAP session replay read model

- scope: MAP / command-center-ui / APPROVED
- task score: 25
- summary: APPROVED: Design MAP session replay read model.
- match: title=session; concepts=session; result=session; changed_paths=session; goal=session
- source warning: none
- ranked evidence choices:
  - `MAP_System/artifacts/designs/session-replay-read-model-design.md` — artifact; can prove task-specific analysis, plan, audit, or experiment evidence
  - `MAP_System/tasks/TASK-172.json` — task_scope; can prove declared intent, scope, status, ownership, and registered outputs

### 4. TASK-173 — Implement MAP-only session replay builder

- scope: MAP / map-runtime / APPROVED
- task score: 25
- summary: APPROVED: Implement MAP-only session replay builder.
- match: title=session; concepts=session; result=session; changed_paths=session; goal=session
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_session_replay.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/scripts/session_replay.py` — implementation; can prove implementation behavior and executable mechanism

### 5. TASK-178 — Refresh mission-control roster from live hcom

- scope: MAP / map-runtime / APPROVED
- task score: 22
- summary: APPROVED: Refresh mission-control roster from live hcom.
- match: title=live; concepts=live; result=live; goal=live
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_mission_control_tui.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/scripts/mission_control_tui.py` — implementation; can prove implementation behavior and executable mechanism

### 6. TASK-176 — Prune stale RnS incidents for absent sessions

- scope: MAP / agent-liveness-and-helpers / APPROVED
- task score: 4
- summary: APPROVED: Prune stale RnS incidents for absent sessions.
- match: goal=live,those
- source warning: none
- ranked evidence choices:
  - `MAP_System/tests/test_limit_watcher.py` — test; can prove executed checks, regression behavior, parity, or validation evidence
  - `MAP_System/scripts/limit_watcher.py` — implementation; can prove implementation behavior and executable mechanism

## Required response

Return: `query ID | selected TASK IDs | up to two selected source paths |
confidence high/medium/low | concise rationale or no strong match`.
Also state ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1071

---
